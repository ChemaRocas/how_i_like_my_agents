"""
new_project.py: a project comes out complete and renamed, and a name or folder that would
break it is refused before anything is created. Runs with --no-install, so no network.
"""

import shutil

import pytest

from conftest import NEW_PROJECT, REPO, SKELETON, run_script

PLACEHOLDERS = ["my_project", "my-project", "My Project"]


def new_project(name, dest, *args):
    return run_script(NEW_PROJECT, name, "--dest", dest, "--no-install", *args)


def test_a_new_project_is_complete_and_has_no_placeholders_left(tmp_path):
    result = new_project("sales_report", tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    project = tmp_path / "sales_report"
    assert (project / "sales_report" / "paths.py").is_file()
    assert not (project / "my_project").exists()
    for folder in ["output", "scratch"]:
        assert (project / folder).is_dir()
    leftovers = [
        path.relative_to(project)
        for path in project.rglob("*")
        if path.is_file() and ".git" not in path.parts
        and any(p in path.read_text(encoding="utf-8", errors="ignore") for p in PLACEHOLDERS)
    ]
    assert leftovers == []


def test_every_skeleton_file_reaches_the_new_project(tmp_path):
    new_project("sales_report", tmp_path)
    project = tmp_path / "sales_report"
    for path in SKELETON.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(SKELETON)
            renamed = type(relative)(*["sales_report" if p == "my_project" else p for p in relative.parts])
            assert (project / renamed).exists(), relative


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_git_is_started_but_nothing_is_committed(tmp_path):
    new_project("sales_report", tmp_path)
    project = tmp_path / "sales_report"
    assert (project / ".git").is_dir()
    log = run_git(project, "log")
    assert log.returncode != 0  # no commits yet


def run_git(folder, *args):
    import subprocess
    return subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True)


@pytest.mark.parametrize(
    "name",
    # The skeleton's folders (data, docs, tests...) and the two the script creates. Files
    # like README.md don't collide: the code folder would be "readme", a different name.
    sorted({p.name for p in SKELETON.iterdir() if p.is_dir() and not p.name.startswith(".")}
           | {"output", "scratch"}),
)
def test_a_name_that_collides_with_the_skeleton_is_refused(tmp_path, name):
    result = new_project(name, tmp_path)
    assert result.returncode != 0
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["json", "os", "pytest", "python_dotenv"])
def test_a_name_that_shadows_a_python_module_is_refused(tmp_path, name):
    result = new_project(name, tmp_path)
    assert result.returncode != 0
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["2026 sales", "class", "!!!"])
def test_a_name_that_cant_be_a_python_package_is_refused(tmp_path, name):
    result = new_project(name, tmp_path)
    assert result.returncode != 0
    assert list(tmp_path.iterdir()) == []


def test_spaces_and_capitals_become_a_valid_name(tmp_path):
    result = new_project("Customer Churn", tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "customer_churn" / "customer_churn").is_dir()


def test_a_folder_inside_the_template_repo_is_refused():
    result = new_project("demo_tool", REPO / "skeleton")
    assert result.returncode != 0
    assert not (REPO / "skeleton" / "demo_tool").exists()


def test_an_existing_project_is_never_overwritten(tmp_path):
    (tmp_path / "sales_report").mkdir()
    (tmp_path / "sales_report" / "keep.txt").write_text("mine")
    result = new_project("sales_report", tmp_path)
    assert result.returncode != 0
    assert (tmp_path / "sales_report" / "keep.txt").read_text() == "mine"
    assert len(list((tmp_path / "sales_report").iterdir())) == 1
