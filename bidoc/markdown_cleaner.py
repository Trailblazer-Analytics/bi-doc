"""Markdown cleaning utilities for formatting and linting compliance."""

import re
from typing import List


class MarkdownCleaner:
    """Utilities for cleaning and formatting markdown content to pass linting."""
    
    def __init__(self):
        self.seen_headings = {}
    
    def clean_markdown(self, content: str) -> str:
        """
        Clean up markdown formatting issues to pass markdownlint.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        # Reset state for each cleaning operation
        self.seen_headings = {}
        
        # Apply cleaning steps in order
        content = self._basic_line_cleaning(content)
        content = self._fix_code_spans(content)
        content = self._wrap_long_lines(content)
        content = self._fix_duplicate_headings(content)
        content = self._fix_blank_lines(content)
        content = self._fix_code_block_spacing(content)
        content = self._final_cleanup(content)
        
        return content
    
    def _basic_line_cleaning(self, content: str) -> str:
        """Remove trailing spaces and fix tabs."""
        lines = content.split("\n")
        
        # Remove trailing spaces from all lines (MD009)
        lines = [line.rstrip() for line in lines]
        
        # Remove any hard tabs and replace with spaces (MD010)
        lines = [line.replace("\t", "    ") for line in lines]
        
        return "\n".join(lines)
    
    def _fix_code_spans(self, content: str) -> str:
        """Fix code span spacing issues (MD038)."""
        lines = content.split("\n")
        
        for i, original_line in enumerate(lines):
            # Remove spaces at the beginning of code spans
            updated_line = re.sub(r"`\s+([^`]+)`", r"`\1`", original_line)
            # Remove spaces at the end of code spans
            updated_line = re.sub(r"`([^`]+)\s+`", r"`\1`", updated_line)
            # Remove spaces at both ends
            updated_line = re.sub(r"`\s+([^`]+)\s+`", r"`\1`", updated_line)
            lines[i] = updated_line
        
        return "\n".join(lines)
    
    def _wrap_long_lines(self, content: str) -> str:
        """Handle long lines by wrapping at 80 characters where possible (MD013)."""
        lines = content.split("\n")
        wrapped_lines = []
        
        for line in lines:
            if self._should_skip_wrapping(line):
                wrapped_lines.append(line)
            elif self._is_wrappable_list_item(line):
                wrapped_lines.extend(self._wrap_list_item(line))
            else:
                wrapped_lines.append(line)
        
        return "\n".join(wrapped_lines)
    
    def _should_skip_wrapping(self, line: str) -> bool:
        """Check if a line should be skipped for wrapping."""
        return (
            len(line) <= 80
            or line.strip().startswith("|")  # Table rows
            or line.strip().startswith("```")  # Code blocks
        )
    
    def _is_wrappable_list_item(self, line: str) -> bool:
        """Check if line is a wrappable list item."""
        return (
            line.strip().startswith("- **") 
            and ": " in line 
            and len(line) > 80
        )
    
    def _wrap_list_item(self, line: str) -> List[str]:
        """Wrap a long list item with key-value pairs."""
        indent = len(line) - len(line.lstrip())
        parts = line.split(": ", 1)
        
        if len(parts) == 2 and len(parts[0]) < 60:
            return [
                parts[0] + ":",
                " " * (indent + 2) + parts[1]
            ]
        else:
            return [line]
    
    def _fix_duplicate_headings(self, content: str) -> str:
        """Fix duplicate heading issues (MD024)."""
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            if line.startswith("#"):
                lines[i] = self._make_heading_unique(line)
        
        return "\n".join(lines)
    
    def _make_heading_unique(self, line: str) -> str:
        """Make a heading unique if it's a duplicate."""
        heading_text = line.lstrip("#").strip()
        
        if heading_text in self.seen_headings:
            self.seen_headings[heading_text] += 1
            level = len(line) - len(line.lstrip("#"))
            
            if level > 1:  # Sub-heading
                return f"{'#' * level} {heading_text} ({self.seen_headings[heading_text]})"
        else:
            self.seen_headings[heading_text] = 1
        
        return line
    
    def _fix_blank_lines(self, content: str) -> str:
        """Remove excessive blank lines (MD012)."""
        # More aggressive blank line removal
        # Remove any occurrence of 3+ consecutive newlines
        return re.sub(r"\n{3,}", "\n\n", content)
    
    def _fix_code_block_spacing(self, content: str) -> str:
        """Ensure fenced code blocks are surrounded by blank lines (MD031)."""
        lines = content.split("\n")
        result_lines = []
        in_code_block = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Starting a code block - ensure blank line before
                    if result_lines and result_lines[-1].strip() != "":
                        result_lines.append("")
                    result_lines.append(line)
                    in_code_block = True
                else:
                    # Ending a code block - ensure blank line after
                    result_lines.append(line)
                    if i < len(lines) - 1 and lines[i + 1].strip() != "":
                        result_lines.append("")
                    in_code_block = False
            else:
                result_lines.append(line)
        
        content = "\n".join(result_lines)
        
        # Clean up multiple blank lines again after code block processing
        return re.sub(r"\n{3,}", "\n\n", content)
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup and normalization."""
        # Remove blank lines at the very beginning
        content = content.lstrip("\n")
        
        # Ensure file ends with exactly one newline (MD047)
        content = content.rstrip() + "\n"
        
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


# Default cleaner instance for convenience
_default_cleaner = None


def get_markdown_cleaner() -> MarkdownCleaner:
    """Get the default markdown cleaner instance."""
    global _default_cleaner
    if _default_cleaner is None:
        _default_cleaner = MarkdownCleaner()
    return _default_cleaner


def clean_markdown(content: str) -> str:
    """
    Clean markdown content using the default cleaner.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Cleaned markdown content
    """
    cleaner = get_markdown_cleaner()
    return cleaner.clean_markdown(content)