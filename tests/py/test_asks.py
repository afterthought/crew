"""What waits on a main-level role that runs as its kind (the role-runs spec; design Decisions 4 to 7): asks.rec read
into asks and turns, every field guarded; what is pending for a role, its asks and the places that wait on it that no
ended turn took, and whether it is wanted, so a burst is one run and an ask during a run waits for the next; a lost
run's open turn superseded and its asks taken again; an ask's key already held; the next numbers; the places the
runner's records show waiting on a role, read from Flume's status; and the role records the teams file makes due.
That crew writes asks.rec and roles.rec on the branch and recfix holds them is the contract tier's (test_recfix)."""
import json
import re

import pytest

import asks

ASKS = """\
%rec: Ask
%key: Id

Id: 1
Role: planner
From: madswan-design
What: tell
Words: record 0053 is accepted
+ and its rule amended
At: 2026-10-31T10:00:00Z

Id: 2
Role: planner
From: crew
What: card
Names: proposal/12
Key: card/req_1/2026-10-31T10:04:00Z
At: 2026-10-31T10:04:10Z

Id: 3
Role: design
From: madswan-planner
What: tell
Words: read batch 4
At: 2026-10-31T10:05:00Z

Id: x
Role: planner
From: crew
What: tell
At: 2026-10-31T10:06:00Z

Id: 4
From: crew
What: tell
At: 2026-10-31T10:07:00Z

%rec: Turn
%key: Turn

Turn: 1
Role: planner
Run: madswan-planner
Place: crew-planner--madswan
Host: deneb
Took: ask/1
Took: place/7@1793440000
Began: 2026-10-31T10:01:00Z
"""


def ask(n, role="planner", key=None):
    return dict({"Id": str(n), "Role": role, "From": "crew", "What": "tell", "At": "2026-10-31T10:00:00Z"}, **({"Key": key} if key else {}))


def turn(n, took, ended=False, superseded=None, role="planner", label="madswan"):
    t = {"Turn": str(n), "Role": role, "Run": f"{label}-{role}", "Place": f"crew-{role}--{label}", "Host": "deneb", "Took": list(took),
         "Began": "2026-10-31T10:00:00Z"}
    if ended:
        t.update(Ended="2026-10-31T10:10:00Z", Said="done")
    if superseded:
        t["Superseded"] = str(superseded)
    return t


class TestParse:
    def test_asks_and_turns_are_read_with_their_fields_and_a_record_with_no_number_or_role_left_out(self):
        got, turns = asks.parse(ASKS)
        assert [a["Id"] for a in got] == ["1", "2", "3"]
        assert got[0]["Words"] == "record 0053 is accepted\nand its rule amended" and "Words" not in got[1]
        assert (got[1]["Names"], got[1]["Key"]) == ("proposal/12", "card/req_1/2026-10-31T10:04:00Z")
        t, = turns
        assert (t["Turn"], t["Run"], t["Took"], t.get("Ended")) == ("1", "madswan-planner", ["ask/1", "place/7@1793440000"], None)

    def test_a_branch_with_no_asks_file_holds_no_ask_and_no_turn(self):
        assert asks.parse(None) == ([], []) and asks.parse("") == ([], []) and asks.parse_roles(None) == []


class TestPending:
    def test_a_burst_of_three_asks_is_one_run_taking_all_three(self):
        """role-runs, A burst: three asks of madswan's planner written within a minute, no run of it standing."""
        three = [ask(1), ask(2), ask(3)]
        mine, places = asks.pending(three, [], [], "planner")
        assert [a["Id"] for a in mine] == ["1", "2", "3"] and places == []
        assert asks.wanted(three, [], [], "planner") and asks.took(mine, places) == ["ask/1", "ask/2", "ask/3"]

    def test_an_ask_written_during_a_run_is_still_pending_once_its_turn_ends(self):
        """role-runs, An ask during a run: the run took two, a third came before it ended."""
        three = [ask(1), ask(2), ask(3)]
        running = [turn(1, ["ask/1", "ask/2"])]
        assert [a["Id"] for a in asks.pending(three, [], running, "planner")[0]] == ["1", "2", "3"]
        ended = [turn(1, ["ask/1", "ask/2"], ended=True)]
        assert [a["Id"] for a in asks.pending(three, [], ended, "planner")[0]] == ["3"] and asks.wanted(three, [], ended, "planner")

    def test_a_role_whose_every_ask_an_ended_turn_took_is_not_wanted(self):
        """role-runs, Nothing pending."""
        assert not asks.wanted([ask(1), ask(2)], [], [turn(1, ["ask/1"], ended=True), turn(2, ["ask/2"], ended=True)], "planner")
        assert not asks.wanted([], [], [], "planner")

    def test_asks_of_another_role_are_not_pending_for_this_one_and_come_oldest_first(self):
        mixed = [ask(4), ask(2, "design"), ask(10), ask(3)]
        assert [a["Id"] for a in asks.pending(mixed, [], [], "planner")[0]] == ["3", "4", "10"]
        assert [a["Id"] for a in asks.pending(mixed, [], [], "design")[0]] == ["2"]
        assert not asks.wanted(mixed, [], [turn(1, ["ask/2"], ended=True, role="design")], "design")

    def test_a_place_that_waits_on_the_role_is_pending_until_an_ended_turn_takes_it(self):
        wait = ("place/7@1793440000", "7", "unit/a", "/kit/places/change--a", "Which bolt?")
        assert asks.pending([], [wait], [], "planner") == ([], [wait]) and asks.wanted([], [wait], [], "planner")
        assert asks.took([], [wait]) == ["place/7@1793440000"]
        assert asks.pending([], [wait], [turn(1, ["place/7@1793440000"])], "planner") == ([], [wait])
        assert not asks.wanted([], [wait], [turn(1, ["place/7@1793440000"], ended=True)], "planner")
        again = ("place/7@1793443600",) + wait[1:]
        assert asks.pending([], [again], [turn(1, ["place/7@1793440000"], ended=True)], "planner") == ([], [again])


class TestTurns:
    def test_a_lost_runs_open_turn_is_superseded_by_the_next_start_and_its_asks_taken_again(self):
        """role-runs, A run that was lost: its turn took an ask and never ended; the retried run's start supersedes it."""
        lost = [turn(1, ["ask/1"])]
        assert [t["Turn"] for t in asks.superseded(lost, "madswan-planner")] == ["1"]
        assert [a["Id"] for a in asks.pending([ask(1)], [], lost, "planner")[0]] == ["1"]
        gone = [turn(1, ["ask/1"], superseded=2), turn(2, ["ask/1"])]
        assert [a["Id"] for a in asks.pending([ask(1)], [], gone, "planner")[0]] == ["1"]
        assert asks.open_turn(gone, "madswan-planner")["Turn"] == "2" and asks.superseded(gone, "madswan-planner") == [gone[1]]

    def test_a_run_with_no_open_turn_has_none_to_end(self):
        assert asks.open_turn([], "madswan-planner") is None
        assert asks.open_turn([turn(1, ["ask/1"], ended=True), turn(2, [], superseded=3)], "madswan-planner") is None
        assert asks.open_turn([turn(1, ["ask/1"])], "swancloud-planner") is None

    def test_the_next_numbers_follow_the_highest_on_the_branch(self):
        assert (asks.next_id([]), asks.next_turn([])) == (1, 1)
        assert (asks.next_id([ask(2), ask(9), ask(3)]), asks.next_turn([turn(4, []), turn(1, [])])) == (10, 5)


class TestKeyed:
    def test_one_answer_seen_twice_is_one_ask(self):
        """role-runs, One answer seen twice: deneb's and mac-studio's followers sweep the same answer of proposal 12's card."""
        key = "card/req_1/2026-10-31T10:04:00Z"
        written = [ask(1), ask(2, key=key)]
        assert asks.keyed(written, key)["Id"] == "2"
        assert asks.keyed(written, "card/req_1/2026-10-31T11:00:00Z") is None

    def test_a_key_is_its_roles_own_so_one_landing_asks_the_planner_and_the_design_agent(self):
        """role-runs, A landing: one ask of the planner and one of the design agent, each keyed by the bolt."""
        written = [ask(1, key="landed/b")]
        assert asks.keyed(written, "landed/b", "planner")["Id"] == "1"
        assert asks.keyed(written, "landed/b", "design") is None
        assert asks.keyed(written, "landed/b")["Id"] == "1"

    def test_an_ask_with_no_key_is_never_held(self):
        assert asks.keyed([ask(1)], None) is None and asks.keyed([dict(ask(1), Key="")], "") is None


PLANNER = {"model": "claude-fable-5-1", "effort": "xhigh"}
OPS = {"model": "claude-opus-5-5[1m]", "effort": "high"}
FALSE = dict.fromkeys(("design", "planner", "reviewer", "ops", "operator"), False)


def madswan(**flume):
    return {"label": "madswan", "machine": "deneb", "blueprints": ["afterthought/blueprints", "afterthought/flywheel-web"], "roles": {},
            "flume": dict(FALSE, **flume)}


class TestRoleRecords:
    def test_the_planners_record_names_its_run(self):
        """role-runs, The planner's record."""
        assert asks.role_record(madswan(planner="madswan-main"), "planner", PLANNER) == {
            "Role": "planner", "Address": "madswan/planner", "Run": "madswan-planner", "Host": "deneb", "Repository": "afterthought/blueprints",
            "Kinds": "crew", "Kind": "crew-planner", "Name": "madswan", "Stream": "madswan-main", "Priority": "0", "Intent": "madswan-planner",
            "Model": "claude-fable-5-1", "Effort": "xhigh"}

    def test_a_role_that_stands_has_no_record(self):
        assert asks.role_record(madswan(), "planner", PLANNER) is None

    def test_a_runs_model_is_its_definitions_after_the_teams_files_override(self):
        """role-runs, An override: wldn sets roles.planner.model; main-ops's override is read for ops."""
        wldn = dict(madswan(planner="wldn-main", ops="wldn-main"), label="wldn", machine="chuck-herdr-alpha",
                    roles={"planner": {"model": "claude-opus-5-5[1m]"}, "main-ops": {"effort": "max"}})
        assert (asks.role_record(wldn, "planner", PLANNER)["Model"], asks.role_record(wldn, "planner", PLANNER)["Effort"]) == ("claude-opus-5-5[1m]", "xhigh")
        assert (asks.role_record(wldn, "ops", OPS)["Model"], asks.role_record(wldn, "ops", OPS)["Effort"]) == ("claude-opus-5-5[1m]", "max")
        assert asks.role_record(madswan(planner="m"), "planner", PLANNER)["Model"] == "claude-fable-5-1"
        assert asks.definition_of("ops") == "main-ops" and asks.definition_of("design") == "design"

    def test_the_records_due_are_those_missing_or_differing_and_a_role_that_stands_again_goes(self):
        """role-runs, The planner moves, An ask before main up and The planner stands again."""
        p = madswan(planner="madswan-main", ops="madswan-main")
        metas = {"planner": PLANNER, "ops": OPS}
        planner, ops = asks.role_record(p, "planner", PLANNER), asks.role_record(p, "ops", OPS)
        assert asks.roles_due([], p, metas) == ([planner, ops], [])
        assert asks.roles_due([planner, ops], p, metas) == ([], [])
        assert asks.roles_due([dict(planner, Stream="old"), ops], p, metas) == ([planner], [])
        assert asks.roles_due([planner, ops], madswan(ops="madswan-main"), {"ops": OPS}) == ([], ["planner"])

    def test_role_records_are_read_from_their_file(self):
        text = "%rec: Role\n%key: Role\n\nRole: planner\nStream: madswan-main\n\nStream: none\n"
        assert asks.parse_roles(text) == [{"Role": "planner", "Stream": "madswan-main"}]


def status(**place):
    """flume status --json <place> as the runner carries it: one place."""
    return json.dumps({"status": {"places": [dict({"place": "/kit/places/change--a", "phase": "live", "waiting_on": None, "stalled": False}, **place)],
                                  "host": {}}})


def launch(n, work="unit/a", recipient="madswan/planner", act="launch"):
    return {"Request": str(n), "Act": act, "Work": work, "Recipient": recipient}


class TestWaitsOn:
    def test_a_stage_that_stopped_short_asking_waits_on_the_planner(self):
        """role-runs, A stage asks the planner: a construct stopped short asking which bolt a finding belongs in."""
        on = {"act": "retry", "stage": "construct", "why": "answer", "since": 1793440000, "words": "Which bolt does the finding belong in?"}
        got = asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Place": "/kit/places/change--a", "Status": status(waiting_on=on)}])
        assert got == [("place/7@1793440000", "7", "unit/a", "/kit/places/change--a", "Which bolt does the finding belong in?")]
        assert asks.waits_on("madswan/design", [launch(7)], [{"Request": "7", "Status": status(waiting_on=on)}]) == []

    def test_a_stage_that_delivers_waits_on_nobody(self):
        """role-runs, A stage that delivers: a construct delivered and its code started."""
        assert asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Status": status()}]) == []
        done = {"act": "done", "stage": None, "why": "delivered", "since": 1793440000, "words": None}
        assert asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Status": status(waiting_on=done)}]) == []

    def test_a_lost_agent_a_place_past_its_bound_a_held_submission_and_a_stalled_wait_are_the_roles(self):
        def wait(why, stage="code", stalled=False):
            on = {"act": "retry", "stage": stage, "why": why, "since": 1793440000, "words": None}
            return asks.waits_on("madswan/ops", [launch(3, "fix/main/crew/red", "madswan/ops")],
                                 [{"Request": "3", "Place": "/p", "Status": status(waiting_on=on, stalled=stalled)}])
        for why in ("lost", "past_bound"):
            assert wait(why) == [("place/3@1793440000", "3", "fix/main/crew/red", "/p", None)]
        assert wait("on_hold", stage=None) != [] and wait("on_hold", stage="code") == []
        assert wait("never_begun") == [] and wait("never_begun", stalled=True) != []

    def test_a_place_a_role_launched_is_pending_for_it_once_it_has_landed(self):
        """role-runs, A record lands: the chore madswan's design run launched for record 0053."""
        landed = {"over": {"over": {"landed": {"commit": "abcdef1234567"}}, "kept": None}}
        req = launch(9, "role/design/record-0053", "madswan/design")
        assert asks.waits_on("madswan/design", [req], [{"Request": "9", "Place": "/crew/places/chore--record-0053", "Status": status(phase=landed)}]) == [
            ("landed/9", "9", "role/design/record-0053", "/crew/places/chore--record-0053", "landed at abcdef1")]
        tidied = {"tidied": {"over": {"landed": {"commit": None}}, "at": 1793440000, "pending_for": []}}
        assert asks.waits_on("madswan/design", [req], [{"Request": "9", "Status": status(phase=tidied)}])[0][4] == "landed"
        assert asks.waits_on("madswan/design", [req], [{"Request": "9", "Status": status(phase="live")}]) == []
        assert asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Status": status(phase=landed)}]) == []

    def test_a_field_flume_left_out_never_becomes_text_and_a_status_that_cant_be_read_is_no_wait(self):
        on = {"act": "retry", "stage": "construct", "why": "answer"}
        got, = asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Status": json.loads(status(waiting_on=on))}])
        assert got == ("place/7", "7", "unit/a", "/kit/places/change--a", None)
        for bad in ("not json", json.dumps({"status": {"places": []}}), None):
            assert asks.waits_on("madswan/planner", [launch(7)], [{"Request": "7", "Status": bad}]) == []

    def test_only_a_launch_naming_the_role_counts_and_places_come_oldest_request_first(self):
        on = json.dumps({"place": "/p", "waiting_on": {"why": "answer", "since": 5}})
        reqs = [launch(12), launch(3), launch(4, act="retry"), launch(5, recipient="madswan/ops")]
        places = [{"Request": n, "Place": f"/p{n}", "Status": on} for n in ("12", "3", "4", "5", "99")]
        assert [w[1] for w in asks.waits_on("madswan/planner", reqs, places)] == ["3", "12"]


MADSWAN = {"partitions": {"madswan": madswan(planner="madswan-main")}, "teams": {}, "hosts": {}}


@pytest.fixture
def deneb(monkeypatch):
    import crew
    monkeypatch.setattr(crew, "this_host", lambda: "deneb")


def written(files=None):
    from facts import FactsWrite
    w = FactsWrite("", files)
    w.label = "madswan"
    return w


@pytest.mark.usefixtures("deneb")
class TestWrite:
    """plan.ask_rec, ask_lines, ask_write and roles_lines: what a write of an ask puts in asks.rec and roles.rec, and how
    the commit names it (design Decision 4; plan.2). That recfix holds the files to their headers is test_recfix's."""

    def test_the_first_ask_starts_asks_rec_and_writes_its_roles_record_beside_it(self):
        """role-runs, An ask before main up: the ask's commit holds the planner's record too."""
        import plan
        w = written()
        rec = plan.ask_rec(w, MADSWAN, "madswan", "planner", "tell", "madswan-design", words="record 0053\nis accepted")
        got, turns = asks.parse(w.files["asks.rec"])
        assert w.files["asks.rec"].startswith(plan.ASKS.split("\n\n")[0]) and turns == []
        assert [(a["Id"], a["Role"], a["From"], a["What"], a["Words"]) for a in got] == [("1", "planner", "madswan-design", "tell", "record 0053\nis accepted")]
        assert rec.get("Id") == "1" and "Key" not in got[0] and "Names" not in got[0]
        assert asks.parse_roles(w.files["roles.rec"]) == [asks.role_record(MADSWAN["partitions"]["madswan"], "planner", PLANNER)]
        assert plan.ask_rec(w, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/t").get("Id") == "2"
        assert [a["Id"] for a in asks.parse(w.files["asks.rec"])[0]] == ["1", "2"]

    def test_an_ask_whose_key_the_tip_holds_writes_nothing(self):
        """role-runs, One answer seen twice: the second write finds the key and leaves every file as it was."""
        import plan
        w = written()
        plan.ask_rec(w, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/t")
        again = written(dict(w.files))
        assert plan.ask_rec(again, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/t") is None
        assert again.files == w.files

    def test_an_ask_in_its_acts_commit_is_named_beside_the_acts_entry_and_a_held_key_is_kept_to_say(self):
        import plan
        w = written()
        rec = plan.ask_lines(w, MADSWAN, "madswan", "planner", "landed", "crew", names="bolt/b", key="landed/b")
        assert [r for _, r in w.asked] == [rec] and w.asked[0][0] and w.held == []
        assert plan.ask_lines(w, MADSWAN, "madswan", "planner", "landed", "crew", names="bolt/b", key="landed/b") is None
        assert len(w.asked) == 1 and w.held == [("madswan-planner", "landed/b")]

    def test_roles_rec_follows_the_teams_file_and_a_branch_with_nothing_due_gets_none(self):
        """role-runs, The planner moves and The planner stands again."""
        import plan
        w = written()
        assert plan.roles_lines(w, MADSWAN, "madswan") and [r["Role"] for r in asks.parse_roles(w.files["roles.rec"])] == ["planner"]
        assert not plan.roles_lines(w, MADSWAN, "madswan")
        moved = {"partitions": {"madswan": madswan(planner="madswan-main", ops="madswan-ops")}}
        assert not plan.roles_lines(w, moved, "madswan", ["planner"])
        assert plan.roles_lines(w, moved, "madswan") and [r["Role"] for r in asks.parse_roles(w.files["roles.rec"])] == ["planner", "ops"]
        assert asks.parse_roles(w.files["roles.rec"])[1]["Model"] == "claude-opus-5-5[1m]"
        stood = {"partitions": {"madswan": madswan(ops="madswan-ops")}}
        assert plan.roles_lines(w, stood, "madswan") and [r["Role"] for r in asks.parse_roles(w.files["roles.rec"])] == ["ops"]
        none = written()
        assert not plan.roles_lines(none, {"partitions": {"madswan": madswan()}}, "madswan") and "roles.rec" not in none.files

    def test_a_write_names_its_acts_entry_and_each_asks_and_emits_the_asks_after_the_act(self, monkeypatch, capsys):
        """plan.2: the commit's Crew-Entry trailers name the act's entry and the ask's, and each is emitted once pushed."""
        import plan
        import record
        made, emitted = [], []
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("afterthought/madswan-state", f"{label}/main"))
        monkeypatch.setattr(plan, "read", lambda repo, ref, tip: plan.Plan(""))
        monkeypatch.setattr(plan, "show", lambda repo, tip, path: None)
        monkeypatch.setattr(plan, "land", lambda repo, ref, path, make: made.append(make("t" * 40)) or "c" * 40)
        monkeypatch.setattr(plan, "notify", lambda fleet, seen, subject: None)
        monkeypatch.setattr(record, "emit", lambda label, act, on=(), frm=(), commit=(), why=None, eid=None, **f: emitted.append((act, on, eid, f)))
        monkeypatch.setattr(plan, "agent", lambda: "madswan-ops")

        def change(w):
            plan.ask_lines(w, MADSWAN, "madswan", "planner", "landed", "crew", names="bolt/b", key="landed/b")
            return []
        plan.write(MADSWAN, "madswan", change, "plan(b): land the bolt", act="bolt.land", on=["bolt/b"])
        (files, msg), = made
        eids = [l.split(": ", 1)[1] for l in msg.splitlines() if l.startswith("Crew-Entry: ")]
        assert len(eids) == 2 and "asks.rec" in files and "roles.rec" in files
        assert [(a, on, eid) for a, on, eid, _ in emitted] == [("bolt.land", ["bolt/b"], eids[0]), ("ask", ["agent/madswan-planner", "bolt/b"], eids[1])]
        assert "asked madswan-planner: landed on bolt/b" in capsys.readouterr().out

    def test_an_ask_alone_whose_key_is_held_commits_nothing_and_says_so(self, monkeypatch, capsys):
        import plan
        held = written()
        plan.ask_rec(held, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/t")
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("afterthought/madswan-state", f"{label}/main"))
        monkeypatch.setattr(plan, "read", lambda repo, ref, tip: plan.Plan(""))
        monkeypatch.setattr(plan, "show", lambda repo, tip, path: held.files.get(path))
        monkeypatch.setattr(plan, "land", lambda repo, ref, path, make: make("t" * 40) and "c" * 40)
        assert plan.ask_write(MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/t") is None
        assert capsys.readouterr().out == "madswan/main: madswan-planner is already asked by card/req_1/t; nothing written\n"

    def test_an_asks_entry_holds_the_length_of_its_words_and_never_their_text(self):
        import record
        assert record.ask_entry("madswan-planner", "tell", None, "x" * 40) == dict(act="ask", on=["agent/madswan-planner"], why="ask madswan-planner: tell", Chars=40)
        assert record.ask_entry("madswan-design", "capture", "signals/s/01-c")["on"] == ["agent/madswan-design", "signals/s/01-c"]
        assert record.ask_entry("madswan-planner", "open")["Chars"] is None


def as_crew_writes(asks_part, turns_part=""):
    """asks.rec as crew writes it: its header's Ask descriptor, the asks, its Turn descriptor and the turns."""
    import plan
    head, turn = plan.ASKS.split("\n%rec: Turn")
    return head + "\n" + asks_part + "\n%rec: Turn" + turn + turns_part


ASKED = """\
Id: 1
Role: planner
From: madswan-design
What: tell
Words: record 0053 is accepted
At: 2026-10-31T10:00:00Z

Id: 2
Role: planner
From: crew
What: card
Names: card/req_a1
Key: card/req_a1/3
Words: the user answered it
At: 2026-10-31T10:04:00Z

Id: 3
Role: design
From: crew
What: tell
Words: not the planner's
At: 2026-10-31T10:05:00Z
"""
TAKEN = as_crew_writes(ASKED)
LOST = as_crew_writes(ASKED, """
Turn: 1
Role: planner
Run: madswan-planner
Place: crew-planner--madswan
Host: deneb
Took: ask/1
Began: 2026-10-31T10:01:00Z
""")


class Branch:
    """madswan's flywheel branch as a role command sees it: its files, each write applied to them, and the entries each
    write emitted."""

    def __init__(self, files):
        self.files, self.writes, self.entries = dict(files), [], []


def on_branch(monkeypatch, fleet, files):
    """madswan's flywheel branch in memory holding files, each write of a command on deneb applied to it and each
    entry it emitted kept (Branch)."""
    import crew
    import plan
    import record
    monkeypatch.delenv("CREW_AGENT", raising=False)
    monkeypatch.setattr(crew, "load", lambda: fleet)
    monkeypatch.setattr(crew, "this_host", lambda: "deneb")
    b = Branch(files)
    monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("afterthought/madswan-state", f"{label}/main"))
    monkeypatch.setattr(plan, "read", lambda repo, ref, tip: plan.Plan(""))
    monkeypatch.setattr(plan, "show", lambda repo, tip, path: b.files.get(path))

    def land(repo, ref, path, make):
        files, msg = make("t" * 40)
        b.files.update({k: v for k, v in files.items() if k != "plan.rec"})
        b.writes.append(msg)
        return "c" * 40
    monkeypatch.setattr(plan, "land", land)
    monkeypatch.setattr(plan, "notify", lambda fleet, seen, subject: None)
    monkeypatch.setattr(record, "emit", lambda label, act, on=(), frm=(), commit=(), why=None, eid=None, by=None, **f:
                        b.entries.append((act, list(on), why, f)))
    monkeypatch.setattr(plan, "runner_facts", lambda fleet, label: ([], {}))
    b.fleet = fleet
    return b


@pytest.fixture
def in_run(monkeypatch, tmp_path):
    """A command run in madswan's planner's run on deneb (FLUME_PLACE crew-planner--madswan), its writes applied to a
    branch in memory, its brief kept under tmp_path and its cards read through run_cards_said, which a case steers."""
    import crew
    import plan
    import record
    fleet = {"partitions": {"madswan": madswan(planner="madswan-main")}, "teams": {}, "hosts": {}}
    monkeypatch.setenv("FLUME_PLACE", "/home/u/.local/state/flume/places/crew-planner--madswan")
    b = on_branch(monkeypatch, fleet, {"asks.rec": TAKEN})
    monkeypatch.setattr(crew, "brief", lambda fleet, scope, role, self_name="": f"the {role} brief of {scope} for {self_name}")
    monkeypatch.setattr(record, "ROOT", tmp_path / "state")
    monkeypatch.setattr(plan, "run_cards_said", lambda fleet, label, run: [f"cards read as {run}"])
    return b


def start(b):
    import argparse
    import plan
    plan.role_start(b.fleet, argparse.Namespace())


def end(b, report, words):
    import argparse
    import plan
    plan.role_end(b.fleet, argparse.Namespace(report=str(report), words=words))


class TestStart:
    """crew role start (design Decision 7; role-runs "A run's start takes everything pending", "A run's start gives its
    brief and what it took" and "A start takes again what a lost run took")."""

    def test_two_asks_waiting_are_one_turn_and_it_prints_the_brief_then_each_ask_then_the_cards(self, in_run, tmp_path, capsys):
        """role-runs, Two asks waiting and What the planner's run reads."""
        start(in_run)
        held, turns = asks.parse(in_run.files["asks.rec"])
        (t,) = turns
        assert (t["Turn"], t["Role"], t["Run"], t["Place"], t["Host"], t["Took"]) == ("1", "planner", "madswan-planner", "crew-planner--madswan", "deneb", ["ask/1", "ask/2"])
        assert "Ended" not in t and len(in_run.writes) == 1
        assert in_run.writes[0].startswith("turn(madswan-planner): 1 takes 2 (madswan-planner)\n")
        assert in_run.entries == [("turn.begin", ["agent/madswan-planner"], "turn 1 of madswan-planner", {"Took": "2"})]
        brief = tmp_path / "state/madswan/turns/planner.md"
        assert brief.read_text() == "the planner brief of madswan for madswan-planner"
        out = capsys.readouterr().out.split("\n")
        at = out.index(f"Read {brief} whole first: it is your brief as madswan-planner, filled for madswan.")
        assert out[at + 1:at + 7] == ["ask 1: tell from madswan-design", "  record 0053 is accepted",
                                      "ask 2: card from crew on card/req_a1", "  the user answered it", "cards read as madswan-planner", ""]

    def test_nothing_waiting_records_no_turn_and_says_so(self, in_run, capsys):
        """role-runs, Nothing waiting."""
        in_run.files["asks.rec"] = LOST.replace("Began:", "Ended: 2026-10-31T10:20:00Z\nSaid: done\nBegan:").replace("Took: ask/1", "Took: ask/1\nTook: ask/2")
        before = dict(in_run.files)
        start(in_run)
        assert in_run.files == before and in_run.writes == [] and in_run.entries == []
        assert "Nothing waits for madswan-planner: no turn is taken and nothing is recorded." in capsys.readouterr().out

    def test_a_start_outside_a_run_is_refused_and_writes_nothing(self, in_run, monkeypatch, tmp_path):
        """role-runs, Not a run: a change's place, and a standing agent's CREW_AGENT, are no run."""
        import crew
        for place in ("/kit/places/change--a", None):
            if place:
                monkeypatch.setenv("FLUME_PLACE", place)
            else:
                monkeypatch.delenv("FLUME_PLACE")
                monkeypatch.setenv("CREW_AGENT", "madswan-planner")
            with pytest.raises(crew.Refusal, match="crew role start runs only in a run of a crew role, in the place Flume made for it"):
                start(in_run)
        assert in_run.writes == [] and not (tmp_path / "state").exists()

    def test_a_lost_runs_open_turn_is_superseded_and_its_ask_taken_again(self, in_run, capsys):
        """role-runs, A run that was lost."""
        in_run.files["asks.rec"] = LOST
        start(in_run)
        _, turns = asks.parse(in_run.files["asks.rec"])
        assert [(t["Turn"], t.get("Superseded"), t["Took"]) for t in turns] == [("1", "2", ["ask/1"]), ("2", None, ["ask/1", "ask/2"])]
        assert asks.open_turn(turns, "madswan-planner")["Turn"] == "2"
        assert in_run.writes[0].startswith("turn(madswan-planner): 2 takes 2, superseding 1 (")
        assert "Turn 2 takes again what turn 1 took, whose run ended before its end: that turn answers nothing." in capsys.readouterr().out

    def test_a_place_that_waits_on_the_role_is_taken_and_a_runner_that_cant_be_read_is_said(self, in_run, monkeypatch, capsys):
        """role-runs, A stage asks the planner: the run takes it with its work, its place and its words."""
        import plan
        import runner
        rq = plan.Rec("Request", [("Request", "7"), ("Act", "launch"), ("Work", "unit/a"), ("Recipient", "madswan/planner")])
        stopped = json.loads(status(waiting_on={"why": "answer", "stage": "construct", "since": 1793440000, "words": "which bolt?"}))
        reads = {"deneb": {"why": None, "places": {7: {"place": "/kit/places/change--a", "at": "t", "status": stopped, "why": None}}},
                 "mac-studio": runner.host_read("madswan", "mac-studio", "abc1234", {}, {})}
        monkeypatch.setattr(plan, "runner_facts", lambda fleet, label: ([rq], reads))
        in_run.files["asks.rec"] = ""
        start(in_run)
        (t,) = asks.parse(in_run.files["asks.rec"])[1]
        assert t["Took"] == ["place/7@1793440000"]
        out = capsys.readouterr().out
        assert "unit/a waits on you: the place /kit/places/change--a, launched by request 7 (place/7@1793440000)\n  which bolt?\n" in out
        assert "mac-studio's runner can't be read: madswan/runner/mac-studio at abc1234: it holds no runner.rec: what waits on madswan-planner there is left for its next run" in out


class TestEnd:
    """crew role end (design Decision 7; role-runs "A run's end answers what it took")."""

    def test_a_turn_ends_and_what_it_took_is_no_longer_pending_and_the_report_is_written(self, in_run, tmp_path, capsys):
        """role-runs, A turn ends."""
        start(in_run)
        in_run.entries.clear()
        report = tmp_path / "place/turn.md"
        end(in_run, report, "proposed the fix bolt")
        held, turns = asks.parse(in_run.files["asks.rec"])
        assert turns[0]["Said"] == "proposed the fix bolt" and turns[0]["Ended"]
        assert asks.pending(held, [], turns, "planner") == ([], []) and not asks.wanted(held, [], turns, "planner")
        assert in_run.entries == [("turn.end", ["agent/madswan-planner"], "turn 1 of madswan-planner ended", {})]
        assert in_run.writes[1].startswith("turn(madswan-planner): 1 ends (madswan-planner)\n")
        text = report.read_text()
        assert text.startswith("# Turn 1 of madswan-planner\n")
        assert "- ask/1: tell from madswan-design\n- ask/2: card from crew on card/req_a1\n" in text and "proposed the fix bolt" in text
        assert f"turn 1 of madswan-planner is ended, and its report is {report}." in capsys.readouterr().out

    def test_an_ask_written_after_the_start_waits_for_the_next_run(self, in_run, tmp_path):
        """role-runs, An ask during a run."""
        start(in_run)
        in_run.files["asks.rec"] = in_run.files["asks.rec"].replace("\n%rec: Turn", "\nId: 4\nRole: planner\nFrom: crew\nWhat: tell\n"
                                                                    "At: 2026-10-31T10:30:00Z\n\n%rec: Turn")
        end(in_run, tmp_path / "turn.md", "done")
        held, turns = asks.parse(in_run.files["asks.rec"])
        assert [a["Id"] for a in asks.pending(held, [], turns, "planner")[0]] == ["4"]

    def test_no_turn_open_writes_the_report_saying_so_and_records_nothing(self, in_run, tmp_path, capsys):
        """role-runs, No turn open."""
        before = dict(in_run.files)
        report = tmp_path / "turn.md"
        end(in_run, report, "nothing waited")
        assert in_run.files == before and in_run.writes == [] and in_run.entries == []
        assert report.read_text().startswith("# No turn of madswan-planner\n") and "nothing waited" in report.read_text()
        assert f"madswan-planner took no turn, so nothing is recorded; the report {report} says so." in capsys.readouterr().out

    def test_an_end_outside_a_run_is_refused_and_writes_no_report(self, in_run, monkeypatch, tmp_path):
        import crew
        monkeypatch.setenv("FLUME_PLACE", "/kit/places/fix-b--n")
        with pytest.raises(crew.Refusal, match="crew role end runs only in a run of a crew role"):
            end(in_run, tmp_path / "turn.md", "done")
        assert not (tmp_path / "turn.md").exists() and in_run.writes == []


class TestRunCards:
    """A run's answered cards, read in its own Pending You name at its start (design Decision 7, briefs.16)."""

    def test_the_cards_on_the_agents_turn_are_read_from_list_pending_as_the_wake_mod_reads_it(self):
        import cards
        listed = {"requests": [{"id": "req_a1", "title": "Approve proposal 12?", "turn": "agent", "status": "answered"},
                               {"id": "req_b2", "title": "Waits", "turn": "you", "status": "pending"},
                               {"requestId": "req_c3", "turn": "agent"}, {"id": "nope", "turn": "agent"}, "x",
                               {"id": "req_d4", "turn": "agent"}], "total": 6}
        assert cards.run_cards(listed) == [("req_a1", "Approve proposal 12?"), ("req_d4", None)]
        assert cards.run_cards({}) == [] and cards.run_cards(None) == [] and cards.run_cards({"requests": "x"}) == []

    def test_the_cards_crew_raised_in_a_name_are_those_it_posted_and_has_not_closed(self):
        import cards
        entries = [{"Act": "card.post", "By": "madswan-planner", "Card": "req_a1", "Key": "proposal/12"},
                   {"Act": "card.post", "By": "madswan-planner", "Card": "req_b2", "Key": "batch/4"},
                   {"Act": "card.post", "By": "madswan-design", "Card": "req_c3", "Key": "record/53"},
                   {"Act": "card.post", "By": "madswan-planner", "Card": "req_e5", "Key": "proposal/13", "Refused": "no"},
                   {"Act": "card.close", "Card": "req_b2"}]
        assert cards.posted_keys(entries, "madswan-planner") == {"req_a1": "proposal/12"}

    @pytest.fixture
    def bridge(self, monkeypatch):
        """Pending You's bridge as the run's start opens it: each call kept, answered from `replies`."""
        import cards
        calls, replies = [], {}

        class Bridge:
            def __init__(self, name, later, held=None):
                calls.append(("open", name))

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

            def call(self, tool, args):
                calls.append((tool, args))
                got = replies[tool]
                if isinstance(got, Exception):
                    raise got
                return got(args) if callable(got) else got
        monkeypatch.setattr(cards, "Bridge", Bridge)
        monkeypatch.setattr(cards, "host_entries", lambda record, label, host: [
            {"Act": "card.post", "By": "madswan-planner", "Card": "req_a1", "Key": "proposal/12"}])
        return calls, replies

    @pytest.mark.usefixtures("deneb")
    def test_each_answered_card_prints_with_its_key_and_answer_read_in_the_runs_own_name(self, bridge):
        """role-runs, What the planner's run reads: the card's key and the user's answer, read in madswan-planner's name."""
        import plan
        calls, replies = bridge
        replies["list_pending"] = {"requests": [{"id": "req_a1", "title": "Approve proposal 12?", "turn": "agent"},
                                                {"id": "req_q9", "title": "Which zone?", "turn": "agent"}]}
        replies["get_request"] = lambda args: {"requestId": args["requestId"], "status": "answered", "turn": "agent", "version": 3,
                                               "answer": {"approved": True} if args["requestId"] == "req_a1" else {"text": "eu-west-1"}}
        lines = plan.run_cards_said(None, "madswan", "madswan-planner")
        assert calls == [("open", "madswan-planner"), ("list_pending", {"name": "madswan-planner"}),
                         ("get_request", {"requestId": "req_a1", "name": "madswan-planner"}),
                         ("get_request", {"requestId": "req_q9", "name": "madswan-planner"})]
        assert lines == ["The cards the user answered, read in Pending You as madswan-planner:",
                         "card card/req_a1/3 (proposal/12): Approve proposal 12?", "  approved: yes",
                         "  crew closes it at the act its answer asks for, as your brief says for proposal/12",
                         "card card/req_q9/3: Which zone?", "  words: eu-west-1",
                         "  once you have acted on it, ack_answer (requestId req_q9, expectedVersion 3, name madswan-planner) with a one-line outcome"]

    def test_no_card_answered_prints_nothing_and_pending_you_not_read_says_to_call_list_pending(self, bridge):
        import crew
        import plan
        calls, replies = bridge
        replies["list_pending"] = {"requests": [{"id": "req_b2", "title": "Waits", "turn": "you"}]}
        assert plan.run_cards_said(None, "madswan", "madswan-planner") == []
        replies["list_pending"] = crew.Refusal("Pending You refused list_pending: signed out. Call list_pending as madswan-planner yourself, "
                                               "and act on what the user answered.")
        assert plan.run_cards_said(None, "madswan", "madswan-planner") == [
            "Your cards could not be read in Pending You as madswan-planner: Pending You refused list_pending: signed out. Call "
            "list_pending as madswan-planner yourself, and act on what the user answered."]


RUN_PLACE = "/home/u/.local/state/flume/places/crew-design--madswan"


def ran(address="madswan/design", phase="live", place=RUN_PLACE, words=None, raw=None):
    """A role's run as places.rec holds it (runner.RUNS): its place and Flume's status of it, a phase of None for a run
    the runner could launch none of, which holds its words and no place."""
    at = f"\nAddress: {address}\n" + (f"Place: {place}\n" if phase else "") + "At: 2026-10-31T12:02:00Z\n"
    told = raw if raw is not None else status(place=place, phase=phase) if phase else None
    return at + (f"Status: {told}\n" if told else "") + (f"Words: {words}\n" if words else "")


def runner_on(runs="", host="deneb"):
    """A host's runner as plan.runners reads it, its places.rec holding no place launched for a request and the runs."""
    import plan
    import runner
    files = {"runner.rec": plan.Plan(runner.RUNNER + f"\nHost: {host}\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n"),
             "answers.rec": plan.Plan(runner.ANSWERS), "places.rec": plan.Plan(runner.PLACES + "\n" + runner.RUNS + runs)}
    return {host: runner.host_read("madswan", host, "5e1f0c2a" + "0" * 32, files, {})}


class TestRoleRun:
    """A role's run as the runner's records on its host show it (R4; runner.role_run): live while its place reads live
    or making, and crew can't tell where the runner or the run's status can't be read (read.1)."""

    def test_a_run_whose_place_reads_live_or_making_is_live_and_one_tidied_or_never_launched_is_not(self):
        import runner
        tidied = {"tidied": {"over": "done", "at": 1793474400, "pending_for": []}}
        live, making = (runner.role_run(runner_on(ran(phase=p))["deneb"], "madswan/design") for p in ("live", "making"))
        assert (live["live"], live["place"], making["live"]) == (True, RUN_PLACE, True)
        gone = runner_on(ran(phase=tidied, raw=status(place=f"{RUN_PLACE}@1793474400", phase=tidied)))["deneb"]
        assert runner.role_run(gone, "madswan/design") == {"live": False, "place": RUN_PLACE, "words": None, "why": None}
        refused = runner_on(ran(phase=None, words="flume refused the launch: no stream madswan-main"))["deneb"]
        assert runner.role_run(refused, "madswan/design") == {"live": False, "place": None, "words": "flume refused the launch: no stream madswan-main", "why": None}
        assert runner.role_run(runner_on(ran())["deneb"], "madswan/planner")["live"] is False

    def test_a_runner_or_a_status_crew_cant_read_cant_tell(self):
        import runner
        assert runner.role_run(runner.of_host({}, "madswan", "deneb"), "madswan/design")["why"] == "no runner answers on deneb: madswan/runner/deneb does not exist"
        bad = runner.role_run(runner_on(ran(raw="{not json"))["deneb"], "madswan/design")
        assert bad["live"] is None and bad["why"].startswith("madswan/runner/deneb at 5e1f0c2: places.rec's status of the run of madswan/design is no JSON (")
        assert runner_on(ran() + ran())["deneb"]["why"] == "deneb's runner can't be read: madswan/runner/deneb at 5e1f0c2: places.rec holds the run of madswan/design twice"


@pytest.fixture
def opening(monkeypatch):
    """The user at deneb running crew role open, madswan's design agent and planner running as their kinds and its ops
    standing: madswan's branch in memory and deneb's runner as a case sets it (reads)."""
    import getpass
    import plan
    fleet = {"partitions": {"madswan": madswan(design="madswan-main", planner="madswan-main")}, "teams": {}, "hosts": {}}
    b = on_branch(monkeypatch, fleet, {})
    monkeypatch.delenv("CREW_LABEL", raising=False)
    monkeypatch.setattr(getpass, "getuser", lambda: "chuck")
    b.reads = runner_on()
    monkeypatch.setattr(plan, "runner_facts", lambda fleet, label: ([], b.reads))
    return b


def open_role(b, role="design", label="madswan"):
    import argparse
    import plan
    plan.role_open(b.fleet, argparse.Namespace(role=role, label=label))


class TestOpen:
    """crew role open (design Decision 13; role-runs "The user opens a role to talk")."""

    def test_with_no_run_live_an_open_ask_from_the_user_is_written_naming_the_place_it_opens_as(self, opening, capsys):
        """role-runs, No run live."""
        open_role(opening)
        (got,), turns = asks.parse(opening.files["asks.rec"])
        assert (got["Role"], got["From"], got["What"], turns) == ("design", "chuck@deneb", "open", [])
        assert "Words" not in got and "Key" not in got
        assert [r["Role"] for r in asks.parse_roles(opening.files["roles.rec"])] == ["design"]
        assert len(opening.writes) == 1 and opening.writes[0].startswith("ask(madswan-design): open from chuck@deneb")
        assert opening.entries == [("ask", ["agent/madswan-design"], "ask madswan-design: open", {"Chars": None})]
        assert capsys.readouterr().out.endswith("\nasked madswan-design to open: its run opens as the place crew-design--madswan in herdr "
                                                "on deneb once the runner there makes it, and greets you in its pane\n")

    def test_a_run_live_writes_nothing_and_names_its_place(self, opening, capsys):
        """role-runs, A run live."""
        opening.reads = runner_on(ran())
        open_role(opening)
        assert opening.files == {} and opening.writes == [] and opening.entries == []
        assert capsys.readouterr().out == (f"madswan-design's run is live on deneb, the place {RUN_PLACE}: talk to it there now, as "
                                           "crew-design--madswan in herdr; nothing is written\n")

    def test_a_run_over_is_asked_again_and_a_launch_the_runner_could_not_make_is_said(self, opening, capsys):
        opening.reads = runner_on(ran(phase=None, words="flume refused the launch: no stream madswan-main"))
        open_role(opening)
        assert [a["What"] for a in asks.parse(opening.files["asks.rec"])[0]] == ["open"]
        assert capsys.readouterr().out.endswith("the runner on deneb could not launch madswan-design's last run: flume refused the launch: no stream madswan-main\n")

    @pytest.mark.parametrize("reads, why", [
        ({}, "no runner answers on deneb: madswan/runner/deneb does not exist"),
        (runner_on(host="alpha"), "no runner answers on deneb: madswan/runner/deneb does not exist"),
        (runner_on(ran(raw="{not json")), "madswan/runner/deneb at 5e1f0c2: places.rec's status of the run of madswan/design is no JSON (")])
    def test_a_runner_crew_cant_read_on_the_roles_host_refuses_and_writes_nothing(self, opening, reads, why):
        """role-runs, The user opens a role to talk: "Where those records cannot be read, it SHALL refuse"."""
        import crew
        opening.reads = reads
        with pytest.raises(crew.Refusal) as e:
            open_role(opening)
        assert str(e.value).startswith(f"crew can't tell whether a run of madswan-design is live: {why}") and str(e.value).endswith("; nothing is written")
        assert opening.files == {} and opening.writes == []

    def test_a_role_that_stands_or_no_partition_named_is_refused(self, opening):
        import crew
        with pytest.raises(crew.Refusal, match="^madswan runs its ops as a standing agent, madswan-ops, in its tab of crew main up madswan: "
                                               "crew role open opens only a role its partition runs as its kind; nothing is written$"):
            open_role(opening, role="ops")
        with pytest.raises(crew.Refusal, match="^which partition's design\\? add --label madswan$"):
            open_role(opening, label=None)
        assert opening.files == {}


CREW_KIT = {"name": "crew", "repo": "afterthought/crew", "dir": "/w/crew", "main": "/w/crew/main"}


@pytest.fixture
def landing(monkeypatch, tmp_path):
    """A command run in madswan's design agent's run on deneb (FLUME_PLACE crew-design--madswan), the design agent
    running as its kind, with swancloud's crw-4 building afterthought/crew, a kit the teams file names for another
    partition; its writes applied to madswan's branch in memory, and a brief over two lines in a file."""
    swancloud = dict(madswan(), label="swancloud", blueprints=["afterthought/blueprints"])
    fleet = {"partitions": {"madswan": madswan(design="madswan-main"), "swancloud": swancloud},
             "teams": {"crw-4": {"name": "crw-4", "label": "swancloud", "kits": [CREW_KIT], "kit": CREW_KIT, "flume": False}}, "hosts": {}}
    monkeypatch.setenv("FLUME_PLACE", RUN_PLACE)
    b = on_branch(monkeypatch, fleet, {})
    b.brief = tmp_path / "record-0053.md"
    b.brief.write_text("Write docs/adr/0053-roles-run-as-kinds.md with this text whole:\n# 53. Roles run as kinds\n")
    return b


def land(b, repo="afterthought/crew", name="record-0053", brief=None):
    import argparse
    import plan
    plan.role_land(b.fleet, argparse.Namespace(repo=repo, name=name, brief_file=str(brief or b.brief)))


def requested(b):
    import plan
    return [dict((f, v) for f, v in reversed(r.fields)) for r in plan.Plan(b.files["requests.rec"]).recs("Request")]


class TestLand:
    """crew role land (design Decision 10; role-runs "A role's work that lands is a place it launches")."""

    def test_the_design_agents_records_are_a_chore_launch_on_the_repositorys_default_branch(self, landing, capsys):
        """role-runs, The design agent's records."""
        land(landing)
        (r,) = requested(landing)
        assert {f: r[f] for f in ("Request", "Act", "Host", "Work", "Repo", "Kind", "Name", "Base", "Stream", "Priority", "Intent",
                                  "Recipient", "By")} == {
            "Request": "1", "Act": "launch", "Host": "deneb", "Work": "role/design/record-0053", "Repo": "afterthought/crew", "Kind": "chore",
            "Name": "record-0053", "Base": "main", "Stream": "madswan-main", "Priority": "0", "Intent": "madswan-design",
            "Recipient": "madswan/design", "By": "madswan-design"}
        assert r["Brief"] == landing.brief.read_text().rstrip("\n") and "Hold" not in r and "After" not in r
        assert [m.split("\n")[0] for m in landing.writes] == ["land(madswan-design): record-0053 in afterthought/crew (madswan-design)"]
        assert landing.entries == [("role.land", ["role/design/record-0053", "agent/madswan-design"],
                                    "land(madswan-design): record-0053 in afterthought/crew", {"Repo": "afterthought/crew"})]
        assert "Write docs" not in str(landing.entries)
        assert capsys.readouterr().out.endswith(
            "the runner on deneb launches chore record-0053 in afterthought/crew on main (request 1) in stream madswan-main, your brief its "
            "brief whole and madswan/design its recipient: Flume builds it and submits it through sluice, and its landing, or a wait on "
            "you, reaches madswan-design's next run\n")

    def test_a_blueprints_repository_or_one_the_plan_names_is_named_and_requests_follow_those_held(self, landing, monkeypatch):
        import plan
        monkeypatch.setattr(plan, "read", lambda repo, ref, tip: plan.Plan(
            plan.HEADER.replace("%rec: Unit", "Bolt: b\nRepo: agentplot/flywheel-web\nGoal: g\n\n%rec: Unit")))
        land(landing, "afterthought/blueprints", "record-0054")
        land(landing, "agentplot/flywheel-web", "diagram-the-method")
        assert [(r["Request"], r["Repo"], r["Work"]) for r in requested(landing)] == [
            ("1", "afterthought/blueprints", "role/design/record-0054"), ("2", "agentplot/flywheel-web", "role/design/diagram-the-method")]

    @pytest.mark.parametrize("repo, why", [
        ("afterthought/crew-state", "^crew names no repository afterthought/crew-state: a role's work lands in a blueprints repository "
                                    "or a kit the teams file names, or a repository the plan names, and it names afterthought/blueprints, "
                                    "afterthought/crew, afterthought/flywheel-web$"),
        ("crew", "^a repository is named by its forge address, <owner>/<name>, which the runner resolves to its clone, not crew$")])
    def test_a_repository_crew_does_not_name_is_refused_writing_nothing_and_the_refusal_is_recorded(self, landing, repo, why):
        """role-runs, A role's work that lands: "A repository neither the teams file nor the plan names SHALL be refused"."""
        import crew
        with pytest.raises(crew.Refusal, match=why):
            land(landing, repo)
        assert landing.files == {} and landing.writes == []
        ((act, on, _, f),) = landing.entries
        assert (act, on, f["Repo"]) == ("role.land", ["role/design/record-0053", "agent/madswan-design"], repo)
        assert re.match(why, f["refused"])

    def test_a_name_in_use_a_name_crew_does_not_mint_and_a_brief_with_no_words_or_no_file_are_refused(self, landing, tmp_path):
        import crew
        land(landing)
        with pytest.raises(crew.Refusal, match="^record-0053 is in use for madswan/design: request 1 launched it in afterthought/crew as "
                                               "Flume place chore--record-0053, so name this work differently$"):
            land(landing, "afterthought/blueprints")
        with pytest.raises(crew.Refusal, match="^work that lands is named with lowercase words and dashes, not Record-53$"):
            land(landing, name="Record-53")
        (tmp_path / "empty.md").write_text("\n \n")
        with pytest.raises(crew.Refusal, match="^the brief for record-0055 holds no words, and a chore's agent starts fresh with its brief alone$"):
            land(landing, name="record-0055", brief=tmp_path / "empty.md")
        with pytest.raises(crew.Refusal, match=f"^the brief {tmp_path}/gone.md can't be read: No such file or directory$"):
            land(landing, name="record-0055", brief=tmp_path / "gone.md")
        assert len(requested(landing)) == 1 and len(landing.writes) == 1

    def test_a_land_outside_a_run_is_refused_and_writes_nothing(self, landing, monkeypatch):
        """role-runs, A role's work that lands: "and so SHALL a run outside a role's run"; a standing design agent's CREW_AGENT is
        no run."""
        import crew
        for place in ("/kit/places/change--a", None):
            if place:
                monkeypatch.setenv("FLUME_PLACE", place)
            else:
                monkeypatch.delenv("FLUME_PLACE")
                monkeypatch.setenv("CREW_AGENT", "madswan-design")
            with pytest.raises(crew.Refusal, match="crew role land runs only in a run of a crew role, in the place Flume made for it"):
                land(landing)
        assert landing.files == {} and landing.writes == [] and landing.entries == []
