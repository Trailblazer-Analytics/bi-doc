import pytest
from bidoc.tableau_parser import TableauParser
import os
from pathlib import Path

# Define the path to the sample Tableau file
SAMPLE_FILE_PATH = str(Path(__file__).parent.parent / 'samples' / 'Tableau' / 'CH2_BBOD_CourseMetrics_v2.twbx')

@pytest.fixture
def tableau_parser():
    """Provides an instance of the TableauParser."""
    return TableauParser()

@pytest.fixture
def parsed_tableau_data(tableau_parser):
    """Provides parsed data from the sample Tableau file."""
    return tableau_parser.parse(Path(SAMPLE_FILE_PATH))

def test_initialization(tableau_parser):
    """Tests that the TableauParser initializes correctly."""
    assert tableau_parser is not None

def test_data_source_extraction(parsed_tableau_data):
    """Tests the extraction of data source information."""
    data_sources = parsed_tableau_data['data_sources']
    assert isinstance(data_sources, list)
    assert len(data_sources) > 0

    # Check for a known data source
    students_source = next((ds for ds in data_sources if ds['caption'] == 'Students (Course Metrics Dashboard Data)'), None)
    assert students_source is not None
    assert students_source['connections'][0]['connection_type'] == 'excel-direct'

def test_worksheet_extraction(parsed_tableau_data):
    """Tests the extraction of worksheet information."""
    worksheets = parsed_tableau_data['worksheets']
    assert isinstance(worksheets, list)
    assert len(worksheets) > 0

    # Check for known worksheets
    worksheet_names = [w['name'] for w in worksheets]
    assert 'Classes' in worksheet_names
    assert 'Enrollments' in worksheet_names

def test_dashboard_extraction(parsed_tableau_data):
    """Tests the extraction of dashboard information."""
    dashboards = parsed_tableau_data['dashboards']
    assert isinstance(dashboards, list)
    assert len(dashboards) > 0

    # Check for a known dashboard
    dashboard_names = [d['name'] for d in dashboards]
    assert 'Course Metrics Dashboard' in dashboard_names
