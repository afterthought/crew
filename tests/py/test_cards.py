"""A crew agent's Pending You cards (the rail-cards and card-sessions specs, briefs.11 to briefs.17): crew's card hook
(plugin/hooks/cards), loaded as a module, on the result shapes it reads, the keys it records, the forms it refuses
(form_refusal, proposal_form) and a call in another agent's name, on any Pending You tool (name_refusal), with the
matcher that runs it; plan.card_refusal on whose key a card or an area may take, its reads given; and the
decisions of a card's plannotator session: plan.card_of, session_verdict, local_link, waited, card_folder,
judged_dead and young; the six cards crew builds from their events' facts, the words rule, what a card follows and
the act's decisions (record 0031); and crew record's: a record's facts and the status its file holds
(plan.record_facts), its refusals made on the teams file alone (record_status) and its raise (raise_record). Posting, closing and sweeping through the hook and the command are the review
journey's (t-journey-review)."""
import argparse
import datetime
import importlib.machinery
import importlib.util
import json
import pathlib
import re

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
        assert "Tell swb-1-conductor what you wait on with crew tell." in key("swb-1-ops", "x")
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

    def test_the_design_agent_posts_for_a_decision_record_of_a_kit_its_partition_builds_under_the_records_key(self):
        assert key("wldn-design", "record/atlas-kit/0021") is None
        said = ("wldn-design posts a card only for a decision record, under record/<kit>/<number> for a kit of wldn's, "
                "atlas-kit, breadboard-kit or switchboard-kit, the number the record's four digits.")
        for k in ("record/flywheel-next/0003", "proposal/1", "record/atlas-kit/21", "record/atlas-kit/0021/abc1234"):
            assert key("wldn-design", k) == f"crew refuses a card under {k}: {said}"
        assert key("madswan-design", "record/flywheel-next/0003", label="madswan") is None

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
        ("batch/3", "batch/3"), ("batch/3-2", "batch/3"), ("record/atlas-kit/0021", "record/atlas-kit/0021"),
        ("record/atlas-kit/0021/abc1234", None),
        ("my own key", None), ("land/tenant-environments", None), ("review/x/abc1234", None)])
    def test_a_card_is_on_its_rows_object_and_any_other_on_its_agent(self, k, row):
        assert cards.keyed(k)[1] == row

    def test_pending_you_is_known_under_any_server_name(self):
        assert cards.is_pending_you("pendingyou") and cards.is_pending_you("plugin_pendingyou_pendingyou") and not cards.is_pending_you("github")


REROUTES = ("Pending You labels a session by the name its latest call gives, so a call in another agent's name reroutes that "
            "agent's answers to this session.")


def hooked(tool, given, server="pendingyou"):
    return {"session_id": None, "hook_event_name": "PreToolUse", "tool_name": f"mcp__{server}__{tool}", "tool_input": given}


class TestNames:
    """briefs.17: on 2026-10-15 one session read swancloud-ops's cards under its name and took its deploy approvals, and
    another took swancloud-planner's answers so, since Pending You labels a session by the name its latest call gives."""

    def test_a_whoami_in_another_agents_name_is_refused_naming_the_agents_own_and_why(self):
        assert cards.name_refusal("swancloud-design", "whoami", {"name": "swancloud-ops"}) == (
            f'crew refuses this whoami: it gives name "swancloud-ops", and this session is swancloud-design\'s. {REROUTES} '
            "Call it again in your own name, swancloud-design.")

    @pytest.mark.parametrize("tool, given, gives", [
        ("get_request", {"requestId": "req_a-1", "name": "swancloud-planner"}, 'name "swancloud-planner"'),
        ("list_pending", {"name": "swancloud-planner"}, 'name "swancloud-planner"'),
        ("ack_answer", {"requestId": "req_a-1", "expectedVersion": 2, "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("cancel_request", {"requestId": "req_a-1", "reason": "done", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("reply_in_thread", {"requestId": "req_a-1", "body": "x", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("update_request", {"requestId": "req_a-1", "expectedVersion": 1, "changeNote": "new", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("hand_back", {"requestId": "req_a-1", "found": "nothing yet", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("answer_delegated", {"requestId": "req_a-1", "expectedVersion": 1, "why": "I read it", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("get_attachment", {"attachmentId": "att_1", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("set_wake_webhook", {"url": "https://x", "name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("report_setup", {"source": "claude-code", "name": "Claude"}, 'name "Claude"'),
        ("match_area", {"cwd": "/w", "task": "swancloud-ops"}, 'task "swancloud-ops"'),
        ("post_request", {"idempotencyKey": "x", "session": {"label": "swancloud-ops", "machine": "mac-studio"}}, 'session.label "swancloud-ops"'),
        ("a_tool_pending_you_adds", {"name": "swancloud-ops"}, 'name "swancloud-ops"'),
        ("whoami", {"name": "swancloud-design", "previousName": "swancloud-ops"}, 'previousName "swancloud-ops"'),
        ("whoami", {"name": "swancloud-ops", "previousName": "swancloud-planner"}, 'name "swancloud-ops" and previousName "swancloud-planner"'),
        ("whoami", {"name": ""}, 'name ""'),
        ("list_pending", {"name": None}, "name null")])
    def test_every_tool_that_names_its_caller_is_refused_in_any_name_but_the_agents_own(self, tool, given, gives):
        said = cards.name_refusal("swancloud-design", tool, given)
        assert said.startswith(f"crew refuses this {tool}: it gives {gives}, and this session is swancloud-design's. {REROUTES}")
        assert said.endswith("or with no previousName." if "previousName" in gives else "Call it again in your own name, swancloud-design.")

    @pytest.mark.parametrize("tool, given", [
        ("whoami", {"name": "swancloud-design", "about": "records"}),
        ("whoami", {"name": "swancloud-design", "previousName": "swancloud-design"}),
        ("list_pending", {"name": "swancloud-design"}),
        ("match_area", {"cwd": "/w", "remote": "github.com/x/y", "task": "swancloud-design"}),
        ("post_request", {"idempotencyKey": "x", "name": "swancloud-design", "session": {"label": "swancloud-design"}})])
    def test_a_call_in_the_agents_own_name_passes(self, tool, given):
        assert cards.name_refusal("swancloud-design", tool, given) is None

    @pytest.mark.parametrize("tool, given", [
        ("get_request", {"requestId": "req_a-1"}), ("list_pending", {}), ("list_areas", {}), ("whoami", {"guide": True}),
        ("match_area", {"cwd": "/w"}), ("post_request", {"idempotencyKey": "x", "session": {"machine": "mac-studio"}})])
    def test_a_call_that_names_no_caller_passes_since_it_claims_no_agents_name(self, tool, given):
        assert cards.name_refusal("swancloud-design", tool, given) is None

    @pytest.mark.parametrize("tool", ["create_area", "rename_area", "suggest_area_name"])
    def test_an_areas_name_is_not_the_callers(self, tool):
        assert cards.name_refusal("swancloud-design", tool, {"areaId": "prj_1", "name": "crew"}) is None

    def test_the_hook_refuses_a_crew_agents_call_in_another_name_on_any_pending_you_tool_and_nothing_else(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "swancloud-design")
        monkeypatch.delenv("CREW_LABEL", raising=False)
        assert cards.refusal(hooked("whoami", {"name": "swancloud-ops"})).startswith('crew refuses this whoami: it gives name "swancloud-ops"')
        assert cards.refusal(hooked("get_request", {"requestId": "req_a-1", "name": "swancloud-planner"}, "plugin_pendingyou_pendingyou")).startswith(
            'crew refuses this get_request: it gives name "swancloud-planner"')
        assert cards.refusal(hooked("whoami", {"name": "swancloud-design"})) is None
        assert cards.refusal(hooked("get_issue", {"name": "swancloud-ops"}, "github")) is None
        with pytest.raises(ValueError, match="its input is not an object"):
            cards.refusal(hooked("whoami", "swancloud-ops"))
        monkeypatch.delenv("CREW_AGENT")
        assert cards.refusal(hooked("whoami", {"name": "swancloud-ops"})) is None

    def test_the_name_is_checked_before_and_apart_from_the_cards_key(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "wldn-planner")
        monkeypatch.setenv("CREW_LABEL", "wldn")
        given = {"idempotencyKey": "proposal/1", "session": {"label": "wldn-ops"}}
        assert cards.refusal(hooked("post_request", given)).startswith('crew refuses this post_request: it gives session.label "wldn-ops"')

    def test_the_hook_runs_before_every_pending_you_tool_under_any_server_name_and_no_other(self):
        hooks = json.loads((HOOK.parent / "hooks.json").read_text())["hooks"]["PreToolUse"]
        matcher = next(h["matcher"] for h in hooks if any("hooks/cards\" --before" in c["command"] for c in h["hooks"]))
        for name in ("mcp__pendingyou__whoami", "mcp__pendingyou__get_request", "mcp__plugin_pendingyou_pendingyou__list_pending",
                     "mcp__pendingyou__a_tool_pending_you_adds", "mcp__pendingyou__post_request"):
            assert re.search(matcher, name), name
        assert not re.search(matcher, "mcp__github__get_issue") and not re.search(matcher, "Bash")


LANDING = {"kind": "approve", "highStakes": True}
TWO = {"options": [{"id": "fix", "label": "Fix both"}, {"id": "merge", "label": "Merge as it is"}]}


def form(k, given, update=False, units=None):
    return cards.form_refusal(k, given, update, units)


class TestForms:
    def test_a_landing_card_is_a_high_stakes_approval_that_asks_only_for_the_landing(self):
        # A step only the user can take is the deploy's, on its own card (record 0025).
        assert form("land/b/abc1234", LANDING) is None
        said = form("land/b/abc1234", dict(LANDING, action={"steps": [{"text": "Open the gateway on your Mac"}]}))
        assert said.startswith("crew refuses card land/b/abc1234. A landing's card is an approval")
        assert said.endswith("This card has steps for the user to take. Post it again in that form.")
        said = form("land/b/abc1234", {"kind": "action", "action": {"steps": [{"text": "Land the bolt", "command": "crew bolt land b"}]}})
        assert 'This card is an "action", is not marked high stakes, and has steps for the user to take. Post it again' in said
        assert form("land/b/abc1234", {"kind": "approve"}).endswith("This card is not marked high stakes. Post it again in that form.")
        assert "This card has options." in form("land/b/abc1234", dict(LANDING, **TWO))

    def test_a_verify_reports_card_has_no_form_since_none_is_posted_and_one_posted_before_changes_unchecked(self):
        assert not cards.formed("verify/x/20261007-1412") and cards.formed("land/b/abc1234")

    def test_a_record_card_is_a_low_risk_reversible_approval(self):
        accept = {"kind": "approve", "approve": {"action": "Accept record 0021", "risk": "low", "reversible": True}}
        assert form("record/atlas-kit/0021", accept) is None
        assert 'This card is a "choice", has options, and has no approve block.' in form("record/atlas-kit/0021", dict(kind="choice", **TWO))
        assert 'This card has risk "high".' in form("record/atlas-kit/0021", {**accept, "approve": {**accept["approve"], "risk": "high"}})
        assert "This card is not reversible." in form("record/atlas-kit/0021", {**accept, "approve": {**accept["approve"], "reversible": False}})

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
            "with highStakes true, whose yes has you tell main-level ops to land; it has no options and no steps. This change clears "
            "its high stakes. Change the card without it.")
        assert form("land/b/abc1234", {"title": "Land it"}, update=True) is None
        assert "This change gives it options." in form("proposal/1", TWO, update=True)
        assert 'This change gives it risk "medium".' in form("record/atlas-kit/0021", {"approve": {"risk": "medium", "reversible": True}}, update=True)

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


    # A batch's card and a long proposal's are raised with their reading session (card-sessions, record 0031 §5).
    def test_a_batchs_card_links_its_session_a_long_proposals_when_its_builder_says_and_no_other_card_any(self):
        assert plan.reading_of({"key": "batch/3"}) == "batch"
        assert plan.reading_of({"key": "proposal/4", "session": True}) == "proposal"
        assert plan.reading_of({"key": "proposal/4", "session": False}) is None
        assert plan.reading_of({"key": "land/b1"}) is None and plan.reading_of({"key": "record/crew/0031"}) is None

    def test_a_proposal_of_more_than_fifteen_new_units_or_more_rows_than_its_lists_hold_has_a_reading(self):
        def args(*dos):
            return [plan.do_args("wldn", d) for d in dos]
        adds = [f'unit add u{i} "U{i}." --bolt t' for i in range(16)]
        assert plan.proposal_reads(args(*adds)) and not plan.proposal_reads(args(*adds[:15]))
        drops = [f'unit drop d{i} "Gone."' for i in range(6)]
        assert plan.proposal_reads(args(*adds[:15], *drops)) and not plan.proposal_reads(args(*adds[:14], *drops))

    def test_the_session_is_started_before_the_card_is_built_and_its_link_handed_to_the_builder(self, capsys):
        acts = ReadingActs()
        b = plan.card_built(acts, "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        assert acts.sessions == [("wldn", "batch/3")]
        assert b["card"]["context"]["links"] == [{"label": "Read batch 3", "url": "http://mac-studio.ts.swancloud.net:19432"}]
        assert b["card"]["context"]["background"].startswith("Read it all in one session: http://mac-studio.ts.swancloud.net:19432")
        landing = plan.card_built(acts, "wldn", built.landing_card, dict(bolt="b1", kit="k", units=["v1"], chores=[], batches={},
                                                                           head="abc1234", at=None, moved=0, pr=None))
        assert acts.sessions == [("wldn", "batch/3")] and landing["key"] == "land/b1"
        assert capsys.readouterr().err == ""

    def test_a_card_whose_session_could_not_open_is_raised_all_the_same_saying_so(self, capsys):
        why = "crew can't read z1's change: mac-studio, atl-1's host, did not answer (ssh: timed out)"
        acts = ReadingActs(refused=why)
        c = plan.card_built(acts, "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))["card"]
        assert c["summary"].startswith("6 changes to read, nothing to approve, since batch 2.\n\nIts reading could not be opened on the tailnet.\n\n")
        assert len(c["summary"]) <= 400
        assert c["context"]["background"].startswith(f"The reading could not be opened on the tailnet: {why}\n\n")
        assert c["context"]["links"] == [] and not [a for a in c["artifacts"] if a["kind"] == "url"]
        assert capsys.readouterr().err == f"card batch/3: its reading could not be opened on the tailnet: {why}\n"

    def test_crews_close_ends_the_keys_session_and_a_refused_close_keeps_it(self, capsys):
        held = [{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}]
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None)}, held)
        assert plan.row_card_close(None, "wldn", "wldn-planner", "batch/3", outcome="Read; no notes", acts=acts) == "req_b3"
        assert acts.ended == [("wldn", "batch/3")]
        assert capsys.readouterr().out.splitlines()[-2:] == ["card batch/3: req_b3 withdrawn", "ended batch/3's session, plannotator pid 42"]
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None), "cancel_request": (None, "Too many requests.")}, held)
        assert plan.row_card_close(None, "wldn", "wldn-planner", "batch/3", outcome="Read; no notes", acts=acts) is None
        assert acts.ended == []
        acts = ReadingActs(entries=[])
        plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome="Landed", acts=acts)
        assert acts.ended == []

    def test_a_batch_wait_returns_the_cards_note_and_the_sessions_annotations_as_the_user_wrote_them(self):
        tapped = {"status": "answered", "turn": "agent", "answer": {"note": {"text": "x1: say what a zone is."}}}
        assert plan.batch_waited("batch/3", None, tapped) == (
            "read", "batch/3: sent back on its card, with a note:\nx1: say what a zone is.", "Read; 1 note sent to its team")
        assert plan.batch_waited("batch/3", None, {"status": "answered", "turn": "agent", "answer": {}}) == (
            "read", "batch/3: sent back on its card, with no note", "Read; no notes")
        notes = "# Annotations\n\n1. Say what z means.\n2. Why one zone?"
        assert plan.batch_waited("batch/3", ("annotated", notes, 2), {"status": "pending", "turn": "you"}) == (
            "read", f"batch/3: annotated\n{notes}", "Read; 2 notes sent to their teams")
        assert plan.batch_waited("batch/3", ("approved", None, 0), None) == ("read", "batch/3: approved", "Read; no notes")
        assert plan.batch_waited("batch/3", ("annotated", notes, 2), tapped)[2] == "Read; 3 notes sent to their teams"
        assert plan.batch_waited("batch/3", ("annotated", notes, None), None)[2] == "Read; its notes sent to their teams"

    def test_a_batch_wait_goes_on_while_neither_has_the_users_word_and_ends_on_a_card_closed_outside_crew(self):
        for decided in (None, ("dismissed", None, None)):
            assert plan.batch_waited("batch/3", decided, {"status": "pending", "turn": "you"}) is None
            assert plan.batch_waited("batch/3", decided, None) is None
        assert plan.batch_waited("batch/3", None, {"status": "cancelled"}) == (
            "closed", "batch/3: its card was closed outside crew; Pending You shows it cancelled", "cancelled")

    def test_a_sessions_result_gives_its_count_of_annotations(self, tmp_path):
        (tmp_path / "result.json").write_text(json.dumps({"decision": "annotated", "feedback": "a", "annotationCount": 2}))
        assert plan.card_result(tmp_path) == ("annotated", "a", 2)
        (tmp_path / "result.json").write_text(json.dumps({"decision": "approved", "annotationCount": "two"}))
        assert plan.card_result(tmp_path) == ("approved", None, None)


class ReadingActs:
    """A stand-in for the act's reach (plan.CardActs) where a card's reading session starts and ends: a session's link
    given, or its start refused with why; Pending You's tools answered from answers, a (got, words) pair."""

    def __init__(self, answers=None, entries=(), refused=None):
        self.answers, self.held, self.refused = dict(answers or {}), list(entries), refused
        self.sessions, self.ended, self.emitted = [], [], []

    def session(self, label, key, facts):
        self.sessions.append((label, key))
        if self.refused:
            raise crew.Refusal(self.refused)
        return "http://mac-studio.ts.swancloud.net:19432"

    def end(self, label, key):
        self.ended.append((label, key))
        return f"ended {key}'s session, plannotator pid 42"

    def bridge(self, name, later, held=None):
        acts = self

        class Py:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

            def answer(self, tool, args):
                return acts.answers.get(tool, ({"ok": True}, None))
        return Py()

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act))

    def entries(self, label):
        return self.held

    def host(self):
        return "mac-studio"

    def caller(self):
        return "wldn-planner"


class TestSessionWords:
    def test_a_landing_key_has_no_session_and_a_batch_cards_runs_on_the_main_levels_host(self):
        assert plan.session_refusal("land/b/abc1234", "wldn", "box", "box") == (
            "a landing card has nothing to read: it has no document to read, so it has no session")
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


# ------------------------------------------------------------------- the six cards crew builds (record 0031 §5)
# cards.py's builders, each a function of its event's facts (code.7, briefs.13): what post_request takes, in the forms
# the card trials settled with the user. The lib's cards is `built` here, since `cards` is the hook.
import cards as built  # noqa: E402

NOTES = """## swancloud-srv-v0.3.0 (2026-10-15)
### Fixes
- deployer: crew reaches the boxes with the peer key (e5b8322)
- cache: deploy a NixOS pusher's token to its machine (4749797)"""
SIX = ["the-deployer-records-each-step", "a-failed-step-holds-its-environment", "the-doctor-names-the-failed-step",
       "a-retry-is-offered-not-run", "the-doctor-shows-the-hosts-sign-in", "a-deploy-ends-with-its-outcome"]


def landing(**more):
    return built.landing_card(dict(bolt="a-deploy-holds-at-a-failure", kit="crew", units=SIX, chores=[],
                                   batches={u: 6 if i < 4 else 7 for i, u in enumerate(SIX)}, head="4581216abcdef",
                                   at="14:02", moved=1, pr={"number": 23, "url": "https://github.com/agentplot/crew/pull/23"},
                                   offers=["srv"], **more))


def deploy(**more):
    return built.deploy_card(dict(dict(
        env="srv", head="c882cff0123", base="6aed25c4567",
        landings=[{"pr": 16, "subject": "The deployer holds at a failure"}, {"pr": 17, "subject": "The doctor names the step"},
                  {"pr": 18, "subject": "A retry is offered"}],
        notes=NOTES, release="swancloud-srv-v0.3.0",
        steps=[{"n": 1, "text": "rotate the kanidm admin password", "doer": "user", "held": False},
               {"n": 2, "text": "restart crew's teams on mac-studio", "doer": "swancloud-ops", "held": True}],
        before=[], after=[{"env": "box", "policy": "auto"}, {"env": "mac-studio", "policy": "manual"}]), **more))


BATCH_UNITS = [{"unit": f"u{i}", "team": "swb-1" if i < 4 else "swb-2", "subject": s, "paragraph": f"What u{i} does, in the reviewer's words. It does it well."}
               for i, s in enumerate(["the deployer holds at a failure", "questions reach you", "the deployer holds at a failure",
                                      "cards reach you", "the doctor names the step", "the rail shows its cards"], 1)]


def words_asked(card):
    """Whether a card asks a question in words: a text field, or a question of kind text."""
    return "text" in card or any(q.get("kind") == "text" for q in card.get("questions") or [])


class TestLanding:
    def test_landing_is_approved_only_by_holding_the_button_never_marked_high_stakes(self):
        c = landing()["card"]
        assert (c["kind"], c["intent"], c["recommendedIds"]) == ("approve", "approve", ["approve"])
        assert c["approve"] == {"action": "Land a-deploy-holds-at-a-failure on crew's main", "risk": "high", "reversible": False,
                                "because": "irreversible"}
        assert "highStakes" not in c and c["blocking"] is False

    def test_six_units_on_a_landing_card_are_a_list_on_its_face_and_the_background_names_none(self):
        b = landing()
        c = b["card"]
        assert b["key"] == "land/a-deploy-holds-at-a-failure" and c["title"] == "Land the bolt a-deploy-holds-at-a-failure on crew's main"
        lands = c["artifacts"][0]
        assert (lands["kind"], lands["lang"], lands["title"]) == ("code", "text", "What lands: 6 units, no chores")
        assert lands["lines"] == SIX and max(len(l) for l in lands["lines"]) <= 40
        assert not [u for u in SIX if u in c["context"]["background"] or u in c["summary"]]

    def test_its_summary_gives_the_counts_the_batches_sluices_verdict_and_how_far_main_moved_and_its_rationale_what_follows(self):
        c = landing()["card"]
        assert c["summary"] == ("6 units land, every one merged and every unit read in a batch (6 and 7). sluice is green at "
                                "4581216 since 14:02, its pull request #23 linked below. main has moved 1 landing since the bolt was cut.")
        assert c["rationale"] == ("After it lands: main-level ops lands it through sluice and every host takes it; srv's deploy "
                                  "will be offered on a card.")
        assert c["context"]["background"].startswith("Read in its batches:\nbatch 6: 4 units\nbatch 7: 2 units\n\nA note naming a defect")

    def test_sluices_pull_request_is_linked_and_a_kit_whose_sluice_opens_none_has_no_link(self):
        c = landing()["card"]
        assert c["artifacts"][1] == {"kind": "url", "title": "Pull request #23 on GitHub, opened by sluice",
                                     "ref": "https://github.com/agentplot/crew/pull/23"}
        assert c["context"]["links"] == [{"label": "Pull request #23 on GitHub, opened by sluice", "url": "https://github.com/agentplot/crew/pull/23"}]
        bare = built.landing_card(dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=["tidy-the-logs"], batches={"v1": 3},
                                       head="abc1234", at=None, moved=0, pr=None))["card"]
        assert [a["kind"] for a in bare["artifacts"]] == ["code"] and bare["context"]["links"] == []
        assert bare["artifacts"][0]["lines"] == ["v1", "tidy-the-logs (chore)"]
        assert bare["summary"] == ("1 unit and 1 chore land, every one merged and every unit read in a batch (3). sluice is green "
                                   "at abc1234. main has not moved since the bolt was cut.")

    def test_a_card_with_nothing_to_show_carries_the_units_and_the_link_and_no_reading_session(self):
        c = landing()["card"]
        assert [(a["kind"], a.get("lang")) for a in c["artifacts"]] == [("code", "text"), ("url", None)]
        assert "plannotator" not in json.dumps(c) and "session" not in c


class TestDeploy:
    def test_three_landings_since_srvs_last_deploy(self):
        b = deploy()
        c = b["card"]
        assert b["key"] == "deploy/srv" and c["title"] == "Deploy main c882cff to srv"
        assert c["approve"] == {"action": "Deploy c882cff to srv", "risk": "high", "reversible": False, "because": "irreversible"}
        assert c["summary"] == ("3 landings since srv's last deploy (6aed25c). box (auto) follows on its own; mac-studio is offered "
                                "after srv. After the deploy: 2 steps, 1 yours.")
        notes, steps = c["artifacts"]
        assert (notes["lang"], notes["title"], notes["lines"]) == ("markdown", "What's in it: swancloud-srv-v0.3.0", NOTES.split("\n"))
        assert (steps["lang"], steps["title"]) == ("text", "After the deploy: 2 steps, 1 yours")
        assert steps["lines"] == ["1  rotate the kanidm admin password", "   you", "2  restart crew's teams on mac-studio",
                                  "   swancloud-ops, held for your word"]
        assert c["context"]["background"] == ("Landings since srv's last deploy:\n#16 The deployer holds at a failure\n"
                                              "#17 The doctor names the step\n#18 A retry is offered")

    def test_a_kit_that_hands_no_notes_has_the_landings_subjects_on_its_face(self):
        c = deploy(notes=None, steps=[])["card"]
        assert [(a["lang"], a["title"]) for a in c["artifacts"]] == [("text", "What's in it: 3 landings")]
        assert c["artifacts"][0]["lines"][0] == "#16 The deployer holds at a failure"

    def test_a_card_follows_the_card_its_thing_follows(self):
        entries = [dict(Act="card.post", Key="land/b24", Card="req_land24"), dict(Act="bolt.land", On=["bolt/b24"], Head="c882cff0123"),
                   dict(Act="card.close", Card="req_land24", State="closed")]
        follows = built.follows_of("deploy", {"env": "srv", "head": "c882cff"}, entries)
        assert follows == "req_land24" and deploy(follows=follows)["card"]["follows"] == "req_land24"


class TestFollows:
    E = [dict(Act="card.post", Key="land/b24/abc1234", Card="req_old"), dict(Act="card.close", Card="req_old"),
         dict(Act="card.post", Key="land/b24", Card="req_land"), dict(Act="bolt.land", On=["bolt/b24"], Head="c882cff"),
         dict(Act="card.close", Card="req_land", State="closed"),
         dict(Act="card.post", Key="deploy/srv", Card="req_d1")]

    def test_a_deploy_of_a_newer_head_after_a_no_follows_the_declined_card(self):
        declined = self.E + [dict(Act="card.close", Card="req_d1", State="declined")]
        assert built.follows_of("deploy", {"env": "srv", "head": "9ab12cd"}, declined) == "req_d1"
        assert built.follows_of("deploy", {"env": "srv", "head": "9ab12cd"}, self.E) is None

    def test_a_step_follows_the_deploys_card_and_each_later_step_the_one_before(self):
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/1"}, self.E) == "req_d1"
        more = self.E + [dict(Act="card.post", Key="op/srv/1", Card="req_s1"), dict(Act="card.close", Card="req_s1")]
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/2"}, more) == "req_s1"

    def test_a_landing_raised_again_follows_the_card_its_defect_note_held_and_an_open_one_is_changed_not_followed(self):
        held = [dict(Act="card.post", Key="land/b7", Card="req_l1"), dict(Act="card.close", Card="req_l1", State="withdrawn")]
        assert built.follows_of("land", {"bolt": "b7"}, held) == "req_l1"
        assert built.follows_of("land", {"bolt": "b7"}, held[:1]) is None

    def test_a_lost_card_is_followed_by_none_and_a_proposal_a_batch_and_a_record_follow_nothing(self):
        lost = [dict(Act="card.post", Key="land/b7", Card="req_l1"), dict(Act="card.close", Card="req_l1", State="lost")]
        assert built.follows_of("land", {"bolt": "b7"}, lost) is None
        assert [built.follows_of(k, {}, self.E) for k in ("proposal", "batch", "record")] == [None, None, None]


class TestStep:
    def test_the_users_step_is_a_do_with_its_commands_whole_where_and_done_when(self):
        b = built.step_card(dict(env="srv", n=1, text="rotate the kanidm admin password", doer="user", held=False,
                                 why="Only you can: the password is in your vault, and no check can tell it was done.",
                                 where="a terminal on mac-studio", done="kanidm's login page takes the new password.",
                                 commands=["clan vars generate swancloud-srv --generator kanidm-admin --regenerate",
                                           "clan machines update swancloud-srv"], follows="req_d1"))
        c = b["card"]
        assert b["key"] == "op/srv/1" and (c["kind"], c["intent"], c["follows"]) == ("action", "do", "req_d1")
        assert c["title"] == "After srv's deploy: rotate the kanidm admin password"
        assert c["action"]["where"] == "a terminal on mac-studio" and c["action"]["done"] == "kanidm's login page takes the new password."
        assert [s["command"] for s in c["action"]["steps"]] == ["clan vars generate swancloud-srv --generator kanidm-admin --regenerate",
                                                                "clan machines update swancloud-srv"]

    def test_a_held_step_is_a_choice_of_when_quiet_recommended(self):
        c = built.step_card(dict(env="mac-studio", n=2, text="restart crew's teams", doer="swancloud-ops", held=True,
                                 why="It ends swc-1's code stage mid-unit.", consequences={"now": "swc-1's stage starts again"}))["card"]
        assert (c["kind"], c["intent"], c["recommendedIds"]) == ("choice", "decide", ["quiet"])
        assert c["title"] == "After mac-studio's deploy: restart crew's teams, now or when the host is quiet?"
        assert [(o["id"], o["label"]) for o in c["options"]] == [("quiet", "When the host is quiet"), ("now", "Now"), ("skip", "Skip it")]
        assert c["options"][1]["consequence"] == "swc-1's stage starts again"
        assert c["summary"] == "swancloud-ops can do it. It ends swc-1's code stage mid-unit. Held for your word."


RECORD = "# 32. switchboard runs GitHub's workflows itself\n\nStatus: proposed\n\n## Context\n\nThe runners cost."


class TestRecord:
    def test_a_documents_substance_on_a_card_is_the_record_as_markdown_and_no_file(self):
        b = built.record_card(dict(kit="switchboard-kit", number=32, title="switchboard runs GitHub's workflows itself",
                                   opening="switchboard runs the workflows. A fleet costs more.", quoted=["I don't want a fleet"],
                                   text=RECORD))
        c = b["card"]
        assert b["key"] == "record/switchboard-kit/0032"
        assert c["artifacts"] == [{"kind": "code", "lang": "markdown", "title": "Record 0032", "ref": "record-0032.md", "lines": RECORD.split("\n")}]
        assert c["approve"] == {"action": "Accept record 0032", "risk": "low", "reversible": True}
        assert c["title"] == "Accept record 0032 in switchboard-kit: switchboard runs GitHub's workflows itself"
        assert c["summary"] == "switchboard runs the workflows. A fleet costs more.\n\nYour own words, recorded as your decision: “I don't want a fleet”"

    def test_a_record_a_rule_decided_between_alternatives_is_one_choice_loosen_accept_or_send_back(self):
        c = built.record_card(dict(kit="switchboard-kit", number=32, title="a CodeBuild fleet runs the workflows", opening="x.",
                                   text=RECORD, alternatives={"rules": ["ops.3", "ops.7"], "other": "switchboard runs them itself",
                                                              "text": "## Where your rules decided\n\nops.3", "recommended": "loosen"}))["card"]
        assert (c["kind"], c["intent"], c["recommendedIds"]) == ("choice", "decide", ["loosen"])
        assert [o["id"] for o in c["options"]] == ["loosen", "accept", "back"] and c["options"][0]["label"] == "Loosen ops.3 and ops.7 as drafted"
        assert [a["title"] for a in c["artifacts"]] == ["Where your rules decided, and the rules loosened", "Record 0032"]


# crew record (briefs.15, record 0031 §1): the record's facts read from its Markdown at a commit, whether the file holds
# the status recorded, the alternatives a rule decided between, the refusals made before anything is read, and the raise
# on the act's stand-in.
MADR = """---
number: 32
title: switchboard runs GitHub's workflows itself
status: proposed
date: 2026-10-16
---

# switchboard runs GitHub's workflows itself

Status: proposed to the user on 2026-10-16, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, in the design talk (“I don't want a fleet”); wldn-design.

## Context and problem statement

The runners cost. A fleet costs more.

## Decision outcome

Switchboard runs them.
"""
ACCEPTED = (MADR.replace("status: proposed", "status: accepted")
            .replace("Status: proposed to the user on 2026-10-16, as `briefs.15` has it; accepted only on their yes.",
                     "Status: accepted by the user on 2026-10-17, on their card."))
AMENDED = ACCEPTED + "\n- **Rented.** The runners are rented by the hour. Status: proposed to the user on 2026-10-18, as `briefs.15` has it; accepted only on their yes.\n"
ALTERNATIVES = """---
rules: ops.3, ops.7
other: switchboard runs the workflows itself
recommended: loosen
---

## Where your rules decided

ops.3 (prefer managed services) chose a CodeBuild fleet.
"""


def recorded(text, status, before=None, alternatives=None):
    return plan.record_facts("switchboard-kit", 32, text, status, before, alternatives)


class TestRecordCommand:
    def test_a_record_proposed_is_put_on_its_card_in_its_own_words_with_the_users_own(self):
        f = recorded(MADR, "proposed")
        assert (f["title"], f["opening"], f["quoted"]) == ("switchboard runs GitHub's workflows itself", "The runners cost. A fleet costs more.",
                                                           ["I don't want a fleet"])
        assert f["text"].startswith("# switchboard runs GitHub's workflows itself") and "status: proposed" not in f["text"]
        b = built.record_card(f)
        assert b["key"] == "record/switchboard-kit/0032" and re.fullmatch(plan.RECORD_KEY, b["key"])
        assert (b["card"]["kind"], b["card"]["approve"]["risk"], b["card"]["approve"]["reversible"]) == ("approve", "low", True)
        assert b["card"]["summary"] == "The runners cost. A fleet costs more.\n\nYour own words, recorded as your decision: “I don't want a fleet”"

    def test_a_record_a_rule_decided_is_a_choice_its_alternatives_file_on_its_face_before_the_record(self):
        f = recorded(MADR, "proposed", alternatives=ALTERNATIVES)
        assert f["alternatives"] == {"rules": ["ops.3", "ops.7"], "other": "switchboard runs the workflows itself", "recommended": "loosen",
                                     "text": "## Where your rules decided\n\nops.3 (prefer managed services) chose a CodeBuild fleet."}
        c = built.record_card(f)["card"]
        assert (c["kind"], c["recommendedIds"], [o["id"] for o in c["options"]]) == ("choice", ["loosen"], ["loosen", "accept", "back"])
        assert [a["lines"][0] for a in c["artifacts"]] == ["## Where your rules decided", "# switchboard runs GitHub's workflows itself"]
        unrecommended = recorded(MADR, "proposed", alternatives=ALTERNATIVES.replace("recommended: loosen\n", ""))
        assert built.record_card(unrecommended)["card"]["recommendedIds"] == ["accept"]

    def test_a_status_the_file_does_not_hold_is_refused_naming_what_it_holds(self):
        with pytest.raises(crew.Refusal, match="crew refuses record 0032 in switchboard-kit as accepted: its file on main says proposed"):
            recorded(MADR, "accepted")
        with pytest.raises(crew.Refusal, match="as proposed: its file on main says accepted. Commit it proposed"):
            recorded(ACCEPTED, "proposed")
        with pytest.raises(crew.Refusal, match="as rejected: its file on main says no status in its frontmatter"):
            recorded(MADR.split("---\n", 2)[2], "rejected")
        assert recorded(ACCEPTED, "accepted", before=MADR)["opening"] == "The runners cost. A fleet costs more."

    def test_an_amendment_is_proposed_while_marked_and_accepted_or_rejected_once_its_mark_is_gone(self):
        f = recorded(AMENDED, "proposed", before=ACCEPTED)
        assert f["opening"] == "- **Rented.** The runners are rented by the hour."
        with pytest.raises(crew.Refusal, match="its file on main says accepted, with an amendment still marked proposed"):
            recorded(AMENDED, "accepted", before=ACCEPTED)
        taken = AMENDED.replace(" Status: proposed to the user on 2026-10-18, as `briefs.15` has it; accepted only on their yes.", "")
        assert recorded(taken, "accepted", before=AMENDED) and recorded(ACCEPTED, "rejected", before=AMENDED)
        with pytest.raises(crew.Refusal, match="as rejected: its file on main says accepted"):
            recorded(ACCEPTED, "rejected", before=MADR)

    @pytest.mark.parametrize("alternatives, said", [
        ("## Where\n\nops.3", "their frontmatter names no rules that decided, as rules: <rule ids, separated by commas>"),
        ("---\nrules: ops.3\n---\n\n## Where", "their frontmatter names no other path, as other: <the path the rules ruled out>"),
        ("---\nrules: ops.3\nother: x\nrecommended: both\n---\n\n## Where", "their frontmatter recommends both, where it takes loosen or accept"),
        ("---\nrules: ops.3\nother: x\n---\n", "the file holds nothing under its frontmatter for the card")])
    def test_alternatives_crew_cannot_put_on_the_card_are_refused_and_nothing_raised(self, alternatives, said):
        with pytest.raises(crew.Refusal) as e:
            recorded(MADR, "proposed", alternatives=alternatives)
        assert str(e.value) == f"crew refuses the alternatives for record 0032 in switchboard-kit: {said}. Nothing is raised."

    @pytest.mark.parametrize("kit, n, status, more, said", [
        ("flywheel-next", 32, "proposed", {}, "crew record takes a kit of wldn's, atlas-kit, breadboard-kit or switchboard-kit, not flywheel-next."),
        ("atlas-kit", 0, "proposed", {}, "a record's number is its one to four digits, not 0"),
        ("atlas-kit", 21, "accepted", {"settled_in_pane": True}, "--settled-in-pane and --alternatives go with --proposed"),
        ("atlas-kit", 21, "rejected", {"alternatives": "a.md"}, "--settled-in-pane and --alternatives go with --proposed"),
        ("atlas-kit", 21, "proposed", {"settled_in_pane": True, "alternatives": "a.md"}, "a record settled in the pane raises no card")])
    def test_a_kit_not_the_partitions_or_flags_that_do_not_go_together_are_refused_on_the_teams_file_alone(self, kit, n, status, more, said):
        a = argparse.Namespace(**dict(dict(kit=kit, number=n, status=status, settled_in_pane=False, alternatives=None, label="wldn"), **more))
        with pytest.raises(crew.Refusal, match=re.escape(said)):
            plan.record_status(FLEET, a)

    def test_the_records_card_is_raised_in_the_design_agents_name_changed_at_a_new_commit_and_followed_once_answered(self, capsys):
        from test_card_commands import Acts, MATCHED, POSTED
        where, f = ("/kit/main", "github.com/WilldanGroup/switchboard-kit"), recorded(MADR, "proposed")
        acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)}, caller="wldn-design")
        assert plan.raise_record(None, "wldn", f, where, "Revised at abc1234: x", acts) == "req_c1"
        sent = acts.calls[1][1]
        assert (acts.names, sent["idempotencyKey"], sent["session"]["label"]) == (["wldn-design"], "record/switchboard-kit/0032", "wldn-design")
        assert acts.emitted[0]["On"] == ["record/switchboard-kit/0032"] and acts.told == []
        held = [dict(Act="card.post", Key="record/switchboard-kit/0032", By="wldn-design", Card="req_c1")]
        acts = Acts({"get_request": ({"status": "pending", "version": 2}, None), "update_request": ({"version": 3}, None)}, entries=held,
                    caller="wldn-design")
        assert plan.raise_record(None, "wldn", f, where, "Revised at def5678: ops.3 loosened", acts) == "req_c1"
        assert acts.calls[1][0] == "update_request" and acts.calls[1][1]["changeNote"] == "Revised at def5678: ops.3 loosened"
        assert capsys.readouterr().out.splitlines()[-1] == "card record/switchboard-kit/0032: req_c1 changed, now version 3"
        acts = Acts({"get_request": ({"status": "answered", "version": 3}, None), "ack_answer": ({"version": 4}, None),
                     "match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=held, caller="wldn-design")
        assert plan.raise_record(None, "wldn", f, where, "Revised at 9ab0123: ops.7 loosened", acts) == "req_c2"
        assert acts.calls[1] == ("ack_answer", {"requestId": "req_c1", "name": "wldn-design", "expectedVersion": 3,
                                                "outcome": "Revised at 9ab0123: ops.7 loosened"})
        assert (acts.calls[3][1]["idempotencyKey"], acts.calls[3][1]["follows"]) == ("record/switchboard-kit/0032:2", "req_c1")


class TestBatch:
    def test_six_units_named_with_their_teams_and_paragraphs_as_prose_and_one_link_to_its_session(self):
        b = built.batch_card(dict(n=2, previous=1, units=BATCH_UNITS, link="http://mac-studio:19432"))
        c, back = b["card"], b["card"]["context"]["background"]
        assert b["key"] == "batch/2" and (c["kind"], c["intent"]) == ("fyi", "tell")
        assert back.startswith("Read it all in one session: http://mac-studio:19432\n\n")
        for u in BATCH_UNITS:
            assert f"{u['unit']} ({u['team']})\n{u['paragraph']}" in back
        assert "```" not in back
        assert c["context"]["links"] == [{"label": "Read batch 2", "url": "http://mac-studio:19432"}]
        assert [a for a in c["artifacts"] if a["kind"] == "url"] == [{"kind": "url", "title": "Read batch 2", "ref": "http://mac-studio:19432"}]

    def test_its_title_is_what_the_batch_is_about_and_its_body_opens_with_what_it_asks(self):
        c = built.batch_card(dict(n=7, previous=6, units=BATCH_UNITS[:4], link="http://mac-studio:19432"))["card"]
        assert c["title"] == "The deployer holds at a failure, questions reach you and cards reach you (batch 7)"
        assert c["summary"].startswith("4 changes to read, nothing to approve, since batch 6.\n\nswb-1 · u1: What u1 does")

    def test_a_batch_cards_summary_holds_each_units_paragraph_as_prose_and_the_reviewers_summary_rides_the_face_as_markdown(self):
        c = built.batch_card(dict(n=7, previous=6, units=BATCH_UNITS[:4], link="http://mac-studio:19432"))["card"]
        md = c["artifacts"][0]
        assert (md["kind"], md["lang"], md["title"]) == ("code", "markdown", "The reviewer's summary")
        assert md["lines"][:3] == ["**swb-1 · u1**", "", "What u1 does, in the reviewer's words. It does it well."]
        assert "**" not in c["summary"] and "`" not in c["summary"]

    def test_a_change_too_long_for_the_summary_ends_at_the_last_whole_sentence_and_the_background_holds_every_paragraph(self):
        long = [dict(u, paragraph=" ".join(f"Sentence {k} of {u['unit']} says a little more." for k in range(8))) for u in BATCH_UNITS]
        c = built.batch_card(dict(n=8, previous=7, units=long, link=None))["card"]
        assert len(c["summary"]) <= 400 and c["summary"].endswith("says a little more.")
        assert all(u["paragraph"] in c["context"]["background"] for u in long)

    def test_a_review_card_carries_the_reviewers_paragraph_in_its_words(self):
        c = built.batch_card(dict(n=3, previous=2, units=BATCH_UNITS[:1], link=None))["card"]
        assert BATCH_UNITS[0]["paragraph"] in c["summary"]


class TestWords:
    def test_prose_keeps_the_documents_words_its_paragraphs_and_cuts_at_whole_sentences(self):
        assert built.prose("The **first** `thing`.  It  runs.\n\nA second  paragraph.") == "The first thing. It runs.\n\nA second paragraph."
        assert built.prose("One short. Two is a longer sentence than fits.", 20) == "One short."
        assert built.prose("A first sentence far longer than the budget it is given.", 20) == "A first sentence…"

    def test_a_list_is_one_thing_a_line_of_at_most_forty_a_long_name_wrapped_at_its_hyphens(self):
        lines = built.lines_of(["the-doctor-shows-the-hosts-pending-you-sign-in-at-last", ("1  a step", "you, after the deploy")])
        assert lines == ["the-doctor-shows-the-hosts-pending-", "  you-sign-in-at-last", "1  a step", "   you, after the deploy"]
        assert max(len(l) for l in lines) <= 40

    def test_no_card_of_crews_asks_a_question_in_words(self):
        cards_built = [landing()["card"], deploy()["card"], built.batch_card(dict(n=2, units=BATCH_UNITS, link=None))["card"],
                       built.record_card(dict(kit="k", number=1, title="t", opening="o.", text="r"))["card"],
                       built.step_card(dict(env="srv", n=1, text="do it", doer="user", held=False))["card"],
                       built.step_card(dict(env="srv", n=2, text="do it", doer="ops", held=True))["card"]]
        assert not [c["title"] for c in cards_built if words_asked(c)]
        assert all(len(c["summary"]) <= 400 and 8 <= len(c["title"]) <= 140 for c in cards_built)

    def test_no_card_carries_a_path_but_a_steps_command(self):
        texts = json.dumps([landing()["card"], deploy()["card"]])
        assert "/Users/" not in texts and "~/" not in texts


class TestActDecisions:
    def test_the_line_that_adopts_a_card_and_whom_it_is_told_to(self):
        assert built.adopt_line("req_abc", "wldn-ops") == "call get_request (requestId req_abc, name wldn-ops)"
        assert built.told_to("wldn-ops", "chuck@mac-studio") == "wldn-ops"
        assert built.told_to("wldn-planner", "wldn-planner") is None

    @pytest.mark.parametrize("key, obj", [("proposal/4", "proposal/4"), ("batch/7", "batch/7"), ("land/b1", "bolt/b1"),
                                          ("deploy/srv", "env/srv"), ("op/srv/2", "env/srv"), ("record/crew/0031", "record/crew/0031"),
                                          ("land/b1/abc1234", None), ("agent-note", None), ("verify/x/20261007-1412", None)])
    def test_each_of_crews_six_keys_is_recorded_on_its_rows_object_and_a_verify_report_has_none(self, key, obj):
        assert built.row_object(key) == obj

    def test_an_approval_the_user_declined_is_read_with_their_words(self):
        assert built.declined({"turn": "agent", "answer": {"approved": False, "note": {"text": "Not before Friday."}}}) == "Not before Friday."
        assert built.declined({"turn": "agent", "answer": {"approved": False}}) == ""
        assert built.declined({"turn": "agent", "answer": {"approved": True}}) is None
        assert built.declined({"turn": "you"}) is None
        assert built.declined_outcome("Not before Friday.") == "Declined: Not before Friday."

    def test_an_answered_card_is_acked_with_the_outcome_and_a_waiting_one_withdrawn(self):
        assert built.close_call({"status": "answered", "version": 3}, "req_a", "wldn-ops", outcome="Deployed at 14:20") == (
            "ack_answer", {"requestId": "req_a", "name": "wldn-ops", "expectedVersion": 3, "outcome": "Deployed at 14:20"}, "closed")
        assert built.close_call({"status": "pending", "version": 1}, "req_a", "wldn-ops", reason="A newer head") == (
            "cancel_request", {"requestId": "req_a", "name": "wldn-ops", "reason": "A newer head"}, "withdrawn")

    def test_a_change_carries_only_what_update_request_takes_and_a_card_posted_again_says_its_older_copy_is_dead(self):
        c = landing()["card"]
        ch = built.change_args(c, "Head is now 9ab12cd after the fix")
        assert set(ch) == {"title", "summary", "context", "artifacts", "approve", "recommendedIds", "rationale", "urgency", "blocking", "changeNote"}
        assert built.posted_again(c)["summary"].startswith("An older copy of this card was lost: dismiss it in the app.\n\n6 units land")
