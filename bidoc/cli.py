"""Command Line Interface for BI Documentation Tool"""

import sys

import click

from bidoc.constants import DEFAULT_DOCS_FOLDER

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
    from .cli_handlers import process_cli_command
    
    exit_code = process_cli_command(
        input_files=input_files,
        output_dir=output_dir,
        output_format=output_format,
        verbose=verbose,
        log_file=log_file,
        with_summary=with_summary,
        config_path=config_path
    )
    
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
