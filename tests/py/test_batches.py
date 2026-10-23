"""Constructed changes reach the user in batches that span the partition (briefs.12): which changes are due
(plan.due_changes), when a batch is due and why (plan.batch_due), a batch's cards (plan.batch_cards), which batches
wait on nothing (plan.batch_settled), and the facts crew raises a batch's one card from once its summary is delivered
(plan.batch_facts, summary_paragraph,
batch_subjects; record 0031). The rail's rows are test_rail's; telling the planner and the reviewer's tab, the review
journey's (t-journey-review); the raise's wiring, its session and its card, t-cards'."""
import datetime

import pytest

from facts import START, at, card_closed, constructed, plan_of, reviewed, told

import plan

PLAN = plan_of(bolts={"b1": "swb-1", "b2": "swb-2", "queued": None},
               units={"x1": "b1", "x2": "b1", "y1": "b2", "z1": "queued", "w1": None})
EVERY_5 = {"every": 5, "hours": 4}
HOUR = datetime.timedelta(hours=1)


class TestDue:
    def test_each_unit_whose_last_construct_no_batch_has_held_is_due_in_the_plans_order(self):
        entries = [constructed("y1", "aaa1"), constructed("x1", "bbb1"), constructed("x2", "ccc1", 5)]
        assert [(u, team, sha) for u, team, sha, _ in plan.due_changes(PLAN, entries)] == [
            ("x1", "swb-1", "bbb1"), ("x2", "swb-1", "ccc1"), ("y1", "swb-2", "aaa1")]

    def test_a_change_a_batch_held_is_not_due_and_constructed_again_it_is(self):
        entries = [constructed("x1", "bbb1"), reviewed(1, [("x1", "swb-1", "bbb1")], 10)]
        assert plan.due_changes(PLAN, entries) == []
        entries.append(constructed("x1", "bbb2", 20))
        assert [(u, sha) for u, _, sha, _ in plan.due_changes(PLAN, entries)] == [("x1", "bbb2")]

    def test_units_of_no_bolt_a_team_holds_are_not_due(self):
        assert plan.due_changes(PLAN, [constructed("z1", "ddd1"), constructed("w1", "eee1")]) == []

    def test_a_construct_that_stopped_or_was_refused_delivers_no_change(self):
        stopped = dict(constructed("x1", "bbb1"), Ended="stopped")
        refused = dict(constructed("x2", "ccc1"), Refused="slots full")
        assert plan.due_changes(PLAN, [stopped, refused]) == []


class TestAnswered:
    """A bolt lands only once every unit's latest change has been in a batch whose card the user has answered
    (briefs.12; the user, 2026-10-19, on card req_5ff4d31d: "Wait for my answer on the batch card")."""

    def test_a_change_in_a_batch_whose_card_the_user_answered_waits_on_nothing(self):
        entries = [constructed("x1", "bbb1"), reviewed(7, [("x1", "swb-1", "bbb1")], 10), card_closed("batch/7", "req_7", 20)]
        assert plan.awaiting_answer(entries) == {}

    def test_a_change_in_a_batch_whose_card_is_unanswered_waits_on_that_batch(self):
        entries = [constructed("x1", "bbb1"), constructed("x2", "ccc1"), reviewed(7, [("x1", "swb-1", "bbb1"), ("x2", "swb-1", "ccc1")], 10)]
        assert plan.awaiting_answer(entries) == {"x1": 7, "x2": 7}

    def test_a_card_sent_back_through_its_reading_session_is_answered_and_one_lost_or_whose_close_was_refused_is_not(self):
        held = [constructed("x1", "bbb1"), reviewed(7, [("x1", "swb-1", "bbb1")], 10)]
        assert plan.awaiting_answer(held + [card_closed("batch/7", "req_7", 20, state="withdrawn")]) == {}
        assert plan.awaiting_answer(held + [card_closed("batch/7", "req_7", 20, state="lost")]) == {"x1": 7}
        assert plan.awaiting_answer(held + [card_closed("batch/7", "req_7", 20, refused="Pending You did not answer")]) == {"x1": 7}

    def test_a_card_posted_again_under_the_key_after_its_close_waits_until_that_card_closes(self):
        held = [constructed("x1", "bbb1"), reviewed(7, [("x1", "swb-1", "bbb1")], 10)]
        posted = lambda card, minutes: {"Act": "card.post", "Key": "batch/7", "Card": card, "At": f"2026-10-12T10:{minutes:02d}:00Z", "On": []}
        assert plan.awaiting_answer(held + [posted("req_7", 11), card_closed("batch/7", "req_7", 20), posted("req_8", 21)]) == {"x1": 7}
        assert plan.awaiting_answer(held + [posted("req_7", 11), posted("req_8", 12), card_closed("batch/7", "req_8", 20)]) == {}
        assert plan.awaiting_answer(held + [posted("req_7", 11), card_closed("batch/7", "req_7", 20),
                                            dict(posted("req_8", 21), Refused="Pending You did not answer")]) == {}

    def test_a_unit_sent_back_by_the_batchs_notes_waits_for_its_new_change_to_be_in_a_batch_and_then_for_its_answer(self):
        entries = [constructed("x1", "bbb1"), reviewed(7, [("x1", "swb-1", "bbb1")], 10), card_closed("batch/7", "req_7", 20),
                   constructed("x1", "bbb2", 30)]
        assert plan.awaiting_answer(entries) == {}
        assert [(u, sha) for u, _, sha, _ in plan.due_changes(PLAN, entries)] == [("x1", "bbb2")]
        entries.append(reviewed(8, [("x1", "swb-1", "bbb2")], 40))
        assert plan.due_changes(PLAN, entries) == [] and plan.awaiting_answer(entries) == {"x1": 8}
        entries.append(card_closed("batch/8", "req_8", 50))
        assert plan.awaiting_answer(entries) == {}

    def test_an_older_change_of_the_unit_in_an_unanswered_batch_holds_nothing(self):
        entries = [constructed("x1", "bbb1"), reviewed(7, [("x1", "swb-1", "bbb1")], 10), constructed("x1", "bbb2", 20),
                   reviewed(8, [("x1", "swb-1", "bbb2")], 30), card_closed("batch/8", "req_8", 40)]
        assert plan.awaiting_answer(entries) == {}

    def test_a_batch_posted_as_cards_of_five_before_waits_on_the_card_that_holds_the_unit(self):
        units = [(f"u{i}", "swb-1", f"{i:04x}") for i in range(7)]
        entries = [constructed(u, sha) for u, _, sha in units] + [reviewed(3, units, 10)] + [
            {"Act": "card.post", "Key": k, "Card": f"req_{k}", "At": "2026-10-12T10:11:00Z", "On": []} for k in ("batch/3-1", "batch/3-2")]
        entries.append(card_closed("batch/3-1", "req_batch/3-1", 20))
        assert plan.awaiting_answer(entries) == {"u5": 3, "u6": 3}


def pane_answer(n, by="swancloud-planner", at="2026-10-22T20:17:04Z", refused=None):
    """A run-record entry: batch n answered in the user's own words in by's pane, as crew card answer records it."""
    return {"Act": "batch.answer", "On": [f"batch/{n}"], "Key": f"batch/{n}", "Batch": str(n), "Chars": "28", "By": by, "At": at,
            "From": [f"session/s-1/u-{n}"], "Refused": refused}


class TestPaneAnswer:
    """A batch is answered by the user's own words in a main-level pane (review-batches; record 0031 as amended
    2026-10-22): the answer closes every key of its batch for good, as a tap closes its card."""

    HELD = [constructed("x1", "bbb1"), reviewed(13, [("x1", "swb-1", "bbb1")], 10),
            {"Act": "card.post", "Key": "batch/13", "Card": "req_13", "At": at(11), "On": ["batch/13"]}]

    def test_an_answer_in_a_pane_closes_its_batch(self):
        assert plan.batch_closed(self.HELD + [pane_answer(13)]) == {"batch/13"}

    def test_a_card_posted_under_its_key_after_the_answer_leaves_it_closed(self):
        entries = self.HELD + [pane_answer(13), {"Act": "card.post", "Key": "batch/13", "Card": "req_14", "At": at(30), "On": ["batch/13"]}]
        assert plan.batch_closed(entries) == {"batch/13"}

    def test_an_answer_of_a_batch_posted_as_cards_of_five_before_closes_each_card(self):
        posts = [{"Act": "card.post", "Key": k, "Card": f"req_{k}", "At": at(11), "On": []} for k in ("batch/6-1", "batch/6-2")]
        assert plan.batch_closed(posts + [pane_answer(6)]) == {"batch/6", "batch/6-1", "batch/6-2"}

    def test_a_refused_answer_closes_nothing(self):
        assert plan.batch_closed(self.HELD + [pane_answer(13, refused="the words are the agent's own")]) == set()
        assert plan.awaiting_answer(self.HELD + [pane_answer(13, refused="x")]) == {"x1": 13}

    def test_the_units_of_a_batch_answered_in_a_pane_wait_on_nothing(self):
        assert plan.awaiting_answer(self.HELD) == {"x1": 13}
        assert plan.awaiting_answer(self.HELD + [pane_answer(13)]) == {}

    def test_its_card_is_closed_answered_naming_whose_pane_and_when(self):
        assert plan.row_gone("batch/13", self.HELD + [pane_answer(13)]) == ("Answered in swancloud-planner's pane at 20:17Z", None)
        assert plan.pane_answered(self.HELD + [pane_answer(13), pane_answer(13, by="swancloud-operator", at="2026-10-22T20:19:00Z")]) == {
            "batch/13": ("swancloud-planner", "2026-10-22T20:17:04Z")}

    def test_no_card_is_raised_again_for_a_batch_answered_in_a_pane(self):
        assert plan.batch_facts(13, self.HELD + [pane_answer(13)], "## x1\n\nIt works.", {}) is None


def landed(bolt, units, minutes=0, refused=None):
    """A run-record entry: bolt landed, with each of its units."""
    return {"Act": "bolt.land", "On": [f"bolt/{bolt}"] + [f"unit/{u}" for u in units], "At": f"2026-10-12T11:{minutes:02d}:00Z",
            "Refused": refused}


def dropped(units, minutes=0, bolt=None, refused=None):
    """A run-record entry: units dropped from the plan, by crew unit drop (or a proposal's approval, which writes the
    same entry) for one, or with bolt by crew bolt drop without --requeue."""
    act, on = ("bolt.drop", [f"bolt/{bolt}"]) if bolt else ("unit.drop", [])
    return {"Act": act, "On": on + [f"unit/{u}" for u in units] + ([] if bolt else ["bolt/b1"]),
            "At": f"2026-10-12T11:{minutes:02d}:00Z", "Refused": refused}


class TestSettled:
    """A batch that waits on nothing is closed by crew (review-batches): each of its units has landed, was dropped since
    the batch was made, or is held by a later batch, read from the run record alone (signal
    2026-10-20-swancloud-planner-1703a4ae/02: 23 batch cards posted on wldn's box, most of them for bolts landed days
    before)."""

    def test_a_batch_every_unit_of_which_has_landed_waits_on_nothing(self):
        entries = [reviewed(3, [("x1", "swb-1", "aaa1"), ("x2", "swb-1", "bbb1")], 10), landed("b1", ["x1", "x2"], 20)]
        assert plan.batch_settled(entries) == {"batch/3": "its batch waits on nothing: x1 and x2 have landed"}

    def test_a_batch_whose_unit_a_later_batch_holds_waits_on_nothing_and_the_later_batch_does_not(self):
        entries = [reviewed(5, [("x1", "swb-1", "aaa1")], 10), constructed("x1", "aaa2", 20), reviewed(7, [("x1", "swb-1", "aaa2")], 30)]
        assert plan.batch_settled(entries) == {"batch/5": "its batch waits on nothing: batch 7 holds a newer change of x1"}

    def test_a_unit_landed_and_another_held_again_are_both_said_landed_first(self):
        entries = [reviewed(6, [("y1", "swb-2", "ccc1"), ("x1", "swb-1", "aaa1")], 10), reviewed(8, [("y1", "swb-2", "ccc2")], 20),
                   landed("b1", ["x1"], 30)]
        assert plan.batch_settled(entries) == {"batch/6": "its batch waits on nothing: x1 has landed; batch 8 holds a newer change of y1"}

    def test_each_later_batch_is_named_oldest_first_with_the_units_it_is_the_newest_to_hold(self):
        entries = [reviewed(2, [("x1", "swb-1", "aaa1"), ("x2", "swb-1", "bbb1"), ("y1", "swb-2", "ccc1")], 0),
                   reviewed(4, [("x1", "swb-1", "aaa2"), ("y1", "swb-2", "ccc2")], 10), reviewed(5, [("x2", "swb-1", "bbb2")], 20),
                   reviewed(6, [("y1", "swb-2", "ccc3")], 30), landed("b1", ["x1"], 40)]
        assert plan.batch_settled(entries)["batch/2"] == "its batch waits on nothing: x1 has landed; batch 5 holds a newer change of x2; batch 6 holds a newer change of y1"
        entries = entries[:2] + [reviewed(5, [("x1", "swb-1", "aaa3"), ("x2", "swb-1", "bbb2")], 20)]
        assert plan.batch_settled(entries)["batch/2"] == "its batch waits on nothing: batch 4 holds a newer change of y1; batch 5 holds newer changes of x1 and x2"

    def test_a_batch_with_one_unit_neither_landed_nor_held_again_still_waits(self):
        entries = [reviewed(9, [("x1", "swb-1", "aaa1"), ("y1", "swb-2", "ccc1")], 10), landed("b1", ["x1"], 20)]
        assert plan.batch_settled(entries) == {}

    def test_a_refused_landing_or_batch_counts_for_nothing(self):
        held = [reviewed(3, [("x1", "swb-1", "aaa1")], 10)]
        assert plan.batch_settled(held + [landed("b1", ["x1"], 20, refused="x1 has not landed")]) == {}
        assert plan.batch_settled(held + [dict(reviewed(4, [("x1", "swb-1", "aaa2")], 20), Refused="x")]) == {}

    def test_the_unit_constructed_a_third_time_leaves_the_batch_settled(self):
        """review-batches, "The unit moves on again": batch 5 stays closed though x1's newest change is in no batch."""
        entries = [constructed("x1", "aaa1"), reviewed(5, [("x1", "swb-1", "aaa1")], 10), constructed("x1", "aaa2", 20),
                   reviewed(7, [("x1", "swb-1", "aaa2")], 30), constructed("x1", "aaa3", 40)]
        assert list(plan.batch_settled(entries)) == ["batch/5"]
        assert [(u, sha) for u, _, sha, _ in plan.due_changes(PLAN, entries)] == [("x1", "aaa3")]

    def test_an_old_batch_card_of_five_is_settled_on_its_own_units(self):
        """rail-cards, "An old batch card whose units have landed": batch/2-2's units have landed, one of batch/2-1's not."""
        units = [(f"u{i}", "swb-1", f"{i:04x}") for i in range(7)]
        entries = [reviewed(2, units, 0)] + [{"Act": "card.post", "Key": k, "Card": f"req_{k}", "At": "2026-10-12T10:01:00Z", "On": []}
                                            for k in ("batch/2-1", "batch/2-2")] + [landed("b1", ["u1", "u2", "u3", "u4", "u5", "u6"], 20)]
        assert plan.batch_settled(entries) == {"batch/2-2": "its batch waits on nothing: u5 and u6 have landed"}

    def test_a_unit_dropped_since_the_batch_was_made_waits_on_nothing(self):
        """review-batches, "A unit dropped": by crew unit drop or a proposal's approval of one."""
        entries = [reviewed(4, [("x1", "swb-1", "aaa1"), ("x2", "swb-1", "bbb1")], 10), landed("b1", ["x1"], 20)]
        assert plan.batch_settled(entries) == {}
        assert plan.batch_settled(entries + [dropped(["x2"], 30)]) == {"batch/4": "its batch waits on nothing: x1 has landed; x2 was dropped"}
        approved = dict(dropped(["x2"], 30), From=["proposal/9"])
        assert plan.batch_settled(entries + [approved]) == {"batch/4": "its batch waits on nothing: x1 has landed; x2 was dropped"}

    def test_units_dropped_with_their_bolt_wait_on_nothing_and_queued_with_it_still_wait(self):
        """review-batches, "A bolt dropped with its units queued": a requeued bolt's drop names no unit."""
        held = [reviewed(11, [("x1", "swb-1", "aaa1"), ("x2", "swb-1", "bbb1")], 10)]
        assert plan.batch_settled(held + [dropped(["x1", "x2"], 20, bolt="b1")]) == {"batch/11": "its batch waits on nothing: x1 and x2 were dropped"}
        assert plan.batch_settled(held + [dropped([], 20, bolt="b1")]) == {}

    def test_a_refused_drop_counts_for_nothing(self):
        held = [reviewed(4, [("x1", "swb-1", "aaa1")], 10)]
        assert plan.batch_settled(held + [dropped(["x1"], 20, refused="unit x1 has merged into its bolt, so it can't be dropped")]) == {}

    def test_a_drop_from_before_the_batch_was_made_counts_for_nothing(self):
        """review-batches, "A unit dropped and added again before the batch"."""
        entries = [dropped(["x1"], 0), constructed("x1", "aaa1", 5), reviewed(10, [("x1", "swb-1", "aaa1")], 10)]
        assert plan.batch_settled(entries) == {}
        assert plan.batch_settled(entries + [dropped(["x1"], 20)]) == {"batch/10": "its batch waits on nothing: x1 was dropped"}

    def test_landed_dropped_and_held_later_are_said_in_that_order(self):
        entries = [reviewed(2, [("y1", "swb-2", "ccc1"), ("x2", "swb-1", "bbb1"), ("x1", "swb-1", "aaa1")], 0),
                   reviewed(5, [("y1", "swb-2", "ccc2")], 10), dropped(["x2"], 20), landed("b1", ["x1"], 30)]
        assert plan.batch_settled(entries)["batch/2"] == "its batch waits on nothing: x1 has landed; x2 was dropped; batch 5 holds a newer change of y1"

    def test_a_unit_dropped_after_a_later_batch_held_it_or_held_again_once_added_back_is_counted_dropped(self):
        later = [reviewed(2, [("x1", "swb-1", "aaa1")], 0), reviewed(3, [("x1", "swb-1", "aaa2")], 10), dropped(["x1"], 20)]
        assert plan.batch_settled(later) == {"batch/2": "its batch waits on nothing: x1 was dropped",
                                             "batch/3": "its batch waits on nothing: x1 was dropped"}
        back = [reviewed(2, [("x1", "swb-1", "aaa1")], 0), dropped(["x1"], 10), constructed("x1", "bbb1", 15),
                reviewed(3, [("x1", "swb-1", "bbb1")], 20)]
        assert plan.batch_settled(back) == {"batch/2": "its batch waits on nothing: x1 was dropped"}

    def test_a_batch_with_one_unit_dropped_and_another_still_waiting_waits(self):
        entries = [reviewed(4, [("x1", "swb-1", "aaa1"), ("y1", "swb-2", "ccc1")], 10), dropped(["x1"], 20)]
        assert plan.batch_settled(entries) == {}

    def test_crews_close_is_not_the_users_answer(self):
        """review-batches, "crew's close is not the user's answer": batch 5 waits on nothing, and x1's bolt still waits on
        the user's answer to batch 7."""
        entries = [constructed("x1", "aaa1"), reviewed(5, [("x1", "swb-1", "aaa1")], 10), constructed("x1", "aaa2", 20),
                   reviewed(7, [("x1", "swb-1", "aaa2")], 30)]
        assert "batch/5" in plan.batch_settled(entries) and plan.awaiting_answer(entries) == {"x1": 7}
        assert plan.batch_closed(entries) == set()


def due(n):
    return [(f"u{i}", "swb-1", f"{i:04x}", "2026-10-12T10:00:00Z") for i in range(n)]


class TestBatchDue:
    def test_nothing_due_is_never_a_batch_however_long_it_has_been(self):
        assert plan.batch_due([], [], EVERY_5, START + 100 * HOUR, []) == []

    def test_four_changes_are_not_yet_a_batch_at_a_setting_of_five(self):
        assert plan.batch_due(due(4), [], EVERY_5, START, []) == []

    def test_the_fifth_change_makes_a_batch_due_with_the_count(self):
        assert plan.batch_due(due(5), [], EVERY_5, START, []) == ["5 changes are due, and a batch is every 5"]

    def test_the_planner_is_told_once_until_a_batch_is_delivered(self):
        assert plan.batch_due(due(5), [told(1)], EVERY_5, START, []) == []
        assert plan.batch_due(due(5), [told(1), reviewed(1, [], 2)], EVERY_5, START, []) == ["5 changes are due, and a batch is every 5"]

    def test_the_hours_run_from_the_last_batch(self):
        entries = [reviewed(1, [], 0)]
        assert plan.batch_due(due(1), entries, EVERY_5, START + 3 * HOUR, []) == []
        assert plan.batch_due(due(1), entries, EVERY_5, START + 4 * HOUR, []) == ["4 hours have passed since the last batch"]

    def test_with_no_batch_yet_the_hours_run_from_the_first_due_construct(self):
        assert plan.batch_due(due(1), [], EVERY_5, START + 4 * HOUR, []) == ["4 hours have passed since the first of them was constructed"]

    def test_a_bolt_with_every_unit_merged_makes_its_due_units_a_batch_at_once(self):
        assert plan.batch_due(due(1), [], EVERY_5, START, [("b1", True, ["u0"])]) == [
            "bolt b1 has every unit merged, and lands only once u0 has been in a batch the user has answered"]
        assert plan.batch_due(due(1), [], EVERY_5, START, [("b1", False, ["u0"]), ("b2", True, [])]) == []


class TestCards:
    UNITS = [(f"u{i}", "swb-1", "aaaa") for i in range(7)]

    def test_a_batch_is_one_card_holding_every_unit(self):
        assert plan.batch_cards(6, self.UNITS, []) == [("batch/6", self.UNITS)]

    def test_a_batch_posted_as_cards_of_five_before_keeps_a_card_for_each_posted(self):
        assert plan.batch_cards(5, self.UNITS, ["batch/5-2", "batch/5-1", "batch/6"]) == [
            ("batch/5-1", self.UNITS[:5]), ("batch/5-2", self.UNITS[5:])]


SUMMARY = """# Batch 3 of wldn

## x1 (swb-1)

The tenant's zone is its own: a tenant gets a hosted zone,
and its records go there.

**The decisions it took**: one zone per tenant.

## x10 (swb-1)
### Its risks
None named.

**z1** (atl-1)
The atlas loads its maps once. The user sees them sooner.
"""
UNITS = [("x1", "swb-1", "aaa1"), ("x10", "swb-1", "bbb1"), ("z1", "atl-1", "ccc1")]
OWNER = "wldn-planner"


class TestBatchFacts:
    def test_a_units_paragraph_is_the_first_under_the_heading_naming_it_and_none_when_its_section_opens_with_none(self):
        assert plan.summary_paragraph(SUMMARY, "x1") == "The tenant's zone is its own: a tenant gets a hosted zone,\nand its records go there."
        assert plan.summary_paragraph(SUMMARY, "z1") == "The atlas loads its maps once. The user sees them sooner."
        assert plan.summary_paragraph(SUMMARY, "x10") is None
        assert plan.summary_paragraph(SUMMARY, "y1") is None

    def test_a_unit_is_about_its_bolts_goal_in_its_own_words(self):
        p = plan.Plan("%rec: Bolt\n\nBolt: b1\nGoal: The deployer holds at a failure.\n\nBolt: b2\nGoal: AWS accounts are named.\n\n"
                      "%rec: Unit\n\nUnit: x1\nBolt: b1\n\nUnit: y1\nBolt: b2\n\nUnit: q1\n\n")
        assert plan.batch_subjects(p) == {"x1": "the deployer holds at a failure", "y1": "AWS accounts are named"}
        assert plan.batch_subjects(None) == {}

    def test_the_summary_delivered_gives_every_unit_in_the_batchs_order_with_its_team_commit_subject_and_paragraph(self):
        entries = [reviewed(2, [("w1", "swb-2", "ddd1")], 0), reviewed(3, UNITS, 10)]
        f = plan.batch_facts(3, entries, SUMMARY, {"x1": "the tenant's zone is its own"})
        assert (f["n"], f["previous"], f["link"]) == (3, 2, None)
        assert [(u["unit"], u["team"], u["commit"], u["subject"]) for u in f["units"]] == [
            ("x1", "swb-1", "aaa1", "the tenant's zone is its own"), ("x10", "swb-1", "bbb1", "x10"), ("z1", "atl-1", "ccc1", "z1")]
        assert f["units"][1]["paragraph"] == "The reviewer's summary has no section for x10."
        assert plan.batch_facts(1, [reviewed(1, UNITS)], SUMMARY, {})["previous"] is None

    def test_no_card_is_raised_before_the_summary_is_there_or_for_a_batch_the_record_does_not_hold(self):
        assert plan.batch_facts(3, [reviewed(3, UNITS)], None, {}) is None
        assert plan.batch_facts(4, [reviewed(3, UNITS)], SUMMARY, {}) is None
        assert plan.batch_facts(3, [dict(reviewed(3, UNITS), Refused="x")], SUMMARY, {}) is None

    def test_a_closed_card_ends_the_batchs_point_and_one_held_open_does_not_since_it_may_be_lost(self):
        posted = {"Act": "card.post", "Key": "batch/3", "By": OWNER, "Card": "req_b3", "On": ["batch/3"]}
        assert plan.batch_facts(3, [reviewed(3, UNITS), posted], SUMMARY, {})["n"] == 3
        closed = {"Act": "card.close", "Key": "batch/3", "By": OWNER, "Card": "req_b3", "On": ["batch/3"]}
        assert plan.batch_facts(3, [reviewed(3, UNITS), posted, closed], SUMMARY, {}) is None
        refused = dict(closed, Refused="Pending You refused the close: x")
        assert plan.batch_facts(3, [reviewed(3, UNITS), posted, refused], SUMMARY, {})["n"] == 3
        assert plan.batch_facts(3, [reviewed(3, UNITS), posted, dict(closed, State="lost")], SUMMARY, {})["n"] == 3
        again = dict(posted, Card="req_9")
        assert plan.batch_facts(3, [reviewed(3, UNITS), posted, closed, again, dict(closed, Card="req_9", State="lost")], SUMMARY, {})["n"] == 3

    def test_no_card_is_raised_for_a_batch_that_waits_on_nothing(self):
        """review-batches: crew review --wait raises no card for a batch whose every unit has landed."""
        held = [reviewed(3, UNITS), {"Act": "bolt.land", "On": ["bolt/b1"] + [f"unit/{u}" for u, *_ in UNITS[:2]]}]
        assert plan.batch_facts(3, held, SUMMARY, {})["n"] == 3
        held[1]["On"].append("unit/z1")
        assert plan.batch_facts(3, held, SUMMARY, {}) is None


@pytest.mark.parametrize("stage, fix, then", [
    ("construct", False, ["batch"]),
    ("construct", True, []),
    ("code", False, []),
    ("verify", False, []),
    ("merge", False, ["landing", "batch", "tidy"]),
    ("merge", True, ["landing", "batch", "tidy"]),
])
def test_a_merge_reckons_a_batch_as_a_construct_does(stage, fix, then):
    """A wait's end reckons a batch after a construct's change and after a merge (briefs.12): a bolt whose last unit
    merged leaves its conductor waiting on nothing, so no later wait would tell the planner its batch is due at once, as
    on 2026-10-19, when every-deploy-has-its-live-card and swc-1's bolt sat merged two hours with no batch begun; and
    a merge's end removes its place and branch as it lands, for the same reason (teams.1, plan.9)."""
    assert plan.after_delivery(stage, fix) == then


def test_the_rails_sweep_reckons_a_batch_for_the_teams_on_its_host():
    """The rail's sweep reckons each partition's batch for its teams on this host holding a bolt, in the plan's order
    (briefs.12), so a bolt whose units have all merged reaches the planner with no conductor waiting; a team elsewhere,
    and a partition whose plan was not read, are not reckoned here."""
    teams = {"swb-1": {"machine": "mac-studio"}, "swb-2": {"machine": "chuck-herdr-alpha"}}
    found = [("wldn", None, None, PLAN), ("swancloud", None, None, None)]
    assert plan.batch_reckoners(found, teams, "mac-studio") == {"wldn": ["swb-1"]}
    assert plan.batch_reckoners(found, teams, "chuck-herdr-alpha") == {"wldn": ["swb-2"]}
    assert plan.batch_reckoners(found, teams, "deneb") == {}
