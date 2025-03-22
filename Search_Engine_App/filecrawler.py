import os,fnmatch

class FileCrawler:
    def __init__(self, ignore_patterns=None):
        # Directories to ignore during crawling
        if ignore_patterns:
            self.ignore_patterns = [
                f"*{pattern}" if not pattern.startswith('*') else pattern
                for pattern in ignore_patterns
            ]
        else:
            self.ignore_patterns = []

    def crawl(self, start_dir):
        file_paths = []
        for root, dirs, files in os.walk(start_dir):
            # Skip ignored dir
            dirs[:] = [
                d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in self.ignore_patterns)
            ]

            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)

                # Normalize extensions for consistent matching
                ext = ext.lower()
                # Separate matching logic for filenames and extensions
                ignore_match = any(fnmatch.fnmatch(file, pattern) for pattern in self.ignore_patterns)
                ext_match = any(pattern.lstrip('*') == ext for pattern in self.ignore_patterns)

                if ignore_match or ext_match:
                    continue

                if file.lower().endswith('.txt'):
                    file_paths.append(os.path.join(root, file))

        return file_paths