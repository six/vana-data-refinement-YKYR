from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model for SQLAlchemy
Base = declarative_base()

# Define database models - the schema is generated using these
class UserRefined(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    locale = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    storage_metrics = relationship("StorageMetric", back_populates="user")
    auth_sources = relationship("AuthSource", back_populates="user")

class StorageMetric(Base):
    __tablename__ = 'storage_metrics'
    
    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    percent_used = Column(Float, nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship("UserRefined", back_populates="storage_metrics")

class AuthSource(Base):
    __tablename__ = 'auth_sources'
    
    auth_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    source = Column(String, nullable=False)
    collection_date = Column(DateTime, nullable=False)
    data_type = Column(String, nullable=False)
    
    user = relationship("UserRefined", back_populates="auth_sources")

# New models for browsing data
class BrowsingAuthor(Base):
    __tablename__ = 'browsing_authors'
    
    author_id = Column(String, primary_key=True)
    created_time = Column(DateTime, nullable=False)
    
    browsing_entries = relationship("BrowsingEntry", back_populates="author")
    browsing_stats = relationship("BrowsingStats", back_populates="author", uselist=False)

class BrowsingEntry(Base):
    __tablename__ = 'browsing_entries'
    
    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, ForeignKey('browsing_authors.author_id'), nullable=False)
    url = Column(String, nullable=False)
    time_spent = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    author = relationship("BrowsingAuthor", back_populates="browsing_entries")

class BrowsingStats(Base):
    __tablename__ = 'browsing_stats'
    
    stats_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, ForeignKey('browsing_authors.author_id'), nullable=False)
    url_count = Column(Integer, nullable=False)
    average_time_spent = Column(Float, nullable=False)
    browsing_type = Column(String, nullable=False)
    
    author = relationship("BrowsingAuthor", back_populates="browsing_stats")
