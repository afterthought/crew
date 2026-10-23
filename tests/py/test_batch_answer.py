"""A batch answered by the user's own words in a main-level pane (review-batches; briefs.12; record 0031 as amended
2026-10-22): plan.pane_answer_refusal, which refuses a caller who is not the planner or the operator, a batch the run
record does not hold, one answered already or waiting on nothing, and words crew does not read as the user's; the act,
plan.batch_answer, on a stand-in for what it reaches, recording one batch.answer with no words in it, closing the
planner's card held on this host with them and telling the planner them when the operator ran it; and the planner's
wait on the batch, plan.batch_wait, which ends on the answer. Reading the words in a transcript is test_transcript's;
the answer's effect on the rail, the board and the landing, test_batches' and test_rail's."""
import argparse

import pytest

import transcript

import plan

FLEET = {"partitions": {"swancloud": {"label": "swancloud", "machine": "deneb", "teams": ["crw-1"]}},
         "teams": {"crw-1": {"name": "crw-1", "label": "swancloud", "machine": "deneb"}}, "hosts": {}}
WORDS = "Batch 13 is fine, approve it"


def heard(asserted_by="user", grade="verified", uuid="u-13", reason=None):
    """A verdict on the words, as transcript.check gives it."""
    if grade == "unverified":
        return transcript.unverified(reason)
    return transcript.Verdict(grade, raw=b'{"type": "user"}', n=4, value={"uuid": uuid} if uuid else {},
                              asserted_by=asserted_by if grade == "verified" else "unknown")


USER = heard()


def batch(n, minutes=0, units="x1:crw-1@aaa1"):
    return {"Act": "review.batch", "Batch": str(n), "Units": units, "At": f"2026-10-22T19:{minutes:02d}:00Z", "On": []}


def posted(key, card, host="deneb", by="swancloud-planner", minutes=1):
    return {"Act": "card.post", "Key": key, "Card": card, "By": by, "Host": host, "At": f"2026-10-22T19:{minutes:02d}:00Z", "On": [key]}


def answered(n, by="swancloud-planner", at="2026-10-22T20:17:04Z"):
    return {"Act": "batch.answer", "On": [f"batch/{n}"], "Key": f"batch/{n}", "Batch": str(n), "Chars": "28", "By": by, "At": at,
            "From": [f"session/s-1/u-{n}"]}


HELD = [batch(13), posted("batch/13", "req_13")]


class TestRefusal:
    def test_the_users_words_in_the_planners_or_the_operators_pane_answer_the_batch(self):
        assert plan.pane_answer_refusal(13, HELD, USER, "planner") is None
        assert plan.pane_answer_refusal(13, HELD, USER, "operator") is None
        assert plan.pane_answer_refusal(13, HELD, heard(uuid=None), "planner") is None

    @pytest.mark.parametrize("kind", ["conductor", "design", "main-ops", "dispatcher", "team", "user", "other"])
    def test_any_other_caller_is_refused(self, kind):
        assert plan.pane_answer_refusal(13, HELD, USER, kind) == (
            "crew records no answer of batch 13: only the planner and the operator record a batch the user answered in their "
            "pane, in the user's own words; the user answers a batch on its card or in one of those two panes")

    def test_a_batch_the_run_record_does_not_hold_is_refused(self):
        assert plan.pane_answer_refusal(14, HELD, USER, "planner") == "crew records no answer of batch 14: the run record holds no batch 14"

    def test_a_batch_answered_on_its_card_or_in_a_pane_is_refused_saying_how(self):
        tapped = HELD + [{"Act": "card.close", "Key": "batch/13", "Card": "req_13", "State": "closed", "At": "2026-10-22T19:30:00Z", "On": []}]
        assert plan.pane_answer_refusal(13, tapped, USER, "planner") == (
            "crew records no answer of batch 13: batch 13 was answered on its card or in its reading session already")
        assert plan.pane_answer_refusal(13, HELD + [answered(13, "swancloud-operator")], USER, "planner") == (
            "crew records no answer of batch 13: batch 13 was answered in swancloud-operator's pane at 20:17Z already")

    def test_a_batch_that_waits_on_nothing_is_refused_with_its_words(self):
        landed = {"Act": "bolt.land", "On": ["bolt/b", "unit/x1"], "At": "2026-10-22T19:40:00Z"}
        assert plan.pane_answer_refusal(13, HELD + [landed], USER, "planner") == (
            "crew records no answer of batch 13: its batch waits on nothing: x1 has landed")

    @pytest.mark.parametrize("v, words", [
        (heard(grade="refused"), "the words are not in a record your session received; only the user's own words answer a "
                                 "batch, quoted as they wrote them in your pane, never your own"),
        (heard("agent:swancloud-operator"), "the words are swancloud-operator's, passed on with crew tell, and not the user's; "
                                            "tell swancloud-operator that the user answers a batch on its card or in your pane"),
        (heard("crew"), "the words are crew's own message, not the user's"),
        (heard("tool"), "the words are a tool's output, not the user's"),
        (heard(grade="found"), "the words are in a record of your transcript crew can't read as anyone's, so it can't tell they are the user's"),
        (heard(grade="unverified", reason="no transcript for session s-9"),
         "crew can't read your session's transcript, so it can't tell the words are the user's: no transcript for session s-9")])
    def test_words_crew_does_not_read_as_the_users_are_refused_naming_who_said_them(self, v, words):
        assert plan.pane_answer_refusal(13, HELD, v, "planner") == f"crew records no answer of batch 13: {words}"


class Py:
    """One session with Pending You: each tool answered from the acts' answers as (got, words)."""

    def __init__(self, acts):
        self.acts = acts

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def answer(self, tool, args):
        self.acts.calls.append((tool, args))
        return self.acts.answers.get(tool, ({"ok": True}, None))


class Acts:
    """A stand-in for what crew card answer and the batch's wait reach: Pending You, this host's run record and the
    partition's whole, the caller's transcript, a tell and the batch's reading session. rounds, when given, are this
    host's entries as each read finds them, the last read again once they run out."""

    def __init__(self, caller="swancloud-planner", entries=HELD, verdict=USER, card=None, told=True, rounds=None, whole=None, session=True):
        self.who, self.held, self.verdict, self.told_ok, self.session = caller, list(entries), verdict, told, session
        self.answers = {"get_request": (card or {"status": "pending", "turn": "you", "version": 1}, None)}
        self.rounds, self.whole = rounds, whole
        self.calls, self.emitted, self.told, self.ended = [], [], [], []

    def bridge(self, name, later, held=None):
        return Py(self)

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act, On=on, label=label))
        return "eid"

    def entries(self, label):
        if self.rounds:
            return self.rounds.pop(0) if len(self.rounds) > 1 else self.rounds[0]
        return self.held + [e for e in self.emitted if e["Act"] == "card.close"]

    def partition(self, label):
        return self.held if self.whole is None else self.whole

    def heard(self, words):
        return self.verdict, "s-1"

    def tell(self, name, text):
        self.told.append((name, text))
        return self.told_ok

    def end(self, label, key):
        if key in self.ended or not self.session:
            return None
        self.ended.append(key)
        return f"ended {key}'s session, plannotator pid 42"

    def release_preview(self, label, key):
        return None

    def host(self):
        return "deneb"

    def caller(self):
        return self.who


def answer(acts, key="batch/13", words=WORDS, label=None):
    return plan.batch_answer(FLEET, argparse.Namespace(key=key, excerpt=words, label=label), acts)


class TestAnswer:
    def test_the_planners_answer_is_one_entry_with_no_words_and_closes_its_card_held_here_with_them(self, capsys):
        acts = Acts(card={"status": "answered", "turn": "agent", "version": 3})
        answer(acts)
        entry, close = acts.emitted
        assert entry == dict(Act="batch.answer", On=["batch/13"], frm=["session/s-1/u-13"], Key="batch/13", Batch="13", Chars=len(WORDS),
                             label="swancloud")
        assert close == dict(Act="card.close", On=["batch/13"], by="swancloud-planner", Card="req_13", Key="batch/13", State="closed",
                             Outcome="Answered in swancloud-planner's pane", label="swancloud")
        assert not any(WORDS in str(e) for e in acts.emitted)
        assert acts.calls[1] == ("ack_answer", {"requestId": "req_13", "name": "swancloud-planner", "expectedVersion": 3,
                                                "outcome": f"Answered in swancloud-planner's pane: {WORDS}"})
        assert acts.told == [] and acts.ended == ["batch/13"]
        assert capsys.readouterr().out.splitlines() == [
            "batch 13 answered in swancloud-planner's pane:", WORDS, "card batch/13: req_13 closed", "ended batch/13's session, plannotator pid 42"]

    def test_a_card_still_waiting_on_the_user_is_withdrawn_with_the_words(self):
        acts = Acts()
        answer(acts)
        assert acts.calls[1] == ("cancel_request", {"requestId": "req_13", "name": "swancloud-planner",
                                                    "reason": f"Answered in swancloud-planner's pane: {WORDS}"})
        assert acts.emitted[1]["Outcome"] == "Answered in swancloud-planner's pane"

    def test_a_record_with_no_uuid_is_named_by_its_lines_hash(self):
        acts = Acts(verdict=heard(uuid=None))
        answer(acts)
        assert acts.emitted[0]["frm"] == [f"session/s-1/line-{heard(uuid=None).line_hash()[:16]}"]

    def test_the_operators_answer_tells_the_planner_the_words_to_send_on(self, capsys):
        acts = Acts(caller="swancloud-operator")
        answer(acts)
        assert acts.emitted[0]["Act"] == "batch.answer" and acts.emitted[1]["Outcome"] == "Answered in swancloud-operator's pane"
        assert acts.told == [("swancloud-planner", f'Batch 13 was answered in swancloud-operator\'s pane: "{WORDS}". Send each unit\'s '
                                                   "part to its conductor, as you send a batch's notes.")]
        out = capsys.readouterr().out.splitlines()
        assert out[0] == "batch 13 answered in swancloud-operator's pane" and WORDS not in out[0]
        assert out[-1] == "swancloud-planner was told the user's words, to send each unit's part to its conductor"

    def test_a_tell_that_fails_is_said_and_the_answer_stands(self, capsys):
        acts = Acts(caller="swancloud-operator", told=False)
        answer(acts)
        assert [e["Act"] for e in acts.emitted] == ["batch.answer", "card.close"]
        assert capsys.readouterr().out.splitlines()[-1] == (
            "crew could not tell swancloud-planner the user's words, and batch 13 stands answered: tell swancloud-planner them "
            "yourself with crew tell, as the user wrote them")

    def test_with_no_card_held_here_the_host_it_was_posted_from_is_named_whose_sweep_closes_it(self, capsys):
        acts = Acts(entries=[batch(13)], whole=[batch(13), posted("batch/13", "req_13", host="mac-studio")], session=False)
        answer(acts)
        assert [e["Act"] for e in acts.emitted] == ["batch.answer"] and acts.calls == []
        assert capsys.readouterr().out.splitlines()[-2:] == [
            "card batch/13: swancloud-planner holds none open on this host, so none is closed",
            "card batch/13: its card was posted from mac-studio, whose rail's sweep closes it answered"]

    @pytest.mark.parametrize("acts, why", [
        (Acts(caller="crw-1-conductor"), "only the planner and the operator record"),
        (Acts(verdict=heard("agent:swancloud-operator")), "the words are swancloud-operator's"),
        (Acts(entries=HELD + [answered(13)]), "batch 13 was answered in swancloud-planner's pane at 20:17Z already")])
    def test_a_refusal_records_nothing_and_closes_nothing(self, acts, why):
        with pytest.raises(plan.Refusal, match=why):
            answer(acts)
        assert acts.emitted == [] and acts.calls == [] and acts.told == []

    @pytest.mark.parametrize("key", ["batch/13-1", "land/y", "proposal/4", "batch/x"])
    def test_any_key_but_a_batchs_is_refused_naming_batch_n(self, key):
        acts = Acts()
        with pytest.raises(plan.Refusal, match="under its key batch/<n>"):
            answer(acts, key=key)
        assert acts.emitted == []

    def test_a_label_not_the_callers_is_refused(self):
        with pytest.raises(plan.Refusal, match="swancloud-planner answers swancloud's batches, not wldn's"):
            answer(Acts(), label="wldn")


class TestWait:
    def test_the_planners_wait_ends_once_the_batch_is_answered_in_a_pane_and_closes_the_card_it_holds(self, tmp_path, monkeypatch, capsys):
        """review-batches, "The planner's wait was running": the operator answers batch 16 while the wait runs."""
        monkeypatch.setattr(plan.time, "sleep", lambda s: None)
        held = [batch(16), posted("batch/16", "req_16")]
        acts = Acts(entries=held, rounds=[held, held, held + [answered(16, "swancloud-operator")]])
        plan.batch_wait(FLEET, "swancloud", "batch/16", tmp_path, acts)
        assert acts.emitted == [dict(Act="card.close", On=["batch/16"], by="swancloud-planner", Card="req_16", Key="batch/16",
                                     State="withdrawn", Outcome="Answered in swancloud-operator's pane at 20:17Z", label="swancloud")]
        assert acts.calls[-1] == ("cancel_request", {"requestId": "req_16", "name": "swancloud-planner",
                                                     "reason": "Answered in swancloud-operator's pane at 20:17Z"})
        out = capsys.readouterr().out.splitlines()
        assert out[0] == "batch/16: answered in swancloud-operator's pane at 20:17Z"
        assert out[1:] == ["card batch/16: req_16 withdrawn", "ended batch/16's session, plannotator pid 42"]
