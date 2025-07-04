# Quick Reference - BI Documentation Tool

## Basic Commands

```bash
# Generate all formats from a single file
python -m bidoc -i report.pbix -o docs/

# Process multiple files with verbose output
python -m bidoc -i *.pbix -i *.twbx -o docs/ --verbose

# Generate only Markdown documentation
python -m bidoc -i dashboard.twbx -f markdown -o exports/

# Docker usage
docker run -v $(pwd):/data bidoc-tool -i /data/report.pbix -o /data/docs/
```

## Command Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | *required* | Input BI file(s) |
| `--output` | `-o` | `docs/` | Output directory |
| `--format` | `-f` | `all` | Format: `markdown`, `json`, `all` |
| `--verbose` | `-v` | off | Detailed logging |
| `--with-summary` | | off | Generate AI summary |

## Supported File Types

| Extension | Type | Support |
|-----------|------|---------|
| `.pbix` | Power BI Desktop | ✅ Full |
| `.twb` | Tableau Workbook | ✅ Full |
| `.twbx` | Tableau Packaged | ✅ Full |

## Output Structure

```text
docs/
├── report1.md          # Markdown documentation
├── report1.json        # JSON metadata
├── dashboard1.md       # Tableau workbook docs
└── dashboard1.json     # Tableau metadata
```

## Common Issues

**Import errors**: Activate virtual environment
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

**Permission denied**: Check output directory permissions
```bash
mkdir -p docs/ && chmod 755 docs/
```

**File not found**: Use absolute paths or check working directory
```bash
python -m bidoc -i /full/path/to/file.pbix -o ./docs/
```

## Quick Setup

```bash
# 1. Clone and setup
git clone <repo-url> && cd bi-doc
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Test installation
python -m bidoc --help

# 3. Process your first file
python -m bidoc -i your_file.pbix -o docs/ --verbose
```

## Docker Quick Start

```bash
# Build once
docker build -t bidoc-tool .

# Use anywhere
docker run -v $(pwd):/data bidoc-tool -i /data/*.pbix -o /data/docs/
```

For detailed information, see [USER_GUIDE.md](USER_GUIDE.md).
