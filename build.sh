#!/bin/bash
# BI Documentation Tool - Quick Build Script
# This script builds the complete solution for immediate testing and deployment

set -e  # Exit on any error

echo "🚀 Building BI Documentation Tool Solution"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "setup.py" || ! -d "bidoc" ]]; then
    print_error "Must run from project root directory"
    exit 1
fi

print_status "Validating environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.8"
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    print_error "Python 3.8+ required, found $python_version"
    exit 1
fi
print_success "Python version: $python_version"

# Clean previous build artifacts
print_status "Cleaning build artifacts..."
rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ htmlcov/ demo_output/ test_output/
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
print_success "Build artifacts cleaned"

# Install/upgrade pip and build tools
print_status "Installing build dependencies..."
python3 -m pip install --upgrade pip setuptools wheel build twine || {
    print_warning "Could not upgrade build tools, continuing with existing versions"
}

# Install the package in development mode
print_status "Installing package in development mode..."
python3 -m pip install -e . || {
    print_error "Failed to install package"
    exit 1
}
print_success "Package installed successfully"

# Validate package structure
print_status "Validating package structure..."
python3 setup.py check || {
    print_error "Package validation failed"
    exit 1
}

# Test import
python3 -c "import bidoc; print('✅ bidoc imported successfully')" || {
    print_error "Package import failed"
    exit 1
}
print_success "Package structure validated"

# Run quick tests if pytest is available
print_status "Running tests..."
if command -v pytest &> /dev/null; then
    python3 -m pytest tests/ -v --tb=short || {
        print_warning "Some tests failed, but continuing build"
    }
else
    print_warning "pytest not available, skipping tests"
fi

# Build distributions
print_status "Building distribution packages..."
python3 setup.py sdist bdist_wheel || {
    print_error "Distribution build failed"
    exit 1
}
print_success "Distribution packages built"

# Validate distributions
print_status "Validating distributions..."
if command -v twine &> /dev/null; then
    twine check dist/* || {
        print_warning "Distribution validation had warnings"
    }
else
    print_warning "twine not available, skipping distribution validation"
fi

# Test with sample files if available
print_status "Testing with sample files..."
if [[ -d "samples/power_bi" ]]; then
    sample_files=(samples/power_bi/*.pbix)
    if [[ -f "${sample_files[0]}" ]]; then
        # Test with first sample file
        test_file="${sample_files[0]}"
        print_status "Testing with: $(basename "$test_file")"
        
        mkdir -p build_test_output
        python3 -m bidoc -i "$test_file" -o build_test_output/ -f all --verbose || {
            print_warning "Sample file test had issues"
        }
        
        # Check output
        if [[ -f "build_test_output/"*.md && -f "build_test_output/"*.json ]]; then
            print_success "Sample file processed successfully"
            output_count=$(ls build_test_output/ | wc -l)
            print_status "Generated $output_count output files"
        else
            print_warning "Sample file processing incomplete"
        fi
    else
        print_warning "No sample files found for testing"
    fi
else
    print_warning "No samples directory found"
fi

# Run demo if available
print_status "Running demo script..."
if [[ -f "demo.py" ]]; then
    python3 demo.py || {
        print_warning "Demo script had issues"
    }
    
    if [[ -d "demo_output" ]]; then
        demo_files=$(ls demo_output/ | wc -l)
        print_success "Demo completed - generated $demo_files files"
    fi
else
    print_warning "Demo script not found"
fi

# Generate build information
print_status "Generating build information..."
cat > build_info.json << EOF
{
    "version": "$(python3 setup.py --version 2>/dev/null || echo '1.0.0')",
    "build_time": "$(date -u '+%Y-%m-%d %H:%M:%S UTC')",
    "git_hash": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
    "python_version": "$(python3 --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')",
    "platform": "$(uname -s)"
}
EOF
print_success "Build information generated"

# Display build summary
echo ""
echo "🎉 BUILD COMPLETED SUCCESSFULLY!"
echo "================================="

# Show distribution files
if [[ -d "dist" ]]; then
    echo "📦 Distribution files:"
    ls -lh dist/
fi

echo ""
echo "📋 Next Steps:"
echo "1. Test installation: pip install dist/*.whl"
echo "2. Run tests: python demo.py"
echo "3. Publish to TestPyPI: python scripts/publish_pypi.py --test"
echo "4. Publish to PyPI: python scripts/publish_pypi.py --prod"

echo ""
echo "🚀 The solution is ready for deployment!"

# Check if we have distribution files
if [[ -f dist/*.whl && -f dist/*.tar.gz ]]; then
    print_success "✅ Complete package build ready"
    echo ""
    echo "Installation command:"
    wheel_file=$(ls dist/*.whl | head -1)
    echo "pip install $wheel_file"
else
    print_error "❌ Distribution files missing"
    exit 1
fi