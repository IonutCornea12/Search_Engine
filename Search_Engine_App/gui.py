from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLineEdit,QPushButton, QListWidget, QFileDialog, QLabel, QHBoxLayout, QStatusBar, QComboBox)
from filecrawler import FileCrawler
from textextractor import TextExtractor
from indexer import Indexer
from database import DatabaseAdapter
from config import Config
from query_parser import parse_query
from export_logs import export_index_report
from search_observer import (SearchObservable,QueryLoggerObserver,SuggestionUpdaterObserver)
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config("config.json")
        self.stored_ignore_patterns = self.config.get_ignore_patterns()
        self.setWindowTitle("Local File Search Engine")
        self.setGeometry(100, 100, 900, 700)

        db_url = self.config.get_db_url()
        self.db = DatabaseAdapter(db_url, self.config)
        self.indexer = Indexer(self.db, TextExtractor(),self.config)
        self.search_observable = SearchObservable()
        self.log_query = True
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.dir_label = QLabel("Directory to Index:")
        self.layout.addWidget(self.dir_label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        self.index_button = QPushButton("Start Indexing")
        self.index_button.clicked.connect(self.start_indexing)
        self.layout.addWidget(self.index_button)

        self.suggestions_combo = QComboBox()
        self.suggestions_combo.setPlaceholderText("Recent Searches")
        self.suggestions_combo.activated.connect(self.on_suggestion_selected)
        self.layout.addWidget(self.suggestions_combo)

        self.search_observable.register_observer(QueryLoggerObserver(self.db))
        self.search_observable.register_observer(SuggestionUpdaterObserver(self.suggestions_combo, self.db))
        # Search layout with filters
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.perform_live_search)
        self.search_bar.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_bar)

        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["All", ".txt", ".csv", ".json", ".xml"])
        search_layout.addWidget(self.file_type_combo)

        self.size_range_combo = QComboBox()
        self.size_range_combo.addItems(["Any size", "< 1MB", "1MB - 10MB", "> 10MB"])
        search_layout.addWidget(self.size_range_combo)

        self.ignore_patterns_input = QLineEdit()
        self.ignore_patterns_input.setPlaceholderText("Ignore Patterns (comma-separated)")
        search_layout.addWidget(self.ignore_patterns_input)

        self.layout.addLayout(search_layout)

        self.results_list = QListWidget()
        self.layout.addWidget(self.results_list)

        action_buttons = QHBoxLayout()

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        action_buttons.addWidget(self.clear_button)

        self.refresh_button = QPushButton("Refresh Index")
        self.refresh_button.clicked.connect(self.start_indexing)
        action_buttons.addWidget(self.refresh_button)

        self.layout.addLayout(action_buttons)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        self.update_suggestions()

    def update_suggestions(self):
        self.suggestions_combo.clear()
        recent_queries = self.db.fetch_recent_queries(limit=5)
        if not recent_queries:
            self.suggestions_combo.addItem("No recent searches.")
        else:
            for q in recent_queries:
                if " | results: " in q:
                    query_text = q.split(" | results: ")[0].strip()
                    results_count = q.split(" | results: ")[1].strip()
                    self.suggestions_combo.addItem(f"{query_text} ({results_count})", userData=query_text)
                else:
                    self.suggestions_combo.addItem(q, userData=q)

    def on_suggestion_selected(self, index):
        query_text = self.suggestions_combo.currentData()
        if query_text is None or not query_text.strip():
            return
        self.log_query = False
        self.search_bar.setText(query_text)
        self.search()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.dir_label.setText(f"Selected: {folder}")
            self.selected_folder = folder
            self.crawler = FileCrawler()


    def start_indexing(self):
        if hasattr(self, 'selected_folder'):
            user_ignore_patterns = [
                pattern.strip()
                for pattern in self.ignore_patterns_input.text().split(',')
                if pattern.strip()
            ]
            combined_patterns = self.stored_ignore_patterns + user_ignore_patterns
            allowed_extensions = self.config.get_allowed_extensions()
            self.crawler = FileCrawler(combined_patterns, allowed_extensions)

            files = self.crawler.crawl(self.selected_folder)
            if files:
                start_time = time.time()
                self.indexer.process_files(files)
                self.indexer.generate_report()
                duration = time.time() - start_time
                msg = f"Indexing completed and logged in {duration:.2f} seconds. {len(files)} file(s) found."
                self.status_bar.showMessage(msg)
                print(msg)
            else:
                self.status_bar.showMessage("No files found for indexing.")
        else:
            self.results_list.addItem("Please select a folder first.")

    def run_search(self, query, log_query=False, update_suggestions=False, notify_observers=True):
        self.results_list.clear()
        file_type = self.file_type_combo.currentText()
        size_range = self.size_range_combo.currentText()

        if not query:
            self.results_list.addItem("Enter a search query.")
            return

        path_terms, content_terms = parse_query(query)
        results = self.db.search_files(path_terms=path_terms, content_terms=content_terms)

        if notify_observers:
            self.search_observable.notify_observers(query, results)

        if update_suggestions:
            self.update_suggestions()

        if not results:
            self.results_list.addItem("No matching files.")
            return

        self.status_bar.showMessage(f"{len(results)} files found.")

        for record in results:
            file_id, file_path, file_name, file_size, extension, last_modified, path_score, content_text = record
            if file_type != "All" and extension != file_type:
                continue
            if not self.size_in_range(file_size, size_range):
                continue
            snippet = "\n".join(content_text.splitlines()[:7]) if content_text else ""
            display_text = (
                    f"Name: {file_name}\n"
                    f"Path: {file_path}\n"
                    f"Size: {file_size} bytes\n"
                    f"Extension: {extension}\n"
                    f"Score: {path_score}\n"
                    f"Preview:\n{snippet}\n"
                    + "-" * 40
            )
            self.results_list.addItem(display_text)

    def search(self):
        query = self.search_bar.text().strip()
        self.run_search(query, log_query=self.log_query, update_suggestions=True, notify_observers=True)
        self.log_query = True

    def perform_live_search(self):
        query = self.search_bar.text().strip()
        if not query:
            self.results_list.clear()
            return
        self.run_search(query, log_query=False, update_suggestions=False, notify_observers=False)

    def size_in_range(self, size, range_text):
        if range_text == "Any size":
            return True
        if range_text == "< 1MB":
            return size < 1 * 1024 * 1024
        if range_text == "1MB - 10MB":
            return 1 * 1024 * 1024 <= size <= 10 * 1024 * 1024
        if range_text == "> 10MB":
            return size > 10 * 1024 * 1024

    def clear_results(self):
        self.results_list.clear()
        self.last_logged_query = None
        self.last_logged_result_count = None