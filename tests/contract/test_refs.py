"""What crew assumes of git's files when the host's follower looks, with no process, at what its read rests on (plan.12):
the tip of a branch in crew's bare cache (plan.tip_here), the state and blueprints caches' look and check, and crew's
own checkout's commit (crew.head_here), the check that crew moved. Each is read from the files git writes, loose or
packed, and through git only when the files can't say."""
import subprocess

import pytest

import crew
import plan


def refuse_processes(monkeypatch):
    """From here on in a case, every way Python starts a process raises."""
    def refuse(*args, **kwargs):
        raise AssertionError(f"this read starts no process, and it ran {args[0] if args else kwargs!r}")
    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, refuse)


@pytest.fixture
def no_process(monkeypatch):
    refuse_processes(monkeypatch)


@pytest.fixture
def cache(repo, tmp_path, monkeypatch):
    """crew's bare cache of WilldanGroup/crew-state, holding refs/crew/wldn/main at the repo's commit, as a fetch leaves
    it."""
    monkeypatch.setattr(plan, "CACHE", tmp_path / "cache")
    c = tmp_path / "cache" / "WilldanGroup" / "crew-state.git"
    c.parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "--bare", str(c)], check=True)
    sha = repo.commit("plan: start")
    subprocess.run(["git", "-C", str(c), "fetch", "-q", str(repo.path), "+refs/heads/main:refs/crew/wldn/main"], check=True)
    return c, sha


def test_a_loose_ref_is_read_from_its_file(cache, no_process):
    c, sha = cache
    assert (c / "refs/crew/wldn/main").is_file()
    assert plan.tip_here("WilldanGroup/crew-state", "wldn/main") == sha


def test_a_packed_ref_is_read_from_packed_refs(cache, monkeypatch):
    c, sha = cache
    subprocess.run(["git", "-C", str(c), "pack-refs", "--all"], check=True)
    assert not (c / "refs/crew/wldn/main").exists()
    refuse_processes(monkeypatch)
    assert plan.tip_here("WilldanGroup/crew-state", "wldn/main") == sha


def test_a_branch_the_cache_does_not_hold_or_a_cache_not_made_reads_empty(cache, no_process):
    assert plan.tip_here("WilldanGroup/crew-state", "swancloud/main") == ""
    assert plan.tip_here("afterthought/crew-state", "swancloud/main") == ""


def test_a_ref_the_files_cannot_say_is_asked_of_git(cache):
    """A symbolic ref holds no commit in its file; git reads it."""
    c, sha = cache
    subprocess.run(["git", "-C", str(c), "symbolic-ref", "refs/crew/madswan/main", "refs/crew/wldn/main"], check=True)
    assert crew.files_ref(c, "refs/crew/madswan/main") is None
    assert plan.tip_here("WilldanGroup/crew-state", "madswan/main") == sha


def test_crews_head_in_a_detached_worktree_and_on_a_branch_is_read_from_its_files(repo, tmp_path, monkeypatch):
    """crew/live is a detached worktree beside crew/main (plan.19); a coder's place is a worktree on a branch."""
    sha = repo.commit("feat: crew")
    live, place = tmp_path / "live", tmp_path / "place"
    repo.git("worktree", "add", "-q", "--detach", str(live), "HEAD")
    repo.git("worktree", "add", "-q", "-b", "unit/x", str(place), "HEAD")
    repo.git("pack-refs", "--all")
    refuse_processes(monkeypatch)
    assert crew.head_here(live) == sha and crew.head_here(place) == sha and crew.head_here(repo.path) == sha
