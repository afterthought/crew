"""Conflicts forecast and amendments reaching a unit (teams.12, teams.13, teams.14, plan.13): plan.forecasts_due for
what a conductor's wait forecasts, a dependent from the head its place took (plan.took_heads), plan.forecast_orders for
which pairs a settle orders and which of crew's own orders it lifts, plan.reach_way for how
a forecast or an amendment reaches the later unit, plan.verified for whether it waits to merge, plan.amended_afters for each After unit constructed again since its
dependent took its head, plan.waiting_for for what the unit's next prompt carries, plan.rebase_waits for a dependent
whose After unit merged and plan.rebase_leaves_out for what its rebase leaves out, and plan.forecast_words and
amendment_words for what it is told; and a bolt against its kit's main (teams.21), plan.bolt_forecast_read for sluice's
answer, plan.bolt_forecast for what it tells the conductor once and plan.unread_said for a forecast sluice can't give,
plan.main_conflict for the conflict with main the record holds at the bolt's head, plan.bolt_said for what the wait does
with sluice's forecast, the kit's landings card raised for a conflict with what main landed,
with plan.forecast_way for a legacy bolt forecast from a place on it (plan.19) and plan.place_checked for what that came to,
and plan.bolt_check's bound on sluice's forecast, plan.FORECAST_BOUND.
That git merge-tree forecasts a conflict and moves no ref, and how a dependent's
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

    def test_a_pair_git_cannot_read_is_neither_ordered_nor_lifted(self):
        assert self.orders([self.forecast(1), self.settle(2)], held=None)[0] == ([], [])
        assert self.orders([self.wrote(1, before=True), self.forecast(1), self.settle(2, "short")], after=["a"], held=None)[0] == ([], [])

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

    def test_a_unit_in_conflict_with_a_bolt_on_github_is_told_to_fetch_it_and_rebase_onto_githubs_copy(self):
        """plan.19: a bolt on GitHub is read at origin/bolt/<bolt>, never at the host's copy, sluice's."""
        assert plan.rebase_words("t", at="origin/bolt/t") == (
            "Rebase your place onto the bolt (git fetch origin && git rebase origin/bolt/t)")
        assert plan.rebase_words("t", ["a@1111111"], "origin/bolt/t") == (
            "Rebase your place onto the bolt, leaving out a's work as your place took it, which the bolt holds as merged "
            "(git fetch origin && git rebase --onto origin/bolt/t $(git commit-tree -p origin/bolt/t -p 1111111 -m upstream "
            "'origin/bolt/t^{tree}'))")
        assert plan.rebase_words("t", at="bolt/t") == plan.rebase_words("t") == "Rebase your place onto the bolt (git rebase bolt/t)"

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


class TestBoltAgainstMain:
    """sluice's forecast of the bolt against main on each conductor's wait (teams.21, sluice's ADR 0039)."""
    H, M = "1" * 40, "2" * 40
    CLEAR = '{"conflict": null, "head": "%s", "onto": "%s", "ahead": []}' % ("1" * 40, "2" * 40)
    LANDED = ('{"conflict": {"paths": ["docs/builds.md"], "with": []}, "head": "%s", "onto": "%s", "ahead": [217]}'
              % ("1" * 40, "2" * 40))
    QUEUED = ('{"conflict": {"paths": ["docs/builds.md", "docs/identity.md"], "with": [{"id": 217, "from": {"agent": '
              '"wldn-design", "worktree": "design/runner-credential"}}]}, "head": "%s", "onto": "%s", "ahead": [217]}'
              % ("1" * 40, "2" * 40))

    def read(self, code, out, err=""):
        return plan.bolt_forecast_read(code, out, err)

    def told(self, out, code=2, done=()):
        doc, why = self.read(code, out)
        assert why is None
        return plan.bolt_forecast("swb-1", "wldn", "tenant-environments", doc, set(done))

    def test_a_bolt_that_merges_cleanly_is_told_nothing(self):
        assert self.told(self.CLEAR, code=0) is None

    def test_a_conflict_with_what_main_landed_is_taken_in_now_by_a_fix(self):
        heads, paths, words = self.told(self.LANDED)
        assert heads == f"bolt/tenant-environments@{self.H[:7]} main@{self.M[:7]}"
        assert paths == ["docs/builds.md"]
        assert words == (
            "bolt/tenant-environments is forecast to conflict with main on docs/builds.md: main has landed work on them "
            "since the bolt took it. Take main into the bolt now, while the conflict is small, by a fix as when wldn-ops "
            f'says a landing conflicts: crew fix swb-1 take-main-{self.M[:7]} "Take main into the bolt: it is forecast to '
            'conflict on docs/builds.md"')

    def test_while_the_team_holds_two_bolts_the_fix_names_the_bolt_forecast(self):
        """A team may hold a bolt that waits to land beside the one it builds (teams.16)."""
        doc, _ = self.read(2, self.LANDED)
        _, _, words = plan.bolt_forecast("swb-1", "wldn", "tenant-environments", doc, set(), two=True)
        assert words.endswith('conflict on docs/builds.md" --bolt tenant-environments')

    def test_a_conflict_with_a_submission_queued_on_main_is_waited_out(self):
        heads, paths, words = self.told(self.QUEUED)
        assert heads == f"bolt/tenant-environments@{self.H[:7]} main@{self.M[:7]} #217"
        assert words == (
            "bolt/tenant-environments is forecast to conflict on docs/builds.md, docs/identity.md with #217 "
            "(design/runner-credential), queued on main ahead of it. Take nothing in for it: it may yet fail and leave "
            "the queue, and crew forecasts the bolt again when main or its queue moves.")

    def test_the_same_forecast_is_told_once(self):
        heads, _, _ = self.told(self.LANDED)
        assert self.told(self.LANDED, done=[heads]) is None

    def test_main_moving_tells_it_again(self):
        heads, _, _ = self.told(self.LANDED)
        moved = self.LANDED.replace(self.M, "3" * 40)
        assert self.told(moved, done=[heads])[0] == f"bolt/tenant-environments@{self.H[:7]} main@3333333"

    def test_a_refusal_is_said_with_sluices_words(self):
        assert self.read(2, '{"error": {"kind": "refused", "message": "no branch bolt/x to forecast", "next": []}}') == (
            None, "it exited 2: no branch bolt/x to forecast")

    def test_a_sluice_without_head_is_named(self):
        assert self.read(2, "", "error: unexpected argument '--head' found\n") == (
            None, "this host's sluice can't forecast a branch no worktree holds (sluice submit --check --head), which a "
                  "newer sluice can")

    def test_an_answer_with_an_absent_field_is_not_read(self):
        # read.2: no head or revision of main becomes text.
        assert self.read(2, '{"conflict": {"paths": ["a"], "with": []}}') == (
            None, "its answer names no head or no revision of main")
        assert self.read(2, '{"conflict": {"with": []}, "head": "h", "onto": "o"}') == (None, "its conflict names no paths")
        assert self.read(1, "", "") == (None, "it exited 1")
        assert self.read(None, "", "this host has no sluice on its path") == (None, "this host has no sluice on its path")

    def test_a_forecast_sluice_cant_give_is_said_once_for_the_bolts_head(self):
        assert plan.unread_said("t", self.H, "it exited 1", set()) == (
            f"bolt/t@{self.H[:7]}", "no forecast of bolt/t against main: it exited 1")
        assert plan.unread_said("t", self.H, "it exited 1", {f"bolt/t@{self.H[:7]}"}) is None
        assert plan.unread_said("t", None, "it exited 1", set()) == (None, "no forecast of bolt/t against main: it exited 1")


class TestWaitChangesTheCard:
    """bolt-teams "A wait's forecast conflict with main changes the kit's landings card": plan.bolt_said, with the run
    record's write and the card's raise stood in for."""
    LANDED, QUEUED = TestBoltAgainstMain.LANDED, TestBoltAgainstMain.QUEUED
    T = {"name": "swb-1", "label": "wldn", "kit": {"name": "switchboard-kit"}}

    def said(self, monkeypatch, out, done=()):
        import record
        emitted, handed, words = [], [], []
        monkeypatch.setattr(record, "emit", lambda label, act, on, **f: emitted.append((label, act, on, f)))
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None, pane=None: handed.append((label, kit, note)))
        b = plan.Plan("%rec: Bolt\n\nBolt: tenant-environments\nRepo: switchboard-kit\nTeam: swb-1\n\n%rec: Unit\n\n").bolt("tenant-environments")
        plan.bolt_said({}, self.T, b, plan.bolt_forecast_read(2, out, "")[0], set(done), False, words.append)
        return emitted, handed, words

    def test_a_conflict_with_what_main_landed_raises_the_kits_card_at_once(self, monkeypatch):
        emitted, handed, words = self.said(monkeypatch, self.LANDED)
        assert [(a, f["Reached"]) for _, a, _, f in emitted] == [("forecast", "wait")]
        assert handed == [("wldn", "switchboard-kit", None)] and len(words) == 1

    def test_one_with_a_submission_queued_on_main_raises_nothing(self, monkeypatch):
        emitted, handed, _ = self.said(monkeypatch, self.QUEUED)
        assert emitted and handed == []

    def test_one_said_already_raises_nothing_again(self, monkeypatch):
        emitted, handed, words = self.said(monkeypatch, self.LANDED, done=["bolt/tenant-environments@1111111 main@2222222"])
        assert (emitted, handed, words) == ([], [], [])


class TestALeftBolt:
    """bolt-teams "A bolt the user left" and "Ticked at the same heads": a conductor's wait says a left bolt's conflict
    with main once, gives no fix and records it as found while left; once the user ticks it, the wait gives the fix
    for the same heads (plan.bolt_forecast, plan.bolt_said, plan.said_heads)."""
    LANDED, QUEUED, H, M = TestBoltAgainstMain.LANDED, TestBoltAgainstMain.QUEUED, TestBoltAgainstMain.H, TestBoltAgainstMain.M
    T = TestWaitChangesTheCard.T
    HEADS = f"bolt/tenant-environments@{'1' * 7} main@{'2' * 7}"

    def said(self, monkeypatch, out, done=(), left=True):
        import record
        emitted, handed, words = [], [], []
        monkeypatch.setattr(record, "emit", lambda label, act, on, **f: emitted.append(dict(f, Act=act, On=on)))
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None, pane=None: handed.append((label, kit, note)))
        b = plan.Plan("%rec: Bolt\n\nBolt: tenant-environments\nRepo: switchboard-kit\nTeam: swb-1\n\n%rec: Unit\n\n").bolt("tenant-environments")
        plan.bolt_said({}, self.T, b, plan.bolt_forecast_read(2, out, "")[0], set(done), False, words.append, left)
        return emitted, handed, words

    def test_a_left_bolts_conflict_with_what_main_landed_gives_no_fix_and_is_recorded_as_found_while_left(self, monkeypatch):
        emitted, handed, words = self.said(monkeypatch, self.LANDED)
        assert words == ["bolt/tenant-environments, which the user left on its kit's landings card, is forecast to conflict "
                         "with main on docs/builds.md. Take nothing in while it is left: crew tells you the take-main fix once "
                         "they tick it."]
        assert "crew fix" not in words[0]
        assert [(e["Act"], e["Heads"], e["Paths"], e["Reached"]) for e in emitted] == [
            ("forecast", self.HEADS, "docs/builds.md", "left")]
        assert handed == [("wldn", "switchboard-kit", "tenant-environments, which you left, would take main first: forecast "
                                                      "to conflict with main on docs/builds.md at 2222222")]

    def test_it_is_said_once_while_it_is_left(self, monkeypatch):
        recorded = [dict(Act="forecast", On=["bolt/tenant-environments"], Heads=self.HEADS, Paths="docs/builds.md", Reached="left")]
        assert self.said(monkeypatch, self.LANDED, plan.said_heads(recorded, {"tenant-environments"})) == ([], [], [])

    def test_ticked_at_the_same_heads_the_wait_gives_the_fix(self, monkeypatch):
        recorded = [dict(Act="forecast", On=["bolt/tenant-environments"], Heads=self.HEADS, Paths="docs/builds.md", Reached="left")]
        emitted, handed, words = self.said(monkeypatch, self.LANDED, plan.said_heads(recorded, set()), left=False)
        assert 'crew fix swb-1 take-main-2222222 "Take main into the bolt' in words[0]
        assert [e["Reached"] for e in emitted] == ["wait"] and handed == [("wldn", "switchboard-kit", None)]

    def test_unless_the_cards_raise_told_it_at_those_heads(self, monkeypatch):
        told = [dict(Act="forecast", On=["bolt/tenant-environments"], Heads=self.HEADS, Paths="docs/builds.md", Reached="told")]
        assert self.said(monkeypatch, self.LANDED, plan.said_heads(told, set()), left=False) == ([], [], [])

    def test_a_conflict_with_a_submission_queued_on_main_reads_as_today(self, monkeypatch):
        emitted, handed, words = self.said(monkeypatch, self.QUEUED)
        assert words[0].endswith("Take nothing in for it: it may yet fail and leave the queue, and crew forecasts the bolt "
                                 "again when main or its queue moves.")
        assert [e["Reached"] for e in emitted] == ["wait"] and handed == []

    def test_what_was_said_counts_a_forecast_found_while_left_only_while_the_bolt_is_still_left(self):
        entries = [dict(Act="forecast", On=["bolt/t"], Heads="bolt/t@1111111 main@2222222", Reached="left"),
                   dict(Act="forecast", On=["bolt/s"], Heads="bolt/s@1111111 main@2222222", Reached="wait"),
                   dict(Act="amendment", On=["unit/a", "unit/b"], Heads="a b@3333333", Reached="prompt"),
                   dict(Act="forecast", On=["bolt/r"], Heads="bolt/r@1111111", Reached="wait", Refused="no")]
        assert plan.said_heads(entries, {"t"}) == {"bolt/t@1111111 main@2222222", "bolt/s@1111111 main@2222222", "a b@3333333"}
        assert plan.said_heads(entries, ()) == {"bolt/s@1111111 main@2222222", "a b@3333333"}


class TestMainConflict:
    """What the run record holds of a bolt's conflict with main at its present head (rail-cards "A row forecast to
    conflict with main takes main first"), as a conductor's wait or a landings card's raise recorded it."""
    H, OLD = "1" * 40, "9" * 40

    def entry(self, heads, paths="docs/builds.md", on=("bolt/t",), **more):
        return dict(Act="forecast", On=list(on), Heads=heads, **({"Paths": paths} if paths else {}), **more)

    def test_a_waits_forecast_at_the_present_head_is_read(self):
        got = plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]} main@2222222", Reached="wait")], "t", self.H)
        assert got == ("2222222", ["docs/builds.md"])

    def test_a_raises_forecast_is_read_the_same_way_the_latest_first(self):
        entries = [self.entry(f"bolt/t@{self.H[:7]} main@2222222", Reached="wait"),
                   self.entry(f"bolt/t@{self.H[:7]} main@3333333", "README.md docs/builds.md", Reached="told")]
        assert plan.main_conflict(entries, "t", self.H) == ("3333333", ["README.md", "docs/builds.md"])

    def test_one_at_a_head_the_bolt_has_moved_from_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.OLD[:7]} main@2222222")], "t", self.H) is None

    def test_one_met_only_queued_on_main_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]} main@2222222 #7")], "t", self.H) is None

    def test_the_form_a_wait_records_when_sluice_could_not_forecast_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]}", paths=None)], "t", self.H) is None

    def test_a_units_forecast_against_the_bolt_another_bolts_and_a_refused_one_hold_nothing(self):
        heads = f"bolt/t@{self.H[:7]} main@2222222"
        assert plan.main_conflict([self.entry(f"u@aaaaaaa bolt/t@{self.H[:7]}", on=("unit/u", "bolt/t")),
                                   self.entry(heads.replace("bolt/t@", "bolt/s@"), on=("bolt/s",)),
                                   self.entry(heads, Refused="no")], "t", self.H) is None
        assert plan.main_conflict([self.entry(heads)], "t", None) is None


class TestLegacyBolt:
    """A legacy bolt, kept in the host's own refs, whose tip names a remote that holds no branch of it, is forecast from
    a place on it, never by its branch name, until it lands (plan.19): sluice reads a branch by its name where the
    policy at its tip routes it, and refuses such a bolt as having no branch."""
    TIP, H, M = "9" * 40, "1" * 40, "2" * 40
    ORIGIN = '[branches."bolt/*"]\nremote = "origin"\nrequired = ["#check-full"]\n'
    LOCAL = '[branches."bolt/*"]\nrequired = ["#check-full"]\n'

    def way(self, policy, tracked="", tip=TIP, bolt="t"):
        import base64
        at = "-" if policy is None else base64.b64encode(policy.encode()).decode()
        return plan.forecast_way(bolt, f"TIP={tip}\nAT_TIP={at}\nTRACKED={tracked}\n")

    def test_a_legacy_bolt_whose_tip_names_origin_is_forecast_from_a_place_on_it(self):
        assert self.way(self.ORIGIN) == ("place", None)
        assert self.way(self.ORIGIN, tracked="upstream ") == ("place", None)

    def test_a_bolt_its_remote_holds_is_forecast_by_its_branch_name(self):
        # Once its landing has pushed it there, or a bolt on GitHub the host also keeps a branch of.
        assert self.way(self.ORIGIN, tracked="origin ") == ("branch", None)

    def test_a_bolt_whose_tip_names_no_remote_is_forecast_by_its_branch_name(self):
        assert self.way(self.LOCAL) == ("branch", None)
        assert self.way(None) == ("branch", None)
        exact = '[branches."bolt/t"]\nrequired = []\n\n' + self.ORIGIN  # the most specific table decides, as sluice's
        assert self.way(exact) == ("branch", None)
        assert self.way(exact, bolt="u")[0] == "place"

    def test_a_bolt_with_no_branch_on_the_host_is_forecast_by_its_branch_name(self):
        assert self.way(self.ORIGIN, tip="-") == ("branch", None)

    def test_what_crew_cant_read_is_said_and_forecasts_nothing(self):
        # read.1, read.2: no way is guessed.
        assert plan.forecast_way("t", "TIP=-\n") == (None, "crew can't read where bolt/t's tip routes it from: TIP=-")
        way, why = self.way("not = [toml")
        assert way is None and why.startswith(".config/sluice.toml at bolt/t is not TOML, so crew can't read where sluice keeps bolt/t:"), why
        way, why = plan.forecast_way("t", f"TIP={self.TIP}\nAT_TIP=*\nTRACKED=\n")
        assert way is None and why.startswith("crew can't read bolt/t's .config/sluice.toml as it was sent:"), why

    def placed(self, said, err=""):
        return plan.place_checked("t", said, err)

    def test_sluices_answer_from_the_place_is_read_as_its_answer_by_name(self):
        import base64
        doc = '{"conflict": {"paths": ["docs/builds.md"], "with": []}, "head": "%s", "onto": "%s", "ahead": []}' % (self.H, self.M)
        said = f"PLACE=/k/places/forecast-t\nRC=2\nSAID={base64.b64encode(doc.encode()).decode()}\n"
        checked, kept = self.placed(said, "sluice's own words\n")
        assert checked == (2, doc, "sluice's own words\n") and kept is None
        assert plan.bolt_forecast_read(*checked)[0]["conflict"]["paths"] == ["docs/builds.md"]

    def test_crews_place_git_could_not_remove_is_named(self):
        said = "PLACE=/k/places/forecast-t\nRC=0\nSAID=\nKEPT=/k/places/forecast-t\nWHY=fatal: it is locked\n"
        checked, kept = self.placed(said)
        assert checked == (0, "", "")
        assert kept == ("/k/places/forecast-t is kept on bolt/t, git refusing to remove it: fatal: it is locked. crew removes "
                        "it at the next forecast; while it stands, the bolt's landing cannot make its worktree")

    def test_no_place_and_no_sluice_are_said_and_forecast_nothing(self):
        assert self.placed("PLACE=-\nWHY=fatal: '/k/places/forecast-t' already exists\n") == (
            (None, "", "no place on bolt/t could be made to forecast it from: fatal: '/k/places/forecast-t' already exists"), None)
        assert self.placed("NOSLUICE=yes\n") == ((None, "", "this host has no sluice on its path"), None)
        assert self.placed("PLACE=/k/places/forecast-t\n") == (
            (None, "", "crew can't read what the forecast from a place on bolt/t came to: PLACE=/k/places/forecast-t"), None)


class TestForecastBound:
    """The time a conductor's wait gives sluice's forecast of a bolt against main follows what the call does, a fetch
    from the remote, so a minute and not a wait's POLL (plan.FORECAST_BOUND; swancloud-design, 2026-10-29, on deneb's
    slow bursts of 2026-10-28, when the check ran 10 to 24 seconds): one as slow as those is read, by the bolt's branch
    name or from a place on it, and one that runs out is said and recorded as unread, never as no conflict (read.1).
    plan.bolt_check with sluice, and the script that runs it from a place, standing for processes that answer after
    so many seconds, the read of the bolt's tip answering at once."""
    H, M, LANDED = TestBoltAgainstMain.H, TestBoltAgainstMain.M, TestBoltAgainstMain.LANDED

    def checked(self, monkeypatch, took, policy=None):
        import base64
        import subprocess

        def run(args, timeout=None, **kw):
            if (args[0] == "sluice" or plan.FORECAST_PLACE in args) and took > timeout:
                raise subprocess.TimeoutExpired(args, timeout)
            if args[0] == "sluice":
                return subprocess.CompletedProcess(args, 2, self.LANDED, "")
            if plan.FORECAST_PLACE in args:
                said = base64.b64encode(self.LANDED.encode()).decode()
                return subprocess.CompletedProcess(args, 0, f"PLACE=/k/places/forecast-t\nRC=2\nSAID={said}\n", "")
            tip, at = ("-", "-") if policy is None else ("9" * 40, base64.b64encode(policy.encode()).decode())
            return subprocess.CompletedProcess(args, 0, f"TIP={tip}\nAT_TIP={at}\nTRACKED=\n", "")
        monkeypatch.setattr(plan.subprocess, "run", run)
        checked, kept = plan.bolt_check({"main": "/k/main", "dir": "/k"}, "t")
        assert kept is None
        return plan.bolt_forecast_read(*checked)

    def test_a_check_that_outruns_a_waits_poll_is_read_by_the_bolts_branch_name(self, monkeypatch):
        doc, why = self.checked(monkeypatch, took=24)
        assert why is None and doc["conflict"]["paths"] == ["docs/builds.md"]

    def test_and_from_a_place_on_a_legacy_bolt(self, monkeypatch):
        doc, why = self.checked(monkeypatch, took=24, policy=TestLegacyBolt.ORIGIN)
        assert why is None and doc["conflict"]["paths"] == ["docs/builds.md"]

    @pytest.mark.parametrize("policy", [None, TestLegacyBolt.ORIGIN], ids=["by-name", "from-a-place"])
    def test_one_that_runs_out_is_recorded_unread_never_as_no_conflict(self, monkeypatch, policy):
        doc, why = self.checked(monkeypatch, took=plan.FORECAST_BOUND + 1, policy=policy)
        assert (doc, why) == (None, "it did not answer within 60 seconds")
        heads, words = plan.unread_said("t", self.H, why, set())
        assert words == "no forecast of bolt/t against main: it did not answer within 60 seconds"
        # Recorded as the wait records it (reach), it names no paths: a conflict recorded at the bolt's head stands,
        # and the next forecast sluice gives at that head is still told.
        unread = dict(Act="forecast", On=["bolt/t"], Heads=heads, Reached="wait")
        found = dict(Act="forecast", On=["bolt/t"], Heads=f"bolt/t@{self.H[:7]} main@{self.M[:7]}", Paths="docs/builds.md",
                     Reached="wait")
        assert plan.main_conflict([found, unread], "t", self.H) == (self.M[:7], ["docs/builds.md"])
        later, _ = plan.bolt_forecast_read(2, self.LANDED, "")
        assert plan.bolt_forecast("swb-1", "wldn", "t", later, plan.said_heads([unread]))[1] == ["docs/builds.md"]
