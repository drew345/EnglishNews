param([switch]$Check)
$ErrorActionPreference = 'Stop'
$devRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$newsRoot = Join-Path $devRoot 'korean-news'
$labRoot = Join-Path $devRoot 'KoreanLessonVideoLab'
$python = Join-Path $newsRoot '.venv/Scripts/python.exe'
foreach ($root in @($newsRoot, $labRoot)) {
    if (-not (Test-Path -LiteralPath (Join-Path $root '.git') -PathType Leaf)) {
        throw "Expected a linked development worktree: $root"
    }
    $branch = git -C $root branch --show-current
    if ($branch -ne 'codex/english-news-prototype') { throw "Unexpected branch in $root`: $branch" }
}
if (-not (Test-Path -LiteralPath $python)) { throw 'Development Python is missing.' }
if ($Check) {
    Write-Output "Development API: $newsRoot (port 8010)"
    Write-Output "Development Video Lab: $labRoot"
    Write-Output 'API only; no cleanup workers, staging workers, renderer watchers or upload handoff.'
    exit 0
}
$saved = @{}
foreach ($name in @('PORT','VIDEO_LAB_PROJECT_ROOT','OUTPUT_CLEANUP_ON_RUN')) {
    $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
try {
    $env:PORT = '8010'
    $env:VIDEO_LAB_PROJECT_ROOT = $labRoot
    $env:OUTPUT_CLEANUP_ON_RUN = '0'
    Push-Location $newsRoot
    try { & $python (Join-Path $newsRoot 'scripts/run_api.py') }
    finally { Pop-Location }
} finally {
    foreach ($name in $saved.Keys) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
}
