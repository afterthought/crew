"""Whether a unit's stage may start (plan.6, plan.13, teams.5, teams.17): plan.stage_refusal, on the unit's stage, its
Amended mark, its After units' stages and who asks; plan.carried_in and plan.carried_refusal for a merge whose branch
carries another unit's open change; plan.archives_owed and plan.archives_refusal for a merge that stops short for
archives it can make. What a started stage is sent, and the place it runs in, are t-unit-run's."""
import pytest

import plan

USER, CONDUCTOR, OTHER_CONDUCTOR, CODER = ("user", None), ("conductor", "swb-1"), ("conductor", "swb-2"), ("team", "swb-1")


def refusal(stage, st, mark=None, after=None, caller=USER, open_tasks=(), delivered_verify=False, has_words=False):
    return plan.stage_refusal("a", "tenant-environments", stage, st, mark, after or {}, caller, "swb-1", list(open_tasks),
                              delivered_verify, has_words)


class TestConstruct:
    def test_waits_on_each_after_unit_whose_change_is_not_committed(self):
        assert refusal("construct", "waiting", after={"b": "construct", "c": "planned", "d": "waiting"}) == (
            "unit a is waiting: it comes after b, d, whose change is not committed yet")

    @pytest.mark.parametrize("st, where", [("merged", "merged into its bolt"), ("landed", "landed on main")])
    def test_is_never_run_on_merged_or_landed_work(self, st, where):
        assert refusal("construct", st) == f"unit a has {where}: a defect in it is a fix (crew fix), and a new need is a new unit"

    def test_runs_on_a_unit_with_no_change_for_anyone(self):
        assert refusal("construct", "construct", caller=CODER) is None

    @pytest.mark.parametrize("st", ["planned", "code", "verify"])
    def test_run_again_on_a_committed_change_only_by_its_conductor_or_the_user(self, st):
        assert refusal("construct", st, caller=USER) is None
        assert refusal("construct", st, caller=CONDUCTOR) is None
        for caller in (OTHER_CONDUCTOR, CODER):
            assert refusal("construct", st, caller=caller) == (
                f"unit a is in {st}, so construct run again marks it amended: a plan write only swb-1-conductor or the user makes")

    @pytest.mark.parametrize("mark", ["intent", "proposal/124"])
    def test_an_amendment_the_user_approved_is_constructed_by_anyone(self, mark):
        assert refusal("construct", "amended", mark=mark, caller=CODER) is None

    def test_a_unit_whose_construct_already_started_again_is_marked_by_its_head(self):
        assert refusal("construct", "construct", mark="abc1234", caller=CODER) == (
            "unit a is in construct, so construct run again marks it amended: a plan write only swb-1-conductor or the user makes")


class TestWhileMarked:
    @pytest.mark.parametrize("stage", ["code", "verify", "settle", "merge"])
    def test_every_other_stage_waits_for_an_amended_units_construct(self, stage):
        assert refusal(stage, "amended", mark="intent") == "unit a was amended and construct has not been run again (crew unit run a construct)"
        assert refusal(stage, "construct", mark="abc1234") == "unit a was amended and its change is being written again, and has not been committed"


class TestCode:
    @pytest.mark.parametrize("st", ["planned", "code", "verify"])
    def test_starts_once_the_change_is_committed_with_no_review(self, st):
        assert refusal("code", st) is None

    def test_waits_for_the_change(self):
        assert refusal("code", "construct") == "unit a is in construct: code waits until its change is committed"
        assert refusal("code", "waiting") == "unit a is in waiting: it has no change to code yet"


class TestVerify:
    def test_starts_once_every_task_is_ticked(self):
        assert refusal("verify", "verify") is None

    def test_names_the_open_tasks_and_records_only_how_many(self):
        assert refusal("verify", "code", open_tasks=["1.2 Write the log", "2.1 Test it"]) == (
            "unit a is in code, with these tasks still open: 1.2 Write the log; 2.1 Test it", "unit a is in code, with 2 tasks still open")

    def test_waits_for_tasks(self):
        assert refusal("verify", "planned") == "unit a is in planned: verify waits until every task is ticked"


class TestSettle:
    def test_runs_for_a_verified_unit_with_what_reached_it(self):
        assert refusal("settle", "verify", delivered_verify=True, has_words=True) is None

    def test_needs_what_reached_it(self):
        assert refusal("settle", "verify", delivered_verify=True) == (
            'settle a with what reached it: crew unit run a settle "<the forecast or the amendment>"')

    def test_needs_a_delivered_verify(self):
        assert refusal("settle", "verify", has_words=True) == (
            "unit a is in verify, and has not delivered its verify: settle runs only for a unit that has delivered its verify and waits to merge")
        assert refusal("settle", "code", has_words=True) == (
            "unit a is in code: settle runs only for a unit that has delivered its verify and waits to merge")


class TestMerge:
    def test_merges_a_verified_unit_whose_after_units_have_merged(self):
        assert refusal("merge", "verify", after={"b": "merged", "c": "landed"}, delivered_verify=True) is None

    def test_waits_on_after_units_not_yet_merged(self):
        assert refusal("merge", "verify", after={"b": "verify", "c": "merged"}, delivered_verify=True) == (
            "unit a merges after b, not yet merged into bolt/tenant-environments")

    def test_a_unit_whose_verify_delivered_no_report_does_not_merge_naming_the_report(self):
        # crw-4, 2026-10-23: crew started a unit's merge with no verify report (signal
        # 2026-10-23-crw-4-conductor-8de4d1fb/01). Its verify may have run, been stuck, stopped short or not ended.
        assert plan.stage_refusal("a", "tenant-environments", "merge", "verify", None, {"b": "merged"}, USER, "swb-1", [], False,
                                  False, reports="/home/.local/state/swb-1-team/reports") == (
            "unit a merges only once its verify has delivered its report, and no verify since its change was last "
            "written has: no report verify-a-<YYYYMMDD-HHMM>.md was delivered from /home/.local/state/swb-1-team/reports "
            "(crew unit run a verify)")

    def test_waits_for_verify(self):
        assert refusal("merge", "code") == "unit a is in code: it merges once every task is ticked and verify has run"


class TestCarried:
    """A unit's or chore's merge carries no other unit's open change (teams.17): wldn, swb-4, 2026-10-13, the
    dependency s merged its dependent d's branch, as an overlap note asked, and d's change reached the bolt open inside
    s's merge (signals 51c2c852/01 and 45f551aa/01)."""
    UNITS = {"s", "d", "x", "y"}

    def test_another_units_change_the_bolt_does_not_hold_archived_is_carried(self):
        assert plan.carried_in("s", self.UNITS, ["d", "s"], []) == ["d"]

    def test_its_own_one_the_bolt_holds_archived_and_one_no_unit_has_are_not(self):
        # a dependent's place took the dependency's work, which the bolt holds archived once its own merge did;
        # a change main has held open since before archives is no unit's of the plan.
        assert plan.carried_in("d", self.UNITS, ["d", "s", "every-crew-card-goes-through-crew"], ["s"]) == []

    def test_its_refusal_says_to_take_out_a_later_units_work_and_merge_any_other_first(self):
        assert plan.carried_refusal("unit", "s", "te", ["d", "x"], {"d": ["s"]}) == (
            "unit s does not merge while unit/s holds the changes of d and x open, which bolt/te does not hold archived: "
            "no unit's change reaches a bolt inside another's merge; d comes after s: take that work out of unit/s "
            "(crew unit run s code \"<what to take out>\"); merge x first, its own merge archiving its change "
            "(crew unit run x merge)")

    def test_a_chores_says_so_with_its_own_command(self):
        assert plan.carried_refusal("chore", "bump", "te", ["x", "y"], {}) == (
            "chore bump does not merge while chore/bump holds the changes of x and y open, which bolt/te does not hold "
            "archived: no unit's change reaches a bolt inside another's merge; merge x and y first, each one's own merge "
            "archiving its change (crew unit run <unit> merge)")


class TestArchivesOwed:
    """A unit's merge archives what its own archive needs first, so it never stops short for an archive it can make
    (teams.17, roles.3): wldn, awb-1, 2026-10-19, the merge of the-production-class-account-is-seeded stopped short for
    five changes the bolt held open with every task ticked, the conductor routed them to the plan as a chore, and the
    chore could not start for the slot the waiting unit held (signal 2026-10-19-awb-1-conductor-5eafeeda/01)."""
    UNITS = {"seeded", "sibling"}
    SPECS = {"seeded": {"accounts"}, "left-1": {"accounts"}, "left-2": {"classes"}, "left-3": {"classes", "hosts"},
             "left-4": {"pages"}, "sibling": {"accounts"}, "open-tasks": {"accounts"}}

    def owed(self, opened, ticked=None, **specs):
        return plan.archives_owed("seeded", self.UNITS, opened, ticked or {c: True for c in opened},
                                  {**self.SPECS, **{c.replace("_", "-"): s for c, s in specs.items()}})

    def test_a_ticked_change_no_unit_has_touching_its_specs_is_its_to_archive(self):
        assert self.owed(["left-1", "seeded"]) == ["left-1"]

    def test_and_each_one_those_touch_in_turn(self):
        # left-1 shares accounts with seeded, and classes with left-2 and left-3, which share nothing with seeded
        assert self.owed(["left-1", "left-2", "left-3", "left-4", "seeded"], left_1={"accounts", "classes"}) == [
            "left-1", "left-2", "left-3"]

    def test_not_one_with_a_task_open_another_units_or_one_touching_nothing_of_its(self):
        # another unit's open change is carried_in's, refused before the merge starts; one with a task open is no
        # archive a merge can make; one touching specs nothing of the unit's touches is main-level ops's
        assert self.owed(["left-4", "open-tasks", "seeded", "sibling"], {"left-4": True, "open-tasks": False}) == []

    def test_none_once_its_own_is_archived(self):
        assert self.owed(["left-1"]) == []

    def test_its_refusal_names_them_and_says_what_the_merge_does(self):
        assert plan.archives_refusal("seeded", ["left-1"]) == (
            "merge on seeded does not stop short for archives it can make: unit/seeded holds left-1 open, every task "
            "ticked, no unit's of the plan, and touching specs its change does; a merge archives what its own archive "
            "needs first: archive it with `openspec archive <change> --yes`, committed as `docs(openspec): archive "
            "<change>`, then seeded's own, and submit. If openspec refuses one of them, say so again with its words, "
            "and crew passes it on")
        assert plan.archives_refusal("seeded", ["left-1", "left-2", "left-3"]).startswith(
            "merge on seeded does not stop short for archives it can make: unit/seeded holds left-1, left-2 and left-3 "
            "open, each with every task ticked, no unit's of the plan, and touching specs its change does; a merge "
            "archives what its own archive needs first: archive each, oldest first, with `openspec archive")
