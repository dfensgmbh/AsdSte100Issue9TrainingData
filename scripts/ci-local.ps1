<#
.SYNOPSIS
    Run the same checks as .github/workflows/ci.yml, locally.

.DESCRIPTION
    Mirrors the GitHub Actions CI pipeline so that "passes locally" also
    means "will pass in CI". Each step is announced, and the script aborts
    on the first failure (unless -ContinueOnError is given).

.PARAMETER Skip
    Comma-separated list of step names to skip. Names match the section
    headers below (case-insensitive).
    Example:  .\scripts\ci-local.ps1 -Skip pylint,mypy

.PARAMETER ContinueOnError
    Run every step even if some fail. The final exit code is non-zero if
    any step failed.

.EXAMPLE
    pwsh .\scripts\ci-local.ps1
    pwsh .\scripts\ci-local.ps1 -Skip black,pylint
    pwsh .\scripts\ci-local.ps1 -ContinueOnError
#>
[CmdletBinding()]
param(
    [string[]] $Skip = @(),
    [switch]   $ContinueOnError
)

$ErrorActionPreference = 'Stop'
$script:Failures = @()

function Invoke-Step {
    param(
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [scriptblock] $Action
    )

    # Allow either -Skip pylint,mypy or -Skip pylint -Skip mypy.
    $normalizedSkip = @($Skip | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($normalizedSkip -contains $Name) {
        Write-Host "`n=== [SKIP] $Name ===" -ForegroundColor DarkGray
        return
    }

    Write-Host "`n=== [RUN ] $Name ===" -ForegroundColor Cyan
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $Action
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            throw "exit code $LASTEXITCODE"
        }
        $sw.Stop()
        Write-Host ("=== [PASS] {0} ({1:N1}s) ===" -f $Name, $sw.Elapsed.TotalSeconds) -ForegroundColor Green
    }
    catch {
        $sw.Stop()
        Write-Host ("=== [FAIL] {0} ({1:N1}s): {2} ===" -f $Name, $sw.Elapsed.TotalSeconds, $_) -ForegroundColor Red
        $script:Failures += $Name
        if (-not $ContinueOnError) { exit 1 }
    }
}

Write-Host "Repository: $(Resolve-Path .)" -ForegroundColor Yellow
Write-Host "uv:         $(uv --version)"  -ForegroundColor Yellow

# Install / refresh deps - matches CI's `uv sync --extra dev --extra test`
Invoke-Step 'sync' {
    uv sync --extra dev --extra test
}

Invoke-Step 'pylint' {
    $files = git ls-files '*.py'
    uv run pylint @files
}

Invoke-Step 'flake8' {
    uv run flake8 src tests
}

Invoke-Step 'black' {
    uv run black --check .
}

Invoke-Step 'mypy' {
    uv run mypy src tests
}

Invoke-Step 'bandit' {
    uv run bandit -r src -ll
}

Invoke-Step 'pip-audit' {
    $req = Join-Path $env:TEMP "requirements-audit-$PID.txt"
    try {
        uv export --no-emit-project --no-hashes `
            --format requirements-txt `
            --output-file $req
        # Filter out the GitHub-hosted spaCy model wheel (same as CI).
        $kept = @()
        $skip = $false
        foreach ($line in Get-Content -LiteralPath $req) {
            if ($line -match '^en-core-web-sm ') { $skip = $true; continue }
            if ($skip -and $line -match '^(\s|#)') { continue }
            $skip = $false
            $kept += $line
        }
        Set-Content -LiteralPath $req -Value $kept -Encoding utf8
        uv run pip-audit --strict --requirement $req
    }
    finally {
        Remove-Item -LiteralPath $req -ErrorAction SilentlyContinue
    }
}

Invoke-Step 'tests' {
    uv run coverage run -m unittest discover -v -s tests -t . -p 'test_*.py'
    uv run coverage report -m
}

Invoke-Step 'build' {
    uv build
}

Write-Host ''
if ($script:Failures.Count -eq 0) {
    Write-Host '*** All checks passed ***' -ForegroundColor Green
    exit 0
} else {
    Write-Host ("*** {0} check(s) failed: {1} ***" -f $script:Failures.Count, ($script:Failures -join ', ')) -ForegroundColor Red
    exit 1
}
