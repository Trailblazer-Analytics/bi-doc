"""Tableau (.twb/.twbx) file parser using Tableau Document API"""

import logging
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from tableaudocumentapi import Workbook
else:
    try:
        from tableaudocumentapi import Workbook
    except ImportError:
        Workbook = None

from bidoc.metadata_schemas import ensure_complete_metadata
from bidoc.utils import MetadataExtractor
from bidoc.metadata_schemas import ensure_complete_metadata, get_default_tableau_metadata


class TableauParser(MetadataExtractor):
    """Parser for Tableau .twb and .twbx files"""

    def __init__(self):
        super().__init__()
        if Workbook is None:
            raise ImportError(
                "tableau-document-api library is required. Install with: pip install tableau-document-api"
            )

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a Tableau workbook file and extract metadata"""
        self.logger.info(f"Parsing Tableau file: {file_path.name}")

        # Get basic file information
        file_stats = file_path.stat() if file_path.exists() else None
        
        # Initialize with comprehensive metadata structure
        metadata = {
            "file": file_path.name,
            "type": "Tableau",
            "file_path": str(file_path),
            "file_size": file_stats.st_size if file_stats else None,
            "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat() if file_stats else "not available",
            "created_date": datetime.fromtimestamp(file_stats.st_ctime).isoformat() if file_stats else "not available",
        }

        try:
            # Handle .twbx and .tdsx files (extract .twb or .tds from zip)
            if file_path.suffix.lower() in [".twbx", ".tdsx"]:
                workbook_path = self._extract_workbook_from_archive(file_path)
            else:
                workbook_path = str(file_path)

            # Load workbook
            workbook = Workbook(workbook_path)

            # Extract all metadata sections
            metadata.update({
                "workbook_info": self._extract_workbook_info(workbook, file_path),
                "data_sources": self._extract_data_sources(workbook),
                "worksheets": self._extract_worksheets(workbook),
                "dashboards": self._extract_dashboards(workbook),
                "parameters": self._extract_parameters(workbook),
                "calculated_fields": self._extract_calculated_fields(workbook),
                "stories": self._extract_stories(workbook),
                "field_usage": self._extract_field_usage(workbook),
                "metadata_records": self._extract_metadata_records(workbook),
                "groups": self._extract_groups(workbook),
                "sets": self._extract_sets(workbook),
                "formatting": self._extract_formatting(workbook),
            })

            # Ensure all possible fields are present
            metadata = ensure_complete_metadata(metadata, "Tableau")

            self._log_extraction_summary(metadata)
            return metadata

        except Exception as e:
            self.logger.error(f"Failed to parse Tableau file: {str(e)}")
            # Return comprehensive structure even if parsing fails
            metadata = ensure_complete_metadata(metadata, "Tableau")
            return metadata

    def _extract_workbook_from_archive(self, archive_path: Path) -> str:
        """Extract .twb or .tds file from .twbx or .tdsx archive"""
        self.log_extraction_progress(f"Extracting from {archive_path.suffix} archive")

        if not archive_path.exists():
            raise FileNotFoundError(f"Archive file not found at: {archive_path}")

        temp_dir = tempfile.mkdtemp()

        file_extension_to_find = ".twb" if archive_path.suffix.lower() == ".twbx" else ".tds"

        with open(archive_path, "rb") as archive_file:
            with zipfile.ZipFile(archive_file, "r") as zip_file:
                # Find the file in the archive
                files = [f for f in zip_file.namelist() if f.endswith(file_extension_to_find)]

                if not files:
                    raise ValueError(f"No {file_extension_to_find} file found in {archive_path.suffix} archive")

                # Extract the first file found
                file_to_extract = files[0]
                zip_file.extract(file_to_extract, temp_dir)

                return str(Path(temp_dir) / file_to_extract)

    def _extract_data_sources(self, workbook) -> List[Dict[str, Any]]:
        """Extract data source information"""
        self.log_extraction_progress("Extracting data sources")

        data_sources = []

        try:
            for datasource in workbook.datasources:
                # Get connection information
                connections = []
                for connection in datasource.connections:
                    conn_info = {
                        "server": getattr(connection, "server", ""),
                        "database": getattr(connection, "dbname", ""),
                        "connection_type": getattr(connection, "dbclass", ""),
                        "username": getattr(connection, "username", ""),
                        "port": getattr(connection, "port", ""),
                    }
                    connections.append(conn_info)

                # Get fields
                fields = []
                for field in datasource.fields.values():
                    field_info = {
                        "name": field.name,
                        "caption": getattr(field, "caption", field.name),
                        "datatype": getattr(field, "datatype", "unknown"),
                        "role": getattr(field, "role", "unknown"),
                        "type": getattr(field, "type", "unknown"),
                        "is_calculated": hasattr(field, "calculation") and field.calculation is not None,
                        "calculation": getattr(field, "calculation", "not available"),
                        "calculation_formatted": self._format_tableau_calculation(getattr(field, "calculation", "")),
                        "description": getattr(field, "description", "not available"),
                        "worksheets": getattr(field, "worksheets", []),
                        "default_aggregation": getattr(field, "default_aggregation", "not available"),
                        "is_hidden": getattr(field, "is_hidden", False),
                        "aliases": {},
                        "folder": getattr(field, "folder", "not available"),
                        "geo_role": getattr(field, "geo_role", "not available"),
                        "semantic_role": getattr(field, "semantic_role", "not available"),
                    }
                    fields.append(field_info)

                ds_type = "unknown"
                if connections:
                    ds_type = connections[0].get("connection_type", "unknown")

                data_sources.append(
                    {
                        "name": datasource.name,
                        "caption": getattr(datasource, "caption", datasource.name),
                        "type": ds_type,
                        "connections": connections,
                        "fields": fields,
                    }
                )

        except Exception as e:
            self.logger.debug(f"Error extracting data sources: {str(e)}")

        self.log_extraction_progress("Data sources extracted", len(data_sources))
        return data_sources

    def _extract_worksheets(self, workbook) -> List[Dict[str, Any]]:
        """Extract worksheet information"""
        self.log_extraction_progress("Extracting worksheets")

        worksheets = []

        try:
            # workbook.worksheets returns a list of worksheet names (strings)
            for worksheet_name in workbook.worksheets:
                worksheet_info = {
                    "name": worksheet_name,
                    "data_source": "",  # Not available in basic API
                    "fields_used": [],  # Would need more complex parsing
                    "filters": [],     # Would need more complex parsing
                    "parameters_used": [],  # Would need more complex parsing
                }
                worksheets.append(worksheet_info)

        except Exception as e:
            self.logger.debug(f"Error extracting worksheets: {str(e)}")

        self.log_extraction_progress("Worksheets extracted", len(worksheets))
        return worksheets

    def _extract_dashboards(self, workbook) -> List[Dict[str, Any]]:
        """Extract dashboard information"""
        self.log_extraction_progress("Extracting dashboards")

        dashboards = []

        try:
            # workbook.dashboards returns a list of dashboard names (strings)
            for dashboard_name in workbook.dashboards:
                dashboard_info = {
                    "name": dashboard_name,
                    "worksheets": [],  # Would need more complex parsing to get worksheet relationships
                    "objects": [],     # Would need more complex parsing
                }
                dashboards.append(dashboard_info)

        except Exception as e:
            self.logger.debug(f"Error extracting dashboards: {str(e)}")

        self.log_extraction_progress("Dashboards extracted", len(dashboards))
        return dashboards

    def _extract_parameters(self, workbook) -> List[Dict[str, Any]]:
        """Extract parameter information"""
        self.log_extraction_progress("Extracting parameters")

        parameters = []

        try:
            # Parameters are typically in datasources
            for datasource in workbook.datasources:
                for field in datasource.fields.values():
                    if getattr(field, "parameter", False):
                        param_info = {
                            "name": field.name,
                            "datatype": getattr(field, "datatype", "unknown"),
                            "default_value": getattr(field, "default_value", None),
                            "allowable_values": getattr(field, "allowable_values", []),
                            "description": getattr(field, "description", ""),
                        }
                        parameters.append(param_info)

        except Exception as e:
            self.logger.debug(f"Error extracting parameters: {str(e)}")

        self.log_extraction_progress("Parameters extracted", len(parameters))
        return parameters

    def _extract_calculated_fields(self, workbook) -> List[Dict[str, Any]]:
        """Extract calculated field information"""
        self.log_extraction_progress("Extracting calculated fields")

        calculated_fields = []

        try:
            for datasource in workbook.datasources:
                for field in datasource.fields.values():
                    if hasattr(field, "calculation") and field.calculation:
                        calc_field = {
                            "name": field.name,
                            "caption": getattr(field, "caption", field.name),
                            "datasource": datasource.name,
                            "calculation": field.calculation,
                            "calculation_formatted": self._format_tableau_calculation(field.calculation),
                            "datatype": getattr(field, "datatype", "unknown"),
                            "role": getattr(field, "role", "unknown"),
                            "description": getattr(field, "description", "not available"),
                            "worksheets_used": getattr(field, "worksheets", []),
                            "folder": getattr(field, "folder", "not available"),
                            "is_hidden": getattr(field, "is_hidden", False),
                            "dependencies": [],  # Would need deeper analysis
                            "comment": getattr(field, "comment", "not available"),
                        }
                        calculated_fields.append(calc_field)

        except Exception as e:
            self.logger.debug(f"Error extracting calculated fields: {str(e)}")

        self.log_extraction_progress(
            "Calculated fields extracted", len(calculated_fields)
        )
        return calculated_fields

    def _extract_field_usage(self, workbook) -> Dict[str, List[str]]:
        """Extract which fields are used in which worksheets"""
        self.log_extraction_progress("Extracting field usage")

        field_usage = {}

        try:
            for datasource in workbook.datasources:
                for field in datasource.fields.values():
                    worksheets = getattr(field, "worksheets", [])
                    if worksheets:
                        field_usage[field.name] = worksheets

        except Exception as e:
            self.logger.debug(f"Error extracting field usage: {str(e)}")

        self.log_extraction_progress("Field usage extracted", len(field_usage))
        return field_usage

    def _get_worksheet_fields(self, worksheet) -> List[str]:
        """Get fields used in a worksheet"""
        fields = []
        try:
            # This would require deeper XML parsing or additional API methods
            # For now, return placeholder
            fields = ["Fields extraction requires deeper XML parsing"]
        except Exception:
            pass
        return fields

    def _get_worksheet_filters(self, worksheet) -> List[Dict[str, Any]]:
        """Get filters applied to a worksheet"""
        filters = []
        try:
            # This would require XML parsing of the worksheet structure
            # For now, return placeholder
            pass
        except Exception:
            pass
        return filters

    def _get_worksheet_parameters(self, worksheet) -> List[str]:
        """Get parameters used in a worksheet"""
        parameters = []
        try:
            # This would require XML parsing
            # For now, return placeholder
            pass
        except Exception:
            pass
        return parameters

    def _get_dashboard_objects(self, dashboard) -> List[Dict[str, Any]]:
        """Get objects in a dashboard"""
        objects = []
        try:
            # This would require XML parsing of dashboard structure
            # For now, return basic info
            if hasattr(dashboard, "worksheets"):
                for worksheet in dashboard.worksheets:
                    objects.append({"type": "worksheet", "name": worksheet.name})
        except Exception:
            pass
        return objects

    def _log_extraction_summary(self, metadata: Dict[str, Any]):
        """Log a summary of extracted metadata"""
        summary = [
            f"Data Sources: {len(metadata.get('data_sources', []))}",
            f"Worksheets: {len(metadata.get('worksheets', []))}",
            f"Dashboards: {len(metadata.get('dashboards', []))}",
            f"Calculated Fields: {len(metadata.get('calculated_fields', []))}",
            f"Parameters: {len(metadata.get('parameters', []))}",
        ]

        self.logger.info(f"Extraction complete - {', '.join(summary)}")

    def _extract_workbook_info(self, workbook, file_path: Path) -> Dict[str, Any]:
        """Extract workbook-level information"""
        self.log_extraction_progress("Extracting workbook information")
        
        workbook_info = {
            "name": file_path.stem,
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
        }
        
        try:
            # Try to extract workbook-level information
            if hasattr(workbook, 'version'):
                workbook_info["version"] = str(getattr(workbook, 'version', 'not available'))
            if hasattr(workbook, 'show_tabs'):
                workbook_info["show_tabs"] = bool(getattr(workbook, 'show_tabs', True))
        except Exception as e:
            self.logger.debug(f"Error extracting workbook info: {str(e)}")
        
        self.log_extraction_progress("Workbook information extracted")
        return workbook_info

    def _extract_stories(self, workbook) -> List[Dict[str, Any]]:
        """Extract stories (Tableau presentations)"""
        self.log_extraction_progress("Extracting stories")
        
        stories = []
        
        try:
            # Check if workbook has stories
            if hasattr(workbook, 'stories'):
                story_names = getattr(workbook, 'stories', [])
                for story_name in story_names:
                    stories.append({
                        "name": str(story_name),
                        "caption": str(story_name),
                        "description": "not available",
                        "story_points": [],
                        "sizing": {},
                        "formatting": {},
                    })
        except Exception as e:
            self.logger.debug(f"Error extracting stories: {str(e)}")
        
        self.log_extraction_progress("Stories extracted", len(stories))
        return stories

    def _extract_metadata_records(self, workbook) -> List[Dict[str, Any]]:
        """Extract metadata records"""
        self.log_extraction_progress("Extracting metadata records")
        
        metadata_records = []
        
        try:
            # Try to extract metadata records if available
            # This would typically require XML parsing for detailed metadata
            pass
        except Exception as e:
            self.logger.debug(f"Error extracting metadata records: {str(e)}")
        
        self.log_extraction_progress("Metadata records extracted", len(metadata_records))
        return metadata_records

    def _extract_groups(self, workbook) -> List[Dict[str, Any]]:
        """Extract groups"""
        self.log_extraction_progress("Extracting groups")
        
        groups = []
        
        try:
            # Groups are typically defined within data sources
            for datasource in workbook.datasources:
                # Check if data source has groups information
                # This would require deeper XML parsing
                pass
        except Exception as e:
            self.logger.debug(f"Error extracting groups: {str(e)}")
        
        self.log_extraction_progress("Groups extracted", len(groups))
        return groups

    def _extract_sets(self, workbook) -> List[Dict[str, Any]]:
        """Extract sets"""
        self.log_extraction_progress("Extracting sets")
        
        sets = []
        
        try:
            # Sets are typically defined within data sources
            for datasource in workbook.datasources:
                # Check if data source has sets information
                # This would require deeper XML parsing
                pass
        except Exception as e:
            self.logger.debug(f"Error extracting sets: {str(e)}")
        
        self.log_extraction_progress("Sets extracted", len(sets))
        return sets

    def _extract_formatting(self, workbook) -> Dict[str, Any]:
        """Extract formatting information"""
        self.log_extraction_progress("Extracting formatting")
        
        formatting = {
            "workbook_formatting": {},
            "default_formatting": {},
            "color_palettes": [],
            "fonts": {},
        }
        
        try:
            # Try to extract formatting information
            # This would typically require XML parsing for detailed formatting
            pass
        except Exception as e:
            self.logger.debug(f"Error extracting formatting: {str(e)}")
        
        self.log_extraction_progress("Formatting extracted")
        return formatting

    def _format_tableau_calculation(self, calculation: str) -> str:
        """Format Tableau calculation for better readability"""
        if not calculation or calculation == "not available":
            return "not available"
        
        try:
            # Basic formatting for Tableau calculations
            # Remove excessive whitespace
            formatted = " ".join(calculation.split())
            
            # Add line breaks for long calculations
            if len(formatted) > 80:
                # Break at logical points like operators
                formatted = formatted.replace(" AND ", "\nAND ")
                formatted = formatted.replace(" OR ", "\nOR ")
                formatted = formatted.replace(", ", ",\n    ")
            
            return formatted
        except Exception:
            return str(calculation)
