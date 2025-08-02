from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from app.core.database import get_db
from app.models.user import User
from app.models.outfit import Outfit, OutfitItem, OutfitLike
from app.models.post import Post
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_outfits(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all public outfits"""
    outfits = db.query(Outfit).filter(Outfit.is_public == True).order_by(
        Outfit.created_at.desc()
    ).offset((page - 1) * size).limit(size).all()
    
    outfit_responses = []
    for outfit in outfits:
        outfit_dict = outfit.__dict__.copy()
        outfit_dict['creator'] = {
            'id': outfit.creator.id,
            'username': outfit.creator.username,
            'profile_picture': outfit.creator.profile_picture
        }
        
        # Get outfit items
        items = []
        for item in outfit.items:
            item_dict = item.__dict__.copy()
            item_dict['post'] = {
                'id': item.post.id,
                'title': item.post.title,
                'main_image': item.post.main_image,
                'brand': item.post.brand
            }
            items.append(item_dict)
        
        outfit_dict['items'] = items
        outfit_responses.append(outfit_dict)
    
    return outfit_responses


@router.post("/", response_model=dict)
async def create_outfit(
    name: str,
    description: Optional[str] = None,
    is_public: bool = True,
    item_ids: List[int] = [],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new outfit"""
    # Validate that all posts exist and belong to the user
    posts = []
    for post_id in item_ids:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {post_id} not found"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Post {post_id} does not belong to you"
            )
        posts.append(post)
    
    # Create outfit
    outfit = Outfit(
        name=name,
        description=description,
        is_public=is_public,
        creator_id=current_user.id
    )
    
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    
    # Add outfit items
    for i, post in enumerate(posts):
        outfit_item = OutfitItem(
            outfit_id=outfit.id,
            post_id=post.id,
            position=i
        )
        db.add(outfit_item)
    
    db.commit()
    
    return {
        "id": outfit.id,
        "name": outfit.name,
        "description": outfit.description,
        "is_public": outfit.is_public,
        "creator_id": outfit.creator_id,
        "created_at": outfit.created_at
    }


@router.get("/{outfit_id}", response_model=dict)
async def get_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific outfit"""
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    if not outfit.is_public and outfit.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this outfit"
        )
    
    # Increment view count
    outfit.view_count += 1
    db.commit()
    
    outfit_dict = outfit.__dict__.copy()
    outfit_dict['creator'] = {
        'id': outfit.creator.id,
        'username': outfit.creator.username,
        'profile_picture': outfit.creator.profile_picture
    }
    
    # Get outfit items
    items = []
    for item in outfit.items:
        item_dict = item.__dict__.copy()
        item_dict['post'] = {
            'id': item.post.id,
            'title': item.post.title,
            'main_image': item.post.main_image,
            'brand': item.post.brand,
            'price': item.post.price
        }
        items.append(item_dict)
    
    outfit_dict['items'] = items
    
    return outfit_dict


@router.put("/{outfit_id}", response_model=dict)
async def update_outfit(
    outfit_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an outfit"""
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    if outfit.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this outfit"
        )
    
    # Update fields
    if name is not None:
        outfit.name = name
    if description is not None:
        outfit.description = description
    if is_public is not None:
        outfit.is_public = is_public
    
    db.commit()
    db.refresh(outfit)
    
    return {
        "id": outfit.id,
        "name": outfit.name,
        "description": outfit.description,
        "is_public": outfit.is_public,
        "creator_id": outfit.creator_id,
        "updated_at": outfit.updated_at
    }


@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an outfit"""
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    if outfit.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this outfit"
        )
    
    db.delete(outfit)
    db.commit()
    
    return {"message": "Outfit deleted successfully"}


@router.post("/{outfit_id}/like")
async def like_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like an outfit"""
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    # Check if already liked
    existing_like = db.query(OutfitLike).filter(
        and_(OutfitLike.user_id == current_user.id, OutfitLike.outfit_id == outfit_id)
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this outfit"
        )
    
    # Create like
    like = OutfitLike(user_id=current_user.id, outfit_id=outfit_id)
    db.add(like)
    
    # Update outfit like count
    outfit.like_count += 1
    
    db.commit()
    
    return {"message": "Outfit liked successfully"}


@router.delete("/{outfit_id}/like")
async def unlike_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike an outfit"""
    like = db.query(OutfitLike).filter(
        and_(OutfitLike.user_id == current_user.id, OutfitLike.outfit_id == outfit_id)
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not liked this outfit"
        )
    
    # Remove like
    db.delete(like)
    
    # Update outfit like count
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if outfit:
        outfit.like_count = max(0, outfit.like_count - 1)
    
    db.commit()
    
    return {"message": "Outfit unliked successfully"} 