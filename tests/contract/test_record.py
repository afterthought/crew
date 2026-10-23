"""What crew assumes of recutils and git for its run record, each case naming what assumes it: a day's file a host began
under an older descriptor, before a card's Card and Key were allowed, takes an entry with them that recsel reads, and
record.carry writes that day to the branch under the descriptor that allows them, which recfix --check passes
(record.emit, record.carry, the card hook's entries); and a chain of entries plan.land pushes to a bare repository
standing for GitHub lands as one commit per entry, each changing its day's file alone, made again on top of another
clone's push that moved the branch between its fetch and its push (plan.land, record.reach, state.1)."""
import datetime
import re
import subprocess

import pytest

import crew
import plan
import record


@pytest.fixture
def runs(tmp_path, monkeypatch):
    monkeypatch.setattr(record, "ROOT", tmp_path / "crew")
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
    d = tmp_path / "crew" / "wldn" / "runs" / "mac-studio"
    d.mkdir(parents=True)
    return d


def test_an_older_days_file_takes_a_cards_fields_and_is_carried_under_the_descriptor_that_allows_them(runs, tmp_path):
    day = record.path_for("wldn", "mac-studio", datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    day.write_text(re.sub(r" Card Key[^\n]*\n", "\n", record.DESCRIPTOR))
    assert "Card" not in day.read_text()
    assert record.emit("wldn", "card.post", ["unit/x"], Card="req_old-1", Key="verify/x/20261007-1400")
    got = subprocess.run(["recsel", "-t", "Entry", "-e", "Act = 'card.post'", "-P", "Card,Key", str(day)], capture_output=True, text=True)
    assert got.stdout.split() == ["req_old-1", "verify/x/20261007-1400"]
    carried, _ = record.carry("wldn", lambda path: None)
    text, = carried.values()
    f = tmp_path / "carried.rec"
    f.write_text(text)
    assert subprocess.run(["recfix", "--check", str(f)], capture_output=True).returncode == 0
    assert subprocess.run(["recsel", "-t", "Entry", "-P", "Card", str(f)], capture_output=True, text=True).stdout.strip() == "req_old-1"


def test_a_days_file_begun_now_allows_them(runs):
    assert record.emit("wldn", "card.post", ["unit/y"], Card="req_new-1", Key="verify/y/20261007-1500")
    day, = runs.glob("*.rec")
    assert subprocess.run(["recfix", "--check", str(day)], capture_output=True).returncode == 0


def test_two_entries_written_at_once_by_two_processes_are_both_whole_and_the_file_passes_recfix(tmp_path):
    """record.emit: the descriptor goes in by a link and each entry in one append, so processes writing at once never
    interleave (record.4)."""
    import os
    import pathlib
    import sys
    lib = pathlib.Path(record.__file__).parent
    env = dict(os.environ, CREW_SESSION="")
    env.pop("CREW_AGENT", None)
    ps = [subprocess.Popen([sys.executable, str(lib / "record.py"), "emit", "--label", "wldn", "--act", f"test.{n}", "--on", f"unit/{n}"], env=env)
          for n in ("one", "two")]
    assert [p.wait() for p in ps] == [0, 0]
    f, = pathlib.Path(os.environ["HOME"]).glob(".local/state/crew/wldn/runs/*/*.rec")
    assert subprocess.run(["recfix", "--check", str(f)], capture_output=True).returncode == 0
    got = subprocess.run(["recsel", "-t", "Entry", "-C", "-P", "Act", str(f)], capture_output=True, text=True).stdout.split()
    assert sorted(got) == ["test.one", "test.two"]


def git(where, *args, input=None):
    r = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, input=input)
    assert r.returncode == 0, f"git {' '.join(args)}: {r.stderr.strip()}"
    return r.stdout.strip()


@pytest.fixture
def github(tmp_path, monkeypatch, runs):
    """A bare repository standing for WilldanGroup/crew-state on GitHub, its wldn/main holding a plan, and crew's cache
    and this command's reading of the branch in scratch."""
    bare = tmp_path / "crew-state.git"
    git(tmp_path, "init", "-q", "--bare", str(bare))
    w = tmp_path / "seed"
    git(tmp_path, "init", "-q", str(w))
    (w / "plan.rec").write_text(plan.HEADER)
    git(w, "add", "plan.rec")
    git(w, "commit", "-q", "-m", "plan: start (chuck@mac-studio)")
    git(w, "push", "-q", str(bare), "HEAD:refs/heads/wldn/main")
    monkeypatch.setattr(plan, "url", lambda repo: str(bare))
    monkeypatch.setattr(plan, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(plan, "READ", plan.Reading())
    return bare


DAY = "2026-10-12"


def two_entries(runs):
    (runs / f"{DAY}.rec").write_text(record.DESCRIPTOR + "".join(
        f"\nId: 20261012T10000{n}Z-000000-mac-studio-1-{n}\nAt: {DAY}T10:00:0{n}Z\nHost: mac-studio\nBy: swb-1-conductor\nAct: tell\n"
        f"On: agent/wldn-planner\nChars: {n}\n" for n in (1, 2)))


def chain_at(tip):
    """What record.reach hands plan.land: the entries the branch lacks at the tip, one commit each."""
    chain, _ = record.unpushed("wldn", lambda path: plan.show("WilldanGroup/crew-state", tip, path))
    return [({path: text}, record.entry_message(lines, "swb-1-conductor")) for _, lines, path, text in chain]


def test_a_chain_of_two_entries_lands_as_two_commits_each_changing_its_days_file_alone(github, runs):
    two_entries(runs)
    before = git(github, "rev-parse", "wldn/main")
    sha = plan.land("WilldanGroup/crew-state", "wldn/main", None, chain_at)
    assert git(github, "rev-parse", "wldn/main") == sha
    commits = git(github, "rev-list", "--reverse", f"{before}..wldn/main").split()
    assert len(commits) == 2
    for c, n in zip(commits, (1, 2)):
        assert git(github, "diff-tree", "--no-commit-id", "--name-only", "-r", c) == f"runs/mac-studio/{DAY}.rec"
        assert git(github, "log", "-1", "--format=%(trailers:key=Crew-Entry,valueonly)", c) == f"20261012T10000{n}Z-000000-mac-studio-1-{n}"
    f = runs.parent / "landed.rec"
    f.write_text(git(github, "show", f"wldn/main:runs/mac-studio/{DAY}.rec") + "\n")
    assert subprocess.run(["recfix", "--check", str(f)], capture_output=True).returncode == 0
    assert git(github, "show", f"{commits[0]}:runs/mac-studio/{DAY}.rec").count("Id: ") == 1


def test_a_push_refused_because_another_clone_pushed_first_makes_the_chain_again_on_top(github, runs, tmp_path):
    two_entries(runs)
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", "--branch", "wldn/main", str(github), str(other))
    tips = []

    def make(tip):
        tips.append(tip)
        if len(tips) == 1:  # another host writes the plan between this command's fetch and its push
            (other / "plan.rec").write_text(plan.HEADER + "\n")
            git(other, "commit", "-q", "-am", "plan: another host's write (wldn-planner)")
            git(other, "push", "-q", "origin", "wldn/main")
        return chain_at(tip)
    sha = plan.land("WilldanGroup/crew-state", "wldn/main", None, make)
    theirs = git(other, "rev-parse", "HEAD")
    assert len(tips) == 2 and tips[1] == theirs
    assert git(github, "rev-parse", "wldn/main") == sha and git(github, "rev-list", "--count", "--first-parent", f"{sha}~2..{sha}") == "2"
    assert git(github, "rev-parse", f"{sha}~2") == theirs
    assert git(github, "show", f"wldn/main:runs/mac-studio/{DAY}.rec").count("Id: ") == 2
