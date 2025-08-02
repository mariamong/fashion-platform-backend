import requests
import json

# Test the API endpoints
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health check: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
        return False

def test_docs():
    """Test the docs endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Docs endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing docs endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing Fashion Platform API...")
    print("=" * 50)
    
    health_ok = test_health_check()
    root_ok = test_root()
    docs_ok = test_docs()
    
    print("=" * 50)
    if health_ok and root_ok and docs_ok:
        print("✅ All tests passed! API is running correctly.")
        print(f"📚 API Documentation: {BASE_URL}/docs")
        print(f"🔗 Alternative Docs: {BASE_URL}/redoc")
    else:
        print("❌ Some tests failed. Check if the server is running.")
        print("To start the server, run: python run.py") 