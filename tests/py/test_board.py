"""The board of a partition's flow (the crew-board spec): board.board_data on one read of the plan, proposals, signals,
kits and run record, as plan.rail_read and board.signals give it, and board.board_text, board.frame_text and
board.stamp on what that makes. That crew board reads it all and writes nothing, and the rail tab's refresh writes the
frame the board tab draws, are the board journey's (t-journey-board)."""
import datetime
import json
import pathlib
import re

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
         "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": BOX, "kit": KIT},
                   "swb-2": {"name": "swb-2", "label": "wldn", "machine": BOX, "kit": KIT},
                   "brd-1": {"name": "brd-1", "label": "wldn", "machine": BOX, "kit": {"name": "breadboard-kit", "main": "/b/main", "dir": "/b"}},
                   "atl-1": {"name": "atl-1", "label": "wldn", "machine": "mac-studio", "kit": {"name": "atlas-kit", "main": "/a/main", "dir": "/a"}}},
         "hosts": {BOX: {"kind": "nixos", "ssh": BOX}, "mac-studio": {"kind": "darwin", "ssh": "mac-studio"}}}
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def ago(minutes):
    return board.iso(NOW - datetime.timedelta(minutes=minutes))


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
           "explorations": [{"name": "command-cost", "first": "Reading: what each crew command costs."}]}
    brd = {"ok": True, "main": ["done-one"], "places": {}, "reports": {}, "bolts": {"board-done": {"head": "e" * 40, "head_at": ago(10), "changes": []}},
           "fixes": [], "slots": {}, "sites": {}, "routes": []}
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
                logs={"wldn": list(logs) or list(entries)},
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
        assert con[:4] == ["  switchboard-kit tenant-environments  swb-1 on chuck-herdr-alpha",
                           "    a  code 1/2  unit-1  https://unit-a--switchboard-kit--box.dev", "    b  planned",
                           "    fix/tenant-environments/edge  fix  unit-4"]
        assert "! breadboard-kit board-done  brd-1 on chuck-herdr-alpha  landed" in con

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
        assert f"  switchboard-kit tenant-environments  swb-1 on {BOX}  unknown" in con and "    a  unknown" in con
        assert out.splitlines()[0].endswith("read from mac-studio")

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
    def test_with_no_frame_the_board_tab_says_how_to_open_both_tabs_afresh(self):
        said = board.frame_text("wldn", None, None, False, NOW)
        assert said.startswith("No board for wldn yet: the rail tab's loop writes it each time it refreshes")
        assert "close the console's rail tab and run crew console up wldn" in said

    def test_a_frame_read_five_minutes_ago_is_headed_with_its_age(self):
        d = data()
        d["read_at"] = board.iso(NOW - datetime.timedelta(minutes=5))
        assert "(5m ago: the rail tab has not refreshed it since)" in board.frame_text("wldn", d, None, False, NOW).splitlines()[0]
        d["read_at"] = board.iso(NOW)
        assert " ago" not in board.frame_text("wldn", d, None, False, NOW).splitlines()[0]


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
        assert sorted(p) == ["attention", "bolt_plan", "cards", "construction", "environments", "hosts", "inception", "label", "operation", "plan",
                             "records", "teams"]
        te = next(b for b in p["construction"] if b["bolt"] == "tenant-environments")
        assert sorted(te) == ["bolt", "fixes", "goal", "host", "markers", "repo", "state", "team", "teams", "units", "url"]
        assert sorted(te["units"][0]) == ["kind", "slot", "stage", "tasks", "unit", "url", "worktree"]
        assert sorted(te["fixes"][0]) == ["fix", "merged", "slot", "url", "worktree"]

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
        assert view("swb-1-conductor") == ["  switchboard-kit  ◑◔  tenant-environments  0 of 2 merged", "    ◑  a  code 1/2  unit-1", "    ◔  b  planned",
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
        assert mine[:4] == ["✓ switchboard-kit  ●  doctor-rows  waits to land  1 of 1 merged  no card open", "    ●  rows-one  merged",
                            "  switchboard-kit  ◑  ssh-fix  0 of 1 merged", "    ◑  ssh-one  code 1/2  unit-1"]
        assert lane(board.board_text(data(sv=sv)), "Construction") == [
            "✓ switchboard-kit doctor-rows  swb-2 on chuck-herdr-alpha  waits to land  no card open", "    rows-one  merged",
            "  switchboard-kit ssh-fix  swb-2 on chuck-herdr-alpha", "    ssh-one  code 1/2  unit-1"]

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
        assert mine[0] == "  switchboard-kit  ??  tenant-environments  unknown  0 of 2 merged" and mine[1] == "    ?  a  unknown"
        assert f"! {BOX} did not answer (its kits: ssh: timed out)" in mine
        assert not [l for l in view("atl-1-conductor", sv=kits(ok=False)) if "did not answer" in l]

    def test_a_bolt_landed_and_still_in_the_plan_is_named_for_attention_to_its_conductor(self):
        assert view("brd-1-conductor") == ["! breadboard-kit  ●  board-done  landed  1 of 1 merged", "    ●  done-one  landed",
                                           "! bolt board-done: every unit has landed on main, and the bolt is still in the plan"]

    def test_the_planner_reads_the_plan_in_brief_each_teams_bolt_and_the_proposals_with_whom_they_wait_on(self):
        assert view("wldn-planner", props=WAITS) == [
            "wldn plan  2 held  1 planned  1 queued  1 proposal open", "  atlas-kit  atl-1  holds no bolt",
            "! breadboard-kit  brd-1  ●  board-done  landed  1 of 1 merged", "  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged",
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
        assert mine[4:8] == ["  atlas-kit  atl-1  holds no bolt", "! breadboard-kit  brd-1  ●  board-done  landed  1 of 1 merged",
                             "  switchboard-kit  swb-1  ◑◔  tenant-environments  0 of 2 merged", "  switchboard-kit  swb-2  holds no bolt"]
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
        assert v["stale"] == [(f"crew: the board was last read at {board.local(data()['read_at'])}, too long ago to show; the rail tab on mac-studio "
                               "has not refreshed it since", "dim")]
        # a day with it: a restart, or a rail tab that stopped, can leave it days old
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
        lines = [v["stale"]] + [l for lines in v["views"].values() for l in lines] + [l for lines in board.agent_views(data(cards=[QUESTION]))["cards"].values() for l in lines]
        assert all(isinstance(l, list) and all(isinstance(t, str) and len(seg) == 2 and style in (None, "bold", "dim") for seg in l for t, style in [seg])
                   for l in lines)


QUESTION = dict(label="wldn", card="req_q1", key=None, on="agent/swb-1-conductor", by="swb-1-conductor", host=BOX,
                at=NOW - datetime.timedelta(minutes=14))


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
    assert mine[:3] == ["  switchboard-kit  ◑◕  tenant-environments  0 of 2 merged", "    ◑  a  code 1/2  unit-1", "    ◕  bump  chore verify  unit-2"]
