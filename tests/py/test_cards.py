"""A crew agent's Pending You cards (the rail-cards and card-sessions specs, briefs.11 to briefs.15): crew's card hook
(plugin/hooks/cards), loaded as a module, on the result shapes it reads, the keys it records and the forms it refuses
(form_refusal, proposal_form); plan.card_refusal on whose key a card or an area may take, its reads given; and the
decisions of a card's plannotator session: plan.card_of, session_verdict, local_link, waited, card_folder,
judged_dead and young. Posting, closing and sweeping through the hook and the command are the review journey's
(t-journey-review)."""
import argparse
import datetime
import importlib.machinery
import importlib.util
import pathlib

import pytest

from facts import FLEET as BASE, FactsWrite, START, apply, plan_text

import crew
import plan

HOOK = pathlib.Path(__file__).resolve().parents[2] / "plugin" / "hooks" / "cards"
_loader = importlib.machinery.SourceFileLoader("cards_hook", str(HOOK))
cards = importlib.util.module_from_spec(importlib.util.spec_from_loader("cards_hook", _loader))
_loader.exec_module(cards)

KIT = {"name": "switchboard-kit", "repo": "WilldanGroup/switchboard-kit", "main": "/kit/main", "dir": "/kit"}
FLEET = {"partitions": {"wldn": dict(BASE["partitions"]["wldn"], teams=["swb-1", "swb-2", "atl-1"]),
                        "madswan": {"label": "madswan", "machine": "mac-studio", "teams": ["apk-1"]}},
         "teams": {"swb-1": dict(BASE["teams"]["swb-1"], kit=KIT), "swb-2": dict(BASE["teams"]["swb-2"], kit=KIT),
                   "atl-1": {"name": "atl-1", "label": "wldn", "machine": "mac-studio",
                             "kit": {"name": "atlas-kit", "repo": "WilldanGroup/atlas-kit", "main": "/a/main", "dir": "/a"}},
                   "brd-1": {"name": "brd-1", "label": "wldn", "machine": "chuck-herdr-alpha",
                             "kit": {"name": "breadboard-kit", "repo": "WilldanGroup/breadboard-kit", "main": "/b/main", "dir": "/b"}},
                   "apk-1": {"name": "apk-1", "label": "madswan", "machine": "mac-studio",
                             "kit": {"name": "flywheel-next", "repo": "agentplot/flywheel-next", "main": "/f/main", "dir": "/f"}}},
         "hosts": {}}
FLEET["partitions"]["wldn"]["teams"].append("brd-1")


class Reads:
    def __init__(self, proposals=("proposal/1",), batches=("batch/1-1", "batch/2"), here="mac-studio", ops=()):
        self.p, self.b, self.h, self.o = list(proposals), list(batches), here, list(ops)

    def open_proposals(self):
        return list(self.p)

    def batch_keys(self):
        return list(self.b)

    def plan(self):
        return plan.Plan(plan_text(bolts=[("tenant-environments", "switchboard-kit", "swb-1"), ("console-pages", "switchboard-kit", "swb-2")],
                                   units=[("x", "switchboard-kit", "tenant-environments", []), ("checked", "switchboard-kit", "tenant-environments", []),
                                          ("z", "switchboard-kit", "console-pages", [])]))

    def ops_keys(self):
        return list(self.o)

    def here(self):
        return self.h


def key(name, k, tool="post_request", label="wldn", **reads):
    return plan.card_refusal(FLEET, name, label, tool, k, Reads(**reads))


ROWS = ("land/tenant-environments/<head>, the head from the `card:` line under its row in "
        f"`{crew.HOME}/plugin/bin/crew rail --label wldn`")


class TestKeys:
    def test_the_users_own_card_is_never_checked(self):
        assert key("chuck@mac-studio", "anything") is None

    def test_a_card_needs_a_key(self):
        assert key("swb-1-conductor", None) == "crew refuses a card with no idempotencyKey."

    def test_a_teams_ops_and_slots_own_no_card_key(self):
        assert "swb-1-ops owns no card key, since a team's cards are its conductor's" in key("swb-1-ops", "land/tenant-environments/abc1234")
        assert "in your proof file, under Left for the user" in key("swb-1-ops", "x")
        assert f"{crew.HOME}/plugin/bin/crew needs" in key("swb-1-unit-2", "verify/x/20261007-1412")

    def test_a_conductor_posts_under_its_own_bolts_landing_row_and_never_a_verify_reports(self):
        assert key("swb-1-conductor", "land/tenant-environments/abc1234") is None
        for k in ("gateway-check", "verify/checked/20261007-1412", "verify/z/20261007-1412", "land/console-pages/abc1234", "review/x/abc1234", "land/tenant-environments"):
            assert key("swb-1-conductor", k) == f"crew refuses a card under {k}: swb-1-conductor posts a card only under a rail row's key of its own: {ROWS}."
        assert key("brd-1-conductor", "land/x/abc1234").endswith("brd-1 holds no bolt, so none is.")

    def test_the_planner_posts_under_an_open_proposal_or_an_open_batch_card(self):
        assert key("wldn-planner", "proposal/1") is None and key("wldn-planner", "batch/2") is None and key("wldn-planner", "batch/1-1") is None
        assert key("wldn-planner", "proposal/2") == (
            "crew refuses a card under proposal/2: wldn-planner posts a card only under proposal/<n> for a proposal of wldn open now, "
            f"or batch/<n> for one of its batches open now, proposal/1, batch/1-1 or batch/2, from the `card:` line under its row in "
            f"`{crew.HOME}/plugin/bin/crew rail --label wldn`.")
        assert key("wldn-planner", "batch/1").endswith("proposal/1, batch/1-1 or batch/2, from the `card:` line under its row in "
                                                      f"`{crew.HOME}/plugin/bin/crew rail --label wldn`.")

    def test_the_design_agent_posts_for_a_decision_record_of_a_kit_its_partition_builds(self):
        assert key("wldn-design", "record/atlas-kit/0021/abc1234") is None
        said = ("wldn-design posts a card only for a decision record, under record/<kit>/<number>/<commit> for a kit of wldn's, "
                "atlas-kit, breadboard-kit or switchboard-kit, the commit the one that proposed the record or its amendment.")
        for k in ("record/flywheel-next/0003/abc1234", "proposal/1", "record/atlas-kit/21/abc1234", "record/atlas-kit/0021/ABC1234"):
            assert key("wldn-design", k) == f"crew refuses a card under {k}: {said}"
        assert key("madswan-design", "record/flywheel-next/0003/abc1234", label="madswan") is None

    def test_main_level_ops_posts_its_operations_cards_where_they_are_kept(self):
        assert key("wldn-ops", "op/dev/1", ops=["op/dev/1"]) is None
        assert "wldn-ops posts its operations' cards on mac-studio" in key("wldn-ops", "op/dev/1", here="chuck-herdr-alpha")
        assert "operations row's key of wldn open now, and none is open" in key("wldn-ops", "land/x/abc1234")

    def test_an_area_is_made_only_under_a_kit_of_the_agents_own(self):
        assert key("swb-1-conductor", "create-area:WilldanGroup/switchboard-kit", "create_area") is None
        assert key("swb-1-conductor", "area:swb-1-conductor", "create_area") == (
            "crew refuses an area under area:swb-1-conductor: swb-1-conductor makes a kit's area only under create-area:WilldanGroup/switchboard-kit.")
        assert key("wldn-planner", "create-area:WilldanGroup/atlas-kit", "create_area") is None
        assert "only under create-area:WilldanGroup/atlas-kit, create-area:WilldanGroup/breadboard-kit or create-area:WilldanGroup/switchboard-kit" in (
            key("wldn-planner", "create-area:agentplot/flywheel-next", "create_area"))

    def test_any_other_agent_owns_no_key(self):
        assert "wldn-operator-mac-studio owns no card key, since only the planner, the conductors, main-level ops" in key("wldn-operator-mac-studio", "x")


class TestResult:
    @pytest.mark.parametrize("result", [
        {"content": [{"type": "text", "text": "Posted."}], "structuredContent": {"requestId": "req_a-1"}},
        [{"type": "text", "text": '{"requestId": "req_a-1", "version": 1}'}],
        {"content": [{"type": "text", "text": "not json"}, {"type": "text", "text": '{"requestId": "req_a-1"}'}]},
        '{"requestId":"req_a-1","status":"pending"}'])
    def test_the_card_id_is_read_from_every_shape_of_a_tools_result(self, result):
        assert cards.result_object(result)["requestId"] == "req_a-1"

    def test_an_error_or_a_denial_is_a_failure(self):
        assert cards.failed({"isError": True}) and cards.failed({"deny": "not yours"}) and not cards.failed({"structuredContent": {}})

    @pytest.mark.parametrize("k, row", [
        ("verify/x/20261007-1400", "unit/x"), ("land/tenant-environments/abc1234", "bolt/tenant-environments"), ("proposal/4", "proposal/4"),
        ("batch/3", "batch/3"), ("batch/3-2", "batch/3"), ("record/atlas-kit/0021/abc1234", "record/atlas-kit/0021"),
        ("my own key", None), ("land/tenant-environments", None), ("review/x/abc1234", None)])
    def test_a_card_is_on_its_rows_object_and_any_other_on_its_agent(self, k, row):
        assert cards.keyed(k)[1] == row

    def test_pending_you_is_known_under_any_server_name(self):
        assert cards.is_pending_you("pendingyou") and cards.is_pending_you("plugin_pendingyou_pendingyou") and not cards.is_pending_you("github")


LANDING = {"kind": "approve", "highStakes": True}
TWO = {"options": [{"id": "fix", "label": "Fix both"}, {"id": "merge", "label": "Merge as it is"}]}


def form(k, given, update=False, units=None):
    return cards.form_refusal(k, given, update, units)


class TestForms:
    def test_a_landing_card_is_a_high_stakes_approval_with_no_step_that_lands_it(self):
        assert form("land/b/abc1234", LANDING) is None
        assert form("land/b/abc1234", dict(LANDING, action={"steps": [{"text": "Open the gateway on your Mac"}]})) is None
        said = form("land/b/abc1234", {"kind": "action", "action": {"steps": [{"text": "Land the bolt", "command": "crew bolt land b"}]}})
        assert said.startswith("crew refuses card land/b/abc1234. A landing's card is an approval")
        assert 'This card is an "action", is not marked high stakes, and has a step that lands the bolt: "Land the bolt crew bolt land b". Post it again' in said
        assert form("land/b/abc1234", {"kind": "approve"}).endswith("This card is not marked high stakes. Post it again in that form.")
        assert "This card has options." in form("land/b/abc1234", dict(LANDING, **TWO))
        assert "has a step that lands the bolt" in form("land/b/abc1234", dict(LANDING, action={"steps": [{"text": "Merge with wt merge main"}]}))

    def test_a_verify_reports_card_has_no_form_since_none_is_posted_and_one_posted_before_changes_unchecked(self):
        assert not cards.formed("verify/x/20261007-1412") and cards.formed("land/b/abc1234")

    def test_a_record_card_is_a_low_risk_reversible_approval(self):
        accept = {"kind": "approve", "approve": {"action": "Accept record 0021", "risk": "low", "reversible": True}}
        assert form("record/atlas-kit/0021/abc1234", accept) is None
        assert 'This card is a "choice", has options, and has no approve block.' in form("record/atlas-kit/0021/abc1234", dict(kind="choice", **TWO))
        assert 'This card has risk "high".' in form("record/atlas-kit/0021/abc1234", {**accept, "approve": {**accept["approve"], "risk": "high"}})
        assert "This card is not reversible." in form("record/atlas-kit/0021/abc1234", {**accept, "approve": {**accept["approve"], "reversible": False}})

    BATCH = {"kind": "fyi", "summary": "This is batch 2 of wldn.",
             "context": {"background": "Read the whole batch.\n\nx1 (swb-1)\nWhat x1 does.\n\nx2 (swb-1)\nWhat x2 does.\n\nz1 (swb-2)\nWhat z1 does.",
                         "links": [{"label": "Read batch 2", "url": "http://mac-studio:19432"}]}}

    def test_a_batch_card_is_one_notice_naming_every_unit_with_one_link_and_nothing_to_answer(self):
        units = ["x1", "x2", "z1"]
        assert form("batch/2", self.BATCH, units=units) is None
        assert 'This card is a "multi", and has options.' in form("batch/2", dict(self.BATCH, kind="multi", **TWO), units=units)
        assert 'This card is an "approve", and approves something.' in form("batch/2", dict(self.BATCH, kind="approve", approve={"action": "x"}), units=units)
        assert "This card attaches its summary." in form("batch/2", dict(self.BATCH, artifacts=[{"kind": "code"}]), units=units)
        fenced = dict(self.BATCH, context=dict(self.BATCH["context"], background="```\n" + self.BATCH["context"]["background"] + "\n```"))
        assert "puts its summary in a code block, which scrolls sideways on the phone" in form("batch/2", fenced, units=units)
        assert "This card leaves out z1." in form("batch/2", dict(self.BATCH, context=dict(self.BATCH["context"], background="x1 x2")), units=units)
        assert "This card leaves out x1, x2 and z1." in form("batch/2", {"kind": "fyi"}, units=units)
        three = dict(self.BATCH, context=dict(self.BATCH["context"], links=[{"url": "a"}, {"url": "b"}]))
        assert "links more than one session; a batch has one reading session" in form("batch/2", three, units=units)

    def test_no_rows_card_asks_a_question_in_words(self):
        said = form("land/b/abc1234", dict(LANDING, text={"placeholder": "Anything else?"}))
        assert "This card asks a question in words, which Pending You makes required. The card's note is where the user's words go." in said

    def test_a_change_is_checked_for_what_it_changes(self):
        assert form("land/b/abc1234", {"highStakes": False}, update=True) == (
            "crew refuses this change to card land/b/abc1234. A landing's card is an approval, kind \"approve\", marked high stakes "
            "with highStakes true, whose yes has you tell main-level ops to land; it has no options, and no step or command for the user "
            "to land it. This change clears its high stakes. Change the card without it.")
        assert form("land/b/abc1234", {"title": "Land it"}, update=True) is None
        assert "This change gives it options." in form("proposal/1", TWO, update=True)
        assert 'This change gives it risk "medium".' in form("record/atlas-kit/0021/abc1234", {"approve": {"risk": "medium", "reversible": True}}, update=True)

    def test_an_old_batch_cards_form_is_read_as_it_was_posted(self):
        assert cards.formed("batch/2") and cards.formed("proposal/1") and not cards.formed("batch/1-1") and not cards.formed("agent-note")


def proposal_card(*dos):
    w = FactsWrite(plan_text(bolts=[("t", "switchboard-kit", None)], units=[("x", "switchboard-kit", "t", [])]))
    pl = plan.Plan(plan.PROPOSALS)
    plan.open_proposal(pl, 4, "Case.", list(dos), "wldn-planner", "2026-10-12")
    return plan.card_model(BASE, "wldn", w, plan.proposal(pl, 4, "wldn"), after=apply(FactsWrite(w.plan.text()), *dos).plan)


class TestProposalForm:
    SHOWN = "`crew plan card 4 --label wldn`"

    def test_a_proposal_making_no_unit_new_is_a_plain_approval(self):
        m = proposal_card('unit amend x "Unit x, again."')
        assert cards.proposal_form(4, m, {"kind": "approve"}, self.SHOWN) is None
        for given, said in (({"kind": "review"}, 'This card is a "review".'), ({"kind": "approve", **TWO}, "This card has options."),
                            ({"kind": "approve", "action": {"steps": [{"text": "Read it"}]}}, "This card has steps for the user to take."),
                            ({"questions": [{"id": "go", "kind": "approve"}]}, "This card is a grouped card of questions.")):
            assert said in cards.proposal_form(4, m, given, self.SHOWN)

    def test_one_with_new_units_asks_plan_and_each_new_unit_once(self):
        m = proposal_card('unit add pb "B." --repo switchboard-kit', 'unit add pc "C." --repo switchboard-kit')
        card = m["card"]
        assert cards.proposal_form(4, m, card, self.SHOWN) is None
        less = dict(card, questions=[card["questions"][0], dict(card["questions"][1], options=card["questions"][1]["options"][:1])])
        assert "This card does not ask about pc, new to a bolt in proposal 4." in cards.proposal_form(4, m, less, self.SHOWN)
        words = dict(card, questions=card["questions"] + [{"id": "notes", "kind": "text"}])
        assert "The card's note is where the user's words go." in cards.proposal_form(4, m, words, self.SHOWN)
        assert "This card asks no questions, as a plain approval." in cards.proposal_form(4, m, {"kind": "approve"}, self.SHOWN)
        first = dict(card, questions=[dict(card["questions"][0], kind="choice"), card["questions"][1]])
        assert 'This card does not ask `plan`, of kind "approve", first.' in cards.proposal_form(4, m, first, self.SHOWN)

    def test_a_lone_new_unit_is_a_choice(self):
        m = proposal_card('unit add g "G." --repo switchboard-kit')
        multi = dict(m["card"], questions=[m["card"]["questions"][0], dict(m["card"]["questions"][1], kind="multi")])
        assert 'This card asks units-1, which is no question of its new units of kind "choice".' in cards.proposal_form(4, m, multi, self.SHOWN)


class TestSessions:
    def args(self, k, unit=None, sub="session", label="wldn"):
        return argparse.Namespace(key=k, unit=unit, sub=sub, label=label)

    def test_a_card_command_runs_on_a_rails_key_for_its_partition(self):
        label, d = plan.card_of(BASE, self.args("batch/1"))
        assert (label, d) == ("wldn", plan.CARDS / "wldn" / "batch/1")
        assert plan.card_of(BASE, self.args("batch/2-1", "x1"))[1] == plan.CARDS / "wldn" / "batch/2-1" / "x1"

    @pytest.mark.parametrize("k, unit, said", [
        ("land/t", None, "land/t is not a card key"), ("verify/x/HEAD", None, "verify/x/HEAD is not a card key"),
        ("batch/1", "x1", "a batch has one reading session, on the whole batch: crew card session batch/1"),
        ("batch/2-1", None, "a batch card posted as cards of five has a session for each of its units: crew card session batch/2-1 <unit>"),
        ("proposal/1", "x1", "only an old batch card's key, batch/<n>-<k>, takes a unit, and proposal/1 is not one")])
    def test_any_other_is_refused(self, k, unit, said):
        with pytest.raises(plan.Refusal, match=said):
            plan.card_of(BASE, self.args(k, unit))

    def test_with_no_partition_it_is_refused(self, monkeypatch):
        monkeypatch.delenv("CREW_LABEL", raising=False)
        with pytest.raises(plan.Refusal, match="crew card runs as the card's partition"):
            plan.card_of(dict(BASE, partitions={**BASE["partitions"], "madswan": {}}), self.args("proposal/1", label=None))

    @pytest.mark.parametrize("serves, decided, verdict", [
        (True, None, "serving"), (False, ("approved", "Ship it."), "decided"), (False, ("annotated", "x"), "decided"),
        (False, ("dismissed", None), "dismissed"), (False, None, "ended")])
    def test_a_recorded_session_is_given_again_kept_for_its_wait_or_started_anew(self, serves, decided, verdict):
        assert plan.session_verdict({"pid": 9}, serves, decided) == verdict

    @pytest.mark.parametrize("url, local", [("http://localhost:19432", True), ("http://127.0.0.1:19432", True),
                                            ("http://[::1]:19432", True), ("http://mac-studio.ts.swancloud.net:19432", False)])
    def test_a_link_only_its_host_could_open_is_refused(self, url, local):
        assert plan.local_link(url) is local

    def test_a_wait_says_the_decision_with_the_users_words_as_they_are(self):
        assert plan.waited("verify/x/1", ("approved", 'Ship it — the "tenant" part reads well.'), True) == (
            'verify/x/1: approved\nShip it — the "tenant" part reads well.')
        assert plan.waited("proposal/1", ("approved", None), True) == "proposal/1: approved"
        assert plan.waited("v", ("dismissed", None), True) == "v: closed in plannotator with no decision"
        assert plan.waited("v", None, True) is None
        assert plan.waited("v", None, False) == "v: crew ended its session, as its card closed or crew card end was run"

    @pytest.mark.parametrize("rel, found", [
        ("proposal/1", ("proposal/1", None)), ("batch/1", ("batch/1", None)), ("batch/2-1/x1", ("batch/2-1", "x1")),
        ("verify/x/20261012-1200", ("verify/x/20261012-1200", None)), ("verify/x", None), ("batch/2-1/X1", None)])
    def test_a_sessions_folder_names_its_key_and_an_old_batch_cards_unit(self, rel, found):
        assert plan.card_folder(pathlib.PurePosixPath(rel)) == found

    def test_a_sweep_ends_a_session_no_live_row_holds_unless_blind_and_once_it_is_two_minutes_old(self):
        assert plan.judged_dead(("proposal/2", None), {"proposal/1"}, ["batch/"])
        assert not plan.judged_dead(("proposal/1", None), {"proposal/1"}, [])
        assert not plan.judged_dead(("batch/1", None), set(), ["batch/"])
        assert not plan.judged_dead(None, set(), [])
        now = START + datetime.timedelta(minutes=10)
        assert plan.young("2026-10-12T10:09:00Z", now) and not plan.young("2026-10-12T10:00:00Z", now)


class TestSessionWords:
    def test_a_landing_key_has_no_session_and_a_batch_cards_runs_on_the_main_levels_host(self):
        assert plan.session_refusal("land/b/abc1234", "wldn", "box", "box") == "a landing card has no document to read, so it has no session"
        assert plan.session_refusal("batch/1", "wldn", "chuck-herdr-alpha", "mac-studio") == (
            "batch/1's reading session runs on chuck-herdr-alpha, where wldn's main level writes the batch's summary: run crew card session batch/1 there")
        assert plan.session_refusal("batch/2-1", "wldn", "chuck-herdr-alpha", "mac-studio") is None
        assert plan.session_refusal("verify/x/20261012-1200", "wldn", "chuck-herdr-alpha", "mac-studio") is None

    def test_a_key_with_no_row_says_its_row_is_gone_or_which_host_did_not_answer(self):
        assert plan.no_row("wldn", "verify/x/1", []) == "no row of wldn's rail has the card key verify/x/1: its row is gone, so its card has nothing to read"
        assert plan.no_row("wldn", "verify/x/1", ["box did not answer (ssh)"]) == (
            "no row of wldn's rail has the card key verify/x/1, and whether one would can't be known: box did not answer (ssh)")

    def test_an_end_that_ends_nothing_says_why(self):
        s = {"pid": 42, "document": "/r/v.md"}
        assert plan.end_said("v", s, None, "plannotator sessions: its registry is locked") == (
            "crew can't read plannotator's sessions (plannotator sessions: its registry is locked): it ended nothing, and keeps v to end later")
        assert plan.end_said("v", None, {}, None) == "no session was recorded for v; its folder is removed"
        assert plan.end_said("v", s, {}, None) == "plannotator lists no session of pid 42 on /r/v.md: crew ended nothing, and v is forgotten"

    def test_a_session_gone_undecided_ends_its_wait(self):
        assert plan.waited("v", None, True, gone=True) == "v: the session ended with no decision"

    def test_a_batch_whose_change_can_not_be_read_names_the_unit_and_the_host(self):
        t = {"name": "atl-1", "machine": "mac-studio", "kit": {"main": "/a/main"}}
        assert plan.unread_change(t, "z1", "abc1234", 255, "ssh: connect to host mac-studio port 22: Operation timed out\n") == (
            "crew can't read z1's change: mac-studio, atl-1's host, did not answer (ssh: connect to host mac-studio port 22: Operation timed out)")
        assert plan.unread_change(t, "z1", "abc1234", 1, "abc1234 is not a commit of /a/main\n") == (
            "crew can't read z1's change at abc1234 in /a/main on mac-studio: abc1234 is not a commit of /a/main")
        assert plan.unread_change(t, "z1", "abc1234", 0, "") is None


def test_a_proposal_opens_by_its_number_and_prints_no_json_beside_it():
    assert plan.open_refusal(None, True, False) == "--open needs a proposal's number: crew plan proposed <n> --open"
    assert plan.open_refusal(1, True, True) == "--open shows the proposal in plannotator and --json prints it: use one"
    assert plan.open_refusal(1, True, False) is None
