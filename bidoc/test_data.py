"""Test utilities and sample data"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict


def create_sample_powerbi_metadata() -> Dict[str, Any]:
    """Create sample Power BI metadata for testing"""
    return {
        "file": "sample_sales_report.pbix",
        "type": "Power BI",
        "file_path": "/data/sample_sales_report.pbix",
        "data_sources": [
            {
                "name": "SalesDB",
                "type": "SQL Server",
                "connection": "sqlserver://server01.company.com/SalesDB",
                "query": 'let Source = Sql.Database("server01.company.com", "SalesDB") in Source',
            }
        ],
        "tables": [
            {
                "name": "Sales",
                "columns": [
                    {
                        "name": "SalesID",
                        "data_type": "Int64",
                        "is_hidden": False,
                        "description": "Unique sales identifier",
                    },
                    {
                        "name": "CustomerID",
                        "data_type": "Int64",
                        "is_hidden": False,
                        "description": "Customer identifier",
                    },
                    {
                        "name": "ProductID",
                        "data_type": "Int64",
                        "is_hidden": False,
                        "description": "Product identifier",
                    },
                    {
                        "name": "SalesAmount",
                        "data_type": "Decimal",
                        "is_hidden": False,
                        "description": "Total sales amount",
                    },
                    {
                        "name": "OrderDate",
                        "data_type": "DateTime",
                        "is_hidden": False,
                        "description": "Date of sale",
                    },
                ],
                "row_count": 50000,
            },
            {
                "name": "Products",
                "columns": [
                    {
                        "name": "ProductID",
                        "data_type": "Int64",
                        "is_hidden": False,
                        "description": "Product identifier",
                    },
                    {
                        "name": "ProductName",
                        "data_type": "Text",
                        "is_hidden": False,
                        "description": "Product name",
                    },
                    {
                        "name": "Category",
                        "data_type": "Text",
                        "is_hidden": False,
                        "description": "Product category",
                    },
                    {
                        "name": "UnitPrice",
                        "data_type": "Decimal",
                        "is_hidden": False,
                        "description": "Unit price",
                    },
                ],
                "row_count": 500,
            },
        ],
        "relationships": [
            {
                "from_table": "Sales",
                "from_column": "ProductID",
                "to_table": "Products",
                "to_column": "ProductID",
                "cardinality": "Many-to-one",
                "is_active": True,
                "cross_filter_direction": "Single",
            }
        ],
        "measures": [
            {
                "name": "Total Sales",
                "table": "Sales",
                "expression": "SUM(Sales[SalesAmount])",
                "format_string": "$#,##0.00",
                "description": "Total sales amount",
                "is_hidden": False,
            },
            {
                "name": "Sales YTD",
                "table": "Sales",
                "expression": "CALCULATE([Total Sales], DATESYTD(Sales[OrderDate]))",
                "format_string": "$#,##0.00",
                "description": "Year-to-date sales",
                "is_hidden": False,
            },
        ],
        "calculated_columns": [
            {
                "name": "Sales Year",
                "table": "Sales",
                "expression": "YEAR(Sales[OrderDate])",
                "data_type": "Int64",
                "description": "Year of sale",
                "is_hidden": False,
            }
        ],
        "visualizations": [
            {
                "page": "Sales Overview",
                "visuals": [
                    {
                        "type": "clusteredColumnChart",
                        "title": "Sales by Category",
                        "fields": ["Products.Category", "Sales.Total Sales"],
                    },
                    {
                        "type": "card",
                        "title": "Total Revenue",
                        "fields": ["Sales.Total Sales"],
                    },
                ],
            }
        ],
        "power_query": {
            "Sales": 'let Source = Sql.Database("server01.company.com", "SalesDB") in Source'
        },
    }


def create_sample_tableau_metadata() -> Dict[str, Any]:
    """Create sample Tableau metadata for testing"""
    return {
        "file": "sample_dashboard.twbx",
        "type": "Tableau",
        "file_path": "/data/sample_dashboard.twbx",
        "data_sources": [
            {
                "name": "Superstore",
                "caption": "Sample Superstore Data",
                "connections": [
                    {
                        "server": "",
                        "database": "Superstore.xlsx",
                        "connection_type": "excel-direct",
                        "username": "",
                        "port": "",
                    }
                ],
                "fields": [
                    {
                        "name": "Sales",
                        "caption": "Sales",
                        "datatype": "real",
                        "role": "measure",
                        "type": "quantitative",
                        "is_calculated": False,
                        "calculation": None,
                        "description": "Sales amount",
                        "worksheets": ["Sales by Region", "Profit Analysis"],
                    },
                    {
                        "name": "Profit Ratio",
                        "caption": "Profit Ratio",
                        "datatype": "real",
                        "role": "measure",
                        "type": "quantitative",
                        "is_calculated": True,
                        "calculation": "SUM([Profit]) / SUM([Sales])",
                        "description": "Profit as percentage of sales",
                        "worksheets": ["Profit Analysis"],
                    },
                ],
            }
        ],
        "worksheets": [
            {
                "name": "Sales by Region",
                "data_source": "Superstore",
                "fields_used": ["Region", "Sales"],
                "filters": [],
                "parameters_used": [],
            },
            {
                "name": "Profit Analysis",
                "data_source": "Superstore",
                "fields_used": ["Category", "Profit", "Profit Ratio"],
                "filters": [],
                "parameters_used": [],
            },
        ],
        "dashboards": [
            {
                "name": "Executive Dashboard",
                "worksheets": ["Sales by Region", "Profit Analysis"],
                "objects": [
                    {"type": "worksheet", "name": "Sales by Region"},
                    {"type": "worksheet", "name": "Profit Analysis"},
                ],
            }
        ],
        "parameters": [],
        "calculated_fields": [
            {
                "name": "Profit Ratio",
                "datasource": "Superstore",
                "calculation": "SUM([Profit]) / SUM([Sales])",
                "datatype": "real",
                "role": "measure",
                "description": "Profit as percentage of sales",
                "worksheets_used": ["Profit Analysis"],
            }
        ],
        "field_usage": {
            "Sales": ["Sales by Region", "Profit Analysis"],
            "Profit": ["Profit Analysis"],
            "Region": ["Sales by Region"],
            "Category": ["Profit Analysis"],
        },
    }


def create_test_files(output_dir: Path):
    """Create test files for development and testing"""

    # Create sample metadata files
    powerbi_metadata = create_sample_powerbi_metadata()
    tableau_metadata = create_sample_tableau_metadata()

    # Write sample JSON files
    with open(output_dir / "sample_powerbi.json", "w", encoding="utf-8") as f:
        json.dump(powerbi_metadata, f, indent=2)

    with open(output_dir / "sample_tableau.json", "w", encoding="utf-8") as f:
        json.dump(tableau_metadata, f, indent=2)

    print(f"Test files created in {output_dir}")


if __name__ == "__main__":
    # Create test files when run directly
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    create_test_files(test_dir)
