"""A proposal from its file to its close (plan.3, plan.4, roles.1): plan.read_proposal_file, who may propose
(plan.proposer_refusal), its number (plan.next_proposal), plan.open_proposal and plan.close in proposals.rec, whose
agreement it waits on (plan.agreements_wanted, plan.agreement_missing), a refused command as said and as recorded
(plan.command_refused), its page (plan.describe drawn alone, plan.amendment_lines, plan.page, plan.code_span), its
card's answers and the change Send applies with its boxes as they stand (plan.card_asks, card_answer, with_answer,
answered, as_they_stand, approved_words), and its card at each step (record 0031 §1): the chain's key
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

    def test_drawn_alone_it_reads_no_stage(self):
        assert plan.amendment_lines(write().plan, self.A, None) == ["**Amend unit `the-deploy-is-logged`** in bolt `tenant-environments` (swb-1)"]


class TestAnswers:
    """The card's questions are the approval and the new units (plan-proposals): what `crew plan answer` gathers of the
    card crew builds, and the change Send applies with its boxes as they stand (plan.card_asks, card_answer,
    with_answer, answered, as_they_stand, approved_words)."""
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
        waits, cleared, keep = plan.answered(asks, held, b["boxes"])
        assert waits == []
        applied = plan.as_they_stand(argvs, cleared, keep, 4)
        return [a.do for a in applied], cleared, keep, plan.approved_words(argvs, applied, cleared, keep)

    DROP_ADD = ('unit drop a "Replaced by three."', 'unit add b "B." --bolt y', 'unit add c "C." --bolt y', 'unit add d "D." --bolt y')

    def test_one_dropped_three_new_sent_as_it_stands_applies_the_proposal_whole(self):
        b, asks, _ = self.card(*self.DROP_ADD)
        assert asks == {"rows-1": ["keep:a", "add:b", "add:c", "add:d"]}
        dos, cleared, keep, words = self.sent(self.DROP_ADD, ("rows-1", ["add:b", "add:c", "add:d"]))
        assert (dos, cleared, keep) == (list(self.DROP_ADD), [], [])
        assert words == "Applied: added b, c and d; dropped a."

    def test_how_to_object_to_a_drop_tick_keep_and_the_rest_is_applied(self):
        dos, cleared, keep, words = self.sent(self.DROP_ADD, ("rows-1", ["keep:a", "add:b", "add:c", "add:d"]))
        assert (dos, keep) == (list(self.DROP_ADD[1:]), ["a"])
        assert words == "Applied: added b, c and d. Kept on your word: a."

    def test_a_new_unit_unticked_is_left_out_and_an_amendment_ticked_is_not_applied(self):
        dos = ('unit amend x "X, done better."', 'unit add b "B." --bolt y', 'unit add c "C." --bolt y --after b')
        applied, cleared, keep, words = self.sent(dos, ("rows-1", ["old:x", "add:b"]))
        assert (applied, cleared, keep) == ([dos[1]], ["c"], ["x"])
        assert words == "Applied: added b. Left out on your word: c. Kept the old intent of x."

    def test_one_new_unit_is_the_choice_of_its_two_sides(self):
        one = ('unit add c "C." --bolt y',)
        assert self.card(*one)[1] == {"rows-1": ["add:c", "unticked"]}
        assert self.sent(one, ("rows-1", ["add:c"]))[:2] == (list(one), [])
        assert self.sent(one, ("rows-1", ["unticked"]))[:3] == ([], ["c"], [])
        assert self.sent(one, ("rows-1", ["unticked"]))[3] == "Nothing applied. Left out on your word: c."

    def test_seven_new_units_wait_for_both_lists(self):
        seven = tuple(f'unit add s-{k} "S{k}." --bolt y' for k in range(1, 8))
        b, asks, _ = self.card(*seven)
        assert list(asks) == ["rows-1", "rows-2"]
        held = plan.with_answer({}, 4, "rows-1", asks["rows-1"])
        assert plan.answered(asks, held, b["boxes"]) == (["rows-2"], [], [])
        held = plan.with_answer(held, 4, "rows-2", asks["rows-2"][1:], "split s-5 later")
        assert plan.answered(asks, held, b["boxes"]) == ([], ["s-5"], [])
        assert held["note"] == "split s-5 later"

    def test_a_move_alone_is_a_hold_to_approve_applied_whole(self):
        move = ("unit order x --first",)
        assert self.card(*move)[1] == {"plan": None}
        assert self.sent(move, ("plan", ["approve"]))[:3] == (list(move), [], [])

    def test_an_answer_the_card_does_not_ask_for_is_refused(self):
        b, asks, _ = self.card(*self.DROP_ADD)
        assert refusal(plan.card_answer, asks, False, 7, "rows-2", ["add:b"]) == "proposal 7's card asks rows-1, not rows-2"
        assert refusal(plan.card_answer, asks, False, 7, "rows-1", ["add:zz"]) == "rows-1 holds keep:a, add:b, add:c or add:d, not add:zz"
        assert refusal(plan.card_answer, {"plan": None}, False, 7, "plan", ["maybe"]) == "plan is answered approve or decline"
        one = self.card('unit add c "C." --bolt y')[1]
        assert refusal(plan.card_answer, one, True, 3, "rows-1", ["add:c", "unticked"]) == "rows-1 is answered add:c or unticked"

    def test_the_same_answer_twice_is_fine_and_a_different_one_refused(self):
        held = plan.with_answer({}, 8, "rows-1", ["add:g-1", "add:g-2"])
        assert plan.with_answer(held, 8, "rows-1", ["add:g-2", "add:g-1"]) == held
        assert refusal(plan.with_answer, held, 8, "rows-1", ["add:g-1"]) == (
            "crew already holds rows-1 add:g-1 add:g-2 for proposal 8: the user answered it once")

    def test_a_kept_unit_the_proposal_neither_drops_nor_amends_is_refused(self):
        assert refusal(plan.as_they_stand, args(*self.DROP_ADD), [], ["b"], 4) == (
            "proposal 4 neither drops nor amends b, so the user can't keep it as it was: the units it drops or amends are a")


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

    def test_an_approval_closes_it_with_what_was_applied_and_a_drop_withdraws_it_with_the_reason(self):
        assert plan.proposal_act("approve", 4, mine=True, outcome="Applied: added b.") == ("close", "Applied: added b.", None)
        assert plan.proposal_act("drop", 4, mine=True, reason="Not now.") == ("close", None, "Not now.")
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
        monkeypatch.setattr(plan, "fetch", lambda repo, ref: "tip")
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


def test_a_rewritten_proposals_rail_row_and_the_planners_card_check_carry_its_chains_key(monkeypatch):
    monkeypatch.setattr(plan.crew, "this_host", lambda: "mac-studio")
    row, = plan.rail_rows(FLEET, [], {}, [dict(label="wldn", proposal=3, first=1, by="wldn-planner", case="Third.", waiting=[],
                                               opened=TODAY)], {})
    assert (row["key"], row["what"][0], row["cmds"][0]) == ("proposal/1", "proposal 3 (wldn), by wldn-planner: Third.",
                                                            ("read", "crew plan proposed 3 --label wldn"))
    pl = proposals_with(("One.", ["x"]), ("Other.", ["y"]))
    plan.open_proposal(pl, 3, "Three.", ["z"], "wldn-planner", TODAY, replaces=1, label="wldn")
    monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("WilldanGroup/crew-state", "wldn/main"))
    monkeypatch.setattr(plan, "fetch", lambda repo, ref: "tip")
    monkeypatch.setattr(plan, "show", lambda repo, tip, path: pl.text())
    assert plan.CardReads(FLEET, "wldn").open_proposals() == ["proposal/2", "proposal/1"]


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
    assert (post["idempotencyKey"], post["follows"], [o["id"] for o in post["options"]]) == ("proposal/1:2", "req_p1", ["add:b-new", "unticked"])
    assert [(e["Act"], e["Key"], e.get("Card")) for e in acts.emitted] == [("card.close", "proposal/1", "req_p1"), ("card.post", "proposal/1", "req_p2")]
    assert "update_request" not in [t for t, _ in acts.calls]
