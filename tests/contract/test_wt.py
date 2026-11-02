"""What crew assumes of worktrunk's wt remove, each case naming what assumes it: plan.tidy removes a finished
worktree through the kit's own `wt remove --foreground --no-delete-branch --force --format json`, run with no input,
so the kit's remove hooks run and the branch is left to crew (plan.9, plan.10); and what it assumes of git and wt for a
bolt's worktree from before record 0026, which the tidy detaches at the bolt's tip while the bolt lasts (plan.18)."""
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


@pytest.fixture
def legacy(repo, tmp_path):
    """A bolt given before record 0026: its worktree at bolts/b on bolt/b, beside the kit's main checkout."""
    repo.commit("chore: start", {"README.md": "r\n"})
    repo.git("branch", "bolt/b")
    path = tmp_path / "bolts" / "b"
    repo.git("worktree", "add", "-q", str(path), "bolt/b")
    return path


def status(path):
    r = subprocess.run(["git", "-C", str(path), "status", "--porcelain"], capture_output=True, text=True)
    return lambda: (r.returncode, r.stdout, r.stderr)


def test_a_clean_bolt_worktree_is_detached_at_its_tip_with_its_files_and_its_branch_marked_crews(repo, legacy, tmp_path):
    """plan.bolt_detach and plan.bolt_detached (plan.9, plan.18): git status reads a clean legacy bolt worktree clean,
    and `git switch --detach` in it leaves it on no branch at the bolt's tip with its files, the branch marked as
    crew's so it goes with the bolt."""
    import plan
    tip = repo.git("rev-parse", "bolt/b")
    assert plan.bolt_detach(str(legacy), "bolt/b", str(tmp_path), None, False, status(legacy), lambda: None) == (True, None)
    said = plan.bolt_detached(str(repo.path), str(legacy), "bolt/b")
    assert said == f"{legacy} is detached at bolt/b's tip, {tip[:7]}, so no worktree holds the bolt's branch"
    assert subprocess.run(["git", "-C", str(legacy), "symbolic-ref", "-q", "HEAD"]).returncode != 0
    assert subprocess.run(["git", "-C", str(legacy), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() == tip
    assert (legacy / "README.md").read_text() == "r\n" and status(legacy)()[1] == ""
    assert repo.git("config", "branch.bolt/b.crew") == "given"


def test_a_bolt_worktree_with_an_edit_or_whose_branch_a_merge_moved_reads_dirty_and_is_left_on_its_branch(repo, legacy, tmp_path):
    """plan.bolt_detach (plan.9): a modified file reads dirty; so does a worktree whose branch sluice moved under it by
    update-ref at a merge, its files at the old tree, which crew leaves on the branch rather than carry a revert along."""
    import plan
    (legacy / "README.md").write_text("edited\n")
    assert plan.bolt_detach(str(legacy), "bolt/b", str(tmp_path), None, False, status(legacy), lambda: None)[0] is False
    (legacy / "README.md").write_text("r\n")
    old = repo.git("rev-parse", "bolt/b")
    (repo.path / "unit.txt").write_text("u\n")
    repo.git("add", "unit.txt")
    landed = repo.git("commit-tree", repo.git("write-tree"), "-p", old, "-m", "chore(land): #1 unit/x")
    repo.git("update-ref", "refs/heads/bolt/b", landed, old)
    assert status(legacy)()[1].strip(), "a branch moved under its worktree reads clean"
    assert plan.bolt_detach(str(legacy), "bolt/b", str(tmp_path), None, False, status(legacy), lambda: None)[0] is False
    assert repo.git("worktree", "list", "--porcelain").count("branch refs/heads/bolt/b") == 1


def test_wt_removes_a_detached_bolt_worktree_and_attempts_no_branch(repo, legacy, monkeypatch, tmp_path):
    """plan.tidy and plan.wt_left_branch: once its bolt is over, the detached worktree goes through the kit's wt remove,
    whose answer names it with no branch and its branch outcome not attempted, so every branch is crew's to judge."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "home" / ".config"))
    subprocess.run(["git", "-C", str(legacy), "switch", "-q", "--detach"], check=True)
    r = remove(repo, legacy)
    assert r.returncode == 0, r.stderr
    told = json.loads(r.stdout)
    assert [(t["branch"], t["branch_outcome"]) for t in told] == [(None, "not_attempted")]
    import plan
    assert plan.wt_left_branch(r.stdout, str(legacy)) and not legacy.exists()
    assert repo.git("branch", "--list", "bolt/b")
