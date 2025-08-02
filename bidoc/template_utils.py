"""Template utilities for loading and rendering Jinja2 templates."""

import os
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Manages template loading and rendering for different file types."""
    
    def __init__(self, templates_dir: Path = None):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory containing template files. Defaults to bidoc/templates
        """
        if templates_dir is None:
            # Default to templates directory relative to this module
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Cache for loaded templates
        self._template_cache = {}
    
    def get_template(self, template_name: str) -> Template:
        """
        Get a template by name with caching.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Jinja2 Template object
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        if template_name not in self._template_cache:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            self._template_cache[template_name] = self.env.get_template(template_name)
        
        return self._template_cache[template_name]
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Template context variables
            
        Returns:
            Rendered template string
        """
        template = self.get_template(template_name)
        return template.render(**context)
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
    
    def list_templates(self) -> list[str]:
        """
        List all available template files.
        
        Returns:
            List of template filenames
        """
        if not self.templates_dir.exists():
            return []
        
        return [
            f.name for f in self.templates_dir.iterdir() 
            if f.is_file() and f.suffix in ['.j2', '.jinja2', '.jinja']
        ]


# Default template manager instance
_default_manager = None


def get_template_manager() -> TemplateManager:
    """Get the default template manager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = TemplateManager()
    return _default_manager


def render_powerbi_template(metadata: Dict[str, Any]) -> str:
    """
    Render the PowerBI markdown template.
    
    Args:
        metadata: PowerBI metadata dictionary
        
    Returns:
        Rendered markdown string
    """
    from datetime import datetime
    
    context = {
        "file_name": metadata.get("file", "Unknown"),
        "file_type": metadata.get("type", "Unknown"),
        "file_path": metadata.get("file_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_summary": metadata.get("ai_summary", ""),
        "data_sources": metadata.get("data_sources", []),
        "tables": metadata.get("tables", []),
        "measures": metadata.get("measures", []),
        "calculated_columns": metadata.get("calculated_columns", []),
        "relationships": metadata.get("relationships", []),
        "visualizations": metadata.get("visualizations", []),
        "power_query": metadata.get("power_query", {}),
    }
    
    manager = get_template_manager()
    return manager.render_template("powerbi.md.j2", context)


def render_tableau_template(metadata: Dict[str, Any]) -> str:
    """
    Render the Tableau markdown template.
    
    Args:
        metadata: Tableau metadata dictionary
        
    Returns:
        Rendered markdown string
    """
    from datetime import datetime
    
    context = {
        "file_name": metadata.get("file", "Unknown"),
        "file_type": metadata.get("type", "Unknown"),
        "file_path": metadata.get("file_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_summary": metadata.get("ai_summary", ""),
        "data_sources": metadata.get("data_sources", []),
        "calculated_fields": metadata.get("calculated_fields", []),
        "worksheets": metadata.get("worksheets", []),
        "dashboards": metadata.get("dashboards", []),
        "parameters": metadata.get("parameters", []),
        "field_usage": metadata.get("field_usage", {}),
    }
    
    manager = get_template_manager()
    return manager.render_template("tableau.md.j2", context)