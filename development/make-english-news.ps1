param([Parameter(Mandatory=$true)][ValidatePattern('^\d{8}_\d{6}_[a-z0-9]+$')][string]$SourceRun)
$ErrorActionPreference = 'Stop'
$englishRoot = Split-Path $PSScriptRoot -Parent
$projectsRoot = 'C:/AI/Codex/Projects'
$pythonExe = Join-Path $englishRoot '.venv/Scripts/python.exe'
Push-Location $englishRoot
try {
    & $pythonExe -X utf8 -m english_news.workflow --source-run "$projectsRoot/korean-news/output/runs/$SourceRun" --staged-run "$projectsRoot/KoreanLessonVideoLab/inputs/korean-news/$SourceRun" --env-file "$projectsRoot/korean-news/.env"
    if ($LASTEXITCODE -ne 0) { throw 'English build failed. Fix the reported problem, then rerun this same command to resume.' }
} finally { Pop-Location }
