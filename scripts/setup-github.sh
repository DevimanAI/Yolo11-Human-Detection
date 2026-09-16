#!/usr/bin/env bash
# Publish Yolo11-Human-Detection to your GitHub account.
# Requires GitHub CLI (gh) with browser auth (works with 2FA).
#
# Usage (from project root):
#   ./scripts/setup-github.sh
#
# Or with a target directory:
#   ./scripts/setup-github.sh --target-dir ~/source/repos/Yolo11-Human-Detection

set -euo pipefail

REPO_NAME="Yolo11-Human-Detection"
TARGET_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_PATH="${SCRIPT_DIR}/yolo11-human-detection.bundle"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)
      TARGET_DIR="$2"
      shift 2
      ;;
    --repo-name)
      REPO_NAME="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--target-dir PATH] [--repo-name NAME]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

info()  { printf '\033[36m%s\033[0m\n' "$*"; }
ok()    { printf '\033[32m%s\033[0m\n' "$*"; }
warn()  { printf '\033[33m%s\033[0m\n' "$*"; }

# --- GitHub CLI ---
if ! command -v gh >/dev/null 2>&1; then
  warn "GitHub CLI (gh) is not installed."
  echo
  echo "Install gh, then re-run this script:"
  echo "  https://cli.github.com/"
  echo
  echo "After install, authenticate (browser flow, works with 2FA):"
  echo "  gh auth login"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  warn "You are not logged in to GitHub."
  echo
  echo "Run this first (choose GitHub.com, HTTPS, login via browser):"
  echo "  gh auth login"
  echo
  echo "Then re-run:"
  echo "  ./scripts/setup-github.sh"
  exit 1
fi

# --- Resolve working directory ---
PROJECT_ROOT=""
if [[ -d .git ]]; then
  PROJECT_ROOT="$(pwd)"
elif [[ -n "$TARGET_DIR" && -d "${TARGET_DIR}/.git" ]]; then
  PROJECT_ROOT="$(cd "$TARGET_DIR" && pwd)"
elif [[ -f "$BUNDLE_PATH" ]]; then
  if [[ -z "$TARGET_DIR" ]]; then
    TARGET_DIR="$(pwd)/${REPO_NAME}"
  fi
  if [[ -d "${TARGET_DIR}/.git" ]]; then
    info "Git repo already exists at ${TARGET_DIR}"
    PROJECT_ROOT="$(cd "$TARGET_DIR" && pwd)"
  else
    info "Not in a git repo — restoring from bundle..."
    echo "  Bundle: ${BUNDLE_PATH}"
    echo "  Target: ${TARGET_DIR}"
    mkdir -p "$(dirname "$TARGET_DIR")"
    git clone "$BUNDLE_PATH" "$TARGET_DIR"
    PROJECT_ROOT="$(cd "$TARGET_DIR" && pwd)"
  fi
else
  warn "Not in a git repository and bundle not found."
  echo
  echo "Expected bundle at:"
  echo "  ${BUNDLE_PATH}"
  echo
  echo "Either clone/extract the project so .git exists, or place"
  echo "yolo11-human-detection.bundle in scripts/ and re-run."
  exit 1
fi

cd "$PROJECT_ROOT"
info "Project root: ${PROJECT_ROOT}"

# --- Create GitHub repo and push ---
if git remote get-url github >/dev/null 2>&1; then
  url="$(git remote get-url github)"
  info "Remote 'github' already configured: ${url}"
  info "Pushing all branches and tags..."
  git push github --all
  git push github --tags 2>/dev/null || true
  ok "Push complete."
  exit 0
fi

info "Creating private GitHub repo '${REPO_NAME}' and pushing..."
if gh repo create "$REPO_NAME" --private --source . --remote github --push; then
  ok "Done! Repository published to GitHub."
  gh repo view --json url -q .url 2>/dev/null || true
else
  warn "gh repo create failed. If the repo already exists on GitHub, add the remote manually:"
  user="$(gh api user -q .login)"
  echo "  git remote add github https://github.com/${user}/${REPO_NAME}.git"
  echo "  git push -u github --all"
  echo "  git push github --tags"
  exit 1
fi
