# Fashion Platform Backend

A modern backend API for a fashion social platform where users can share their clothing items, reviews, and discover new styles.

## Features

### Core Features
- **User Authentication & Profiles** - Secure JWT-based authentication with user profiles
- **Clothing Posts** - Upload clothing items with photos, descriptions, and purchase links
- **Reviews & Ratings** - Personal reviews and ratings for clothing items
- **Social Features** - Follow users, like posts, and comment on items
- **Search & Discovery** - Advanced search by brand, style, price range, and preferences
- **Outfit Inspiration** - Create and share outfit combinations
- **Brand & Store Integration** - Track favorite brands and stores
- **Fashion Trends** - Trending items and styles based on user engagement
- **Notifications** - Real-time notifications for social interactions

### Technical Features
- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Robust relational database
- **Redis** - Caching and session management
- **Celery** - Background task processing
- **JWT Authentication** - Secure token-based authentication
- **File Upload** - Image upload and processing
- **Search Engine** - Full-text search capabilities
- **Real-time Updates** - WebSocket support for live updates

## Project Structure

```
fashion_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and utilities
│   ├── models/                 # SQLAlchemy database models
│   ├── schemas/                # Pydantic schemas for request/response
│   ├── api/                    # API routes and endpoints
│   ├── services/               # Business logic services
│   ├── utils/                  # Utility functions
│   └── tests/                  # Test files
├── alembic/                    # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd fashion_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis credentials
   ```

3. **Database Setup**
   ```bash
   alembic upgrade head
   ```

4. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `GET /users/{user_id}` - Get user profile
- `GET /users/{user_id}/posts` - Get user's posts
- `POST /users/{user_id}/follow` - Follow user
- `DELETE /users/{user_id}/follow` - Unfollow user

### Posts
- `GET /posts` - Get all posts with filters
- `POST /posts` - Create new post
- `GET /posts/{post_id}` - Get specific post
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post
- `POST /posts/{post_id}/like` - Like post
- `DELETE /posts/{post_id}/like` - Unlike post
- `POST /posts/{post_id}/comments` - Add comment
- `GET /posts/{post_id}/comments` - Get post comments

### Search & Discovery
- `GET /search/posts` - Search posts
- `GET /search/users` - Search users
- `GET /trending` - Get trending items
- `GET /recommendations` - Get personalized recommendations

### Outfits
- `GET /outfits` - Get all outfits
- `POST /outfits` - Create new outfit
- `GET /outfits/{outfit_id}` - Get specific outfit
- `PUT /outfits/{outfit_id}` - Update outfit
- `DELETE /outfits/{outfit_id}` - Delete outfit

### Notifications
- `GET /notifications` - Get user notifications
- `PUT /notifications/{notification_id}/read` - Mark notification as read
- `DELETE /notifications/{notification_id}` - Delete notification

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/fashion_db

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting
```bash
black app/
isort app/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details 