from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post, Comment, Like, Tag, PostTag, ClothingCategory
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostList, CommentCreate, CommentResponse, CommentList
from app.api.v1.endpoints.auth import get_current_active_user
from app.utils.file_upload import save_upload_file
import json

router = APIRouter()


@router.get("/", response_model=PostList)
async def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts with filters"""
    query = db.query(Post).filter(Post.is_public == True)
    
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
    
    # Paginate
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    # Add author info and check if liked
    post_responses = []
    for post in posts:
        post_dict = post.__dict__.copy()
        post_dict['author'] = {
            'id': post.author.id,
            'username': post.author.username,
            'profile_picture': post.author.profile_picture
        }
        
        # Check if current user liked this post
        is_liked = db.query(Like).filter(
            and_(Like.user_id == current_user.id, Like.post_id == post.id)
        ).first() is not None
        post_dict['is_liked'] = is_liked
        
        # Get tags
        tags = [tag.tag.name for tag in post.tags]
        post_dict['tags'] = tags
        
        # Parse additional_images JSON string
        if post.additional_images:
            try:
                post_dict['additional_images'] = json.loads(post.additional_images)
            except:
                post_dict['additional_images'] = []
        else:
            post_dict['additional_images'] = []
        
        post_responses.append(PostResponse(**post_dict))
    
    return PostList(
        posts=post_responses,
        total=total,
        page=page,
        size=size
    )


@router.post("/", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: ClothingCategory = Form(...),
    brand: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    purchase_link: Optional[str] = Form(None),
    store_name: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    review: Optional[str] = Form(None),
    is_public: bool = Form(True),
    tags: Optional[str] = Form(None),  # JSON string or comma-separated
    main_image: UploadFile = File(...),
    additional_images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post with image upload"""
    # Save main image
    main_image_path = save_upload_file(main_image, folder="posts")
    
    # Save additional images if provided
    additional_image_paths = []
    if additional_images:
        for img in additional_images:
            img_path = save_upload_file(img, folder="posts")
            additional_image_paths.append(img_path)
    
    # Parse tags
    tag_list = []
    if tags:
        try:
            # Try parsing as JSON first
            tag_list = json.loads(tags)
        except:
            # If not JSON, treat as comma-separated
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Create post
    db_post = Post(
        title=title,
        description=description,
        category=category,
        brand=brand,
        price=price,
        purchase_link=purchase_link,
        store_name=store_name,
        rating=rating,
        review=review,
        is_public=is_public,
        main_image=main_image_path,
        additional_images=json.dumps(additional_image_paths) if additional_image_paths else None,
        author_id=current_user.id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Add tags if provided
    if tag_list:
        for tag_name in tag_list:
            # Get or create tag
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            # Create post-tag relationship
            post_tag = PostTag(post_id=db_post.id, tag_id=tag.id)
            db.add(post_tag)
    
    db.commit()
    db.refresh(db_post)
    
    # Return response with author info
    post_dict = db_post.__dict__.copy()
    post_dict['author'] = {
        'id': db_post.author.id,
        'username': db_post.author.username,
        'profile_picture': db_post.author.profile_picture
    }
    post_dict['tags'] = tag_list
    post_dict['is_liked'] = False
    # Parse additional_images JSON string
    if db_post.additional_images:
        post_dict['additional_images'] = json.loads(db_post.additional_images)
    else:
        post_dict['additional_images'] = []
    
    return PostResponse(**post_dict)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Increment view count
    post.view_count += 1
    db.commit()
    
    # Return response with author info
    post_dict = post.__dict__.copy()
    post_dict['author'] = {
        'id': post.author.id,
        'username': post.author.username,
        'profile_picture': post.author.profile_picture
    }
    
    # Check if current user liked this post
    is_liked = db.query(Like).filter(
        and_(Like.user_id == current_user.id, Like.post_id == post.id)
    ).first() is not None
    post_dict['is_liked'] = is_liked
    
    # Get tags
    tags = [tag.tag.name for tag in post.tags]
    post_dict['tags'] = tags
    
    # Parse additional_images JSON string
    if post.additional_images:
        try:
            post_dict['additional_images'] = json.loads(post.additional_images)
        except:
            post_dict['additional_images'] = []
    else:
        post_dict['additional_images'] = []
    
    return PostResponse(**post_dict)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Update fields
    update_data = post_update.dict(exclude_unset=True)
    if 'additional_images' in update_data:
        update_data['additional_images'] = json.dumps(update_data['additional_images'])
    
    for field, value in update_data.items():
        if field != 'tags':
            setattr(post, field, value)
    
    # Update tags if provided
    if post_update.tags is not None:
        # Remove existing tags
        db.query(PostTag).filter(PostTag.post_id == post_id).delete()
        
        # Add new tags
        for tag_name in post_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            post_tag = PostTag(post_id=post_id, tag_id=tag.id)
            db.add(post_tag)
    
    db.commit()
    db.refresh(post)
    
    # Return response
    post_dict = post.__dict__.copy()
    post_dict['author'] = {
        'id': post.author.id,
        'username': post.author.username,
        'profile_picture': post.author.profile_picture
    }
    post_dict['tags'] = post_update.tags or []
    post_dict['is_liked'] = False
    
    # Parse additional_images JSON string
    if post.additional_images:
        try:
            post_dict['additional_images'] = json.loads(post.additional_images)
        except:
            post_dict['additional_images'] = []
    else:
        post_dict['additional_images'] = []
    
    return PostResponse(**post_dict)


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        and_(Like.user_id == current_user.id, Like.post_id == post_id)
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this post"
        )
    
    # Create like
    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    
    # Update post like count
    post.like_count += 1
    
    db.commit()
    
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    like = db.query(Like).filter(
        and_(Like.user_id == current_user.id, Like.post_id == post_id)
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not liked this post"
        )
    
    # Remove like
    db.delete(like)
    
    # Update post like count
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.like_count = max(0, post.like_count - 1)
    
    db.commit()
    
    return {"message": "Post unliked successfully"}


@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        post_id=post_id
    )
    
    db.add(comment)
    
    # Update post comment count
    post.comment_count += 1
    
    db.commit()
    db.refresh(comment)
    
    # Return response with author info
    comment_dict = comment.__dict__.copy()
    comment_dict['author'] = {
        'id': comment.author.id,
        'username': comment.author.username,
        'profile_picture': comment.author.profile_picture
    }
    
    return CommentResponse(**comment_dict)


@router.get("/{post_id}/comments", response_model=CommentList)
async def get_post_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get comments for a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get comments
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(
        Comment.created_at.desc()
    ).offset((page - 1) * size).limit(size).all()
    
    total = db.query(Comment).filter(Comment.post_id == post_id).count()
    
    # Add author info
    comment_responses = []
    for comment in comments:
        comment_dict = comment.__dict__.copy()
        comment_dict['author'] = {
            'id': comment.author.id,
            'username': comment.author.username,
            'profile_picture': comment.author.profile_picture
        }
        comment_responses.append(CommentResponse(**comment_dict))
    
    return CommentList(
        comments=comment_responses,
        total=total,
        page=page,
        size=size
    ) 