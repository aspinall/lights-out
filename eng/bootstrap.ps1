[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'RepoEnvironment.ps1')
$repoEnvironment = Set-LightsOutRepoEnvironment
$globalJsonPath = Join-Path $repoEnvironment.RepoRoot 'global.json'
$sdkVersion = (Get-Content -LiteralPath $globalJsonPath -Raw | ConvertFrom-Json).sdk.version

$installedVersion = $null
if (Test-Path -LiteralPath $repoEnvironment.DotNetExecutable) {
    $installedVersion = & $repoEnvironment.DotNetExecutable --version 2>$null
}

if ($installedVersion -ne $sdkVersion) {
    $installerPath = Join-Path $repoEnvironment.ToolsRoot 'cache\dotnet-install.ps1'
    if (-not (Test-Path -LiteralPath $installerPath)) {
        Write-Host 'Downloading the official .NET non-admin installer...'
        Invoke-WebRequest -UseBasicParsing -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $installerPath
    }

    Write-Host "Installing .NET SDK $sdkVersion into $($repoEnvironment.DotNetRoot)..."
    & $installerPath `
        -Version $sdkVersion `
        -Architecture 'x64' `
        -InstallDir $repoEnvironment.DotNetRoot `
        -NoPath

    if (-not $?) {
        throw 'The .NET installer did not complete successfully.'
    }
}

$actualVersion = & $repoEnvironment.DotNetExecutable --version
if ($actualVersion -ne $sdkVersion) {
    throw "Expected .NET SDK $sdkVersion but the repo-local host selected $actualVersion."
}

Write-Host "Repo-local .NET SDK $actualVersion is ready."
Write-Host "Enter an isolated development shell with:"
Write-Host '  powershell -NoProfile -NoExit -ExecutionPolicy Bypass -File eng/shell.ps1'
