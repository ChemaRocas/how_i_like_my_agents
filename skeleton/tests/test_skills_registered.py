"""
Every project skill in skills/ is registered where each agent looks for skills, and every
registration points at a real skill.

A skill in skills/ is invisible to an agent until it's linked from that agent's skills
folder, and registering it is a manual step that gets forgotten: a session once answered
a data question by guessing because the skill explaining the data wasn't registered.
These tests turn "remember to register it" into a failure you can't miss.

The agents' folders are read from the table in skills/README.md, so adding an agent there
is enough; nothing is listed twice.
"""

import re

import pytest

from my_project import paths

SKILLS = paths.ROOT / "skills"
# A table row like: | Claude Code | `.claude/skills/<skill-name>` | `../../skills/<skill-name>` |
REGISTRATION_ROW = re.compile(r"^\|[^|]+\|\s*`([^`]+)/<skill-name>`\s*\|", re.M)


def agent_skill_folders():
    """Each agent's project skills folder, from the table in skills/README.md."""
    readme = (SKILLS / "README.md").read_text(encoding="utf-8")
    return [paths.ROOT / folder for folder in REGISTRATION_ROW.findall(readme)]


def project_skills():
    """Every folder in skills/ that has a SKILL.md."""
    return sorted(path.parent for path in SKILLS.glob("*/SKILL.md"))


def test_the_readme_names_the_agent_folders():
    """Guards the parser: if the table changed shape, the checks below would check nothing."""
    assert len(agent_skill_folders()) >= 2


@pytest.mark.parametrize("skill", project_skills(), ids=lambda p: p.name)
def test_every_skill_is_registered_for_every_agent(skill):
    missing = []
    for folder in agent_skill_folders():
        link = folder / skill.name
        if not link.exists() or link.resolve() != skill.resolve():
            missing.append(str(link.relative_to(paths.ROOT)))
    assert missing == [], f"register {skill.name} (see skills/README.md): {missing}"


def test_every_registration_points_to_a_real_skill():
    """A skill renamed or deleted in skills/ leaves a link to nothing behind."""
    dead = [
        str(entry.relative_to(paths.ROOT))
        for folder in agent_skill_folders() if folder.is_dir()
        for entry in folder.iterdir()
        if entry.is_symlink() and not (entry.resolve() / "SKILL.md").is_file()
    ]
    assert dead == [], f"links to skills that no longer exist: {dead}"
