"""A bolt landed on the user's own words in main-level ops's pane (plan.16; briefs.12; main-level spec): crew bolt
submit --excerpt submits nothing unless crew reads the words in ops's own transcript as the user's
(plan.submit_word_refusal), naming who said any others and holding none of the words. Reading the words in a
transcript is test_transcript's."""
import pytest

import transcript

import plan

WORDS = "Land crw-5's bolt"
HEAD = "crew submits nothing of bolt y"


def heard(asserted_by="user", grade="verified", uuid="u-7", reason=None):
    """A verdict on the words, as transcript.check gives it."""
    if grade == "unverified":
        return transcript.unverified(reason)
    return transcript.Verdict(grade, raw=b'{"type": "user"}', n=4, value={"uuid": uuid} if uuid else {},
                              asserted_by=asserted_by if grade == "verified" else "unknown")


class TestTheWordToLand:
    def test_the_users_words_typed_or_told_from_a_shell_pass(self):
        assert plan.submit_word_refusal("y", heard()) is None
        assert plan.submit_word_refusal("y", heard(uuid=None)) is None

    def test_words_another_agent_passed_on_are_refused_naming_it_and_the_two_ways(self):
        assert plan.submit_word_refusal("y", heard("agent:swancloud-operator")) == (
            f"{HEAD}: the words are swancloud-operator's, passed on with crew tell, and not the user's; tell "
            "swancloud-operator that the user lands a bolt on its landing card or in main-level ops's pane")

    @pytest.mark.parametrize("v, words", [
        (heard(grade="refused"), "the words are not in a record your session received; only the user's own words land a "
                                 "bolt, quoted as they wrote them in your pane, never your own"),
        (heard("crew"), "the words are crew's own message, not the user's"),
        (heard("tool"), "the words are a tool's output, not the user's"),
        (heard(grade="found"), "the words are in a record of your transcript crew can't read as anyone's, so it can't tell they are the user's"),
        (heard(grade="unverified", reason="no transcript for session s-9"),
         "crew can't read your session's transcript, so it can't tell the words are the user's: no transcript for session s-9")])
    def test_words_crew_does_not_read_as_the_users_are_refused(self, v, words):
        assert plan.submit_word_refusal("y", v) == f"{HEAD}: {words}"

    @pytest.mark.parametrize("v", [heard(grade="refused"), heard("agent:swancloud-operator"), heard("crew"), heard("tool"),
                                   heard(grade="found"), heard(grade="unverified", reason="stale")])
    def test_no_refusal_holds_the_words(self, v):
        assert WORDS not in plan.submit_word_refusal("y", v)
