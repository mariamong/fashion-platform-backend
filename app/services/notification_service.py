from sqlalchemy.orm import Session
from typing import Optional
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.post import Post, Like, Comment
from app.models.outfit import Outfit


class NotificationService:
    @staticmethod
    def create_like_notification(
        db: Session,
        post: Post,
        liker: User
    ) -> Notification:
        """Create notification when someone likes a post"""
        if liker.id == post.author_id:
            return None  # Don't notify if user likes their own post
        
        notification = Notification(
            user_id=post.author_id,
            type=NotificationType.LIKE,
            title="New Like",
            message=f"{liker.username} liked your post '{post.title}'",
            sender_id=liker.id,
            post_id=post.id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def create_comment_notification(
        db: Session,
        post: Post,
        commenter: User,
        comment_content: str
    ) -> Notification:
        """Create notification when someone comments on a post"""
        if commenter.id == post.author_id:
            return None  # Don't notify if user comments on their own post
        
        # Truncate comment content for notification
        truncated_content = comment_content[:50] + "..." if len(comment_content) > 50 else comment_content
        
        notification = Notification(
            user_id=post.author_id,
            type=NotificationType.COMMENT,
            title="New Comment",
            message=f"{commenter.username} commented on your post '{post.title}': {truncated_content}",
            sender_id=commenter.id,
            post_id=post.id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def create_follow_notification(
        db: Session,
        follower: User,
        followed_user: User
    ) -> Notification:
        """Create notification when someone follows a user"""
        notification = Notification(
            user_id=followed_user.id,
            type=NotificationType.FOLLOW,
            title="New Follower",
            message=f"{follower.username} started following you",
            sender_id=follower.id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def create_mention_notification(
        db: Session,
        mentioned_user: User,
        mentioner: User,
        post: Post,
        mention_text: str
    ) -> Notification:
        """Create notification when someone mentions a user in a comment"""
        notification = Notification(
            user_id=mentioned_user.id,
            type=NotificationType.MENTION,
            title="You were mentioned",
            message=f"{mentioner.username} mentioned you in a comment: {mention_text}",
            sender_id=mentioner.id,
            post_id=post.id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def create_trending_notification(
        db: Session,
        user: User,
        trending_posts: list
    ) -> Notification:
        """Create notification for trending items"""
        if not trending_posts:
            return None
        
        notification = Notification(
            user_id=user.id,
            type=NotificationType.TRENDING,
            title="Trending Items",
            message=f"Check out {len(trending_posts)} trending fashion items!",
            data={"post_ids": [post.id for post in trending_posts]}
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_notification_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_notifications_read(
        db: Session,
        user_id: int
    ) -> int:
        """Mark all notifications as read for a user"""
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        return result
    
    @staticmethod
    def get_unread_count(
        db: Session,
        user_id: int
    ) -> int:
        """Get count of unread notifications for a user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count() 