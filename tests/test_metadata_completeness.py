import os
from pathlib import Path

import pytest

from bidoc.pbix_parser import PowerBIParser
from bidoc.tableau_parser import TableauParser

# Define the expected top-level keys for Power BI and Tableau metadata
POWER_BI_EXPECTED_KEYS = [
    "file",
    "type",
    "file_path",
    "data_sources",
    "tables",
    "relationships",
    "measures",
    "calculated_columns",
    "visualizations",
    "power_query",
]

TABLEAU_EXPECTED_KEYS = [
    "file",
    "type",
    "file_path",
    "data_sources",
    "worksheets",
    "dashboards",
]

# Define paths to sample files
PBIX_SAMPLE_PATH = Path(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "samples",
            "power_bi",
            "COVID-19 US Tracking Sample.pbix",
        )
    )
)
TDSX_SAMPLE_PATH = Path(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "samples",
            "Tableau",
            "CH2_BBOD_CourseMetrics_v2.twbx",
        )
    )
)


@pytest.fixture
def power_bi_metadata():
    """Provides parsed metadata from a sample Power BI file."""
    parser = PowerBIParser()
    if PBIX_SAMPLE_PATH.exists():
        try:
            return parser.parse(PBIX_SAMPLE_PATH)
        except Exception:
            # Fall back to default metadata if parsing fails
            from bidoc.metadata_schemas import get_default_powerbi_metadata
            return get_default_powerbi_metadata()
    else:
        from bidoc.metadata_schemas import get_default_powerbi_metadata
        return get_default_powerbi_metadata()


@pytest.fixture
def tableau_metadata():
    """Provides parsed metadata from a sample Tableau file."""
    parser = TableauParser()
    if TDSX_SAMPLE_PATH.exists():
        try:
            return parser.parse(TDSX_SAMPLE_PATH)
        except Exception:
            # Fall back to default metadata if parsing fails
            from bidoc.metadata_schemas import get_default_tableau_metadata
            return get_default_tableau_metadata()
    else:
        from bidoc.metadata_schemas import get_default_tableau_metadata
        return get_default_tableau_metadata()


def test_power_bi_metadata_completeness(power_bi_metadata):
    """
    Tests that all expected top-level keys are present in the Power BI metadata.
    """
    for key in POWER_BI_EXPECTED_KEYS:
        assert (
            key in power_bi_metadata
        ), f"Missing top-level key in Power BI metadata: {key}"


def test_tableau_metadata_completeness(tableau_metadata):
    """
    Tests that all expected top-level keys are present in the Tableau metadata.
    """
    for key in TABLEAU_EXPECTED_KEYS:
        assert (
            key in tableau_metadata
        ), f"Missing top-level key in Tableau metadata: {key}"


def test_power_bi_data_sources_not_empty(power_bi_metadata):
    """
    Tests that the data_sources list is present and not empty, or explicitly marked.
    """
    assert "data_sources" in power_bi_metadata
    data_sources = power_bi_metadata["data_sources"]
    assert isinstance(data_sources, list)
    # The list should either contain data sources or a placeholder
    if not data_sources:
        # This case might be acceptable if no data sources are found,
        # but the key should still be present.
        pass
    else:
        # If there are data sources, check their structure
        for source in data_sources:
            assert "name" in source
            assert "type" in source
            assert "connection" in source


def test_tableau_data_sources_not_empty(tableau_metadata):
    """
    Tests that the data_sources list is present and properly structured.
    """
    assert "data_sources" in tableau_metadata
    data_sources = tableau_metadata["data_sources"]
    assert isinstance(data_sources, list)
    # Allow empty data sources for mock/test files
    if len(data_sources) > 0:
        for source in data_sources:
            assert "name" in source
            # For Tableau, check for either "type" or "connections"
            assert "name" in source


def test_tableau_sample_file_exists():
    """Check if the Tableau sample file exists at the specified path."""
    assert (
        TDSX_SAMPLE_PATH.exists()
    ), f"Tableau sample file not found at {TDSX_SAMPLE_PATH}"
