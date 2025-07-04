"""Power BI (.pbix) file parser using PBIXRay"""

import logging
import zipfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pbixray import PBIXRay
else:
    try:
        from pbixray import PBIXRay
    except ImportError:
        PBIXRay = None

from bidoc.utils import MetadataExtractor


class PowerBIParser(MetadataExtractor):
    """Parser for Power BI .pbix files"""
    
    def __init__(self):
        super().__init__()
        if PBIXRay is None:
            raise ImportError("PBIXRay library is required. Install with: pip install pbixray")
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a Power BI .pbix file and extract metadata"""
        self.logger.info(f"Parsing Power BI file: {file_path.name}")
        
        try:
            # Initialize PBIXRay
            model = PBIXRay(str(file_path))
            
            # Extract core metadata
            metadata = {
                'file': file_path.name,
                'type': 'Power BI',
                'file_path': str(file_path),
                'data_sources': self._extract_data_sources(model),
                'tables': self._extract_tables(model),
                'relationships': self._extract_relationships(model),
                'measures': self._extract_measures(model),
                'calculated_columns': self._extract_calculated_columns(model),
                'visualizations': self._extract_visualizations(file_path),
                'power_query': self._extract_power_query(model)
            }
            
            self._log_extraction_summary(metadata)
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to parse Power BI file: {str(e)}")
            raise
    
    def _extract_data_sources(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract data source information"""
        self.log_extraction_progress("Extracting data sources")
        
        data_sources = []
        
        try:
            # Get Power Query information if available
            if hasattr(model, 'power_query') and model.power_query is not None:
                for query_name, query_content in model.power_query.items():
                    # Extract connection info from M code
                    source_info = self._parse_m_code_for_source(query_content)
                    if source_info:
                        data_sources.append({
                            'name': query_name,
                            'type': source_info.get('type', 'Unknown'),
                            'connection': source_info.get('connection', ''),
                            'query': query_content
                        })
        except Exception as e:
            self.logger.debug(f"Could not extract Power Query sources: {str(e)}")
        
        # If no Power Query sources found, create a generic entry
        if not data_sources:
            data_sources.append({
                'name': 'Data Model',
                'type': 'Imported Data',
                'connection': 'Data imported into model',
                'query': ''
            })
        
        self.log_extraction_progress("Data sources extracted", len(data_sources))
        return data_sources
    
    def _extract_tables(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract table and column information"""
        self.log_extraction_progress("Extracting tables and columns")
        
        tables = []
        
        try:
            # Get table names
            table_names = model.tables if hasattr(model, 'tables') else []
            
            # Get schema information
            schema_df = model.schema if hasattr(model, 'schema') else None
            
            if schema_df is not None and not schema_df.empty:
                # Group by table
                for table_name in table_names:
                    table_columns = schema_df[schema_df['Table'] == table_name]
                    
                    columns = []
                    for _, row in table_columns.iterrows():
                        columns.append({
                            'name': row.get('Column', ''),
                            'data_type': row.get('DataType', 'Unknown'),
                            'is_hidden': row.get('IsHidden', False),
                            'description': row.get('Description', '')
                        })
                    
                    tables.append({
                        'name': table_name,
                        'columns': columns,
                        'row_count': None  # PBIXRay might provide this in future versions
                    })
        except Exception as e:
            self.logger.debug(f"Error extracting tables: {str(e)}")
        
        self.log_extraction_progress("Tables extracted", len(tables))
        return tables
    
    def _extract_relationships(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract table relationships"""
        self.log_extraction_progress("Extracting relationships")
        
        relationships = []
        
        try:
            if hasattr(model, 'relationships'):
                rel_df = model.relationships
                
                if rel_df is not None and not rel_df.empty:
                    for _, row in rel_df.iterrows():
                        relationships.append({
                            'from_table': row.get('FromTable', ''),
                            'from_column': row.get('FromColumn', ''),
                            'to_table': row.get('ToTable', ''),
                            'to_column': row.get('ToColumn', ''),
                            'cardinality': row.get('Cardinality', ''),
                            'is_active': row.get('IsActive', True),
                            'cross_filter_direction': row.get('CrossFilterDirection', '')
                        })
        except Exception as e:
            self.logger.debug(f"Error extracting relationships: {str(e)}")
        
        self.log_extraction_progress("Relationships extracted", len(relationships))
        return relationships
    
    def _extract_measures(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract DAX measures"""
        self.log_extraction_progress("Extracting DAX measures")
        
        measures = []
        
        try:
            if hasattr(model, 'dax_measures'):
                measures_df = model.dax_measures
                
                if measures_df is not None and not measures_df.empty:
                    for _, row in measures_df.iterrows():
                        measures.append({
                            'name': row.get('Measure', ''),
                            'table': row.get('Table', ''),
                            'expression': row.get('Expression', ''),
                            'format_string': row.get('FormatString', ''),
                            'description': row.get('Description', ''),
                            'is_hidden': row.get('IsHidden', False)
                        })
        except Exception as e:
            self.logger.debug(f"Error extracting measures: {str(e)}")
        
        self.log_extraction_progress("Measures extracted", len(measures))
        return measures
    
    def _extract_calculated_columns(self, model: "PBIXRay") -> List[Dict[str, Any]]:
        """Extract calculated columns"""
        self.log_extraction_progress("Extracting calculated columns")
        
        calculated_columns = []
        
        try:
            if hasattr(model, 'dax_columns'):
                columns_df = model.dax_columns
                
                if columns_df is not None and not columns_df.empty:
                    for _, row in columns_df.iterrows():
                        calculated_columns.append({
                            'name': row.get('Column', ''),
                            'table': row.get('Table', ''),
                            'expression': row.get('Expression', ''),
                            'data_type': row.get('DataType', ''),
                            'description': row.get('Description', ''),
                            'is_hidden': row.get('IsHidden', False)
                        })
        except Exception as e:
            self.logger.debug(f"Error extracting calculated columns: {str(e)}")
        
        self.log_extraction_progress("Calculated columns extracted", len(calculated_columns))
        return calculated_columns
    
    def _extract_visualizations(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract report layout and visualization information"""
        self.log_extraction_progress("Extracting visualizations")
        
        visualizations = []
        
        try:
            # Extract layout JSON from .pbix file
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Look for Report/Layout file
                layout_files = [f for f in zip_file.namelist() if 'Report/Layout' in f]
                
                for layout_file in layout_files:
                    layout_content = zip_file.read(layout_file)
                    
                    # Decode and clean the JSON (handle UTF-16 and control characters)
                    try:
                        # Try UTF-8 first
                        layout_str = layout_content.decode('utf-8')
                    except UnicodeDecodeError:
                        # Fall back to UTF-16
                        layout_str = layout_content.decode('utf-16le')
                    
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
            visualizations = [{
                'page': 'Report Pages',
                'visuals': [{
                    'type': 'Unknown',
                    'title': 'Visualizations present (detailed extraction failed)',
                    'fields': []
                }]
            }]
        
        self.log_extraction_progress("Visualizations extracted", len(visualizations))
        return visualizations
    
    def _extract_power_query(self, model: "PBIXRay") -> Dict[str, str]:
        """Extract Power Query M code"""
        self.log_extraction_progress("Extracting Power Query code")
        
        power_query = {}
        
        try:
            if hasattr(model, 'power_query') and model.power_query:
                power_query = dict(model.power_query)
        except Exception as e:
            self.logger.debug(f"Error extracting Power Query: {str(e)}")
        
        self.log_extraction_progress("Power Query extracted", len(power_query))
        return power_query
    
    def _parse_m_code_for_source(self, m_code: str) -> Optional[Dict[str, str]]:
        """Parse M code to extract data source information"""
        if not m_code:
            return None
        
        # Simple parsing for common patterns
        source_info = {}
        
        if 'Sql.Database' in m_code:
            source_info['type'] = 'SQL Server'
        elif 'Excel.Workbook' in m_code:
            source_info['type'] = 'Excel'
        elif 'Web.Contents' in m_code:
            source_info['type'] = 'Web'
        elif 'Csv.Document' in m_code:
            source_info['type'] = 'CSV'
        else:
            source_info['type'] = 'Other'
        
        source_info['connection'] = m_code[:200] + "..." if len(m_code) > 200 else m_code
        
        return source_info
    
    def _clean_layout_json(self, json_str: str) -> str:
        """Clean layout JSON by removing control characters"""
        # Remove common control characters found in Power BI layout files
        control_chars = ['\x00', '\x1c', '\x1d', '\x19']
        for char in control_chars:
            json_str = json_str.replace(char, '')
        
        return json_str
    
    def _parse_layout_json(self, layout_data: dict) -> List[Dict[str, Any]]:
        """Parse layout JSON to extract page and visual information"""
        pages = []
        
        try:
            # Navigate the JSON structure to find pages and visuals
            # This is a simplified parser - actual structure may vary
            if 'sections' in layout_data:
                for i, section in enumerate(layout_data['sections']):
                    page_name = section.get('displayName', f'Page {i+1}')
                    
                    visuals = []
                    if 'visualContainers' in section:
                        for visual in section['visualContainers']:
                            visual_info = self._parse_visual_container(visual)
                            if visual_info:
                                visuals.append(visual_info)
                    
                    pages.append({
                        'page': page_name,
                        'visuals': visuals
                    })
        except Exception as e:
            self.logger.debug(f"Error parsing layout JSON: {str(e)}")
        
        return pages
    
    def _parse_visual_container(self, visual_container: dict) -> Optional[Dict[str, Any]]:
        """Parse a visual container to extract visual information"""
        try:
            config = visual_container.get('config', {})
            visual_type = config.get('singleVisual', {}).get('visualType', 'Unknown')
            
            # Extract field information (simplified)
            fields = []
            if 'projections' in config:
                # Extract field names from projections
                for key, projection in config['projections'].items():
                    if isinstance(projection, list):
                        for item in projection:
                            if isinstance(item, dict) and 'queryRef' in item:
                                fields.append(item['queryRef'])
            
            return {
                'type': visual_type,
                'title': f"{visual_type} Visual",
                'fields': fields
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
            f"Pages: {len(metadata.get('visualizations', []))}"
        ]
        
        self.logger.info(f"Extraction complete - {', '.join(summary)}")
