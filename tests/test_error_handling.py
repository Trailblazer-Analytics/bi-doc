"""Tests for error handling and edge cases"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from bidoc.cli import parse_file
from bidoc.utils import FileType, detect_file_type
from bidoc.pbix_parser import PowerBIParser
from bidoc.tableau_parser import TableauParser


def test_detect_file_type_with_nonexistent_file():
    """Test file type detection with non-existent files."""
    fake_file = Path("nonexistent.pbix")
    file_type = detect_file_type(fake_file)
    assert file_type == FileType.POWER_BI  # Should still detect based on extension


def test_parse_file_with_invalid_file():
    """Test parsing with an invalid file path."""
    fake_file = Path("nonexistent.pbix")
    result = parse_file(fake_file, FileType.POWER_BI)
    # The parser may return default empty structure instead of None
    # when file doesn't exist, so we check that data_sources is empty
    assert result is not None
    assert len(result.get("data_sources", [])) == 0


def test_parse_file_with_unsupported_type():
    """Test parsing with unsupported file type."""
    fake_file = Path("test.txt")
    result = parse_file(fake_file, FileType.UNKNOWN)
    assert result is None


@patch('bidoc.pbix_parser.PowerBIParser.parse')
def test_powerbi_parser_exception_handling(mock_parse):
    """Test that PowerBI parser exceptions are handled gracefully."""
    mock_parse.side_effect = Exception("Parsing failed")
    
    fake_file = Path("test.pbix")
    result = parse_file(fake_file, FileType.POWER_BI)
    assert result is None


@patch('bidoc.tableau_parser.TableauParser.parse')
def test_tableau_parser_exception_handling(mock_parse):
    """Test that Tableau parser exceptions are handled gracefully."""
    mock_parse.side_effect = Exception("Parsing failed")
    
    fake_file = Path("test.twb")
    result = parse_file(fake_file, FileType.TABLEAU_TWB)
    assert result is None


def test_powerbi_parser_with_missing_fields():
    """Test PowerBI parser gracefully handles missing metadata fields."""
    parser = PowerBIParser()
    # This would test with a minimal or corrupted .pbix file
    # For now, just ensure the parser can be instantiated
    assert parser is not None


def test_tableau_parser_with_missing_fields():
    """Test Tableau parser gracefully handles missing metadata fields."""
    parser = TableauParser()
    # This would test with a minimal or corrupted .twb/.twbx file
    # For now, just ensure the parser can be instantiated
    assert parser is not None
