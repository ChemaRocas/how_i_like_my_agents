"""
The documentation's links point at files that exist, and every command the project
defines is listed in AGENTS.md.

Docs go stale silently: a page keeps naming a script after it's renamed, or links to a page
after it's deleted. Nothing fails, so nobody notices until someone follows a dead pointer.
These tests fail the moment that happens.

Which documents to check is derived, not listed: every Markdown file git would track
(committed, or new and not ignored). That keeps output/, scratch/, .venv/ and other
sessions' copies out by the project's own .gitignore, and picks up a new doc without
anyone editing this file.
"""

import re
import subprocess
import tomllib

import pytest

from my_project import paths

# [text](target): the target up to the first space or closing parenthesis.
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL = ("http://", "https://", "mailto:")
# Examples inside code blocks and `inline code` aren't real links.
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def ignored_folders():
    """Folder patterns from .gitignore (lines like `output/`), for when git can't answer."""
    lines = (paths.ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    return {line.strip().strip("/") for line in lines
            if line.strip().endswith("/") and "*" not in line and not line.startswith("#")}


def markdown_files():
    """Every .md file git would track; before `git init`, the same files found by walking
    the project and skipping the folders .gitignore names."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.md"],
        cwd=paths.ROOT, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return sorted(paths.ROOT / line for line in result.stdout.splitlines() if line)
    skip = ignored_folders() | {".git"}
    return sorted(
        path for path in paths.ROOT.rglob("*.md")
        if not skip.intersection(path.relative_to(paths.ROOT).parts[:-1])
    )


def links_in(doc):
    """(line number, target) for every local link in a Markdown file."""
    text = CODE.sub(lambda m: "\n" * m.group().count("\n"), doc.read_text(encoding="utf-8"))
    for number, line in enumerate(text.splitlines(), 1):
        for target in LINK.findall(line):
            if not target.startswith(EXTERNAL) and not target.startswith("#"):
                yield number, target.split("#", 1)[0]


def test_there_are_docs_to_check():
    """Guards the discovery itself: an empty list would make the next test pass vacuously."""
    assert paths.ROOT / "AGENTS.md" in markdown_files()


@pytest.mark.parametrize("doc", markdown_files(), ids=lambda p: str(p.relative_to(paths.ROOT)))
def test_every_link_points_to_a_file_that_exists(doc):
    broken = [
        f"line {number}: {target}"
        for number, target in links_in(doc)
        if not (doc.parent / target).exists()
    ]
    assert broken == [], f"dead links in {doc.relative_to(paths.ROOT)}"


def test_every_command_is_listed_in_agents_md():
    """Commands live in pyproject.toml; AGENTS.md is where agents and people look for them."""
    with open(paths.ROOT / "pyproject.toml", "rb") as f:
        commands = tomllib.load(f).get("project", {}).get("scripts", {})
    agents = (paths.ROOT / "AGENTS.md").read_text(encoding="utf-8")
    missing = [name for name in commands if name not in agents]
    assert missing == [], f"add these commands to AGENTS.md: {missing}"
