"""What a unit's stage is sent, and what starting it ends (teams.5, teams.12, plan.15): plan.stage_prompt on the stage's
facts, plan.again_words on an amended intent's mark, plan.ends_row for the rail row whose card its conductor closes,
plan.merge_command for how a unit merges, plan.unit_team for the team that runs its stages, and the effort each stage
starts at, from its role's definition. That a started stage is sent its prompt in a fresh agent is the journey's
(t-journey-units)."""
import pytest

import crew
import plan
from facts import plan_of


class TestConstruct:
    def test_proposes_the_change_from_the_intent_and_its_sources(self):
        assert plan.stage_prompt("construct", "a", intent="Unit a.", sources=["books/x.md", "switchboard-kit:docs/y.md"]) == (
            "/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.")

    def test_the_users_words_come_last(self):
        assert plan.stage_prompt("construct", "a", "Use the words the user gave.", intent="Unit a.") == (
            "/opsx:propose a Unit a. Use the words the user gave.")

    def test_an_intent_the_user_amended_is_revised(self):
        assert plan.stage_prompt("construct", "a", intent="Unit a, amended.", again=plan.again_words("intent")) == (
            "/opsx:propose a Unit a, amended. This unit's intent was amended by the user; revise the existing change to it.")

    def test_an_intent_a_proposal_amended_carries_the_planners_case_as_approved(self):
        assert plan.again_words("proposal/4", "The operator reads\n  the deploy's log first.") == (
            " This unit's intent was amended by proposal 4; revise the existing change to it. The planner's case, as the "
            "user approved it: The operator reads the deploy's log first.")

    @pytest.mark.parametrize("mark", [None, "", "3f2a9c1"])
    def test_a_unit_whose_construct_already_started_again_adds_nothing(self, mark):
        assert plan.again_words(mark) == ""


class TestCode:
    def test_applies_the_change(self):
        assert plan.stage_prompt("code", "a") == "/opsx:apply a"

    def test_with_findings_to_fix(self):
        assert plan.stage_prompt("code", "a", "Fix these findings from the verify: the error names no unit.") == (
            "/opsx:apply a Fix these findings from the verify: the error names no unit.")

    def test_names_each_overlap_after_the_words(self):
        assert plan.stage_prompt("code", "c", "Mind the docs.", overlaps=["Its Touches overlap those of a."]) == (
            "/opsx:apply c Mind the docs. Its Touches overlap those of a.")


class TestVerify:
    def test_verifies_the_change(self):
        assert plan.stage_prompt("verify", "a", touches={"entries": ["src/a/**"]}) == "/opsx:verify a"

    def test_names_each_path_changed_and_not_declared(self):
        assert plan.stage_prompt("verify", "b", loose=["README.md", "docs/b.md"], touches={"entries": ["tests/**"]}) == (
            "/opsx:verify b Changed and not declared in its Touches: README.md, docs/b.md.")

    def test_a_change_that_declares_nothing_is_told_why(self):
        assert plan.stage_prompt("verify", "b", loose=["README.md"], touches={"missing": "its proposal.md has no `## Touches` heading"}) == (
            "/opsx:verify b Changed and not declared in its Touches: README.md. Its change declares no Touches: its "
            "proposal.md has no `## Touches` heading.")


def test_settle_names_what_reached_it():
    assert plan.stage_prompt("settle", "a", "Your branch is forecast to conflict with bolt/b on x.") == (
        "Settle a: Your branch is forecast to conflict with bolt/b on x.")


class TestMerge:
    T = {"kit": {"name": "switchboard-kit"}, "machine": "chuck-herdr-alpha"}

    def test_a_unit_merges_through_wt_merge_into_its_bolt(self):
        merge = plan.merge_command(self.T, {"sluice": False}, "tenant-environments")
        assert plan.stage_prompt("merge", "a", bolt="tenant-environments", merge=merge) == (
            "Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove")

    def test_a_kit_on_sluice_submits(self):
        assert plan.merge_command(self.T, {"sluice": True}, "b") == "wt submit bolt/b"

    def test_a_kit_crew_could_not_read_is_refused(self):
        with pytest.raises(plan.Refusal, match="its checkout on chuck-herdr-alpha was not read"):
            plan.merge_command(self.T, None, "b")
        with pytest.raises(plan.Refusal, match="whether switchboard-kit merges through sluice: its config is unreadable"):
            plan.merge_command(self.T, {"sluice": None, "sluice_error": "its config is unreadable"}, "b")


def test_what_reached_the_unit_is_carried_last():
    assert plan.stage_prompt("code", "d", carried=["Your branch is forecast to conflict."]) == (
        "/opsx:apply d Your branch is forecast to conflict.")


class TestEndsRow:
    @pytest.mark.parametrize("stage", ["construct", "code", "merge"])
    def test_acting_on_a_verified_unit_ends_its_verify_row(self, stage):
        assert plan.ends_row("e", stage, "verify", None, "verify") == "verify/e"

    @pytest.mark.parametrize("stage, st", [("verify", "verify"), ("settle", "verify"), ("construct", "planned"), ("code", "code")])
    def test_any_other_start_ends_none(self, stage, st):
        assert plan.ends_row("e", stage, st, None, st) == ""

    def test_construct_on_an_amended_intent_ends_the_verify_row_it_held_before(self):
        assert plan.ends_row("m", "construct", "amended", "intent", "verify") == "verify/m"
        assert plan.ends_row("m", "construct", "amended", "proposal/4", "code") == ""


class TestTeam:
    def test_the_team_holding_the_units_bolt_runs_its_stages(self):
        assert plan.unit_team(plan_of({"b": "swb-1"}, {"a": "b"}), "a") == "swb-1"

    def test_a_queued_unit_is_refused(self):
        with pytest.raises(plan.Refusal, match="unit a is queued: move it into a bolt first"):
            plan.unit_team(plan_of({}, {"a": None}), "a")

    def test_a_bolt_no_team_holds_is_refused(self):
        with pytest.raises(plan.Refusal, match="bolt b is held by no team yet: crew bolt give <team> b"):
            plan.unit_team(plan_of({"b": None}, {"a": "b"}), "a")


@pytest.mark.parametrize("stage, effort", [("construct", "high"), ("code", "xhigh"), ("verify", "high"), ("settle", "xhigh"),
                                           ("merge", "xhigh"), ("fix", "xhigh")])
def test_each_stage_starts_at_its_roles_effort(stage, effort):
    meta, _ = crew.definition(crew.STAGES[stage])
    assert (meta["model"], meta["effort"]) == ("claude-opus-5-5[1m]", effort)
