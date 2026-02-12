import subprocess
import sys
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(script_dir, "requirements.txt")

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    print("Dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing dependencies: {e}")
    sys.exit(1)
