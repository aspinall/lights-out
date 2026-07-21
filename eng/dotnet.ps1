Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'RepoEnvironment.ps1')
$repoEnvironment = Set-LightsOutRepoEnvironment

if (-not (Test-Path -LiteralPath $repoEnvironment.DotNetExecutable)) {
    throw 'The repo-local SDK is missing. Run eng/bootstrap.ps1 first.'
}

& $repoEnvironment.DotNetExecutable @args
exit $LASTEXITCODE
