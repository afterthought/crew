"""crew card read and crew's own cards (the rail-cards spec, briefs.16, record 0031): the decisions in
plugin/lib/cards.py, each on plain facts. The card a key names in the run record; what crew sets on a card; a git
remote as Pending You files by it; the area match_area chose, and the kit's
area to make; a tool's reply read as Pending You's CLI reads it, its refusal in Pending You's words, and the bridge's
own error; and what `crew card read` prints. Then the act that sends crew's own cards, plan.row_card_post,
row_card_change and row_card_close, on a stand-in for the bridge, the run record, a tell and an upload (record 0031):
what each sends and records, the line that adopts a card and whom it is told to, a card the user answered left as it
is unless what it asked changed since, a landing's head among it, and then followed by its new version under the key's
revision rather than changed, and each failure said and recorded. Then the port range a card's session starts
plannotator on, plan.session_env.
The bridge itself, and every command's wiring, are t-cards'."""
import json
import re

import pytest

import cards
import crew


def post(key, by, card, at="2026-10-12T10:00:00Z", **more):
    return dict(Act="card.post", Key=key, By=by, Card=card, At=at, **more)


def close(card, by="swb-1-conductor", **more):
    return dict(Act="card.close", Card=card, By=by, **more)


# --------------------------------------------------------------------------------------- the card a key names

def test_the_card_a_key_names_is_the_agents_newest_post_under_it():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"),
               post("land/b1/abc1234", "swb-1-conductor", "req_b")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") == "req_b"


def test_a_closed_card_is_no_longer_held():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"), close("req_a")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") is None


def test_another_agents_card_under_the_same_key_is_not_this_ones():
    entries = [post("land/b1/abc1234", "swb-2-conductor", "req_a")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") is None


def test_a_refused_post_or_close_holds_nothing_and_closes_nothing():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"),
               post("land/b1/abc1234", "swb-1-conductor", None, Refused="Pending You refused post_request: x"),
               close("req_a", Refused="Pending You refused cancel_request: y")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") == "req_a"


def test_a_close_of_an_older_card_leaves_the_newer_held():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"), post("land/b1/abc1234", "swb-1-conductor", "req_b"),
               close("req_a")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") == "req_b"


def test_crew_sets_the_key_the_session_and_the_area():
    card = {"kind": "choice", "title": "Which fix for v1?", "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]}
    got = cards.post_args(card, "land/b1/abc1234", "swb-1-conductor", "chuck-herdr-alpha", "/w/places/v1", "prj_kit")
    assert got == dict(card, idempotencyKey="land/b1/abc1234", areaId="prj_kit",
                       session={"label": "swb-1-conductor", "machine": "chuck-herdr-alpha", "cwd": "/w/places/v1"})


# -------------------------------------------------------------------------------------------- where it goes

@pytest.mark.parametrize("url, remote", [
    ("https://github.com/WilldanGroup/switchboard-kit.git", "github.com/WilldanGroup/switchboard-kit"),
    ("git@github.com:afterthought/crew.git", "github.com/afterthought/crew"),
    ("ssh://git@github.com:22/afterthought/crew", "github.com/afterthought/crew"),
    ("https://github.com/afterthought/crew/", "github.com/afterthought/crew"),
    ("/Users/chuck/remotes/crew.git", None),
    ("", None)])
def test_a_remote_is_filed_by_its_host_and_repository(url, remote):
    assert cards.remote_of(url) == remote


def test_match_areas_first_suggestion_is_the_cards_area():
    assert cards.area_of({"decision": "use", "suggestions": [{"areaId": "prj_kit", "name": "switchboard-kit"},
                                                             {"areaId": "prj_other"}]}) == "prj_kit"


@pytest.mark.parametrize("matched", [
    {"decision": "create", "suggestions": [{"areaId": "prj_kit"}]},
    {"decision": "use", "suggestions": []},
    {"decision": "choose", "suggestions": [{"name": "no id"}]},
    {"decision": "use", "suggestions": [{"areaId": "kit"}]},
    {}])
def test_no_area_is_taken_when_match_area_says_create_or_names_none(matched):
    assert cards.area_of(matched) is None


def test_the_kits_area_is_made_under_its_key_in_the_partitions_group():
    got = cards.create_area_args("github.com/WilldanGroup/switchboard-kit", "wldn", {"proposedTint": "sage"})
    assert got == {"idempotencyKey": "create-area:WilldanGroup/switchboard-kit", "name": "switchboard-kit",
                   "description": "What crew's agents ask about switchboard-kit.", "tint": "sage", "group": "wldn",
                   "repo": {"remote": "github.com/WilldanGroup/switchboard-kit"}}


def test_an_unknown_tint_is_sky():
    assert cards.create_area_args("github.com/a/b", "wldn", {"proposedTint": "teal"})["tint"] == "sky"


# --------------------------------------------------------------------------------------- reading a reply

def test_a_reply_is_its_structured_content():
    assert cards.reply_object({"structuredContent": {"requestId": "req_1"}, "content": [{"type": "text", "text": "{}"}]}) == {"requestId": "req_1"}


def test_a_reply_is_else_its_first_text_block_that_is_an_object():
    result = {"content": [{"type": "text", "text": "Posted."}, {"type": "text", "text": '{"requestId": "req_1"}'}]}
    assert cards.reply_object(result) == {"requestId": "req_1"}


@pytest.mark.parametrize("result", [{"content": [{"type": "text", "text": "[1]"}]}, {"content": []}, None, "text"])
def test_a_reply_with_no_object_is_none(result):
    assert cards.reply_object(result) is None


def test_a_refusal_is_pending_yous_words():
    result = {"content": [{"type": "text", "text": "Approve requests give their risk in approve.risk."}], "isError": True}
    assert cards.refused_by(result) == "Approve requests give their risk in approve.risk."


def test_a_long_refusal_is_cut_as_pending_yous_cli_cuts_it():
    assert len(cards.refused_by({"content": [{"type": "text", "text": "x" * 400}], "isError": True})) == 300


def test_a_result_not_marked_an_error_is_no_refusal():
    assert cards.refused_by({"content": [{"type": "text", "text": "Not found"}]}) is None


def test_a_refusal_with_no_words_says_so():
    assert cards.refused_by({"isError": True, "content": []}) == "Pending You refused it, and said nothing more"


def test_a_missing_sign_in_is_the_users_to_redo_never_npx():
    said = cards.bridge_said({"code": -32001, "message": "Claude Code on this computer isn’t signed in to Pending You "
                                                         "(https://www.pendingyou.com). Run: npx -y pendingyou@latest init"})
    assert said == ("this host can't ask through Pending You: Claude Code on this computer isn’t signed in to Pending "
                    "You (https://www.pendingyou.com). The user signs it in with pendingyou-signin")


def test_any_other_bridge_error_is_pending_you_unreached():
    assert cards.bridge_said({"code": -32000, "message": "Pending You (https://www.pendingyou.com) couldn’t be reached. "
                                                         "Check this computer’s connection, then try again."}) == \
        ("crew could not reach Pending You: Pending You (https://www.pendingyou.com) couldn’t be reached. "
         "Check this computer’s connection, then try again")


def test_a_reply_naming_no_card_is_refused_as_unread():
    with pytest.raises(crew.Refusal, match="Pending You's answer to post_request names no card"):
        cards.request_id({"status": "pending"}, "post_request")


def test_a_reply_with_no_version_is_refused():
    with pytest.raises(crew.Refusal, match="Pending You gave no version for req_1"):
        cards.version_of({"status": "answered", "version": True}, "req_1")


def test_not_found_is_a_lost_card():
    assert cards.lost("Not found: request:req_5de3dad46fba41068fba.")
    assert not cards.lost("Approve requests give their risk in approve.risk.")
    assert not cards.lost(None)


def test_a_lost_card_is_posted_again_under_its_key_by_the_rails_next_read():
    said = cards.lost_said("land/b1", "req_old", "Not found: request:req_old.")
    assert said.startswith("card req_old under land/b1 is lost to its owner (Pending You: \"Not found: request:req_old.\")")
    assert said.endswith("the rail's next read posts it again under its key, its summary saying an older copy is dead and "
                         "to dismiss it in the app")
    assert cards.lost_said("ask/swb-1-conductor/hold", "req_q", "Not found.").endswith(
        "Ask it again if it still matters, saying in it that an older copy is dead and to dismiss it in the app")


# ----------------------------------------------------------------------------------------- what read prints

def test_a_card_waiting_on_the_user():
    got = {"requestId": "req_1", "status": "pending", "turn": "you", "version": 1, "url": "https://www.pendingyou.com/app/r/req_1"}
    assert cards.answer_lines("land/b1/abc1234", "req_1", got) == [
        "card land/b1/abc1234: req_1, pending, waiting on the user", "  https://www.pendingyou.com/app/r/req_1"]


def test_an_answer_with_the_users_words():
    got = {"status": "answered", "turn": "agent", "answer": {"choiceIds": ["fix"], "note": {"text": "Both, please.", "via": "voice"}},
           "messages": [{"from": "you", "body": "And add a test."}, {"from": "you"}, "not a message"]}
    assert cards.answer_lines("land/b1/abc1234", "req_1", got) == [
        "card land/b1/abc1234: req_1, answered, your turn: the user has answered", "  picked: fix", "  note: Both, please.",
        "  you: And add a test."]


def test_an_approval_and_a_grouped_answer():
    got = {"status": "answered", "turn": "agent",
           "answer": {"approved": False, "answers": {"plan": {"approved": True}, "units-1": {"choiceIds": ["u1", "u2"]}}}}
    assert cards.answer_lines("proposal/4", "req_1", got)[1:] == ["  approved: no", "  plan: approved", "  units-1: u1, u2"]


def test_an_answer_is_shown_only_on_the_agents_turn():
    got = {"status": "pending", "turn": "you", "answer": {"choiceIds": ["fix"]}}
    assert cards.answer_lines("land/b1/abc1234", "req_1", got) == ["card land/b1/abc1234: req_1, pending, waiting on the user"]


def test_what_the_reply_leaves_out_is_left_out():
    assert cards.answer_lines("land/b1/abc1234", "req_1", {}) == ["card land/b1/abc1234: req_1"]


# ------------------------------------------------------------- the act that sends crew's own cards (record 0031)
# plan.row_card_post, row_card_change and row_card_close on a stand-in for what they reach: the bridge answers as
# Pending You would, and every emit, tell and upload is kept to be read. What each sends and records, and that a
# refusal, a host not signed in, an unread reply and a card not found are said and recorded and refuse nothing.
import plan  # noqa: E402

WHERE = ("/kit/main", "github.com/WilldanGroup/switchboard-kit")
FACTS = dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 3}, head="abc1234", at=None, moved=0, pr=None)


class Py:
    """A stand-in for one session with Pending You: each tool answered from answers, a (got, words) pair, a Refusal
    raised when it is one; a session that can't open raises its refusal on entry."""

    def __init__(self, acts, answers, opening=None):
        self.acts, self.answers, self.opening = acts, answers, opening

    def __enter__(self):
        if self.opening:
            raise crew.Refusal(self.opening)
        return self

    def __exit__(self, *exc):
        pass

    def answer(self, tool, args):
        self.acts.calls.append((tool, args))
        got = self.answers.get(tool, ({"ok": True}, None))
        if isinstance(got, crew.Refusal):
            raise got
        return got

    def call(self, tool, args):
        got, words = self.answer(tool, args)
        if words is not None:
            raise crew.Refusal(f"Pending You refused {tool}: {words}")
        return got


class Acts:
    def __init__(self, answers=None, entries=(), caller="swb-1-conductor", opening=None, put=None):
        self.answers, self.held, self.who, self.opening, self.put_said = dict(answers or {}), list(entries), caller, opening, put
        self.calls, self.emitted, self.told, self.puts, self.names = [], [], [], [], []

    def bridge(self, name, later, held=None):
        self.names.append(name)
        return Py(self, self.answers, self.opening)

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act, On=on, label=label))

    def entries(self, label):
        return self.held

    def tell(self, name, text):
        self.told.append((name, text))
        return True

    def put(self, url, data, kind):
        self.puts.append((url, len(data), kind))
        return self.put_said

    def session(self, label, key, facts):  # a landing card's reading, which crew starts before it builds the card
        return "http://chuck-herdr-alpha.ts.swancloud.net:19432"

    def end(self, label, key):  # no reading recorded on this host, so its close ends none
        return None

    def release_preview(self, label, key):  # no preview recorded on this host, so its close releases none
        return None

    def host(self):
        return "chuck-herdr-alpha"

    def caller(self):
        return self.who

    def kits(self, label):  # the kits the partition's teams build, which tell land/<kit> from land/<bolt>
        return ("switchboard-kit",)


MATCHED = {"decision": "use", "suggestions": [{"areaId": "prj_kit"}]}
POSTED = {"requestId": "req_c1", "url": "https://www.pendingyou.com/app/r/req_c1", "version": 1}


def act_post(acts):
    return plan.row_card_post(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, WHERE, acts)


def test_a_card_is_posted_in_its_owners_name_under_its_rows_key_filed_in_its_kit_and_recorded_on_its_row(capsys):
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)})
    assert act_post(acts) == "req_c1"
    assert acts.names == ["swb-1-conductor"]
    assert [t for t, _ in acts.calls] == ["match_area", "post_request"]
    sent = acts.calls[1][1]
    assert (sent["idempotencyKey"], sent["areaId"], sent["session"]) == (
        "land/b1_", "prj_kit", {"label": "swb-1-conductor", "machine": "chuck-herdr-alpha", "cwd": "/kit/main"})
    assert sent["approve"]["risk"] == "high"
    assert acts.emitted == [dict(Act="card.post", On=["bolt/b1"], by="swb-1-conductor", Card="req_c1", Key="land/b1", Head="abc1234",
                                 label="wldn")]
    assert capsys.readouterr().out == ("card land/b1: req_c1 https://www.pendingyou.com/app/r/req_c1\n"
                                       "call get_request (requestId req_c1, name swb-1-conductor)\n")
    assert acts.told == []


def test_a_card_raised_outside_its_owners_turn_is_told_to_its_owner_with_the_line_that_adopts_it(capsys):
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)}, caller="chuck@chuck-herdr-alpha")
    act_post(acts)
    assert acts.told == [("swb-1-conductor", "Your card land/b1 is up for the user: call get_request (requestId req_c1, "
                                             "name swb-1-conductor), to hear their answer.")]
    assert "told swb-1-conductor: call get_request (requestId req_c1, name swb-1-conductor)" in capsys.readouterr().out


def test_the_first_card_in_a_kit_makes_its_area_under_the_kits_key_in_the_partitions_group():
    acts = Acts({"match_area": ({"decision": "create", "proposedTint": "sage"}, None),
                 "create_area": ({"areaId": "prj_new"}, None), "post_request": (POSTED, None)})
    act_post(acts)
    made = acts.calls[1]
    assert made[0] == "create_area" and (made[1]["idempotencyKey"], made[1]["group"]) == ("create-area:WilldanGroup/switchboard-kit", "wldn")
    assert acts.calls[2][1]["areaId"] == "prj_new"


def test_pending_you_refusing_the_card_is_said_in_its_words_recorded_and_refuses_nothing_of_the_event(capsys):
    acts = Acts({"match_area": (MATCHED, None), "post_request": (None, "Approve requests give their risk in approve.risk.")})
    assert act_post(acts) is None
    assert acts.emitted == [dict(Act="card.post", On=["bolt/b1"], by="swb-1-conductor", Key="land/b1", label="wldn",
                                 refused="Pending You refused post_request: Approve requests give their risk in approve.risk.")]
    assert "card land/b1 not posted: Pending You refused post_request: Approve requests give their risk in approve.risk." in capsys.readouterr().err


def test_a_host_not_signed_in_is_said_and_recorded_and_the_event_stands(capsys):
    said = cards.bridge_said({"code": cards.SIGNED_OUT, "message": "Claude Code on this computer isn’t signed in to Pending You. Run: npx x"})
    acts = Acts(opening=f"{said}. {plan.CARD_LATER}")
    assert act_post(acts) is None
    assert "this computer isn’t signed in to Pending You" in acts.emitted[0]["refused"] and acts.calls == []
    assert "not posted: this host can't ask through Pending You" in capsys.readouterr().err


def test_a_reply_naming_no_card_is_recorded_as_unread_never_taken_as_empty():
    acts = Acts({"match_area": (MATCHED, None), "post_request": ({"status": "pending"}, None)})
    assert act_post(acts) is None
    assert acts.emitted[0]["refused"] == "Pending You's answer to post_request names no card: crew can't tell what it did"


def test_a_cards_picture_is_put_to_the_upload_url_its_post_returned_with_its_content_type(capsys):
    case = "One more unit."
    facts = dict(n=4, state="open", case=case, before=plan.Plan(PLAN), after=plan.Plan(PLAN_AFTER),
                 argvs=[plan.do_args("wldn", 'unit add g-one "One unit." --repo switchboard-kit')], waiting=[])
    up = dict(POSTED, uploads=[{"title": "The change, once approved", "uploadUrl": "https://up.example/p", "expiresAt": "x"}])
    acts = Acts({"match_area": (MATCHED, None), "post_request": (up, None)}, caller="wldn-planner")
    plan.row_card_post(None, "wldn", "wldn-planner", cards.proposal_card, facts, WHERE, acts)
    assert acts.puts and acts.puts[0][0] == "https://up.example/p" and acts.puts[0][2] == "image/png" and acts.puts[0][1] > 1000
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)}, caller="wldn-planner")
    plan.row_card_post(None, "wldn", "wldn-planner", cards.proposal_card, facts, WHERE, acts)
    assert "its picture did not reach the card: Pending You gave no upload URL for it" in capsys.readouterr().err


HELD = [dict(Act="card.post", Key="land/b1", By="swb-1-conductor", Card="req_c1")]


def test_a_change_goes_to_the_owners_card_at_the_version_pending_you_reports_with_its_note(capsys):
    acts = Acts({"get_request": ({"status": "pending", "version": 3}, None), "update_request": ({"version": 4}, None)}, entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "Head is now abc1234", WHERE, acts) == "req_c1"
    tool, sent = acts.calls[1]
    assert tool == "update_request" and (sent["requestId"], sent["name"], sent["expectedVersion"], sent["changeNote"]) == (
        "req_c1", "swb-1-conductor", 3, "Head is now abc1234")
    assert "kind" not in sent and "idempotencyKey" not in sent
    assert acts.emitted == [dict(Act="card.update", On=["bolt/b1"], by="swb-1-conductor", Card="req_c1", Key="land/b1", Head="abc1234",
                                 label="wldn")]
    assert capsys.readouterr().out == "card land/b1: req_c1 changed, now version 4\n"


def test_a_change_that_finds_its_card_not_found_posts_it_again_saying_the_older_copy_is_dead():
    acts = Acts({"get_request": (None, "Not found: request:req_c1."), "match_area": (MATCHED, None),
                 "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "x note", WHERE, acts) == "req_c2"
    assert [(e["Act"], e.get("State"), e.get("Card")) for e in acts.emitted] == [("card.close", "lost", "req_c1"), ("card.post", None, "req_c2")]
    assert acts.calls[-1][1]["summary"].startswith(cards.DEAD)
    assert (acts.calls[-1][1]["idempotencyKey"], acts.emitted[-1]["Key"]) == ("land/b1:2", "land/b1")


ANSWERED = {"status": "answered", "turn": "agent", "version": 3}
MOVED = {"approved": "0123abc" + "0" * 33}  # the head the user approved, before the bolt's head moved to abc1234


def test_a_change_to_a_card_the_user_answered_asking_anew_acks_it_with_the_note_and_posts_the_new_version_following_it(capsys):
    acts = Acts({"get_request": (ANSWERED, None), "ack_answer": ({"version": 4}, None),
                 "match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "Head is now abc1234", WHERE, acts,
                                anew=MOVED) == "req_c2"
    assert [t for t, _ in acts.calls] == ["get_request", "ack_answer", "match_area", "post_request"]
    assert acts.calls[1][1] == {"requestId": "req_c1", "name": "swb-1-conductor", "expectedVersion": 3, "outcome": "Head is now abc1234"}
    sent = acts.calls[3][1]
    assert (sent["idempotencyKey"], sent["follows"], sent["kind"]) == ("land/b1:2", "req_c1", "approve")
    opening, _, rest = sent["summary"].partition("\n\n")
    assert re.fullmatch(r"You answered the card before this one, by [0-9-]+ [0-9:]+ UTC: crew holds no record of what you "
                        r"answered\. Since then: head is now abc1234\.", opening)
    assert rest.startswith("Its head moved since your approval, from 0123abc to abc1234: approving this lands abc1234.")
    assert [(e["Act"], e.get("Card"), e["Key"], e.get("State"), e.get("Outcome"), e.get("Head")) for e in acts.emitted] == [
        ("card.close", "req_c1", "land/b1", "closed", plan.REVISED, None), ("card.post", "req_c2", "land/b1", None, None, "abc1234")]
    out = capsys.readouterr().out
    assert out.startswith("card land/b1: req_c1 closed, the user having answered it, and its new version follows it\n"
                          "card land/b1: req_c2 https://") and "call get_request (requestId req_c2, name swb-1-conductor)" in out
    after = HELD + [dict(Act="card.close", Card="req_c1", Key="land/b1", By="swb-1-conductor", State="closed"),
                    dict(Act="card.post", Key="land/b1", By="swb-1-conductor", Card="req_c2")]
    assert cards.card_under(after, "land/b1", "swb-1-conductor") == "req_c2"


def test_a_close_refused_on_a_card_the_user_answered_posts_nothing_and_is_recorded_as_the_change_refused(capsys):
    acts = Acts({"get_request": ({"status": "answered", "version": 3}, None), "ack_answer": (None, "Your latest message asks them something.")},
                entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "x note", WHERE, acts, anew=MOVED) is None
    assert [t for t, _ in acts.calls] == ["get_request", "ack_answer"]
    assert acts.emitted[0]["refused"] == ("Pending You refused the close of the card the user answered: "
                                          "Your latest message asks them something.")


@pytest.mark.parametrize("status, kind_changed, questions, anew, how", [
    ("pending", False, False, False, "change"), ("snoozed", False, False, False, "change"), ("pending", True, False, False, "follow"),
    ("pending", False, True, False, "follow"), ("snoozed", False, True, False, "follow"), ("pending", False, False, True, "change"),
    ("answered", False, False, False, "leave"), ("answered", False, True, False, "leave"), ("answered", False, False, True, "follow"),
    ("answered", True, False, False, "follow"), ("answered", False, True, True, "follow"),
    ("resolved", False, False, False, "leave"), ("closed", False, True, False, "leave"), ("resolved", False, False, True, "ended"),
    ("resolved", True, False, False, "ended"), ("cancelled", False, False, False, "ended"), ("expired", False, True, False, "ended")])
def test_a_card_waiting_on_the_user_is_changed_in_place_and_one_they_answered_is_left_unless_what_it_asks_changed(
        status, kind_changed, questions, anew, how):
    """record 0031 §1 and §3: a card the user has answered is final for what it asked, picked up or acked since or not;
    only its kind changed, or what it asks changed since (anew), follows it, or posts again once Pending You ended it;
    a waiting card is changed in place, or followed when its kind or its questions would not change in place."""
    assert cards.revision({"status": status, "version": 2}, kind_changed, questions, anew) == how


@pytest.mark.parametrize("status", ["answered", "resolved", "closed"])
@pytest.mark.parametrize("note", ["A yes now frees swb-1 for b2", "Its preview of abc1234 is up", "Its reading is at a new link"])
def test_a_change_to_a_card_the_user_answered_that_asks_nothing_anew_leaves_it_as_it_is(capsys, status, note):
    """A landing card the user approved, before ops lands it: a merge freeing the team's next bolt (teams.16), a
    preview's end and a reading's new link change what it offers, not what it asked, so it is neither acked, closed nor
    followed, nothing is recorded, and the approval goes on to ops (plan.16)."""
    acts = Acts({"get_request": (dict(ANSWERED, status=status), None)}, entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, note, WHERE, acts) == "req_c1"
    assert [t for t, _ in acts.calls] == ["get_request"] and acts.emitted == [] and acts.told == []
    assert capsys.readouterr().out == "card land/b1: req_c1 is left as it is: the user has answered it\n"


def test_a_card_pending_you_ended_after_the_users_answer_asking_anew_is_recorded_closed_and_followed(capsys):
    """The conductor acked the approval it passed on to ops, so Pending You reads the card resolved; a merge then moved
    the head: the card is recorded closed as Pending You ended it, and the new card follows it, saying so."""
    acts = Acts({"get_request": (dict(ANSWERED, status="resolved"), None), "match_area": (MATCHED, None),
                 "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=HELD)
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "Its head is now abc1234", WHERE, acts,
                                anew={"approved": ""}) == "req_c2"
    assert [t for t, _ in acts.calls] == ["get_request", "match_area", "post_request"]
    sent = acts.calls[2][1]
    assert sent["follows"] == "req_c1" and sent["summary"].startswith("You answered the card before this one, by ")
    assert sent["summary"].split("\n\n")[1].startswith(
        "Its head is now abc1234, and crew holds no record of the head you approved: approving this lands abc1234.")
    assert [(e["Act"], e.get("Card"), e.get("State"), e.get("Outcome")) for e in acts.emitted] == [
        ("card.close", "req_c1", "closed", plan.ENDED_ELSEWHERE), ("card.post", "req_c2", None, None)]


@pytest.mark.parametrize("entries, head, anew", [
    ([], "abc1234", None),
    ([post("land/b1", "swb-1-conductor", "req_c1", Head="abc1234")], "abc1234", None),
    ([post("land/b1", "swb-1-conductor", "req_c1", Head="0123abc")], "abc1234", {"approved": "0123abc"}),
    ([post("land/b1", "swb-1-conductor", "req_c1")], "abc1234", {"approved": ""}),
    ([post("land/b1", "swb-1-conductor", "req_c1", Head="0123abc"), dict(Act="card.update", Card="req_c1", Key="land/b1", Head="abc1234")],
     "abc1234", None),
    ([post("land/b1", "swb-1-conductor", "req_c1", Head="0123abc"),
      dict(Act="card.update", Card="req_c1", Key="land/b1", Head="abc1234", Refused="Pending You refused update_request: x")],
     "abc1234", {"approved": "0123abc"}),
    ([post("land/b1", "swb-1-conductor", "req_c0", Head="abc1234"), post("land/b1", "swb-1-conductor", "req_c1", Head="0123abc")],
     "abc1234", {"approved": "0123abc"})])
def test_a_card_asks_anew_only_once_the_head_moved_since_the_head_its_last_post_or_change_recorded(entries, head, anew):
    """The head a landing's or a deploy's card asks about is the one its last post or change done recorded, a refused
    change showing the user nothing; a card with none recorded, posted before crew recorded heads, asks anew, since
    crew can't tell which head the user approved (read.1)."""
    held = cards.card_under(entries, "land/b1", "swb-1-conductor")
    assert cards.head_anew(entries, held, head) == anew


STEP = dict(env="srv", n=1, text="restart crew's teams", doer="swancloud-ops", held=True, why=None, where=None, commands=[], done=None,
            consequences={"now": "It runs at once; no stage is working on srv now"})


def test_a_card_whose_kind_changed_is_withdrawn_while_it_waits_and_its_new_version_posted_following_it(capsys):
    """A step recorded again with an agent as its doer, held, where the user was: its `do` card becomes a choice,
    which update_request never changes (cards.CHANGED)."""
    acts = Acts({"get_request": ({"status": "pending", "version": 3}, None), "cancel_request": ({"version": 4}, None),
                 "match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_s2"), None)},
                entries=[post("op/srv/1", "swancloud-ops", "req_s1")], caller="swancloud-ops")
    note = "Recorded again: its doer and its hold changed"
    assert plan.row_card_change(None, "swancloud", "swancloud-ops", cards.step_card, STEP, note, WHERE, acts, kind_changed=True) == "req_s2"
    assert [t for t, _ in acts.calls] == ["get_request", "cancel_request", "match_area", "post_request"]
    assert acts.calls[1][1] == {"requestId": "req_s1", "name": "swancloud-ops", "reason": note}
    sent = acts.calls[3][1]
    assert (sent["idempotencyKey"], sent["follows"], sent["kind"]) == ("op/srv/1:2", "req_s1", "choice")
    assert [(e["Act"], e.get("Card"), e.get("State"), e.get("Outcome")) for e in acts.emitted] == [
        ("card.close", "req_s1", "withdrawn", plan.RENEWED), ("card.post", "req_s2", None, None)]
    assert capsys.readouterr().out.startswith("card op/srv/1: req_s1 withdrawn, its kind having changed, and its new version follows it\n"
                                              "card op/srv/1: req_s2 https://")


def test_a_post_pending_you_answers_with_the_card_the_record_already_holds_open_is_recorded_once(capsys):
    """Read on mac-studio on 2026-10-18: two rail reads, from swancloud-ops's start and the design agent's, swept at
    once; each raised op/swancloud-srv/1's card, Pending You's idempotency gave both req_2a16bbe95cd841c58611, and the
    run record held two posts of it, at 15:24:51Z and 15:24:52Z. Here the other read's post is recorded while this
    one's is asked: this host's record holds nothing under the key until post_request is answered, then that post."""
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)}, caller="chuck@chuck-herdr-alpha")
    acts.entries = lambda label: [post("land/b1", "swb-1-conductor", "req_c1")] if any(t == "post_request" for t, _ in acts.calls) else []
    assert act_post(acts) == "req_c1"
    assert acts.emitted == [] and acts.told == []
    assert capsys.readouterr().out == ("card land/b1: req_c1 https://www.pendingyou.com/app/r/req_c1, its post recorded already\n"
                                       "call get_request (requestId req_c1, name swb-1-conductor)\n")


# A step's card following its deploy's card, which swancloud-ops's run record still holds open (rail-cards: a post
# that follows an open card reads it).
DEPLOY_HELD = [post("deploy/srv", "swancloud-ops", "req_d1")]


def act_follow(get_request, entries=DEPLOY_HELD, follows="req_d1", since=None):
    acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_s1"), None), "get_request": get_request},
                entries=entries, caller="swancloud-ops")
    facts = dict(STEP, follows=follows) if follows else STEP
    return acts, plan.row_card_post(None, "swancloud", "swancloud-ops", cards.step_card, facts, WHERE, acts, since)


def test_a_post_following_a_card_pending_you_then_reports_resolved_records_the_post_and_then_that_card_closed(capsys):
    acts, card = act_follow(({"status": "resolved", "version": 4}, None))
    assert card == "req_s1"
    assert [t for t, _ in acts.calls] == ["match_area", "post_request", "get_request"]
    assert acts.calls[1][1]["follows"] == "req_d1" and acts.calls[2][1] == {"requestId": "req_d1", "name": "swancloud-ops"}
    assert [(e["Act"], e["On"], e["Card"], e["Key"], e.get("State"), e.get("Outcome")) for e in acts.emitted] == [
        ("card.post", ["env/srv"], "req_s1", "op/srv/1", None, None),
        ("card.close", ["env/srv"], "req_d1", "deploy/srv", "closed", plan.FOLLOWED)]
    assert capsys.readouterr().out.splitlines()[-1] == "card deploy/srv: req_d1 picked up in Pending You by req_s1, which follows it"
    assert cards.card_under(DEPLOY_HELD + [dict(e, By=e["by"]) for e in acts.emitted], "deploy/srv", "swancloud-ops") is None


@pytest.mark.parametrize("status", ["pending", "answered"])
def test_a_post_following_a_card_that_still_waits_or_is_answered_leaves_it_open(status):
    acts, card = act_follow(({"status": status, "turn": "agent", "version": 3}, None))
    assert card == "req_s1" and [t for t, _ in acts.calls] == ["match_area", "post_request", "get_request"]
    assert [e["Act"] for e in acts.emitted] == ["card.post"]


@pytest.mark.parametrize("get_request, why", [
    ((None, "Too many requests."), "Pending You refused get_request: Too many requests."),
    ((None, "Not found: request:req_d1."), "Pending You refused get_request: Not found: request:req_d1."),
    (crew.Refusal(f"Pending You did not answer get_request within 60 seconds. {plan.CARD_LATER}"),
     "Pending You did not answer get_request within 60 seconds.")])
def test_a_post_whose_read_of_the_card_it_follows_fails_stands_and_says_so(capsys, get_request, why):
    acts, card = act_follow(get_request)
    assert card == "req_s1" and [(e["Act"], e.get("refused")) for e in acts.emitted] == [("card.post", None)]
    assert capsys.readouterr().err == f"card deploy/srv: whether req_d1 was picked up can't be read: {why}\n"


@pytest.mark.parametrize("entries, follows", [
    (DEPLOY_HELD, None),
    (DEPLOY_HELD + [dict(Act="card.close", Card="req_d1", Key="deploy/srv", By="swancloud-ops", State="closed")], "req_d1"),
    ([post("deploy/srv", "swb-1-conductor", "req_d1")], "req_d1")])
def test_a_post_following_nothing_or_a_card_the_record_holds_closed_reads_nothing(entries, follows):
    acts, card = act_follow(({"status": "resolved", "version": 4}, None), entries, follows, ["The deploy ended, and this is its step 1"])
    assert card == "req_s1" and [t for t, _ in acts.calls] == ["match_area", "post_request"]
    assert [e["Act"] for e in acts.emitted] == ["card.post"]


def test_a_post_following_a_card_given_back_as_already_recorded_reads_nothing():
    acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_s1"), None)}, caller="swancloud-ops")
    acts.entries = lambda label: DEPLOY_HELD + ([post("op/srv/1", "swancloud-ops", "req_s1")]
                                                if any(t == "post_request" for t, _ in acts.calls) else [])
    plan.row_card_post(None, "swancloud", "swancloud-ops", cards.step_card, dict(STEP, follows="req_d1"), WHERE, acts)
    assert [t for t, _ in acts.calls] == ["match_area", "post_request"] and acts.emitted == []


POST, CLOSE = (lambda card, by="swb-1-conductor", key="land/b1": dict(Act="card.post", Key=key, By=by, Card=card),
               lambda card, state="closed": dict(Act="card.close", Card=card, State=state))


@pytest.mark.parametrize("entries, asked", [
    ([], "land/b1_"),
    ([POST("req_1")], "land/b1_"),
    ([POST("req_1"), POST("req_1")], "land/b1_"),
    ([POST("req_1"), CLOSE("req_1", "declined")], "land/b1:2"),
    ([POST("req_1"), CLOSE("req_1"), POST("req_2")], "land/b1:2"),
    ([POST("req_1"), CLOSE("req_1"), POST("req_2"), CLOSE("req_2", "lost")], "land/b1:3"),
    ([POST("req_1", by="swb-2-conductor"), CLOSE("req_1")], "land/b1_"),
    ([POST("req_1", key="land/b2"), CLOSE("req_1")], "land/b1_"),
    ([dict(POST("req_1"), Refused="x"), CLOSE("req_1")], "land/b1_")])
def test_a_card_is_posted_under_its_rows_key_and_after_a_closed_one_under_the_key_with_its_revision(entries, asked):
    assert cards.post_key(entries, "land/b1", "swb-1-conductor") == asked


@pytest.mark.parametrize("key, first, revised", [
    ("batch/7", "batch/7_", "batch/7:2"), ("land/a", "land/a__", "land/a:2"), ("op/a/1", "op/a/1__", "op/a/1:2"),
    ("batch/12", "batch/12", "batch/12:2"), ("deploy/dev", "deploy/dev", "deploy/dev:2")])
def test_a_key_shorter_than_pending_you_takes_is_filled_out_to_eight_characters_the_same_on_every_post(key, first, revised):
    """rail-cards: a row's key shorter than Pending You takes. Read on mac-studio on 2026-10-19 (test D): crew could not
    post batch 7's card, the rail saying "card: batch/7, none open; its last post was refused: Pending You refused
    post_request: Some fields need fixing. idempotencyKey: Too small: expected string to have >=8 characters.", since
    batch/<n> under ten is seven characters. A short key is filled out at its end, the same on a retry and while its
    card is open; its revision, and a key long enough, are sent as they are."""
    by = "wldn-planner"
    held, closed = [POST("req_1", by=by, key=key)], [POST("req_1", by=by, key=key), CLOSE("req_1")]
    sent = [cards.post_key([], key, by), cards.post_key([], key, by), cards.post_key(held, key, by), cards.post_key(closed, key, by)]
    assert sent == [first, first, first, revised] and all(len(k) >= cards.KEY_LEAST for k in sent)


def test_a_change_with_no_card_held_posts_it():
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)})
    assert plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "x note", WHERE, acts) == "req_c1"
    assert [t for t, _ in acts.calls] == ["match_area", "post_request"]


def test_a_close_acks_an_answered_card_with_its_outcome_and_withdraws_a_waiting_one_with_its_reason(capsys):
    acts = Acts({"get_request": ({"status": "answered", "version": 3}, None)}, entries=HELD)
    assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome="Landed as #24 at 14:02", acts=acts) == "req_c1"
    assert acts.calls[1] == ("ack_answer", {"requestId": "req_c1", "name": "swb-1-conductor", "expectedVersion": 3, "outcome": "Landed as #24 at 14:02"})
    assert acts.emitted[0] == dict(Act="card.close", On=["bolt/b1"], by="swb-1-conductor", Card="req_c1", Key="land/b1", State="closed",
                                   Outcome="Landed as #24 at 14:02", label="wldn")
    acts = Acts({"get_request": ({"status": "pending", "version": 1}, None)}, entries=HELD)
    plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", reason="Held for a fix: the log is empty", acts=acts)
    assert acts.calls[1] == ("cancel_request", {"requestId": "req_c1", "name": "swb-1-conductor", "reason": "Held for a fix: the log is empty"})
    assert acts.emitted[0]["State"] == "withdrawn"
    assert capsys.readouterr().out.splitlines()[-1] == "card land/b1: req_c1 withdrawn"


def test_a_landing_on_the_users_words_sends_them_answered_here_and_records_the_outcome_without_them(capsys):
    """plan.16, main-level spec "The card closes with the user's words": a landing card still waiting closes as answered
    in the conversation, Pending You sent the user's words, the run record the outcome alone (record.3); one the user
    also tapped is acked with the words."""
    landed = plan.landed_words("c" * 40, "24")
    outcome, said = plan.pane_landed(landed, "wldn-ops", "2026-10-22T21:04:00Z", "Land swb-1's bolt")
    acts = Acts({"get_request": ({"status": "pending", "version": 1}, None)}, entries=HELD)
    assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome=outcome, acts=acts, said=said, here=True) == "req_c1"
    assert acts.calls[1] == ("cancel_request", {"requestId": "req_c1", "name": "swb-1-conductor", "reason": cards.cut(said, cards.OUTCOME),
                                                "answeredHere": True})
    assert acts.calls[1][1]["reason"].startswith('Landed on the user\'s word in wldn-ops\'s pane, "Land swb-1\'s bolt"; landed on')
    assert (acts.emitted[0]["State"], acts.emitted[0]["Outcome"]) == ("closed", outcome)
    assert "Land swb-1's bolt" not in repr(acts.emitted)
    assert capsys.readouterr().out.splitlines()[0] == "card land/b1: req_c1 closed"
    acts = Acts({"get_request": ({"status": "answered", "version": 3}, None)}, entries=HELD)
    plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome=outcome, acts=acts, said=said, here=True)
    assert acts.calls[1][0] == "ack_answer" and "answeredHere" not in acts.calls[1][1]
    assert (acts.emitted[0]["State"], acts.emitted[0]["Outcome"]) == ("closed", outcome)


LONG = ("Applied: added " + ", ".join(f"the-unit-that-does-thing-{i}" for i in range(1, 9))
        + "; 3 other changes. Left out on your word: the-briefs-say-never-wt-submit-help.")


def test_a_close_cuts_its_outcome_and_its_reason_to_pending_yous_two_hundred_characters_and_records_them_whole():
    """Read on 2026-10-18: the planner's `crew plan answer 142 ...` applied the proposal and printed "card
    proposal/139 not closed: Pending You refused the close: Some fields need fixing. outcome: Too big: expected
    string to have <=200 characters.", the card left open. Pending You takes an outcome or a reason of 200 characters
    at most (cards.OUTCOME)."""
    assert len(LONG) > cards.OUTCOME
    held = [post("proposal/139", "wldn-planner", "req_p1")]
    acts = Acts({"get_request": ({"status": "answered", "turn": "agent", "version": 3}, None)}, entries=held, caller="wldn-planner")
    acts.end = lambda label, key: None  # a proposal's reading session, which this one has none of
    assert plan.row_card_close(None, "wldn", "wldn-planner", "proposal/139", outcome=LONG, acts=acts) == "req_p1"
    tool, sent = acts.calls[1]
    assert (tool, len(sent["outcome"]), sent["outcome"][-1]) == ("ack_answer", cards.OUTCOME, "…")
    assert LONG.startswith(sent["outcome"][:-1]) and acts.emitted[0]["Outcome"] == LONG
    acts = Acts({"get_request": ({"status": "pending", "version": 1}, None)}, entries=held, caller="wldn-planner")
    acts.end = lambda label, key: None
    plan.row_card_close(None, "wldn", "wldn-planner", "proposal/139", reason=LONG, acts=acts)
    tool, sent = acts.calls[1]
    assert (tool, len(sent["reason"]), acts.emitted[0]["Outcome"]) == ("cancel_request", cards.OUTCOME, LONG)
    short = cards.close_call({"status": "pending"}, "req_p1", "wldn-planner", reason="Dropped: not now")
    assert short[1]["reason"] == "Dropped: not now"


def test_the_close_of_a_card_the_user_answered_records_what_they_answered_in_crews_words_and_a_withdrawal_none():
    """rail-cards "The close of an answered card records the answer": the landings card sent with land:y ticked,
    land:z cleared and a note; a deploy declined with "not tonight"; a card still waiting, withdrawn, records none."""
    sent = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y"], "note": "z after its fix"}}
    held = [post("land/crew", "swancloud-ops", "req_k1")]
    acts = Acts({"get_request": (sent, None)}, entries=held, caller="swancloud-ops")
    plan.row_card_close(None, "swancloud", "swancloud-ops", "land/crew", outcome="Landing as you ticked: y.", acts=acts,
                        offered=["land:y", "land:z"], Rows="1")
    assert (acts.emitted[0]["State"], acts.emitted[0]["Answer"], acts.emitted[0]["Rows"]) == ("closed", "ticked y, left z, with a note", "1")
    assert "after its fix" not in repr(acts.emitted)
    declined = {"status": "answered", "turn": "agent", "version": 3, "answer": {"approved": False, "text": "not tonight"}}
    acts = Acts({"get_request": (declined, None)}, entries=[post("deploy/srv", "swancloud-ops", "req_d1")], caller="swancloud-ops")
    plan.row_card_close(None, "swancloud", "swancloud-ops", "deploy/srv", outcome="Declined", acts=acts)
    assert acts.emitted[0]["Answer"] == "declined, with a note" and "tonight" not in repr(acts.emitted)
    acts = Acts({"get_request": ({"status": "pending", "turn": "you", "version": 1}, None)}, entries=HELD)
    plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", reason="Held for a fix", acts=acts)
    assert acts.emitted[0]["State"] == "withdrawn" and "Answer" not in acts.emitted[0]


def test_a_card_closed_as_answered_in_its_owners_pane_records_the_pane_as_its_answer():
    landed = plan.landed_words("c" * 40, "24")
    outcome, said = plan.pane_landed(landed, "wldn-ops", "2026-10-22T21:04:00Z", "Land swb-1's bolt")
    acts = Acts({"get_request": ({"status": "pending", "turn": "you", "version": 1}, None)}, entries=HELD)
    plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome=outcome, acts=acts, said=said, here=True)
    assert (acts.emitted[0]["State"], acts.emitted[0]["Answer"]) == ("closed", "answered in swb-1-conductor's pane")


def test_a_card_followed_once_answered_records_the_answer_on_its_close_and_on_the_entries_its_new_card_follows(monkeypatch):
    acts = Acts({"get_request": (dict(ANSWERED, answer={"approved": True}), None), "ack_answer": ({"version": 4}, None),
                 "match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_c2"), None)}, entries=HELD)
    seen, posted = [], plan.card_posted
    monkeypatch.setattr(plan, "card_posted", lambda *a, **kw: seen.append(a[5]) or posted(*a, **kw))
    plan.row_card_change(None, "wldn", "swb-1-conductor", cards.landing_card, FACTS, "Head is now abc1234", WHERE, acts, anew=MOVED)
    close = acts.emitted[0]
    assert (close["Act"], close["State"], close["Answer"]) == ("card.close", "closed", "approved")
    (entries,) = seen
    assert {k: entries[-1][k] for k in ("Act", "Card", "State", "Answer")} == {"Act": "card.close", "Card": "req_c1", "State": "closed",
                                                                             "Answer": "approved"}
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", entries[-1]["At"])


def test_a_followed_card_pending_you_picked_up_records_the_answer_its_reply_still_carries():
    acts, card = act_follow(({"status": "resolved", "version": 4, "answer": {"approved": True}}, None))
    assert [(e["Act"], e.get("Answer")) for e in acts.emitted] == [("card.post", None), ("card.close", "approved")]


# A record's card the user answered with a note, and the design agent's revision of the record after it (rail-cards
# "A card that follows one the user answered says so first", "A follow-on with nothing changed is not posted").
DESIGN, RKEY = "swancloud-design", "record/crew/0019"
RECORD = dict(kit="crew", number=19, title="One card per thing", opening="A card asked again says what changed.", quoted=[],
              text="# 19. One card per thing\n\nBody.", alternatives=None)
ANSWERED_ON = [post(RKEY, DESIGN, "req_1", at="2026-10-23T13:10:04Z"),
               dict(Act="card.close", Key=RKEY, By=DESIGN, Card="req_1", State="closed", At="2026-10-23T14:02:41Z",
                    Answer="declined, with a note")]
OPENED = "You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: declined, with a note. Since then: "


def record_post(entries, since, follows="req_1"):
    acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_2"), None)}, entries=entries, caller=DESIGN)
    acts.kits = lambda label: ("crew",)
    b = cards.record_card(dict(RECORD, follows=follows))
    return acts, plan.card_posted(acts, "swancloud", DESIGN, b, WHERE, since=since)


def test_a_post_following_a_card_the_user_answered_opens_with_what_they_answered_and_what_changed_and_follows_it():
    acts, card = record_post(ANSWERED_ON, ["Revised at 4be21c0: docs(adr): 0019 takes the user's note"])
    assert card == "req_2"
    sent = acts.calls[-1][1]
    said = OPENED + "revised at 4be21c0: docs(adr): 0019 takes the user's note."
    assert sent["summary"].startswith(said + "\n\nA card asked again says what changed.")
    assert sent["context"]["background"].startswith(said) and sent["follows"] == "req_1"
    assert [(e["Act"], e.get("Card"), e.get("State")) for e in acts.emitted] == [("card.post", "req_2", None)]


@pytest.mark.parametrize("since", [None, []])
def test_a_post_following_a_card_the_user_answered_with_nothing_changed_is_recorded_standing_and_not_posted(capsys, since):
    acts, card = record_post(ANSWERED_ON, since)
    assert card is None and acts.calls == [] and acts.names == []
    words = "Not posted: nothing has changed since the user answered req_1 by 2026-10-23 14:02 UTC, so their answer stands"
    assert acts.emitted == [dict(Act="card.post", On=["record/crew/0019"], by=DESIGN, refused=words, Card="req_1", Key=RKEY,
                                 State="stands", label="swancloud")]
    assert capsys.readouterr().err == f"card {RKEY}: {words}\n"
    stood = ANSWERED_ON + [dict(acts.emitted[0], By=DESIGN, Refused=words)]
    assert cards.card_under(stood, RKEY, DESIGN) is None and plan.last_refusal(stood, RKEY) == words


def test_a_later_post_with_something_changed_follows_the_card_whose_answer_stands():
    stood = ANSWERED_ON + [dict(Act="card.post", Key=RKEY, By=DESIGN, Card="req_1", State="stands", Refused="Not posted: …")]
    acts, card = record_post(stood, ["Revised at 9c0ffee: docs(adr): 0019 names the key"], follows=None)
    sent = acts.calls[-1][1]
    assert card == "req_2" and sent["follows"] == "req_1" and sent["summary"].startswith(OPENED + "revised at 9c0ffee")
    assert sent["idempotencyKey"] == "record/crew/0019:2"


def test_a_post_following_no_card_the_user_answered_is_posted_as_built():
    acts, card = record_post([], None, follows=None)
    sent = acts.calls[-1][1]
    assert sent["summary"] == cards.record_card(RECORD)["card"]["summary"] and "follows" not in sent
    acts = Acts({"match_area": (MATCHED, None), "post_request": (POSTED, None)})
    act_post(acts)
    assert acts.calls[-1][1]["summary"] == cards.landing_card(FACTS)["card"]["summary"]


def test_a_change_with_no_card_held_hands_what_changed_to_the_post_it_makes():
    """The record's card was withheld once, its answer standing: the change holds no card, and posts the next revision
    following req_1, saying what changed, or withholds it again when the event gives nothing changed."""
    stood = ANSWERED_ON + [dict(Act="card.post", Key=RKEY, By=DESIGN, Card="req_1", State="stands", Refused="Not posted: …")]
    acts = Acts({"match_area": (MATCHED, None), "post_request": (dict(POSTED, requestId="req_2"), None)}, entries=stood, caller=DESIGN)
    acts.kits = lambda label: ("crew",)
    assert plan.row_card_change(None, "swancloud", DESIGN, cards.record_card, RECORD, "Revised at 4be21c0: x", WHERE, acts,
                                since=["Revised at 4be21c0: x"]) == "req_2"
    assert acts.calls[-1][1]["summary"].startswith(OPENED + "revised at 4be21c0: x.") and acts.calls[-1][1]["follows"] == "req_1"
    acts = Acts(entries=stood, caller=DESIGN)
    acts.kits = lambda label: ("crew",)
    assert plan.row_card_change(None, "swancloud", DESIGN, cards.record_card, RECORD, "x", WHERE, acts, since=[]) is None
    assert acts.calls == [] and acts.emitted[0]["State"] == "stands"


def test_a_close_pending_you_does_not_find_is_recorded_lost_and_a_refused_one_recorded_refused():
    acts = Acts({"get_request": (None, "Not found: request:req_c1.")}, entries=HELD)
    assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome="x", acts=acts) is None
    assert [(e["Act"], e["State"]) for e in acts.emitted] == [("card.close", "lost")]
    acts = Acts({"get_request": ({"status": "pending", "version": 1}, None), "cancel_request": (None, "Too many requests.")}, entries=HELD)
    assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", reason="x", acts=acts) is None
    assert acts.emitted[0]["refused"] == "Pending You refused the close: Too many requests."


def test_a_close_with_no_card_held_closes_nothing_and_says_so(capsys):
    acts = Acts()
    assert plan.row_card_close(None, "wldn", "swb-1-conductor", "land/b1", outcome="x", acts=acts) is None
    assert acts.calls == [] and acts.emitted == []
    assert capsys.readouterr().out == "card land/b1: swb-1-conductor holds none open on this host, so none is closed\n"


PLAN = "%rec: Bolt\n%key: Bolt\n\n%rec: Unit\n%key: Unit\n"
PLAN_AFTER = PLAN + "\nUnit: g-one\nRepo: switchboard-kit\nIntent: One unit.\n"


# ------------------------------------------------------------------------------------ the port a session takes
# plan.session_env: the environment a card's session starts plannotator in, so it takes the first free port of a
# range wherever crew runs (card-sessions), read against plannotator 0.28.26's reading of PLANNOTATOR_PORT.

def test_a_session_with_no_port_named_takes_crews_range():
    assert plan.session_env({})["PLANNOTATOR_PORT"] == "19432-19451" == plan.CARD_PORTS


def test_a_range_the_environment_names_is_kept():
    assert plan.session_env({"PLANNOTATOR_PORT": "19440-19460"})["PLANNOTATOR_PORT"] == "19440-19460"


@pytest.mark.parametrize("named", ["19432", "abc", "19451-19432", "0-10", "19432-70000", ""])
def test_one_port_or_one_plannotator_cant_read_gives_crews_range(named):
    assert plan.session_env({"PLANNOTATOR_PORT": named})["PLANNOTATOR_PORT"] == "19432-19451"


@pytest.mark.parametrize("environ", [{}, {"PLANNOTATOR_PORT": "19440-19460"},
                                     {"PLANNOTATOR_REMOTE": "0", "PLANNOTATOR_SKIP_BROWSER_OPEN": "0"}])
def test_every_session_is_remote_and_opens_no_browser(environ):
    env = plan.session_env(environ)
    assert env["PLANNOTATOR_REMOTE"] == "1" and env["PLANNOTATOR_SKIP_BROWSER_OPEN"] == "1"


def test_the_rest_of_the_environment_passes_through_and_the_one_given_is_not_changed():
    environ = {"PLANNOTATOR_URL_HOST": "auto", "PATH": "/bin", "PLANNOTATOR_PORT": "19432"}
    env = plan.session_env(environ)
    assert env["PLANNOTATOR_URL_HOST"] == "auto" and env["PATH"] == "/bin"
    assert environ == {"PLANNOTATOR_URL_HOST": "auto", "PATH": "/bin", "PLANNOTATOR_PORT": "19432"}


# --------------------------------------------------------------------------------- a session's end, swept
# plan.end_session, and crew card wait on a batch whose card's close ends its session: the key's folder swept whether
# or not the partition's cards folder for it exists, a folder another end swept first, as the card hook's crew card end
# or the rail's sweep may while this one reads plannotator's list, swept as empty and never raised.

class TestSessionEnd:
    S = {"pid": 42, "document": "/c/00-summary.md", "url": "http://chuck-herdr-alpha.ts.swancloud.net:19432",
         "started": "2026-10-23T10:00:00Z"}

    def recorded(self, monkeypatch, tmp_path, key):
        """The key's session recorded under the partition's cards folder, and another end sweeping its folder while
        this one reads plannotator's list, which still lists the session, whose pid has gone by its signal."""
        d = tmp_path / "wldn" / key
        d.mkdir(parents=True)
        (d / "session.json").write_text(json.dumps(self.S))
        (tmp_path / "wldn" / "proposal").mkdir()  # another key's folder, so the partition's stays

        def listed():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()
            return {42: {"target": self.S["document"]}}, None

        def kill(pid, sig):
            raise ProcessLookupError(pid)
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        monkeypatch.setattr(plan, "plannotator_sessions", listed)
        monkeypatch.setattr(plan.os, "kill", kill)
        return d

    def test_a_folder_swept_by_another_end_meanwhile_is_swept_as_empty_and_its_end_said(self, monkeypatch, tmp_path):
        d = self.recorded(monkeypatch, tmp_path, "batch/3")
        assert plan.end_session("wldn", "batch/3") == ("batch/3's session had already ended, and batch/3 is forgotten", False)
        assert not d.parent.exists() and (tmp_path / "wldn" / "proposal").is_dir()

    def test_a_key_with_no_folder_ends_nothing_and_makes_none(self, monkeypatch, tmp_path):
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        assert plan.end_session("wldn", "proposal/9") == ("no session was running for proposal/9", False)
        assert not (tmp_path / "wldn").exists()

    def test_a_batch_wait_returns_once_its_card_is_closed_and_its_session_ended_though_another_end_swept_its_folder(
            self, monkeypatch, tmp_path, capsys):
        d = self.recorded(monkeypatch, tmp_path, "batch/3")
        sent = {"status": "answered", "turn": "agent", "version": 2, "answer": {"note": {"text": "Read."}}}
        acts = Acts({"get_request": (sent, None)}, [post("batch/3", "wldn-planner", "req_b3", On=["batch/3"])])
        acts.end = lambda label, key: plan.end_session(label, key)[0]
        fleet = {"partitions": {"wldn": {"label": "wldn", "machine": "chuck-herdr-alpha"}}, "teams": {}, "hosts": {}}
        plan.batch_wait(fleet, "wldn", "batch/3", d, acts)
        assert [e["Act"] for e in acts.emitted] == ["card.close"]
        assert capsys.readouterr().out.splitlines() == [
            "batch/3: sent back on its card, with a note:", "Read.", "card batch/3: req_b3 closed",
            "batch/3's session had already ended, and batch/3 is forgotten"]
        assert not d.parent.exists()


# ------------------------------------------------------------------------------- crew card wait on a bolt's row

class TestLandWait:
    """crew card wait land/<bolt> (card-sessions "A wait on a landing card starts its reading when none runs"): while
    the bolt is a row of its kit's landings card that can land, its reading started on its team's host and the kit's
    card raised on the main machine to carry its link; refused while it is no row, and for the kit's own key."""
    FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "chuck-herdr-alpha", "teams": ["swb-1"]}},
             "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": "chuck-herdr-alpha",
                                 "kit": {"name": "switchboard-kit", "repo": "WilldanGroup/switchboard-kit", "main": "/kit/main", "dir": "/kit"}}},
             "hosts": {}}
    LINK = "http://chuck-herdr-alpha.ts.swancloud.net:19432"

    def wait(self, monkeypatch, tmp_path, row, key="land/y"):
        import argparse
        handed = []
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        monkeypatch.setattr(crew, "this_host", lambda: "chuck-herdr-alpha")
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, plan.Rec("Bolt", [("Bolt", "y"), ("Repo", "switchboard-kit")]),
                                                                           self.FLEET["teams"]["swb-1"]))
        monkeypatch.setattr(plan, "land_read", lambda fleet, label, p, b, t: (row, None) if row else (None, "unit a has not merged"))
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None: handed.append((kit, note)))

        def opened(fleet, label, key, facts):  # the reading started, and the user's notes in it at once
            d = tmp_path / label / key
            d.mkdir(parents=True, exist_ok=True)
            (d / "session.json").write_text(json.dumps({"pid": 42, "document": "/c/00-y.md", "url": self.LINK, "started": "2026-10-23T10:00:00Z"}))
            (d / "result.json").write_text(json.dumps({"decision": "annotated", "feedback": "y: say what the zone is."}))
            return self.LINK, False, True
        monkeypatch.setattr(plan, "reading_open", opened)
        plan.card_wait(self.FLEET, argparse.Namespace(key=key, unit=None, label="wldn", sub="wait"))
        return handed

    def test_a_wait_on_a_row_starts_its_reading_and_the_kits_card_is_raised_to_carry_its_link(self, monkeypatch, tmp_path, capsys):
        row = dict(bolt="y", box=True, facts=dict(bolt="y", kit="switchboard-kit", head="a" * 40))
        assert self.wait(monkeypatch, tmp_path, row) == [("switchboard-kit", "y: Its reading is open again at a new link")]
        assert capsys.readouterr().out == (f"{self.LINK}\nland/y: notes from its reading, as notes on the landing card:\n"
                                           "y: say what the zone is.\n")

    def test_a_wait_on_a_bolt_that_is_no_row_is_refused_and_starts_nothing(self, monkeypatch, tmp_path):
        with pytest.raises(crew.Refusal, match="^no session was started for card land/y, and y is no row of its kit's landings card$"):
            self.wait(monkeypatch, tmp_path, None)
        assert not (tmp_path / "wldn" / "land/y").exists()

    def test_a_wait_on_the_kits_own_card_is_refused(self, monkeypatch, tmp_path):
        with pytest.raises(crew.Refusal, match="^land/switchboard-kit is switchboard-kit's landings card, wldn-ops's"):
            self.wait(monkeypatch, tmp_path, None, key="land/switchboard-kit")


# ------------------------------------------------------------------------- crew card read of a kit's landings card

def test_a_sent_landings_card_reads_the_ticked_bolts_in_its_order_and_the_submit_that_lands_them():
    """rail-cards "Landing approved": a and c ticked, b cleared."""
    heads = plan.card_heads("a@abc1234 b@abc1234 c@def5678")
    got = {"status": "answered", "turn": "agent", "answer": {"choiceIds": ["land:c", "land:a"], "note": {"text": "c first"}}}
    assert plan.landing_lines("swancloud", got, heads) == [
        "  to land, in the card's order: a and c", "  lands them: crew bolt submit a c --label swancloud"]
    assert "  note: c first" in cards.answer_lines("land/crew", "req_k1", got)


def test_a_lone_row_approved_lands_it_and_a_send_ticking_none_lands_nothing():
    one = plan.card_heads("y@abc1234")
    approved = {"status": "answered", "turn": "agent", "answer": {"approved": True}}
    assert plan.landing_lines("wldn", approved, one)[-1] == "  lands them: crew bolt submit y --label wldn"
    none = {"status": "answered", "turn": "agent", "answer": {"choiceIds": []}}
    assert plan.landing_lines("wldn", none, one) == ["  no bolt ticked: nothing lands"]
    assert plan.landing_lines("wldn", {"status": "pending", "turn": "you"}, one) == []
