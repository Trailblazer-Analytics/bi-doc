# BI Documentation Tool

A command-line tool for automatically generating documentation from Business Intelligence files. Supports Power BI (.pbix) and Tableau (.twb/.twbx) workbooks, extracting metadata to produce comprehensive Markdown and JSON documentation.

## Features

- **Multi-format Support**: Parse Power BI (.pbix) and Tableau (.twb/.twbx) files
- **Rich Metadata Extraction**: Extract datasets, fields, measures, calculations, data sources, and visual layouts
- **Dual Output Formats**: Generate both human-readable Markdown and machine-readable JSON
- **Docker Ready**: Containerized for easy CI/CD integration
- **Modular Architecture**: Extensible design for future enhancements
- **Future AI Integration**: Built-in hooks for AI-powered summarization and insights

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd bi-doc-tool

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Usage

```bash
# Parse a Power BI file
bidoc-cli --input report.pbix --output docs/ --format all

# Parse a Tableau workbook
bidoc-cli --input dashboard.twbx --output docs/ --format markdown

# Batch processing with verbose logging
bidoc-cli --input *.pbix --output docs/ --format all --verbose
```

### Docker Usage

```bash
# Build the Docker image
docker build -t bidoc-tool .

# Run with mounted volumes
docker run -v $(pwd):/data bidoc-tool --input /data/report.pbix --output /data/docs
```

## What Gets Extracted

### Power BI (.pbix)
- **Data Model**: Tables, columns, data types, relationships
- **DAX Measures**: All measures with their formulas
- **Calculated Columns**: Custom calculations and their DAX expressions
- **Data Sources**: Connection details and source information
- **Report Layout**: Pages, visuals, and field mappings
- **Power Query**: M code and transformation steps

### Tableau (.twb/.twbx)
- **Data Sources**: Connection details and database information
- **Fields**: Dimensions, measures, calculated fields with formulas
- **Worksheets**: Individual sheet layouts and field usage
- **Dashboards**: Dashboard structure and contained worksheets
- **Parameters**: User-defined parameters and default values

## Output Examples

### Markdown Output
```markdown
# Documentation for Sales Dashboard

## Data Sources
- **SQL Server**: server01.company.com/SalesDB
- **Excel File**: Q4_Targets.xlsx

## Tables and Fields
### Sales
| Field Name | Type | Description |
|------------|------|-------------|
| SalesAmount | Decimal | Total sales value |
| CustomerID | Integer | Customer identifier |
| TotalSalesYTD* | Decimal | Calculated: `SUM(Sales[SalesAmount])` |

## Visualizations
### Page: Overview
- **Bar Chart**: Sales by Region
  - Fields: [Geography.Region], [Sales.TotalSalesYTD]
- **Card**: Total Revenue
  - Field: [Sales.TotalSalesYTD]
```

### JSON Output
```json
{
  "file": "sales_dashboard.pbix",
  "type": "Power BI",
  "data_sources": [
    {
      "name": "SalesDB",
      "connection": "sqlserver://server01.company.com/SalesDB",
      "tables": [
        {
          "name": "Sales",
          "columns": [
            {"name": "SalesAmount", "data_type": "Decimal"},
            {"name": "CustomerID", "data_type": "Integer"}
          ],
          "measures": [
            {"name": "TotalSalesYTD", "expression": "SUM(Sales[SalesAmount])"}
          ]
        }
      ]
    }
  ]
}
```

## Architecture

The tool follows a modular architecture with clear separation of concerns:

```
bidoc/
├── cli.py              # Command-line interface
├── pbix_parser.py      # Power BI parsing logic
├── tableau_parser.py   # Tableau parsing logic
├── markdown_generator.py  # Markdown output formatting
├── json_generator.py   # JSON output formatting
├── ai_summary.py       # Future AI integration hooks
└── utils.py           # Common utilities
```

## Future Enhancements

- **BYO AI Integration**: Bring Your Own AI for custom summarization
- **Additional Formats**: HTML, PDF, Confluence output
- **Advanced Analytics**: Usage patterns and impact analysis
- **Lineage Tracking**: Enhanced data lineage visualization
- **Vertical Templates**: Industry-specific documentation templates

## Dependencies

- **PBIXRay**: Power BI file parsing
- **tableau-document-api**: Tableau workbook parsing
- **Click**: CLI framework
- **Jinja2**: Template rendering

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
