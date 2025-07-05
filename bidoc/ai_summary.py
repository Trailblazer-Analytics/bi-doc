"""AI Summary module - Future integration hook for AI-powered insights"""

import logging
from typing import Any, Dict, Union

from bidoc.config import AppConfig
from bidoc.summary_strategies import (
    AISummaryStrategy,
    DefaultSummaryStrategy,
    PowerBISummaryStrategy,
    TableauSummaryStrategy,
)
from bidoc.utils import FileType


class AISummary:
    """AI Summary generator - placeholder for future BYO AI integration"""

    def __init__(self, strategy: AISummaryStrategy, config: AppConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.strategy = strategy

    def generate_summary(self, metadata: Dict[str, Any]) -> str:
        """
        Generate AI-powered summary of BI metadata
        """

        self.logger.debug("Generating AI summary")

        if self._is_ai_configured():
            # Future: Implement actual AI integration
            # return self._call_ai_service(metadata)
            pass

        return self.strategy.generate_summary(metadata)

    def _is_ai_configured(self) -> bool:
        """Check if AI service is properly configured"""
        return bool(self.config.ai.endpoint and self.config.ai.api_key)


def get_summary_strategy(file_type: Union[str, FileType]) -> AISummaryStrategy:
    """Get the appropriate summary strategy for the file type."""
    # Handle both FileType enum and string inputs
    if isinstance(file_type, str):
        if file_type == "Power BI":
            return PowerBISummaryStrategy()
        elif file_type == "Tableau":
            return TableauSummaryStrategy()
        else:
            return DefaultSummaryStrategy()

    # Handle FileType enum
    if file_type == FileType.POWER_BI:
        return PowerBISummaryStrategy()
    elif file_type in [FileType.TABLEAU_TWB, FileType.TABLEAU_TWBX]:
        return TableauSummaryStrategy()
    else:
        return DefaultSummaryStrategy()
