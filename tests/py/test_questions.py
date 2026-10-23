"""Which session crew recorded of an agent in a pane herdr names no session for (teams.11, main-level "Any agent crew
starts is reached by name"): questions.session_in, the newest record naming the agent, its herdr session and its pane,
and questions.answer's --pane form, which reads crew's records and the session's question mark. A file read is no
process, so these are logic cases; that crew pipes questions.py to the agent's host is the journeys'."""
import json

import pytest

import questions

PLANNER = {"CREW_AGENT": "wldn-planner", "CREW_LABEL": "wldn", "CREW_HERDR_SESSION": "wldn-2", "CREW_PANE": "w1:p2"}


def test_the_newest_of_two_records_of_the_agent_in_its_pane_is_its_session():
    records = [(100.0, "old", PLANNER), (200.0, "new", PLANNER)]
    assert questions.session_in(records, "wldn-planner", "wldn-2", "w1:p2") == "new"
    assert questions.session_in(list(reversed(records)), "wldn-planner", "wldn-2", "w1:p2") == "new"


@pytest.mark.parametrize("fields", [
    dict(PLANNER, CREW_PANE="w1:p3"),
    dict(PLANNER, CREW_HERDR_SESSION="wldn-1"),
    {k: v for k, v in PLANNER.items() if k not in ("CREW_HERDR_SESSION", "CREW_PANE")},
    dict(PLANNER, CREW_AGENT="wldn-design")])
def test_a_record_in_another_pane_or_session_with_no_pane_or_of_another_agent_is_not_taken(fields):
    assert questions.session_in([(300.0, "other", fields), (100.0, "mine", PLANNER)], "wldn-planner", "wldn-2", "w1:p2") == "mine"
    assert questions.session_in([(300.0, "other", fields)], "wldn-planner", "wldn-2", "w1:p2") is None


def test_no_records_is_no_session():
    assert questions.session_in([], "wldn-planner", "wldn-2", "w1:p2") is None


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(questions, "RECORDS", tmp_path / "sessions")
    monkeypatch.setattr(questions, "MARKS", tmp_path / "questions")
    return tmp_path


def recorded(home, sid, fields):
    (home / "sessions").mkdir(exist_ok=True)
    (home / "sessions" / sid).write_text("".join(f"{k}={v}\n" for k, v in fields.items()))


def test_the_pane_form_answers_the_recorded_sessions_mark_with_the_session(home):
    recorded(home, "sid-1", PLANNER)
    (home / "questions").mkdir()
    (home / "questions" / "sid-1").write_text(json.dumps({"tool_use_id": "toolu_01", "transcript_path": str(home / "t.jsonl")}))
    (home / "t.jsonl").write_text("")
    assert questions.answer(["--pane", "wldn-2", "w1:p2", "wldn-planner"]) == {"session": "sid-1", "question": "open", "id": "toolu_01"}
    (home / "questions" / "sid-1").unlink()
    assert questions.answer(["--pane", "wldn-2", "w1:p2", "wldn-planner"]) == {"session": "sid-1", "question": None}


def test_the_pane_form_with_no_record_or_no_folder_answers_no_session(home):
    assert questions.answer(["--pane", "wldn-2", "w1:p2", "wldn-planner"]) == {"session": None, "question": None}
    recorded(home, "sid-1", dict(PLANNER, CREW_PANE="w1:p3"))
    assert questions.answer(["--pane", "wldn-2", "w1:p2", "wldn-planner"]) == {"session": None, "question": None}


@pytest.mark.parametrize("args, what", [
    (["--pane", "../x", "w1:p2", "wldn-planner"], 'its herdr session "../x"'),
    (["--pane", "wldn-2", "w1/p2", "wldn-planner"], 'its pane "w1/p2"'),
    (["--pane", "wldn-2", "w1:p2", "Wldn-Planner"], 'its agent "Wldn-Planner"')])
@pytest.mark.usefixtures("home")
def test_a_name_crew_reads_no_record_by_is_unread(args, what):
    assert questions.answer(args) == {"unread": f"{what} is not one crew reads"}


def test_an_argument_list_of_neither_form_is_none():
    assert questions.answer([]) is None
    assert questions.answer(["--pane", "wldn-2", "w1:p2"]) is None
