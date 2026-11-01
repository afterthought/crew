"""crew send (briefs.10, record 0035, the operator-agent spec "Anything sent to another partition reaches its operator",
the run-record spec "A send is one entry in the receiving partition's record"): crew.send_door for where a
send goes, from the teams file alone, and crew.send for what it types and records. That the command reaches the
operator's pane on its host is the main level's journey's (t-journey-main)."""
import pytest

import crew
import facts
import record

FLEET = {**facts.FLEET, "partitions": {**facts.FLEET["partitions"],
                                       "swancloud": {"label": "swancloud", "machine": "mac-studio"}},
         "teams": {**facts.FLEET["teams"], "crw-5": {"name": "crw-5", "label": "swancloud", "machine": "mac-studio"}}}


class TestDoor:
    """A partition's label resolves to its operator; nothing else is placed."""

    def test_a_partition_goes_to_its_operator_by_its_label(self):
        assert crew.send_door(FLEET, "wldn", "user@mac-studio") == ("wldn", "wldn-operator")

    @pytest.mark.parametrize("name", ["swb-1", "swb-2", "crw-5"])
    def test_a_teams_name_from_before_teams_left_is_refused_naming_the_partitions(self, name):
        """operator-agent "A name crew does not know"."""
        with pytest.raises(crew.Refusal, match=rf"^crew send sends to a partition by its label, not '{name}': partitions swancloud wldn$"):
            crew.send_door(FLEET, name, "swancloud-planner")

    def test_an_agents_name_is_refused_naming_the_partitions(self):
        with pytest.raises(crew.Refusal, match=r"crew send sends to a partition by its label, not 'wldn-planner': "
                                               r"partitions swancloud wldn"):
            crew.send_door(FLEET, "wldn-planner", "swancloud-planner")

    def test_an_unknown_name_is_refused(self):
        with pytest.raises(crew.Refusal, match="not 'nosuch'"):
            crew.send_door(FLEET, "nosuch", None)

    def test_the_door_sending_to_its_own_label_is_refused(self):
        with pytest.raises(crew.Refusal, match=r"you are wldn's door: carry it on with `crew tell <agent>`"):
            crew.send_door(FLEET, "wldn", "wldn-operator")

    def test_another_partitions_operator_may_send(self):
        assert crew.send_door(FLEET, "wldn", "swancloud-operator") == ("wldn", "wldn-operator")


class TestSend:
    """A send is a tell to the door, the addressee before the text, and one `send` entry in the receiving partition's
    record holding its length and never its text; a send that typed nothing records nothing."""

    @pytest.fixture
    def acts(self, monkeypatch):
        told, emitted, sent = [], [], {"ok": True}
        monkeypatch.setenv("CREW_AGENT", "swancloud-planner")
        monkeypatch.setattr(crew, "tell", lambda fleet, name, text, **kw: told.append((name, text, kw)) or sent["ok"])
        monkeypatch.setattr(record, "emit", lambda label, act, on=(), **f: emitted.append((label, act, list(on), f)))
        return told, emitted, sent

    def test_a_delivered_send_is_a_tell_to_the_door_and_one_send_entry(self, acts):
        told, emitted, _ = acts
        text = "The zone check fails on tenants with no region"
        assert crew.send(FLEET, "wldn", text) is True
        assert told == [("wldn-operator", f"(sent to wldn) {text}", {"record": False, "sender": "swancloud-planner", "ask": "send", "reading": None})]
        assert emitted == [("wldn", "send", ["agent/wldn-operator"], {"why": "send wldn", "Chars": 46})]
        assert text not in repr(emitted)

    def test_a_send_that_typed_nothing_records_nothing(self, acts):
        told, emitted, sent = acts
        sent["ok"] = False
        assert crew.send(FLEET, "wldn", "hello") is False
        assert len(told) == 1 and emitted == []

    def test_a_refused_send_types_and_records_nothing(self, acts):
        told, emitted, _ = acts
        with pytest.raises(crew.Refusal):
            crew.send(FLEET, "swb-1", "hello")
        assert told == [] and emitted == []
