"""CLI command handlers and utilities for the BI Documentation Tool."""

import logging
from pathlib import Path
from typing import Tuple

import click
from colorama import Fore, Style

from .ai_summary import AISummary, get_summary_strategy
from .config import load_config
from .constants import JSON_FORMAT, MARKDOWN_FORMAT
from .json_generator import JSONGenerator
from .logger import LOG_FILE_NAME, get_logger, setup_logging
from .markdown_generator import MarkdownGenerator
from .parsers import PowerBIParser, TableauParser
from .utils import FileType, detect_file_type


def parse_file(file_path: Path, file_type: FileType) -> dict:
    """Parse a BI file and extract metadata"""
    logger = get_logger(__name__)

    try:
        if file_type == FileType.POWER_BI:
            parser = PowerBIParser()
            logger.debug("Using Power BI parser")
        elif file_type in [FileType.TABLEAU_TWB, FileType.TABLEAU_TWBX]:
            parser = TableauParser()
            logger.debug("Using Tableau parser")
        else:
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return None

        return parser.parse(file_path)

    except Exception as e:
        logger.error(f"Parser error: {str(e)}")
        return None


class CLIProcessor:
    """Handles the main CLI processing logic."""
    
    def __init__(self, output_dir: str, output_format: str, verbose: bool, 
                 log_file: bool, with_summary: bool, config_path: str = None):
        """
        Initialize the CLI processor.
        
        Args:
            output_dir: Directory for output files
            output_format: Output format(s) - 'markdown', 'json', or 'both'
            verbose: Enable verbose logging
            log_file: Write log file
            with_summary: Generate AI summaries
            config_path: Optional config file path
        """
        self.output_dir = output_dir
        self.output_format = output_format
        self.verbose = verbose
        self.log_file = log_file
        self.with_summary = with_summary
        self.config_path = config_path
        
        # Processing counters
        self.successful_files = 0
        self.failed_files = 0
        
        # Will be initialized in setup()
        self.output_path = None
        self.logger = None
        self.config = None
    
    def setup(self) -> None:
        """Set up the processor - config, output directory, and logging."""
        # Load configuration
        self.config = load_config(self.config_path) if self.config_path else load_config()
        
        # Create output directory
        self.output_path = Path(self.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file_path = self.output_path / LOG_FILE_NAME if self.log_file else None
        setup_logging(logging.DEBUG if self.verbose else logging.INFO, log_file_path)
        self.logger = get_logger(__name__)
        
        # Log initialization info
        self._log_initialization(log_file_path)
    
    def _log_initialization(self, log_file_path) -> None:
        """Log initialization information."""
        self.logger.info(f"{Fore.CYAN}Starting BI Documentation Tool{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}Starting BI Documentation Tool{Style.RESET_ALL}")
        self.logger.info(f"Output directory: {self.output_path.absolute()}")
        self.logger.info(f"Output format(s): {self.output_format}")
        if log_file_path:
            self.logger.info(f"Log file: {log_file_path.absolute()}")
    
    def process_files(self, input_files: Tuple[str, ...]) -> int:
        """
        Process all input files.
        
        Args:
            input_files: Tuple of input file paths
            
        Returns:
            Exit code (0 for success, 1 for failures)
        """
        for input_file in input_files:
            self._process_single_file(input_file)
        
        return self._finalize_processing()
    
    def _process_single_file(self, input_file: str) -> None:
        """Process a single input file."""
        input_path = Path(input_file)
        
        self.logger.info(f"{Fore.YELLOW}Processing: {input_file}{Style.RESET_ALL}")
        
        try:
            # Parse the file
            metadata = self._parse_input_file(input_path)
            if metadata is None:
                self.failed_files += 1
                return
            
            # Add AI summary if requested
            if self.with_summary:
                metadata = self._add_ai_summary(metadata)
            
            # Generate outputs
            success = self._generate_outputs(metadata, input_path.stem)
            if success:
                self.successful_files += 1
            else:
                self.failed_files += 1
                
        except Exception as e:
            self.logger.error(f"Error processing {input_file}: {str(e)}")
            self.failed_files += 1
    
    def _parse_input_file(self, input_path: Path) -> dict:
        """Parse a single input file and return metadata."""
        try:
            file_type = detect_file_type(input_path)
            metadata = parse_file(input_path, file_type)
            
            if metadata is None:
                self.logger.error(f"Failed to parse file: {input_path}")
                return None
                
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to parse {input_path}: {str(e)}")
            return None
    
    def _add_ai_summary(self, metadata: dict) -> dict:
        """Add AI summary to metadata if requested."""
        self.logger.info(f"{Fore.BLUE}Generating AI summary...{Style.RESET_ALL}")
        
        try:
            # Get the appropriate strategy based on file type
            file_type = detect_file_type(Path(metadata.get("file_path", "")))
            strategy = get_summary_strategy(file_type)
            ai_summary = AISummary(strategy, self.config)
            summary = ai_summary.generate_summary(metadata)
            
            if summary:
                metadata["ai_summary"] = summary
            else:
                self.logger.warning("Failed to generate AI summary")
        except Exception as e:
            self.logger.warning(f"AI summary generation failed: {str(e)}")
        
        return metadata
    
    def _generate_outputs(self, metadata: dict, base_filename: str) -> bool:
        """Generate output files in requested formats."""
        success = True
        
        if "markdown" in self.output_format:
            if not self._generate_markdown_output(metadata, base_filename):
                success = False
        
        if "json" in self.output_format:
            if not self._generate_json_output(metadata, base_filename):
                success = False
        
        return success
    
    def _generate_markdown_output(self, metadata: dict, base_filename: str) -> bool:
        """Generate markdown output file."""
        try:
            markdown_gen = MarkdownGenerator()
            markdown_content = markdown_gen.generate(metadata)
            markdown_path = self.output_path / f"{base_filename}.md"
            
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            self.logger.info(f"Generated: {markdown_path}")
            click.echo(f"{Fore.GREEN}Generated: {markdown_path}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate Markdown: {str(e)}")
            return False
    
    def _generate_json_output(self, metadata: dict, base_filename: str) -> bool:
        """Generate JSON output file."""
        try:
            json_gen = JSONGenerator()
            json_content = json_gen.generate(metadata)
            json_path = self.output_path / f"{base_filename}.json"
            
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            self.logger.info(f"Generated: {json_path}")
            click.echo(f"{Fore.GREEN}Generated: {json_path}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON: {str(e)}")
            return False
    
    def _finalize_processing(self) -> int:
        """Finalize processing and return exit code."""
        # Final summary
        self.logger.info(f"{Fore.CYAN}Processing complete!{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}Processing complete!{Style.RESET_ALL}")
        self.logger.info(f"Successfully processed: {self.successful_files} files")
        self.logger.info(f"Failed to process: {self.failed_files} files")
        click.echo(f"Successfully processed: {self.successful_files} files")
        click.echo(f"Failed to process: {self.failed_files} files")
        
        if self.failed_files > 0:
            click.echo(f"{Fore.RED}Some files failed to process. Check logs for details.{Style.RESET_ALL}")
            return 1
        
        return 0


def process_cli_command(
    input_files: tuple,
    output_dir: str,
    output_format: str,
    verbose: bool,
    log_file: bool,
    with_summary: bool,
    config_path: str = None,
) -> int:
    """
    Process the CLI command with all parameters.
    
    Args:
        input_files: Tuple of input file paths
        output_dir: Output directory path
        output_format: Output format ('markdown', 'json', or 'both')
        verbose: Enable verbose logging
        log_file: Write log file
        with_summary: Generate AI summaries
        config_path: Optional config file path
        
    Returns:
        Exit code (0 for success, 1 for failures)
    """
    processor = CLIProcessor(
        output_dir=output_dir,
        output_format=output_format,
        verbose=verbose,
        log_file=log_file,
        with_summary=with_summary,
        config_path=config_path
    )
    
    processor.setup()
    return processor.process_files(input_files)