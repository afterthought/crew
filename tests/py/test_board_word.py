"""A word from the board (record 0038 §3, the board-page spec "A word reaches its agent as the user's tell from the
board, naming the item", "A word not of the board's form is refused" and "A word from the board answers nothing"):
crew.board_word for the check of what the board's listener pipes, crew.board_tell for the tell it makes, and the
refusals of a landing, a batch's answer and a record settled on words that came from the board. That the command
reaches the planner's pane on its host is the main level's journey's (t-journey-main)."""
import getpass
import json

import pytest

import crew
import facts

FLEET = {**facts.FLEET, "partitions": {**facts.FLEET["partitions"], "swancloud": {"label": "swancloud", "machine": "mac-studio"}},
         "teams": {**facts.FLEET["teams"], "crw-5": {"name": "crw-5", "label": "swancloud", "machine": "mac-studio"}}}


def word(**f):
    return json.dumps({"label": "wldn", "key": "unit:a", "to": "swb-1-conductor", "text": "Keep the zone check", **f})


class TestTell:
    """A word is told its agent as the user's from the board, the item named before the text."""

    @pytest.fixture
    def told(self, monkeypatch):
        told, sent = [], {"ok": True}
        monkeypatch.setattr(getpass, "getuser", lambda: "chuck")
        monkeypatch.setattr(crew, "tell", lambda fleet, name, text, **kw: told.append((name, text, kw)) or sent["ok"])
        return told, sent

    def test_a_word_on_a_unit_is_told_its_conductor_from_the_board_naming_the_item(self, told, capsys):
        """board-page "A word on a unit"."""
        told, _ = told
        assert crew.board_tell(FLEET, word()) is True
        assert told == [("swb-1-conductor", "(on unit a) Keep the zone check", {"sender": "chuck@board"})]
        assert len(told[0][1]) == 31 and capsys.readouterr().out == "sent to swb-1-conductor\n"

    def test_a_word_on_a_proposal_goes_to_the_planner_and_one_on_a_deploy_to_main_level_ops(self, told):
        assert crew.board_word(FLEET, word(key="proposal:4", to="wldn-planner")) == ("wldn-planner", "(on proposal 4) Keep the zone check")
        key = "deploy:mac-studio/" + "a" * 40 + "/2026-10-12T10:06:00Z"
        assert crew.board_word(FLEET, word(key=key, to="wldn-ops"))[1].startswith(f"(on deploy {key[7:]}) ")
        assert crew.board_word(FLEET, word(key="signal:2026-10-01-planning/01-zones", to="wldn-design"))[0] == "wldn-design"
        assert crew.board_word(FLEET, word(key="team:swb-1", to="wldn-operator"))[0] == "wldn-operator"

    def test_a_bolts_word_goes_to_any_conductor_of_the_partition_or_its_operator(self, told):
        """Which team holds a bolt is the page's read, not the command's (design, Decision 1)."""
        for to in ("swb-1-conductor", "swb-2-conductor", "wldn-operator"):
            assert crew.board_word(FLEET, word(key="bolt:tenant-environments", to=to))[0] == to

    def test_a_tell_that_types_nothing_prints_nothing_and_fails(self, told, capsys):
        """board-page "An agent waiting on a question": the tell's own words are on standard error, tell's to say."""
        told, sent = told
        sent["ok"] = False
        assert crew.board_tell(FLEET, word()) is False
        assert len(told) == 1 and capsys.readouterr().out == ""


class TestRefused:
    """board-page "A word not of the board's form is refused": each is refused with its words, and nothing is told."""

    @pytest.fixture(autouse=True)
    def told(self, monkeypatch):
        told = []
        monkeypatch.setattr(crew, "tell", lambda *a, **kw: told.append(a) or True)
        yield
        assert told == []

    @pytest.mark.parametrize("raw, said", [
        ("not json", "a word from the board is one JSON object holding label, key, to and text"),
        ('["wldn"]', "one JSON object holding label, key, to and text"),
        (json.dumps({"label": "wldn", "key": "unit:a", "to": "swb-1-conductor"}), "one JSON object holding label, key, to and text"),
        (word(text=7), "one JSON object holding label, key, to and text"),
        (word(label="nosuch"), "no partition 'nosuch'. partitions: wldn swancloud"),
        (word(key="ledger:a"), "a word from the board is on no item of the kind 'ledger': kinds signal proposal"),
        (word(key="unit:a b"), "a word from the board is on an item's key, <kind>:<name>, not 'unit:a b'"),
        (word(key="proposal:4"), "a word on a proposal goes to wldn-planner, not swb-1-conductor"),
        (word(key="operation:mac-studio/rotate-key", to="wldn-planner"), "a word on an operation goes to wldn-ops, not wldn-planner"),
        (word(to="crw-5-conductor"), "a word on a unit goes to the conductor of the wldn team holding its bolt, or to wldn-operator, not crw-5-conductor"),
        (word(text="  "), "a word from the board holds no text"),
        (word(text="x" * 1001), "a word from the board is at most 1000 characters, not 1001"),
        (word(text="Keep\nthe zone check"), "a word from the board is one line"),
        (word(text="Keep\rthe zone check"), "a word from the board is one line"),
    ])
    def test_refused(self, raw, said):
        with pytest.raises(crew.Refusal) as e:
            crew.board_tell(FLEET, raw)
        assert said in str(e.value)

    def test_a_word_of_the_most_characters_passes(self):
        assert crew.board_word(FLEET, word(text="x" * 1000))[1].endswith("x" * 1000)


class TestSenders:
    def test_every_briefs_roster_says_what_a_tell_from_the_board_is(self):
        """Decision 7: the line on who is speaking, in every brief's roster (teams.10)."""
        assert ("one that begins `[crew tell from <user>@board]` is the user's word sent from the board about the item it "
                "names, and answers no card") in crew.SENDERS
