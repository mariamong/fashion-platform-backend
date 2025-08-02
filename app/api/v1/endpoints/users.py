from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from app.core.database import get_db
from app.models.user import User, user_followers
from app.schemas.user import UserResponse, UserUpdate, UserProfile, UserList
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a user's profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user is following this user
    is_following = db.query(user_followers).filter(
        and_(
            user_followers.c.follower_id == current_user.id,
            user_followers.c.following_id == user_id
        )
    ).first() is not None
    
    # Get counts
    followers_count = db.query(user_followers).filter(
        user_followers.c.following_id == user_id
    ).count()
    
    following_count = db.query(user_followers).filter(
        user_followers.c.follower_id == user_id
    ).count()
    
    posts_count = db.query(user.posts).count()
    
    return UserProfile(
        **user.__dict__,
        followers_count=followers_count,
        following_count=following_count,
        posts_count=posts_count,
        is_following=is_following
    )


@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already following
    existing_follow = db.query(user_followers).filter(
        and_(
            user_followers.c.follower_id == current_user.id,
            user_followers.c.following_id == user_id
        )
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Create follow relationship
    db.execute(
        user_followers.insert().values(
            follower_id=current_user.id,
            following_id=user_id
        )
    )
    db.commit()
    
    return {"message": "Successfully followed user"}


@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    # Check if following
    existing_follow = db.query(user_followers).filter(
        and_(
            user_followers.c.follower_id == current_user.id,
            user_followers.c.following_id == user_id
        )
    ).first()
    
    if not existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    
    # Remove follow relationship
    db.execute(
        user_followers.delete().where(
            and_(
                user_followers.c.follower_id == current_user.id,
                user_followers.c.following_id == user_id
            )
        )
    )
    db.commit()
    
    return {"message": "Successfully unfollowed user"}


@router.get("/{user_id}/followers", response_model=UserList)
async def get_user_followers(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get a user's followers"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get followers
    followers = db.query(User).join(
        user_followers, User.id == user_followers.c.follower_id
    ).filter(
        user_followers.c.following_id == user_id
    ).offset((page - 1) * size).limit(size).all()
    
    total = db.query(user_followers).filter(
        user_followers.c.following_id == user_id
    ).count()
    
    return UserList(
        users=followers,
        total=total,
        page=page,
        size=size
    )


@router.get("/{user_id}/following", response_model=UserList)
async def get_user_following(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get users that a user is following"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get following
    following = db.query(User).join(
        user_followers, User.id == user_followers.c.following_id
    ).filter(
        user_followers.c.follower_id == user_id
    ).offset((page - 1) * size).limit(size).all()
    
    total = db.query(user_followers).filter(
        user_followers.c.follower_id == user_id
    ).count()
    
    return UserList(
        users=following,
        total=total,
        page=page,
        size=size
    ) 