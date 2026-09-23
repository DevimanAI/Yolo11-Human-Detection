# Download CrowdHuman dataset for person-detection fine-tuning.
# Requires Kaggle API credentials in %USERPROFILE%\.kaggle\kaggle.json
# or env vars KAGGLE_USERNAME / KAGGLE_KEY.
#
# Usage: .\scripts\download_dataset.ps1
# Optional: .\scripts\download_dataset.ps1 -DatasetSlug "nkk754/crowdhuman-crowd-human-detection-dataset"

param(
    [string]$DatasetSlug = "nkk754/crowdhuman-crowd-human-detection-dataset"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

function Write-Info([string]$Message) { Write-Host $Message -ForegroundColor Cyan }
function Write-Warn([string]$Message) { Write-Host $Message -ForegroundColor Yellow }
function Write-Ok([string]$Message) { Write-Host $Message -ForegroundColor Green }

$RawRoot = Join-Path $ProjectRoot "data\raw\crowdhuman"
New-Item -ItemType Directory -Force -Path $RawRoot | Out-Null

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Warn "Run .\scripts\setup-train.ps1 first."
    exit 1
}

$kaggle = Get-Command kaggle -ErrorAction SilentlyContinue
if (-not $kaggle) {
    Write-Info "Installing kaggle CLI in venv..."
    & $VenvPython -m pip install kaggle
    $kaggleCmd = Join-Path $ProjectRoot ".venv\Scripts\kaggle.exe"
} else {
    $kaggleCmd = "kaggle"
}

if (-not (Test-Path $kaggleCmd) -and $kaggle) {
    $kaggleCmd = "kaggle"
}

Write-Info "Downloading Kaggle dataset: $DatasetSlug"
Write-Info "Target: $RawRoot"

& $kaggleCmd datasets download -d $DatasetSlug -p $RawRoot --unzip
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Kaggle download failed."
    Write-Host ""
    Write-Host "Setup Kaggle credentials:"
    Write-Host "  1. Create API token at https://www.kaggle.com/settings"
    Write-Host "  2. Save kaggle.json to $env:USERPROFILE\.kaggle\kaggle.json"
    Write-Host "  3. Or set KAGGLE_USERNAME and KAGGLE_KEY in .env"
    Write-Host ""
    Write-Host "Manual alternative:"
    Write-Host "  - Download CrowdHuman from https://www.crowdhuman.org/"
    Write-Host "  - Extract Images + annotation_train.odgt + annotation_val.odgt into data\raw\crowdhuman\"
    Write-Host ""
    Write-Host "Smoke training without full dataset:"
    Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py --mini"
    exit 1
}

Write-Ok "Download complete."
Write-Host ""
Write-Host "Next (keeps 2000 train + 500 val only — not the full 5 GB in YOLO folder):"
Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py"
Write-Host ""
Write-Host "Optional — delete raw download after convert to free ~5 GB:"
Write-Host "  Remove-Item -Recurse -Force data\raw\crowdhuman"
