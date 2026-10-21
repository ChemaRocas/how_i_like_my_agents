"""
The skeleton's AGENT_PERMISSIONS.md is the source; its .claude/settings.json is a copy.
If someone edits one and forgets the other, agents get different blocks than the ones
written down. Both lists are read from the files, never typed here.
"""

import json
import re

import pytest

from conftest import SKELETON

PERMISSIONS = (SKELETON / "AGENT_PERMISSIONS.md").read_text(encoding="utf-8")
SETTINGS = json.loads((SKELETON / ".claude" / "settings.json").read_text())["permissions"]

TABLES = {
    "deny": "Never run (hard block)",
    "ask": "Ask first, every time",
    "allow": "Allowed without asking (read-only or safe)",
}


def commands_in_table(title):
    """The commands in the first column of a table in AGENT_PERMISSIONS.md."""
    section = PERMISSIONS.split(f"## {title}", 1)[1].split("\n## ", 1)[0]
    commands = set()
    for row in re.findall(r"^\|(.+?)\|", section, re.M):
        for command in re.findall(r"`([^`]+)`", row):
            if command.startswith("-"):
                continue  # a flag mentioned in the explanation, like "even `-n`"
            commands.add(re.sub(r"\s*<[^>]+>$", "", command))
    return commands


def commands_in_settings(key):
    """The commands in one of settings.json's lists: "Bash(git add:*)" -> "git add"."""
    return {re.fullmatch(r"Bash\((.+?)(?::\*)?\)", rule).group(1) for rule in SETTINGS.get(key, [])}


@pytest.mark.parametrize("key", TABLES)
def test_claude_settings_match_agent_permissions(key):
    assert commands_in_settings(key) == commands_in_table(TABLES[key])


def test_every_table_lists_at_least_one_command():
    """Guards the parser itself: a renamed heading would make the comparison above vacuous."""
    for title in TABLES.values():
        assert commands_in_table(title)
