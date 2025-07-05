# BI Documentation Tool - User Guide

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Command Reference](#command-reference)
4. [File Format Support](#file-format-support)
5. [Output Examples](#output-examples)
6. [Advanced Usage](#advanced-usage)
7. [Enterprise Integration](#enterprise-integration)
8. [Docker Usage](#docker-usage)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Installation

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large files)
- **Storage**: 100MB for tool + space for output files

### Step-by-Step Installation

#### Method 1: Local Python Installation (Recommended for Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd bi-doc

# 2. Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -m bidoc --help
```

#### Method 2: Docker Installation (Recommended for Production)

```bash
# 1. Build the Docker image
docker build -t bidoc-tool .

# 2. Verify installation
docker run bidoc-tool --help

# 3. Create alias for easier usage (optional)
alias bidoc="docker run -v \$(pwd):/data bidoc-tool"
```

## Basic Usage

### Your First Documentation

Let's start with a simple example. Assume you have a Power BI file called `sales_report.pbix`:

```bash
# Generate documentation in all formats
python -m bidoc -i sales_report.pbix -o documentation/

# This creates:
# documentation/
# ├── sales_report.md      # Human-readable Markdown
# └── sales_report.json    # Machine-readable JSON
```

### Single File Processing

```bash
# Markdown only
python -m bidoc -i report.pbix -f markdown -o docs/

# JSON only
python -m bidoc -i dashboard.twbx -f json -o exports/

# All formats with verbose logging
python -m bidoc -i workbook.twb -f all -o docs/ --verbose
```

### Multiple File Processing

```bash
# Process multiple specific files
python -m bidoc -i file1.pbix -i file2.twbx -i file3.twb -o docs/

# Process all Power BI files in current directory
python -m bidoc -i *.pbix -o docs/

# Process all supported files in a directory
python -m bidoc -i /path/to/files/*.pbix -i /path/to/files/*.twb* -o docs/
```

## Command Reference

### Complete Command Syntax

```bash
python -m bidoc [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--input` | `-i` | TEXT | Required | Input BI file(s) to parse |
| `--output` | `-o` | TEXT | `docs/` | Output directory |
| `--format` | `-f` | CHOICE | `all` | Output format: `markdown`, `json`, or `all` |
| `--verbose` | `-v` | FLAG | False | Enable detailed logging |
| `--with-summary` | | FLAG | False | Generate AI summary (when configured) |
| `--version` | | FLAG | | Show version and exit |
| `--help` | | FLAG | | Show help message |

### Examples by Option

#### Input Files (`--input` / `-i`)

```bash
# Single file
python -m bidoc -i report.pbix

# Multiple files
python -m bidoc -i file1.pbix -i file2.twbx

# Wildcard patterns
python -m bidoc -i *.pbix
python -m bidoc -i /data/*.twb*

# Mixed file types
python -m bidoc -i sales.pbix -i marketing.twbx -i operations.twb
```

#### Output Directory (`--output` / `-o`)

```bash
# Default directory (docs/)
python -m bidoc -i report.pbix

# Custom directory
python -m bidoc -i report.pbix -o /path/to/output/

# Relative path
python -m bidoc -i report.pbix -o ../documentation/

# Current directory
python -m bidoc -i report.pbix -o ./
```

#### Output Format (`--format` / `-f`)

```bash
# Markdown only
python -m bidoc -i report.pbix -f markdown

# JSON only
python -m bidoc -i report.pbix -f json

# Both formats (default)
python -m bidoc -i report.pbix -f all
```

#### Verbose Logging (`--verbose` / `-v`)

```bash
# Basic output
python -m bidoc -i report.pbix

# Detailed logging
python -m bidoc -i report.pbix --verbose

# Example verbose output:
# INFO: Processing file: report.pbix
# INFO: Detected file type: Power BI
# INFO: Extracting data model...
# INFO: Found 5 tables, 23 measures
# INFO: Generating markdown documentation...
# INFO: Documentation saved to: docs/report.md
```

## File Format Support

### Supported File Types

| Format | Extension | Description | Support Level |
|--------|-----------|-------------|---------------|
| Power BI | `.pbix` | Power BI Desktop files | ✅ Full Support |
| Tableau Workbook | `.twb` | Tableau workbook (XML) | ✅ Full Support |
| Tableau Packaged | `.twbx` | Packaged Tableau workbook | ✅ Full Support |

### What Gets Extracted

#### Power BI Files (.pbix)

**Data Model:**
- Tables and relationships
- Column names, types, and descriptions
- Primary and foreign keys
- Calculated columns with DAX formulas

**Measures and Calculations:**
- DAX measures with complete formulas
- KPIs and their target values
- Calculated tables and columns

**Data Sources:**
- Connection strings and server details
- Data source types (SQL Server, Excel, Web, etc.)
- Authentication methods
- Refresh schedules (when available)

**Report Structure:**
- Page layouts and navigation
- Visual types and configurations
- Field mappings and filters
- Bookmarks and drill-through actions

**Power Query:**
- M code for data transformations
- Query dependencies
- Data source parameters

#### Tableau Files (.twb/.twbx)

**Data Connections:**
- Database connections and server details
- File-based data sources
- Custom SQL queries
- Data source filters

**Field Definitions:**
- Dimensions and measures
- Calculated fields with formulas
- Parameters and their default values
- Field aliases and descriptions

**Worksheets:**
- Chart types and configurations
- Field assignments (rows, columns, filters)
- Sorting and grouping rules
- Reference lines and annotations

**Dashboards:**
- Layout and sizing information
- Worksheet dependencies
- Action filters and highlighting
- URL actions and navigation

## Output Examples

### Markdown Documentation Structure

The generated Markdown follows a consistent structure:

```markdown
# Documentation for [Filename]

## Overview
- **File Type**: Power BI/Tableau
- **File Size**: [size]
- **Generated**: [timestamp]
- **Tool Version**: [version]

## Data Sources
### [Source Name]
- **Type**: [SQL Server/Excel/etc.]
- **Connection**: [connection details]
- **Tables**: [table count]

## Data Model
### Tables
#### [Table Name]
- **Row Count**: [if available]
- **Relationships**: [related tables]

##### Columns
| Name | Type | Description |
|------|------|-------------|
| CustomerID | Integer | Unique customer identifier |
| SalesAmount | Decimal | Total sales value |

##### Measures
| Name | Formula | Description |
|------|---------|-------------|
| Total Sales | SUM([SalesAmount]) | Sum of all sales |

## Visualizations
### Page: [Page Name]
#### [Visual Type]: [Visual Title]
- **Fields**: [field list]
- **Filters**: [applied filters]

## Summary
- **Total Tables**: [count]
- **Total Measures**: [count]
- **Total Visualizations**: [count]
```

### JSON Output Structure

```json
{
  "metadata": {
    "filename": "sales_report.pbix",
    "file_type": "Power BI",
    "file_size": "2.5 MB",
    "generated_at": "2025-01-15T10:30:00Z",
    "tool_version": "1.0.0"
  },
  "data_sources": [
    {
      "name": "SalesDB",
      "type": "SQL Server",
      "connection": "server01.company.com",
      "tables": ["Sales", "Customers", "Products"]
    }
  ],
  "data_model": {
    "tables": [
      {
        "name": "Sales",
        "columns": [
          {
            "name": "SalesAmount",
            "data_type": "Decimal",
            "is_key": false,
            "description": "Total sales value"
          }
        ],
        "measures": [
          {
            "name": "Total Sales",
            "expression": "SUM(Sales[SalesAmount])",
            "description": "Sum of all sales amounts"
          }
        ],
        "relationships": [
          {
            "to_table": "Customers",
            "from_column": "CustomerID",
            "to_column": "CustomerID",
            "cardinality": "many_to_one"
          }
        ]
      }
    ]
  },
  "visualizations": [
    {
      "page": "Overview",
      "type": "Bar Chart",
      "title": "Sales by Region",
      "fields": {
        "axis": ["Geography[Region]"],
        "values": ["Measures[Total Sales]"]
      }
    }
  ]
}
```

## Advanced Usage

### Batch Processing with Scripts

Create a batch processing script:

```bash
#!/bin/bash
# process_all_reports.sh

# Set common parameters
OUTPUT_DIR="documentation"
FORMAT="all"

# Create output directory
mkdir -p $OUTPUT_DIR

# Process all Power BI files
for file in reports/*.pbix; do
    echo "Processing: $file"
    python -m bidoc -i "$file" -o "$OUTPUT_DIR" -f "$FORMAT" --verbose
done

# Process all Tableau files
for file in dashboards/*.twb*; do
    echo "Processing: $file"
    python -m bidoc -i "$file" -o "$OUTPUT_DIR" -f "$FORMAT" --verbose
done

echo "All files processed!"
```

### Integration with CI/CD

#### GitHub Actions Example

```yaml
# .github/workflows/document-bi.yml
name: Generate BI Documentation

on:
  push:
    paths:
      - 'reports/**/*.pbix'
      - 'dashboards/**/*.twb*'

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build documentation tool
        run: docker build -t bidoc-tool .

      - name: Generate documentation
        run: |
          docker run -v ${{ github.workspace }}:/data bidoc-tool \
            -i /data/reports/*.pbix \
            -i /data/dashboards/*.twb* \
            -o /data/docs \
            -f all --verbose

      - name: Commit documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "Update BI documentation" || exit 0
          git push
```

### AI Summary Integration

When AI integration is configured:

```bash
# Generate enhanced documentation with AI summaries
python -m bidoc -i complex_report.pbix -o docs/ --with-summary

# This adds AI-generated sections like:
# - Executive Summary
# - Key Insights
# - Data Quality Assessment
# - Recommended Actions
```

## Enterprise Integration

The BI Documentation Tool is designed for seamless integration with enterprise data management platforms. See [INTEGRATION_HOOKS.md](INTEGRATION_HOOKS.md) for comprehensive examples and implementation patterns.

### Quick Integration Examples

#### Confluence Integration

```bash
# Generate documentation and push to Confluence
python -m bidoc -i "reports/*.pbix" -o "temp_docs" -f markdown
python scripts/confluence_upload.py --docs-dir temp_docs --space "BITOOLS"
```

#### Data Catalog Integration

```bash
# Generate JSON metadata for data catalog ingestion
python -m bidoc -i "*.pbix" -f json -o "metadata_export"
python scripts/ataccama_sync.py --metadata-dir metadata_export
```

#### CI/CD Integration with Multiple Platforms

```yaml
# Example: Multi-platform CI/CD pipeline
- name: Generate BI Documentation
  run: python -m bidoc -i "bi-files/" -o "docs/" -f all

- name: Deploy to Confluence
  run: python scripts/confluence_deploy.py

- name: Update Data Catalog
  run: python scripts/catalog_sync.py

- name: Notify Teams
  run: python scripts/teams_notification.py
```

### Supported Integration Platforms

- **Data Catalogs**: Ataccama DGC, Microsoft Purview, Apache Atlas, DataHub
- **Documentation**: Confluence, SharePoint, GitBook, Notion
- **Version Control**: Git-based workflows with automated documentation updates
- **Notification**: Slack, Microsoft Teams, email alerts

## Docker Usage

### Basic Docker Commands

```bash
# Build the image
docker build -t bidoc-tool .

# Run with current directory mounted
docker run -v $(pwd):/data bidoc-tool -i /data/report.pbix -o /data/docs/

# Interactive mode for debugging
docker run -it -v $(pwd):/data bidoc-tool bash
```

### Docker Compose for Regular Processing

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  bidoc:
    build: .
    volumes:
      - ./input:/data/input
      - ./output:/data/output
    command: >
      sh -c "
        python -m bidoc -i /data/input/*.pbix -o /data/output -f all --verbose &&
        python -m bidoc -i /data/input/*.twb* -o /data/output -f all --verbose
      "
```

Run with:

```bash
docker-compose up
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "No module named 'bidoc'"

**Cause**: Package not installed or virtual environment not activated

**Solution**:
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Or reinstall
pip install -e .
```

#### Issue: "Permission denied" when writing output

**Cause**: Insufficient permissions for output directory

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p docs/
chmod 755 docs/

# Or use a different output directory
python -m bidoc -i file.pbix -o ~/Documents/bi-docs/
```

#### Issue: "Unsupported file format"

**Cause**: File extension not recognized or file corrupted

**Solution**:
```bash
# Check file extension
ls -la *.pbix *.twb*

# Verify file is not corrupted
file report.pbix  # Should show "Microsoft Office document"

# Try with different file
python -m bidoc -i known_good_file.pbix -o test/
```

#### Issue: Docker "bind mount" errors

**Cause**: Path issues in Docker volume mounting

**Solution**:
```bash
# Use absolute paths
docker run -v /full/path/to/files:/data bidoc-tool

# On Windows, use proper path format
docker run -v C:\Projects\BI:/data bidoc-tool
```

### Getting Help

#### Enable Verbose Logging

```bash
python -m bidoc -i file.pbix --verbose
```

#### Check System Information

```bash
# Python version
python --version

# Package versions
pip list

# System info
python -c "import sys; print(sys.version)"
```

#### Log Files

The tool creates log files in:
- **Default**: `./logs/bidoc.log`
- **Custom**: Set via environment variable `BIDOC_LOG_PATH`

## Best Practices

### File Organization

**Recommended Directory Structure**:
```
project/
├── input/
│   ├── powerbi/
│   │   ├── sales_reports/
│   │   └── marketing_dashboards/
│   └── tableau/
│       ├── operational_dashboards/
│       └── executive_reports/
├── output/
│   ├── documentation/
│   └── archives/
└── scripts/
    ├── process_all.sh
    └── update_docs.py
```

### Performance Optimization

**For Large Files**:
- Use SSD storage for better I/O performance
- Allocate sufficient memory (4GB+ recommended)
- Process files individually rather than in large batches
- Consider using `--format json` for faster processing

**Batch Processing Tips**:
```bash
# Process files sequentially to avoid memory issues
for file in *.pbix; do
    python -m bidoc -i "$file" -o docs/ --verbose
    sleep 2  # Brief pause between files
done
```

### Version Control

**Include in Git**:
- Source BI files (if appropriate for your organization)
- Generated documentation
- Processing scripts
- Configuration files

**Git ignore**:
```gitignore
# Temporary files
*.tmp
*.log

# Large binary files (optional)
*.pbix
*.twbx

# Output directories (optional)
docs/generated/
```

### Documentation Standards

**Naming Conventions**:
- Use descriptive filenames: `sales_q4_2024.pbix` vs `report1.pbix`
- Consistent date formats: `YYYY-MM-DD` or `YYYY_Q#`
- Environment indicators: `prod_`, `test_`, `dev_`

**Organization**:
- Group by business function
- Separate by environment (prod/test/dev)
- Use consistent folder structures

### Security Considerations

**Sensitive Data**:
- Review generated documentation for sensitive information
- Consider using `.gitignore` for files containing PII
- Implement access controls for documentation repositories

**Connection Strings**:
- The tool extracts connection information which may include server names
- Review output before sharing externally
- Consider masking sensitive server details in documentation

## Future Enhancements & Roadmap

### Quality of Life Improvements

The development team actively works on improving user experience. For detailed information about planned enhancements, see [QOL_SUGGESTIONS.md](QOL_SUGGESTIONS.md).

**High Priority Improvements:**

- **Progress Indicators**: Real-time progress bars for file processing
- **Better Error Messages**: Context-aware error reporting with suggested fixes
- **Parallel Processing**: Faster batch processing using multiple CPU cores
- **Enhanced Output**: Table of contents, collapsible sections, syntax highlighting
- **Incremental Updates**: Only reprocess files that have changed

**Medium Priority Features:**

- **Template System**: Custom Jinja2 templates for different documentation styles
- **Enterprise Integration**: Direct export to Confluence, SharePoint, and wikis
- **Advanced Analytics**: Usage patterns, similarity detection, complexity scoring
- **Configuration Files**: Save and reuse processing preferences

**Long-term Vision:**

- **Web Interface**: Browser-based tool for non-technical users
- **AI Integration**: Smart summarization and pattern recognition
- **Real-time Processing**: Live dashboard documentation updates
- **Plugin System**: Community-developed extensions and parsers

### Contributing Ideas

We welcome feedback and suggestions! Ways to contribute:

- **Feature Requests**: Submit GitHub issues with enhancement ideas
- **User Feedback**: Share your experience and pain points
- **Community Templates**: Contribute custom templates for different use cases
- **Documentation**: Help improve guides and examples

---

This completes the comprehensive user guide. The tool is now ready for production use with detailed documentation for users of all skill levels.
