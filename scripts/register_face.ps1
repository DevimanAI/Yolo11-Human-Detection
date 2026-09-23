# Create a folder for your face photos under data/known_faces/
# Usage: .\scripts\register_face.ps1 -Name "Iman"

param(
    [Parameter(Mandatory = $true)]
    [string]$Name
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FaceDir = Join-Path $ProjectRoot "data\known_faces\$Name"

New-Item -ItemType Directory -Force -Path $FaceDir | Out-Null

Write-Host "Created: $FaceDir" -ForegroundColor Green
Write-Host ""
Write-Host "Next:"
Write-Host "  1. Copy 2-3 front-facing photos (jpg/png) into that folder"
Write-Host "  2. .\.venv\Scripts\python.exe -m pip install -r requirements-face.txt"
Write-Host "  3. .\.venv\Scripts\python.exe scripts\build_face_gallery.py --build"
Write-Host "  4. .\.venv\Scripts\python.exe run.py"
Write-Host ""
Write-Host "See docs/face-recognition.md"
