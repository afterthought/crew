"""A unit amended in flight (plan.6, plan.15, roles.1): crew unit amend on a plan in memory with the unit's stage
given, who may write it (plan.may_write), plan.construct_again for the construct the amendment hands to its team's
host, plan.handed_state for where that construct stands for crew unit wait (code.9), plan.amend_told for what its
conductor is told, and plan.in_step for a plan whose descriptors predate the mark. That the
amendment's construct starts in the applier's name and its wait clears the mark is the journey's (t-journey-prompts);
an amendment through a proposal, the proposals journey's (t-journey-plan)."""
import pytest

from facts import FLEET, FactsWrite, apply, known, plan_text

import plan

KIT, TE = "switchboard-kit", "tenant-environments"


def fresh():
    return FactsWrite(plan_text(bolts=[(TE, KIT, "swb-1")], units=[("coding", KIT, TE, []), ("later", KIT, None, [])]))


def amend(unit, stage, n=None):
    w = fresh()
    apply(w, f'unit amend {unit} "Done another way."', ctx=known(w, stages={unit: stage}, n=n))
    u = w.plan.unit(unit)
    return u.get("Intent"), u.get("Amended")


class TestAmend:
    def test_a_queued_units_intent_is_replaced_and_nothing_else(self):
        assert amend("later", "ready") == ("Done another way.", None)

    def test_a_unit_with_a_worktree_is_marked_by_whoever_amends_it(self):
        assert amend("coding", "code") == ("Done another way.", "intent")
        assert amend("coding", "verify", n=4) == ("Done another way.", "proposal/4")

    @pytest.mark.parametrize("stage, said", [("merged", "has merged into its bolt"), ("landed", "has landed on main")])
    def test_merged_work_is_not_amended(self, stage, said):
        with pytest.raises(plan.Refusal, match=f"unit coding {said}, so it is not amended: a defect in it is a fix, and new work is a new unit"):
            amend("coding", stage)

    def test_a_unit_whose_stage_crew_cannot_tell_is_refused(self):
        with pytest.raises(plan.Refusal, match="cannot tell unit coding's stage: its host did not answer"):
            amend("coding", "unknown")


class TestWho:
    @pytest.mark.parametrize("agent, said", [
        ("wldn-planner", "the planner changes the plan through a proposal: crew plan propose, not crew unit amend"),
        ("swb-1-conductor", "swb-1-conductor does not write the plan with crew unit amend: tell wldn-planner, who proposes it")])
    def test_only_the_user_amends_directly(self, monkeypatch, agent, said):
        monkeypatch.setenv("CREW_AGENT", agent)
        with pytest.raises(plan.Refusal, match=said):
            plan.may_write(FLEET, ("unit", "amend"), None)

    def test_the_user_does(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "chuck@mac-studio")
        assert plan.may_write(FLEET, ("unit", "amend"), None) is None


class TestConstructAgain:
    @pytest.mark.parametrize("stage", ["planned", "code", "verify"])
    def test_an_agent_past_construct_is_ended_where_it_stands(self, stage):
        assert plan.construct_again("swb-1", "coding", stage, "proposal 4") == [
            "_construct-again", "swb-1", "coding", "--by", "proposal 4", "--force"]

    def test_a_construct_still_writing_the_change_is_not_ended(self):
        assert plan.construct_again("swb-1", "coding", "construct", "the user") == [
            "_construct-again", "swb-1", "coding", "--by", "the user"]


class TestHanded:
    """An amendment's command answers once its construct is handed to the team's host (plan.15, code.9); crew unit wait
    reads where that construct stands from its marker there."""

    def test_nothing_handed_or_one_that_started_leaves_the_wait_to_the_stage(self):
        assert plan.handed_state("b", None, False, 100.0) == (None, None)

    def test_one_whose_process_is_alive_or_not_yet_named_is_starting(self):
        said = "construct on unit b is starting on this host, handed there by proposal 4"
        assert plan.handed_state("b", {"by": "proposal 4", "at": 100.0, "pid": 7}, True, 500.0) == ("starting", said)
        assert plan.handed_state("b", {"by": "proposal 4", "at": 100.0}, False, 100.0 + plan.HAND_NAMED - 1) == ("starting", said)

    def test_one_that_could_not_start_says_why(self):
        assert plan.handed_state("b", {"by": "the user", "at": 1.0, "pid": 7, "failed": "swb-1 is down"}, False, 2.0) == (
            "failed", "construct did not start on unit b: swb-1 is down")

    def test_one_whose_process_ended_or_never_named_itself_is_gone(self):
        gone = ("gone", "construct handed to this host for unit b ended before it said whether it started (its words are "
                        "in /s/handed/b.log): crew unit run b construct runs it")
        assert plan.handed_state("b", {"by": "the user", "at": 1.0, "pid": 7, "log": "/s/handed/b.log"}, False, 2.0) == gone
        assert plan.handed_state("b", {"by": "the user", "at": 1.0, "log": "/s/handed/b.log"}, False, 1.0 + plan.HAND_NAMED) == gone


class TestTold:
    def test_the_conductor_waits_for_the_construct_that_started(self):
        assert plan.amend_told("coding", "the user", "swb-1-unit-1") == (
            "Unit coding's intent was amended by the user, and construct runs again on it in swb-1-unit-1: wait for it "
            "(crew unit wait coding); once it has committed, the unit goes on from its tasks.",
            "construct runs again on unit coding in swb-1-unit-1")

    def test_one_that_did_not_start_says_why_and_names_no_card(self):
        text, unsaid = plan.amend_told("in-verify", "proposal 1", None, "chuck-herdr-alpha did not answer (ssh: timed out)")
        assert text == ("Unit in-verify's intent was amended by proposal 1, and construct did not start: chuck-herdr-alpha did "
                        "not answer (ssh: timed out). Run it once it can (crew unit run in-verify construct); once it has "
                        "committed, the unit goes on from its tasks.")
        assert unsaid == "unit in-verify waits, amended, for construct to be run again"

    def test_a_team_taken_down_is_said(self):
        assert plan.amend_told("c", "the user", None, "swb-1 is down; crew up swb-1 brings it back")[0].endswith(
            "construct did not start: swb-1 is down; crew up swb-1 brings it back. Run it once it can (crew unit run c "
            "construct); once it has committed, the unit goes on from its tasks.")


def test_a_plan_from_before_the_mark_is_brought_in_step_once():
    old = plan.HEADER.replace(" Amended", "")
    p = plan.Plan(old + "\n%rec: Bolt\n\n")
    assert plan.in_step(p) is True
    assert "%allowed: Unit Repo Bolt Kind Intent After Source Amended" in p.text()
    assert plan.in_step(p) is False
