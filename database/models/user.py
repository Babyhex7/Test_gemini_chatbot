"""
User Model - Siswa yang menggunakan EduMindAI
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database.base import Base


class User(Base):
    """Model untuk menyimpan data user (siswa)"""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, unique=True)
    school_id = Column(String(50), nullable=True, index=True)
    grade = Column(String(20), nullable=True)  # Kelas/tingkat
    is_active = Column(Boolean, default=True)
    
    # Preferences
    preferred_language = Column(String(10), default="id")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, student_id={self.student_id})>"
