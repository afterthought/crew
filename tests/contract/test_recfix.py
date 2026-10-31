"""What crew assumes of recfix --check, each case naming what assumes it: plan.checked runs it on every file a write
commits, a signal's and a capture's markdown by its frontmatter as one record, so a value that breaks the record is
refused, named by its file and line, and nothing is pushed (plan.1, signals.4); a Move the moves file's enum does not
allow is refused (the route a unit add --signal writes); a hand edit that duplicates a key is refused by name
(read.1, crew bolts naming the commit); a bolt given to a crossed team is marked Path: flume, the one Path the
plan takes; and requests.rec is refused for what its descriptor does not allow."""
import re

import pytest

from crew import Refusal
import plan
import runner

SIG = "2026-10-12-chuck-mac-studio-abcd1234/01-tiles-split"


def test_a_signal_and_its_capture_pass_by_their_frontmatter():
    plan.checked({f"signals/{SIG}.md": plan.signal_md(SIG, "ask", "user", "tiles, seams", "Tiles split.", plan.quoted("Tiles split.", "14:00:00Z")),
                  "signals/2026-10-12-chuck-mac-studio-abcd1234/capture.md": "---\ncapture: x\nsource: operator\nsignals: 1\n---\n\n# x\n"})


def test_a_value_that_breaks_a_signals_frontmatter_is_refused_naming_the_file_and_its_line():
    text = plan.signal_md(SIG, "ask", "user", "tiles\nseams", "Tiles split at the seam.", plan.quoted("Tiles split.", "14:00:00Z"))
    with pytest.raises(Refusal, match=re.escape(f"signals/{SIG}.md fails recfix --check: 01-tiles-split.md: 6: error")):
        plan.checked({f"signals/{SIG}.md": text})


def test_a_route_the_moves_files_enum_does_not_allow_is_refused():
    route = "\n".join(plan.Rec("Move", [("Signal", SIG), ("Move", "route"), ("Target", "unit/u"), ("Date", "2026-10-12"), ("By", "d")]).lines())
    assert " drop route" in plan.MOVES
    plan.checked({"moves.rec": plan.MOVES + "\n" + route + "\n"})
    with pytest.raises(Refusal, match="^moves.rec fails recfix --check"):
        plan.checked({"moves.rec": plan.MOVES.replace(" drop route", " drop") + "\n" + route + "\n"})


def test_a_plan_with_a_duplicated_key_is_refused_by_name():
    text = "%rec: Unit\n%key: Unit\n\nUnit: a\nRepo: switchboard-kit\nIntent: once\n\nUnit: a\nRepo: switchboard-kit\nIntent: twice\n"
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check: .*duplicated key"):
        plan.recfix(text, "plan.rec")


def test_the_plan_takes_a_chore_among_its_units_and_refuses_any_other_kind():
    """op_unit_add's chore and plan.checked: a Unit record marked Kind: chore sits among the units, between two of them,
    and passes the plan's schema; a Kind the schema's enum does not hold is refused (plan.1, plan.11)."""
    unit = lambda name, kind=None: f"Unit: {name}\nRepo: crew\nBolt: b\n" + (f"Kind: {kind}\n" if kind else "") + f"Intent: {name} is done.\n\n"
    bolt = "Bolt: b\nRepo: crew\nGoal: Upkeep.\n\n"
    text = plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit") + "\n" + unit("a") + unit("bump", "chore") + unit("c")
    plan.recfix(text, "plan.rec")
    assert [u.name() for u in plan.Plan(text).chores()] == ["bump"]
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(text.replace("Kind: chore", "Kind: spike"), "plan.rec")


def test_a_bolt_given_to_a_crossed_team_is_marked_flume_and_no_other_path_passes():
    """A give to a crossed team marks its bolt Path: flume beside Team (the change teams-cross-to-flume-as-their-bolts-land,
    Decision 2): plan.checked takes it, and refuses a Path the Bolt set's enum does not hold (plan.1)."""
    bolt = "Bolt: x\nRepo: crew\nGoal: Cross.\nTeam: crw-4\nPath: flume\n\n"
    text = plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit")
    plan.recfix(text, "plan.rec")
    assert [b.get("Path") for b in plan.Plan(text).bolts()] == ["flume"]
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(text.replace("Path: flume", "Path: other"), "plan.rec")


def launch_rec(n, work="unit/a", after=(), **more):
    """A launch request as plan.request writes it (runner.request_fields), its brief over two lines."""
    given = dict(Repo="afterthought/crew", Kind="change", Name=work.split("/")[-1], Base="bolt/b", Stream="madswan",
                 Priority=2, Intent="madswan/b", Recipient="madswan/planner", After=list(after), Brief="Build a.\nSource: a.md", **more)
    return plan.Rec("Request", runner.request_fields(n, "launch", "deneb", work, given, "2026-10-31T12:00:00Z", "madswan-dispatch-deneb"))


def requests_text(*recs):
    return runner.REQUESTS + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)


def test_requests_of_every_act_pass_and_the_descriptor_refuses_what_it_does_not_allow():
    """plan.request appends each act's request to requests.rec, and land checks the file by recfix with the plan write
    (runner.REQUESTS; Decision 4 of teams-cross-to-flume-as-their-bolts-land, plan.1): a launch with its brief over two
    lines and its After, a retry with a stage and words, a retry of the submission, a drop and a priority pass; an act,
    a kind or a hold the enums do not hold, a number that is no number and a date that is none are refused."""
    other = lambda n, act, **g: plan.Rec("Request", runner.request_fields(n, act, "deneb", "unit/a", g, "2026-10-31T12:00:00Z", "madswan-planner"))
    text = requests_text(launch_rec(1, "unit/a"), launch_rec(2, "unit/b", after=[1]), other(3, "retry", Of=1, Stage="construct", Words="Read it again."),
                         other(4, "retry", Of=1, Submission=True), other(5, "drop", Of=2), other(6, "priority", Of=1, Priority=5))
    plan.checked({"requests.rec": text})
    assert [r.get("Act") for r in plan.Plan(text).recs("Request")] == ["launch", "launch", "retry", "retry", "drop", "priority"]
    assert plan.Plan(text).recs("Request")[0].get("Brief") == "Build a.\nSource: a.md"
    for right, wrong in (("Act: priority", "Act: reorder"), ("Kind: change", "Kind: spike"), ("Submission: yes", "Submission: maybe"),
                         ("Request: 6", "Request: six"), ("Date: 2026-10-31T12:00:00Z", "Date: soon"), ("Of: 2", "Of: 2\nTeam: crw-4")):
        with pytest.raises(Refusal, match="^requests.rec fails recfix --check"):
            plan.checked({"requests.rec": text.replace(right + "\n", wrong + "\n", 1)})


def launch_of_a(w, **more):
    """A change function's request: a launch of unit a on bolt b, as a give appends it."""
    return plan.request(w, "launch", "deneb", "unit/a", **dict(dict(Repo="afterthought/crew", Kind="change", Name="a", Base="bolt/b",
                        Stream="madswan", Priority=1, Intent="madswan/b", Recipient="madswan/planner", Brief="Build a."), **more))


def test_a_request_is_written_in_the_commit_of_the_plan_write_that_occasions_it_and_a_refused_one_pushes_nothing(state, monkeypatch):
    """plan.write commits requests.rec with the plan, one commit and one Crew-Entry (state.1, plan.2); a request crew's
    rules refuse, one recfix refuses and a write that changes a request the branch holds each refuse the whole write,
    and the branch is as it was (Decision 4 of teams-cross-to-flume-as-their-bolts-land)."""
    monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")
    ref = f"{state.LABEL}/main"
    before = state.git("rev-parse", ref)

    def give(w):
        w.plan.insert(plan.Rec("Bolt", [("Bolt", "b"), ("Repo", "afterthought/crew"), ("Goal", "Cross."), ("Team", "crw-4"), ("Path", "flume")]))
        assert launch_of_a(w) == 1
        return []
    sha = plan.write(state.fleet, state.LABEL, give, "plan(bolt b): give to crw-4")
    assert state.git("rev-parse", ref) == sha and state.git("rev-list", "--count", f"{before}..{sha}") == "1"
    assert state.git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).split() == ["plan.rec", "requests.rec"]
    assert len(state.git("log", "-1", "--format=%(trailers:key=Crew-Entry,valueonly)", sha).split()) == 1
    held = state.git("show", f"{sha}:requests.rec")
    assert held.startswith(runner.REQUESTS.split("\n")[0]) and "Request: 1\nAct: launch\nHost: deneb\nWork: unit/a\n" in held

    for change, said in ((lambda w: launch_of_a(w, Stream=None), "names no Stream"),
                         (lambda w: launch_of_a(w, Priority="high"), "^requests.rec fails recfix --check"),
                         (lambda w: w.replace("requests.rec", w.text("requests.rec").replace("Name: a", "Name: b")), "request 1 would be changed")):
        with pytest.raises(Refusal, match=said):
            plan.write(state.fleet, state.LABEL, lambda w: change(w) and [], "plan: ask again")
        assert state.git("rev-parse", ref) == sha
