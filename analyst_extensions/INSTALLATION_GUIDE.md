# Analyst Extensions - Installation Guide

## 🎯 Overview

This guide helps business analysts and Windows users install and use the BI Documentation Tool through user-friendly interfaces that don't require command-line knowledge.

## 📋 Prerequisites

**System Requirements:**
- Windows 10 or later
- Python 3.8 or higher (with PATH configuration)
- BI Documentation Tool installed and working

**Verify Installation:**
1. Open Command Prompt or PowerShell
2. Run: `python --version` (should show Python 3.8+)
3. Run: `python -m bidoc --help` (should show help text)

If either command fails, see the main installation guide first.

## 🚀 Quick Start Options

Choose the method that best fits your comfort level:

### 1. Drag-and-Drop Batch File (Easiest)

**Best for:** Complete beginners, occasional use

**Setup:**
1. Navigate to `analyst_extensions\` folder
2. Right-click `BI-Doc-Quick-Scan.bat` 
3. Select "Send to" > "Desktop (create shortcut)"

**Usage:**
1. Drag any .pbix, .twb, or .twbx file onto the desktop shortcut
2. Follow the prompts in the popup window
3. Documentation is automatically generated and opened

**Benefits:**
- Zero learning curve
- Works immediately
- No installation required
- Perfect for single files

### 2. PowerShell Module (Recommended for Windows Users)

**Best for:** Windows power users, batch processing, automation

**Installation:**
```powershell
# Open PowerShell as Administrator
# Navigate to the PowerShell module directory
cd "C:\Path\To\bi-doc\analyst_extensions\powershell"

# Install for current user
$ModulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation"
New-Item -ItemType Directory -Path $ModulePath -Force
Copy-Item "*.ps*" -Destination $ModulePath

# Import the module
Import-Module BIDocumentation

# Show help and examples
Show-BIDocHelp
```

**Quick Examples:**
```powershell
# Scan a single file with progress and auto-open
Invoke-BIFileScan "dashboard.pbix" -ShowProgress -OpenResult

# Or use the shorter alias for convenience
Scan-BIFile "dashboard.pbix" -ShowProgress -OpenResult

# Get file information without full scan
Get-BIFileInfo "report.pbix" | Format-List

# Process all BI files in current directory
Get-ChildItem "*.pbix","*.twb*" | Invoke-BIFileScan -ShowProgress

# Open documentation folder
Open-BIDocFolder
```

**Benefits:**
- Native Windows integration
- Powerful batch processing
- Excel export capabilities
- Professional logging and error handling

### 3. Graphical User Interface (Most User-Friendly)

**Best for:** Non-technical users, visual interface preference

**Installation:**
```cmd
# Navigate to GUI directory
cd "C:\Path\To\bi-doc\analyst_extensions\gui"

# Install optional dependencies for enhanced features
pip install -r requirements.txt

# Launch the GUI
launch_gui.bat
```

**Usage:**
1. Double-click `launch_gui.bat` or run `python bidoc_gui.py`
2. Add files by clicking "Add Files..." or drag-and-drop
3. Choose output directory and format
4. Click "Scan BI Files" and watch progress
5. Open results directly from the application

**Benefits:**
- Complete graphical interface
- Real-time progress indication
- Drag-and-drop support
- Built-in results viewer
- No command-line knowledge needed

## 📊 Detailed Setup Instructions

### PowerShell Module Setup (Detailed)

#### Step 1: Verify PowerShell Execution Policy
```powershell
# Check current policy
Get-ExecutionPolicy

# If restricted, allow script execution for current user
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 2: Install the Module
```powershell
# Create module directory
$ModulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\BIDocumentation"
if (-not (Test-Path $ModulePath)) {
    New-Item -ItemType Directory -Path $ModulePath -Force
    Write-Host "Created module directory: $ModulePath"
}

# Copy module files (adjust path as needed)
$SourcePath = "C:\SecretProjects\bi-doc\analyst_extensions\powershell"
Copy-Item "$SourcePath\BIDocumentation.psm1" -Destination $ModulePath
Copy-Item "$SourcePath\BIDocumentation.psd1" -Destination $ModulePath

Write-Host "Module files copied successfully"
```

#### Step 3: Test Installation
```powershell
# Import and test
Import-Module BIDocumentation -Force
Get-Command -Module BIDocumentation

# Show help
Show-BIDocHelp
```

#### Step 4: Make It Permanent (Optional)
Add to your PowerShell profile for automatic loading:
```powershell
# Edit your PowerShell profile
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content $PROFILE "Import-Module BIDocumentation"
```

### GUI Application Setup (Detailed)

#### Step 1: Install Python Dependencies
```cmd
cd "C:\SecretProjects\bi-doc\analyst_extensions\gui"
pip install -r requirements.txt
```

#### Step 2: Test the GUI
```cmd
python bidoc_gui.py
```

#### Step 3: Create Desktop Shortcut
1. Right-click on `launch_gui.bat`
2. Select "Send to" > "Desktop (create shortcut)"
3. Rename shortcut to "BI Documentation Tool"
4. (Optional) Change icon by right-clicking > Properties > Change Icon

#### Step 4: Register File Associations (Advanced)
For right-click integration:
1. Run as Administrator
2. Execute the Windows Shell Extension installer (when available)
3. Or manually add registry entries for .pbix, .twb, .twbx files

## 📖 Usage Examples by Scenario

### Scenario 1: Monthly Report Documentation

**Using PowerShell:**
```powershell
# Process monthly reports with date-based organization
$MonthFolder = "Documentation\$(Get-Date -Format 'yyyy-MM')"
Get-ChildItem "Monthly_Reports\*.pbix" | Scan-BIFile -OutputPath $MonthFolder -ShowProgress

# Generate Excel analysis for stakeholders
Get-ChildItem "$MonthFolder\*.json" | ForEach-Object {
    ConvertTo-BIExcel -JSONPath $_.FullName
}
```

**Using GUI:**
1. Open BI Documentation GUI
2. Add all monthly report files
3. Set output to "Documentation\2024-12"
4. Choose "All" format
5. Click scan and review results

### Scenario 2: BI Asset Inventory

**Using PowerShell:**
```powershell
# Create comprehensive inventory
$AllFiles = Get-ChildItem "\\SharePoint\BI-Files" -Include "*.pbix","*.twb*" -Recurse
$Inventory = $AllFiles | Get-BIFileInfo
$Inventory | Export-Csv "BI-Asset-Inventory.csv" -NoTypeInformation
$Inventory | Format-Table Name, Type, SizeMB, LastModified
```

**Using Batch File:**
1. Create a folder with all BI files
2. Run `BI-Doc-Quick-Scan.bat` on each file
3. Collect all generated documentation

### Scenario 3: Team Collaboration Setup

**For Team Lead (PowerShell):**
```powershell
# Setup automated documentation for team files
$TeamFiles = "\\TeamShare\BI-Dashboards"
$OutputBase = "\\TeamShare\Documentation"

# Process all files and organize by owner
Get-ChildItem "$TeamFiles\*.pbix" | ForEach-Object {
    $Owner = $_.Name.Split('_')[0]  # Assuming naming convention
    $OutputPath = "$OutputBase\$Owner"
    Scan-BIFile $_.FullName -OutputPath $OutputPath -ShowProgress
}
```

**For Team Members (GUI):**
1. Each member documents their own files
2. Save to shared documentation folder
3. Use consistent naming conventions
4. Regular updates via scheduled scans

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "Python is not recognized"
**Problem:** Python not in system PATH
**Solution:**
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Or manually add Python to PATH in System Environment Variables

#### "BI Documentation Tool not found"
**Problem:** CLI tool not installed
**Solution:**
```cmd
# Test the CLI directly
python -m bidoc --help

# If error, reinstall the BI Documentation Tool
cd "C:\SecretProjects\bi-doc"
pip install -e .
```

#### PowerShell "Execution Policy" errors
**Problem:** Scripts blocked by security policy
**Solution:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### GUI crashes or won't start
**Problem:** Missing dependencies or configuration
**Solution:**
```cmd
# Install all optional dependencies
pip install tkinterdnd2 openpyxl

# Test basic functionality
python -c "import tkinter; tkinter.Tk().mainloop()"
```

#### "Permission denied" on output directories
**Problem:** Insufficient write permissions
**Solution:**
1. Choose a different output directory (like Desktop or Documents)
2. Run as Administrator
3. Check folder permissions in Properties > Security

### Performance Tips

**For Large Files:**
- Use SSD storage for better I/O performance
- Close other applications during processing
- Consider processing files in smaller batches
- Monitor system memory usage

**For Batch Processing:**
- Use PowerShell parallel processing when available
- Process files during off-hours
- Use incremental processing for regular updates
- Archive old documentation to save space

## 🎯 Best Practices for Analysts

### File Organization
```text
Recommended folder structure:
BI-Documentation/
├── Sources/           # Original BI files
│   ├── PowerBI/
│   ├── Tableau/
│   └── Archive/
├── Documentation/     # Generated docs
│   ├── 2024-12/
│   ├── 2024-11/
│   └── Archive/
└── Analysis/          # Excel exports and reports
    ├── Inventories/
    └── Comparisons/
```

### Naming Conventions
- Use descriptive filenames: `Sales_Dashboard_Q4_2024.pbix`
- Include dates in ISO format: `YYYY-MM-DD`
- Use consistent prefixes: `PROD_`, `TEST_`, `DEV_`
- Avoid spaces and special characters in file paths

### Regular Maintenance
- **Weekly:** Update documentation for modified files
- **Monthly:** Generate inventory reports
- **Quarterly:** Archive old documentation
- **Annually:** Review and clean up file organization

### Team Collaboration
- **Shared Templates:** Use consistent documentation templates
- **Version Control:** Track changes in documentation
- **Access Control:** Manage permissions on shared folders
- **Communication:** Share documentation locations with stakeholders

## 📞 Support and Resources

### Getting Help
1. **Built-in Help:** Use `Show-BIDocHelp` in PowerShell
2. **Documentation:** Check the main USER_GUIDE.md
3. **Examples:** Review QOL_SUGGESTIONS.md for advanced features
4. **Community:** Join user forums and discussions

### Advanced Features
- **Automation:** Schedule regular documentation updates
- **Integration:** Connect with SharePoint, Confluence
- **Customization:** Create custom templates and formats
- **Analytics:** Track documentation usage and patterns

---

*This guide makes BI documentation accessible to every analyst, regardless of technical background. Choose the method that fits your workflow and gradually explore more advanced features as needed.*
