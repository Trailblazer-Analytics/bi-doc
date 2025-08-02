"""Optimized processors for handling large files and datasets efficiently."""

import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union
import gc

from bidoc.cache_utils import hybrid_cached
from bidoc.performance_utils import (
    BatchProcessor,
    performance_monitored,
    performance_context,
    memory_efficient_generator,
    optimize_large_data_structure
)


class StreamingMetadataProcessor:
    """Process metadata in streaming fashion to handle large datasets."""
    
    def __init__(self, max_memory_mb: float = 500.0, batch_size: int = 100):
        """Initialize streaming processor.
        
        Args:
            max_memory_mb: Maximum memory usage before optimization
            batch_size: Batch size for processing
        """
        self.max_memory_mb = max_memory_mb
        self.batch_size = batch_size
        self.batch_processor = BatchProcessor(batch_size, max_memory_mb)
        self.logger = logging.getLogger(__name__)
    
    @performance_monitored
    def process_tables_streaming(self, tables: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Process tables in streaming fashion to reduce memory usage.
        
        Args:
            tables: List of table metadata
            
        Yields:
            Processed table metadata
        """
        self.logger.debug(f"Processing {len(tables)} tables in streaming mode")
        
        for chunk in memory_efficient_generator(tables, self.batch_size):
            for table in chunk:
                # Optimize individual table to reduce memory footprint
                optimized_table = optimize_large_data_structure(table, max_string_length=500)
                
                # Add computed fields
                if 'columns' in optimized_table:
                    optimized_table['column_count'] = len(optimized_table['columns'])
                    optimized_table['hidden_columns'] = sum(
                        1 for col in optimized_table['columns'] 
                        if col.get('is_hidden', False)
                    )
                
                yield optimized_table
            
            # Force garbage collection after each chunk
            gc.collect()
    
    @performance_monitored
    def process_measures_streaming(self, measures: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Process measures in streaming fashion.
        
        Args:
            measures: List of measure metadata
            
        Yields:
            Processed measure metadata
        """
        self.logger.debug(f"Processing {len(measures)} measures in streaming mode")
        
        for chunk in memory_efficient_generator(measures, self.batch_size):
            processed_measures = []
            
            for measure in chunk:
                # Optimize and add computed fields
                optimized_measure = optimize_large_data_structure(measure, max_string_length=1000)
                
                # Add expression complexity metrics
                expression = optimized_measure.get('expression', '')
                if expression:
                    optimized_measure['expression_length'] = len(expression)
                    optimized_measure['has_complex_logic'] = any(
                        keyword in expression.upper() 
                        for keyword in ['CALCULATE', 'FILTER', 'SUMX', 'AVERAGEX']
                    )
                
                processed_measures.append(optimized_measure)
            
            # Yield processed batch
            for measure in processed_measures:
                yield measure
            
            # Clear batch and collect garbage
            processed_measures.clear()
            gc.collect()
    
    @performance_monitored
    def process_relationships_streaming(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process relationships efficiently.
        
        Args:
            relationships: List of relationship metadata
            
        Returns:
            Processed relationships
        """
        if not relationships:
            return []
        
        self.logger.debug(f"Processing {len(relationships)} relationships")
        
        def process_batch(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            processed = []
            for rel in batch:
                optimized_rel = optimize_large_data_structure(rel)
                
                # Add relationship type categorization
                cardinality = optimized_rel.get('cardinality', '')
                if 'One-to-Many' in cardinality:
                    optimized_rel['relationship_type'] = 'lookup'
                elif 'Many-to-Many' in cardinality:
                    optimized_rel['relationship_type'] = 'bridge'
                else:
                    optimized_rel['relationship_type'] = 'standard'
                
                processed.append(optimized_rel)
            
            return processed
        
        return self.batch_processor.process_items(
            relationships,
            process_batch,
            lambda results: [item for batch in results for item in batch]
        )


class ConcurrentFileProcessor:
    """Process multiple files concurrently with controlled resource usage."""
    
    def __init__(self, max_workers: int = 4, max_memory_mb: float = 1000.0):
        """Initialize concurrent processor.
        
        Args:
            max_workers: Maximum number of worker threads
            max_memory_mb: Maximum memory usage across all workers
        """
        self.max_workers = max_workers
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
    
    @performance_monitored
    def process_files_concurrent(
        self,
        file_paths: List[Path],
        processor_func: Any,  # Function to process individual files
        max_concurrent: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process multiple files concurrently.
        
        Args:
            file_paths: List of file paths to process
            processor_func: Function to process each file
            max_concurrent: Maximum concurrent files (defaults to max_workers)
            
        Returns:
            Dictionary mapping file names to processing results
        """
        if not file_paths:
            return {}
        
        max_concurrent = max_concurrent or self.max_workers
        results = {}
        failed_files = []
        
        self.logger.info(f"Processing {len(file_paths)} files with {max_concurrent} workers")
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_file_safe, file_path, processor_func): file_path
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    if result is not None:
                        results[file_path.name] = result
                        self.logger.debug(f"Successfully processed: {file_path.name}")
                    else:
                        failed_files.append(file_path.name)
                        self.logger.warning(f"Processing returned None: {file_path.name}")
                        
                except Exception as e:
                    failed_files.append(file_path.name)
                    self.logger.error(f"Failed to process {file_path.name}: {e}")
        
        # Log summary
        success_count = len(results)
        total_count = len(file_paths)
        self.logger.info(
            f"Concurrent processing completed: {success_count}/{total_count} succeeded"
        )
        
        if failed_files:
            self.logger.warning(f"Failed files: {', '.join(failed_files)}")
        
        return {
            'results': results,
            'failed_files': failed_files,
            'success_rate': success_count / total_count if total_count > 0 else 0
        }
    
    def _process_file_safe(self, file_path: Path, processor_func: Any) -> Optional[Any]:
        """Safely process a single file with error handling."""
        try:
            with performance_context(f"process_file_{file_path.name}"):
                return processor_func(file_path)
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return None


class MemoryOptimizedGenerator:
    """Generate documentation in memory-efficient chunks."""
    
    def __init__(self, chunk_size: int = 10, temp_dir: Optional[Path] = None):
        """Initialize memory-optimized generator.
        
        Args:
            chunk_size: Number of items to process per chunk
            temp_dir: Temporary directory for intermediate files
        """
        self.chunk_size = chunk_size
        self.temp_dir = temp_dir or Path(tempfile.gettempdir())
        self.logger = logging.getLogger(__name__)
    
    @performance_monitored
    def generate_documentation_streaming(
        self,
        metadata: Dict[str, Any],
        generator_func: Any
    ) -> Generator[str, None, None]:
        """Generate documentation in streaming fashion.
        
        Args:
            metadata: Full metadata dictionary
            generator_func: Function to generate documentation from metadata
            
        Yields:
            Documentation chunks
        """
        # Break metadata into processable chunks
        sections = self._split_metadata_into_sections(metadata)
        
        self.logger.debug(f"Generating documentation in {len(sections)} sections")
        
        for section_name, section_data in sections.items():
            try:
                with performance_context(f"generate_section_{section_name}"):
                    # Generate documentation for this section
                    section_doc = generator_func(section_data)
                    
                    if section_doc and section_doc.strip():
                        yield section_doc
                
                # Clear section data to free memory
                section_data.clear()
                gc.collect()
                
            except Exception as e:
                self.logger.error(f"Error generating section {section_name}: {e}")
                continue
    
    def _split_metadata_into_sections(self, metadata: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Split metadata into logical sections for processing."""
        base_metadata = {
            key: value for key, value in metadata.items()
            if key not in ['tables', 'measures', 'calculated_columns', 'relationships']
        }
        
        sections = {
            'header': {**base_metadata},
            'data_sources': {**base_metadata, 'data_sources': metadata.get('data_sources', [])},
        }
        
        # Split large sections into chunks
        tables = metadata.get('tables', [])
        if tables:
            for i in range(0, len(tables), self.chunk_size):
                chunk = tables[i:i + self.chunk_size]
                sections[f'tables_chunk_{i//self.chunk_size}'] = {
                    **base_metadata,
                    'tables': chunk
                }
        
        measures = metadata.get('measures', [])
        if measures:
            for i in range(0, len(measures), self.chunk_size):
                chunk = measures[i:i + self.chunk_size]
                sections[f'measures_chunk_{i//self.chunk_size}'] = {
                    **base_metadata,
                    'measures': chunk
                }
        
        # Other sections
        for section_name in ['calculated_columns', 'relationships', 'visualizations']:
            section_data = metadata.get(section_name, [])
            if section_data:
                sections[section_name] = {**base_metadata, section_name: section_data}
        
        return sections


class LargeFileHandler:
    """Handle very large BI files efficiently."""
    
    def __init__(self, size_threshold_mb: float = 100.0):
        """Initialize large file handler.
        
        Args:
            size_threshold_mb: File size threshold for special handling
        """
        self.size_threshold_mb = size_threshold_mb
        self.logger = logging.getLogger(__name__)
    
    @hybrid_cached(memory_ttl=1800, file_max_age=3600)
    @performance_monitored
    def process_large_file(self, file_path: Path, processor_func: Any) -> Optional[Dict[str, Any]]:
        """Process large files with special optimizations.
        
        Args:
            file_path: Path to the file
            processor_func: Function to process the file
            
        Returns:
            Processed metadata or None if failed
        """
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        
        if file_size_mb < self.size_threshold_mb:
            # Use normal processing for smaller files
            return processor_func(file_path)
        
        self.logger.info(f"Processing large file ({file_size_mb:.1f}MB): {file_path.name}")
        
        try:
            with performance_context(f"large_file_{file_path.name}"):
                # Use streaming processor for large files
                streaming_processor = StreamingMetadataProcessor(
                    max_memory_mb=self.size_threshold_mb * 2,
                    batch_size=50  # Smaller batches for large files
                )
                
                # Process with memory optimization
                raw_metadata = processor_func(file_path)
                
                if not raw_metadata:
                    return None
                
                # Optimize the metadata structure
                optimized_metadata = optimize_large_data_structure(
                    raw_metadata,
                    max_string_length=500
                )
                
                # Process large sections in streaming fashion
                if 'tables' in optimized_metadata:
                    tables_generator = streaming_processor.process_tables_streaming(
                        optimized_metadata['tables']
                    )
                    optimized_metadata['tables'] = list(tables_generator)
                
                if 'measures' in optimized_metadata:
                    measures_generator = streaming_processor.process_measures_streaming(
                        optimized_metadata['measures']
                    )
                    optimized_metadata['measures'] = list(measures_generator)
                
                if 'relationships' in optimized_metadata:
                    optimized_metadata['relationships'] = streaming_processor.process_relationships_streaming(
                        optimized_metadata['relationships']
                    )
                
                # Add processing metadata
                optimized_metadata['_processing_info'] = {
                    'file_size_mb': file_size_mb,
                    'optimized': True,
                    'streaming_processed': True
                }
                
                self.logger.info(f"Successfully processed large file: {file_path.name}")
                return optimized_metadata
                
        except Exception as e:
            self.logger.error(f"Failed to process large file {file_path}: {e}")
            return None
    
    def should_use_large_file_processing(self, file_path: Path) -> bool:
        """Check if file should use large file processing."""
        try:
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            return file_size_mb >= self.size_threshold_mb
        except OSError:
            return False


# Factory function to create optimized processors
def create_optimized_processor(
    file_size_mb: float = 0,
    concurrent_files: int = 1,
    max_memory_mb: float = 500.0
) -> Union[StreamingMetadataProcessor, ConcurrentFileProcessor, LargeFileHandler]:
    """Create appropriate processor based on requirements.
    
    Args:
        file_size_mb: Size of files being processed
        concurrent_files: Number of files to process concurrently
        max_memory_mb: Maximum memory to use
        
    Returns:
        Appropriate processor instance
    """
    if file_size_mb > 100:
        return LargeFileHandler(size_threshold_mb=50.0)
    elif concurrent_files > 1:
        return ConcurrentFileProcessor(
            max_workers=min(concurrent_files, 8),
            max_memory_mb=max_memory_mb
        )
    else:
        return StreamingMetadataProcessor(
            max_memory_mb=max_memory_mb,
            batch_size=100
        )