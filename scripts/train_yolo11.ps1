# Fine-tune YOLO11n on person dataset.
# Usage: .\scripts\train_yolo11.ps1
# Optional: .\scripts\train_yolo11.ps1 -Epochs 5 -Batch 4

param(
    [int]$Epochs = 0,
    [int]$Batch = 0,
    [int]$Imgsz = 0,
    [string]$Name = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot
. (Join-Path $PSScriptRoot "project_env.ps1") -ProjectRoot $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Run .\scripts\setup-train.ps1 first." -ForegroundColor Yellow
    exit 1
}

$Args = @("$ProjectRoot\scripts\train_yolo11.py")
if ($Epochs -gt 0) { $Args += @("--epochs", $Epochs) }
if ($Batch -gt 0) { $Args += @("--batch", $Batch) }
if ($Imgsz -gt 0) { $Args += @("--imgsz", $Imgsz) }
if ($Name -ne "") { $Args += @("--name", $Name) }

& $VenvPython @Args
exit $LASTEXITCODE
