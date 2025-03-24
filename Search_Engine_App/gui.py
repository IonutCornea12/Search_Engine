from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QLabel, QHBoxLayout, QStatusBar, QComboBox, QDateEdit, QSizePolicy
)
from filecrawler import FileCrawler
from textextractor import TextExtractor
from indexer import Indexer
from database import DatabaseAdapter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local File Search Engine")
        self.setGeometry(100, 100, 900, 700)
        # Database connection user ionutcornea, pass ionutcornea
        db_url = "postgresql+psycopg2://ionutcornea:ionutcornea@localhost/search_engine_db"
        self.db = DatabaseAdapter(db_url)
        self.indexer = Indexer(self.db, TextExtractor())

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Display selected directory
        self.dir_label = QLabel("Directory to Index:")
        self.layout.addWidget(self.dir_label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        # Button to start indexing
        self.index_button = QPushButton("Start Indexing")
        self.index_button.clicked.connect(self.start_indexing)
        self.layout.addWidget(self.index_button)

        # Search Bar with Filters
        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.search)
        search_layout.addWidget(self.search_bar)

        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["All", ".txt", ".csv", ".json", ".xml"])
        search_layout.addWidget(self.file_type_combo)

        self.size_range_combo = QComboBox()
        self.size_range_combo.addItems(["Any size", "< 1MB", "1MB - 10MB", "> 10MB"])
        search_layout.addWidget(self.size_range_combo)

        self.layout.addLayout(search_layout)

        # Search Results
        self.results_list = QListWidget()
        self.layout.addWidget(self.results_list)

        # Action Buttons
        action_buttons = QHBoxLayout()

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        action_buttons.addWidget(self.clear_button)

        self.refresh_button = QPushButton("Refresh Index")
        self.refresh_button.clicked.connect(self.start_indexing)
        action_buttons.addWidget(self.refresh_button)


        self.ignore_patterns_input = QLineEdit()
        self.ignore_patterns_input.setPlaceholderText("Ignore Patterns (comma-separated)")
        search_layout.addWidget(self.ignore_patterns_input)
        self.layout.addLayout(action_buttons)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add layout to window
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    # Open file dialog to select a directory
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.dir_label.setText(f"Selected: {folder}")
            self.selected_folder = folder
            self.crawler = FileCrawler()
    # Start the indexing process
    def start_indexing(self):
        if hasattr(self, 'selected_folder'): #retunrs if it has atribute with that name
            # Read ignore patterns from GUI
            ignore_patterns = [
                pattern.strip() for pattern in self.ignore_patterns_input.text().strip().split(',') if pattern.strip()
            ]

            self.crawler = FileCrawler(ignore_patterns)
            files = self.crawler.crawl(self.selected_folder)
            if files:
                self.indexer.process_files(files)
                self.indexer.generate_report()
                self.status_bar.showMessage("Indexing completed and logged.")
            else:
                self.status_bar.showMessage("No files found for indexing.")
        else:
            self.results_list.addItem("Please select a folder first.")

    # Search the database for matching content
    def search(self):
        self.results_list.clear()
        query = self.search_bar.text().strip()
        file_type = self.file_type_combo.currentText()
        size_range = self.size_range_combo.currentText()

        if query:
            results = self.db.search_files(query)

            for file_record in results:
                if file_type != "All" and file_record.extension != file_type:
                    continue
                if not self.size_in_range(file_record.file_size, size_range):
                    continue
                content_preview = "\n".join(
                    file_record.content_text.splitlines()[:3]) if file_record.content_text else ""
                display_text = (
                        f"Name: {file_record.file_name}\n"
                        f"Path: {file_record.file_path}\n"
                        f"Size: {file_record.file_size} bytes\n"
                        f"Extension: {file_record.extension}\n"
                        f"Preview:\n{content_preview}\n"
                        + "-" * 40
                )
                self.results_list.addItem(display_text)
        else:
            self.results_list.addItem("Enter a search query.")

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

# End of GUI
