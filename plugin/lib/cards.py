"""cards.py: a crew agent's Pending You card, posted, changed, closed and read through crew (briefs.16, ADR 0005 as
amended 2026-10-12).

crew speaks to Pending You as the asking assistant through the fleet's `pendingyou mcp --app claude-code`, a stdio MCP
server that passes each line on to Pending You under the host's sign-in: one JSON-RPC message a line each way, with the
token, its refresh and the MCP session kept inside it. Each crew command opens one session, introduces the agent with
`whoami`, does its act and ends, so a session that failed leaves nothing for the next. A reply is read as Pending You's
own CLI reads it (its dist/bridge.js, 0.28.0): structuredContent, else the first text block that is a JSON object; a
refusal is a result marked isError, whose first text block is Pending You's words.

Everything here but Bridge and the reads named so is a decision: a function of plain facts that starts no process
(code.7)."""
import importlib.machinery, importlib.util, json, os, pathlib, re, select, subprocess, time

from crew import fail

BRIDGE = ("pendingyou", "mcp", "--app", "claude-code")
PROTOCOL = "2025-06-18"  # the MCP revision Pending You's CLI opens its sessions with
CALL = 60  # seconds a call waits for its reply: what Claude Code's own transport waited on 2026-10-09
CLOSE = 5  # seconds the bridge is given to end once its input is closed
SIGNED_OUT = -32001  # the bridge's code when this computer has no sign-in, or its sign-in has ended
WORDS = 300  # the most of Pending You's words a refusal carries, as its CLI cuts them
# What crew sets on a card, never the agent: the key is the card key, the session the agent's, the area its kit's.
CREW_FIELDS = ("idempotencyKey", "areaId", "session")
# What crew sets on a change, read from the run record and from Pending You.
CHANGE_FIELDS = ("requestId", "name", "expectedVersion")
REQUEST_ID = re.compile(r"^req_[A-Za-z0-9-]{1,40}$")
AREA_ID = re.compile(r"^prj_[A-Za-z0-9_-]{1,80}$")
TINTS = ("peri", "sage", "peach", "sun", "lilac", "sky", "mint", "rose")
DAYS = 30  # how far back the run record is read for a key's card, as the card hook reads a close's post
HOOK = pathlib.Path(__file__).resolve().parent.parent / "hooks" / "cards"
_hook = None


def hook():
    """crew's card hook, loaded as a module: its key and form checks are the ones `crew card post` and `change` apply,
    so a card refused through Pending You's tools is refused through crew alike, until every-crew-card-goes-through-crew
    builds a row's card instead."""
    global _hook
    if _hook is None:
        loader = importlib.machinery.SourceFileLoader("crew_card_hook", str(HOOK))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        _hook = importlib.util.module_from_spec(spec)
        loader.exec_module(_hook)
    return _hook


def hook_refusal(tool, given):
    """The hook's words refusing a Pending You call it is given before it runs, or None: as Claude Code would hand it
    the call, with no session id, so the agent is the one CREW_AGENT and CREW_LABEL name."""
    return hook().refusal({"tool_name": f"mcp__pendingyou__{tool}", "tool_input": given, "session_id": None})


def object_of(key):
    """The run record's object for a card key, as the hook records it: the row's, or None for a key that is no row's."""
    return hook().keyed(key)[1]


# ------------------------------------------------------------------------------------------------- decisions

def given(text, what, crew_fields):
    """The card or change an agent gives on standard input, as a JSON object; refused when it is not one, or when it
    sets a field crew sets itself."""
    try:
        got = json.loads(text)
    except ValueError as e:
        fail(f"crew could not read the {what} on standard input as JSON: {e}")
    isinstance(got, dict) or fail(f"the {what} on standard input is not a JSON object")
    mine = [f for f in crew_fields if f in got]
    not mine or fail(f"the {what} gives {', '.join(mine)}, which crew sets itself: leave {'it' if len(mine) == 1 else 'them'} out")
    return got


def remote_of(url):
    """A git remote's address as Pending You files an area by it, github.com/<owner>/<repo>, as its CLI's remoteOf
    makes it; None for one that names no repository."""
    plain = re.sub(r"^[a-z][a-z0-9+.-]*://", "", (url or "").strip(), flags=re.I)
    plain = re.sub(r"^[^@/]+@", "", plain)
    plain = re.sub(r"^([^/:]+):\d+/", r"\1/", plain)
    plain = re.sub(r"^([^/:]+):", r"\1/", plain)
    plain = re.sub(r"/{2,}", "/", plain)
    plain = re.sub(r"/+$", "", plain)
    plain = re.sub(r"\.git$", "", plain)
    return plain if re.fullmatch(r"[\w.-]+/[\w./-]+", plain) else None


def kit_of(remote):
    """The kit a remote names, <owner>/<repo>, as an area's key names it."""
    return remote.split("/", 1)[1]


def post_args(card, key, name, machine, cwd, area):
    """post_request's arguments: the agent's card, with crew's key, session and area."""
    return dict(card, idempotencyKey=key, areaId=area, session={"label": name, "machine": machine, "cwd": cwd})


def area_of(matched):
    """The area match_area chose for the card, or None when one is to be made: its first suggestion's, unless its
    decision is create, as Pending You's CLI reads it."""
    suggestions = [s for s in matched.get("suggestions") or [] if isinstance(s, dict)] if isinstance(matched, dict) else []
    top = suggestions[0].get("areaId") if suggestions else None
    if matched.get("decision") != "create" and isinstance(top, str) and AREA_ID.match(top):
        return top
    return None


def create_area_args(remote, label, matched):
    """create_area's arguments for the kit's area: under create-area:<owner>/<kit> (briefs.11), named for the kit, in
    the partition's group, with match_area's proposed tint, and the remote linked so later posts match it."""
    repo = remote.rsplit("/", 1)[1]
    tint = matched.get("proposedTint") if isinstance(matched, dict) else None
    return {"idempotencyKey": f"create-area:{kit_of(remote)}", "name": repo,
            "description": f"What crew's agents ask about {repo}.", "tint": tint if tint in TINTS else "sky",
            "group": label, "repo": {"remote": remote}}


def reply_object(result):
    """A tool's result as an object: its structuredContent, else its first text block that parses as a JSON object;
    None when it holds neither."""
    if not isinstance(result, dict):
        return None
    if isinstance(result.get("structuredContent"), dict):
        return result["structuredContent"]
    for block in result.get("content") or []:
        if isinstance(block, dict) and isinstance(block.get("text"), str):
            try:
                parsed = json.loads(block["text"])
            except ValueError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def refused_by(result):
    """Pending You's words refusing a call, or None when the result is no refusal."""
    if not isinstance(result, dict) or result.get("isError") is not True:
        return None
    for block in result.get("content") or []:
        if isinstance(block, dict) and isinstance(block.get("text"), str) and block["text"].strip():
            return block["text"].strip()[:WORDS]
    return "Pending You refused it, and said nothing more"


def bridge_said(error):
    """What crew says of the bridge's own error, a JSON-RPC error object: its words up to any `Run:`, since the fleet's
    pendingyou is never run from npm (ADR 0005), and for a missing sign-in, whose it is to redo."""
    code = error.get("code") if isinstance(error, dict) else None
    words = error.get("message") if isinstance(error, dict) and isinstance(error.get("message"), str) else ""
    words = re.split(r"\s+Run:", words, maxsplit=1)[0].strip().rstrip(".")
    if code == SIGNED_OUT:
        return (f"this host can't ask through Pending You: {words or 'it is not signed in'}. The user signs it in with "
                "pendingyou-signin")
    return f"crew could not reach Pending You: {words or 'its bridge gave no reason'}"


def card_under(entries, key, by):
    """The card the agent `by` holds under a key: its newest card.post under the key, done and naming a card, that no
    later card.close of that card closes; None when there is none. entries are in the order they were written."""
    held = None
    for e in entries:
        act, card = e.get("Act"), e.get("Card")
        if act == "card.post" and not e.get("Refused") and e.get("Key") == key and e.get("By") == by and card:
            held = card
        elif act == "card.close" and not e.get("Refused") and card == held:
            held = None
    return held


def lost(words):
    """Whether Pending You's refusal says it no longer finds the card: what a card posted under another sign-in reads
    as to its owner once the host has signed in again (ADR 0005 as amended 2026-10-11)."""
    return isinstance(words, str) and words.lower().startswith("not found")


def lost_said(key, card, words):
    """The refusal of a change, close or read of a lost card: the card is still the user's to see, but no longer its
    owner's to reach, so the row's card is posted again under the key, the summary saying the older copy is dead."""
    return (f"card {card} under {key} is lost to its owner (Pending You: \"{words}\"): it was posted under another "
            "sign-in than this host's, and the user may still see it and answer it, to nobody. While the row still waits, "
            f"post its card again with crew card post {key}, its summary saying an older copy is dead and to dismiss it in "
            "the app")


def version_of(got, card):
    """A card's version, as get_request gives it; refused when it gives none, since a change or an ack needs it."""
    v = got.get("version") if isinstance(got, dict) else None
    isinstance(v, int) and not isinstance(v, bool) or fail(f"Pending You gave no version for {card}, so crew can't change it")
    return v


def request_id(got, tool):
    """The card's id in a reply, refused as unread when it is missing or not a card's."""
    card = got.get("requestId") if isinstance(got, dict) else None
    isinstance(card, str) and REQUEST_ID.match(card) or fail(f"Pending You's answer to {tool} names no card: crew can't tell what it did")
    return card


def text_of(v):
    """A field's words, or None for anything else: a note may come as words or as an object holding them."""
    if isinstance(v, dict):
        v = v.get("text")
    return v.strip() if isinstance(v, str) and v.strip() else None


def answer_lines(key, card, got):
    """What `crew card read` prints of a card get_request gave: its status and whose turn it is, then, on the agent's
    turn, the answer and the user's words, and every message after; what the reply leaves out is left out."""
    status, turn = got.get("status"), got.get("turn")
    head = f"card {key}: {card}"
    if isinstance(status, str):
        head += f", {status}"
    if turn == "agent":
        head += ", your turn: the user has answered"
    elif turn == "you":
        head += ", waiting on the user"
    lines = [head]
    answer = got.get("answer") if turn == "agent" and isinstance(got.get("answer"), dict) else {}
    picked = [c for c in answer.get("choiceIds") or [] if isinstance(c, str)]
    if picked:
        lines.append(f"  picked: {', '.join(picked)}")
    if isinstance(answer.get("approved"), bool):
        lines.append(f"  approved: {'yes' if answer['approved'] else 'no'}")
    for q, a in (answer.get("answers") or {}).items() if isinstance(answer.get("answers"), dict) else []:
        said = a if isinstance(a, str) else ", ".join(c for c in a.get("choiceIds") or [] if isinstance(c, str)) if isinstance(a, dict) else ""
        if isinstance(a, dict) and isinstance(a.get("approved"), bool):
            said = "approved" if a["approved"] else "declined"
        if said:
            lines.append(f"  {q}: {said}")
    if answer.get("done") is True:
        lines.append("  done")
    if isinstance(answer.get("failedStep"), int):
        lines.append(f"  step {answer['failedStep']} did not work")
    if answer.get("handled") is True:
        lines.append("  the user will handle it themselves")
    for label, v in (("words", answer.get("text")), ("note", answer.get("note"))):
        if text_of(v):
            lines.append(f"  {label}: {text_of(v)}")
    for m in got.get("messages") or []:
        said = text_of(m.get("body")) or text_of(m.get("text")) if isinstance(m, dict) else None
        if said:
            who = m.get("from") or m.get("by")
            lines.append(f"  {who if isinstance(who, str) else 'message'}: {said}")
    if isinstance(got.get("url"), str):
        lines.append(f"  {got['url']}")
    return lines


# ------------------------------------------------------------------------------------- reads and the bridge

def host_entries(record, label, host):
    """This host's run record entries for the label, the last DAYS days', oldest first: an owner posts from its own
    host, so its card acts are here before they reach the branch."""
    import datetime
    d = record.ROOT / label / "runs" / host
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=DAYS)).isoformat()
    out = []
    for f in sorted(d.glob("*.rec")) if d.is_dir() else []:
        if f.stem >= since:
            out += record.parse(f.read_text())
    return out


def git_remote(cwd):
    """The origin remote of the folder a command runs in, as Pending You files by it, or None."""
    try:
        r = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return remote_of(r.stdout.splitlines()[0]) if r.returncode == 0 and r.stdout.strip() else None


class Bridge:
    """One session with Pending You through the fleet's `pendingyou mcp`, as the agent `name`: opened with initialize
    and whoami, each call waiting CALL seconds for its reply. Every failure is a Refusal that ends with `later`, what to
    do about it; `held`, the (key, card) a change, close or read acts on, turns Pending You's "not found" into the lost
    card's refusal."""

    def __init__(self, name, later, held=None):
        self.name, self.later, self.held, self.buf, self.next, self.proc = name, later, held, b"", 0, None

    def __enter__(self):
        try:
            self.proc = subprocess.Popen(BRIDGE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        except OSError as e:
            fail(f"crew could not start Pending You's bridge, `{' '.join(BRIDGE)}`: {e.strerror or e}. {self.later}")
        try:
            self.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                        "clientInfo": {"name": "crew", "version": "1"}})
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            self.call("whoami", {"name": self.name})
        except BaseException:
            self.end()
            raise
        return self

    def __exit__(self, *exc):
        self.end()

    def end(self):
        if not self.proc:
            return
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            self.proc.wait(timeout=CLOSE)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self.proc.stdout.close()
        self.proc = None

    def send(self, message):
        try:
            self.proc.stdin.write((json.dumps(message) + "\n").encode())
            self.proc.stdin.flush()
        except OSError as e:
            self.end()
            fail(f"crew could not write to Pending You's bridge: {e.strerror or e}. {self.later}")

    def line(self, what, deadline):
        fd = self.proc.stdout.fileno()
        while b"\n" not in self.buf:
            left = deadline - time.monotonic()
            if left <= 0:
                self.end()
                fail(f"Pending You did not answer {what} within {CALL} seconds. {self.later}")
            ready, _, _ = select.select([fd], [], [], left)
            if not ready:
                continue
            chunk = os.read(fd, 65536)
            if not chunk:
                self.end()
                fail(f"Pending You's bridge ended before it answered {what}. {self.later}")
            self.buf += chunk
        line, _, self.buf = self.buf.partition(b"\n")
        return line

    def request(self, method, params, what=None):
        """One request's reply message, matched by its id; other lines are skipped."""
        self.next += 1
        rid, what = f"crew-{self.next}", what or method
        self.send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        deadline = time.monotonic() + CALL
        while True:
            try:
                m = json.loads(self.line(what, deadline))
            except ValueError:
                continue
            if isinstance(m, dict) and m.get("id") == rid and "method" not in m:
                break
        if isinstance(m.get("error"), dict):
            self.end()
            fail(f"{bridge_said(m['error'])}. {self.later}")
        return m.get("result")

    def call(self, tool, args):
        """A Pending You tool's answer, as an object; refused in Pending You's words when it refuses, or as unread
        when it answers with no object."""
        result = self.request("tools/call", {"name": tool, "arguments": args}, tool)
        words = refused_by(result)
        if words is not None and self.held and lost(words):
            fail(lost_said(*self.held, words))
        if words is not None:
            fail(f"Pending You refused {tool}: {words}")
        got = reply_object(result)
        got is not None or fail(f"Pending You answered {tool} with nothing crew can read. {self.later}")
        return got
