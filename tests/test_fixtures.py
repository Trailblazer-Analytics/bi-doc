"""Test fixtures and utilities for BI Documentation Tool tests."""

import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pytest


class MockPBIXFile:
    """Mock .pbix file for testing."""
    
    def __init__(self, name: str = "test.pbix"):
        self.name = name
        self.content = {
            "model_info": {
                "name": "Test Model",
                "description": "Test Description",
                "culture": "en-US"
            },
            "data_sources": [
                {
                    "name": "Test Source",
                    "type": "SQL Server",
                    "connection": "test-server.database.windows.net"
                }
            ],
            "tables": [
                {
                    "name": "Sales",
                    "columns": [
                        {"name": "SalesID", "data_type": "Int64", "is_hidden": False},
                        {"name": "Amount", "data_type": "Decimal", "is_hidden": False}
                    ],
                    "row_count": 1000
                }
            ],
            "measures": [
                {
                    "name": "Total Sales",
                    "table": "Sales",
                    "expression": "SUM(Sales[Amount])",
                    "data_type": "Currency"
                }
            ]
        }
    
    def create_file(self, directory: Path) -> Path:
        """Create a mock .pbix file in the specified directory."""
        file_path = directory / self.name
        
        # Create a minimal zip file structure
        with zipfile.ZipFile(file_path, 'w') as zf:
            zf.writestr("DataModel", '{"version": "1.0"}')
            zf.writestr("Report/Layout", '{"sections": []}')
            zf.writestr("Connections", '[]')
        
        return file_path


class MockTableauFile:
    """Mock Tableau file for testing."""
    
    def __init__(self, name: str = "test.twbx", file_type: str = "twbx"):
        self.name = name
        self.file_type = file_type
        self.content = {
            "data_sources": [
                {
                    "name": "Test Data",
                    "caption": "Test Data Source",
                    "connections": [
                        {
                            "connection_type": "postgres",
                            "server": "localhost",
                            "database": "testdb"
                        }
                    ],
                    "fields": [
                        {
                            "name": "Category", 
                            "caption": "Product Category",
                            "datatype": "string",
                            "role": "dimension",
                            "type": "nominal"
                        }
                    ]
                }
            ],
            "worksheets": [
                {
                    "name": "Sales Dashboard",
                    "data_source": "Test Data",
                    "fields_used": ["Category", "Sales"]
                }
            ]
        }
    
    def create_file(self, directory: Path) -> Path:
        """Create a mock Tableau file in the specified directory."""
        file_path = directory / self.name
        
        if self.file_type == "twbx":
            # Create a ZIP file with a .twb inside
            with zipfile.ZipFile(file_path, 'w') as zf:
                twb_content = '''<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <datasources>
    <datasource caption='Test Data'>
      <connection class='postgres' />
    </datasource>
  </datasources>
  <worksheets>
    <worksheet name='Sales Dashboard' />
  </worksheets>
</workbook>'''
                zf.writestr("test.twb", twb_content)
        else:
            # Create a plain .twb file
            twb_content = '''<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <datasources>
    <datasource caption='Test Data'>
      <connection class='postgres' />
    </datasource>
  </datasources>
</workbook>'''
            file_path.write_text(twb_content)
        
        return file_path


@pytest.fixture
def temp_directory():
    """Create and cleanup a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_pbix_file(temp_directory):
    """Create a mock .pbix file for testing."""
    mock_file = MockPBIXFile()
    file_path = mock_file.create_file(temp_directory)
    return file_path, mock_file.content


@pytest.fixture
def mock_tableau_twbx_file(temp_directory):
    """Create a mock .twbx file for testing."""
    mock_file = MockTableauFile("test.twbx", "twbx")
    file_path = mock_file.create_file(temp_directory)
    return file_path, mock_file.content


@pytest.fixture
def mock_tableau_twb_file(temp_directory):
    """Create a mock .twb file for testing."""
    mock_file = MockTableauFile("test.twb", "twb")
    file_path = mock_file.create_file(temp_directory)
    return file_path, mock_file.content


@pytest.fixture
def sample_powerbi_metadata():
    """Return sample PowerBI metadata for testing."""
    return {
        "file": "sample.pbix",
        "type": "Power BI",
        "file_path": "/path/to/sample.pbix",
        "file_size": 1024000,
        "last_modified": "2024-01-01T00:00:00",
        "model_info": {
            "name": "Sales Model",
            "description": "Comprehensive sales analysis model",
            "culture": "en-US"
        },
        "data_sources": [
            {
                "name": "Sales Database",
                "type": "SQL Server",
                "connection": "sales-server.database.windows.net",
                "tables": ["Sales", "Products", "Customers"]
            }
        ],
        "tables": [
            {
                "name": "Sales",
                "columns": [
                    {"name": "SalesID", "data_type": "Int64", "is_hidden": False, "description": "Unique sales identifier"},
                    {"name": "ProductID", "data_type": "Int64", "is_hidden": False, "description": "Product identifier"},
                    {"name": "Amount", "data_type": "Decimal", "is_hidden": False, "description": "Sales amount"}
                ],
                "row_count": 50000
            }
        ],
        "measures": [
            {
                "name": "Total Sales",
                "table": "Sales",
                "expression": "SUM(Sales[Amount])",
                "expression_formatted": "SUM ( Sales[Amount] )",
                "data_type": "Currency",
                "format_string": "$#,##0.00",
                "description": "Total sales amount"
            }
        ],
        "relationships": [
            {
                "from_table": "Sales",
                "from_column": "ProductID", 
                "to_table": "Products",
                "to_column": "ProductID",
                "cardinality": "Many-to-One",
                "is_active": True,
                "cross_filter_direction": "Single"
            }
        ],
        "visualizations": [
            {
                "page": "Sales Overview",
                "visuals": [
                    {
                        "title": "Sales by Category",
                        "type": "Column Chart",
                        "fields": ["Products[Category]", "Total Sales"]
                    }
                ]
            }
        ]
    }


@pytest.fixture 
def sample_tableau_metadata():
    """Return sample Tableau metadata for testing."""
    return {
        "file": "sample.twbx",
        "type": "Tableau", 
        "file_path": "/path/to/sample.twbx",
        "file_size": 2048000,
        "last_modified": "2024-01-01T00:00:00",
        "data_sources": [
            {
                "name": "Sales Data",
                "caption": "Sales Analysis Data",
                "connections": [
                    {
                        "connection_type": "postgres", 
                        "server": "localhost",
                        "database": "sales_db",
                        "port": 5432,
                        "username": "analyst"
                    }
                ],
                "fields": [
                    {
                        "name": "Category",
                        "caption": "Product Category", 
                        "datatype": "string",
                        "role": "dimension",
                        "type": "nominal",
                        "is_calculated": False
                    },
                    {
                        "name": "Sales",
                        "caption": "Sales Amount",
                        "datatype": "real", 
                        "role": "measure",
                        "type": "quantitative",
                        "is_calculated": False
                    }
                ]
            }
        ],
        "calculated_fields": [
            {
                "name": "Profit Margin",
                "datasource": "Sales Data",
                "datatype": "real",
                "role": "measure", 
                "calculation": "([Profit] / [Sales]) * 100",
                "calculation_formatted": "([Profit] / [Sales]) * 100",
                "description": "Profit margin percentage"
            }
        ],
        "worksheets": [
            {
                "name": "Sales Dashboard",
                "data_source": "Sales Data",
                "fields_used": ["Category", "Sales", "Profit Margin"],
                "filters": [
                    {"field": "Year", "value": "2024"}
                ]
            }
        ],
        "dashboards": [
            {
                "name": "Executive Dashboard",
                "worksheets": ["Sales Dashboard", "Profit Analysis"],
                "objects": [
                    {"type": "text", "name": "Title"},
                    {"type": "image", "name": "Company Logo"}
                ]
            }
        ]
    }


class MockPBIXRay:
    """Mock PBIXRay for testing without actual dependencies."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tables = [
            Mock(name="Sales", columns=[
                Mock(name="SalesID", data_type="Int64"),
                Mock(name="Amount", data_type="Decimal")
            ])
        ]
        self.measures = [
            Mock(name="Total Sales", table="Sales", expression="SUM(Sales[Amount])")
        ]
    
    def get_model_info(self):
        return {"name": "Test Model", "culture": "en-US"}


class MockTableauWorkbook:
    """Mock Tableau Workbook for testing without actual dependencies."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.datasources = [
            Mock(name="Test Data", caption="Test Data Source")
        ]
        self.worksheets = [
            Mock(name="Sales Dashboard")
        ]


def create_malicious_zip(file_path: Path, zip_bomb: bool = False, path_traversal: bool = False) -> Path:
    """Create a malicious ZIP file for security testing."""
    with zipfile.ZipFile(file_path, 'w') as zf:
        if zip_bomb:
            # Create a file with high compression ratio
            large_content = "0" * (10 * 1024 * 1024)  # 10MB of zeros
            zf.writestr("bomb.txt", large_content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        
        if path_traversal:
            # Create files with path traversal attempts
            zf.writestr("../../../etc/passwd", "malicious content")
            zf.writestr("normal.txt", "normal content")
    
    return file_path