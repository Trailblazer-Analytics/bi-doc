"""
Comprehensive metadata schemas for Power BI and Tableau files.

This module defines all possible metadata fields that can be extracted from
Power BI and Tableau files, ensuring complete documentation coverage.
"""

from typing import Any, Dict, List, Optional

# Power BI Comprehensive Metadata Schema
POWERBI_METADATA_SCHEMA = {
    # Basic file information
    "file": str,
    "type": str,
    "file_path": str,
    "file_size": Optional[int],
    "last_modified": Optional[str],
    "created_date": Optional[str],
    # Model information
    "model_info": {
        "name": str,
        "description": str,
        "culture": str,
        "compatibility_level": Optional[int],
        "default_mode": str,
        "version": Optional[str],
        "annotations": Dict[str, Any],
    },
    # Enhanced data sources
    "data_sources": [
        {
            "name": str,
            "type": str,
            "connection": str,
            "query": str,
            "server": str,
            "database": str,
            "schema": str,
            "authentication_type": str,
            "privacy_setting": str,
            "refresh_policy": Dict[str, Any],
            "connection_details": Dict[str, Any],
        }
    ],
    # Enhanced tables with complete information
    "tables": [
        {
            "name": str,
            "description": str,
            "is_hidden": bool,
            "is_date_table": bool,
            "source_table": str,
            "refresh_policy": Dict[str, Any],
            "partitions": List[Dict[str, Any]],
            "columns": [
                {
                    "name": str,
                    "data_type": str,
                    "is_hidden": bool,
                    "is_key": bool,
                    "is_nullable": bool,
                    "encoding": str,
                    "description": str,
                    "display_folder": str,
                    "format_string": str,
                    "source_column": str,
                    "sort_by_column": str,
                    "summarize_by": str,
                    "data_category": str,
                    "annotations": Dict[str, Any],
                }
            ],
            "row_count": Optional[int],
            "annotations": Dict[str, Any],
        }
    ],
    # Enhanced relationships
    "relationships": [
        {
            "name": str,
            "from_table": str,
            "from_column": str,
            "to_table": str,
            "to_column": str,
            "cardinality": str,
            "is_active": bool,
            "cross_filter_direction": str,
            "security_filtering_behavior": str,
            "rely_on_referential_integrity": bool,
            "annotations": Dict[str, Any],
        }
    ],
    # Enhanced measures with formatting
    "measures": [
        {
            "name": str,
            "table": str,
            "expression": str,
            "expression_formatted": str,  # DAX formatted version
            "format_string": str,
            "description": str,
            "display_folder": str,
            "is_hidden": bool,
            "data_type": str,
            "kpi": Optional[Dict[str, Any]],
            "detail_rows_expression": str,
            "annotations": Dict[str, Any],
        }
    ],
    # Enhanced calculated columns
    "calculated_columns": [
        {
            "name": str,
            "table": str,
            "expression": str,
            "expression_formatted": str,  # DAX formatted version
            "data_type": str,
            "format_string": str,
            "description": str,
            "is_hidden": bool,
            "display_folder": str,
            "sort_by_column": str,
            "summarize_by": str,
            "data_category": str,
            "annotations": Dict[str, Any],
        }
    ],
    # Calculated tables
    "calculated_tables": [
        {
            "name": str,
            "expression": str,
            "expression_formatted": str,  # DAX formatted version
            "description": str,
            "is_hidden": bool,
            "annotations": Dict[str, Any],
        }
    ],
    # Enhanced visualizations with complete structure
    "visualizations": [
        {
            "page": str,
            "page_id": str,
            "page_description": str,
            "page_hidden": bool,
            "page_order": int,
            "visuals": [
                {
                    "id": str,
                    "type": str,
                    "title": str,
                    "subtitle": str,
                    "x": float,
                    "y": float,
                    "width": float,
                    "height": float,
                    "z_order": int,
                    "fields": List[str],
                    "filters": List[Dict[str, Any]],
                    "interactions": Dict[str, Any],
                    "formatting": Dict[str, Any],
                    "data_bindings": Dict[str, Any],
                }
            ],
        }
    ],
    # Enhanced Power Query
    "power_query": {
        "queries": [
            {
                "name": str,
                "expression": str,
                "kind": str,
                "description": str,
                "is_privacy_sensitive": bool,
                "load_enabled": bool,
                "refresh_policy": Dict[str, Any],
            }
        ],
        "data_sources": List[Dict[str, Any]],
        "parameters": List[Dict[str, Any]],
    },
    # Role-Level Security
    "rls_roles": [
        {
            "name": str,
            "description": str,
            "table_permissions": [
                {
                    "table": str,
                    "filter_expression": str,
                    "filter_expression_formatted": str,  # DAX formatted
                }
            ],
            "model_permission": str,
            "annotations": Dict[str, Any],
        }
    ],
    # Hierarchies
    "hierarchies": [
        {
            "name": str,
            "table": str,
            "description": str,
            "is_hidden": bool,
            "display_folder": str,
            "levels": [
                {
                    "name": str,
                    "column": str,
                    "ordinal": int,
                }
            ],
            "annotations": Dict[str, Any],
        }
    ],
    # Translations
    "translations": [
        {
            "language": str,
            "objects": [
                {
                    "object_type": str,
                    "object_name": str,
                    "property": str,
                    "value": str,
                }
            ],
        }
    ],
    # Perspectives
    "perspectives": [
        {
            "name": str,
            "description": str,
            "objects": List[str],
            "annotations": Dict[str, Any],
        }
    ],
    # Culture and formatting
    "culture_info": {
        "culture": str,
        "date_format": str,
        "time_format": str,
        "currency_symbol": str,
        "thousand_separator": str,
        "decimal_separator": str,
    },
    # Model annotations and extended properties
    "model_annotations": Dict[str, Any],
    "extended_properties": Dict[str, Any],
}

# Tableau Comprehensive Metadata Schema
TABLEAU_METADATA_SCHEMA = {
    # Basic file information
    "file": str,
    "type": str,
    "file_path": str,
    "file_size": Optional[int],
    "last_modified": Optional[str],
    "created_date": Optional[str],
    # Workbook information
    "workbook_info": {
        "name": str,
        "version": str,
        "repository_url": str,
        "thumbnail": str,
        "show_tabs": bool,
        "locale": str,
        "created_by": str,
        "last_updated_by": str,
        "tags": List[str],
        "project": str,
        "site": str,
    },
    # Enhanced data sources with complete connection details
    "data_sources": [
        {
            "name": str,
            "caption": str,
            "type": str,
            "version": str,
            "inline": bool,
            "extract": bool,
            "connections": [
                {
                    "server": str,
                    "database": str,
                    "schema": str,
                    "connection_type": str,
                    "username": str,
                    "port": str,
                    "authentication": str,
                    "ssl_mode": str,
                    "initial_sql": str,
                    "vendor": str,
                    "driver": str,
                    "connection_attributes": Dict[str, Any],
                }
            ],
            "fields": [
                {
                    "name": str,
                    "caption": str,
                    "datatype": str,
                    "role": str,
                    "type": str,
                    "is_calculated": bool,
                    "calculation": str,
                    "calculation_formatted": str,  # Formatted calculation
                    "description": str,
                    "worksheets": List[str],
                    "default_aggregation": str,
                    "is_hidden": bool,
                    "aliases": Dict[str, str],
                    "folder": str,
                    "geo_role": str,
                    "semantic_role": str,
                }
            ],
            "extracts": [
                {
                    "connection": str,
                    "incremental": bool,
                    "refresh_schedule": Dict[str, Any],
                    "filters": List[Dict[str, Any]],
                    "aggregation": Dict[str, Any],
                }
            ],
            "refresh_info": Dict[str, Any],
        }
    ],
    # Enhanced worksheets with complete structure
    "worksheets": [
        {
            "name": str,
            "caption": str,
            "description": str,
            "data_source": str,
            "view_type": str,
            "show_title": bool,
            "fields_used": List[str],
            "filters": [
                {
                    "field": str,
                    "type": str,
                    "value": Any,
                    "function": str,
                    "include_null": bool,
                    "exclude": bool,
                }
            ],
            "parameters_used": List[str],
            "marks": {
                "type": str,
                "encoding": Dict[str, Any],
                "size": Dict[str, Any],
                "color": Dict[str, Any],
                "shape": Dict[str, Any],
                "label": Dict[str, Any],
                "tooltip": List[str],
                "detail": List[str],
            },
            "axes": {
                "columns": List[Dict[str, Any]],
                "rows": List[Dict[str, Any]],
            },
            "formatting": Dict[str, Any],
            "annotations": List[Dict[str, Any]],
            "reference_lines": List[Dict[str, Any]],
            "trend_lines": List[Dict[str, Any]],
            "table_calculations": List[Dict[str, Any]],
        }
    ],
    # Enhanced dashboards with layout information
    "dashboards": [
        {
            "name": str,
            "caption": str,
            "description": str,
            "size_type": str,
            "width": int,
            "height": int,
            "worksheets": List[str],
            "objects": [
                {
                    "type": str,
                    "name": str,
                    "x": float,
                    "y": float,
                    "width": float,
                    "height": float,
                    "worksheet": str,
                    "title": str,
                    "formatting": Dict[str, Any],
                    "interactions": Dict[str, Any],
                }
            ],
            "filters": List[Dict[str, Any]],
            "parameters": List[str],
            "device_layouts": List[Dict[str, Any]],
            "actions": [
                {
                    "name": str,
                    "type": str,
                    "source": str,
                    "target": str,
                    "fields": List[str],
                    "clear_all_filters": bool,
                }
            ],
        }
    ],
    # Enhanced parameters with complete configuration
    "parameters": [
        {
            "name": str,
            "caption": str,
            "datatype": str,
            "current_value": Any,
            "default_value": Any,
            "allowable_values": List[Any],
            "value_when_null": Any,
            "range": Dict[str, Any],
            "format": str,
            "description": str,
            "global": bool,
            "worksheets_used": List[str],
            "actions": List[Dict[str, Any]],
        }
    ],
    # Enhanced calculated fields with formatting
    "calculated_fields": [
        {
            "name": str,
            "caption": str,
            "datasource": str,
            "calculation": str,
            "calculation_formatted": str,  # Formatted calculation
            "datatype": str,
            "role": str,
            "description": str,
            "worksheets_used": List[str],
            "folder": str,
            "is_hidden": bool,
            "dependencies": List[str],
            "comment": str,
        }
    ],
    # Stories (Tableau's presentation feature)
    "stories": [
        {
            "name": str,
            "caption": str,
            "description": str,
            "story_points": [
                {
                    "caption": str,
                    "description": str,
                    "worksheet": str,
                    "dashboard": str,
                    "update_type": str,
                }
            ],
            "sizing": Dict[str, Any],
            "formatting": Dict[str, Any],
        }
    ],
    # Enhanced field usage analytics
    "field_usage": {
        "by_worksheet": Dict[str, List[str]],
        "by_dashboard": Dict[str, List[str]],
        "unused_fields": List[str],
        "most_used_fields": List[Dict[str, Any]],
        "field_dependencies": Dict[str, List[str]],
    },
    # Metadata and performance
    "metadata_records": [
        {
            "object_type": str,
            "object_name": str,
            "property": str,
            "value": str,
            "remote_name": str,
            "parent": str,
        }
    ],
    # Groups and sets
    "groups": [
        {
            "name": str,
            "caption": str,
            "field": str,
            "members": List[Dict[str, Any]],
            "description": str,
        }
    ],
    "sets": [
        {
            "name": str,
            "caption": str,
            "description": str,
            "condition": str,
            "fixed": bool,
            "members": List[Any],
        }
    ],
    # Formatting and themes
    "formatting": {
        "workbook_formatting": Dict[str, Any],
        "default_formatting": Dict[str, Any],
        "color_palettes": List[Dict[str, Any]],
        "fonts": Dict[str, Any],
    },
}


def get_default_powerbi_metadata() -> Dict[str, Any]:
    """Get default Power BI metadata structure with empty/not available values."""
    return {
        "file": "not available",
        "type": "Power BI",
        "file_path": "not available",
        "file_size": None,
        "last_modified": "not available",
        "created_date": "not available",
        "model_info": {
            "name": "not available",
            "description": "not available",
            "culture": "not available",
            "compatibility_level": None,
            "default_mode": "not available",
            "version": "not available",
            "annotations": {},
        },
        "data_sources": [],
        "tables": [],
        "relationships": [],
        "measures": [],
        "calculated_columns": [],
        "calculated_tables": [],
        "visualizations": [],
        "power_query": {
            "queries": [],
            "data_sources": [],
            "parameters": [],
        },
        "rls_roles": [],
        "hierarchies": [],
        "translations": [],
        "perspectives": [],
        "culture_info": {
            "culture": "not available",
            "date_format": "not available",
            "time_format": "not available",
            "currency_symbol": "not available",
            "thousand_separator": "not available",
            "decimal_separator": "not available",
        },
        "model_annotations": {},
        "extended_properties": {},
    }


def get_default_tableau_metadata() -> Dict[str, Any]:
    """Get default Tableau metadata structure with empty/not available values."""
    return {
        "file": "not available",
        "type": "Tableau",
        "file_path": "not available",
        "file_size": None,
        "last_modified": "not available",
        "created_date": "not available",
        "workbook_info": {
            "name": "not available",
            "version": "not available",
            "repository_url": "not available",
            "thumbnail": "not available",
            "show_tabs": True,
            "locale": "not available",
            "created_by": "not available",
            "last_updated_by": "not available",
            "tags": [],
            "project": "not available",
            "site": "not available",
        },
        "data_sources": [],
        "worksheets": [],
        "dashboards": [],
        "parameters": [],
        "calculated_fields": [],
        "stories": [],
        "field_usage": {
            "by_worksheet": {},
            "by_dashboard": {},
            "unused_fields": [],
            "most_used_fields": [],
            "field_dependencies": {},
        },
        "metadata_records": [],
        "groups": [],
        "sets": [],
        "formatting": {
            "workbook_formatting": {},
            "default_formatting": {},
            "color_palettes": [],
            "fonts": {},
        },
    }


def ensure_complete_metadata(
    metadata: Dict[str, Any], file_type: str
) -> Dict[str, Any]:
    """
    Ensure that metadata contains all possible fields for the file type.

    Args:
        metadata: Existing metadata dictionary
        file_type: "Power BI" or "Tableau"

    Returns:
        Complete metadata dictionary with all fields present
    """
    if file_type == "Power BI":
        default = get_default_powerbi_metadata()
    elif file_type == "Tableau":
        default = get_default_tableau_metadata()
    else:
        return metadata

    # Deep merge the metadata with defaults
    def deep_merge(
        default_dict: Dict[str, Any], actual_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge dictionaries, preserving actual values."""
        result = default_dict.copy()

        for key, value in actual_dict.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    return deep_merge(default, metadata)
