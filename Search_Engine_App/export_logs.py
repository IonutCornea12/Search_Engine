from database import LogEntry, FileRecord
import pandas as pd
from fpdf import FPDF
import os
def export_logs_to_txt(db_adapter, filename="logs_export.txt"):
    session = db_adapter.Session()
    try:
        logs = session.query(LogEntry).order_by(LogEntry.timestamp).all()
        with open(filename, "w", encoding="utf-8") as f:
            for log in logs:
                f.write(f"{log.timestamp} [{log.level}] {log.message}\n")
        print(f"Logs exported to {filename}")
    except Exception as e:
        print(f"Error exporting logs: {e}")
    finally:
        session.close()

def truncate_middle_path(path, max_parts_start=2, max_parts_end=1):
    parts = path.strip(os.sep).split(os.sep)
    if len(parts) <= (max_parts_start + max_parts_end):
        return path
    start = parts[:max_parts_start]
    end = parts[-max_parts_end:]
    return os.sep + os.sep.join(start) + os.sep + "..." + os.sep + os.sep.join(end)

def export_index_report(db_adapter, config, filename="index_report"):
    session = db_adapter.Session()
    try:
        records = session.query(FileRecord).order_by(FileRecord.file_path).all()
        ext = config.get_report_format().lower()
        out_file = f"{filename}.{ext}"

        data = [{
            "file_path": r.file_path,
            "file_name": r.file_name,
            "extension": r.extension,
            "file_size": r.file_size,
            "path_score": r.path_score,
            "last_modified": r.last_modified
        } for r in records]

        df = pd.DataFrame(data)

        if ext == "csv":
            df.to_csv(out_file, index=False)

        elif ext == "json":
            df.to_json(out_file, orient="records", indent=2)

        elif ext == "txt":
            df.to_csv(out_file, index=False, sep='\t')

        elif ext in ["xlsx", "xls"]:
            df.to_excel(out_file, index=False, engine='openpyxl')

        elif ext == "pdf":
            class PDFReport(FPDF):
                def __init__(self):
                    super().__init__()
                    self.set_auto_page_break(auto=True, margin=15)
                    self.add_page()
                    self.set_font("Arial", size=8)

                def header_row(self, headers, col_widths):
                    for header, width in zip(headers, col_widths):
                        self.cell(width, 8, txt=str(header), border=1, align='C')
                    self.ln()

                def data_rows(self, dataframe, col_widths):
                    for row in dataframe.itertuples(index=False):
                        for col_name, value, width in zip(df.columns, row, col_widths):
                            value_str = str(value)
                            if col_name == "file_path":
                                truncated = truncate_middle_path(value_str)
                            else:
                                truncated = value_str if len(value_str) <= 40 else value_str[:37] + "..."
                            self.cell(width, 8, txt=truncated, border=1)
                        self.ln()

            pdf = PDFReport()
            col_widths = [55, 35, 20, 20, 20, 35]
            pdf.header_row(df.columns, col_widths)
            pdf.data_rows(df, col_widths)
            pdf.output(out_file)

        else:
            print(f"Unsupported report format: {ext}")
            return

        print(f"Report exported successfully to: {out_file}")

    finally:
        session.close()