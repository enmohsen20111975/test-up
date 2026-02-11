#!/usr/bin/env python3
"""Test script to verify EngiSuite Analytics Pro installation"""

import sys
import os
import subprocess
import time

def test_python_version():
    print("📦 Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or later is required")
        return False
    
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def test_dependencies():
    print("\n📦 Checking dependencies...")
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy',
        'psycopg2-binary', 'python-jose', 'passlib',
        'python-multipart', 'pdfkit', 'python-dotenv',
        'openai', 'pandas', 'numpy', 'matplotlib',
        'seaborn', 'werkzeug', 'stripe'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing dependencies: {', '.join(missing_packages)}")
        print("💡 To install dependencies: pip install -r backend/requirements.txt")
        return False
    
    return True

def test_project_structure():
    print("\n📁 Checking project structure...")
    required_dirs = [
        'backend', 'frontend', 'frontend/shared/css', 'frontend/shared/js',
        'backend/ai', 'backend/ai/prompts', 'backend/analytics',
        'backend/auth', 'backend/calculators', 'backend/calculators/services'
    ]
    
    required_files = [
        'backend/main.py', 'backend/config.py', 'backend/database.py',
        'backend/requirements.txt', 'frontend/index.html',
        'frontend/dashboard.html', 'frontend/login.html',
        'frontend/register.html', 'frontend/calculators.html',
        'frontend/analytics.html', 'frontend/ai-assistant.html',
        'frontend/shared/css/engisuite-theme.css',
        'frontend/shared/js/auth.js', 'frontend/shared/js/ai-service.js',
        '.env', 'docker-compose.yml', 'README.md', 'start.sh', 'start.py'
    ]
    
    all_ok = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - Not found")
            all_ok = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Not found")
            all_ok = False
    
    return all_ok

def test_api_connection():
    print("\n🌐 Testing API connection...")
    try:
        import requests
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API not reachable: {e}")
        print("💡 Make sure the backend server is running")
        return False
    except ImportError:
        print("⚠️  requests library not installed - skipping API test")
        return False

def main():
    print("🚀 EngiSuite Analytics Pro Installation Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("API Connection", test_api_connection)
    ]
    
    results = []
    for name, test in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Error in {name} test: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {results.count(True)}")
    print(f"❌ Failed: {results.count(False)}")
    
    if all(results):
        print("\n🎉 Installation is complete and all tests passed!")
        print("\n📱 Frontend: http://localhost")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Installation incomplete. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())