"""What a team's read frees and removes (teams.1, plan.9): plan.slot_stage for the work each slot holds,
plan.tidy_over for which worktrees are crew's and whose work is over, plan.kept_why for one kept, plan.wt_refused and
plan.wt_left_branch for what the kit's wt remove said, plan.branch_target and plan.branch_kept for whether a branch
goes with its place (plan.10) and plan.branch_said for what is said of it, plan.bolt_branch_judged for a bolt's own
branch and plan.kept_record for what a kept one's record says, and plan.unread_plans for a tidy that removes nothing. How worktrunk's remove behaves is a contract case (tests/contract/test_wt.py); the read that frees a slot once its agent
settles, the journey's (t-journey-merge, t-journey-fix)."""
import pytest

from facts import plan_of

import plan

KD = "/kit"


# A fix branch's facts as gather.fix_facts reads them: in flight, merged into its bolt, landed with it, or cut at a
# commit main holds and never moved.
GOING = {"bolt": "t", "merged": False, "on_main": False, "moved": None}
MERGED = dict(GOING, merged=True, moved=True)
LANDED = dict(GOING, on_main=True, moved=True)
CUT = dict(GOING, on_main=True, moved=False)


def over(path, branch, up="", bolts=("t",), units=("planned",), on_main=(), merged=(), fix=GOING, dropped=()):
    return plan.tidy_over(f"{KD}/{path}", branch, KD, up, set(bolts), set(units), set(on_main),
                          lambda bolt: set(merged), lambda b: fix, dropped=set(dropped))


class TestOver:
    def test_a_bolts_worktree_is_over_once_no_plan_has_the_bolt(self):
        assert over("bolts/gone", "bolt/gone") == (None, "bolt gone is in no plan")
        assert over("bolts/t", "bolt/t") == (None, None)

    def test_a_bolts_worktree_the_tidy_detached_is_still_crews_and_goes_with_its_bolt(self):
        assert over("bolts/gone", "") == (None, "bolt gone is in no plan")
        assert over("bolts/t", "") == (None, None)

    def test_a_units_place_is_over_once_it_merged_landed_or_left_every_plan(self):
        assert over("places/merged-one", "unit/merged-one", "bolt/t", merged={"merged-one"}) == (
            "merged-one", "unit merged-one has merged into bolt/t")
        assert over("places/a", "unit/a", "bolt/t", on_main={"a"}) == ("a", "unit a has landed on main")
        assert over("places/ignored-only", "unit/ignored-only", "bolt/t") == ("ignored-only", "unit ignored-only is in no plan")
        assert over("places/planned", "unit/planned", "bolt/t") == ("planned", None)

    def test_a_fixs_place_is_over_once_it_merged_was_dropped_or_its_bolt_left_every_plan(self):
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", fix=MERGED) == ("fix/t/y", "fix/t/y has merged into bolt/t")
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", dropped={"fix/t/y"}) == ("fix/t/y", "fix/t/y was dropped")
        assert over("places/fix-gone--y", "fix/gone/y", "bolt/gone") == ("fix/gone/y", "bolt gone, which fix/gone/y was made from, is in no plan")
        assert over("places/fix-t--y", "fix/t/y", "bolt/t") == ("fix/t/y", None)

    def test_a_landed_fixs_place_is_over_with_its_bolt_planned_or_gone(self):
        # wldn, swb-3, 2026-10-20: fixes of landed bolts held their slots and branches (teams.3).
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", fix=LANDED) == ("fix/t/y", "fix/t/y has landed on main")
        assert over("places/fix-gone--y", "fix/gone/y", "bolt/gone", fix=LANDED) == ("fix/gone/y", "fix/gone/y has landed on main")
        assert over("places/fix-gone--y", "fix/gone/y", "bolt/gone", fix=CUT) == ("fix/gone/y", "fix/gone/y has landed on main")
        assert over("places/fix-t--y", "fix/t/y", "bolt/t", fix=CUT) == ("fix/t/y", None)

    def test_a_fix_tracking_its_bolt_on_github_is_crews_and_over_once_merged(self):
        # plan.19: a place cut from origin/bolt/<bolt> tracks the remote-tracking branch.
        assert over("places/fix-t--y", "fix/t/y", "origin/bolt/t", fix=MERGED) == ("fix/t/y", "fix/t/y has merged into bolt/t")
        assert over("places/fix-t--y", "fix/t/y", "origin/bolt/t") == ("fix/t/y", None)
        assert over("places/fix-gone--y", "fix/gone/y", "origin/bolt/gone") == (
            "fix/gone/y", "bolt gone, which fix/gone/y was made from, is in no plan")

    @pytest.mark.parametrize("path, branch, up", [
        ("mine", "mine", ""), ("places/fix-t--y", "fix/t/y", "origin/main"), ("x", "unit/x", "bolt/t"), ("bolts/not-elsewhere", "bolt/elsewhere", ""),
        ("places/detached", "", ""), ("places/fix-t--y", "fix/t/y", ""), ("main", "main", "")])
    def test_a_worktree_crew_did_not_make_is_never_touched(self, path, branch, up):
        assert over(path, branch, up, units=()) is None


class TestFixBranchesOver:
    """A fix's branch whose place is gone goes once main or its bolt holds its tip and no slot or worktree holds it
    (teams.3, plan.10): read on the box on 2026-10-20, more than forty fix/ branches of long-gone bolts in
    switchboard-kit, each one's tip on origin/main."""

    def gone(self, facts, held=(), dropped=(), bolts=("t",)):
        return plan.fix_branches_over(facts, set(held), set(dropped), set(bolts))

    def test_a_merged_or_landed_branch_goes_saying_why(self):
        facts = {"fix/t/merged": MERGED, "fix/gone/landed": dict(LANDED, bolt="gone"), "fix/gone/cut": dict(CUT, bolt="gone"),
                 "fix/t/landed": LANDED}
        assert self.gone(facts) == [("fix/gone/cut", "it has landed on main"), ("fix/gone/landed", "it has landed on main"),
                                    ("fix/t/landed", "it has landed on main"), ("fix/t/merged", "it has merged into bolt/t")]

    def test_one_a_slot_or_a_worktree_holds_stays(self):
        assert self.gone({"fix/t/merged": MERGED, "fix/t/landed": LANDED}, held={"fix/t/merged", "fix/t/landed"}) == []

    def test_one_its_conductor_dropped_is_left_to_the_dropped_sweep(self):
        assert self.gone({"fix/t/merged": MERGED}, dropped={"fix/t/merged"}) == []

    def test_one_holding_work_main_and_its_bolt_lack_stays(self):
        assert self.gone({"fix/gone/kept": dict(GOING, bolt="gone"), "fix/none/kept": dict(GOING, bolt=None, on_main=True, moved=False)}) == []

    def test_one_whose_bolt_is_planned_and_not_merged_stays(self):
        assert self.gone({"fix/t/y": GOING, "fix/t/cut": CUT}) == []


class TestLegacyBolt:
    """crew removes only its own worktrees (bolt-teams): a bolt's worktree from before record 0026, still on its
    branch, is detached at the bolt's tip by the team's read while the bolt lasts when it is clean, and named as kept on
    the branch while it is not (plan.9, plan.18)."""

    def detach(self, path="bolts/t", branch="bolt/t", over=None, locked=False, status=(0, "", "")):
        return plan.bolt_detach(f"{KD}/{path}", branch, KD, over, locked, lambda: status)

    def test_a_legacy_bolt_worktree_on_its_branch_with_nothing_modified_is_detached(self):
        assert self.detach() == (True, None)

    def test_a_legacy_bolt_worktree_with_changes_stays_on_its_branch_named_as_kept_for_them(self):
        assert self.detach(status=(0, " M README.md\n", "")) == (False, (
            "it has uncommitted changes, which are the user's to keep or discard, and crew detaches it at the bolt's tip "
            "once it is clean"))

    def test_a_locked_one_or_one_git_cannot_read_stays_on_its_branch(self):
        assert self.detach(locked=True, status=None) == (False, "it is locked, and crew detaches it at the bolt's tip once it is not")
        assert self.detach(status=(128, "", "fatal: bad index\n"))[1].startswith("git cannot read its status (fatal: bad index)")

    @pytest.mark.parametrize("path, branch, over", [
        ("bolts/t", "", None), ("bolts/t", "bolt/t", "bolt t is in no plan"), ("bolts/t", "bolt/other", None),
        ("places/t", "bolt/t", None), ("main", "main", None)])
    def test_nothing_else_is_detached_and_a_finished_bolts_worktree_goes_as_any(self, path, branch, over):
        assert self.detach(path, branch, over, status=None) is None


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
           "fixes": [{"fix": "fix/t/done", "merged": True, "bolt": "t", "on_main": False, "moved": True},
                     {"fix": "fix/gone/y", "merged": False, "bolt": "gone", "on_main": False, "moved": None},
                     {"fix": "fix/t/y", "merged": False, "bolt": "t", "on_main": False, "moved": None},
                     {"fix": "fix/t/cut", "merged": False, "bolt": "t", "on_main": True, "moved": False},
                     {"fix": "fix/t/landed", "merged": False, "bolt": "t", "on_main": True, "moved": True},
                     {"fix": "fix/gone/never-moved", "merged": False, "bolt": "gone", "on_main": True, "moved": False}],
           # Fix branches no worktree holds, their places gone (wldn, swb-3, 2026-10-20: four slots kept, read `none`).
           "fix_branches": {"fix/gone/landed": {"merged": False, "bolt": "gone", "on_main": True, "moved": True},
                            "fix/t/merged": {"merged": True, "bolt": "t", "on_main": False, "moved": True},
                            "fix/gone/kept": {"merged": False, "bolt": "gone", "on_main": False, "moved": None}}}

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

    @pytest.mark.parametrize("name, stage", [
        ("fix/t/landed", "landed"), ("fix/gone/never-moved", "landed"), ("fix/t/done", "merged"), ("fix/gone/y", "dropped"),
        ("fix/t/y", "fix"), ("fix/t/cut", "fix"), ("fix/t/z", "none")])
    def test_a_fixs(self, name, stage):
        assert self.stage("fix", name) == (stage, None)

    @pytest.mark.parametrize("name, stage", [("fix/gone/landed", "landed"), ("fix/t/merged", "merged"), ("fix/gone/kept", "dropped")])
    def test_a_fix_whose_place_is_gone_is_read_from_its_branch(self, name, stage):
        assert self.stage("fix", name) == (stage, None)

    @pytest.mark.parametrize("name, stage", [
        ("fix/gone/y", "fix"), ("fix/gone/never-moved", "fix"), ("fix/gone/kept", "fix"), ("fix/t/landed", "landed"), ("fix/t/done", "merged")])
    def test_with_the_plan_unread_no_fix_is_read_dropped_or_landed_by_the_plan(self, name, stage):
        assert self.stage("fix", name, plan_=None) == (stage, None)

    def test_a_fix_tracking_no_bolt_is_never_read_dropped(self):
        f = {"merged": False, "bolt": None, "on_main": True, "moved": False}
        assert plan.fix_stage(f, None) == "fix"

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
    has the bolt and no worktree holds it (plan.9), and a landed bolt's only when git cherry finds nothing on it whose
    patch main lacks, kept and named otherwise (plan.10, record 0003)."""
    NOW = "refs/remotes/origin/main"

    def test_a_bolt_no_plan_has_goes(self):
        assert plan.bolt_branch_over("b", {"a"}, False) == "bolt b is in no plan"

    def test_a_planned_bolt_or_one_a_worktree_holds_stays(self):
        assert plan.bolt_branch_over("b", {"b"}, False) is None
        assert plan.bolt_branch_over("b", set(), True) is None

    @pytest.mark.parametrize("mark", ["given", "landed", None])
    def test_a_bolt_still_planned_or_held_by_a_worktree_is_left_whatever_its_mark(self, mark):
        assert plan.bolt_branch_judged("b", {"b"}, False, mark, self.NOW, (0, "+ 1a2b3c\n", "")) is None
        assert plan.bolt_branch_judged("b", set(), True, mark, self.NOW, (0, "+ 1a2b3c\n", "")) is None

    def test_a_landed_bolt_whose_every_commit_main_holds_goes_saying_so(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", self.NOW, (0, "", "")) == (
            "bolt b has landed, and origin/main holds every commit of it (git cherry)", None)
        assert plan.bolt_branch_judged("b", set(), False, "landed", self.NOW, (0, "- 1a2b3c\n", ""))[1] is None

    def test_a_landed_bolt_holding_a_commit_main_lacks_is_kept_and_counted(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", self.NOW, (0, "- 1a2b3c\n+ 4d5e6f\n", "")) == (
            "bolt b has landed", ("it holds 1 commit whose patch origin/main lacks (git cherry), the user's to keep or delete", 1))

    def test_a_landed_bolt_git_cannot_compare_with_main_is_kept(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", self.NOW, (128, "", "fatal: bad revision\n")) == (
            "bolt b has landed", ("git cannot compare it with origin/main: fatal: bad revision", None))

    @pytest.mark.parametrize("mark", ["given", None])
    def test_a_dropped_bolts_or_one_landed_before_the_mark_goes_as_before_unread(self, mark):
        assert plan.bolt_branch_judged("b", set(), False, mark, self.NOW, None) == ("bolt b is in no plan", None)

    def test_what_is_said_of_a_landed_bolts_branch(self):
        assert plan.branch_said("bolt/b", None, "1a2b3c4", "bolt b has landed, and origin/main holds every commit of it "
                                "(git cherry)", None) == (
            "bolt/b is removed: bolt b has landed, and origin/main holds every commit of it (git cherry); it was at 1a2b3c4")
        kept = ("it holds 2 commits whose patch origin/main lacks (git cherry), the user's to keep or delete", 2)
        assert plan.branch_said("bolt/b", None, "1a2b3c4", "bolt b has landed", kept) == (
            "bolt/b is kept at 1a2b3c4: bolt b has landed, and it holds 2 commits whose patch origin/main lacks (git "
            "cherry), the user's to keep or delete")
        assert plan.branch_said("bolt/b", "/kit/bolts/b", "1a2b3c4", "bolt b has landed",
                                ("git cannot compare it with origin/main: fatal: bad revision", None)) == (
            "/kit/bolts/b is removed, and bolt/b is kept at 1a2b3c4: bolt b has landed, and git cannot compare it with "
            "origin/main: fatal: bad revision, the user's to keep or delete")

    def test_its_record_names_main_from_names_alone(self):
        """record.3: the Why of a kept branch's branch.kept entry is composed from names, main named in it since the
        run record has no kind for a kit's main."""
        assert plan.kept_record("bolt b has landed", self.NOW, ("it holds 1 commit …", 1)) == (
            "bolt b has landed, and origin/main lacks its patches")
        assert plan.kept_record("bolt b has landed", self.NOW, ("git cannot compare it with origin/main: exit 1", None)) == (
            "bolt b has landed, and git cannot compare it with origin/main: exit 1")


class TestBranch:
    """A unit's, chore's or fix's branch goes with its place only when git cherry finds nothing on it whose patch its
    target lacks: its bolt while the bolt's branch stands unlanded, else the kit's main now, a fix's as a unit's since
    its bolt goes with its landing; nothing for a fix tracking no bolt (plan.10, record 0003, record 0028, teams.3).
    Else it is kept, counted for the run record."""
    NOW = "refs/remotes/origin/main"

    @pytest.mark.parametrize("kind", ["unit", "chore", "fix"])
    def test_one_is_compared_with_its_bolt_while_the_bolts_branch_stands_unlanded(self, kind):
        assert plan.branch_target(kind, "bolt/t", True, False, self.NOW) == "bolt/t"

    @pytest.mark.parametrize("kind", ["unit", "chore", "fix"])
    def test_once_its_bolt_is_marked_landed_it_is_compared_with_the_kits_main_now_not_the_bolt(self, kind):
        assert plan.branch_target(kind, "bolt/t", True, True, self.NOW) == self.NOW

    @pytest.mark.parametrize("kind", ["unit", "chore", "fix"])
    def test_once_the_bolts_branch_is_gone_it_is_compared_with_the_kits_main_now(self, kind):
        assert plan.branch_target(kind, "bolt/gone", False, False, self.NOW) == self.NOW

    @pytest.mark.parametrize("kind", ["unit", "chore"])
    def test_a_unit_or_chore_tracking_nothing_is_compared_with_main(self, kind):
        assert plan.branch_target(kind, "", False, False, "refs/heads/main") == "refs/heads/main"

    def test_a_fix_tracking_no_bolt_has_nothing_to_compare_with(self):
        assert plan.branch_target("fix", "", False, False, self.NOW) is None

    def test_only_plus_lines_are_counted_and_keep_it(self):
        assert plan.branch_kept("bolt/t", (0, "+ 1a2b3c\n- 4d5e6f\n+ 7a8b9c\n", "")) == (
            "it holds 2 commits whose patch bolt/t lacks (git cherry), the user's to keep or delete", 2)

    def test_minus_lines_or_nothing_let_it_go(self):
        assert plan.branch_kept("bolt/t", (0, "- 1a2b3c\n- 4d5e6f\n", "")) is None
        assert plan.branch_kept(self.NOW, (0, "", "")) is None

    def test_main_is_named_as_its_branch_not_its_ref(self):
        assert plan.branch_kept(self.NOW, (0, "+ 1a2b3c\n", ""))[0] == (
            "it holds 1 commit whose patch origin/main lacks (git cherry), the user's to keep or delete")
        assert plan.branch_kept("refs/heads/main", (0, "+ 1a2b3c\n", ""))[0].startswith("it holds 1 commit whose patch main lacks")

    def test_a_non_zero_exit_keeps_it_in_gits_words_uncounted(self):
        assert plan.branch_kept("bolt/gone", (128, "", "fatal: unknown commit bolt/gone\n")) == (
            "git cannot compare it with bolt/gone: fatal: unknown commit bolt/gone", None)
        assert plan.branch_kept("bolt/t", (1, "", "")) == ("git cannot compare it with bolt/t: exit 1", None)


class TestBranchSaid:
    """What the tidy says of a branch whose place goes (plan.10, record 0003): removed with the commit it was at, or
    kept at it, named as the user's, a unit's or chore's for the next of its name to start from; a fix's in its own
    words (record 0028)."""
    KEPT = ("it holds 1 commit whose patch bolt/t lacks (git cherry), the user's to keep or delete", 1)

    def test_one_holding_nothing_of_its_own_is_removed_saying_where_it_was(self):
        assert plan.branch_said("unit/u", "/kit/places/u", "1a2b3c4", "unit u is in no plan", None) == (
            "/kit/places/u and unit/u are removed; the branch was at 1a2b3c4")

    def test_a_units_kept_branch_is_named_with_its_commit_and_count_and_who_starts_from_it(self):
        assert plan.branch_said("unit/u", "/kit/places/u", "1a2b3c4", "unit u is in no plan", self.KEPT) == (
            "/kit/places/u is removed, and unit/u is kept at 1a2b3c4: unit u is in no plan, and it holds 1 commit whose "
            "patch bolt/t lacks (git cherry), the user's to keep or delete; a unit added as u starts from it")

    def test_a_chores_says_a_chore_starts_from_it(self):
        assert plan.branch_said("chore/bump", "/kit/places/chore-bump", "1a2b3c4", "chore bump is in no plan", self.KEPT).endswith(
            "the user's to keep or delete; a chore added as bump starts from it")

    def test_one_git_cannot_compare_says_gits_words_and_is_the_users(self):
        kept = ("git cannot compare it with bolt/t: fatal: bad revision", None)
        assert plan.branch_said("unit/u", "/kit/places/u", "1a2b3c4", "unit u is in no plan", kept) == (
            "/kit/places/u is removed, and unit/u is kept at 1a2b3c4: unit u is in no plan, and git cannot compare it "
            "with bolt/t: fatal: bad revision, the user's to keep or delete; a unit added as u starts from it")

    def test_a_dropped_fixs_keeps_its_words(self):
        assert plan.branch_said("fix/t/y", "/kit/places/fix-t--y", "1a2b3c4", "it was dropped", self.KEPT) == (
            "/kit/places/fix-t--y is removed, and fix/t/y is kept at 1a2b3c4: it was dropped, and it holds 1 commit whose "
            "patch bolt/t lacks (git cherry), the user's to keep or delete")
        assert plan.branch_said("fix/t/y", None, "1a2b3c4", "it was dropped", None) == (
            "fix/t/y is removed: it was dropped; it was at 1a2b3c4")

    def test_a_deletion_git_refuses_keeps_it_in_gits_words(self):
        assert plan.branch_said("unit/u", "/kit/places/u", "1a2b3c4", "unit u is in no plan", None, "error: refused") == (
            "/kit/places/u is removed, and unit/u is kept: error: refused")
