import os

class FileCrawler:
    def __init__(self, root_dir, ignore_patterns=None):
        self.root_dir = root_dir
        # Directories to ignore during crawling
        if ignore_patterns is None:
            ignore_patterns = ['.git', '__pycache__']
        self.ignore_patterns = ignore_patterns

    def crawl(self):
        file_paths = []
        for root, dirs, files in os.walk(self.root_dir):
            # Skip ignored dir
            dirs[:] = [d for d in dirs if not any(ignore in d for ignore in self.ignore_patterns)]
            for file in files:
                # Only include .txt files
                if file.lower().endswith('.txt'):
                    file_paths.append(os.path.join(root, file))
        return file_paths