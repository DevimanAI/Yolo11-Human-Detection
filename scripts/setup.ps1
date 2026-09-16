# Create a project venv and install core dependencies.
# Usage (from repo root or anywhere):
#   .\scripts\setup.ps1

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
    Write-Host "and check 'Add python.exe to PATH'. The 'py' launcher is optional."
    exit 1
}

Write-Info "Project root: $ProjectRoot"
Write-Info "Creating .venv with: python -m venv .venv"
python -m venv .venv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Warn "venv was created but .venv\Scripts\python.exe is missing."
    exit 1
}

Write-Info "Upgrading pip in the venv..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Info "Installing requirements.txt into the venv..."
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Info "Created .env from .env.example"
}

Write-Ok "Setup complete. Run smoke test and the server with the venv Python:"
Write-Host "  .\.venv\Scripts\python.exe scripts\smoke_test.py"
Write-Host "  .\.venv\Scripts\python.exe run.py"
Write-Host ""
Write-Host "Optional face recognition (heavy: TensorFlow + DeepFace):"
Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements-face.txt"
