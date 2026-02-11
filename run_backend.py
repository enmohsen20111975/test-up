import subprocess
import sys
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, "backend")

try:
    # Ensure uvicorn is installed (this is a fallback, should ideally be installed via requirements.txt)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn"])
    
    # Run uvicorn from the backend directory
    print(f"Starting uvicorn server from: {backend_dir}")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=backend_dir  # Set current working directory for uvicorn
    )
except subprocess.CalledProcessError as e:
    print(f"Error running backend: {e}")
    sys.exit(1)
except FileNotFoundError:
    print("Error: Python executable not found. Ensure Python is installed and in your PATH.")
    sys.exit(1)
