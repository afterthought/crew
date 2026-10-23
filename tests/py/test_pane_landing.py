"""A bolt landed on the user's own words in main-level ops's pane (plan.16; briefs.12; main-level spec): crew bolt
submit --excerpt submits nothing unless crew reads the words in ops's own transcript as the user's
(plan.submit_word_refusal), naming who said any others and holding none of the words; the act, plan.bolt_submit, on
stand-ins for what it reaches, recording the landing's bolt.submit with the transcript record and the words' length
and keeping the words on its host; and crew bolt land's reads of it, plan.pane_word_of from the run record and
plan.landing_word_read from the kept file. Reading the words in a transcript is test_transcript's; the card's close,
test_landing's and test_card_commands'."""
import argparse

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


class Ran:
    def __init__(self, stdout, returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


class Plan:
    def bolt(self, name):
        return {"Bolt": name, "Team": "crw-5"}


OLD, NEW = "a" * 40, "b" * 40
TEAM = {"name": "crw-5", "label": "swancloud", "machine": "deneb", "kit": {"name": "crew", "dir": "/k", "main": "/k/main"}}


@pytest.fixture
def submit(monkeypatch, tmp_path):
    """crew bolt submit on stand-ins for what it reaches: the plan, ops's transcript, the team's host, which lands the
    bolt unless told otherwise, and this host's run record and kept words, under tmp_path."""
    got = {"ran": [], "emitted": [], "verdict": heard()}
    monkeypatch.setattr(plan, "locate", lambda fleet, kind, name, label: ("swancloud", "crew", "tip", Plan()))
    monkeypatch.setattr(plan, "default_label", lambda fleet, a: "swancloud")
    monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: TEAM)
    monkeypatch.setattr(plan.CardActs, "heard", lambda self, words: (got["verdict"], "s-1"))
    monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: got["ran"].append(argv) or Ran(f"RC=0 OLD={OLD} NEW={NEW} KEPT='' LEVEL=detached MARKED=yes\n"))
    monkeypatch.setattr(plan.READ, "drop_kit", lambda *a: None)
    monkeypatch.setattr(plan.record, "emit", lambda label, act, on, **f: got["emitted"].append(dict(f, Act=act, On=on)) or "eid")
    monkeypatch.setattr(plan.record, "who", lambda: "swancloud-ops")
    monkeypatch.setattr(plan, "LANDINGS", tmp_path / "landings")

    def run(excerpt=None):
        a = argparse.Namespace(bolt="y", label=None, excerpt=excerpt)
        plan.bolt_submit({"teams": {}, "partitions": {}}, a)
        return got
    got["run"] = run
    return got


class TestTheSubmission:
    def test_the_users_words_land_the_bolt_recorded_by_their_record_and_length_and_kept_here(self, submit):
        got = submit["run"](WORDS)
        assert len(got["ran"]) == 1
        [e] = got["emitted"]
        assert e["Act"] == "bolt.submit" and e["frm"] == ["session/s-1/u-7"] and e["Chars"] == len(WORDS)
        assert WORDS not in repr(e)
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") == WORDS

    def test_a_record_with_no_uuid_is_named_by_its_lines_hash(self, submit):
        submit["verdict"] = heard(uuid=None)
        e = submit["run"](WORDS)["emitted"][0]
        assert e["frm"] == [f"session/s-1/line-{heard(uuid=None).line_hash()[:16]}"]

    @pytest.mark.parametrize("v", [heard("agent:swancloud-operator"), heard(grade="refused"), heard("tool"),
                                   heard(grade="unverified", reason="session s-1 is on mac-studio, not deneb")])
    def test_words_crew_does_not_read_as_the_users_submit_nothing(self, submit, v):
        submit["verdict"] = v
        with pytest.raises(plan.Refusal) as e:
            submit["run"](WORDS)
        assert str(e.value) == plan.submit_word_refusal("y", v)
        assert submit["ran"] == [] and submit["emitted"] == []
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") is None

    def test_blank_words_ask_for_the_users(self, submit):
        with pytest.raises(plan.Refusal, match="needs the user's words"):
            submit["run"]("  ")
        assert submit["ran"] == []

    def test_the_cards_approval_lands_as_before_naming_no_record(self, submit):
        e = submit["run"]()["emitted"][0]
        assert e["frm"] == [] and e.get("Chars") is None
        assert not (plan.LANDINGS / "swancloud" / "y.json").exists()

    def test_a_submission_that_did_not_land_keeps_no_words(self, submit, monkeypatch):
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: Ran(f"RC=1 OLD={OLD} NEW={OLD} KEPT='' LEVEL=no MARKED=''\n"))
        with pytest.raises(plan.Refusal, match="did not land"):
            submit["run"](WORDS)
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") is None


def submitted(bolt="y", frm=None, refused=None, by="swancloud-ops", at="2026-10-22T21:04:00Z", host="deneb"):
    e = {"Act": "bolt.submit", "On": [f"bolt/{bolt}"], "From": [frm] if frm else [], "By": by, "At": at, "Host": host}
    return dict(e, Refused=refused) if refused else e


class TestTheWordRead:
    def test_a_landing_on_the_card_names_no_pane(self):
        assert plan.pane_word_of([submitted()], "y") is None
        assert plan.pane_word_of([], "y") is None

    def test_a_landing_on_the_users_words_is_read_from_its_entry(self):
        entries = [submitted(), submitted(frm="session/s-1/u-7")]
        assert plan.pane_word_of(entries, "y") == ("swancloud-ops", "2026-10-22T21:04:00Z", "session/s-1/u-7", "deneb")
        assert plan.pane_word_of(entries, "z") is None

    def test_a_refused_pane_submission_after_a_card_one_names_no_pane(self):
        entries = [submitted(), submitted(frm="session/s-1/u-7", refused="crew submits nothing of bolt y: …")]
        assert plan.pane_word_of(entries, "y") is None

    def test_the_words_are_read_back_only_for_the_landing_that_kept_them(self, monkeypatch, tmp_path):
        monkeypatch.setattr(plan, "LANDINGS", tmp_path)
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") is None
        plan.landing_word_keep("swancloud", "y", WORDS, "swancloud-ops", "2026-10-22T21:04:00Z", "session/s-1/u-7")
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") == WORDS
        assert plan.landing_word_read("swancloud", "y", "session/s-2/u-9") is None
        plan.landing_word_drop("swancloud", "y")
        assert plan.landing_word_read("swancloud", "y", "session/s-1/u-7") is None
        plan.landing_word_drop("swancloud", "y")

    def test_kept_words_crew_cant_read_are_refused_naming_the_file(self, monkeypatch, tmp_path):
        monkeypatch.setattr(plan, "LANDINGS", tmp_path)
        (tmp_path / "swancloud").mkdir()
        (tmp_path / "swancloud" / "y.json").write_text("{not json")
        with pytest.raises(plan.Refusal, match=r"can't read the user's words kept for bolt y's landing in .*y\.json"):
            plan.landing_word_read("swancloud", "y", "session/s-1/u-7")
