#!/usr/bin/env python3
"""questions.py: whether a Claude session on this host is waiting on a question crew's own hook saw it open.

  python3 questions.py <session id>      or, sent over ssh:  python3 - <session id> < questions.py

crew's PreToolUse hook (plugin/hooks/questions) leaves ~/.local/state/crew/questions/<session id> when a crew agent
opens AskUserQuestion or ExitPlanMode: one JSON object holding the call's tool_use_id and its transcript_path. The
mark counts until that transcript holds the call's answer. The answer, on stdout, is one JSON object:

  {"question": null}                       no mark: the hook saw no question open in the session
  {"question": "open", "id": <call>}       a mark whose call has no answer in the transcript yet
  {"question": "answered", "id": <call>}   a mark whose call the transcript holds the answer to
  {"unread": "<what>"}                     what crew could not read to know: the mark, or the transcript it names

It leans on two facts of Claude Code, which it does not document as a format. A PreToolUse hook's input holds
session_id, transcript_path and tool_use_id (Claude Code's hooks reference, "PreToolUse" and "Common input fields").
A call's answer, given, dismissed or abandoned, is a transcript record holding an object of type tool_result whose
tool_use_id is the call's (wldn-ops' transcript of session 4ec81fa0, Claude Code 2.1.286, its AskUserQuestion of
2026-10-07 answered at 19:29:37). It finds that object anywhere in a record, walking every value as transcript.py
does, and skips lines that are not JSON. When either fact stops holding, the mark is never written, or never reads
as answered, and a tell to that agent is refused until its next start.

It writes nothing, and needs nothing but python3's standard library, since it is sent to hosts whose crew may be
older."""
import json, pathlib, re, sys

MARKS = pathlib.Path.home() / ".local/state/crew/questions"


def answers(v, call):
    """Whether a JSON value holds, anywhere in it, the tool_result of the call."""
    if isinstance(v, dict):
        if v.get("type") == "tool_result" and v.get("tool_use_id") == call:
            return True
        v = v.values()
    elif not isinstance(v, list):
        return False
    return any(answers(x, call) for x in v)


def read(sid):
    if not re.fullmatch(r"[A-Za-z0-9-]+", sid):
        return {"unread": f"its session id {json.dumps(sid)} is not one crew reads"}
    mark = MARKS / sid
    try:
        held = json.loads(mark.read_text())
    except FileNotFoundError:
        return {"question": None}
    except (OSError, ValueError) as e:
        return {"unread": f"its question mark {mark} can't be read ({getattr(e, 'strerror', None) or e})"}
    call = held.get("tool_use_id") if isinstance(held, dict) else None
    path = held.get("transcript_path") if isinstance(held, dict) else None
    if not isinstance(call, str) or not call:
        return {"unread": f"its question mark {mark} names no call"}
    if not isinstance(path, str) or not path:
        return {"unread": f"its question mark {mark} names no transcript"}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if call not in line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if answers(record, call):
                    return {"question": "answered", "id": call}
    except FileNotFoundError:
        return {"unread": f"its transcript {path} is missing"}
    except OSError as e:
        return {"unread": f"its transcript {path} can't be read ({e.strerror or e})"}
    return {"question": "open", "id": call}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: questions.py <session id>")
    print(json.dumps(read(sys.argv[1])))
