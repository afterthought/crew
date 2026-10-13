"""What a team's read frees and removes (teams.1, plan.9): plan.slot_stage for the work each slot holds,
plan.tidy_over for which worktrees are crew's and whose work is over, plan.kept_why for one kept, plan.wt_refused and
plan.wt_left_branch for what the kit's wt remove said, and plan.unread_plans for a tidy that removes nothing. How
worktrunk's remove behaves is a contract case (tests/contract/test_wt.py); the read that frees a slot once its agent
settles, the journey's (t-journey-merge, t-journey-fix)."""
import pytest

from facts import plan_of

import plan

KD = "/kit"


def over(path, branch, up="", bolts=("t",), units=("planned",), on_main=(), merged=(), fix_merged=False, dropped=()):
    return plan.tidy_over(f"{KD}/{path}", branch, KD, up, set(bolts), set(units), set(on_main),
                          lambda bolt: set(merged), lambda fix, bolt: fix_merged, dropped=set(dropped))


class TestOver:
    def test_a_bolts_worktree_is_over_once_no_plan_has_the_bolt(self):
        assert over("bolts/gone", "bolt/gone") == (None, "bolt gone is in no plan")
        assert over("bolts/t", "bolt/t") == (None, None)

    def test_a_units_place_is_over_once_it_merged_landed_or_left_every_plan(self):
        assert over("places/merged-one", "unit/merged-one", "bolt/t", merged={"merged-one"}) == (
            "merged-one", "unit merged-one has merged into bolt/t")
        assert over("places/a", "unit/a", "bolt/t", on_main={"a"}) == ("a", "unit a has landed on main")
        assert over("places/ignored-only", "unit/ignored-only", "bolt/t") == ("ignored-only", "unit ignored-only is in no plan")
        assert over("places/planned", "unit/planned", "bolt/t") == ("planned", None)

    def test_a_fixs_place_is_over_once_it_merged_was_dropped_or_its_bolt_left_every_plan(self):
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", fix_merged=True) == ("fix/t/y", "fix/t/y has merged into bolt/t")
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", dropped={"fix/t/y"}) == ("fix/t/y", "fix/t/y was dropped")
        assert over("places/fix-gone--y", "fix/gone/y", "bolt/gone") == ("fix/gone/y", "bolt gone, which fix/gone/y was made from, is in no plan")
        assert over("places/fix-t--y", "fix/t/y", "bolt/t") == ("fix/t/y", None)

    @pytest.mark.parametrize("path, branch, up", [
        ("mine", "mine", ""), ("x", "unit/x", "bolt/t"), ("bolts/not-elsewhere", "bolt/elsewhere", ""),
        ("places/detached", "", ""), ("places/fix-t--y", "fix/t/y", ""), ("main", "main", "")])
    def test_a_worktree_crew_did_not_make_is_never_touched(self, path, branch, up):
        assert over(path, branch, up, units=()) is None


class TestKept:
    def test_a_locked_one_is_kept_unread(self):
        assert plan.kept_why("x", True, None) == "it is locked"

    def test_one_with_uncommitted_changes_is_the_users(self):
        assert plan.kept_why("unit stray has merged into bolt/t", False, (0, "?? note\n", "")) == (
            "unit stray has merged into bolt/t, and it has uncommitted changes, which are the user's to keep or discard")

    def test_one_git_cannot_read_is_kept(self):
        assert plan.kept_why("x", False, (128, "", "fatal: not a git repository\n")) == "git cannot read its status: fatal: not a git repository"

    def test_a_clean_one_goes(self):
        assert plan.kept_why("x", False, (0, "", "")) is None


class TestWt:
    def test_remove_hooks_waiting_for_approval_name_the_command_without_wts_advice(self):
        said = plan.wt_refused(1, "✗ Cannot prompt for approval in non-interactive environment\n↳ To skip prompts in CI/CD, add --yes\n",
                               "chuck-herdr-alpha", "/kit/main")
        assert said == "the kit's remove hooks wait for the user's approval on chuck-herdr-alpha: wt config approvals add, in /kit/main"

    def test_a_refusal_is_its_error_lines_without_the_advice_to_skip_hooks(self):
        assert plan.wt_refused(1, "✗ pre-remove command failed: teardown\n↳ To skip, use --no-hooks\n", "h", "/m") == (
            "the kit's wt remove refused it: pre-remove command failed: teardown")
        assert plan.wt_refused(1, "something odd\n", "h", "/m") == "the kit's wt remove refused it: something odd"
        assert plan.wt_refused(9, "", "h", "/m") == "the kit's wt remove refused it: wt remove exited 9"

    def test_only_an_answer_naming_this_worktree_with_its_branch_untouched_leaves_the_branch_to_crew(self, tmp_path):
        p = str(tmp_path)
        assert plan.wt_left_branch(f'[{{"path": "{p}", "branch_outcome": "not_attempted"}}]', p) is True
        for out in (f'[{{"path": "{p}", "branch_outcome": "deleted"}}]', "not json", "[]",
                    f'[{{"path": "{p}/other", "branch_outcome": "not_attempted"}}]'):
            assert plan.wt_left_branch(out, p) is False


def test_a_plan_that_cannot_be_read_removes_nothing_saying_why_on_one_line():
    assert plan.unread_plans({"wldn/main of WilldanGroup/crew-state": "fatal: '/x' does not\n appear to be a git repository"}) == (
        "no worktree was removed: wldn/main of WilldanGroup/crew-state could not be read: fatal: '/x' does not appear to be a git repository")


class TestSlotStage:
    PLAN = plan_of({"t": "swb-1", "other": "swb-2"}, {"a": "t", "c": "t", "moved": "other", "carried": "t", "carried-gone": "t"})
    KIT = {"ok": True, "main": {"landed-one"},
           "bolts": {"t": {"changes": ["merged-one", "carried"], "archived": ["merged-one"], "open": {"carried": [3, 3], "carried-gone": [2, 3]}}},
           "places": {"merged-one": {"bolt": "t"}, "a": {"bolt": "t", "tasks": (1, 4), "planning": True, "head": "h"},
                      "c": {"bolt": "t", "tasks": None, "planning": False, "head": "h"},
                      "carried": {"bolt": "t", "tasks": (3, 3), "planning": True, "head": "h", "open": []}},
           "fixes": [{"fix": "fix/t/done", "merged": True, "bolt": "t"}, {"fix": "fix/gone/y", "merged": False, "bolt": "gone"},
                     {"fix": "fix/t/y", "merged": False, "bolt": "t"}]}

    def stage(self, kind, name, kit=None, plan_=PLAN):
        return plan.slot_stage(kind, name, kit or self.KIT, plan_, {"t"}, {})

    @pytest.mark.parametrize("name, stage", [
        ("landed-one", "landed"), ("merged-one", "merged"), ("dropped-one", "dropped"), ("moved", "left"), ("c", "construct")])
    def test_a_units(self, name, stage):
        assert self.stage("unit", name) == (stage, None)

    def test_a_unit_in_code_counts_its_tasks(self):
        assert self.stage("unit", "a") == ("code", "1/4")

    def test_a_unit_whose_change_the_bolt_holds_open_has_not_merged_and_is_said_carried(self):
        # wldn, swb-4, 2026-10-13: carried onto its bolt inside another unit's merge (teams.17, signal 45f551aa/01).
        assert self.stage("unit", "carried") == ("verify", "3/3", True)

    def test_one_whose_place_is_gone_reads_its_stage_from_the_change_on_the_bolt(self):
        assert self.stage("unit", "carried-gone") == ("code", "2/3", True)

    @pytest.mark.parametrize("name, stage", [("fix/t/done", "merged"), ("fix/gone/y", "dropped"), ("fix/t/y", "fix"), ("fix/t/z", "none")])
    def test_a_fixs(self, name, stage):
        assert self.stage("fix", name) == (stage, None)

    def test_a_kit_crew_could_not_read_is_unknown(self):
        assert self.stage("unit", "a", kit={"ok": False}) == ("unknown", None)

    def test_with_the_plan_unread_nothing_is_taken_for_dropped(self):
        assert self.stage("unit", "dropped-one", plan_=None) == ("none", None)


class TestTidied:
    def test_a_host_that_does_not_answer_leaves_the_removal_to_the_teams_next_read(self):
        assert plan.tidied("swb-2", "bolt lint-twice", 255, "", "ssh: connect to host chuck-herdr-alpha port 22: Operation timed out\n") == (
            "swb-2's host did not answer, so its worktrees for bolt lint-twice are not removed yet: the team's next read removes them")

    def test_a_tidy_that_failed_says_its_last_line(self):
        assert plan.tidied("swb-2", "unit d", 1, "", "one\nno such team\n") == (
            "swb-2's host failed (no such team), so its worktrees for unit d are not removed yet: the team's next read removes them")

    def test_else_it_says_what_the_tidy_said(self):
        assert plan.tidied("swb-2", "unit d", 0, "swb-2-unit-1 is free\n", "") == "swb-2-unit-1 is free"


class TestBoltBranch:
    """A bolt is a branch and no worktree (record 0026): the branch crew marked when it gave the bolt goes once no plan
    has the bolt and no worktree holds it (plan.9)."""

    def test_a_bolt_no_plan_has_goes(self):
        assert plan.bolt_branch_over("b", {"a"}, False) == "bolt b is in no plan"

    def test_a_planned_bolt_or_one_a_worktree_holds_stays(self):
        assert plan.bolt_branch_over("b", {"b"}, False) is None
        assert plan.bolt_branch_over("b", set(), True) is None
