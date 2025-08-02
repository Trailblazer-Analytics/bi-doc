#!/usr/bin/env python3
"""Development environment setup script for BI Documentation Tool.

This script sets up the development environment by installing dependencies,
configuring pre-commit hooks, and running initial quality checks.

Usage:
    python scripts/setup_dev.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str, check: bool = True) -> bool:
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ {description} failed - command not found")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up BI Documentation Tool development environment")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # Set default branch to 'main' for this repository only
    subprocess.run(["git", "config", "--local", "init.defaultBranch", "main"], 
                  check=False, capture_output=True)
    
    steps = [
        # Install dependencies
        (
            ["python3", "-m", "pip", "install", "-e", ".[dev,test,docs]"],
            "Installing development dependencies"
        ),
        
        # Install pre-commit hooks
        (
            ["python3", "-m", "pre_commit", "install"],
            "Installing pre-commit hooks"
        ),
        
        # Update pre-commit hooks
        (
            ["python3", "-m", "pre_commit", "autoupdate"],
            "Updating pre-commit hooks"
        ),
        
        # Run initial formatting
        (
            ["python3", "scripts/format_code.py", "--fix"],
            "Running initial code formatting"
        ),
    ]
    
    success_count = 0
    for cmd, description in steps:
        if run_command(cmd, description, check=False):
            success_count += 1
    
    print("\n" + "=" * 60)
    if success_count == len(steps):
        print("✅ Development environment setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run 'python scripts/format_code.py --all' to verify setup")
        print("2. Run 'pytest' to execute the test suite")
        print("3. Make changes and commit - pre-commit hooks will run automatically")
        print("4. Use 'python scripts/format_code.py --fix' before committing")
    else:
        print(f"⚠️  Setup completed with {len(steps) - success_count} warnings")
        print("Some tools may not be available in this environment")
        print("The project can still be used, but some quality checks may be skipped")
    
    print("\n🔗 Useful commands:")
    print("  python scripts/format_code.py --check   # Check code quality")
    print("  python scripts/format_code.py --fix     # Format and fix issues")
    print("  python scripts/format_code.py --all     # Full quality check")
    print("  pytest                                   # Run tests")
    print("  pytest --cov=bidoc                      # Run tests with coverage")


if __name__ == "__main__":
    main()