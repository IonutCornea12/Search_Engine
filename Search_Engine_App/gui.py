from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QLabel
)
from filecrawler import FileCrawler
from textextractor import TextExtractor
from indexer import Indexer
from database import DatabaseAdapter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local File Search Engine")
        self.setGeometry(100, 100, 800, 600)

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

        # Button to select a folder
        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        # Button to start indexing
        self.index_button = QPushButton("Start Indexing")
        self.index_button.clicked.connect(self.start_indexing)
        self.layout.addWidget(self.index_button)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.search)
        self.layout.addWidget(self.search_bar)

        # Display search results
        self.results_list = QListWidget()
        self.layout.addWidget(self.results_list)

        # Add layout to window
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    # Open file dialog to select a directory
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.dir_label.setText(f"Selected: {folder}")
            self.crawler = FileCrawler(folder)

    # Start the indexing process
    def start_indexing(self):
        if hasattr(self, 'crawler'): #retunrs if it has atribute with that name
            files = self.crawler.crawl()
            self.indexer.process_files(files)
            self.indexer.generate_report()
            self.results_list.addItem("Indexing completed and logged.")

    # Search the database for matching content
    def search(self, text):
        self.results_list.clear()
        if text.strip():
            results = self.db.search_files(text)
            for file_record in results:
                preview = "\n".join(file_record.content.splitlines()[:3]) if file_record.content else ""
                display_text = (
                    f"Name: {file_record.file_name}\n"
                    f"Path: {file_record.file_path}\n"
                    f"Size: {file_record.file_size} bytes\n"
                    f"Extension: {file_record.extension}\n"
                    f"Preview:\n{preview}\n"
                    + "-" * 40
                )
                self.results_list.addItem(display_text)
        else:
            self.results_list.addItem("Enter a search query.")