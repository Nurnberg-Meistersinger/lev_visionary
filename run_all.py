from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = ROOT_DIR / ".the_vis" / "Scripts" / ("python.exe" if os.name == "nt" else "python")
PYTHON = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)

# (name, path) pairs in the order they should be executed
PROJECTS = [
    ("project_a16z", ROOT_DIR / "project_a16z"),
    ("project_techcrunch_startup", ROOT_DIR / "project_techcrunch_startup"),
    ("project_techcrunch_venture", ROOT_DIR / "project_techcrunch_venture"),
    ("project_twitter", ROOT_DIR / "project_twitter"),
]


def run_project(name: str, folder: Path) -> bool:
    main_path = folder / "main.py"
    if not main_path.exists():
        print(f"[{name}] main.py not found at {main_path}")
        return False

    print(f"\n=== Running {name} with {PYTHON} ===")
    result = subprocess.run([str(PYTHON), str(main_path)], cwd=folder)

    if result.returncode != 0:
        print(f"[{name}] failed with exit code {result.returncode}")
        return False

    print(f"[{name}] completed successfully")
    return True


def main() -> None:
    print(f"Using interpreter: {PYTHON}")

    statuses = []
    for name, folder in PROJECTS:
        ok = run_project(name, folder)
        statuses.append((name, ok))

    print("\n=== Summary ===")
    for name, ok in statuses:
        state = "OK" if ok else "FAILED"
        print(f"{name}: {state}")


if __name__ == "__main__":
    main()
