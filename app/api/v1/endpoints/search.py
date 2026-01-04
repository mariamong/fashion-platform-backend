from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_, or_, func, desc

from app.core.database import get_db
from app.models.user import User, user_followers
from app.models.post import Post, Tag, PostTag, Like
from app.models.outfit import Outfit
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/posts", response_model=List[dict])
async def search_posts(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search posts by query and filters"""
    query = db.query(Post).filter(Post.is_public == True)
    
    # Apply search query
    if q:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{q}%"),
                Post.description.ilike(f"%{q}%"),
                Post.brand.ilike(f"%{q}%"),
                Post.store_name.ilike(f"%{q}%")
            )
        )
    
    # Apply filters
    if category:
        query = query.filter(Post.category == category)
    if brand:
        query = query.filter(Post.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Post.price >= min_price)
    if max_price is not None:
        query = query.filter(Post.price <= max_price)
    
    # Get total count
    total = query.count()
    
    # Paginate and order by relevance (likes + views)
    posts = query.order_by(
        desc(Post.like_count + Post.view_count)
    ).offset((page - 1) * size).limit(size).all()
    
    # Format response
    post_responses = []
    for post in posts:
        post_dict = post.__dict__.copy()
        post_dict['author'] = {
            'id': post.author.id,
            'username': post.author.username,
            'profile_picture': post.author.profile_picture
        }
        
        # Get tags
        tags = [tag.tag.name for tag in post.tags]
        post_dict['tags'] = tags
        
        post_responses.append(post_dict)
    
    return {
        "posts": post_responses,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/users", response_model=List[dict])
async def search_users(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search users by username, first name, or last name"""
    query = db.query(User).filter(User.is_active == True)
    
    # Apply search query
    if q:
        query = query.filter(
            or_(
                User.username.ilike(f"%{q}%"),
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%")
            )
        )
    
    # Get total count
    total = query.count()
    
    # Paginate and order by username
    users = query.order_by(User.username).offset((page - 1) * size).limit(size).all()
    
    # Format response
    user_responses = []
    for user in users:
        user_dict = user.__dict__.copy()
        # Remove sensitive information
        user_dict.pop('hashed_password', None)
        user_responses.append(user_dict)
    
    return {
        "users": user_responses,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/trending", response_model=List[dict])
async def get_trending_items(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trending posts based on likes and views"""
    # Get trending posts (high engagement in last 7 days)
    trending_posts = db.query(Post).filter(
        and_(
            Post.is_public == True,
            Post.created_at >= func.date(func.now() - func.interval('7 days'))
        )
    ).order_by(
        desc(Post.like_count + Post.view_count)
    ).offset((page - 1) * size).limit(size).all()
    
    # Format response
    post_responses = []
    for post in trending_posts:
        post_dict = post.__dict__.copy()
        post_dict['author'] = {
            'id': post.author.id,
            'username': post.author.username,
            'profile_picture': post.author.profile_picture
        }
        
        # Get tags
        tags = [tag.tag.name for tag in post.tags]
        post_dict['tags'] = tags
        
        post_responses.append(post_dict)
    
    return {
        "posts": post_responses,
        "page": page,
        "size": size
    }


@router.get("/recommendations", response_model=List[dict])
async def get_recommendations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations based on user's likes and follows"""
    # Get posts from users that the current user follows
    following_posts = db.query(Post).join(
        User, Post.author_id == User.id
    ).join(
        user_followers, User.id == user_followers.c.following_id
    ).filter(
        and_(
            Post.is_public == True,
            user_followers.c.follower_id == current_user.id
        )
    ).order_by(desc(Post.created_at)).limit(size // 2).all()
    
    # Get posts with similar tags to what the user has liked
    liked_posts = db.query(Post).join(
        Like, Post.id == Like.post_id
    ).filter(Like.user_id == current_user.id).all()
    
    # Get tags from liked posts
    liked_tags = set()
    for post in liked_posts:
        for tag in post.tags:
            liked_tags.add(tag.tag.name)
    
    # Get posts with similar tags
    similar_posts = []
    if liked_tags:
        similar_posts = db.query(Post).join(
            PostTag, Post.id == PostTag.post_id
        ).join(
            Tag, PostTag.tag_id == Tag.id
        ).filter(
            and_(
                Post.is_public == True,
                Post.author_id != current_user.id,
                Tag.name.in_(list(liked_tags))
            )
        ).order_by(desc(Post.created_at)).limit(size // 2).all()
    
    # Combine and deduplicate
    all_posts = list(set(following_posts + similar_posts))
    all_posts.sort(key=lambda x: x.created_at, reverse=True)
    
    # Paginate
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_posts = all_posts[start_idx:end_idx]
    
    # Format response
    post_responses = []
    for post in paginated_posts:
        post_dict = post.__dict__.copy()
        post_dict['author'] = {
            'id': post.author.id,
            'username': post.author.username,
            'profile_picture': post.author.profile_picture
        }
        
        # Get tags
        tags = [tag.tag.name for tag in post.tags]
        post_dict['tags'] = tags
        
        post_responses.append(post_dict)
    
    return {
        "posts": post_responses,
        "page": page,
        "size": size
    }


@router.get("/tags", response_model=List[dict])
async def search_tags(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search tags"""
    query = db.query(Tag)
    
    # Apply search query
    if q:
        query = query.filter(Tag.name.ilike(f"%{q}%"))
    
    # Get total count
    total = query.count()
    
    # Paginate and order by name
    tags = query.order_by(Tag.name).offset((page - 1) * size).limit(size).all()
    
    # Format response
    tag_responses = []
    for tag in tags:
        tag_dict = tag.__dict__.copy()
        tag_responses.append(tag_dict)
    
    return {
        "tags": tag_responses,
        "total": total,
        "page": page,
        "size": size
    } 