"""What crew assumes of moon, each case naming what assumes it. tests/suite runs every selected task afresh, for
--force and for a landing's gate, with `moon exec --cache off`, because moon installs a project's dependencies then and
skips them under its own --force ("Force updating cache, skipping dependency install", moon 2.6.1): deliverable-race's
landing on 2026-10-12, the first suite run in its worktree since crew's toolchain moved to proto, ran crew's tests
with no pytest in tests/.venv. The workspace here is crew's own toolchain, its .prototools and .moon/toolchains.yml,
with a project that has no dependencies, so uv needs nothing it has not got; moon checks for a network before it
installs, and skips the install on a host with none."""
import json
import os
import pathlib
import shutil
import subprocess

import pytest

CREW = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def workspace(tmp_path):
    ws = tmp_path / "ws"
    (ws / ".moon").mkdir(parents=True)
    (ws / "proj").mkdir()
    shutil.copy(CREW / ".prototools", ws / ".prototools")
    shutil.copy(CREW / ".moon" / "toolchains.yml", ws / ".moon" / "toolchains.yml")
    (ws / ".moon" / "workspace.yml").write_text("projects:\n  proj: 'proj'\ntelemetry: false\n")
    (ws / "proj" / "pyproject.toml").write_text('[project]\nname = "proj"\nversion = "0"\nrequires-python = ">=3.13"\ndependencies = []\n')
    (ws / "proj" / "moon.yml").write_text("tasks:\n  check:\n    command: 'python3 -c pass'\n")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(ws), *args], check=True, capture_output=True)
    return ws


def installed(ws, *flags):
    """The status moon's run report gives the project's dependency install, after `moon exec proj:check` with flags."""
    # moon reads MOON_* as options, and a moon task hands its own to this test: only crew's moon home goes through.
    env = {k: v for k, v in os.environ.items() if not k.startswith("MOON_") or k == "MOON_HOME"}
    r = subprocess.run(["moon", "exec", "proj:check", *flags], cwd=ws, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stdout + r.stderr
    report = json.loads((ws / ".moon" / "cache" / "runReport.json").read_text())
    return {a["label"].split("(")[0]: a["status"] for a in report["actions"]}["InstallDependencies"]


def test_moons_force_skips_installing_a_projects_dependencies(workspace):
    assert installed(workspace, "--force") == "skipped"
    assert not (workspace / "proj" / "uv.lock").exists()


def test_an_uncached_run_installs_them_and_still_runs_every_task_afresh(workspace):
    assert installed(workspace, "--cache", "off") == "passed"
    assert (workspace / "proj" / "uv.lock").exists()
