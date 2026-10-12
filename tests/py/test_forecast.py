"""Conflicts forecast and amendments reaching a unit (teams.12, teams.13, teams.14, plan.13): plan.forecasts_due for
what a conductor's wait forecasts, a dependent from the head its place took (plan.took_heads), plan.reach_way for how
a forecast or an amendment reaches the later unit, plan.amended_afters for each After unit constructed again since its
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
        got = plan.forecasts_due([("a", A, []), ("b", B, [])], "t", BOLT, lambda o, h, base: None if o == BOLT else ["x"],
                                 set(), {})
        assert got == ([("b", "a", ["x"], f"b@{B[:7]} a@{A[:7]}", True)], [("a", "bolt/t"), ("b", "bolt/t")])

    def test_units_clean_with_each_other_have_none(self):
        assert due([("a", A, []), ("b", B, []), ("c", C, [])]) == ([], [])


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
        assert got == ([("b", "a", ["shared.txt"], f"b@{B[:7]} a@{A[:7]}", False)], [])

    def test_one_with_no_took_is_compared_from_their_merge_base_as_before(self):
        got, asked = self.due(lambda base: ["openspec/changes/a/design.md"] if base is None else [], took={})
        assert got == ([("b", "a", ["openspec/changes/a/design.md"], f"b@{B[:7]} a@{A[:7]}", False)], [])
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
