from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    is_read: bool = False


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    sender_id: Optional[int] = None
    post_id: Optional[int] = None
    outfit_id: Optional[int] = None
    data: Optional[str] = None
    created_at: datetime
    sender: Optional[dict] = None
    
    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    page: int
    size: int


class UnreadCount(BaseModel):
    unread_count: int 