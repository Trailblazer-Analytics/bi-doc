# PowerShell Module Installation Guide

## Quick Install for Analysts

### Option 1: Local Installation (Recommended)

1. **Download the module files** to your computer
2. **Open PowerShell as Administrator**
3. **Run the installation script:**

```powershell
# Navigate to the module directory
cd "C:\Path\To\bi-doc\analyst_extensions\powershell"

# Install the module for current user
$ModulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation"
New-Item -ItemType Directory -Path $ModulePath -Force
Copy-Item "*.ps*" -Destination $ModulePath

# Import the module
Import-Module BIDocumentation

# Verify installation
Show-BIDocHelp
```

### Option 2: Manual Setup

1. **Create module directory:**
   ```powershell
   $ModulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation"
   New-Item -ItemType Directory -Path $ModulePath -Force
   ```

2. **Copy module files** (`BIDocumentation.psm1` and `BIDocumentation.psd1`) to the created directory

3. **Import the module:**
   ```powershell
   Import-Module BIDocumentation -Force
   ```

## Quick Start for Analysts

### Your First BI File Scan

```powershell
# Show help and examples
Show-BIDocHelp

# Scan a Power BI file with progress
Invoke-BIFileScan "C:\Reports\sales_dashboard.pbix" -ShowProgress -OpenResult

# Or use the shorter alias
Scan-BIFile "C:\Reports\sales_dashboard.pbix" -ShowProgress -OpenResult

# Get quick info about a file
Get-BIFileInfo "C:\Reports\sales_dashboard.pbix"
```

### Common Analyst Workflows

#### 1. Inventory All BI Files

```powershell
# Get information about all BI files in a directory
Get-ChildItem "C:\Reports" -Include "*.pbix","*.twb*" -Recurse | Get-BIFileInfo | Format-Table

# Export inventory to CSV
Get-ChildItem "C:\Reports" -Include "*.pbix","*.twb*" -Recurse | Get-BIFileInfo | Export-Csv "bi-inventory.csv" -NoTypeInformation
```

#### 2. Batch Documentation Generation

```powershell
# Process all Power BI files in current directory
Get-ChildItem "*.pbix" | Invoke-BIFileScan -ShowProgress -OutputPath ".\documentation"

# Process with results tracking (using alias for shorter syntax)
$results = Get-ChildItem "*.pbix" | Scan-BIFile -ShowProgress
$results | Where-Object Success | Format-Table FileName, OutputPath
```

#### 3. Excel Analysis Workflow

```powershell
# Scan file and convert to Excel for analysis
Invoke-BIFileScan "dashboard.pbix" -Format JSON -ShowProgress
ConvertTo-BIExcel -JSONPath ".\docs\dashboard.json"
```

#### 4. Organize Documentation by Date

```powershell
# Create date-based folder structure
$DateFolder = "documentation\$(Get-Date -Format 'yyyy-MM-dd')"
Invoke-BIFileScan "monthly_report.pbix" -OutputPath $DateFolder -ShowProgress -OpenResult
```

## Troubleshooting for Analysts

### Common Issues and Solutions

#### "Python is not installed"
```powershell
# Check if Python is available
python --version

# If not found, download from: https://python.org
# Make sure to check "Add Python to PATH" during installation
```

#### "Module not found"
```powershell
# Check module installation
Get-Module BIDocumentation -ListAvailable

# Reinstall if needed
Remove-Module BIDocumentation -Force
Import-Module BIDocumentation -Force
```

#### "Permission denied on output directory"
```powershell
# Use a different output directory you have access to
Scan-BIFile "file.pbix" -OutputPath "$env:USERPROFILE\Desktop\BI-Docs"
```

#### "Excel conversion fails"
```powershell
# Install the ImportExcel module
Install-Module ImportExcel -Scope CurrentUser -Force
```

### Getting Help

```powershell
# Show all available commands
Get-Command -Module BIDocumentation

# Get detailed help for any command
Get-Help Invoke-BIFileScan -Full
Get-Help Get-BIFileInfo -Examples
Get-Help ConvertTo-BIExcel -Detailed

# Show quick help and examples
Show-BIDocHelp
```

## Advanced Tips for Power Users

### Custom Output Organization

```powershell
# Organize by file type
$FileType = if ($file.Extension -eq '.pbix') { 'PowerBI' } else { 'Tableau' }
Scan-BIFile $file.FullName -OutputPath "docs\$FileType"

# Organize by business area (assuming naming convention)
$BusinessArea = $file.BaseName.Split('_')[0]  # e.g., "Sales_Dashboard" -> "Sales"
Scan-BIFile $file.FullName -OutputPath "docs\$BusinessArea"
```

### Automated Reporting

```powershell
# Weekly BI file inventory
$WeeklyReport = @{
    Date = Get-Date
    TotalFiles = (Get-ChildItem "*.pbix","*.twb*" | Measure-Object).Count
    ProcessedFiles = 0
    Errors = @()
}

Get-ChildItem "*.pbix","*.twb*" | ForEach-Object {
    $result = Scan-BIFile $_.FullName -ShowProgress
    if ($result.Success) {
        $WeeklyReport.ProcessedFiles++
    } else {
        $WeeklyReport.Errors += $result
    }
}

$WeeklyReport | ConvertTo-Json | Out-File "weekly-report.json"
```

### Integration with Excel Workflows

```powershell
# Process and immediately analyze in Excel
$files = Get-ChildItem "*.pbix"
foreach ($file in $files) {
    $result = Scan-BIFile $file.FullName -Format JSON -ShowProgress
    if ($result.Success) {
        ConvertTo-BIExcel -JSONPath $result.JSONFile -OutputPath "$($file.BaseName)-analysis.xlsx"
    }
}
```

## Security Notes for IT Administrators

### Module Execution Policy

The module requires PowerShell execution policy to allow script execution:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative: Bypass policy for this session only
Set-ExecutionPolicy Bypass -Scope Process
```

### Network and File Access

- Module processes files locally - no network communication for file parsing
- Python subprocess calls are made to the BI Documentation Tool CLI
- Output files are created in user-specified directories
- No sensitive data is transmitted outside the local system

### Installation Verification

```powershell
# Verify module signature and integrity
Get-AuthenticodeSignature "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation\BIDocumentation.psm1"

# Check module dependencies
Test-ModuleManifest "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation\BIDocumentation.psd1"
```

---

This PowerShell module makes BI documentation accessible to Windows analysts through familiar PowerShell commands, while maintaining the full power and flexibility of the underlying CLI tool.
