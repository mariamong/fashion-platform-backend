from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OutfitBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True


class OutfitCreate(OutfitBase):
    item_ids: List[int] = []


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class OutfitResponse(OutfitBase):
    id: int
    creator_id: int
    like_count: int
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator: dict
    items: List[dict] = []
    
    class Config:
        from_attributes = True


class OutfitItemResponse(BaseModel):
    id: int
    position: int
    notes: Optional[str] = None
    created_at: datetime
    post: dict
    
    class Config:
        from_attributes = True


class OutfitList(BaseModel):
    outfits: List[OutfitResponse]
    total: int
    page: int
    size: int 