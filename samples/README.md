# BI Documentation Tool - Sample Files

This directory contains sample BI files for testing and demonstration purposes. Use these files to validate and showcase the capabilities of the BI Documentation Tool.

## Structure

- `power_bi/` — Power BI sample reports (`.pbix` files)
- *(future)* `tableau/` — Tableau sample workbooks (`.twb`, `.twbx` files)
- *(future)* `qlik/` — Qlik sample files, etc.

## Usage

You can use these files as input for the BI Documentation Tool, for example:

```bash
python -m bidoc -i samples/power_bi/Sales\ \&\ Returns\ Sample\ v201912.pbix -o docs/ --verbose
```

## Source

The Power BI sample files are sourced from the official Microsoft [powerbi-desktop-samples](https://github.com/microsoft/powerbi-desktop-samples) repository.

## License

Sample files are provided for non-commercial, educational, and testing purposes only. See the original source repository for their specific license terms.
