# BIDocumentation Module Manifest

@{
    # Script module or binary module file associated with this manifest.
    RootModule = 'BIDocumentation.psm1'

    # Version number of this module.
    ModuleVersion = '1.0.0'

    # Supported PSEditions
    CompatiblePSEditions = @('Desktop', 'Core')

    # ID used to uniquely identify this module
    GUID = 'a8b5c3d7-e2f4-4a6b-9c8d-1e3f5a7b9c2d'

    # Author of this module
    Author = 'BI Documentation Tool Team'

    # Company or vendor of this module
    CompanyName = 'BI-Doc'

    # Copyright statement for this module
    Copyright = '(c) 2024 BI Documentation Tool. All rights reserved.'

    # Description of the functionality provided by this module
    Description = 'PowerShell module for analyst-friendly BI file documentation. Scan Power BI (.pbix) and Tableau (.twb/.twbx) files to generate comprehensive documentation in Markdown and JSON formats.'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'

    # Functions to export from this module
    FunctionsToExport = @(
        'Invoke-BIFileScan',
        'Get-BIFileInfo',
        'Open-BIDocFolder',
        'ConvertTo-BIExcel',
        'Show-BIDocHelp'
    )

    # Cmdlets to export from this module
    CmdletsToExport = @()

    # Variables to export from this module
    VariablesToExport = @()

    # Aliases to export from this module
    AliasesToExport = @('Scan-BIFile')

    # Private data to pass to the module specified in RootModule/ModuleToProcess
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @('BI', 'PowerBI', 'Tableau', 'Documentation', 'Analysis', 'Metadata', 'Business-Intelligence')

            # A URL to the license for this module.
            LicenseUri = 'https://github.com/your-org/bi-doc/blob/main/LICENSE'

            # A URL to the main website for this project.
            ProjectUri = 'https://github.com/your-org/bi-doc'

            # ReleaseNotes of this module
            ReleaseNotes = @'
## Version 1.0.0
- Initial release of analyst-friendly PowerShell module
- Scan-BIFile cmdlet for processing BI files
- Get-BIFileInfo for quick file inspection
- Excel export capabilities
- Progress indicators and user-friendly output
- Support for Power BI (.pbix) and Tableau (.twb/.twbx) files
'@
        }
    }
}
