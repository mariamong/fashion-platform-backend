from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.models.post import ClothingCategory


class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: ClothingCategory
    brand: Optional[str] = None
    price: Optional[float] = None
    purchase_link: Optional[str] = None
    store_name: Optional[str] = None
    rating: Optional[float] = None
    review: Optional[str] = None
    is_public: bool = True


class PostCreate(PostBase):
    main_image: str
    additional_images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ClothingCategory] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    purchase_link: Optional[str] = None
    store_name: Optional[str] = None
    rating: Optional[float] = None
    review: Optional[str] = None
    is_public: Optional[bool] = None
    main_image: Optional[str] = None
    additional_images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class PostResponse(PostBase):
    id: int
    author_id: int
    main_image: str
    additional_images: Optional[List[str]] = None
    is_featured: bool
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: dict  # Will be populated with user info
    tags: List[str] = []
    is_liked: bool = False
    
    class Config:
        from_attributes = True


class PostList(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    size: int


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: dict  # Will be populated with user info
    
    class Config:
        from_attributes = True


class CommentList(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    size: int


class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 