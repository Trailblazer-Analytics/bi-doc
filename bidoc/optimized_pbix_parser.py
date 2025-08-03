"""Optimized Power BI (.pbix) file parser with performance enhancements."""

import json
import logging
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import gc

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False

if TYPE_CHECKING:
    from pbixray import PBIXRay
else:
    try:
        from pbixray import PBIXRay
    except ImportError:
        PBIXRay = None

from bidoc.cache_utils import hybrid_cached, memory_cached
from bidoc.dax_formatter import DAXFormatter, format_dax_expression
from bidoc.metadata_schemas import (
    ensure_complete_metadata,
    get_default_powerbi_metadata,
)
from bidoc.optimized_processors import (
    StreamingMetadataProcessor,
    LargeFileHandler,
)
from bidoc.performance_utils import (
    performance_monitored,
    performance_context,
    optimize_large_data_structure,
)
from bidoc.utils import MetadataExtractor


class OptimizedPowerBIParser(MetadataExtractor):
    """Optimized parser for Power BI .pbix files with caching and performance monitoring."""

    def __init__(self, cache_enabled: bool = True, optimize_large_files: bool = True):
        """Initialize optimized PowerBI parser.
        
        Args:
            cache_enabled: Enable caching for parsed results
            optimize_large_files: Use optimizations for large files
        """
        super().__init__()
        if PBIXRay is None:
            raise ImportError(
                "PBIXRay library is required. Install with: pip install pbixray"
            )
        
        self.dax_formatter = DAXFormatter()
        self.cache_enabled = cache_enabled
        self.optimize_large_files = optimize_large_files
        self.streaming_processor = StreamingMetadataProcessor()
        self.large_file_handler = LargeFileHandler(size_threshold_mb=50.0)
        
        self.logger.debug(f"Initialized OptimizedPowerBIParser (cache: {cache_enabled})")

    @performance_monitored
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a Power BI .pbix file with optimizations."""
        file_size_mb = file_path.stat().st_size / 1024 / 1024 if file_path.exists() else 0
        
        self.logger.info(f"Parsing Power BI file: {file_path.name} ({file_size_mb:.1f}MB)")
        
        # Use large file handler for big files
        if self.optimize_large_files and file_size_mb > 50:
            return self.large_file_handler.process_large_file(file_path, self._parse_internal)
        
        # Use cached parsing for regular files
        if self.cache_enabled:
            return self._parse_cached(file_path)
        else:
            return self._parse_internal(file_path)

    @hybrid_cached(memory_ttl=1800, file_max_age=3600)  # 30min memory, 1hr file cache
    def _parse_cached(self, file_path: Path) -> Dict[str, Any]:
        """Parse with caching enabled."""
        return self._parse_internal(file_path)

    @performance_monitored
    def _parse_internal(self, file_path: Path) -> Dict[str, Any]:
        """Internal parsing method with performance monitoring."""
        with performance_context(f"parse_pbix_{file_path.name}"):
            # Start with default metadata
            metadata = get_default_powerbi_metadata()
            
            # Update basic file information
            metadata.update({
                "file": file_path.name,
                "type": "Power BI",
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size if file_path.exists() else None,
            })

            try:
                # Initialize PBIXRay
                pbix = PBIXRay(str(file_path))
                
                # Extract metadata sections with performance monitoring
                metadata.update(self._extract_model_info(pbix))
                metadata.update(self._extract_data_sources(pbix))
                metadata.update(self._extract_tables_optimized(pbix))
                metadata.update(self._extract_measures_optimized(pbix))
                metadata.update(self._extract_relationships_optimized(pbix))
                metadata.update(self._extract_calculated_columns_optimized(pbix))
                
                # Add processing info
                metadata["_processing_info"] = {
                    "parser": "OptimizedPowerBIParser",
                    "cache_enabled": self.cache_enabled,
                    "optimized": True
                }
                
            except Exception as e:
                self.logger.error(f"Error parsing {file_path}: {e}")
                metadata["error"] = str(e)
                metadata["parsing_successful"] = False
            
            # Ensure complete metadata and optimize structure
            metadata = ensure_complete_metadata(metadata, "powerbi")
            
            # Optimize large data structures
            if self.optimize_large_files:
                metadata = optimize_large_data_structure(metadata, max_string_length=1000)
            
            return metadata

    @memory_cached(ttl=900)  # 15 minute cache for model info
    @performance_monitored
    def _extract_model_info(self, pbix) -> Dict[str, Any]:
        """Extract model information with caching."""
        try:
            model_info = {
                "name": getattr(pbix, 'model_name', 'Unknown'),
                "description": getattr(pbix, 'model_description', ''),
                "culture": getattr(pbix, 'model_culture', 'en-US'),
            }
            self.log_extraction_progress("Model info extracted")
            return {"model_info": model_info}
            
        except Exception as e:
            self.logger.warning(f"Could not extract model info: {e}")
            return {"model_info": {"name": "Unknown", "culture": "en-US"}}

    @performance_monitored
    def _extract_data_sources(self, pbix) -> Dict[str, Any]:
        """Extract data sources with optimization."""
        try:
            data_sources = []
            
            # Get data sources from pbix
            raw_sources = getattr(pbix, 'data_sources', [])
            
            for source in raw_sources:
                source_data = {
                    "name": getattr(source, 'name', 'Unknown'),
                    "type": getattr(source, 'type', 'Unknown'),
                    "connection": getattr(source, 'connection_string', ''),
                }
                
                # Optimize connection string (remove sensitive info)
                if source_data["connection"]:
                    source_data["connection"] = self._sanitize_connection_string(
                        source_data["connection"]
                    )
                
                data_sources.append(source_data)
            
            self.log_extraction_progress("Data sources", len(data_sources))
            return {"data_sources": data_sources}
            
        except Exception as e:
            self.logger.warning(f"Could not extract data sources: {e}")
            return {"data_sources": []}

    @performance_monitored
    def _extract_tables_optimized(self, pbix) -> Dict[str, Any]:
        """Extract tables using streaming processor for large datasets."""
        try:
            raw_tables = getattr(pbix, 'tables', [])
            
            if not raw_tables:
                return {"tables": []}
            
            # Convert raw tables to standard format
            tables_data = []
            for table in raw_tables:
                table_data = {
                    "name": getattr(table, 'name', 'Unknown'),
                    "columns": self._extract_table_columns(table),
                    "row_count": getattr(table, 'row_count', None),
                }
                tables_data.append(table_data)
            
            # Use streaming processor for large table sets
            if len(tables_data) > 50:
                processed_tables = list(
                    self.streaming_processor.process_tables_streaming(tables_data)
                )
            else:
                processed_tables = tables_data
            
            self.log_extraction_progress("Tables", len(processed_tables))
            return {"tables": processed_tables}
            
        except Exception as e:
            self.logger.warning(f"Could not extract tables: {e}")
            return {"tables": []}

    @performance_monitored
    def _extract_measures_optimized(self, pbix) -> Dict[str, Any]:
        """Extract measures using streaming processor."""
        try:
            raw_measures = getattr(pbix, 'measures', [])
            
            if not raw_measures:
                return {"measures": []}
            
            # Convert raw measures to standard format
            measures_data = []
            for measure in raw_measures:
                expression = getattr(measure, 'expression', '')
                
                measure_data = {
                    "name": getattr(measure, 'name', 'Unknown'),
                    "table": getattr(measure, 'table', ''),
                    "expression": expression,
                    "expression_formatted": self._format_dax_safe(expression),
                    "data_type": getattr(measure, 'data_type', ''),
                    "format_string": getattr(measure, 'format_string', ''),
                    "description": getattr(measure, 'description', ''),
                    "is_hidden": getattr(measure, 'is_hidden', False),
                }
                measures_data.append(measure_data)
            
            # Use streaming processor for large measure sets
            if len(measures_data) > 100:
                processed_measures = list(
                    self.streaming_processor.process_measures_streaming(measures_data)
                )
            else:
                processed_measures = measures_data
            
            self.log_extraction_progress("Measures", len(processed_measures))
            return {"measures": processed_measures}
            
        except Exception as e:
            self.logger.warning(f"Could not extract measures: {e}")
            return {"measures": []}

    @performance_monitored
    def _extract_relationships_optimized(self, pbix) -> Dict[str, Any]:
        """Extract relationships with batch processing."""
        try:
            raw_relationships = getattr(pbix, 'relationships', [])
            
            if not raw_relationships:
                return {"relationships": []}
            
            # Convert to standard format
            relationships_data = []
            for rel in raw_relationships:
                rel_data = {
                    "from_table": getattr(rel, 'from_table', ''),
                    "from_column": getattr(rel, 'from_column', ''),
                    "to_table": getattr(rel, 'to_table', ''),
                    "to_column": getattr(rel, 'to_column', ''),
                    "cardinality": getattr(rel, 'cardinality', ''),
                    "is_active": getattr(rel, 'is_active', True),
                    "cross_filter_direction": getattr(rel, 'cross_filter_direction', 'Single'),
                }
                relationships_data.append(rel_data)
            
            # Process with streaming processor
            processed_relationships = self.streaming_processor.process_relationships_streaming(
                relationships_data
            )
            
            self.log_extraction_progress("Relationships", len(processed_relationships))
            return {"relationships": processed_relationships}
            
        except Exception as e:
            self.logger.warning(f"Could not extract relationships: {e}")
            return {"relationships": []}

    @performance_monitored
    def _extract_calculated_columns_optimized(self, pbix) -> Dict[str, Any]:
        """Extract calculated columns with optimization."""
        try:
            calculated_columns = []
            tables = getattr(pbix, 'tables', [])
            
            # Process in batches to avoid memory issues
            for table in tables:
                table_name = getattr(table, 'name', 'Unknown')
                columns = getattr(table, 'columns', [])
                
                for column in columns:
                    if hasattr(column, 'expression') and column.expression:
                        expression = column.expression
                        
                        calc_column = {
                            "name": getattr(column, 'name', 'Unknown'),
                            "table": table_name,
                            "expression": expression,
                            "expression_formatted": self._format_dax_safe(expression),
                            "data_type": getattr(column, 'data_type', ''),
                            "description": getattr(column, 'description', ''),
                            "is_hidden": getattr(column, 'is_hidden', False),
                        }
                        calculated_columns.append(calc_column)
                
                # Periodic garbage collection for large models
                if len(calculated_columns) % 100 == 0:
                    gc.collect()
            
            self.log_extraction_progress("Calculated columns", len(calculated_columns))
            return {"calculated_columns": calculated_columns}
            
        except Exception as e:
            self.logger.warning(f"Could not extract calculated columns: {e}")
            return {"calculated_columns": []}

    def _extract_table_columns(self, table) -> List[Dict[str, Any]]:
        """Extract columns from a table."""
        columns = []
        raw_columns = getattr(table, 'columns', [])
        
        for column in raw_columns:
            column_data = {
                "name": getattr(column, 'name', 'Unknown'),
                "data_type": getattr(column, 'data_type', 'Unknown'),
                "is_hidden": getattr(column, 'is_hidden', False),
                "description": getattr(column, 'description', ''),
            }
            columns.append(column_data)
        
        return columns

    def _format_dax_safe(self, expression: str) -> str:
        """Safely format DAX expression with error handling."""
        if not expression or not expression.strip():
            return expression
        
        try:
            return format_dax_expression(expression)
        except Exception as e:
            self.logger.debug(f"DAX formatting failed: {e}")
            return expression

    def _sanitize_connection_string(self, connection_string: str) -> str:
        """Remove sensitive information from connection strings."""
        if not connection_string:
            return connection_string
        
        # Remove passwords and keys
        sensitive_patterns = [
            'password=',
            'pwd=',
            'key=',
            'secret=',
            'token=',
        ]
        
        sanitized = connection_string.lower()
        for pattern in sensitive_patterns:
            if pattern in sanitized:
                # Replace everything after the pattern until next semicolon
                start = sanitized.find(pattern)
                if start != -1:
                    end = sanitized.find(';', start)
                    if end == -1:
                        end = len(sanitized)
                    connection_string = (
                        connection_string[:start + len(pattern)] + 
                        "***REDACTED***" + 
                        connection_string[end:]
                    )
        
        return connection_string


# Factory function for backward compatibility
def create_powerbi_parser(optimized: bool = True, **kwargs) -> MetadataExtractor:
    """Create PowerBI parser with optional optimizations.
    
    Args:
        optimized: Use optimized parser if True
        **kwargs: Additional arguments for parser initialization
        
    Returns:
        PowerBI parser instance
    """
    if optimized:
        return OptimizedPowerBIParser(**kwargs)
    else:
        # Fall back to original parser
        from bidoc.pbix_parser import PowerBIParser
        return PowerBIParser()