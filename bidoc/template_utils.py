"""Template management utilities for external Jinja2 templates."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Manages external Jinja2 templates for markdown generation."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize template manager with template directory.
        
        Args:
            template_dir: Directory containing template files. 
                         Defaults to bidoc/templates/
        """
        self.logger = logging.getLogger(__name__)
        
        if template_dir is None:
            # Default to templates directory relative to this file
            template_dir = Path(__file__).parent / "templates"
        
        if not template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        
        self.logger.debug(f"Initialized template manager with directory: {template_dir}")

    def load_template(self, template_name: str) -> Template:
        """Load a template by name.
        
        Args:
            template_name: Name of the template file (e.g., 'powerbi.md.j2')
            
        Returns:
            Loaded Jinja2 template
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        try:
            template = self.env.get_template(template_name)
            self.logger.debug(f"Loaded template: {template_name}")
            return template
        except Exception as e:
            self.logger.error(f"Failed to load template {template_name}: {e}")
            raise FileNotFoundError(f"Template not found: {template_name}") from e

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Template context variables
            
        Returns:
            Rendered template content
        """
        template = self.load_template(template_name)
        
        try:
            content = template.render(**context)
            self.logger.debug(f"Rendered template {template_name} with {len(context)} context vars")
            return content
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise

    def list_templates(self) -> list[str]:
        """List all available template files.
        
        Returns:
            List of template filenames
        """
        templates = []
        for template_file in self.template_dir.glob("*.j2"):
            templates.append(template_file.name)
        
        self.logger.debug(f"Found {len(templates)} templates")
        return sorted(templates)


# Global template manager instance
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Get or create global template manager instance.
    
    Returns:
        Global TemplateManager instance
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


def render_powerbi_template(metadata: Dict[str, Any]) -> str:
    """Render PowerBI markdown template with metadata.
    
    Args:
        metadata: PowerBI metadata dictionary
        
    Returns:
        Rendered markdown content
    """
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
    """Render Tableau markdown template with metadata.
    
    Args:
        metadata: Tableau metadata dictionary
        
    Returns:
        Rendered markdown content
    """
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


def render_generic_template(metadata: Dict[str, Any]) -> str:
    """Render generic markdown template with metadata.
    
    Args:
        metadata: Generic metadata dictionary
        
    Returns:
        Rendered markdown content
    """
    context = {
        "file_name": metadata.get("file", "Unknown"),
        "file_type": metadata.get("type", "Unknown"),
        "file_path": metadata.get("file_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata_json": json.dumps(metadata, indent=2, default=str),
    }
    
    manager = get_template_manager()
    return manager.render_template("generic.md.j2", context)