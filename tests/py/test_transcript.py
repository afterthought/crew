"""What crew reads of a Claude Code transcript, on transcripts written as Claude Code writes them: what an agent's own
transcript says it still waits on (teams.4), transcript.pending and last_at, and whether its turn is over,
transcript.turn_over; a signal's excerpt checked and graded
(signals.2, signals.5), transcript.check; and whether a session received a prompt crew sent (teams.15),
transcript.end and received. A file read is no process, so these are logic cases; that crew pipes transcript.py to
the agent's host is the journeys'."""
import datetime
import json
import os

import pytest

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
    assert transcript.turn_over(tmp_path / "gone.jsonl") is None


# Whether the session's turn is over (record 0007): its last message the model's, ending its turn, as Claude Code
# 2.1.307 writes it, the records that are no message (a stop hook's summary, the cost) after it.
ENDED = [{"type": "user", "timestamp": "2026-10-23T02:46:10.000Z", "message": {"content": "<command-name>/opsx:verify</command-name>"}},
         {"type": "assistant", "timestamp": "2026-10-23T02:47:13.236Z", "message": {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Nothing to do."}]}},
         {"type": "system", "subtype": "stop_hook_summary", "timestamp": "2026-10-23T02:47:13.414Z"},
         {"type": "cost-state", "totalCostUSD": 1}]


def test_a_turn_ended_by_the_models_message_is_over_at_its_time(tmp_path):
    assert transcript.turn_over(write(tmp_path, *ENDED)).isoformat() == "2026-10-23T02:47:13.236000+00:00"


def test_a_turn_going_on_is_not_over(tmp_path):
    working = {"type": "assistant", "timestamp": LONG_AGO, "message": {"stop_reason": "tool_use", "content": [{"type": "tool_use", "name": "Bash"}]}}
    assert transcript.turn_over(write(tmp_path, ENDED[0], working)) is None
    assert transcript.turn_over(write(tmp_path, ENDED[0])) is None


def test_a_turn_ended_and_then_sent_something_is_not_over(tmp_path):
    notice = {"type": "user", "timestamp": "2026-10-23T02:50:00.000Z",
              "message": {"content": "<task-notification>\n<task-id>b8y1gomwj</task-id>\n</task-notification>"}}
    assert transcript.turn_over(write(tmp_path, *ENDED, notice)) is None


def test_a_subagents_message_is_not_the_sessions_turn(tmp_path):
    sub = {"type": "assistant", "isSidechain": True, "timestamp": LONG_AGO, "message": {"stop_reason": "end_turn"}}
    assert transcript.turn_over(write(tmp_path, ENDED[0], sub)) is None


# What crew reads of a transcript to check a signal's excerpt (signals.2, signals.5), and whether a session received a
# prompt crew sent (teams.15): transcript.check, end and received, on transcripts written under a scratch HOME as
# Claude Code writes them, in ~/<account>/projects/<folder>/<session>.jsonl.

def ago(minutes):
    t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


@pytest.fixture
def put(tmp_path, monkeypatch):
    """put(session, *records, account=".claude", raw=None, old=False): a session's transcript, each record a JSON line
    (raw, bytes written as they are); old sets the file's time to 2020. Returns its path."""
    monkeypatch.setenv("HOME", str(tmp_path))

    def put(session, *records, account=".claude", raw=None, old=False):
        d = tmp_path / account / "projects" / "-work"
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{session}.jsonl"
        path.write_bytes(raw if raw is not None else "".join(json.dumps(r) + "\n" for r in records).encode())
        if old:
            os.utime(path, (1577836800, 1577836800))
        return path
    return put


def said(session, excerpt, *skip, stage_by=None):
    v = transcript.check(session, excerpt, skip, stage_by)
    return " ".join(str(x) for x in (v.grade, v.asserted_by, v.n, v.uuid)) + (f": {v.reason}" if v.reason else "")


def user(uuid, content, **more):
    return dict(type="user", uuid=uuid, message={"role": "user", "content": content}, **more)


def tool(uuid, content):
    return user(uuid, [{"type": "tool_result", "tool_use_id": "t", "content": content}])


def wrote(uuid, text):
    return {"type": "assistant", "uuid": uuid, "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


# Claude Code's copy of a message it sends the model, as Claude Code 2.1.303 writes it (read on deneb, session f965a6bb,
# 2026-10-22): a line of its own type holding the message's role and content blocks as sent, with no uuid or timestamp.
def copied(role, content):
    return {"type": "api-request-blob", "sessionId": "s", "hash": "3f9a1c0e5b7d2468ace013579bdf2468ace013579bdf2468ace013579bdf2468",
            "message": {"role": role, "content": content}}


# A Bash call's result, a background task's notice and a Read's result, as Claude Code 2.1.303 writes them (read on
# mac-studio, 2026-10-20): a call's output in its tool_result block and as toolUseResult's stdout, a background call's
# stdout empty and its task named; the notice names the task's output file and not the output; a Read's tool_result
# numbers each line of the file, and its toolUseResult holds the file's text as it is.
def ran(uuid, content, stdout, **more):
    return dict(tool(uuid, content), toolUseResult={"stdout": stdout, "stderr": "", "interrupted": False, "isImage": False,
                                                    "noOutputExpected": False, **more})


def told(task, output, description):
    return {"type": "queue-operation", "operation": "enqueue",
            "content": f"<task-notification>\n<task-id>{task}</task-id>\n<tool-use-id>t</tool-use-id>\n<output-file>{output}</output-file>\n"
                       f"<status>completed</status>\n<summary>Background command \"{description}\" completed (exit code 0)</summary>\n</task-notification>"}


def read(uuid, path, text):
    lines = text.splitlines()
    return dict(tool(uuid, "\n".join(f"{n}\t{s}" for n, s in enumerate(lines, 1))),
                toolUseResult={"type": "text", "file": {"filePath": path, "content": text, "numLines": len(lines), "startLine": 1, "totalLines": len(lines)}})


LINE = "no session was started for card land/every-deploy-offer-reaches-the-user"
OUTPUT = "/private/tmp/claude-501/-work/s-bg/tasks/bbsbed1vr.output"
BACKGROUND = [ran("u-40", f"Command running in background with ID: bbsbed1vr. Output is being written to: {OUTPUT}", "", backgroundTaskId="bbsbed1vr"),
              told("bbsbed1vr", OUTPUT, "Wait for the landing card")]


CMD = {"type": "assistant", "uuid": "a-9", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Bash", "input": {
    "command": '/w/crew/main/plugin/bin/crew signal open-groups "Templates need a check." --excerpt "open security groups"'}}]}}


class TestCheck:
    def test_typed_text_is_verified_asserted_by_the_user_in_an_accounts_own_folder(self, put):
        put("s-typed", user("u-1", "Also check the templates for open security groups, please.", timestamp=ago(1)), wrote("a-1", "I'll record that."),
            account=".claude-sub-ia")
        assert said("s-typed", "open security groups") == "verified user 1 u-1"

    def test_a_tools_output_with_string_content_or_blocks_is_verified_asserted_by_a_tool(self, put):
        put("s-tool", tool("u-2", "sg-0a1 ingress 0.0.0.0/0: open security groups in 3 templates"),
            tool("u-3", [{"type": "text", "text": "WARN open security groups in stack edge"}]))
        assert said("s-tool", "open security groups in 3 templates") == "verified tool 1 u-2"
        assert said("s-tool", "open security groups in stack edge") == "verified tool 2 u-3"

    def test_a_crew_commands_printed_line_is_verified_as_a_tools_and_refused_recapitalized(self, put):
        put("s-printed", ran("u-41", LINE, LINE))
        assert said("s-printed", LINE) == "verified tool 1 u-41"
        assert said("s-printed", "No session was started for card land/every-deploy-offer-reaches-the-user") == "refused unknown None None"

    def test_a_background_tasks_output_is_refused_until_a_read_of_its_file_puts_it_in_the_transcript(self, put):
        put("s-unread", *BACKGROUND)
        assert said("s-unread", LINE) == "refused unknown None None"
        put("s-read", *BACKGROUND, read("u-42", OUTPUT, f"waiting for card land/every-deploy-offer-reaches-the-user\n{LINE}\n"))
        assert said("s-read", LINE) == "verified tool 3 u-42"
        assert said("s-read", "waiting for card land/every-deploy-offer-reaches-the-user") == "verified tool 3 u-42"
        assert said("s-read", f"waiting for card land/every-deploy-offer-reaches-the-user\n{LINE}") == "verified tool 3 u-42"

    def test_a_tell_is_its_senders_the_users_own_tell_the_users_and_crews_notice_crews(self, put):
        put("s-tell", user("u-4", "[crew tell from swb-2-conductor] The deploy left open security groups behind."),
            user("u-5", "[crew tell from chuck@mac-studio] Leave the open security groups for now."),
            user("u-6", "[crew] plan(edge): open security groups move to the queue (chuck@mac-studio)"))
        assert said("s-tell", "The deploy left open security groups behind.") == "verified agent:swb-2-conductor 1 u-4"
        assert said("s-tell", "Leave the open security groups for now.") == "verified user 2 u-5"
        assert said("s-tell", "open security groups move to the queue") == "verified crew 3 u-6"

    def test_a_stages_own_prompt_and_its_skill_text_are_its_conductors_elsewhere_or_not_next_the_users(self, put):
        put("s-stage", user("u-20", "<command-message>opsx:apply</command-message>\n<command-name>/opsx:apply</command-name>\n"
                                    "<command-args>edge-groups Close the open security groups verify found.</command-args>"),
            user("u-21", [{"type": "text", "text": "Implement tasks from an OpenSpec change.\n\n\nARGUMENTS: edge-groups Close the open security groups verify found."}],
                 isMeta=True),
            user("u-22", "Fix: The deploy leaves open security groups on stack edge."),
            user("u-23", "Merge fix/smoke-2/edge into bolt/smoke-2: wt merge bolt/smoke-2 --no-squash --no-remove"),
            user("u-24", "Leave Fix: as it is, the open security groups are mine.\n\nARGUMENTS: edge-groups Close the open security groups verify found."),
            user("u-25", "Merge fix/smoke-2/rule into bolt/smoke-2: wt submit bolt/smoke-2 --no-remove"))
        by = "swb-2-conductor"
        assert said("s-stage", "/opsx:apply", stage_by=by) == "verified agent:swb-2-conductor 1 u-20"
        assert said("s-stage", "Implement tasks from an OpenSpec change.", stage_by=by) == "verified agent:swb-2-conductor 2 u-21"
        assert said("s-stage", "open security groups on stack edge", stage_by=by) == "verified agent:swb-2-conductor 3 u-22"
        assert said("s-stage", "wt merge bolt/smoke-2", stage_by=by) == "verified agent:swb-2-conductor 4 u-23"
        assert said("s-stage", "wt submit bolt/smoke-2", stage_by=by) == "verified agent:swb-2-conductor 6 u-25"
        assert said("s-stage", "the open security groups are mine", stage_by=by) == "verified user 5 u-24"
        assert said("s-stage", "Close the open security groups verify found.", stage_by=by) == "verified user 5 u-24"
        assert said("s-stage", "open security groups on stack edge") == "verified user 3 u-22"
        assert said("s-stage", "Implement tasks from an OpenSpec change.") == "verified user 2 u-21"

    def test_the_words_a_stages_command_carries_are_the_conductors_in_the_skill_text_ending_with_them(self, put):
        put("s-args", user("u-25", "<command-message>opsx:verify</command-message>\n<command-name>/opsx:verify</command-name>\n"
                                   "<command-args>edge-groups The groups still open?</command-args>"),
            user("u-26", [{"type": "text", "text": "Verify that an implementation matches the change.\n\n\nARGUMENTS: edge-groups The groups still open?"}], isMeta=True))
        assert said("s-args", "The groups still open?", stage_by="swb-2-conductor") == "verified agent:swb-2-conductor 2 u-26"

    def test_words_only_in_the_agents_own_record_nowhere_or_only_in_a_crew_signal_command_are_refused(self, put):
        put("s-own", user("u-7", "Have a look at the templates."), wrote("a-7", "The templates leave open security groups."), CMD)
        for words in ("The templates leave open security groups.", "the user wants every template locked down", "open security groups"):
            assert said("s-own", words) == "refused unknown None None"

    def test_the_agents_own_reply_and_command_are_refused_though_claude_code_copied_them(self, put):
        reply = "The sweep leaves cards open on a closed row."
        sent = copied("assistant", [{"type": "thinking", "thinking": ""}, {"type": "text", "text": reply}])
        put("s-copied", user("u-50", "Look at the sweep."), wrote("a-50", reply), sent)
        put("s-copied-first", user("u-50", "Look at the sweep."), sent, wrote("a-50", reply))
        assert said("s-copied", reply) == "refused unknown None None"
        assert said("s-copied-first", reply) == "refused unknown None None"
        call = [{"type": "tool_use", "id": "t", "name": "Bash", "input": {"command": 'echo "cards stay open on a closed row"'}}]
        put("s-ran", user("u-50", "Look at the sweep."), {"type": "assistant", "uuid": "a-51", "message": {"role": "assistant", "content": call}},
            copied("assistant", call))
        assert said("s-ran", "cards stay open on a closed row") == "refused unknown None None"

    def test_words_only_in_claude_codes_copy_of_what_it_sent_the_model_are_refused(self, put):
        put("s-reminder", user("u-50", "Look at the sweep."),
            copied("system", [{"type": "text", "text": "The user hasn't heard from you in a while"}]))
        assert said("s-reminder", "The user hasn't heard from you in a while") == "refused unknown None None"

    def test_the_users_words_and_a_tools_output_with_their_copies_beside_them_are_verified_from_their_own_record(self, put):
        put("s-asked", user("u-51", "Close the open cards on a dropped row."),
            copied("user", [{"type": "text", "text": "Close the open cards on a dropped row."}]))
        assert said("s-asked", "Close the open cards on a dropped row.") == "verified user 1 u-51"
        put("s-printed-copy", tool("u-52", "3 cards left open"),
            copied("user", [{"type": "tool_result", "tool_use_id": "t", "content": "3 cards left open"}]))
        assert said("s-printed-copy", "3 cards left open") == "verified tool 1 u-52"

    def test_a_message_or_output_mentioning_crew_signal_is_searched_all_but_its_command_lines(self, put):
        put("s-mention", user("u-30", "[crew tell from swc-1-conductor] crew signal refused to record this: the deploy left open security groups behind."),
            tool("u-31", "Verify report: crew signal land lands each capture of the pass on main."),
            tool("u-32", 'the templates keep their groups open\n+ /w/crew/main/plugin/bin/crew signal open-groups "Templates need a check." '
                         '--excerpt "every template is open to the world"\n+ crew signal edge-drifts "Edge drifts." \\\n'
                         '    --excerpt="edge drifted overnight"\nsignal 2026-10-08-x/01-open-groups: excerpt verified'))
        assert said("s-mention", "crew signal refused to record this: the deploy left open security groups behind.") == "verified agent:swc-1-conductor 1 u-30"
        assert said("s-mention", "crew signal land lands each capture of the pass") == "verified tool 2 u-31"
        assert said("s-mention", "the templates keep their groups open") == "verified tool 3 u-32"
        assert said("s-mention", "01-open-groups: excerpt verified") == "verified tool 3 u-32"
        for words in ("every template is open to the world", "Templates need a check.", "edge drifted overnight"):
            assert said("s-mention", words) == "refused unknown None None"

    def test_a_transcript_with_no_type_fields_grades_found_its_line_the_source(self, put):
        put("s-untyped", {"uuid": "x-1", "payload": {"text": "open security groups everywhere"}},
            {"payload": {"command": "crew signal open-groups --excerpt-file /tmp/e.txt"}})
        assert said("s-untyped", "open security groups everywhere") == "found unknown 1 x-1"

    def test_not_json_lines_no_session_and_no_file_each_grade_unverified(self, put):
        put("s-garbled", raw=b'{"type":"user","message":{"content":"open security groups"}}\nthis is not JSON\n')
        assert said("s-garbled", "open security groups") == "unverified unknown None None: the transcript is not JSON lines"
        assert said("", "open security groups") == "unverified unknown None None: herdr names no session"
        assert said("s-none", "open security groups") == "unverified unknown None None: no transcript for session s-none"

    def test_a_transcript_last_written_over_fifteen_minutes_ago_by_its_timestamp_or_else_the_files_time_grades_unverified(self, put):
        put("s-stale", user("u-8", "open security groups", timestamp=ago(20)), wrote("a-8", "Noted."))
        assert said("s-stale", "open security groups") == ("unverified unknown None None: session s-stale's transcript has not been written for 20 "
                                                           "minutes: crew may be reading another session's")
        put("s-quiet", user("u-9", "open security groups"), old=True)
        assert said("s-quiet", "open security groups").startswith("unverified unknown None None: session s-quiet's transcript has not been written for ")
        put("s-recent", user("u-10", "open security groups", timestamp=ago(30)), tool("u-11", "done") | {"timestamp": ago(14)}, old=True)
        assert said("s-recent", "open security groups") == "verified user 1 u-10"

    def test_whitespace_differs_freely_and_a_trailing_line_still_being_written_is_left_out(self, put):
        put("s-space", raw=(json.dumps(user("u-12", "check   for open\n   security\tgroups")) + "\n"
                            + '{"type":"user","uuid":"u-13","message":{"content":"open sec').encode())
        assert said("s-space", "open security\n groups") == "verified user 1 u-12"

    def test_of_two_records_holding_the_words_the_latest_is_the_source(self, put):
        put("s-twice", user("u-14", "open security groups, again"), user("u-15", "I said: open security groups"))
        assert said("s-twice", "open security groups") == "verified user 2 u-15"

    def test_with_an_excerpt_file_the_records_that_wrote_it_are_not_searched(self, put):
        put("s-file", user("u-16", [{"type": "tool_result", "tool_use_id": "t3", "content": "File created successfully at: /tmp/e.txt"}],
                           toolUseResult={"type": "create", "filePath": "/tmp/e.txt", "content": "the words I wrote myself"}))
        assert said("s-file", "the words I wrote myself", "/tmp/e.txt") == "refused unknown None None"
        assert said("s-file", "the words I wrote myself") == "verified tool 1 u-16"


class TestReceived:
    def test_a_session_with_no_transcript_ends_at_0_and_has_received_nothing(self, put):
        assert transcript.end("s-fresh") == {"path": None, "size": 0}
        assert transcript.received("s-fresh", 0, "Fix: The banner flickers.") == {"received": False}

    def test_a_plain_prompt_a_slash_command_with_its_arguments_and_a_queued_prompt_are_received(self, put):
        f = put("s-sent", user(None, "[crew] Read where your bolt stands, then carry on."), user(None, "Carry on with the sign-in."))
        n = f.stat().st_size
        assert transcript.end("s-sent") == {"path": str(f), "size": n}
        with open(f, "a") as out:
            for r in (wrote(None, "Fix: The banner flickers. [crew tell from swb-1-conductor] Carry on."), user(None, "Fix:   The banner\n flickers."),
                      user(None, "<command-message>opsx:apply</command-message>\n<command-name>/opsx:apply</command-name>\n<command-args>edge-groups Close   the groups.</command-args>"),
                      {"type": "queue-operation", "operation": "enqueue", "content": "[crew tell from swb-1-conductor] Carry on."}):
                out.write(json.dumps(r) + "\n")
        for text in ("Fix: The banner flickers.", "/opsx:apply edge-groups Close the groups.", "[crew tell from swb-1-conductor] Carry on."):
            assert transcript.received("s-sent", n, text) == {"received": True}
        assert transcript.received("s-sent", 0, "[crew] Read where your bolt stands, then carry on.") == {"received": True}
        assert transcript.received("s-sent", n, "[crew] Read where your bolt stands, then carry on.") == {"received": False}
        assert transcript.received("s-sent", n - 10, "Carry on with the sign-in.") == {"received": False}

    def test_the_agents_own_words_quoting_a_prompt_and_another_commands_name_or_arguments_are_not_received(self, put):
        put("s-said", user(None, "<command-name>/opsx:verify</command-name>\n<command-args>edge-groups</command-args>"),
            wrote(None, "Merge a into bolt/b: wt submit bolt/b --no-remove"))
        assert transcript.received("s-said", 0, "Merge a into bolt/b: wt submit bolt/b --no-remove") == {"received": False}
        assert transcript.received("s-said", 0, "/opsx:verify edge-groups Close the groups.") == {"received": False}
        assert transcript.received("s-said", 0, "/opsx:apply edge-groups") == {"received": False}
        assert transcript.received("s-said", 0, "/opsx:verify edge-groups") == {"received": True}

    def test_a_transcript_that_is_not_json_lines_and_a_session_id_crew_does_not_read_are_unread(self, put):
        put("s-garbled", raw=b'{"type":"user","message":{"content":"Carry on."}}\nthis is not JSON\n')
        assert transcript.received("s-garbled", 0, "Carry on.") == {"unread": "the transcript is not JSON lines"}
        assert transcript.end("../x") == {"unread": 'session id "../x" is not one crew reads'}
        assert transcript.received("", 0, "Carry on.") == {"unread": 'session id "" is not one crew reads'}
