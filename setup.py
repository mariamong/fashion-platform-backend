#!/usr/bin/env python3
"""
Setup script for Fashion Platform Backend
This script helps set up the initial project configuration
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_env_file():
    """Create .env file from template"""
    env_content = """# Database
DATABASE_URL=postgresql://user:password@localhost/fashion_db

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
APP_NAME=Fashion Platform API
APP_VERSION=1.0.0
DEBUG=True
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")


def create_uploads_directory():
    """Create uploads directory"""
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print("✅ Created uploads directory")


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def install_dependencies():
    """Install project dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")


def run_tests():
    """Run project tests"""
    return run_command("python -m pytest app/tests/ -v", "Running tests")


def main():
    """Main setup function"""
    print("🚀 Setting up Fashion Platform Backend...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create necessary directories and files
    create_env_file()
    create_uploads_directory()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Run tests
    print("\n🧪 Running tests...")
    if run_tests():
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed, but setup can continue")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Set up PostgreSQL database")
    print("3. Run: python run.py")
    print("4. Visit: http://localhost:8000/docs")
    print("\n📚 Documentation: README.md")


if __name__ == "__main__":
    main() 