from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NotificationType(enum.Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    MENTION = "mention"
    SYSTEM = "system"
    TRENDING = "trending"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Optional data for specific notification types
    data = Column(Text, nullable=True)  # JSON data for additional info
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who triggered the notification
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications", foreign_keys=[user_id])
    sender = relationship("User", foreign_keys=[sender_id])
    post = relationship("Post")
    outfit = relationship("Outfit") 