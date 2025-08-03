#!/bin/bash
# Install all required dependencies for BI Documentation Tool

echo "🔧 Installing BI Documentation Tool Dependencies"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Activate virtual environment if it exists, otherwise create one
if [[ -d "venv" ]]; then
    print_status "Activating existing virtual environment..."
    source venv/bin/activate
else
    print_status "Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

print_success "Virtual environment ready"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install all required dependencies from requirements.txt
print_status "Installing project dependencies..."
pip install -r requirements.txt

# Install additional dependencies that might be missing
print_status "Installing additional dependencies..."
pip install pandas>=1.5.0
pip install lxml>=4.9.0
pip install tableaudocumentapi>=0.11
pip install pbixray>=0.3.3
pip install click>=8.0.0
pip install jinja2>=3.1.0
pip install colorama>=0.4.0
pip install toml>=0.10.2

# Install development dependencies
print_status "Installing development dependencies..."
pip install pytest pytest-cov build twine

# Install the package itself
print_status "Installing bidoc package..."
pip install -e .

print_success "All dependencies installed successfully!"

# Verify installation
print_status "Verifying installation..."
python -c "
import sys
print('✅ Python:', sys.version.split()[0])

modules = ['pandas', 'lxml', 'click', 'jinja2', 'colorama', 'toml', 'bidoc']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: imported successfully')
    except ImportError as e:
        print(f'❌ {module}: {e}')

# Test pbixray and tableaudocumentapi separately
try:
    import pbixray
    print('✅ pbixray: imported successfully')
except ImportError as e:
    print(f'⚠️  pbixray: {e}')

try:
    import tableaudocumentapi
    print('✅ tableaudocumentapi: imported successfully')
except ImportError as e:
    print(f'⚠️  tableaudocumentapi: {e}')
"

echo ""
print_success "Dependency installation complete!"
echo ""
echo "🚀 Now you can run:"
echo "source venv/bin/activate"
echo "python demo.py"
echo "python -m bidoc --help"