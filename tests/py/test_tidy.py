"""What crew's sweep removes on a kit's host (plan.9, bolt-teams "crew removes only its own worktrees"): plan.tidy_over
for which worktree is crew's own, a landing's place alone, and whether its work is over, plan.kept_why for one kept,
plan.wt_refused and plan.wt_left_branch for what the kit's wt remove said, plan.branch_kept and plan.branch_said for a
branch kept, plan.bolt_branch_judged for a bolt's own branch and plan.kept_record for what a kept one's record says,
plan.unread_plans for a sweep that removes nothing, plan.overview_runs and plan.run_kept for a worktree sluice has a
run in, and plan.release_kept for one sluice did not release before its removal. The documents under sluice-0.36.4/
were recorded from sluice 0.36.4 on deneb, 2026-10-22, their scratch folder written /scratch: a kit whose place a ran
`sluice exec main -- sleep 25` (overview-run.json) until it ended (overview-ended.json); and on mac-studio,
2026-10-23, the same way: a kit whose policy's release command, `sh -c 'echo tearing down; exit 1'`, failed after a
`sluice exec main -- true` in places/unit-u, `sluice release --worktree <place> --json` exiting 3
(release-failed.json), then, the command's exit taken out and merged in, exiting 0 once with it released
(release.json) and once with nothing left to release (release-nothing.json). How worktrunk's remove behaves is a
contract case (tests/contract/test_wt.py); the landing's sweep, the landing journey's (t-journey-land)."""
import json
import pathlib

import pytest

import plan

KD = "/kit"
RECORDED = pathlib.Path(__file__).parent / "sluice-0.36.4"


def over(path, branch, bolts=("t",)):
    return plan.tidy_over(f"{KD}/{path}", branch, KD, set(bolts))


class TestOver:

    def test_a_landings_place_goes_with_its_bolt(self):
        """bolt-teams "A bolt lands on main on the user's word" (plan.19): the landing's place, <kit>/places/land-<bolt>
        on bolt/<bolt>, which git could not remove after its submission or a stopped landing left, is crew's, and over
        once the landing ends the bolt."""
        assert over("places/land-gone", "bolt/gone") == ("land-gone", "bolt gone is in no plan")
        assert over("places/land-t", "bolt/t") == ("land-t", None)

    @pytest.mark.parametrize("path, branch", [
        ("mine", "mine"), ("places/fix-t--y", "fix/t/y"), ("x", "unit/x"), ("bolts/gone", "bolt/gone"), ("bolts/t", ""),
        ("places/detached", ""), ("main", "main"), ("places/land-gone", "bolt/elsewhere"), ("places/land-gone", ""),
        ("places/gone", "bolt/gone"), ("places/a", "unit/a"), ("places/chore-c", "chore/c"), ("places/change--a", "change/a")])
    def test_a_worktree_crew_did_not_make_is_never_touched(self, path, branch):
        """bolt-teams "crew removes only its own worktrees": a unit's, a chore's or a fix's place, Flume's or one an older
        crew made, a bolt's worktree from before record 0026 and every other worktree are left alone."""
        assert over(path, branch) is None


class TestRemovalRecorded:
    """plan.9: a slot.free crew wrote before it stopped freeing slots named the place its tidy removed in Paths, and
    crew events still reads it so; the sweep of a landing's place says it in its output alone."""

    def test_a_removal_reads_as_one_in_crew_events_and_a_forecast_still_as_its_conflict(self):
        import record
        e = {"At": "2026-10-29T10:00:00Z", "Act": "slot.free", "On": ["agent/t-unit-1", "unit/a"], "From": [], "Commit": [],
             "Paths": f"{KD}/places/a"}
        assert record.line(e).endswith(f"agent/t-unit-1 unit/a (removed {KD}/places/a)")
        assert record.line(dict(e, Act="forecast", Paths="a.txt", Reached="told")).endswith("(conflict on a.txt, told)")


@pytest.mark.parametrize("up, bolt", [
    ("bolt/b", "b"), ("origin/bolt/b", "b"), ("origin/bolt/tenant-environments", "tenant-environments"),
    ("", None), (None, None), ("main", None), ("origin/main", None), ("unit/x", None), ("bolt/", None), ("upstream/bolt/b", None)])
def test_a_places_bolt_is_read_from_either_upstream(up, bolt):
    """gather.bolt_of (plan.19): every read of a place's bolt from its upstream takes bolt/<bolt>, a bolt made before,
    and origin/bolt/<bolt>, a bolt on GitHub, alike."""
    import gather
    assert gather.bolt_of(up) == bolt


class TestBoltMadeBefore:
    """bolt-plan "A bolt made before stays local" (plan.19, record 0032's amendment): each read of a team holding a bolt
    on its host only, while the kit's main names a remote for its bolts, says once that it is local until it lands."""
    LINE = ("bolt/b is local until it lands: it was made before bolts were on GitHub, so its places are cut from the "
            "local branch, and its landing puts it on GitHub")

    def test_a_local_bolt_while_main_names_a_remote_is_said(self):
        assert plan.bolt_local_said("b", None, "origin") == self.LINE

    def test_a_bolt_on_github_is_not(self):
        assert plan.bolt_local_said("b", "origin", "origin") is None

    def test_a_local_bolt_while_main_names_none_is_not_since_every_bolt_is(self):
        assert plan.bolt_local_said("b", None, None) is None


class TestKept:
    def test_a_locked_one_is_kept_unread(self):
        assert plan.kept_why("x", True, None, lambda: None) == "it is locked"

    def test_one_with_uncommitted_changes_is_the_users(self):
        assert plan.kept_why("unit stray has merged into bolt/t", False, (0, "?? note\n", ""), lambda: None) == (
            "unit stray has merged into bolt/t, and it has uncommitted changes, which are the user's to keep or discard")

    def test_one_git_cannot_read_is_kept(self):
        assert plan.kept_why("x", False, (128, "", "fatal: not a git repository\n"), lambda: None) == "git cannot read its status: fatal: not a git repository"

    def test_a_clean_one_goes(self):
        assert plan.kept_why("x", False, (0, "", ""), lambda: None) is None

    def test_a_landings_place_whose_submission_is_still_with_sluice_is_kept_and_named(self):
        assert plan.kept_why("bolt gone is in no plan", False, (0, "", ""), lambda: None, True) == (
            "bolt gone is in no plan, and its submission is still with sluice")

    def test_a_clean_one_sluice_has_a_run_in_is_kept_and_named_for_it_and_only_then_is_the_overview_read(self):
        ran = "sluice's overview lists a run in it, `sleep 25`, started 2026-10-22T23:31:30Z"
        assert plan.kept_why("unit a has merged into bolt/t", False, (0, "", ""), lambda: ran) == (
            f"unit a has merged into bolt/t, and {ran}")

        def unread():
            raise AssertionError("the overview is read only for a worktree nothing else keeps")
        assert plan.kept_why("x", True, None, unread) == "it is locked"
        assert plan.kept_why("x", False, (0, " M a\n", ""), unread).endswith("uncommitted changes, which are the user's to keep or discard")


def recorded(name):
    return json.loads((RECORDED / f"{name}.json").read_text())


class TestRun:
    """Whether sluice has a run in a worktree the tidy would detach or remove (plan.9; sluice ADR 0024 and 0035): read
    from `sluice overview --json` as sluice 0.36.4 prints it, and named; one crew can't read keeps it (read.1)."""

    def test_the_overview_lists_the_worktree_a_run_is_in_and_none_once_it_has_ended(self):
        assert plan.overview_runs(recorded("overview-run")) == {
            "/scratch/places/a": {"command": "sleep 25", "started": "2026-10-22T23:31:30Z"}}
        assert plan.overview_runs(recorded("overview-ended")) == {}

    @pytest.mark.parametrize("d", [
        None, {}, dict(recorded("overview-run"), schema="sluice/overview@2"),
        {k: v for k, v in recorded("overview-run").items() if k != "sessions"},
        dict(recorded("overview-run"), sessions=[{"run": {"started": "2026-10-22T23:31:30Z"}}])])
    def test_a_document_sluice_0_36_4_would_not_print_is_no_overview(self, d):
        assert plan.overview_runs(d) is None

    def test_a_run_is_named_by_its_command_or_as_its_checks_with_when_it_started(self):
        assert plan.run_kept({"command": "sleep 25", "started": "2026-10-22T23:31:30Z"}, None) == (
            "sluice's overview lists a run in it, `sleep 25`, started 2026-10-22T23:31:30Z")
        assert plan.run_kept({"started": "2026-10-22T23:31:30Z", "tasks": []}, None) == (
            "sluice's overview lists a run of its checks in it, started 2026-10-22T23:31:30Z")
        assert plan.run_kept({}, None) == "sluice's overview lists a run of its checks in it"

    def test_no_run_lets_it_go_and_an_overview_crew_cannot_read_keeps_it(self):
        assert plan.run_kept(None, None) is None
        assert plan.run_kept(None, "this host has no sluice on its path") == (
            "sluice's overview can't be read (this host has no sluice on its path), so crew can't tell whether a run is in it")


class TestRelease:
    """Whether sluice released a place the tidy would remove, before the kit's worktree tool removes it (plan.9, as
    amended 2026-10-23; wldn's signal 2026-10-23-wldn-planner-e42b04cf/01): `sluice release --worktree <place> --json` as
    sluice 0.36.4 answers it; one it did not release is kept, in sluice's words (read.1)."""

    @pytest.mark.parametrize("name", ["release", "release-nothing"])
    def test_a_place_released_or_holding_nothing_to_release_may_go(self, name):
        assert plan.release_kept(recorded(name), None) is None

    def test_a_release_command_that_failed_keeps_it_in_sluices_words(self):
        # sluice_read's words for release-failed.json, which sluice printed exiting 3
        why = f"it exited 3: {recorded('release-failed')['error']['message']}"
        assert plan.release_kept(None, why) == (
            "sluice's release of it failed: it exited 3: the release command of /scratch/places/unit-u ended exit "
            "status: 1: tearing down")
        assert plan.release_kept(None, "this host has no sluice on its path") == (
            "sluice's release of it failed: this host has no sluice on its path")

    @pytest.mark.parametrize("d", [None, [], {}, {"preview": "--worktree", "released": False},
                                   dict(recorded("release"), released="yes")])
    def test_a_document_sluice_0_36_4_would_not_print_keeps_it(self, d):
        assert plan.release_kept(d, None) == "sluice's release of it printed no document crew reads"


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


class TestBoltBranch:
    """A bolt is a branch and no worktree (record 0026): the branch crew marked when it gave the bolt goes once no plan
    has the bolt and no worktree holds it (plan.9), a landed bolt's only when git cherry finds nothing on it whose patch
    main lacks, kept and named otherwise (plan.10, record 0003), and any other by sluice's delete alone, a dropped
    bolt's kept branch asked again only once main holds its tip (plan.19)."""
    NOW = "refs/remotes/origin/main"

    def test_a_bolt_no_plan_has_goes(self):
        assert plan.bolt_branch_over("b", {"a"}, False) == "bolt b is in no plan"

    def test_a_planned_bolt_or_one_a_worktree_holds_stays(self):
        assert plan.bolt_branch_over("b", {"b"}, False) is None
        assert plan.bolt_branch_over("b", set(), True) is None

    def test_a_mark_whose_branch_sluice_deleted_is_read_as_gone(self):
        """plan.19: sluice's delete leaves the branch's git config section, so the tidy unsets each mark whose branch is
        gone, saying nothing, rather than judge a branch that is not there on every read."""
        marks = {"bolt/a": "given", "bolt/b": "landed", "bolt/c": "given"}
        assert plan.marks_gone(marks, {"bolt/a"}) == ["bolt/b", "bolt/c"]
        assert plan.marks_gone(marks, {"bolt/a", "bolt/b", "bolt/c", "bolt/d"}) == []
        assert plan.marks_gone({}, set()) == []

    @pytest.mark.parametrize("mark", ["given", "landed", "dropped", None])
    def test_a_bolt_still_planned_or_held_by_a_worktree_is_left_whatever_its_mark(self, mark):
        assert plan.bolt_branch_judged("b", {"b"}, False, mark, True, self.NOW, (0, "+ 1a2b3c\n", "")) is None
        assert plan.bolt_branch_judged("b", set(), True, mark, True, self.NOW, (0, "+ 1a2b3c\n", "")) is None

    def test_a_landed_bolt_whose_every_commit_main_holds_goes_saying_so(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", False, self.NOW, (0, "", "")) == (
            "delete", "bolt b has landed, and origin/main holds every commit of it (git cherry)", None)
        assert plan.bolt_branch_judged("b", set(), False, "landed", False, self.NOW, (0, "- 1a2b3c\n", ""))[0] == "delete"

    def test_a_landed_bolt_holding_a_commit_main_lacks_is_kept_and_counted(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", False, self.NOW, (0, "- 1a2b3c\n+ 4d5e6f\n", "")) == (
            "keep", "bolt b has landed", ("it holds 1 commit whose patch origin/main lacks (git cherry), the user's to keep or delete", 1))

    def test_a_landed_bolt_git_cannot_compare_with_main_is_kept(self):
        assert plan.bolt_branch_judged("b", set(), False, "landed", False, self.NOW, (128, "", "fatal: bad revision\n")) == (
            "keep", "bolt b has landed", ("git cannot compare it with origin/main: fatal: bad revision", None))

    @pytest.mark.parametrize("mark", ["given", None])
    def test_a_dropped_bolts_or_one_landed_before_the_mark_is_sluices_to_delete_unread(self, mark):
        """plan.19: a bolt branch marked given that no plan has, a drop's whatever its host answered, or a legacy bolt
        worktree's with no mark, is asked of sluice's delete, never git's, whose answer keeps a tip main lacks."""
        assert plan.bolt_branch_judged("b", set(), False, mark, False, self.NOW, None) == ("ask", "bolt b is in no plan", None)

    def test_a_dropped_bolts_kept_branch_is_asked_again_only_once_main_holds_its_tip(self):
        """bolt-plan "Main comes to hold a dropped bolt's work" and "A dropped bolt's kept branch while main lacks it"."""
        assert plan.bolt_branch_judged("b", set(), False, "dropped", True, self.NOW, None) == (
            "ask", "main now holds bolt b's tip", None)
        assert plan.bolt_branch_judged("b", set(), False, "dropped", False, self.NOW, None) is None

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
