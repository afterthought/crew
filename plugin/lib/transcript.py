#!/usr/bin/env python3
"""transcript.py: what crew reads of a Claude Code transcript, to check the excerpt a signal quotes and find the one
record that holds it.

Claude Code keeps each session's transcript at ~/.claude*/projects/<folder>/<session id>.jsonl (each account keeps
its own directory, ~/.claude-sub-<name>/), one JSON value per line, in a format it does not document and may change.
crew leans on it as little as it can: it parses each line as JSON and walks every string in it, knowing no field
name. It knows two facts of the format: a top-level type of user marks a record the session received, and one of
assistant a record the agent wrote itself. When either stops holding, a grade falls; nothing that is not a paraphrase
is refused, and no capture is stopped.

  verified    the excerpt is in a record the session received; who asserted it is read as far as crew can
  found       it is in the transcript, in a record crew cannot classify
  unverified  crew could not read the transcript, with the reason
  refused     crew sees its own running command in the transcript, and the excerpt nowhere but there and in what
              the agent wrote itself: a paraphrase"""
import hashlib, json, pathlib, re

COMMAND = "crew signal"
TELL = re.compile(r"^\[crew tell from ([^\]\s]+)\]")


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


def asserter(value, hit):
    """Who asserted a received record's excerpt, from the record and the string that holds it: a tool, for a record
    holding a tool_result block; the agent crew tell names, or the user when that names <user>@<host>; crew, for
    crew's own message; otherwise the user."""
    if holds_tool_result(value):
        return "tool"
    text = hit.lstrip()
    m = TELL.match(text)
    if m:
        return "user" if "@" in m.group(1) else f"agent:{m.group(1)}"
    if text.startswith("[crew]"):
        return "crew"
    return "user"


def holds_tool_result(v):
    """Whether a JSON value holds a tool_result block anywhere: a record of a tool's output."""
    if isinstance(v, dict):
        return v.get("type") == "tool_result" or any(holds_tool_result(x) for x in v.values())
    if isinstance(v, list):
        return any(holds_tool_result(x) for x in v)
    return False


def check(session, slug, excerpt, skip=()):
    """Look for the excerpt in the session's transcript, whitespace aside. The canary is the running command: a string
    holding `crew signal` and the slug; without it crew cannot read this transcript. Strings holding `crew signal`
    are the command and its echoes, lines of type assistant what the agent wrote, and lines that name a path in skip
    the writing of the excerpt's file: none of them is searched. Returns a Verdict; refused is one too."""
    if not session:
        return unverified("herdr names no session")
    path = find(session)
    if path is None:
        return unverified(f"no transcript for session {session}")
    found = lines(path)
    if isinstance(found, str):
        return unverified(found)
    if not any(COMMAND in s and slug in s for _, _, v in found for s in strings(v)):
        return unverified("crew could not find its own command in the transcript")
    needle = collapse(excerpt)
    received = other = None
    for n, raw, v in found:
        if kind(v) == "assistant":
            continue
        every = list(strings(v))
        if any(p in s for s in every for p in skip):
            continue
        hits = [s for s in every if COMMAND not in s and needle in collapse(s)]
        if not hits:
            continue
        if kind(v) == "user":
            received = (n, raw, v, hits)
        else:
            other = (n, raw, v, hits)
    if received:
        n, raw, v, hits = received
        return Verdict("verified", raw=raw, n=n, value=v, asserted_by=asserter(v, hits[-1]))
    if other:
        n, raw, v, _ = other
        return Verdict("found", raw=raw, n=n, value=v)
    return Verdict("refused")
