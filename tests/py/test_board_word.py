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
import plan
import transcript

FLEET = {**facts.FLEET, "partitions": {**facts.FLEET["partitions"], "swancloud": {"label": "swancloud", "machine": "mac-studio"}},
         "teams": {**facts.FLEET["teams"], "crw-5": {"name": "crw-5", "label": "swancloud", "machine": "mac-studio"}}}


def word(**f):
    return json.dumps({"label": "wldn", "key": "unit:a", "to": "wldn-planner", "text": "Keep the zone check", **f})


class TestTell:
    """A word is told its agent as the user's from the board, the item named before the text."""

    @pytest.fixture
    def told(self, monkeypatch):
        told, sent = [], {"ok": True}
        monkeypatch.setattr(getpass, "getuser", lambda: "chuck")
        monkeypatch.setattr(crew, "tell", lambda fleet, name, text, **kw: told.append((name, text, kw)) or sent["ok"])
        return told, sent

    def test_a_word_on_a_unit_is_told_the_planner_from_the_board_naming_the_item(self, told, capsys):
        """board-page "A word on a unit"; "A word goes to the agent its item's kind names"."""
        told, _ = told
        assert crew.board_tell(FLEET, word()) is True
        assert told == [("wldn-planner", "(on unit a) Keep the zone check", {"sender": "chuck@board"})]
        assert len(told[0][1]) == 31 and capsys.readouterr().out == "sent to wldn-planner\n"

    def test_a_word_on_a_proposal_goes_to_the_planner_and_one_on_a_deploy_to_main_level_ops(self, told):
        assert crew.board_word(FLEET, word(key="proposal:4", to="wldn-planner")) == ("wldn-planner", "(on proposal 4) Keep the zone check")
        key = "deploy:mac-studio/" + "a" * 40 + "/2026-10-12T10:06:00Z"
        assert crew.board_word(FLEET, word(key=key, to="wldn-ops"))[1].startswith(f"(on deploy {key[7:]}) ")
        assert crew.board_word(FLEET, word(key="signal:2026-10-01-planning/01-zones", to="wldn-design"))[0] == "wldn-design"
        assert crew.board_word(FLEET, word(key="team:swb-1", to="wldn-operator"))[0] == "wldn-operator"

    def test_a_word_on_a_bolt_or_a_fix_goes_to_the_planner(self, told):
        """board-page "Each kind's agent": a bolt's and a fix's word goes to the planner, as a unit's does."""
        assert crew.board_word(FLEET, word(key="bolt:tenant-environments"))[0] == "wldn-planner"
        assert crew.board_word(FLEET, word(key="fix:tenant-environments/edge"))[0] == "wldn-planner"

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
        (json.dumps({"label": "wldn", "key": "unit:a", "to": "wldn-planner"}), "one JSON object holding label, key, to and text"),
        (word(text=7), "one JSON object holding label, key, to and text"),
        (word(label="nosuch"), "no partition 'nosuch'. partitions: wldn swancloud"),
        (word(key="ledger:a"), "a word from the board is on no item of the kind 'ledger': kinds signal proposal"),
        (word(key="unit:a b"), "a word from the board is on an item's key, <kind>:<name>, not 'unit:a b'"),
        (word(key="proposal:4", to="wldn-ops"), "a word on a proposal goes to wldn-planner, not wldn-ops"),
        (word(key="operation:mac-studio/rotate-key", to="wldn-planner"), "a word on an operation goes to wldn-ops, not wldn-planner"),
        (word(to="swb-1-conductor"), "a word on a unit goes to wldn-planner, not swb-1-conductor"),
        (word(key="bolt:tenant-environments", to="wldn-operator"), "a word on a bolt goes to wldn-planner, not wldn-operator"),
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


class TestAnswersNothing:
    """board-page "A word from the board answers nothing": words verified as the user's only in a tell from the board
    land no bolt, answer no batch and settle no record, each saying where the user answers instead; the same words
    typed in the pane, a verdict not from the board, still do."""
    FROM_BOARD = "the words came from the board, which answers nothing"

    def heard(self, board):
        return transcript.Verdict("verified", raw=b'{"type": "user"}', n=4, value={"uuid": "u-60"}, asserted_by="user", board=board)

    def test_a_landing_asked_from_the_board_submits_nothing(self):
        """board-page "A landing asked from the board"."""
        assert plan.submit_word_refusal("y", self.heard(True)) == (
            f"crew submits nothing of bolt y: {self.FROM_BOARD}; the user lands a bolt on its landing card or in main-level ops's pane")
        assert plan.submit_word_refusal("y", self.heard(False)) is None

    def test_a_batch_answered_from_the_board_is_not_answered(self):
        """board-page "A batch answered from the board"."""
        held = [{"Act": "review.batch", "Batch": "14", "Units": "x1:crw-1@aaa1", "At": "2026-10-22T19:00:00Z", "On": []},
                {"Act": "card.post", "Key": "batch/14", "Card": "req_14", "By": "swancloud-planner", "Host": "deneb",
                 "At": "2026-10-22T19:01:00Z", "On": ["batch/14"]}]
        assert plan.pane_answer_refusal(14, held, self.heard(True), "planner") == (
            f"crew records no answer of batch 14: {self.FROM_BOARD}; the user answers a batch on its card or in your pane")
        assert plan.pane_answer_refusal(14, held, self.heard(False), "planner") is None

    def test_a_record_settled_from_the_board_is_settled_in_no_pane(self):
        why = plan.settled_refusal(38, "crew", self.heard(True))
        assert why == (f"crew records record 0038 in crew as settled in no pane: {self.FROM_BOARD}; the user settles a record in "
                       "your pane or on its card; run crew record crew 38 --proposed without --settled-in-pane, and the user answers on its card")
        assert plan.settled_refusal(38, "crew", self.heard(False)) is None


class TestSenders:
    def test_every_briefs_roster_says_what_a_tell_from_the_board_is(self):
        """Decision 7: the line on who is speaking, in every brief's roster (teams.10)."""
        assert ("one that begins `[crew tell from <user>@board]` is the user's word sent from the board about the item it "
                "names, and answers no card") in crew.SENDERS
