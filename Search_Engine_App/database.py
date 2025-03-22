from sqlalchemy import create_engine, Column,or_, Integer, String, Float, Text, DateTime, ForeignKey, Index, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime
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
                    last_modified=last_modified,
                    updated_at=datetime.now()
                )
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

                    # Update content if available
                    if file_record.content:
                        file_record.content.content_text = content
                        file_record.content.updated_at = datetime.now()
                    else:
                        content_record = FileContent(
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

    from sqlalchemy.orm import joinedload

    def search_files(self, query):
        session = self.Session()
        try:
            keywords = query.split()
            q = session.query(
                FileRecord.id,
                FileRecord.file_path,
                FileRecord.file_name,
                FileRecord.file_size,
                FileRecord.extension,
                FileRecord.last_modified,
                Content.content_text
            ).join(Content)

            for kw in keywords:
                like_kw = f"%{kw}%"
                q = q.filter(or_(
                    Content.content_text.ilike(like_kw),
                    FileRecord.file_name.ilike(like_kw),
                    FileRecord.file_path.ilike(like_kw),
                    FileRecord.extension.ilike(like_kw)
                ))
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