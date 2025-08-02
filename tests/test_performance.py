"""Performance benchmarks and stress tests for BI Documentation Tool."""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from bidoc.markdown_generator import MarkdownGenerator
from bidoc.json_generator import JSONGenerator
from bidoc.pbix_parser import PowerBIParser
from bidoc.tableau_parser import TableauParser

from .test_fixtures import MockPBIXFile, MockTableauFile, sample_powerbi_metadata


class TestPerformanceBenchmarks:
    """Performance benchmarks for key operations."""
    
    @pytest.mark.performance
    def test_markdown_generation_benchmark(self, sample_powerbi_metadata):
        """Benchmark markdown generation performance."""
        # Create large metadata structure
        large_metadata = self._create_large_metadata(
            tables=50, columns_per_table=20, measures=100, relationships=75
        )
        
        markdown_gen = MarkdownGenerator()
        
        # Warm up
        _ = markdown_gen.generate(sample_powerbi_metadata)
        
        # Benchmark
        start_time = time.time()
        result = markdown_gen.generate(large_metadata)
        end_time = time.time()
        
        execution_time = end_time - start_time
        content_length = len(result)
        
        # Assertions
        assert execution_time < 5.0, f"Markdown generation took {execution_time:.2f}s, expected < 5.0s"
        assert content_length > 50000, f"Generated content too small: {content_length} chars"
        
        # Calculate performance metrics
        throughput = content_length / execution_time  # chars per second
        assert throughput > 10000, f"Throughput too low: {throughput:.0f} chars/s"
        
        print(f"\nMarkdown Generation Performance:")
        print(f"  Execution time: {execution_time:.3f}s")
        print(f"  Content length: {content_length:,} characters")
        print(f"  Throughput: {throughput:,.0f} chars/second")
    
    @pytest.mark.performance
    def test_json_generation_benchmark(self, sample_powerbi_metadata):
        """Benchmark JSON generation performance."""
        # Create large metadata structure
        large_metadata = self._create_large_metadata(
            tables=100, columns_per_table=30, measures=200, relationships=150
        )
        
        json_gen = JSONGenerator()
        
        # Warm up
        _ = json_gen.generate(sample_powerbi_metadata)
        
        # Benchmark
        start_time = time.time()
        result = json_gen.generate(large_metadata)
        end_time = time.time()
        
        execution_time = end_time - start_time
        content_length = len(result)
        
        # Assertions
        assert execution_time < 2.0, f"JSON generation took {execution_time:.2f}s, expected < 2.0s"
        assert content_length > 100000, f"Generated content too small: {content_length} chars"
        
        # Validate JSON structure
        json_data = json.loads(result)
        assert len(json_data["tables"]) == 100
        assert len(json_data["measures"]) == 200
        
        # Calculate performance metrics
        throughput = content_length / execution_time
        assert throughput > 50000, f"Throughput too low: {throughput:.0f} chars/s"
        
        print(f"\nJSON Generation Performance:")
        print(f"  Execution time: {execution_time:.3f}s")
        print(f"  Content length: {content_length:,} characters")
        print(f"  Throughput: {throughput:,.0f} chars/second")
    
    @pytest.mark.performance
    def test_memory_usage_large_metadata(self):
        """Test memory usage with large metadata structures."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create very large metadata structure
        large_metadata = self._create_large_metadata(
            tables=200, columns_per_table=50, measures=500, relationships=300
        )
        
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate outputs
        markdown_gen = MarkdownGenerator()
        json_gen = JSONGenerator()
        
        markdown_result = markdown_gen.generate(large_metadata)
        json_result = json_gen.generate(large_metadata)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory usage assertions
        creation_memory_delta = after_creation_memory - initial_memory
        total_memory_delta = final_memory - initial_memory
        
        assert creation_memory_delta < 100, f"Metadata creation used {creation_memory_delta:.1f}MB, expected < 100MB"
        assert total_memory_delta < 200, f"Total memory usage {total_memory_delta:.1f}MB, expected < 200MB"
        
        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.1f}MB")
        print(f"  After metadata creation: {after_creation_memory:.1f}MB (+{creation_memory_delta:.1f}MB)")
        print(f"  After generation: {final_memory:.1f}MB (+{total_memory_delta:.1f}MB total)")
        print(f"  Markdown size: {len(markdown_result):,} chars")
        print(f"  JSON size: {len(json_result):,} chars")
    
    @pytest.mark.performance
    def test_concurrent_processing_simulation(self, temp_directory):
        """Simulate concurrent processing of multiple files."""
        import threading
        import queue
        
        # Create multiple mock files
        files = []
        for i in range(10):
            mock_file = MockPBIXFile(f"concurrent_{i:02d}.pbix")
            pbix_path = mock_file.create_file(temp_directory)
            files.append(pbix_path)
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def process_file(file_path):
            """Process a single file in a thread."""
            try:
                start_time = time.time()
                
                # Mock processing
                with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
                    mock_model = Mock()
                    mock_pbixray.return_value = mock_model
                    
                    # Simulate some processing time
                    time.sleep(0.1)
                    
                    # Create sample result
                    metadata = {
                        "file": file_path.name,
                        "type": "Power BI",
                        "processing_time": time.time() - start_time
                    }
                    
                    results.put(metadata)
            except Exception as e:
                errors.put((file_path, str(e)))
        
        # Process files in parallel
        threads = []
        start_time = time.time()
        
        for file_path in files:
            thread = threading.Thread(target=process_file, args=(file_path,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        processed_files = []
        while not results.empty():
            processed_files.append(results.get())
        
        processing_errors = []
        while not errors.empty():
            processing_errors.append(errors.get())
        
        # Assertions
        assert len(processing_errors) == 0, f"Processing errors: {processing_errors}"
        assert len(processed_files) == 10, f"Expected 10 files, processed {len(processed_files)}"
        assert total_time < 5.0, f"Concurrent processing took {total_time:.2f}s, expected < 5.0s"
        
        avg_processing_time = sum(f["processing_time"] for f in processed_files) / len(processed_files)
        
        print(f"\nConcurrent Processing:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Files processed: {len(processed_files)}")
        print(f"  Average processing time: {avg_processing_time:.3f}s")
        print(f"  Throughput: {len(processed_files) / total_time:.1f} files/second")
    
    def _create_large_metadata(self, tables: int, columns_per_table: int, 
                             measures: int, relationships: int) -> dict:
        """Create large metadata structure for performance testing."""
        metadata = {
            "file": "large_model.pbix",
            "type": "Power BI",
            "file_path": "/path/to/large_model.pbix",
            "file_size": 50 * 1024 * 1024,  # 50MB
            "model_info": {
                "name": "Performance Test Model",
                "description": f"Large model with {tables} tables, {measures} measures",
                "culture": "en-US"
            },
            "data_sources": [
                {
                    "name": f"DataSource_{i:03d}",
                    "type": "SQL Server" if i % 2 == 0 else "Azure SQL",
                    "connection": f"server-{i:03d}.database.windows.net",
                    "tables": [f"Table_{j:03d}" for j in range(i * 5, (i + 1) * 5)]
                }
                for i in range(min(10, tables // 5))
            ],
            "tables": [],
            "measures": [],
            "relationships": [],
            "calculated_columns": [],
            "visualizations": []
        }
        
        # Generate tables
        for i in range(tables):
            table = {
                "name": f"Table_{i:03d}",
                "description": f"Performance test table {i}",
                "columns": [],
                "row_count": 10000 + (i * 1000)
            }
            
            # Generate columns
            for j in range(columns_per_table):
                column = {
                    "name": f"Column_{j:03d}",
                    "data_type": ["String", "Integer", "Decimal", "DateTime", "Boolean"][j % 5],
                    "is_hidden": j % 10 == 0,
                    "description": f"Column {j} in table {i}"
                }
                table["columns"].append(column)
            
            metadata["tables"].append(table)
        
        # Generate measures
        for i in range(measures):
            table_idx = i % tables
            measure = {
                "name": f"Measure_{i:03d}",
                "table": f"Table_{table_idx:03d}",
                "expression": f"SUM(Table_{table_idx:03d}[Column_000])",
                "expression_formatted": f"SUM ( Table_{table_idx:03d}[Column_000] )",
                "data_type": ["Currency", "Decimal", "Integer", "Percentage"][i % 4],
                "format_string": ["$#,##0.00", "#,##0.00", "#,##0", "0.00%"][i % 4],
                "description": f"Performance test measure {i}",
                "is_hidden": i % 20 == 0
            }
            metadata["measures"].append(measure)
        
        # Generate relationships
        for i in range(relationships):
            from_table_idx = i % tables
            to_table_idx = (i + 1) % tables
            
            relationship = {
                "from_table": f"Table_{from_table_idx:03d}",
                "from_column": "Column_000",
                "to_table": f"Table_{to_table_idx:03d}",
                "to_column": "Column_000",
                "cardinality": ["One-to-Many", "Many-to-One", "One-to-One"][i % 3],
                "is_active": i % 5 != 0,
                "cross_filter_direction": ["Single", "Both"][i % 2]
            }
            metadata["relationships"].append(relationship)
        
        # Generate visualizations
        for i in range(min(20, tables // 5)):
            page = {
                "page": f"Page_{i:02d}",
                "visuals": [
                    {
                        "title": f"Chart_{j:02d}",
                        "type": ["Column Chart", "Line Chart", "Pie Chart", "Table", "Card"][j % 5],
                        "fields": [f"Table_{(i*3+j) % tables:03d}[Column_000]", f"Measure_{(i*5+j) % measures:03d}"]
                    }
                    for j in range(5)
                ]
            }
            metadata["visualizations"].append(page)
        
        return metadata


class TestStressTests:
    """Stress tests for extreme conditions."""
    
    @pytest.mark.stress
    def test_extreme_table_count(self):
        """Test handling of models with extreme number of tables."""
        # Create metadata with 1000 tables
        metadata = {
            "file": "extreme_model.pbix",
            "type": "Power BI",
            "tables": [
                {
                    "name": f"Table_{i:04d}",
                    "columns": [
                        {"name": f"Col_{j:02d}", "data_type": "String"}
                        for j in range(10)
                    ]
                }
                for i in range(1000)
            ],
            "measures": [],
            "relationships": []
        }
        
        # Should handle gracefully without crashing
        start_time = time.time()
        markdown_gen = MarkdownGenerator()
        result = markdown_gen.generate(metadata)
        execution_time = time.time() - start_time
        
        assert len(result) > 100000  # Should generate substantial content
        assert execution_time < 30  # Should complete within 30 seconds
        assert "Table_0000" in result
        assert "Table_0999" in result
    
    @pytest.mark.stress
    def test_very_long_strings(self):
        """Test handling of very long strings in metadata."""
        long_description = "A" * 10000  # 10KB description
        long_expression = "SUM(" + " + ".join([f"Table[Column_{i:03d}]" for i in range(100)]) + ")"
        
        metadata = {
            "file": "long_strings.pbix",
            "type": "Power BI",
            "model_info": {
                "description": long_description
            },
            "measures": [
                {
                    "name": "Complex Measure",
                    "expression": long_expression,
                    "description": long_description
                }
            ],
            "tables": [
                {
                    "name": "Test Table",
                    "columns": [
                        {
                            "name": "Long Description Column",
                            "description": long_description,
                            "data_type": "String"
                        }
                    ]
                }
            ]
        }
        
        # Should handle long strings without issues
        markdown_gen = MarkdownGenerator()
        result = markdown_gen.generate(metadata)
        
        assert long_description in result
        assert len(result) > 50000  # Should include all content
        
        # JSON should also handle it
        json_gen = JSONGenerator()
        json_result = json_gen.generate(metadata)
        json_data = json.loads(json_result)
        
        assert json_data["model_info"]["description"] == long_description
    
    @pytest.mark.stress
    def test_deeply_nested_structures(self):
        """Test handling of deeply nested data structures."""
        # Create metadata with deeply nested visualization structure
        deep_visuals = []
        for i in range(100):
            visual = {
                "title": f"Nested Visual {i}",
                "type": "Complex Chart",
                "config": {
                    "axes": {
                        "x": {
                            "field": f"Field_{i}",
                            "formatting": {
                                "color": "#000000",
                                "font": {
                                    "family": "Arial",
                                    "size": 12,
                                    "style": {"bold": True, "italic": False}
                                }
                            }
                        },
                        "y": {
                            "measures": [f"Measure_{j}" for j in range(10)],
                            "formatting": {
                                "number": {
                                    "format": "#,##0.00",
                                    "decimal_places": 2
                                }
                            }
                        }
                    }
                }
            }
            deep_visuals.append(visual)
        
        metadata = {
            "file": "deep_nested.pbix",
            "type": "Power BI",
            "visualizations": [{"page": "Complex Page", "visuals": deep_visuals}],
            "tables": [],
            "measures": []
        }
        
        # Should handle nested structures
        json_gen = JSONGenerator()
        result = json_gen.generate(metadata)
        json_data = json.loads(result)
        
        assert len(json_data["visualizations"][0]["visuals"]) == 100
        assert json_data["visualizations"][0]["visuals"][0]["config"]["axes"]["x"]["field"] == "Field_0"