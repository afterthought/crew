"""Constructed changes reach the user in batches that span the partition (briefs.12): which changes are due
(plan.due_changes), when a batch is due and why (plan.batch_due), and a batch's cards (plan.batch_cards). The rail's
rows are test_rail's; telling the planner and the reviewer's tab, the review journey's (t-journey-review)."""
import datetime

from facts import START, constructed, plan_of, reviewed, told

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
            "bolt b1 has every unit merged, and lands only once u0 has been in a batch"]
        assert plan.batch_due(due(1), [], EVERY_5, START, [("b1", False, ["u0"]), ("b2", True, [])]) == []


class TestCards:
    UNITS = [(f"u{i}", "swb-1", "aaaa") for i in range(7)]

    def test_a_batch_is_one_card_holding_every_unit(self):
        assert plan.batch_cards(6, self.UNITS, []) == [("batch/6", self.UNITS)]

    def test_a_batch_posted_as_cards_of_five_before_keeps_a_card_for_each_posted(self):
        assert plan.batch_cards(5, self.UNITS, ["batch/5-2", "batch/5-1", "batch/6"]) == [
            ("batch/5-1", self.UNITS[:5]), ("batch/5-2", self.UNITS[5:])]
