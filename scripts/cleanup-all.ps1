# Remove all project-local dependencies and downloads (keeps source code + docs).
# Usage: .\scripts\cleanup-all.ps1
# Add -Force to skip confirmation.

param([switch]$Force)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$Targets = @(
    ".venv",
    ".cache",
    "data\raw",
    "data\datasets",
    "runs",
    ".deepface",
    "deepface_weights",
    "yolo11n.pt",
    "configs\.person_crowdhuman.generated.yaml"
)

Write-Host "This deletes local Python env, datasets, training runs, and caches under:"
Write-Host "  $ProjectRoot"
Write-Host ""
foreach ($t in $Targets) {
    $p = Join-Path $ProjectRoot $t
    if (Test-Path $p) { Write-Host "  - $t" }
}

if (-not $Force) {
    $answer = Read-Host "Continue? (y/N)"
    if ($answer -notmatch '^[yY]') {
        Write-Host "Cancelled."
        exit 0
    }
}

foreach ($t in $Targets) {
    $p = Join-Path $ProjectRoot $t
    if (Test-Path $p) {
        Remove-Item -Recurse -Force $p
        Write-Host "Removed $t"
    }
}

Write-Host ""
Write-Host "Done. Re-run .\scripts\setup-train.ps1 to train again." -ForegroundColor Green
