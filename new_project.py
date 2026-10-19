"""
Create a new project from skeleton/, ready to work in.

What it does, in order:
  1. Copies skeleton/ to a new folder.
  2. Renames the placeholder code folder (my_project) and every mention of it.
  3. Creates the git-ignored folders the skeleton can't carry: output/ and scratch/.
  4. Creates a .venv and installs the project with its test tools.
  5. Runs the tests once, so you start from a passing suite.
  6. Starts git (git init). It commits nothing: the first commit is yours.

Run it with:
  python3 new_project.py                              (asks for the name and the folder)
  python3 new_project.py sales_report                 (creates ./sales_report)
  python3 new_project.py sales_report --dest ~/Code   (creates ~/Code/sales_report)
  python3 new_project.py --help
"""

import argparse
import keyword
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKELETON = Path(__file__).resolve().parent / "skeleton"

# The placeholders the skeleton uses, in the three spellings Python projects need.
PLACEHOLDER_PACKAGE = "my_project"    # code folder and imports
PLACEHOLDER_DIST = "my-project"       # name in pyproject.toml
PLACEHOLDER_TITLE = "My Project"      # README heading

# Never copied from the skeleton, in case it was ever run or tested in place.
COPY_IGNORE = shutil.ignore_patterns(
    ".venv", "__pycache__", "*.pyc", "*.egg-info", ".pytest_cache", ".coverage",
    "output", "scratch", ".DS_Store",
)

GITIGNORED_FOLDERS = ["output", "scratch"]


def clean_path(raw):
    """Turn a pasted path into a Path: strips quotes and macOS drag-and-drop escapes."""
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        text = text[1:-1]
    elif sys.platform != "win32":
        text = re.sub(r"\\(.)", r"\1", text)
    return Path(text).expanduser()


def package_name(name):
    """The name as a Python package: lowercase, words joined by underscores.

    Returns None if it can't be one (starts with a digit, is a Python keyword, or has no
    letters), so the user can pick another name instead of getting a broken project.
    """
    package = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not package or package[0].isdigit() or keyword.iskeyword(package) or not package.isidentifier():
        return None
    return package


def ask(prompt, default=None):
    while True:
        answer = input(f"{prompt}{f' (Enter for {default})' if default else ''}: ").strip()
        if answer:
            return answer
        if default:
            return default


def venv_python(project):
    if sys.platform == "win32":
        return project / ".venv" / "Scripts" / "python.exe"
    return project / ".venv" / "bin" / "python"


def replace_placeholders(project, package, title):
    """Rename the code folder and every placeholder in the project's text files."""
    (project / PLACEHOLDER_PACKAGE).rename(project / package)
    dist = package.replace("_", "-")
    changed = []
    for path in sorted(project.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # not a text file
        new = (
            text.replace(PLACEHOLDER_TITLE, title)
            .replace(PLACEHOLDER_DIST, dist)
            .replace(PLACEHOLDER_PACKAGE, package)
        )
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(path.relative_to(project))
    return changed


def run(step, command, cwd):
    """Run one setup step, showing its name. Returns True if it worked."""
    print(f"  {step} ... ", end="", flush=True)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        print("done")
        return True
    print("FAILED")
    output = (result.stdout + result.stderr).strip()
    print("    " + "\n    ".join(output.splitlines()[-15:]))
    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a new project from the skeleton. Run with no arguments to be asked.",
    )
    parser.add_argument("name", nargs="?", help="project name, e.g. sales_report")
    parser.add_argument("--dest", help="folder to create the project in (default: the current folder)")
    parser.add_argument(
        "--no-install", action="store_true",
        help="skip creating the .venv, installing and running the tests (e.g. when offline)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("=== New project ===\n")

    name = args.name or ask("Project name (e.g. sales_report)")
    package = package_name(name)
    if package is None:
        sys.exit(f"'{name}' can't be a Python project name: use letters first, then letters, "
                 "digits or underscores (e.g. sales_report_2026).")
    dest = clean_path(args.dest) if args.dest else (
        Path.cwd() if args.name else clean_path(ask("Create it in which folder", str(Path.cwd())))
    )
    project = dest.resolve() / package
    if project.exists():
        sys.exit(f"{project} already exists. Pick another name or folder; nothing was changed.")
    title = package.replace("_", " ").title()

    print(f"\nCreating {project}")
    shutil.copytree(SKELETON, project, ignore=COPY_IGNORE)
    replace_placeholders(project, package, title)
    for folder in GITIGNORED_FOLDERS:
        (project / folder).mkdir()
    print(f"  copied the skeleton; code folder is {package}/")

    problems = []
    if args.no_install:
        problems.append("skipped .venv, install and tests (--no-install)")
    else:
        if not run("creating .venv", [sys.executable, "-m", "venv", ".venv"], project):
            problems.append("creating the .venv failed")
        elif not run("installing the project and test tools",
                     [str(venv_python(project)), "-m", "pip", "install", "-e", ".[dev]"], project):
            problems.append("installing failed (are you online?)")
        elif not run("running the tests", [str(venv_python(project)), "-m", "pytest"], project):
            problems.append("some tests failed: check the output above")

    if shutil.which("git") is None:
        problems.append("git isn't installed, so git init was skipped")
    elif not run("starting git (git init, no commit)", ["git", "init", "-b", "main"], project):
        problems.append("git init failed")

    print("\n----- Summary -----")
    if problems:
        print("Created, with problems to look at:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("Created: the tests pass and git is ready. Nothing is committed yet.")
    print(f"""
Next:
  1. Fill in the TODOs in AGENTS.md and README.md (what the project is).
  2. Copy .env.example to .env and add the keys, when the project needs any.
  3. The first time an agent works here, it should set up its own command rules from
     AGENT_PERMISSIONS.md (it will ask you first).
  4. If this is a personal repo, set it up as described in
     global/general_instructions/personal-repos.md.

Project folder: {project}""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
