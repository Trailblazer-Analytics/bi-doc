# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-08-03

### Security
- **CRITICAL**: Fixed ZIP file path traversal vulnerabilities in Tableau parser
- Added input validation and length limits for DAX expressions  
- Implemented timeout protection for regex operations to prevent ReDoS attacks
- Added safe extraction method for ZIP file operations

### Added
- Comprehensive security testing and validation framework
- Production-ready PyPI package with complete build infrastructure
- PowerShell Gallery publishing capabilities for enterprise integration
- Complete dependency management with install_dependencies.sh
- Professional build system with virtual environment isolation
- Demonstration script showcasing all tool capabilities
- Enhanced JSON generation with comprehensive metadata capture
- Performance monitoring and optimization infrastructure
- Caching system for improved processing speed

### Changed
- **BREAKING**: DAX formatter now enforces input length limits (default: 10,000 characters)
- Standardized dependency versions across all configuration files
- Improved CI/CD reliability across macOS, Windows, and Linux platforms
- Enhanced error handling and logging throughout the application
- Optimized memory usage for large file processing
- Updated documentation with security best practices

### Fixed
- Resolved CI/CD pipeline failures on macOS with proper system dependencies
- Fixed dependency management inconsistencies between setup.py and pyproject.toml
- Improved error handling for malformed BI files
- Enhanced test coverage for security and edge cases

### Development
- Added comprehensive code review guidelines and security checklist
- Enhanced test suite with 48 passing tests and improved coverage
- Added security scanning tools (safety, pip-audit) to development workflow
- Implemented pre-commit hooks for code quality assurance

## [1.0.0] - Previous Release

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
