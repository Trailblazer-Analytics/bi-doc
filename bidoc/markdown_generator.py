"""Markdown documentation generator"""

import logging
from typing import Any, Dict

from bidoc.template_utils import (
    render_generic_template,
    render_powerbi_template,
    render_tableau_template,
)


class MarkdownGenerator:
    """Generate Markdown documentation from extracted metadata"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate(self, metadata: Dict[str, Any]) -> str:
        """Generate Markdown documentation from metadata"""
        self.logger.debug("Generating Markdown documentation")

        # Determine file type and use appropriate template
        file_type = metadata.get("type", "Unknown")

        if file_type == "Power BI":
            content = self._generate_powerbi_markdown(metadata)
        elif file_type == "Tableau":
            content = self._generate_tableau_markdown(metadata)
        else:
            content = self._generate_generic_markdown(metadata)

        # Clean up markdown formatting issues
        return self._clean_markdown(content)

    def _generate_powerbi_markdown(self, metadata: Dict[str, Any]) -> str:
        """Generate Markdown for Power BI files"""
        return render_powerbi_template(metadata)

    def _generate_tableau_markdown(self, metadata: Dict[str, Any]) -> str:
        """Generate Markdown for Tableau files"""
        return render_tableau_template(metadata)

    def _generate_generic_markdown(self, metadata: Dict[str, Any]) -> str:
        """Generate generic Markdown for unknown file types"""
        return render_generic_template(metadata)

    def _clean_markdown(self, content: str) -> str:
        """Clean up markdown formatting issues to pass markdownlint"""
        import re

        # First, split into lines for easier processing
        lines = content.split("\n")

        # Remove trailing spaces from all lines (MD009)
        lines = [line.rstrip() for line in lines]

        # Remove any hard tabs and replace with spaces (MD010)
        lines = [line.replace("\t", "    ") for line in lines]

        # Fix code span issues by removing extra spaces (MD038)
        # Handle multiple patterns: spaces at start, end, or both
        for i, original_line in enumerate(lines):
            # Remove spaces at the beginning of code spans
            updated_line = re.sub(r"`\s+([^`]+)`", r"`\1`", original_line)
            # Remove spaces at the end of code spans
            updated_line = re.sub(r"`([^`]+)\s+`", r"`\1`", updated_line)
            # Remove spaces at both ends
            updated_line = re.sub(r"`\s+([^`]+)\s+`", r"`\1`", updated_line)
            lines[i] = updated_line

        # Handle long lines by wrapping at 80 characters where possible (MD013)
        wrapped_lines = []
        for line in lines:
            if (
                len(line) <= 80
                or line.strip().startswith("|")
                or line.strip().startswith("```")
            ):
                # Don't wrap table rows, code blocks, or already short lines
                wrapped_lines.append(line)
            elif line.strip().startswith("- **") and ": " in line:
                # Wrap list items with key-value pairs
                if len(line) > 80:
                    indent = len(line) - len(line.lstrip())
                    parts = line.split(": ", 1)
                    if len(parts) == 2 and len(parts[0]) < 60:
                        wrapped_lines.append(parts[0] + ":")
                        wrapped_lines.append(" " * (indent + 2) + parts[1])
                    else:
                        wrapped_lines.append(line)
                else:
                    wrapped_lines.append(line)
            else:
                wrapped_lines.append(line)

        lines = wrapped_lines

        # Track headings to fix duplicate issues (MD024)
        seen_headings = {}
        for i, line in enumerate(lines):
            if line.startswith("#"):
                # Extract heading text (remove # and strip)
                heading_text = line.lstrip("#").strip()
                if heading_text in seen_headings:
                    # Make heading unique by adding context
                    seen_headings[heading_text] += 1
                    # Add section number or parent context
                    level = len(line) - len(line.lstrip("#"))
                    if level > 1:  # Sub-heading
                        lines[i] = (
                            f"{'#' * level} {heading_text} ({seen_headings[heading_text]})"
                        )
                else:
                    seen_headings[heading_text] = 1

        # Rejoin content
        content = "\n".join(lines)

        # More aggressive blank line removal (MD012)
        # Remove any occurrence of 3+ consecutive newlines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Ensure fenced code blocks are surrounded by blank lines (MD031)
        # Split content to handle code blocks more carefully
        parts = []
        current_part = ""
        in_code_block = False

        for line in content.split("\n"):
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Starting a code block
                    if current_part and not current_part.endswith("\n\n"):
                        current_part = current_part.rstrip() + "\n\n"
                    current_part += line + "\n"
                    in_code_block = True
                else:
                    # Ending a code block
                    current_part += line + "\n\n"
                    in_code_block = False
            elif in_code_block:
                current_part += line + "\n"
            elif line.strip() == "":
                current_part += "\n"
            else:
                current_part += line + "\n"

        content = current_part

        # Clean up multiple blank lines again after code block processing
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Remove blank lines at the very beginning
        content = content.lstrip("\n")

        # Ensure file ends with exactly one newline (MD047)
        content = content.rstrip() + "\n"

        # Final cleanup of any remaining issues
        # Remove trailing spaces that might have been reintroduced
        lines = content.split("\n")
        lines = [line.rstrip() for line in lines]
        content = "\n".join(lines)

        # Ensure exactly one final newline
        if not content.endswith("\n"):
            content += "\n"
        elif content.endswith("\n\n"):
            content = content.rstrip("\n") + "\n"

        return content
