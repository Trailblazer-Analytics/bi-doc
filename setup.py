from setuptools import find_packages, setup
import os

# Read the README file
def read_readme():
    try:
        with open("README.md", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "BI Documentation Tool - Generate comprehensive documentation from Power BI and Tableau files"

# Read version from __version__.py
def read_version():
    try:
        with open(os.path.join("bidoc", "__version__.py"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "1.0.0"

setup(
    name="bidoc",
    version=read_version(),
    description="Business Intelligence documentation tool for Power BI and Tableau",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="BI Documentation Tool Team",
    author_email="noreply@trailblazer-analytics.com",
    url="https://github.com/Trailblazer-Analytics/bi-doc",
    project_urls={
        "Documentation": "https://github.com/Trailblazer-Analytics/bi-doc#readme",
        "Repository": "https://github.com/Trailblazer-Analytics/bi-doc",
        "Bug Tracker": "https://github.com/Trailblazer-Analytics/bi-doc/issues",
        "Changelog": "https://github.com/Trailblazer-Analytics/bi-doc/blob/main/CHANGELOG.md",
        "Integration Guide": "https://github.com/Trailblazer-Analytics/bi-doc/blob/main/INTEGRATION_HOOKS.md",
    },
    keywords=[
        "power-bi", "tableau", "business-intelligence", "documentation", 
        "metadata", "data-catalog", "enterprise-integration", "dax-formatter"
    ],
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*", "archive*", "scripts*"]),
    package_data={
        "bidoc": ["templates/*.j2", "*.toml"],
    },
    include_package_data=True,
    install_requires=[
        "pbixray>=0.3.3,<0.4.0",
        "tableaudocumentapi>=0.11,<0.12",
        "click>=8.0.0,<9.0.0",
        "jinja2>=3.1.0,<4.0.0",
        "pandas>=1.5.0,<3.0.0",
        "lxml>=4.9.0,<5.0.0",
        "colorama>=0.4.0,<0.5.0",
        "toml>=0.10.2,<0.11.0",
        "psutil>=5.9.0,<6.0.0",
        "importlib-metadata>=1.0.0,<7.0.0; python_version < '3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
            "sphinx-click>=4.4.0",
        ],
        "performance": [
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bidoc=bidoc.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Documentation",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    zip_safe=False,
)
