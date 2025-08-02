"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark"
    )
    config.addinivalue_line(
        "markers", "stress: mark test as a stress test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file names."""
    for item in items:
        # Add markers based on test file names
        if "test_performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
        if "test_security" in item.fspath.basename:
            item.add_marker(pytest.mark.security)
        if "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to performance and stress tests
        if any(marker in item.keywords for marker in ["performance", "stress"]):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# Skip tests requiring expensive operations in fast test runs
def pytest_runtest_setup(item):
    """Skip expensive tests when running fast tests."""
    if item.config.getoption("--fast", default=False):
        if "performance" in item.keywords or "stress" in item.keywords:
            pytest.skip("Skipping expensive test in fast mode")


def pytest_addoption(parser):
    """Add command line options for test execution."""
    parser.addoption(
        "--fast",
        action="store_true", 
        default=False,
        help="Run only fast tests, skip performance and stress tests"
    )
    parser.addoption(
        "--security-only",
        action="store_true",
        default=False,
        help="Run only security tests"
    )
    parser.addoption(
        "--performance-only", 
        action="store_true",
        default=False,
        help="Run only performance tests"
    )