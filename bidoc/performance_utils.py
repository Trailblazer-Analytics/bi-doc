"""Performance monitoring and optimization utilities."""

import functools
import logging
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, TypeVar
from collections import defaultdict

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """Performance metrics for a function call."""
    function_name: str
    execution_time: float
    memory_before: float  # MB
    memory_after: float   # MB
    memory_peak: float    # MB
    memory_delta: float   # MB
    cpu_percent: float
    timestamp: float
    args_count: int
    kwargs_count: int


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)
        self._start_memory = self._get_memory_usage()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:  # Handle all exceptions when psutil might not be available
            return 0.0
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        if not HAS_PSUTIL:
            return 0.0  # Return 0 if psutil not available
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0
    
    @contextmanager
    def measure(self, operation_name: str) -> Generator[None, None, None]:
        """Context manager to measure performance of an operation."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        peak_memory = start_memory
        
        try:
            yield
            
            # Update peak memory during operation
            current_memory = self._get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
            
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            cpu_percent = self._get_cpu_percent()
            
            metric = PerformanceMetrics(
                function_name=operation_name,
                execution_time=end_time - start_time,
                memory_before=start_memory,
                memory_after=end_memory,
                memory_peak=peak_memory,
                memory_delta=end_memory - start_memory,
                cpu_percent=cpu_percent,
                timestamp=start_time,
                args_count=0,
                kwargs_count=0
            )
            
            self.metrics.append(metric)
            self.logger.debug(
                f"Performance: {operation_name} took {metric.execution_time:.3f}s, "
                f"memory: {metric.memory_delta:+.1f}MB"
            )
    
    def record_function_call(
        self, 
        func_name: str,
        execution_time: float,
        memory_before: float,
        memory_after: float,
        memory_peak: float,
        cpu_percent: float,
        args_count: int = 0,
        kwargs_count: int = 0
    ) -> None:
        """Record metrics for a function call."""
        metric = PerformanceMetrics(
            function_name=func_name,
            execution_time=execution_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            memory_delta=memory_after - memory_before,
            cpu_percent=cpu_percent,
            timestamp=time.time(),
            args_count=args_count,
            kwargs_count=kwargs_count
        )
        
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics:
            return {"total_functions": 0}
        
        total_time = sum(m.execution_time for m in self.metrics)
        total_memory_delta = sum(m.memory_delta for m in self.metrics)
        avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
        
        # Group by function name
        by_function = defaultdict(list)
        for metric in self.metrics:
            by_function[metric.function_name].append(metric)
        
        function_stats = {}
        for func_name, func_metrics in by_function.items():
            function_stats[func_name] = {
                "call_count": len(func_metrics),
                "total_time": sum(m.execution_time for m in func_metrics),
                "avg_time": sum(m.execution_time for m in func_metrics) / len(func_metrics),
                "max_time": max(m.execution_time for m in func_metrics),
                "total_memory_delta": sum(m.memory_delta for m in func_metrics),
                "max_memory_peak": max(m.memory_peak for m in func_metrics),
            }
        
        return {
            "total_functions": len(self.metrics),
            "total_execution_time": total_time,
            "total_memory_delta": total_memory_delta,
            "average_cpu_percent": avg_cpu,
            "function_stats": function_stats,
            "slowest_functions": sorted(
                function_stats.items(),
                key=lambda x: x[1]["total_time"],
                reverse=True
            )[:5],
            "memory_intensive_functions": sorted(
                function_stats.items(),
                key=lambda x: x[1]["total_memory_delta"],
                reverse=True
            )[:5],
        }
    
    def clear(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()
        self.logger.debug("Performance metrics cleared")


# Global performance monitor
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_monitored(func: F) -> F:
    """Decorator to monitor function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        
        start_time = time.time()
        start_memory = monitor._get_memory_usage()
        peak_memory = start_memory
        
        try:
            result = func(*args, **kwargs)
            
            # Check memory usage during execution
            current_memory = monitor._get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
            
            return result
            
        finally:
            end_time = time.time()
            end_memory = monitor._get_memory_usage()
            cpu_percent = monitor._get_cpu_percent()
            
            monitor.record_function_call(
                func_name=f"{func.__module__}.{func.__name__}",
                execution_time=end_time - start_time,
                memory_before=start_memory,
                memory_after=end_memory,
                memory_peak=peak_memory,
                cpu_percent=cpu_percent,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
    
    return wrapper


# Alias for backwards compatibility
performance_monitor = performance_monitored


class BatchProcessor:
    """Process items in batches to optimize memory usage."""
    
    def __init__(self, batch_size: int = 100, max_memory_mb: float = 500.0):
        """Initialize batch processor.
        
        Args:
            batch_size: Number of items per batch
            max_memory_mb: Maximum memory usage before forcing batch processing
        """
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:  # Handle all exceptions when psutil might not be available
            return 0.0
    
    def _should_force_batch(self) -> bool:
        """Check if memory usage requires batch processing."""
        return self._get_memory_usage() > self.max_memory_mb
    
    def process_items(
        self,
        items: List[Any],
        processor_func: Callable[[List[Any]], Any],
        combine_func: Optional[Callable[[List[Any]], Any]] = None
    ) -> Any:
        """Process items in batches.
        
        Args:
            items: List of items to process
            processor_func: Function to process each batch
            combine_func: Function to combine batch results (optional)
            
        Returns:
            Combined result or list of batch results
        """
        if not items:
            return [] if combine_func else None
        
        # Determine effective batch size
        effective_batch_size = self.batch_size
        if self._should_force_batch():
            # Reduce batch size if memory is high
            effective_batch_size = max(10, self.batch_size // 2)
            self.logger.warning(f"High memory usage detected, reducing batch size to {effective_batch_size}")
        
        # Process in batches
        results = []
        total_batches = (len(items) + effective_batch_size - 1) // effective_batch_size
        
        for i in range(0, len(items), effective_batch_size):
            batch = items[i:i + effective_batch_size]
            batch_num = i // effective_batch_size + 1
            
            self.logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            try:
                batch_result = processor_func(batch)
                results.append(batch_result)
                
                # Monitor memory after each batch
                memory_usage = self._get_memory_usage()
                if memory_usage > self.max_memory_mb * 1.5:
                    self.logger.warning(f"High memory usage: {memory_usage:.1f}MB")
                
            except Exception as e:
                self.logger.error(f"Error processing batch {batch_num}: {e}")
                raise
        
        # Combine results if function provided
        if combine_func and results:
            return combine_func(results)
        
        return results


def memory_efficient_generator(items: List[Any], chunk_size: int = 100) -> Generator[List[Any], None, None]:
    """Generator that yields items in memory-efficient chunks.
    
    Args:
        items: List of items to process
        chunk_size: Size of each chunk
        
    Yields:
        Chunks of items
    """
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def optimize_large_data_structure(data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
    """Optimize large data structures by truncating long strings and removing empty values.
    
    Args:
        data: Data structure to optimize
        max_string_length: Maximum length for string values
        
    Returns:
        Optimized data structure
    """
    if isinstance(data, dict):
        optimized = {}
        for key, value in data.items():
            if value is None or value == "":
                continue  # Skip empty values
            
            if isinstance(value, str) and len(value) > max_string_length:
                # Truncate long strings
                optimized[key] = value[:max_string_length] + "... [truncated]"
            elif isinstance(value, (dict, list)):
                # Recursively optimize nested structures
                optimized_nested = optimize_large_data_structure(value, max_string_length)
                if optimized_nested:  # Only include if not empty
                    optimized[key] = optimized_nested
            else:
                optimized[key] = value
        
        return optimized
    
    elif isinstance(data, list):
        optimized = []
        for item in data:
            if item is None or item == "":
                continue  # Skip empty values
            
            if isinstance(item, (dict, list)):
                optimized_item = optimize_large_data_structure(item, max_string_length)
                if optimized_item:  # Only include if not empty
                    optimized.append(optimized_item)
            else:
                optimized.append(item)
        
        return optimized
    
    else:
        return data


def log_performance_summary(monitor: Optional[PerformanceMonitor] = None) -> None:
    """Log performance summary to logger."""
    if monitor is None:
        monitor = get_performance_monitor()
    
    summary = monitor.get_summary()
    logger = logging.getLogger(__name__)
    
    if summary["total_functions"] == 0:
        logger.info("No performance metrics recorded")
        return
    
    logger.info(f"Performance Summary:")
    logger.info(f"  Total function calls: {summary['total_functions']}")
    logger.info(f"  Total execution time: {summary['total_execution_time']:.3f}s")
    logger.info(f"  Total memory delta: {summary['total_memory_delta']:+.1f}MB")
    logger.info(f"  Average CPU usage: {summary['average_cpu_percent']:.1f}%")
    
    if summary["slowest_functions"]:
        logger.info("  Slowest functions:")
        for func_name, stats in summary["slowest_functions"]:
            logger.info(f"    {func_name}: {stats['total_time']:.3f}s ({stats['call_count']} calls)")
    
    if summary["memory_intensive_functions"]:
        logger.info("  Memory intensive functions:")
        for func_name, stats in summary["memory_intensive_functions"]:
            logger.info(f"    {func_name}: {stats['total_memory_delta']:+.1f}MB ({stats['call_count']} calls)")


@contextmanager
def performance_context(operation_name: str) -> Generator[PerformanceMonitor, None, None]:
    """Context manager for performance monitoring with automatic summary logging.
    
    Args:
        operation_name: Name of the operation being monitored
        
    Yields:
        PerformanceMonitor instance
    """
    monitor = get_performance_monitor()
    
    with monitor.measure(operation_name):
        yield monitor
    
    # Log summary if this was a significant operation
    summary = monitor.get_summary()
    if summary["total_execution_time"] > 1.0:  # Log if operation took more than 1 second
        log_performance_summary(monitor)