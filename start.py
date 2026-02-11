#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import time

def main():
    print("Starting EngiSuite Analytics Pro...")
    
    # Check if Python is installed
    if sys.version_info < (3, 10):
        print("Python 3.10 or later is required")
        return
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print(".env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r", encoding="utf-8") as f_src:
                with open(".env", "w", encoding="utf-8") as f_dst:
                    f_dst.write(f_src.read())
            print("Please edit the .env file with your API keys before starting.")
        else:
            print(".env.example file not found")
            return
    
    # Start the application
    print("🔧 Starting backend server...")
    try:
        os.chdir("backend")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--reload", "--host", "127.0.0.1", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()