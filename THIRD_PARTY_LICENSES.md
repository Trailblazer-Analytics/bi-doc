# Third-Party Licenses and Attributions

This document provides comprehensive attribution and licensing information for all third-party components used in the BI Documentation Tool project.

## Core Dependencies

### PBIXRay

**Package**: pbixray
**Version**: >=0.3.3
**Purpose**: Power BI (.pbix) file parsing and metadata extraction
**Repository**: <https://github.com/aafvstam/pbixray>
**License**: MIT License

```text
MIT License

Copyright (c) 2021 Arjen van Stam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Attribution**: This project uses PBIXRay by Arjen van Stam for parsing Power BI files. We are grateful for this excellent open-source tool that makes Power BI file analysis possible.

### Tableau Document API

**Package**: tableaudocumentapi
**Version**: >=0.11
**Purpose**: Tableau (.twb/.twbx) workbook parsing and metadata extraction
**Repository**: <https://github.com/tableau/document-api-python>
**License**: MIT License

```text
MIT License

Copyright (c) 2016 Tableau Software

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Attribution**: This project uses the Tableau Document API by Tableau Software for parsing Tableau workbooks. We thank Tableau for providing this valuable open-source library.

### DAX Formatter (Inspiration)

**Project**: DAX Formatter by SQL BI
**Purpose**: Inspiration for DAX expression formatting standards
**Repository**: <https://github.com/sql-bi/DaxFormatter>
**Web Interface**: <https://www.daxformatter.com/>
**License**: Not directly used as dependency - formatting conventions inspired by this project

**Attribution**: The DAX formatting functionality in this tool implements formatting conventions compatible with and inspired by DAX Formatter by SQL BI, which is the industry standard for DAX code formatting. DAX Formatter is developed by the SQL BI team and provides comprehensive formatting capabilities for DAX expressions. Our implementation follows similar principles to ensure consistency with established DAX coding standards.

Special thanks to the SQL BI team for their contributions to the DAX community and for establishing formatting standards that improve DAX code readability across the ecosystem.

For advanced DAX formatting needs beyond what this tool provides, we recommend using the official DAX Formatter tools:

- GitHub: <https://github.com/sql-bi/DaxFormatter>
- Web interface: <https://www.daxformatter.com/>
- VS Code extension: DAX Formatter extension by SQL BI

## Supporting Libraries

### Click

**Package**: click
**Version**: >=8.0.0
**Purpose**: Command-line interface framework
**Repository**: <https://github.com/pallets/click>
**License**: BSD-3-Clause License

**Attribution**: Command-line interface powered by Click, a Python package for creating beautiful command line interfaces.

### Jinja2

**Package**: jinja2
**Version**: >=3.1.0
**Purpose**: Template engine for generating documentation
**Repository**: <https://github.com/pallets/jinja>
**License**: BSD-3-Clause License

**Attribution**: Documentation templates rendered using Jinja2, a modern and designer-friendly templating language for Python.

### Pandas

**Package**: pandas
**Version**: >=1.5.0
**Purpose**: Data manipulation and analysis
**Repository**: <https://github.com/pandas-dev/pandas>
**License**: BSD-3-Clause License

**Attribution**: Data processing capabilities provided by pandas, a powerful data analysis and manipulation library for Python.

### lxml

**Package**: lxml
**Version**: >=4.9.0
**Purpose**: XML and HTML processing
**Repository**: <https://github.com/lxml/lxml>
**License**: BSD-3-Clause License

**Attribution**: XML processing capabilities provided by lxml, the most feature-rich and easy-to-use library for processing XML and HTML in Python.

### Colorama

**Package**: colorama
**Version**: >=0.4.0
**Purpose**: Cross-platform colored terminal text
**Repository**: <https://github.com/tartley/colorama>
**License**: BSD-3-Clause License

**Attribution**: Cross-platform colored output provided by Colorama, making ANSI escape character sequences work under MS Windows.

## Optional Dependencies (GUI Extensions)

### tkinterdnd2

**Package**: tkinterdnd2
**Version**: >=0.3.0
**Purpose**: Drag-and-drop functionality for tkinter GUIs
**Repository**: <https://github.com/pmgagne/tkinterdnd2>
**License**: MIT License

**Attribution**: Drag-and-drop functionality in the analyst GUI provided by tkinterdnd2, a Python wrapper for the tkdnd drag-and-drop library.

### OpenPyXL

**Package**: openpyxl
**Version**: >=3.0.0
**Purpose**: Excel file creation and manipulation
**Repository**: <https://foss.heptapod.net/openpyxl/openpyxl>
**License**: MIT License

**Attribution**: Excel export functionality provided by OpenPyXL, a Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files.

## Sample Files and Test Data

### Microsoft Power BI Sample Files

**Source**: Microsoft PowerBI Desktop Samples
**Repository**: <https://github.com/Microsoft/powerbi-desktop-samples>
**License**: MIT License
**Purpose**: Demonstration and testing of Power BI file parsing capabilities

```text
MIT License

Copyright (c) Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Attribution**: Sample Power BI files provided by Microsoft Corporation for demonstration and educational purposes. We are grateful to Microsoft for making these samples freely available.

## Development Dependencies

The following dependencies are used during development and testing but are not included in the runtime distribution:

- **pytest**: Testing framework (MIT License)
- **black**: Code formatting (MIT License)
- **flake8**: Code linting (MIT License)
- **mypy**: Type checking (MIT License)

## License Summary

All third-party dependencies use permissive licenses (MIT, BSD-3-Clause) that are compatible with our Business Source License 1.1. No copyleft licenses (GPL, LGPL) are used in this project.

### License Compatibility Matrix

| Our License | Third-Party License | Compatibility | Notes |
|-------------|-------------------|---------------|-------|
| BSL 1.1 | MIT | ✅ Compatible | Full compatibility |
| BSL 1.1 | BSD-3-Clause | ✅ Compatible | Full compatibility |
| BSL 1.1 | Apache 2.0 | ✅ Compatible | Full compatibility |

## Attribution Requirements Compliance

### Code Attribution

All major third-party libraries are properly imported and used according to their license terms. No license headers need to be included in source files as all dependencies use permissive licenses.

### Documentation Attribution

This document serves as the central attribution file, acknowledging all third-party contributions to the project.

### Binary Distribution

When distributing binary packages, this attribution file should be included to ensure proper credit is given to all third-party contributors.

## Trademark Acknowledgments

- **Power BI** is a trademark of Microsoft Corporation
- **Tableau** is a trademark of Tableau Software, LLC
- **Python** is a trademark of the Python Software Foundation
- **Windows** is a trademark of Microsoft Corporation

## Updates and Maintenance

This attribution file is maintained alongside the project's dependency management. When dependencies are added, removed, or updated, this file should be updated accordingly.

**Last Updated**: July 4, 2025
**Next Review**: Next major release or dependency update

## Contact

For questions about licensing or attribution, please contact the project maintainers through the project's official communication channels.

---

**Note**: This file provides attribution for third-party software used in the BI Documentation Tool. The BI Documentation Tool itself is licensed under the Business Source License 1.1. See the LICENSE file for complete license terms.
