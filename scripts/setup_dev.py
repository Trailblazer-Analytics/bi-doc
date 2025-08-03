#!/usr/bin/env python3
"""Development environment setup script for BI Documentation Tool"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description="", check=True):
    """Run a shell command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False


def check_python_version():
    """Check if Python version is supported"""
    version = sys.version_info
    if version < (3, 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please use Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
    return True


def setup_virtual_environment():
    """Setup Python virtual environment"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    return run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment")


def install_dependencies():
    """Install project dependencies"""
    pip_cmd = ".venv/bin/pip" if os.name != "nt" else ".venv\\Scripts\\pip.exe"
    
    commands = [
        f"{pip_cmd} install --upgrade pip setuptools wheel",
        f"{pip_cmd} install -r requirements.txt",
        f"{pip_cmd} install -r requirements-dev.txt",
        f"{pip_cmd} install -e .",
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd.split()[-1]}"):
            return False
    
    return True


def setup_pre_commit():
    """Setup pre-commit hooks"""
    if not Path(".pre-commit-config.yaml").exists():
        print("⚠️  No pre-commit config found, skipping pre-commit setup")
        return True
    
    activate_cmd = "source .venv/bin/activate" if os.name != "nt" else ".venv\\Scripts\\activate.bat"
    return run_command(f"{activate_cmd} && pre-commit install", "Setting up pre-commit hooks")


def verify_installation():
    """Verify the installation works"""
    python_cmd = ".venv/bin/python" if os.name != "nt" else ".venv\\Scripts\\python.exe"
    
    tests = [
        (f"{python_cmd} -c 'import bidoc; print(\"✅ bidoc module imports successfully\")'", "Testing bidoc import"),
        (f"{python_cmd} -m pytest tests/ -v --tb=short", "Running test suite"),
        (f"{python_cmd} -m bidoc --help", "Testing CLI functionality"),
    ]
    
    for cmd, desc in tests:
        if not run_command(cmd, desc, check=False):
            print(f"⚠️  {desc} failed, but continuing...")
    
    return True


def main():
    """Main setup function"""
    print("🚀 Setting up BI Documentation Tool development environment\n")
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up pre-commit hooks", setup_pre_commit),
        ("Verifying installation", verify_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            return 1
    
    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name != "nt":
        print("   source .venv/bin/activate")
    else:
        print("   .venv\\Scripts\\activate.bat")
    print("2. Run tests: python -m pytest tests/")
    print("3. Run the tool: python -m bidoc --help")
    print("4. Start developing! 🎯")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())