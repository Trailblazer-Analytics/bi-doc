from setuptools import setup, find_packages

setup(
    name="bidoc",
    version="1.0.0",
    description="Business Intelligence documentation tool for Power BI and Tableau",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="BI Documentation Tool",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "pbixray>=0.3.3",
        "tableaudocumentapi>=0.11",
        "click>=8.0.0",
        "jinja2>=3.1.0",
        "pandas>=1.5.0",
        "lxml>=4.9.0",
        "colorama>=0.4.0",
        "toml>=0.10.2",
    ],
    entry_points={
        "console_scripts": [
            "bidoc-cli=bidoc.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
