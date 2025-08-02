# Code Style Guide

This document outlines the coding standards and style guidelines for the BI Documentation Tool project.

## Overview

We use automated tools to maintain consistent code quality and style:

- **Black** for code formatting
- **isort** for import sorting  
- **Ruff** for linting and code quality
- **MyPy** for type checking
- **Bandit** for security analysis
- **pre-commit** for automated checks

## Quick Start

### Setup Development Environment

```bash
# Install development dependencies
pip install -e .[dev,test,docs]

# Setup pre-commit hooks
python scripts/setup_dev.py

# Check code quality
python scripts/format_code.py --check

# Format and fix issues
python scripts/format_code.py --fix

# Run all checks
python scripts/format_code.py --all
```

### Before Committing

```bash
# Format code and run checks
python scripts/format_code.py --fix

# Run tests
pytest

# Commit (pre-commit hooks will run automatically)
git commit -m "Your commit message"
```

## Code Formatting Standards

### Python Code Style

We follow [PEP 8](https://pep8.org/) with the following specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String quotes**: Double quotes preferred by Black
- **Trailing commas**: Added by Black for multi-line constructs

### Import Organization

Imports are sorted using isort with Black profile:

```python
# Standard library imports
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
from jinja2 import Template

# Local imports
from bidoc.config import load_config
from bidoc.utils import detect_file_type
```

### Type Hints

All functions should include type hints:

```python
def process_metadata(data: Dict[str, Any]) -> Optional[str]:
    """Process metadata and return formatted string."""
    if not data:
        return None
    return format_data(data)
```

### Docstrings

Use Google-style docstrings:

```python
def parse_file(file_path: Path, file_type: FileType) -> Optional[Dict[str, Any]]:
    """Parse a BI file and extract metadata.
    
    Args:
        file_path: Path to the file to parse
        file_type: Type of file (PowerBI, Tableau, etc.)
        
    Returns:
        Dictionary containing extracted metadata, or None if parsing failed
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If file cannot be read
        
    Example:
        >>> metadata = parse_file(Path("model.pbix"), FileType.POWER_BI)
        >>> print(metadata["type"])
        "Power BI"
    """
```

## Code Quality Standards

### Complexity Limits

- **McCabe complexity**: Maximum 10 per function
- **Function length**: Aim for <50 lines, maximum 100
- **Class length**: Aim for <300 lines, maximum 500
- **File length**: Aim for <500 lines, maximum 1000

### Error Handling

Use specific exception types and proper error messages:

```python
from bidoc.exceptions import BIDocError, ParsingError

def parse_data(data: str) -> Dict[str, Any]:
    """Parse data with proper error handling."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ParsingError(
            f"Invalid JSON data: {e}",
            error_code=ErrorCode.PARSING_INVALID_JSON,
            context={"data_preview": data[:100]}
        ) from e
```

### Security Guidelines

- Never commit secrets or API keys
- Validate all external inputs
- Use secure file handling for archives
- Sanitize data in outputs
- Follow OWASP guidelines for web security

### Testing Standards

- **Coverage target**: 90%+ line coverage
- **Test organization**: Mirror source structure in tests/
- **Naming**: `test_<function_name>_<scenario>`
- **Fixtures**: Use pytest fixtures for common test data

```python
def test_parse_file_with_valid_pbix(mock_pbix_file):
    """Test parsing a valid PBIX file."""
    file_path, expected_data = mock_pbix_file
    
    parser = PowerBIParser()
    result = parser.parse(file_path)
    
    assert result is not None
    assert result["type"] == "Power BI"
    assert len(result["tables"]) > 0
```

## Configuration Files

### pyproject.toml

Contains all tool configurations:
- Black formatting settings
- Ruff linting rules
- MyPy type checking options
- Pytest configuration
- Coverage settings
- Bandit security rules

### .pre-commit-config.yaml

Defines pre-commit hooks for:
- Code formatting (Black, isort)
- Linting (Ruff, flake8)  
- Type checking (MyPy)
- Security scanning (Bandit)
- General quality checks

### .editorconfig

Editor configuration for consistent formatting across IDEs.

## IDE Integration

### VS Code

Recommended extensions:
- Python
- Black Formatter
- isort
- Pylance
- Ruff

Settings:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. Install Black plugin
2. Configure Black as external tool
3. Enable MyPy integration
4. Set up Ruff as external tool
5. Configure format on save

## Automated Checks

### Pre-commit Hooks

Automatically run on every commit:
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON validation
- Python formatting and linting
- Type checking
- Security scanning

### CI/CD Pipeline

GitHub Actions runs:
- Full test suite
- Code coverage analysis
- Security scans
- Documentation builds
- Multi-platform testing

## Best Practices

### General

1. **Write self-documenting code** with clear names
2. **Keep functions focused** on single responsibilities
3. **Use meaningful variable names** (no `x`, `data`, `temp`)
4. **Add comments for complex logic** but prefer clear code
5. **Handle edge cases** and validate inputs

### Performance

1. **Use generators** for large data sets
2. **Cache expensive operations** when appropriate
3. **Profile performance** for critical paths
4. **Avoid premature optimization** but design for scale

### Security

1. **Validate all inputs** at boundaries
2. **Use secure defaults** for configurations
3. **Log security events** appropriately
4. **Keep dependencies updated** for security patches

### Documentation

1. **Keep README current** with setup instructions
2. **Document API changes** in CHANGELOG.md
3. **Add docstrings** to all public functions
4. **Include usage examples** in documentation

## Tools Reference

### Format Code Script

```bash
# Check formatting and quality
python scripts/format_code.py --check

# Fix formatting issues  
python scripts/format_code.py --fix

# Run all checks including tests
python scripts/format_code.py --all

# Skip tests
python scripts/format_code.py --all --no-tests
```

### Direct Tool Usage

```bash
# Black formatting
black --line-length=88 bidoc/ tests/

# Import sorting
isort --profile=black bidoc/ tests/

# Linting
ruff check bidoc/ tests/

# Type checking
mypy bidoc/

# Security scanning
bandit -r bidoc/

# Tests with coverage
pytest --cov=bidoc --cov-report=html
```

## Troubleshooting

### Common Issues

1. **Import order conflicts**: Run `isort --profile=black`
2. **Line length violations**: Use Black to auto-format
3. **Type checking errors**: Add appropriate type hints
4. **Security warnings**: Review Bandit output and fix issues

### Getting Help

1. Check existing issues in the repository
2. Review the documentation
3. Ask questions in discussions
4. Contribute improvements to this guide

---

This style guide is a living document. Please suggest improvements and keep it updated as the project evolves.