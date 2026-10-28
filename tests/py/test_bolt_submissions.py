"""Every submission's number on its bolt's row (bolt-teams "A submission's number is on its bolt's row from the
submit", teams.22, record 0046 part 2): the gather's read of sluice's queue, gather.submissions_of, on sluice 0.51.3's
own overview (tests/py/sluice-0.51.3/), every field guarded and a document of another schema said; gather.queue's
failures, each said, on a stand-in for the process; whose line each submission is, plan.submission_rows; and what
crew bolts shows of them, plan.bolts_data and plan.bolts_text, beside the rest of crew bolts in test_rail.py and
test_chores.py."""
import json
import pathlib
import subprocess

import pytest

from facts import plan_text

import crew
import gather
import plan

RECORDED = pathlib.Path(__file__).parent / "sluice-0.51.3"


def overview():
    return json.loads((RECORDED / "overview-standing.json").read_text())


# ------------------------------------------------------------------------------------- the gather's read of the queue

def test_the_overview_gives_each_standing_submission_with_its_branch_state_and_where_it_came_from():
    assert gather.submissions_of(overview()) == ([
        {"id": 317, "branch": "bolt/crews-chores-of-the-24th-night", "head": "aa1a9c7fa2f7a64d505f4c6a99e0f76b5f948d2b",
         "state": "testing", "worktree": "chore/a-proven-bolts-batch-is-reckoned-at-once-wherever-it-lives", "pull_head": None},
        {"id": 318, "branch": "bolt/crews-chores-of-the-24th-night", "head": "ed8e7a92d5f8385895c2cf99d277a4c147738e6f",
         "state": "queued", "worktree": "chore/a-stage-drives-a-browser-only-the-kits-way", "pull_head": None},
        {"id": 355, "branch": "main", "head": "b49230ce242d7a965174cc0f52589739ed97f375", "state": "queued",
         "worktree": "pull/198", "pull_head": "bolt/crew-opens-no-tab-the-user-does-not-use"}], None)


def test_an_empty_queue_is_none_standing_and_not_a_failure():
    doc = dict(overview(), branches=[dict(b, submissions=[]) for b in overview()["branches"]])
    assert gather.submissions_of(doc) == ([], None)


def test_a_field_missing_or_mistyped_is_none_and_a_submission_with_no_number_or_branch_is_left_out():
    """read.2: a missing value never becomes text."""
    doc = overview()
    subs = doc["branches"][0]["submissions"]
    del subs[0]["state"], subs[0]["from"]
    subs[1]["id"] = "318"
    doc["branches"][1]["submissions"][0]["from"] = "pull/198"
    doc["branches"][1]["submissions"].append({"id": True, "branch": "main"})
    doc["branches"][1]["submissions"].append("#356")
    got, why = gather.submissions_of(doc)
    assert why is None and [(s["id"], s["state"], s["worktree"], s["pull_head"]) for s in got] == [
        (317, None, None, None), (355, "queued", None, None)]


def test_a_submission_with_no_branch_of_its_own_takes_its_branch_views():
    doc = overview()
    del doc["branches"][0]["submissions"][0]["branch"]
    assert gather.submissions_of(doc)[0][0]["branch"] == "bolt/crews-chores-of-the-24th-night"


@pytest.mark.parametrize("doc, why", [
    (dict(overview(), schema="sluice/overview@2"), "sluice overview printed sluice/overview@2, not the sluice/overview@1 crew reads"),
    ({"branches": []}, "sluice overview printed no schema, where crew reads sluice/overview@1"),
    ([], "sluice overview printed no schema, where crew reads sluice/overview@1"),
    (dict(overview(), branches=None), "sluice overview's sluice/overview@1 holds no list of branches")])
def test_a_document_of_another_schema_is_said_never_read_as_an_empty_queue(doc, why):
    assert gather.submissions_of(doc) == (None, why)


class Ran:
    def __init__(self, code, out="", err=""):
        self.returncode, self.stdout, self.stderr = code, out, err


@pytest.mark.parametrize("run, why", [
    (FileNotFoundError("sluice"), "this host has no sluice on its path"),
    (subprocess.TimeoutExpired("sluice", 15), "sluice overview did not answer within 15 seconds"),
    (Ran(2, '{"error":{"kind":"refused","message":"not a repository sluice serves"}}'),
     "sluice overview exited 2: not a repository sluice serves"),
    (Ran(2, "", "error: unrecognized subcommand 'overview'\n"), "sluice overview exited 2: error: unrecognized subcommand 'overview'"),
    (Ran(0, "not json"), "sluice overview printed no JSON")])
def test_a_queue_that_cant_be_read_says_why(monkeypatch, run, why):
    def ran(args, **kw):
        assert args == ["sluice", "overview", "--json"] and kw["cwd"] == "/k/main" and kw["timeout"] == 15
        if isinstance(run, BaseException):
            raise run
        return run
    monkeypatch.setattr(gather.subprocess, "run", ran)
    assert gather.queue("/k/main") == (None, why)


def test_a_queue_read_is_the_documents_submissions(monkeypatch):
    monkeypatch.setattr(gather.subprocess, "run", lambda args, **kw: Ran(0, (RECORDED / "overview-standing.json").read_text()))
    assert [s["id"] for s in gather.queue("/k/main")[0]] == [317, 318, 355]


# --------------------------------------------------------------------------------------- whose line each one is

def sub(n, branch, worktree, state="queued", pull_head=None, head="a" * 40):
    return {"id": n, "branch": branch, "head": head, "state": state, "worktree": worktree, "pull_head": pull_head}


LINES = [("a", "unit"), ("bump", "chore"), ("fix/y/gap", "fix")]


def test_a_merge_into_the_bolt_is_its_lines_and_a_landing_on_main_the_bolts():
    """bolt-teams "A unit's merge under test" and "A bolt's landing queued on main"."""
    subs = [sub(41, "bolt/y", "unit/a", "testing"), sub(42, "bolt/y", "chore/bump"), sub(43, "bolt/y", "fix/y/gap", "passed"),
            sub(355, "main", "bolt/y", head="b" * 40)]
    assert plan.submission_rows(subs, "y", LINES) == (
        {"a": {"id": 41, "state": "testing"}, "bump": {"id": 42, "state": "queued"}, "fix/y/gap": {"id": 43, "state": "passed"}},
        {"id": 355, "state": "queued", "head": "b" * 40})


def test_a_landing_by_pull_request_is_the_bolts_it_was_opened_from():
    assert plan.submission_rows([sub(355, "main", "pull/198", pull_head="bolt/y")], "y", LINES)[1]["id"] == 355
    assert plan.submission_rows([sub(355, "main", "pull/198", pull_head="bolt/z")], "y", LINES) == ({}, None)


def test_another_bolts_submissions_and_a_hand_submission_are_no_line_of_this_one():
    subs = [sub(41, "bolt/z", "unit/a"), sub(44, "bolt/y", "unit/elsewhere"), sub(45, "bolt/y", "unit/a-b"), sub(46, "main", "bolt/z"),
            sub(47, "bolt/y", None)]
    assert plan.submission_rows(subs, "y", LINES) == ({}, None)


def test_the_newest_of_a_lines_two_is_its_own():
    subs = [sub(52, "bolt/y", "unit/a", "testing"), sub(50, "bolt/y", "unit/a", "passed")]
    assert plan.submission_rows(subs, "y", LINES)[0] == {"a": {"id": 52, "state": "testing"}}


def test_nothing_read_gives_no_line_a_submission():
    assert plan.submission_rows(None, "y", LINES) == ({}, None)


@pytest.mark.parametrize("state, said", [("testing", "#41 under test"), ("queued", "#41 queued"), ("passed", "#41 passed, to land next"),
                                         ("waiting", "#41 waiting on a submission it comes after"), ("landing", "#41 landing"),
                                         ("forming", "#41 forming"), (None, "#41")])
def test_a_standing_state_is_said_in_crews_words_and_sluices_own_for_one_crew_has_none_for(state, said):
    assert plan.standing_said({"id": 41, "state": state}) == said


# ------------------------------------------------------------------------------------------------- crew bolts

BOX = "chuck-herdr-alpha"
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": BOX, "teams": ["swb-1"]}},
         "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": BOX,
                             "kit": {"main": "/kit/main", "dir": "/kit", "name": "switchboard-kit"}}},
         "hosts": {BOX: {"ssh": BOX, "home": "/h/box"}}}


@pytest.fixture(autouse=True)
def here(monkeypatch):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")


def bolts(submissions=None, error=None):
    p = plan.Plan(plan_text(bolts=[("y", "switchboard-kit", "swb-1")],
                            units=[("a", "switchboard-kit", "y", []), ("b", "switchboard-kit", "y", []), ("bump", "switchboard-kit", "y", [], "chore")]))
    place = {"path": "/kit/places/a", "head": "f" * 40, "head_at": "2026-10-28T10:00:00Z", "tasks": (2, 2), "planning": True, "open": [],
             "bolt": "y"}
    kit = {"ok": True, "main": [], "fixes": [], "places": {"a": place}, "bolts": {"y": {"exists": True, "head": "d" * 40, "changes": []}},
           **({"submissions": submissions} if submissions is not None else {}), **({"submissions_error": error} if error else {})}
    sv = {BOX: {"ok": True, "kits": {"/kit/main": kit}}}
    return plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", "abcdef1" + "0" * 33, p)], sv, {})


def held(d):
    return d["partitions"][0]["plans"][0]["bolts"][0]


def test_crew_bolts_shows_a_merge_under_test_on_its_line_and_the_landing_on_the_head_line():
    """bolt-teams "A unit's merge under test", "A bolt's landing queued on main"."""
    d = bolts([sub(41, "bolt/y", "unit/a", "testing"), sub(355, "main", "pull/198", pull_head="bolt/y", head="d" * 40)])
    b = held(d)
    assert {u["unit"]: u["submission"] for u in b["units"]} == {"a": {"id": 41, "state": "testing"}, "b": None, "bump": None}
    assert (b["landing"], b["submissions_error"]) == ({"id": 355, "state": "queued", "head": "d" * 40}, None)
    out = plan.bolts_text(d).splitlines()
    assert out[1] == f"y  switchboard-kit  swb-1 @ {BOX}  active  landing #355 queued"
    assert "  a                                        verify 2/2 #41 under test places/a" in out
    assert json.loads(json.dumps(d))["partitions"][0]["plans"][0]["bolts"][0]["units"][0]["submission"] == {"id": 41, "state": "testing"}


def test_a_merge_passed_and_nothing_waiting_on_it_still_shows():
    """bolt-teams "Read again after the session that submitted it ended": the queue is sluice's, so a restart loses nothing."""
    out = plan.bolts_text(bolts([sub(41, "bolt/y", "unit/a", "passed")]))
    assert "#41 passed, to land next" in out


def test_once_decided_no_line_shows_a_submission():
    """bolt-teams "Decided": sluice's overview holds a landed submission in no chain."""
    d = bolts([])
    assert all(u["submission"] is None for u in held(d)["units"]) and held(d)["landing"] is None
    assert "#" not in plan.bolts_text(d)


def test_a_queue_that_cant_be_read_is_said_once_on_the_head_line_and_no_line_shows_a_number():
    """bolt-teams "sluice's record can't be read"."""
    d = bolts([sub(41, "bolt/y", "unit/a", "testing")], error="sluice overview exited 2: not a repository sluice serves")
    assert all(u["submission"] is None for u in held(d)["units"]) and held(d)["landing"] is None
    assert held(d)["submissions_error"] == "sluice overview exited 2: not a repository sluice serves"
    out = plan.bolts_text(d)
    assert out.count("can't be read") == 1 and "#41" not in out
    assert out.splitlines()[2] == f"  submissions: can't be read on {BOX}: sluice overview exited 2: not a repository sluice serves"
