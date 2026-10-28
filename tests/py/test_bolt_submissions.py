"""Every submission's number on its bolt's row (bolt-teams "A submission's number is on its bolt's row from the
submit", teams.22, record 0046 part 2): the gather's read of sluice's queue, gather.submissions_of, on sluice 0.51.3's
own overview (tests/py/sluice-0.51.3/), every field guarded and a document of another schema said; and gather.queue's
failures, each said, on a stand-in for the process."""
import json
import pathlib
import subprocess

import pytest

import gather

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
