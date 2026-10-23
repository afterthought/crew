"""A crew agent's Pending You calls and crew's own cards (the rail-cards and card-sessions specs, briefs.11 to briefs.17,
record 0031): crew's card hook (plugin/hooks/cards), loaded as a module, on the result shapes it reads, what it records
after a call, and a call in another agent's name, on any Pending You tool (name_refusal), with the matcher that runs it;
plan.card_refusal on who may post, change or close a card and under which key, and make an area; the decisions of a
card's plannotator session: plan.card_of, session_verdict, local_link, waited, card_folder, judged_dead and young; the
six cards crew builds from their events' facts, the words rule, what a card follows and the act's decisions; and crew
record's: a record's facts and the status its file holds (plan.record_facts), its refusals made on the teams file
alone (record_status) and its raise (raise_record). A question asked through the hook, and the commands' wiring, are
the cards journey's (t-cards) and the review journey's (t-journey-review)."""
import argparse
import datetime
import importlib.machinery
import importlib.util
import json
import pathlib
import re

import pytest

from facts import FLEET as BASE, START

import crew
import plan
import transcript

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


@pytest.fixture(autouse=True)
def previews(monkeypatch, tmp_path):
    """crew's records of the previews it asked for, in a scratch folder rather than the host's."""
    monkeypatch.setattr(plan, "PREVIEWS", tmp_path / "previews")
    return tmp_path / "previews"


def key(name, k, tool="post_request", label="wldn"):
    return plan.card_refusal(FLEET, name, label, tool, k)


ASK = f"{crew.HOME}/plugin/bin/crew"


class TestKeys:
    """rail-cards: a question is asked by four roles in their own name, and crew refuses one from any other role or
    under a row's key (record 0031, briefs.11)."""

    def test_the_users_own_card_is_never_checked(self):
        assert key("chuck@mac-studio", "land/tenant-environments") is None

    @pytest.mark.parametrize("name", ["swb-1-conductor", "wldn-planner", "wldn-ops", "wldn-design"])
    @pytest.mark.parametrize("tool", ["post_request", "update_request", "cancel_request", "ack_answer"])
    def test_the_four_ask_post_change_and_close_a_question_under_a_key_of_their_own_or_none(self, name, tool):
        assert key(name, f"ask/{name}/hold-the-macs", tool) is None and key(name, None, tool) is None

    @pytest.mark.parametrize("name, words", [
        ("swb-1-unit-2", f"Say what you need with `{ASK} needs`, and your conductor gets it and asks if it must."),
        ("swb-1-ops", f"Tell swb-1-conductor what you wait on with `{ASK} tell`."),
        ("wldn-dispatch-mac-studio", f"Ask through wldn-planner with `{ASK} tell`."),
        ("wldn-operator", "The user is in your pane: ask them there."),
        ("crw-9-unit-1", "Tell the partition's operator what you wait on, as your brief says.")])
    def test_any_other_role_asks_nothing_on_a_card_and_is_told_whom_to_ask(self, name, words):
        """rail-cards: a coder asks; the agent's role cannot be read, as for crw-9-unit-1, whose team the teams file
        does not name."""
        for tool in ("post_request", "update_request", "cancel_request", "ack_answer", "create_area"):
            what = "an area" if tool == "create_area" else "a card"
            assert key(name, f"ask/{name}/x", tool) == (
                f"crew refuses {what} from {name}: only a conductor, the planner, main-level ops and the design agent ask "
                f"the user on a card. {words}")

    @pytest.mark.parametrize("name, k, said", [
        ("swb-1-conductor", "land/tenant-environments", "a landing card is crew's, raised when the bolt reads proven and closed when it lands"),
        ("swb-1-conductor", "land/tenant-environments/abc1234", "a landing card is crew's"),
        ("wldn-planner", "proposal/4", "a proposal's card is crew's, raised by crew plan propose and closed at its approval or drop"),
        ("wldn-planner", "proposal/4:2", "a proposal's card is crew's"),
        ("wldn-planner", "batch/3", "a batch's card is crew's"),
        ("wldn-design", "batch/2-1", "a batch's card is crew's"),
        ("wldn-ops", "deploy/dev", "a deploy's card is crew's, raised by crew ops offer"),
        ("wldn-ops", "op/dev/1", "a step's card is crew's, raised by crew ops step"),
        ("wldn-design", "record/atlas-kit/0021", "a record's card is crew's, raised by crew record"),
        ("wldn-design", "proposal/1", "a proposal's card is crew's")])
    def test_none_of_the_four_posts_changes_or_closes_crews_own_card(self, name, k, said):
        for tool, verb in (("post_request", "post"), ("update_request", "change"), ("ack_answer", "close"), ("cancel_request", "close")):
            why = key(name, k, tool)
            assert why.startswith(f"crew refuses {name}'s {verb} of the card under {k}: {said}"), why
            assert why.endswith(f"Ask a question of your own under a key of your own, ask/{name}/<what it is about>.")

    @pytest.mark.parametrize("name", ["swb-1-conductor", "wldn-planner", "wldn-ops", "wldn-design"])
    def test_an_asker_closes_an_answered_verify_card_and_posts_changes_or_withdraws_none(self, name):
        """A card under verify/<unit>/<stamp>, a row form crew no longer raises (teams.17), was a conductor's own, and
        no event of crew's closes it: its ack passes, so its asker closes it with the user's outcome, and its post,
        change and withdrawal are refused, as is any other role's close (crw-2-conductor's three cards of 2026-10-11,
        signal 2026-10-19-crw-2-conductor-2bec975e/01)."""
        k = "verify/a-card-lost-to-its-owner-is-posted-again/20261011-2238"
        assert key(name, k, "ack_answer", label="wldn") is None
        for tool, verb in (("post_request", "post"), ("update_request", "change"), ("cancel_request", "close")):
            assert key(name, k, tool).startswith(f"crew refuses {name}'s {verb} of the card under {k}: a verify report has no card")
        for other in ("verify/x", "verify/x/abc1234", "verify/x/20261007-1412/y"):
            assert key(name, other, "ack_answer").startswith(f"crew refuses {name}'s close of the card under {other}: a verify report")
        assert key("swb-1-unit-2", k, "ack_answer").startswith("crew refuses a card from swb-1-unit-2")

    def test_the_planner_closes_an_old_batch_card_it_posted_and_posts_or_changes_none(self):
        """rail-cards: the planner closes an old batch card. A card under batch/<n>-<k> was the planner's own, posted
        before a batch was one card, which crew never raises; its close passes, its post and change are refused."""
        for tool in ("cancel_request", "ack_answer"):
            assert key("wldn-planner", "batch/2-1", tool) is None
        for tool, verb in (("post_request", "post"), ("update_request", "change")):
            assert key("wldn-planner", "batch/2-1", tool).startswith(f"crew refuses wldn-planner's {verb} of the card under batch/2-1: a batch's card is crew's")
        assert key("wldn-planner", "batch/2", "cancel_request").startswith("crew refuses wldn-planner's close of the card under batch/2")

    def test_a_key_outside_crews_own_is_a_questions_whatever_it_is(self):
        for k in ("gateway-check", "review/x/abc1234", "landing-of-y", "ask/swb-1-conductor/hold"):
            assert key("swb-1-conductor", k) is None

    def test_an_area_is_made_only_under_a_kit_of_the_agents_own(self):
        assert key("swb-1-conductor", "create-area:WilldanGroup/switchboard-kit", "create_area") is None
        assert key("swb-1-conductor", "area:swb-1-conductor", "create_area") == (
            "crew refuses an area under area:swb-1-conductor: swb-1-conductor makes a kit's area only under create-area:WilldanGroup/switchboard-kit.")
        assert key("wldn-planner", "create-area:WilldanGroup/atlas-kit", "create_area") is None
        assert "only under create-area:WilldanGroup/atlas-kit, create-area:WilldanGroup/breadboard-kit or create-area:WilldanGroup/switchboard-kit" in (
            key("wldn-planner", "create-area:agentplot/flywheel-next", "create_area"))


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

    def after(self, monkeypatch, tool, given, response, held=None):
        """The PostToolUse half on one call by swb-1-conductor, its emit caught; held, the key this host's run record
        holds a card under."""
        import io
        import record
        caught = []
        monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
        monkeypatch.setenv("CREW_LABEL", "wldn")
        monkeypatch.setattr(record, "emit", lambda label, act, on, **fields: caught.append((label, act, on, fields)))
        monkeypatch.setattr(cards, "posted", lambda record, label, card: held)
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(
            {"session_id": None, "tool_name": f"mcp__pendingyou__{tool}", "tool_input": given, "tool_response": response})))
        cards.main()
        return caught

    def test_a_question_posted_is_recorded_on_its_asker_with_its_id_and_key_and_nothing_written_on_it(self, monkeypatch):
        given = {"idempotencyKey": "ask/swb-1-conductor/hold-the-macs", "title": "Hold the Macs?", "summary": "Words."}
        assert self.after(monkeypatch, "post_request", given, {"structuredContent": {"requestId": "req_q1"}}) == [
            ("wldn", "card.post", ["agent/swb-1-conductor"], dict(Card="req_q1", Key="ask/swb-1-conductor/hold-the-macs", State=None))]

    def test_a_reply_that_gives_no_card_is_recorded_unread(self, monkeypatch):
        assert self.after(monkeypatch, "post_request", {"idempotencyKey": "ask/swb-1-conductor/x"}, "Posted.") == [
            ("wldn", "card.post", ["agent/swb-1-conductor"], dict(Card=None, Key="ask/swb-1-conductor/x", State="unread"))]

    def test_a_close_is_recorded_under_the_key_its_post_was(self, monkeypatch):
        caught = self.after(monkeypatch, "ack_answer", {"requestId": "req_q1", "outcome": "Held."}, {"structuredContent": {"status": "resolved"}},
                            held="ask/swb-1-conductor/hold-the-macs")
        assert caught == [("wldn", "card.close", ["agent/swb-1-conductor"], dict(Card="req_q1", Key="ask/swb-1-conductor/hold-the-macs", State=None))]

    def test_an_error_writes_nothing(self, monkeypatch):
        assert self.after(monkeypatch, "post_request", {"idempotencyKey": "x"}, {"isError": True}) == []

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

    def test_the_hook_refuses_a_stage_agents_card_and_a_card_of_crews_own_and_lets_a_question_through(self, monkeypatch):
        """rail-cards: a coder asks; a conductor posts its landing card by hand; a conductor closes crew's card; a
        conductor asks."""
        monkeypatch.setenv("CREW_LABEL", "wldn")
        monkeypatch.setattr(plan.crew, "load", lambda: FLEET)
        monkeypatch.setenv("CREW_AGENT", "swb-1-unit-1")
        assert cards.refusal(hooked("post_request", {"idempotencyKey": "ask/swb-1-unit-1/x"})).startswith(
            "crew refuses a card from swb-1-unit-1: only a conductor, the planner, main-level ops and the design agent ask")
        monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
        assert "a landing card is crew's, raised when the bolt reads proven" in cards.refusal(
            hooked("post_request", {"idempotencyKey": "land/tenant-environments", "name": "swb-1-conductor"}))
        monkeypatch.setattr(cards, "posted", lambda record, label, card: "land/tenant-environments" if card == "req_l1" else None)
        assert "close of the card under land/tenant-environments" in cards.refusal(hooked("cancel_request", {"requestId": "req_l1", "reason": "x"}))
        assert cards.refusal(hooked("cancel_request", {"requestId": "req_q1", "reason": "x"})) is None
        assert cards.refusal(hooked("post_request", {"idempotencyKey": "ask/swb-1-conductor/hold", "kind": "text"})) is None

    def test_the_hook_lets_a_conductor_ack_its_answered_verify_card_by_the_key_its_record_holds(self, monkeypatch):
        """crw-2-conductor's ack of req_6d9cca5680a84e08abb2, refused on 2026-10-19 under the key its run record holds
        (signal 2026-10-19-crw-2-conductor-2bec975e/01), goes through; its withdrawal is still refused."""
        monkeypatch.setenv("CREW_LABEL", "wldn")
        monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
        monkeypatch.setattr(plan.crew, "load", lambda: FLEET)
        k = "verify/a-card-lost-to-its-owner-is-posted-again/20261011-2238"
        monkeypatch.setattr(cards, "posted", lambda record, label, card: k if card == "req_v1" else None)
        assert cards.refusal(hooked("ack_answer", {"requestId": "req_v1", "expectedVersion": 2, "outcome": "Fixed"})) is None
        assert f"close of the card under {k}: a verify report has no card" in cards.refusal(
            hooked("cancel_request", {"requestId": "req_v1", "reason": "x"}))

    @pytest.mark.parametrize("agent, row, said", [
        ("wldn-planner", "batch/7", "a batch's card is crew's"), ("swb-1-conductor", "land/b1", "a landing card is crew's"),
        ("wldn-ops", "op/a/1", "a step's card is crew's")])
    def test_the_hook_refuses_an_agents_post_under_crews_key_as_crew_sends_it(self, monkeypatch, agent, row, said):
        """rail-cards: a conductor posts its landing card by hand, under the key as crew sends it: a row's key shorter
        than Pending You's eight characters filled out (cards.post_key, batch/7 as batch/7_), and its revision."""
        monkeypatch.setenv("CREW_LABEL", "wldn")
        monkeypatch.setenv("CREW_AGENT", agent)
        monkeypatch.setattr(plan.crew, "load", lambda: FLEET)
        closed = [dict(Act="card.post", Key=row, By=agent, Card="req_1"), dict(Act="card.close", Card="req_1")]
        for sent in (plan.cards.post_key([], row, agent), plan.cards.post_key(closed, row, agent)):
            assert len(sent) >= plan.cards.KEY_LEAST
            assert cards.refusal(hooked("post_request", {"idempotencyKey": sent, "name": agent})).startswith(
                f"crew refuses {agent}'s post of the card under {sent}: {said}")

    def test_a_close_the_run_record_cannot_key_is_refused_and_a_question_reads_no_plan(self, monkeypatch):
        """rail-cards: crew's record of its cards cannot be read; the plan cannot be read."""
        monkeypatch.setenv("CREW_LABEL", "wldn")
        monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
        monkeypatch.setattr(plan.crew, "load", lambda: FLEET)

        def unread(*a, **k):
            raise OSError("wldn's run record on mac-studio can't be read")
        monkeypatch.setattr(cards, "posted", unread)
        assert cards.refusal(hooked("cancel_request", {"requestId": "req_q1", "reason": "x"})) == (
            "crew could not check this card: wldn's run record on mac-studio can't be read. Try it again later.")
        monkeypatch.setattr(plan, "fetch", unread)
        monkeypatch.setattr(plan, "read", unread)
        assert cards.refusal(hooked("post_request", {"idempotencyKey": "ask/swb-1-conductor/hold-the-macs"})) is None

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


class TestSessions:
    def args(self, k, unit=None, sub="session", label="wldn"):
        return argparse.Namespace(key=k, unit=unit, sub=sub, label=label)

    def test_a_card_command_runs_on_a_rails_key_for_its_partition(self):
        label, d = plan.card_of(BASE, self.args("batch/1"))
        assert (label, d) == ("wldn", plan.CARDS / "wldn" / "batch/1")
        assert plan.card_of(BASE, self.args("batch/2-1", "x1"))[1] == plan.CARDS / "wldn" / "batch/2-1" / "x1"

    @pytest.mark.parametrize("k, unit, said", [
        ("land/t/HEAD", None, "land/t/HEAD is not a card key"), ("verify/x/HEAD", None, "verify/x/HEAD is not a card key"),
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

    def test_a_sweep_releases_a_landings_preview_whose_card_no_live_row_holds_once_it_is_two_minutes_old(self):
        """rail-cards "A card closed elsewhere": the preview crew asked for goes with a landing card the rail holds
        dead, and one asked since the rail's read is left for a later sweep."""
        now = START + datetime.timedelta(minutes=10)
        assert plan.preview_dead("land/y", "2026-10-12T10:00:00Z", {"land/z"}, [], now)
        assert not plan.preview_dead("land/y", "2026-10-12T10:09:00Z", {"land/z"}, [], now)
        assert not plan.preview_dead("land/y", "2026-10-12T10:00:00Z", {"land/y"}, [], now)
        assert not plan.preview_dead("land/y", "2026-10-12T10:00:00Z", set(), ["land/"], now)
        assert not plan.preview_dead("land/y", "not a time", {"land/y"}, [], now)
        with pytest.raises(ValueError):
            plan.preview_dead("land/y", "not a time", set(), [], now)


    # A batch's card, a landing's and a long proposal's are raised with their reading session (card-sessions, record
    # 0031 §5).
    def test_a_batchs_and_a_landings_card_link_their_session_a_long_proposals_when_its_builder_says_and_no_other_card_any(self):
        assert plan.reading_of({"key": "batch/3"}) == "batch" and plan.reading_of({"key": "land/b1"}) == "land"
        assert plan.reading_of({"key": "proposal/4", "session": True}) == "proposal"
        assert plan.reading_of({"key": "proposal/4", "session": False}) is None
        assert plan.reading_of({"key": "deploy/srv"}) is None and plan.reading_of({"key": "record/crew/0031"}) is None

    def test_a_proposal_of_more_than_fifteen_new_units_has_a_reading_whatever_else_it_changes(self):
        def args(*dos):
            return [plan.do_args("wldn", d) for d in dos]
        adds = [f'unit add u{i} "U{i}." --bolt t' for i in range(16)]
        assert plan.proposal_reads(args(*adds)) and not plan.proposal_reads(args(*adds[:15]))
        drops = [f'unit drop d{i} "Gone."' for i in range(20)]
        assert not plan.proposal_reads(args(*adds[:15], *drops)) and not plan.proposal_reads(args(*drops))

    def test_the_session_is_started_before_the_card_is_built_and_its_link_handed_to_the_builder(self, capsys):
        acts = ReadingActs()
        b = plan.card_built(acts, "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        assert acts.sessions == [("wldn", "batch/3")]
        assert b["card"]["context"]["links"] == [{"label": "Read batch 3", "url": "http://mac-studio.ts.swancloud.net:19432"}]
        assert b["card"]["context"]["background"].startswith("Read it all in one session: http://mac-studio.ts.swancloud.net:19432")
        landing = plan.card_built(acts, "wldn", built.landing_card, LANDING)
        assert acts.sessions == [("wldn", "batch/3"), ("wldn", "land/b1")] and landing["key"] == "land/b1"
        assert landing["card"]["context"]["links"] == [{"label": "Read bolt b1", "url": "http://mac-studio.ts.swancloud.net:19432"}]
        assert landing["card"]["context"]["background"].startswith("Read the bolt in one session: http://mac-studio.ts.swancloud.net:19432")
        assert capsys.readouterr().err == ""

    def test_a_card_whose_session_could_not_open_is_raised_all_the_same_saying_so(self, capsys):
        """card-sessions "A batch whose reading could not open": tried twice, and named as the planner's to start."""
        why = "crew can't read z1's change: mac-studio, atl-1's host, did not answer (ssh: timed out)"
        acts = ReadingActs(refused=why)
        c = plan.card_built(acts, "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))["card"]
        assert acts.sessions == [("wldn", "batch/3"), ("wldn", "batch/3")]
        assert c["summary"].startswith("6 changes to read, nothing to approve, since batch 2.\n\nIts reading could not be opened on the "
                                       "tailnet: crew tries it again when the rail is read, and the planner starts it with crew card "
                                       "session batch/3; this card then carries its link.\n\n")
        assert len(c["summary"]) <= 400
        assert c["context"]["background"].startswith(f"The reading could not be opened on the tailnet: {why}\n\n")
        assert c["context"]["links"] == [] and not [a for a in c["artifacts"] if a["kind"] == "url"]
        assert capsys.readouterr().err == (f"card batch/3: its reading could not be opened on the tailnet: {why}; crew tries once more\n"
                                           f"card batch/3: its reading could not be opened on the tailnet: {why}; crew card session "
                                           "batch/3 starts it\n")

    # A batch's or a long proposal's raise tries its reading twice (card-sessions).
    SLOW = "plannotator did not list batch/3's session within 10 seconds, so crew ended it"
    ENDED = "plannotator ended before batch/3's session was ready: stub: refused to start"

    def test_the_first_start_fails_and_the_second_opens(self, capsys):
        acts = ReadingActs(refusals=[self.SLOW, None])
        b = plan.card_built(acts, "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        assert acts.sessions == [("wldn", "batch/3"), ("wldn", "batch/3")]
        assert b["card"]["context"]["links"] == [{"label": "Read batch 3", "url": "http://mac-studio.ts.swancloud.net:19432"}]
        assert "unread" not in b and "could not be opened" not in b["card"]["summary"]
        assert capsys.readouterr().err == f"card batch/3: its reading could not be opened on the tailnet: {self.SLOW}; crew tries once more\n"

    def test_the_second_start_is_made_with_nothing_read_kept(self):
        """The second start writes the batch's files afresh: nothing the first read kept is served to it."""
        fresh = []

        class Acts(ReadingActs):
            def reading(self, label, key, facts):
                fresh.append(plan.READ.bypass > 0)
                return super().reading(label, key, facts)
        plan.card_built(Acts(refusals=[self.SLOW, None]), "wldn", built.batch_card, dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        assert fresh == [False, True]

    def test_both_starts_fail_and_the_card_holds_the_second_reason(self, capsys):
        b = plan.card_built(ReadingActs(refusals=[self.SLOW, self.ENDED]), "wldn", built.batch_card,
                            dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        assert b["unread"] == self.ENDED and b["card"]["context"]["links"] == []
        assert b["card"]["context"]["background"].startswith(f"The reading could not be opened on the tailnet: {self.ENDED}\n\n")
        assert capsys.readouterr().err.splitlines()[-1] == (
            f"card batch/3: its reading could not be opened on the tailnet: {self.ENDED}; crew card session batch/3 starts it")

    def test_a_landings_facts_carry_its_raises_two_tries_so_its_card_tries_once(self):
        """A landing's raise tries twice itself (landing_opened): card_built makes one start for facts with neither."""
        acts = ReadingActs(refused="plannotator is not on this host's path, and a card's session is a plannotator session")
        plan.card_built(acts, "wldn", built.landing_card, LANDING)
        assert acts.sessions == [("wldn", "land/b1")]

    def test_a_landing_whose_reading_could_not_open_is_raised_all_the_same_an_approval_as_before(self, capsys):
        """card-sessions "A landing whose reading could not open"."""
        why = "plannotator is not on this host's path, and a card's session is a plannotator session"
        b = plan.card_built(ReadingActs(refused=why), "wldn", built.landing_card, LANDING)
        c, bare = b["card"], built.landing_card(LANDING)["card"]
        assert c["summary"] == bare["summary"] + ("\n\nIts reading could not be opened on the tailnet: the bolt's conductor starts "
                                                  "it with crew card session land/b1, and this card then carries its link.")
        assert c["context"]["background"] == f"The reading could not be opened on the tailnet: {why}\n\n" + bare["context"]["background"]
        assert (c["kind"], c["approve"], c["context"]["links"]) == ("approve", bare["approve"], [])
        assert b["unread"] == why
        assert capsys.readouterr().err == (f"card land/b1: its reading could not be opened on the tailnet: {why}; "
                                           "crew card session land/b1 starts it\n")

    def test_facts_carrying_the_readings_link_or_why_it_could_not_open_start_no_session(self, capsys):
        """A landing's raise opens the reading itself (landing_opened): the card is built from what it found."""
        link = "http://mac-studio.ts.swancloud.net:19432"
        acts = ReadingActs()
        opened = plan.card_built(acts, "wldn", built.landing_card, dict(LANDING, link=link))
        assert opened["card"]["context"]["links"] == [{"label": "Read bolt b1", "url": link}] and "unread" not in opened
        why = "plannotator did not list land/b1's session within 10 seconds, so crew ended it"
        unread = plan.card_built(acts, "wldn", built.landing_card, dict(LANDING, unread=why))
        assert unread["unread"] == why and unread["card"]["context"]["links"] == []
        assert "crew card session land/b1" in unread["card"]["summary"]
        assert acts.sessions == []
        assert capsys.readouterr().err == (f"card land/b1: its reading could not be opened on the tailnet: {why}; "
                                           "crew card session land/b1 starts it\n")

    def test_crews_close_ends_the_keys_session_and_a_refused_close_keeps_it(self, capsys):
        held = [{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}]
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None)}, held)
        assert plan.row_card_close(None, "wldn", "wldn-planner", "batch/3", outcome="Read; no notes", acts=acts) == "req_b3"
        assert acts.ended == [("wldn", "batch/3")]
        assert capsys.readouterr().out.splitlines()[-2:] == ["card batch/3: req_b3 withdrawn", "ended batch/3's session, plannotator pid 42"]
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None), "cancel_request": (None, "Too many requests.")}, held)
        assert plan.row_card_close(None, "wldn", "wldn-planner", "batch/3", outcome="Read; no notes", acts=acts) is None
        assert acts.ended == []
        landing = [{"Act": "card.post", "Key": "land/b1", "By": "swb-1-conductor", "Card": "req_l1", "On": ["bolt/b1"]}]
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None)}, landing)
        assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", reason="held for a fix: The zone list misses one zone.",
                                   acts=acts) == "req_l1"
        assert acts.ended == [("wldn", "land/b1")]
        assert capsys.readouterr().out.splitlines()[-2:] == ["card land/b1: req_l1 withdrawn", "ended land/b1's session, plannotator pid 42"]

    def test_a_landing_cards_close_releases_its_preview_whatever_became_of_the_card_and_no_other_cards_does(self, capsys):
        """rail-cards "The bolt lands" and "A fix holds the landing": the preview crew asked for goes with the card."""
        landing = [{"Act": "card.post", "Key": "land/b1", "By": "swb-1-conductor", "Card": "req_l1", "On": ["bolt/b1"]}]
        released = "released land/b1's preview of abc1234, preview/0123456789ab"
        for answers in ({"get_request": ({"status": "pending", "version": 1}, None)},
                        {"get_request": ({"status": "pending", "version": 1}, None), "cancel_request": (None, "Too many requests.")}):
            acts = ReadingActs(answers, landing, released=released)
            plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", reason="held for a fix: The zone list misses one zone.", acts=acts)
            assert acts.releases == [("wldn", "land/b1")] and capsys.readouterr().out.splitlines()[-1] == released
        acts = ReadingActs({"get_request": ({"status": "pending", "version": 1}, None)},
                           [{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}])
        plan.row_card_close(None, "wldn", "wldn-planner", "batch/3", outcome="Read; no notes", acts=acts)
        assert acts.releases == []

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

    def test_a_batch_whose_session_was_sent_is_recorded_read_by_crew_whenever_no_card_of_it_closed(self):
        """review-batches, "A batch whose reading session is sent is read, with or without its card": a card closed is
        the record; none held, or one lost or whose close was refused, which row_card_close gives as None, is not."""
        assert plan.batch_read_close("req_b13") is False
        assert plan.batch_read_close(None) is True

    def test_a_batch_wait_goes_on_while_neither_has_the_users_word_and_ends_on_a_card_closed_outside_crew(self):
        for decided in (None, ("dismissed", None, None)):
            assert plan.batch_waited("batch/3", decided, {"status": "pending", "turn": "you"}) is None
            assert plan.batch_waited("batch/3", decided, None) is None
        assert plan.batch_waited("batch/3", None, {"status": "cancelled"}) == (
            "closed", "batch/3: its card was closed outside crew; Pending You shows it cancelled", "cancelled")

    # A batch's wait starts its reading when none runs (card-sessions).
    @pytest.mark.parametrize("recorded, held, refused, step", [
        ({"pid": 42}, "req_b3", None, ("wait", None)), (None, None, None, ("wait", None)), ({"pid": 42}, None, None, ("wait", None)),
        (None, "req_b3", None, ("start", None)),
        (None, "req_b3", "plannotator is not on this host's path", ("card", "batch/3's reading could not be opened: plannotator is not "
                                                                    "on this host's path; crew card session batch/3 starts it once that "
                                                                    "is mended, and the wait goes on for its card"))])
    def test_a_batch_wait_with_its_card_held_and_no_session_starts_its_reading_and_says_once_when_it_cannot(self, recorded, held, refused, step):
        assert plan.batch_unstarted("batch/3", recorded, held, refused) == step

    def test_a_batch_wait_starts_no_reading_for_a_batch_answered_in_a_pane(self):
        """review-batches "A batch answered in a main-level pane": it waits on the user no more, and the wait ends on its
        answer."""
        assert plan.batch_unstarted("batch/3", None, "req_b3", answered=True) == ("wait", None)

    def waited_on(self, monkeypatch, tmp_path, acts):
        """crew card wait batch/3 on mac-studio, the main level's host, its card and its reading read as acts gives them."""
        monkeypatch.setattr(plan, "batch_read", lambda fleet, label, n, acts: dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        monkeypatch.setattr(plan, "raise_batch", lambda fleet, row, acts=None, note=None: acts.emit("wldn", "card.update", ["batch/3"],
                                                                                                   Card="req_b3", Key=row["key"], note=note))
        fleet = dict(FLEET, partitions=dict(FLEET["partitions"], wldn=dict(FLEET["partitions"]["wldn"], machine="mac-studio")))
        plan.batch_wait(fleet, "wldn", "batch/3", tmp_path, acts)

    def test_a_batch_wait_starts_the_missing_reading_and_changes_its_card_to_carry_it(self, monkeypatch, tmp_path, capsys):
        """card-sessions "A card raised without its reading", for a batch's wait: the start is recorded and the card
        changed before the wait reads it."""
        reads = []

        class Acts(ReadingActs):
            def bridge(self, name, later, held=None):
                py = super().bridge(name, later, held)
                answer = py.answer

                def answered(tool, args):
                    if tool == "get_request":
                        reads.append(args["requestId"])
                        return ({"status": "pending", "turn": "you", "version": 3} if len(reads) == 1 else
                                {"status": "answered", "turn": "agent", "answer": {}}), None
                    return answer(tool, args)
                py.answer = answered
                return py
        acts = Acts(entries=[{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}])
        self.waited_on(monkeypatch, tmp_path, acts)
        assert acts.sessions == [("wldn", "batch/3")]
        assert [(e["Act"], e.get("note")) for e in acts.emitted][:2] == [("card.reading", None), ("card.update", plan.RELINKED)]
        out = capsys.readouterr().out.splitlines()
        assert out[:2] == ["http://mac-studio.ts.swancloud.net:19432", "batch/3: sent back on its card, with no note"]

    def test_a_batch_wait_whose_reading_will_not_open_says_so_once_and_waits_on_its_card(self, monkeypatch, tmp_path, capsys):
        """card-sessions "The reading still will not open": the card is left as it is and returns the user's word."""
        why = "plannotator is not on this host's path, and a card's session is a plannotator session"
        acts = ReadingActs({"get_request": ({"status": "answered", "turn": "agent", "version": 3, "answer": {"note": {"text": "Read."}}}, None)},
                           [{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}], refused=why)
        self.waited_on(monkeypatch, tmp_path, acts)
        assert not [t for t, _ in acts.calls if t == "update_request"]
        assert (acts.emitted[0]["Act"], acts.emitted[0]["refused"]) == ("card.reading", why)
        assert capsys.readouterr().err.splitlines() == [
            f"batch/3's reading could not be opened: {why}; crew card session batch/3 starts it once that is mended, and the wait "
            "goes on for its card"]

    def test_a_sessions_result_gives_its_count_of_annotations(self, tmp_path):
        (tmp_path / "result.json").write_text(json.dumps({"decision": "annotated", "feedback": "a", "annotationCount": 2}))
        assert plan.card_result(tmp_path) == ("annotated", "a", 2)
        (tmp_path / "result.json").write_text(json.dumps({"decision": "approved", "annotationCount": "two"}))
        assert plan.card_result(tmp_path) == ("approved", None, None)

    def test_the_sweeps_raise_of_a_batch_whose_card_is_lost_posts_it_again_saying_its_older_copy_is_dead(self, monkeypatch, tmp_path):
        (tmp_path / "batch-wldn-3.md").write_text("## x1 (swb-1)\n\nx1 gives each tenant its own zone.\n")
        monkeypatch.setattr(plan, "batch_file", lambda label, n: tmp_path / f"batch-{label}-{n}.md")
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: None)
        held = [{"Act": "review.batch", "Batch": "3", "Units": "x1:swb-1@aaa1", "On": ["batch/3"], "At": "2026-10-12T10:00:00Z"},
                {"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}]
        acts = ReadingActs({"get_request": (None, "Not found: request:req_b3."), "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                            "post_request": ({"requestId": "req_b4", "version": 1}, None)}, held)
        row = {"label": "wldn", "key": "batch/3", "group": "batches"}
        assert plan.raise_batch(FLEET, row, acts) == "req_b4"
        assert [(e["Act"], e.get("State"), e["Card"]) for e in acts.emitted] == [("card.close", "lost", "req_b3"), ("card.post", None, "req_b4")]
        sent = next(a for t, a in acts.calls if t == "post_request")
        assert sent["summary"].startswith("An older copy of this card was lost: dismiss it in the app.\n\n1 change to read")
        assert acts.sessions == [("wldn", "batch/3")]
        assert plan.raise_batch(FLEET, dict(row, key="batch/3-1"), acts) is None
        assert plan.raise_batch(FLEET, dict(row, key="batch/4"), acts) is None

    def test_the_sweeps_raise_of_a_batch_handed_an_older_copy_this_host_cant_reach_posts_it_saying_that_copy_is_dead(self, monkeypatch, tmp_path):
        """rail-cards, "The main level moved to another host": batch 3's card is held under another host's sign-in, so
        this host holds none and its raise, handed the older copy, posts one card saying it is dead and closes nothing;
        a raise handed none posts the batch's card as it is."""
        (tmp_path / "batch-wldn-3.md").write_text("## x1 (swb-1)\n\nx1 gives each tenant its own zone.\n")
        monkeypatch.setattr(plan, "batch_file", lambda label, n: tmp_path / f"batch-{label}-{n}.md")
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: None)
        held = [{"Act": "review.batch", "Batch": "3", "Units": "x1:swb-1@aaa1", "On": ["batch/3"], "At": "2026-10-12T10:00:00Z"}]
        answers = {"match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
                   "post_request": ({"requestId": "req_b4", "version": 1}, None)}
        row = {"label": "wldn", "key": "batch/3", "group": "batches"}
        acts = ReadingActs(answers, held)
        assert plan.raise_batch(FLEET, dict(row, dead="req_b3"), acts) == "req_b4"
        assert [(e["Act"], e["Card"]) for e in acts.emitted] == [("card.post", "req_b4")]
        assert [t for t, _ in acts.calls if t != "tell"] == ["match_area", "post_request"]
        assert acts.calls[[t for t, _ in acts.calls].index("post_request")][1]["summary"].startswith(f"{built.DEAD}\n\n1 change to read")
        acts = ReadingActs(answers, held)
        assert plan.raise_batch(FLEET, row, acts) == "req_b4"
        assert next(a for t, a in acts.calls if t == "post_request")["summary"].startswith("1 change to read")

    POSTED = {"match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
              "post_request": ({"requestId": "req_n2", "version": 1}, None)}

    def summaries(self, acts):
        return [a["summary"] for t, a in acts.calls if t == "post_request"]

    def test_the_sweeps_raise_of_a_proposal_handed_an_older_copy_posts_it_saying_that_copy_is_dead(self, monkeypatch):
        """rail-cards, "A proposal's card left on the host the main level left": proposal 1's card is held under another
        host's sign-in, so this host holds none, and its raise at the sweep, handed dead, posts one card saying the older
        copy is dead; without it, the plain card."""
        from test_proposal_life import CARDED, proposals_with, write
        monkeypatch.setattr(plan, "recfix", lambda text, what: None)
        w = write()
        w.files["proposals.rec"] = proposals_with(("Console first.", ['unit add a-new "A new unit." --bolt console-pages'])).text()
        acts = ReadingActs(self.POSTED)
        assert plan.raise_proposal_at(CARDED, "wldn", w, 1, "sweep", acts, dead=True) == "req_n2"
        assert [(e["Act"], e["Card"]) for e in acts.emitted] == [("card.post", "req_n2")]
        plain = ReadingActs(self.POSTED)
        assert plan.raise_proposal_at(CARDED, "wldn", w, 1, "sweep", plain) == "req_n2"
        (dead,), (bare,) = self.summaries(acts), self.summaries(plain)
        assert dead == f"{built.DEAD}\n\n{bare}"

    def test_the_sweeps_raise_of_a_landing_handed_an_older_copy_posts_it_saying_that_copy_is_dead(self, monkeypatch):
        """rail-cards, "A landing's card left on the host its team left": an approval of risk high, saying an older copy
        was lost."""
        team = dict(FLEET["teams"]["swb-1"], machine="mac-studio")
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, object(), team))
        monkeypatch.setattr(plan, "land_facts", lambda fleet, label, p, b, t: (dict(LANDING, team="swb-1", host="mac-studio", base="abc0000"), None))
        monkeypatch.setattr(plan, "landing_opened", lambda fleet, label, p, b, t, card, acts: dict(card, link="http://mac-studio.ts.swancloud.net:19432"))
        monkeypatch.setattr(plan, "landing_preview", lambda fleet, t, label, bolt, card, acts: None)
        row = {"label": "wldn", "key": "land/b1", "group": "land"}
        acts, plain = ReadingActs(self.POSTED), ReadingActs(self.POSTED)
        assert plan.raise_land(FLEET, dict(row, dead="req_l1"), acts) == "req_n2"
        assert plan.raise_land(FLEET, row, plain) == "req_n2"
        assert [(e["Act"], e["Card"]) for e in acts.emitted] == [("card.post", "req_n2")]
        (dead,), (bare,) = self.summaries(acts), self.summaries(plain)
        assert dead == f"{built.DEAD}\n\n{bare}"
        assert next(a for t, a in acts.calls if t == "post_request")["approve"]["risk"] == "high"

LANDING = dict(bolt="b1", kit="k", units=["v1"], chores=[], batches={}, head="abc1234", at=None, moved=0, pr=None)


class ReadingActs:
    """A stand-in for the act's reach (plan.CardActs) where a card's reading session starts and ends, and a landing's
    preview is asked for and released: a session's link given, or its start refused with why, always (refused) or for
    each start in turn (refusals, None for a start that opens); the preview given (preview), and its release said
    (released); Pending You's tools answered from answers, a (got, words) pair."""

    def __init__(self, answers=None, entries=(), refused=None, started=True, preview=None, released=None, refusals=()):
        self.answers, self.held, self.refused, self.started = dict(answers or {}), list(entries), refused, started
        self.refusals = list(refusals)
        self.given, self.said = preview, released
        self.sessions, self.ended, self.emitted, self.calls, self.previews, self.releases = [], [], [], [], [], []

    def preview(self, label, key, facts):
        self.previews.append((label, key, facts["head"], facts["previewed"]))
        return self.given

    def release_preview(self, label, key):
        self.releases.append((label, key))
        return self.said

    def tell(self, name, text):
        self.calls.append(("tell", {"to": name, "text": text}))
        return True

    def session(self, label, key, facts):
        return self.reading(label, key, facts)[0]

    def reading(self, label, key, facts):
        self.sessions.append((label, key))
        why = self.refusals.pop(0) if self.refusals else self.refused
        if why:
            raise crew.Refusal(why)
        return "http://mac-studio.ts.swancloud.net:19432", False, self.started

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
                acts.calls.append((tool, args))
                return acts.answers.get(tool, ({"ok": True}, None))

            def call(self, tool, args):
                got, words = self.answer(tool, args)
                if words is not None:
                    raise crew.Refusal(f"Pending You refused {tool}: {words}")
                return got
        return Py()

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act))

    def entries(self, label):
        return self.held

    def host(self):
        return "mac-studio"

    def caller(self):
        return "wldn-planner"


class TestLandingSession:
    """crew card session land/<bolt> (card-sessions "A landing's session follows the bolt's head"): its link printed,
    the open card changed in place to carry it when the session was started anew while the card waits on the user, and
    left once the user answered it; refused for a bolt that does not read proven, and off its team's host."""
    TEAM = dict(FLEET["teams"]["swb-1"], machine="mac-studio")
    HELD = [{"Act": "card.post", "Key": "land/b1", "By": "swb-1-conductor", "Card": "req_l1", "On": ["bolt/b1"]}]
    LINK = "http://mac-studio.ts.swancloud.net:19432"

    def run(self, monkeypatch, acts, why=None, team=TEAM, previewed=False):
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, object(), team))
        monkeypatch.setattr(plan, "land_facts", lambda fleet, label, p, b, t: (None, why) if why else (
            dict(LANDING, team="swb-1", host="mac-studio", base="abc0000"), None))
        monkeypatch.setattr(plan, "head_previewed", lambda fleet, t, head: (previewed, None))
        plan.land_session(FLEET, "wldn", "land/b1", acts)

    @pytest.mark.parametrize("started, got, change", [
        (True, {"status": "pending", "turn": "you"}, True), (True, {"status": "snoozed"}, True), (False, {"status": "pending"}, False),
        (True, {"status": "answered", "turn": "agent"}, False), (True, {"status": "resolved"}, False), (True, None, False)])
    def test_the_card_is_changed_only_for_a_session_started_anew_while_it_waits_on_the_user(self, started, got, change):
        assert plan.relinks(started, got) is change

    def test_a_session_started_anew_changes_the_waiting_card_in_place_to_carry_its_link(self, monkeypatch, capsys):
        acts = ReadingActs({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None)}, self.HELD)
        self.run(monkeypatch, acts)
        sent = [a for t, a in acts.calls if t == "update_request"]
        assert len(sent) == 1 and sent[0]["changeNote"] == "Its reading is open again at a new link"
        assert (sent[0]["requestId"], sent[0]["expectedVersion"]) == ("req_l1", 3)
        assert sent[0]["context"]["links"][0] == {"label": "Read bolt b1", "url": self.LINK}
        assert not [t for t, _ in acts.calls if t == "post_request"]
        assert capsys.readouterr().out.splitlines() == [self.LINK, "card land/b1: req_l1 changed"]

    def test_a_card_carrying_its_new_link_keeps_the_preview_it_lists(self, monkeypatch):
        """crew card session's change of the card lists the head's preview as the raise did, taken by keep."""
        p = dict(head=LANDING["head"], name="preview/0123456789ab", state="up", addresses={"web": "http://web.example"})
        acts = ReadingActs({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None)}, self.HELD, preview=p)
        self.run(monkeypatch, acts, previewed=True)
        sent = next(a for t, a in acts.calls if t == "update_request")
        assert acts.previews == [("wldn", "land/b1", LANDING["head"], True)]
        assert {"label": "Preview: web", "url": "http://web.example"} in sent["context"]["links"]

    def test_a_running_session_given_again_changes_nothing(self, monkeypatch, capsys):
        acts = ReadingActs(entries=self.HELD, started=False)
        self.run(monkeypatch, acts)
        assert acts.calls == [] and capsys.readouterr().out == f"{self.LINK}\n"

    def test_a_card_the_user_has_answered_is_left_and_no_card_follows_it(self, monkeypatch, capsys):
        """card-sessions "A card already approved"."""
        acts = ReadingActs({"get_request": ({"status": "answered", "turn": "agent", "answer": {"approved": True}}, None)}, self.HELD)
        self.run(monkeypatch, acts)
        assert [t for t, _ in acts.calls] == ["get_request"] and acts.emitted == []
        assert capsys.readouterr().out.splitlines() == [self.LINK, "card land/b1: req_l1 is left as it is: the user has answered it"]

    def test_a_bolt_that_does_not_read_proven_is_refused_saying_why_and_nothing_is_started(self, monkeypatch):
        """card-sessions "A landing card", while a unit has not merged."""
        acts = ReadingActs(entries=self.HELD)
        with pytest.raises(plan.Refusal, match="^bolt b1 does not read proven, so its landing card is not raised and has no "
                                               "reading: unit b has not merged: it is verify$"):
            self.run(monkeypatch, acts, why="unit b has not merged: it is verify")
        assert acts.sessions == []

    def test_off_its_teams_host_it_is_refused_naming_that_host(self, monkeypatch):
        acts = ReadingActs(entries=self.HELD)
        with pytest.raises(plan.Refusal, match="land/b1's reading session runs on chuck-herdr-alpha, the host of the team holding its bolt"):
            self.run(monkeypatch, acts, team=FLEET["teams"]["swb-1"])
        assert acts.sessions == []

    def started(self, monkeypatch, acts, team=TEAM):
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, object(), team))
        monkeypatch.setattr(plan, "land_facts", lambda fleet, label, p, b, t: (dict(LANDING, team="swb-1", host="mac-studio", base="abc0000"), None))
        monkeypatch.setattr(plan, "head_previewed", lambda fleet, t, head: (False, None))
        plan.land_start(FLEET, "wldn", "land/b1", acts)

    def test_a_wait_with_no_session_starts_the_reading_and_changes_the_held_card_to_carry_it(self, monkeypatch, capsys):
        """card-sessions "A card raised without its reading" and "Waiting again after a decision"."""
        acts = ReadingActs({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None)}, self.HELD)
        self.started(monkeypatch, acts)
        assert acts.sessions == [("wldn", "land/b1")]
        change = next(a for t, a in acts.calls if t == "update_request")
        assert change["context"]["links"][0] == {"label": "Read bolt b1", "url": self.LINK}
        assert capsys.readouterr().out.splitlines() == [self.LINK, "card land/b1: req_l1 changed"]

    def test_a_wait_whose_reading_still_will_not_open_is_refused_naming_crew_card_session(self, monkeypatch):
        """card-sessions "The reading still will not open": the card is not changed."""
        acts = ReadingActs(entries=self.HELD, refused="plannotator is not on this host's path, and a card's session is a plannotator session")
        with pytest.raises(plan.Refusal, match=r"^land/b1's reading could not be opened: plannotator is not on this host's path, "
                                               r"and a card's session is a plannotator session; crew card session land/b1 starts "
                                               r"it once that is mended$"):
            self.started(monkeypatch, acts)
        assert acts.calls == [] and acts.emitted == []

    def test_a_wait_with_no_card_held_is_refused_and_starts_nothing(self, monkeypatch):
        """card-sessions "No landing card held"."""
        acts = ReadingActs(entries=[])
        with pytest.raises(plan.Refusal, match="^no session was started for card land/b1, and no landing card of b1 is held on this host$"):
            self.started(monkeypatch, acts)
        assert acts.sessions == []
        with pytest.raises(plan.Refusal, match="no landing card of b1 is held"):
            self.started(monkeypatch, ReadingActs(entries=self.HELD), team=None)

    def opened(self, monkeypatch, tmp_path, on):
        """reading_open of land/b1 at head def5678, its recorded session serving the bolt as it stood at on: what it
        ended, and the folder of the session it opened."""
        d = tmp_path / "wldn" / "land/b1"
        (d / on).mkdir(parents=True)
        docs = ", ".join(str((d / on).resolve() / f) for f in ("00-b1.md", "01-v1-proposal.md", "02-b1-diff.txt"))
        (d / "session.json").write_text(json.dumps({"pid": 42, "document": docs, "url": self.LINK, "started": "2026-10-19T10:00:00Z"}))
        ended, opened = [], []
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        monkeypatch.setattr(plan, "end_session", lambda label, key, unit=None: ended.append((label, key)) or [f"ended {key}'s session, plannotator pid 42"])
        monkeypatch.setattr(plan, "landing_write", lambda fleet, facts, folder: folder)
        monkeypatch.setattr(plan, "session_open", lambda at, name, write: opened.append((at, name, write())) or (self.LINK, None, True))
        facts = dict(LANDING, team="swb-1", host="mac-studio", base="abc0000", head="def5678" + "0" * 33)
        assert plan.reading_open(FLEET, "wldn", "land/b1", facts) == (self.LINK, None, True)
        assert opened == [(d, "land/b1's session", d / "def5678")]
        return ended

    def test_a_merge_that_moves_the_head_ends_the_old_heads_session_and_opens_one_on_the_new(self, monkeypatch, tmp_path, capsys):
        """card-sessions "A merge moves the head"."""
        assert self.opened(monkeypatch, tmp_path, "abc1234") == [("wldn", "land/b1")]
        assert capsys.readouterr().out == "ended land/b1's session, plannotator pid 42\n"

    def test_a_session_on_the_head_as_it_stands_is_given_again_and_nothing_is_ended(self, monkeypatch, tmp_path, capsys):
        assert self.opened(monkeypatch, tmp_path, "def5678") == []
        assert capsys.readouterr().out == ""


class TestReadingAgain:
    """crew card session batch/<n> or proposal/<n> (card-sessions "Starting a batch's or a proposal's reading changes
    its card", "A later try of a reading is recorded"): its link printed, the planner's card changed in place to carry
    it while it waits on the user when the session started anew or the card stands without its reading, and the try
    recorded as card.reading when it started or refused."""
    HELD = [{"Act": "card.post", "Key": "batch/3", "By": "wldn-planner", "Card": "req_b3", "On": ["batch/3"]}]
    UNREAD = [dict(HELD[0], Unread="plannotator ended before batch/3's session was ready: stub: refused to start", At="2026-10-12T10:00:00Z")]
    LINK = "http://mac-studio.ts.swancloud.net:19432"
    WAITING = {"get_request": ({"status": "pending", "turn": "you", "version": 3}, None),
               "match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None)}

    def run(self, monkeypatch, tmp_path, acts, key="batch/3"):
        """crew card session <key> on mac-studio, the main level's host, its rail row read as present."""
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        monkeypatch.setattr(plan, "card_row", lambda fleet, label, k: (dict(key=k, doc=("batch", "wldn", 3)), []))
        monkeypatch.setattr(plan, "batch_read", lambda fleet, label, n, acts: dict(n=3, previous=2, units=BATCH_UNITS, link=None))
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: None)
        (tmp_path / "batch-wldn-3.md").write_text("# Batch 3\n")
        monkeypatch.setattr(plan, "batch_file", lambda label, n: tmp_path / f"batch-{label}-{n}.md")
        fleet = dict(FLEET, partitions=dict(FLEET["partitions"], wldn=dict(FLEET["partitions"]["wldn"], machine="mac-studio")))
        plan.card_session(fleet, argparse.Namespace(key=key, unit=None, sub="session", label="wldn"), acts)

    def test_a_start_anew_changes_the_waiting_card_to_carry_its_link_and_is_recorded(self, monkeypatch, tmp_path, capsys):
        """card-sessions "A batch card raised without its reading"."""
        acts = ReadingActs(dict(self.WAITING), self.UNREAD)
        self.run(monkeypatch, tmp_path, acts)
        sent = [a for t, a in acts.calls if t == "update_request"]
        assert len(sent) == 1 and (sent[0]["requestId"], sent[0]["changeNote"]) == ("req_b3", plan.RELINKED)
        assert sent[0]["context"]["links"][0] == {"label": "Read batch 3", "url": self.LINK}
        assert [(e["Act"], e["Key"], e.get("Card"), e.get("refused"), e.get("Unread")) for e in acts.emitted] == [
            ("card.reading", "batch/3", "req_b3", None, None), ("card.update", "batch/3", "req_b3", None, None)]
        assert capsys.readouterr().out.splitlines() == [self.LINK, "card batch/3: req_b3 changed"]

    def test_a_card_the_user_has_answered_is_left_and_no_card_follows_it(self, monkeypatch, tmp_path, capsys):
        """card-sessions "A proposal card already answered", for a batch's: the start is recorded, the card left."""
        acts = ReadingActs({"get_request": ({"status": "answered", "turn": "agent", "answer": {}}, None)}, self.HELD)
        self.run(monkeypatch, tmp_path, acts)
        assert [t for t, _ in acts.calls] == ["get_request"] and [e["Act"] for e in acts.emitted] == ["card.reading"]
        assert capsys.readouterr().out.splitlines() == [self.LINK, "card batch/3: req_b3 is left as it is: the user has answered it"]

    def test_a_session_given_again_on_a_card_with_its_link_changes_and_records_nothing(self, monkeypatch, tmp_path, capsys):
        """card-sessions "A session that still runs" and "A link given again"."""
        acts = ReadingActs(entries=self.HELD, started=False)
        self.run(monkeypatch, tmp_path, acts)
        assert acts.calls == [] and acts.emitted == [] and capsys.readouterr().out == f"{self.LINK}\n"

    def test_a_session_given_again_on_a_card_standing_without_its_reading_changes_it(self, monkeypatch, tmp_path):
        """A start whose card change did not go through: the link given again is put on the card."""
        acts = ReadingActs(dict(self.WAITING), self.UNREAD, started=False)
        self.run(monkeypatch, tmp_path, acts)
        assert [t for t, _ in acts.calls if t == "update_request"] == ["update_request"]
        assert [e["Act"] for e in acts.emitted] == ["card.update"]

    def test_a_refusal_is_recorded_with_crews_words_and_raised(self, monkeypatch, tmp_path):
        """card-sessions "A try that refuses": the card is not changed."""
        why = "plannotator did not list batch/3's session within 10 seconds, so crew ended it"
        acts = ReadingActs(entries=self.HELD, refused=why)
        with pytest.raises(plan.Refusal, match=f"^{re.escape(why)}$"):
            self.run(monkeypatch, tmp_path, acts)
        assert acts.calls == []
        assert acts.emitted == [dict(Act="card.reading", by="wldn-planner", refused=why, Key="batch/3", Card="req_b3")]

    def test_a_proposals_reading_is_opened_on_the_open_proposal_of_its_chain_and_its_card_changed_by_its_raise(self, monkeypatch, tmp_path):
        seen = []
        monkeypatch.setattr(plan, "chain_read", lambda fleet, label, first: ("w", 6))
        monkeypatch.setattr(plan, "raise_proposal", lambda fleet, row, acts=None, event="sweep": seen.append((row["key"], event)))

        class Acts(ReadingActs):
            def reading(self, label, key, facts):
                seen.append(facts)
                return super().reading(label, key, facts)
        held = [dict(self.HELD[0], Key="proposal/4", Card="req_p4", On=["proposal/4"])]
        acts = Acts({"get_request": ({"status": "pending", "turn": "you", "version": 3}, None)}, held)
        monkeypatch.setattr(plan, "card_row", lambda fleet, label, k: (dict(key=k, doc=("page", "wldn", 6)),
                                                                       [{"proposal": 6, "changes": [{"do": f'unit add u{i} "U{i}." --bolt t'} for i in range(16)]}]))
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        fleet = dict(FLEET, partitions=dict(FLEET["partitions"], wldn=dict(FLEET["partitions"]["wldn"], machine="mac-studio")))
        plan.card_session(fleet, argparse.Namespace(key="proposal/4", unit=None, sub="session", label="wldn"), acts)
        assert seen == [dict(n=6, first=4), ("proposal/4", "relink")]
        assert [(e["Act"], e["Key"], e["Card"]) for e in acts.emitted] == [("card.reading", "proposal/4", "req_p4")]


class TestLandingPreview:
    """A landing card is raised with its preview asked for first when the kit's policy at the head declares one
    (rail-cards, record 0031 §3), through the act's reach, and with none and no word of one when it does not."""
    TEAM = dict(FLEET["teams"]["swb-1"], machine="mac-studio")
    PREVIEW = dict(head=LANDING["head"], name="preview/0123456789ab", state="starting", addresses={"web": "http://web.example"})
    POSTED = {"match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
              "post_request": ({"requestId": "req_l2", "version": 1}, None)}

    def raised(self, monkeypatch, acts, previewed, note=None):
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, object(), self.TEAM))
        monkeypatch.setattr(plan, "land_facts", lambda fleet, label, p, b, t: (dict(LANDING, team="swb-1", host="mac-studio", base="abc0000"), None))
        monkeypatch.setattr(plan, "head_previewed", lambda fleet, t, head: previewed)
        return plan.raise_land(FLEET, {"label": "wldn", "key": "land/b1"}, acts, note=note)

    def sent(self, acts, tool):
        return next(a for t, a in acts.calls if t == tool)

    def test_a_kit_declaring_a_preview_has_it_asked_first_and_listed_on_the_card(self, monkeypatch):
        """rail-cards "A kit that declares a preview"."""
        acts = ReadingActs(dict(self.POSTED), preview=self.PREVIEW)
        assert self.raised(monkeypatch, acts, (True, None)) == "req_l2"
        assert acts.previews == [("wldn", "land/b1", LANDING["head"], True)]
        card = self.sent(acts, "post_request")
        assert {"label": "Preview: web", "url": "http://web.example"} in card["context"]["links"]
        assert card["approve"]["risk"] == "high"

    def test_a_kit_declaring_none_is_asked_nothing_and_its_card_says_nothing_of_one(self, monkeypatch):
        """rail-cards "A kit that declares none"."""
        acts = ReadingActs(dict(self.POSTED), preview=self.PREVIEW)
        self.raised(monkeypatch, acts, (False, None))
        assert acts.previews == [] and "preview" not in json.dumps(self.sent(acts, "post_request")).lower()

    def test_a_preview_recorded_where_the_policy_now_declares_none_is_handed_to_the_act_to_release(self, monkeypatch, previews):
        (previews / "wldn").mkdir(parents=True)
        (previews / "wldn" / "b1.json").write_text(json.dumps({"head": "0" * 40, "main": "/kit/main"}))
        acts = ReadingActs(dict(self.POSTED))
        self.raised(monkeypatch, acts, (False, None))
        assert acts.previews == [("wldn", "land/b1", LANDING["head"], False)]

    def test_a_policy_crew_cannot_read_is_said_as_a_preview_not_asked_and_the_card_raised(self, monkeypatch):
        why = "git show in /kit/main on mac-studio failed: fatal: bad object abc1234"
        acts = ReadingActs(dict(self.POSTED), preview=self.PREVIEW)
        assert self.raised(monkeypatch, acts, (None, why)) == "req_l2"
        assert acts.previews == []
        assert f"A preview of abc1234 was asked for and is not there: {why}. Nothing waits on it." in (
            self.sent(acts, "post_request")["context"]["background"])

    def test_a_previews_end_changes_the_open_card_with_its_own_note(self, monkeypatch):
        """rail-cards "The host is busy when the card is raised": the card changed in place with the preview's note."""
        held = [{"Act": "card.post", "Key": "land/b1", "By": "swb-1-conductor", "Card": "req_l1", "On": ["bolt/b1"]}]
        acts = ReadingActs({"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)}, held,
                           preview=dict(self.PREVIEW, state="up"))
        assert self.raised(monkeypatch, acts, (True, None), note="Its preview of abc1234 is up") == "req_l1"
        change = self.sent(acts, "update_request")
        assert change["changeNote"] == "Its preview of abc1234 is up"
        assert {"label": "Preview: web", "url": "http://web.example"} in change["context"]["links"]


class TestLandingReading:
    """A landing's raise opens its reading itself, and tries once more when it refuses, as crew card session would
    (card-sessions "A landing's raise tries its reading again before raising without it"): the kit's main fetched on
    the team's host, the landing read afresh and its reading opened again with those facts."""
    TEAM = dict(FLEET["teams"]["swb-1"], machine="mac-studio")
    POSTED = {"match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}, None),
              "post_request": ({"requestId": "req_l2", "version": 1}, None)}
    LINK = "http://mac-studio.ts.swancloud.net:19432"
    SLOW = "plannotator did not list land/b1's session within 10 seconds, so crew ended it"
    ENDED = "plannotator ended before land/b1's session was ready: stub: refused to start"

    def raised(self, monkeypatch, acts, fresh=None, fetched=None):
        """raise_land of land/b1: the first read proven at abc1234, the second as fresh gives it, (facts, why), or
        refused with fresh's words, proven at def5678 when None; the card, whether each read was a fresh one, and what
        was fetched."""
        reads, fetches = [], []
        first = dict(LANDING, team="swb-1", host="mac-studio", base="abc0000")

        def facts(fleet, label, p, b, t):
            reads.append(plan.READ.bypass > 0)
            if len(reads) > 1 and isinstance(fresh, str):
                raise plan.Refusal(fresh)
            return (first, None) if len(reads) == 1 else fresh or (dict(first, head="def5678"), None)

        def fetch(fleet, t, where, *args):
            fetches.append((where, *args))
            if fetched:
                raise plan.Refusal(fetched)
            return 0, ""
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, object(), self.TEAM))
        monkeypatch.setattr(plan, "land_facts", facts)
        monkeypatch.setattr(plan, "head_previewed", lambda fleet, t, head: (False, None))
        monkeypatch.setattr(plan.gather, "has_origin", lambda main: True)
        monkeypatch.setattr(plan, "kit_git", fetch)
        card = plan.raise_land(FLEET, {"label": "wldn", "key": "land/b1"}, acts)
        return card, reads, fetches

    def sent(self, acts):
        return next((a for t, a in acts.calls if t == "post_request"), None)

    def test_a_reading_that_opens_at_once_is_started_once_and_nothing_is_fetched(self, monkeypatch):
        acts = ReadingActs(dict(self.POSTED))
        assert self.raised(monkeypatch, acts) == ("req_l2", [False], [])
        assert acts.sessions == [("wldn", "land/b1")]
        assert self.sent(acts)["context"]["links"][0] == {"label": "Read bolt b1", "url": self.LINK}

    def test_the_first_start_fails_and_the_second_opens(self, monkeypatch, capsys):
        """card-sessions "The first start fails and the second opens": the card carries the second try's link, built
        from the landing read afresh after the kit's main was fetched."""
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW])
        assert self.raised(monkeypatch, acts) == ("req_l2", [False, True], [("/kit/main", "fetch", "-q", "origin")])
        assert acts.sessions == [("wldn", "land/b1"), ("wldn", "land/b1")]
        card = self.sent(acts)
        assert card["context"]["links"][0] == {"label": "Read bolt b1", "url": self.LINK}
        assert "sluice is green at def5678" in card["summary"] and "could not be opened" not in card["summary"]
        assert capsys.readouterr().err == (f"card land/b1: its reading could not be opened on the tailnet: {self.SLOW}; crew "
                                           "fetches switchboard-kit's main and tries once more\n")

    def test_both_starts_fail(self, monkeypatch, capsys):
        """card-sessions "Both starts fail": the card says so with the second start's reason and names crew card
        session."""
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW, self.ENDED])
        assert self.raised(monkeypatch, acts)[0] == "req_l2"
        card = self.sent(acts)
        assert "the bolt's conductor starts it with crew card session land/b1, and this card then carries its link." in card["summary"]
        assert card["context"]["background"].startswith(f"The reading could not be opened on the tailnet: {self.ENDED}\n\n")
        assert card["context"]["links"] == []
        assert capsys.readouterr().err.splitlines()[-1] == (
            f"card land/b1: its reading could not be opened on the tailnet: {self.ENDED}; crew card session land/b1 starts it")

    def test_a_fetch_that_fails_is_said_and_the_reading_is_tried_again(self, monkeypatch, capsys):
        why = "git fetch in /kit/main on mac-studio failed: fatal: unable to access GitHub"
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW])
        assert self.raised(monkeypatch, acts, fetched=why)[0] == "req_l2"
        assert len(acts.sessions) == 2 and self.sent(acts)["context"]["links"][0]["url"] == self.LINK
        assert f"card land/b1: {why}; the reading is tried again all the same" in capsys.readouterr().err

    def test_the_bolt_no_longer_reads_proven_at_the_second_try(self, monkeypatch):
        """card-sessions "The bolt no longer reads proven at the second try": nothing posted or changed."""
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW])
        card, reads, _ = self.raised(monkeypatch, acts, fresh=(None, "fix/b1/gap is in flight on it"))
        assert (card, reads) == (None, [False, True])
        assert acts.sessions == [("wldn", "land/b1")] and acts.calls == [] and acts.emitted == []

    # Why is kept in the run record, on the card's own entry (card-sessions "Why is kept in the run record").
    def test_a_post_whose_reading_could_not_open_records_why(self, monkeypatch):
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW, self.ENDED])
        self.raised(monkeypatch, acts)
        post, = acts.emitted
        assert (post["Act"], post["Card"], post["Key"], post["Unread"]) == ("card.post", "req_l2", "land/b1", self.ENDED)

    def test_a_change_whose_reading_could_not_open_records_why(self, monkeypatch):
        """A merge that moves the head changes the card the conductor holds, without its reading."""
        held = [{"Act": "card.post", "Key": "land/b1", "By": "swb-1-conductor", "Card": "req_l1", "On": ["bolt/b1"]}]
        acts = ReadingActs({"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)}, held, refused=self.ENDED)
        assert self.raised(monkeypatch, acts)[0] == "req_l1"
        change, = acts.emitted
        assert (change["Act"], change["Card"], change["Unread"]) == ("card.update", "req_l1", self.ENDED)

    def test_a_card_whose_reading_opened_records_no_reason(self, monkeypatch):
        """card-sessions "A card whose reading opened records no reason"."""
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW])
        self.raised(monkeypatch, acts)
        post, = acts.emitted
        assert post["Act"] == "card.post" and post.get("Unread") is None

    def test_the_run_record_takes_why_on_a_cards_entry_and_leaves_an_empty_one_out(self, monkeypatch, tmp_path):
        import record
        monkeypatch.setattr(record, "ROOT", tmp_path / "crew")
        monkeypatch.setattr(record, "_session", None)
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        record.emit("wldn", "card.post", ["bolt/b1"], by="swb-1-conductor", Card="req_l2", Key="land/b1", Unread=self.ENDED)
        record.emit("wldn", "card.post", ["bolt/b2"], by="swb-1-conductor", Card="req_l3", Key="land/b2", Unread=None)
        f, = (tmp_path / "crew" / "wldn" / "runs" / "mac-studio").glob("*.rec")
        assert " Unread " in f.read_text().split("%allowed:")[1].splitlines()[0] + " "
        unread, opened = record.parse(f.read_text())
        assert unread["Unread"] == self.ENDED and "Unread" not in opened

    def test_a_fresh_read_that_is_refused_raises_the_first_facts_with_the_first_reason(self, monkeypatch):
        """read.1: what the second read could not read is not guessed past."""
        acts = ReadingActs(dict(self.POSTED), refusals=[self.SLOW])
        assert self.raised(monkeypatch, acts, fresh="bolt b1's kit could not be read: ssh: timed out")[0] == "req_l2"
        assert acts.sessions == [("wldn", "land/b1")]
        card = self.sent(acts)
        assert "sluice is green at abc1234" in card["summary"]
        assert card["context"]["background"].startswith(f"The reading could not be opened on the tailnet: {self.SLOW}\n\n")


class TestSessionWords:
    def test_a_landings_session_runs_on_its_bolts_teams_host_and_a_batch_cards_on_the_main_levels(self):
        """card-sessions "A landing's session on another host": refused naming the team's host, the main level's
        being no matter."""
        assert plan.session_refusal("land/y", "wldn", "mac-studio", "mac-studio", "box") == (
            "land/y's reading session runs on box, the host of the team holding its bolt, where its landing card is raised: "
            "run crew card session land/y there")
        assert plan.session_refusal("land/y", "wldn", "mac-studio", "box", "box") is None
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

    def test_a_landings_reading_is_notes_on_its_card_and_its_approval_lands_nothing(self):
        """card-sessions "Annotated in a landing's session" and "Approved in a landing's session"."""
        notes = "# Annotations\n\n1. 03-y-diff.txt: this drops the retry\n"
        assert plan.land_waited("land/y", ("annotated", notes, 1), True) == (
            "land/y: notes from its reading, as notes on the landing card:\n# Annotations\n\n1. 03-y-diff.txt: this drops the retry")
        assert plan.land_waited("land/y", ("approved", None, 0), True) == (
            "land/y: approved in its reading, which lands nothing: the card's approval is the word to land")
        assert plan.land_waited("land/y", ("approved", "Looks right.", 0), True).endswith("the word to land\nLooks right.")
        assert plan.land_waited("land/y", ("dismissed", None, None), True) == "land/y: closed in plannotator with no decision"
        assert plan.land_waited("land/y", None, True) is None
        assert plan.land_waited("land/y", None, True, gone=True) == "land/y: the session ended with no decision"
        assert plan.land_waited("land/y", None, False) == "land/y: crew ended its session, as its card closed or crew card end was run"

    @pytest.mark.parametrize("recorded, held, refused, step, words", [
        (True, False, None, "wait", None),
        (False, True, None, "start", None),
        (False, True, "plannotator is not on this host's path, and a card's session is a plannotator session", "refuse",
         "land/y's reading could not be opened: plannotator is not on this host's path, and a card's session is a plannotator "
         "session; crew card session land/y starts it once that is mended"),
        (False, False, None, "refuse", "no session was started for card land/y, and no landing card of y is held on this host")])
    def test_a_wait_on_a_landing_with_no_session_starts_its_reading_while_its_card_is_held(self, recorded, held, refused, step, words):
        """card-sessions "A wait on a landing card starts its reading when none runs"."""
        assert plan.land_unstarted("land/y", recorded, held, refused) == (step, words)

    def test_a_decided_landing_reading_is_set_aside_and_forgotten_and_an_undecided_one_kept(self, tmp_path):
        s = {"pid": 42, "document": "/c/00-y.md", "url": "http://mac-studio.ts.swancloud.net:19432", "started": "2026-10-19T10:00:00Z"}
        (tmp_path / "session.json").write_text(json.dumps(s))
        (tmp_path / "result.json").write_text(json.dumps({"decision": "dismissed"}))
        plan.reading_decided(tmp_path, ("dismissed", None, None))
        assert sorted(p.name for p in tmp_path.iterdir()) == ["result.json", "session.json"]
        (tmp_path / "result.json").write_text(json.dumps({"decision": "annotated", "feedback": "x"}))
        plan.reading_decided(tmp_path, ("annotated", "x", 1))
        assert sorted(p.name for p in tmp_path.iterdir()) == [".lock", "result.20261019T100000Z.json"]
        assert plan.card_recorded(tmp_path) is None and plan.card_result(tmp_path) is None
        plan.reading_decided(tmp_path / "gone", ("approved", None, 0))

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

    def test_its_summary_says_what_a_yes_frees_when_its_team_holds_another_proven_bolt_and_nothing_otherwise(self):
        """A team may hold a bolt waiting to land beside the one it builds; once both are proven a yes frees it (teams.16)."""
        assert landing(frees={"team": "swc-1", "next": "d"})["card"]["summary"].endswith(
            "main has moved 1 landing since the bolt was cut. A yes frees swc-1 for d, which waits behind this landing.")
        assert landing(frees={"team": "swc-1", "next": None})["card"]["summary"].endswith(
            "since the bolt was cut. A yes frees swc-1, and nothing is planned for it.")
        assert landing(frees=None)["card"]["summary"].endswith("main has moved 1 landing since the bolt was cut.")

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

    def test_a_card_built_without_a_reading_carries_the_units_and_the_pull_request_and_no_session(self):
        c = landing()["card"]
        assert [(a["kind"], a.get("lang")) for a in c["artifacts"]] == [("code", "text"), ("url", None)]
        assert "plannotator" not in json.dumps(c) and "session" not in c

    READ = "http://mac-studio.ts.swancloud.net:19433"

    def test_a_card_built_with_its_reading_opens_its_details_with_it_and_leads_its_links_with_it(self):
        """rail-cards "A landing card links its reading": the link first in its details and among its links, before
        sluice's pull request, saying the reading lands nothing; the face, the summary and the approval as without."""
        bare, c = landing()["card"], landing(link=self.READ)["card"]
        assert c["context"]["background"] == (f"Read the bolt in one session: {self.READ}\n\nIt lands nothing: approving this "
                                              "card is the word to land.\n\n" + bare["context"]["background"])
        assert c["context"]["links"] == [{"label": "Read bolt a-deploy-holds-at-a-failure", "url": self.READ},
                                         {"label": "Pull request #23 on GitHub, opened by sluice", "url": "https://github.com/agentplot/crew/pull/23"}]
        assert c["artifacts"][0] == bare["artifacts"][0]
        assert c["artifacts"][1:] == [{"kind": "url", "title": "Read bolt a-deploy-holds-at-a-failure", "ref": self.READ},
                                      bare["artifacts"][1]]
        assert {k: c[k] for k in ("title", "summary", "approve", "rationale", "kind")} == {
            k: bare[k] for k in ("title", "summary", "approve", "rationale", "kind")}

    def test_a_card_with_its_reading_and_no_pull_request_links_the_reading_alone(self):
        c = built.landing_card(dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 3}, head="abc1234",
                                    at=None, moved=0, pr=None, link=self.READ))["card"]
        assert c["context"]["links"] == [{"label": "Read bolt b1", "url": self.READ}]
        assert [a["kind"] for a in c["artifacts"]] == ["code", "url"]

    WEB, API = "http://web-4581216--bolt-y--crew.localhost:4321", "http://api-4581216--bolt-y--crew.localhost:4322"
    PREVIEW = dict(head="4581216abcdef", name="preview/0123456789ab", state="starting", addresses={"web": WEB, "api": API})
    PR = {"kind": "url", "title": "Pull request #23 on GitHub, opened by sluice", "ref": "https://github.com/agentplot/crew/pull/23"}

    def same_but_details(self, c, bare):
        assert {k: c[k] for k in ("title", "summary", "approve", "rationale", "kind")} == {
            k: bare[k] for k in ("title", "summary", "approve", "rationale", "kind")}

    def test_a_preview_coming_up_is_listed_after_the_reading_and_lands_nothing(self):
        """rail-cards "A kit that declares a preview": each address under the name the kit gives it, after the
        reading's link and its sentence, in the links and on the face after the reading's and before the pull
        request, saying the preview is coming up and lands nothing; the rest of the card as without."""
        bare, c = landing(link=self.READ)["card"], landing(link=self.READ, preview=self.PREVIEW)["card"]
        reading = (f"Read the bolt in one session: {self.READ}\n\nIt lands nothing: approving this card is the word to land.\n\n")
        assert c["context"]["background"] == (
            reading + "Try it running: a preview of 4581216 sluice brings up, at these addresses once it is up. It lands "
            f"nothing; approving this card is the word to land.\nweb: {self.WEB}\napi: {self.API}\n\n"
            + bare["context"]["background"].removeprefix(reading))
        assert c["context"]["links"] == [{"label": "Read bolt a-deploy-holds-at-a-failure", "url": self.READ},
                                         {"label": "Preview: web", "url": self.WEB}, {"label": "Preview: api", "url": self.API},
                                         {"label": self.PR["title"], "url": self.PR["ref"]}]
        assert c["artifacts"] == [bare["artifacts"][0], bare["artifacts"][1], {"kind": "url", "title": "Preview: web", "ref": self.WEB},
                                  {"kind": "url", "title": "Preview: api", "ref": self.API}, self.PR]
        self.same_but_details(c, bare)

    def test_a_preview_up_is_listed_as_up(self):
        c = landing(link=self.READ, preview=dict(self.PREVIEW, state="up"))["card"]
        assert ("Try it running: a preview of 4581216, up at these addresses. It lands nothing; approving this card is the "
                f"word to land.\nweb: {self.WEB}\napi: {self.API}\n\n") in c["context"]["background"]
        assert [a["title"] for a in c["artifacts"][2:4]] == ["Preview: web", "Preview: api"]

    def test_a_preview_that_failed_says_so_with_the_end_of_its_output_and_lists_no_address(self):
        """rail-cards "The stack fails to come up"."""
        output = "".join(f"step {i}: building the stack's images, which takes its time\n" for i in range(8)) + "error: port 4321 in use\n"
        bare = landing(link=self.READ)["card"]
        c = landing(link=self.READ, preview=dict(self.PREVIEW, state="failed", output=output))["card"]
        said = c["context"]["background"].split("\n\n")[2]
        assert said == ("A preview of 4581216 was asked for and is not there: step 6: building the stack's images, which takes "
                        "its time / step 7: building the stack's images, which takes its time / error: port 4321 in use. Nothing "
                        "waits on it.")
        assert "Preview:" not in json.dumps(c) and c["artifacts"] == bare["artifacts"]
        self.same_but_details(c, bare)

    def test_a_preview_not_asked_says_why_and_the_card_is_raised_all_the_same(self):
        """rail-cards "The host's sluice has no preview command"."""
        why = "sluice exited 2: unrecognized subcommand 'preview'"
        bare, c = landing()["card"], landing(preview={"head": "4581216abcdef", "why": why})["card"]
        assert c["context"]["background"] == (f"A preview of 4581216 was asked for and is not there: {why}. Nothing waits on it.\n\n"
                                              + bare["context"]["background"])
        assert c["artifacts"] == bare["artifacts"] and c["context"]["links"] == bare["context"]["links"]
        self.same_but_details(c, bare)

    def test_a_preview_of_nine_addresses_keeps_the_cards_face_at_eight_artifacts(self):
        many = {f"site{i}": f"http://site{i}-4581216.localhost:{4320 + i}" for i in range(9)}
        c = landing(link=self.READ, preview=dict(self.PREVIEW, addresses=many))["card"]
        assert len(c["artifacts"]) == 8
        assert [a["title"] for a in c["artifacts"]] == (["What lands: 6 units, no chores", "Read bolt a-deploy-holds-at-a-failure"]
                                                        + [f"Preview: site{i}" for i in range(5)] + [self.PR["title"]])
        assert [l["label"] for l in c["context"]["links"]][1:10] == [f"Preview: site{i}" for i in range(9)]
        assert all(f"site{i}: {u}" in c["context"]["background"] for i, u in enumerate(many.values()))

    def test_a_card_built_with_no_preview_is_as_before(self):
        """rail-cards "A kit that declares none": no preview and no word of one."""
        c = landing(link=self.READ, preview=None)["card"]
        assert c == landing(link=self.READ)["card"] and "preview" not in json.dumps(c).lower()


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

    def test_a_head_a_landing_card_put_on_main_follows_no_card_and_its_details_name_the_landing(self):
        """rail-cards "A head a landing card put on main": the landing card is its conductor's, which Pending You
        takes no follows to from main-level ops, so the deploy's card follows nothing and names the landing."""
        entries = [dict(Act="card.post", Key="land/b24", By="swb-1-conductor", Card="req_land24"),
                   dict(Act="bolt.land", On=["bolt/b24"], Head="c882cff0123"),
                   dict(Act="card.close", Card="req_land24", State="closed")]
        follows = built.follows_of("deploy", {"env": "srv", "head": "c882cff"}, entries, "swancloud-ops")
        c = deploy(follows=follows, landings=[{"pr": 24, "subject": "The deployer holds at a failure"}])["card"]
        assert follows is None and "follows" not in c and "#24 The deployer holds at a failure" in c["context"]["background"]

    def test_a_kit_that_hands_no_notes_is_said_to_and_landings_crew_cant_read_are_said_not_counted(self):
        assert deploy(notes=None, steps=[])["card"]["summary"] == (
            "3 landings since srv's last deploy (6aed25c). The kit handed no release notes. box (auto) follows on its own; "
            "mac-studio is offered after srv.")
        c = deploy(notes=None, steps=[], landings=[], landings_why="c882cff is no landing's commit in the record")["card"]
        assert c["summary"].startswith("Which landings it carries since srv's last deploy (6aed25c) can't be read: c882cff is no landing's")
        assert [(a["title"], a["lines"][0]) for a in c["artifacts"]] == [("What's in it", "c882cff is no landing's commit in the")]


class TestFollows:
    """What a card follows (rail-cards "A card follows only a card in its owner's name"): only a card the run record
    shows posted in the poster's own name, since Pending You takes follows to no other."""
    OPS, CONDUCTOR = "swancloud-ops", "swb-1-conductor"
    E = [dict(Act="card.post", Key="land/b24/abc1234", By=CONDUCTOR, Card="req_old"), dict(Act="card.close", Card="req_old"),
         dict(Act="card.post", Key="land/b24", By=CONDUCTOR, Card="req_land"), dict(Act="bolt.land", On=["bolt/b24"], Head="c882cff"),
         dict(Act="card.close", Card="req_land", State="closed"),
         dict(Act="card.post", Key="deploy/srv", By=OPS, Card="req_d1")]

    def test_a_deploy_of_a_newer_head_after_a_no_follows_the_declined_card(self):
        declined = self.E + [dict(Act="card.close", Card="req_d1", State="declined")]
        assert built.follows_of("deploy", {"env": "srv", "head": "9ab12cd"}, declined, self.OPS) == "req_d1"
        assert built.follows_of("deploy", {"env": "srv", "head": "9ab12cd"}, self.E, self.OPS) is None

    def test_a_deploy_after_one_that_ran_follows_nothing_and_none_follows_a_landing_card(self):
        """rail-cards "A deploy after one that ran" and "A deploy of the head a landing left"."""
        ran = self.E + [dict(Act="card.close", Card="req_d1", State="closed")]
        assert built.follows_of("deploy", {"env": "srv", "head": "9ab12cd"}, ran, self.OPS) is None
        assert built.follows_of("deploy", {"env": "srv", "head": "c882cff"}, ran, self.OPS) is None
        assert built.follows_of("deploy", {"env": "srv", "head": "c882cff"}, ran, self.CONDUCTOR) is None

    def test_a_step_follows_the_deploys_card_and_each_later_step_the_one_before(self):
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/1"}, self.E, self.OPS) == "req_d1"
        more = self.E + [dict(Act="card.post", Key="op/srv/1", By=self.OPS, Card="req_s1"), dict(Act="card.close", Card="req_s1")]
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/2"}, more, self.OPS) == "req_s1"

    def test_a_step_whose_deploy_card_is_another_owners_follows_nothing(self):
        """A deploy card a person posted under deploy/srv: the step's card, main-level ops's, follows none of it."""
        theirs = [dict(e, By="chuck") if e.get("Key") == "deploy/srv" else e for e in self.E]
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/1"}, theirs, self.OPS) is None
        more = theirs + [dict(Act="card.post", Key="op/srv/1", By="chuck", Card="req_s1"), dict(Act="card.close", Card="req_s1")]
        assert built.follows_of("step", {"env": "srv", "key": "op/srv/2"}, more, self.OPS) is None

    def test_a_landing_raised_again_follows_the_card_its_defect_note_held_and_an_open_one_is_changed_not_followed(self):
        held = [dict(Act="card.post", Key="land/b7", By=self.CONDUCTOR, Card="req_l1"),
                dict(Act="card.close", Card="req_l1", State="withdrawn")]
        assert built.follows_of("land", {"bolt": "b7"}, held, self.CONDUCTOR) == "req_l1"
        assert built.follows_of("land", {"bolt": "b7"}, held[:1], self.CONDUCTOR) is None

    def test_a_landing_raised_again_on_a_team_that_did_not_post_the_last_one_follows_nothing(self):
        """rail-cards "A landing raised again on a team that did not post the last one": b7 now held by swb-2."""
        held = [dict(Act="card.post", Key="land/b7", By=self.CONDUCTOR, Card="req_l1"),
                dict(Act="card.close", Card="req_l1", State="withdrawn")]
        assert built.follows_of("land", {"bolt": "b7"}, held, "swb-2-conductor") is None

    def test_a_lost_card_is_followed_by_none_and_a_proposal_a_batch_and_a_record_follow_nothing(self):
        lost = [dict(Act="card.post", Key="land/b7", By=self.CONDUCTOR, Card="req_l1"),
                dict(Act="card.close", Card="req_l1", State="lost")]
        assert built.follows_of("land", {"bolt": "b7"}, lost, self.CONDUCTOR) is None
        assert [built.follows_of(k, {}, self.E, self.OPS) for k in ("proposal", "batch", "record")] == [None, None, None]

    D1 = dict(Act="card.post", Key="deploy/srv", By="swancloud-ops", Card="req_d1")

    @pytest.mark.parametrize("entries, key", [
        ([D1], "deploy/srv"),
        ([D1, dict(Act="card.close", Card="req_d1", Key="deploy/srv", State="closed")], None),
        ([D1, dict(Act="card.close", Card="req_d1")], None),
        ([dict(D1, By="swb-1-conductor")], None),
        ([D1, dict(Act="card.close", Card="req_d1", Refused="Pending You refused the close: This request is already closed.")], "deploy/srv"),
        ([dict(D1, Card=None, Refused="Pending You refused post_request: x")], None),
        ([dict(Act="card.post", Key="land/b1", By="swancloud-ops", Card="req_l1")], None)])
    def test_the_key_a_followed_card_is_still_open_under_is_read_from_the_record_alone(self, entries, key):
        assert built.followed_open(entries, "req_d1", "swancloud-ops") == key


class TestStranded:
    """rail-cards, "A batch's card the main level's host can't reach is raised again there": which of the planner's
    cards under a batch's key the main level's host, deneb, can't reach (cards.stranded), from the run record alone."""
    POST = dict(Act="card.post", Key="batch/13", By="swancloud-planner", Card="req_b13", Host="mac-studio")

    def lost(self, host="mac-studio"):
        return dict(Act="card.close", Key="batch/13", By="swancloud-planner", Card="req_b13", State="lost", Host=host)

    @pytest.mark.parametrize("entries, card", [
        ([POST], "req_b13"),
        ([dict(POST, Host="deneb")], None),
        ([POST, dict(Act="card.close", Card="req_b13", State="closed")], None),
        ([POST, dict(Act="card.close", Card="req_b13", State="withdrawn", Host="mac-studio")], None),
        ([POST, dict(Act="card.close", Card="req_b13", State="lost", Host="mac-studio")], "req_b13"),
        ([dict(POST, Host="deneb"), dict(Act="card.close", Card="req_b13", State="lost", Host="deneb")], "req_b13"),
        ([POST, dict(Act="card.close", Card="req_b13", State="lost"), dict(POST, Card="req_b14", Host="deneb")], None),
        ([POST, dict(Act="card.close", Card="req_b13", State="closed", Refused="Pending You refused the close: x")], "req_b13"),
        ([dict(POST, Host="deneb"), dict(POST, Card=None, Refused="Pending You refused post_request: x")], None),
        ([dict(POST, By="swancloud-design")], None),
        ([dict(POST, Key="batch/12")], None),
        ([dict(POST, Host=None)], None),
        ([], None)])
    def test_the_owners_newest_card_held_on_another_host_or_lost_is_the_one_this_host_cant_reach(self, entries, card):
        assert built.stranded(entries, "batch/13", "swancloud-planner", "deneb") == card



class TestTheRefusedDeployCards:
    """The run record of 2026-10-19 23:54Z to 2026-10-20 00:16Z on swancloud/main (runs/mac-studio/2026-10-19.rec and
    2026-10-20.rec, signal 2026-10-20-swancloud-planner-c422e742/01): swc-2-conductor's landing card for
    the-box-works-in-wldn-prod, the landing leaving swancloud's main at ddcf2cb, and the deployer's offers of ddcf2cb to
    five environments, whose every card swancloud-ops posted followed that landing card and was refused as another
    agent's. Each now follows no card; and a post Pending You refuses is recorded refused in its words."""
    OPS, HEAD = "swancloud-ops", "ddcf2cb4e5ad15281a11fe1e636d17dfed9c66b9"
    LANDING = "req_5de89eb68b7c495fbb36"
    ENVS = ("deneb", "mac-studio", "macbook-pro", "chuck-herdr-alpha", "swancloud-srv")
    WORDS = "This is swc-2-conductor’s card; leave it. You’re “swancloud-ops”: act only on the cards you posted."
    WHERE = ("/kit/main", "github.com/agentplot/swancloud")
    ENTRIES = ([dict(Act="card.post", At="2026-10-19T18:02:11Z", On=["env/deneb"], By=OPS, Key="deploy/deneb", Card="req_deneb1"),
                dict(Act="card.close", At="2026-10-19T18:40:03Z", On=["env/deneb"], By=OPS, Key="deploy/deneb", Card="req_deneb1",
                     State="closed"),
                dict(Act="card.post", At="2026-10-19T21:50:41Z", On=["bolt/the-box-works-in-wldn-prod"], By="swc-2-conductor",
                     Key="land/the-box-works-in-wldn-prod", Card=LANDING),
                dict(Act="bolt.land", At="2026-10-19T23:36:27Z", On=["bolt/the-box-works-in-wldn-prod"], By="swancloud-ops",
                     Head=HEAD, Repo="swancloud")]
               + [dict(Act="ops.offer", At=f"2026-10-19T23:5{4 + i}:39Z", On=[f"env/{env}"], By="swancloud-deployer", Head=head,
                       Base="d46500a" + "0" * 33) for i, env, head in zip(range(5), ENVS, [HEAD] * 5)]
               + [dict(Act="card.close", At="2026-10-19T23:57:19Z", On=["bolt/the-box-works-in-wldn-prod"], By="swc-2-conductor",
                       Key="land/the-box-works-in-wldn-prod", Card=LANDING, State="closed")])

    def facts(self, follows):
        return dict(env="deneb", head=self.HEAD, base="d46500a" + "0" * 33,
                    landings=[{"pr": None, "subject": "the-box-works-in-wldn-prod"}], notes=None, steps=[], before=[], after=[],
                    follows=follows)

    def test_none_of_the_five_environments_deploy_cards_follows_the_conductors_landing_card(self):
        """rail-cards "Five environments offered that head"."""
        assert [built.follows_of("deploy", {"env": env, "head": self.HEAD}, self.ENTRIES, self.OPS) for env in self.ENVS] == [None] * 5

    def test_a_post_pending_you_refuses_is_recorded_refused_in_its_words_and_refuses_nothing_else(self, capsys):
        """rail-cards "Pending You refuses a deploy card"."""
        from test_card_commands import Acts, MATCHED
        acts = Acts({"match_area": (MATCHED, None), "post_request": (None, self.WORDS)}, entries=self.ENTRIES, caller=self.OPS)
        follows = built.follows_of("deploy", {"env": "deneb", "head": self.HEAD}, self.ENTRIES, self.OPS)
        assert plan.row_card_post(None, "swancloud", self.OPS, built.deploy_card, self.facts(follows), self.WHERE, acts) is None
        assert acts.emitted == [{"Act": "card.post", "On": ["env/deneb"], "label": "swancloud", "by": self.OPS, "Key": "deploy/deneb",
                                 "refused": f"Pending You refused post_request: {self.WORDS}"}]
        assert f"card deploy/deneb not posted: Pending You refused post_request: {self.WORDS}" in capsys.readouterr().err

    def test_the_post_sends_no_follows_and_its_face_names_the_landing(self):
        """rail-cards "A deploy of the head a landing left"."""
        from test_card_commands import Acts, MATCHED, POSTED
        acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_deneb2"), None)},
                    entries=self.ENTRIES, caller=self.OPS)
        follows = built.follows_of("deploy", {"env": "deneb", "head": self.HEAD}, self.ENTRIES, self.OPS)
        assert plan.row_card_post(None, "swancloud", self.OPS, built.deploy_card, self.facts(follows), self.WHERE, acts) == "req_deneb2"
        sent = next(a for t, a in acts.calls if t == "post_request")
        assert sent["idempotencyKey"] == "deploy/deneb:2" and "follows" not in sent
        assert sent["artifacts"][0]["lines"] == ["the-box-works-in-wldn-prod"]
        assert [(e["Act"], e["Card"], e["Key"], e["by"]) for e in acts.emitted] == [("card.post", "req_deneb2", "deploy/deneb", self.OPS)]


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

    RUN = "https://github.com/WilldanGroup/switchboard-kit/actions/runs/38612817613"

    def gate(self, **f):
        """swb-4's break-glass stand at dev's gate, 2026-10-14, as ops.step_facts gives it (plan.14)."""
        return built.step_card(dict(dict(env="dev", n=1, text=self.RUN, doer="user", held=False, commands=[], gate=self.RUN,
                                         to="4f2a9c1" + "0" * 33, follows="req_d1"), **f))

    def test_a_deploy_waiting_at_its_gate_is_the_users_do_to_approve_it_there_its_one_step_and_where_the_gates_link(self):
        b = self.gate()
        c = b["card"]
        assert b["key"] == "op/dev/1" and (c["kind"], c["intent"], c["urgency"], c["follows"]) == ("action", "do", "today", "req_d1")
        assert c["title"] == "Approve the deploy of 4f2a9c1 to dev at its gate"
        assert c["summary"] == ("The deploy of 4f2a9c1 to dev waits at its gate for your approval there. Approving it at the gate is "
                                "the word to deploy; nothing else asks for it.")
        assert c["action"] == {"steps": [{"text": self.RUN}], "where": self.RUN, "done": "The run goes on past its gate."}
        assert c["context"]["links"] == [{"label": "The gate", "url": self.RUN}] and "approve" not in c

    def test_a_gate_whose_step_names_no_commit_and_one_with_a_why(self):
        c = self.gate(to=None)["card"]
        assert c["title"] == "Approve the deploy to dev at its gate"
        assert c["summary"].startswith("The deploy to dev waits at its gate for your approval there.")
        c = self.gate(why="The break-glass stand, while the tenant is down.")["card"]
        assert c["summary"].endswith("nothing else asks for it. The break-glass stand, while the tenant is down.")

    def test_a_users_step_with_no_gate_keeps_its_card(self):
        c = built.step_card(dict(env="srv", n=1, text="Open https://example.com and rotate the key", doer="user", held=False,
                                 gate=None, to="4f2a9c1" + "0" * 33))["card"]
        assert c["title"] == "After srv's deploy: Open https://example.com and rotate the key"
        assert c["action"] == {"steps": [{"text": "Open https://example.com and rotate the key"}]}

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


def heard(asserted_by="user", grade="verified", uuid="u-32", reason=None):
    """A verdict on the user's yes in the design agent's transcript, as transcript.check gives it."""
    if grade == "unverified":
        return transcript.unverified(reason)
    return transcript.Verdict(grade, raw=b'{"type": "user"}', n=4, value={"uuid": uuid} if uuid else {},
                              asserted_by=asserted_by if grade == "verified" else "unknown")


SETTLED = "crew records record 0032 in switchboard-kit as settled in no pane"
TO_CARD = "run crew record switchboard-kit 32 --proposed without --settled-in-pane, and the user answers on its card"


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
        ("atlas-kit", 21, "proposed", {"settled_in_pane": True, "alternatives": "a.md"}, "a record settled in the pane raises no card"),
        ("atlas-kit", 21, "proposed", {"settled_in_pane": True}, "--settled-in-pane needs --excerpt"),
        ("atlas-kit", 21, "proposed", {"settled_in_pane": True, "excerpt": " "}, "--settled-in-pane needs --excerpt"),
        ("atlas-kit", 21, "proposed", {"excerpt": "Yes, accept 21"}, "--excerpt goes with --settled-in-pane")])
    def test_a_kit_not_the_partitions_or_flags_that_do_not_go_together_are_refused_on_the_teams_file_alone(self, kit, n, status, more, said):
        a = argparse.Namespace(**dict(dict(kit=kit, number=n, status=status, settled_in_pane=False, excerpt=None, alternatives=None,
                                           label="wldn"), **more))
        with pytest.raises(crew.Refusal, match=re.escape(said)):
            plan.record_status(FLEET, a)

    def test_the_users_yes_in_the_callers_own_pane_settles_the_record(self):
        assert plan.settled_refusal(32, "switchboard-kit", heard()) is None
        assert plan.settled_refusal(32, "switchboard-kit", heard(uuid=None)) is None

    @pytest.mark.parametrize("caller", ["wldn-design", "wldn-planner", "wldn-operator", "swb-1-conductor", "madswan-design", "chuck@mac-studio"])
    def test_no_caller_is_refused_by_who_it_is_the_users_yes_read_in_its_own_transcript(self, monkeypatch, caller):
        """roles.2: crew records who ran it and in which session, and refuses no caller; the words are still read."""
        asked = []
        monkeypatch.setattr(crew, "this_host", lambda: FLEET["partitions"]["wldn"]["machine"])
        monkeypatch.setenv("CREW_AGENT", caller)
        monkeypatch.setattr(plan.CardActs, "heard", lambda self, words: asked.append(words) or (heard(), "s-9"))
        a = argparse.Namespace(kit="switchboard-kit", number=32, status="proposed", settled_in_pane=True, excerpt="Yes, accept 32",
                               alternatives=None, label="wldn")
        with pytest.raises(crew.Refusal, match="no session of .* keeps WilldanGroup/switchboard-kit"):
            plan.record_status(FLEET, a)
        assert asked == ["Yes, accept 32"]

    @pytest.mark.parametrize("v, words", [
        (heard(grade="refused"), "the words are not in a record your session received; only the user's own words settle a "
                                 "record, quoted as they wrote them in your pane, never your own"),
        (heard("agent:swancloud-planner"), "the words are swancloud-planner's, passed on with crew tell, and not the user's; "
                                           "tell swancloud-planner that the user settles a record in your pane or on its card"),
        (heard("crew"), "the words are crew's own message, not the user's"),
        (heard("tool"), "the words are a tool's output, not the user's"),
        (heard(grade="found"), "the words are in a record of your transcript crew can't read as anyone's, so it can't tell they are the user's"),
        (heard(grade="unverified", reason="session s-9 is on deneb, not mac-studio"),
         "crew can't read your session's transcript, so it can't tell the words are the user's: session s-9 is on deneb, not mac-studio")])
    def test_words_crew_does_not_read_as_the_users_are_refused_naming_who_said_them_and_sent_to_the_card(self, v, words):
        assert plan.settled_refusal(32, "switchboard-kit", v) == f"{SETTLED}: {words}; {TO_CARD}"

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

    def test_the_sweeps_raise_of_a_record_posts_it_again_from_its_record_saying_an_older_copy_was_lost(self, monkeypatch):
        """rail-cards, "A record's card left on the host the main level left": the record read with status proposed on
        the kit's main, as crew record reads it, and its card posted in the design agent's name; one raised with
        alternatives refused naming the command that raises it again, nothing read or posted."""
        from test_card_commands import Acts, MATCHED, POSTED
        where, reads = ("/kit/main", "github.com/WilldanGroup/switchboard-kit"), []

        def read(fleet, label, kit, number, status, alternatives=None):
            reads.append((label, kit, number, status, alternatives))
            return recorded(MADR, status), where, "abc1234" + "0" * 33, "switchboard runs GitHub's workflows itself"
        monkeypatch.setattr(plan, "record_read", read)
        row = dict(label="wldn", key="record/switchboard-kit/0032", group="records", alternatives=False, dead="req_c0")
        acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)}, caller="wldn-design")
        assert plan.raise_record_again(None, row, acts) == "req_c1"
        assert reads == [("wldn", "switchboard-kit", 32, "proposed", None)]
        sent = next(a for t, a in acts.calls if t == "post_request")
        assert (acts.names, sent["idempotencyKey"]) == (["wldn-design"], "record/switchboard-kit/0032")
        assert sent["summary"] == f"{built.DEAD}\n\n" + built.record_card(recorded(MADR, "proposed"))["card"]["summary"]
        acts = Acts({}, caller="wldn-design")
        with pytest.raises(crew.Refusal) as e:
            plan.raise_record_again(None, dict(row, alternatives=True), acts)
        assert str(e.value) == ("crew keeps no copy of record 0032's alternatives, so wldn-design raises it again with "
                                "crew record switchboard-kit 32 --proposed --alternatives <file>")
        assert (acts.calls, len(reads)) == ([], 1)

    def test_a_card_pending_you_ended_already_is_recorded_closed_and_followed_never_changed_or_closed_again(self, capsys):
        from test_card_commands import Acts, MATCHED, POSTED
        where, f = ("/kit/main", "github.com/WilldanGroup/switchboard-kit"), recorded(MADR, "proposed")
        held = [dict(Act="card.post", Key="record/switchboard-kit/0032", By="wldn-design", Card="req_c1")]
        for status, state, follows in (("resolved", "closed", "req_c1"), ("closed", "closed", "req_c1"), ("cancelled", "withdrawn", None),
                                       ("expired", "withdrawn", None)):
            acts = Acts({"get_request": ({"status": status, "version": 4}, None), "match_area": (MATCHED, None),
                         "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=held, caller="wldn-design")
            assert plan.raise_record(None, "wldn", f, where, "Revised at 9ab0123: ops.7 loosened", acts) == "req_c2"
            assert [c[0] for c in acts.calls] == ["get_request", "match_area", "post_request"]
            assert (acts.emitted[0]["Act"], acts.emitted[0]["State"], acts.emitted[0]["Outcome"]) == ("card.close", state, plan.ENDED_ELSEWHERE)
            assert acts.calls[2][1]["idempotencyKey"] == "record/switchboard-kit/0032:2"
            assert acts.calls[2][1].get("follows") == follows
        for status in ("resolved", "closed"):
            acts = Acts({"get_request": ({"status": status, "version": 4}, None)}, entries=held, caller="wldn-design")
            assert plan.row_card_close(None, "wldn", "wldn-design", "record/switchboard-kit/0032", outcome="Accepted", acts=acts) == "req_c1"
            assert [c[0] for c in acts.calls] == ["get_request"]
            assert (acts.emitted[0]["State"], acts.emitted[0]["Outcome"]) == ("closed", plan.ENDED_ELSEWHERE)

    def test_a_record_accepted_or_rejected_closes_its_card_under_either_key_form(self, capsys):
        """swancloud's record 0029, rejected on 2026-10-22 by crew record, whose card the design agent had posted
        before record 0031 under record/swancloud/0029/5eba218 stayed open: crew record closes each card its design
        agent holds open under the record's key or the key with the commit after it, and none of another record's."""
        from test_card_commands import Acts
        held = [dict(Act="card.post", Key="record/switchboard-kit/0032/5eba218", By="wldn-design", Card="req_c0"),
                dict(Act="card.post", Key="record/switchboard-kit/0031/abc1234", By="wldn-design", Card="req_c9"),
                dict(Act="card.post", Key="record/switchboard-kit/0032/def5678", By="wldn-design", Card="req_c8"),
                dict(Act="card.close", Key="record/switchboard-kit/0032/def5678", By="wldn-design", Card="req_c8"),
                dict(Act="card.post", Key="record/switchboard-kit/0032", By="wldn-design", Card="req_c1")]
        acts = Acts({"get_request": ({"status": "pending", "version": 2}, None)}, entries=held, caller="wldn-design")
        assert plan.record_card_close(None, "wldn", "wldn-design", "record/switchboard-kit/0032", "Rejected at 447980b", acts) == ["req_c0", "req_c1"]
        assert [(e["Act"], e["On"], e["Card"], e["Key"], e["State"], e["Outcome"]) for e in acts.emitted] == [
            ("card.close", ["record/switchboard-kit/0032"], "req_c0", "record/switchboard-kit/0032/5eba218", "withdrawn", "Rejected at 447980b"),
            ("card.close", ["record/switchboard-kit/0032"], "req_c1", "record/switchboard-kit/0032", "withdrawn", "Rejected at 447980b")]
        acts = Acts(entries=held[1:4], caller="wldn-design")
        assert plan.record_card_close(None, "wldn", "wldn-design", "record/switchboard-kit/0032", "Accepted at 447980b", acts) == []
        assert (acts.calls, capsys.readouterr().out.splitlines()[-1]) == (
            [], "card record/switchboard-kit/0032: wldn-design holds none open on this host, so none is closed")


class TestPickedUp:
    """mac-studio's run record of 2026-10-19 (signal 2026-10-19-swancloud-ops-5b7775dd/01): the user approved
    deploy/mac-studio's card, its deploy recorded a step that is the user's, and crew posted op/mac-studio/1's card
    following the deploy's card, which Pending You then resolved. The deploy's end was refused "This request is already
    closed.", and the offer of d35fbf2 went to the resolved card as a change, refused "This was already answered"."""
    OWNER, WHERE = "swancloud-ops", ("/kit/main", "github.com/agentplot/swancloud")
    STEP = dict(env="mac-studio", n=1, text="restart crew's teams on mac-studio", doer="user", held=False, gate=None, follows="req_d1")
    OFFER = dict(env="mac-studio", head="d35fbf2" + "0" * 33, base="97e54d5" + "0" * 33,
                 landings=[{"pr": 48, "subject": "A deploy card resolved under its step card reads closed"}],
                 notes=None, steps=[], before=[{"env": "deneb", "policy": "manual"}], after=[])

    def held(self, entries, acts):
        """The run record after an act: what it held, and each entry the act emitted, as record.emit writes it."""
        return entries + [dict({k: v for k, v in e.items() if k not in ("by", "label", "refused")}, By=e["by"],
                               **({"Refused": e["refused"]} if "refused" in e else {})) for e in acts.emitted]

    def test_a_deploy_card_picked_up_by_its_steps_card_then_the_deploys_end_and_the_next_offer_to_that_environment(self):
        from test_card_commands import Acts, MATCHED, POSTED
        entries = [dict(Act="card.post", Key="land/b48", By="crw-2-conductor", Card="req_l48"),
                   dict(Act="bolt.land", On=["bolt/b48"], Head=self.OFFER["head"]),
                   dict(Act="card.close", Card="req_l48", Key="land/b48", By="crw-2-conductor", State="closed"),
                   dict(Act="card.post", Key="deploy/mac-studio", By=self.OWNER, Card="req_d1")]
        acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_s1"), None),
                     "get_request": ({"status": "resolved", "version": 5}, None)}, entries=entries, caller=self.OWNER)
        assert plan.row_card_change(None, "swancloud", self.OWNER, built.step_card, self.STEP, "x", self.WHERE, acts) == "req_s1"
        assert acts.calls[2] == ("get_request", {"requestId": "req_d1", "name": self.OWNER})
        assert [(e["Act"], e["Card"], e["Key"], e.get("State"), e.get("Outcome")) for e in acts.emitted] == [
            ("card.post", "req_s1", "op/mac-studio/1", None, None), ("card.close", "req_d1", "deploy/mac-studio", "closed", plan.FOLLOWED)]
        entries = self.held(entries, acts)
        assert built.card_under(entries, "deploy/mac-studio", self.OWNER) is None

        acts = Acts({"get_request": ({"status": "resolved", "version": 5}, None),
                     "cancel_request": (None, "This request is already closed.")}, entries=entries, caller=self.OWNER)
        assert plan.row_card_close(None, "swancloud", self.OWNER, "deploy/mac-studio",
                                   outcome="Deployed 97e54d5 to mac-studio: machine ok, suite ok.", acts=acts) is None
        assert acts.calls == [] and acts.emitted == []

        follows = built.follows_of("deploy", {"env": "mac-studio", "head": self.OFFER["head"]}, entries, self.OWNER)
        assert follows is None
        acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_d2"), None),
                     "update_request": (None, "This was already answered; follow up with reply_in_thread.")},
                    entries=entries, caller=self.OWNER)
        assert plan.row_card_change(None, "swancloud", self.OWNER, built.deploy_card, dict(self.OFFER, follows=follows),
                                    "Now d35fbf2", self.WHERE, acts) == "req_d2"
        assert [t for t, _ in acts.calls] == ["match_area", "post_request"]
        assert acts.calls[1][1]["idempotencyKey"] == "deploy/mac-studio:2" and "follows" not in acts.calls[1][1]
        entries = self.held(entries, acts)
        assert built.card_under(entries, "deploy/mac-studio", self.OWNER) == "req_d2"


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
                       built.step_card(dict(env="srv", n=2, text="do it", doer="ops", held=True))["card"],
                       TestStep().gate(why="A why. " * 60)["card"]]
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
                                          ("record/crew/0029/e6fa15f", "record/crew/0029"), ("record/crew/0029/x", None),
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

    def test_a_close_given_an_outcome_and_a_reason_acks_an_answered_card_with_the_outcome_and_withdraws_a_waiting_one_with_the_reason(self):
        both = dict(outcome="Dropped on your note", reason="Why now?")
        assert built.close_call({"status": "answered", "version": 3}, "req_a", "wldn-planner", **both)[1]["outcome"] == "Dropped on your note"
        assert built.close_call({"status": "pending", "version": 1}, "req_a", "wldn-planner", **both)[1]["reason"] == "Why now?"
        assert [built.close_words({"status": s}, **both) for s in ("answered", "pending")] == ["Dropped on your note", "Why now?"]

    @pytest.mark.parametrize("got, state", [
        ({"status": "resolved"}, "closed"), ({"status": "cancelled"}, "withdrawn"), ({"status": "expired"}, "withdrawn"),
        ({"status": "pending"}, None), ({"status": "snoozed"}, None), ({"status": "delegated"}, None),
        ({"status": "answered"}, None), ({"status": "closed"}, "closed"), ({}, None), (None, None), ("resolved", None)])
    def test_a_card_pending_you_resolved_reads_closed_and_one_it_cancelled_or_expired_withdrawn(self, got, state):
        """Pending You 0.35.1 ends a card as resolved, cancelled or expired, and gives no `closed` (its wake mod's
        CLOSED), which reads closed all the same: mac-studio's deploy card of 2026-10-19 was resolved by its step's
        card, which followed it."""
        assert built.ended(got) == state

    def test_a_change_carries_only_what_update_request_takes_and_a_card_posted_again_says_its_older_copy_is_dead(self):
        c = landing()["card"]
        ch = built.change_args(c, "Head is now 9ab12cd after the fix")
        assert set(ch) == {"title", "summary", "context", "artifacts", "approve", "recommendedIds", "rationale", "urgency", "blocking", "changeNote"}
        assert built.posted_again(c)["summary"].startswith("An older copy of this card was lost: dismiss it in the app.\n\n6 units land")


def test_a_picture_is_put_with_crews_own_agent(monkeypatch):
    """A card's picture is put with its content type and crew's User-Agent, never urllib's own, which Pending You's host
    refuses as a banned browser signature (403, "error code: 1010": every proposal card's picture, 2026-10-18)."""
    import urllib.request
    sent = []

    class Answer:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        sent.append(req)
        return Answer()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert plan.cards.put("https://pendingyou.test/up", b"png", "image/png") is None
    (req,) = sent
    assert req.get_method() == "PUT"
    assert req.get_header("Content-type") == "image/png"
    assert req.get_header("User-agent") == plan.cards.AGENT
    assert not req.get_header("User-agent").startswith("Python-urllib")
