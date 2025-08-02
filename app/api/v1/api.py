from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, posts, outfits, search, notifications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"]) 