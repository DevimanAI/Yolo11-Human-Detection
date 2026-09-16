from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_IMPORTS = (
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
    ("ultralytics", "ultralytics"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
)


def venv_python() -> Path:
    if sys.platform == "win32":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def in_virtualenv() -> bool:
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def missing_packages() -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for module, package in REQUIRED_IMPORTS:
        try:
            __import__(module)
        except ImportError:
            missing.append((module, package))
    return missing


def abort_if_missing() -> None:
    missing = missing_packages()
    if not missing:
        return

    names = ", ".join(package for _, package in missing)
    venv = venv_python()
    print(f"ERROR: Missing Python packages: {names}", file=sys.stderr)
    print(file=sys.stderr)
    print("Install into a project virtual environment.", file=sys.stderr)
    print(
        "Do not pip-install into Microsoft Store Python - that path is too long",
        file=sys.stderr,
    )
    print("for PyTorch on Windows (WinError 206) and leaves ultralytics missing.", file=sys.stderr)
    print(file=sys.stderr)
    if sys.platform == "win32":
        print("  .\\scripts\\setup.ps1", file=sys.stderr)
        print("  .\\.venv\\Scripts\\python.exe scripts\\smoke_test.py", file=sys.stderr)
        print("  .\\.venv\\Scripts\\python.exe run.py", file=sys.stderr)
        if venv.exists() and Path(sys.executable).resolve() != venv.resolve():
            print(file=sys.stderr)
            print(f"A venv already exists at {venv}", file=sys.stderr)
            print("This process is using a different Python. Run the venv commands above.", file=sys.stderr)
        elif "windowsapps" in sys.executable.lower() and not in_virtualenv():
            print(file=sys.stderr)
            print(f"Current interpreter: {sys.executable}", file=sys.stderr)
            print("That is Microsoft Store Python, not the project .venv.", file=sys.stderr)
    else:
        print("  python3 -m venv .venv", file=sys.stderr)
        print("  source .venv/bin/activate", file=sys.stderr)
        print("  python -m pip install -r requirements.txt", file=sys.stderr)
        print("  python scripts/smoke_test.py", file=sys.stderr)
        print("  python run.py", file=sys.stderr)
    raise SystemExit(1)
