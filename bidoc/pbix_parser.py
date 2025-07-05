"""Power BI (.pbix) file parser using PBIXRay"""

import json
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pandas as pd

if TYPE_CHECKING:
    from pbixray import PBIXRay
else:
    try:
        from pbixray import PBIXRay
    except ImportError:
        PBIXRay = None

from bidoc.dax_formatter import DAXFormatter, format_dax_expression
from bidoc.metadata_schemas import (
    ensure_complete_metadata,
    get_default_powerbi_metadata,
)
from bidoc.utils import MetadataExtractor


class PowerBIParser(MetadataExtractor):
    """Parser for Power BI .pbix files"""

    def __init__(self):
        super().__init__()
        if PBIXRay is None:
            raise ImportError(
                "PBIXRay library is required. Install with: pip install pbixray"
            )
        self.dax_formatter = DAXFormatter()

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a Power BI .pbix file and extract metadata"""
        self.logger.info(f"Parsing Power BI file: {file_path.name}")

        # Start with comprehensive default metadata structure
        metadata = get_default_powerbi_metadata()

        # Update basic file information
        metadata.update(
            {
                "file": file_path.name,
                "type": "Power BI",
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size if file_path.exists() else None,
                "last_modified": (
                    str(file_path.stat().st_mtime)
                    if file_path.exists()
                    else "not available"
                ),
            }
        )

        try:
            # Initialize PBIXRay
            model = PBIXRay(str(file_path))

            # Extract and enhance model information
            metadata["model_info"] = self._extract_model_info(model)

            # Overwrite default values with extracted data
            metadata.update(
                {
                    "data_sources": self._extract_data_sources(model),
                    "tables": self._extract_tables(model),
                    "relationships": self._extract_relationships(model),
                    "measures": self._extract_measures(model),
                    "calculated_columns": self._extract_calculated_columns(model),
                    "calculated_tables": self._extract_calculated_tables(model),
                    "visualizations": self._extract_visualizations(file_path),
                    "power_query": self._extract_power_query(model),
                    "rls_roles": self._extract_rls_roles(model),
                    "hierarchies": self._extract_hierarchies(model),
                    "culture_info": self._extract_culture_info(model),
                    "translations": self._extract_translations(model),
                    "perspectives": self._extract_perspectives(model),
                    "annotations": self._extract_model_annotations(model),
                    "extended_properties": self._extract_extended_properties(model),
                }
            )

            # Ensure all metadata fields are present
            metadata = ensure_complete_metadata(metadata, "Power BI")

            self._log_extraction_summary(metadata)
            return metadata

        except Exception as e:
            self.logger.error(f"Failed to parse Power BI file: {str(e)}")
            # Return the complete default structure even if parsing fails
            return ensure_complete_metadata(metadata, "Power BI")

    def _extract_model_info(self, model: "PBIXRay") -> Dict[str, Any]:
        """Extract model-level information"""
        self.log_extraction_progress("Extracting model information")

        model_info = {
            "name": "not available",
            "description": "not available",
            "culture": "not available",
            "compatibility_level": None,
            "default_mode": "not available",
            "version": "not available",
            "annotations": {},
        }

        try:
            # Try to extract model-level information from PBIXRay
            if hasattr(model, "model"):
                model_data = getattr(model, "model", None)
                if model_data is not None:
                    model_info["name"] = str(
                        getattr(model_data, "name", "not available")
                    )
                    model_info["description"] = str(
                        getattr(model_data, "description", "not available")
                        or "not available"
                    )
                    model_info["culture"] = str(
                        getattr(model_data, "culture", "not available")
                        or "not available"
                    )
                    compatibility_level = getattr(
                        model_data, "compatibilityLevel", None
                    )
                    if compatibility_level is not None:
                        model_info["compatibility_level"] = compatibility_level
        except Exception as e:
            self.logger.debug(f"Could not extract model info: {str(e)}")

        self.log_extraction_progress("Model information extracted")
        return model_info

    def _extract_data_sources(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract data source information"""
        self.log_extraction_progress("Extracting data sources")

        data_sources = []

        try:
            # Get Power Query information if available
            if hasattr(model, "power_query"):
                pq_data = model.power_query

                if pq_data is not None:
                    try:
                        # Handle different types of power_query data safely
                        if isinstance(pq_data, dict) or hasattr(pq_data, "items"):
                            query_items = pq_data.items()
                        else:
                            # Skip if we can't iterate safely
                            query_items = []

                        for query_name, query_content in query_items:
                            # Extract connection info from M code
                            source_info = self._parse_m_code_for_source(
                                str(query_content)
                            )
                            if source_info:
                                data_sources.append(
                                    {
                                        "name": str(query_name),
                                        "type": source_info.get("type", "Unknown"),
                                        "connection": source_info.get("connection", ""),
                                        "query": str(query_content),
                                    }
                                )

                    except Exception as inner_e:
                        self.logger.debug(
                            f"Error processing Power Query items: {str(inner_e)}"
                        )

        except Exception as e:
            self.logger.debug(f"Could not extract Power Query sources: {str(e)}")

        # If no Power Query sources found, create a generic entry
        if not data_sources:
            data_sources.append(
                {
                    "name": "Data Model",
                    "type": "Imported Data",
                    "connection": "Data imported into model",
                    "query": "",
                }
            )

        self.log_extraction_progress("Data sources extracted", len(data_sources))
        return data_sources

    def _extract_tables(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract table and column information"""
        self.log_extraction_progress("Extracting tables and columns")

        tables = []

        try:
            # Get schema information
            if hasattr(model, "schema"):
                schema_df = model.schema

                if schema_df is not None and not schema_df.empty:
                    # Debug: Log available columns
                    self.logger.debug(f"Schema columns: {list(schema_df.columns)}")

                    # Use correct column names from PBIXRay
                    if "TableName" in schema_df.columns:
                        unique_tables = schema_df["TableName"].unique()

                        for table_name in unique_tables:
                            if pd.isna(table_name):
                                continue

                            table_columns = schema_df[
                                schema_df["TableName"] == table_name
                            ]

                            columns = []
                            for _, row in table_columns.iterrows():
                                # Use correct column names from PBIXRay
                                column_name = row.get("ColumnName", "")
                                data_type = row.get("PandasDataType", "Unknown")

                                columns.append(
                                    {
                                        "name": str(column_name),
                                        "data_type": str(data_type),
                                        "is_hidden": bool(row.get("IsHidden", False)),
                                        "description": str(row.get("Description", "")),
                                    }
                                )

                            tables.append(
                                {
                                    "name": str(table_name),
                                    "columns": columns,
                                    "row_count": None,
                                }
                            )
                    else:
                        self.logger.debug("No table column found in schema")

        except Exception as e:
            self.logger.debug(f"Error extracting tables: {str(e)}")
            # Try alternative method
            try:
                if hasattr(model, "tables") and model.tables:
                    for table_name in model.tables:
                        tables.append(
                            {
                                "name": str(table_name),
                                "columns": [],
                                "row_count": None,
                            }
                        )
            except Exception as e2:
                self.logger.debug(f"Alternative table extraction failed: {str(e2)}")

        self.log_extraction_progress("Tables extracted", len(tables))
        return tables

    def _extract_relationships(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract table relationships"""
        self.log_extraction_progress("Extracting relationships")

        relationships = []

        try:
            if hasattr(model, "relationships"):
                rel_df = model.relationships

                if rel_df is not None and not rel_df.empty:
                    # Debug: Log available columns
                    self.logger.debug(f"Relationships columns: {list(rel_df.columns)}")

                    for _, row in rel_df.iterrows():
                        # Use correct column names from PBIXRay
                        from_table = row.get("FromTableName", "")
                        from_column = row.get("FromColumnName", "")
                        to_table = row.get("ToTableName", "")
                        to_column = row.get("ToColumnName", "")
                        cardinality = row.get("Cardinality", "")

                        relationships.append(
                            {
                                "from_table": str(from_table),
                                "from_column": str(from_column),
                                "to_table": str(to_table),
                                "to_column": str(to_column),
                                "cardinality": str(cardinality),
                                "is_active": bool(row.get("IsActive", True)),
                                "cross_filter_direction": str(
                                    row.get("CrossFilteringBehavior", "")
                                ),
                            }
                        )
        except Exception as e:
            self.logger.debug(f"Error extracting relationships: {str(e)}")

        self.log_extraction_progress("Relationships extracted", len(relationships))
        return relationships

    def _extract_measures(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract DAX measures"""
        self.log_extraction_progress("Extracting DAX measures")

        measures = []

        try:
            if hasattr(model, "dax_measures"):
                measures_df = model.dax_measures

                if measures_df is not None and not measures_df.empty:
                    # Debug: Log available columns
                    self.logger.debug(f"Measures columns: {list(measures_df.columns)}")

                    for _, row in measures_df.iterrows():
                        # Use correct column names from PBIXRay
                        measure_name = row.get("Name", "")
                        table_name = row.get("TableName", "")
                        expression = row.get("Expression", "")

                        measures.append(
                            {
                                "name": str(measure_name),
                                "table": str(table_name),
                                "expression": str(expression),
                                "expression_formatted": format_dax_expression(
                                    str(expression)
                                ),
                                "format_string": str(
                                    row.get("FormatString", "not available")
                                ),
                                "description": str(
                                    row.get("Description", "not available")
                                ),
                                "display_folder": str(
                                    row.get("DisplayFolder", "not available")
                                ),
                                "is_hidden": bool(row.get("IsHidden", False)),
                                "data_type": str(row.get("DataType", "not available")),
                            }
                        )
        except Exception as e:
            self.logger.debug(f"Error extracting measures: {str(e)}")

        self.log_extraction_progress("Measures extracted", len(measures))
        return measures

    def _extract_calculated_columns(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract calculated columns"""
        self.log_extraction_progress("Extracting calculated columns")

        calculated_columns = []

        try:
            if hasattr(model, "dax_columns"):
                columns_df = model.dax_columns

                if columns_df is not None and not columns_df.empty:
                    # Debug: Log available columns
                    self.logger.debug(
                        f"Calculated columns columns: {list(columns_df.columns)}"
                    )

                    for _, row in columns_df.iterrows():
                        # Use correct column names from PBIXRay
                        column_name = row.get("ColumnName", "")
                        table_name = row.get("TableName", "")
                        expression = row.get("Expression", "")

                        calculated_columns.append(
                            {
                                "name": str(column_name),
                                "table": str(table_name),
                                "expression": str(expression),
                                "expression_formatted": format_dax_expression(
                                    str(expression)
                                ),
                                "data_type": str(row.get("DataType", "not available")),
                                "format_string": str(
                                    row.get("FormatString", "not available")
                                ),
                                "description": str(
                                    row.get("Description", "not available")
                                ),
                                "is_hidden": bool(row.get("IsHidden", False)),
                                "display_folder": str(
                                    row.get("DisplayFolder", "not available")
                                ),
                                "sort_by_column": str(
                                    row.get("SortByColumn", "not available")
                                ),
                                "summarize_by": str(
                                    row.get("SummarizeBy", "not available")
                                ),
                                "data_category": str(
                                    row.get("DataCategory", "not available")
                                ),
                            }
                        )
        except Exception as e:
            self.logger.debug(f"Error extracting calculated columns: {str(e)}")

        self.log_extraction_progress(
            "Calculated columns extracted", len(calculated_columns)
        )
        return calculated_columns

    def _extract_calculated_tables(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract calculated tables"""
        self.log_extraction_progress("Extracting calculated tables")

        calculated_tables = []

        try:
            # Check if model has calculated tables information
            calc_tables_df = getattr(model, "calculated_tables", None)
            if calc_tables_df is not None and not calc_tables_df.empty:
                for _, row in calc_tables_df.iterrows():
                    table_name = row.get("TableName", "Unknown")
                    expression = row.get("Expression", "")

                    calculated_tables.append(
                        {
                            "name": str(table_name),
                            "expression": str(expression),
                            "expression_formatted": (
                                self.dax_formatter.format(str(expression))
                                if expression
                                else "not available"
                            ),
                            "description": str(row.get("Description", "not available")),
                            "is_hidden": bool(row.get("IsHidden", False)),
                            "annotations": {},
                        }
                    )
        except Exception as e:
            self.logger.debug(f"Error extracting calculated tables: {str(e)}")

        self.log_extraction_progress(
            "Calculated tables extracted", len(calculated_tables)
        )
        return calculated_tables

    def _extract_visualizations(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract report layout and visualization information"""
        self.log_extraction_progress("Extracting visualizations")

        visualizations = []

        try:
            # Extract layout JSON from .pbix file
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Look for Report/Layout file
                layout_files = [f for f in zip_file.namelist() if "Report/Layout" in f]

                for layout_file in layout_files:
                    layout_content = zip_file.read(layout_file)

                    # Decode and clean the JSON (handle UTF-16 and control characters)
                    try:
                        # Try UTF-8 first
                        layout_str = layout_content.decode("utf-8")
                    except UnicodeDecodeError:
                        # Fall back to UTF-16
                        layout_str = layout_content.decode("utf-16le")

                    # Remove control characters
                    layout_str = self._clean_layout_json(layout_str)

                    # Parse JSON
                    layout_data = json.loads(layout_str)

                    # Extract visualization info
                    pages = self._parse_layout_json(layout_data)
                    visualizations.extend(pages)

        except Exception as e:
            self.logger.debug(f"Error extracting visualizations: {str(e)}")
            # Return a placeholder if extraction fails
            visualizations = [
                {
                    "page": "Report Pages",
                    "visuals": [
                        {
                            "type": "Unknown",
                            "title": "Visualizations present (detailed extraction failed)",
                            "fields": [],
                        }
                    ],
                }
            ]

        self.log_extraction_progress("Visualizations extracted", len(visualizations))
        return visualizations

    def _extract_power_query(self, model: "PBIXRay") -> Dict[str, str]:
        """Extract Power Query M code"""
        self.log_extraction_progress("Extracting Power Query code")

        power_query = {}

        try:
            if hasattr(model, "power_query"):
                pq_data = model.power_query

                # Handle different types of power_query data
                if pq_data is not None:
                    if isinstance(pq_data, dict):
                        power_query = pq_data
                    elif hasattr(pq_data, "to_dict"):
                        power_query = pq_data.to_dict()
                    elif hasattr(pq_data, "__iter__"):
                        # Handle iterable but avoid DataFrame boolean ambiguity
                        try:
                            power_query = dict(pq_data)
                        except Exception:
                            # If conversion fails, create a summary
                            power_query = {
                                "Summary": f"Power Query data available ({type(pq_data).__name__})"
                            }
                    else:
                        power_query = {"Content": str(pq_data)}

        except Exception as e:
            self.logger.debug(f"Error extracting Power Query: {str(e)}")

        self.log_extraction_progress("Power Query extracted", len(power_query))
        return power_query

    def _extract_rls_roles(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract Role-Level Security roles"""
        self.log_extraction_progress("Extracting RLS roles")

        rls_roles = []

        try:
            # Check if model has RLS roles information
            roles_df = getattr(model, "rls_roles", None)
            if roles_df is not None and not roles_df.empty:
                for _, row in roles_df.iterrows():
                    role_name = row.get("RoleName", "Unknown")

                    rls_roles.append(
                        {
                            "name": str(role_name),
                            "description": str(row.get("Description", "not available")),
                            "table_permissions": [],  # Would need deeper extraction
                            "model_permission": str(
                                row.get("ModelPermission", "not available")
                            ),
                            "annotations": {},
                        }
                    )
        except Exception as e:
            self.logger.debug(f"Error extracting RLS roles: {str(e)}")

        self.log_extraction_progress("RLS roles extracted", len(rls_roles))
        return rls_roles

    def _extract_hierarchies(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract hierarchies"""
        self.log_extraction_progress("Extracting hierarchies")

        hierarchies = []

        try:
            # Check if model has hierarchies information
            hier_df = getattr(model, "hierarchies", None)
            if hier_df is not None and not hier_df.empty:
                for _, row in hier_df.iterrows():
                    hierarchy_name = row.get("HierarchyName", "Unknown")
                    table_name = row.get("TableName", "Unknown")

                    hierarchies.append(
                        {
                            "name": str(hierarchy_name),
                            "table": str(table_name),
                            "description": str(row.get("Description", "not available")),
                            "is_hidden": bool(row.get("IsHidden", False)),
                            "display_folder": str(
                                row.get("DisplayFolder", "not available")
                            ),
                            "levels": [],  # Would need deeper extraction
                            "annotations": {},
                        }
                    )
        except Exception as e:
            self.logger.debug(f"Error extracting hierarchies: {str(e)}")

        self.log_extraction_progress("Hierarchies extracted", len(hierarchies))
        return hierarchies

    def _extract_translations(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract translations"""
        self.log_extraction_progress("Extracting translations")

        translations = []

        try:
            # Check if model has translations information
            trans_df = getattr(model, "translations", None)
            if trans_df is not None and not trans_df.empty:
                # Group by language
                languages = trans_df.get("Language", pd.Series()).unique()

                for lang in languages:
                    if pd.isna(lang):
                        continue

                    lang_translations = trans_df[trans_df["Language"] == lang]
                    objects = []

                    for _, row in lang_translations.iterrows():
                        objects.append(
                            {
                                "object_type": str(
                                    row.get("ObjectType", "not available")
                                ),
                                "object_name": str(
                                    row.get("ObjectName", "not available")
                                ),
                                "property": str(row.get("Property", "not available")),
                                "value": str(row.get("Value", "not available")),
                            }
                        )

                    translations.append(
                        {
                            "language": str(lang),
                            "objects": objects,
                        }
                    )
        except Exception as e:
            self.logger.debug(f"Error extracting translations: {str(e)}")

        self.log_extraction_progress("Translations extracted", len(translations))
        return translations

    def _extract_perspectives(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract perspectives"""
        self.log_extraction_progress("Extracting perspectives")

        perspectives = []

        try:
            # Check if model has perspectives information
            persp_df = getattr(model, "perspectives", None)
            if persp_df is not None and not persp_df.empty:
                # Group by perspective name
                perspective_names = persp_df.get(
                    "PerspectiveName", pd.Series()
                ).unique()

                for persp_name in perspective_names:
                    if pd.isna(persp_name):
                        continue

                    persp_objects = persp_df[persp_df["PerspectiveName"] == persp_name]
                    objects = []

                    for _, row in persp_objects.iterrows():
                        objects.append(str(row.get("ObjectName", "not available")))

                    perspectives.append(
                        {
                            "name": str(persp_name),
                            "description": "not available",  # Usually not available in basic extraction
                            "objects": objects,
                            "annotations": {},
                        }
                    )
        except Exception as e:
            self.logger.debug(f"Error extracting perspectives: {str(e)}")

        self.log_extraction_progress("Perspectives extracted", len(perspectives))
        return perspectives

    def _extract_culture_info(self, model: "PBIXRay") -> Dict[str, Any]:
        """Extract culture and formatting information"""
        self.log_extraction_progress("Extracting culture information")

        culture_info = {
            "culture": "not available",
            "date_format": "not available",
            "time_format": "not available",
            "currency_symbol": "not available",
            "thousand_separator": "not available",
            "decimal_separator": "not available",
        }

        try:
            # Try to extract culture information from model
            model_data = getattr(model, "model", None)
            if model_data is not None:
                culture = getattr(model_data, "culture", None)
                if culture:
                    culture_info["culture"] = str(culture)
        except Exception as e:
            self.logger.debug(f"Error extracting culture info: {str(e)}")

        self.log_extraction_progress("Culture information extracted")
        return culture_info

    def _extract_model_annotations(self, model: "PBIXRay") -> Dict[str, Any]:
        """Extract model-level annotations"""
        self.log_extraction_progress("Extracting model annotations")

        annotations = {}

        try:
            # Try to extract annotations from model
            annotations_df = getattr(model, "annotations", None)
            if annotations_df is not None and not annotations_df.empty:
                for _, row in annotations_df.iterrows():
                    name = row.get("Name", "unknown")
                    value = row.get("Value", "")
                    annotations[str(name)] = str(value)
        except Exception as e:
            self.logger.debug(f"Error extracting model annotations: {str(e)}")

        self.log_extraction_progress("Model annotations extracted", len(annotations))
        return annotations

    def _extract_extended_properties(self, model: "PBIXRay") -> Dict[str, Any]:
        """Extract extended properties"""
        self.log_extraction_progress("Extracting extended properties")

        extended_properties = {}

        try:
            # Try to extract extended properties
            ext_props = getattr(model, "extended_properties", None)
            if ext_props is not None and isinstance(ext_props, dict):
                extended_properties = ext_props
        except Exception as e:
            self.logger.debug(f"Error extracting extended properties: {str(e)}")

        self.log_extraction_progress(
            "Extended properties extracted", len(extended_properties)
        )
        return extended_properties

    def _parse_m_code_for_source(self, m_code: str) -> Optional[Dict[str, str]]:
        """Parse M code to extract data source information"""
        if not m_code:
            return None

        # Simple parsing for common patterns
        source_info = {}

        if "Sql.Database" in m_code:
            source_info["type"] = "SQL Server"
        elif "Excel.Workbook" in m_code:
            source_info["type"] = "Excel"
        elif "Web.Contents" in m_code:
            source_info["type"] = "Web"
        elif "Csv.Document" in m_code:
            source_info["type"] = "CSV"
        else:
            source_info["type"] = "Other"

        source_info["connection"] = (
            m_code[:200] + "..." if len(m_code) > 200 else m_code
        )

        return source_info

    def _clean_layout_json(self, json_str: str) -> str:
        """Clean layout JSON by removing control characters"""
        # Remove common control characters found in Power BI layout files
        control_chars = ["\x00", "\x1c", "\x1d", "\x19"]
        for char in control_chars:
            json_str = json_str.replace(char, "")

        return json_str

    def _parse_layout_json(self, layout_data: dict) -> List[Dict[str, Any]]:
        """Parse layout JSON to extract page and visual information"""
        pages = []

        try:
            # Navigate the JSON structure to find pages and visuals
            # This is a simplified parser - actual structure may vary
            if "sections" in layout_data:
                for i, section in enumerate(layout_data["sections"]):
                    page_name = section.get("displayName", f"Page {i+1}")

                    visuals = []
                    if "visualContainers" in section:
                        for visual in section["visualContainers"]:
                            visual_info = self._parse_visual_container(visual)
                            if visual_info:
                                visuals.append(visual_info)

                    pages.append({"page": page_name, "visuals": visuals})
        except Exception as e:
            self.logger.debug(f"Error parsing layout JSON: {str(e)}")

        return pages

    def _parse_visual_container(
        self, visual_container: dict
    ) -> Optional[Dict[str, Any]]:
        """Parse a visual container to extract visual information"""
        try:
            config = visual_container.get("config", {})
            visual_type = config.get("singleVisual", {}).get("visualType", "Unknown")

            # Extract field information (simplified)
            fields = []
            if "projections" in config:
                # Extract field names from projections
                for _key, projection in config["projections"].items():
                    if isinstance(projection, list):
                        for item in projection:
                            if isinstance(item, dict) and "queryRef" in item:
                                fields.append(item["queryRef"])

            return {
                "type": visual_type,
                "title": f"{visual_type} Visual",
                "fields": fields,
            }
        except Exception:
            return None

    def _log_extraction_summary(self, metadata: Dict[str, Any]):
        """Log a summary of extracted metadata"""
        summary = [
            f"Tables: {len(metadata.get('tables', []))}",
            f"Measures: {len(metadata.get('measures', []))}",
            f"Calculated Columns: {len(metadata.get('calculated_columns', []))}",
            f"Relationships: {len(metadata.get('relationships', []))}",
            f"Pages: {len(metadata.get('visualizations', []))}",
        ]

        self.logger.info(f"Extraction complete - {', '.join(summary)}")
