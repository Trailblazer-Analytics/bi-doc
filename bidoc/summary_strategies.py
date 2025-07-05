"""AI Summary Strategies"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AISummaryStrategy(ABC):
    """Base class for AI summary generation strategies."""

    @abstractmethod
    def generate_summary(self, metadata: Dict[str, Any]) -> str:
        """Generate a summary from metadata."""
        pass


class PowerBISummaryStrategy(AISummaryStrategy):
    """Summary strategy for Power BI files."""

    def generate_summary(self, metadata: Dict[str, Any]) -> str:
        file_name = metadata.get("file_name") or metadata.get("file", "Unknown")
        tables = metadata.get("tables", [])
        measures = metadata.get("measures", [])
        relationships = metadata.get("relationships", [])
        visualizations = metadata.get("visualizations", [])

        summary_parts = [f"**{file_name}** is a Power BI report containing:"]

        if tables:
            total_columns = sum(len(table.get("columns", [])) for table in tables)
            summary_parts.append(
                f"- **{len(tables)} data tables** with {total_columns} total columns"
            )

        if measures:
            summary_parts.append(
                f"- **{len(measures)} DAX measures** for calculations and KPIs"
            )

        if relationships:
            summary_parts.append(
                f"- **{len(relationships)} table relationships** defining the data model"
            )

        if visualizations:
            total_visuals = sum(len(page.get("visuals", [])) for page in visualizations)
            summary_parts.append(
                f"- **{len(visualizations)} report pages** with {total_visuals} total visualizations"
            )

        return "\n".join(summary_parts)


class TableauSummaryStrategy(AISummaryStrategy):
    """Summary strategy for Tableau files."""

    def generate_summary(self, metadata: Dict[str, Any]) -> str:
        file_name = metadata.get("file_name") or metadata.get("file", "Unknown")
        datasources = metadata.get("data_sources", [])  # Use data_sources instead of datasources
        worksheets = metadata.get("worksheets", [])
        dashboards = metadata.get("dashboards", [])

        summary_parts = [f"**{file_name}** is a Tableau workbook containing:"]

        if datasources:
            summary_parts.append(f"- **{len(datasources)} data sources**")

        if worksheets:
            summary_parts.append(f"- **{len(worksheets)} worksheets**")

        if dashboards:
            summary_parts.append(f"- **{len(dashboards)} dashboards**")

        return "\n".join(summary_parts)


class DefaultSummaryStrategy(AISummaryStrategy):
    """Default summary strategy for unknown file types."""

    def generate_summary(self, metadata: Dict[str, Any]) -> str:
        file_type = metadata.get("type", "Unknown")
        return f"This is a {file_type} file containing business intelligence assets."
