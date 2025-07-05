"""Tests for utility functions"""

from pathlib import Path

import pytest

from bidoc.utils import FileType, detect_file_type, format_file_size, sanitize_filename


@pytest.mark.parametrize(
    "file_name, expected_type",
    [
        ("report.pbix", FileType.POWER_BI),
        ("dashboard.twb", FileType.TABLEAU_TWB),
        ("analysis.twbx", FileType.TABLEAU_TWBX),
        ("data.txt", FileType.UNKNOWN),
        ("archive.zip", FileType.UNKNOWN),
    ],
)
def test_detect_file_type(file_name, expected_type):
    """Test that file types are detected correctly from file extensions."""
    assert detect_file_type(Path(file_name)) == expected_type


@pytest.mark.parametrize(
    "input_name, expected_name",
    [
        ("My Report: Final Version", "My Report_ Final Version"),
        ("file/with\\slashes", "file_with_slashes"),
        ("a*b?c>d<e|f", "a_b_c_d_e_f"),
        ('"quoted"', "_quoted_"),
        (" clean name ", "clean name"),
    ],
)
def test_sanitize_filename(input_name, expected_name):
    """Test the sanitization of filenames with invalid characters."""
    assert sanitize_filename(input_name) == expected_name


@pytest.mark.parametrize(
    "size_bytes, expected_format",
    [
        (0, "0 B"),
        (1023, "1023.0 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1610612736, "1.5 GB"),
    ],
)
def test_format_file_size(size_bytes, expected_format):
    """Test the human-readable formatting of file sizes."""
    assert format_file_size(size_bytes) == expected_format
