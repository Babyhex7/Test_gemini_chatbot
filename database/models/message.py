"""
Message Model - Chat messages dalam session
"""
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from database.base import Base


class MessageRole(str, enum.Enum):
    """Enum untuk role pengirim pesan"""
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"


class Message(Base):
    """Model untuk menyimpan pesan dalam session"""
    
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    # Message content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Metadata
    phase = Column(String(50), nullable=True)  # Fase saat pesan dikirim
    message_type = Column(String(50), nullable=True)  # story, question, answer, narrative, tips
    sequence_number = Column(Integer, nullable=False)  # Urutan pesan dalam session
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, seq={self.sequence_number})>"
