"""What waits on the user (the crew-rail and rail-cards specs, briefs.12): plan.rail_rows on the plans, the open
proposals, the run record's batches and the kits as surveyed; plan.rail_text on what those rows and the open cards
make; plan.record_reading for what the rail reads of the run record; and plan.sweep_judgment for the card sessions a
read judges dead. That crew rail reads all of it from the branch and the hosts, writes nothing and sweeps on every
host is the review journey's (t-journey-review)."""
import datetime

import pytest

from facts import START, plan_text

import crew
import plan

BOX = "chuck-herdr-alpha"
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": BOX, "teams": ["swb-1", "swb-2"]}},
         "teams": {t: {"name": t, "label": "wldn", "machine": BOX, "kit": {"main": "/kit/main", "dir": "/kit", "name": "switchboard-kit"}}
                   for t in ("swb-1", "swb-2")},
         "hosts": {BOX: {"ssh": BOX, "home": "/h/box"}, "mac-studio": {"ssh": "mac-studio", "home": "/h/mac"}}}
KIT = "switchboard-kit"
NOW = START + datetime.timedelta(hours=4)


def iso(minutes_ago):
    return (NOW - datetime.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture(autouse=True)
def here(monkeypatch):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")


def the_plan():
    return plan.Plan(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("apex-zones", KIT, "swb-2")],
                               units=[(u, KIT, "tenant-environments", []) for u in ("early", "checked", "stale")]
                               + [("zone-one", KIT, "apex-zones", [])]))


def place(unit, tasks, ago, planning=True):
    return {"path": f"/kit/places/{unit}", "head": "f" * 40, "head_at": iso(ago), "tasks": tasks, "planning": planning, "open": [],
            "bolt": "tenant-environments"}


def survey(ok=True, merged=True):
    kit = {"ok": True, "main": [], "fixes": [],
           "places": {"early": place("early", (0, 2), 180), "checked": place("checked", (2, 2), 120), "stale": place("stale", (2, 2), 50)},
           "reports": {"checked": {"path": "/r/verify-checked-20261012-1200.md", "at": iso(100)},
                       "stale": {"path": "/r/verify-stale-20261012-1250.md", "at": iso(70)}},
           "bolts": {"apex-zones": {"head": "abc1234" + "0" * 33, "head_at": iso(30), "changes": ["zone-one"] if merged else []},
                     "tenant-environments": {"head": "d" * 40, "head_at": iso(200), "changes": []}}}
    return {BOX: {"ok": True, "kits": {"/kit/main": kit}}} if ok else {BOX: {"ok": False, "error": "ssh: connect to host timed out"}}


FOUND = [("wldn", "WilldanGroup/crew-state", "tip", None)]


def rows(props=(), times=None, held=None, sv=None):
    found = [("wldn", "WilldanGroup/crew-state", "tip", the_plan())]
    return plan.rail_rows(FLEET, found, sv or survey(), list(props), times or {}, held)


def text(rs, cards=(), sv=None, unread=None, **more):
    read = dict(found=[("wldn", "WilldanGroup/crew-state", "tip", the_plan())], rows=rs, cards=list(cards), sv=sv or survey(),
                unread=unread or {}, **more)
    return plan.rail_text(FLEET, ["wldn"], read, NOW)


def proposal(n, waiting=(), opened="2026-10-12"):
    return {"label": "wldn", "proposal": n, "by": "chuck@mac-studio", "case": f"The console gets bolt {n}.\nMore.", "waiting": list(waiting),
            "opened": opened}


class TestRows:
    def test_a_unit_whose_change_is_committed_waits_on_nobody(self):
        assert not [r for r in rows() if "early" in r["key"]]

    def test_a_unit_in_verify_waits_with_its_newest_report_while_that_is_newer_than_its_last_commit(self):
        verify = [r for r in rows() if r["group"] == "verify"]
        assert [r["key"] for r in verify] == ["verify/checked/20261012-1200"]
        r = verify[0]
        assert r["what"] == [f"unit checked (wldn), swb-1 on {BOX}: report /r/verify-checked-20261012-1200.md"]
        assert r["cmds"] == [("open", f"ssh -t {BOX} plannotator-tui /r/verify-checked-20261012-1200.md"),
                             ("answer", "crew tell swb-1-conductor \"On checked's verify report: \"")]
        assert r["doc"] == (BOX, "/r/verify-checked-20261012-1200.md")

    def test_on_its_host_the_report_opens_beside_the_rail(self, monkeypatch):
        monkeypatch.setattr(crew, "this_host", lambda: BOX)
        assert ("open", "plannotator-tui herdr open /r/verify-checked-20261012-1200.md") in [r for r in rows() if r["group"] == "verify"][0]["cmds"]

    def test_a_bolt_whose_every_unit_merged_waits_to_land_timed_by_its_last_merge(self):
        land, = [r for r in rows() if r["group"] == "land"]
        assert (land["key"], land["at"]) == ("land/apex-zones/abc1234", plan.utc(iso(30)))
        assert land["what"] == [f"bolt apex-zones (wldn), swb-2 on {BOX}: every unit merged; wldn-ops lands it"]
        assert land["cmds"] == [("answer", 'crew tell wldn-ops "Land bolt apex-zones."')]

    def test_a_bolt_lands_only_once_every_units_latest_change_has_been_in_a_batch(self):
        held = {"wldn": {"batches": [], "closed": set(), "posts": set(), "due": {"zone-one"}}}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1] == "lands once zone-one has been in a batch, which is due for them" and land["cmds"] == []
        held["wldn"]["due"] = None
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1] == "whether every unit's latest change has been in a batch can't be told: a host did not answer"

    def test_a_proposal_is_timed_by_its_entry_else_its_opened_date_naming_whom_it_waits_on(self):
        p1, p2 = [r for r in rows([proposal(1), proposal(2, ["swb-1"])], times={("wldn", "proposal/1"): NOW}) if r["group"] == "proposals"]
        assert (p1["at"], p1.get("date"), p2["date"]) == (NOW, None, "2026-10-12")
        assert p1["what"] == ["proposal 1 (wldn), by chuck@mac-studio: The console gets bolt 1."]
        assert p2["what"][1] == "still needs the agreement of swb-1-conductor"
        assert p1["cmds"] == [("read", "crew plan proposed 1 --label wldn"), ("open", "crew plan proposed 1 --label wldn --open"),
                              ("answer", "crew plan approve 1 --label wldn")]

    def test_a_batch_is_one_row_holding_every_unit_until_its_card_closes(self):
        units = [(f"u{c}", "swb-1", "abc1234") for c in "abcdefg"]
        held = {"wldn": {"batches": [(2, iso(10), units)], "closed": set(), "posts": set(), "due": set()}}
        b, = [r for r in rows(held=held) if r["group"] == "batches"]
        assert (b["key"], b["what"]) == ("batch/2", ["batch 2 (wldn): " + ", ".join(f"u{c} (swb-1)" for c in "abcdefg")])
        assert b["cmds"] == [("open", f"ssh -t {BOX} plannotator-tui /h/box/.local/state/crew/wldn-main/reports/batch-wldn-2.md"),
                             ("answer", 'crew tell wldn-planner "On batch 2: "')]
        held["wldn"]["closed"] = {"batch/2"}
        assert not [r for r in rows(held=held) if r["group"] == "batches"]

    def test_a_batch_posted_as_cards_of_five_before_keeps_a_row_for_each_card_until_it_closes(self):
        units = [(f"u{c}", "swb-1", "abc1234") for c in "abcdefg"]
        held = {"wldn": {"batches": [(3, iso(10), units)], "closed": {"batch/3-2"}, "posts": {"batch/3-1", "batch/3-2"}, "due": set()}}
        b, = [r for r in rows(held=held) if r["group"] == "batches"]
        assert (b["key"], b["what"][0]) == ("batch/3-1", "batch 3 (wldn), card 1 of 2: ua (swb-1), ub (swb-1), uc (swb-1), ud (swb-1), ue (swb-1)")


class TestText:
    def test_with_nothing_waiting_each_group_says_none_in_order(self):
        out = text([])
        assert [l for l in out.splitlines() if l.isalpha()] == ["proposals", "batches", "verify", "land", "operations"]
        assert out.count("\n  none") == 5 and "card:" not in out and "open cards with no row" not in out

    def test_each_row_names_its_card_key_and_whether_a_card_is_open_whose_and_its_id(self):
        rs = rows([proposal(1)])
        out = text(rs, cards=[dict(label="wldn", card="req_prop-1", key="proposal/1", by="wldn-planner", host="mac-studio", at=NOW)])
        assert "    card:   proposal/1, open, asked by wldn-planner (req_prop-1)" in out
        assert "    card:   verify/checked/20261012-1200, none open" in out
        assert "    card:   land/apex-zones/abc1234, none open" in out

    def test_an_open_card_whose_row_is_gone_is_listed_with_the_tell_to_close_it(self):
        old = dict(label="wldn", card="req_old-1", key="verify/checked/20260101-0000", by="swb-1-conductor", host=BOX, at=NOW)
        out = text(rows(), cards=[old])
        stray = out.split("open cards with no row:\n")[1].splitlines()
        assert stray[0].endswith(f"verify/checked/20260101-0000 (wldn), asked by swb-1-conductor on {BOX}")
        assert stray[1] == '    answer: crew tell swb-1-conductor "Close your Pending You card verify/checked/20260101-0000: its row is gone."'

    def test_a_decision_records_open_card_is_under_a_heading_of_its_own_with_no_command(self):
        rec = dict(label="wldn", card="req_rec-1", key="record/atlas-kit/0021/abc1234", by="wldn-design", host="mac-studio", at=NOW)
        out = text([], cards=[rec])
        heads = [l for l in out.splitlines() if l and not l.startswith(" ")]
        assert heads[-1] == "decision records waiting on you:" and "open cards with no row" not in out
        assert out.splitlines()[-1].endswith("record/atlas-kit/0021/abc1234 (wldn), asked by wldn-design on mac-studio")

    def test_a_host_that_does_not_answer_is_named_and_a_stray_card_of_its_teams_is_not_listed(self):
        sv = survey(ok=False)
        card = dict(label="wldn", card="req_v-1", key="verify/checked/20260101-0000", by="swb-1-conductor", host="mac-studio", at=NOW)
        out = text(rows(sv=sv), cards=[card], sv=sv)
        assert f"{BOX} did not answer (ssh: connect to host timed out): its units and bolts may also wait on you" in out
        assert "open cards with no row" not in out

    def test_a_read_that_swept_says_each_session_it_ended_and_each_host_it_could_not_check(self):
        out = text([], ended=[dict(key="proposal/1", unit=None, label="wldn", host=BOX, why="its row is gone",
                                   said="ended proposal/1's session, plannotator pid 42")],
                   unchecked=[dict(label="wldn", host="mac-studio", why="did not answer (ssh: timed out)")])
        assert out.endswith(f"card sessions ended:\n  proposal/1 (wldn) on {BOX}: its row is gone; ended proposal/1's session, plannotator pid 42\n"
                            "card sessions not checked:\n  mac-studio (wldn): did not answer (ssh: timed out)")


def post(card, key, by="wldn-planner", minutes=0, act="card.post"):
    return {"Act": act, "Card": card, "Key": key, "On": [key], "By": by, "Host": "mac-studio",
            "At": (START + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")}


class TestRecord:
    def read(self, entries):
        return plan.record_reading("wldn", entries, the_plan(), START - datetime.timedelta(days=1))

    def test_a_card_is_open_from_its_post_until_its_close(self):
        r = self.read([post("req_1", "proposal/1"), post("req_1", "proposal/1", act="card.close", minutes=1)])
        assert (r["cards"], r["held"]["closed"]) == ([], {"proposal/1"})

    def test_a_card_its_owner_posts_again_under_a_key_replaces_the_older_but_another_agents_does_not(self):
        r = self.read([post("req_1", "proposal/1"), post("req_2", "proposal/1", minutes=1), post("req_9", "proposal/1", by="wldn-design", minutes=2)])
        assert [c["card"] for c in r["cards"]] == ["req_2", "req_9"]

    def test_a_proposal_is_timed_by_its_first_entry_and_a_bolt_by_its_last_give(self):
        r = self.read([{"Act": "plan.propose", "On": ["proposal/1"], "At": "2026-10-12T10:00:00Z"},
                       {"Act": "plan.propose", "On": ["proposal/1"], "At": "2026-10-12T11:00:00Z"},
                       {"Act": "bolt.give", "On": ["bolt/apex-zones", "team/swb-2"], "At": "2026-10-12T11:00:00Z"},
                       {"Act": "bolt.give", "On": ["bolt/apex-zones", "team/swb-1"], "At": "2026-10-12T12:00:00Z", "Refused": "x"}])
        assert r["times"] == {("wldn", "proposal/1"): plan.utc("2026-10-12T10:00:00Z")}
        assert r["gives"] == {("wldn", "apex-zones"): "swb-2"}

    def test_while_a_host_of_the_record_does_not_answer_no_unit_is_known_due(self):
        assert plan.record_reading("wldn", [], the_plan(), START, missing={"mac-studio": "x"})["held"]["due"] is None


class TestSweep:
    def test_every_row_is_live_but_one_the_record_holds_closed_with_no_card_open(self):
        cards = [dict(label="wldn", key="proposal/1")]
        assert plan.sweep_judgment("wldn", {"proposal/1", "verify/v2/x", "batch/1"}, cards, None,
                                   {"closed": {"proposal/1", "verify/v2/x", "batch/1"}}, []) == {"live": ["proposal/1"], "blind": []}

    def test_what_the_rail_cannot_judge_is_blind_and_nothing_is_taken_for_closed(self):
        assert plan.sweep_judgment("wldn", {"batch/1"}, [], {"mac-studio": "x"}, {"closed": {"batch/1"}}, ["v3"]) == (
            {"live": ["batch/1"], "blind": ["batch/", "verify/v3/"]})


class TestBolts:
    def data(self, sv=None, bolt=None):
        return plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", "abcdef1" + "0" * 33, the_plan())], sv or survey(), {}, bolt)

    def test_each_units_stage_is_read_from_its_kit_and_a_planned_bolt_from_the_plan_alone(self):
        b = {x["bolt"]: x for x in self.data()["partitions"][0]["plans"][0]["bolts"]}
        assert {u["unit"]: u["stage"] for u in b["tenant-environments"]["units"]} == {"early": "planned", "checked": "verify", "stale": "verify"}
        assert (b["tenant-environments"]["team"], b["tenant-environments"]["host"], b["tenant-environments"]["state"]) == ("swb-1", BOX, "active")
        assert b["apex-zones"]["state"] == "active" and b["apex-zones"]["units"] == [dict(unit="zone-one", after=[], sources=[], stage="merged", tasks=None, worktree=None)]

    def test_the_text_names_the_branch_each_bolt_and_each_units_stage_and_place(self):
        out = plan.bolts_text(self.data())
        assert out.splitlines()[0] == "wldn/main abcdef1  WilldanGroup/crew-state"
        assert f"tenant-environments  switchboard-kit  swb-1 @ {BOX}  active" in out
        assert "  checked                                  verify 2/2   places/checked" in out

    def test_an_unreachable_hosts_bolts_read_unknown_and_the_host_is_named(self):
        d = self.data(sv=survey(ok=False))
        assert {u["stage"] for b in d["partitions"][0]["plans"][0]["bolts"] for u in b["units"]} == {"unknown"}
        assert plan.bolts_text(d).splitlines()[-1] == f"{BOX} did not answer (ssh: connect to host timed out): the stages of its bolts are unknown"

    def test_a_plan_not_started_says_how_to_start_it(self):
        d = plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", None, None)], {}, {})
        assert plan.bolts_text(d) == "wldn/main  WilldanGroup/crew-state  not started: crew state init wldn"
