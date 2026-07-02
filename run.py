"""
Starts both the FastAPI backend and the Streamlit frontend together.

Usage:
    python run.py
"""
import subprocess
import sys
import os
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def main():
    print("Starting AI Lead Management System...\n")

    # Start FastAPI backend
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=BACKEND_DIR,
    )
    print("Backend starting at http://localhost:8000 (docs at /docs)")

    # Give the backend a moment to start before frontend tries to call it
    time.sleep(3)

    # Start Streamlit frontend
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "Home.py"],
        cwd=FRONTEND_DIR,
    )
    print("Frontend starting at http://localhost:8501\n")

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()


if __name__ == "__main__":
    main()
