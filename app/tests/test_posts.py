import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.post import Post
from app.core.security import get_password_hash


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user and return auth token"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Register user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    return {"token": token, "user_data": user_data}


def test_get_posts_requires_auth():
    """Test that getting posts requires authentication"""
    response = client.get("/api/v1/posts")
    assert response.status_code == 401


def test_get_posts_with_auth(test_user):
    """Test getting posts with authentication"""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/api/v1/posts", headers=headers)
    assert response.status_code == 200
    assert "posts" in response.json()
    assert "total" in response.json()


def test_create_post_requires_auth():
    """Test that creating a post requires authentication"""
    response = client.post("/api/v1/posts")
    assert response.status_code == 401


def test_get_user_profile(test_user):
    """Test getting current user profile"""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["user_data"]["email"]
    assert data["username"] == test_user["user_data"]["username"]


def test_update_user_profile(test_user):
    """Test updating user profile"""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "bio": "Updated bio"
    }
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["bio"] == "Updated bio"

