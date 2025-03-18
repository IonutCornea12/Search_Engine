class TextExtractor:
    def extract(self, file_path):
        try:
            # Open and read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # Handle read errors
            print(f"Error reading {file_path}: {e}")
            return ""