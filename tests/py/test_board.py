"""The board of a partition's flow (the crew-board spec): board.board_data on one read of the plan, proposals, signals,
kits and run record, as plan.rail_read and board.signals give it, and board.board_text, board.frame_text and
board.stamp on what that makes. That crew board reads it all and writes nothing, and the host's follower's refresh writes the
frame the board tab draws, are the board journey's (t-journey-board)."""
import datetime
import json
import os
import pathlib
import re
import sys

import pytest

from facts import plan_text

import board
import crew
import ops
import plan

BOX = "chuck-herdr-alpha"
KIT = {"name": "switchboard-kit", "main": "/kit/main", "dir": "/kit"}
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio", "teams": ["swb-1", "swb-2", "brd-1", "atl-1"],
                                 "blueprints": ["WilldanGroup/willdan-blueprints"], "state": "WilldanGroup/crew-state"}},
         "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": BOX, "flume": False, "kit": KIT},
                   "swb-2": {"name": "swb-2", "label": "wldn", "machine": BOX, "flume": False, "kit": KIT},
                   "brd-1": {"name": "brd-1", "label": "wldn", "machine": BOX, "flume": False,
                             "kit": {"name": "breadboard-kit", "main": "/b/main", "dir": "/b"}},
                   "atl-1": {"name": "atl-1", "label": "wldn", "machine": "mac-studio", "flume": False,
                             "kit": {"name": "atlas-kit", "main": "/a/main", "dir": "/a"}}},
         "hosts": {BOX: {"kind": "nixos", "ssh": BOX}, "mac-studio": {"kind": "darwin", "ssh": "mac-studio"}}}
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def ago(minutes):
    return board.iso(NOW - datetime.timedelta(minutes=minutes))


def hm(minutes):
    """A time minutes before the board was read as a head line says when a holder began (plan.time_said)."""
    t = (NOW - datetime.timedelta(minutes=minutes)).astimezone()
    return f"{t:%H:%M}" if t.date() == NOW.astimezone().date() else f"{t:%Y-%m-%d %H:%M}"


# Each held bolt's give, as the run record holds it: tenant-environments 200 minutes before the board was read, and
# board-done 30; with nothing else of theirs recorded, each has been nobody's since (plan.20).
GIVES = [dict(Id=f"{ago(200)}-mac-studio-1-0", At=ago(200), Host="mac-studio", Act="bolt.give", On=["bolt/tenant-environments", "team/swb-1"]),
         dict(Id=f"{ago(30)}-mac-studio-1-0", At=ago(30), Host="mac-studio", Act="bolt.give", On=["bolt/board-done", "team/brd-1"])]
TE_TIME = f"3h 20m: nobody 3h 20m; stalled since {hm(200)}"
DONE_TIME = f"30m: nobody 30m; stalled since {hm(30)}"
NO_GIVE = "its age can't be told: the run record of the last 60 days holds no give of it"


@pytest.fixture(autouse=True)
def here(monkeypatch):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")


def the_plan():
    return plan.Plan(plan_text(
        bolts=[("apex-zones", "switchboard-kit", None), ("tenant-environments", "switchboard-kit", "swb-1"), ("board-done", "breadboard-kit", "brd-1")],
        units=[("zone-one", "switchboard-kit", "apex-zones", []), ("a", "switchboard-kit", "tenant-environments", []),
               ("b", "switchboard-kit", "tenant-environments", []), ("done-one", "breadboard-kit", "board-done", []),
               ("zone-two", "switchboard-kit", None, [])]).replace("Unit: zone-two\nRepo: switchboard-kit\n", "Unit: zone-two\nRepo: switchboard-kit\nSource: docs/zones.md\n"))


def kits(ok=True):
    place = lambda u, tasks: {"path": f"/kit/places/{u}", "head": "a" * 40, "head_at": ago(90), "tasks": tasks, "planning": True, "open": [],
                              "bolt": "tenant-environments"}
    swb = {"ok": True, "main": [], "places": {"a": place("a", (1, 2)), "b": place("b", (0, 2))}, "reports": {},
           "bolts": {"tenant-environments": {"head": "d" * 40, "head_at": ago(200), "changes": [], "worktree": "/kit/bolts/tenant-environments"}},
           "fixes": [{"fix": "fix/tenant-environments/edge", "merged": False, "bolt": "tenant-environments", "path": "/kit/places/fix-edge"}],
           "slots": {"swb-1": [{"slot": "unit-1", "kind": "unit", "name": "a"}, {"slot": "unit-4", "kind": "fix", "name": "fix/tenant-environments/edge"}]},
           "sites": {"/kit/places/a": {"here": "http://unit-a--switchboard-kit.localhost", "tailnet": "https://unit-a--switchboard-kit--box.dev"}},
           "routes": [{"name": "unit-a--switchboard-kit", "url": "http://unit-a.localhost"}],
           "explorations": [{"name": "command-cost", "first": "Reading: what each crew command costs."}], "submissions": [], "decided": []}
    brd = {"ok": True, "main": ["done-one"], "places": {}, "reports": {}, "bolts": {"board-done": {"head": "e" * 40, "head_at": ago(10), "changes": []}},
           "fixes": [], "slots": {}, "sites": {}, "routes": [], "submissions": [], "decided": []}
    mac = {"mac-studio": {"ok": True, "kits": {"/a/main": {"ok": True, "main": [], "places": {}, "reports": {}, "bolts": {}, "fixes": []}}}}
    return {BOX: {"ok": True, "kits": {"/kit/main": swb, "/b/main": brd}}, **mac} if ok else {BOX: {"ok": False, "error": "ssh: timed out"}, **mac}


def read(sv=None, signals=None, props=(), landings=(), gives=None, rows=None, cards=(), errors=None, unread=None, pl=True, entries=(), logs=()):
    """The read the board is made from; entries are the partition's run record entries the operations are read from,
    whose rail rows join the plan's, as plan.rail_record makes them, and logs every entry it read."""
    p = the_plan() if pl else None
    found = [("wldn", "WilldanGroup/crew-state", "tip0" if pl else None, p)]
    sv = sv or kits()
    ops_rows = [dict(r, at=plan.utc(r["at"]), doc=None) for r in ops.rows(FLEET, "wldn", list(entries))]
    return dict(found=found, sv=sv, props=list(props), cards=list(cards), unread=unread or {}, errors=errors or {},
                landings=list(landings), gives=gives or {}, signals={"wldn": (signals or [], {})}, ops={"wldn": list(entries)},
                logs={"wldn": GIVES + (list(logs) or list(entries))},
                rows=rows if rows is not None else (plan.rail_rows(FLEET, found, sv, list(props), {}, None) if p else []) + ops_rows)


def data(**kw):
    return board.board_data(FLEET, ["wldn"], read(**kw), NOW)


def lane(text, name):
    out, on = [], False
    for l in text.splitlines():
        if l == name:
            on = True
        elif l and l[0] not in " !✓✎":
            on = False
        elif on:
            out.append(l)
    return out


S1, S2 = "a" * 40, "b" * 40
N = iter(range(1, 1000))


def entry(act, minutes, env="mac-studio", **f):
    """A run-record entry on the partition's main level's host, minutes before the board was read."""
    on = [f"bolt/{f.pop('bolt')}"] if act == "bolt.land" else [f"env/{env}"]
    return dict(Id=f"{ago(minutes)}-mac-studio-1-{next(N)}", At=ago(minutes), Host="mac-studio", Act=act, On=on, From=[], Commit=[], **f)


# A deploy of atlas-kit to mac-studio approved and done, a newer one offered, an operation handed to the dispatcher
# and one waiting on the user.
OPS = [entry("bolt.land", 95, bolt="atlas-maps", Repo="atlas-kit", Head=S1), entry("ops.offer", 90, Head=S1, Base="none"),
       entry("ops.approve", 70, Head=S1, By="wldn-ops"), entry("ops.deploy", 60, Head=S1, Base="none", Phase="start"),
       entry("ops.deploy", 50, Head=S1, Phase="end", Outcome="done"), entry("bolt.land", 45, bolt="atlas-zones", Repo="atlas-kit", Head=S2),
       entry("ops.offer", 40, Head=S2, Base=S1),
       entry("ops.step", 30, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher", Agent="wldn-dispatch-mac-studio"),
       entry("ops.step", 20, Key="rotate-key", State="waiting", Doer="user", Text="Rotate the key.")]
DEPLOY_CARD = dict(label="wldn", card="req_9", key="deploy/mac-studio", by="wldn-ops", host="mac-studio", at=NOW)
# The deploy's card, posted in wldn-ops's name when the offer was made, refused by Pending You (rail-cards "A row's card
# that Pending You refused is owed until it posts").
REFUSED_POST = entry("card.post", 39, Key="deploy/mac-studio", By="wldn-ops",
                     Refused="Pending You refused post_request: This is atl-1-conductor’s card; leave it.")


SIGS = [{"signal": "2026-10-01-planning/01-zones", "home": "blueprints", "captured_by": "wldn-planner", "at": "2026-10-01", "kind": "ask",
         "first": "Every apex should be a zone of its own."},
        {"signal": "2026-10-01-planning/02-tenants", "home": "blueprints", "captured_by": "wldn-planner", "at": "2026-10-01", "kind": "constraint",
         "first": "Tenants never share an environment."},
        {"signal": "2026-10-12-chuck/01-checked", "home": "branch", "captured_by": "chuck@mac-studio", "at": None, "kind": "ask",
         "first": "Plans should be checked before they run."}]


class TestText:
    def test_with_nothing_in_flight_each_lane_and_attention_say_none_plain_into_a_pipe(self):
        sv = {BOX: {"ok": True, "kits": {}}, "mac-studio": {"ok": True, "kits": {}}}
        empty = board.board_data(FLEET, ["wldn"], read(sv=sv, pl=False), NOW)
        out = board.board_text(empty)
        assert out.splitlines()[0].startswith("wldn board, as of ") and out.splitlines()[0].endswith(f"read from {BOX}, mac-studio")
        assert [l for l in out.splitlines()[1:] if l and l[0].isalpha()] == ["Inception", "Bolt plan", "Construction", "Operation", "attention"]
        assert "\033" not in out

    def test_inception_lists_unmoved_signals_by_who_captured_them_and_each_exploration(self):
        inc = lane(board.board_text(data(signals=SIGS)), "Inception")
        assert "  signals captured by wldn-planner  2 not moved, the oldest captured 2026-10-01" in inc
        assert "  signals captured by chuck@mac-studio  1 not moved" in inc
        assert "    ask  Every apex should be a zone of its own.  2026-10-01-planning/01-zones" in inc
        assert "  exploration  switchboard-kit command-cost  Reading: what each crew command costs." in inc

    def test_bolt_plan_lists_each_planned_bolt_with_its_units_and_the_queue_with_its_sources(self):
        bp = lane(board.board_text(data()), "Bolt plan")
        assert bp == ["  switchboard-kit apex-zones  Goal of apex-zones.", "    zone-one  ready", "  switchboard-kit zone-two  queued  docs/zones.md"]

    def test_construction_shows_a_held_bolt_as_a_ledger(self):
        con = lane(board.board_text(data()), "Construction")
        assert con[:4] == [f"  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  {TE_TIME}",
                           "    a  code 1/2  unit-1  https://unit-a--switchboard-kit--box.dev", "    b  planned",
                           "    fix/tenant-environments/edge  fix  unit-4"]
        assert f"! breadboard-kit board-done  brd-1 on chuck-herdr-alpha  landed  {DONE_TIME}" in con

    def test_a_held_bolt_every_unit_of_which_landed_is_named_for_attention(self):
        att = lane(board.board_text(data()), "attention")
        assert att == ["! bolt board-done: every unit has landed on main, and the bolt is still in the plan"]

    def test_a_rail_row_is_a_marker_on_its_object_with_its_card(self):
        props = [{"label": "wldn", "proposal": 1, "by": "chuck@mac-studio", "opened": "2026-10-12", "case": "The console gets a bolt.", "waiting": [],
                  "changes": [{"do": 'bolt new console-two "x" --repo switchboard-kit', "bolts": ["console-two"]}]}]
        card = dict(label="wldn", card="req_1", key="proposal/1", by="wldn-planner", host="mac-studio", at=NOW)
        bp = lane(board.board_text(data(props=props, cards=[card])), "Bolt plan")
        assert bp[0] == "✓ proposal 1 by chuck@mac-studio  The console gets a bolt.  card open, asked by wldn-planner"

    def test_a_rewritten_proposals_marker_is_its_chains_card(self):
        props = [{"label": "wldn", "proposal": 2, "first": 1, "by": "wldn-planner", "opened": "2026-10-12", "case": "The console, again.",
                  "waiting": [], "changes": [{"do": 'bolt new console-two "x" --repo switchboard-kit', "bolts": ["console-two"]}]}]
        card = dict(label="wldn", card="req_1", key="proposal/1", by="wldn-planner", host="mac-studio", at=NOW)
        bp = lane(board.board_text(data(props=props, cards=[card])), "Bolt plan")
        assert bp[0] == "✓ proposal 2 by wldn-planner  The console, again.  card open, asked by wldn-planner"

    def test_operation_lists_a_bolt_landed_this_week_and_not_one_landed_eight_days_ago(self):
        landings = [dict(label="wldn", bolt="atlas-maps", units=["map-one"], at=NOW - datetime.timedelta(hours=1), by="chuck@mac-studio", host="mac-studio"),
                    dict(label="wldn", bolt="old-maps", units=["old"], at=NOW - datetime.timedelta(days=8), by="wldn-ops", host="mac-studio")]
        op = lane(board.board_text(data(landings=landings, gives={("wldn", "atlas-maps"): "atl-1"})), "Operation")
        assert len(op) == 1 and op[0].startswith("  atlas-maps  landed ") and op[0].endswith(" by chuck@mac-studio  atl-1  map-one")

    def test_operation_shows_each_environments_deploys_and_the_operations_waiting_with_their_markers(self):
        op = lane(board.board_text(data(entries=OPS, cards=[DEPLOY_CARD])), "Operation")
        assert op == [f"✓ mac-studio  deploy {S2[:7]} from {S1[:7]}  waits on the user's word  carrying atlas-zones  card open, asked by wldn-ops",
                      f"  mac-studio  deploy {S1[:7]} from nothing deployed  done {board.local(ago(50))}  approved by wldn-ops  carrying atlas-maps",
                      "  mac-studio  restart-teams/1  handed to wldn-dispatch-mac-studio",
                      "✓ mac-studio  rotate-key  waits on the user  Rotate the key.  no card open"]
        env, = data(entries=OPS)["partitions"][0]["environments"]
        assert (env["env"], env["teams"], [d["row"] for d in env["deploys"]], [w["row"] for w in env["waiting"]]) == (
            "mac-studio", ["atl-1"], ["deploy/mac-studio", None], [None, "op/mac-studio/2"])

    def test_a_deploy_whose_only_post_was_refused_owes_its_card_and_a_row_with_no_post_has_none_open(self):
        """crew-board "A row whose card post was refused": the row's last post under its key, refused, with no card
        open; the rotate-key step, never posted, has none open and says no more."""
        logs = OPS + [REFUSED_POST]
        op = lane(board.board_text(data(entries=OPS, logs=logs)), "Operation")
        assert op[0] == f"✓ mac-studio  deploy {S2[:7]} from {S1[:7]}  waits on the user's word  carrying atlas-zones  no card open, its post refused"
        assert op[-1] == "✓ mac-studio  rotate-key  waits on the user  Rotate the key.  no card open"
        env, = data(entries=OPS, logs=logs)["partitions"][0]["environments"]
        assert env["deploys"][0]["markers"][0]["refused"] == REFUSED_POST["Refused"]
        assert env["waiting"][1]["markers"][0]["refused"] is None

    def test_a_card_posted_after_a_refused_post_is_open_and_owes_nothing(self):
        d = data(entries=OPS, logs=OPS + [REFUSED_POST], cards=[DEPLOY_CARD])
        assert d["partitions"][0]["environments"][0]["deploys"][0]["markers"][0]["refused"] is None
        assert lane(board.board_text(d), "Operation")[0].endswith("card open, asked by wldn-ops")

    def test_a_deploy_that_failed_says_at_which_step_and_one_whose_commit_no_landing_holds_says_so(self):
        es = [entry("ops.deploy", 30, Head=S2, Base=S1, Phase="start"), entry("ops.deploy", 20, Head=S2, Phase="step", Step="machine", Outcome="failed"),
              entry("ops.deploy", 10, Head=S2, Phase="end", Outcome="failed")]
        assert lane(board.board_text(data(entries=es)), "Operation") == [
            f"  mac-studio  deploy {S2[:7]} from {S1[:7]}  failed {board.local(ago(10))} at the machine  carrying what can't be read: {S2[:7]} is no landing's commit in the record"]

    def test_a_host_that_does_not_answer_is_named_and_its_ledgers_units_are_unknown(self):
        out = board.board_text(data(sv=kits(ok=False)))
        assert f"! {BOX} did not answer (its kits: ssh: timed out)" in lane(out, "attention")
        con = lane(out, "Construction")
        assert (f"  switchboard-kit tenant-environments  swb-1 on {BOX}  unknown  3h 20m; who held its time can't be told: its submissions "
                "can't be read: its kit was not read") in con and "    a  unknown" in con
        assert out.splitlines()[0].endswith("read from mac-studio")

    def test_an_operator_host_with_no_team_is_never_named_for_its_run_record(self):
        """crew-board, "An operator host asleep": the run record is read from the branch, so a host that runs no team
        is asked for nothing and named for nothing, and the landings and cards read from wldn/main are drawn whole."""
        fleet = dict(FLEET, hosts=dict(FLEET["hosts"], **{"macbook-pro": {"kind": "darwin", "ssh": "macbook-pro",
                                                                           "sessions": {"wldn": {"partition": "clients/willdan"}}}}))
        sv = dict(kits(), **{"macbook-pro": {"ok": False, "error": "ssh: connect to host macbook-pro port 22: Operation timed out"}})
        landed = [dict(label="wldn", bolt="tenant-environments", units=["a", "b"], at=plan.utc(ago(5)), by="wldn-ops", host="macbook-pro")]
        d = board.board_data(fleet, ["wldn"], read(sv=sv, unread={"wldn": {}}, landings=landed), NOW)
        p = d["partitions"][0]
        assert "macbook-pro" not in p["hosts"] and "macbook-pro" not in json.dumps(p["attention"])
        assert [a for a in p["attention"] if a["what"] in ("host", "plan")] == []

    def test_a_branch_whose_run_record_cannot_be_read_is_named_as_the_plans(self):
        d = data(unread={"wldn": {"wldn/main": "could not fetch wldn/main of WilldanGroup/crew-state over https: timed out"}})
        assert [a for a in d["partitions"][0]["attention"] if a["what"] in ("host", "plan")] == [
            {"what": "plan", "name": "wldn/main", "why": "its run record: could not fetch wldn/main of WilldanGroup/crew-state over https: timed out"}]
        assert ("! the plan, wldn/main: its run record: could not fetch wldn/main of WilldanGroup/crew-state over https: timed out"
                in lane(board.board_text(d), "attention"))
        assert sorted(d["partitions"][0]["hosts"]) == [BOX, "mac-studio"]

    def test_a_plan_that_cannot_be_read_is_named_for_attention(self):
        d = board.board_data(FLEET, ["wldn"], read(pl=False, errors={"wldn/main of WilldanGroup/crew-state": "plan.rec fails recfix --check"}), NOW)
        assert "! the plan, wldn/main of WilldanGroup/crew-state: plan.rec fails recfix --check" in lane(board.board_text(d), "attention")


class TestData:
    def test_each_object_says_the_teams_it_belongs_to(self):
        p = data(signals=SIGS)["partitions"][0]
        assert [t["team"] for t in p["teams"]] == ["swb-1", "swb-2", "brd-1", "atl-1"]
        assert next(b for b in p["construction"] if b["bolt"] == "tenant-environments")["teams"] == ["swb-1"]
        assert p["bolt_plan"]["planned"][0]["teams"] == ["swb-1", "swb-2"] and p["bolt_plan"]["queue"][0]["teams"] == ["swb-1", "swb-2"]
        assert p["inception"]["explorations"][0]["teams"] == ["swb-1", "swb-2"]
        assert [s["teams"] for s in p["inception"]["signals"]] == [[], [], []]

    def test_a_signal_a_teams_agent_captured_is_its_teams(self):
        sig = dict(SIGS[0], captured_by="swb-1-conductor")
        assert data(signals=[sig])["partitions"][0]["inception"]["signals"][0]["teams"] == ["swb-1"]

    def test_the_hosts_are_named_with_whether_they_answered(self):
        assert data()["partitions"][0]["hosts"] == {BOX: True, "mac-studio": True}

    @pytest.mark.parametrize("at, held", [("2026-10-01", "2026-10-01"), ("2026-10-01T10:00:00", "2026-10-01T10:00:00Z"),
                                          ("2026-10-01T12:00:00+02:00", "2026-10-01T10:00:00Z"), ("not a time", None)])
    def test_a_captures_time_is_held_in_utc_and_a_date_as_it_is(self, at, held):
        assert board.stamp(at) == held


class TestFrame:
    def test_with_no_frame_the_board_tab_says_the_hosts_follower_writes_it(self):
        assert board.frame_text("wldn", None, None, False, NOW) == (
            "No board for wldn yet: the host's follower writes it each time it refreshes, swancloud's job or the console's rail tab, "
            "which crew console up wldn opens while no job runs.")

    def test_a_frame_read_five_minutes_ago_is_headed_with_its_age(self):
        d = data()
        d["read_at"] = board.iso(NOW - datetime.timedelta(minutes=5))
        assert "(5m ago: the host's follower has not refreshed it since)" in board.frame_text("wldn", d, None, False, NOW).splitlines()[0]
        d["read_at"] = board.iso(NOW)
        assert " ago" not in board.frame_text("wldn", d, None, False, NOW).splitlines()[0]


class TestFollower:
    """The host's one follower (the crew-board spec, A host has one follower): an OS lock on a file beside the frames,
    held for the follower's life and saying who holds it. Two open()s are two open file descriptions, so the lock
    conflicts between them in one process as between two processes."""

    def test_a_held_lock_refuses_a_second_try_and_says_the_tab_holds_it(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        held = board.lock_follower("tab", "wldn", wait=False)
        assert held
        assert board.lock_follower("job", wait=False) is None and board.lock_follower("tab", "madswan", wait=False) is None
        assert board.lock_path().read_text().startswith("tab wldn ")
        assert board.follower_here() == "tab"
        held.close()
        assert board.follower_here() == "none"

    def test_the_job_holding_it_reads_as_the_job(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        held = board.lock_follower("job", wait=False)
        assert board.lock_path().read_text().split()[0] == "job" and board.follower_here() == "job"
        held.close()

    def test_a_released_lock_is_free_and_taken_again_with_its_holder_written_anew(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        board.lock_follower("job", wait=False).close()
        held = board.lock_follower("tab", "wldn", wait=False)
        assert held and len(board.lock_path().read_text().splitlines()) == 1 and board.follower_here() == "tab"
        held.close()

    @pytest.mark.parametrize("line, free, who", [("", False, "unknown"), (None, False, "unknown"), ("job 12 2026-10-28T10:00:00Z", False, "job"),
                                                 ("tab wldn 12 2026-10-28T10:00:00Z", False, "tab"), ("tab 12 2026-10-28T10:00:00Z", False, "unknown"),
                                                 ("someone else", False, "unknown"), ("job 12 2026-10-28T10:00:00Z", True, "none"), ("", True, "none")])
    def test_who_follows_is_read_from_the_lock_and_an_unreadable_holder_is_unknown(self, line, free, who):
        assert board.follower_of(line, free) == who

    def test_it_follows_each_partition_whose_session_of_its_name_on_the_host_is_its_own(self):
        fleet = {"partitions": {"wldn": {"partition": "clients/willdan"}, "swancloud": {"partition": "personal"},
                                "madswan": {"partition": "business"}, "agentplot": {"partition": "agentplot"}},
                 "hosts": {"mac-studio": {"sessions": {"wldn": {"partition": "clients/willdan"}, "wldn-5": {"partition": "clients/willdan"},
                                                       "swancloud": {"partition": "personal"}, "madswan": {"partition": "personal"},
                                                       "agentplot": {"partition": None}}},
                           BOX: {"sessions": {"wldn": {"partition": "clients/willdan"}}}}}
        assert board.labels_here(fleet, "mac-studio") == ["wldn", "swancloud"]
        assert board.labels_here(fleet, BOX) == ["wldn"] and board.labels_here(fleet, "macbook-pro") == []

    @pytest.mark.parametrize("m, kept, crew_read, how", [
        ({"crew": True, "read": True, "any": True}, False, True, "read"), ({"crew": True, "read": True, "any": True}, True, True, "update"),
        ({"crew": True, "read": True, "any": True}, True, False, "read"), ({"crew": False, "read": True, "any": True}, True, True, "read"),
        ({"crew": False, "read": False, "any": True}, True, True, "sweep"), ({"crew": False, "read": False, "any": False}, True, True, "render")])
    def test_a_refresh_reads_once_with_none_kept_hands_out_restarts_once_crew_moved_and_renders_when_nothing_moved(self, m, kept, crew_read, how):
        """A tip or a kit moved reads; only a readings folder or the cards moved sweeps; nothing moved renders."""
        assert board.refresh_plan(m, kept, crew_read) == how

    NOTHING = {"crew": False, "state": set(), "blueprints": set(), "kits": set(), "readings": set(), "cards": False, "read": False, "any": False}
    READINGS = {"mac-studio": ["wldn", "swancloud"], BOX: ["wldn"]}

    def test_after_only_a_hosts_readings_moved_its_card_sessions_alone_are_swept(self):
        """The card-sessions spec, A reading sent on one host."""
        assert board.sweeps_after(dict(self.NOTHING, readings={BOX}, any=True), self.READINGS, []) == {"cards": False, "sessions": {"wldn": {BOX}}}
        assert board.sweeps_after(dict(self.NOTHING, readings={"mac-studio"}, any=True), self.READINGS, []) == (
            {"cards": False, "sessions": {"wldn": {"mac-studio"}, "swancloud": {"mac-studio"}}})

    def test_after_only_the_cards_moved_the_card_sweep_alone_runs(self):
        assert board.sweeps_after(dict(self.NOTHING, cards=True, any=True), self.READINGS, []) == {"cards": True, "sessions": {}}

    def test_with_nothing_moved_only_the_hosts_the_last_could_not_check_are_swept_beside_what_moved(self):
        unchecked = [{"label": "wldn", "host": "mac-studio", "why": "did not answer (exit 255)"}]
        assert board.sweeps_after(self.NOTHING, self.READINGS, unchecked) == {"cards": False, "sessions": {"wldn": {"mac-studio"}}}
        assert board.sweeps_after(dict(self.NOTHING, readings={BOX}, any=True), self.READINGS, unchecked) == (
            {"cards": False, "sessions": {"wldn": {"mac-studio", BOX}}})

    @pytest.mark.parametrize("now, tick_at, seen, looked, how", [
        (100.0, 100.0, "a", "a", "tick"), (100.0, 0.0, "a", "b", "tick"), (100.0, 160.0, "a", "b", "refresh"), (100.0, 160.0, "a", "a", None)])
    def test_a_look_ticks_when_its_clock_is_due_refreshes_when_a_cache_moved_and_else_reads_nothing(self, now, tick_at, seen, looked, how):
        assert board.wake(now, tick_at, seen, looked) == how

    def test_the_clock_is_a_minute_a_frame_is_stale_after_three_and_sigusr1_makes_the_next_tick_now(self):
        assert board.PERIOD == 60 and board.STALE == 3 * board.PERIOD
        f = board.Follower(None)
        f.tick_at = 1e12
        assert board.wake(100.0, f.tick_at, "a", "a") is None
        f.tick_now()
        assert board.wake(100.0, f.tick_at, "a", "a") == "tick"


class TestRefresh:
    """The host's follower's refresh (the crew-board spec, The rail and the board come from one read, A refresh after
    nothing moved reads nothing, A refresh after a change reads only what moved): one read for every partition with an
    operator session on the host, kept, and the frames written from it; each step around it stands in here, the read,
    the views and the stamps, so what is asked is what the case shows."""

    FLEET = {"partitions": {"wldn": {"label": "wldn", "partition": "clients/willdan", "state": "o/state", "blueprints": ["o/bp"],
                                     "machine": "mac-studio", "teams": ["swb-1"]},
                            "swancloud": {"label": "swancloud", "partition": "personal", "state": "o/state", "blueprints": ["o/bp"],
                                          "machine": "mac-studio", "teams": []}},
             "teams": {"swb-1": {"machine": BOX}},
             "hosts": {"mac-studio": {"sessions": {"wldn": {"partition": "clients/willdan"}, "swancloud": {"partition": "personal"}}}}}

    @pytest.fixture
    def follower(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        monkeypatch.setattr(crew, "SESSIONS", tmp_path / "sessions")
        monkeypatch.setattr(crew, "HOLD", tmp_path / "hold")
        self.looks = {"crew": ("c" * 40, b"{teams}"), "state": {"wldn": "a" * 40, "swancloud": ""}, "blueprints": {"wldn": "b" * 40, "swancloud": "b" * 40}}
        self.stamps, self.reads, self.swept, self.again, self.unchecked = {(BOX, "/kit/main"): "s1"}, [], [], [], []
        self.readings, self.asked = {BOX: "r1", "mac-studio": "r2"}, []
        monkeypatch.setattr(board, "look", lambda fleet, labels: {k: dict(v) if isinstance(v, dict) else v for k, v in self.looks.items()})

        self.overviews, self.overviews_asked, self.routes = {}, [], {}

        def stamps_now(fleet, kits, readings, overviews=None, routes=False):
            self.asked.append(readings)
            self.overviews_asked += [(h, m) for h, ms in (overviews or {}).items() for m in ms]
            return {"kits": {k: v for k, v in self.stamps.items() if k[1] in kits.get(k[0], {})}, "readings": {h: self.readings[h] for h in readings},
                    "overviews": {(h, m): self.overviews[(h, m)] for h, ms in (overviews or {}).items() for m in ms},
                    "routes": {h: r for h, r in self.routes.items() if h in kits} if routes else {}}
        monkeypatch.setattr(board, "stamps_now", stamps_now)

        self.req, self.handed, self.found = {"main": "/kit/main"}, [], []

        def flow_read(fleet, labels, sweep=False):
            kept = plan.READ.follower
            self.reads.append((list(labels), sweep, plan.READ.tip("o/state", "wldn/main"), plan.READ.tip("o/state", "swancloud/main")))
            self.handed.append(dict(kept.queued))
            served = kept.served(BOX, "/kit/main", self.req)
            kept.use(BOX, "/kit/main", self.req, served or {"ok": True, "stamp": self.stamps[(BOX, "/kit/main")], "routes": []})
            if kept.cards is None:  # the tick's ask, which rail_read makes when the follower kept no read to ask from
                kept.cards = ({}, None)
            print("crew: a word the read said", file=sys.stderr)
            return {"found": list(self.found), "errors": {"wldn/main of o/state": "a plan it could not read"}, "signals": {}, "unchecked": list(self.unchecked),
                    "sv": {}, "rows": [], "cards": [], "unread": {}, "batched": {}, "served": served is not None}
        monkeypatch.setattr(board, "flow_read", flow_read)
        monkeypatch.setattr(board, "board_data", lambda fleet, labels, read, now: {"read_at": board.iso(now), "from": "mac-studio",
                                                                                   "partitions": [{"label": labels[0]}], "unread": {}})
        monkeypatch.setattr(plan, "rail_text", lambda fleet, labels, read, now: f"rail of {labels[0]}" + (", served" if read["served"] else ""))
        monkeypatch.setattr(board, "here_read", lambda fleet, l: {"host": "mac-studio", "version": None, "held": None, "agents": {}})
        monkeypatch.setattr(board, "agent_views", lambda data: {"read_at": data["read_at"], "views": {}})
        monkeypatch.setattr(plan, "sweep_sessions", lambda fleet, found, sv, rows, cards, unread, batched, only=None: self.swept.append(only) or ([], []))
        test = self

        class Here(board.Follower):
            def fleet(self):
                self.fleet_, self.labels = test.FLEET, board.labels_here(test.FLEET, "mac-studio")
                return test.FLEET

            def again(self, fleet):
                test.again.append(list(self.labels))
        return Here(None)

    def frame(self, label, kind="rail"):
        return json.loads((board.FRAMES / f"{label}{'.' + kind if kind != 'board' else ''}.json").read_text())

    def test_one_read_writes_every_partitions_frames_with_what_it_said(self, follower):
        follower.refresh()
        assert self.reads == [(["wldn", "swancloud"], True, "a" * 40, "")], "the read was not handed the tips the caches hold"
        assert self.frame("wldn")["text"] == "rail of wldn\ncrew: a word the read said\na plan it could not read"
        assert self.frame("swancloud")["text"] == "rail of swancloud\ncrew: a word the read said"
        assert self.frame("swancloud", "board")["partitions"] == [{"label": "swancloud"}] and self.frame("wldn", "agents")["views"] == {}

    def test_a_refresh_with_nothing_moved_reads_nothing_sweeps_nothing_and_writes_the_frames_again(self, follower):
        follower.refresh()
        was = self.frame("wldn")["read_at"]
        follower.refresh()
        assert len(self.reads) == 1 and self.swept == []
        assert self.frame("wldn")["text"] == "rail of wldn\na plan it could not read" and self.frame("wldn")["read_at"] >= was

    def test_a_refresh_after_a_kit_moved_reads_again_with_the_rest_served(self, follower):
        follower.refresh()
        self.stamps[(BOX, "/kit/main")] = "s2"
        follower.refresh()
        assert len(self.reads) == 2 and self.frame("wldn")["text"].startswith("rail of wldn\n")
        follower.refresh()
        assert len(self.reads) == 2, "a kit read at its new stamp was taken as moved again"
        self.looks["state"] = {"wldn": "d" * 40, "swancloud": ""}
        follower.refresh()
        assert len(self.reads) == 3 and self.frame("wldn")["text"].startswith("rail of wldn, served"), "an unmoved kit was not served"

    def test_its_check_stamps_the_readings_of_each_partitions_hosts_with_its_kits(self, follower):
        """The card-sessions spec, A reading sent on one host: every host where a partition's card sessions are swept,
        its main machine and its teams', has its readings stamped, from its first refresh on."""
        follower.refresh()
        follower.refresh()
        assert self.asked == [{"mac-studio": ["wldn", "swancloud"], BOX: ["wldn"]}] * 2

    def test_a_refresh_after_crew_moved_hands_out_the_restarts_and_starts_again(self, follower):
        follower.refresh()
        self.looks["crew"] = ("e" * 40, b"{teams}")
        follower.refresh()
        assert self.again == [["wldn", "swancloud"]]

    def test_the_clock_asks_pending_you_after_the_kept_reads_cards_once_a_tick_and_never_between(self, follower, monkeypatch):
        """The crew-board spec, The follower asks Pending You about cards on its clock: one bridge a tick for the cards the
        kept read's sweep would act on, none on a tick when it names none, and none at a refresh between ticks."""
        bridges, test = [], self
        self.to_ask = []

        class Py:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

            def answer(self, tool, args):
                return {"status": "pending"}, None

        class Acts:
            def __init__(self, fleet):
                pass

            def bridge(self, name, later, held=None):
                bridges.append(name)
                return Py()
        monkeypatch.setattr(plan, "SweepActs", Acts)
        monkeypatch.setattr(plan, "cards_asked", lambda fleet, read, here, now: list(test.to_ask))
        monkeypatch.setattr(plan, "sweep_cards", lambda fleet, read, acts=None, answers=None, listed=None: {"done": [], "unswept": []})
        monkeypatch.setattr(type(follower), "fetch", lambda self, fleet: None)
        follower.tick()
        follower.tick()
        assert bridges == [] and follower.kept.cards == ({}, None) and len(self.reads) == 1
        self.to_ask = ["req_p4"]
        follower.tick()
        assert bridges == ["crew"] and follower.kept.cards == ({"req_p4": ({"status": "pending"}, None)}, None)
        follower.refresh()
        follower.refresh()
        assert bridges == ["crew"], "a refresh between ticks asked Pending You"

    def test_a_refresh_after_only_a_hosts_readings_moved_sweeps_its_card_sessions_and_reads_nothing(self, follower):
        """The crew-board spec, A reading sent back: plannotator wrote the result in the box's readings folder."""
        follower.refresh()
        self.readings[BOX] = "r9"
        follower.refresh()
        assert len(self.reads) == 1 and self.swept == [{"wldn": {BOX}}]
        follower.refresh()
        assert len(self.reads) == 1 and self.swept == [{"wldn": {BOX}}], "a readings folder swept was taken as moved again"

    def test_a_refresh_after_only_the_cards_moved_runs_the_card_sweep_alone_against_the_kept_read(self, follower, monkeypatch):
        """The crew-board spec, A card lost between ticks: the tick's answers say proposal 4's card is lost."""
        swept = []
        monkeypatch.setattr(plan, "sweep_cards", lambda fleet, read, acts=None, answers=None, listed=None: swept.append((read["served"], answers)) or {
            "done": [dict(label="wldn", key="proposal/4", card="req_p4", by="wldn-planner", did="lost", words="posted again as req_p5", new="req_p5")],
            "unswept": []})
        follower.refresh()
        lost = ({"req_p4": (None, "Not found: request:req_p4.")}, None)
        follower.kept.cards, follower.cards = lost, board.cards_stamp(*lost, False, 2)
        follower.refresh()
        assert len(self.reads) == 1 and swept == [(False, lost)] and self.swept == []
        assert [c["card"] for c in follower.last["read"]["cards"]] == ["req_p5"]
        follower.refresh()
        assert swept == [(False, lost)], "the cards swept were taken as moved again before the next tick"

    def test_a_refresh_with_nothing_moved_sweeps_the_sessions_only_where_the_last_could_not(self, follower):
        """The card-sessions spec, A host the last sweep missed."""
        self.unchecked = [{"label": "wldn", "host": BOX, "why": "did not answer (exit 255)"}]
        follower.refresh()
        follower.refresh()
        assert self.swept == [{"wldn": {BOX}}] and len(self.reads) == 1
        follower.refresh()
        assert self.swept == [{"wldn": {BOX}}], "a host the sweep reached was asked again"


    class Watching(board.Watches):
        """The follower's watches with no process: what opens and closes is recorded, and a test sets what each read."""

        def __init__(self):
            super().__init__()
            self.opened, self.closed = [], []

        def open(self, fleet, host, main):
            self.ended.discard((host, main))
            self.opened.append((host, main))
            self.running[(host, main)] = None

        def close(self, key):
            if self.running.pop(key, "none") != "none":
                self.closed.append(key)

        def poll(self):
            pass

    QUEUED = {"schema": "sluice/overview@1", "at": "2026-10-28T16:24:41Z", "branches": [
        {"branch": "bolt/te", "submissions": [{"id": 41, "branch": "bolt/te", "state": "testing", "from": {"worktree": "unit/a"}}]}]}

    def test_a_new_line_from_a_kits_watch_remakes_its_submissions_with_nothing_gathered(self, follower):
        """The crew-board spec, A merge moves in sluice's queue: the watch opened at the first read prints a submission;
        the next refresh takes it into the kept answer, gathers nothing, and a line differing only in its time moves
        nothing; a refresh that gathers the kit hands it the line in place of running sluice."""
        self.req = {"main": "/kit/main", "bolts": ["te"]}
        follower.watches = w = self.Watching()
        follower.refresh()
        assert w.opened == [(BOX, "/kit/main")] and len(self.reads) == 1
        empty = dict(self.QUEUED, branches=[])
        w.states[(BOX, "/kit/main")] = {"doc": empty}
        follower.refresh()
        assert len(self.reads) == 1 and follower.kept.kits[BOX]["/kit/main"][1]["submissions"] == []
        w.states[(BOX, "/kit/main")] = {"doc": self.QUEUED}
        follower.refresh()
        answer = follower.kept.kits[BOX]["/kit/main"][1]
        assert len(self.reads) == 1 and [s["id"] for s in answer["submissions"]] == [41] and "submissions_error" not in answer
        assert follower.last["read"]["served"] is False, "the queue's move read again"
        w.states[(BOX, "/kit/main")] = {"doc": dict(self.QUEUED, at="2026-10-28T16:30:00Z")}
        assert not board.moved(follower.last["stamps"], dict(follower.last["stamps"], queues=w.stamp()))["any"]
        self.stamps[(BOX, "/kit/main")] = "s2"
        follower.refresh()
        assert len(self.reads) == 2 and self.handed[-1] == {(BOX, "/kit/main"): [answer["submissions"], None]}
        assert w.opened == [(BOX, "/kit/main")] and w.closed == [], "a watch was opened twice"

    def test_a_merge_decided_between_gathers_is_kept_at_its_recent_events_time_and_after_the_next_gather(self, follower):
        """The crew-board spec, A merge decided between gathers: b's merge #41, kept since it was submitted at 16:00 and
        tested from 16:05, leaves the queue on a line whose recent events say it landed at 16:17; the follower keeps it
        decided at 16:17, starts no process to learn it, and still holds it after the next gather of the kit, which it
        hands what it kept."""
        self.req = {"main": "/kit/main", "bolts": ["te"]}
        follower.watches = w = self.Watching()
        follower.refresh()
        answer = follower.kept.kits[BOX]["/kit/main"][1]
        testing = dict(self.QUEUED, branches=[dict(self.QUEUED["branches"][0], candidates=[
            {"id": "c1", "state": "testing", "started": "2026-10-28T16:05:00Z", "submissions": [41]}], submissions=[
            dict(self.QUEUED["branches"][0]["submissions"][0], submitted="2026-10-28T16:00:00Z")])])
        w.states[(BOX, "/kit/main")] = {"doc": testing}
        follower.refresh()
        assert answer["decided"] == [] and [s["started"] for s in answer["submissions"]] == ["2026-10-28T16:05:00Z"]
        w.states[(BOX, "/kit/main")] = {"doc": dict(self.QUEUED, at="2026-10-28T16:18:00Z", branches=[dict(self.QUEUED["branches"][0], submissions=[],
            recent=[{"at": "2026-10-28T16:17:00Z", "event": "landed", "ids": [41]}], recent_from={"41": "unit/a"})])}
        follower.refresh()
        landed = {"id": 41, "bolt": "te", "branch": "bolt/te", "worktree": "unit/a", "pull_head": None, "submitted": "2026-10-28T16:00:00Z",
                  "started": "2026-10-28T16:05:00Z", "decided": "2026-10-28T16:17:00Z", "event": "landed"}
        assert len(self.reads) == 1 and answer["submissions"] == [] and answer["decided"] == [landed], "the queue's move gathered the kit"
        self.stamps[(BOX, "/kit/main")] = "s2"
        follower.refresh()
        assert len(self.reads) == 2 and plan.READ.follower is None
        assert follower.kept.kits[BOX]["/kit/main"][1]["decided"] == [landed], "a gather threw away what the follower kept"

    def test_a_kits_gather_is_handed_what_the_follower_kept_beside_its_queue(self, follower):
        self.req = {"main": "/kit/main", "bolts": ["te"]}
        follower.watches = w = self.Watching()
        follower.refresh()
        w.states[(BOX, "/kit/main")] = {"doc": self.QUEUED}
        follower.refresh()
        w.states[(BOX, "/kit/main")] = {"doc": dict(self.QUEUED, at="2026-10-28T16:30:00Z", branches=[])}
        follower.refresh()
        self.stamps[(BOX, "/kit/main")] = "s2"
        decided = []
        gathered = board.flow_read

        def kept_too(fleet, labels, sweep=False):
            decided.append(dict(plan.READ.follower.decided))
            return gathered(fleet, labels, sweep)
        board.flow_read = kept_too
        try:
            follower.refresh()
        finally:
            board.flow_read = gathered
        assert decided == [{(BOX, "/kit/main"): [[{"id": 41, "bolt": "te", "branch": "bolt/te", "worktree": "unit/a", "pull_head": None,
                                                    "submitted": None, "started": None, "decided": "2026-10-28T16:30:00Z", "event": "gone"}], None]}]

    def test_a_new_watch_starts_from_the_overview_its_kits_gather_read_so_its_first_line_moves_nothing(self, follower, monkeypatch):
        """A kit's queue is read once: the gather's own overview is the kept line the watch's first is compared with."""
        self.req = {"main": "/kit/main", "bolts": ["te"]}
        follower.watches = w = self.Watching()
        gathered = board.flow_read

        def with_overview(fleet, labels, sweep=False):
            got = gathered(fleet, labels, sweep)
            plan.READ.follower.used[BOX]["/kit/main"][1]["overview"] = self.QUEUED
            return got
        monkeypatch.setattr(board, "flow_read", with_overview)
        follower.refresh()
        assert w.states == {(BOX, "/kit/main"): {"doc": self.QUEUED}}
        w.states[(BOX, "/kit/main")] = {"doc": dict(self.QUEUED, at="2026-10-28T16:30:00Z")}
        assert follower.look(self.FLEET) == follower.seen, "the watch's first line woke the follower"
        follower.refresh()
        answer = follower.kept.kits[BOX]["/kit/main"][1]
        assert len(self.reads) == 1 and "submissions" not in answer and "overview" not in answer, "the first line was taken as a move"

    def test_a_queue_an_ended_watch_left_unread_takes_the_overview_its_gather_read_and_never_a_stale_one(self):
        w = self.Watching()
        w.end((BOX, "/kit/main"), "sluice overview --watch exited 255")
        answer = {"ok": True, "overview": self.QUEUED}
        assert w.seed({BOX: {"/kit/main": ({"main": "/kit/main"}, answer)}}) and w.states[(BOX, "/kit/main")] == {"doc": self.QUEUED}
        assert "overview" not in answer
        w.end((BOX, "/kit/main"), "sluice overview --watch exited 255")
        assert not w.seed({BOX: {"/kit/main": ({"main": "/kit/main"}, answer)}}) and "why" in w.states[(BOX, "/kit/main")]
        w.states[(BOX, "/kit/main")] = {"doc": dict(self.QUEUED, branches=[])}
        assert not w.seed({BOX: {"/kit/main": ({"main": "/kit/main"}, {"ok": True, "overview": self.QUEUED})}}), "a watch's line was overwritten"

    def test_a_watch_that_ended_says_why_on_its_rows_and_is_opened_and_asked_once_at_the_next_tick(self, follower, monkeypatch):
        """The crew-board spec, A watch ends: the ssh holding it dropped."""
        self.req = {"main": "/kit/main", "bolts": ["te"]}
        follower.watches = w = self.Watching()
        monkeypatch.setattr(type(follower), "fetch", lambda self, fleet: None)
        monkeypatch.setattr(type(follower), "ask", lambda self, fleet: None)
        follower.refresh()
        w.running.pop((BOX, "/kit/main"))
        w.end((BOX, "/kit/main"), "sluice overview --watch exited 255: Connection closed, on " + BOX)
        follower.refresh()
        answer = follower.kept.kits[BOX]["/kit/main"][1]
        assert answer["submissions"] is None and answer["submissions_error"].startswith("its overview watch ended (sluice overview --watch exited 255")
        assert w.opened == [(BOX, "/kit/main")] and self.overviews_asked == [], "the watch was opened again, or asked, between ticks"
        self.overviews[(BOX, "/kit/main")] = {"doc": self.QUEUED}
        follower.tick()
        assert w.opened == [(BOX, "/kit/main")] * 2 and self.overviews_asked == [(BOX, "/kit/main")]
        assert [s["id"] for s in follower.kept.kits[BOX]["/kit/main"][1]["submissions"]] == [41] and len(self.reads) == 1


    def test_every_refresh_reckons_a_batch_from_the_kept_read_and_one_told_is_not_reckoned_again_at_that_tip(self, follower, monkeypatch):
        """The crew-board spec, A batch made due by the hours: nothing moves, and each refresh reckons from the kept read."""
        reckoned = []
        monkeypatch.setattr(plan, "reckon_batches", lambda fleet, found, read, skip=(): reckoned.append(set(skip)) or ({"wldn": True} if not skip else {}))
        self.found = [("wldn", "o/state", "a" * 40, None)]
        follower.refresh()
        follower.refresh()
        follower.refresh()
        assert len(self.reads) == 1 and reckoned == [set(), {"wldn"}]
        self.looks["state"] = {"wldn": "d" * 40, "swancloud": ""}
        self.found = [("wldn", "o/state", "d" * 40, None)]
        follower.refresh()
        follower.refresh()
        assert len(self.reads) == 2 and reckoned[-1] == set(), "a partition told at an older tip was not reckoned at the new one"

    def test_a_tell_that_did_not_go_through_is_tried_again_at_the_next_tick_and_not_between(self, follower, monkeypatch):
        """wldn's planner is not up: the tell starts herdr, so it is not made at every refresh."""
        reckoned = []
        monkeypatch.setattr(plan, "reckon_batches", lambda fleet, found, read, skip=(): reckoned.append(set(skip)) or ({} if skip else {"wldn": False}))
        monkeypatch.setattr(type(follower), "fetch", lambda self, fleet: None)
        monkeypatch.setattr(type(follower), "ask", lambda self, fleet: None)
        self.found = [("wldn", "o/state", "a" * 40, None)]
        follower.refresh()
        follower.refresh()
        follower.refresh()
        follower.tick()
        assert len(self.reads) == 1 and reckoned == [set(), {"wldn"}, set()]

    def test_a_dev_server_started_by_hand_is_drawn_after_the_next_tick_with_nothing_gathered(self, follower, monkeypatch):
        """The crew-board spec, A dev server started by hand: the tick reads the box's portless routes again."""
        monkeypatch.setattr(type(follower), "fetch", lambda self, fleet: None)
        monkeypatch.setattr(type(follower), "ask", lambda self, fleet: None)
        follower.refresh()
        route = [{"url": "https://unit-a--switchboard-kit.local", "name": "unit-a--switchboard-kit"}]
        self.routes = {BOX: route}
        follower.refresh()
        assert follower.kept.kits[BOX]["/kit/main"][1]["routes"] == [], "routes were read between ticks"
        follower.tick()
        assert len(self.reads) == 1 and follower.kept.kits[BOX]["/kit/main"][1]["routes"] == route
        follower.tick()
        assert len(self.reads) == 1 and self.swept == []

    def test_an_askers_pane_emptied_moves_the_cards_at_the_tick_and_the_sweep_judges_with_the_listing(self, follower, monkeypatch):
        """The crew-board spec, An asker's agent gone: herdr's listing is read at the tick beside Pending You's answers,
        and the card sweep between ticks judges with it."""
        listing, swept = {"crw-3-conductor": (True, None)}, []
        monkeypatch.setattr(type(follower), "fetch", lambda self, fleet: None)
        monkeypatch.setattr(plan, "cards_asked", lambda fleet, read, here, now: [])
        monkeypatch.setattr(plan, "askers_asked", lambda fleet, read, here, now: ["crw-3-conductor"])
        monkeypatch.setattr(plan, "askers_listed", lambda fleet, names: {n: listing[n] for n in names})
        monkeypatch.setattr(plan, "sweep_cards", lambda fleet, read, acts=None, answers=None, listed=None: swept.append(listed) or {"done": [], "unswept": []})
        follower.tick()
        follower.tick()  # the first tick read the kits and asked nothing of herdr, having no read to ask from
        swept.clear()
        follower.tick()
        assert swept == [] and follower.kept.listed == {"crw-3-conductor": (True, None)}, "the same listing moved the cards"
        listing["crw-3-conductor"] = (False, None)
        follower.refresh()
        assert swept == [], "herdr was read between ticks"
        follower.tick()
        assert swept == [{"crw-3-conductor": (False, None)}] and len(self.reads) == 1


def test_the_session_sweep_after_nothing_moved_asks_the_host_the_last_could_not_check_and_no_other(monkeypatch):
    """The card-sessions spec, A host the last sweep missed: unchecked {box} and nothing moved, the box alone is asked."""
    import subprocess
    asked = []
    monkeypatch.setattr(crew, "crew_argv", lambda fleet, h, *a: ["crew", *a])
    monkeypatch.setattr(crew, "on_machine", lambda fleet, h, argv, input=None: asked.append(h) or subprocess.CompletedProcess(argv, 0, "[]", ""))
    found = [("wldn", "WilldanGroup/crew-state", "a" * 40, the_plan())]
    only = plan.sessions_unchecked([{"label": "wldn", "host": BOX, "why": "did not answer (exit 255)"}])
    assert only == {"wldn": {BOX}}
    assert plan.sweep_sessions(FLEET, found, {}, [], [], {}, {}, only) == ([], []) and asked == [BOX]
    asked.clear()
    plan.sweep_sessions(FLEET, found, {}, [], [], {}, {})
    assert asked == [BOX, "mac-studio"], "a refresh after a change did not sweep every host"
    assert plan.sessions_unchecked([]) == {}


def test_the_check_asks_each_host_once_for_its_kits_and_its_readings(monkeypatch):
    """The crew-board spec, A refresh after nothing moved reads nothing: a host's kits and its card readings folders are
    stamped in one request to it, a host with no kit asked for its readings alone, and one that does not answer has
    every stamp of its None, which counts as moved (read.1)."""
    asked = []

    def stamped(fleet, host, kits, labels=(), overviews=(), routes=False):
        asked.append((host, [k["main"] for k in kits], list(labels)))
        return (None, "exit 255") if host == "macbook-pro" else ({"kits": {k["main"]: "s" for k in kits}, "readings": "r"}, None)
    monkeypatch.setattr(plan, "stamped", stamped)
    got = board.stamps_now({}, {BOX: {"/kit/main": ({"main": "/kit/main"}, {})}, "macbook-pro": {"/b/main": ({"main": "/b/main"}, {})}},
                           {BOX: ["wldn"], "mac-studio": ["wldn", "swancloud"], "macbook-pro": ["wldn"]})
    assert asked == [(BOX, ["/kit/main"], ["wldn"]), ("mac-studio", [], ["wldn", "swancloud"]), ("macbook-pro", ["/b/main"], ["wldn"])]
    assert got == {"kits": {(BOX, "/kit/main"): "s", ("macbook-pro", "/b/main"): None}, "readings": {BOX: "r", "mac-studio": "r", "macbook-pro": None},
                   "overviews": {}, "routes": {}}
    fleet = {"partitions": {"wldn": {"machine": "mac-studio", "teams": ["swb-1", "swb-2"]}, "swancloud": {"machine": "mac-studio", "teams": []}},
             "teams": {"swb-1": {"machine": BOX}, "swb-2": {"machine": BOX}}}
    assert board.readings_hosts(fleet, ["wldn", "swancloud"]) == {BOX: ["wldn"], "mac-studio": ["wldn", "swancloud"]}


class TestMoved:
    """The follower's check before it reads (the crew-board spec, A refresh after nothing moved reads nothing): what moved
    between the stamps its last read was made at and the stamps now."""

    KEPT = {"crew": ("c" * 40, b"{teams}"), "state": {"wldn": "a" * 40, "swancloud": ""}, "blueprints": {"wldn": "b" * 40, "swancloud": "b" * 40},
            "kits": {(BOX, "/kit/main"): "s1", ("mac-studio", "/a/main"): "s2"}, "readings": {BOX: "r1", "mac-studio": "r2"}}

    def now(self, **kw):
        return {k: ({**self.KEPT[k], **kw[k]} if k in kw and isinstance(self.KEPT[k], dict) else kw.get(k, self.KEPT[k])) for k in self.KEPT}

    def test_nothing_moved_names_nothing_and_a_branch_the_cache_lacks_stands(self):
        assert board.moved(self.KEPT, self.now()) == {"crew": False, "state": set(), "blueprints": set(), "kits": set(), "readings": set(),
                                                      "cards": False, "queues": set(), "read": False, "any": False}

    def test_one_state_tip_moved_names_its_partition_alone(self):
        m = board.moved(self.KEPT, self.now(state={"wldn": "d" * 40}))
        assert m["state"] == {"wldn"} and not m["crew"] and m["blueprints"] == m["kits"] == set() and m["any"]

    def test_one_kit_moved_names_that_kit_on_its_host(self):
        m = board.moved(self.KEPT, self.now(kits={(BOX, "/kit/main"): "s9"}))
        assert m["kits"] == {(BOX, "/kit/main")} and m["state"] == set() and m["any"]

    def test_a_kit_whose_stamp_could_not_be_read_counts_as_moved(self):
        assert board.moved(self.KEPT, self.now(kits={(BOX, "/kit/main"): None}))["kits"] == {(BOX, "/kit/main")}
        assert board.moved(dict(self.KEPT, kits={(BOX, "/kit/main"): None}), dict(self.KEPT, kits={(BOX, "/kit/main"): None}))["kits"] == {(BOX, "/kit/main")}

    def test_a_kit_new_to_the_read_or_gone_from_it_counts_as_moved(self):
        m = board.moved(self.KEPT, dict(self.KEPT, kits={("mac-studio", "/a/main"): "s2", (BOX, "/b/main"): "s3"}))
        assert m["kits"] == {(BOX, "/kit/main"), (BOX, "/b/main")}

    def test_only_one_hosts_readings_moved_names_that_host_and_nothing_to_read(self):
        """The crew-board spec, A reading sent back: plannotator wrote a result in the box's readings folder."""
        m = board.moved(self.KEPT, self.now(readings={BOX: "r9"}))
        assert m["readings"] == {BOX} and m["kits"] == m["state"] == m["blueprints"] == set() and not m["crew"]
        assert m["any"] and not m["read"]

    def test_a_host_whose_readings_could_not_be_stamped_counts_as_moved(self):
        assert board.moved(self.KEPT, self.now(readings={BOX: None}))["readings"] == {BOX}

    FOUND = {"req_p4": ({"status": "pending", "version": 2}, None), "req_q1": (None, "This is wldn-ops's card; leave it.")}

    def test_the_same_answers_at_the_next_tick_leave_the_cards_and_one_card_now_lost_moves_them(self):
        """The crew-board spec, A card lost between ticks: Pending You answered alike, then no longer finds proposal 4's."""
        kept = dict(self.KEPT, cards=board.cards_stamp(self.FOUND, None, False, 1))
        assert not board.moved(kept, dict(kept, cards=board.cards_stamp(dict(self.FOUND), None, False, 2)))["any"]
        m = board.moved(kept, dict(kept, cards=board.cards_stamp(dict(self.FOUND, req_p4=(None, "Not found: request:req_p4.")), None, False, 2)))
        assert m["cards"] and m["any"] and not m["read"] and m["readings"] == m["kits"] == set()

    def test_a_failed_bridge_or_a_card_the_last_sweep_left_moves_the_cards_at_each_tick_and_only_then(self):
        """A card left because its act did not go through is tried again once a minute, not at every refresh."""
        for why, left in (("Pending You did not answer whoami within 30 seconds.", False), (None, True)):
            at_tick = board.cards_stamp(self.FOUND, why, left, 2)
            assert board.moved(dict(self.KEPT, cards=board.cards_stamp(self.FOUND, None, False, 1)), dict(self.KEPT, cards=at_tick))["cards"]
            kept = dict(self.KEPT, cards=at_tick)
            assert not board.moved(kept, dict(kept))["cards"], "a refresh between ticks took the cards as moved again"
            assert board.moved(kept, dict(kept, cards=board.cards_stamp(self.FOUND, why, left, 3)))["cards"]

    def test_an_askers_pane_now_empty_at_the_tick_moves_the_cards(self):
        """The crew-board spec, An asker's agent gone: herdr's listing read at the tick beside Pending You's answers."""
        kept = dict(self.KEPT, cards=board.cards_stamp(self.FOUND, None, False, 1, {"crw-3-conductor": (True, None)}))
        assert not board.moved(kept, dict(kept, cards=board.cards_stamp(self.FOUND, None, False, 2, {"crw-3-conductor": (True, None)})))["any"]
        m = board.moved(kept, dict(kept, cards=board.cards_stamp(self.FOUND, None, False, 2, {"crw-3-conductor": (False, None)})))
        assert m["cards"] and not m["read"]

    def test_crews_head_or_the_teams_file_moved_or_unreadable_says_crew_moved(self):
        assert board.moved(self.KEPT, self.now(crew=("e" * 40, b"{teams}")))["crew"]
        assert board.moved(self.KEPT, self.now(crew=("c" * 40, b"{teams, again}")))["crew"]
        assert board.moved(self.KEPT, self.now(crew=(None, b"{teams}")))["crew"]

    def test_with_no_read_kept_everything_has_moved(self):
        m = board.moved(None, self.KEPT)
        assert m["crew"] and m["state"] == {"wldn", "swancloud"} and m["kits"] == set(self.KEPT["kits"]) and m["any"] and m["read"]
        assert m["readings"] == {BOX, "mac-studio"}


def test_no_asker_to_ask_after_reads_no_herdr_and_each_asker_named_is_listed_afresh(monkeypatch):
    """herdr's listing of the askers is read afresh at the tick, its sessions listed again (crew.herdr_fresh)."""
    fresh = []
    monkeypatch.setattr(crew, "herdr_fresh", lambda: fresh.append(1))
    assert plan.askers_listed(FLEET, []) == {} and fresh == []

    class Acts:
        def listed(self, name):
            return (name == "swb-1-conductor", None)
    assert plan.askers_listed(FLEET, ["swb-1-conductor", "crw-3-conductor"], Acts()) == {"swb-1-conductor": (True, None), "crw-3-conductor": (False, None)}
    assert fresh == [1]


def test_no_card_to_ask_after_starts_no_bridge_and_the_cards_asked_are_asked_in_one():
    """The crew-board spec, No card to ask about: no bridge at all (a logic test's subprocess raises); and the cards the
    clock's tick asks after are asked in one bridge in crew's own name."""
    assert plan.cards_fetched(FLEET, []) == ({}, None)
    opened = []

    class Py:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def answer(self, tool, args):
            opened.append((tool, args["requestId"], args["name"]))
            return {"status": "pending"}, None

    class Acts:
        def bridge(self, name, later, held=None):
            opened.append(name)
            return Py()
    assert plan.cards_fetched(FLEET, ["req_1", "req_2"], Acts()) == ({"req_1": ({"status": "pending"}, None), "req_2": ({"status": "pending"}, None)}, None)
    assert opened == ["crew", ("get_request", "req_1", "crew"), ("get_request", "req_2", "crew")]


class TestWatches:
    """The follower's overview watches (the crew-board spec, The follower follows each kit's queue through sluice's
    overview): what moves a kit's queue, and which watches open, close and are asked on the clock."""

    DOC = {"schema": "sluice/overview@1", "at": "2026-10-28T16:24:41Z", "host": BOX, "branches": [
        {"branch": "bolt/te", "submissions": [{"id": 41, "branch": "bolt/te", "state": "testing", "from": {"worktree": "unit/a"}}]}]}
    KIT, OTHER = (BOX, "/kit/main"), ("mac-studio", "/a/main")

    def test_a_line_differing_only_in_its_time_moves_nothing_and_a_new_submission_moves_the_queue(self):
        assert not board.queue_moved(self.DOC, dict(self.DOC, at="2026-10-28T16:30:00Z"))
        queued = dict(self.DOC, branches=[dict(self.DOC["branches"][0], submissions=self.DOC["branches"][0]["submissions"] + [
            {"id": 42, "branch": "bolt/te", "state": "queued", "from": {"worktree": "unit/b"}}])])
        assert board.queue_moved(self.DOC, queued) and board.queue_moved(None, self.DOC)
        assert board.queue_stamp({"doc": self.DOC}) == board.queue_stamp({"doc": dict(self.DOC, at="2026-10-28T17:00:00Z")})
        assert [s["id"] for s in board.queue_of({"doc": queued})[0]] == [41, 42]
        assert board.queue_of({"why": "its overview watch ended"}) == (None, "its overview watch ended")

    @staticmethod
    def line(at, standing=(), testing=None, recent=(), recent_from=None, main=()):
        """An overview's document at a time (at): b's branch, bolt/te, holding its standing submissions, the one testing
        from testing's time, and its recent events; main holding its own standing."""
        branches = [{"branch": "bolt/te", "submissions": list(standing), "recent": list(recent), "recent_from": recent_from or {},
                     "candidates": [{"state": "testing", "started": testing, "submissions": [standing[0]["id"]]}] if testing else []},
                    {"branch": "main", "submissions": list(main), "recent": [], "recent_from": {}}]
        return {"schema": "sluice/overview@1", **({"at": at} if at else {}), "branches": branches}

    A = {"id": 41, "branch": "bolt/te", "state": "queued", "submitted": "2026-10-28T14:00:00Z", "from": {"worktree": "unit/a"}}

    def kept41(self, **fields):
        return dict({"id": 41, "bolt": "te", "branch": "bolt/te", "worktree": "unit/a", "pull_head": None, "submitted": "2026-10-28T14:00:00Z",
                     "started": None, "decided": None, "event": None}, **fields)

    def test_a_merge_kept_from_its_submit_takes_its_checks_start_once_seen_and_never_clears_it(self):
        """Decision 2 of a-rows-age-and-holder-come-from-the-followers-overview: started from the candidate testing it."""
        kept = board.kept_submissions({}, self.line("2026-10-28T14:01:00Z", [self.A]), ["te"])
        assert kept == {41: self.kept41()}
        kept = board.kept_submissions(kept, self.line("2026-10-28T14:06:00Z", [dict(self.A, state="testing")], testing="2026-10-28T14:05:00Z"), ["te"])
        assert kept[41]["started"] == "2026-10-28T14:05:00Z"
        kept = board.kept_submissions(kept, self.line("2026-10-28T14:10:00Z", [dict(self.A, state="passed")]), ["te"])
        assert kept == {41: self.kept41(started="2026-10-28T14:05:00Z")}, "a start of checks once seen was cleared"

    def test_a_merge_that_leaves_the_queue_is_decided_at_its_recent_events_time(self):
        """The crew-board spec, A merge decided between gathers."""
        kept = {41: self.kept41(started="2026-10-28T14:05:00Z")}
        got = board.kept_submissions(kept, self.line("2026-10-28T14:18:00Z", recent=[{"at": "2026-10-28T14:17:00Z", "event": "landed", "ids": [41]}],
                                                     recent_from={"41": "unit/a"}), ["te"])
        assert got == {41: self.kept41(started="2026-10-28T14:05:00Z", decided="2026-10-28T14:17:00Z", event="landed")}
        assert board.kept_submissions(got, self.line("2026-10-28T15:00:00Z"), ["te"]) == got, "a decided merge was decided again"

    def test_a_withdrawn_merge_is_decided_at_the_lines_time(self):
        """The crew-board spec, A withdrawn merge: a line printed at 14:20 whose recent events do not name it."""
        got = board.kept_submissions({41: self.kept41()}, self.line("2026-10-28T14:20:00Z"), ["te"])
        assert got == {41: self.kept41(decided="2026-10-28T14:20:00Z", event="gone")}

    def test_a_merge_decided_before_the_follower_saw_it_is_kept_with_its_decision_alone(self):
        recent = [{"at": "2026-10-28T13:58:00Z", "event": "landed", "id": 40}]
        got = board.kept_submissions({}, self.line("2026-10-28T14:20:00Z", recent=recent, recent_from={"40": "unit/b"}), ["te"])
        assert got == {40: {"id": 40, "bolt": "te", "branch": "bolt/te", "worktree": "unit/b", "pull_head": None, "submitted": None,
                            "started": None, "decided": "2026-10-28T13:58:00Z", "event": "landed"}}
        assert board.decided_kept(got) == [got[40]]

    def test_a_submission_of_a_bolt_no_longer_asked_is_dropped(self):
        other = dict(self.A, id=50, branch="bolt/zz", **{"from": {"worktree": "unit/z"}})
        got = board.kept_submissions({41: self.kept41()}, self.line("2026-10-28T14:20:00Z", [self.A]), [])
        assert got == {}, "a bolt no longer asked was kept"
        assert board.kept_submissions({}, dict(self.line("2026-10-28T14:20:00Z"), branches=[{"branch": "bolt/zz", "submissions": [other]}]), ["te"]) == {}

    def test_a_line_with_no_time_decides_nothing_and_one_crew_cant_read_changes_nothing(self):
        """read.1: a document with no time decides a kept merge at no guess."""
        kept = {41: self.kept41()}
        assert board.kept_submissions(kept, self.line(None), ["te"]) == kept
        assert board.kept_submissions(kept, {"schema": "sluice/overview@2"}, ["te"]) == kept
        got = board.kept_submissions(kept, self.line(None, recent=[{"at": "2026-10-28T14:17:00Z", "event": "blamed", "ids": [41]}]), ["te"])
        assert got[41]["decided"] == "2026-10-28T14:17:00Z", "sluice's own time for a decision was not taken from a line with none of its own"

    def test_a_landing_on_main_is_kept_by_the_bolt_it_came_from_and_one_by_pull_request_alone_while_the_line_names_it(self):
        """crew-board "A landing by pull request": the follower can't tell a pull/<n> landing's bolt from its events, so
        it keeps it while the line names it, for plan.bolt_facts to take by the run record's number."""
        landing = {"id": 52, "branch": "main", "state": "queued", "submitted": "2026-10-28T15:00:00Z", "from": {"worktree": "pull/9", "head": "bolt/te"}}
        got = board.kept_submissions({}, self.line("2026-10-28T15:01:00Z", main=[landing]), ["te"])
        assert (got[52]["bolt"], got[52]["pull_head"]) == ("te", "bolt/te")
        doc = self.line("2026-10-28T15:30:00Z")
        doc["branches"][1].update(recent=[{"at": "2026-10-28T15:20:00Z", "event": "landed", "ids": [53]}], recent_from={"53": "pull/10"})
        got = board.kept_submissions(got, doc, ["te"])
        assert (got[52]["decided"], got[52]["event"]) == ("2026-10-28T15:30:00Z", "gone") and (got[53]["bolt"], got[53]["worktree"]) == (None, "pull/10")
        assert 53 not in board.kept_submissions(got, self.line("2026-10-28T16:00:00Z"), ["te"]), "a landing no line names any more was kept"

    def test_a_watch_opens_for_each_kit_shown_and_closes_for_one_no_longer_shown(self):
        assert board.watch_plan({self.KIT, self.OTHER}, set(), set(), set(), False) == {"open": [self.KIT, self.OTHER], "close": [], "ask": []}
        assert board.watch_plan({self.KIT}, {self.KIT, self.OTHER}, set(), set(), True) == {"open": [], "close": [self.OTHER], "ask": []}

    def test_a_host_whose_sluice_refused_watch_is_asked_on_the_clock_alone(self):
        """The crew-board spec, A host whose sluice has no watch."""
        assert board.watch_plan({self.KIT, self.OTHER}, {self.OTHER}, {BOX}, set(), False) == {"open": [], "close": [], "ask": []}
        assert board.watch_plan({self.KIT, self.OTHER}, {self.OTHER}, {BOX}, set(), True) == {"open": [], "close": [], "ask": [self.KIT]}
        assert board.watch_refused(2, "sluice overview --watch exited 2: error: unexpected argument '--watch' found")
        assert not board.watch_refused(255, "sluice overview --watch exited 255: Connection closed")

    def test_an_ended_watch_is_opened_again_at_the_next_tick_and_asked_once_then(self):
        """The crew-board spec, A watch ends."""
        assert board.watch_plan({self.KIT}, set(), set(), {self.KIT}, False) == {"open": [], "close": [], "ask": []}
        assert board.watch_plan({self.KIT}, set(), set(), {self.KIT}, True) == {"open": [self.KIT], "close": [], "ask": [self.KIT]}

    def test_the_same_routes_move_nothing_and_a_new_one_moves_its_host(self):
        """The crew-board spec, A dev server started by hand."""
        a = {"url": "https://unit-a--switchboard-kit.local", "name": "unit-a--switchboard-kit"}
        kits = {BOX: {"/kit/main": ({"main": "/kit/main"}, {"ok": True, "routes": [a]}), "/b/main": ({"main": "/b/main"}, {"ok": False})},
                "mac-studio": {"/a/main": ({"main": "/a/main"}, {"ok": True, "routes": None})}}
        assert board.routes_moved(kits, {BOX: [a], "mac-studio": None}) == set()
        assert board.routes_moved(kits, {BOX: [a, dict(a, name="unit-b--switchboard-kit")], "mac-studio": None}) == {BOX}
        assert board.routes_moved(kits, {"mac-studio": []}) == {"mac-studio"}

    def test_the_kits_shown_are_those_read_with_bolts(self):
        kits = {BOX: {"/kit/main": ({"main": "/kit/main", "bolts": ["te"]}, {"ok": True}), "/b/main": ({"main": "/b/main", "bolts": []}, {"ok": True})},
                "mac-studio": {"/a/main": ({"main": "/a/main", "bolts": ["maps"]}, None)}}
        assert board.queue_kits(kits) == {self.KIT}

    def test_a_watch_is_read_without_blocking_its_last_line_taken_and_its_end_said(self, monkeypatch):
        """Watches.poll on a stand-in for the watch's process, its output a pipe: a line read whole, a part line kept for
        the next look, and an end that says sluice refused --watch marks the host as asking on the clock."""
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")

        class Proc:
            def __init__(self):
                (r, self.w), (e, self.ew) = os.pipe(), os.pipe()
                self.stdout, self.stderr = os.fdopen(r, "rb"), os.fdopen(e, "rb")

            def wait(self, timeout=None):
                return 2
        w, p = board.Watches(), Proc()
        for pipe in (p.stdout, p.stderr):
            os.set_blocking(pipe.fileno(), False)
        w.running[self.KIT] = {"proc": p, "out": b"", "err": b""}
        w.poll()
        assert w.states == {} and self.KIT in w.running
        line = json.dumps(self.DOC).encode()
        os.write(p.w, line + b"\n" + line[:10])
        w.poll()
        assert w.states == {self.KIT: {"doc": self.DOC}} and w.running[self.KIT]["out"] == line[:10]
        os.write(p.ew, b"error: unexpected argument '--watch' found\n")
        os.close(p.w)
        os.close(p.ew)
        w.poll()
        assert self.KIT not in w.running and w.ended == {self.KIT} and w.refused == {BOX}
        assert w.states[self.KIT]["why"] == ("its overview watch ended (sluice overview --watch exited 2: error: unexpected argument '--watch' "
                                             f"found, on {BOX}), and is opened again at the follower's next tick")


class TestKept:
    """What the host's follower keeps between its refreshes and serves while it has not moved (the crew-board spec, A
    refresh after a change reads only what moved; plan.12's reading of 2026-10-28)."""

    REQ = {"main": "/kit/main", "dir": "/kit", "bolts": [], "slots": {"swb-1": "~/.local/state/swb-1-team/slots"}}
    ANSWER = {"ok": True, "main": [], "stamp": "s1"}

    def test_a_kit_is_served_only_at_the_stamp_and_request_it_was_read_at(self):
        kept = (self.REQ, self.ANSWER)
        assert plan.kit_served(kept, "s1", self.REQ) == self.ANSWER
        assert plan.kit_served(kept, "s2", self.REQ) is None, "a moved kit was served"
        assert plan.kit_served(kept, "s1", dict(self.REQ, bolts=["tenant-environments"])) is None, "a kit asked of anew was served"
        assert plan.kit_served(kept, None, self.REQ) is None, "a kit whose stamp could not be read was served"
        assert plan.kit_served((self.REQ, None), "s1", self.REQ) is None and plan.kit_served(None, "s1", self.REQ) is None

    def test_a_board_survey_asks_each_host_for_its_moved_kits_alone_and_keeps_what_it_read(self, monkeypatch):
        asked = []

        def gathered(fleet, host, req):
            asked.append((host, sorted(k["main"] for k in req["kits"]), req.get("stamped")))
            return {k["main"]: {"ok": True, "stamp": "new"} for k in req["kits"]}, None
        monkeypatch.setattr(plan, "gathered", gathered)
        held = [(t, None) for t in FLEET["partitions"]["wldn"]["teams"]]
        k = plan.Kept()
        monkeypatch.setattr(plan.READ, "follower", k)
        first = plan.survey(FLEET, held, board=True)
        assert sorted(asked) == [("chuck-herdr-alpha", ["/b/main", "/kit/main"], True), ("mac-studio", ["/a/main"], True)]
        k.settle()
        k.stamps = {(BOX, "/kit/main"): "new", (BOX, "/b/main"): "moved", ("mac-studio", "/a/main"): "new"}
        asked.clear()
        again = plan.survey(FLEET, held, board=True)
        assert asked == [(BOX, ["/b/main"], True)], "an unmoved kit was gathered again, or a moved one served"
        assert again[BOX]["kits"]["/kit/main"] == first[BOX]["kits"]["/kit/main"] and again["mac-studio"] == first["mac-studio"]
        assert set(k.used) == {BOX, "mac-studio"} and set(k.used[BOX]) == {"/kit/main", "/b/main"}

    def test_a_board_survey_hands_each_kit_its_queue_as_the_watch_read_it_in_place_of_running_sluice(self, monkeypatch):
        """The crew-board spec, One watch for each kit: a refresh that gathers the kit takes its queue from the watch's line."""
        asked = []
        monkeypatch.setattr(plan, "gathered", lambda fleet, host, req: asked.append(req) or ({k["main"]: {"ok": True} for k in req["kits"]}, None))
        k = plan.Kept()
        k.queued = {(BOX, "/kit/main"): [[{"id": 41, "branch": "bolt/te"}], None]}
        monkeypatch.setattr(plan.READ, "follower", k)
        plan.survey(FLEET, [("swb-1", "te")], board=True)
        assert [x.get("queued") for x in asked[0]["kits"]] == [[[{"id": 41, "branch": "bolt/te"}], None]]
        assert "queued" not in k.used[BOX]["/kit/main"][0], "the kit was kept by a request that names its queue"

    def test_a_host_that_does_not_answer_is_kept_with_no_answer_so_its_kits_read_as_moved(self, monkeypatch):
        monkeypatch.setattr(plan, "gathered", lambda fleet, host, req: (None, "ssh: connect timed out") if host == BOX else
                            ({k["main"]: {"ok": True, "stamp": "s"} for k in req["kits"]}, None))
        k = plan.Kept()
        monkeypatch.setattr(plan.READ, "follower", k)
        sv = plan.survey(FLEET, [(t, None) for t in FLEET["partitions"]["wldn"]["teams"]], board=True)
        assert sv[BOX] == {"ok": False, "error": "ssh: connect timed out"}
        assert {m: a for m, (_, a) in k.used[BOX].items()} == {"/kit/main": None, "/b/main": None}

    def test_a_survey_of_any_other_command_is_served_nothing_the_follower_kept(self, monkeypatch):
        asked = []
        monkeypatch.setattr(plan, "gathered", lambda fleet, host, req: asked.append(host) or ({k["main"]: {"ok": True} for k in req["kits"]}, None))
        plan.survey(FLEET, [("swb-1", None)], board=True)
        assert asked == [BOX] and plan.READ.follower is None

    def test_a_state_file_at_a_tip_already_listed_is_its_kept_blob_and_starts_no_git(self, monkeypatch):
        calls = []
        tip = "f" * 40
        monkeypatch.setattr(plan, "git", lambda repo, *args, **kw: calls.append(args[0]) or f"100644 blob {'1' * 40}\tplan.rec\n100644 blob {'2' * 40}\tsignals/c/01-x.md")
        monkeypatch.setattr(plan, "cat_file", lambda repo, names: calls.append("cat-file") or [f"text of {n}" for n in names])
        k = plan.Kept()
        monkeypatch.setattr(plan.READ, "follower", k)
        assert plan.show("o/state", tip, "plan.rec") == f"text of {'1' * 40}" and plan.show("o/state", tip, "moves.rec") is None
        assert plan.paths_at("o/state", tip, "signals/") == ["signals/c/01-x.md"]
        assert board.texts("o/state", tip, ["signals/c/01-x.md", "signals/c/capture.md"]) == {"signals/c/01-x.md": f"text of {'2' * 40}"}
        assert calls == ["ls-tree", "cat-file"], "a kept tip was listed again or a held blob read again"
        k.settle()
        assert plan.show("o/state", tip, "plan.rec") == f"text of {'1' * 40}" and calls == ["ls-tree", "cat-file"]
        k.settle()
        k.settle()
        assert k.listings == {} and k.blobs == {}, "a tip no refresh read kept its blobs"


class TestRailFrame:
    """The rail tab draws the rail frame the host's follower writes (the crew-board spec, The rail and the board come
    from one read)."""

    RAIL = {"read_at": board.iso(NOW), "from": "mac-studio", "text": "What waits on you (wldn), as of 10:00:00\n\nproposals\n  none", "updated": None}

    def test_a_fresh_frame_is_the_rail_as_its_round_printed_it(self):
        assert board.rail_frame_text("wldn", self.RAIL, NOW) == self.RAIL["text"]

    def test_what_handing_out_the_restarts_said_follows_the_rail(self):
        said = board.rail_frame_text("wldn", dict(self.RAIL, updated="wldn-planner is due a restart: crew _renew restarts it once idle"), NOW)
        assert said == self.RAIL["text"] + "\n\nwldn-planner is due a restart: crew _renew restarts it once idle"

    def test_a_frame_read_five_minutes_ago_is_headed_with_its_age(self):
        said = board.rail_frame_text("wldn", dict(self.RAIL, read_at=board.iso(NOW - datetime.timedelta(minutes=5))), NOW).splitlines()
        assert said[0].startswith("wldn's rail as read at ")
        assert said[0].endswith(", 5m ago: the host's follower on mac-studio has not refreshed it since")
        assert said[1:] == ["", *self.RAIL["text"].splitlines()]
        assert board.rail_frame_text("wldn", dict(self.RAIL, read_at=board.iso(NOW - datetime.timedelta(seconds=board.STALE - 5))), NOW) == self.RAIL["text"]

    def test_with_no_frame_the_rail_tab_says_the_hosts_follower_writes_it(self):
        assert board.rail_frame_text("wldn", None, NOW) == (
            "No rail for wldn yet: the host's follower writes it each time it refreshes, swancloud's job or the console's rail tab, "
            "which crew console up wldn opens while no job runs.")

    def test_the_rail_tab_draws_the_frame_once_and_follows_nothing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        board.write_frame("wldn", self.RAIL, board.rail_path("wldn"))
        board.rail_follow("wldn", once=True)
        assert capsys.readouterr().out == self.RAIL["text"] + "\n" and board.follower_here() == "none"

    def test_the_rail_tab_draws_the_jobs_frames_and_follows_itself_once_the_job_ends(self, tmp_path, monkeypatch, capsys):
        """The host's job holds the lock: the tab draws and waits; once the job lets go, the tab takes the lock as a tab
        and makes the rounds itself."""
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        board.write_frame("wldn", self.RAIL, board.rail_path("wldn"))
        job, slept, stepped = board.lock_follower("job", wait=False), [], []

        class Done(Exception):
            pass

        class Stepping:
            def __init__(self, lock):
                self.lock = lock

            def step(self, most):
                stepped.append((board.lock_path().read_text().split()[:2], most))
                raise Done

            def close(self):
                self.lock.close()

        def sleep(s):
            slept.append(s)
            job.close()
        monkeypatch.setattr(board, "Follower", Stepping)
        monkeypatch.setattr(board.time, "sleep", sleep)
        with pytest.raises(Done):
            board.rail_follow("wldn")
        assert slept == [1] and stepped == [(["tab", "wldn"], 1)] and board.follower_here() == "none"
        assert capsys.readouterr().out == self.RAIL["text"] + "\n"

    def test_half_a_rail_frame_or_one_with_no_text_reads_as_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        assert board.read_rail("wldn") is None
        (tmp_path / "wldn.rail.json").write_text('{"read_at": ')
        assert board.read_rail("wldn") is None
        (tmp_path / "wldn.rail.json").write_text(json.dumps(dict(self.RAIL, text=None)))
        assert board.read_rail("wldn") is None
        board.write_frame("wldn", self.RAIL, board.rail_path("wldn"))
        assert board.read_rail("wldn") == self.RAIL and board.read_frame("wldn") is None
        assert sorted(p.name for p in tmp_path.iterdir()) == ["wldn.rail.json"]


class TestMore:
    def test_a_proposal_adding_to_a_held_bolt_belongs_to_the_team_holding_it(self):
        props = [{"label": "wldn", "proposal": 2, "by": "chuck@mac-studio", "opened": "2026-10-12", "case": "Tenants get d.", "waiting": [],
                  "changes": [{"do": 'unit add d "Unit d." --bolt tenant-environments', "bolts": ["tenant-environments"]}]}]
        assert data(props=props)["partitions"][0]["bolt_plan"]["proposals"][0]["teams"] == ["swb-1"]

    def test_a_captures_age_is_said_from_its_time_and_a_date_as_it_is(self):
        sigs = [dict(SIGS[0], captured_by="otter", at=ago(5 * 60)), dict(SIGS[1], captured_by="otter", at=ago(3 * 60))]
        line = next(l for l in lane(board.board_text(data(signals=sigs)), "Inception") if "signals captured by otter" in l)
        assert "2 not moved, the oldest captured 5h" in line and line.endswith(" ago")

    def test_the_board_answers_nothing_it_offers_no_approving_or_telling_command(self):
        props = [{"label": "wldn", "proposal": 1, "by": "chuck@mac-studio", "opened": "2026-10-12", "case": "The console.", "waiting": [],
                  "changes": [{"do": 'bolt new console-two "x" --repo switchboard-kit', "bolts": ["console-two"]}]}]
        out = board.board_text(data(props=props, signals=SIGS))
        for no in ("crew plan approve", "crew unit approve", "crew tell"):
            assert no not in out

    def test_the_json_holds_each_lanes_objects_and_the_ledgers_units_and_fixes(self):
        d = data(signals=SIGS)
        p = d["partitions"][0]
        assert sorted(d) == ["from", "partitions", "read_at", "unread"]
        assert sorted(p) == ["asking", "attention", "bolt_plan", "cards", "construction", "environments", "fixing", "hosts", "inception", "label",
                             "operation", "plan", "records", "teams"]
        assert sorted(p["teams"][0]) == ["host", "kit", "kits", "stream", "team"]
        te = next(b for b in p["construction"] if b["bolt"] == "tenant-environments")
        assert sorted(te) == ["bolt", "fixes", "given", "goal", "host", "landing", "markers", "record", "repo", "state", "stream", "submissions_error",
                              "team", "teams", "time", "units", "url"]
        assert sorted(te["units"][0]) == ["flume", "kind", "slot", "stage", "submission", "tasks", "unit", "url", "worktree"]
        assert sorted(te["fixes"][0]) == ["fix", "flume", "merged", "slot", "submission", "url", "worktree"]

    def test_half_a_frame_or_one_with_no_time_reads_as_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        assert board.read_frame("wldn") is None
        (tmp_path / "wldn.json").write_text('{"read_at": ')
        assert board.read_frame("wldn") is None
        (tmp_path / "wldn.json").write_text('{"partitions": []}')
        assert board.read_frame("wldn") is None
        board.write_frame("wldn", dict(data(), read_at=board.iso(NOW)))
        assert board.read_frame("wldn")["partitions"][0]["label"] == "wldn" and sorted(p.name for p in tmp_path.iterdir()) == ["wldn.json"]


def view(name, **kw):
    """An agent's view of the fixture's board, a line to a string as its mod draws it, styles left out."""
    return ["".join(s for s, _ in line) for line in board.agent_views(data(**kw))["views"][name]]


WAITS = [{"label": "wldn", "proposal": 2, "by": "wldn-planner", "opened": "2026-10-12", "case": "Tenants get d.", "waiting": ["swb-1"],
          "changes": [{"do": 'unit add d "Unit d." --bolt tenant-environments', "bolts": ["tenant-environments"]}]}]


class TestViews:
    def test_a_conductor_reads_its_bolt_as_a_ledger_a_pip_to_each_unit_then_what_comes_next(self):
        assert view("swb-1-conductor") == [f"  switchboard-kit  ◑◔  tenant-environments  0 of 2 merged  {TE_TIME}", "    ◑  a  code 1/2  unit-1", "    ◔  b  planned",
                                           "    fix/tenant-environments/edge  fix  unit-4", "  switchboard-kit  next  apex-zones", "  queued  1 in switchboard-kit"]

    def test_a_team_holding_a_bolt_that_waits_to_land_and_one_it_builds_draws_both(self, monkeypatch):
        """A team builds one bolt and may hold one more, proven, that waits to land (teams.16): its conductor's band and
        the Construction lane draw both, the proven one saying it waits to land."""
        two = plan.Plan(plan_text(bolts=[("doctor-rows", "switchboard-kit", "swb-2"), ("ssh-fix", "switchboard-kit", "swb-2")],
                                  units=[("rows-one", "switchboard-kit", "doctor-rows", []), ("ssh-one", "switchboard-kit", "ssh-fix", [])]))
        monkeypatch.setitem(globals(), "the_plan", lambda: two)
        sv = kits()
        swb = sv[BOX]["kits"]["/kit/main"]
        swb["bolts"].update({"doctor-rows": {"head": "f" * 40, "head_at": ago(30), "changes": ["rows-one"], "archived": ["rows-one"],
                                             "verdict": "passed (2 run)"},
                             "ssh-fix": {"head": "c" * 40, "head_at": ago(20), "changes": []}})
        swb["places"]["ssh-one"] = dict(swb["places"]["a"], path="/kit/places/ssh-one", bolt="ssh-fix")
        swb["slots"]["swb-2"] = [{"slot": "unit-1", "kind": "unit", "name": "ssh-one"}]
        mine = view("swb-2-conductor", sv=sv)
        assert mine[:4] == [f"✓ switchboard-kit  ●  doctor-rows  waits to land  1 of 1 merged  {NO_GIVE}  no card open", "    ●  rows-one  merged",
                            f"  switchboard-kit  ◑  ssh-fix  0 of 1 merged  {NO_GIVE}", "    ◑  ssh-one  code 1/2  unit-1"]
        assert lane(board.board_text(data(sv=sv)), "Construction") == [
            f"✓ switchboard-kit doctor-rows  swb-2 on chuck-herdr-alpha  waits to land  {NO_GIVE}  no card open", "    rows-one  merged",
            f"  switchboard-kit ssh-fix  swb-2 on chuck-herdr-alpha  {NO_GIVE}", "    ssh-one  code 1/2  unit-1"]

    def test_each_bolt_is_marked_from_its_kits_landing_row_and_ops_band_draws_the_row_with_its_card(self, monkeypatch):
        """Two proven bolts of one kit are one landing row, land/<kit> (crew-rail "Two bolts of one kit"): each bolt's
        marker is that row's, its card main-level ops's, which ops's band draws, the row naming both, and the card above
        ops's prompt; the operator counts the row once (code.8)."""
        two = plan.Plan(plan_text(bolts=[("doctor-rows", "switchboard-kit", "swb-1"), ("ssh-fix", "switchboard-kit", "swb-2")],
                                  units=[("rows-one", "switchboard-kit", "doctor-rows", []), ("ssh-one", "switchboard-kit", "ssh-fix", [])]))
        monkeypatch.setitem(globals(), "the_plan", lambda: two)
        sv = kits()
        sv[BOX]["kits"]["/kit/main"]["bolts"].update({
            "doctor-rows": {"head": "f" * 40, "head_at": ago(30), "changes": ["rows-one"], "archived": ["rows-one"], "verdict": "passed (2 run)"},
            "ssh-fix": {"head": "c" * 40, "head_at": ago(20), "changes": ["ssh-one"], "archived": ["ssh-one"], "verdict": "passed (1 run)"}})
        card = dict(label="wldn", card="req_k1", key="land/switchboard-kit", by="wldn-ops", host="mac-studio", at=NOW)
        d = data(sv=sv, cards=[card])
        ledgers = {b["bolt"]: b["markers"] for b in d["partitions"][0]["construction"]}
        assert [m["key"] for m in ledgers["doctor-rows"]] == [m["key"] for m in ledgers["ssh-fix"]] == ["land/switchboard-kit"]
        assert ledgers["ssh-fix"][0]["card"]["by"] == "wldn-ops"
        assert "✓ land/switchboard-kit  doctor-rows, ssh-fix  wait to land  card open, asked by wldn-ops" in view("wldn-ops", sv=sv, cards=[card])
        v = board.agent_views(d)
        assert "".join(t for t, _ in v["cards"]["wldn-ops"][0]).startswith("  your card  land/switchboard-kit  req_k1")
        assert "✓ 1 to approve" in "\n".join(view("wldn-operator", sv=sv, cards=[card]))
        assert view("swb-1-conductor", sv=sv, cards=[card])[0].endswith(f"doctor-rows  waits to land  1 of 1 merged  {NO_GIVE}  card open, asked by wldn-ops")

    def test_a_unit_waits_on_no_answer_so_it_has_no_marker_even_with_an_old_verify_card_open(self):
        card = dict(label="wldn", card="req_2", key="verify/a/20261012-1200", by="swb-1-conductor", host="mac-studio", at=NOW)
        assert view("swb-1-conductor", cards=[card])[1] == "    ◑  a  code 1/2  unit-1"

    def test_a_team_holding_no_bolt_says_so_and_what_is_planned_for_its_kit(self):
        assert view("swb-2-conductor") == ["  swb-2 holds no bolt", "  switchboard-kit  next  apex-zones", "  queued  1 in switchboard-kit"]
        assert view("atl-1-conductor") == ["  atl-1 holds no bolt"]

    def test_a_proposal_waiting_on_a_conductors_agreement_is_in_its_view_alone(self):
        assert "✓ proposal 2 by wldn-planner  Tenants get d.  waits on your agreement  no card open" in view("swb-1-conductor", props=WAITS)
        assert not [l for l in view("brd-1-conductor", props=WAITS) if "proposal" in l]

    def test_a_conductor_whose_host_does_not_answer_is_told_and_its_units_are_unknown(self):
        mine = view("swb-1-conductor", sv=kits(ok=False))
        assert mine[0] == ("  switchboard-kit  ??  tenant-environments  unknown  0 of 2 merged  3h 20m; who held its time can't be told: its "
                           "submissions can't be read: its kit was not read") and mine[1] == "    ?  a  unknown"
        assert f"! {BOX} did not answer (its kits: ssh: timed out)" in mine
        assert not [l for l in view("atl-1-conductor", sv=kits(ok=False)) if "did not answer" in l]

    def test_a_bolt_landed_and_still_in_the_plan_is_named_for_attention_to_its_conductor(self):
        assert view("brd-1-conductor") == [f"! breadboard-kit  ●  board-done  landed  1 of 1 merged  {DONE_TIME}", "    ●  done-one  landed",
                                           "! bolt board-done: every unit has landed on main, and the bolt is still in the plan"]

    QUEUED = [dict(entry("bolt.submit", 30, Outcome="queued", Submission="412", Head=S1), On=["bolt/tenant-environments", "team/swb-1"])]
    READY = "chore tidy-a has not landed on main: it is ready"
    UNCLOSED = [dict(entry("bolt.submit", 30, Outcome="landed", Submission="412", Head=S1), On=["bolt/tenant-environments"]),
                entry("bolt.land", 29, bolt="tenant-environments", Refused=READY, By="wldn-ops")]

    def test_a_landing_queued_is_said_on_its_bolts_head_line_with_sluices_number(self):
        """crew-board "A landing queued": on the lane and in its conductor's band."""
        assert view("swb-1-conductor", logs=self.QUEUED)[0] == f"  switchboard-kit  ◑◔  tenant-environments  landing queued as #412  0 of 2 merged  {TE_TIME}"
        assert f"  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  landing queued as #412  {TE_TIME}" in lane(
            board.board_text(data(logs=self.QUEUED)), "Construction")

    def test_a_close_refused_is_said_on_its_head_line_in_the_attention_gutter_to_its_conductor_and_main_level_ops(self):
        """crew-board "A close refused": on the lane, in its conductor's band and in main-level ops's band, in the
        words of its last refused close, which its conductor's attention names too."""
        said = f"landed on main, not closed: {self.READY}"
        mine = view("swb-1-conductor", logs=self.UNCLOSED)
        assert mine[0] == f"! switchboard-kit  ◑◔  tenant-environments  {said}  0 of 2 merged  {TE_TIME}"
        assert f"! bolt tenant-environments: it landed on main and was not closed: {self.READY}" in mine
        assert f"! switchboard-kit  swb-1  ◑◔  tenant-environments  {said}  0 of 2 merged  {TE_TIME}" in view("wldn-ops", logs=self.UNCLOSED)
        assert f"! switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  {said}  {TE_TIME}" in lane(board.board_text(data(logs=self.UNCLOSED)),
                                                                                                             "Construction")
        assert not [l for l in view("wldn-ops") if "not closed" in l]

    def test_a_landing_queued_that_sluices_queue_shows_standing_is_said_once_by_sluices_state(self):
        """The run record has it queued as #355 and sluice's queue has #355 standing: its head line says it once, in
        sluice's state, and says the record's queued again only once sluice's queue no longer shows it."""
        logs = [dict(self.QUEUED[0], Submission="355")]
        sv = queued(STANDING_SUBS)
        assert view("swb-1-conductor", sv=sv, logs=logs)[0] == f"  switchboard-kit  ◑◔  tenant-environments  landing #355 queued  0 of 2 merged  {QUEUED_TIME}"
        assert view("swb-1-conductor", logs=logs)[0] == f"  switchboard-kit  ◑◔  tenant-environments  landing queued as #355  0 of 2 merged  {TE_TIME}"

    def test_what_a_held_bolts_landing_is_read_from_the_run_record(self):
        """Decision 5 (board.landing_of): queued while its last bolt.submit is, unclosed while its last bolt.land since
        its landing is refused, and nothing once a close went through or before any landing."""
        b = "tenant-environments"
        assert board.landing_of(self.QUEUED, b) == {"queued": "412"}
        assert board.landing_of(self.UNCLOSED, b) == {"unclosed": self.READY}
        assert board.landing_of(self.UNCLOSED + [entry("bolt.land", 20, bolt=b, Repo="switchboard-kit", Head=S2)], b) is None
        assert board.landing_of(self.UNCLOSED[:1], b) is None and board.landing_of([], b) is None
        refused_before = [entry("bolt.land", 40, bolt=b, Refused=self.READY)] + self.UNCLOSED[:1]
        assert board.landing_of(refused_before, b) is None
        assert board.landing_of(self.UNCLOSED, "ssh-fix") is None

    def test_the_planner_reads_the_plan_in_brief_each_teams_bolt_and_the_proposals_with_whom_they_wait_on(self):
        assert view("wldn-planner", props=WAITS) == [
            "wldn plan  2 held  1 planned  1 queued  1 proposal open", "  atlas-kit  atl-1  holds no bolt",
            f"! breadboard-kit  brd-1  ●  board-done  landed  1 of 1 merged  {DONE_TIME}",
            f"  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged  {TE_TIME}",
            "  switchboard-kit  swb-2  holds no bolt", "✓ proposal 2 by wldn-planner  Tenants get d.  waiting on swb-1-conductor  no card open",
            "  switchboard-kit  next  apex-zones", "  queued  1 in switchboard-kit",
            "! bolt board-done: every unit has landed on main, and the bolt is still in the plan"]

    def test_each_bolt_held_or_planned_is_led_by_its_product_and_a_held_ones_team_is_dim_after_it(self):
        lines = board.agent_views(data())["views"]["wldn-planner"]
        held = next(l for l in lines if "tenant-environments" in "".join(s for s, _ in l))
        assert held[:4] == [("  ", None), ("switchboard-kit", None), ("  ", None), ("swb-1", "dim")]
        idle = next(l for l in lines if "swb-2" in "".join(s for s, _ in l))
        assert idle[:4] == [("  ", None), ("switchboard-kit", None), ("  ", None), ("swb-2", "dim")]
        planned = next(l for l in lines if "apex-zones" in "".join(s for s, _ in l))
        assert planned[:4] == [("  ", None), ("switchboard-kit", None), ("  ", None), ("next", "dim")]

    def test_the_design_agent_reads_the_signals_by_who_captured_them_and_the_first_explorations(self, monkeypatch):
        monkeypatch.setattr(board, "SHOWN", 0)
        assert view("wldn-design", signals=SIGS) == ["wldn inception  3 signals not moved  1 exploration", "  signals captured by wldn-planner  2 not moved",
                                                     "  signals captured by chuck@mac-studio  1 not moved", "  and 1 more exploration"]
        monkeypatch.setattr(board, "SHOWN", 6)
        assert view("wldn-design")[1:] == ["  switchboard-kit command-cost  Reading: what each crew command costs."]

    def test_an_operator_reads_the_partitions_board_in_brief_and_what_waits_on_the_user(self):
        mine = view("wldn-operator", props=WAITS, signals=SIGS)
        assert mine[:4] == [f"wldn board  read from {BOX}, mac-studio", "Inception  3 signals not moved  1 exploration",
                            "Bolt plan  1 proposal open  1 planned  1 queued", "Construction"]
        assert mine[4:8] == ["  atlas-kit  atl-1  holds no bolt", f"! breadboard-kit  brd-1  ●  board-done  landed  1 of 1 merged  {DONE_TIME}",
                             f"  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged  {TE_TIME}", "  switchboard-kit  swb-2  holds no bolt"]
        assert "Operation  0 landed in seven days" in mine and "waits on the user  ✓ 1 to approve" in mine

    def test_an_operator_reads_each_environment_with_a_deploy_or_an_operation_waiting_and_counts_their_cards(self):
        mine = view("wldn-operator", entries=OPS)
        at = mine.index("Operation  0 landed in seven days")
        assert mine[at + 1] == f"✓ mac-studio  deploy {S2[:7]}  waits on the user's word  2 operations waiting"
        assert "waits on the user  ✓ 2 to approve" in mine

    def test_main_level_ops_reads_each_deploy_waiting_on_the_word_or_running_and_each_operation_step_with_its_doer(self):
        running = entry("ops.deploy", 10, env="swancloud-srv", Head=S1, Base="none", Phase="start")
        assert view("wldn-ops", entries=OPS + [running], cards=[DEPLOY_CARD]) == [
            "wldn operations  1 deploy waits on the user's word  1 deploy running  2 operations waiting",
            f"✓ mac-studio  deploy {S2[:7]}  waits on the user's word  card open, asked by wldn-ops",
            f"  mac-studio  restart-teams/1  after {S1[:7]}  handed  doer dispatcher, wldn-dispatch-mac-studio",
            "✓ mac-studio  rotate-key  waiting  doer user  no card open",
            f"  swancloud-srv  deploy {S1[:7]}  deploying since {board.local(ago(10))}"]

    def test_main_level_ops_reads_a_deploy_whose_card_post_was_refused_as_owing_its_card(self):
        """crew-board "A deploy whose card was refused", in main-level ops's view."""
        assert view("wldn-ops", entries=OPS, logs=OPS + [REFUSED_POST])[1] == (
            f"✓ mac-studio  deploy {S2[:7]}  waits on the user's word  no card open, its post refused")

    def test_a_step_held_for_the_users_word_is_marked_held_and_waits_on_its_card(self):
        held = entry("ops.step", 10, Head=S1, Key="restart-herdr/1", State="waiting", Doer="main-ops", Agent="wldn-ops", When="quiet held")
        assert view("wldn-ops", entries=OPS + [held])[-1] == (
            f"✓ mac-studio  restart-herdr/1  after {S1[:7]}  waiting  doer main-ops, wldn-ops, held for the user's word  no card open")
        assert lane(board.board_text(data(entries=OPS + [held])), "Operation")[-1] == (
            "✓ mac-studio  restart-herdr/1  held for the user's word, for wldn-ops  no card open")

    def test_a_deploy_waiting_at_its_gate_is_said_to_wait_there_for_the_user_and_main_level_ops_names_it_the_gate_of_its_commit(self):
        run = "https://github.com/WilldanGroup/switchboard-kit/actions/runs/38612817613"
        gate = entry("ops.step", 10, Head=S1, Key="gate-38612817613", State="waiting", Doer="user", Text=run)
        assert view("wldn-ops", entries=OPS + [gate])[-1] == f"✓ mac-studio  gate-38612817613  gate of {S1[:7]}  waiting  doer user  no card open"
        assert lane(board.board_text(data(entries=OPS + [gate])), "Operation")[-1] == (
            f"✓ mac-studio  gate-38612817613  waits at its gate for the user  {run}  no card open")
        bare = dict(gate, Head=None)
        assert view("wldn-ops", entries=OPS + [bare])[-1] == "✓ mac-studio  gate-38612817613  gate  waiting  doer user  no card open"

    def test_main_level_ops_with_nothing_waiting_reads_its_head_and_no_deploy_done_or_replaced(self):
        done = [entry("ops.offer", 30, Head=S1, Base="none"), entry("ops.offer", 20, Head=S2, Base="none"), entry("ops.approve", 15, Head=S2),
                entry("ops.deploy", 12, Head=S2, Phase="start"), entry("ops.deploy", 10, Head=S2, Phase="end", Outcome="done")]
        assert view("wldn-ops", entries=done) == ["wldn operations  0 deploys wait on the user's word  0 deploys running  0 operations waiting"]

    def test_an_approved_deploy_whose_word_went_to_a_newer_offer_leaves_main_level_opss_view_and_the_board_says_so(self):
        """mac-studio, 2026-10-15 to 18: 45eecf3 approved and never deployed, its word gone to 291a4e6, deployed since,
        stood as approved, not yet deployed in swancloud-ops's band."""
        moved = [entry("ops.offer", 30, Head=S1, Base="none"), entry("ops.approve", 25, Head=S1), entry("ops.offer", 20, Head=S2, Base=S1),
                 entry("ops.approve", 15, Head=S2), entry("ops.deploy", 12, Head=S2, Base=S1, Phase="start"),
                 entry("ops.deploy", 10, Head=S2, Phase="end", Outcome="done")]
        assert view("wldn-ops", entries=moved) == ["wldn operations  0 deploys wait on the user's word  0 deploys running  0 operations waiting"]
        assert lane(board.board_text(data(entries=moved)), "Operation")[-1].startswith(
            f"  mac-studio  deploy {S1[:7]} from nothing deployed  approved, then the word went to a newer offer  carrying")

    def test_each_conductor_the_planner_the_design_agent_main_level_ops_and_the_operator_has_a_view_and_no_other_agent(self):
        v = board.agent_views(data())
        assert sorted(v["views"]) == sorted(["swb-1-conductor", "swb-2-conductor", "brd-1-conductor", "atl-1-conductor", "wldn-planner", "wldn-design",
                                             "wldn-ops", "wldn-operator"])
        assert v["read_at"] == data()["read_at"] and v["stale_after_ms"] == board.STALE * 1000
        assert v["stale"] == [(f"crew: the board was last read at {board.local(data()['read_at'])}, too long ago to show; crew's follower on mac-studio "
                               "has not refreshed it since", "dim")]
        # a day with it: a restart, or a follower that stopped, can leave it days old
        assert re.fullmatch(r"crew: the board was last read at [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}, .*", v["stale"][0][0])

    @pytest.mark.parametrize("stages, shown", [(["queued", "waiting", "ready"], "○○○"), (["amended", "construct", "planned"], "◔◔◔"),
                                               (["code", "verify"], "◑◕"), (["merged", "landed"], "●●"), (["unknown"], "?")])
    def test_a_units_pip_fills_as_its_stage_goes_and_one_crew_cannot_read_is_a_question(self, stages, shown):
        assert board.pips([{"stage": s} for s in stages]) == shown

    def test_the_rail_tabs_refresh_writes_the_views_whole_beside_the_frame(self, tmp_path, monkeypatch):
        monkeypatch.setattr(board, "FRAMES", tmp_path)
        board.write_frame("wldn", board.agent_views(data()), board.agents_path("wldn"))
        assert sorted(p.name for p in tmp_path.iterdir()) == ["wldn.agents.json"]
        assert board.read_frame("wldn") is None

    def test_the_views_file_holds_every_key_crews_mod_reads_in_the_form_it_draws(self):
        """code.8: plugin/hooks/status.js reads exactly these keys from the views file, finds its agent's view by name,
        and draws each line as (text, style) segments, bold, dim or plain; a change to the views' shape, or a key the
        mod reads that they lack, fails here."""
        mod = (pathlib.Path(board.__file__).resolve().parent.parent / "hooks/status.js").read_text()
        v = json.loads(json.dumps(board.agent_views(data(props=WAITS, signals=SIGS))))
        assert set(re.findall(r"live\.frame\.(\w+)", mod)) == set(v) == {"read_at", "stale_after_ms", "stale", "views", "cards"}
        assert "live.frame.views[live.agent]" in mod and "(live.frame.cards || {})[live.agent]" in mod and "Date.parse(live.frame.read_at)" in mod
        assert re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", v["read_at"]) and isinstance(v["stale_after_ms"], int)
        assert "home + '/.cache/crew/board/' + label + '.agents.json'" in mod and board.agents_path("wldn").parts[-4:] == (".cache", "crew", "board", "wldn.agents.json")
        assert re.findall(r"style === '(\w+)'", mod) == ["bold"] and "dimColor: true" in mod
        assert v["cards"] == {} and json.loads(json.dumps(board.agent_views(data(cards=[QUESTION]))))["cards"]["swb-1-conductor"]
        standing = board.agent_views(data(sv=queued(STANDING_SUBS)))["views"]  # a merge and a landing standing in sluice, drawn as plain segments
        lines = [v["stale"]] + [l for lines in v["views"].values() for l in lines] + [l for lines in board.agent_views(data(cards=[QUESTION]))["cards"].values() for l in lines]
        lines += [l for lines in standing.values() for l in lines]
        assert any("#41 under test" in t for l in standing["swb-1-conductor"] for t, _ in l)
        assert all(isinstance(l, list) and all(isinstance(t, str) and len(seg) == 2 and style in (None, "bold", "dim") for seg in l for t, style in [seg])
                   for l in lines)


QUESTION = dict(label="wldn", card="req_q1", key=None, on="agent/swb-1-conductor", by="swb-1-conductor", host=BOX,
                at=NOW - datetime.timedelta(minutes=14))


# Merges and a landing standing in sluice's queue, as the gather reads them on swb-1's host (gather.submissions_of).
STANDING_SUBS = [{"id": 41, "branch": "bolt/tenant-environments", "head": "a" * 40, "state": "testing", "worktree": "unit/a", "pull_head": None,
                  "submitted": ago(30), "started": ago(20)},
                 {"id": 43, "branch": "bolt/tenant-environments", "head": "c" * 40, "state": "queued", "worktree": "fix/tenant-environments/edge",
                  "pull_head": None, "submitted": ago(25), "started": None},
                 {"id": 355, "branch": "main", "head": "d" * 40, "state": "queued", "worktree": "pull/198", "pull_head": "bolt/tenant-environments",
                  "submitted": ago(10), "started": None}]
# tenant-environments' time with those standing: #41 queued ten minutes, the team's, then under test twenty, the kit's.
QUEUED_TIME = f"3h 20m: team 10m, kit 20m, nobody 2h 50m; kit since {hm(20)}, #41"


def queued(subs=(), error=None):
    sv = kits()
    sv[BOX]["kits"]["/kit/main"].update({"submissions": list(subs)} if error is None else {"submissions": None, "submissions_error": error})
    return sv


class TestSubmissions:
    """crew-board "Construction shows each bolt in flight as a ledger, with no server for a started bolt's work": each standing merge's number and state on its line,
    the landing's on the bolt's head line, in the lane and in the bands (teams.22, code.8)."""

    def test_a_merge_standing_in_sluice_is_on_its_line_in_the_lane_and_the_conductors_band(self):
        """crew-board "A merge standing in sluice"."""
        sv = queued(STANDING_SUBS)
        assert lane(board.board_text(data(sv=sv)), "Construction")[1:4] == [
            "    a  code 1/2  #41 under test  unit-1  https://unit-a--switchboard-kit--box.dev", "    b  planned",
            "    fix/tenant-environments/edge  fix  #43 queued  unit-4"]
        assert view("swb-1-conductor", sv=sv)[1:4] == ["    ◑  a  code 1/2  #41 under test  unit-1", "    ◔  b  planned",
                                                       "    fix/tenant-environments/edge  fix  #43 queued  unit-4"]

    def test_a_landing_standing_in_sluice_is_on_the_bolts_head_line_in_the_lane_and_the_bands(self):
        """crew-board "A landing standing in sluice": the lane, its conductor's band and main-level ops's."""
        sv = queued(STANDING_SUBS)
        assert lane(board.board_text(data(sv=sv)), "Construction")[0] == (
            f"  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  landing #355 queued  {QUEUED_TIME}")
        assert view("swb-1-conductor", sv=sv)[0] == f"  switchboard-kit  ◑◔  tenant-environments  landing #355 queued  0 of 2 merged  {QUEUED_TIME}"
        assert "  switchboard-kit  tenant-environments  landing #355 queued" in view("wldn-ops", sv=sv)

    def test_a_landing_on_ops_landing_row_is_named_with_its_bolt(self, monkeypatch):
        two = plan.Plan(plan_text(bolts=[("doctor-rows", "switchboard-kit", "swb-1")], units=[("rows-one", "switchboard-kit", "doctor-rows", [])]))
        monkeypatch.setitem(globals(), "the_plan", lambda: two)
        sv = queued([dict(STANDING_SUBS[2], pull_head="bolt/doctor-rows")])
        sv[BOX]["kits"]["/kit/main"]["bolts"]["doctor-rows"] = {"head": "f" * 40, "head_at": ago(30), "changes": ["rows-one"],
                                                                "archived": ["rows-one"], "verdict": "passed (2 run)"}
        card = dict(label="wldn", card="req_k1", key="land/switchboard-kit", by="wldn-ops", host="mac-studio", at=NOW)
        assert ("✓ land/switchboard-kit  doctor-rows landing #355 queued  waits to land  card open, asked by wldn-ops"
                in view("wldn-ops", sv=sv, cards=[card]))
        assert not [l for l in view("wldn-ops", sv=sv, cards=[card]) if l.startswith("  switchboard-kit  doctor-rows")]

    def test_a_queue_that_cant_be_read_is_said_on_the_head_line_and_no_line_shows_a_number(self):
        """crew-board "A queue that can't be read"."""
        sv = queued(error="sluice overview exited 2: not a repository sluice serves")
        out = lane(board.board_text(data(sv=sv)), "Construction")
        assert out[0] == ("  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  submissions can't be read: sluice overview "
                          "exited 2: not a repository sluice serves  3h 20m; who held its time can't be told: its submissions can't be read: "
                          "sluice overview exited 2: not a repository sluice serves")
        assert not [l for l in out if "#" in l]
        mine = view("swb-1-conductor", sv=sv)
        assert mine[0] == ("  switchboard-kit  ◑◔  tenant-environments  submissions can't be read  0 of 2 merged  3h 20m; who held its time "
                           "can't be told: its submissions can't be read: sluice overview exited 2: not a repository sluice serves")
        assert not [l for l in mine if "#" in l]

    def test_a_landing_queued_whose_queue_cant_be_read_shows_no_number(self):
        """crew-board "A queue that can't be read": the run record has its landing queued as #412, and sluice's queue
        could not be read on the team's host, so its head line says its submissions can't be read and no line shows
        the record's number (read.1)."""
        sv = queued(error="sluice overview exited 2: not a repository sluice serves")
        out = lane(board.board_text(data(sv=sv, logs=TestViews.QUEUED)), "Construction")
        assert out[0] == ("  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha  submissions can't be read: sluice overview "
                          "exited 2: not a repository sluice serves  3h 20m; who held its time can't be told: its submissions can't be "
                          "read: sluice overview exited 2: not a repository sluice serves")
        assert not [l for l in out if "#" in l]
        mine = view("swb-1-conductor", sv=sv, logs=TestViews.QUEUED)
        assert mine[0] == ("  switchboard-kit  ◑◔  tenant-environments  submissions can't be read  0 of 2 merged  3h 20m; who held its time "
                           "can't be told: its submissions can't be read: sluice overview exited 2: not a repository sluice serves")
        assert not [l for l in mine if "#" in l]

    def test_nothing_standing_draws_nothing_new(self):
        assert view("swb-1-conductor", sv=queued([])) == view("swb-1-conductor")


class TestTime:
    """crew-board "A held bolt's head line shows its age and who held its time" (plan.20): each holder now as the lane,
    the JSON and the bands draw tenant-environments' head line, given 200 minutes before the board was read."""

    @staticmethod
    def head(**kw):
        return lane(board.board_text(data(**kw)), "Construction")[0]

    def test_the_team_while_a_stage_runs(self):
        logs = [dict(Act="stage.start", On=["stage/a/code", "unit/a", "agent/swb-1-unit-1"], At=ago(50))]
        said = f"3h 20m: team 50m, nobody 2h 30m; team since {hm(50)}, code on a"
        assert self.head(logs=logs).endswith(f"swb-1 on {BOX}  {said}")
        assert view("swb-1-conductor", logs=logs)[0] == f"  switchboard-kit  ◑◔  tenant-environments  0 of 2 merged  {said}"
        assert f"  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged  {said}" in view("wldn-planner", logs=logs)

    def test_the_kit_while_a_merge_is_under_test(self):
        assert self.head(sv=queued(STANDING_SUBS)).endswith(QUEUED_TIME)

    def test_the_user_while_a_card_of_the_bolts_is_open(self):
        logs = [dict(Act="card.post", On=["bolt/tenant-environments"], Card="req_l", Key="land/tenant-environments", By="swb-1-conductor", At=ago(40))]
        assert self.head(logs=logs).endswith(f"3h 20m: user 40m, nobody 2h 40m; user since {hm(40)}, land/tenant-environments")

    def test_a_hold_while_its_teams_host_is_held(self):
        logs = [dict(Act="host.hold", On=[f"host/{BOX}"], By="chuck", At=ago(15))]
        assert self.head(logs=logs).endswith(f"3h 20m: hold 15m, nobody 3h 05m; held since {hm(15)}: its host {BOX} is held by chuck")

    def test_stalled_once_nobody_has_held_it_five_minutes_and_not_before(self):
        assert self.head().endswith(TE_TIME)
        logs = [dict(Act="stage.start", On=["stage/a/code", "unit/a", "agent/swb-1-unit-1"], At=ago(50)),
                dict(Act="stage.end", On=["stage/a/code", "unit/a", "agent/swb-1-unit-1"], At=ago(2))]
        assert self.head(logs=logs).endswith(f"3h 20m: team 48m, nobody 2h 32m; nobody since {hm(2)}")

    def test_minutes_that_cant_be_split_show_as_team_or_kit_with_why_in_the_lane_the_json_and_the_bands(self):
        """crew-board "Minutes that can't be split": twelve minutes of the bolt's age were a decided merge's stay in sluice,
        kept by the follower with no start of its checks."""
        sv = kits()
        sv[BOX]["kits"]["/kit/main"]["decided"] = [{"id": 41, "bolt": "tenant-environments", "branch": "bolt/tenant-environments", "worktree": "unit/a",
                                                    "pull_head": None, "submitted": ago(30), "started": None, "decided": ago(18), "event": "landed"}]
        said = f"3h 20m: team or kit 12m, nobody 3h 08m; stalled since {hm(18)}; team or kit: sluice keeps no start of its checks"
        assert self.head(sv=sv).endswith(f"swb-1 on {BOX}  {said}")
        assert data(sv=sv)["partitions"][0]["construction"][0]["time"]["shares"]["team_or_kit"] == 12
        assert view("swb-1-conductor", sv=sv)[0] == f"  switchboard-kit  ◑◔  tenant-environments  0 of 2 merged  {said}"
        assert f"  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged  {said}" in view("wldn-planner", sv=sv)

    def test_an_age_that_cant_be_told_says_why_and_shows_no_share(self):
        unread = {"wldn": {"wldn/main of WilldanGroup/crew-state": "fetch failed"}}
        said = "its age can't be told: wldn/main of WilldanGroup/crew-state could not be read (fetch failed)"
        assert self.head(unread=unread).endswith(said)
        assert view("swb-1-conductor", unread=unread)[0].endswith(f"0 of 2 merged  {said}")

    def test_the_json_carries_the_age_the_shares_and_the_holder_now(self):
        logs = [dict(Act="stage.start", On=["stage/a/code", "unit/a", "agent/swb-1-unit-1"], At=ago(50))]
        te = data(logs=logs)["partitions"][0]["construction"][0]
        assert te["time"] == {"age": 200, "shares": {"team": 50, "kit": 0, "team_or_kit": 0, "user": 0, "hold": 0, "nobody": 150},
                              "now": {"holder": "team", "what": "code on a", "since": ago(50)}, "stalled": False,
                              "said": f"3h 20m: team 50m, nobody 2h 30m; team since {hm(50)}, code on a"}
        assert json.loads(json.dumps(te))["time"] == te["time"]


class TestCards:
    def test_each_agent_sees_its_open_cards_its_questions_among_them_above_its_view(self):
        """code.8: the band crew's mod draws above an agent's prompt opens with the agent's open cards, oldest first."""
        p2 = dict(label="wldn", card="req_p2", key="proposal/2", by="wldn-planner", host="mac-studio", at=NOW - datetime.timedelta(hours=2, minutes=5))
        stray = dict(QUESTION, card="req_x", key="ask/wldn-reviewer/x", by="wldn-reviewer")
        v = board.agent_views(data(props=WAITS, cards=[p2, QUESTION, stray]))
        drawn = {a: ["".join(t for t, _ in l) for l in lines] for a, lines in v["cards"].items()}
        assert drawn == {"wldn-planner": ["  your card  proposal/2  req_p2  open 2h 05m"], "swb-1-conductor": ["  your question  req_q1  open 14m"]}
        assert ("req_q1", "dim") in v["cards"]["swb-1-conductor"][0]

    def test_the_board_lists_each_open_card_with_what_it_is(self):
        rec = dict(QUESTION, card="req_r1", key="record/atlas-kit/0021", by="wldn-design")
        assert [(c["card"], c["kind"], c["by"]) for c in data(cards=[rec, QUESTION])["partitions"][0]["cards"]] == [
            ("req_q1", "question", "swb-1-conductor"), ("req_r1", "record", "wldn-design")]

    def test_the_design_agent_sees_each_record_proposed_and_not_yet_accepted_or_rejected_with_its_card(self, monkeypatch):
        """The design band reads crew record's record.<status> entries: 0021 proposed and its card open, 0022 settled
        in the pane, 0023 proposed and then accepted, so gone."""
        monkeypatch.setattr(board, "SHOWN", 0)
        logs = [dict(Act="record.proposed", On=["record/atlas-kit/0021"], At=ago(60)), dict(Act="record.proposed", On=["record/atlas-kit/0022"], At=ago(50),
                                                                                            State="settled in the pane"),
                dict(Act="record.proposed", On=["record/atlas-kit/0023"], At=ago(40)), dict(Act="record.accepted", On=["record/atlas-kit/0023"], At=ago(30))]
        rec = dict(QUESTION, card="req_r1", key="record/atlas-kit/0021", by="wldn-design")
        assert [(r["kit"], r["number"], r["settled"], r["card"] and r["card"]["card"]) for r in data(logs=logs, cards=[rec])["partitions"][0]["records"]] == [
            ("atlas-kit", "0021", False, "req_r1"), ("atlas-kit", "0022", True, None)]
        assert view("wldn-design", logs=logs, cards=[rec]) == [
            "wldn inception  0 signals not moved  2 records proposed  1 exploration",
            f"✓ atlas-kit record 0021  proposed {board.local(ago(60))}  card open, asked by wldn-design",
            f"  atlas-kit record 0022  proposed {board.local(ago(50))}  settled in the pane", "  and 1 more exploration"]
        assert board.agent_views(data(logs=logs, cards=[rec]))["cards"]["wldn-design"]


def test_a_chore_is_marked_in_a_ledger_a_planned_bolt_and_the_queue(monkeypatch):
    """A chore stands among the units in build order, its kind in the JSON and `chore` before its stage in the text
    (plan.11); its place is read from the kit's chore places."""
    import sys
    text = plan_text(bolts=[("apex-zones", "switchboard-kit", None), ("tenant-environments", "switchboard-kit", "swb-1")],
                     units=[("pin", "switchboard-kit", "apex-zones", [], "chore"), ("a", "switchboard-kit", "tenant-environments", []),
                            ("bump", "switchboard-kit", "tenant-environments", [], "chore"), ("tidy", "switchboard-kit", None, [], "chore")])
    monkeypatch.setattr(sys.modules[__name__], "the_plan", lambda: plan.Plan(text))
    sv = kits()
    sv[BOX]["kits"]["/kit/main"].update(chores=[], chore_places={"bump": {"path": "/kit/places/chore-bump", "head": "c" * 40, "head_at": ago(5),
                                                                         "ahead": 1, "bolt": "tenant-environments"}})
    sv[BOX]["kits"]["/kit/main"]["slots"]["swb-1"].append({"slot": "unit-2", "kind": "chore", "name": "bump"})
    d = data(sv=sv)
    ledger = next(b for b in d["partitions"][0]["construction"] if b["bolt"] == "tenant-environments")
    assert [(u["unit"], u["kind"], u["stage"], u["slot"]) for u in ledger["units"]] == [("a", "unit", "code", "unit-1"), ("bump", "chore", "verify", "unit-2")]
    out = board.board_text(d)
    assert "    bump  chore verify  unit-2" in lane(out, "Construction")
    assert lane(out, "Bolt plan") == ["  switchboard-kit apex-zones  Goal of apex-zones.", "    pin  chore ready", "  switchboard-kit tidy  chore queued"]
    # Its conductor's view, the mod's band, draws the chore in its ledger as the board does (code.8).
    mine = view("swb-1-conductor", sv=sv)
    assert mine[:3] == [f"  switchboard-kit  ◑◕  tenant-environments  0 of 2 merged  {TE_TIME}", "    ◑  a  code 1/2  unit-1", "    ◕  bump  chore verify  unit-2"]


class TestCrossed:
    """crew-board "Construction shows a crossed team's bolts from the runner's records" and "The planner's and ops's bands
    show what a crossed team's places wait on them for" (Decision 14 of teams-cross-to-flume-as-their-bolts-land, code.8):
    crw-4 holds x, given through Flume, a launched as request 1 and b after a as request 2; crw-5, in stream madswan too,
    holds y, given before it was given through Flume; deneb's runner as each case gives it."""

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")

    def data(self, runners, extra=(), kit=None, bolts=None):
        """The board of madswan, its runner as given and extra requests appended to those the give wrote; kit what deneb's
        read of crew holds beside, and bolts each bolt's facts there."""
        from facts import crew_read, crossed_fleet_read, launched
        fleet = crossed_fleet_read(**{"crw-5": "madswan"})
        fleet["partitions"]["madswan"].update(machine="deneb", blueprints=["afterthought/blueprints"], state="afterthought/crew-state")
        p, requests = launched(["x"], work=[("a", "x", [], "unit", []), ("b", "x", ["a"], "unit", []), ("y1", "y", [], "unit", [])],
                               fleet=fleet, held=[("y", "crw-5")])
        runs = {"madswan": (requests + [plan.Rec("Request", list(f.items())) for f in extra], runners)}
        found, sv = [("madswan", "afterthought/crew-state", "tip0", p)], crew_read(bolts=bolts or {"x": {}, "y": {}})
        sv["deneb"]["kits"]["/crew/main"].update(kit or {})
        r = dict(found=found, sv=sv, props=[], cards=[], unread={}, errors={}, landings=[], gives={}, signals={"madswan": ([], {})},
                 ops={"madswan": []}, logs={"madswan": []}, runs=runs, rows=plan.rail_rows(fleet, found, sv, [], {}, None, runs))
        return board.board_data(fleet, ["madswan"], r, NOW)

    def views(self, runners, extra=()):
        return {a: ["".join(s for s, _ in line) for line in v] for a, v in board.agent_views(self.data(runners, extra))["views"].items()}

    def test_a_crossed_teams_ledger(self):
        """crew-board "A crossed team's ledger": x on deneb in stream madswan, a at code, b waiting on a, and no slot line."""
        from facts import ran
        d = self.data(ran({1: "code"}, held=[2]))
        assert lane(board.board_text(d), "Construction")[:3] == [
            "  crew x  crw-4 on deneb  in Flume stream madswan  its age can't be told: the run record of the last 60 days holds no give of it",
            "    a  code 6/26", "    b  waiting  on a"]
        assert {t["team"]: t["stream"] for t in d["partitions"][0]["teams"]} == {"crw-4": "madswan", "crw-5": "madswan"}
        assert lane(board.board_text(d), "Construction")[3].startswith("  crew y  crw-5 on deneb  in Flume stream madswan")

    def test_a_started_bolts_ledger_shows_no_server(self, monkeypatch):
        """crew-board "A started bolt's work shows no server": a server running in x's own worktree, as a bolt given before
        record 0026 had one, is drawn for no part of x, its places being Flume's (_open.md: the runner reports a place's
        addresses), where y, given before, has it drawn."""
        from facts import ran
        monkeypatch.setattr(crew, "this_host", lambda: "deneb")
        site = {"here": "https://bolt--crew.local"}
        kit = dict(sites={"/crew/bolts/x": site, "/crew/bolts/y": site}, routes=[{"name": "bolt--crew", "url": "https://bolt--crew.local"}])
        d = self.data(ran({1: "code"}, held=[2]), kit=kit, bolts={"x": {"worktree": "/crew/bolts/x"}, "y": {"worktree": "/crew/bolts/y"}})
        x, y = (next(b for b in d["partitions"][0]["construction"] if b["bolt"] == n) for n in "xy")
        assert x["url"] is None and {u["url"] for u in x["units"]} == {None}
        assert y["url"] == "https://bolt--crew.local"
        assert "server" not in "\n".join(lane(board.board_text(d), "Construction")[:3])

    def test_a_question_in_the_planners_band(self):
        """crew-board "A question in the planner's band": a's construct stopped short asking."""
        from facts import ran
        v = self.views(ran({1: "stopped-short"}))["madswan-planner"]
        assert v[0].endswith("1 place waits on an answer")
        assert next(l for l in v if "asks at" in l).startswith("  crew  x  a  needs  asks at code: Head 118ec46 is ready for your flume:live run")

    def test_a_fix_of_main_in_ops_band(self):
        """crew-board "A fix of main in ops's band": main--a-test-reads-its-fixture is in code."""
        from facts import ran
        fix = {"Request": "3", "Act": "launch", "Host": "deneb", "Work": "fix/main/crew/a-test-reads-its-fixture", "Repo": "afterthought/crew",
               "Kind": "fix", "Name": "main--a-test-reads-its-fixture", "Base": "main", "Hold": "submission"}
        v = self.views(ran({3: "code"}), extra=[fix])["madswan-ops"]
        assert v[0].endswith("1 fix in flight") and v[1] == "  crew  fix main--a-test-reads-its-fixture  code 6/26  on deneb"

    def test_a_take_main_fix_in_flight_is_in_ops_band_and_on_its_ledger(self):
        from facts import ran
        fix = {"Request": "3", "Act": "launch", "Host": "deneb", "Work": "fix/x/take-main-4d3d9be", "Repo": "afterthought/crew", "Kind": "fix",
               "Name": "x--take-main-4d3d9be", "Base": "bolt/x"}
        d = self.data(ran({3: "code"}), extra=[fix])
        assert "    fix/x/take-main-4d3d9be  fix code 6/26" in lane(board.board_text(d), "Construction")
        assert "  crew  fix x--take-main-4d3d9be  code 6/26  on deneb" in self.views(ran({3: "code"}), extra=[fix])["madswan-ops"]

    def test_a_runner_crew_cant_read_is_named_for_attention(self):
        d = self.data({})
        assert {"what": "runner", "name": "deneb's runner", "why": "no runner answers on deneb: madswan/runner/deneb does not exist"} in (
            d["partitions"][0]["attention"])
        assert {u["stage"] for b in d["partitions"][0]["construction"] if b["bolt"] == "x" for u in b["units"]} == {"unknown"}

    def test_a_crossed_pieces_pip_is_the_stage_it_waits_at(self):
        assert board.pips([{"stage": "needs", "flume": {"of": "code"}}, {"stage": "submitted"}, {"stage": "launching"}, {"stage": "refused"}]) == "◑◕○?"
