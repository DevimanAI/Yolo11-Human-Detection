# Create/reuse .venv and install training dependencies.
# Usage: .\scripts\setup-train.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

function Write-Info([string]$Message) { Write-Host $Message -ForegroundColor Cyan }
function Write-Ok([string]$Message) { Write-Host $Message -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host $Message -ForegroundColor Yellow }

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Warn "Python is not on PATH."
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Info "No .venv found — running setup.ps1 first..."
    & (Join-Path $ProjectRoot "scripts\setup.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Info "Installing training requirements..."
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements-train.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Info "Checking CUDA / GPU availability..."
& $VenvPython -c @"
import torch
cuda = torch.cuda.is_available()
print('CUDA available:', cuda)
if cuda:
    print('GPU:', torch.cuda.get_device_name(0))
else:
    print('Training will run on CPU (slower). Use --epochs 5 --max-images 200 for smoke training.')
"@

Write-Ok "Training environment ready."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\scripts\download_dataset.ps1"
Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py"
Write-Host "  .\scripts\train_yolo11.ps1"
Write-Host ""
Write-Host "Docs: docs\README.md  |  Train: docs\train-yolo.md  |  Face: docs\face-recognition.md"
