from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ClothingCategory(enum.Enum):
    TOPS = "tops"
    BOTTOMS = "bottoms"
    DRESSES = "dresses"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORIES = "accessories"
    BAGS = "bags"
    JEWELRY = "jewelry"
    UNDERWEAR = "underwear"
    SWIMWEAR = "swimwear"
    ACTIVE_WEAR = "active_wear"
    FORMAL = "formal"
    CASUAL = "casual"
    VINTAGE = "vintage"
    OTHER = "other"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ClothingCategory), nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    purchase_link = Column(String, nullable=True)
    store_name = Column(String, nullable=True)
    rating = Column(Float, nullable=True)  # User's rating (1-5)
    review = Column(Text, nullable=True)  # User's review text
    
    # Images
    main_image = Column(String, nullable=False)  # Main image URL
    additional_images = Column(Text, nullable=True)  # JSON array of additional image URLs
    
    # Metadata
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    outfit_items = relationship("OutfitItem", back_populates="post", cascade="all, delete-orphan")
    
    # Tags for search and categorization
    tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")


class PostTag(Base):
    __tablename__ = "post_tags"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="post_tags") 