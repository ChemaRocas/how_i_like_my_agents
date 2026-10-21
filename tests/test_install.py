"""
global/install.py: what it writes, what it backs up, what it retires, and that a test
install (--home) never touches anything outside the test folder.
"""

from conftest import INSTALL, REPO, run_script


def install(home, *args, env=None):
    result = run_script(INSTALL, "--home", home, *args, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_every_instruction_is_installed_for_both_agents(tmp_path, sources):
    install(tmp_path)
    claude_index = (tmp_path / ".claude" / "CLAUDE.md").read_text()
    codex = (tmp_path / ".codex" / "AGENTS.md").read_text()
    for folder, name in sources:
        source = (REPO / "global" / folder / f"{name}.md").read_text()
        copy = tmp_path / ".claude" / "how_i_like_my_agents" / folder / f"{name}.md"
        assert copy.read_text() == source
        assert f"@~/.claude/how_i_like_my_agents/{folder}/{name}.md" in claude_index
        assert source.strip() in codex


def test_nothing_is_installed_into_claudes_auto_loaded_rules_folder(tmp_path):
    """Claude Code can load ~/.claude/rules/ by itself; a copy there would load twice."""
    install(tmp_path)
    assert not (tmp_path / ".claude" / "rules").exists()


def skill_folders():
    return sorted(path.parent for path in (REPO / "global" / "skills").glob("*/SKILL.md"))


def files_in(folder):
    return [p for p in folder.rglob("*") if p.is_file() and not p.name.startswith(".")]


def test_a_second_run_changes_nothing(tmp_path, sources):
    install(tmp_path)
    second = install(tmp_path)
    # Every instruction, CLAUDE.md and AGENTS.md, and for each of the two agents every
    # skill file plus its ownership marker.
    skill_files = sum(len(files_in(folder)) + 1 for folder in skill_folders())
    expected_files = len(sources) + 2 + 2 * skill_files
    assert second.count("unchanged") == expected_files
    assert "created" not in second and "updated" not in second and "retired" not in second


def test_a_dry_run_writes_nothing(tmp_path):
    install(tmp_path, "--dry-run")
    assert list(tmp_path.iterdir()) == []


def test_an_existing_different_file_is_backed_up_not_lost(tmp_path):
    codex = tmp_path / ".codex" / "AGENTS.md"
    codex.parent.mkdir()
    codex.write_text("my old instructions")
    install(tmp_path)
    backups = list(codex.parent.glob("AGENTS.md.backup-*"))
    assert [b.read_text() for b in backups] == ["my old instructions"]


def test_old_copies_of_our_rules_in_the_auto_loaded_folder_are_retired(tmp_path, sources):
    """Left by an earlier manual setup: they would load twice next to the new copies."""
    rules = tmp_path / ".claude" / "rules"
    rules.mkdir(parents=True)
    _, name = sources[0]
    (rules / f"{name}.md").write_text("an old version")
    (rules / "a-rule-of-my-own.md").write_text("mine")
    install(tmp_path)
    assert not (rules / f"{name}.md").exists()
    assert len(list(rules.glob(f"{name}.md.backup-*"))) == 1
    assert (rules / "a-rule-of-my-own.md").read_text() == "mine"


def test_an_instruction_removed_from_the_repo_is_retired_from_claude(tmp_path):
    """Otherwise Claude would keep following it while Codex no longer gets it."""
    install(tmp_path)
    stale = tmp_path / ".claude" / "how_i_like_my_agents" / "rules" / "a-deleted-rule.md"
    stale.write_text("no longer in the repo")
    install(tmp_path)
    assert not stale.exists()
    assert len(list(stale.parent.glob("a-deleted-rule.md.backup-*"))) == 1


LOCAL_MARKER = "<!-- local: kept by install.py -->"


def test_codex_instructions_below_the_local_line_survive_every_install(tmp_path):
    """That's the only place for computer-only instructions in Codex's single file."""
    install(tmp_path)
    codex = tmp_path / ".codex" / "AGENTS.md"
    codex.write_text(codex.read_text() + "\nUse the company VPN for internal APIs.\n")
    install(tmp_path)
    text = codex.read_text()
    assert text.count(LOCAL_MARKER) == 1
    assert text.split(LOCAL_MARKER, 1)[1].strip().endswith("Use the company VPN for internal APIs.")
    assert "unchanged" in install(tmp_path)  # and keeping it doesn't count as a change


def test_codex_file_lists_rule_a_before_rule_b(tmp_path):
    install(tmp_path)
    text = (tmp_path / ".codex" / "AGENTS.md").read_text()
    assert text.index("# Rule A") < text.index("# Rule B")


CLAUDE_SKILLS = (".claude", "skills")
CODEX_SKILLS = (".agents", "skills")


def test_every_skill_is_installed_for_both_agents_with_its_marker(tmp_path):
    install(tmp_path)
    assert skill_folders(), "global/skills/ has no skill to test with"
    for folder in skill_folders():
        for root in (tmp_path.joinpath(*CLAUDE_SKILLS), tmp_path.joinpath(*CODEX_SKILLS)):
            installed = root / folder.name
            for source in files_in(folder):
                assert (installed / source.relative_to(folder)).read_text() == source.read_text()
            assert (installed / ".installed-by-how_i_like_my_agents").is_file()


def test_a_skill_removed_from_the_repo_is_retired_outside_the_skills_folder(tmp_path):
    """Moved, not deleted, and to a folder no agent loads skills from."""
    install(tmp_path)
    for parts in (CLAUDE_SKILLS, CODEX_SKILLS):
        old = tmp_path.joinpath(*parts) / "an-old-skill"
        old.mkdir()
        (old / "SKILL.md").write_text("---\nname: an-old-skill\n---\n")
        (old / ".installed-by-how_i_like_my_agents").write_text("")
    install(tmp_path)
    for parts in (CLAUDE_SKILLS, CODEX_SKILLS):
        root = tmp_path.joinpath(*parts)
        assert not (root / "an-old-skill").exists()
        assert not list(root.glob("an-old-skill*"))
    kept = [p for p in tmp_path.rglob("an-old-skill.backup-*/SKILL.md")]
    assert len(kept) == 2


def test_a_skill_that_isnt_ours_is_left_alone(tmp_path):
    """No marker means someone else installed it: never touched."""
    theirs = tmp_path.joinpath(*CODEX_SKILLS) / "someone-elses-skill"
    theirs.mkdir(parents=True)
    (theirs / "SKILL.md").write_text("theirs")
    install(tmp_path)
    assert (theirs / "SKILL.md").read_text() == "theirs"


def test_a_test_install_ignores_codex_home(tmp_path):
    """CODEX_HOME points at the real Codex folder; --home must never write outside itself."""
    elsewhere = tmp_path / "real_codex"
    install(tmp_path / "home", env={"CODEX_HOME": str(elsewhere)})
    assert not elsewhere.exists()
    assert (tmp_path / "home" / ".codex" / "AGENTS.md").exists()
