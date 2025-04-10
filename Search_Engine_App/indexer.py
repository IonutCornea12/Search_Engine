import os
from datetime import datetime
from export_logs import export_logs_to_txt


class Indexer:
    def __init__(self, db_adapter, text_extractor):
        self.db_adapter = db_adapter
        self.text_extractor = text_extractor
        self.processed_files = 0  # Counter for processed files
        self.errors = 0           # Counter for errors
        self.report_lines = []    # Store logs for the report

    def process_file(self, file_path):
        try:
            last_modified = os.path.getmtime(file_path)
            existing = self.db_adapter.get_file_last_modified(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            _, extension = os.path.splitext(file_path)
            #Add to db if it does not exist
            if existing is None or last_modified > existing:
                content = self.text_extractor.extract(file_path)
                self.db_adapter.insert_or_update_file(
                    file_path, file_name, file_size, extension, content, last_modified
                )
                if existing is None:
                    log_msg = f"Indexed new file: {file_path}"
                else:
                    log_msg = f"Updated file: {file_path}"
                self.report_lines.append(log_msg)
                self.processed_files += 1
            else:
                # Skip file if it's unchanged
                self.report_lines.append(f"Skipped unchanged file: {file_path}")
        except Exception as e:
            # Log error if something goes wrong
            self.report_lines.append(f"Error processing {file_path}: {e}")
            self.errors += 1

    def process_files(self, file_paths):
        for file_path in file_paths:
            self.process_file(file_path)

    def generate_report(self):
        # Insert each log into the logs table
        for line in self.report_lines:
            self.db_adapter.insert_log("INFO", line)
            # Insert a summary of the indexing process
        summary = (f"Indexing Summary - Timestamp: {datetime.now()}. "
                   f"Total files processed: {self.processed_files}. Errors: {self.errors}.\n")
        self.db_adapter.insert_log("SUMMARY", summary)
        print("\n")
        print("Indexing report has been logged into the database.")

        # Automatically export logs to a file after indexing
        export_logs_to_txt(self.db_adapter)
        print("Logs have been automatically exported.")

        self.db_adapter.export_index_report(filename="index_report")