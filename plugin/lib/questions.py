#!/usr/bin/env python3
"""questions.py: whether a Claude session on this host is waiting on a question crew's own hook saw it open.

  python3 questions.py <session id>      or, sent over ssh:  python3 - <session id> < questions.py
  python3 questions.py --pane <herdr session> <pane id> <agent>

crew's PreToolUse hook (plugin/hooks/questions) leaves ~/.local/state/crew/questions/<session id> when a crew agent
opens AskUserQuestion or ExitPlanMode: one JSON object holding the call's tool_use_id and its transcript_path. The
mark counts until that transcript holds the call's answer. The answer, on stdout, is one JSON object:

  {"question": null}                       no mark: the hook saw no question open in the session
  {"question": "open", "id": <call>}       a mark whose call has no answer in the transcript yet
  {"question": "answered", "id": <call>}   a mark whose call the transcript holds the answer to
  {"unread": "<what>"}                     what crew could not read to know: the mark, or the transcript it names

The second form asks for an agent herdr names no Claude session for, by the herdr session and pane it runs in. crew's
SessionStart hook (plugin/hooks/session-start) records every crew agent's session in
~/.local/state/crew/sessions/<session id>, lines of KEY=value, among them CREW_AGENT, the agent's name, and
CREW_HERDR_SESSION and CREW_PANE, the herdr session and pane the session started in or herdr resumed it in. The
session is the newest record, by its file's time, naming that agent, herdr session and pane, and the answer is the
first form's for it with "session": <its id> added; with no such record it is {"session": null, "question": null}. A
record written by a hook older than those keys names no pane and matches nothing. A record it cannot read is passed
over, and a records folder it cannot list is unread.

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
RECORDS = pathlib.Path.home() / ".local/state/crew/sessions"
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
PANE = re.compile(r"[A-Za-z0-9:]+")
SESSION = re.compile(r"[A-Za-z0-9-]+")


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
    if not SESSION.fullmatch(sid):
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


def session_in(records, agent, session, pane):
    """The session crew recorded of the agent starting in that herdr session and pane, from its records, each (its
    file's time, its session id, its fields): the newest that names all three, or None."""
    held = [(t, sid) for t, sid, fields in records
            if (fields.get("CREW_AGENT"), fields.get("CREW_HERDR_SESSION"), fields.get("CREW_PANE")) == (agent, session, pane)]
    return max(held)[1] if held else None


def records():
    """crew's records of the sessions on this host, as session_in takes them, passing over one it cannot read; or what
    it could not list. No folder is no record."""
    try:
        names = [f for f in RECORDS.iterdir() if SESSION.fullmatch(f.name)]
    except FileNotFoundError:
        return []
    except OSError as e:
        return f"crew's session records {RECORDS} can't be listed ({e.strerror or e})"
    held = []
    for f in names:
        try:
            t, text = f.stat().st_mtime, f.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        held.append((t, f.name, dict(line.split("=", 1) for line in text.splitlines() if "=" in line)))
    return held


def by_pane(session, pane, agent):
    """The second form's answer: the session crew recorded of the agent in that herdr session and pane, and its mark."""
    for what, v, shape in (("herdr session", session, NAME), ("pane", pane, PANE), ("agent", agent, NAME)):
        if not shape.fullmatch(v):
            return {"unread": f"its {what} {json.dumps(v)} is not one crew reads"}
    held = records()
    if isinstance(held, str):
        return {"unread": held}
    sid = session_in(held, agent, session, pane)
    if sid is None:
        return {"session": None, "question": None}
    got = read(sid)
    return got if "unread" in got else {"session": sid, **got}


def answer(args):
    """What the command line's arguments ask, or None when they are not one of its forms."""
    if len(args) == 1:
        return read(args[0])
    if len(args) == 4 and args[0] == "--pane":
        return by_pane(*args[1:])
    return None


if __name__ == "__main__":
    got = answer(sys.argv[1:])
    if got is None:
        sys.exit("usage: questions.py <session id> | --pane <herdr session> <pane id> <agent>")
    print(json.dumps(got))
