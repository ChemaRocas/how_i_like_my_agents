"""
Shared helpers for testing the template's scripts. Every test runs a script as a separate
process, the way I'd run it, against folders under pytest's tmp_path: never my real home
folder, never a real project.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "global" / "install.py"
NEW_PROJECT = REPO / "new_project.py"
SKELETON = REPO / "skeleton"
SOURCE_FOLDERS = ["rules", "general_instructions"]


def run_script(script, *args, env=None):
    """Run one of the template's scripts; returns the finished process (output as text)."""
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True, text=True, env={**os.environ, **(env or {})},
    )


@pytest.fixture
def sources():
    """(folder, name) for every instruction file in global/, the same set install.py reads."""
    return [
        (folder, path.stem)
        for folder in SOURCE_FOLDERS
        for path in sorted((REPO / "global" / folder).glob("*.md"))
    ]
