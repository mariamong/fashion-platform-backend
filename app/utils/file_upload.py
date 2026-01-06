import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

from app.core.config import settings


def save_upload_file(upload_file: UploadFile, folder: str = "uploads") -> str:
    """Save uploaded file and return the file path"""
    
    # Validate file type
    if not is_valid_image(upload_file):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    # Create folder if it doesn't exist
    upload_folder = os.path.join(settings.UPLOAD_DIR, folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename
    file_extension = get_file_extension(upload_file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save file and check size
    try:
        content = upload_file.file.read()
        # Validate file size after reading
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Return relative path for database storage (matches StaticFiles mount)
    return f"/uploads/{folder}/{unique_filename}"


def is_valid_image(upload_file: UploadFile) -> bool:
    """Check if uploaded file is a valid image"""
    if not upload_file.filename:
        return False
    
    file_extension = get_file_extension(upload_file.filename).lower()
    return file_extension in settings.ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1]


def resize_image(image_path: str, max_size: tuple = (800, 800)) -> None:
    """Resize image to specified dimensions"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error resizing image {image_path}: {str(e)}")


def delete_file(file_path: str) -> bool:
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False


def get_file_url(file_path: str) -> str:
    """Get full URL for file"""
    if file_path.startswith('/'):
        return f"http://localhost:8000{file_path}"
    return f"http://localhost:8000/{file_path}" 