"""A stage's prompt is taken or sent again (teams.15): crew.send_taken on a pane that behaves as Claude's does under
herdr, as the stub herdr does: a prompt that lands before the agent is ready, or whose Enter is lost, is left typed in
its input and never reaches its transcript; ctrl+c clears the input. The clock is the pane's, so a case waits on
nothing. That a stage's prompt goes through this exchange, and what crew says of one never taken, are the journey's
(t-journey-slots)."""
import json
import types

import pytest

import crew


class Pane:
    """An agent's pane: its status, the prompts its transcript holds, what is left typed, and what crew did to it."""

    def __init__(self, status="idle", leave=0, then=None):
        self.status, self.leave, self.then = status, leave, then
        self.host, self.sid, self.transcript, self.typed, self.did, self.clock = "chuck-herdr-alpha", "s1", [], "", "", 0.0

    def reading(self):
        return (None, False, None, None) if self.status is None else (self.status, self.status == "blocked", self.sid, None)

    def agent(self):
        return ({"agent_status": self.status, "agent_session": {"value": self.sid}}, None) if self.status else (None, None)

    def end(self, sid):
        return {"size": len(self.transcript)}

    def received(self, sid, size, text):
        return {"received": text in self.transcript[int(size):]}

    def herdr(self, verb, name, arg):
        if verb == "send-keys":
            self.did, self.typed = self.did + "C", ""
            return types.SimpleNamespace(returncode=0, stderr="")
        if self.status == "blocked":
            return types.SimpleNamespace(returncode=1, stderr=json.dumps({"error": {"code": "agent_blocked", "message": "blocked"}}))
        self.did += "P"
        if self.leave:
            self.leave, self.typed = self.leave - 1, self.typed + arg
            self.status = self.then or self.status
        else:
            self.transcript.append(self.typed + arg)
            self.typed = ""
        return types.SimpleNamespace(returncode=0, stderr="")

    def unanswered(self, r):
        return None

    def now(self):
        return self.clock

    def sleep(self, seconds):
        self.clock += seconds


def send(pane, text="/opsx:apply a"):
    return crew.send_taken({}, "swb-1-unit-1", text, pane=pane)


def test_a_prompt_taken_at_once_is_sent_once_and_nothing_is_pressed():
    pane = Pane()
    assert send(pane) == ("taken", 1)
    assert (pane.did, pane.transcript) == ("P", ["/opsx:apply a"])


def test_a_prompt_left_typed_is_cleared_with_one_ctrl_c_and_sent_once_more_received_alone():
    pane = Pane(leave=1)
    assert send(pane, "Fix: The banner flickers.") == ("taken", 2)
    assert (pane.did, pane.transcript, pane.typed) == ("PCP", ["Fix: The banner flickers."], "")


def test_a_prompt_not_taken_twice_is_cleared_twice_and_nothing_is_left_typed():
    pane = Pane(leave=2)
    assert send(pane) == ("never", "sent twice")
    assert (pane.did, pane.transcript, pane.typed) == ("PCPC", [], "")


def test_an_agent_waiting_on_a_question_throughout_is_never_sent_it():
    pane = Pane(status="blocked")
    assert send(pane) == ("never", "as it was waiting on a question in its pane")
    assert pane.did == ""


def test_an_agent_not_up_is_never_sent_it():
    assert send(Pane(status=None)) == ("never", "as it was not up")


def test_an_agent_that_went_to_work_with_no_record_of_its_prompt_is_neither_pressed_nor_sent_it_again():
    pane = Pane(leave=1, then="working")
    assert send(pane) == ("unread", "it went to work, and its transcript showed no prompt received 60 seconds on, so it may have taken it")
    assert pane.did == "P"


def test_a_limit_crew_cannot_read_is_refused_before_anything_is_typed(monkeypatch):
    monkeypatch.setenv("CREW_TAKEN_WITHIN", "0")
    crew.taken_within.cache_clear()
    pane = Pane()
    try:
        with pytest.raises(crew.Refusal, match='CREW_TAKEN_WITHIN is a whole number of seconds above 0, not "0"'):
            send(pane)
    finally:
        crew.taken_within.cache_clear()
    assert pane.did == ""
