"""Command Line Interface for BI Documentation Tool"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

import click
from colorama import init, Fore, Style

from bidoc.pbix_parser import PowerBIParser
from bidoc.tableau_parser import TableauParser
from bidoc.markdown_generator import MarkdownGenerator
from bidoc.json_generator import JSONGenerator
from bidoc.ai_summary import AISummary
from bidoc.utils import setup_logging, detect_file_type, FileType

# Initialize colorama for cross-platform colored output
init()

@click.command()
@click.option('--input', '-i', 'input_files', multiple=True, required=True,
              help='Input BI file(s) to parse (.pbix, .twb, .twbx)')
@click.option('--output', '-o', default='docs/',
              help='Output directory for generated documentation (default: docs/)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['markdown', 'json', 'all'], case_sensitive=False),
              default='all', help='Output format(s) (default: all)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--with-summary', is_flag=True,
              help='Generate AI summary (requires AI configuration)')
@click.version_option()
def main(input_files: tuple, output: str, output_format: str, verbose: bool, with_summary: bool):
    """
    BI Documentation Tool - Generate documentation from Power BI and Tableau files.
    
    Extract metadata from .pbix, .twb, and .twbx files to create comprehensive
    documentation in Markdown and JSON formats.
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    # Create output directory
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Track processing results
    successful_files = 0
    failed_files = 0
    
    logger.info(f"{Fore.CYAN}Starting BI Documentation Tool{Style.RESET_ALL}")
    logger.info(f"Output directory: {output_path.absolute()}")
    logger.info(f"Output format(s): {output_format}")
    
    # Process each input file
    for input_file in input_files:
        input_path = Path(input_file)
        
        if not input_path.exists():
            logger.error(f"{Fore.RED}File not found: {input_file}{Style.RESET_ALL}")
            failed_files += 1
            continue
            
        logger.info(f"{Fore.YELLOW}Processing: {input_file}{Style.RESET_ALL}")
        
        try:
            # Detect file type and parse
            file_type = detect_file_type(input_path)
            metadata = parse_file(input_path, file_type)
            
            if metadata is None:
                logger.error(f"{Fore.RED}Failed to parse: {input_file}{Style.RESET_ALL}")
                failed_files += 1
                continue
            
            # Add AI summary if requested
            if with_summary:
                ai_summary = AISummary()
                metadata['ai_summary'] = ai_summary.generate_summary(metadata)
            
            # Generate outputs
            base_name = input_path.stem
            generate_outputs(metadata, output_path, base_name, output_format)
            
            logger.info(f"{Fore.GREEN}✓ Successfully processed: {input_file}{Style.RESET_ALL}")
            successful_files += 1
            
        except Exception as e:
            logger.error(f"{Fore.RED}Error processing {input_file}: {str(e)}{Style.RESET_ALL}")
            if verbose:
                logger.exception("Full error details:")
            failed_files += 1
    
    # Summary
    total_files = successful_files + failed_files
    logger.info(f"\n{Fore.CYAN}Processing complete:{Style.RESET_ALL}")
    logger.info(f"  Total files: {total_files}")
    logger.info(f"  {Fore.GREEN}Successful: {successful_files}{Style.RESET_ALL}")
    if failed_files > 0:
        logger.info(f"  {Fore.RED}Failed: {failed_files}{Style.RESET_ALL}")
    
    # Exit with error code if any files failed
    if failed_files > 0:
        sys.exit(1)


def parse_file(file_path: Path, file_type: FileType) -> Optional[dict]:
    """Parse a BI file and extract metadata"""
    logger = logging.getLogger(__name__)
    
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


def generate_outputs(metadata: dict, output_path: Path, base_name: str, output_format: str):
    """Generate documentation outputs in the specified format(s)"""
    logger = logging.getLogger(__name__)
    
    if output_format in ['markdown', 'all']:
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(metadata)
        
        markdown_file = output_path / f"{base_name}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"  Generated Markdown: {markdown_file}")
    
    if output_format in ['json', 'all']:
        json_gen = JSONGenerator()
        json_content = json_gen.generate(metadata)
        
        json_file = output_path / f"{base_name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        logger.info(f"  Generated JSON: {json_file}")


if __name__ == "__main__":
    main()
