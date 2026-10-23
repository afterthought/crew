"""What waits on the user (the crew-rail and rail-cards specs, briefs.12): plan.rail_rows on the plans, the open
proposals, the run record's batches and the kits as surveyed; plan.rail_text on what those rows and the open cards
make, the questions among them, and what the read's sweep did; plan.record_reading for what the rail reads of the run
record; plan.sweep_judgment for the card sessions a read judges dead; and the sweep of the cards (record 0031 §1, §2):
plan.sweep_judged, which judges from the rows, the run record and the cards which to close, ask after, post again or
post, and plan.sweep_cards, which acts on a stand-in for Pending You, herdr and the kinds' raises. That crew rail reads
all of it from the branch and the hosts and sweeps on every host is the review journey's (t-journey-review), and the
sweep's acts through the stubs the cards journey's (t-cards)."""
import datetime

import pytest

from facts import START, plan_text

import cards
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
           "bolts": {"apex-zones": {"exists": True, "head": "abc1234" + "0" * 33, "head_at": iso(30), "changes": ["zone-one"] if merged else [],
                                    "archived": ["zone-one"] if merged else [],
                                    "verdict": "passed (3 run, 1 replayed)"},
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

    def test_a_unit_in_verify_waits_on_nobody_since_its_report_is_fixed_in_one_round_with_no_card(self):
        assert not [r for r in rows() if "checked" in r["key"] or "stale" in r["key"]]
        assert {r["group"] for r in rows()} <= set(plan.RAIL) and "verify" not in plan.RAIL

    HEAD = f"{KIT} (wldn): 1 bolt waits to land on its main, in the plan's order; wldn-ops lands them"

    def test_a_kit_with_a_bolt_whose_every_unit_merged_is_one_row_timed_by_its_last_merge(self):
        """crew-rail "The last unit merges": one row a kit, main-level ops's, naming the bolt with its team."""
        land, = [r for r in rows() if r["group"] == "land"]
        assert (land["key"], land["at"]) == (f"land/{KIT}", plan.utc(iso(30)))
        assert land["what"] == [self.HEAD, f"apex-zones, swb-2 on {BOX}: can land"]
        assert land["cmds"] == [("answer", 'crew tell wldn-ops "Land apex-zones."')]
        assert land["bolts"] == [dict(bolt="apex-zones", team="swb-2", host=BOX, can=True)]

    def two_bolts(self, merged, planned=True):
        """swb-2 holds apex-zones, proven, and beta, given after it, whose unit b-one has merged or not."""
        p = plan.Plan(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("apex-zones", KIT, "swb-2"), ("beta", KIT, "swb-2")]
                                + ([("d", KIT, None)] if planned else []),
                                units=[("zone-one", KIT, "apex-zones", []), ("b-one", KIT, "beta", [])]))
        sv = survey()
        sv[BOX]["kits"]["/kit/main"]["bolts"]["beta"] = {"head": "bbb1234" + "0" * 33, "head_at": iso(20), "verdict": "passed (2 run)",
                                                         "changes": ["b-one"] if merged else [], "archived": ["b-one"] if merged else []}
        return {r["key"]: r for r in plan.rail_rows(FLEET, [("wldn", "WilldanGroup/crew-state", "tip", p)], sv, [], {}) if r["group"] == "land"}

    def test_a_landing_row_names_the_bolt_its_team_builds_meanwhile(self):
        land = self.two_bolts(merged=False)
        assert list(land) == [f"land/{KIT}"]
        assert land[f"land/{KIT}"]["what"][1] == f"apex-zones, swb-2 on {BOX}: swb-2 builds beta meanwhile; can land"
        assert land[f"land/{KIT}"]["cmds"] == [("answer", 'crew tell wldn-ops "Land apex-zones."')]

    def test_two_bolts_of_one_kit_are_one_row_its_tell_naming_both_in_order_each_saying_a_yes_frees_the_team(self):
        """crew-rail "Two bolts of one kit" and "A yes frees the team"."""
        land, = self.two_bolts(merged=True).values()
        assert land["what"][1:] == [f"apex-zones, swb-2 on {BOX}: a yes frees swb-2 for d; can land",
                                    f"beta, swb-2 on {BOX}: a yes frees swb-2 for d; can land"]
        assert land["what"][0].startswith(f"{KIT} (wldn): 2 bolts wait to land on its main")
        assert land["cmds"] == [("answer", 'crew tell wldn-ops "Land apex-zones, beta."')] and land["at"] == plan.utc(iso(30))

    def test_with_nothing_planned_a_yes_frees_the_team_for_nothing(self):
        land = self.two_bolts(merged=True, planned=False)
        assert land[f"land/{KIT}"]["what"][1] == f"apex-zones, swb-2 on {BOX}: a yes frees swb-2, and nothing is planned for it; can land"

    def test_a_bolt_with_a_fix_in_flight_lands_once_it_has_merged_or_been_dropped(self):
        sv = survey()
        sv[BOX]["kits"]["/kit/main"]["fixes"] = [{"fix": "fix/apex-zones/gap", "bolt": "apex-zones", "merged": False},
                                                {"fix": "fix/apex-zones/done", "bolt": "apex-zones", "merged": True}]
        land, = [r for r in rows(sv=sv) if r["group"] == "land"]
        assert (land["what"][1], land["cmds"]) == (f"apex-zones, swb-2 on {BOX}: lands once fix/apex-zones/gap has merged or been dropped", [])
        assert land["bolts"][0]["can"] is False
        sv[BOX]["kits"]["/kit/main"]["fixes"][0]["dropped"] = True  # dropped, its place not yet removed
        land, = [r for r in rows(sv=sv) if r["group"] == "land"]
        assert land["what"][1] == f"apex-zones, swb-2 on {BOX}: can land" and land["cmds"] == [("answer", 'crew tell wldn-ops "Land apex-zones."')]

    def test_a_landing_sluice_refused_at_the_bolts_head_is_held_in_its_words(self):
        """crew-rail "A refused landing"."""
        held = {"wldn": {"batches": [], "closed": set(), "posts": set(), "due": set(), "unanswered": {},
                         "refused": {"apex-zones": ("abc1234" + "0" * 33, "bolt/apex-zones did not land: sluice found a conflict")}}}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1] == (f"apex-zones, swb-2 on {BOX}: held: sluice refused its landing at abc1234, until its team's fix "
                                   "moves its head: bolt/apex-zones did not land: sluice found a conflict")
        assert land["cmds"] == []
        held["wldn"]["refused"] = {"apex-zones": ("c" * 40, "an older head's")}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1] == f"apex-zones, swb-2 on {BOX}: can land"

    def test_a_bolt_lands_only_once_its_verification_is_green(self, monkeypatch):
        sv = survey()
        sv[BOX]["kits"]["/kit/main"]["bolts"]["apex-zones"]["verdict"] = ""
        land, = [r for r in rows(sv=sv) if r["group"] == "land"]
        assert land["what"][1] == (f"apex-zones, swb-2 on {BOX}: lands once its verification is green; now its head abc1234 is no "
                                   "landing of sluice's, so it has no verdict")
        assert land["cmds"] == []

    def test_a_bolt_lands_only_once_every_units_latest_change_has_been_in_a_batch(self):
        held = {"wldn": {"batches": [], "closed": set(), "posts": set(), "due": {"zone-one"}}}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1] == f"apex-zones, swb-2 on {BOX}: lands once zone-one has been in a batch, which is due for them" and land["cmds"] == []
        held["wldn"]["due"] = None
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1].endswith("whether every unit's latest change has been in a batch can't be told: a host did not answer")

    def test_a_bolt_lands_only_once_the_user_has_answered_each_batch_holding_a_units_latest_change(self):
        """briefs.12: the user, 2026-10-19, on card req_5ff4d31d: "Wait for my answer on the batch card"."""
        held = {"wldn": {"batches": [(8, iso(10), [("zone-one", "swb-2", "abc1234")])], "closed": set(), "posts": set(), "due": set(),
                         "unanswered": {"zone-one": 8, "early": 7}}}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1:] == [f"apex-zones, swb-2 on {BOX}: lands once you have answered batch 8"] and land["cmds"] == []
        held["wldn"]["unanswered"] = {}
        land, = [r for r in rows(held=held) if r["group"] == "land"]
        assert land["what"][1:] == [f"apex-zones, swb-2 on {BOX}: can land"] and land["cmds"] == [("answer", 'crew tell wldn-ops "Land apex-zones."')]

    def test_a_landing_row_names_both_the_units_due_a_batch_and_the_batches_that_wait_on_the_user(self):
        p = plan.Plan(plan_text(bolts=[("apex-zones", KIT, "swb-2")], units=[(u, KIT, "apex-zones", []) for u in ("zone-one", "zone-two", "zone-three")]))
        sv, zones = survey(), ["zone-one", "zone-two", "zone-three"]
        sv[BOX]["kits"]["/kit/main"]["bolts"]["apex-zones"].update(changes=zones, archived=zones)
        held = {"wldn": {"batches": [], "closed": set(), "posts": set(), "due": {"zone-one"}, "unanswered": {"zone-two": 8, "zone-three": 9}}}
        land, = [r for r in plan.rail_rows(FLEET, [("wldn", "WilldanGroup/crew-state", "tip", p)], sv, [], {}, held) if r["group"] == "land"]
        assert land["what"][1:] == [f"apex-zones, swb-2 on {BOX}: lands once zone-one has been in a batch, which is due for them; "
                                    "lands once you have answered batches 8 and 9"]
        assert land["cmds"] == []

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
        assert [l for l in out.splitlines() if l.isalpha()] == ["proposals", "batches", "land", "operations"]
        assert out.count("\n  none") == 4 and "card:" not in out and "open cards whose row is gone" not in out and "swept" not in out

    def test_each_row_names_its_card_key_and_whether_a_card_is_open_whose_and_its_id(self):
        rs = rows([proposal(1)])
        out = text(rs, cards=[dict(label="wldn", card="req_prop-1", key="proposal/1", by="wldn-planner", host="mac-studio", at=NOW)])
        assert "    card:   proposal/1, open, asked by wldn-planner (req_prop-1)" in out
        assert f"    card:   land/{KIT}, none open" in out

    def test_an_open_card_whose_row_is_gone_is_listed_with_the_host_whose_rail_read_closes_it(self):
        old = dict(label="wldn", card="req_old-1", key="verify/checked/20260101-0000", by="swb-1-conductor", host=BOX, at=NOW)
        here = dict(old, card="req_old-2", key="proposal/9", by="wldn-planner", host="mac-studio")
        stray = text(rows(), cards=[old, here]).split("open cards whose row is gone:\n")[1].splitlines()
        assert stray[0].endswith(f"verify/checked/20260101-0000 (wldn), asked by swb-1-conductor on {BOX}")
        assert stray[1] == f"    left:   a rail read on {BOX} closes it, under that host's sign-in"
        assert stray[2].endswith("proposal/9 (wldn), asked by wldn-planner on mac-studio") and stray[3] == "    left:   a later rail read here closes it"
        assert "crew tell" not in "\n".join(stray)

    def test_a_row_without_a_card_names_the_refusal_of_its_last_post(self):
        refused = {"Act": "card.post", "Key": "proposal/1", "On": ["proposal/1"], "By": "wldn-planner", "At": iso(5),
                   "Refused": "Pending You refused post_request: Too many requests."}
        out = text(rows([proposal(1)]), logs={"wldn": [refused]})
        assert "    card:   proposal/1, none open; its last post was refused: Pending You refused post_request: Too many requests." in out
        posted = dict(refused, Refused=None, Card="req_1")
        assert "    card:   proposal/1, none open\n" in text(rows([proposal(1)]), logs={"wldn": [refused, posted]}) + "\n"

    def test_a_row_with_its_card_and_a_question_open(self):
        """The rail-cards scenario: proposal/4's card is open, the planner's, and swb-1-conductor's question is listed
        after the groups with its key, its asker and its age, and no words of the card's (record.3)."""
        p4 = dict(label="wldn", card="req_p4", key="proposal/4", by="wldn-planner", host=BOX, at=NOW)
        q1 = dict(label="wldn", card="req_q1", key="ask/swb-1-conductor/hold-the-macs", on="agent/swb-1-conductor", by="swb-1-conductor",
                  host="mac-studio", at=NOW - datetime.timedelta(minutes=14))
        bare = dict(q1, card="req_q2", key=None, at=NOW - datetime.timedelta(minutes=5))
        out = text(rows([proposal(4)]), cards=[p4, q1, bare])
        assert "    card:   proposal/4, open, asked by wldn-planner (req_p4)" in out
        asked = out.split("questions waiting on you:\n")[1].splitlines()
        assert [l[18:] for l in asked] == ["  14m      ask/swb-1-conductor/hold-the-macs (wldn), asked by swb-1-conductor on mac-studio (req_q1)",
                                           "  5m       a question (wldn), asked by swb-1-conductor on mac-studio (req_q2)"]
        assert "title" not in out and "open cards whose row is gone" not in out

    def test_a_read_that_swept_lists_each_card_it_closed_withdrew_or_posted_again_and_what_it_could_not_sweep(self):
        done = [dict(label="wldn", key="proposal/4", card="req_p4", by="wldn-planner", did="closed", words="its proposal was applied", new=None),
                dict(label="wldn", key="land/y", card="req_l1", by="swb-1-conductor", did="withdrawn", words="its bolt was dropped", new=None),
                dict(label="wldn", key=None, card="req_q1", by="crw-3-conductor", did="withdrawn", words="crw-3-conductor ended", new=None),
                dict(label="wldn", key="proposal/17", card="req_1", by="wldn-planner", did="lost", words="posted again as req_2", new="req_2")]
        out = text([], swept={"done": done, "unswept": [dict(label="madswan", why="this host can't ask through Pending You")]})
        assert out.split("cards swept:\n")[1].split("\n\n")[0].splitlines() == [
            "  proposal/4 (wldn), wldn-planner's req_p4: closed: its proposal was applied",
            "  land/y (wldn), swb-1-conductor's req_l1: withdrawn: its bolt was dropped",
            "  a question (wldn), crw-3-conductor's req_q1: withdrawn: crw-3-conductor ended",
            "  proposal/17 (wldn), wldn-planner's req_1: lost: posted again as req_2"]
        assert out.endswith("cards not swept:\n  madswan: this host can't ask through Pending You")

    def test_a_batch_crew_closed_with_no_card_is_named_so_beside_its_card_withdrawn(self):
        """review-batches, "Its card is already open": the read says both what it closed and the card it withdrew."""
        words = "its batch waits on nothing: x1 and x2 have landed"
        done = [dict(label="wldn", key="batch/3", card=None, by="wldn-planner", did="closed", words=words, new=None),
                dict(label="wldn", key="batch/3", card="req_b3", by="wldn-planner", did="withdrawn", words=words, new=None),
                dict(label="wldn", key="proposal/5", card=None, by="wldn-planner", did="left", words="its raise refused: x", new=None)]
        out = text([], swept={"done": done, "unswept": []})
        assert out.split("cards swept:\n")[1].splitlines() == [
            f"  batch/3 (wldn), wldn-planner, no card: closed: {words}",
            f"  batch/3 (wldn), wldn-planner's req_b3: withdrawn: {words}",
            "  proposal/5 (wldn), wldn-planner, no card: left: its raise refused: x"]

    def test_a_card_posted_again_under_its_rows_key_is_the_rows_and_the_older_is_listed_lost(self):
        """The rail-cards scenario: req_1 under proposal/17 read not found and the read posted req_2, so the row's card
        line names req_2, and req_1 is listed lost."""
        old = dict(label="wldn", card="req_1", key="proposal/17", by="wldn-planner", host="mac-studio", at=NOW)
        swept = {"done": [dict(label="wldn", key="proposal/17", card="req_1", by="wldn-planner", did="lost", words="posted again as req_2",
                               new="req_2")], "unswept": []}
        now = plan.swept_cards([old], swept, "mac-studio", NOW)
        assert [(c["card"], c["key"], c["by"], c["host"], c["on"]) for c in now] == [("req_2", "proposal/17", "wldn-planner", "mac-studio", "proposal/17")]
        out = text(rows([proposal(17)]), cards=now, swept=swept)
        assert "    card:   proposal/17, open, asked by wldn-planner (req_2)" in out and "req_1: lost: posted again as req_2" in out

    @pytest.mark.parametrize("key", ["record/atlas-kit/0021/abc1234", "record/atlas-kit/0021"])
    def test_a_decision_records_open_card_is_under_a_heading_of_its_own_with_no_command(self, key):
        rec = dict(label="wldn", card="req_rec-1", key=key, by="wldn-design", host="mac-studio", at=NOW)
        out = text([], cards=[rec])
        heads = [l for l in out.splitlines() if l and not l.startswith(" ")]
        assert heads[-1] == "decision records waiting on you:" and "open cards with no row" not in out
        assert out.splitlines()[-1].endswith(f"{key} (wldn), asked by wldn-design on mac-studio") and "questions" not in out

    def test_a_host_that_does_not_answer_is_named_and_a_stray_card_of_its_teams_is_not_listed(self):
        sv = survey(ok=False)
        card = dict(label="wldn", card="req_l-1", key="land/apex-zones/abc1234", by="swb-2-conductor", host="mac-studio", at=NOW)
        out = text(rows(sv=sv), cards=[card], sv=sv)
        assert f"{BOX} did not answer (ssh: connect to host timed out): its units and bolts may also wait on you" in out
        assert "open cards whose row is gone" not in out

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

    def test_a_refused_close_leaves_its_card_open_and_a_lost_cards_close_leaves_its_row_for_its_card_posted_again(self):
        refused = dict(post("req_1", "batch/1", act="card.close", minutes=1), Refused="Pending You refused the close: x")
        r = self.read([post("req_1", "batch/1"), refused])
        assert ([c["card"] for c in r["cards"]], r["held"]["closed"]) == (["req_1"], set())
        lost = dict(post("req_1", "batch/1", act="card.close", minutes=1), State="lost")
        r = self.read([post("req_1", "batch/1"), lost, post("req_2", "batch/1", minutes=2)])
        assert ([c["card"] for c in r["cards"]], r["held"]["closed"]) == (["req_2"], set())

    def test_a_batch_card_posted_again_after_its_close_keeps_its_row_and_the_sweep_holds_it(self):
        units = [("zone-one", "swb-2", "abc1")]
        batch = {"Act": "review.batch", "Batch": "1", "Units": "zone-one:swb-2@abc1", "At": "2026-10-12T09:59:00Z", "On": []}
        closed = post("req_1", "batch/1", act="card.close", minutes=1)
        r = self.read([batch, post("req_1", "batch/1"), closed, post("req_2", "batch/1", minutes=2)])
        assert ([c["card"] for c in r["cards"]], r["held"]["closed"]) == (["req_2"], set())
        b, = [x for x in rows(held={"wldn": r["held"]}) if x["group"] == "batches"]
        assert (b["key"], b["units"]) == ("batch/1", [u for u, *_ in units])
        j = TestSweepJudged().judged(rows=[b], cards_=[card("batch/1", "req_2", "wldn-planner")])
        assert (j["held"], j["gone"]) == ([(card("batch/1", "req_2", "wldn-planner"), b)], [])
        r = self.read([batch, post("req_1", "batch/1"), closed, post("req_2", "batch/1", minutes=2),
                       post("req_2", "batch/1", act="card.close", minutes=3)])
        assert r["held"]["closed"] == {"batch/1"} and not [x for x in rows(held={"wldn": r["held"]}) if x["group"] == "batches"]

    def test_a_batch_that_waits_on_nothing_is_no_row_and_one_with_a_unit_still_waiting_is(self):
        """review-batches, "Every unit has landed" and "One unit still waits on the user"; rail-cards, "An old batch card
        whose units have landed": batch 1's unit has landed, batch 2's second card's units have landed and one of its
        first's has not, and batch 9 holds a unit that has neither landed nor been held again."""
        def batch(n, units, minutes):
            return {"Act": "review.batch", "Batch": str(n), "Units": " ".join(f"{u}:swb-2@{i:04x}" for i, u in enumerate(units)),
                    "At": f"2026-10-12T09:{minutes:02d}:00Z", "On": []}
        seven = [f"u{i}" for i in range(7)]
        entries = [batch(1, ["zone-one"], 0), batch(2, seven, 1), post("req_21", "batch/2-1"), post("req_22", "batch/2-2"),
                   batch(9, ["early", "stale"], 2),
                   {"Act": "bolt.land", "On": ["bolt/b"] + [f"unit/{u}" for u in ["zone-one", "early"] + seven[1:]], "At": "2026-10-12T10:30:00Z"}]
        r = self.read(entries)
        assert r["held"]["settled"] == {"batch/1": "its batch waits on nothing: zone-one has landed",
                                        "batch/2-2": "its batch waits on nothing: u5 and u6 have landed"}
        assert {"batch/1", "batch/2-2"} <= r["held"]["closed"]
        assert [x["key"] for x in rows(held={"wldn": r["held"]}) if x["group"] == "batches"] == ["batch/2-1", "batch/9"]

    def test_a_card_its_owner_posts_again_under_a_key_replaces_the_older_but_another_agents_does_not(self):
        r = self.read([post("req_1", "proposal/1"), post("req_2", "proposal/1", minutes=1), post("req_9", "proposal/1", by="wldn-design", minutes=2)])
        assert [c["card"] for c in r["cards"]] == ["req_2", "req_9"]

    def test_a_post_refused_by_crew_card_or_pending_you_is_no_card(self):
        """crew card post records a refused post as card.post with Refused and no Card or Key: the rail, and so the
        board's markers and the agents' views (code.8), see no card for it."""
        refused = {"Act": "card.post", "On": ["unit/v1"], "By": "swb-1-conductor", "Host": BOX, "At": "2026-10-12T10:00:00Z",
                   "Refused": "Pending You refused post_request: Approve requests give their risk in approve.risk."}
        r = self.read([refused, post("req_1", "batch/1", minutes=1), dict(refused, On=["batch/2"])])
        assert ([c["card"] for c in r["cards"]], r["held"]["posts"]) == (["req_1"], {"batch/1"})

    def test_a_proposal_is_timed_by_its_first_entry_and_a_bolt_by_its_last_give(self):
        r = self.read([{"Act": "plan.propose", "On": ["proposal/1"], "At": "2026-10-12T10:00:00Z"},
                       {"Act": "plan.propose", "On": ["proposal/1"], "At": "2026-10-12T11:00:00Z"},
                       {"Act": "bolt.give", "On": ["bolt/apex-zones", "team/swb-2"], "At": "2026-10-12T11:00:00Z"},
                       {"Act": "bolt.give", "On": ["bolt/apex-zones", "team/swb-1"], "At": "2026-10-12T12:00:00Z", "Refused": "x"}])
        assert r["times"] == {("wldn", "proposal/1"): plan.utc("2026-10-12T10:00:00Z")}
        assert r["gives"] == {("wldn", "apex-zones"): "swb-2"}

    def test_while_a_host_of_the_record_does_not_answer_no_unit_is_known_due(self):
        held = plan.record_reading("wldn", [], the_plan(), START, missing={"mac-studio": "x"})["held"]
        assert (held["due"], held["unanswered"]) == (None, None)

    def test_the_units_waiting_on_the_users_answer_to_their_batch_are_read_with_the_batches(self):
        made = {"Act": "stage.end", "Ended": "delivered", "On": ["stage/zone-one/construct", "unit/zone-one"], "Delivered": "unit/zone-one@abc1",
                "At": "2026-10-12T10:00:00Z"}
        batch = {"Act": "review.batch", "Batch": "8", "Units": "zone-one:swb-2@abc1", "At": "2026-10-12T10:10:00Z", "On": []}
        r = self.read([made, batch, post("req_8", "batch/8", minutes=11)])
        assert (r["held"]["due"], r["held"]["unanswered"]) == (set(), {"zone-one": 8})
        r = self.read([made, batch, post("req_8", "batch/8", minutes=11), post("req_8", "batch/8", act="card.close", minutes=12)])
        assert r["held"]["unanswered"] == {}


def card(key, cid, by, host="mac-studio", minutes=0):
    return dict(label="wldn", card=cid, key=key, on=cards.row_object(key or "") or f"agent/{by}", by=by, host=host,
                at=NOW - datetime.timedelta(minutes=minutes))


def did(e, minutes=30, **f):
    """A run-record entry of the partition, minutes before NOW."""
    return dict(f, Act=e, At=iso(minutes), Host="mac-studio", By=f.pop("By", "wldn-planner"))


def row(key, group="proposals", label="wldn"):
    return dict(group=group, label=label, key=key, at=NOW, what=[key], cmds=[])


OWNERS = {"proposal/4": ("wldn-planner", "mac-studio"), "deploy/dev": ("wldn-ops", "mac-studio"), "land/y": ("swb-1-conductor", BOX)}


class TestSweepJudged:
    def judged(self, rows=(), cards_=(), entries=(), blind=(), proposed=(4,), kits=(), kit_of=None):
        return plan.sweep_judged("mac-studio", list(rows), list(cards_), list(entries), OWNERS, set(blind),
                                 None if proposed is None else set(proposed), NOW, kits=kits, kit_of=kit_of)

    def test_a_rows_card_whose_row_is_gone_is_closed_with_its_events_outcome_or_withdrawn_with_why(self):
        p4, y = card("proposal/4", "req_p4", "wldn-planner"), card("land/y", "req_l1", "swb-1-conductor")
        j = self.judged(cards_=[p4, y], entries=[did("plan.approve", On=["proposal/4"]), did("bolt.drop", On=["bolt/y"])])
        assert j["gone"] == [(p4, "its proposal was applied", None), (y, None, "its bolt was dropped")]
        assert (j["questions"], j["held"], j["none"]) == ([], [], [])

    @pytest.mark.parametrize("key, entries, why", [
        ("proposal/4", [{"Act": "plan.drop", "On": ["proposal/4"]}], (None, "its proposal was dropped")),
        ("proposal/4", [], (None, "its proposal is closed")),
        ("land/y", [{"Act": "bolt.land", "On": ["bolt/y"]}], ("its bolt landed", None)),
        ("land/y/abc1234", [{"Act": "bolt.land", "On": ["bolt/y"], "Refused": "x"}], (None, "its bolt no longer waits to land at abc1234")),
        ("verify/c/20261012-1200", [], (None, "a verify report has no card, its findings fixed in one round")),
        ("deploy/dev", [], (None, "its deploy no longer waits on your word")),
        ("op/dev/2", [], (None, "its step no longer waits on you")),
        ("batch/3", [], (None, "its batch no longer waits to be read")),
        ("batch/3", [{"Act": "review.batch", "Batch": "3", "Units": "x1:swb-1@aaa1", "At": iso(60), "On": []}, {"Act": "bolt.land", "On": ["bolt/b", "unit/x1"]}],
         (None, "its batch waits on nothing: x1 has landed"))])
    def test_why_a_rows_card_has_no_row_is_read_from_the_run_record(self, key, entries, why):
        assert plan.row_gone(key, entries) == why

    def test_a_deploys_card_whose_word_stands_is_left_for_its_deploys_end_to_close_and_listed_as_no_stray(self):
        d = card("deploy/dev", "req_d1", "wldn-ops")
        word = [did("ops.offer", On=["env/dev"], Head="a" * 40, Base="none"), did("ops.approve", On=["env/dev"], Head="a" * 40)]
        assert self.judged(cards_=[d], entries=word)["gone"] == []
        assert "open cards whose row is gone" not in text(rows(), cards=[d], logs={"wldn": word})
        ended = word + [did("ops.deploy", On=["env/dev"], Head="a" * 40, Phase="end", Outcome="ok")]
        assert self.judged(cards_=[d], entries=ended)["gone"] == [(d, None, "its deploy no longer waits on your word")]
        assert "deploy/dev (wldn), asked by wldn-ops on mac-studio" in text(rows(), cards=[d], logs={"wldn": ended})

    def test_only_the_cards_posted_on_this_host_are_judged_and_a_decision_records_only_once_it_is_settled(self):
        there = card("proposal/4", "req_p4", "wldn-planner", host=BOX)
        rec = card("record/atlas-kit/0021", "req_r1", "wldn-design")
        assert self.judged(cards_=[there, rec]) == {"gone": [], "questions": [], "held": [], "none": [], "settled": []}
        proposed = [did("record.proposed", On=["record/atlas-kit/0021"], Commit=["WilldanGroup/atlas-kit@" + "a" * 40], By="wldn-design")]
        assert self.judged(cards_=[rec], entries=proposed)["gone"] == []

    def test_a_decision_records_card_under_either_key_form_is_closed_at_its_status_wherever_crew_record_ran(self):
        """swancloud's record 0029, rejected on 2026-10-22 by crew record on deneb, whose card the design agent had
        posted on mac-studio before record 0031 under record/swancloud/0029/5eba218, which stayed open: the sweep on
        the card's host closes it, and one under record 0031's key, at the record's last status."""
        old, new = card("record/atlas-kit/0021/5eba218", "req_r0", "wldn-design"), card("record/atlas-kit/0021", "req_r1", "wldn-design")
        other = card("record/atlas-kit/0022", "req_r2", "wldn-design")
        status = [did("record.proposed", 60, On=["record/atlas-kit/0021"], By="wldn-design"),
                  dict(did("record.rejected", On=["record/atlas-kit/0021"], Commit=["WilldanGroup/atlas-kit@447980bd615c"], By="wldn-design"),
                       Host=BOX)]
        assert self.judged(cards_=[old, new, other], entries=status)["gone"] == [(old, "Rejected at 447980b", None), (new, "Rejected at 447980b", None)]
        again = status + [did("record.proposed", 10, On=["record/atlas-kit/0021"], By="wldn-design")]
        assert self.judged(cards_=[old, new], entries=again)["gone"] == []
        refused = status + [did("card.close", 5, Card="req_r0", Refused="Pending You refused the close: Too many requests.")]
        assert self.judged(cards_=[old, new], entries=refused)["gone"] == [(new, "Rejected at 447980b", None)]

    @pytest.mark.parametrize("key, entries, outcome", [
        ("record/atlas-kit/0021", [], None),
        ("record/atlas-kit/0021/abc1234", [{"Act": "record.accepted", "On": ["record/atlas-kit/0021"], "Commit": ["r@0123456789"]}], "Accepted at 0123456"),
        ("record/atlas-kit/0021", [{"Act": "record.accepted", "On": ["record/atlas-kit/0021"], "Commit": []}], "Accepted"),
        ("record/atlas-kit/0021", [{"Act": "record.rejected", "On": ["record/atlas-kit/0021"], "Commit": ["r@0123456789"], "Refused": "x"}], None),
        ("record/atlas-kit/0021", [{"Act": "record.rejected", "On": ["record/atlas-kit/0022"], "Commit": ["r@0123456789"]}], None)])
    def test_a_records_status_is_read_from_the_run_record_under_either_key_form(self, key, entries, outcome):
        assert plan.record_settled(key, entries) == outcome

    def test_a_question_is_asked_after_and_a_rows_card_with_its_row_checked(self):
        q, p4 = card(None, "req_q1", "crw-3-conductor"), card("proposal/4", "req_p4", "wldn-planner")
        j = self.judged(rows=[row("proposal/4")], cards_=[q, p4])
        assert (j["questions"], j["held"], j["gone"]) == ([q], [(p4, row("proposal/4"))], [])

    def test_a_row_with_no_card_open_on_any_host_is_posted_where_its_owner_runs_and_in_record_0031s_key_form_alone(self):
        rows_ = [row("proposal/4"), row("deploy/dev", "operations"), row("land/y", "land"), row("deploy/dev/abc1234", "operations")]
        assert self.judged(rows=rows_)["none"] == [row("proposal/4"), row("deploy/dev", "operations")]
        assert self.judged(rows=rows_, cards_=[card("proposal/4", "req_p4", "wldn-planner", host=BOX)])["none"] == [row("deploy/dev", "operations")]

    def test_a_card_or_row_whose_last_close_or_post_was_refused_lately_is_left_for_a_later_read(self):
        p4 = card("proposal/4", "req_p4", "wldn-planner")
        recent = [did("card.close", 5, Card="req_p4", Refused="Pending You refused the close: Too many requests."),
                  did("card.post", 5, Key="deploy/dev", Refused="Pending You refused post_request: x")]
        assert self.judged(rows=[row("deploy/dev", "operations")], cards_=[p4], entries=recent) == {"gone": [], "questions": [], "held": [], "none": [],
                                                                                                "settled": []}
        old = [dict(e, At=iso(plan.CARD_RETRY // 60 + 1)) for e in recent]
        j = self.judged(rows=[row("deploy/dev", "operations")], cards_=[p4], entries=old)
        assert ([c for c, *_ in j["gone"]], j["none"]) == ([p4], [row("deploy/dev", "operations")])

    def test_a_land_card_of_a_bolt_whose_teams_host_did_not_answer_is_left(self):
        assert self.judged(cards_=[card("land/y", "req_l1", "swb-1-conductor")], blind={"y"})["gone"] == []

    def test_a_proposals_card_is_withdrawn_only_on_a_plan_read_at_or_past_the_commit_it_was_raised_at(self):
        """A rail read that fetched the plan before the planner's proposal 5 was written, and read the planner's
        host's card.post for it after: the card has no row on that read, which holds no proposal 5, so it is left,
        its proposal open; a read that holds proposal 5 with no row for it withdraws it."""
        p5 = card("proposal/5", "req_p5", "wldn-planner")
        assert self.judged(cards_=[p5], proposed={1, 2, 3, 4}) == {"gone": [], "questions": [], "held": [], "none": [], "settled": []}
        assert self.judged(cards_=[p5], proposed=None)["gone"] == []
        assert self.judged(cards_=[p5], proposed={4, 5})["gone"] == [(p5, None, "its proposal is closed")]
        assert self.judged(rows=[row("proposal/5")], cards_=[p5], proposed={4, 5})["held"] == [(p5, row("proposal/5"))]

    @pytest.mark.parametrize("key, proposed, older", [
        ("proposal/5", {4}, True), ("proposal/5", None, True), ("proposal/5", {4, 5, 6}, False),
        ("land/y", set(), False), ("batch/5", None, False), (None, None, False)])
    def test_a_plan_read_is_older_than_a_proposals_card_when_it_holds_no_proposal_by_its_keys_number(self, key, proposed, older):
        assert plan.older_than_card(key, proposed) is older

    def test_an_old_card_of_a_bolts_own_is_withdrawn_as_a_row_of_its_kits_card(self):
        """rail-cards "A card from before": the conductor's land/y, swept on its host, while y waits to land."""
        y = card("land/y", "req_l1", "swb-1-conductor")
        j = self.judged(cards_=[y], kits=("crew",), kit_of={"y": "crew"})
        assert j["gone"] == [(y, None, "y is now a row of crew's landings card")]
        assert plan.row_gone("land/y", [{"Act": "bolt.land", "On": ["bolt/y"]}], ("crew",), {"y": "crew"}) == ("its bolt landed", None)

    def test_a_kits_card_whose_row_is_gone_is_withdrawn_saying_nothing_waits_on_its_main(self):
        assert plan.row_gone("land/crew", [], ("crew",), {}) == (None, "nothing waits to land on crew's main")

    def test_a_kits_card_is_left_while_the_host_of_a_bolt_of_it_does_not_answer(self):
        p = plan.Plan(plan_text(bolts=[("apex-zones", KIT, "swb-2")], units=[]))
        assert plan.blind_land(FLEET, p, survey(ok=False), f"land/{KIT}") is True
        assert plan.blind_land(FLEET, p, survey(), f"land/{KIT}") is False
        assert plan.blind_land(FLEET, p, survey(ok=False), "land/other-kit") is False

    def test_a_rows_owner_and_its_host(self):
        pl = the_plan()
        assert plan.row_owner(FLEET, pl, row("proposal/4")) == ("wldn-planner", BOX)
        assert plan.row_owner(FLEET, pl, row("deploy/dev", "operations")) == ("wldn-ops", BOX)
        assert plan.row_owner(FLEET, pl, row(f"land/{KIT}", "land")) == ("wldn-ops", BOX)  # the kit's landings card, main-level ops's


class Py:
    """A stand-in for one session with Pending You: each tool answered from answers, a (got, words) pair, or a
    function of the arguments giving one."""

    def __init__(self, acts, name):
        self.acts, self.name = acts, name

    def __enter__(self):
        if self.acts.opening:
            raise crew.Refusal(self.acts.opening)
        return self

    def __exit__(self, *exc):
        pass

    def answer(self, tool, args):
        self.acts.calls.append((self.name, tool, args))
        got = self.acts.answers.get(tool, ({"status": "pending", "version": 1}, None))
        return got(args) if callable(got) else got

    def call(self, tool, args):
        got, words = self.answer(tool, args)
        if words is not None:
            raise crew.Refusal(f"Pending You refused {tool}: {words}")
        return got


class Acts:
    """A stand-in for what the sweep reaches: Pending You, this host's run record, herdr's listing and the raises."""

    def __init__(self, answers=None, entries=(), listed=None, raises=None, opening=None, here="mac-studio", writes=True):
        self.answers, self.held, self.listing, self.raises, self.opening = dict(answers or {}), list(entries), listed or {}, raises or {}, opening
        self.here, self.writes = here, writes
        self.calls, self.emitted, self.raised = [], [], []

    def bridge(self, name, later, held=None):
        return Py(self, name)

    def emit(self, label, act, on, **fields):
        """The entry's id, as record.emit gives it, or None as when it could not be written (writes)."""
        self.emitted.append(dict(fields, Act=act, On=on))
        return f"e{len(self.emitted)}" if self.writes else None

    def entries(self, label):
        return self.held

    def tell(self, name, text):
        return True

    def put(self, url, data, kind):
        return None

    def host(self):
        return self.here

    def caller(self):
        return "chuck@mac-studio"

    def kits(self, label):  # the kits the partition's teams build, which tell land/<kit> from land/<bolt>
        return ("switchboard-kit",)

    def now(self):
        return NOW

    def listed(self, name):
        return self.listing.get(name, (False, None))

    def raise_of(self, kind):
        return self.raises.get(kind)

    def session(self, label, key, facts):
        return None

    def end(self, label, key):
        return None

    def release_preview(self, label, key):
        return None


def swept(rows_=(), cards_=(), entries=(), unread=None, proposed=(4, 5), **kw):
    """The sweep of a read of wldn on mac-studio, the partition's main machine here, with these rows and cards, its
    plan holding the proposals numbered proposed."""
    fleet = dict(FLEET, partitions={"wldn": dict(FLEET["partitions"]["wldn"], machine="mac-studio")})
    read = dict(found=[("wldn", "WilldanGroup/crew-state", "tip", the_plan())], sv=survey(), rows=list(rows_), cards=list(cards_),
                unread=unread or {}, logs={"wldn": list(entries)}, proposed={"wldn": set(proposed)})
    acts = Acts(entries=[{"Act": "card.post", "Key": c["key"], "By": c["by"], "Card": c["card"]} for c in cards_], **kw)
    return plan.sweep_cards(fleet, read, acts), acts


NOT_FOUND = (None, "Not found: request:req_x.")


class TestSweep:
    def test_every_row_is_live_but_one_the_record_holds_closed_with_no_card_open(self):
        cards = [dict(label="wldn", key="proposal/1")]
        assert plan.sweep_judgment("wldn", {"proposal/1", "land/b/abc1234", "batch/1"}, cards, None,
                                   {"closed": {"proposal/1", "land/b/abc1234", "batch/1"}}) == {"live": ["proposal/1"], "blind": []}

    def test_what_the_rail_cannot_judge_is_blind_and_nothing_is_taken_for_closed(self):
        assert plan.sweep_judgment("wldn", {"batch/1"}, [], {"mac-studio": "x"}, {"closed": {"batch/1"}}) == (
            {"live": ["batch/1"], "blind": ["batch/"]})

    def test_a_forgotten_card_is_closed_with_the_approvals_outcome_after_crew_asks_after_it_in_its_own_name(self):
        """The rail-cards scenario: proposal 4 was approved from the planner's pane and its card is still open."""
        p4 = card("proposal/4", "req_p4", "wldn-planner")
        out, acts = swept(cards_=[p4], entries=[did("plan.approve", On=["proposal/4"])],
                          answers={"get_request": ({"status": "pending", "version": 2}, None)})
        assert acts.calls[0] == ("crew", "get_request", {"requestId": "req_p4", "name": "crew"})
        assert acts.calls[2] == ("wldn-planner", "cancel_request", {"requestId": "req_p4", "name": "wldn-planner", "reason": "its proposal was applied"})
        assert [(e["Act"], e["Card"], e["State"], e["Outcome"]) for e in acts.emitted] == [("card.close", "req_p4", "withdrawn", "its proposal was applied")]
        assert out["done"] == [dict(label="wldn", key="proposal/4", card="req_p4", by="wldn-planner", did="closed", words="its proposal was applied", new=None)]

    def test_a_fresh_proposals_card_on_a_plan_read_older_than_it_is_neither_asked_after_nor_withdrawn(self):
        """The read's plan was fetched before proposal 6 was written, and the planner's card.post for it was read
        from its host after: Pending You is asked nothing and the card stays open, for a read that holds it."""
        p6 = card("proposal/6", "req_p6", "wldn-planner")
        out, acts = swept(cards_=[p6], proposed=(4, 5))
        assert (out, acts.calls, acts.emitted) == ({"done": [], "unswept": []}, [], [])
        out, acts = swept(cards_=[p6], proposed=(4, 5, 6))
        assert out["done"] == [dict(label="wldn", key="proposal/6", card="req_p6", by="wldn-planner", did="withdrawn", words="its proposal is closed", new=None)]

    def test_a_card_whose_bolt_was_dropped_is_withdrawn(self):
        y = card("land/y", "req_l1", "swb-1-conductor")
        out, acts = swept(cards_=[y], entries=[did("bolt.drop", On=["bolt/y"])])
        assert acts.calls[-1][1:] == ("cancel_request", {"requestId": "req_l1", "name": "swb-1-conductor", "reason": "its bolt was dropped"})
        assert [(d["did"], d["words"]) for d in out["done"]] == [("withdrawn", "its bolt was dropped")]

    def test_a_question_whose_asker_herdr_no_longer_lists_is_withdrawn_naming_the_asker(self):
        """The rail-cards scenario: crw-3-conductor's question card is open and crw-3's team is closed."""
        q = card("ask/crw-3-conductor/hold", "req_q1", "crw-3-conductor")
        out, acts = swept(cards_=[q], listed={"crw-3-conductor": (False, None)})
        assert acts.calls[1:] == [("crw-3-conductor", "get_request", {"requestId": "req_q1", "name": "crw-3-conductor"}),
                                  ("crw-3-conductor", "cancel_request", {"requestId": "req_q1", "name": "crw-3-conductor",
                                                                         "reason": "crw-3-conductor ended; ask again if it still matters"})]
        assert acts.emitted == [dict(Act="card.close", On=["agent/crw-3-conductor"], by="crw-3-conductor", Card="req_q1", Key="ask/crw-3-conductor/hold",
                                     State="withdrawn", Outcome="crw-3-conductor ended; ask again if it still matters")]
        assert [(d["did"], d["words"]) for d in out["done"]] == [("withdrawn", "crw-3-conductor ended")]

    def test_a_question_pending_you_already_ended_when_its_asker_is_gone_is_recorded_closed_and_sent_nothing(self):
        """The rail-cards scenario: crw-3-conductor's question, which Pending You reports resolved, after crw-3's team
        closed."""
        q = card("ask/crw-3-conductor/hold", "req_q1", "crw-3-conductor")
        out, acts = swept(cards_=[q], listed={"crw-3-conductor": (False, None)},
                          answers={"get_request": ({"status": "resolved", "version": 3}, None),
                                   "cancel_request": (None, "This request is already closed.")})
        assert acts.calls[1:] == [("crw-3-conductor", "get_request", {"requestId": "req_q1", "name": "crw-3-conductor"})]
        assert acts.emitted == [dict(Act="card.close", On=["agent/crw-3-conductor"], by="crw-3-conductor", Card="req_q1", Key="ask/crw-3-conductor/hold",
                                     State="closed", Outcome=plan.ENDED_ELSEWHERE)]
        assert [(d["did"], d["words"]) for d in out["done"]] == [("closed", "crw-3-conductor ended")]

    def test_a_question_whose_asker_runs_is_kept_and_one_herdr_cant_answer_for_is_kept_saying_why(self):
        q, r = card(None, "req_q1", "swb-1-conductor"), card(None, "req_q2", "wldn-ops")
        out, acts = swept(cards_=[q, r], listed={"swb-1-conductor": (True, None), "wldn-ops": (None, "herdr's agent list in session wldn-3 failed: x")},
                          answers={"get_request": (None, "This is wldn-ops's card; leave it.")})
        assert [(d["card"], d["did"], d["words"]) for d in out["done"]] == [
            ("req_q2", "left", "whether wldn-ops still runs can't be told: herdr's agent list in session wldn-3 failed: x")]
        assert acts.emitted == [] and {n for n, *_ in acts.calls} == {"crew"}

    def test_a_conductor_herdr_lists_by_no_name_is_kept(self):
        """swc-3-conductor's question on deneb, 2026-10-23: herdr had dropped its name, its pane still holding it, and
        its card was withdrawn within a minute as the conductor's ending (signal 2026-10-23-swc-3-conductor-8556b697/01)."""
        q = card("ask/swc-3-conductor/q", "req_q1", "swc-3-conductor")
        unnamed = {"pane_id": "w7:p1", "agent": "claude", "agent_status": "done"}
        out, acts = swept(cards_=[q], listed={"swc-3-conductor": crew.pane_holds("swc-3-conductor", "w7:p1", {"pane_id": "w7:p1"}, unnamed)},
                          answers={"get_request": (None, "This is swc-3-conductor's card; leave it.")})
        assert (out["done"], acts.emitted) == ([], [])
        assert {n for n, *_ in acts.calls} == {"crew"}

    def test_a_question_whose_askers_pane_crew_cant_read_is_left_saying_why(self):
        q = card("ask/swc-3-conductor/q", "req_q1", "swc-3-conductor")
        out, acts = swept(cards_=[q], listed={"swc-3-conductor": crew.pane_holds("swc-3-conductor", "w7:p1", None, None)},
                          answers={"get_request": (None, "This is swc-3-conductor's card; leave it.")})
        assert [(d["did"], d["words"]) for d in out["done"]] == [
            ("left", "whether swc-3-conductor still runs can't be told: herdr lists no pane w7:p1, which crew keeps for swc-3-conductor")]
        assert acts.emitted == []

    def test_a_rows_card_pending_you_no_longer_finds_is_posted_again_through_its_kinds_raise_saying_the_older_copy_is_dead(self):
        """The rail-cards scenario of a lost operations card: deploy/dev's card reads not found while the offer waits;
        its raise posts through the act's change, which finds it lost and posts it again."""
        facts = dict(env="dev", head="abc1234", base=None, landings=[], notes=None, release=None, steps=[], before=[], after=[])
        raise_deploy = lambda fleet, r, acts=None: plan.row_card_change(fleet, r["label"], "wldn-ops", cards.deploy_card, facts, "x", ("/kit/main", "github.com/o/k"), acts)
        d = card("deploy/dev", "req_d1", "wldn-ops")
        out, acts = swept(rows_=[row("deploy/dev", "operations")], cards_=[d], raises={"deploy": raise_deploy},
                          answers={"get_request": NOT_FOUND, "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_k"}]}, None),
                                   "post_request": ({"requestId": "req_d2", "version": 1}, None)})
        assert [(n, t) for n, t, _ in acts.calls] == [("crew", "get_request"), ("wldn-ops", "get_request"), ("wldn-ops", "match_area"), ("wldn-ops", "post_request")]
        posted = acts.calls[-1][2]
        assert posted["idempotencyKey"] == "deploy/dev:2" and posted["summary"].startswith(cards.DEAD)
        assert [(e["Act"], e.get("State"), e["Card"]) for e in acts.emitted] == [("card.close", "lost", "req_d1"), ("card.post", None, "req_d2")]
        assert out["done"] == [dict(label="wldn", key="deploy/dev", card="req_d1", by="wldn-ops", did="lost", words="posted again as req_d2", new="req_d2")]

    def test_a_card_pending_you_refuses_crew_as_its_owners_is_there_and_left(self):
        """Read in the recovery session on 2026-10-16: get_request on crw-2-conductor's card under another name, on this
        host's connection, answers with the card's ownership, not "not found", which only a card stranded on an older
        connection reads."""
        c = card("proposal/4", "req_188b8b6a", "crw-2-conductor")
        refused = "This is crw-2-conductor's card; leave it. You're \"recovery\": act only on the cards you posted."
        out, acts = swept(rows_=[row("proposal/4")], cards_=[c], answers={"get_request": (None, refused)})
        assert out["done"] == [] and acts.emitted == [] and [n for n, *_ in acts.calls] == ["crew"]

    def test_a_lost_card_of_a_kind_with_no_raise_is_recorded_lost_for_its_owner_to_raise_again(self):
        p4 = card("proposal/4", "req_p4", "wldn-planner")
        out, acts = swept(rows_=[row("proposal/4")], cards_=[p4], answers={"get_request": NOT_FOUND})
        assert [(e["Act"], e["State"], e["Card"]) for e in acts.emitted] == [("card.close", "lost", "req_p4")]
        assert [(d["did"], d["words"]) for d in out["done"]] == [("lost", "crew raises no card for proposal/4 on a rail read, so wldn-planner raises it again with the command that raised it")]

    def test_a_lost_card_whose_row_is_gone_is_posted_again_by_nobody(self):
        p4 = card("proposal/4", "req_p4", "wldn-planner")
        out, acts = swept(cards_=[p4], raises={"proposal": lambda *a, **k: pytest.fail("raised")}, answers={"get_request": NOT_FOUND})
        assert [(e["Act"], e["State"]) for e in acts.emitted] == [("card.close", "lost")] and out["done"][0]["did"] == "lost"

    def test_a_row_with_no_card_is_posted_through_its_kinds_raise_and_a_kind_with_none_is_left_as_it_is(self):
        seen = []

        def raise_proposal(fleet, r, acts=None):
            seen.append((r["key"], acts))
            return "req_p5"
        out, acts = swept(rows_=[row("proposal/5"), row("deploy/dev", "operations")], raises={"proposal": raise_proposal})
        assert [k for k, _ in seen] == ["proposal/5"] and seen[0][1] is acts
        assert out["done"] == [dict(label="wldn", key="proposal/5", card=None, by="wldn-planner", did="posted", words="its row had none open", new="req_p5")]
        out, acts = swept(rows_=[row("deploy/dev", "operations")])
        assert out == {"done": [], "unswept": []} and acts.calls == []

    def test_a_landing_row_whose_point_has_not_come_has_its_raise_asked_and_nothing_done(self):
        """A land row stands once every unit has merged, saying why the bolt can't land yet; its card is raised only once
        the bolt reads proven, so the sweep's raise for it, finding the point not come, posts nothing and nothing is
        recorded."""
        seen = []

        def raise_land(fleet, r, acts=None):
            seen.append(r["key"])
            return None
        out, acts = swept(rows_=[row(f"land/{KIT}", "land")], raises={"land": raise_land})
        assert seen == [f"land/{KIT}"] and out == {"done": [], "unswept": []} and acts.emitted == []

    def test_a_raise_that_refuses_is_said_and_refuses_nothing_else(self):
        def raise_proposal(fleet, r, acts=None):
            crew.fail("proposal 5's plan can't be read")
        out, _ = swept(rows_=[row("proposal/5")], raises={"proposal": raise_proposal})
        assert [(d["key"], d["did"], d["words"]) for d in out["done"]] == [("proposal/5", "left", "its raise refused: proposal 5's plan can't be read")]

    def test_a_host_not_signed_in_changes_nothing_and_says_so(self):
        said = "this host can't ask through Pending You: it is not signed in. The user signs it in with pendingyou-signin. " + plan.SWEEP_LATER
        out, acts = swept(cards_=[card("proposal/4", "req_p4", "wldn-planner")], entries=[did("plan.approve", On=["proposal/4"])], opening=said)
        assert out == {"done": [], "unswept": [dict(label="wldn", why=said)]} and acts.emitted == []

    def test_a_partition_whose_record_did_not_answer_on_its_branch_here_or_its_main_host_is_not_swept(self):
        out, acts = swept(cards_=[card("proposal/4", "req_p4", "wldn-planner")], unread={"wldn": {"mac-studio": "x"}})
        assert out["unswept"] == [dict(label="wldn", why="its run record did not answer whole, so which cards are open can't be told: mac-studio: x")]
        assert acts.calls == []
        out, acts = swept(cards_=[card("proposal/4", "req_p4", "wldn-planner")], unread={"wldn": {"macbook-pro": "x"}})
        assert out["unswept"] == [] and acts.calls


LANDED = [did("review.batch", 60, Batch="3", Units="x1:swb-1@aaa1 x2:swb-1@bbb1"), did("bolt.land", 40, On=["bolt/b", "unit/x1", "unit/x2"])]
WORDS = "its batch waits on nothing: x1 and x2 have landed"
CLOSE = dict(by="wldn-planner", why="batch: closed by crew, it waits on nothing", Key="batch/3", Outcome=WORDS, Act="batch.close", On=["batch/3"])


class TestAskerPane:
    """How the sweep reads whether a question's asker ended (briefs.11, read.1): from its pane, never its name."""

    def test_an_agent_in_the_askers_pane_runs_named_or_not(self):
        pane = {"pane_id": "w7:p1"}
        assert crew.pane_holds("swc-3-conductor", "w7:p1", pane, {"pane_id": "w7:p1", "name": "swc-3-conductor"}) == (True, None)
        assert crew.pane_holds("swc-3-conductor", "w7:p1", pane, {"pane_id": "w7:p1"}) == (True, None)

    def test_the_askers_pane_with_no_agent_in_it_is_its_ending(self):
        assert crew.pane_holds("crw-3-conductor", "w2:p1", {"pane_id": "w2:p1"}, None) == (False, None)

    def test_a_pane_crew_keeps_none_of_or_herdr_lists_none_of_is_a_read_it_names(self):
        assert crew.pane_holds("crw-3-conductor", "", None, None) == (None, "crew keeps no pane for crw-3-conductor")
        assert crew.pane_holds("crw-3-conductor", "w2:p1", None, None) == (None, "herdr lists no pane w2:p1, which crew keeps for crw-3-conductor")


class TestSettledSweep:
    """review-batches: the rail's sweep, on the partition's main-level host, records crew's close of a batch that waits
    on nothing once, in the planner's name, before it reaches Pending You, and withdraws a card open under its key with
    the same words."""

    def test_a_batch_that_waits_on_nothing_with_no_card_is_closed_by_crew_and_nothing_is_posted(self):
        out, acts = swept(entries=LANDED, raises={"batch": lambda *a, **k: pytest.fail("raised")})
        assert acts.emitted == [CLOSE] and acts.calls == []
        assert out == {"done": [dict(label="wldn", key="batch/3", card=None, by="wldn-planner", did="closed", words=WORDS, new=None)], "unswept": []}

    def test_its_card_open_here_is_withdrawn_with_the_words_of_crews_close(self):
        """review-batches, "Its card is already open"."""
        b3 = card("batch/3", "req_b3", "wldn-planner")
        out, acts = swept(cards_=[b3], entries=LANDED)
        assert acts.calls[-1] == ("wldn-planner", "cancel_request", {"requestId": "req_b3", "name": "wldn-planner", "reason": WORDS})
        assert [(e["Act"], e.get("Card"), e.get("State"), e["Outcome"]) for e in acts.emitted] == [
            ("batch.close", None, None, WORDS), ("card.close", "req_b3", "withdrawn", WORDS)]
        assert [(d["card"], d["did"], d["words"]) for d in out["done"]] == [(None, "closed", WORDS), ("req_b3", "withdrawn", WORDS)]

    def test_its_card_open_here_is_withdrawn_once_its_last_unit_is_dropped(self):
        """review-batches, "A unit dropped"."""
        words = "its batch waits on nothing: x1 has landed; x2 was dropped"
        entries = [did("review.batch", 60, Batch="3", Units="x1:swb-1@aaa1 x2:swb-1@bbb1"), did("bolt.land", 40, On=["bolt/b", "unit/x1"])]
        out, acts = swept(cards_=[card("batch/3", "req_b3", "wldn-planner")], entries=entries + [did("unit.drop", 35, On=["unit/x2", "bolt/b"])])
        assert acts.calls[-1] == ("wldn-planner", "cancel_request", {"requestId": "req_b3", "name": "wldn-planner", "reason": words})
        assert [(e["Act"], e.get("Card"), e.get("State"), e["Outcome"]) for e in acts.emitted] == [
            ("batch.close", None, None, words), ("card.close", "req_b3", "withdrawn", words)]

    def test_a_batch_crew_closed_or_the_user_answered_records_nothing_more(self):
        """review-batches, "Read again after the close": no second close is recorded, and nothing is posted."""
        again = LANDED + [did("batch.close", 30, On=["batch/3"], Key="batch/3", Outcome=WORDS)]
        out, acts = swept(entries=again, raises={"batch": lambda *a, **k: pytest.fail("raised")})
        assert (out, acts.emitted) == ({"done": [], "unswept": []}, [])
        refused = LANDED + [did("batch.close", 30, On=["batch/3"], Key="batch/3", Refused="x")]
        assert swept(entries=refused)[1].emitted == [CLOSE]
        answered = LANDED + [did("card.post", 50, Card="req_b3", Key="batch/3", On=["batch/3"]),
                             did("card.close", 45, Card="req_b3", Key="batch/3", On=["batch/3"], State="closed")]
        assert swept(entries=answered)[1].emitted == []

    def test_the_sweep_on_a_host_other_than_the_main_levels_records_nothing(self):
        out, acts = swept(entries=LANDED, here=BOX)
        assert (out, acts.emitted) == ({"done": [], "unswept": []}, [])

    def test_a_host_not_signed_in_still_records_the_close_and_leaves_the_card_for_a_later_read(self):
        said = "this host can't ask through Pending You: it is not signed in. " + plan.SWEEP_LATER
        out, acts = swept(cards_=[card("batch/3", "req_b3", "wldn-planner")], entries=LANDED, opening=said)
        assert acts.emitted == [CLOSE] and acts.calls == []
        assert out == {"done": [dict(label="wldn", key="batch/3", card=None, by="wldn-planner", did="closed", words=WORDS, new=None)],
                       "unswept": [dict(label="wldn", why=said)]}

    def test_a_partition_whose_record_did_not_answer_whole_records_no_close(self):
        """review-batches, "The record did not answer whole"."""
        out, acts = swept(entries=LANDED, unread={"wldn": {"mac-studio": "x"}})
        assert acts.emitted == [] and out["done"] == [] and out["unswept"][0]["label"] == "wldn"

    def test_a_close_the_run_record_could_not_take_is_said_and_tried_again_on_the_next_read(self):
        out, acts = swept(entries=LANDED, writes=False)
        assert acts.emitted == [CLOSE]
        assert out["done"] == [dict(label="wldn", key="batch/3", card=None, by="wldn-planner", did="left",
                                    words="crew's close was not recorded, as said above", new=None)]


class TestBolts:
    def data(self, sv=None, bolt=None):
        return plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", "abcdef1" + "0" * 33, the_plan())], sv or survey(), {}, bolt)

    def test_each_units_stage_is_read_from_its_kit_and_a_planned_bolt_from_the_plan_alone(self):
        b = {x["bolt"]: x for x in self.data()["partitions"][0]["plans"][0]["bolts"]}
        assert {u["unit"]: u["stage"] for u in b["tenant-environments"]["units"]} == {"early": "planned", "checked": "verify", "stale": "verify"}
        assert (b["tenant-environments"]["team"], b["tenant-environments"]["host"], b["tenant-environments"]["state"]) == ("swb-1", BOX, "active")
        assert b["apex-zones"]["state"] == "waits" and b["apex-zones"]["units"] == [dict(unit="zone-one", kind="unit", after=[], sources=[], stage="merged", tasks=None, worktree=None)]

    def test_the_text_names_the_branch_each_bolt_and_each_units_stage_and_place(self):
        out = plan.bolts_text(self.data())
        assert out.splitlines()[0] == "wldn/main abcdef1  WilldanGroup/crew-state"
        assert f"tenant-environments  switchboard-kit  swb-1 @ {BOX}  active" in out
        assert "  checked                                  verify 2/2   places/checked" in out

    def test_a_held_bolt_shows_its_verification(self):
        b = {x["bolt"]: x for x in self.data()["partitions"][0]["plans"][0]["bolts"]}
        assert b["apex-zones"]["verification"] == {"state": "green", "said": "sluice's verdict on its last landing, abc1234: passed (3 run, 1 replayed)"}
        assert "  verification: green, sluice's verdict on its last landing, abc1234: passed (3 run, 1 replayed)" in plan.bolts_text(self.data())

    def test_an_unreachable_hosts_bolts_read_unknown_and_the_host_is_named(self):
        d = self.data(sv=survey(ok=False))
        assert {u["stage"] for b in d["partitions"][0]["plans"][0]["bolts"] for u in b["units"]} == {"unknown"}
        assert plan.bolts_text(d).splitlines()[-1] == f"{BOX} did not answer (ssh: connect to host timed out): the stages of its bolts are unknown"

    def test_a_plan_not_started_says_how_to_start_it(self):
        d = plan.bolts_data(FLEET, ["wldn"], [("wldn", "WilldanGroup/crew-state", None, None)], {}, {})
        assert plan.bolts_text(d) == "wldn/main  WilldanGroup/crew-state  not started: crew state init wldn"


def test_a_card_act_whose_reply_named_no_card_is_listed_after_the_questions():
    """rail-cards: a question whose reply names no card. The card hook records the act unread on its agent, and the
    rail lists it with its agent, act and time; one older than CARD_DAYS days is not listed."""
    fresh = dict(Act="card.post", By="swb-1-conductor", Host=BOX, At=iso(30), State="unread", Key="ask/swb-1-conductor/hold")
    old = dict(fresh, At=(NOW - datetime.timedelta(days=plan.CARD_DAYS + 1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    assert plan.unread_card_acts({"wldn": [old, fresh, dict(fresh, State=None, Card="req_q1")]}, NOW) == [("wldn", fresh)]
    out = text(rows(), logs={"wldn": [fresh]})
    assert "card acts crew could not read:" in out
    assert f"card.post by swb-1-conductor on {BOX} (wldn), under ask/swb-1-conductor/hold: Pending You's reply named no card" in out
