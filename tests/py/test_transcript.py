"""What an agent's own transcript says it still waits on (teams.4): transcript.pending and transcript.last_at, on a
transcript written as Claude Code writes one. A file read is no process, so these are logic cases."""
import json

import transcript

LONG_AGO = "2026-10-12T09:30:00.000Z"


def write(tmp_path, *records):
    path = tmp_path / "s.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    return path


STARTED = [{"type": "assistant", "timestamp": LONG_AGO, "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
           {"type": "user", "timestamp": LONG_AGO, "toolUseResult": {"stdout": "", "backgroundTaskId": "b8y1gomwj"}}]
TOLD = {"type": "queue-operation", "timestamp": LONG_AGO, "operation": "enqueue",
        "content": "<task-notification>\n<task-id>b8y1gomwj</task-id>\n<status>completed</status>\n</task-notification>"}


def test_a_background_task_started_and_not_told_over_is_pending(tmp_path):
    assert transcript.pending(write(tmp_path, *STARTED)) == ["b8y1gomwj"]


def test_a_task_notification_naming_it_ends_it(tmp_path):
    assert transcript.pending(write(tmp_path, *STARTED, TOLD)) == []


def test_the_last_record_is_when_the_session_last_wrote(tmp_path):
    assert transcript.last_at(write(tmp_path, *STARTED, TOLD)).isoformat() == "2026-10-12T09:30:00+00:00"


def test_a_missing_transcript_is_none_never_an_empty_list(tmp_path):
    assert transcript.pending(tmp_path / "gone.jsonl") is None
    assert transcript.last_at(tmp_path / "gone.jsonl") is None
