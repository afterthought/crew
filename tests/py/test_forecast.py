"""Conflicts forecast and amendments reaching a unit (teams.12, teams.13, teams.14, plan.13): plan.forecasts_due for
what a conductor's wait forecasts, plan.reach_way for how a forecast or an amendment reaches the later unit,
plan.amended_afters for each After unit constructed again since its dependent took its head, plan.waiting_for for
what the unit's next prompt carries, plan.rebase_waits for a dependent whose After unit merged, and
plan.forecast_words and amendment_words for what it is told. That git merge-tree forecasts a conflict and moves no ref
is a contract case (tests/contract/test_git.py); the wait that tells, starts a settle or carries, the journey's."""
import pytest

from facts import at, plan_of

import plan

A, B, C, BOLT = "a" * 40, "b" * 40, "c" * 40, "f" * 40


def due(live, bolt_head=BOLT, clash=(), done=()):
    """forecasts_due over units whose heads conflict as clash says: pairs of heads, each (theirs, ours)."""
    return plan.forecasts_due(live, "t", bolt_head, lambda o, h: ["shared.txt"] if (o, h) in clash else [], set(done))


class TestDue:
    def test_two_unmerged_units_in_conflict_give_the_later_the_forecast_and_after_on_the_earlier(self):
        assert due([("a", A, []), ("b", B, [])], clash=[(A, B)]) == (
            [("b", "a", ["shared.txt"], f"b@{B[:7]} a@{A[:7]}", True)], [])

    def test_a_unit_already_after_the_other_is_not_put_after_it_again(self):
        assert due([("a", A, []), ("b", B, ["a"])], clash=[(A, B)])[0][0][4] is False

    def test_a_forecast_made_for_the_same_heads_is_not_made_again(self):
        assert due([("a", A, []), ("b", B, [])], clash=[(A, B)], done=[f"b@{B[:7]} a@{A[:7]}"]) == ([], [])

    def test_a_unit_in_conflict_with_the_bolt_resolves_that_first(self):
        assert due([("a", A, []), ("b", B, [])], clash=[(BOLT, B), (A, B)]) == (
            [("b", "bolt/t", ["shared.txt"], f"b@{B[:7]} bolt/t@{BOLT[:7]}", False)], [])
        assert due([("a", A, []), ("b", B, [])], clash=[(BOLT, B), (A, B)], done=[f"b@{B[:7]} bolt/t@{BOLT[:7]}"]) == ([], [])

    def test_what_git_cannot_read_is_named_and_the_rest_forecast(self):
        got = plan.forecasts_due([("a", A, []), ("b", B, [])], "t", BOLT, lambda o, h: None if o == BOLT else ["x"], set())
        assert got == ([("b", "a", ["x"], f"b@{B[:7]} a@{A[:7]}", True)], [("a", "bolt/t"), ("b", "bolt/t")])

    def test_units_clean_with_each_other_have_none(self):
        assert due([("a", A, []), ("b", B, []), ("c", C, [])]) == ([], [])


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
    def fc(self, eid, unit="d", reached="prompt", act="forecast"):
        return {"Act": act, "Id": eid, "On": [f"unit/{unit}", "bolt/t"], "Reached": reached}

    def test_what_reached_the_unit_by_prompt_waits_until_a_start_carries_it(self):
        entries = [self.fc("f1"), self.fc("f2", act="amendment"), self.fc("f3", reached="told"), self.fc("f4", unit="e")]
        assert [e["Id"] for e in plan.waiting_for("d", entries)] == ["f1", "f2"]
        carried = {"Act": "stage.start", "On": ["stage/d/code", "unit/d"], "Forecast": "f1 f2"}
        assert plan.waiting_for("d", entries + [carried]) == []


class TestRebase:
    def test_a_dependent_whose_agent_works_waits(self):
        assert plan.rebase_waits("c", "t", ["a"], "working", lambda: pytest.fail("a working place's state is not read"), "/p/c") == (
            "c waits to be rebased onto bolt/t, now that a merged: its agent is working")

    def test_a_dependent_whose_place_is_not_clean_waits(self):
        assert plan.rebase_waits("c", "t", ["a"], "idle", lambda: False, "/p/c") == (
            "c waits to be rebased onto bolt/t, now that a merged: /p/c has uncommitted changes or work in progress")

    def test_else_it_is_rebased(self):
        assert plan.rebase_waits("c", "t", ["a"], None, lambda: True, "/p/c") is None


class TestWords:
    T = {"kit": {"main": "/kit/main", "dir": "/kit"}}

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
