"""A unit amended in flight (plan.6, roles.1): crew unit amend on a plan in memory with the unit's stage given, who
may write it (plan.may_write), an amendment reaching a started bolt's place as a retry of its construct, and
plan.in_step for a plan whose descriptors predate the mark. An amendment through a proposal is the proposals journey's
(t-journey-plan)."""
import json
import pathlib

import pytest

from facts import FLEET, FactsWrite, apply, crossed_fleet, flume_plan, known, plan_text

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


def test_a_plan_from_before_the_mark_is_brought_in_step_once():
    old = plan.HEADER.replace(" Amended", "")
    p = plan.Plan(old + "\n%rec: Bolt\n\n")
    assert plan.in_step(p) is True
    assert "%allowed: Unit Repo Bolt Kind Intent After Source Amended" in p.text()
    assert plan.in_step(p) is False


class TestCrossed:
    """An approved amendment of a unit of a bolt given through Flume reaches its place as the approval's own act
    (Decision 7 of teams-cross-to-flume-as-their-bolts-land): a retry of its construct with the amendment's words once
    its place is launched, else a drop of its launch and a launch anew carrying the amendment; no mark, no conductor."""
    FLEET = crossed_fleet()
    FLUME = pathlib.Path(__file__).parent / "flume-0.3.6"

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "chuck@mac-studio")

    def reading(self, outcome=None, fixture=None, why=None):
        """deneb's runner as crew read it: request 1, a's launch, answered as given, its place's status a flume 0.3.6
        fixture."""
        if why:
            return {"deneb": {"host": "deneb", "branch": "madswan/runner/deneb", "tip": "a" * 40, "why": why}}
        status = json.loads((self.FLUME / f"{fixture}.json").read_text()) if fixture else None
        where = status["status"]["places"][0]["place"].split("@")[0] if status else "/crew/places/change--a"
        answers = {1: plan.Rec("Answer", [("Request", "1"), ("Outcome", outcome), ("Place", where), ("At", "2026-10-31T12:01:00Z")])} if outcome else {}
        places = {1: {"place": where, "at": "2026-10-31T12:02:00Z", "status": status, "why": None}} if status else {}
        return {"deneb": {"host": "deneb", "branch": "madswan/runner/deneb", "tip": "a" * 40, "why": None,
                          "runner": None, "answers": answers, "places": places}}

    def amend(self, runners, n=None, proposals=None):
        """a and b after it, launched on crossed crw-4's x as the give launched them, then a amended."""
        w = FactsWrite(flume_plan([("x", None, None)], [("a", "x", [], "unit", ["README.md"]), ("b", "x", ["a"], "unit", [])]),
                       runners=runners, label="madswan")
        w.plan.bolt("x").set("Team", "crw-4")
        w.plan.bolt("x").set("Path", "flume")
        plan.reach_places(self.FLEET, w, "x", self.FLEET["teams"]["crw-4"])
        if proposals:
            w.files["proposals.rec"] = proposals
        apply(w, 'unit amend a "Build a another way."', ctx=known(w, n=n, fleet=self.FLEET))
        rs = plan.Plan(w.files["requests.rec"]).recs("Request")[2:]
        return w, [{f: v for f, v in r.fields if f not in ("Date", "By")} for r in rs]

    def test_a_unit_in_code_is_a_retry_of_its_construct_with_the_amendments_words(self):
        """The user approves an amendment of a, whose place on crw-4's runner is in code."""
        w, new = self.amend(self.reading("launched", "code"))
        assert new == [{"Request": "3", "Act": "retry", "Host": "deneb", "Work": "unit/a", "Of": "1", "Stage": "construct",
                        "Words": "Build a another way. Sources: README.md. This unit's intent was amended by the user; revise the "
                                 "existing change to it."}]
        assert (w.plan.unit("a").get("Intent"), w.plan.unit("a").get("Amended")) == ("Build a another way.", None)

    def test_by_proposal_the_words_carry_the_planners_case(self):
        proposals = plan.PROPOSALS + "\nProposal: 4\nState: open\nDo: unit amend a \"Build a another way.\"\nCase: The rail reads it.\n"
        _, new = self.amend(self.reading("launched", "code"), n=4, proposals=proposals)
        assert new[0]["Words"].endswith("This unit's intent was amended by proposal 4; revise the existing change to it. "
                                        "The planner's case, as the user approved it: The rail reads it.")

    @pytest.mark.parametrize("outcome", ["held", "refused", None])
    def test_a_unit_not_yet_launched_is_dropped_and_launched_anew_and_its_dependent_with_it(self, outcome):
        _, new = self.amend(self.reading(outcome))
        assert [(r["Request"], r["Act"], r["Work"], r.get("Of"), r.get("After"), r.get("Brief")) for r in new] == [
            ("3", "drop", "unit/a", "1", None, None), ("4", "drop", "unit/b", "2", None, None),
            ("5", "launch", "unit/a", None, None, "Build a another way. Sources: README.md."),
            ("6", "launch", "unit/b", None, "5", "Build b.")]

    def test_a_runner_crew_cannot_read_refuses_the_amendment(self):
        with pytest.raises(plan.Refusal, match="^can't tell how far unit/a's place has got, so the amendment can't reach it: "
                                               "no runner answers on deneb: madswan/runner/deneb does not exist$"):
            self.amend({})
        with pytest.raises(plan.Refusal, match="the amendment can't reach it: deneb's runner can't be read"):
            self.amend(self.reading(why="deneb's runner can't be read: madswan/runner/deneb at aaaaaaa: it holds no runner.rec"))

    def test_a_place_that_has_merged_is_not_amended(self):
        with pytest.raises(plan.Refusal, match=r"^unit/a's place .* has merged into its bolt, so it is not amended"):
            self.amend(self.reading("launched", "landed"))
