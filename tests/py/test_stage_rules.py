"""Whether a unit's stage may start (plan.6, plan.13, teams.5): plan.stage_refusal, on the unit's stage, its Amended
mark, its After units' stages and who asks. What a started stage is sent, and the place it runs in, are
t-unit-run's."""
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
        assert refusal("merge", "verify", after={"b": "merged", "c": "landed"}) is None

    def test_waits_on_after_units_not_yet_merged(self):
        assert refusal("merge", "verify", after={"b": "verify", "c": "merged"}) == (
            "unit a merges after b, not yet merged into bolt/tenant-environments")

    def test_waits_for_verify(self):
        assert refusal("merge", "code") == "unit a is in code: it merges once every task is ticked and verify has run"
