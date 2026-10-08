#!/usr/bin/env python3
"""transcript.py: what crew reads of a Claude Code transcript, to check the excerpt a signal quotes and find the one
record that holds it.

Claude Code keeps each session's transcript at ~/.claude*/projects/<folder>/<session id>.jsonl (each account keeps
its own directory, ~/.claude-sub-<name>/), one JSON value per line, in a format it does not document and may change.
crew leans on it as little as it can: it parses each line as JSON and walks every string in it, knowing no field
name. It knows two facts of the format: a top-level type of user marks a record the session received, and one of
assistant a record the agent wrote itself. When either stops holding, a grade falls; nothing that is not a paraphrase
is refused, and no capture is stopped.

Who asserted the words is read from the mark crew puts on what it sends, and a stage's own prompt, which crew cannot
mark, from its form: `Fix: …`, the merge line, and the /opsx: commands, which Claude Code records as a string holding
<command-name>/opsx:apply</command-name> and <command-args>…</command-args>, the skill's text following in the next
record received, ending ARGUMENTS: and the same words. When these stop holding, a stage's words are read as the user's.

Claude Code writes a tool call's record only once the tool returns, so the running crew signal is never in the
transcript it reads. What shows crew it is reading the live session is the record before it, the user's message or
the last tool's output, written moments earlier: a transcript whose last record is older than FRESH may be another
session's, such as the one before a /clear, and is not searched.

  verified    the excerpt is in a record the session received; who asserted it is read as far as crew can
  found       it is in the transcript, in a record crew cannot classify
  unverified  crew could not read the transcript, or it is not the live session's, with the reason
  refused     the transcript is the live session's, and the excerpt is nowhere in it but in crew signal commands and
              in what the agent wrote itself: a paraphrase"""
import datetime, hashlib, json, pathlib, re

COMMAND = "crew signal"
TELL = re.compile(r"^\[crew tell from ([^\]\s]+)\]")
# A stage's own prompt, as crew's run_stage sends it: a fix, a merge, or construct, code and verify as slash commands.
STAGE = re.compile(r"^(Fix: |Merge \S+ into bolt/\S+: wt merge bolt/\S+ --no-squash --no-remove)")
SLASH = re.compile(r"<command-name>/opsx:(propose|apply|verify)</command-name>")
ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
FRESH = datetime.timedelta(minutes=15)


def collapse(s):
    """A string with every run of whitespace one space, so a quotation matches across line breaks and indents."""
    return " ".join(s.split())


def find(session):
    """A session's transcript: the first of ~/.claude*/projects/*/<session id>.jsonl, or None."""
    if not session or not re.fullmatch(r"[A-Za-z0-9._:-]+", session):
        return None
    found = sorted(pathlib.Path.home().glob(f".claude*/projects/*/{session}.jsonl"))
    return found[0] if found else None


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
    its line as written, its number, its uuid and time when it has them, and who asserted the excerpt."""

    def __init__(self, grade, reason=None, raw=None, n=None, value=None, asserted_by="unknown"):
        self.grade, self.reason, self.raw, self.n, self.asserted_by = grade, reason, raw, n, asserted_by
        v = value if isinstance(value, dict) else {}
        self.uuid = v["uuid"] if isinstance(v.get("uuid"), str) and v["uuid"] else None
        self.at = v["timestamp"] if isinstance(v.get("timestamp"), str) and v["timestamp"] else None

    def line_hash(self):
        """The source line's sha256, in hex: a record's name where it has no uuid."""
        return hashlib.sha256(self.raw).hexdigest()


def unverified(reason):
    return Verdict("unverified", reason)


def lines(path):
    """The transcript's complete lines, as (number, the line's bytes, its JSON value), a trailing partial line left
    out, since Claude Code may be writing it; or the reason it can't be read."""
    try:
        data = path.read_bytes()
    except OSError as e:
        return f"the transcript {path} can't be read: {e.strerror or e}"
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


def holds_tool_result(v):
    """Whether a JSON value holds a tool_result block anywhere: a record of a tool's output."""
    if isinstance(v, dict):
        return v.get("type") == "tool_result" or any(holds_tool_result(x) for x in v.values())
    if isinstance(v, list):
        return any(holds_tool_result(x) for x in v)
    return False


def check(session, excerpt, skip=(), stage_by=None):
    """Look for the excerpt in the session's transcript, whitespace aside, once it shows it is the live session's: its
    last record written within FRESH. Strings holding `crew signal` are crew's commands and their echoes, lines of type
    assistant what the agent wrote, and lines that name a path in skip the writing of the excerpt's file: none of them
    is searched. stage_by is the conductor whose stage the session runs, None for a session that runs none, where a
    prompt of a stage's form is the user's. Returns a Verdict; refused is one too."""
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
    received = other = args = None  # args: the words of the stage command just received, which its expansion ends with
    for n, raw, v in found:
        if kind(v) == "assistant":
            continue
        every = list(strings(v))
        expansion = False
        if kind(v) == "user":
            expansion = args is not None and any(collapse(s).endswith(collapse(f"ARGUMENTS: {args}")) for s in every)
            args = next((x for x in map(stage_args, every) if x is not None), None)
        if any(p in s for s in every for p in skip):
            continue
        hits = [s for s in every if COMMAND not in s and needle in collapse(s)]
        if not hits:
            continue
        if kind(v) == "user":
            received = (n, raw, v, hits, expansion)
        else:
            other = (n, raw, v, hits)
    if received:
        n, raw, v, hits, expansion = received
        return Verdict("verified", raw=raw, n=n, value=v, asserted_by=asserter(v, hits[-1], stage_by, expansion))
    if other:
        n, raw, v, _ = other
        return Verdict("found", raw=raw, n=n, value=v)
    return Verdict("refused")
