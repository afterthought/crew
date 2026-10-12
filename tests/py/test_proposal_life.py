"""A proposal from its file to its close (plan.3, plan.4, roles.1): plan.read_proposal_file, who may propose
(plan.proposer_refusal), its number (plan.next_proposal), plan.open_proposal and plan.close in proposals.rec, whose
agreement it waits on (plan.agreements_wanted, plan.agreement_missing), a refused command as said and as recorded
(plan.command_refused), its page (plan.describe drawn alone, plan.amendment_lines, plan.page, plan.code_span), and its
card's answers (plan.card_answer, plan.with_answer, plan.answered). The commits, the tells and the approval's
constructs are the proposals journey's (t-journey-plan)."""
import pytest

from facts import FLEET, FactsWrite, plan_text

import plan

KIT, TE, CP = "switchboard-kit", "tenant-environments", "console-pages"
TODAY = "2026-10-12"


def write():
    return FactsWrite(plan_text(
        bolts=[(TE, KIT, "swb-1"), (CP, KIT, None)],
        units=[("the-deploy-names-its-host-tenant", KIT, TE, []), ("the-deploy-is-logged", KIT, TE, []), ("queued-one", KIT, None, [])]))


def args(*dos):
    return [plan.do_args("wldn", d) for d in dos]


def proposals_with(*opened):
    """proposals.rec with each (case, dos) opened in turn by the planner."""
    pl = plan.Plan(plan.PROPOSALS)
    for case, dos in opened:
        plan.open_proposal(pl, plan.next_proposal(pl), case, dos, "wldn-planner", TODAY)
    return pl


def refusal(fn, *a, **kw):
    with pytest.raises(plan.Refusal) as e:
        fn(*a, **kw)
    return str(e.value)


class TestFile:
    def test_one_record_of_a_case_and_its_commands(self, tmp_path):
        f = tmp_path / "p.rec"
        f.write_text("Case: Two findings belong together,\n+ and the queued work joins them.\nDo: unit move queued-one console-pages\n")
        assert plan.read_proposal_file(f) == ("Two findings belong together,\nand the queued work joins them.", ["unit move queued-one console-pages"])

    @pytest.mark.parametrize("text, said", [
        ("", "holds 0 records"), ("Case: x\nDo: y\nWhy: z\n", "has fields a proposal file doesn't: Why; only Case and Do"),
        ("Do: y\n", "needs one Case"), ("Case: x\n", "has no Do")])
    def test_anything_else_is_refused(self, tmp_path, text, said):
        f = tmp_path / "p.rec"
        f.write_text(text)
        assert said in refusal(plan.read_proposal_file, f)


def test_only_the_planner_and_the_user_propose():
    assert plan.proposer_refusal(FLEET, "swb-1-conductor", "conductor", "swb-1") == (
        "swb-1-conductor does not write proposals: tell wldn-planner, who proposes changes to the plan")


class TestOpen:
    def test_a_proposal_is_written_open_with_the_next_number(self):
        pl = proposals_with(("Case one.", ["unit move queued-one console-pages"]), ("Case two.", ["unit order queued-one --first"]))
        p = plan.proposal(pl, 2, "wldn")
        assert [p.get(f) for f in ("Case", "State", "Opened", "By")] == ["Case two.", "open", TODAY, "wldn-planner"]
        assert p.all("Do") == ["unit order queued-one --first"]
        assert plan.next_proposal(pl) == 3

    def test_a_number_is_never_reused(self):
        pl = proposals_with(("One.", ["x"]))
        plan.close(plan.proposal(pl, 1, "wldn"), "dropped", TODAY, "not now")
        assert plan.next_proposal(pl) == 2

    def test_a_replacement_drops_the_open_one_and_carries_none_of_its_agreements(self):
        pl = proposals_with(("Four.", ["x"]))
        plan.proposal(pl, 1, "wldn").add("Agreed", "swb-1", after="Do")
        assert plan.open_proposal(pl, 2, "Five.", ["y"], "wldn-planner", TODAY, replaces=1, label="wldn") == "wldn-planner"
        old, new = plan.proposal(pl, 1, "wldn"), plan.proposal(pl, 2, "wldn")
        assert [old.get(f) for f in ("State", "Closed", "Reason")] == ["dropped", TODAY, "replaced by proposal 2"]
        assert (new.get("Replaces"), new.all("Agreed")) == ("1", [])

    def test_only_an_open_proposal_is_replaced(self):
        pl = proposals_with(("One.", ["x"]))
        plan.close(plan.proposal(pl, 1, "wldn"), "approved", TODAY)
        assert refusal(plan.open_proposal, pl, 2, "Two.", ["y"], "wldn-planner", TODAY, 1, "wldn") == "proposal 1 is approved, so nothing replaces it"


class TestClose:
    def test_an_approval_records_the_units_the_user_left_out(self):
        p = plan.proposal(proposals_with(("One.", ["x"])), 1, "wldn")
        plan.close(p, "approved", TODAY, cleared=["c-clear"])
        assert [p.get("State"), p.get("Closed"), p.all("Cleared")] == ["approved", TODAY, ["c-clear"]]

    def test_a_drop_records_its_reason(self):
        p = plan.proposal(proposals_with(("One.", ["x"])), 1, "wldn")
        plan.close(p, "dropped", TODAY, "the console waits")
        assert [p.get("State"), p.get("Reason")] == ["dropped", "the console waits"]
        assert refusal(plan.close, p, "dropped", TODAY, "again") == "proposal 1 is dropped, so it can't be dropped"


class TestAgreement:
    DOS = args('unit add zone-first "The zone exists." --bolt tenant-environments --unblocks tenant-environments')

    def p(self, agreed=()):
        p = plan.proposal(proposals_with(("Zone.", [a.do for a in self.DOS])), 1, "wldn")
        for t in agreed:
            p.add("Agreed", t, after="Do")
        return p

    def test_the_conductor_of_a_bolt_it_touches_agrees_once(self):
        assert plan.agreements_wanted(write().plan, self.DOS, self.p(), 1, "conductor", "swb-1") == ["swb-1"]
        assert plan.agreements_wanted(write().plan, self.DOS, self.p(["swb-1"]), 1, "conductor", "swb-1") == []

    def test_a_conductor_whose_bolt_it_does_not_touch_is_refused(self):
        assert refusal(plan.agreements_wanted, write().plan, self.DOS, self.p(), 1, "conductor", "swb-2") == (
            "proposal 1 touches no bolt swb-2 holds: it touches the bolts of swb-1")

    def test_no_other_agent_agrees(self):
        assert refusal(plan.agreements_wanted, write().plan, self.DOS, self.p(), 1, "design", "wldn", None, "wldn-design") == (
            "wldn-design does not agree to proposals: the conductor of a bolt a proposal touches agrees to it")

    def test_the_user_agrees_for_every_team_it_touches_or_one_named(self):
        assert plan.agreements_wanted(write().plan, self.DOS, self.p(), 1, "user", None) == ["swb-1"]
        assert refusal(plan.agreements_wanted, write().plan, self.DOS, self.p(), 1, "user", None, "swb-2") == "proposal 1 touches no bolt swb-2 holds"

    def test_approval_waits_on_each_conductor_whose_bolt_is_held_now(self):
        assert plan.agreement_missing(write().plan, self.DOS, self.p(), 1) == (
            "proposal 1 waits on the agreement of swb-1-conductor: crew plan agree 1")
        assert plan.agreement_missing(write().plan, self.DOS, self.p(["swb-1"]), 1) is None
        given = write().plan
        given.bolt(CP).set("Team", "swb-2")
        dos = args('unit add a-page "The console has a page." --bolt console-pages')
        assert plan.agreement_missing(given, dos, self.p(), 1) == "proposal 1 waits on the agreement of swb-2-conductor: crew plan agree 1"


def test_a_refused_command_is_recorded_without_the_words_typed_in_it():
    a, = args('unit add y "Typed ZQXA." --bolt nowhere')
    said, recorded = plan.command_refused(a, plan.Refusal("no bolt nowhere in wldn/main"))
    assert said == '`unit add y "Typed ZQXA." --bolt nowhere`: no bolt nowhere in wldn/main'
    assert recorded == "`unit add y`: no bolt nowhere in wldn/main"


class TestPage:
    DOS = ['bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit',
           'unit add a-plan-only-deploy-is-checked "A plan-only deploy is checked." --bolt deploy-checks',
           'unit move queued-one deploy-checks']

    def page(self, dos, agreed=()):
        p = plan.proposal(proposals_with(("Two findings about the deploy belong together.", dos)), 1, "wldn")
        for t in agreed:
            p.add("Agreed", t, after="Do")
        d = plan.describe(FLEET, "wldn", write().plan, p, alone=True)
        return d, plan.page(d, "wldn")

    def test_each_change_reads_in_plain_words_with_the_command_approval_runs(self):
        d, out = self.page(self.DOS)
        for line in ["# Proposal 1 — open, by wldn-planner, " + TODAY, "1. **New bolt `deploy-checks`** in switchboard-kit",
                     "   Goal: The deploy is checked before it runs.",
                     "2. **New unit `a-plan-only-deploy-is-checked`** in bolt `deploy-checks` (new in this proposal)",
                     "3. **Move unit `queued-one`** from the queue to bolt `deploy-checks` (new in this proposal)", "   Intent: Unit queued-one.",
                     '   Runs: `crew bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit`',
                     "   Runs: `crew unit move queued-one deploy-checks`", "- the user, to approve it or say what to change"]:
            assert line in out.splitlines()
        assert "crew plan approve" not in out
        assert d["changes"][2]["do"] == "unit move queued-one deploy-checks"

    def test_work_a_held_bolt_needs_says_so_and_waits_on_its_conductor(self):
        d, out = self.page(['unit add zone-first "The tenant\'s zone exists." --bolt tenant-environments --unblocks tenant-environments'])
        assert "1. **New unit `zone-first`** in bolt `tenant-environments`, held by swb-1" in out
        assert "   Unblocks: bolt `tenant-environments`, which can't be proven or land without it" in out
        assert "   Bolt's goal: Goal of tenant-environments." in out
        assert "- swb-1-conductor, to agree, or tell wldn-planner why not" in out
        assert "- agreed: swb-1" in self.page([d["changes"][0]["do"]], ["swb-1"])[1]

    def test_a_closed_proposal_says_when_and_why(self):
        p = plan.proposal(proposals_with(("x", ["unit order queued-one --first"])), 1, "wldn")
        plan.close(p, "dropped", TODAY, "not now")
        assert plan.page(plan.describe(FLEET, "wldn", write().plan, p, alone=True), "wldn").endswith(f"Closed {TODAY}: not now.\n")

    def test_a_command_holding_a_backtick_is_fenced_longer_than_it(self):
        assert plan.code_span('crew unit add ticks "The `x` command works."') == '``crew unit add ticks "The `x` command works."``'
        assert plan.code_span("`x`") == "`` `x` ``"


class TestAmendment:
    A, = args('unit amend the-deploy-is-logged "The deploy writes a log the operator can search."')

    def test_a_unit_with_a_change_shows_both_intents_its_stage_and_what_follows(self):
        assert plan.amendment_lines(write().plan, self.A, {"stage": "code", "worktree": "/kit/places/x"}) == [
            "**Amend unit `the-deploy-is-logged`** in bolt `tenant-environments` (swb-1), now in code",
            "Intent, as it stands: Unit the-deploy-is-logged.",
            "Intent, as proposed:  The deploy writes a log the operator can search.",
            "On approval: construct runs again at once in swb-1's slot, and once that has committed the unit goes on from "
            "its tasks with no approval asked, its revised change due for the next batch."]

    def test_one_with_no_change_yet_only_has_its_intent_replaced(self):
        assert plan.amendment_lines(write().plan, self.A, {"stage": "ready", "worktree": None})[-1] == (
            "On approval: its intent is replaced; it has no change written yet, so nothing else changes.")

    def test_drawn_alone_it_reads_no_stage(self):
        assert plan.amendment_lines(write().plan, self.A, None) == ["**Amend unit `the-deploy-is-logged`** in bolt `tenant-environments` (swb-1)"]


class TestAnswers:
    ASKS = {"plan": None, "units-1": ["f-1", "f-2"]}

    def test_an_answer_the_card_does_not_ask_for_is_refused(self):
        assert refusal(plan.card_answer, self.ASKS, False, 7, "units-2", ["f-1"]) == "proposal 7's card asks plan or units-1, not units-2"
        assert refusal(plan.card_answer, self.ASKS, False, 7, "units-1", ["zz"]) == "units-1 holds f-1 or f-2, not zz"
        assert refusal(plan.card_answer, self.ASKS, False, 7, "plan", ["maybe"]) == "plan is answered approve or decline"
        assert refusal(plan.card_answer, {"plan": None, "units-1": ["g-one"]}, True, 3, "units-1", ["x"]) == "units-1 is answered g-one or leave-out"

    def test_a_lone_unit_left_out_is_none_ticked(self):
        assert plan.card_answer({"plan": None, "units-1": ["g-one"]}, True, 3, "units-1", ["leave-out"]) == []

    def test_the_approval_waits_for_every_question_then_clears_each_unit_left_unticked(self):
        held = plan.with_answer({}, 7, "plan", "approve")
        assert plan.answered(self.ASKS, held, ["f-1", "f-2"]) == (["units-1"], [])
        held = plan.with_answer(held, 7, "units-1", ["f-1"], "split f-1 in two later")
        assert plan.answered(self.ASKS, held, ["f-1", "f-2"]) == ([], ["f-2"])
        assert held["note"] == "split f-1 in two later"

    def test_the_same_answer_twice_is_fine_and_a_different_one_refused(self):
        held = plan.with_answer({}, 8, "units-1", ["g-1", "g-2"])
        assert plan.with_answer(held, 8, "units-1", ["g-2", "g-1"]) == held
        assert refusal(plan.with_answer, held, 8, "units-1", ["g-1"]) == (
            "crew already holds units-1 g-1 g-2 for proposal 8: the user answered it once")


def test_a_closed_proposal_is_not_approved_and_its_reason_is_not_recorded():
    p = plan.proposal(proposals_with(("x", ["unit order queued-one --first"])), 1, "wldn")
    assert plan.closed_refusal(p, 1) is None
    plan.close(p, "dropped", TODAY, "Dropped ZQXF.")
    assert plan.closed_refusal(p, 1) == ("proposal 1 is dropped: Dropped ZQXF.", "proposal 1 is dropped")


class TestSignalOnThePage:
    SIG = "2026-10-12-chuck-mac-studio-abcd1234/01-deploys-are-dry-run"

    def page(self, signal_of, alone=False):
        dos = [f'unit add deploys-dry-run-first "A deploy is dry-run before it runs." --repo switchboard-kit --signal {self.SIG}']
        p = plan.proposal(proposals_with(("The user asked for it.", dos)), 1, "wldn")
        return plan.page(plan.describe(FLEET, "wldn", write().plan, p, alone=alone, signal_of=signal_of), "wldn")

    def test_a_unit_from_a_signal_shows_its_assertion_and_its_excerpt_with_the_excerpts_grade(self):
        text = f'---\nsignal: {self.SIG}\nkind: ask\n---\n\nDeploys should be dry-run first.\n\n> "Deploys should be dry-run first." — 14:00:00Z\n'
        out = self.page(lambda sig: (*plan.asserted(text), "own"))
        assert f'From: signals/{self.SIG}: "Deploys should be dry-run first."' in out
        assert 'Excerpt (own): > "Deploys should be dry-run first." — 14:00:00Z' in out

    def test_a_signal_crew_cannot_read_is_named_alone_and_a_card_reads_none(self):
        assert f"From: signals/{self.SIG}\n" in self.page(lambda sig: (None, None, None)) + "\n"
        assert "From: signals/" not in self.page(lambda sig: pytest.fail("a card reads no signal"), alone=True)
