param(
    [Parameter(Mandatory=$true)][string]$PreparedRun,
    [Parameter(Mandatory=$true)][string]$StagedRun,
    [Parameter(Mandatory=$true)][string]$VideoLab,
    [string]$EnvFile,
    [switch]$ReviewedText
)
$ErrorActionPreference = 'Stop'
if (-not $ReviewedText) { throw 'Review the prepared written lesson before using -ReviewedText for media generation.' }
$englishRoot = Split-Path $PSScriptRoot -Parent
$pythonExe = Join-Path $englishRoot '.venv/Scripts/python.exe'
$videoRoot = (Resolve-Path -LiteralPath $VideoLab).Path
$preparedPath = (Resolve-Path -LiteralPath $PreparedRun).Path
$stagedPath = (Resolve-Path -LiteralPath $StagedRun).Path
$arguments = @('-X', 'utf8', '-m', 'english_news.workflow', '--prepared-run', $preparedPath,
    '--staged-run', $stagedPath, '--reviewed-text')
if ($EnvFile) { $arguments += @('--env-file', (Resolve-Path -LiteralPath $EnvFile).Path) }
$savedLab = $env:ENGLISH_NEWS_VIDEO_LAB
$savedPython = $env:ENGLISH_NEWS_VIDEO_PYTHON
Push-Location $englishRoot
try {
    $env:ENGLISH_NEWS_VIDEO_LAB = $videoRoot
    $env:ENGLISH_NEWS_VIDEO_PYTHON = Join-Path $videoRoot '.venv/Scripts/python.exe'
    & $pythonExe @arguments
    if ($LASTEXITCODE -ne 0) { throw 'English build failed. Fix the reported problem, then rerun this same command to resume.' }
} finally {
    $env:ENGLISH_NEWS_VIDEO_LAB = $savedLab
    $env:ENGLISH_NEWS_VIDEO_PYTHON = $savedPython
    Pop-Location
}
