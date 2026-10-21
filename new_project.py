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
import importlib.util
import json
import keyword
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

TEMPLATE_REPO = Path(__file__).resolve().parent
SKELETON = TEMPLATE_REPO / "skeleton"
PERSONAL_REPOS_GUIDE = TEMPLATE_REPO / "global" / "general_instructions" / "personal-repos.md"

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


def name_conflict(package):
    """Why this package name would break the new project, or None if it's safe.

    Checked before anything is created, so a bad name never leaves a half-made folder.
    """
    # The skeleton's own top-level folders and files (data, tests, docs...) plus the
    # git-ignored folders created later: the code folder would collide with one of them,
    # and output/ or scratch/ would also be ignored by git.
    reserved = {path.name.split(".")[0] for path in SKELETON.iterdir()} | set(GITIGNORED_FOLDERS)
    if package in reserved:
        return f"'{package}' is already a folder or file in every project"
    # The libraries every project installs (pytest, python-dotenv...), by their names in
    # the skeleton's pyproject.toml: they aren't necessarily installed here yet.
    if package in skeleton_dependency_names():
        return f"'{package}' is the name of a library every project installs, so imports would clash"
    # A name Python already knows (the standard library, or a library installed here,
    # like dotenv or pytest) would shadow it: imports would load the wrong code.
    if package in sys.stdlib_module_names or importlib.util.find_spec(package) is not None:
        return f"'{package}' is the name of an existing Python module, so imports would clash"
    return None


def skeleton_dependency_specs():
    """Every dependency in the skeleton's pyproject.toml, as written there ("pytest>=8.0")."""
    with open(SKELETON / "pyproject.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    return project.get("dependencies", []) + [
        spec for group in project.get("optional-dependencies", {}).values() for spec in group
    ]


def python_name(distribution):
    """A library's name the way it would appear as a folder name ("pytest-cov" -> "pytest_cov")."""
    return re.split(r"[\s<>=!~;\[]", distribution, maxsplit=1)[0].lower().replace("-", "_").replace(".", "_")


def skeleton_dependency_names():
    """The skeleton's direct dependencies, by Python name. Works offline."""
    return {python_name(spec) for spec in skeleton_dependency_specs()}


def installed_library_names():
    """Every library a new project's .venv will contain, hidden dependencies included.

    Asks pip what it would install (nothing is installed). A project named like one of
    these (say `iniconfig`, which pytest needs) would replace it and break the tools.
    Returns None when pip can't answer (offline), so the caller can say it couldn't check.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--dry-run", "--ignore-installed", "--quiet",
         "--report", "-", *skeleton_dependency_specs()],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return {python_name(item["metadata"]["name"]) for item in report.get("install", [])}


def required_python():
    """(major, minor) from the skeleton's requires-python, e.g. ">=3.12" -> (3, 12)."""
    with open(SKELETON / "pyproject.toml", "rb") as f:
        spec = tomllib.load(f)["project"]["requires-python"]
    match = re.search(r">=\s*(\d+)\.(\d+)", spec)
    return (int(match.group(1)), int(match.group(2))) if match else None


def inside(path, folder):
    """True if path is folder itself or anywhere inside it."""
    return path == folder or folder in path.parents


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

    # The project's tools need this Python; checked first so the failure isn't a
    # confusing pip error halfway through.
    needed = required_python()
    if needed and sys.version_info[:2] < needed:
        sys.exit(f"New projects need Python {needed[0]}.{needed[1]} or newer; this is "
                 f"{sys.version_info[0]}.{sys.version_info[1]}. Install a newer Python "
                 "and run this script with it. Nothing was changed.")

    name = args.name or ask("Project name (e.g. sales_report)")
    package = package_name(name)
    if package is None:
        sys.exit(f"'{name}' can't be a Python project name: use letters first, then letters, "
                 "digits or underscores (e.g. sales_report_2026).")
    conflict = name_conflict(package)
    if conflict:
        sys.exit(f"{conflict}. Pick another name; nothing was changed.")
    if not args.no_install:
        libraries = installed_library_names()
        if libraries is None:
            print("  (couldn't ask pip which libraries get installed; continuing, the tests will tell)")
        elif package in libraries:
            sys.exit(f"'{package}' is the name of a library every project installs, so imports "
                     "would clash. Pick another name; nothing was changed.")

    # Never inside this template repo: the project would end up in its git history.
    # Run from inside it, the default is the folder that contains it.
    default_dest = TEMPLATE_REPO.parent if inside(Path.cwd().resolve(), TEMPLATE_REPO) else Path.cwd()
    if args.dest:
        dest = clean_path(args.dest)
    elif args.name:
        dest = default_dest
    else:
        dest = clean_path(ask("Create it in which folder", str(default_dest)))
    dest = dest.resolve()
    if inside(dest, TEMPLATE_REPO):
        sys.exit(f"{dest} is inside the template repo; pick a folder outside {TEMPLATE_REPO}. "
                 "Nothing was changed.")
    project = dest / package
    if project.exists():
        sys.exit(f"{project} already exists. Pick another name or folder; nothing was changed.")
    title = package.replace("_", " ").title()

    print(f"\nCreating {project}")
    try:
        shutil.copytree(SKELETON, project, ignore=COPY_IGNORE)
        replace_placeholders(project, package, title)
        for folder in GITIGNORED_FOLDERS:
            (project / folder).mkdir()
    except Exception as exc:
        # The folder didn't exist before this run, so removing it loses nothing and
        # leaves no half-made project behind.
        shutil.rmtree(project, ignore_errors=True)
        sys.exit(f"Could not create the project ({exc}). Nothing was left behind.")
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
        # Last line of defence for name clashes: a library installed only inside the new
        # .venv (a dependency of a dependency) can't be seen by the checks done earlier.
        elif not run("checking no installed library uses the same name",
                     [str(venv_python(project)), "-c",
                      "import importlib.metadata as m, sys; "
                      f"owners = m.packages_distributions().get({package!r}, []); "
                      f"sys.exit(1 if [o for o in owners if o.lower().replace('-', '_') != {package!r}] else 0)"],
                     project):
            problems.append(f"'{package}' clashes with a library installed in the .venv: "
                            "delete this project and pick another name")
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
     {PERSONAL_REPOS_GUIDE}

Project folder: {project}""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
