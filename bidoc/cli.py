"""Command Line Interface for BI Documentation Tool"""

import logging
from pathlib import Path
import sys
from typing import List, Optional

import click
from colorama import Fore, Style, init

from bidoc.ai_summary import AISummary, get_summary_strategy
from bidoc.config import load_config
from bidoc.json_generator import JSONGenerator
from bidoc.markdown_generator import MarkdownGenerator
from bidoc.pbix_parser import PowerBIParser
from bidoc.tableau_parser import TableauParser
from bidoc.utils import FileType, detect_file_type
from bidoc.logger import setup_logging, get_logger
from bidoc.constants import (
    DEFAULT_DOCS_FOLDER,
    JSON_FORMAT,
    LOG_FILE_NAME,
    MARKDOWN_FORMAT,
)

# Initialize colorama for cross-platform colored output
init()


@click.command()
@click.option(
    "--input",
    "-i",
    "input_files",
    multiple=True,
    required=True,
    type=click.Path(exists=True, readable=True, resolve_path=True),
    help="Input BI file(s) to parse (.pbix, .twb, .twbx)",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    default=DEFAULT_DOCS_FOLDER,
    type=click.Path(file_okay=False, resolve_path=True),
    help=f"Output directory for generated documentation (default: {DEFAULT_DOCS_FOLDER})",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to a custom TOML configuration file.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice([MARKDOWN_FORMAT, JSON_FORMAT, "all"], case_sensitive=False),
    default="all",
    help="Output format(s) (default: all)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--log-file",
    is_flag=True,
    help=f"Save logs to a file ({LOG_FILE_NAME}) in the output directory",
)
@click.option(
    "--with-summary",
    is_flag=True,
    help="Generate AI summary (requires AI configuration)",
)
@click.version_option()
def main(
    input_files: tuple,
    output_dir: str,
    output_format: str,
    verbose: bool,
    log_file: bool,
    with_summary: bool,
    config_path: str,
):
    """
    BI Documentation Tool - Generate documentation from Power BI and Tableau files.

    Extract metadata from .pbix, .twb, and .twbx files to create comprehensive
    documentation in Markdown and JSON formats.
    """
    # Load configuration
    config = load_config(config_path) if config_path else load_config()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Setup logging
    log_file_path = output_path / LOG_FILE_NAME if log_file else None
    setup_logging(logging.DEBUG if verbose else logging.INFO, log_file_path)
    logger = get_logger(__name__)

    # Track processing results
    successful_files = 0
    failed_files = 0

    logger.info(f"{Fore.CYAN}Starting BI Documentation Tool{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}Starting BI Documentation Tool{Style.RESET_ALL}")
    logger.info(f"Output directory: {output_path.absolute()}")
    logger.info(f"Output format(s): {output_format}")
    if log_file_path:
        logger.info(f"Log file: {log_file_path.absolute()}")

    # Process each input file
    for input_file in input_files:
        input_path = Path(input_file)

        logger.info(f"{Fore.YELLOW}Processing: {input_file}{Style.RESET_ALL}")

        try:
            # Detect file type and parse
            file_type = detect_file_type(input_path)
            metadata = parse_file(input_path, file_type)

            if metadata is None:
                logger.error(
                    f"{Fore.RED}Failed to parse: {input_file}{Style.RESET_ALL}"
                )
                failed_files += 1
                continue

            # Add AI summary if requested
            if with_summary:
                strategy = get_summary_strategy(file_type)
                ai_summary = AISummary(strategy, config)
                metadata["ai_summary"] = ai_summary.generate_summary(metadata)

            # Generate outputs
            base_name = input_path.stem
            generate_outputs(metadata, output_path, base_name, output_format)

            logger.info(
                f"{Fore.GREEN}✓ Successfully processed: {input_file}{Style.RESET_ALL}"
            )
            successful_files += 1

        except Exception as e:
            logger.error(
                f"{Fore.RED}Error processing {input_file}: {str(e)}{Style.RESET_ALL}"
            )
            if verbose:
                logger.exception("Full error details:")
            failed_files += 1

    # Summary
    total_files = successful_files + failed_files
    logger.info(f"\n{Fore.CYAN}Processing complete:{Style.RESET_ALL}")
    click.echo(f"\n{Fore.CYAN}Processing complete:{Style.RESET_ALL}")
    logger.info(f"  Total files: {total_files}")
    logger.info(f"  {Fore.GREEN}Successful: {successful_files}{Style.RESET_ALL}")
    if failed_files > 0:
        logger.info(f"  {Fore.RED}Failed: {failed_files}{Style.RESET_ALL}")

    # Exit with error code if any files failed
    if failed_files > 0:
        sys.exit(1)


def parse_file(file_path: Path, file_type: FileType) -> Optional[dict]:
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


def generate_outputs(
    metadata: dict, output_path: Path, base_name: str, output_format: str
):
    """Generate documentation outputs in the specified format(s)"""
    logger = get_logger(__name__)

    formats_to_generate = []
    if output_format == "all":
        formats_to_generate.extend([MARKDOWN_FORMAT, JSON_FORMAT])
    else:
        formats_to_generate.append(output_format)

    if MARKDOWN_FORMAT in formats_to_generate:
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(metadata)
        markdown_file = output_path / f"{base_name}.md"
        try:
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            logger.info(f"  Generated Markdown: {markdown_file}")
        except IOError as e:
            logger.error(f"  Failed to write Markdown file: {e}")

    if JSON_FORMAT in formats_to_generate:
        json_gen = JSONGenerator()
        json_content = json_gen.generate(metadata)
        json_file = output_path / f"{base_name}.json"
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                f.write(json_content)
            logger.info(f"  Generated JSON: {json_file}")
        except IOError as e:
            logger.error(f"  Failed to write JSON file: {e}")


if __name__ == "__main__":
    main()
