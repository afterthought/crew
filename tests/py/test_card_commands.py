"""crew card post, change, close and read (the rail-cards spec, briefs.16, ADR 0005 as amended 2026-10-12): the
decisions in plugin/lib/cards.py, each on plain facts. The card a key names in the run record; what crew sets on a
card and refuses the agent setting; a git remote as Pending You files by it; the area match_area chose, and the kit's
area to make; a tool's reply read as Pending You's CLI reads it, its refusal in Pending You's words, and the bridge's
own error; and what `crew card read` prints. The bridge itself, and every command's wiring, are t-card-commands'."""
import json

import pytest

import cards
import crew


def post(key, by, card, at="2026-10-12T10:00:00Z", **more):
    return dict(Act="card.post", Key=key, By=by, Card=card, At=at, **more)


def close(card, by="swb-1-conductor", **more):
    return dict(Act="card.close", Card=card, By=by, **more)


# --------------------------------------------------------------------------------------- the card a key names

def test_the_card_a_key_names_is_the_agents_newest_post_under_it():
    entries = [post("verify/v1/20261012-1000", "swb-1-conductor", "req_a"),
               post("verify/v1/20261012-1000", "swb-1-conductor", "req_b")]
    assert cards.card_under(entries, "verify/v1/20261012-1000", "swb-1-conductor") == "req_b"


def test_a_closed_card_is_no_longer_held():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"), close("req_a")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") is None


def test_another_agents_card_under_the_same_key_is_not_this_ones():
    entries = [post("verify/v1/20261012-1000", "swb-2-conductor", "req_a")]
    assert cards.card_under(entries, "verify/v1/20261012-1000", "swb-1-conductor") is None


def test_a_refused_post_or_close_holds_nothing_and_closes_nothing():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"),
               post("land/b1/abc1234", "swb-1-conductor", None, Refused="Pending You refused post_request: x"),
               close("req_a", Refused="Pending You refused cancel_request: y")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") == "req_a"


def test_a_close_of_an_older_card_leaves_the_newer_held():
    entries = [post("land/b1/abc1234", "swb-1-conductor", "req_a"), post("land/b1/abc1234", "swb-1-conductor", "req_b"),
               close("req_a")]
    assert cards.card_under(entries, "land/b1/abc1234", "swb-1-conductor") == "req_b"


# ------------------------------------------------------------------------------------- what the agent gives

def test_a_card_is_one_json_object():
    assert cards.given('{"kind": "choice", "title": "Which?"}', "card", cards.CREW_FIELDS) == {"kind": "choice", "title": "Which?"}


@pytest.mark.parametrize("text, said", [("[1, 2]", "the card on standard input is not a JSON object"),
                                         ("{kind", "crew could not read the card on standard input as JSON")])
def test_a_card_that_is_not_an_object_is_refused(text, said):
    with pytest.raises(crew.Refusal, match=said):
        cards.given(text, "card", cards.CREW_FIELDS)


def test_a_card_that_sets_crews_fields_is_refused_naming_them():
    with pytest.raises(crew.Refusal, match="the card gives areaId, session, which crew sets itself: leave them out"):
        cards.given(json.dumps({"title": "x", "areaId": "prj_mine", "session": {}}), "card", cards.CREW_FIELDS)


def test_a_change_that_sets_the_version_is_refused():
    with pytest.raises(crew.Refusal, match="the change gives expectedVersion, which crew sets itself: leave it out"):
        cards.given('{"expectedVersion": 3, "changeNote": "x"}', "change", cards.CHANGE_FIELDS)


def test_crew_sets_the_key_the_session_and_the_area():
    card = {"kind": "choice", "title": "Which fix for v1?", "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]}
    got = cards.post_args(card, "verify/v1/20261012-1000", "swb-1-conductor", "chuck-herdr-alpha", "/w/places/v1", "prj_kit")
    assert got == dict(card, idempotencyKey="verify/v1/20261012-1000", areaId="prj_kit",
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


# ----------------------------------------------------------------------------------------- what read prints

def test_a_card_waiting_on_the_user():
    got = {"requestId": "req_1", "status": "pending", "turn": "you", "version": 1, "url": "https://www.pendingyou.com/app/r/req_1"}
    assert cards.answer_lines("verify/v1/s", "req_1", got) == [
        "card verify/v1/s: req_1, pending, waiting on the user", "  https://www.pendingyou.com/app/r/req_1"]


def test_an_answer_with_the_users_words():
    got = {"status": "answered", "turn": "agent", "answer": {"choiceIds": ["fix"], "note": {"text": "Both, please.", "via": "voice"}},
           "messages": [{"from": "you", "body": "And add a test."}, {"from": "you"}, "not a message"]}
    assert cards.answer_lines("verify/v1/s", "req_1", got) == [
        "card verify/v1/s: req_1, answered, your turn: the user has answered", "  picked: fix", "  note: Both, please.",
        "  you: And add a test."]


def test_an_approval_and_a_grouped_answer():
    got = {"status": "answered", "turn": "agent",
           "answer": {"approved": False, "answers": {"plan": {"approved": True}, "units-1": {"choiceIds": ["u1", "u2"]}}}}
    assert cards.answer_lines("proposal/4", "req_1", got)[1:] == ["  approved: no", "  plan: approved", "  units-1: u1, u2"]


def test_an_answer_is_shown_only_on_the_agents_turn():
    got = {"status": "pending", "turn": "you", "answer": {"choiceIds": ["fix"]}}
    assert cards.answer_lines("verify/v1/s", "req_1", got) == ["card verify/v1/s: req_1, pending, waiting on the user"]


def test_what_the_reply_leaves_out_is_left_out():
    assert cards.answer_lines("land/b1/abc1234", "req_1", {}) == ["card land/b1/abc1234: req_1"]
