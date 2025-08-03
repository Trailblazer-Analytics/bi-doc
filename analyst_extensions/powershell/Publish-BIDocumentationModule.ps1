# PowerShell Gallery Publishing Script for BI Documentation Tool
# This script publishes the BIDocumentation PowerShell module to PowerShell Gallery
# 
# Usage:
#   .\Publish-BIDocumentationModule.ps1 -WhatIf          # Test mode
#   .\Publish-BIDocumentationModule.ps1 -Confirm        # Interactive mode
#   .\Publish-BIDocumentationModule.ps1 -Force          # Direct publish

[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$Force,
    [switch]$WhatIf,
    [string]$Repository = "PSGallery",
    [string]$ModulePath = $PSScriptRoot,
    [string]$NuGetApiKey = $env:POWERSHELL_GALLERY_API_KEY
)

# Module information
$ModuleName = "BIDocumentation"
$ModuleVersion = "1.0.0"

Write-Host "🚀 PowerShell Gallery Publishing for BI Documentation Tool" -ForegroundColor Cyan
Write-Host "Module: $ModuleName" -ForegroundColor Green
Write-Host "Version: $ModuleVersion" -ForegroundColor Green
Write-Host "Repository: $Repository" -ForegroundColor Green

function Test-Prerequisites {
    Write-Host "Validating prerequisites..." -ForegroundColor Yellow
    
    # Check if PowerShellGet is available
    if (-not (Get-Module -ListAvailable -Name PowerShellGet)) {
        Write-Error "PowerShellGet module is required. Install with: Install-Module PowerShellGet -Force"
        return $false
    }
    
    # Check if module files exist
    $moduleFile = Join-Path $ModulePath "$ModuleName.psm1"
    $manifestFile = Join-Path $ModulePath "$ModuleName.psd1"
    
    if (-not (Test-Path $moduleFile)) {
        Write-Error "Module file not found: $moduleFile"
        return $false
    }
    
    if (-not (Test-Path $manifestFile)) {
        Write-Error "Module manifest not found: $manifestFile"
        return $false
    }
    
    # Check API key for publishing
    if (-not $WhatIf -and -not $NuGetApiKey) {
        Write-Warning "No API key provided. Set POWERSHELL_GALLERY_API_KEY environment variable or use -NuGetApiKey parameter"
        $script:NuGetApiKey = Read-Host "Enter PowerShell Gallery API Key" -AsSecureString
        $script:NuGetApiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($script:NuGetApiKey))
    }
    
    Write-Host "✅ Prerequisites validated" -ForegroundColor Green
    return $true
}

function Test-ModuleStructure {
    Write-Host "Validating module structure..." -ForegroundColor Yellow
    
    # Test module manifest
    $manifestPath = Join-Path $ModulePath "$ModuleName.psd1"
    try {
        $manifest = Test-ModuleManifest -Path $manifestPath -ErrorAction Stop
        Write-Host "✅ Module manifest is valid" -ForegroundColor Green
        Write-Host "  Version: $($manifest.Version)" -ForegroundColor Gray
        Write-Host "  Author: $($manifest.Author)" -ForegroundColor Gray
        Write-Host "  Description: $($manifest.Description)" -ForegroundColor Gray
    }
    catch {
        Write-Error "Module manifest validation failed: $_"
        return $false
    }
    
    # Test module import
    try {
        Import-Module $manifestPath -Force -ErrorAction Stop
        $functions = Get-Command -Module $ModuleName
        Write-Host "✅ Module imports successfully" -ForegroundColor Green
        Write-Host "  Exported functions: $($functions.Count)" -ForegroundColor Gray
        foreach ($func in $functions) {
            Write-Host "    - $($func.Name)" -ForegroundColor Gray
        }
        Remove-Module $ModuleName -Force
    }
    catch {
        Write-Error "Module import failed: $_"
        return $false
    }
    
    return $true
}

function Test-ExistingVersion {
    Write-Host "Checking for existing versions..." -ForegroundColor Yellow
    
    try {
        $existingModule = Find-Module -Name $ModuleName -Repository $Repository -ErrorAction SilentlyContinue
        if ($existingModule) {
            Write-Host "Found existing module version: $($existingModule.Version)" -ForegroundColor Yellow
            
            $manifestPath = Join-Path $ModulePath "$ModuleName.psd1"
            $manifest = Test-ModuleManifest -Path $manifestPath
            $currentVersion = $manifest.Version
            
            if ($currentVersion -le $existingModule.Version) {
                Write-Warning "Current version ($currentVersion) is not greater than published version ($($existingModule.Version))"
                Write-Warning "Consider updating the version in $ModuleName.psd1"
                
                if (-not $Force) {
                    $response = Read-Host "Continue anyway? (y/N)"
                    if ($response -ne 'y' -and $response -ne 'Y') {
                        Write-Host "Publishing cancelled" -ForegroundColor Red
                        return $false
                    }
                }
            }
        }
        else {
            Write-Host "No existing version found - this will be the first publication" -ForegroundColor Green
        }
    }
    catch {
        Write-Warning "Could not check existing versions: $_"
    }
    
    return $true
}

function Publish-ModuleToGallery {
    Write-Host "Publishing module to PowerShell Gallery..." -ForegroundColor Yellow
    
    $publishParams = @{
        Path = $ModulePath
        Repository = $Repository
        NuGetApiKey = $NuGetApiKey
        Force = $Force.IsPresent
        Verbose = $VerbosePreference -eq 'Continue'
    }
    
    if ($WhatIf) {
        Write-Host "WhatIf: Would publish module with parameters:" -ForegroundColor Magenta
        $publishParams | ConvertTo-Json | Write-Host -ForegroundColor Gray
        return $true
    }
    
    try {
        if ($PSCmdlet.ShouldProcess("$ModuleName to $Repository", "Publish Module")) {
            Publish-Module @publishParams
            Write-Host "✅ Module published successfully!" -ForegroundColor Green
            Write-Host "Installation command: Install-Module $ModuleName" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Error "Publishing failed: $_"
        return $false
    }
    
    return $true
}

function Show-PostPublishInfo {
    Write-Host "`n📋 Post-Publication Information" -ForegroundColor Cyan
    Write-Host "Module Name: $ModuleName" -ForegroundColor Green
    Write-Host "Repository: $Repository" -ForegroundColor Green
    Write-Host "`nInstallation Commands:" -ForegroundColor Yellow
    Write-Host "  Install-Module $ModuleName" -ForegroundColor Gray
    Write-Host "  Import-Module $ModuleName" -ForegroundColor Gray
    Write-Host "`nUsage Examples:" -ForegroundColor Yellow
    Write-Host "  New-BIDocumentation -InputPath 'C:\Reports\*.pbix' -OutputPath 'C:\Docs'" -ForegroundColor Gray
    Write-Host "  Process-BIFiles -Path 'C:\Reports' -Recursive" -ForegroundColor Gray
    Write-Host "`nDocumentation:" -ForegroundColor Yellow
    Write-Host "  Get-Help New-BIDocumentation -Full" -ForegroundColor Gray
    Write-Host "  https://github.com/Trailblazer-Analytics/bi-doc" -ForegroundColor Gray
}

# Main execution
try {
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    if (-not (Test-ModuleStructure)) {
        exit 1
    }
    
    if (-not (Test-ExistingVersion)) {
        exit 1
    }
    
    if (-not (Publish-ModuleToGallery)) {
        exit 1
    }
    
    Show-PostPublishInfo
    Write-Host "`n🎉 PowerShell module publishing completed successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Publishing failed: $_"
    exit 1
}