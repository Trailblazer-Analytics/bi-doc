"""Tests for the command-line interface"""

from click.testing import CliRunner
from bidoc.cli import main
import os


def test_cli_runs_successfully():
    """Test that the CLI runs without crashing on a sample file."""
    runner = CliRunner()
    # Use a known sample file for testing
    sample_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "samples",
            "power_bi",
            "COVID-19 US Tracking Sample.pbix",
        )
    )
    result = runner.invoke(main, ["--input", sample_file, "--output", "test_output", "--verbose"])
    
    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.output}")
        print(f"Exception: {result.exception}")
        if result.exception:
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
    
    assert result.exit_code == 0
    assert "Processing complete" in result.output or "Successfully processed" in result.output
