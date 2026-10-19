"""Conflicts forecast and amendments reaching a unit (teams.12, teams.13, teams.14, plan.13): plan.forecasts_due for
what a conductor's wait forecasts, a dependent from the head its place took (plan.took_heads), plan.forecast_orders for
which pairs a settle orders and which of crew's own orders it lifts, plan.reach_way for how
a forecast or an amendment reaches the later unit, plan.verified for whether it waits to merge, plan.amended_afters for each After unit constructed again since its
dependent took its head, plan.waiting_for for what the unit's next prompt carries, plan.rebase_waits for a dependent
whose After unit merged and plan.rebase_leaves_out for what its rebase leaves out, and plan.forecast_words and
amendment_words for what it is told. That git merge-tree forecasts a conflict and moves no ref, and how a dependent's
rebase replays its commits, are contract cases (tests/contract/test_git.py); the wait that tells, starts a settle or
carries, and the rebase at a merge, the journey's."""
import pytest

from facts import at, plan_of

import plan

A, B, C, BOLT = "a" * 40, "b" * 40, "c" * 40, "f" * 40


def due(live, bolt_head=BOLT, clash=(), done=(), took=None):
    """forecasts_due over units whose heads conflict as clash says: pairs of heads, each (theirs, ours), compared from
    their merge base."""
    return plan.forecasts_due(live, "t", bolt_head, lambda o, h, base: ["shared.txt"] if (o, h) in clash and base is None else [],
                              set(done), took or {})


class TestDue:
    def test_two_unmerged_units_in_conflict_give_the_later_the_forecast_and_nothing_else(self):
        # wldn, swb-1, 2026-10-15: the forecast's own After held finished units for a proposal each (plan.13).
        assert due([("a", A, []), ("b", B, [])], clash=[(A, B)]) == (
            [("b", "a", ["shared.txt"], f"b@{B[:7]} a@{A[:7]}")], [])

    def test_a_unit_already_after_the_other_is_forecast_with_its_four_parts(self):
        assert due([("a", A, []), ("b", B, ["a"])], clash=[(A, B)]) == (
            [("b", "a", ["shared.txt"], f"b@{B[:7]} a@{A[:7]}")], [])

    def test_a_forecast_made_for_the_same_heads_is_not_made_again(self):
        assert due([("a", A, []), ("b", B, [])], clash=[(A, B)], done=[f"b@{B[:7]} a@{A[:7]}"]) == ([], [])

    def test_a_unit_in_conflict_with_the_bolt_resolves_that_first(self):
        assert due([("a", A, []), ("b", B, [])], clash=[(BOLT, B), (A, B)]) == (
            [("b", "bolt/t", ["shared.txt"], f"b@{B[:7]} bolt/t@{BOLT[:7]}")], [])
        assert due([("a", A, []), ("b", B, [])], clash=[(BOLT, B), (A, B)], done=[f"b@{B[:7]} bolt/t@{BOLT[:7]}"]) == ([], [])

    def test_what_git_cannot_read_is_named_and_the_rest_forecast(self):
        got = plan.forecasts_due([("a", A, []), ("b", B, [])], "t", BOLT, lambda o, h, base: None if o == BOLT else ["x"],
                                 set(), {})
        assert got == ([("b", "a", ["x"], f"b@{B[:7]} a@{A[:7]}")], [("a", "bolt/t"), ("b", "bolt/t")])

    def test_units_clean_with_each_other_have_none(self):
        assert due([("a", A, []), ("b", B, []), ("c", C, [])]) == ([], [])

    def test_a_dependent_listed_first_is_forecast_against_the_unit_it_comes_after_never_the_other_way(self):
        # wldn, swb-4, 2026-10-13: d comes after s and the file lists d first; s was told d was ahead (signal 51c2c852/01).
        assert due([("d", B, ["s"]), ("s", A, [])], clash=[(A, B), (B, A)]) == (
            [("d", "s", ["shared.txt"], f"d@{B[:7]} s@{A[:7]}")], [])

    def test_one_that_comes_after_at_any_depth_is_forecast_with_its_four_parts(self):
        # c comes after b, which comes after a: c is forecast against a, and a is never forecast against c.
        got = plan.forecasts_due([("c", C, ["b"]), ("a", A, [])], "t", None,
                                 lambda o, h, base: ["shared.txt"] if {o, h} == {A, C} else [], set(), {}, {"c": ["b"], "b": ["a"]})
        assert got == ([("c", "a", ["shared.txt"], f"c@{C[:7]} a@{A[:7]}")], [])


class TestOrders:
    """Which pairs crew orders and which orders of its own it lifts (plan.13, teams.12, teams.14): b, later in the bolt,
    is forecast to conflict with a, both unmerged; a settle of b that delivers holding a's work puts b after a, once
    for the pair; an order crew wrote whose settle then stopped short, b not holding a's work, is lifted; one someone
    else lifted stays lifted."""

    def forecast(self, minutes, unit="b", other="a"):
        return {"Act": "forecast", "On": [f"unit/{unit}", f"unit/{other}"], "At": at(minutes), "Id": f"f{minutes}",
                "Heads": f"{unit}@{B[:7]} {other}@{A[:7]}", "Reached": "settle"}

    def settle(self, minutes, how="delivered", unit="b"):
        return {"Act": "stage.end", "On": [f"stage/{unit}/settle", f"unit/{unit}", "agent/swb-1-unit-2"], "At": at(minutes),
                "Id": f"s{minutes}", "Ended": how, "Delivered": f"unit/{unit}@{B[:7]}" if how == "delivered" else None}

    def wrote(self, minutes, before=False, **fields):
        # before: an order a forecast wrote before this change, known by crew's own subject
        why = "plan(t): b after a, forecast to conflict" if before else (
            "plan(t): b no longer after a, its settle found nothing to change" if "Lifted" in fields else "plan(t): b after a, its settle took a's work")
        return {"Act": "unit.after", "On": ["unit/b", "bolt/t"], "At": at(minutes), "Id": f"w{minutes}", "Why": why, **fields}

    def orders(self, entries, after=(), held=False, unmerged=("a", "b")):
        asked = []

        def holds(unit, other, head):
            asked.append((unit, other, head))
            return held
        got = plan.forecast_orders({"a": [], "b": list(after)}, set(unmerged), entries, holds)
        return got, asked

    def test_a_forecast_with_no_settle_orders_nothing(self):
        assert self.orders([self.forecast(1)]) == (([], []), [])

    def test_a_settle_that_delivers_holding_the_others_work_orders_the_pair(self):
        got, asked = self.orders([self.forecast(1), self.settle(2)], held=True)
        assert got == ([("b", "a", "s2")], [])
        assert asked == [("b", "a", A[:7])]

    def test_a_second_delivered_settle_does_not_order_it_again(self):
        entries = [self.forecast(1), self.settle(2), self.wrote(3, After="a", Settle="s2"), self.forecast(4), self.settle(5)]
        assert self.orders(entries, after=["a"], held=True)[0] == ([], [])
        assert self.orders(entries, held=True)[0] == ([], [])  # lifted since by someone else: once for a pair

    def test_a_settle_that_delivered_without_holding_the_others_work_orders_nothing(self):
        assert self.orders([self.forecast(1), self.settle(2)], held=False)[0] == ([], [])

    def test_a_settle_before_any_forecast_for_the_pair_orders_nothing(self):
        assert self.orders([self.settle(1), self.forecast(2)], held=True) == (([], []), [])

    def test_a_short_settle_orders_nothing(self):
        assert self.orders([self.forecast(1), self.settle(2, "short")], held=True)[0] == ([], [])

    def test_an_order_a_forecast_wrote_whose_settle_stopped_short_is_lifted(self):
        # wldn, swb-1, 2026-10-15: proposals 346 and 347 lifted such orders, a card for the user each time.
        entries = [self.wrote(1, before=True), self.forecast(1), self.settle(2, "short")]
        assert self.orders(entries, after=["a"])[0] == ([], [("b", "a", "s2")])

    def test_one_whose_branch_holds_the_others_work_is_not_lifted(self):
        entries = [self.wrote(1, before=True), self.forecast(1), self.settle(2, "short")]
        assert self.orders(entries, after=["a"], held=True)[0] == ([], [])

    def test_one_whose_settle_has_not_ended_or_delivered_since_is_not_lifted(self):
        assert self.orders([self.wrote(1, before=True), self.forecast(1)], after=["a"]) == (([], []), [])
        entries = [self.wrote(1, before=True), self.forecast(1), self.settle(2), self.settle(3, "short")]
        assert self.orders(entries, after=["a"])[0] == ([], [])
        assert self.orders([self.wrote(1, before=True), self.forecast(1), self.settle(2, "stopped")], after=["a"])[0] == ([], [])

    def test_an_order_the_user_lifted_is_neither_written_nor_lifted_and_a_later_settle_does_not_write_it_back(self):
        # wldn, swb-1, 2026-10-15: proposal 346 lifted the order, and the next forecast on new heads wrote it back.
        entries = [self.wrote(1, before=True), self.forecast(1), self.settle(2, "short"), self.forecast(3)]
        assert self.orders(entries)[0] == ([], [])
        assert self.orders(entries + [self.settle(4)], held=True)[0] == ([], [])

    def test_crews_own_lift_followed_by_a_delivered_settle_holding_the_others_work_orders_it(self):
        entries = [self.wrote(1, before=True), self.forecast(1), self.settle(2, "short"), self.wrote(3, Lifted="a", Settle="s2")]
        assert self.orders(entries + [self.forecast(4), self.settle(5)], held=True)[0] == ([("b", "a", "s5")], [])
        assert self.orders(entries, held=True)[0] == ([], [])  # the settle before the lift decided nothing more

    def test_an_order_set_by_hand_is_never_lifted(self):
        hand = {"Act": "unit.after", "On": ["unit/b", "bolt/t"], "At": at(1), "Id": "w1", "Why": "plan(t): b after a"}
        assert self.orders([hand, self.forecast(1), self.settle(2, "short")], after=["a"]) == (([], []), [])

    def test_one_that_comes_after_the_other_through_another_unit_is_not_ordered(self):
        got = plan.forecast_orders({"a": [], "c": ["a"], "b": ["c"]}, {"a", "b", "c"}, [self.forecast(1), self.settle(2)],
                                   lambda unit, other, head: True)
        assert got == ([], [])

    def test_a_merged_other_gives_no_pair(self):
        assert self.orders([self.forecast(1), self.settle(2)], held=True, unmerged=("b",)) == (([], []), [])
        assert self.orders([self.wrote(1, before=True), self.forecast(1), self.settle(2, "short")], after=["a"], unmerged=("b",)) == (([], []), [])

    def test_a_forecast_against_the_bolt_or_an_amendment_is_no_pair(self):
        bolt = dict(self.forecast(1), On=["unit/b", "bolt/t"])
        amendment = dict(self.forecast(1), Act="amendment")
        assert self.orders([bolt, amendment, self.settle(2)], held=True) == (([], []), [])


class TestDependent:
    """A dependent b holds a's work as its place took it, a@1111111; a was since rebased onto the bolt and settled, its
    head now A. git compares the two from 1111111, what b adds beyond it, else from their merge base, where both
    change a's own files."""
    OLD = "1111111"

    def due(self, git, took=None, after=("a",)):
        asked = []

        def conflicts(o, h, base):
            asked.append((o, h, base))
            return git(base)
        got = plan.forecasts_due([("a", A, []), ("b", B, list(after))], "t", None, conflicts, set(),
                                 {"b": {"a": self.OLD}} if took is None else took)
        return got, asked

    def test_one_holding_its_after_units_old_head_is_not_forecast_on_that_units_own_files(self):
        got, asked = self.due(lambda base: [] if base == self.OLD else ["openspec/changes/a/design.md"])
        assert got == ([], [])
        assert asked == [(A, B, self.OLD)]

    def test_one_whose_own_commit_overlaps_the_after_units_rewritten_change_is(self):
        got, _ = self.due(lambda base: ["shared.txt"])
        assert got == ([("b", "a", ["shared.txt"], f"b@{B[:7]} a@{A[:7]}")], [])

    def test_one_with_no_took_is_compared_from_their_merge_base_as_before(self):
        got, asked = self.due(lambda base: ["openspec/changes/a/design.md"] if base is None else [], took={})
        assert got == ([("b", "a", ["openspec/changes/a/design.md"], f"b@{B[:7]} a@{A[:7]}")], [])
        assert asked == [(A, B, None)]

    def test_a_head_taken_of_a_unit_it_does_not_come_after_is_not_its_base(self):
        _, asked = self.due(lambda base: [], after=())
        assert asked == [(A, B, None)]


class TestTook:
    def test_the_latest_construct_start_that_took_a_head_says_it(self):
        refused = dict(start("b", 3, took="a@3333333"), Refused="all slots are in flight")
        entries = [start("b", 1, took="a@1111111 c@cccccc1"), start("b", 2), refused, start("a", 4, took="z@2222222")]
        assert plan.took_heads("b", entries) == {"a": "1111111", "c": "cccccc1"}
        assert plan.took_heads("b", entries + [start("b", 5, took="a@5555555")]) == {"a": "5555555", "c": "cccccc1"}

    def test_a_start_recorded_before_took_existed_took_none(self):
        assert plan.took_heads("b", [dict(start("b", 1), Took=None)]) == {}


class TestWay:
    def test_not_yet_while_its_stages_agent_works(self):
        assert plan.reach_way(True, "working", "code", False) is None

    @pytest.mark.parametrize("status", ["idle", "done", "blocked"])
    def test_told_to_the_agent_of_the_stage_it_owes(self, status):
        assert plan.reach_way(True, status, "code", False) == "told"

    def test_a_unit_that_delivered_its_verify_and_waits_to_merge_settles(self):
        assert plan.reach_way(False, None, "verify", True) == "settle"

    @pytest.mark.parametrize("stage, verified", [("planned", False), ("verify", False), ("code", False)])
    def test_else_its_next_stages_prompt_carries_it(self, stage, verified):
        assert plan.reach_way(False, None, stage, verified) == "prompt"


def start(unit, minutes, took="", eid=None, forecast=""):
    return {"Act": "stage.start", "On": [f"stage/{unit}/construct", f"unit/{unit}"], "At": at(minutes), "Id": eid or f"s{minutes}",
            "Took": took, "Forecast": forecast}


def end(unit, minutes, head):
    return {"Act": "stage.end", "On": [f"stage/{unit}/construct", f"unit/{unit}"], "Ended": "delivered", "At": at(minutes),
            "Id": f"e{minutes}", "Delivered": f"unit/{unit}@{head}"}


def began(stage, unit="a"):
    return {"Act": "stage.start", "On": [f"stage/{unit}/{stage}", f"unit/{unit}"]}


def ended(stage, unit="a", how="delivered"):
    return {"Act": "stage.end", "On": [f"stage/{unit}/{stage}", f"unit/{unit}"], "Ended": how}


class TestVerified:
    """A unit that has delivered its verify waits to merge, through its one round of fixes after it, so a forecast
    reaches it as a settle (teams.14, teams.17); a chore's merge reads the same."""

    def test_a_delivered_verify_stands_through_the_fix_round_after_it(self):
        assert plan.verified("wldn", "a", [began("code"), ended("code"), began("verify"), ended("verify"), began("code"), ended("code")])

    def test_construct_run_again_undoes_it(self):
        assert not plan.verified("wldn", "a", [began("verify"), ended("verify"), began("construct")])

    def test_a_verify_that_stopped_short_or_was_refused_is_none(self):
        assert not plan.verified("wldn", "a", [began("verify"), ended("verify", how="stopped")])
        assert not plan.verified("wldn", "a", [began("code"), dict(ended("verify"), Refused="x")])


class TestAmendedAfters:
    PLAN = plan_of({"t": "swb-1"}, {"a": "t", "b": "t"})

    def afters(self, entries, stage="code", holds=lambda held, head: False):
        self.PLAN.unit("b").set("After", "a")
        return plan.amended_afters(self.PLAN.bolts(), self.PLAN, lambda n: stage, entries, holds)

    def test_an_after_unit_constructed_again_since_its_dependent_took_its_head(self):
        assert self.afters([end("a", 0, "1111111"), start("b", 1, took="a@1111111"), end("a", 2, "2222222")]) == [("t", "b", "a", "2222222")]

    def test_a_construct_before_the_dependent_took_its_head_is_none(self):
        assert self.afters([start("b", 1, took="a@1111111"), end("a", 0, "1111111")]) == []

    def test_a_head_the_dependent_already_holds_is_none(self):
        assert self.afters([start("b", 1, took="a@2222222"), end("a", 2, "2222222")]) == []
        assert self.afters([start("b", 1, took="a@3333333"), end("a", 2, "2222222")], holds=lambda held, head: True) == []

    @pytest.mark.parametrize("stage", ["merged", "landed", "unknown"])
    def test_a_dependent_that_merged_or_cannot_be_read_is_reached_by_nothing(self, stage):
        assert self.afters([start("b", 1, took="a@1111111"), end("a", 2, "2222222")], stage=stage) == []


class TestCarried:
    def fc(self, eid, unit="d", reached="prompt", act="forecast", other="bolt/t"):
        return {"Act": act, "Id": eid, "On": [f"unit/{unit}", other], "Reached": reached}

    def test_what_reached_the_unit_by_prompt_waits_until_a_start_carries_it(self):
        entries = [self.fc("f1"), self.fc("f2", act="amendment", other="unit/a"), self.fc("f3", reached="told", other="unit/a"),
                   self.fc("f4", unit="e")]
        assert [e["Id"] for e in plan.waiting_for("d", entries)] == ["f1", "f2"]
        carried = {"Act": "stage.start", "On": ["stage/d/code", "unit/d"], "Forecast": "f1 f2"}
        assert plan.waiting_for("d", entries + [carried]) == []

    def test_a_forecast_against_the_bolt_is_dropped_once_a_newer_one_against_the_bolt_was_made(self):
        entries = [self.fc("f1"), self.fc("f2", other="unit/a"), self.fc("f3"), self.fc("f4", unit="e")]
        assert [e["Id"] for e in plan.waiting_for("d", entries)] == ["f2", "f3"]
        assert [e["Id"] for e in plan.waiting_for("d", entries + [self.fc("f5", reached="told")])] == ["f2"]

    def test_a_newer_forecast_against_another_unit_drops_none(self):
        entries = [self.fc("f1", other="unit/a"), self.fc("f2", act="amendment", other="unit/a"), self.fc("f3", other="unit/a")]
        assert [e["Id"] for e in plan.waiting_for("d", entries)] == ["f1", "f2", "f3"]


class TestRebase:
    def test_a_dependent_whose_agent_works_waits(self):
        assert plan.rebase_waits("c", "t", ["a"], "working", lambda: pytest.fail("a working place's state is not read"), "/p/c") == (
            "c waits to be rebased onto bolt/t, now that a merged: its agent is working")

    def test_a_dependent_whose_place_is_not_clean_waits(self):
        assert plan.rebase_waits("c", "t", ["a"], "idle", lambda: False, "/p/c") == (
            "c waits to be rebased onto bolt/t, now that a merged: /p/c has uncommitted changes or work in progress")

    def test_else_it_is_rebased(self):
        assert plan.rebase_waits("c", "t", ["a"], None, lambda: True, "/p/c") is None

    def test_a_dependent_holding_the_head_its_place_took_of_a_merged_unit_leaves_that_work_out(self):
        assert plan.rebase_leaves_out(["a"], {"a": "1111111"}, lambda head: head == "1111111") == ["a@1111111"]

    def test_one_with_no_took_is_rebased_onto_the_bolt_alone_as_before(self):
        assert plan.rebase_leaves_out(["a"], {}, lambda head: pytest.fail("nothing taken is read")) == []

    def test_a_head_it_no_longer_holds_is_not_left_out(self):
        assert plan.rebase_leaves_out(["a"], {"a": "1111111"}, lambda head: False) == []

    def test_each_merged_unit_whose_taken_head_it_holds_is_left_out_and_no_unmerged_one(self):
        took = {"a": "1111111", "c": "3333333", "d": "4444444"}
        assert plan.rebase_leaves_out(["a", "c"], took, lambda head: True) == ["a@1111111", "c@3333333"]
        assert plan.rebase_leaves_out(["a", "c"], took, lambda head: head != "1111111") == ["c@3333333"]


class TestWords:
    T = {"kit": {"main": "/kit/main", "dir": "/kit"}}

    def test_a_unit_in_conflict_with_the_bolt_is_told_to_rebase_onto_it(self):
        assert plan.rebase_words("t") == "Rebase your place onto the bolt (git rebase bolt/t)"

    def test_a_dependent_whose_rebase_left_out_its_after_units_work_is_told_the_upstream_crew_used(self):
        assert plan.rebase_words("t", ["a@1111111"]) == (
            "Rebase your place onto the bolt, leaving out a's work as your place took it, which the bolt holds as merged "
            "(git rebase --onto bolt/t $(git commit-tree -p bolt/t -p 1111111 -m upstream 'bolt/t^{tree}'))")
        assert plan.rebase_words("t", ["a@1111111", "c@3333333", "d@4444444"]) == (
            "Rebase your place onto the bolt, leaving out the work of a, c and d as your place took it, which the bolt holds "
            "as merged (git rebase --onto bolt/t $(git commit-tree -p bolt/t -p 1111111 -p 3333333 -p 4444444 -m upstream "
            "'bolt/t^{tree}'))")

    def place(self, tmp_path, unit):
        d = tmp_path / unit / "openspec" / "changes" / unit
        d.mkdir(parents=True)
        (d / "proposal.md").write_text("# Proposal\n\n## Why\n\nx\n\n## What Changes\n\n- y. And more.\n")
        return {"places": {unit: {"path": str(tmp_path / unit)}}}

    def test_the_later_unit_is_told_the_paths_how_to_keep_both_intents_and_the_others_change(self, tmp_path):
        k = self.place(tmp_path, "a")
        assert plan.forecast_words(self.T, k, "t", "b", "a", ["shared.txt"]) == (
            "Your merge after a, ahead of you in the bolt and not merged, is forecast to conflict on shared.txt. You merge "
            "after it: take its work into your place (git merge unit/a), resolve each conflict keeping both changes' intents, "
            f"run the tests those paths affect, and commit. a's change is {tmp_path}/a/openspec/changes/a/. Its Why: x What it changes: y.")

    def test_a_dependent_is_told_its_after_unit_was_constructed_again(self, tmp_path):
        k = self.place(tmp_path, "a")
        assert plan.amendment_words(self.T, k, "t", "a") == (
            "a, which you come after, was constructed again, and you are not held for it: build on its revised change, keeping "
            "yours true to it. Your place holds its work as it stood when your place was made, and is rebased onto the bolt "
            f"once it merges. a's change is {tmp_path}/a/openspec/changes/a/. Its Why: x What it changes: y.")
