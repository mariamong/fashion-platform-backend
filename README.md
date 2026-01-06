# Fashion Platform Backend

A modern backend API for a fashion social platform where users can share their clothing items, reviews, and discover new styles.

## Current Status: MVP Implementation

This is a focused MVP (Minimum Viable Product) implementation with core features that are **fully functional**. The codebase prioritizes working, tested features over ambitious scope.

### Implemented Features (MVP)

- **User Authentication** - JWT-based authentication with register, login, and token refresh
- **User Profiles** - Get and update user profiles with follow/unfollow functionality
- **Posts** - Create, read, update, and delete clothing posts with image uploads
- **Likes** - Like and unlike posts
- **Comments** - Add comments to posts and view post comments
- **Image Upload** - Upload images for posts with validation

###  Planned Features (Not Yet Implemented)

The following features are planned but **not currently implemented**:
- Outfits (creating outfit combinations)
- Advanced search and filtering
- Trending items
- Personalized recommendations
- Real-time notifications
- Background task processing (Celery)

##  Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **JWT** - Token-based authentication
- **Pillow** - Image processing
- **Pydantic** - Data validation

##  Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd fashion-platform-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/fashion_db

# Security Configuration
# Generate a strong random secret key: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

### 3. Database Setup

Create a PostgreSQL database:

```bash
createdb fashion_db
```

Run migrations:

```bash
alembic upgrade head
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "fashionista",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Doe",
  "bio": "Fashion enthusiast"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "fashionista",
  "first_name": "Jane",
  "last_name": "Doe",
  "bio": "Fashion enthusiast",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Users

#### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

#### Update User Profile
```http
PUT /api/v1/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "bio": "Updated bio"
}
```

#### Get User Profile
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

#### Follow User
```http
POST /api/v1/users/{user_id}/follow
Authorization: Bearer <access_token>
```

#### Unfollow User
```http
DELETE /api/v1/users/{user_id}/follow
Authorization: Bearer <access_token>
```

### Posts

#### Get All Posts
```http
GET /api/v1/posts?page=1&size=20&category=tops&brand=nike
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `size` (int): Items per page (default: 20, max: 100)
- `category` (string, optional): Filter by category
- `brand` (string, optional): Filter by brand
- `min_price` (float, optional): Minimum price filter
- `max_price` (float, optional): Maximum price filter

#### Create Post
```http
POST /api/v1/posts
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

title: "Summer Dress"
description: "Beautiful summer dress"
category: "dresses"
brand: "Zara"
price: 49.99
main_image: <file>
tags: "summer,dress,casual"
```

**Form Fields:**
- `title` (required): Post title
- `description` (optional): Post description
- `category` (required): One of: tops, bottoms, dresses, outerwear, shoes, accessories, bags, jewelry, underwear, swimwear, active_wear, formal, casual, vintage, other
- `brand` (optional): Brand name
- `price` (optional): Price as float
- `purchase_link` (optional): Link to purchase
- `store_name` (optional): Store name
- `rating` (optional): Rating 1-5
- `review` (optional): Review text
- `is_public` (optional): Boolean (default: true)
- `main_image` (required): Image file
- `additional_images` (optional): Multiple image files
- `tags` (optional): Comma-separated tags or JSON array

#### Get Post
```http
GET /api/v1/posts/{post_id}
Authorization: Bearer <access_token>
```

#### Update Post
```http
PUT /api/v1/posts/{post_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

#### Delete Post
```http
DELETE /api/v1/posts/{post_id}
Authorization: Bearer <access_token>
```

#### Like Post
```http
POST /api/v1/posts/{post_id}/like
Authorization: Bearer <access_token>
```

#### Unlike Post
```http
DELETE /api/v1/posts/{post_id}/like
Authorization: Bearer <access_token>
```

#### Add Comment
```http
POST /api/v1/posts/{post_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Great outfit!"
}
```

#### Get Post Comments
```http
GET /api/v1/posts/{post_id}/comments?page=1&size=20
Authorization: Bearer <access_token>
```

##  Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

##  Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

##  Troubleshooting

### Database Connection Error

- Ensure PostgreSQL is running
- Check that `DATABASE_URL` in `.env` is correct
- Verify database exists: `psql -l | grep fashion_db`

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### File Upload Issues

- Ensure `uploads` directory exists (created automatically)
- Check file size limits (default: 10MB)
- Verify allowed file types: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

### Authentication Errors

- Verify `SECRET_KEY` is set in `.env`
- Check token expiration settings
- Ensure token is included in `Authorization` header: `Bearer <token>`

## 📁 Project Structure

```
fashion-platform-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database connection
│   │   └── security.py        # Authentication utilities
│   ├── models/                 # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── post.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── post.py
│   │   └── ...
│   ├── api/                    # API routes and endpoints
│   │   └── v1/
│   │       ├── api.py         # Main API router
│   │       └── endpoints/    # Individual endpoint modules
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── posts.py
│   ├── services/               # Business logic services
│   ├── utils/                  # Utility functions
│   │   └── file_upload.py     # File upload handling
│   └── tests/                  # Test files
├── alembic/                    # Database migrations
├── uploads/                    # Uploaded files (created automatically)
├── requirements.txt
├── alembic.ini
└── README.md
```

##  Security Notes

- **Never commit `.env` file** - It contains sensitive credentials
- Use strong, random `SECRET_KEY` in production
- Configure CORS properly for production (currently allows all origins)
- Implement rate limiting for production
- Use HTTPS in production
- Validate and sanitize all user inputs

##  License

MIT License - see LICENSE file for details

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request


