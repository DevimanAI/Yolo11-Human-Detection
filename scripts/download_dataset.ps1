# Download CrowdHuman for person-detection fine-tuning.
# Default: annotations + 2500 images only (~1-2 GB), NOT the full 11 GB Kaggle archive.
#
# Usage: .\scripts\download_dataset.ps1
# Full archive: .\scripts\download_dataset.ps1 -Full

param(
    [string]$DatasetSlug = "leducnhuan/crowdhuman",
    [int]$MaxTrain = 2000,
    [int]$MaxVal = 500,
    [switch]$Full
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot
. (Join-Path $PSScriptRoot "project_env.ps1") -ProjectRoot $ProjectRoot

function Write-Info([string]$Message) { Write-Host $Message -ForegroundColor Cyan }
function Write-Warn([string]$Message) { Write-Host $Message -ForegroundColor Yellow }
function Write-Ok([string]$Message) { Write-Host $Message -ForegroundColor Green }

$KaggleDir = Join-Path $ProjectRoot ".kaggle"
$KaggleJson = Join-Path $KaggleDir "kaggle.json"
$AccessTokenFile = Join-Path $KaggleDir "access_token"
New-Item -ItemType Directory -Force -Path $KaggleDir | Out-Null

$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*KAGGLE_API_TOKEN\s*=\s*(.+)\s*$') { $env:KAGGLE_API_TOKEN = $Matches[1].Trim() }
        if ($_ -match '^\s*KAGGLE_USERNAME\s*=\s*(.+)\s*$') { $env:KAGGLE_USERNAME = $Matches[1].Trim() }
        if ($_ -match '^\s*KAGGLE_KEY\s*=\s*(.+)\s*$') { $env:KAGGLE_KEY = $Matches[1].Trim() }
    }
}

if ($env:KAGGLE_API_TOKEN -and -not (Test-Path $AccessTokenFile)) {
    Set-Content -Path $AccessTokenFile -Value $env:KAGGLE_API_TOKEN.Trim() -Encoding ASCII -NoNewline
    Write-Info "Created .kaggle\access_token from .env"
}

if (-not $env:KAGGLE_API_TOKEN -and (Test-Path $AccessTokenFile)) {
    $env:KAGGLE_API_TOKEN = (Get-Content $AccessTokenFile -Raw).Trim()
}

if ($env:KAGGLE_USERNAME -and $env:KAGGLE_KEY -and -not (Test-Path $KaggleJson)) {
    $payload = @{ username = $env:KAGGLE_USERNAME; key = $env:KAGGLE_KEY } | ConvertTo-Json -Compress
    Set-Content -Path $KaggleJson -Value $payload -Encoding UTF8
    Write-Info "Created .kaggle\kaggle.json from .env (legacy credentials)"
}

if (-not $env:KAGGLE_API_TOKEN -and -not (Test-Path $KaggleJson)) {
    $userToken = Join-Path $env:USERPROFILE ".kaggle\access_token"
    $userKaggle = Join-Path $env:USERPROFILE ".kaggle\kaggle.json"
    if (Test-Path $userToken) {
        Copy-Item $userToken $AccessTokenFile
        $env:KAGGLE_API_TOKEN = (Get-Content $AccessTokenFile -Raw).Trim()
        Write-Info "Copied access_token from $env:USERPROFILE\.kaggle\"
    } elseif (Test-Path $userKaggle) {
        Copy-Item $userKaggle $KaggleJson
        Write-Info "Copied kaggle.json from $env:USERPROFILE\.kaggle\"
    }
}

$env:KAGGLE_CONFIG_DIR = $KaggleDir

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Warn "Run .\scripts\setup-train.ps1 first."
    exit 1
}

Write-Info "Dataset: $DatasetSlug"
if ($Full) {
    Write-Warn "Full mode: downloading entire Kaggle archive (~11 GB)."
} else {
    Write-Info "Subset mode: annotations + $MaxTrain train + $MaxVal val images (not 11 GB)."
    Write-Host "  Accept license once: https://www.kaggle.com/datasets/leducnhuan/crowdhuman"
}

$Args = @(
    (Join-Path $ProjectRoot "scripts\download_crowdhuman_subset.py"),
    "--slug", $DatasetSlug,
    "--max-train", $MaxTrain,
    "--max-val", $MaxVal
)
if ($Full) { $Args += "--full" }

& $VenvPython @Args
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Download failed."
    Write-Host ""
    Write-Host "Setup Kaggle credentials (inside this repo):"
    Write-Host "  New token (KGAT_...): save to .kaggle\access_token"
    Write-Host "  Or set KAGGLE_API_TOKEN=... in .env"
    Write-Host ""
    Write-Host "If you see 403 Forbidden:"
    Write-Host "  - Open https://www.kaggle.com/datasets/leducnhuan/crowdhuman"
    Write-Host "  - Click Download once to accept the dataset license"
    Write-Host ""
    Write-Host "Smoke training without CrowdHuman:"
    Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py --mini"
    exit 1
}

Write-Ok "Download complete."
Write-Host ""
Write-Host "Next:"
Write-Host "  .\.venv\Scripts\python.exe scripts\convert_crowdhuman.py"
Write-Host ""
Write-Host "Optional: delete raw images after convert (keep annotations if re-converting):"
Write-Host "  Remove-Item -Recurse -Force data\raw\crowdhuman\Images, data\raw\crowdhuman\Images_val"
