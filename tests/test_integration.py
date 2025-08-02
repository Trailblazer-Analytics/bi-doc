"""Integration tests for the BI Documentation Tool."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bidoc.cli import main, parse_file, generate_outputs
from bidoc.constants import MARKDOWN_FORMAT, JSON_FORMAT
from bidoc.markdown_generator import MarkdownGenerator
from bidoc.json_generator import JSONGenerator
from bidoc.utils import detect_file_type, FileType

from .test_fixtures import (
    MockPBIXFile,
    MockTableauFile,
    sample_powerbi_metadata,
    sample_tableau_metadata
)


class TestEndToEndProcessing:
    """Test complete end-to-end processing workflows."""
    
    def test_powerbi_file_processing(self, temp_directory, sample_powerbi_metadata):
        """Test complete PowerBI file processing workflow."""
        # Create mock file
        mock_file = MockPBIXFile("test.pbix")
        pbix_path = mock_file.create_file(temp_directory)
        
        # Mock the parser to return our sample metadata
        with patch('bidoc.cli.PowerBIParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = sample_powerbi_metadata
            mock_parser_class.return_value = mock_parser
            
            # Test file type detection
            file_type = detect_file_type(pbix_path)
            assert file_type == FileType.POWER_BI
            
            # Test parsing
            metadata = parse_file(pbix_path, file_type)
            assert metadata is not None
            assert metadata["type"] == "Power BI"
            assert metadata["file"] == "sample.pbix"
            assert len(metadata["data_sources"]) > 0
            assert len(metadata["tables"]) > 0
            assert len(metadata["measures"]) > 0
    
    def test_tableau_file_processing(self, temp_directory, sample_tableau_metadata):
        """Test complete Tableau file processing workflow."""
        # Create mock file
        mock_file = MockTableauFile("test.twbx", "twbx")
        twbx_path = mock_file.create_file(temp_directory)
        
        # Mock the parser to return our sample metadata
        with patch('bidoc.cli.TableauParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = sample_tableau_metadata
            mock_parser_class.return_value = mock_parser
            
            # Test file type detection
            file_type = detect_file_type(twbx_path)
            assert file_type == FileType.TABLEAU_TWBX
            
            # Test parsing
            metadata = parse_file(twbx_path, file_type)
            assert metadata is not None
            assert metadata["type"] == "Tableau"
            assert metadata["file"] == "sample.twbx"
            assert len(metadata["data_sources"]) > 0
            assert len(metadata["worksheets"]) > 0
    
    def test_output_generation(self, temp_directory, sample_powerbi_metadata):
        """Test output generation in both formats."""
        output_dir = temp_directory / "output"
        output_dir.mkdir()
        
        # Test Markdown generation
        generate_outputs(sample_powerbi_metadata, output_dir, "test", MARKDOWN_FORMAT)
        
        markdown_file = output_dir / "test.md"
        assert markdown_file.exists()
        
        content = markdown_file.read_text()
        assert "# Documentation for sample.pbix" in content
        assert "## Data Sources" in content
        assert "## Tables and Fields" in content
        assert "## Measures" in content
        
        # Test JSON generation
        generate_outputs(sample_powerbi_metadata, output_dir, "test", JSON_FORMAT)
        
        json_file = output_dir / "test.json"
        assert json_file.exists()
        
        json_content = json.loads(json_file.read_text())
        assert json_content["type"] == "Power BI"
        assert "data_sources" in json_content
        assert "tables" in json_content
    
    def test_cli_integration(self, temp_directory, sample_powerbi_metadata):
        """Test CLI integration with mocked dependencies."""
        # Create mock file
        mock_file = MockPBIXFile("integration_test.pbix")
        pbix_path = mock_file.create_file(temp_directory)
        
        output_dir = temp_directory / "cli_output"
        
        # Mock the parser
        with patch('bidoc.cli.PowerBIParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = sample_powerbi_metadata
            mock_parser_class.return_value = mock_parser
            
            # Mock click context to avoid CLI execution
            with patch('bidoc.cli.click.echo'):
                with patch('bidoc.cli.sys.exit') as mock_exit:
                    # Test CLI processing
                    try:
                        main(
                            input_files=(str(pbix_path),),
                            output_dir=str(output_dir),
                            output_format="all",
                            verbose=False,
                            log_file=False,
                            with_summary=False,
                            config_path=None
                        )
                    except SystemExit:
                        pass  # Expected for successful completion
            
            # Verify outputs were created
            assert output_dir.exists()
            assert (output_dir / "integration_test.md").exists()
            assert (output_dir / "integration_test.json").exists()


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_unsupported_file_type(self, temp_directory):
        """Test handling of unsupported file types."""
        # Create a file with unsupported extension
        unsupported_file = temp_directory / "test.xlsx"
        unsupported_file.write_text("dummy content")
        
        file_type = detect_file_type(unsupported_file)
        assert file_type == FileType.UNKNOWN
        
        result = parse_file(unsupported_file, file_type)
        assert result is None
    
    def test_missing_file(self, temp_directory):
        """Test handling of missing files."""
        missing_file = temp_directory / "nonexistent.pbix"
        
        result = parse_file(missing_file, FileType.POWER_BI)
        assert result is None
    
    def test_parser_failure(self, temp_directory):
        """Test handling of parser failures."""
        # Create mock file
        mock_file = MockPBIXFile("failing.pbix")
        pbix_path = mock_file.create_file(temp_directory)
        
        # Mock parser to raise an exception
        with patch('bidoc.cli.PowerBIParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.side_effect = Exception("Parser failed")
            mock_parser_class.return_value = mock_parser
            
            result = parse_file(pbix_path, FileType.POWER_BI)
            assert result is None
    
    def test_output_write_failure(self, temp_directory, sample_powerbi_metadata):
        """Test handling of output write failures."""
        # Create a read-only directory
        output_dir = temp_directory / "readonly"
        output_dir.mkdir()
        
        # Make directory read-only (on Unix systems)
        try:
            output_dir.chmod(0o444)
            
            # Attempt to generate outputs (should handle gracefully)
            try:
                generate_outputs(sample_powerbi_metadata, output_dir, "test", MARKDOWN_FORMAT)
            except Exception:
                # Should not propagate unhandled exceptions
                pytest.fail("Output generation should handle write failures gracefully")
        finally:
            # Restore permissions for cleanup
            try:
                output_dir.chmod(0o755)
            except:
                pass


class TestPerformance:
    """Performance and scalability tests."""
    
    def test_large_metadata_processing(self, temp_directory):
        """Test processing of large metadata structures."""
        # Create large metadata structure
        large_metadata = {
            "file": "large_model.pbix",
            "type": "Power BI",
            "file_path": "/path/to/large_model.pbix",
            "data_sources": [],
            "tables": [],
            "measures": [],
            "relationships": []
        }
        
        # Add many tables
        for i in range(100):
            table = {
                "name": f"Table_{i:03d}",
                "columns": [
                    {"name": f"Column_{j:03d}", "data_type": "String", "is_hidden": False}
                    for j in range(50)
                ],
                "row_count": 10000
            }
            large_metadata["tables"].append(table)
        
        # Add many measures
        for i in range(200):
            measure = {
                "name": f"Measure_{i:03d}",
                "table": f"Table_{i % 100:03d}",
                "expression": f"SUM(Table_{i % 100:03d}[Column_000])",
                "data_type": "Decimal"
            }
            large_metadata["measures"].append(measure)
        
        # Test generation performance
        import time
        
        # Test Markdown generation
        start_time = time.time()
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(large_metadata)
        markdown_time = time.time() - start_time
        
        assert len(markdown_content) > 10000  # Should generate substantial content
        assert markdown_time < 30  # Should complete within 30 seconds
        
        # Test JSON generation
        start_time = time.time()
        json_gen = JSONGenerator()
        json_content = json_gen.generate(large_metadata)
        json_time = time.time() - start_time
        
        assert len(json_content) > 10000  # Should generate substantial content
        assert json_time < 10  # Should complete within 10 seconds
    
    def test_multiple_file_processing(self, temp_directory):
        """Test processing multiple files sequentially."""
        # Create multiple mock files
        files = []
        for i in range(5):
            mock_file = MockPBIXFile(f"test_{i:02d}.pbix")
            pbix_path = mock_file.create_file(temp_directory)
            files.append(pbix_path)
        
        output_dir = temp_directory / "multi_output"
        
        # Mock the parser for all files
        with patch('bidoc.cli.PowerBIParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = {
                "file": "test.pbix",
                "type": "Power BI", 
                "data_sources": [],
                "tables": [],
                "measures": []
            }
            mock_parser_class.return_value = mock_parser
            
            # Process all files
            import time
            start_time = time.time()
            
            with patch('bidoc.cli.click.echo'):
                with patch('bidoc.cli.sys.exit'):
                    try:
                        main(
                            input_files=tuple(str(f) for f in files),
                            output_dir=str(output_dir),
                            output_format="markdown",
                            verbose=False,
                            log_file=False,
                            with_summary=False,
                            config_path=None
                        )
                    except SystemExit:
                        pass
            
            processing_time = time.time() - start_time
            
            # Verify all files were processed
            assert output_dir.exists()
            for i in range(5):
                assert (output_dir / f"test_{i:02d}.md").exists()
            
            # Should process all files within reasonable time
            assert processing_time < 60  # Within 60 seconds


class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_metadata_completeness(self, sample_powerbi_metadata):
        """Test that generated outputs contain all expected metadata."""
        # Generate Markdown
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(sample_powerbi_metadata)
        
        # Check for key sections in markdown
        expected_sections = [
            "# Documentation for",
            "## Overview", 
            "## Data Sources",
            "## Tables and Fields",
            "## Measures",
            "## Relationships"
        ]
        
        for section in expected_sections:
            assert section in markdown_content, f"Missing section: {section}"
        
        # Generate JSON
        json_gen = JSONGenerator()
        json_content = json_gen.generate(sample_powerbi_metadata)
        json_data = json.loads(json_content)
        
        # Check for key fields in JSON
        expected_fields = [
            "file", "type", "file_path", "data_sources", 
            "tables", "measures", "relationships"
        ]
        
        for field in expected_fields:
            assert field in json_data, f"Missing field: {field}"
    
    def test_data_type_consistency(self, sample_tableau_metadata):
        """Test that data types are consistently handled."""
        json_gen = JSONGenerator()
        json_content = json_gen.generate(sample_tableau_metadata)
        json_data = json.loads(json_content)
        
        # Check data types
        assert isinstance(json_data["file"], str)
        assert isinstance(json_data["data_sources"], list)
        assert isinstance(json_data["worksheets"], list)
        
        if json_data["data_sources"]:
            datasource = json_data["data_sources"][0]
            assert isinstance(datasource["name"], str)
            assert isinstance(datasource["fields"], list)
    
    def test_unicode_handling(self, temp_directory):
        """Test handling of unicode characters in metadata."""
        unicode_metadata = {
            "file": "测试文件.pbix",  # Chinese characters
            "type": "Power BI",
            "data_sources": [
                {
                    "name": "Données Françaises",  # French accents
                    "description": "Descripción en Español"  # Spanish characters
                }
            ],
            "tables": [
                {
                    "name": "Ταμπλό",  # Greek characters
                    "columns": [
                        {"name": "العمود", "data_type": "String"}  # Arabic characters
                    ]
                }
            ]
        }
        
        # Test Markdown generation with unicode
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(unicode_metadata)
        
        assert "测试文件.pbix" in markdown_content
        assert "Données Françaises" in markdown_content
        assert "Descripción en Español" in markdown_content
        
        # Test JSON generation with unicode
        json_gen = JSONGenerator()
        json_content = json_gen.generate(unicode_metadata)
        json_data = json.loads(json_content)
        
        assert json_data["file"] == "测试文件.pbix"
        assert "العمود" in json_content  # Arabic should be preserved