# Project-local paths — keeps downloads/caches inside the repo folder.
# Dot-source from other scripts:  . (Join-Path $PSScriptRoot "project_env.ps1")
#
# Delete the whole repo folder after your defense to remove Python, datasets,
# weights, and pip caches (see scripts/cleanup-all.ps1).

param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

function Set-ProjectEnvironment {
    param([string]$Root)

    $cache = Join-Path $Root ".cache"
    $dirs = @(
        $cache,
        (Join-Path $cache "pip"),
        (Join-Path $cache "torch"),
        (Join-Path $cache "ultralytics"),
        (Join-Path $cache "ultralytics\weights"),
        (Join-Path $cache "huggingface"),
        (Join-Path $Root ".deepface"),
        (Join-Path $Root ".deepface\weights"),
        (Join-Path $Root "data\raw"),
        (Join-Path $Root "data\datasets"),
        (Join-Path $Root "runs"),
        (Join-Path $Root ".kaggle")
    )
    foreach ($d in $dirs) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }

    $env:PIP_CACHE_DIR = Join-Path $cache "pip"
    $env:TORCH_HOME = Join-Path $cache "torch"
    $env:HF_HOME = Join-Path $cache "huggingface"
    $env:TRANSFORMERS_CACHE = Join-Path $cache "huggingface"
    $env:KAGGLE_CONFIG_DIR = Join-Path $Root ".kaggle"
    $env:ULTRALYTICS_CONFIG_DIR = Join-Path $cache "ultralytics"
    $env:TEMP = Join-Path $cache "tmp"
    $env:TMP = $env:TEMP
    New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null

    $env:DEEPFACE_HOME = $Root

    $accessTokenFile = Join-Path $Root ".kaggle\access_token"
    if (-not $env:KAGGLE_API_TOKEN -and (Test-Path $accessTokenFile)) {
        $env:KAGGLE_API_TOKEN = (Get-Content $accessTokenFile -Raw).Trim()
    }
}

Set-ProjectEnvironment -Root $ProjectRoot
