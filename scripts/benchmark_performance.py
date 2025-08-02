#!/usr/bin/env python3
"""Performance benchmark script for BI Documentation Tool optimizations."""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from bidoc.cache_utils import get_memory_cache, get_file_cache, clear_all_caches
    from bidoc.performance_utils import (
        get_performance_monitor,
        log_performance_summary,
        performance_context
    )
    from bidoc.optimized_pbix_parser import OptimizedPowerBIParser, create_powerbi_parser
    from bidoc.optimized_processors import (
        StreamingMetadataProcessor,
        ConcurrentFileProcessor,
        LargeFileHandler
    )
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure to install the package with: pip install -e .")
    exit(1)


class PerformanceBenchmark:
    """Benchmark performance improvements in BI Documentation Tool."""
    
    def __init__(self, test_files_dir: Path):
        self.test_files_dir = test_files_dir
        self.results = {}
        
    def run_parser_benchmark(self, file_paths: List[Path], iterations: int = 3) -> Dict[str, Any]:
        """Benchmark parser performance with and without optimizations."""
        logger.info(f"Running parser benchmark with {len(file_paths)} files")
        
        results = {
            'optimized': {'times': [], 'cache_hits': 0},
            'standard': {'times': [], 'cache_hits': 0}
        }
        
        # Clear caches before starting
        clear_all_caches()
        
        # Test optimized parser
        logger.info("Testing optimized parser...")
        optimized_parser = create_powerbi_parser(optimized=True, cache_enabled=True)
        
        for i in range(iterations):
            start_time = time.time()
            
            for file_path in file_paths:
                if file_path.suffix.lower() == '.pbix':
                    try:
                        with performance_context(f"optimized_parse_{i}"):
                            metadata = optimized_parser.parse(file_path)
                            if metadata and 'error' not in metadata:
                                logger.debug(f"Successfully parsed {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to parse {file_path}: {e}")
            
            execution_time = time.time() - start_time
            results['optimized']['times'].append(execution_time)
            logger.info(f"Optimized iteration {i+1}: {execution_time:.2f}s")
        
        # Test standard parser (if available)
        logger.info("Testing standard parser...")
        try:
            standard_parser = create_powerbi_parser(optimized=False)
            
            for i in range(iterations):
                start_time = time.time()
                
                for file_path in file_paths:
                    if file_path.suffix.lower() == '.pbix':
                        try:
                            metadata = standard_parser.parse(file_path)
                            if metadata and 'error' not in metadata:
                                logger.debug(f"Successfully parsed {file_path.name}")
                        except Exception as e:
                            logger.warning(f"Failed to parse {file_path}: {e}")
                
                execution_time = time.time() - start_time
                results['standard']['times'].append(execution_time)
                logger.info(f"Standard iteration {i+1}: {execution_time:.2f}s")
                
        except Exception as e:
            logger.warning(f"Standard parser not available: {e}")
            results['standard'] = None
        
        # Calculate statistics
        optimized_avg = sum(results['optimized']['times']) / len(results['optimized']['times'])
        
        benchmark_results = {
            'file_count': len(file_paths),
            'iterations': iterations,
            'optimized_avg_time': optimized_avg,
            'optimized_times': results['optimized']['times']
        }
        
        if results['standard']:
            standard_avg = sum(results['standard']['times']) / len(results['standard']['times'])
            improvement = ((standard_avg - optimized_avg) / standard_avg) * 100
            
            benchmark_results.update({
                'standard_avg_time': standard_avg,
                'standard_times': results['standard']['times'],
                'performance_improvement': improvement
            })
        
        return benchmark_results
    
    def run_cache_benchmark(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Benchmark caching performance."""
        logger.info("Running cache benchmark...")
        
        memory_cache = get_memory_cache()
        file_cache = get_file_cache()
        
        # Clear caches
        memory_cache.clear()
        file_cache.clear()
        
        results = {
            'memory_cache': {'write_times': [], 'read_times': []},
            'file_cache': {'write_times': [], 'read_times': []},
            'no_cache': {'process_times': []}
        }
        
        # Test memory cache
        for i, data in enumerate(test_data):
            key = f"test_key_{i}"
            
            # Write test
            start_time = time.time()
            memory_cache.set(key, data)
            write_time = time.time() - start_time
            results['memory_cache']['write_times'].append(write_time)
            
            # Read test
            start_time = time.time()
            cached_data = memory_cache.get(key)
            read_time = time.time() - start_time
            results['memory_cache']['read_times'].append(read_time)
            
            assert cached_data == data, "Memory cache data mismatch"
        
        # Test file cache
        for i, data in enumerate(test_data):
            key = f"test_key_{i}"
            
            # Write test
            start_time = time.time()
            file_cache.set(key, data)
            write_time = time.time() - start_time
            results['file_cache']['write_times'].append(write_time)
            
            # Read test
            start_time = time.time()
            cached_data = file_cache.get(key)
            read_time = time.time() - start_time
            results['file_cache']['read_times'].append(read_time)
            
            assert cached_data == data, "File cache data mismatch"
        
        # Test without cache (simulate processing time)
        for data in test_data:
            start_time = time.time()
            # Simulate some processing
            processed_data = json.dumps(data)
            json.loads(processed_data)
            process_time = time.time() - start_time
            results['no_cache']['process_times'].append(process_time)
        
        # Calculate averages
        cache_results = {}
        for cache_type, metrics in results.items():
            cache_results[cache_type] = {}
            for metric_name, times in metrics.items():
                cache_results[cache_type][f'avg_{metric_name}'] = sum(times) / len(times)
                cache_results[cache_type][f'total_{metric_name}'] = sum(times)
        
        return cache_results
    
    def run_streaming_benchmark(self, large_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Benchmark streaming processor performance."""
        logger.info(f"Running streaming benchmark with {len(large_dataset)} items")
        
        processor = StreamingMetadataProcessor(max_memory_mb=100, batch_size=50)
        
        # Test streaming processing
        start_time = time.time()
        
        processed_count = 0
        for processed_item in processor.process_tables_streaming(large_dataset):
            processed_count += 1
        
        streaming_time = time.time() - start_time
        
        # Test batch processing
        start_time = time.time()
        
        batch_results = processor.batch_processor.process_items(
            large_dataset,
            lambda batch: [item for item in batch],  # Identity function
            lambda results: [item for batch in results for item in batch]
        )
        
        batch_time = time.time() - start_time
        
        return {
            'dataset_size': len(large_dataset),
            'streaming_time': streaming_time,
            'streaming_throughput': len(large_dataset) / streaming_time,
            'batch_time': batch_time,
            'batch_throughput': len(large_dataset) / batch_time,
            'processed_count': processed_count
        }
    
    def generate_test_data(self, size: int = 1000) -> List[Dict[str, Any]]:
        """Generate test data for benchmarking."""
        test_data = []
        
        for i in range(size):
            item = {
                'id': i,
                'name': f'Test Item {i}',
                'description': f'This is test item number {i} with some longer description text to simulate realistic data sizes.',
                'metadata': {
                    'created': '2024-01-01',
                    'modified': '2024-01-02',
                    'tags': [f'tag{j}' for j in range(5)],
                    'properties': {
                        f'prop{k}': f'value{k}' for k in range(10)
                    }
                },
                'data': list(range(20))  # Some numeric data
            }
            test_data.append(item)
        
        return test_data
    
    def run_all_benchmarks(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Run all benchmark tests."""
        logger.info("Starting comprehensive performance benchmark...")
        
        all_results = {}
        
        # Parser benchmark
        if file_paths:
            logger.info("=== Parser Benchmark ===")
            all_results['parser'] = self.run_parser_benchmark(file_paths)
        
        # Cache benchmark
        logger.info("=== Cache Benchmark ===")
        test_data = self.generate_test_data(100)
        all_results['cache'] = self.run_cache_benchmark(test_data)
        
        # Streaming benchmark
        logger.info("=== Streaming Benchmark ===")
        large_dataset = self.generate_test_data(1000)
        all_results['streaming'] = self.run_streaming_benchmark(large_dataset)
        
        # Performance monitor summary
        logger.info("=== Performance Monitor Summary ===")
        log_performance_summary()
        monitor = get_performance_monitor()
        all_results['performance_summary'] = monitor.get_summary()
        
        return all_results


def main():
    """Main benchmark function."""
    parser = argparse.ArgumentParser(description="Benchmark BI Documentation Tool performance")
    parser.add_argument(
        "--test-files", 
        type=Path,
        help="Directory containing test PBIX files"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="benchmark_results.json",
        help="Output file for benchmark results"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations for parser benchmark"
    )
    
    args = parser.parse_args()
    
    # Find test files
    file_paths = []
    if args.test_files and args.test_files.exists():
        file_paths = list(args.test_files.glob("*.pbix"))
        logger.info(f"Found {len(file_paths)} PBIX files for testing")
    else:
        logger.warning("No test files directory specified or found")
    
    # Run benchmarks
    benchmark = PerformanceBenchmark(args.test_files or Path.cwd())
    results = benchmark.run_all_benchmarks(file_paths)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Benchmark results saved to {args.output}")
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    if 'parser' in results:
        parser_results = results['parser']
        print(f"Parser Benchmark:")
        print(f"  Files processed: {parser_results['file_count']}")
        print(f"  Optimized average time: {parser_results['optimized_avg_time']:.2f}s")
        
        if 'performance_improvement' in parser_results:
            print(f"  Performance improvement: {parser_results['performance_improvement']:.1f}%")
    
    if 'cache' in results:
        cache_results = results['cache']
        print(f"\nCache Benchmark:")
        print(f"  Memory cache avg read: {cache_results['memory_cache']['avg_read_times']*1000:.2f}ms")
        print(f"  File cache avg read: {cache_results['file_cache']['avg_read_times']*1000:.2f}ms")
    
    if 'streaming' in results:
        streaming_results = results['streaming']
        print(f"\nStreaming Benchmark:")
        print(f"  Dataset size: {streaming_results['dataset_size']} items")
        print(f"  Streaming throughput: {streaming_results['streaming_throughput']:.1f} items/sec")
        print(f"  Batch throughput: {streaming_results['batch_throughput']:.1f} items/sec")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()