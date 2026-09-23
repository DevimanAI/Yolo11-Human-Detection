# Create/reuse .venv and install training dependencies.
# Usage: .\scripts\setup-train.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot
. (Join-Path $PSScriptRoot "project_env.ps1") -ProjectRoot $ProjectRoot

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
    Write-Info "No .venv found - running setup.ps1 first..."
    & (Join-Path $ProjectRoot "scripts\setup.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Info "Installing training requirements..."
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements-train.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$hasNvidia = $false
try {
    $null = Get-Command nvidia-smi -ErrorAction Stop
    $smi = & nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) { $hasNvidia = $true }
} catch {
    $hasNvidia = $false
}

if ($hasNvidia) {
    Write-Info "NVIDIA GPU detected - installing CUDA PyTorch (driver only, not full CUDA Toolkit)."
    Write-Host "  The PyTorch wheel bundles CUDA runtime libraries."
    & $VenvPython -m pip uninstall -y torch torchvision torchaudio | Out-Null
    & $VenvPython -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Warn "No NVIDIA GPU detected - training will use CPU (much slower)."
}

Write-Info "Pinning Ultralytics / cache paths to this repo..."
& $VenvPython (Join-Path $ProjectRoot "scripts\configure_project.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Ok "Training environment ready."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\scripts\download_dataset.ps1"
Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py"
Write-Host "  .\scripts\train_yolo11.ps1"
Write-Host ""
Write-Host "Docs: docs\README.md (see train-yolo.md and face-recognition.md)"
