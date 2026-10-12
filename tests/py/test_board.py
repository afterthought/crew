"""The board of a partition's flow (the crew-board spec): board.board_data on one read of the plan, proposals, signals,
kits and run record, as plan.rail_read and board.signals give it, and board.board_text, board.frame_text and
board.stamp on what that makes. That crew board reads it all and writes nothing, and the rail tab's refresh writes the
frame the board tab draws, are the board journey's (t-journey-board)."""
import datetime

import pytest

from facts import plan_text

import board
import crew
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


def read(sv=None, signals=None, props=(), landings=(), gives=None, rows=None, cards=(), errors=None, unread=None, pl=True):
    p = the_plan() if pl else None
    found = [("wldn", "WilldanGroup/crew-state", "tip0" if pl else None, p)]
    sv = sv or kits()
    return dict(found=found, sv=sv, props=list(props), cards=list(cards), unread=unread or {}, errors=errors or {},
                landings=list(landings), gives=gives or {}, signals={"wldn": (signals or [], {})},
                rows=rows if rows is not None else (plan.rail_rows(FLEET, found, sv, list(props), {}, None) if p else []))


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

    def test_operation_lists_a_bolt_landed_this_week_and_not_one_landed_eight_days_ago(self):
        landings = [dict(label="wldn", bolt="atlas-maps", units=["map-one"], at=NOW - datetime.timedelta(hours=1), by="chuck@mac-studio", host="mac-studio"),
                    dict(label="wldn", bolt="old-maps", units=["old"], at=NOW - datetime.timedelta(days=8), by="wldn-ops", host="mac-studio")]
        op = lane(board.board_text(data(landings=landings, gives={("wldn", "atlas-maps"): "atl-1"})), "Operation")
        assert len(op) == 1 and op[0].startswith("  atlas-maps  landed ") and op[0].endswith(" by chuck@mac-studio  atl-1  map-one")

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
        assert "close the operator workspace's rail tab and run crew operator up wldn" in said

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
        assert sorted(p) == ["attention", "bolt_plan", "construction", "hosts", "inception", "label", "operation", "plan", "teams"]
        te = next(b for b in p["construction"] if b["bolt"] == "tenant-environments")
        assert sorted(te) == ["bolt", "fixes", "goal", "host", "markers", "repo", "state", "team", "teams", "units", "url"]
        assert sorted(te["units"][0]) == ["markers", "slot", "stage", "tasks", "unit", "url", "worktree"]
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
