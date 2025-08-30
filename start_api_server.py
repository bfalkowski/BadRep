#!/usr/bin/env python3
"""
Startup script for ReviewLab API Server.

This script launches the FastAPI server with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install -r requirements_api.txt")
        return False

def create_directories():
    """Create necessary directories for the API server."""
    directories = [
        "reports/injection_sessions",
        "reports/evaluation_results",
        "reports/archives"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def start_server():
    """Start the API server."""
    print("🚀 Starting ReviewLab API Server...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    print()
    print("🌐 Server Configuration:")
    print("   Host: 0.0.0.0")
    print("   Port: 8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print()
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "core.api_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("ReviewLab API Server Launcher")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not Path("core/api_server.py").exists():
        print("❌ Error: core/api_server.py not found")
        print("   Make sure you're running this from the project root")
        sys.exit(1)
    
    # Start the server
    success = start_server()
    
    if not success:
        print("\n❌ Failed to start server")
        sys.exit(1)
