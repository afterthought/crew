"""What crew assumes of worktrunk's wt remove, each case naming what assumes it: plan.tidy removes a finished
worktree through the kit's own `wt remove --foreground --no-delete-branch --force --format json`, run with no input,
so the kit's remove hooks run and the branch is left to crew (plan.9, plan.10)."""
import json
import os
import subprocess
import time

import pytest


@pytest.fixture
def kit(repo, tmp_path, monkeypatch):
    """A kit's main checkout and one place, unit/x at places/x, made after the kit's wt.toml (hooks) is committed."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "home" / ".config"))
    for k in [k for k in os.environ if k.startswith("WORKTRUNK_")]:
        monkeypatch.delenv(k)
    log = tmp_path / "hooks.log"

    def make(hooks=""):
        repo.commit("chore: start", {"README.md": "r\n", ".config/wt.toml": hooks.replace("LOG", str(log))})
        place = tmp_path / "places" / "x"
        repo.git("worktree", "add", "-q", "-b", "unit/x", str(place))
        return place
    make.log = log
    return make


def remove(repo, place):
    return subprocess.run(["wt", "-C", str(repo.path), "remove", str(place), "--foreground", "--no-delete-branch", "--force",
                           "--format", "json"], capture_output=True, text=True, stdin=subprocess.DEVNULL)


HOOKS = '''[pre-remove]
teardown = "echo pre {{ worktree_name }} $(test -e README.md && echo present || echo absent) >> LOG; test ! -e $HOME/fail-{{ worktree_name }}"

[post-remove]
after = "echo post {{ worktree_name }} $(test -e {{ worktree_path }} && echo present || echo absent) >> LOG"
'''


def test_remove_hooks_not_approved_refuse_saying_so_and_run_nothing(repo, kit):
    """plan.wt_refused: hooks waiting for approval refuse with no input to answer them, saying it can't prompt."""
    place = kit(HOOKS)
    r = remove(repo, place)
    assert r.returncode != 0 and "Cannot prompt for approval" in r.stderr
    assert place.is_dir() and not kit.log.exists()


def test_approved_hooks_run_before_the_files_go_and_after_and_the_branch_is_left_to_crew(repo, kit, tmp_path):
    """plan.tidy and plan.wt_left_branch: pre-remove runs with the place's files there, post-remove once they are gone,
    and the JSON answer names the worktree with its branch not attempted."""
    place = kit(HOOKS)
    subprocess.run(["wt", "-C", str(repo.path), "config", "approvals", "add", "--yes"], check=True, capture_output=True)
    r = remove(repo, place)
    assert r.returncode == 0, r.stderr
    told = json.loads(r.stdout)
    assert [(os.path.realpath(t["path"]), t["branch_outcome"]) for t in told] == [(os.path.realpath(place), "not_attempted")]
    assert not place.exists() and repo.git("branch", "--list", "unit/x")
    end = time.monotonic() + 600  # post-remove runs in the background (tests.8: a condition, not the clock)
    while "post x" not in (kit.log.read_text() if kit.log.exists() else "") and time.monotonic() < end:
        time.sleep(0.1)
    assert kit.log.read_text().splitlines() == ["pre x present", "post x absent"]


def test_a_failing_pre_remove_hook_keeps_the_worktree_saying_so_on_an_error_line(repo, kit, tmp_path):
    """plan.wt_refused: a hook that fails refuses the removal, its ✗ line saying which."""
    place = kit(HOOKS)
    subprocess.run(["wt", "-C", str(repo.path), "config", "approvals", "add", "--yes"], check=True, capture_output=True)
    (tmp_path / "home" / "fail-x").touch()
    r = remove(repo, place)
    assert r.returncode != 0 and place.is_dir()
    assert any(l.strip().startswith("✗") and "pre-remove" in l for l in r.stderr.splitlines()), r.stderr


def test_a_kit_with_merge_hooks_only_asks_no_approval_to_remove(repo, kit):
    """plan.tidy: a kit whose wt.toml gates merges only sees its places go with nothing approved."""
    place = kit('[pre-merge]\ngate = "true"\n')
    r = remove(repo, place)
    assert r.returncode == 0, r.stderr
    assert not place.exists()
