from sqlalchemy import create_engine, Column,or_, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, joinedload
from datetime import datetime
from config import Config
import pandas as pd
from fpdf import FPDF
import os

Base = declarative_base()
# Table to store file metadata
class FileRecord(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, unique=True, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    extension = Column(String, nullable=True)
    last_modified = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    path_score = Column(Float, default=0.0)

    content = relationship("Content", back_populates="file", cascade="all, delete-orphan", uselist=False)

    __table_args__ = (
        Index('ix_file_path', 'file_path'),
    )

# Table to store file content
class Content(Base):
    __tablename__ = 'contents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    content_text = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Establish relationship with FileRecord
    file = relationship("FileRecord", back_populates="content")

# Table to store log entries
class LogEntry(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)  # Time of log entry
    level = Column(String, nullable=True)                               # Log level (INFO, ERROR)
    message = Column(Text, nullable=False)                             # Log message

def compute_lenght_score(file_path):
    #compute lenght
    base_score = 100.0
    length_penalty = len(file_path) * 0.5
    score = base_score - length_penalty

    # extension bonus :) +10 if ends with .txt
    lower_path = file_path.lower()
    if lower_path.endswith(".txt"):
        score += 10

    if score <= 0:
        score = 1.0
    return score
def compute_depth_score(file_path):
    base_score = 100.0
    #compute depth
    depth_penalty = file_path.count(os.sep) * 2.5  # adjust 2.5 as needed
    score = base_score - depth_penalty

    if score <= 0:
        score = 1.0
    return score

class DatabaseAdapter:
    def __init__(self, db_url, config):
        # Create database connection
        self.engine = create_engine(db_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

        method = config.get_ranking_method()
        if method == "depth":
            self.score_function = compute_depth_score
        else:
            self.score_function = compute_lenght_score
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
                    last_modified=last_modified,
                    updated_at=datetime.now()
                )
                file_record.path_score = self.score_function(file_path)

                session.add(file_record)
                session.flush()
                # Insert content in the separate table
                content_record = Content(
                    file_id=file_record.id,
                    content_text=content,
                    updated_at=datetime.now()
                )
                session.add(content_record)
            else:
                # Update record if file has changed
                if last_modified > file_record.last_modified:
                    file_record.file_name = file_name
                    file_record.file_size = file_size
                    file_record.extension = extension
                    file_record.last_modified = last_modified
                    file_record.updated_at = datetime.now()
                    file_record.path_score = self.score_function(file_path)                    # Update content if available
                    if file_record.content:
                        file_record.content.content_text = content
                        file_record.content.updated_at = datetime.now()
                    else:
                        content_record = Content(
                            file_id=file_record.id,
                            content_text=content,
                            updated_at=datetime.now()
                        )
                        session.add(content_record)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error in insert_or_update_file: {e}")
        finally:
            session.close()



    def search_files(self, path_terms=None, content_terms=None):

        session = self.Session()
        try:
            # Base query
            q = session.query(
                FileRecord.id,
                FileRecord.file_path,
                FileRecord.file_name,
                FileRecord.file_size,
                FileRecord.extension,
                FileRecord.last_modified,
                FileRecord.path_score,
                Content.content_text
            ).join(Content)

            # Filter by path terms
            from sqlalchemy import or_

            # Path filtering (OR if more "path:", AND if only one"path:")
            if path_terms:
                if len(path_terms) == 1:
                    q = q.filter(FileRecord.file_path.ilike(f"%{path_terms[0]}%"))
                else:
                    path_conditions = [FileRecord.file_path.ilike(f"%{term}%") for term in path_terms]
                    q = q.filter(or_(*path_conditions))

            # Filter by content terms
            if content_terms:
                for term in content_terms:
                    like_term = f"%{term}%"
                    q = q.filter(or_(
                        Content.content_text.ilike(like_term),
                        FileRecord.file_name.ilike(like_term),
                        FileRecord.extension.ilike(like_term)
                    ))

            # Order by path_score
            q = q.order_by(FileRecord.path_score.desc())
            return q.all()
        finally:
            session.close()

    def insert_log(self, level, message):
        session = self.Session()
        try:
            log_entry = LogEntry(timestamp=datetime.now(), level=level, message=message)
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error in insert_log: {e}")
        finally:
            session.close()

    def get_file_last_modified(self, file_path):
        session = self.Session()
        try:
            record = session.query(FileRecord).filter_by(file_path=file_path).first()
            return record.last_modified if record else None
        finally:
            session.close()

    def insert_search_query(self, raw_query, result_count=None):
        msg = f"QUERY: {raw_query}"
        if result_count is not None:
            msg += f" | results: {result_count}"
        self.insert_log("SEARCH", msg)

    def fetch_recent_queries(self, limit=5):

        session = self.Session()
        try:
            q = (session.query(LogEntry)
                 .filter(LogEntry.level == "SEARCH")
                 .order_by(LogEntry.timestamp.desc())
                 .limit(limit))
            results = q.all()
            # Extract the actual query text
            queries = []
            for r in results:
                if r.message.startswith("QUERY: "):
                    queries.append(r.message.replace("QUERY: ", "").strip())
            return queries
        finally:
            session.close()