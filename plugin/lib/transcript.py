#!/usr/bin/env python3
"""transcript.py: what crew reads of a Claude Code transcript, to check the excerpt a signal quotes and find the one
record that holds it.

Claude Code keeps each session's transcript at ~/.claude*/projects/<folder>/<session id>.jsonl (each account keeps
its own directory, ~/.claude-sub-<name>/), one JSON value per line, in a format it does not document and may change.
crew leans on it as little as it can: it parses each line as JSON and walks every string in it, knowing no field
name. It knows three facts of the format: a top-level type of user marks a record the session received, one of
assistant a record the agent wrote itself, and one of api-request-blob Claude Code's copy of a message it sent the
model, the agent's own among them, read from Claude Code 2.1.303's transcript of session
f965a6bb-1725-4522-8d49-576f4bb1fc50, a chore's verify of 2026-10-20, on deneb on 2026-10-22. When any stops holding, a
grade falls; nothing that is not a paraphrase is refused, and no capture is stopped: when the copy's type changes, a
quote of the agent's own earlier words grades found again.

Who asserted the words is read from the mark crew puts on what it sends, and a stage's own prompt, which crew cannot
mark, from its form: `Fix: …`, a chore's `Chore <name>: …` and `Verify chore <name>: …`, the merge line, and the /opsx:
commands, which Claude Code records as a string holding <command-name>/opsx:apply</command-name> and
<command-args>…</command-args>, the skill's text following in the next record received, ending ARGUMENTS: and the same
words. When these stop holding, a stage's words are read as the user's.

Claude Code writes a tool call's record only once the tool returns, so the running crew signal is never in the
transcript it reads. What shows crew it is reading the live session is the record before it, the user's message or
the last tool's output, written moments earlier: a transcript whose last record is older than FRESH may be another
session's, such as the one before a /clear, and is not searched.

  verified    the excerpt is in a record the session received; who asserted it is read as far as crew can
  found       it is in the transcript, in a record crew cannot classify
  unverified  crew could not read the transcript, or it is not the live session's, with the reason
  refused     the transcript is the live session's, and the excerpt is nowhere in it but in crew signal commands, in
              what the agent wrote itself, or Claude Code's copies of what it sent the model: a paraphrase

A wait on a stage reads the same transcript for the work the agent started in the background and is still waiting on
(pending), and for when the session last wrote (last_at). It knows two more facts of the format, read from Claude Code
2.1.286's transcript of session f9b10eee-83e1-4c51-991f-820f7a2fe367, a coder that ran suites in the background on
2026-10-08: a Bash call run in the background is answered by a record whose toolUseResult holds
"backgroundTaskId": "<id>"; and when that work ends, the session receives a string holding <task-notification> with
<task-id><id></task-id> in it, recorded as a queue-operation and again as an attachment. When these stop holding, a
quiet agent waiting on its own work reads as waiting on nothing, and is reported stuck sooner; never as finished.

It reads there too whether the session's turn is over (turn_over), by two facts read from Claude Code 2.1.307's
transcripts of 80 sessions on deneb of 2026-10-22 and 23: every record the model writes, of type assistant, carries
message.stop_reason, tool_use while its turn goes on and end_turn on the message that ends it (237 turns ended so, no
other value seen); and a record of type user follows it only once the session is sent something, its next prompt or a
background task's notice. A record of a subagent's, isSidechain true, is neither. When these stop holding, no turn
reads as over, and a verify whose agent has finished with no report is reported stuck at crew's limit instead.

When crew sends an agent a prompt, a stage's or a greeting, it reads here whether Claude received
it (teams.15). Run on the agent's host, sent there as questions.py is, it answers one JSON object and writes nothing:

  python3 - end <session>                      where the session's transcript ends: {"path": <path>, "size": <bytes>},
                                               {"path": null, "size": 0} when it has none yet, or {"unread": "<what>"}
  python3 - received <session> <offset> <text> whether a complete line past that many bytes is the prompt as Claude
                                               received it: {"received": true|false}, or {"unread": "<what>"}

It knows four more facts of the format, read from Claude Code 2.1.292's transcripts of a construct's session 0bd4a771
of 2026-10-10 and swc-2-conductor's session e78bbab4 of 2026-10-08: a fresh session's transcript does not exist until
its first prompt, its SessionStart hook's record written with the prompt's; a plain prompt is a record of type user
whose message.content is the text as sent, crew's mark included; a slash command is a user record holding
<command-name>/<command></command-name> and <command-args>, the arguments as typed; and a prompt sent while the agent
works is recorded at once as {"type": "queue-operation", "operation": "enqueue", "content": "<text>"}, then as a user
record when Claude submits it. When these stop holding, no prompt reads as received: crew sends each twice and reports
its stage as never started, loudly, never as a stage that began."""
import datetime, json, pathlib, re, sys

# A crew signal command line that carries an excerpt, the agent's own or an echo of it: from `crew signal` to the end of
# its line, a backslash-newline running it on, when a word after it starts --excerpt.
COMMAND = re.compile(r"crew signal(?:\\\n|.)*?(?<!\S)--excerpt(?:\\\n|.)*")
TELL = re.compile(r"^\[crew tell from ([^\]\s]+)\]")
# How a tell's sender ends when it carries the user's word from the board, crew tell --board's <user>@board (record
# 0038 §3): the user's words, which answer nothing.
BOARD = "@board"
# A stage's own prompt, as crew's run_stage sends it: a fix, a chore's code or verify, a merge, or construct, code and
# verify as slash commands. A merge is a submission to the bolt through sluice; one sent before record 0026 merged with
# wt merge, and a transcript of then still reads as the conductor's.
STAGE = re.compile(r"^(Fix: |Chore \S+: |Verify chore \S+: |Merge \S+ into bolt/\S+: wt (?:submit bolt/\S+|merge bolt/\S+ --no-squash) --no-remove)")
SLASH = re.compile(r"<command-name>/opsx:(propose|apply|verify)</command-name>")
ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
FRESH = datetime.timedelta(minutes=15)
# The types of the lines that hold the agent's own writing: its records, and api-request-blob, Claude Code's copy of
# each message it sends the model (2.1.303, session f965a6bb).
WROTE = {"assistant", "api-request-blob"}
NOTICE = "<task-notification>"
TASK_ID = re.compile(r"<task-id>(.*?)</task-id>", re.S)
SESSION = re.compile(r"[A-Za-z0-9._:-]+")
# A prompt that is a slash command: the command, then its arguments.
COMMAND_LINE = re.compile(r"/(\S+)(?:\s+(.*))?", re.S)


def collapse(s):
    """A string with every run of whitespace one space, so a quotation matches across line breaks and indents."""
    return " ".join(s.split())


def find(session):
    """A session's transcript: the first of ~/.claude*/projects/*/<session id>.jsonl, or None."""
    if not session or not SESSION.fullmatch(session):
        return None
    found = sorted(pathlib.Path.home().glob(f".claude*/projects/*/{session}.jsonl"))
    return found[0] if found else None


def searched(s):
    """The pieces of a string the search reads: all of it but the crew signal command lines in it that carry an
    excerpt, whose --excerpt holds the words too. A message or an output that only mentions crew signal is read whole."""
    return COMMAND.split(s)


def strings(v):
    """Every string of a JSON value, keys aside, in the order written."""
    if isinstance(v, str):
        yield v
    elif isinstance(v, (list, dict)):
        for x in (v.values() if isinstance(v, dict) else v):
            yield from strings(x)


def stamp(at):
    """A record's timestamp as a UTC time, or None when it has none crew can read."""
    try:
        t = datetime.datetime.fromisoformat(at.replace("Z", "+00:00")) if isinstance(at, str) and at else None
    except ValueError:
        return None
    return (t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)).astimezone(datetime.timezone.utc) if t else None


def last_written(path, found):
    """When the session last wrote its transcript: the time of its last complete line that carries a timestamp, else
    the file's modification time."""
    for _, _, v in reversed(found):
        t = stamp(v.get("timestamp")) if isinstance(v, dict) else None
        if t:
            return t
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc)


def kind(value):
    """A record's top-level type, or None for a line that has none."""
    return value.get("type") if isinstance(value, dict) else None


class Verdict:
    """What the check found: the grade, its reason when unverified, and for verified and found the source record:
    its line as written, its number, its uuid and time when it has them, who asserted the excerpt, and whether the
    record is the user's word from the board, a tell from <user>@board."""

    def __init__(self, grade, reason=None, raw=None, n=None, value=None, asserted_by="unknown", board=False):
        self.grade, self.reason, self.raw, self.n, self.asserted_by, self.board = grade, reason, raw, n, asserted_by, board
        v = value if isinstance(value, dict) else {}
        self.uuid = v["uuid"] if isinstance(v.get("uuid"), str) and v["uuid"] else None
        self.at = v["timestamp"] if isinstance(v.get("timestamp"), str) and v["timestamp"] else None

    def line_hash(self):
        """The source line's sha256, in hex: a record's name where it has no uuid."""
        import hashlib
        return hashlib.sha256(self.raw).hexdigest()


def unverified(reason):
    return Verdict("unverified", reason)


def lines(path, start=0):
    """The transcript's complete lines, as (number, the line's bytes, its JSON value), a trailing partial line left
    out, since Claude Code may be writing it; or the reason it can't be read. With start, only the lines that begin at
    that many bytes in or later, numbered from there."""
    try:
        data = path.read_bytes()
    except OSError as e:
        return f"the transcript {path} can't be read: {e.strerror or e}"
    if start:  # a line that began before start is not read, though it ends after it
        data = data[start:] if data[start - 1:start] == b"\n" else data[start:].partition(b"\n")[2]
    out = []
    parts = data.split(b"\n")
    for n, raw in enumerate(parts[:-1], 1):  # the last part is empty, or a line not yet finished
        if not raw.strip():
            continue
        try:
            out.append((n, raw, json.loads(raw.decode("utf-8"))))
        except (UnicodeDecodeError, ValueError):
            return "the transcript is not JSON lines"
    return out


def stage_args(s):
    """The words of a stage's /opsx: command, as Claude Code records the command, or None for any other string."""
    text = s.lstrip()
    m = ARGS.search(text) if text.startswith("<command-") and SLASH.search(text) else None
    return m.group(1) if m else None


def asserter(value, hit, stage_by=None, expansion=False):
    """Who asserted a received record's excerpt, from the record and the string that holds it: a tool, for a record
    holding a tool_result block; the agent crew tell names, or the user when that names <user>@<host>; crew, for
    crew's own message; stage_by, the conductor whose stage the session runs, for the stage's own prompt or the
    expansion of its command; otherwise the user."""
    if holds_tool_result(value):
        return "tool"
    text = hit.lstrip()
    m = TELL.match(text)
    if m:
        return "user" if "@" in m.group(1) else f"agent:{m.group(1)}"
    if text.startswith("[crew]"):
        return "crew"
    if stage_by and (expansion or STAGE.match(text) or stage_args(text) is not None):
        return f"agent:{stage_by}"
    return "user"


def from_board(hit):
    """Whether the string that holds an excerpt is a tell from the board, its sender <user>@board."""
    m = TELL.match(hit.lstrip())
    return bool(m) and m.group(1).endswith(BOARD)


def holds_tool_result(v):
    """Whether a JSON value holds a tool_result block anywhere: a record of a tool's output."""
    if isinstance(v, dict):
        return v.get("type") == "tool_result" or any(holds_tool_result(x) for x in v.values())
    if isinstance(v, list):
        return any(holds_tool_result(x) for x in v)
    return False


def check(session, excerpt, skip=(), stage_by=None, want=None):
    """Look for the excerpt in the session's transcript, whitespace aside, once it shows it is the live session's: its
    last record written within FRESH. The crew signal command lines that carry an excerpt are crew's commands and their
    echoes, lines of type assistant what the agent wrote and lines of type api-request-blob Claude Code's copies of
    what it sent the model, the agent's own among them, and lines that name a path in skip the writing of the excerpt's
    file: none of them is searched, and the rest of a string that holds such a command line is. stage_by is
    the conductor whose stage the session runs, None for a session that runs none, where a prompt of a stage's form is
    the user's. The source is the last received record that holds the excerpt; with want="user", the last one the user
    asserted, so that a later echo of the user's words in a tool's output or a tell does not hide them, one not from the
    board before one that is, so the same words typed in the pane count however the board's word fell beside them, and
    the last received record only when the user asserted none. Returns a Verdict; refused is one too."""
    if not session:
        return unverified("herdr names no session")
    path = find(session)
    if path is None:
        return unverified(f"no transcript for session {session}")
    found = lines(path)
    if isinstance(found, str):
        return unverified(found)
    try:
        age = datetime.datetime.now(datetime.timezone.utc) - last_written(path, found)
    except OSError as e:
        return unverified(f"the transcript {path} can't be read: {e.strerror or e}")
    if age > FRESH:
        return unverified(f"session {session}'s transcript has not been written for {int(age.total_seconds() // 60)} "
                          "minutes: crew may be reading another session's")
    needle = collapse(excerpt)
    received = received_user = received_board = other = args = None  # args: the words of the stage command just received, which its expansion ends with
    for n, raw, v in found:
        if kind(v) in WROTE:
            continue
        every = list(strings(v))
        expansion = False
        if kind(v) == "user":
            expansion = args is not None and any(collapse(s).endswith(collapse(f"ARGUMENTS: {args}")) for s in every)
            args = next((x for x in map(stage_args, every) if x is not None), None)
        if any(p in s for s in every for p in skip):
            continue
        hits = [s for s in every if any(needle in collapse(p) for p in searched(s))]
        if not hits:
            continue
        if kind(v) == "user":
            received = (n, raw, v, hits, expansion)
            if asserter(v, hits[-1], stage_by, expansion) == "user":
                if from_board(hits[-1]):
                    received_board = received
                else:
                    received_user = received
        else:
            other = (n, raw, v, hits)
    if want == "user" and (received_user or received_board):
        received = received_user or received_board
    if received:
        n, raw, v, hits, expansion = received
        by = asserter(v, hits[-1], stage_by, expansion)
        return Verdict("verified", raw=raw, n=n, value=v, asserted_by=by, board=by == "user" and from_board(hits[-1]))
    if other:
        n, raw, v, _ = other
        return Verdict("found", raw=raw, n=n, value=v)
    return Verdict("refused")


def pending(path):
    """The background work the session started and has not been told is over: the ids of every toolUseResult's
    backgroundTaskId with no <task-id> naming it in a string holding <task-notification>, in the order started. None,
    never an empty list, when the transcript is missing or can't be read."""
    found = lines(path) if path else None
    if found is None or isinstance(found, str):
        return None
    started, told = [], set()
    for _, _, v in found:
        r = v.get("toolUseResult") if isinstance(v, dict) else None
        tid = r.get("backgroundTaskId") if isinstance(r, dict) else None
        if isinstance(tid, str) and tid and tid not in started:
            started.append(tid)
        for x in strings(v):
            if NOTICE in x:
                told.update(TASK_ID.findall(x))
    return [t for t in started if t not in told]


def started_commands(path):
    """The command of each background task the session started, by the task's id: the Bash call's command whose result
    names the task (toolUseResult's backgroundTaskId, its tool_result's tool_use_id the call's id), None for a task whose
    call can't be found or ran no command. None, never an empty dict, when the transcript is missing or can't be read."""
    found = lines(path) if path else None
    if found is None or isinstance(found, str):
        return None
    calls, out = {}, {}
    for _, _, v in found:
        content = (v.get("message") or {}).get("content") if isinstance(v, dict) and isinstance(v.get("message"), dict) else None
        for c in content if isinstance(content, list) else []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and isinstance(c.get("id"), str):
                command = (c.get("input") or {}).get("command") if isinstance(c.get("input"), dict) else None
                calls[c["id"]] = command if isinstance(command, str) else None
        r = v.get("toolUseResult") if isinstance(v, dict) else None
        tid = r.get("backgroundTaskId") if isinstance(r, dict) else None
        if not (isinstance(tid, str) and tid):
            continue
        used = [c.get("tool_use_id") for c in (content if isinstance(content, list) else [])
                if isinstance(c, dict) and c.get("type") == "tool_result"]
        out[tid] = next((calls.get(u) for u in used if u in calls), None)
    return out

def last_at(path):
    """When the session last wrote its transcript: the newest timestamp of any of its records, as a UTC time. None when
    the transcript is missing or can't be read, or no record carries a time crew can read."""
    found = lines(path) if path else None
    if found is None or isinstance(found, str):
        return None
    times = [t for t in (stamp(v.get("timestamp")) for _, _, v in found if isinstance(v, dict)) if t]
    return max(times) if times else None


def turn_over(path):
    """When the session's turn ended, with nothing sent to it since: the time of its last record of type user or
    assistant, not a subagent's, when that record is the model's and ended its turn (message.stop_reason end_turn).
    None while a turn goes on, or when the transcript is missing or can't be read, or that record carries no time crew
    reads."""
    found = lines(path) if path else None
    if found is None or isinstance(found, str):
        return None
    said = [v for _, _, v in found if kind(v) in ("user", "assistant") and not v.get("isSidechain")]
    last = said[-1] if said else None
    message = last.get("message") if last and kind(last) == "assistant" else None
    if not isinstance(message, dict) or message.get("stop_reason") != "end_turn":
        return None
    return stamp(last.get("timestamp"))


def unnamed(session):
    """What crew can't read of a session it is not given an id it reads, or None."""
    return None if session and SESSION.fullmatch(session) else f"session id {json.dumps(session)} is not one crew reads"


def end(session):
    """Where a session's transcript ends, noted before crew sends it a prompt: its path and length in bytes, no path
    and 0 when it has none yet, or what could not be read."""
    if unnamed(session):
        return {"unread": unnamed(session)}
    path = find(session)
    if path is None:
        return {"path": None, "size": 0}
    try:
        return {"path": str(path), "size": path.stat().st_size}
    except OSError as e:
        return {"unread": f"the transcript {path} can't be read: {e.strerror or e}"}


def received(session, offset, text):
    """Whether the session received the prompt crew sent as text, in a complete line of its transcript that begins
    offset bytes in or later: a record of type user any of whose strings holds the text, whitespace collapsed; for a
    text that is a slash command, a user record holding <command-name>/<command></command-name> whose <command-args>
    are the text's arguments, whitespace collapsed; or a queue-operation enqueue whose content holds the text. A record
    of type assistant never counts, and a session with no transcript yet has received nothing."""
    if unnamed(session):
        return {"unread": unnamed(session)}
    path = find(session)
    if path is None:
        return {"received": False}
    found = lines(path, offset)
    if isinstance(found, str):
        return {"unread": found}
    needle = collapse(text)
    m = COMMAND_LINE.fullmatch(text.strip())
    name, args = (f"<command-name>/{m.group(1)}</command-name>", collapse(m.group(2) or "")) if m else (None, None)
    for _, _, v in found:
        if kind(v) == "user":
            for s in strings(v):
                if needle in collapse(s):
                    return {"received": True}
                a = ARGS.search(s) if name and s.lstrip().startswith("<command-") and name in s else None
                if a and collapse(a.group(1)) == args:
                    return {"received": True}
        elif (kind(v) == "queue-operation" and v.get("operation") == "enqueue" and isinstance(v.get("content"), str)
              and needle in collapse(v["content"])):
            return {"received": True}
    return {"received": False}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["end"] and len(a) == 2:
        print(json.dumps(end(a[1])))
    elif a[:1] == ["received"] and len(a) == 4 and a[2].isdigit():
        print(json.dumps(received(a[1], int(a[2]), a[3])))
    else:
        sys.exit("usage: transcript.py end <session> | received <session> <offset> <text>")
