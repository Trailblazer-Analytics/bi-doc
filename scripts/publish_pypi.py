#!/usr/bin/env python3
"""
PyPI Publishing Script for BI Documentation Tool

This script automates the publishing process to PyPI with validation,
testing, and deployment steps.

Usage:
    python scripts/publish_pypi.py --test      # Publish to TestPyPI
    python scripts/publish_pypi.py --prod      # Publish to PyPI
    python scripts/publish_pypi.py --check     # Validate package only
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )

def run_command(command, check=True, capture_output=False):
    """Run a shell command with error handling"""
    logger.info(f"Running: {command}")
    result = subprocess.run(
        command,
        shell=True,
        check=check,
        capture_output=capture_output,
        text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result

def validate_environment():
    """Validate the publishing environment"""
    logger.info("Validating environment...")
    
    # Check if we're in the right directory
    if not Path("setup.py").exists() or not Path("bidoc").exists():
        logger.error("Must run from project root directory")
        sys.exit(1)
    
    # Check required tools
    required_tools = ["python", "pip", "twine"]
    for tool in required_tools:
        try:
            run_command(f"{tool} --version", capture_output=True)
        except subprocess.CalledProcessError:
            logger.error(f"Required tool not found: {tool}")
            sys.exit(1)
    
    logger.info("✅ Environment validation passed")

def clean_build_artifacts():
    """Clean up build artifacts from previous runs"""
    logger.info("Cleaning build artifacts...")
    
    artifacts = ["build/", "dist/", "*.egg-info/"]
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                logger.info(f"Removed: {path}")
    
    logger.info("✅ Build artifacts cleaned")

def run_tests():
    """Run the test suite"""
    logger.info("Running test suite...")
    
    try:
        result = run_command("python -m pytest tests/ -v --tb=short", check=False)
        if result.returncode != 0:
            logger.warning("Some tests failed, but continuing with publish")
        else:
            logger.info("✅ All tests passed")
    except Exception as e:
        logger.warning(f"Could not run tests: {e}")

def validate_package():
    """Validate the package structure and metadata"""
    logger.info("Validating package...")
    
    # Check setup.py syntax
    try:
        run_command("python setup.py check", capture_output=True)
        logger.info("✅ setup.py syntax is valid")
    except subprocess.CalledProcessError as e:
        logger.error(f"setup.py validation failed: {e}")
        sys.exit(1)
    
    # Check that required files exist
    required_files = [
        "README.md",
        "LICENSE",
        "bidoc/__init__.py",
        "bidoc/cli.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"Required file missing: {file}")
            sys.exit(1)
    
    logger.info("✅ Package validation passed")

def build_package():
    """Build the distribution packages"""
    logger.info("Building distribution packages...")
    
    # Build source and wheel distributions
    run_command("python setup.py sdist bdist_wheel")
    
    # Validate the built packages
    try:
        run_command("twine check dist/*")
        logger.info("✅ Package build completed and validated")
    except subprocess.CalledProcessError as e:
        logger.error(f"Package validation failed: {e}")
        sys.exit(1)

def publish_to_test_pypi():
    """Publish to TestPyPI for testing"""
    logger.info("Publishing to TestPyPI...")
    
    try:
        run_command("twine upload --repository testpypi dist/*")
        logger.info("✅ Successfully published to TestPyPI")
        logger.info("Test installation with:")
        logger.info("pip install --index-url https://test.pypi.org/simple/ bidoc")
    except subprocess.CalledProcessError as e:
        logger.error(f"TestPyPI upload failed: {e}")
        sys.exit(1)

def publish_to_pypi():
    """Publish to production PyPI"""
    logger.info("Publishing to PyPI...")
    
    # Final confirmation
    response = input("This will publish to production PyPI. Continue? (yes/no): ")
    if response.lower() != "yes":
        logger.info("Publishing cancelled")
        sys.exit(0)
    
    try:
        run_command("twine upload dist/*")
        logger.info("✅ Successfully published to PyPI")
        logger.info("Installation command:")
        logger.info("pip install bidoc")
    except subprocess.CalledProcessError as e:
        logger.error(f"PyPI upload failed: {e}")
        sys.exit(1)

def get_package_info():
    """Get current package information"""
    logger.info("Package Information:")
    
    # Get version from setup.py
    try:
        version_output = run_command("python setup.py --version", capture_output=True)
        logger.info(f"  Version: {version_output}")
    except Exception:
        logger.info("  Version: Could not determine")
    
    # Check if version exists on PyPI
    try:
        import requests
        response = requests.get("https://pypi.org/pypi/bidoc/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["info"]["version"]
            logger.info(f"  Latest on PyPI: {latest_version}")
        else:
            logger.info("  Latest on PyPI: Package not found")
    except Exception:
        logger.info("  Latest on PyPI: Could not check")

def main():
    """Main publishing workflow"""
    parser = argparse.ArgumentParser(description="Publish BI Documentation Tool to PyPI")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI")
    parser.add_argument("--prod", action="store_true", help="Publish to production PyPI")
    parser.add_argument("--check", action="store_true", help="Validate package only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    logger.info("🚀 Starting BI Documentation Tool PyPI Publishing")
    
    # Always run these steps
    validate_environment()
    get_package_info()
    clean_build_artifacts()
    validate_package()
    
    if args.check:
        logger.info("✅ Package validation completed successfully")
        return
    
    # Build package
    build_package()
    
    # Run tests (optional)
    run_tests()
    
    # Publish based on arguments
    if args.test:
        publish_to_test_pypi()
    elif args.prod:
        publish_to_pypi()
    else:
        logger.info("Package built and validated. Use --test or --prod to publish.")
        logger.info("Built packages available in dist/")
    
    logger.info("🎉 Publishing workflow completed!")

if __name__ == "__main__":
    main()