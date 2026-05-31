<#
.SYNOPSIS
    Install the project's git hooks into .git/hooks/.

.DESCRIPTION
    Safe to re-run; overwrites existing hooks of the same name.
    Hooks live in scripts/hooks/ (tracked by git) and are copied into
    .git/hooks/ (not tracked).
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$src = Join-Path $repoRoot 'scripts/hooks'
$dst = Join-Path $repoRoot '.git/hooks'
New-Item -ItemType Directory -Path $dst -Force | Out-Null

Get-ChildItem -LiteralPath $src -File | ForEach-Object {
    $target = Join-Path $dst $_.Name
    Copy-Item -LiteralPath $_.FullName -Destination $target -Force
    # Git on Windows respects the shebang; no chmod needed, but make sure
    # the file is not blocked by Zone.Identifier when downloaded.
    Unblock-File -LiteralPath $target -ErrorAction SilentlyContinue
    Write-Host "installed: $target"
}

Write-Host 'Done. Bypass any hook with: git <cmd> --no-verify'
