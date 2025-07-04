"""Tableau (.twb/.twbx) file parser using Tableau Document API"""

import logging
import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from tableaudocumentapi import Workbook
else:
    try:
        from tableaudocumentapi import Workbook
    except ImportError:
        Workbook = None

from bidoc.utils import MetadataExtractor


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

        try:
            # Handle .twbx files (extract .twb from zip)
            if file_path.suffix.lower() == ".twbx":
                workbook_path = self._extract_twb_from_twbx(file_path)
            else:
                workbook_path = str(file_path)

            # Load workbook
            workbook = Workbook(workbook_path)

            # Extract core metadata
            metadata = {
                "file": file_path.name,
                "type": "Tableau",
                "file_path": str(file_path),
                "data_sources": self._extract_data_sources(workbook),
                "worksheets": self._extract_worksheets(workbook),
                "dashboards": self._extract_dashboards(workbook),
                "parameters": self._extract_parameters(workbook),
                "calculated_fields": self._extract_calculated_fields(workbook),
                "field_usage": self._extract_field_usage(workbook),
            }

            self._log_extraction_summary(metadata)
            return metadata

        except Exception as e:
            self.logger.error(f"Failed to parse Tableau file: {str(e)}")
            raise

    def _extract_twb_from_twbx(self, twbx_path: Path) -> str:
        """Extract .twb file from .twbx archive"""
        self.log_extraction_progress("Extracting .twb from .twbx archive")

        temp_dir = tempfile.mkdtemp()

        with zipfile.ZipFile(twbx_path, "r") as zip_file:
            # Find the .twb file in the archive
            twb_files = [f for f in zip_file.namelist() if f.endswith(".twb")]

            if not twb_files:
                raise ValueError("No .twb file found in .twbx archive")

            # Extract the first .twb file
            twb_file = twb_files[0]
            zip_file.extract(twb_file, temp_dir)

            return str(Path(temp_dir) / twb_file)

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
                        "is_calculated": hasattr(field, "calculation")
                        and field.calculation is not None,
                        "calculation": getattr(field, "calculation", None),
                        "description": getattr(field, "description", ""),
                        "worksheets": getattr(field, "worksheets", []),
                    }
                    fields.append(field_info)

                data_sources.append(
                    {
                        "name": datasource.name,
                        "caption": getattr(datasource, "caption", datasource.name),
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
                            "datasource": datasource.name,
                            "calculation": field.calculation,
                            "datatype": getattr(field, "datatype", "unknown"),
                            "role": getattr(field, "role", "unknown"),
                            "description": getattr(field, "description", ""),
                            "worksheets_used": getattr(field, "worksheets", []),
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
