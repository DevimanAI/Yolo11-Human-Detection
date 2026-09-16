# Publish Yolo11-Human-Detection to your GitHub account.
# Requires GitHub CLI (gh) with browser auth (works with 2FA).
#
# Usage (from project root):
#   .\scripts\setup-github.ps1
#
# Or from any folder that contains scripts\yolo11-human-detection.bundle:
#   .\scripts\setup-github.ps1 -TargetDir C:\Users\Megam\source\repos\Yolo11-Human-Detection

param(
    [string]$TargetDir = "",
    [string]$RepoName = "Yolo11-Human-Detection"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundlePath = Join-Path $ScriptDir "yolo11-human-detection.bundle"

function Write-Info([string]$Message) { Write-Host $Message -ForegroundColor Cyan }
function Write-Ok([string]$Message) { Write-Host $Message -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host $Message -ForegroundColor Yellow }

# --- GitHub CLI ---
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Warn "GitHub CLI (gh) is not installed."
    Write-Host ""
    Write-Host "Install gh, then re-run this script:"
    Write-Host "  https://cli.github.com/"
    Write-Host ""
    Write-Host "After install, authenticate (browser flow, works with 2FA):"
    Write-Host "  gh auth login"
    exit 1
}

gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warn "You are not logged in to GitHub."
    Write-Host ""
    Write-Host "Run this first (choose GitHub.com, HTTPS, login via browser):"
    Write-Host "  gh auth login"
    Write-Host ""
    Write-Host "Then re-run:"
    Write-Host "  .\scripts\setup-github.ps1"
    exit 1
}

# --- Resolve working directory ---
$ProjectRoot = $null
if (Test-Path (Join-Path (Get-Location) ".git")) {
    $ProjectRoot = (Get-Location).Path
} elseif ($TargetDir -ne "" -and (Test-Path (Join-Path $TargetDir ".git"))) {
    $ProjectRoot = (Resolve-Path $TargetDir).Path
} elseif (Test-Path $BundlePath) {
    if ($TargetDir -eq "") {
        $TargetDir = Join-Path (Get-Location) $RepoName
    }
    if (Test-Path (Join-Path $TargetDir ".git")) {
        Write-Info "Git repo already exists at $TargetDir"
        $ProjectRoot = (Resolve-Path $TargetDir).Path
    } else {
        Write-Info "Not in a git repo — restoring from bundle..."
        Write-Host "  Bundle: $BundlePath"
        Write-Host "  Target: $TargetDir"
        New-Item -ItemType Directory -Force -Path (Split-Path $TargetDir -Parent) | Out-Null
        git clone $BundlePath $TargetDir
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $ProjectRoot = (Resolve-Path $TargetDir).Path
    }
} else {
    Write-Warn "Not in a git repository and bundle not found."
    Write-Host ""
    Write-Host "Expected bundle at:"
    Write-Host "  $BundlePath"
    Write-Host ""
    Write-Host "Either clone/extract the project so .git exists, or place"
    Write-Host "yolo11-human-detection.bundle in scripts\ and re-run."
    exit 1
}

Set-Location $ProjectRoot
Write-Info "Project root: $ProjectRoot"

# --- Create GitHub repo and push ---
$GithubRemote = git remote get-url github 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Info "Remote 'github' already configured: $GithubRemote"
    Write-Info "Pushing all branches and tags..."
    git push github --all
    git push github --tags 2>$null
    Write-Ok "Push complete."
    exit 0
}

Write-Info "Creating private GitHub repo '$RepoName' and pushing..."
gh repo create $RepoName --private --source . --remote github --push
if ($LASTEXITCODE -ne 0) {
    Write-Warn "gh repo create failed. If the repo already exists on GitHub, add the remote manually:"
    $user = (gh api user -q .login)
    Write-Host "  git remote add github https://github.com/$user/$RepoName.git"
    Write-Host "  git push -u github --all"
    Write-Host "  git push github --tags"
    exit $LASTEXITCODE
}

Write-Ok "Done! Repository published to GitHub."
$Url = gh repo view --json url -q .url 2>$null
if ($Url) { Write-Host "  $Url" }
