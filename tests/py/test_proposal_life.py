"""A proposal from its file to its close (plan.3, plan.4, roles.1): plan.read_proposal_file, who may propose
(plan.proposer_refusal), its number (plan.next_proposal), plan.open_proposal and plan.close in proposals.rec, whose
agreement it waits on (plan.agreements_wanted, plan.agreement_missing), a refused command as said and as recorded
(plan.command_refused), its page (plan.describe drawn alone, plan.amendment_lines, plan.page, plan.code_span), its
card's answers and the change Send applies with its boxes as they stand (plan.card_asks, card_answer, with_answer,
answered, kept, approved_words), and its card at each step (record 0031 §1): the chain's key
(plan.proposal_chain, chain_open), which act each step makes (plan.proposal_act), and what crew raises with it at each
step and at the rail's sweep (plan.raise_proposal_at, raise_proposal, proposal_facts, named_kit) on a stand-in for the
act. The commits, the tells and the approval's constructs are the
proposals journey's (t-journey-plan), and the card on the stub pendingyou the cards journey's (t-cards)."""
import pytest

from facts import FLEET, FactsWrite, apply, plan_text

import cards
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

    def test_a_launched_unit_of_a_bolt_given_through_flume_has_its_construct_retried(self):
        """bolt-teams "Plan writes reach a started bolt's places": the page says what the approval's write does."""
        s = {"stage": "verify", "worktree": None, "flume": {"stage": "verify", "place": "/flume/places/change--x"}}
        assert plan.amendment_lines(write().plan, self.A, s)[-1] == (
            "On approval: Flume runs its construct again with the new intent, and the unit goes on from its tasks with no "
            "approval asked, its revised change due for the next batch.")

    @pytest.mark.parametrize("stage", ["launching", "waiting"])
    def test_a_launch_flume_has_not_started_is_dropped_and_launched_again(self, stage):
        s = {"stage": stage, "worktree": None, "flume": {"stage": stage}}
        assert plan.amendment_lines(write().plan, self.A, s)[-1] == (
            "On approval: its launch, which Flume has not started, is dropped and launched again carrying the new intent.")

    def test_drawn_alone_it_reads_no_stage(self):
        assert plan.amendment_lines(write().plan, self.A, None) == ["**Amend unit `the-deploy-is-logged`** in bolt `tenant-environments` (swb-1)"]


class TestAnswers:
    """The card's questions are the approval and the new units (plan-proposals): what `crew plan answer` gathers of the
    card crew builds, and the change Send applies with its boxes as they stand (plan.card_asks, card_answer,
    with_answer, answered, kept, approved_words)."""
    BOLT = "y"

    def card(self, *dos):
        given = lambda: FactsWrite(plan_text(bolts=[(self.BOLT, KIT, None), ("z", KIT, None)],
                                             units=[(u, KIT, self.BOLT, []) for u in ("a", "x")]))
        argvs = args(*dos)
        b = cards.proposal_card(dict(n=4, state="open", case="The case.", before=given().plan, after=apply(given(), *dos).plan,
                                     argvs=argvs, waiting=[], session=None))
        return b, plan.card_asks(b["card"]), argvs

    def sent(self, dos, *answers):
        """Each (question, boxes) the user sent, gathered, then what Send applies: the commands and the words."""
        b, asks, argvs = self.card(*dos)
        held = {}
        for q, boxes in answers:
            held = plan.with_answer(held, 4, q, plan.card_answer(asks, b["card"].get("kind") == "choice", 4, q, boxes))
        waits, cleared = plan.answered(asks, held, b["boxes"])
        assert waits == []
        applied = plan.kept(argvs, cleared, 4)
        return [a.do for a in applied], cleared, plan.approved_words(applied, cleared)

    DROP_ADD = ('unit drop a "Replaced by three."', 'unit add b "B." --bolt y', 'unit add c "C." --bolt y', 'unit add d "D." --bolt y')

    def test_one_dropped_three_new_sent_as_it_stands_applies_the_proposal_whole(self):
        b, asks, _ = self.card(*self.DROP_ADD)
        assert asks == {"rows-1": ["add:b", "add:c", "add:d"]}
        dos, cleared, words = self.sent(self.DROP_ADD, ("rows-1", ["add:b", "add:c", "add:d"]))
        assert (dos, cleared) == (list(self.DROP_ADD), [])
        assert words == "Applied: added b, c and d; dropped a."

    def test_drops_alone_are_a_hold_to_approve_applied_whole_or_declined_with_a_note(self):
        drops = ('unit drop a "Superseded."', 'unit drop x "Done elsewhere."')
        b, asks, _ = self.card(*drops)
        assert (asks, b["boxes"]) == ({"plan": None}, [])
        assert b["card"]["summary"].endswith("to keep a unit it drops or amends, decline with a note.")
        assert self.sent(drops, ("plan", ["approve"])) == (list(drops), [], "Applied: dropped a and x.")
        declined = plan.with_answer({}, 4, "plan", plan.card_answer(asks, False, 4, "plan", ["decline"]), "keep x")
        assert declined == {"plan": "decline", "note": "keep x"}

    def test_a_new_unit_unticked_is_left_out_and_an_amendment_beside_it_applied(self):
        dos = ('unit amend x "X, done better."', 'unit add b "B." --bolt y', 'unit add c "C." --bolt y --after b')
        applied, cleared, words = self.sent(dos, ("rows-1", ["add:b"]))
        assert (applied, cleared) == (list(dos[:2]), ["c"])
        assert words == "Applied: added b; amended x. Left out on your word: c."

    def test_one_new_unit_is_the_choice_of_its_two_sides(self):
        one = ('unit add c "C." --bolt y',)
        assert self.card(*one)[1] == {"rows-1": ["add:c", "unticked"]}
        assert self.sent(one, ("rows-1", ["add:c"]))[:2] == (list(one), [])
        assert self.sent(one, ("rows-1", ["unticked"])) == ([], ["c"], "Nothing applied. Left out on your word: c.")

    def test_seven_new_units_wait_for_both_lists(self):
        seven = tuple(f'unit add s-{k} "S{k}." --bolt y' for k in range(1, 8))
        b, asks, _ = self.card(*seven)
        assert list(asks) == ["rows-1", "rows-2"]
        held = plan.with_answer({}, 4, "rows-1", asks["rows-1"])
        assert plan.answered(asks, held, b["boxes"]) == (["rows-2"], [])
        held = plan.with_answer(held, 4, "rows-2", asks["rows-2"][1:], "split s-5 later")
        assert plan.answered(asks, held, b["boxes"]) == ([], ["s-5"])
        assert held["note"] == "split s-5 later"

    def test_a_move_alone_is_a_hold_to_approve_applied_whole(self):
        move = ("unit order x --first",)
        assert self.card(*move)[1] == {"plan": None}
        assert self.sent(move, ("plan", ["approve"]))[:2] == (list(move), [])

    def test_sixteen_new_units_approved_on_their_hold_are_applied_every_one(self):
        sixteen = tuple(f'unit add h-{k} "H{k}." --bolt y' for k in range(1, 17))
        assert self.card(*sixteen)[1] == {"plan": None}
        assert self.sent(sixteen, ("plan", ["approve"]))[:2] == (list(sixteen), [])

    def test_an_answer_the_card_does_not_ask_for_is_refused(self):
        b, asks, _ = self.card(*self.DROP_ADD)
        assert refusal(plan.card_answer, asks, False, 7, "rows-2", ["add:b"]) == "proposal 7's card asks rows-1, not rows-2"
        assert refusal(plan.card_answer, asks, False, 7, "rows-1", ["add:zz"]) == "rows-1 holds add:b, add:c or add:d, not add:zz"
        assert refusal(plan.card_answer, asks, False, 7, "rows-1", ["keep:a", "add:b"]) == "rows-1 holds add:b, add:c or add:d, not keep:a"
        assert refusal(plan.card_answer, {"plan": None}, False, 7, "plan", ["maybe"]) == "plan is answered approve or decline"
        one = self.card('unit add c "C." --bolt y')[1]
        assert refusal(plan.card_answer, one, True, 3, "rows-1", ["add:c", "unticked"]) == "rows-1 is answered add:c or unticked"

    def test_the_same_answer_twice_is_fine_and_a_different_one_refused(self):
        held = plan.with_answer({}, 8, "rows-1", ["add:g-1", "add:g-2"])
        assert plan.with_answer(held, 8, "rows-1", ["add:g-2", "add:g-1"]) == held
        assert refusal(plan.with_answer, held, 8, "rows-1", ["add:g-1"]) == (
            "crew already holds rows-1 add:g-1 add:g-2 for proposal 8: the user answered it once")


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


# ------------------------------------------------------------------------------------------- the card's acts

def test_a_proposal_rewritten_twice_is_one_chain_keyed_by_its_first():
    pl = proposals_with(("One.", ["x"]))
    plan.open_proposal(pl, 2, "Two.", ["y"], "wldn-planner", TODAY, replaces=1, label="wldn")
    plan.open_proposal(pl, 3, "Three.", ["z"], "wldn-planner", TODAY, replaces=2, label="wldn")
    plan.open_proposal(pl, 4, "Four.", ["w"], "wldn-planner", TODAY)
    assert [plan.proposal_chain(pl, n) for n in (1, 3, 4)] == [[1], [1, 2, 3], [4]]
    assert (plan.chain_open(pl, 1), plan.chain_open(pl, 4), plan.chain_open(pl, 2)) == (3, 4, None)


class TestWhichAct:
    """Which act each step makes on the proposal's card (record 0031 §1): plan.proposal_act."""

    def test_the_planners_proposal_is_posted_once_accepted_and_the_users_own_has_no_card(self):
        assert plan.proposal_act("propose", 4, mine=True) == ("post",)
        assert plan.proposal_act("propose", 4, mine=False) is None

    def test_a_rewrite_changes_the_chains_card_after_the_users_note(self):
        assert plan.proposal_act("replace", 5, mine=True) == ("change", "Rewritten as proposal 5 after your note")

    def test_the_sweep_raises_the_planners_proposal_again_and_no_one_elses(self):
        assert plan.proposal_act("sweep", 5, mine=True) == ("change", "Raised again as the plan stands")
        assert plan.proposal_act("sweep", 5, mine=False) is None

    def test_the_users_rewrite_of_the_planners_proposal_withdraws_its_card(self):
        assert plan.proposal_act("replace", 5, mine=False, was_mine=True, by="chuck@mac-studio") == (
            "close", None, "Rewritten by chuck@mac-studio as proposal 5, which has no card")
        assert plan.proposal_act("replace", 5, mine=False, was_mine=False) is None

    def test_a_conductors_agreement_changes_it_to_say_it_no_longer_waits_on_that_conductor(self):
        assert plan.proposal_act("agree", 4, mine=True, agreed=["swb-1"]) == ("change", "No longer waits on swb-1-conductor")

    def test_a_card_is_changed_only_where_it_was_posted_or_on_the_planners_host(self):
        assert plan.proposal_act("agree", 4, mine=True, held=False, home=False, agreed=["swb-1"]) == ("skip",)
        assert plan.proposal_act("agree", 4, mine=True, held=True, home=False, agreed=["swb-1"])[0] == "change"
        assert plan.proposal_act("agree", 4, mine=True, held=False, home=True, agreed=["swb-1"])[0] == "change"

    def test_an_approval_closes_it_with_what_was_applied_and_a_drop_with_the_reason_or_as_dropped_on_the_users_note(self):
        assert plan.proposal_act("approve", 4, mine=True, outcome="Applied: added b.") == ("close", "Applied: added b.", None)
        assert plan.proposal_act("drop", 4, mine=True, reason="Not now.") == ("close", plan.DROPPED, "Not now.")
        assert plan.proposal_act("approve", 4, mine=False, outcome="x") is None


CARDED = dict(FLEET, partitions={"wldn": dict(FLEET["partitions"]["wldn"], teams=["swb-1"], state="WilldanGroup/crew-state",
                                              checkout="/w/willdan-blueprints/main", blueprints=["WilldanGroup/willdan-blueprints"])},
              teams={"swb-1": dict(FLEET["teams"]["swb-1"], kit={"name": KIT, "repo": f"WilldanGroup/{KIT}", "dir": f"/w/{KIT}",
                                                                 "main": f"/w/{KIT}/main"})})


class TestRaise:
    """What crew raises at each step (plan.raise_proposal_at), and at the rail's sweep (plan.raise_proposal): the act it calls, in the planner's name, under the chain's
    key, with the facts the proposal's builder takes and the kit's area; on a stand-in for the act and what it reads."""

    class Acts:
        def __init__(self, host="mac-studio", entries=()):
            self._host, self._entries = host, list(entries)

        def entries(self, label):
            return self._entries

        def host(self):
            return self._host

    @pytest.fixture(autouse=True)
    def acts(self, monkeypatch):
        self.called = []
        monkeypatch.setattr(plan, "recfix", lambda text, what: None)
        def act(name):
            def called(*a, **kw):  # the act builds the card first, as row_card_post and row_card_change do
                name == "row_card_close" or a[3](a[4])
                self.called.append((name, a, kw))
                return "req_1"
            return called
        for name in ("row_card_post", "row_card_change", "row_card_close"):
            monkeypatch.setattr(plan, name, act(name))

    def raised(self, pl, n, event, by_host="mac-studio", entries=(), **said):
        w = write()
        w.files["proposals.rec"] = pl.text()
        return plan.raise_proposal_at(CARDED, "wldn", w, n, event, self.Acts(by_host, entries), **said)

    DOS = ['unit add a-new "A new unit." --bolt console-pages']

    def test_the_planners_proposal_is_posted_in_its_name_under_its_key_in_its_kits_area(self):
        assert self.raised(proposals_with(("Console first.", self.DOS)), 1, "propose") == "req_1"
        (name, (fleet, label, owner, build, facts, where, acts), _), = self.called
        assert (name, label, owner, build) == ("row_card_post", "wldn", "wldn-planner", cards.proposal_card)
        assert where == (f"/w/{KIT}/main", f"github.com/WilldanGroup/{KIT}")
        assert (facts["n"], facts["first"], facts["waiting"], [a.unit for a in facts["argvs"]]) == (1, 1, [], ["a-new"])
        assert [u.name() for u in facts["after"].work_of("console-pages")] == ["a-new"]
        assert build(facts)["key"] == "proposal/1"

    def test_a_rewrite_changes_the_chains_card_to_the_successor(self):
        pl = proposals_with(("Console first.", self.DOS))
        plan.open_proposal(pl, 2, "Console last.", ['unit add b-new "B." --bolt console-pages'], "wldn-planner", TODAY, 1, "wldn")
        self.raised(pl, 2, "replace")
        (name, (_, _, owner, build, facts, note, _, _), _), = self.called
        assert (name, owner, facts["n"], facts["first"], note) == ("row_card_change", "wldn-planner", 2, 1, "Rewritten as proposal 2 after your note")
        assert build(facts)["key"] == "proposal/1" and build(facts)["boxes"][0]["unit"] == "b-new"

    def test_an_agreement_on_a_host_that_holds_no_card_changes_nothing_there(self, capsys):
        dos = ['unit add zone-first "The zone exists." --bolt tenant-environments --unblocks tenant-environments']
        assert self.raised(proposals_with(("Zone.", dos)), 1, "agree", "chuck-herdr-alpha", agreed=["swb-1"]) is None
        assert self.called == []
        assert capsys.readouterr().out == "card proposal/1 not changed here: wldn-planner holds it on mac-studio, and chuck-herdr-alpha holds none\n"
        held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_9"}]
        self.raised(proposals_with(("Zone.", dos)), 1, "agree", "chuck-herdr-alpha", held, agreed=["swb-1"])
        assert [(c[0], c[1][5]) for c in self.called] == [("row_card_change", "No longer waits on swb-1-conductor")]
        assert self.called[0][1][4]["waiting"] == ["swb-1"]

    def test_an_approval_of_a_rewrite_closes_the_chains_card_with_what_was_applied(self):
        pl = proposals_with(("Console first.", self.DOS))
        plan.open_proposal(pl, 2, "Console last.", self.DOS, "wldn-planner", TODAY, 1, "wldn")
        plan.close(plan.proposal(pl, 2, "wldn"), "approved", TODAY)
        self.raised(pl, 2, "approve", outcome="Applied: added a-new.")
        assert self.called == [("row_card_close", (CARDED, "wldn", "wldn-planner", "proposal/1"),
                                {"outcome": "Applied: added a-new.", "reason": None, "acts": self.called[0][2]["acts"]})]

    def swept(self, monkeypatch, pl, key):
        """The sweep's raise of the row keyed so, the branch's tip holding the plan and proposals.rec (pl)."""
        monkeypatch.setattr(plan, "fetch", lambda repo, ref, fresh=False: "tip")
        monkeypatch.setattr(plan, "read", lambda repo, ref, tip: write().plan)
        monkeypatch.setattr(plan, "show", lambda repo, tip, path: pl.text() if path == "proposals.rec" else None)
        return plan.raise_proposal(CARDED, {"label": "wldn", "key": key, "group": "proposals"}, self.Acts())

    def test_the_sweep_raises_the_chains_open_proposal_through_the_change_which_posts_a_card_missing_or_lost(self, monkeypatch):
        pl = proposals_with(("Console first.", self.DOS))
        plan.open_proposal(pl, 2, "Console last.", ['unit add b-new "B." --bolt console-pages'], "wldn-planner", TODAY, 1, "wldn")
        assert self.swept(monkeypatch, pl, "proposal/1") == "req_1"
        (name, (_, label, owner, build, facts, note, where, _), _), = self.called
        assert (name, label, owner, facts["n"], note) == ("row_card_change", "wldn", "wldn-planner", 2, "Raised again as the plan stands")
        assert build(facts)["key"] == "proposal/1" and where == (f"/w/{KIT}/main", f"github.com/WilldanGroup/{KIT}")

    def test_the_sweep_raises_nothing_once_the_chain_is_closed_or_for_a_key_that_is_no_chains(self, monkeypatch):
        pl = proposals_with(("Console first.", self.DOS))
        plan.close(plan.proposal(pl, 1, "wldn"), "approved", TODAY)
        assert self.swept(monkeypatch, pl, "proposal/1") is None
        assert self.swept(monkeypatch, pl, "proposal/7") is None and self.swept(monkeypatch, pl, "batch/1") is None
        assert self.called == []

    def test_the_users_own_proposal_raises_nothing(self):
        pl = plan.Plan(plan.PROPOSALS)
        plan.open_proposal(pl, 1, "Mine.", self.DOS, "chuck@mac-studio", TODAY)
        assert self.raised(pl, 1, "propose") is None and self.called == []

    def test_a_card_crew_cannot_build_refuses_nothing_of_the_proposal(self, capsys):
        pl = proposals_with(("Gone.", self.DOS))
        plan.close(plan.proposal(pl, 1, "wldn"), "dropped", TODAY, "not now")
        assert self.raised(pl, 1, "propose") is None
        assert capsys.readouterr().err == "card proposal/1 not raised: proposal 1 is dropped: it is closed, so it has no card\n"


def test_a_proposals_card_is_filed_in_the_kit_of_the_first_bolt_or_unit_it_names():
    given = write().plan
    assert plan.named_kit(given, args('bolt new b "B." --repo breadboard-kit', 'unit add u "U." --bolt b')) == "breadboard-kit"
    assert plan.named_kit(given, args("unit order queued-one --first")) == KIT
    assert plan.named_kit(given, args('unit add u "U." --bolt console-pages')) == KIT
    assert plan.named_kit(given, args('unit add u "U." --repo breadboard-kit')) == "breadboard-kit"


def test_a_rewritten_proposals_rail_row_carries_its_chains_key(monkeypatch):
    monkeypatch.setattr(plan.crew, "this_host", lambda: "mac-studio")
    row, = plan.rail_rows(FLEET, [], {}, [dict(label="wldn", proposal=3, first=1, by="wldn-planner", case="Third.", waiting=[],
                                               opened=TODAY)], {})
    assert (row["key"], row["what"][0], row["cmds"][0]) == ("proposal/1", "proposal 3 (wldn), by wldn-planner: Third.",
                                                            ("read", "crew plan proposed 3 --label wldn"))


def test_a_rewrite_after_the_users_note_acks_the_card_they_answered_and_its_new_version_follows_it(monkeypatch, capsys):
    """The rewrite goes through the act's change (row_card_change), which follows a card the user answered, on its
    stand-in for Pending You (test_card_commands.Acts): acked with the rewrite's note, the successor posted following it
    under the row's key with its revision, recorded under the row's key."""
    from test_card_commands import Acts
    monkeypatch.setattr(plan, "recfix", lambda text, what: None)
    pl = proposals_with(("Console first.", TestRaise.DOS))
    plan.open_proposal(pl, 2, "Console last.", ['unit add b-new "B." --bolt console-pages'], "wldn-planner", TODAY, 1, "wldn")
    w = write()
    w.files["proposals.rec"] = pl.text()
    held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_p1"}]
    acts = Acts({"get_request": ({"status": "answered", "turn": "agent", "version": 3}, None), "ack_answer": ({"version": 4}, None),
                 "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                 "post_request": ({"requestId": "req_p2", "version": 1}, None)}, held, caller="wldn-planner")
    assert plan.raise_proposal_at(CARDED, "wldn", w, 2, "replace", acts) == "req_p2"
    ack, = [a for t, a in acts.calls if t == "ack_answer"]
    post, = [a for t, a in acts.calls if t == "post_request"]
    assert (ack["requestId"], ack["outcome"]) == ("req_p1", "Rewritten as proposal 2 after your note")
    assert (post["idempotencyKey"], post["follows"], [o["id"] for o in post["options"]]) == ("proposal/1@wldn:2", "req_p1", ["add:b-new", "unticked"])
    assert [(e["Act"], e["Key"], e.get("Card")) for e in acts.emitted] == [("card.close", "proposal/1", "req_p1"), ("card.post", "proposal/1", "req_p2")]
    assert "update_request" not in [t for t, _ in acts.calls]


def rewritten_after_a_note(monkeypatch, *rewrites):
    """Proposal 1 (TestRaise.DOS, "Console first.") answered with a note on its card req_p1, then each rewrite, (case,
    dos), opened in turn and raised as a replace through the act on its stand-in for Pending You
    (test_card_commands.Acts), the run record growing with what each raise recorded: the acts of the last raise."""
    from test_card_commands import Acts
    monkeypatch.setattr(plan, "recfix", lambda text, what: None)
    pl = proposals_with(("Console first.", TestRaise.DOS))
    held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_p1", "At": "2026-10-23T13:10:00Z"}]
    note = {"status": "answered", "turn": "agent", "version": 3, "answer": {"approved": False, "note": "console last, and b-new"}}
    for n, (case, rewrite) in enumerate(rewrites, 2):
        plan.open_proposal(pl, n, case, rewrite, "wldn-planner", TODAY, n - 1, "wldn")
        w = write()
        w.files["proposals.rec"] = pl.text()
        acts = Acts({"get_request": (note, None), "ack_answer": ({"version": 4}, None),
                     "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                     "post_request": ({"requestId": f"req_p{n}", "version": 1}, None)}, held, caller="wldn-planner")
        plan.raise_proposal_at(CARDED, "wldn", w, n, "replace", acts)
        held = held + [dict(e, By=e["by"], At=f"2026-10-23T14:0{n}:00Z") for e in acts.emitted]
    return acts, held


def test_a_rewrite_after_the_users_note_opens_saying_what_they_answered_and_what_the_rewrite_changed(monkeypatch):
    """rail-cards "A proposal rewritten after the user's note": the card that follows says first what the user answered
    and what proposal 2 changed against proposal 1."""
    acts, _ = rewritten_after_a_note(monkeypatch, ("Console last.", ['unit add b-new "B." --bolt console-pages']))
    post, = [a for t, a in acts.calls if t == "post_request"]
    assert post["follows"] == "req_p1" and post["summary"].startswith(
        "You answered the card before this one, posted 2026-10-23 13:10 UTC, by ")
    assert ": declined, with a note. Since then: the planner rewrote it as proposal 2. It adds b-new. It no longer adds a-new. Its case is " \
           "rewritten." in post["summary"] and "console last, and b-new" not in repr(acts.emitted)
    assert acts.emitted[0]["Answer"] == "declined, with a note"


def test_a_rewrite_changing_neither_its_commands_nor_its_case_is_withheld_and_the_next_that_does_follows_the_answered_card(monkeypatch):
    """rail-cards "A proposal rewritten with nothing changed" and "Something changes after a withheld card"."""
    acts, held = rewritten_after_a_note(monkeypatch, ("Console first.", TestRaise.DOS))
    assert "post_request" not in [t for t, _ in acts.calls]
    assert [(e["Act"], e.get("Card"), e.get("State"), e["Key"]) for e in acts.emitted] == [
        ("card.close", "req_p1", "closed", "proposal/1"), ("card.post", "req_p1", "stands", "proposal/1")]
    assert acts.emitted[1]["refused"].startswith("Not posted: nothing has changed since the user answered req_p1 by ")
    # proposal 3, rewriting 2, adds unit w: posted following req_p1, whose answer stood
    acts, _ = rewritten_after_a_note(monkeypatch, ("Console first.", TestRaise.DOS),
                                     ("Console first.", TestRaise.DOS + ['unit add w "W." --bolt console-pages']))
    post, = [a for t, a in acts.calls if t == "post_request"]
    assert post["follows"] == "req_p1" and "Since then: the planner rewrote it as proposal 3. It adds w." in post["summary"]
    assert post["idempotencyKey"] == "proposal/1@wldn:2"


ASKS = "Why is this a unit at all? Isn't it the chore we already have?"


def dropped(status, cancelled=None):
    """Proposal 1 dropped with ASKS, the user's note, as its reason, while the chain's card req_p1 is in the status
    given, through the act's close on its stand-in for Pending You (test_card_commands.Acts): the calls it made and
    what it recorded."""
    from test_card_commands import Acts
    pl = proposals_with(("Console first.", TestRaise.DOS))
    plan.close(plan.proposal(pl, 1, "wldn"), "dropped", TODAY, ASKS)
    w = write()
    w.files["proposals.rec"] = pl.text()
    held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_p1"}]
    acts = Acts({"get_request": ({"status": status, "turn": "agent" if status == "answered" else "you", "version": 3}, None),
                 "ack_answer": ({"version": 4}, None), "cancel_request": ({"version": 4}, None)}, held, caller="wldn-planner")
    assert plan.raise_proposal_at(CARDED, "wldn", w, 1, "drop", acts, reason=ASKS) == "req_p1"
    assert plan.Plan(w.files["proposals.rec"]).recs("Proposal")[0].get("Reason") == ASKS
    return acts.calls[1:], [(e["Act"], e.get("State"), e.get("Outcome")) for e in acts.emitted]


def test_a_drop_acks_the_card_the_user_answered_as_dropped_on_their_note_whatever_their_note_asks():
    """Read on 2026-10-19: proposal 161 was dropped with the user's own note on its card as the reason, a question, and
    crew acked the card with it, which Pending You refused, "Your outcome asks your person something; put it on a new
    card with follows instead.", the card left answered and open on the rail with its proposal gone. The note stays
    whole on the proposal's record, and the card is acked saying it was dropped on it."""
    calls, emitted = dropped("answered")
    assert calls == [("ack_answer", {"requestId": "req_p1", "name": "wldn-planner", "expectedVersion": 3, "outcome": plan.DROPPED})]
    assert "?" not in plan.DROPPED and emitted == [("card.close", "closed", plan.DROPPED)]


def test_a_drop_withdraws_the_card_that_still_waits_with_the_reason():
    calls, emitted = dropped("pending")
    assert calls == [("cancel_request", {"requestId": "req_p1", "name": "wldn-planner", "reason": ASKS})]
    assert emitted == [("card.close", "withdrawn", ASKS)]


def rewritten_while_waiting(monkeypatch, first, second):
    """Proposal 1 (first, its Do lines) rewritten as proposal 2 (second) while the chain's card req_p1 waits on the
    user, through the act's change on its stand-in for Pending You (test_card_commands.Acts): the calls it made, by
    tool, and what it recorded."""
    from test_card_commands import Acts
    monkeypatch.setattr(plan, "recfix", lambda text, what: None)
    pl = proposals_with(("Console first.", first))
    plan.open_proposal(pl, 2, "Console last.", second, "wldn-planner", TODAY, 1, "wldn")
    w = write()
    w.files["proposals.rec"] = pl.text()
    held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_p1"}]
    acts = Acts({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None), "cancel_request": ({"version": 4}, None),
                 "update_request": ({"version": 4}, None), "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                 "post_request": ({"requestId": "req_p2", "version": 1}, None)}, held, caller="wldn-planner")
    assert plan.raise_proposal_at(CARDED, "wldn", w, 2, "replace", acts) in ("req_p1", "req_p2")
    calls = {}
    for t, a in acts.calls:
        calls.setdefault(t, []).append(a)
    return calls, [(e["Act"], e["Key"], e.get("Card"), e.get("State"), e.get("Outcome")) for e in acts.emitted]


def rows(*units):
    return [f'unit add {u} "{u}." --bolt console-pages' for u in units]


def test_a_rewrite_of_a_card_with_questions_while_it_waits_withdraws_it_and_its_new_version_follows_it(monkeypatch, capsys):
    """Read live on 2026-10-18 in test D: proposal 140 replaced 139 while 139's card waited, and crew changed that card
    in place, which Pending You's update_request does for its title and summary but never its questions: the card
    showed 140's title over 139's rows, and the user's answer carried a row of 139's that `crew plan answer 140 rows-1`
    refused. A proposal whose rows fill more than one list asks them as questions (rows-1, rows-2), so its rewrite withdraws the
    waiting card with the rewrite's note and posts the new version following it."""
    calls, emitted = rewritten_while_waiting(monkeypatch, rows("a-1", "a-2", "a-3", "a-4", "a-5", "a-6"),
                                             rows("a-1", "a-2", "a-3", "a-4", "a-5", "b-6"))
    assert "update_request" not in calls
    assert calls["cancel_request"] == [{"requestId": "req_p1", "name": "wldn-planner", "reason": "Rewritten as proposal 2 after your note"}]
    post, = calls["post_request"]
    assert (post["idempotencyKey"], post["follows"]) == ("proposal/1@wldn:2", "req_p1")
    assert [(q["id"], [o["id"] for o in q["options"]]) for q in post["questions"]] == [
        ("rows-1", ["add:a-1", "add:a-2", "add:a-3"]), ("rows-2", ["add:a-4", "add:a-5", "add:b-6"])]
    assert emitted == [("card.close", "proposal/1", "req_p1", "withdrawn", plan.REASKED), ("card.post", "proposal/1", "req_p2", None, None)]
    assert capsys.readouterr().out.startswith("card proposal/1: req_p1 withdrawn, its questions having to be asked anew, "
                                              "and its new version follows it\n")


def test_a_rewrite_of_a_card_without_questions_while_it_waits_still_changes_it_in_place(monkeypatch):
    calls, emitted = rewritten_while_waiting(monkeypatch, rows("a-1", "a-2"), rows("a-1", "b-2"))
    assert "cancel_request" not in calls and "post_request" not in calls
    change, = calls["update_request"]
    assert (change["requestId"], change["changeNote"], [o["id"] for o in change["options"]]) == (
        "req_p1", "Rewritten as proposal 2 after your note", ["add:a-1", "add:b-2"])
    assert emitted == [("card.update", "proposal/1", "req_p1", None, None)]


@pytest.mark.parametrize("first, second, asked", [
    (rows("a-1", "a-2", "a-3", "a-4", "a-5", "a-6"), rows("a-1", "a-2", "b-3"), "options"),
    (rows("a-1", "a-2", "a-3"), rows("a-1", "a-2", "a-3", "a-4", "a-5", "b-6"), "questions"),
    (["unit order queued-one --first"], rows("a-1", "a-2"), "options")],
    ids=["lists-to-one-list", "one-list-to-lists", "approve-to-one-list"])
def test_a_rewrite_that_moves_its_card_to_another_form_withdraws_it_while_it_waits_and_its_new_version_follows_it(
        monkeypatch, capsys, first, second, asked):
    """A rewrite whose card takes another form than the replaced proposal's, lists of questions to one list, one list
    to lists, a hold-to-approve to one list: update_request changes neither a card's kind nor its questions, so the
    waiting card is withdrawn with the rewrite's note and the new form posted following it."""
    calls, emitted = rewritten_while_waiting(monkeypatch, first, second)
    assert "update_request" not in calls
    assert calls["cancel_request"] == [{"requestId": "req_p1", "name": "wldn-planner", "reason": "Rewritten as proposal 2 after your note"}]
    post, = calls["post_request"]
    assert (post["idempotencyKey"], post["follows"], asked in post) == ("proposal/1@wldn:2", "req_p1", True)
    assert emitted == [("card.close", "proposal/1", "req_p1", "withdrawn", plan.RENEWED), ("card.post", "proposal/1", "req_p2", None, None)]
    assert capsys.readouterr().out.startswith("card proposal/1: req_p1 withdrawn, its kind having changed, and its new version follows it\n")


def test_an_agreement_on_a_card_with_questions_withdraws_it_while_it_waits_and_posts_it_again_following_it(monkeypatch):
    """The same proposal's card built again, its questions as they were, when a conductor agrees: followed all the
    same, since crew holds no copy of the card's questions to compare, accepted 2026-10-18 as churn a card of lists
    bears rarely."""
    from test_card_commands import Acts
    monkeypatch.setattr(plan, "recfix", lambda text, what: None)
    dos = [f'unit add z-{i} "z-{i}." --bolt tenant-environments' for i in range(1, 7)]
    w = write()
    w.files["proposals.rec"] = proposals_with(("Zone.", dos)).text()
    held = [{"Act": "card.post", "Key": "proposal/1", "By": "wldn-planner", "Card": "req_p1"}]
    acts = Acts({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None), "cancel_request": ({"version": 4}, None),
                 "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                 "post_request": ({"requestId": "req_p2", "version": 1}, None)}, held, caller="wldn-planner")
    assert plan.raise_proposal_at(CARDED, "wldn", w, 1, "agree", acts, agreed=["swb-1"]) == "req_p2"
    assert [t for t, _ in acts.calls] == ["get_request", "cancel_request", "match_area", "post_request"]
    assert acts.calls[1][1]["reason"] == "No longer waits on swb-1-conductor"
