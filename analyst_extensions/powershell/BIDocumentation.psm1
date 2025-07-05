# BIDocumentation PowerShell Module
# Analyst-friendly wrapper for the BI Documentation Tool

# Import required modules if available
if (Get-Module -ListAvailable -Name "Microsoft.PowerShell.Utility") {
    Import-Module Microsoft.PowerShell.Utility
}

<#
.SYNOPSIS
    Scans a Business Intelligence file and generates documentation.

.DESCRIPTION
    The Invoke-BIFileScan cmdlet processes Power BI (.pbix) and Tableau (.twb/.twbx) files
    to extract metadata and generate comprehensive documentation in Markdown and JSON formats.

.PARAMETER Path
    The path to the BI file to scan. Supports .pbix, .twb, and .twbx files.

.PARAMETER OutputPath
    The directory where documentation will be saved. Defaults to current directory + '\docs'.

.PARAMETER Format
    The output format(s). Valid values are 'Markdown', 'JSON', or 'All'. Defaults to 'All'.

.PARAMETER ShowProgress
    Display progress information during processing.

.PARAMETER OpenResult
    Automatically open the generated documentation when complete.

.EXAMPLE
    Invoke-BIFileScan -Path "C:\Reports\sales_dashboard.pbix"
    Scans the Power BI file and saves documentation to .\docs\

.EXAMPLE
    Invoke-BIFileScan -Path "dashboard.twbx" -OutputPath "C:\Documentation" -Format Markdown -ShowProgress
    Scans a Tableau file with progress display and saves only Markdown output.

.EXAMPLE
    Get-ChildItem "*.pbix" | Invoke-BIFileScan -ShowProgress
    Scans all Power BI files in the current directory.
#>
function Invoke-BIFileScan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [Alias("FullName", "FilePath")]
        [string]$Path,

        [Parameter()]
        [string]$OutputPath = ".\docs",

        [Parameter()]
        [ValidateSet("Markdown", "JSON", "All")]
        [string]$Format = "All",

        [Parameter()]
        [switch]$ShowProgress,

        [Parameter()]
        [switch]$OpenResult
    )

    begin {
        Write-Verbose "Starting BI file scanning process"

        # Ensure output directory exists
        if (-not (Test-Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
            Write-Verbose "Created output directory: $OutputPath"
        }

        # Check if Python and bidoc are available
        try {
            $pythonVersion = python --version 2>&1
            Write-Verbose "Python version: $pythonVersion"
        }
        catch {
            throw "Python is not installed or not in PATH. Please install Python 3.8+ and the BI Documentation Tool."
        }
    }

    process {
        # Resolve full path
        $FullPath = Resolve-Path $Path -ErrorAction Stop
        $FileName = [System.IO.Path]::GetFileNameWithoutExtension($FullPath)
        $Extension = [System.IO.Path]::GetExtension($FullPath).ToLower()

        # Validate file type
        if ($Extension -notin @('.pbix', '.twb', '.twbx')) {
            Write-Warning "Unsupported file type: $Extension. Supported types: .pbix, .twb, .twbx"
            return
        }

        Write-Host "📊 Scanning BI file: " -NoNewline
        Write-Host $FileName -ForegroundColor Cyan

        if ($ShowProgress) {
            Write-Progress -Activity "Scanning BI File" -Status "Processing $FileName" -PercentComplete 0
        }

        # Build command arguments
        $formatArg = switch ($Format) {
            "Markdown" { "markdown" }
            "JSON" { "json" }
            "All" { "all" }
        }

        $arguments = @(
            "-m", "bidoc",
            "-i", "`"$FullPath`"",
            "-o", "`"$OutputPath`"",
            "-f", $formatArg
        )

        if ($ShowProgress) {
            $arguments += "-v"
        }

        try {
            if ($ShowProgress) {
                Write-Progress -Activity "Scanning BI File" -Status "Extracting metadata..." -PercentComplete 25
            }

            # Execute the BI documentation tool
            $result = & python $arguments 2>&1

            if ($LASTEXITCODE -eq 0) {
                if ($ShowProgress) {
                    Write-Progress -Activity "Scanning BI File" -Status "Documentation generated successfully" -PercentComplete 100
                    Start-Sleep -Milliseconds 500
                    Write-Progress -Activity "Scanning BI File" -Completed
                }

                Write-Host "✅ Successfully generated documentation for " -NoNewline
                Write-Host $FileName -ForegroundColor Green

                # Create result object
                $resultObj = [PSCustomObject]@{
                    FileName = $FileName
                    FilePath = $FullPath
                    OutputPath = $OutputPath
                    Format = $Format
                    MarkdownFile = if ($Format -in @("Markdown", "All")) { Join-Path $OutputPath "$FileName.md" } else { $null }
                    JSONFile = if ($Format -in @("JSON", "All")) { Join-Path $OutputPath "$FileName.json" } else { $null }
                    Success = $true
                    Timestamp = Get-Date
                }

                # Auto-open result if requested
                if ($OpenResult) {
                    if ($resultObj.MarkdownFile -and (Test-Path $resultObj.MarkdownFile)) {
                        Write-Host "📖 Opening documentation..." -ForegroundColor Yellow
                        Invoke-Item $resultObj.MarkdownFile
                    }
                    elseif ($resultObj.JSONFile -and (Test-Path $resultObj.JSONFile)) {
                        Write-Host "📄 Opening JSON output..." -ForegroundColor Yellow
                        Invoke-Item $resultObj.JSONFile
                    }
                }

                return $resultObj
            }
            else {
                throw "BI documentation tool failed with exit code $LASTEXITCODE. Error: $result"
            }
        }
        catch {
            if ($ShowProgress) {
                Write-Progress -Activity "Scanning BI File" -Completed
            }

            Write-Error "❌ Failed to process $FileName : $($_.Exception.Message)"

            return [PSCustomObject]@{
                FileName = $FileName
                FilePath = $FullPath
                OutputPath = $OutputPath
                Format = $Format
                Success = $false
                Error = $_.Exception.Message
                Timestamp = Get-Date
            }
        }
    }

    end {
        Write-Verbose "BI file scanning process completed"
    }
}

<#
.SYNOPSIS
    Gets basic information about a BI file without generating full documentation.

.DESCRIPTION
    The Get-BIFileInfo cmdlet provides a quick overview of a BI file's contents,
    including basic metadata like data sources, table count, and file size.

.PARAMETER Path
    The path to the BI file to inspect.

.EXAMPLE
    Get-BIFileInfo -Path "sales_dashboard.pbix"
    Shows basic information about the Power BI file.

.EXAMPLE
    Get-ChildItem "*.pbix" | Get-BIFileInfo | Format-Table
    Shows information for all Power BI files in a table format.
#>
function Get-BIFileInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [Alias("FullName", "FilePath")]
        [string]$Path
    )

    process {
        $FullPath = Resolve-Path $Path -ErrorAction Stop
        $FileInfo = Get-Item $FullPath
        $Extension = $FileInfo.Extension.ToLower()

        # Validate file type
        if ($Extension -notin @('.pbix', '.twb', '.twbx')) {
            Write-Warning "Unsupported file type: $Extension"
            return
        }

        $FileType = switch ($Extension) {
            '.pbix' { 'Power BI Desktop' }
            '.twb' { 'Tableau Workbook' }
            '.twbx' { 'Tableau Packaged Workbook' }
        }

        # Basic file information
        $info = [PSCustomObject]@{
            Name = $FileInfo.BaseName
            Type = $FileType
            Extension = $Extension
            SizeMB = [Math]::Round($FileInfo.Length / 1MB, 2)
            LastModified = $FileInfo.LastWriteTime
            FullPath = $FullPath
            CanScan = $true
        }

        return $info
    }
}

<#
.SYNOPSIS
    Opens the output directory for BI documentation.

.DESCRIPTION
    Opens the specified directory in Windows Explorer, or the default docs directory.

.PARAMETER Path
    The path to open. Defaults to .\docs

.EXAMPLE
    Open-BIDocFolder
    Opens the default .\docs directory.

.EXAMPLE
    Open-BIDocFolder -Path "C:\Documentation\BI"
    Opens the specified directory.
#>
function Open-BIDocFolder {
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Path = ".\docs"
    )

    if (Test-Path $Path) {
        Write-Host "📁 Opening documentation folder..." -ForegroundColor Yellow
        Invoke-Item $Path
    }
    else {
        Write-Warning "Documentation folder not found: $Path"
        Write-Host "Use Scan-BIFile to generate documentation first." -ForegroundColor Yellow
    }
}

<#
.SYNOPSIS
    Converts BI documentation to Excel format for analysis.

.DESCRIPTION
    Takes JSON output from BI documentation and converts it to Excel worksheets
    for easier analysis by business analysts.

.PARAMETER JSONPath
    Path to the JSON documentation file.

.PARAMETER OutputPath
    Path for the Excel output file.

.EXAMPLE
    ConvertTo-BIExcel -JSONPath ".\docs\dashboard.json" -OutputPath ".\analysis.xlsx"
    Converts the JSON documentation to Excel format.
#>
function ConvertTo-BIExcel {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$JSONPath,

        [Parameter()]
        [string]$OutputPath
    )

    if (-not (Test-Path $JSONPath)) {
        throw "JSON file not found: $JSONPath"
    }

    if (-not $OutputPath) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($JSONPath)
        $OutputPath = "$baseName-analysis.xlsx"
    }

    try {
        $jsonContent = Get-Content $JSONPath -Raw | ConvertFrom-Json

        Write-Host "📊 Converting BI documentation to Excel..." -ForegroundColor Yellow
        Write-Host "📄 Input: $JSONPath"
        Write-Host "📁 Output: $OutputPath"

        # Check if ImportExcel module is available
        if (Get-Module -ListAvailable -Name "ImportExcel") {
            Import-Module ImportExcel

            # Create Excel workbook with multiple sheets
            $excelParams = @{
                Path = $OutputPath
                WorksheetName = "Overview"
                TableStyle = "Medium2"
                AutoSize = $true
                FreezeTopRow = $true
            }

            # Overview sheet
            $overview = [PSCustomObject]@{
                "File Name" = $jsonContent.file_name
                "File Type" = $jsonContent.file_type
                "Data Sources" = ($jsonContent.data_sources | Measure-Object).Count
                "Tables" = if ($jsonContent.tables) { ($jsonContent.tables | Measure-Object).Count } else { 0 }
                "Measures" = if ($jsonContent.measures) { ($jsonContent.measures | Measure-Object).Count } else { 0 }
                "Generated" = Get-Date
            }

            $overview | Export-Excel @excelParams

            # Data Sources sheet
            if ($jsonContent.data_sources) {
                $jsonContent.data_sources | Export-Excel -Path $OutputPath -WorksheetName "Data Sources" -TableStyle "Medium2" -AutoSize
            }

            # Tables sheet
            if ($jsonContent.tables) {
                $tables = $jsonContent.tables | ForEach-Object {
                    [PSCustomObject]@{
                        "Table Name" = $_.name
                        "Column Count" = ($_.columns | Measure-Object).Count
                        "Data Type" = $_.type
                        "Description" = $_.description
                    }
                }
                $tables | Export-Excel -Path $OutputPath -WorksheetName "Tables" -TableStyle "Medium2" -AutoSize
            }

            Write-Host "✅ Excel analysis file created: $OutputPath" -ForegroundColor Green
            Write-Host "📖 Opening Excel file..." -ForegroundColor Yellow
            Invoke-Item $OutputPath
        }
        else {
            Write-Warning "ImportExcel module not found. Installing..."
            Write-Host "Run: Install-Module ImportExcel -Scope CurrentUser" -ForegroundColor Yellow
            Write-Host "Then try the command again." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Error "Failed to convert to Excel: $($_.Exception.Message)"
    }
}

<#
.SYNOPSIS
    Shows help and examples for the BI Documentation PowerShell module.

.DESCRIPTION
    Displays common usage examples and tips for working with BI files.

.EXAMPLE
    Show-BIDocHelp
    Displays help and usage examples.
#>
function Show-BIDocHelp {
    Write-Host ""
    Write-Host "🔧 BI Documentation Tool - PowerShell Module" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Quick Examples:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  # Scan a single file with progress"
    Write-Host "  Invoke-BIFileScan 'dashboard.pbix' -ShowProgress -OpenResult"
    Write-Host ""
    Write-Host "  # Scan all BI files in current directory"
    Write-Host "  Get-ChildItem '*.pbix','*.twb*' | Invoke-BIFileScan -ShowProgress"
    Write-Host ""
    Write-Host "  # Get file information without full scan"
    Write-Host "  Get-BIFileInfo 'report.pbix' | Format-List"
    Write-Host ""
    Write-Host "  # Convert documentation to Excel"
    Write-Host "  ConvertTo-BIExcel -JSONPath '.\docs\dashboard.json'"
    Write-Host ""
    Write-Host "📁 File Management:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  # Open documentation folder"
    Write-Host "  Open-BIDocFolder"
    Write-Host ""
    Write-Host "  # Scan and organize by date"
    Write-Host "  Invoke-BIFileScan 'report.pbix' -OutputPath 'docs\$(Get-Date -Format yyyy-MM-dd)'"
    Write-Host ""
    Write-Host "🔍 Advanced Usage:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  # Batch processing with results"
    Write-Host "  `$results = Get-ChildItem '*.pbix' | Invoke-BIFileScan -ShowProgress"
    Write-Host "  `$results | Where-Object Success | Format-Table"
    Write-Host ""
    Write-Host "  # Generate inventory report"
    Write-Host "  Get-ChildItem '*.pbix','*.twb*' | Get-BIFileInfo | Export-Csv 'bi-inventory.csv'"
    Write-Host ""
    Write-Host "� Tip: You can also use the shorter alias 'Scan-BIFile' instead of 'Invoke-BIFileScan'"
    Write-Host ""
    Write-Host "�📖 For detailed help on any command, use:"
    Write-Host "  Get-Help <CommandName> -Full"
    Write-Host ""
    Write-Host "  Example: Get-Help Invoke-BIFileScan -Full"
    Write-Host ""
}

# Module exports
Export-ModuleMember -Function @(
    'Invoke-BIFileScan',
    'Get-BIFileInfo',
    'Open-BIDocFolder',
    'ConvertTo-BIExcel',
    'Show-BIDocHelp'
) -Alias @(
    'Scan-BIFile'
)

# Create alias for backward compatibility and easier typing
New-Alias -Name 'Scan-BIFile' -Value 'Invoke-BIFileScan' -Description 'Backward compatibility alias for Invoke-BIFileScan'
