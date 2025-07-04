# BI Documentation Tool

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Trailblazer-Analytics/bi-doc/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/Trailblazer-Analytics/bi-doc)

A powerful command-line tool for automatically generating comprehensive documentation from Business Intelligence files. Supports Power BI (.pbix) and Tableau (.twb/.twbx) workbooks, extracting detailed metadata to produce professional Markdown and JSON documentation.

**🎉 Version 1.0.0 - Official Public Release!** Complete with analyst-friendly extensions for users at all technical levels.

## 🚀 Features

- **Multi-format Support**: Parse Power BI (.pbix) and Tableau (.twb/.twbx) files
- **Rich Metadata Extraction**: Extract datasets, fields, measures, calculations, data sources, and visual layouts
- **Dual Output Formats**: Generate both human-readable Markdown and machine-readable JSON
- **Docker Ready**: Containerized for easy CI/CD integration
- **Modular Architecture**: Extensible design for future enhancements
- **AI Integration Ready**: Built-in hooks for AI-powered summarization and insights
- **Batch Processing**: Process multiple files simultaneously
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

#### Option 1: Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd bi-doc

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

#### Option 2: Docker (Recommended for CI/CD)
```bash
# Build the Docker image
docker build -t bidoc-tool .

# Verify installation
docker run bidoc-tool --help
```

### Basic Usage

```bash
# Parse a single Power BI file
python -m bidoc -i report.pbix -o docs/ -f all

# Parse a Tableau workbook with verbose output
python -m bidoc -i dashboard.twbx -o docs/ -f markdown --verbose

# Batch processing multiple files
python -m bidoc -i *.pbix -i *.twbx -o docs/ -f all

# Generate AI-enhanced summaries (when configured)
python -m bidoc -i report.pbix -o docs/ --with-summary
```

### Analyst-Friendly Options

**For Windows analysts who prefer GUI tools:**

```powershell
# PowerShell Module (recommended for Windows users)
Invoke-BIFileScan "dashboard.pbix" -ShowProgress -OpenResult
# Or use the shorter alias: Scan-BIFile "dashboard.pbix" -ShowProgress -OpenResult

# Drag-and-drop batch file
# Simply drag any .pbix/.twb/.twbx file onto BI-Doc-Quick-Scan.bat

# Graphical user interface
python analyst_extensions/gui/bidoc_gui.py
```

See **[Analyst Extensions Guide](analyst_extensions/INSTALLATION_GUIDE.md)** for complete setup instructions.

### Docker Usage

```bash
# Build the Docker image
docker build -t bidoc-tool .

# Run with mounted volumes
docker run -v $(pwd):/data bidoc-tool --input /data/report.pbix --output /data/docs
```

## 📖 Documentation

- **[User Guide](USER_GUIDE.md)** - Comprehensive usage guide with examples
- **[Analyst Extensions](analyst_extensions/INSTALLATION_GUIDE.md)** - Windows-friendly GUI and PowerShell tools
- **[QoL Suggestions](QOL_SUGGESTIONS.md)** - Quality of life improvements and roadmap
- **[Roadmap](ROADMAP.md)** - Development roadmap and planned features
- **[Deployment Summary](DEPLOYMENT_SUMMARY.md)** - Production deployment information

## 🔍 What Gets Extracted

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

## 📄 Output Examples

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

## 🏗️ Architecture

The tool follows a modular architecture with clear separation of concerns:

```text
bidoc/
├── cli.py              # Command-line interface
├── pbix_parser.py      # Power BI parsing logic
├── tableau_parser.py   # Tableau parsing logic
├── markdown_generator.py  # Markdown output formatting
├── json_generator.py   # JSON output formatting
├── ai_summary.py       # AI integration hooks
└── utils.py           # Common utilities
```

## 🚀 Current Status & Roadmap

### ✅ Completed Features

- **Multi-format Support**: Robust parsing of Power BI (.pbix) and Tableau (.twb/.twbx) files
- **Rich Metadata Extraction**: Complete extraction of datasets, fields, measures, calculations, and visuals
- **Dual Output Formats**: High-quality Markdown (markdownlint compliant) and structured JSON
- **Production Ready**: Robust CLI, Docker support, comprehensive error handling
- **Batch Processing**: Efficient processing of multiple files with detailed logging
- **Modular Architecture**: Extensible design ready for future enhancements

### 🔄 Next Priorities

For detailed roadmap and quality-of-life improvements, see [QOL_SUGGESTIONS.md](QOL_SUGGESTIONS.md):

- **Enhanced User Experience**: Progress indicators, better error messages, interactive mode
- **Performance Optimizations**: Parallel processing, incremental updates, caching
- **Output Quality**: Enhanced Markdown with TOC, collapsible sections, syntax highlighting
- **Enterprise Integration**: Git hooks, Confluence export, SharePoint integration
- **Advanced Analytics**: Usage patterns, similarity detection, AI-powered insights

## 🔧 Dependencies

- **pbixray**: Power BI file parsing (`>=0.3.3`)
- **tableaudocumentapi**: Tableau workbook parsing (`>=0.11`)
- **click**: CLI framework (`>=8.0.0`)
- **jinja2**: Template rendering (`>=3.1.0`)
- **pandas**: Data processing (`>=1.5.0`)
- **lxml**: XML processing (`>=4.9.0`)
- **colorama**: Cross-platform colored output (`>=0.4.0`)

## 🙏 Acknowledgments

We are grateful to the open-source community and the following projects that make this tool possible:

- **[PBIXRay](https://github.com/aafvstam/pbixray)** by Arjen van Stam - Essential Power BI file parsing capabilities
- **[Tableau Document API](https://github.com/tableau/document-api-python)** by Tableau Software - Comprehensive Tableau workbook analysis
- **Microsoft** - Power BI sample files for testing and demonstration
- **Python Community** - The amazing ecosystem of libraries (pandas, click, jinja2, etc.)

For complete attribution and licensing information, see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Submit a pull request

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd bi-doc
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=bidoc tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [USER_GUIDE.md](USER_GUIDE.md) for detailed usage instructions
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for questions and ideas

## 📊 Status

- ✅ **Production Ready**: All core features implemented and tested
- ✅ **Docker Support**: Containerized for easy deployment
- ✅ **CI/CD Ready**: Automated testing and deployment pipelines
- 🔄 **Active Development**: Regular updates and new features

## Commercial Use & Licensing

This software is licensed under the Business Source License 1.1 (BSL). Production or commercial use requires a commercial license from the author.

**To use this tool in production or for commercial purposes, please contact:**

- Email: <your@email.com>
- Website: <https://yourproductsite.com>

We offer flexible licensing, support, and enterprise options. Non-commercial, research, and evaluation use is always free under the BSL.

For organizations or users interested in a commercial license, see the [COMMERCIAL_LICENSE_TEMPLATE.md](COMMERCIAL_LICENSE_TEMPLATE.md) file for a sample agreement.

---

Made with ❤️ for the BI community
