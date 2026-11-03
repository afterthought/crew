"""Every submission's number on its bolt's row (bolt-teams "A submission's number is on its bolt's row from the
submit", teams.22, record 0046 part 2): the gather's read of sluice's queue, gather.submissions_of, on sluice 0.51.3's
own overview (tests/py/sluice-0.51.3/), every field guarded and a document of another schema said; gather.queue's
failures, each said, on a stand-in for the process; the submissions an overview's recent events name decided,
gather.decided_in, on sluice 0.56.0's and 0.51.3's own overviews (tests/py/sluice-0.56.0/); sluice's record of every
submission a branch has had, gather.decided_of, as the landing reads it once, on its own `status --all` documents;
whose line each submission is, plan.submission_rows; and what
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
RECENT = pathlib.Path(__file__).parent / "sluice-0.56.0" / "overview-recent.json"


def overview():
    return json.loads((RECORDED / "overview-standing.json").read_text())


# ------------------------------------------------------------------------------------- the gather's read of the queue

def test_the_overview_gives_each_standing_submission_with_its_branch_state_and_where_it_came_from():
    assert gather.submissions_of(overview()) == ([
        {"id": 317, "branch": "bolt/crews-chores-of-the-24th-night", "head": "aa1a9c7fa2f7a64d505f4c6a99e0f76b5f948d2b",
         "state": "testing", "worktree": "chore/a-proven-bolts-batch-is-reckoned-at-once-wherever-it-lives", "pull_head": None,
         "submitted": "2026-10-28T00:01:43Z", "started": "2026-10-28T01:03:27Z"},
        {"id": 318, "branch": "bolt/crews-chores-of-the-24th-night", "head": "ed8e7a92d5f8385895c2cf99d277a4c147738e6f",
         "state": "queued", "worktree": "chore/a-stage-drives-a-browser-only-the-kits-way", "pull_head": None,
         "submitted": "2026-10-28T00:23:06Z", "started": None},
        {"id": 355, "branch": "main", "head": "b49230ce242d7a965174cc0f52589739ed97f375", "state": "queued",
         "worktree": "pull/198", "pull_head": "bolt/crew-opens-no-tab-the-user-does-not-use",
         "submitted": "2026-10-28T15:30:29Z", "started": None}], None)


def test_a_submission_under_test_takes_the_start_of_its_candidates_checks_and_a_candidate_only_formed_gives_none():
    """The design's Decision 2: a standing submission under test is the kit's from the start of its checks."""
    doc = overview()
    doc["branches"][0]["candidates"][0]["started"] = 7
    doc["branches"][0]["candidates"][1]["state"] = "testing"
    got, _ = gather.submissions_of(doc)
    assert [(s["id"], s["started"]) for s in got] == [(317, None), (318, None), (355, None)]
    del doc["branches"][0]["candidates"]
    assert gather.submissions_of(doc)[0][0]["started"] is None


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


# ------------------------------------------------------------------------- sluice's record of every submission had

def recorded(name):
    return json.loads((RECORDED / name).read_text())


def test_a_branchs_record_gives_every_submission_it_had_with_when_it_was_submitted_and_told():
    """crew-board "A held bolt's decided merges": sluice 0.51.3's record of a bolt's branch, landed and withdrawn."""
    got, why = gather.decided_of(recorded("status-bolt-all.json"))
    assert why is None and [(s["id"], s["state"], s["worktree"], s["submitted"], s["told"]) for s in got] == [
        (356, "landed", "fix/crew-costs-an-idle-host-nothing/take-main-448c543", "2026-10-28T15:47:07Z", "2026-10-28T15:48:24Z"),
        (357, "landed", "chore/a-wait-ends-with-the-session-that-started-it", "2026-10-28T16:10:48Z", "2026-10-28T16:21:02Z"),
        (358, "withdrawn", "unit/crew-keeps-no-card-wait-and-a-row-carries-its-submission-number", "2026-10-28T17:47:07Z", "2026-10-28T17:47:13Z"),
        (359, "withdrawn", "unit/crew-keeps-no-card-wait-and-a-row-carries-its-submission-number", "2026-10-28T17:56:48Z", "2026-10-28T18:23:56Z"),
        (361, "landed", "unit/crew-keeps-no-card-wait-and-a-row-carries-its-submission-number", "2026-10-28T18:36:05Z", "2026-10-28T18:55:42Z"),
        (362, "landed", "unit/a-rail-refresh-after-no-change-reads-nothing", "2026-10-28T18:57:11Z", "2026-10-28T19:09:03Z")]
    assert (got[0]["branch"], got[0]["head"], got[0]["pull_head"]) == (
        "bolt/crew-costs-an-idle-host-nothing", "e79d32a4061c5a028dbd765d6c397458f249719b", None)


def test_mains_record_names_a_landing_by_its_pull_request_and_a_withdrawal_never_told_by_its_time():
    got, _ = gather.decided_of(recorded("status-main-all.json"))
    assert [(s["id"], s["state"], s["worktree"], s["pull_head"], s["told"]) for s in got] == [
        (305, "withdrawn", "pull/171", "design/bolt-cycle-time", "2026-10-27T18:34:17Z"),
        (363, "landed", "pull/200", "bolt/crew-costs-an-idle-host-nothing", "2026-10-28T19:13:46Z"),
        (364, "landed", "pull/201", "design/the-words", "2026-10-28T19:23:54Z")]


def test_a_record_field_missing_or_mistyped_is_none_and_one_with_no_number_is_left_out():
    """read.2."""
    doc = recorded("status-bolt-all.json")
    del doc["submissions"][0]["told"], doc["submissions"][0]["from"]
    doc["submissions"][1]["submitted"] = 1730000000
    doc["submissions"][2]["id"] = "358"
    del doc["submissions"][3]["branch"]
    doc["submissions"].append("#400")
    got, why = gather.decided_of(doc)
    assert why is None and [(s["id"], s["told"], s["worktree"], s["submitted"]) for s in got][:3] == [
        (356, None, None, "2026-10-28T15:47:07Z"), (357, "2026-10-28T16:21:02Z", "chore/a-wait-ends-with-the-session-that-started-it", None),
        (359, "2026-10-28T18:23:56Z", "unit/crew-keeps-no-card-wait-and-a-row-carries-its-submission-number", "2026-10-28T17:56:48Z")]
    assert got[2]["branch"] == "bolt/crew-costs-an-idle-host-nothing"


@pytest.mark.parametrize("doc, why", [
    ({"branch": "main"}, "sluice status printed no list of submissions"),
    ([], "sluice status printed no list of submissions"),
    ({"submissions": [{"schema": "sluice/submission@2", "id": 1, "branch": "main"}]},
     "sluice status printed a record of sluice/submission@2, not the sluice/submission@1 crew reads")])
def test_a_record_of_another_shape_is_said(doc, why):
    assert gather.decided_of(doc) == (None, why)


# ------------------------------------------------------------------- the decided an overview's recent events name

def recent():
    return json.loads(RECENT.read_text())


def test_each_number_a_branchs_recent_events_name_is_decided_at_its_events_time_from_the_place_it_came_from():
    """crew-board "A row drawn from the overview": sluice 0.56.0's events name their submissions as a list, ids."""
    got, why = gather.decided_in(recent())
    assert why is None and [(s["id"], s["branch"], s["worktree"], s["event"], s["decided"]) for s in got][:3] == [
        (365, "bolt/crew-reads-a-bolts-time-and-its-landing", "fix/crew-reads-a-bolts-time-and-its-landing/take-main", "landed", "2026-10-28T19:30:45Z"),
        (366, "bolt/crew-reads-a-bolts-time-and-its-landing", "unit/a-bolts-row-shows-its-age-and-who-holds-it", "landed", "2026-10-28T20:40:09Z"),
        (367, "bolt/crew-reads-a-bolts-time-and-its-landing", "unit/a-landing-is-read-from-sluices-record", "landed", "2026-10-28T21:56:08Z")]
    assert all((s["pull_head"], s["submitted"], s["started"]) == (None, None, None) for s in got), "an event was read for what it does not give"
    main = [(s["id"], s["worktree"]) for s in got if s["branch"] == "main"]
    assert len(main) == 10 and main[4] == (355, "pull/198"), "a landing by pull request is named by its pull request alone"


def test_an_event_naming_its_one_submission_as_id_is_read_as_sluice_0_51_3_printed_it():
    blamed = [(s["id"], s["event"], s["worktree"]) for s in gather.decided_in(recent())[0] if s["branch"] == "bolt/crews-chores-of-the-24th-night"]
    assert blamed == [(313, "blamed", "chore/a-stage-drives-a-browser-only-the-kits-way"),
                      (315, "blamed", "chore/crew-needs-help-prints-its-usage-and-records-nothing"),
                      (316, "blamed", "chore/a-failed-taking-with-no-conflict-is-said-in-gits-words")]
    assert [s["id"] for s in gather.decided_in(overview())[0]] == [313, 315, 316]


def test_a_standing_submission_is_none_decided():
    assert {s["id"] for s in gather.decided_in(recent())[0]}.isdisjoint({317, 318})


def test_a_recent_field_missing_or_mistyped_is_none_and_a_number_that_is_none_is_left_out():
    """read.2: a missing value never becomes text."""
    doc = recent()
    landed = doc["branches"][0]
    landed["recent"][0]["at"] = 1730000000
    del landed["recent"][1]["event"]
    landed["recent"][2]["ids"] = [367, "368", True]
    landed["recent"].append("landed #369")
    landed["recent_from"] = ["unit/a"]
    doc["branches"][1]["recent"] = None
    doc["branches"][2] = dict(doc["branches"][2], branch=None)
    got, why = gather.decided_in(doc)
    assert why is None and [(s["id"], s["worktree"], s["event"], s["decided"]) for s in got] == [
        (365, None, "landed", None), (366, None, None, "2026-10-28T20:40:09Z"), (367, None, "landed", "2026-10-28T21:56:08Z")]


@pytest.mark.parametrize("doc, why", [
    (dict(recent(), schema="sluice/overview@2"), "sluice overview printed sluice/overview@2, not the sluice/overview@1 crew reads"),
    ([], "sluice overview printed no schema, where crew reads sluice/overview@1"),
    (dict(recent(), branches={}), "sluice overview's sluice/overview@1 holds no list of branches")])
def test_an_overview_of_another_schema_names_no_decided_and_says_why(doc, why):
    assert gather.decided_in(doc) == (None, why)


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


def test_a_flume_places_submission_is_its_lines():
    """bolt-teams "A unit's merge under test", for a started bolt's work: Flume submits a place from its own branch,
    change/<u>, chore/<c> or fix/<bolt>--<f>, as flume-0.3.6's status names it."""
    subs = [sub(41, "bolt/y", "change/a", "testing"), sub(42, "bolt/y", "chore/bump"), sub(43, "bolt/y", "fix/y--gap", "passed"),
            sub(44, "bolt/y", "change/bump")]
    assert plan.submission_rows(subs, "y", LINES)[0] == {
        "a": {"id": 41, "state": "testing"}, "bump": {"id": 42, "state": "queued"}, "fix/y/gap": {"id": 43, "state": "passed"}}


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
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": BOX}},
         "hosts": {BOX: {"ssh": BOX, "home": "/h/box"}}}


@pytest.fixture(autouse=True)
def here(monkeypatch):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setenv("CREW_AGENT", "chuck")


def bolts(submissions=None, error=None, at="code"):
    """crew bolts of wldn's plan, its bolt y started and its work launched, taken by the runner on the box, which keeps
    switchboard-kit in /kit/main, a's place at the Flume 0.3.6 status fixture named (tests/py/flume-0.3.6/<at>.json), the
    kit's submissions in sluice's queue as given."""
    from facts import FactsWrite, ran
    import runner
    w = FactsWrite(plan_text(bolts=[("y", "switchboard-kit", "swb-1")],
                             units=[("a", "switchboard-kit", "y", []), ("b", "switchboard-kit", "y", []), ("bump", "switchboard-kit", "y", [], "chore")]))
    plan.reach_places(FLEET, w, "y")
    requests = plan.Plan(w.files.get("requests.rec") or runner.REQUESTS).recs("Request")
    kit = {"ok": True, "main": [], "fixes": [], "places": {}, "bolts": {"y": {"exists": True, "head": "d" * 40, "changes": []}},
           **({"submissions": submissions} if submissions is not None else {}), **({"submissions_error": error} if error else {})}
    sv = {BOX: {"ok": True, "kits": {"/kit/main": kit}}}
    return plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", "abcdef1" + "0" * 33, w.plan)], sv, {},
                           runs={"wldn": (requests, ran({1: at}, host=BOX, label="wldn", repository="/kit/main"))})


def held(d):
    return d["partitions"][0]["plans"][0]["bolts"][0]


def test_crew_bolts_shows_a_merge_under_test_on_its_line_and_the_landing_on_the_head_line():
    """bolt-teams "A unit's merge under test", "A bolt's landing queued on main"."""
    d = bolts([sub(41, "bolt/y", "unit/a", "testing"), sub(355, "main", "pull/198", pull_head="bolt/y", head="d" * 40)], at="submitted")
    b = held(d)
    assert {u["unit"]: u["submission"] for u in b["units"]} == {"a": {"id": 41, "state": "testing"}, "b": None, "bump": None}
    assert (b["landing"], b["submissions_error"]) == ({"id": 355, "state": "queued", "head": "d" * 40}, None)
    out = plan.bolts_text(d).splitlines()
    assert out[1] == f"y  switchboard-kit  @ {BOX}, in Flume stream wldn  active  landing #355 queued"
    assert "  a                                        submitted #413 flume/change--teams-cross-to-flume-as-their-bolts-land" in out
    assert json.loads(json.dumps(d))["partitions"][0]["plans"][0]["bolts"][0]["units"][0]["submission"] == {"id": 41, "state": "testing"}


def test_a_merge_passed_and_nothing_waiting_on_it_still_shows():
    """bolt-teams "Read again after the session that submitted it ended": the queue is sluice's, so a restart loses nothing."""
    d = bolts([sub(41, "bolt/y", "unit/a", "passed")])
    assert held(d)["units"][0]["submission"] == {"id": 41, "state": "passed"}
    assert plan.standing_said(held(d)["units"][0]["submission"]) == "#41 passed, to land next"


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
