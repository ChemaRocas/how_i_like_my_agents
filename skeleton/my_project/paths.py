"""
Every location the project uses, resolved once, plus the one way to read a secret.

Import this module instead of building paths by hand:

    from my_project import paths

    source = paths.DATA_DIR / "rubric.xlsx"
    api_key = paths.require_env("EXAMPLE_API_KEY")

Why one module: if each script finds the project root on its own (counting ".." levels,
or a hardcoded "/Users/..." path), the folder layout can never change and the code breaks
on anyone else's computer. Here the root is found once, from this file's own location.

Need a new location? Add it below, under DATA_DIR (committed inputs) or OUTPUT_DIR (things
a run produces), and be deliberate about which: OUTPUT_DIR is git-ignored, DATA_DIR is not.
Machine-specific locations (a synced Drive folder, say) belong in .env, not here.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# my_project/paths.py -> the project root is one level up from this folder.
ROOT = Path(__file__).resolve().parent.parent

# Inputs the code is built from: templates, reference tables, rubrics. Committed.
DATA_DIR = ROOT / "data"

# Everything a run produces or downloads. Git-ignored: it can contain personal data.
OUTPUT_DIR = ROOT / "output"

# .env holds the real keys (git-ignored); .env.example lists their names.
ENV_FILE = ROOT / ".env"
load_dotenv(ENV_FILE)


def output_dir(*parts):
    """A folder under OUTPUT_DIR, created if missing. Use for anything a run writes."""
    path = OUTPUT_DIR.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


def require_env(name):
    """The value of a key from .env (or the environment); exits with a clear message if unset.

    A missing key stops the run here, with instructions, instead of failing later with a
    confusing error from whatever service the key was for.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(
            f"Missing {name}. Add it to {ENV_FILE} (copy .env.example to .env if it doesn't "
            "exist yet) and run again."
        )
    return value
