[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'RepoEnvironment.ps1')
$repoEnvironment = Set-LightsOutRepoEnvironment

if (-not (Test-Path -LiteralPath $repoEnvironment.DotNetExecutable)) {
    throw 'The repo-local SDK is missing. Run eng/bootstrap.ps1 first.'
}

Set-Location -LiteralPath $repoEnvironment.RepoRoot
Write-Host "Lights Out environment: $(& $repoEnvironment.DotNetExecutable --version)"
Write-Host "SDK: $($repoEnvironment.DotNetRoot)"
Write-Host "NuGet: $env:NUGET_PACKAGES"
