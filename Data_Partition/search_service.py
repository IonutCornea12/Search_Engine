import os

class SearchService:
    def search_files_in_directory(self, directory, query):
        matches = []
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if query.lower() in file_name.lower():
                    full_path = os.path.join(root, file_name)
                    matches.append(full_path)
        return matches