"""What crew assumes of recutils for its run record, each case naming what assumes it: a day's file a host began under
an older descriptor, before a card's Card and Key were allowed, takes an entry with them that recsel reads, and
record.carry writes that day to the branch under the descriptor that allows them, which recfix --check passes
(record.emit, record.carry, the card hook's entries)."""
import datetime
import re
import subprocess

import pytest

import crew
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
