"""
Setup and installation script for the Autonomous Learning Agent.
Automates the installation and configuration process.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is suitable."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def install_ollama():
    """Guide user through Ollama installation."""
    print("\n🦙 Ollama Installation")
    print("-" * 30)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Please install Ollama for Windows:")
        print("1. Go to https://ollama.com/download")
        print("2. Download Ollama for Windows")
        print("3. Run the installer")
        print("4. After installation, open Command Prompt and run:")
        print("   ollama pull llama3.1")
    
    elif system == "darwin":  # macOS
        print("Please install Ollama for macOS:")
        print("1. Go to https://ollama.com/download")
        print("2. Download Ollama for macOS") 
        print("3. Install the app")
        print("4. After installation, run in Terminal:")
        print("   ollama pull llama3.1")
    
    else:  # Linux
        print("Installing Ollama for Linux:")
        if run_command("curl -fsSL https://ollama.com/install.sh | sh", "Install Ollama"):
            print("Pulling llama3.1 model...")
            run_command("ollama pull llama3.1", "Pull Llama 3.1 model")
    
    print("\nPress Enter after completing Ollama installation...")
    input()


def test_ollama():
    """Test if Ollama is installed and working."""
    print("\n🧪 Testing Ollama installation...")
    
    # Test if ollama command exists
    if not run_command("ollama --version", "Check Ollama version"):
        print("⚠️  Ollama doesn't seem to be installed or in PATH")
        return False
    
    # Test if service is running
    if not run_command("ollama list", "List available models"):
        print("⚠️  Ollama service might not be running")
        print("Try running: ollama serve")
        return False
    
    print("✅ Ollama is installed and running")
    return True


def install_python_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrade pip")
    
    # Install requirements
    if Path("requirements.txt").exists():
        success = run_command(f"{sys.executable} -m pip install -r requirements.txt", "Install requirements")
        if not success:
            print("⚠️  Some packages failed to install. This might be normal.")
            print("The system should still work with most packages installed.")
    else:
        print("❌ requirements.txt not found")
        return False
    
    return True


def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    directories = [
        "data/chroma_db",
        "data/user_notes", 
        "tests/results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")


def create_environment_file():
    """Create .env file if it doesn't exist."""
    print("\n⚙️  Setting up environment configuration...")
    
    if not Path(".env").exists():
        print("❌ .env file not found")
        print("This should have been created during setup. Please check the installation.")
        return False
    
    print("✅ Environment configuration found")
    return True


def run_initial_test():
    """Run initial system test."""
    print("\n🎯 Running initial system test...")
    
    success = run_command(f"{sys.executable} app.py --action test-llm", "Test LLM connection")
    
    if success:
        print("✅ System test passed!")
        return True
    else:
        print("⚠️  System test failed. Check the logs for details.")
        return False


def main():
    """Main setup function."""
    print("🎓 Autonomous Learning Agent - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        return
    
    # Setup directories
    setup_directories()
    
    # Check environment file
    if not create_environment_file():
        return
    
    # Install Ollama
    install_ollama()
    
    # Test Ollama
    if not test_ollama():
        print("\n⚠️  Ollama installation incomplete.")
        print("Please complete Ollama installation and try running the test manually:")
        print("python app.py --action test-llm")
        return
    
    # Run initial test
    if run_initial_test():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Test individual checkpoints:")
        print("   python app.py --action quick-test --checkpoint 'Python Variables and Data Types'")
        print("\n2. Run full evaluation:")
        print("   python app.py --action evaluate")
        print("\n3. List available checkpoints:")
        print("   python app.py --action list-checkpoints")
    else:
        print("\n⚠️  Setup completed with warnings.")
        print("Some components may need manual configuration.")


if __name__ == "__main__":
    main()