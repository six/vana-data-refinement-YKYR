from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model for SQLAlchemy
Base = declarative_base()
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
