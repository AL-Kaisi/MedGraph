#!/usr/bin/env python
"""Setup script for MedGraph application."""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_env():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    pip_path = Path("venv/bin/pip") if os.name != 'nt' else Path("venv/Scripts/pip")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    print("✓ Dependencies installed")

def setup_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("✓ .env file created")
        print("⚠️  Please update .env with your Neo4j credentials")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠️  .env.example not found")

def main():
    """Main setup function."""
    print("MedGraph Setup")
    print("=" * 40)
    
    check_python_version()
    create_virtual_env()
    install_dependencies()
    setup_env_file()
    
    print("\n" + "=" * 40)
    print("Setup complete! 🎉")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name != 'nt':
        print("   source venv/bin/activate")
    else:
        print("   venv\\Scripts\\activate")
    print("2. Update .env with your Neo4j credentials")
    print("3. Run the application:")
    print("   python app/gradio_app.py")

if __name__ == "__main__":
    main()