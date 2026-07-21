Set-StrictMode -Version Latest

function Set-LightsOutRepoEnvironment {
    [CmdletBinding()]
    param()

    $repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
    $toolsRoot = Join-Path $repoRoot '.tools'
    $dotnetRoot = Join-Path $toolsRoot 'dotnet'
    $requiredDirectories = @(
        $toolsRoot,
        $dotnetRoot,
        (Join-Path $toolsRoot 'cache'),
        (Join-Path $toolsRoot 'dotnet-home'),
        (Join-Path $toolsRoot 'nuget\packages'),
        (Join-Path $toolsRoot 'nuget\http-cache'),
        (Join-Path $toolsRoot 'temp')
    )

    foreach ($directory in $requiredDirectories) {
        [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    }

    $env:DOTNET_ROOT = $dotnetRoot
    $env:DOTNET_CLI_HOME = Join-Path $toolsRoot 'dotnet-home'
    $env:DOTNET_MULTILEVEL_LOOKUP = '0'
    $env:DOTNET_SKIP_FIRST_TIME_EXPERIENCE = '1'
    $env:DOTNET_NOLOGO = '1'
    $env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
    $env:NUGET_PACKAGES = Join-Path $toolsRoot 'nuget\packages'
    $env:NUGET_HTTP_CACHE_PATH = Join-Path $toolsRoot 'nuget\http-cache'
    $env:TEMP = Join-Path $toolsRoot 'temp'
    $env:TMP = $env:TEMP

    $pathEntries = $env:PATH -split [System.IO.Path]::PathSeparator
    if ($pathEntries -notcontains $dotnetRoot) {
        $env:PATH = $dotnetRoot + [System.IO.Path]::PathSeparator + $env:PATH
    }

    return [pscustomobject]@{
        RepoRoot = $repoRoot
        ToolsRoot = $toolsRoot
        DotNetRoot = $dotnetRoot
        DotNetExecutable = Join-Path $dotnetRoot 'dotnet.exe'
    }
}
