"""
Guards the project's structure: the folders, what git must ignore, and paths.py as the
only place locations are defined. These break quietly (a results file committed by
accident, a hardcoded path that only works on one computer), so they're tested.
"""

import re

import pytest

from my_project import paths

PACKAGE_DIR = paths.ROOT / "my_project"


def gitignore_lines():
    text = (paths.ROOT / ".gitignore").read_text(encoding="utf-8")
    return {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}


def test_paths_finds_the_project_root():
    assert (paths.ROOT / "pyproject.toml").is_file()
    assert paths.DATA_DIR.parent == paths.ROOT
    assert paths.OUTPUT_DIR.parent == paths.ROOT


@pytest.mark.parametrize("folder", ["my_project", "data", "docs", "tests"])
def test_the_committed_folders_exist(folder):
    assert (paths.ROOT / folder).is_dir()


@pytest.mark.parametrize("entry", ["output/", "scratch/", ".env", ".venv/"])
def test_private_folders_and_secrets_are_git_ignored(entry):
    """output/ and scratch/ can hold personal data, .env holds keys: none may be committed."""
    assert entry in gitignore_lines()


def test_env_example_stays_committed():
    """.env.* is ignored, so .env.example needs its own exception or it never reaches git."""
    assert "!.env.example" in gitignore_lines()


def test_output_dir_creates_the_folder_under_output(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "OUTPUT_DIR", tmp_path / "output")
    folder = paths.output_dir("results", "2026")
    assert folder.is_dir()
    assert folder == tmp_path / "output" / "results" / "2026"


def test_require_env_returns_the_value(monkeypatch):
    monkeypatch.setenv("SOME_TEST_KEY", "  abc123 ")
    assert paths.require_env("SOME_TEST_KEY") == "abc123"


@pytest.mark.parametrize("value", [None, "", "   "])
def test_a_missing_key_stops_with_a_message_naming_it(monkeypatch, value):
    """A blank key counts as missing: it would fail later, with a far less clear error."""
    if value is None:
        monkeypatch.delenv("SOME_TEST_KEY", raising=False)
    else:
        monkeypatch.setenv("SOME_TEST_KEY", value)
    with pytest.raises(SystemExit) as exit_info:
        paths.require_env("SOME_TEST_KEY")
    assert "SOME_TEST_KEY" in str(exit_info.value)


def test_no_module_builds_paths_by_hand():
    """Only paths.py may locate the project; anything else breaks when the layout changes
    or the project runs on another computer."""
    offenders = []
    for module in PACKAGE_DIR.rglob("*.py"):
        if module.name == "paths.py":
            continue
        text = module.read_text(encoding="utf-8")
        if "__file__" in text or re.search(r"""["'](/Users/|/home/|[A-Za-z]:\\)""", text):
            offenders.append(module.relative_to(paths.ROOT))
    assert offenders == [], f"use my_project.paths instead in: {offenders}"
