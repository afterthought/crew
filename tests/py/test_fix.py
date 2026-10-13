"""A fix (teams.3, teams.5, plan.8, teams.15): plan.fix_in_slot for what crew fix <name> acts on, plan.leftover and
plan.own_place for a fix refused its place, plan.bolt_held for the bolt a fix is of, and crew.never_started for a
fix's or unit's stage whose prompt was never taken. A fix merges as a unit does, by a submission to sluice (teams.5);
the fix's place and stage through the command are the journey's (t-journey-fix)."""
import pytest

from facts import plan_of

import crew
import plan

KD = "/kit"


class TestWhich:
    def test_a_new_fix_gets_a_branch_and_place_of_its_bolt(self):
        assert plan.fix_in_slot([], "tenant-environments", "edge-sign-in", KD) == (
            None, "fix/tenant-environments/edge-sign-in", "/kit/places/fix-tenant-environments--edge-sign-in")

    def test_two_teams_fixes_of_one_name_are_each_their_own_bolts(self):
        assert plan.fix_in_slot([], "console-pages", "bolt-takes-main", KD)[1:] == (
            "fix/console-pages/bolt-takes-main", "/kit/places/fix-console-pages--bolt-takes-main")

    def test_a_fix_in_flight_keeps_what_its_slot_recorded(self):
        held = [["unit-1", "fix", "fix/t/edge", "/kit/places/fix-t--edge"], ["unit-2", "fix", "fix/old-sign-in", "/kit/places/fix-old-sign-in"]]
        assert plan.fix_in_slot(held, "t", "edge", KD) == ("unit-1", "fix/t/edge", "/kit/places/fix-t--edge")
        assert plan.fix_in_slot(held, "t", "old-sign-in", KD) == ("unit-2", "fix/old-sign-in", "/kit/places/fix-old-sign-in")

    def test_the_fix_of_its_bolt_comes_before_one_named_before_fixes_held_their_bolt(self):
        held = [["unit-2", "fix", "fix/x", "/kit/places/fix-x"], ["unit-1", "fix", "fix/t/x", "/kit/places/fix-t--x"]]
        assert plan.fix_in_slot(held, "t", "x", KD)[0] == "unit-1"

    def test_a_fix_is_named_as_crew_names_things(self):
        assert crew.NAME.match("edge-sign-in") and not crew.NAME.match("Edge_Sign")

    def test_a_team_holding_no_bolt_has_no_fix(self):
        assert plan.bolt_held(plan_of({"t": "swb-1"}), "swb-1") == "t"
        with pytest.raises(plan.Refusal, match="swb-2 holds no bolt: crew bolt give swb-2"):
            plan.bolt_held(plan_of({"t": "swb-1"}), "swb-2")


class TestPlace:
    def test_a_new_fixs_branch_or_place_already_there_is_not_taken_over(self):
        assert plan.leftover("fix/t/stray", "/kit/places/fix-t--stray", "swb-1", True, False) == (
            "fix/t/stray already has a place at /kit/places/fix-t--stray that no slot of swb-1 holds: name this fix differently")
        assert plan.leftover("fix/t/leftover", "/kit/places/fix-t--leftover", "swb-1", False, True) == (
            "fix/t/leftover already has a branch that no slot of swb-1 holds, though no place at /kit/places/fix-t--leftover: "
            "name this fix differently")
        assert plan.leftover("fix/t/new", "/p", "swb-1", False, False) is None

    def test_a_place_on_its_own_branch_from_the_bolt_is_its_own_mid_rebase_too(self):
        assert plan.own_place("/p", "fix/t/x", "bolt/t", "fix/t/x", "bolt/t") is None

    @pytest.mark.parametrize("on, up, said", [
        ("elsewhere", "", "/p is on elsewhere, made from no bolt, not fix/t/x from bolt/t"),
        ("fix/t/x", "bolt/other", "/p is on fix/t/x, made from bolt/other, not fix/t/x from bolt/t"),
        ("", "", "/p is on no branch, made from no bolt, not fix/t/x from bolt/t")])
    def test_any_other_is_refused(self, on, up, said):
        assert plan.own_place("/p", on, up, "fix/t/x", "bolt/t") == said + ": crew starts a fix only in its own place"


class TestNeverStarted:
    @pytest.mark.parametrize("stage, what, obj, again", [
        ("code", "a", "unit/a", "crew unit run a code"),
        ("fix", "fix/t/edge", "fix/t/edge", 'crew fix swb-1 edge "<what is wrong>"'),
        ("merge", "fix/t/edge", "fix/t/edge", "crew fix swb-1 edge --merge")])
    def test_a_prompt_never_taken_names_how_to_run_the_stage_again(self, stage, what, obj, again):
        assert crew.never_started("swb-1-unit-1", stage, what, obj, "swb-1", "never", "sent twice") == (
            f"swb-1-unit-1 never took its {stage} prompt for {what}, sent twice; the stage never started and nothing is left "
            f"typed in its pane: run it again with {again}")

    def test_a_fix_whose_agent_stayed_on_a_question_was_typed_nothing(self):
        assert crew.never_started("swb-2-unit-3", "fix", "fix/c/n", "fix/c/n", "swb-2", "never", "as it was waiting on a question in its pane") == (
            "swb-2-unit-3 never took its fix prompt for fix/c/n, as it was waiting on a question in its pane; the stage never "
            'started and nothing is left typed in its pane: run it again with crew fix swb-2 n "<what is wrong>"')

    def test_one_crew_could_not_tell_was_taken_sends_nothing_more(self):
        assert crew.never_started("swb-1-unit-1", "merge", "a", "unit/a", "swb-1", "unread", "it is waiting on a question in its pane") == (
            "crew could not tell whether swb-1-unit-1 took its merge prompt for a: it is waiting on a question in its pane; "
            "nothing more was sent, and the stage is taken as never started: run it again with crew unit run a merge")
