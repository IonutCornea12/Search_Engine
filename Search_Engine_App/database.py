from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

Base = declarative_base()

# Table to store file metadata and content
class FileRecord(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, unique=True, nullable=False)   # Full file path - unique
    file_name = Column(String, nullable=False)    # Name
    file_size = Column(Integer, nullable=True)         # File size - bytes
    extension = Column(String, nullable=True)           # File extension (ex:.txt)
    content = Column(Text, nullable=True)                 # File content
    last_modified = Column(Float, nullable=False)       # Last modified timestamp

    __table_args__ = (
        Index('ix_file_path', 'file_path'),  # Add index for faster lookups
    )

# Table to store log entries
class LogEntry(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)  # Time of log entry
    level = Column(String, nullable=True)                              # Log level (INFO, ERROR)
    message = Column(Text, nullable=False)                             # Log message

class DatabaseAdapter:
    def __init__(self, db_url):
        # Create database connection
        self.engine = create_engine(db_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def insert_or_update_file(self, file_path, file_name, file_size, extension, content, last_modified):
        session = self.Session()
        try:
            # Check if the file already exists
            file_record = session.query(FileRecord).filter_by(file_path=file_path).first()
            if file_record is None:
                # Create new record if it does not exist
                file_record = FileRecord(
                    file_path=file_path,
                    file_name=file_name,
                    file_size=file_size,
                    extension=extension,
                    content=content,
                    last_modified=last_modified
                )
                session.add(file_record)
            else:
                # Update record if file has changed
                if last_modified > file_record.last_modified:
                    file_record.file_name = file_name
                    file_record.file_size = file_size
                    file_record.extension = extension
                    file_record.content = content
                    file_record.last_modified = last_modified
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error in insert or update file: {e}")
        finally:
            session.close()

    def get_file_last_modified(self, file_path):
        session = self.Session()
        try:
            file_record = session.query(FileRecord).filter_by(file_path=file_path).first()
            return file_record.last_modified if file_record else None
        finally:
            session.close()

    def search_files(self, query):
        session = self.Session()
        try:
            keywords = query.split()
            q = session.query(FileRecord)
            for kw in keywords:
                q = q.filter(FileRecord.content.ilike(f"%{kw}%"))
            return q.all()
        finally:
            session.close()

    def insert_log(self, level, message):
        session = self.Session()
        try:
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=message
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error in insert_log: {e}")
        finally:
            session.close()