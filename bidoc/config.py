"""Configuration management for the bidoc application."""

import os
from dataclasses import dataclass, field
from typing import Optional

import toml


@dataclass
class AIConfig:
    """Configuration for AI-powered summaries."""

    endpoint: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration."""

    ai: AIConfig = field(default_factory=AIConfig)


def load_config(path: str = "config.toml") -> AppConfig:
    """Load configuration from a TOML file."""
    if os.path.exists(path):
        config_data = toml.load(path)
        ai_config_data = config_data.get("ai", {})
        ai_config = AIConfig(
            endpoint=ai_config_data.get("endpoint"),
            model=ai_config_data.get("model", "gpt-3.5-turbo"),
            api_key=ai_config_data.get("api_key"),
        )
        return AppConfig(ai=ai_config)
    return AppConfig()
