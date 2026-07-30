"""
StreamGuard AI - Development Server Launcher
"""
import os
import sys

# Force UTF-8 encoding for standard streams and child processes
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Force sys.executable to be the virtual environment's python.exe so uvicorn reloader spawns child processes using the correct python environment/version.
sys.executable = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe"))

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
