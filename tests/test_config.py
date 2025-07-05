"""Tests for configuration management"""

import os

from bidoc.config import AIConfig, AppConfig, load_config


def test_default_config():
    """Test loading default configuration when no file exists."""
    config = load_config("nonexistent_config.toml")
    assert isinstance(config, AppConfig)
    assert isinstance(config.ai, AIConfig)
    assert config.ai.model == "gpt-3.5-turbo"
    assert config.ai.endpoint is None
    assert config.ai.api_key is None


def test_config_from_file():
    """Test loading configuration from a TOML file."""
    config_content = """
[ai]
endpoint = "https://api.openai.com/v1"
model = "gpt-4"
api_key = "test-key"
"""

    # Create a temporary file in the current directory
    temp_path = "test_config.toml"
    try:
        with open(temp_path, "w") as f:
            f.write(config_content)

        config = load_config(temp_path)
        assert config.ai.endpoint == "https://api.openai.com/v1"
        assert config.ai.model == "gpt-4"
        assert config.ai.api_key == "test-key"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_partial_config():
    """Test loading partial configuration (only some fields specified)."""
    config_content = """
[ai]
endpoint = "https://custom.ai.endpoint"
"""

    # Create a temporary file in the current directory
    temp_path = "test_partial_config.toml"
    try:
        with open(temp_path, "w") as f:
            f.write(config_content)

        config = load_config(temp_path)
        assert config.ai.endpoint == "https://custom.ai.endpoint"
        assert config.ai.model == "gpt-3.5-turbo"  # Default value
        assert config.ai.api_key is None
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
