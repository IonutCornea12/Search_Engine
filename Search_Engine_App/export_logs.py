from database import LogEntry

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