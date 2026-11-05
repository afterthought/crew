"""What crew assumes of recfix --check, each case naming what assumes it: plan.checked runs it on every file a write
commits, a signal's and a capture's markdown by its frontmatter as one record, so a value that breaks the record is
refused, named by its file and line, and nothing is pushed (plan.1, signals.4); a Move the moves file's enum does not
allow is refused (the route a unit add --signal writes); a hand edit that duplicates a key is refused by name
(read.1, crew bolts naming the commit); a started bolt is marked Path: flume, the one Path the plan takes, and a new
branch allows no Team or Agreed while an old branch's records still pass; requests.rec and a runner's branch files are refused for what their descriptors do not allow;
and a kit's rename (plan.op_kit_rename) is one commit whose plan passes, its entry the commit after, while a plan it
would leave naming a record's Repo twice is refused before any commit."""
import json
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


MADSWAN = {"partitions": {"madswan": {"label": "madswan", "machine": "deneb", "blueprints": ["afterthought/blueprints"], "roles": {},
                                      "flume": {"design": False, "planner": "madswan-main", "reviewer": False, "ops": "madswan-main",
                                                "operator": False}}}}


def an_asks_write():
    """A write of the drive holding no asks.rec or roles.rec yet, as a branch before its first ask."""
    class W(plan.Write):
        def text(self, path):
            return self.files.get(path)
    return W(None, "madswan", None, plan.Plan(""))


def test_the_asks_turns_and_role_records_crew_writes_pass_recfix():
    """plan.ask_rec and plan.roles_lines, checked as land() checks every file a commit holds (plan.checked; plan.1,
    state.1): asks.rec with its two record sets, an ask with words over two lines and one keyed naming a card, a turn
    that took both and ended and one superseded, and roles.rec with the planner's and ops's records."""
    w = an_asks_write()
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "tell", "madswan-design", words="record 0053 is accepted\nand its rule amended")
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/2026-10-31T10:04:00Z")
    plan.roles_lines(w, MADSWAN, "madswan")
    pl = plan.Plan(w.files["asks.rec"])
    for n, end in ((1, [("Superseded", "2")]), (2, [("Ended", "2026-10-31T10:20:00Z"), ("Said", "proposed the fix bolt")])):
        pl.insert(plan.Rec("Turn", [("Turn", str(n)), ("Role", "planner"), ("Run", "madswan-planner"), ("Place", "crew-planner--madswan"),
                                    ("Host", "deneb"), ("Took", "ask/1"), ("Took", "place/7@1793440000"), ("Began", "2026-10-31T10:10:00Z")] + end))
    plan.checked({"asks.rec": pl.text(), "roles.rec": w.files["roles.rec"]})
    assert [r.get("Role") for r in plan.Plan(w.files["roles.rec"]).recs("Role")] == ["planner", "ops"]


@pytest.mark.parametrize("path, drop, field, value", [
    ("asks.rec", "Role", None, None), ("asks.rec", None, "What", "nudge"), ("asks.rec", None, "Id", "one"), ("asks.rec", "At", None, None),
    ("roles.rec", "Stream", None, None), ("roles.rec", None, "Effort", "fast"), ("roles.rec", None, "Role", "dispatcher")])
def test_an_ask_or_a_role_record_the_headers_do_not_allow_is_refused(path, drop, field, value):
    """role-runs, A malformed ask: an ask with no Role, of a kind the enum does not hold, numbered with no number or with
    no time, and a role record with no stream, an effort or a role crew has no kind for, each refused by recfix, so the
    write commits nothing (plan.1)."""
    w = an_asks_write()
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "tell", "madswan-design", words="Go.")
    pl = plan.Plan(w.files[path])
    rec = pl.recs("Ask" if path == "asks.rec" else "Role")[0]
    if drop:
        rec.drop(drop)
    else:
        rec.set(field, value)
    with pytest.raises(Refusal, match=f"^{path} fails recfix --check"):
        plan.checked({path: pl.text()})


def test_a_started_bolt_is_marked_flume_and_no_other_path_passes():
    """crew bolt start marks its bolt Path: flume (Decision 14 of the-team-machinery-leaves): plan.checked takes it, and
    refuses a Path the Bolt set's enum does not hold (plan.1)."""
    bolt = "Bolt: x\nRepo: crew\nGoal: Start.\nPath: flume\n\n"
    text = plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit")
    plan.recfix(text, "plan.rec")
    assert [b.get("Path") for b in plan.Plan(text).bolts()] == ["flume"]
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(text.replace("Path: flume", "Path: other"), "plan.rec")


def test_a_new_branch_allows_no_team_or_agreement_and_an_old_branchs_records_still_pass():
    """bolt-plan (Decision 9 of the-team-machinery-leaves): a new state branch's descriptors (HEADER, PROPOSALS) allow
    no Bolt's Team and no Proposal's Agreed, so recfix --check refuses a record that carries one; a branch whose own
    descriptor allows Team keeps allowing it when crew brings it in step (plan.in_step, still_allowed), so a bolt still
    carrying Team passes, nothing stripped from it (plan.1, state.2)."""
    bolt = "Bolt: x\nRepo: crew\nGoal: Start.\nTeam: crw-4\nPath: flume\n\n"
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit"), "plan.rec")
    proposal = "\nProposal: 1\nCase: Why.\nDo: bolt start x\nAgreed: crw-4-conductor\nState: open\nOpened: 2026-10-31\nBy: madswan-planner\n"
    with pytest.raises(Refusal, match="^proposals.rec fails recfix --check"):
        plan.recfix(plan.PROPOSALS + proposal, "proposals.rec")
    old = plan.Plan(plan.HEADER.replace("%allowed: Bolt Repo Goal Source Path", "%allowed: Bolt Repo Goal Team Source Path")
                    .replace("%rec: Unit", bolt + "%rec: Unit"))
    assert not plan.in_step(old) or "Team" in old.text()
    plan.recfix(old.text(), "plan.rec")
    assert [b.get("Team") for b in old.bolts()] == ["crw-4"]


def launch_rec(n, work="unit/a", after=(), **more):
    """A kit's launch request as plan.request writes it (runner.request_fields), naming its repository and no host or
    stream, its brief over two lines."""
    given = dict(Repo="afterthought/crew", Kind="change", Name=work.split("/")[-1], Base="bolt/b",
                 Priority=2, Intent="madswan/b", Recipient="madswan/planner", After=list(after), Brief="Build a.\nSource: a.md", **more)
    return plan.Rec("Request", runner.request_fields(n, "launch", work, given, "2026-10-31T12:00:00Z", "madswan-dispatch-deneb"))


def requests_text(*recs):
    return runner.REQUESTS + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)


def test_requests_of_every_act_pass_and_the_descriptor_refuses_what_it_does_not_allow():
    """plan.request appends each act's request to requests.rec, and land checks the file by recfix with the plan write
    (runner.REQUESTS; Decision 4 of teams-cross-to-flume-as-their-bolts-land, plan.1): a launch with its brief over two
    lines and its After, a retry with a stage and words, a retry of the submission, a drop, a priority and a role's chore
    launch on main at priority 0 (runner.role_launch; Decision 10 of roles-run-as-flume-kinds) pass; an act, a kind or a
    hold the enums do not hold, a number that is no number and a date that is none are refused."""
    other = lambda n, act, **g: plan.Rec("Request", runner.request_fields(n, act, "unit/a", g, "2026-10-31T12:00:00Z", "madswan-planner"))
    (_, work, given), _ = runner.role_launch([], {"afterthought/crew"}, "madswan", "design", "deneb", "madswan-main", "afterthought/crew",
                                             "record-0053", "Write docs/adr/0053.md whole:\n# 53. Roles run as kinds")
    role_land = plan.Rec("Request", runner.request_fields(7, "launch", work, given, "2026-10-31T12:00:00Z", "madswan-design"))
    text = requests_text(launch_rec(1, "unit/a"), launch_rec(2, "unit/b", after=[1]), other(3, "retry", Of=1, Stage="construct", Words="Read it again."),
                         other(4, "retry", Of=1, Submission=True), other(5, "drop", Of=2), other(6, "priority", Of=1, Priority=5), role_land)
    plan.checked({"requests.rec": text})
    assert [r.get("Act") for r in plan.Plan(text).recs("Request")] == ["launch", "launch", "retry", "retry", "drop", "priority", "launch"]
    assert [(r.get("Work"), r.get("Kind"), r.get("Base"), r.get("Priority")) for r in plan.Plan(text).recs("Request")][-1] == (
        "role/design/record-0053", "chore", "main", "0")
    assert plan.Plan(text).recs("Request")[0].get("Brief") == "Build a.\nSource: a.md"
    for right, wrong in (("Act: priority", "Act: reorder"), ("Kind: change", "Kind: spike"), ("Submission: yes", "Submission: maybe"),
                         ("Request: 6", "Request: six"), ("Date: 2026-10-31T12:00:00Z", "Date: soon"), ("Of: 2", "Of: 2\nTeam: crw-4")):
        with pytest.raises(Refusal, match="^requests.rec fails recfix --check"):
            plan.checked({"requests.rec": text.replace(right + "\n", wrong + "\n", 1)})


def test_a_runners_branch_files_pass_by_their_descriptors_and_an_outcome_they_do_not_allow_is_refused():
    """What a runner writes on <label>/runner/<host>, as crew reads it (runner.RUNNER, ANSWERS, PLACES, RUNS; plan.runners
    checks each by recfix before host_read reads it): the runner's record, an answer per request, a place whose Status
    is Flume's answer on one line and, after the places, a role's run keyed by its address, one holding only the
    runner's words, pass; an Outcome the enum does not hold is refused."""
    status = json.dumps({"status": {"places": [{"place": "/kit/places/change--a", "phase": "live"}], "host": {}}})
    files = {"runner.rec": runner.RUNNER + "\nHost: deneb\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n",
             "answers.rec": runner.ANSWERS + "\nRequest: 1\nOutcome: launched\nPlace: /kit/places/change--a\nAt: 2026-10-31T12:01:00Z\n"
                            "\nRequest: 2\nOutcome: held\nAt: 2026-10-31T12:01:00Z\n",
             "places.rec": runner.PLACES + f"\nRequest: 1\nPlace: /kit/places/change--a\nAt: 2026-10-31T12:02:00Z\nStatus: {status}\n"
                           "\n" + runner.RUNS + "\nAddress: madswan/design\nAt: 2026-10-31T12:03:00Z\nWords: no stream madswan-main\n"
                           f"\nAddress: madswan/planner\nPlace: /flume/places/crew-planner--madswan\nAt: 2026-10-31T12:03:00Z\nStatus: {status}\n"}
    plan.checked(files)
    assert json.loads(plan.Plan(files["places.rec"]).recs("Place")[0].get("Status")) == json.loads(status)
    assert [r.get("Address") for r in plan.Plan(files["places.rec"]).recs("Run")] == ["madswan/design", "madswan/planner"]
    with pytest.raises(Refusal, match="^answers.rec fails recfix --check"):
        plan.checked({"answers.rec": files["answers.rec"].replace("Outcome: held", "Outcome: queued")})


def launch_of_a(w, **more):
    """A change function's request: a launch of unit a on bolt b in its repository, as a start appends it."""
    return plan.request(w, "launch", "unit/a", **dict(dict(Repo="afterthought/crew", Kind="change", Name="a", Base="bolt/b",
                        Priority=1, Intent="madswan/b", Recipient="madswan/planner", Brief="Build a."), **more))


def test_a_request_is_written_in_the_commit_of_the_plan_write_that_occasions_it_and_a_refused_one_pushes_nothing(state, monkeypatch):
    """plan.write commits requests.rec with the plan, one commit and one Crew-Entry (state.1, plan.2); a request crew's
    rules refuse, one recfix refuses and a write that changes a request the branch holds each refuse the whole write,
    and the branch is as it was (Decision 4 of teams-cross-to-flume-as-their-bolts-land)."""
    monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")
    ref = f"{state.LABEL}/main"
    before = state.git("rev-parse", ref)

    def start(w):
        w.plan.insert(plan.Rec("Bolt", [("Bolt", "b"), ("Repo", "afterthought/crew"), ("Goal", "Start."), ("Path", "flume")]))
        assert launch_of_a(w) == 1
        return []
    sha = plan.write(state.fleet, state.LABEL, start, "plan(b): start the bolt")
    assert state.git("rev-parse", ref) == sha and state.git("rev-list", "--count", f"{before}..{sha}") == "1"
    assert state.git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).split() == ["plan.rec", "requests.rec"]
    assert len(state.git("log", "-1", "--format=%(trailers:key=Crew-Entry,valueonly)", sha).split()) == 1
    held = state.git("show", f"{sha}:requests.rec")
    assert held.startswith(runner.REQUESTS.split("\n")[0]) and "Request: 1\nAct: launch\nWork: unit/a\n" in held

    for change, said in ((lambda w: launch_of_a(w, Stream="madswan"), "names a Host or a Stream"),
                         (lambda w: launch_of_a(w, Priority="high"), "^requests.rec fails recfix --check"),
                         (lambda w: w.replace("requests.rec", w.text("requests.rec").replace("Name: a", "Name: b")), "request 1 would be changed")):
        with pytest.raises(Refusal, match=said):
            plan.write(state.fleet, state.LABEL, lambda w: change(w) and [], "plan: ask again")
        assert state.git("rev-parse", ref) == sha


def madswan_plan():
    """madswan's plan.rec as afterthought/crew-state held it on 2026-11-05, under crew's descriptors (plan.HEADER): 21
    Bolt and Unit records in tailrace, the started bolt you-sign-in-to-staging and its unit in flywheel-cloud, and a
    bolt of timber's own whose goal a tailrace bolt shares."""
    bolt = lambda b, repo, goal, path=None: f"Bolt: {b}\nRepo: {repo}\nGoal: {goal}\n" + (f"Path: {path}\n" if path else "") + "\n"
    unit = lambda u, repo, b: f"Unit: {u}\nRepo: {repo}\nBolt: {b}\nIntent: {u} is built.\n\n"
    bolts = "".join(bolt(f"trc-{n}", "tailrace", f"Goal {n}.") for n in (1, 2, 3)) + bolt("you-sign-in-to-staging", "flywheel-cloud", "Sign in.", "flume")
    bolts += bolt("timber-own", "timber", "Goal 1.")
    units = "".join(unit(f"tailrace-work-{n}", "tailrace", f"trc-{1 + n % 3}") for n in range(18))
    units += unit("one-seam-turns-every-credential-into-a-principal", "flywheel-cloud", "you-sign-in-to-staging")
    return plan.HEADER.replace("%rec: Unit", bolts + "%rec: Unit") + "\n" + units


def renamed_fleet(state):
    """madswan's fleet with its main level on deneb, whose spaces keep agentplot/timber and no tailrace."""
    return dict(state.fleet, partitions={state.LABEL: dict(state.fleet["partitions"][state.LABEL], machine="deneb")},
                hosts={"deneb": {"sessions": {"main": {"dir": "/d", "repos": ["agentplot/timber", "agentplot/boomdrive-cloud"]}}}})


def a_rename(state, monkeypatch):
    """crew kit rename tailrace timber, run by the user on deneb over madswan's plan: the fleet crew reads, the
    entry's push to the branch (record.reach) among it, and the command's arguments."""
    import argparse
    import crew
    import record
    fleet = renamed_fleet(state)
    monkeypatch.setenv("CREW_AGENT", "")
    monkeypatch.setenv("CREW_SESSION", "")
    monkeypatch.setattr(crew, "load", lambda: fleet)
    monkeypatch.setattr(crew, "this_host", lambda: "deneb")
    monkeypatch.setattr(record, "_session", ...)
    state.push(f"{state.LABEL}/main", {"plan.rec": madswan_plan()}, "plan: madswan's plan (chuck@deneb)")
    return fleet, argparse.Namespace(cmd="kit", sub="rename", old="tailrace", new="timber", label=state.LABEL)


def test_a_rename_is_one_commit_whose_plan_passes_recfix_and_its_entry_names_both_names(state, monkeypatch):
    """Decision 2 of a-kit-renamed-on-its-host-is-renamed-across-the-plan (plan.1, plan.2, state.1): the user's crew kit
    rename tailrace timber is one commit of plan.rec alone, under its Crew-Entry, the plan it leaves passing a real
    recfix --check with every tailrace record naming timber, two bolts of one goal now under one name among them, since
    %unique holds a field once within a record and not across records; its kit.rename entry, the commit after on the
    branch (read.5), names kit/timber and kit/tailrace with Repo timber and Count 21."""
    import datetime
    import record
    fleet, a = a_rename(state, monkeypatch)
    ref = f"{state.LABEL}/main"
    before = state.git("rev-parse", ref)
    plan.COMMANDS[("kit", "rename")](fleet, a)
    commits = state.git("rev-list", "--reverse", f"{before}..{ref}").split()
    assert len(commits) == 2
    sha, entry = commits
    assert state.git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).split() == ["plan.rec"]
    assert state.git("log", "-1", "--format=%s", sha) == f"plan(kit): rename tailrace timber ({plan.agent()})"
    eid = state.git("log", "-1", "--format=%(trailers:key=Crew-Entry,valueonly)", sha).strip()
    text = state.git("show", f"{sha}:plan.rec")
    plan.recfix(text, "plan.rec")
    p = plan.Plan(text)
    assert [r.name() for r in p.bolts() + p.work() if r.get("Repo") == "timber"][:4] == ["trc-1", "trc-2", "trc-3", "timber-own"]
    assert sum(1 for r in p.bolts() + p.work() if r.get("Repo") == "timber") == 22 and "Repo: tailrace" not in text
    assert [(b.get("Repo"), b.get("Path")) for b in p.bolts() if b.name() == "you-sign-in-to-staging"] == [("flywheel-cloud", "flume")]
    day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    e, = [e for e in record.parse(state.git("show", f"{entry}:runs/deneb/{day}.rec")) if e["Id"] == eid]
    assert (e["Act"], e["On"], e["From"], e["Repo"], e["Count"], e.get("Refused")) == (
        "kit.rename", ["kit/timber"], ["kit/tailrace"], "timber", "21", None)
    assert plan.renames_in([e]) == [("tailrace", "timber")]


def test_a_rename_whose_plan_breaks_unique_repo_goal_is_refused_before_any_commit(state, monkeypatch):
    """plan.1: the plan a rename leaves goes through a real recfix --check before land commits it, so one that would
    hold a record naming its Repo twice, against %unique: Repo Goal, is refused, the branch as it was."""
    fleet, a = a_rename(state, monkeypatch)
    ref = f"{state.LABEL}/main"
    before = state.git("rev-parse", ref)
    op = plan.op_kit_rename(plan.Direct(fleet, a), a)

    def twice(w):
        op.change(w)
        w.plan.bolt("trc-1").add("Repo", "tailrace")
        return []
    with pytest.raises(Refusal, match=r"^plan.rec fails recfix --check: .*field 'Repo' should be unique in this record"):
        plan.write(fleet, state.LABEL, twice, op.subject, act=op.act, on=op.on, frm=op.frm, fields=op.fields)
    assert state.git("rev-parse", ref) == before
