# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Centralized configuration management with TOML support
- Strategy pattern for AI summary generation
- Comprehensive logging system with file output option
- Enhanced test suite with error handling and configuration tests
- GitHub Actions release automation workflow
- Support for `--log-file` option in CLI
- Support for `--config` option to specify custom configuration file

### Changed

- Refactored AI summary module to use extensible strategy pattern
- Improved error handling throughout the application
- Enhanced type hint coverage across the codebase
- Standardized logging across all modules
- Updated CLI to use `click.echo()` for better test compatibility

### Fixed

- Fixed AI summary strategy selection for different file types
- Fixed test suite to handle new architecture changes
- Fixed PowerBI parser test data source validation
- Fixed logging configuration for test environments
- Fixed dataclass mutable default error in configuration

### Removed

- Removed unreliable subprocess-based tests
- Removed old logging implementation from utils module

## [1.0.0] - 2025-01-XX

### Initial Release

- Initial release with Power BI and Tableau file parsing
- Markdown and JSON output generation
- Basic AI summary placeholder functionality
- Command-line interface
- Docker support
- GitHub Actions CI/CD pipeline

### Core Features

- Parse .pbix, .twb, and .twbx files
- Extract metadata including tables, measures, relationships, and visualizations
- Generate comprehensive documentation in multiple formats
- Cross-platform support (Windows, macOS, Linux)
