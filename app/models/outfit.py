from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    like_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    likes = relationship("OutfitLike", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer, nullable=False)  # Order in the outfit
    notes = Column(Text, nullable=True)  # Notes about this item in the outfit
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # Relationships
    outfit = relationship("Outfit", back_populates="items")
    post = relationship("Post", back_populates="outfit_items")


class OutfitLike(Base):
    __tablename__ = "outfit_likes"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    
    # Relationships
    user = relationship("User")
    outfit = relationship("Outfit", back_populates="likes") 