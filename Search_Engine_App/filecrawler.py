import os,fnmatch

class FileCrawler:
    def __init__(self, ignore_patterns=None,allowed_extensions = None):
        # Directories to ignore during crawling
        if ignore_patterns:
            self.ignore_patterns = [
                f"*{pattern}" if not pattern.startswith('*') else pattern
                for pattern in ignore_patterns
            ]
        else:
            self.ignore_patterns = []
        self.allowed_extensions = allowed_extensions if allowed_extensions else [".txt"]

    def crawl(self, start_dir):
        file_paths = []
        for root, dirs, files in os.walk(start_dir):
            # Skip ignored dir
            dirs[:] = [
                d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in self.ignore_patterns)
            ]

            for file in files:
                if not any(file.lower().endswith(ext) for ext in self.allowed_extensions):
                    continue

                # Skip file if it matches an ignore pattern
                if any(fnmatch.fnmatch(file, pattern) for pattern in self.ignore_patterns):
                    continue

                file_paths.append(os.path.join(root, file))

        return file_paths