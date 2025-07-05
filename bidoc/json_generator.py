"""JSON documentat        # Add generation metadata
        output_metadata = {
            **metadata,
            "generation_info": {
                "generated_at": datetime.now().isoformat(),
                "generator": "BI Documentation Tool",
                "version": "0.1.0",
            },
        }tor"""

import json
import logging
from datetime import datetime
from typing import Any, Dict


class JSONGenerator:
    """Generate JSON documentation from extracted metadata"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate(self, metadata: Dict[str, Any]) -> str:
        """Generate JSON documentation from metadata"""
        self.logger.debug("Generating JSON documentation")

        # Add generation metadata
        output_metadata = {
            **metadata,
            "generation_info": {
                "generated_at": datetime.now().isoformat(),
                "generator": "BI Documentation Tool",
                "version": "1.0.0",
            },
        }

        # Clean and format the metadata
        cleaned_metadata = self._clean_metadata(output_metadata)

        # Generate formatted JSON
        return json.dumps(
            cleaned_metadata,
            indent=2,
            ensure_ascii=False,
            default=self._json_serializer,
        )

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize metadata for JSON output"""

        # Create a copy to avoid modifying the original
        cleaned = dict(metadata)

        # Ensure all required fields exist with default values
        if "file" not in cleaned:
            cleaned["file"] = "unknown.file"

        if "type" not in cleaned:
            cleaned["type"] = "Unknown"

        # Standardize structure based on file type
        file_type = cleaned.get("type", "Unknown")

        if file_type == "Power BI":
            cleaned = self._standardize_powerbi_metadata(cleaned)
        elif file_type == "Tableau":
            cleaned = self._standardize_tableau_metadata(cleaned)

        return cleaned

    def _standardize_powerbi_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize Power BI metadata structure"""

        # Ensure all expected sections exist
        default_sections = {
            "model_info": {},
            "data_sources": [],
            "tables": [],
            "relationships": [],
            "measures": [],
            "calculated_columns": [],
            "calculated_tables": [],
            "visualizations": [],
            "power_query": {},
            "rls_roles": [],
            "hierarchies": [],
            "translations": [],
            "perspectives": [],
            "culture_info": {},
            "model_annotations": {},
            "extended_properties": {},
        }

        for section, default_value in default_sections.items():
            if section not in metadata:
                metadata[section] = default_value

        # Clean up table structure
        for table in metadata.get("tables", []):
            if "columns" not in table:
                table["columns"] = []

            # Ensure each column has required fields
            for column in table["columns"]:
                if "name" not in column:
                    column["name"] = "Unknown"
                if "data_type" not in column:
                    column["data_type"] = "Unknown"
                if "is_hidden" not in column:
                    column["is_hidden"] = False

        # Clean up measures
        for measure in metadata.get("measures", []):
            if "name" not in measure:
                measure["name"] = "Unknown"
            if "expression" not in measure:
                measure["expression"] = ""
            if "table" not in measure:
                measure["table"] = ""

        # Clean up relationships
        for relationship in metadata.get("relationships", []):
            required_fields = ["from_table", "from_column", "to_table", "to_column"]
            for field in required_fields:
                if field not in relationship:
                    relationship[field] = ""

            if "cardinality" not in relationship:
                relationship["cardinality"] = "Unknown"
            if "is_active" not in relationship:
                relationship["is_active"] = True

        return metadata

    def _standardize_tableau_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize Tableau metadata structure"""

        # Ensure all expected sections exist
        default_sections = {
            "workbook_info": {},
            "data_sources": [],
            "worksheets": [],
            "dashboards": [],
            "parameters": [],
            "calculated_fields": [],
            "stories": [],
            "field_usage": {},
            "metadata_records": [],
            "groups": [],
            "sets": [],
            "formatting": {},
        }

        for section, default_value in default_sections.items():
            if section not in metadata:
                metadata[section] = default_value

        # Clean up data sources
        for data_source in metadata.get("data_sources", []):
            if "name" not in data_source:
                data_source["name"] = "Unknown"
            if "connections" not in data_source:
                data_source["connections"] = []
            if "fields" not in data_source:
                data_source["fields"] = []

            # Clean up fields
            for field in data_source["fields"]:
                if "name" not in field:
                    field["name"] = "Unknown"
                if "datatype" not in field:
                    field["datatype"] = "unknown"
                if "role" not in field:
                    field["role"] = "unknown"
                if "is_calculated" not in field:
                    field["is_calculated"] = False

        # Clean up worksheets
        for worksheet in metadata.get("worksheets", []):
            if "name" not in worksheet:
                worksheet["name"] = "Unknown"
            if "fields_used" not in worksheet:
                worksheet["fields_used"] = []
            if "filters" not in worksheet:
                worksheet["filters"] = []

        # Clean up dashboards
        for dashboard in metadata.get("dashboards", []):
            if "name" not in dashboard:
                dashboard["name"] = "Unknown"
            if "worksheets" not in dashboard:
                dashboard["worksheets"] = []
            if "objects" not in dashboard:
                dashboard["objects"] = []

        return metadata

    def _json_serializer(self, obj):
        """Custom JSON serializer for special object types"""
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return str(obj)

    def validate_json(self, json_string: str) -> bool:
        """Validate that the generated JSON is valid"""
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"Generated JSON is invalid: {str(e)}")
            return False

    def get_schema(self, file_type: str) -> Dict[str, Any]:
        """Get the JSON schema for a specific file type"""

        base_schema = {
            "type": "object",
            "properties": {
                "file": {"type": "string"},
                "type": {"type": "string"},
                "file_path": {"type": "string"},
                "generation_info": {
                    "type": "object",
                    "properties": {
                        "generated_at": {"type": "string"},
                        "generator": {"type": "string"},
                        "version": {"type": "string"},
                    },
                },
            },
            "required": ["file", "type"],
        }

        if file_type == "Power BI":
            base_schema["properties"].update(
                {
                    "data_sources": {"type": "array"},
                    "tables": {"type": "array"},
                    "relationships": {"type": "array"},
                    "measures": {"type": "array"},
                    "calculated_columns": {"type": "array"},
                    "visualizations": {"type": "array"},
                    "power_query": {"type": "object"},
                }
            )

        elif file_type == "Tableau":
            base_schema["properties"].update(
                {
                    "data_sources": {"type": "array"},
                    "worksheets": {"type": "array"},
                    "dashboards": {"type": "array"},
                    "parameters": {"type": "array"},
                    "calculated_fields": {"type": "array"},
                    "field_usage": {"type": "object"},
                }
            )

        return base_schema
