"""cards.py: crew's Pending You cards. The six of crew's own, built from the facts of their events (record 0031, briefs.13):
the proposal's, the batch's, the landing's, the deploy's, the step's and the record's, in the words rule's forms, each
following the card its thing follows when its own owner posted that card, and read by its owner through crew card read
(briefs.16). plan.py's act,
row_card_post, row_card_change and row_card_close, sends them; an agent's own question goes through Pending You's own
tools in its session, and crew's card hook records it.

crew speaks to Pending You as the asking assistant through the fleet's `pendingyou mcp --app claude-code`, a stdio MCP
server that passes each line on to Pending You under the host's sign-in: one JSON-RPC message a line each way, with the
token, its refresh and the MCP session kept inside it. Each crew command opens one session, introduces the agent with
`whoami`, does its act and ends, so a session that failed leaves nothing for the next. A reply is read as Pending You's
own CLI reads it (its dist/bridge.js, 0.28.0): structuredContent, else the first text block that is a JSON object; a
refusal is a result marked isError, whose first text block is Pending You's words.

Everything here but Bridge and the reads named so is a decision: a function of plain facts that starts no process
(code.7)."""
import json, os, re, select, struct, subprocess, time

import picture
from crew import fail
from picture import cut, wrap

BRIDGE = ("pendingyou", "mcp", "--app", "claude-code")
PROTOCOL = "2025-06-18"  # the MCP revision Pending You's CLI opens its sessions with
CALL = 60  # seconds a call waits for its reply: what Claude Code's own transport waited on 2026-10-09
AGENT = "crew"  # the User-Agent a picture is put with (put)
IMAGE_BYTES = 5_000_000  # the most an image put to a card may weigh: "up to 5 MB", Pending You's guide, read 2026-10-23
IMAGE_PIXELS = 8_000_000  # and its most pixels, "and 8 megapixels": a proposal of 20 rows or so is past it
CLOSE = 5  # seconds the bridge is given to end once its input is closed
SIGNED_OUT = -32001  # the bridge's code when this computer has no sign-in, or its sign-in has ended
WORDS = 300  # the most of Pending You's words a refusal carries, as its CLI cuts them
REQUEST_ID = re.compile(r"^req_[A-Za-z0-9-]{1,40}$")
AREA_ID = re.compile(r"^prj_[A-Za-z0-9_-]{1,80}$")
TINTS = ("peri", "sage", "peach", "sun", "lilac", "sky", "mint", "rose")
DAYS = 30  # how far back the run record is read for a key's card, as the card hook reads a close's post


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


def stranded(entries, key, owner, here):
    """The owner's newest card under a key when this host (here) can't reach it: one posted from another host, done and
    naming a card, that no later card.close of it closes, or one whose last close was as lost to its owner, on any
    host; None for a card posted here and still open, which its owner asks Pending You after, one closed any other
    way, a post that names no host, and none. A refused post or close changes nothing, as in card_under. entries are in
    the order they were written."""
    card, host, state = None, None, None
    for e in entries:
        if e.get("Refused") or not e.get("Card"):
            continue
        if e.get("Act") == "card.post" and e.get("Key") == key and e.get("By") == owner:
            card, host, state = e["Card"], e.get("Host"), None
        elif e.get("Act") == "card.close" and e["Card"] == card:
            state = e.get("State") or "closed"
    return card if state == "lost" or (card and state is None and host not in (None, here)) else None


def followed_open(entries, card, by):
    """The key under which the run record still holds open the agent `by`'s card a new post follows: the key of its
    newest card.post of that card, done, that no later card.close of the card closes, a close naming no key among
    them; None when it holds none. entries are in the order they were written."""
    key = None
    for e in entries:
        if e.get("Card") != card or e.get("Refused"):
            continue
        if e.get("Act") == "card.post" and e.get("By") == by:
            key = e.get("Key")
        elif e.get("Act") == "card.close":
            key = None
    return key


def lost(words):
    """Whether Pending You's refusal says it no longer finds the card: what a card posted under another sign-in reads
    as to its owner once the host has signed in again (ADR 0005 as amended 2026-10-11)."""
    return isinstance(words, str) and words.lower().startswith("not found")


def lost_said(key, card, words):
    """The refusal of a read of a lost card: the card is still the user's to see, but no longer its owner's to reach. A
    row's card, while its row still waits, the rail's next read posts again under the key, the summary saying the older
    copy is dead; a question its asker asks again, if it still matters."""
    again = ("While the row still waits, the rail's next read posts it again under its key, its summary saying an older "
             "copy is dead and to dismiss it in the app" if row_object(key) else
             "Ask it again if it still matters, saying in it that an older copy is dead and to dismiss it in the app")
    return (f"card {card} under {key} is lost to its owner (Pending You: \"{words}\"): it was posted under another "
            f"sign-in than this host's, and the user may still see it and answer it, to nobody. {again}")


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


# ------------------------------------------------------------------------------- a proposal's change, drawn

TEXT, SAYS = 40, 33  # the card's text, monospace lines of at most forty characters; what a block says, indented seven
COUNTS = (("dropped", "dropped"), ("amended", "amended"), ("new", "new"), ("moved", "moved"), ("split", "amended"))
CAPTION = "Struck and dashed: dropped, with its reason. Gold: amended, old intent struck above the new. Mint: new."


def plural(k, word):
    return f"{k} {word}" + ("" if k == 1 else "s")


def joined(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def by_words(text, width):
    """text cut by whole words to at most width characters, ending with … when it was cut."""
    text = " ".join(text.split())
    if len(text) <= width:
        return text
    head = text[:width - 1]
    return (head.rsplit(" ", 1)[0] if " " in head else head).rstrip(" ,;:") + "…"


def new_units(argvs):
    """The units and chores a proposal makes new to a bolt, in its order and once each: every one a `unit add` or
    `chore add` names, to a bolt or to the queue, which is the first the user hears of it, and every one a `unit move`
    or `chore move` puts into a bolt. Each is the user's to keep or leave out, row by row (plan.3, signals.7)."""
    return list(dict.fromkeys(a.unit for a in argvs if a.cmd in ("unit", "chore")
                              and (a.sub == "add" or (a.sub == "move" and a.bolt != "queue"))))


def chore_words(words):
    """A chore's words as a proposal's card says them beside its name, where a unit's intent goes: marked a chore's."""
    return f"Chore: {words}" if words else words


def put_back(now, was):
    """The units a group holds once approved, each it held before and no longer does put back where it stood: after
    the unit it followed, or first."""
    out = list(now)
    for i, u in enumerate(was):
        if u not in out:
            prev = next((was[j] for j in range(i - 1, -1, -1) if was[j] in out), None)
            out.insert(out.index(prev) + 1 if prev else 0, u)
    return out


def block(head, name, says):
    """One change in the card's text: its heading padded to seven and the unit or bolt, a heading longer than six on
    its own line with the name under it, then what it says, indented seven."""
    names = wrap(name, SAYS)
    if len(head) > 6:
        return [head] + ["       " + x for x in names] + ["       " + x for x in says]
    return [f"{head:<7}{names[0]}"] + ["       " + x for x in names[1:] + says]


def drawn(before, after, argvs):
    """A proposal's change, from the plan at the tip, the plan its commands leave and its commands, parsed: each bolt
    they touch and each kit's queue a unit goes to, before and after, as the picture's sections; the change as the
    card's text, lines of at most forty characters; the counts; and what the card says of each unit, its intent, why
    it is dropped, the intent an amendment replaces, the bolt a unit moved in comes from, the parts of a split. A
    function of those facts alone, no kit read (plan.12), shared by every proposal card crew builds."""
    where = {u.name(): u.get("Bolt") for u in before.work()}
    repo = {u.name(): u.get("Repo") for u in before.work()}
    # A chore's words are said as its intent, marked as a chore's, on the picture and in its option (plan.11).
    intent = {u.name(): chore_words(u.get("Intent")) if u.get("Kind") == "chore" else u.get("Intent") for u in before.work()}
    kits = {b.name(): b.get("Repo") for b in before.bolts()}
    goals = {b.name(): b.get("Goal") for b in before.bolts()}
    dropped, out, came_from, amended, split, parts, ordered, queued = {}, {}, {}, {}, {}, {}, set(), set()
    counts, bolt_moves, touched, order, blocks = dict.fromkeys(dict(COUNTS), 0), {}, set(), [], []

    def group(u):
        return ("bolt", where[u]) if where.get(u) else ("queue", repo[u])
    for a in argvs:
        key = ("unit" if a.cmd == "chore" else a.cmd, a.sub)  # a chore's command draws as the unit's
        if a.cmd in ("unit", "chore"):
            touched.add(a.unit)
        if key == ("bolt", "new"):
            kits[a.bolt], goals[a.bolt] = a.repo, a.goal
            secs, b = [("bolt", a.bolt)], block("NEW BOLT", a.bolt, wrap(a.goal, SAYS, 3))
        elif key == ("bolt", "order"):
            counts["moved"] += 1
            bolt_moves[a.bolt] = bolt_moves.get(a.bolt, 0) + 1
            secs, b = [("bolt", a.bolt)], block("ORDER BOLT", a.bolt, wrap(f"before {a.before}" if a.before else "first" if a.first else "last", SAYS))
        elif key == ("bolt", "drop"):
            units = [u for u, x in where.items() if x == a.bolt]
            secs = [("bolt", a.bolt)] + ([("queue", kits[a.bolt])] if a.requeue and units else [])
            for u in units:
                touched.add(u)
                if a.requeue:
                    out[u], where[u] = "to the queue", None
                    queued.add(u)
                    counts["moved"] += 1
                else:
                    dropped[u] = a.reason
                    counts["dropped"] += 1
            b = block("DROP BOLT", a.bolt, wrap(a.reason, SAYS, 3) + (["its units to the queue"] if a.requeue else []))
        elif key == ("unit", "add"):
            where[a.unit], repo[a.unit] = a.bolt, a.repo or kits.get(a.bolt)
            intent[a.unit] = chore_words(a.intent) if a.cmd == "chore" else a.intent
            counts["new"] += 1
            secs, b = [group(a.unit)], block("CHORE" if a.cmd == "chore" else "ADD", a.unit, wrap(a.intent, SAYS, 2))
        elif key == ("unit", "move"):
            src, to = where.get(a.unit), None if a.bolt == "queue" else a.bolt
            secs = ([("bolt", src)] if src else []) + [("bolt", to) if to else ("queue", repo[a.unit])]
            if src:
                out[a.unit] = f"to {to}" if to else "to the queue"
                counts["moved"] += 1
            if to:
                came_from.setdefault(a.unit, src)
                counts["new"] += 1
            else:
                queued.add(a.unit)
            where[a.unit] = to
            b = block("MOVE", a.unit, wrap(f"from {src or 'the queue'} to {to or 'the queue'}", SAYS))
        elif key == ("unit", "split"):
            counts["split"] += 1
            split.setdefault(a.unit, intent[a.unit])
            intent[a.unit] = a.intent
            for m, i in a.into:
                parts[m], where[m], repo[m], intent[m] = a.unit, where[a.unit], repo[a.unit], i
                touched.add(m)
            secs, b = [group(a.unit)], block("SPLIT", a.unit, wrap(a.intent, SAYS, 2) + list(dict.fromkeys(x for m, _ in a.into for x in wrap(f"into {m}", SAYS))))
        elif key == ("unit", "amend"):
            counts["amended"] += 1
            amended.setdefault(a.unit, intent[a.unit])
            intent[a.unit] = a.intent
            secs, b = [group(a.unit)], block("AMEND", a.unit, wrap(a.intent, SAYS, 3))
        elif key in (("unit", "order"), ("unit", "after")):
            counts["moved"] += 1
            ordered.add(a.unit)
            said = (("after " + ", ".join(a.deps) if a.deps else "after nothing") if a.sub == "after" else
                    f"before {a.before}" if a.before else "first" if a.first else "last")
            secs, b = [group(a.unit)], block(a.sub.upper(), a.unit, wrap(said, SAYS))
        else:  # unit drop
            counts["dropped"] += 1
            dropped[a.unit] = a.reason
            secs, b = [group(a.unit)], block("DROP", a.unit, wrap(a.reason, SAYS, 3))
        order += [s for s in secs if s not in order]
        blocks.append((secs[0], b))

    sections, lines = [], []
    for kind, name in order:
        if kind == "bolt":
            was = [u.name() for u in before.work_of(name)] if before.bolt(name) else []
            now = numbered = [u.name() for u in after.work_of(name)] if after.bolt(name) else []
            heading = name
            said = (f"a new bolt → {len(now)}" if not before.bolt(name) else f"{plural(len(was), 'unit')} → "
                    + (str(len(now)) if after.bolt(name) else "dropped"))
            line = (f"A new bolt; {plural(len(now), 'unit')} once approved" if not before.bolt(name) else
                    f"{plural(len(was), 'unit')} now; " + (f"{len(now)} once approved" if after.bolt(name) else "dropped once approved"))
        else:
            was_all, numbered = [u.name() for u in before.queue(name)], [u.name() for u in after.queue(name)]
            was, now = [u for u in was_all if u in touched], [u for u in numbered if u in touched]
            heading, said = f"the {name} queue", f"{len(was_all)} queued → {len(numbered)}"
            line = f"{len(was_all)} queued now; {len(numbered)} once approved"
        rows = []
        for u in put_back(now, was):
            r = {"n": str(numbered.index(u) + 1) if u in now else "–", "name": u, "tag": None, "intent": intent.get(u)}
            if u not in now and u in dropped:
                r.update(tag="drop", under=f"Why: {dropped[u]}", struck=True, outline="dashed", colour="dropped")
            elif u not in now:
                r.update(tag="out", under=out.get(u, ""), struck=True, outline="dashed", colour="moved")
            elif u not in was and u in parts:
                r.update(tag="split", colour="amended", mark="+")
            elif u not in was and kind == "queue" and u in queued:
                r.update(tag="moved", colour="moved", mark="↕")
            elif u not in was:
                r.update(tag="new", outline="solid", colour="new", mark="+")
            elif u in amended or u in split:
                r.update(tag="amend" if u in amended else "split", old=amended.get(u, split.get(u)), colour="amended", mark="~")
            elif u in ordered:
                r.update(tag="moved", colour="moved", mark="↕")
            rows.append(r)
        tags = [r["tag"] for r in rows]
        mine = {"dropped": tags.count("drop"), "amended": tags.count("amend"), "new": tags.count("new"),
                "moved": tags.count("moved") + tags.count("out") + bolt_moves.get(name, 0) * (kind == "bolt"),
                "split": sum(1 for r in rows if r["tag"] == "split" and r["name"] not in parts)}
        sections.append({"kind": kind, "name": name, "heading": heading, "said": said, "line": line, "rows": rows,
                         "counts": [(f"{mine[c]} {c}", colour) for c, colour in COUNTS if mine[c]]})
        lines += ([""] if lines else []) + wrap(heading, TEXT) + [said, ""]
        for sec, b in blocks:
            if sec == (kind, name):
                lines += b + [""]
        lines.append("ONCE APPROVED")
        for r in rows:
            if r["n"] != "–":
                first, *rest = wrap(r["name"], TEXT - 5)
                lines += [f"{r['n']:>2} {r.get('mark', ' ')} {first}"] + ["     " + x for x in rest]
        if kind == "bolt" and not after.bolt(name):
            lines.append("   the bolt is dropped")

    return {"sections": sections, "lines": lines, "counts": counts, "intent": intent, "dropped": dropped,
            "amended": amended, "came_from": came_from, "parts": parts, "goals": goals}


# --------------------------------------------------------------------------------- the words rule (briefs.13)

TITLE, SUMMARY, DETAIL, LABEL = 140, 400, 200, 80  # Pending You's budgets: a title, a summary, a detail, consequence or rationale, an option's label
OUTCOME = 200  # Pending You's budget for a close's words: ack_answer's outcome and cancel_request's reason
ARTIFACTS = 8  # Pending You's most artifacts on a card: post_request's artifacts maxItems (read 2026-10-19)
LINE = 40  # the most characters a line of a list on a card's face holds: the phone shows it in monospace
CARD_NEW = 15  # the most units new to a bolt a proposal's card takes as boxes; more link its reading session (briefs.9)
BOXES = 5  # Pending You's most options in a question; a card holds four questions, so CARD_NEW's fit in three
SENTENCE = re.compile(r"(?<=[.!?…])\s+(?=\S)")
MARKS = re.compile(r"\*\*|__|`")


def prose(text, budget=SUMMARY):
    """A document's own words as prose the phone wraps (briefs.13): its paragraphs kept, each run of spaces one, the
    Markdown marks a reader would see as marks left out, and cut at whole sentences to budget; a first sentence longer
    than the budget is cut at whole words, ending with …."""
    out = ""
    for p in re.split(r"\n\s*\n", text or ""):
        p = " ".join(MARKS.sub("", re.sub(r"^#+\s+", "", p.strip(), flags=re.M)).split())
        for i, s in enumerate(SENTENCE.split(p) if p else []):
            more = out + (" " if i else "\n\n" if out else "") + s
            if len(more) > budget:
                return out or by_words(s, budget)
            out = more
    return out


def lines_of(things, width=LINE):
    """A list the user scans as lines of at most width characters, one thing a line: a thing longer than a line
    wrapped at its words, and a name at its hyphens, its later lines indented two; a thing given as a tuple, its line
    and what is said under it, each line under it indented three."""
    out = []
    for t in things:
        head, *under = (t,) if isinstance(t, str) else t
        if len(head) <= width:
            out.append(head)
        else:
            first, *rest = wrap(head, width - 2)
            out += [first] + ["  " + x for x in rest]
        out += ["   " + x for u in under for x in wrap(u, width - 3)]
    return out


def text_list(title, ref, things):
    """A list the user scans, as a text artifact on the card's face, one thing a line (briefs.13)."""
    return {"kind": "code", "lang": "text", "title": title, "ref": ref, "lines": lines_of(things)}


def markdown(title, ref, text):
    """A document's substance as inline Markdown, an artifact of kind code with lang markdown and the text as its
    lines: the one form Pending You renders."""
    return {"kind": "code", "lang": "markdown", "title": title, "ref": ref, "lines": text.rstrip("\n").split("\n")}


def link(title, url):
    """A link as a url artifact."""
    return {"kind": "url", "title": title, "ref": url}


def context(background="", links=()):
    """A card's details: what the user reads only when its face is not enough, and its links as (label, url)."""
    return {"background": background, "trace": [], "filesTouched": [], "tried": [],
            "links": [{"label": label, "url": url} for label, url in links]}


def unfit(png):
    """Why a card's PNG is past what Pending You takes for an image put to a card, in the words its card says; None
    when it fits."""
    w, h = struct.unpack(">II", png[16:24])
    if w * h > IMAGE_PIXELS:
        return f"at {w} by {h} pixels it is past the {IMAGE_PIXELS // 10 ** 6} megapixels Pending You takes for an image"
    if len(png) > IMAGE_BYTES:
        return f"at {len(png) / 10 ** 6:.1f} MB it is past the {IMAGE_BYTES // 10 ** 6} MB Pending You takes for an image"
    return None


def built(key, title, summary, background="", links=(), artifacts=(), follows=None, urgency="today", picture=None,
          head=None, **form):
    """A card of crew's as a builder hands it to the act: its row's key, post_request's arguments but the area and the
    session, which the act sets, the picture's PNG when it has one, and the head it asks about, a landing's or a
    deploy's, which the act records with each post and change of it (head_anew). Its title cut to Pending You's
    budget, its summary prose cut at whole sentences, never blocking, following the card its thing follows. A picture
    past what Pending You takes (unfit) is left off with the artifact it was to be put to, and why said once, at the
    end of its background."""
    why = unfit(picture) if picture else None
    if why:
        artifacts, picture = [a for a in artifacts if not a.get("upload")], None
        background = "\n\n".join(x for x in (background, f"Its picture is left off the card: {why}.") if x)
    card = {"title": cut(title, TITLE), "summary": prose(summary), "context": context(background, links),
            "blocking": False, "urgency": urgency, **form}
    if artifacts:
        card["artifacts"] = list(artifacts)
    if follows:
        card["follows"] = follows
    return dict({"key": key, "card": card, "picture": picture}, **({"head": head} if head else {}))


def high(action):
    """The approve block of a card that is not undone, a landing's or a deploy's: risk high, with why, so it is
    approved only by holding the button in the app, never with a key in Herdr's popup, and never highStakes, which
    Pending You refuses on an approval."""
    return {"action": action, "risk": "high", "reversible": False, "because": "irreversible"}


# ---------------------------------------------------------------------------------------- the six builders

def preview_said(p):
    """What a landing card says of a preview of the bolt's head (rail-cards, record 0031 §3): the paragraph its details
    hold after the reading's, and the addresses it lists, [(label, address)] in the order sluice gives them. p is a
    preview sluice named, {head, name, addresses, state}, its output with it when it failed, or one that is not there,
    {head, why}; None says nothing. One that waits or starts lists its addresses for once it is up, one up lists them as
    up, each saying it lands nothing; one that failed or is not there says why, the end of a failure's output cut to a
    detail's budget by whole lines, and lists none."""
    if not p:
        return "", []
    h = p["head"][:7]
    if p.get("state") in ("waiting", "starting", "up"):
        shown = list(p["addresses"].items())
        where = f"a preview of {h}, up at these addresses" if p["state"] == "up" else (
            f"a preview of {h} sluice brings up, at these addresses once it is up")
        return (f"Try it running: {where}. It lands nothing; approving this card is the word to land.\n"
                + "".join(f"{label}: {url}\n" for label, url in shown) + "\n"), shown
    why = (last_lines(p.get("output"), DETAIL) or "its command failed, printing nothing") if p.get("state") == "failed" else p["why"]
    return f"A preview of {h} was asked for and is not there: {why.rstrip('.')}. Nothing waits on it.\n\n", []


def last_lines(text, budget):
    """The last lines of a command's output that fit budget characters together, joined by " / ", the blank ones left
    out; a last line longer than the budget cut by whole words."""
    out = []
    for line in reversed([l.strip() for l in (text or "").splitlines() if l.strip()]):
        if len(" / ".join([line] + out)) > budget:
            break
        out.insert(0, line)
    if not out and (text or "").strip():
        return by_words([l for l in text.splitlines() if l.strip()][-1].strip(), budget)
    return " / ".join(out)


def landing_card(f):
    """A bolt's landing card (record 0031 §5, briefs.9): an approval of risk high, the units and chores that land as a
    list on its face, the counts, the batches, sluice's verdict and how far main moved in its summary, what follows as
    its rationale; its details opening with the one link to the landing's reading session, which lands nothing, then
    the batches; the reading linked first, then sluice's pull request when the submission has one. f: bolt, kit,
    units, chores, batches ({unit: the batch it was read in}), head, at (sluice's time), moved (landings on main since
    the bolt was cut), pr ({number, url}) or None, offers (the environments whose deploy will be offered on a card),
    link (the reading session's) or None, preview (a preview of the head as preview_said takes it) or None, frees
    ({team, next}, when its team holds another bolt proven too) or None, follows, and approved, on a card that follows
    one the user answered at another head, the head they approved, "" when crew holds no record of it (head_anew).
    A preview's addresses follow the reading in its details and links, each on its face as a link after the reading's
    and before the pull request, as many as the card's artifacts leave room for (record 0031 §3).
    As the one row of its kit's landings card (landings_card), f also holds key, land/<kit>; conductor; forecast and
    forecast_why, as forecast_said takes them; held, [{bolt, why}], the bolts held on the card with no box; and left,
    whether the user cleared this bolt on their last send."""
    units, chores, batches = list(f["units"]), list(f.get("chores") or []), f.get("batches") or {}
    parts = ([plural(len(units), "unit")] if units else []) + ([plural(len(chores), "chore")] if chores else [])
    what = joined(parts) if parts else "nothing"
    read = sorted({batches[u] for u in units if u in batches})
    approved, head = f.get("approved"), f["head"][:7]
    said = [] if approved is None else [  # the head moved after the user's answer and before the landing (plan.16)
        f"Its head moved since your approval, from {approved[:7]} to {head}: approving this lands {head}." if approved else
        f"Its head is now {head}, and crew holds no record of the head you approved: approving this lands {head}."]
    said.append(f"{what[0].upper()}{what[1:]} {'lands' if len(units) + len(chores) == 1 else 'land'}, every one merged"
                + (f" and every unit read in a batch ({joined([str(b) for b in read])})." if read else "."))
    pr = f.get("pr")
    said.append(f"sluice is green at {f['head'][:7]}" + (f" since {f['at']}" if f.get("at") else "")
                + (f", its pull request #{pr['number']} linked below." if pr else "."))
    moved = f.get("moved") or 0
    said.append(f"main has moved {plural(moved, 'landing')} since the bolt was cut." if moved else
                "main has not moved since the bolt was cut.")
    if "forecast" in f:  # a row of its kit's landings card (rail-cards "The landings card forecasts each row's conflicts")
        said.append(forecast_said(f["forecast"], f.get("forecast_why")))
    frees = f.get("frees")
    if frees:  # its team holds another bolt, proven too, so a yes frees it (teams.16)
        said.append(f"A yes frees {frees['team']} for {frees['next']}, which waits behind this landing." if frees.get("next")
                    else f"A yes frees {frees['team']}, and nothing is planned for it.")
    offers = list(f.get("offers") or [])
    then = ("After it lands: main-level ops lands it through sluice and every host takes it"
            + (f"; {joined(offers)}'s deploy will be offered on a card." if offers else "."))
    lands = text_list(f"What lands: {plural(len(units), 'unit') if units else 'no units'}, "
                      f"{plural(len(chores), 'chore') if chores else 'no chores'}", f"land-{f['bolt']}.txt",
                      units + [f"{c} (chore)" for c in chores])
    counted = [f"batch {b}: {plural(sum(1 for u in units if batches.get(u) == b), 'unit')}" for b in read]
    reading = (f"Read the bolt in one session: {f['link']}\n\n"
               "It lands nothing: approving this card is the word to land.\n\n") if f.get("link") else ""
    tried, addresses = preview_said(f.get("preview"))
    held = list(f.get("held") or [])
    if held:
        said.append(f"Held, with no box: {joined([h['bolt'] for h in held])}.")
    if f.get("left"):
        said.insert(0, "Left on your last send.")
    if "key" in f and f.get("unread") and not f.get("link"):
        said.insert(1, f"Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and "
                       f"{f.get('conductor') or 'its conductor'} starts it with crew card session land/{f['bolt']}; this card "
                       "then carries its link.")
    defect = ("A note naming a defect holds the landing: crew withdraws this card, and raises it again, following this "
              "one, once the bolt is green again." if "key" not in f else
              f"A note naming a defect in {f['bolt']} goes to {f.get('conductor') or 'its conductor'}, and holds it on "
              "this card with no box until its fix merges.")
    unread = (f"The reading could not be opened on the tailnet: {f['unread']}\n\n"
              if "key" in f and f.get("unread") and not f.get("link") else "")
    background = (unread + reading + tried + ("Read in its batches:\n" + "\n".join(counted) + "\n\n" if counted else "")
                  + defect)
    pr_title = f"Pull request #{pr['number']} on GitHub, opened by sluice" if pr else None
    read = [(f"Read bolt {f['bolt']}", f["link"])] if f.get("link") else []
    pulled = [(pr_title, pr["url"])] if pr else []
    previews = [(f"Preview: {label}", url) for label, url in addresses]
    shown = [lands] + ([markdown(f"Held on {f['kit']}'s main, with no box", f"held-{f['kit']}.md",
                                 "\n\n".join(f"**{h['bolt']}**: {h['why']}" for h in held))] if held else [])
    room = ARTIFACTS - len(shown) - len(read) - len(pulled)  # the face's lists, the reading and the pull request kept
    return built(f.get("key") or f"land/{f['bolt']}", f"Land the bolt {f['bolt']} on {f['kit']}'s main", " ".join(said),
                 background, read + previews + pulled, shown + [link(title, url) for title, url in read + previews[:room] + pulled],
                 f.get("follows"), head=f["head"], kind="approve", intent="approve",
                 approve=high(f"Land {f['bolt']} on {f['kit']}'s main"), recommendedIds=["approve"], rationale=by_words(then, DETAIL))


def forecast_said(forecast, why=None):
    """What a row of a kit's landings card says of its forecast (rail-cards "The landings card forecasts each row's
    conflicts"): forecast, [(with, paths)] as plan.row_forecasts gives it, "main" or a bolt above it, paths None for one
    not made, with why. No conflict forecast; the files and the bolt or main each is with; or that its forecast could
    not be made and why, which holds nothing."""
    hits = [(w, p) for w, p in forecast if p]
    unmade = [w for w, p in forecast if p is None]
    said = ([f"It is forecast to conflict with " + "; and with ".join(f"{w} on {joined(list(p))}" for w, p in hits) + "."]
            if hits else [] if unmade else ["No conflict is forecast."])
    if unmade:
        said.append(f"Its forecast against {joined(unmade)} could not be made: {(why or 'git could not tell').rstrip('.')}.")
    return " ".join(said)


def landings_form(n):
    """The form of a kit's landings card by how many of its rows can land (rail-cards, record 0031 as amended
    2026-10-23): "approve", a hold-to-approve of risk high, for one; "multi", one list of boxes carrying highStakes, for
    two to BOXES; "lists", lists of BOXES at most, each a question, for more. Pending You changes neither a card's kind
    nor its questions, so a change from one form to another is followed rather than changed."""
    return "approve" if n <= 1 else "multi" if n <= BOXES else "lists"


def row_bits(r):
    """A landings row's counts, the batches its units were read in (None when none was), sluice's verdict and when,
    and its conductor."""
    units, chores, batches = list(r["units"]), list(r.get("chores") or []), r.get("batches") or {}
    parts = ([plural(len(units), "unit")] if units else []) + ([plural(len(chores), "chore")] if chores else [])
    read = sorted({batches[u] for u in units if u in batches})
    return (joined(parts) if parts else "nothing to land",
            f"read in batch{'' if len(read) == 1 else 'es'} {joined([str(b) for b in read])}" if read else None,
            f"green at {r['head'][:7]}" + (f" since {r['at']}" if r.get("at") else ""),
            r.get("conductor") or f"{r['team']}-conductor")


def row_counts(r):
    """A landings row's counts, batches, verdict and conductor, the detail of its box."""
    return "; ".join(x for x in row_bits(r) if x)


def row_paragraph(n, r):
    """A landings row on the card's face, as Markdown: its place, bolt and conductor, its units and chores one a line,
    its batches, sluice's verdict and when, how far main moved, what a yes frees, its forecast, and its reading,
    preview and pull request as links."""
    units, chores = list(r["units"]), list(r.get("chores") or [])
    moved = r.get("moved") or 0
    lines = [f"**{n}. {r['bolt']}** · {r.get('conductor') or r['team'] + '-conductor'}"
             + (" · *left on your last send*" if r.get("left") else ""), ""]
    lines += [f"- {u}" for u in units] + [f"- {c} (chore)" for c in chores] + [""]
    _, read, green, _ = row_bits(r)
    said = ([f"Read in {read[8:]}."] if read else []) + [f"sluice is {green}."]
    said.append(f"main has moved {plural(moved, 'landing')} since it was cut." if moved else "main has not moved since it was cut.")
    frees = r.get("frees")
    if frees:
        said.append(f"A yes frees {frees['team']} for {frees['next']}." if frees.get("next") else
                    f"A yes frees {frees['team']}, and nothing is planned for it.")
    said.append(forecast_said(r.get("forecast") or [], r.get("forecast_why")))
    lines.append(" ".join(said))
    links = ([f"[Read {r['bolt']}]({r['link']})"] if r.get("link") else
             [f"Its reading could not be opened: {r['unread']}; crew tries it again when the rail is read, and "
              f"{r.get('conductor') or 'its conductor'} starts it with crew card session land/{r['bolt']}"] if r.get("unread") else [])
    _, addresses = preview_said(r.get("preview"))
    links += [f"[Preview {label}]({url})" for label, url in addresses]
    if r.get("preview") and not addresses:
        links.append(preview_said(r["preview"])[0].strip())
    if r.get("pr"):
        links.append(f"[Pull request #{r['pr']['number']}]({r['pr']['url']})")
    return "\n".join(lines + ([""] + [" · ".join(links)] if links else []))


def landings_card(f):
    """A kit's landings card (rail-cards, record 0031 as amended 2026-10-23, briefs.13), keyed land/<kit>, main-level
    ops's: every bolt of the kit that can land, a row each in the plan's order, one send the word for every row the
    user leaves ticked, in the order shown. One row is the landing card of today (landing_card), an approve of risk
    high that never carries highStakes; two to BOXES, one list of boxes carrying highStakes, each `<n>. <bolt>`, its
    detail the row's counts, batches, verdict and conductor, its consequence its forecast, each ticked as crew
    proposes but one the user cleared on their last send; more, lists of BOXES at most, in order, each a question
    about the kit's main (landings_form). What follows a yes is its rationale, each list's own when it has several,
    since Pending You refuses a card's rationale beside questions. On its face, one Markdown artifact, a paragraph a row (row_paragraph), then
    the rows held with no box and why; in its details, every row's reading first, then its previews and pull request,
    as many as the card's artifacts leave room for. f: kit, rows (each the facts landing_card takes, with team,
    conductor, forecast, forecast_why, link or unread and preview), held ([{bolt, why}]), left (the bolts the user
    cleared on their last send), follows. Also handed back: heads, each row as <bolt>@<head> and :left for one the user
    cleared, which the run record keeps on the card's post and change for the next raise to read (plan.landings_step),
    and linked, since each row's reading was opened with it and the card has no reading of its own."""
    kit, rows, held, left = f["kit"], [dict(r) for r in f["rows"]], list(f.get("held") or []), set(f.get("left") or [])
    key, form = f"land/{kit}", landings_form(len(rows))
    rows or fail(f"{key} has no bolt that can land, so it has no card")
    for r in rows:
        r["left"] = r["bolt"] in left
    heads = [f"{r['bolt']}@{r['head'][:7]}" + (":left" if r["left"] else "") for r in rows]
    unread = [(r["bolt"], r["unread"]) for r in rows if r.get("unread")]
    why = unread[0][1] if len(rows) == 1 and unread else "; ".join(f"{b}: {w}" for b, w in unread)
    if form == "approve":
        out = landing_card(dict(rows[0], key=key, held=held, follows=f.get("follows")))
        out.update(heads=heads, linked=True, **({"unread": why} if why else {}))
        return out
    n = len(rows)
    about = f"{kit}'s main"
    face = "\n\n".join(row_paragraph(i, r) for i, r in enumerate(rows, 1))
    if held:
        face += "\n\n**Held, with no box**\n\n" + "\n".join(f"- **{h['bolt']}**: {h['why']}" for h in held)
    left_said = [r["bolt"] for r in rows if r["left"]]
    summary = (f"{n} bolts wait to land on {about}, in the order below. One send lands the ticked ones in that order, each "
               "queued behind the one before; clear a box to leave that bolt waiting. A note can move one in the order, or "
               "name a defect in one, which goes to its conductor."
               + (f" {joined(left_said)} {'was' if len(left_said) == 1 else 'were'} left on your last send, and "
                  f"{'is' if len(left_said) == 1 else 'are'} unticked." if left_said else "")
               + (f" Held, with no box: {joined([h['bolt'] for h in held])}." if held else ""))

    def option(i, r):
        return {"id": f"land:{r['bolt']}", "label": cut(f"{i}. {r['bolt']}", LABEL),
                "detail": by_words(("Left on your last send. " if r["left"] else "") + row_counts(r), DETAIL),
                "consequence": by_words(forecast_said(r.get("forecast") or [], r.get("forecast_why")), DETAIL)}
    options = [option(i, r) for i, r in enumerate(rows, 1)]
    ticked = [o["id"] for o, r in zip(options, rows) if not r["left"]]
    then = by_words("After they land: main-level ops lands them through sluice in this order, closing each as it lands, "
                    "and every host takes them.", DETAIL)
    if form == "multi":
        shape = dict(kind="multi", intent="decide", options=options, multi={"min": 0, "max": n}, recommendedIds=ticked,
                     rationale=then)
    else:  # Pending You refuses a card's rationale beside questions, so each list carries what follows a yes
        g = -(-n // BOXES)
        sizes = [n // g + (1 if k < n % g else 0) for k in range(g)]
        groups = [options[sum(sizes[:k]):sum(sizes[:k + 1])] for k in range(g)]
        shape = dict(intent="decide", about={"kind": "other", "title": cut(f"Land on {about}", 120)},
                     questions=[dict(id=f"rows-{k}", kind="multi", title=f"Bolts {grp[0]['label'].split('.')[0]} to "
                                     f"{grp[-1]['label'].split('.')[0]} of {n}, in order", options=grp,
                                     multi={"min": 0, "max": len(grp)}, recommendedIds=[o["id"] for o in grp if o["id"] in ticked],
                                     rationale=then)
                                for k, grp in enumerate(groups, 1)])
    reads = [(f"Read {r['bolt']}", r["link"]) for r in rows if r.get("link")]
    previews = [(f"Preview {r['bolt']}: {label}", url) for r in rows for label, url in preview_said(r.get("preview"))[1]]
    pulls = [(f"Pull request #{r['pr']['number']} for {r['bolt']}, opened by sluice", r["pr"]["url"]) for r in rows if r.get("pr")]
    links = reads + previews + pulls
    background = ("\n\n".join(f"{i}. {r['bolt']} ({r.get('conductor') or r['team'] + '-conductor'}): {row_counts(r)}. "
                              + forecast_said(r.get("forecast") or [], r.get("forecast_why"))
                              + (f" Read it: {r['link']}" if r.get("link") else
                                 f" Its reading could not be opened: {r['unread']}" if r.get("unread") else "")
                              for i, r in enumerate(rows, 1))
                  + ("\n\nA preview lands nothing; your send is the word to land." if previews else "")
                  + "\n\nA note naming a defect in a bolt goes to its conductor, and holds that bolt on this card with no "
                    "box until its fix merges.")
    shown = [markdown(f"What lands on {about}, in order", f"land-{kit}.md", face)]
    out = built(key, f"Land on {about}: {n} bolts in order", summary, background, links,
                shown + [link(t, u) for t, u in links[:ARTIFACTS - len(shown)]], f.get("follows"), highStakes=True, **shape)
    out.update(heads=heads, linked=True, **({"unread": why} if why else {}))
    return out


def deploy_card(f):
    """A deploy's card (record 0031 §5, plan.14): an approval of risk high naming the environment and the commit; its
    summary counting the landings since the environment's last deploy, or saying it is the first deploy, which carries
    all of main, and naming the environments before and after it; on its face the kit's release notes as the deployer
    hands them, as inline Markdown, crew writing none, or the landings' subjects when it hands none, saying so, and the
    after-deploy steps with their doers; the landings' subjects in its details. f: env, head, base (what the environment
    runs) or None, landings ([{pr, subject}], oldest first), landings_why (why they can't be read) or None, notes
    (Markdown) or None, release (the notes' name) or None, steps ([{n, text, doer, held}]), before ([env]), after ([{env,
    policy}]), follows."""
    env, head, landings, steps = f["env"], f["head"][:7], list(f.get("landings") or []), list(f.get("steps") or [])
    why, first = f.get("landings_why"), not f.get("base")
    since = f"in the first deploy to {env}" if first else f"since {env}'s last deploy ({f['base'][:7]})"
    said = [f"Which landings it carries {since} can't be read: {why}." if why else
            f"The first deploy to {env}, carrying all of main up to {head}." if first else
            f"{plural(len(landings), 'landing')} since {env}'s last deploy ({f['base'][:7]})."]
    if not f.get("notes"):
        said.append("The kit handed no release notes.")
    if f.get("before"):
        said.append(f"It comes after {joined(list(f['before']))}.")
    after = list(f.get("after") or [])
    auto = [a["env"] for a in after if a.get("policy") == "auto"]
    manual = [a["env"] for a in after if a.get("policy") != "auto"]
    then = ([f"{joined([f'{e} (auto)' for e in auto])} {'follows' if len(auto) == 1 else 'follow'} on "
             f"{'its' if len(auto) == 1 else 'their'} own"] if auto else []) + \
           ([f"{joined(manual)} {'is' if len(manual) == 1 else 'are'} offered after {env}"] if manual else [])
    if then:
        said.append("; ".join(then) + ".")
    yours = sum(1 for s in steps if s["doer"] == "user")
    if steps:
        said.append(f"After the deploy: {plural(len(steps), 'step')}, {yours} yours.")
    subjects = [(f"#{l['pr']} " if l.get("pr") else "") + l["subject"] for l in landings]
    shown = ([markdown("What's in it" + (f": {f['release']}" if f.get("release") else ""), f"deploy-{env}.md", f["notes"])]
             if f.get("notes") else [text_list("What's in it" + ("" if why or first else f": {plural(len(landings), 'landing')}"),
                                               f"deploy-{env}.txt", subjects or ([why] if why else [f"All of main up to {head}"] if first else []))])
    if steps:
        shown.append(text_list(f"After the deploy: {plural(len(steps), 'step')}, {yours} yours", f"deploy-{env}-steps.txt",
                               [(f"{s['n']}  {s['text']}", "you" if s["doer"] == "user" else
                                 f"{s['doer']}, held for your word" if s.get("held") else s["doer"]) for s in steps]))
    background = f"Landings since {env}'s last deploy:\n" + "\n".join(subjects) if subjects else ""
    return built(f"deploy/{env}", f"Deploy main {head} to {env}", " ".join(said), background, (), shown, f.get("follows"),
                 head=f["head"], kind="approve", intent="approve", approve=high(f"Deploy {head} to {env}"), recommendedIds=["approve"],
                 rationale=f"{env} deploys only on your word, and a deploy is not undone.")


QUIET = {"quiet": ("When the host is quiet", "No stage is cut; it could be hours"),
         "now": ("Now", "It runs at once, whatever is running"),
         "skip": ("Skip it", "It is not done")}


def step_card(f):
    """An after-deploy step's card (record 0031 §5, plan.14): the user's step a `do` with its words, where, each
    command whole and what is seen when it worked, its Done, Skip and Later the app's own; an agent's step held for
    the user's word a choice of when, quiet recommended, now or skip, each with its consequence; a deploy waiting at
    its gate (plan.14) the user's `do` to approve it there, its one step, its where and its link the gate's. f: env, n,
    text, doer ("user" or the agent), held, why, where, commands, done, gate (the gate's link) or None, to (the commit
    the step names) or None, consequences ({quiet, now, skip}), follows."""
    key, title = f"op/{f['env']}/{f['n']}", f"After {f['env']}'s deploy: {f['text']}"
    if f.get("gate"):
        link, of = f["gate"], f" of {f['to'][:7]}" if f.get("to") else ""
        said = (f"The deploy{of} to {f['env']} waits at its gate for your approval there. Approving it at the gate is the "
                "word to deploy; nothing else asks for it.")
        return built(key, f"Approve the deploy{of} to {f['env']} at its gate", said + (f" {f['why']}" if f.get("why") else ""),
                     links=[("The gate", link)], follows=f.get("follows"), kind="action", intent="do",
                     action={"steps": [{"text": link}], "where": link, "done": "The run goes on past its gate."})
    if f["doer"] == "user":
        steps = [{"text": c, "command": c} for c in f.get("commands") or []] or [{"text": f["text"]}]
        action = dict({"steps": steps}, **{k: f[k] for k in ("where", "done") if f.get(k)})
        return built(key, title, f.get("why") or f["text"], follows=f.get("follows"), kind="action", intent="do",
                     action=action)
    said = dict(f.get("consequences") or {})
    options = [{"id": k, "label": label, "consequence": by_words(said.get(k) or then, DETAIL)}
               for k, (label, then) in QUIET.items()]
    return built(key, f"{title}, now or when the host is quiet?",
                 f"{f['doer']} can do it. " + (f"{f['why']} " if f.get("why") else "") + "Held for your word.",
                 follows=f.get("follows"), urgency="whenever", kind="choice", intent="decide", options=options,
                 recommendedIds=["quiet"])


AMENDED = re.compile(r"^Amended\b[^:.]*:\s*")


def first_words(text):
    """An amendment's own first words, which title its record's card (record 0031 as amended 2026-10-24): the first
    sentence of its paragraph, with its `Amended <date>:` lead, a list item's marker, its Markdown marks and its
    closing stop left out."""
    p = AMENDED.sub("", " ".join(MARKS.sub("", re.sub(r"^[-*+]\s+", "", (text or "").strip())).split()))
    return SENTENCE.split(p, 1)[0].rstrip(".") if p else ""


def record_card(f):
    """A decision record's card (record 0031 §5): a plain record's a hold-to-accept of low risk, holding the record
    whole as Markdown, its opening sentences the summary and the user's own words beside them; a record a rule of the
    user's decided between alternatives a choice asked once, loosen the rules as drafted and take the other path,
    accept the record as ruled, or send it back, its face the alternatives, the rules that decided and each loosened,
    then the record. An amendment's card is titled by the amendment's own first words, cut at whole words, not the
    record's title, so each amendment of one record reads as its own question (record 0031 as amended 2026-10-24).
    f: kit, number, title, opening, quoted (the user's words it records), text (the record, Markdown), amendment (its
    first words, first_words) or None, alternatives ({rules, other, text, recommended: loosen or accept}) or None,
    follows."""
    n = f"{int(f['number']):04d}"
    quoted = list(f.get("quoted") or [])
    words = "Your own words, recorded as your decision:\n" + "\n".join(f"“{q}”" for q in quoted) if quoted else ""
    record = markdown(f"Record {n}", f"record-{n}.md", f["text"])
    alt, amended = f.get("alternatives"), f.get("amendment")

    def titled(head):
        head += f" {n} in {f['kit']}: "
        return head + (by_words(amended, TITLE - len(head)) if amended else f["title"])
    if not alt:
        return built(f"record/{f['kit']}/{n}", titled("Accept an amendment to record" if amended else "Accept record"),
                     f["opening"] + ("\n\n" + words if words else ""), words, (), [record], f.get("follows"),
                     urgency="whenever", kind="approve", intent="approve",
                     approve={"action": f"Accept record {n}", "risk": "low", "reversible": True}, recommendedIds=["approve"])
    rules = joined(list(alt["rules"]))
    options = [{"id": "loosen", "label": cut(f"Loosen {rules} as drafted", LABEL), "detail": by_words(f"Take the other path: {alt['other']}", DETAIL),
                "consequence": "The design agent rewrites the record and amends the rules in one commit"},
               {"id": "accept", "label": "Accept the record as ruled", "consequence": "The record stands as written"},
               {"id": "back", "label": "Send it back with a note", "consequence": "The design agent revises it from your note"}]
    summary = (f"Your rules decided this one: {rules} chose the record's path over the other, {alt['other']}. One decision: "
               "the record as ruled, or loosen the rules as drafted and take the other path.")
    return built(f"record/{f['kit']}/{n}", titled("An amendment to record" if amended else "Record"), summary, words, (),
                 [markdown("Where your rules decided, and the rules loosened", f"record-{n}-rules.md", alt["text"]), record],
                 f.get("follows"), urgency="whenever", kind="choice", intent="decide", options=options,
                 recommendedIds=[alt.get("recommended") or "accept"])


def batch_card(f):
    """A batch's card (record 0031 §5, briefs.9): a one-tap notice titled by what the batch is about, from its units'
    subjects; its summary opening "N changes to read, nothing to approve" with each unit's paragraph after it, cut at
    whole sentences; the reviewer's summary on its face as inline Markdown, a paragraph per unit with its team; its
    details opening with the one link to the batch's reading session, then where notes go and every unit with its
    team and paragraph. f: n, previous (the batch before) or None, units ([{unit, team, subject, paragraph}]), link
    (the reading session's) or None."""
    n, units = f["n"], list(f["units"])
    subjects = list(dict.fromkeys(u["subject"] for u in units if u.get("subject"))) or [u["unit"] for u in units]
    tail = f" (batch {n})"
    about = next(said for k in range(len(subjects), 0, -1)
                 for said in [joined(subjects[:k] + ([f"{len(subjects) - k} more"] if k < len(subjects) else []))]
                 if len(said) + len(tail) <= TITLE or k == 1)
    first = f"{plural(len(units), 'change')} to read, nothing to approve" + (f", since batch {f['previous']}." if f.get("previous") else ".")
    paragraphs = [f"{u['team']} · {u['unit']}: {u['paragraph']}" for u in units]
    notes = ("Notes go in the reading or in this card's note, naming the unit; each reaches its team as your words, and the "
             "units go on building whatever you do with this card.")
    background = ((f"Read it all in one session: {f['link']}\n\n" if f.get("link") else "") + notes + "\n\n"
                  + "\n\n".join(f"{u['unit']} ({u['team']})\n{prose(u['paragraph'], 10 ** 6)}" for u in units))
    summary = "\n\n".join(f"**{u['team']} · {u['unit']}**\n\n{u['paragraph'].strip()}" for u in units)
    shown = [markdown("The reviewer's summary", f"batch-{n}.md", summary)] + ([link(f"Read batch {n}", f["link"])] if f.get("link") else [])
    return built(f"batch/{n}", about[0].upper() + about[1:] + tail, "\n\n".join([first] + paragraphs), background,
                 [(f"Read batch {n}", f["link"])] if f.get("link") else (), shown, urgency="whenever", kind="fyi", intent="tell")


def proposal_rows(argvs):
    """The rows of a proposal's card from its commands alone, in order, each ("new", command): a unit or chore new to a
    bolt or the queue, once, at the command that adds it or moves it in. A drop, an amendment, a move out, an order or a
    new bolt is no row: it is drawn on the card's face and applies with it (briefs.13)."""
    new, seen, rows = new_units(argvs), set(), []
    for a in argvs:
        if (a.cmd in ("unit", "chore") and (a.sub == "add" or (a.sub == "move" and a.bolt != "queue"))
                and a.unit in new and a.unit not in seen):
            seen.add(a.unit)
            rows.append(("new", a))
    return rows


def proposal_form(argvs):
    """The form of a proposal's card from its commands alone (proposal_card), by the count of units and chores it makes
    new: "approve", a hold-to-approve, when it makes none, or more than CARD_NEW, which link its reading session;
    "choice" for one; "multi" for one list, BOXES at most; "lists" for more, each list a question. Pending You's
    update_request changes neither a card's kind nor its questions, so a rewrite that moves its chain's card from one
    form to another is followed rather than changed (plan.raise_proposal_at)."""
    k = len(new_units(argvs))
    if not k or k > CARD_NEW:
        return "approve"
    return "choice" if k == 1 else "multi" if k <= BOXES else "lists"


def proposal_card(f):
    """A proposal's card (record 0031 §5, plan-proposals): titled "Plan change to <bolt>: <counts>", with no number and
    no question; a sentence of what the planner proposes and why, from its case, and what the user does with it; one
    checkbox list, a box only for each unit or chore new to a bolt or the queue, ticked, in groups of five, and nothing
    else to tap, what else it changes drawn and applied with it; a lone new unit the choice of its two sides, Pending
    You's lists holding two at least; a hold-to-approve of low risk when it makes no unit or chore new, declined with a
    note to keep what it drops or amends, or more than CARD_NEW, which link its reading session; a paragraph per new
    and dropped unit on its face as inline Markdown; the change drawn at twice the density and as text. f: n, first
    (the first proposal of its chain, its key's), state, case, before and after (the plan at the tip and as its
    commands leave it), argvs (its commands, parsed), waiting ([teams whose conductor has yet to agree]), session (the
    reading session's link) or None. Also handed back: the boxes, each {id, unit, is: new, ticked: true}, and whether
    the card needs its reading session."""
    n, argvs = f["n"], list(f["argvs"])
    f.get("state", "open") == "open" or fail(f"proposal {n} is {f['state']}: it is closed, so it has no card")
    d = drawn(f["before"], f["after"], argvs)
    counts = ", ".join(f"{d['counts'][c]} {c}" for c, _ in COUNTS if d["counts"][c])
    headings = [s["heading"] for s in d["sections"]]
    room = TITLE - len(f"Plan change to : {counts}")
    to = next(said for k in range(len(headings), 0, -1)
              for said in [joined(headings[:k] + ([f"{len(headings) - k} more"] if k < len(headings) else []))]
              if len(said) <= room or k == 1)
    title = f"Plan change to {to}" + (f": {counts}" if counts else "")
    new, made, units, rows = new_units(argvs), {a.unit: a for _, a in proposal_rows(argvs)}, {}, []
    for a in argvs:  # the new units and the dropped ones, in the order the commands name them, for the face
        if a.cmd not in ("unit", "chore") or a.unit in units:
            continue
        if made.get(a.unit) is a:
            units[a.unit] = a
            moved = a.sub == "move"
            src = d["came_from"].get(a.unit)
            rows.append({"id": f"add:{a.unit}", "unit": a.unit, "is": "new", "ticked": True,
                         "label": f"Move {a.unit} in" if moved else f"Add {a.unit}", "detail": d["intent"].get(a.unit) or "",
                         "consequence": f"Cleared: stays in {'the queue' if src is None else 'bolt ' + src}; the rest still applies"
                         if moved else "Cleared: not added; the rest still applies"})
        elif a.sub == "drop" and a.unit not in made:
            units[a.unit] = a
    session = len(new) > CARD_NEW
    shape = proposal_form(argvs)
    also = bool(d["dropped"] or d["amended"])  # it drops or amends a unit, which no box asks

    def option(r):
        return {"id": r["id"], "label": cut(r["label"], LABEL), "detail": by_words(r["detail"], DETAIL),
                "consequence": by_words(r["consequence"], DETAIL)}
    if shape == "approve":
        how = ("Hold to apply it whole; to keep a unit it drops or amends, decline with a note." if also and not session
               else "Hold to apply it whole.")
        form = dict(kind="approve", intent="approve", recommendedIds=["approve"],
                    approve={"action": f"Apply the plan change to {to}", "risk": "low", "reversible": True})
    elif shape == "choice":
        r = rows[0]
        how = "Its one new unit is set as proposed; pick the other side and send to leave it out."
        options = [option(r), {"id": "unticked", "label": cut(f"Leave {r['unit']} out", LABEL)}]
        form = dict(kind="choice", intent="decide", options=options, recommendedIds=[r["id"]])
    else:
        how = "Each new unit below is ticked; clear any to leave it out, and send."
        g = -(-len(rows) // BOXES)
        sizes = [len(rows) // g + (1 if k < len(rows) % g else 0) for k in range(g)]
        groups = [rows[sum(sizes[:k]):sum(sizes[:k + 1])] for k in range(g)]
        lists = [{"options": [option(r) for r in grp], "multi": {"min": 0, "max": len(grp)},
                  "recommendedIds": [r["id"] for r in grp]} for grp in groups]
        form = (dict(kind="multi", intent="decide", **lists[0]) if g == 1 else
                dict(intent="decide", about={"kind": "other", "title": cut(f"Plan change to {to}", 120)},
                     questions=[dict(id=f"rows-{k}", kind="multi", title=f"The change, part {k} of {g}: each row as proposed", **q)
                                for k, q in enumerate(lists, 1)]))
    if shape != "approve" and also:
        how += " What it drops or amends applies with it."
    waiting = [f"{t}-conductor" for t in f.get("waiting") or []]
    case = prose(f["case"], 10 ** 6)
    said = ((f"Read it all in one session: {f['session']}\n\n" if f.get("session") else "")
            + f"{SENTENCE.split(case)[0] if case else ''} {how}"
            + (f" It waits on {joined(waiting)} to agree." if waiting else ""))
    paragraphs = []
    for u, a in units.items():
        if a.sub == "drop":
            paragraphs.append(f"**Drop {u}**\n\n{d['intent'].get(u) or ''}\n\nWhy: {a.reason}")
        else:
            where = (f"from {d['came_from'].get(u) or 'the queue'} into {a.bolt}" if a.sub == "move" else
                     (f"into {a.bolt}" if a.bolt else f"to the {a.repo} queue") + (f", before {a.before}" if a.before else "")
                     + (f", after {joined(list(a.after))}" if a.after else ""))
            paragraphs.append(f"**{'Move' if a.sub == 'move' else 'Add'} {u}**\n\n{d['intent'].get(u) or ''}\n\nDirection: {where}.")
    named = ["dropped" if a.sub == "drop" else "new" for a in units.values()]
    shown = ([markdown(f"The {joined([w for w in ('new', 'dropped') if w in named])} units", f"proposal-{n}-units.md",
                       "\n\n".join(paragraphs))] if paragraphs else [])
    shown += [{"kind": "image", "title": "The change, once approved", "ref": f"proposal-{n}.png", "upload": True, "caption": CAPTION},
              {"kind": "code", "lang": "text", "title": "The change, in text", "ref": f"proposal-{n}.txt", "lines": d["lines"]}]
    background = f["case"].strip() + (f"\n\nWaiting on {joined(waiting)} to agree." if waiting else "")
    links = [(f"Read proposal {n}", f["session"])] if f.get("session") else ()
    out = built(f"proposal/{f.get('first') or n}", title, said, background, links, shown, picture=picture.draw(d["sections"]), **form)
    out.update(boxes=[{k: r[k] for k in ("id", "unit", "is", "ticked")} for r in rows], session=session)
    return out


# ------------------------------------------------------------------------------------- what a card follows

def posted_cards(entries):
    """Each card the run record's entries show posted, oldest first: {key, card, by, state, rows}, by the agent its post
    names, its state None while it is open, else its close's, closed, withdrawn, declined or lost, and rows, how many
    rows a kit's landings card left that can land when it closed, as its close's Rows says (plan.landings_step), else
    0."""
    out = []
    for e in entries:
        if e.get("Act") == "card.post" and e.get("Card") and not e.get("Refused"):
            out.append({"key": e.get("Key") or "", "card": e["Card"], "by": e.get("By"), "state": None, "rows": 0})
        elif e.get("Act") == "card.close" and e.get("Card") and not e.get("Refused"):
            for c in out:
                if c["card"] == e["Card"] and c["state"] is None:
                    c["state"] = e.get("State") or "closed"
                    c["rows"] = int(e["Rows"]) if re.fullmatch(r"\d+", str(e.get("Rows") or "")) else 0
    return out


def follows_of(kind, thing, entries, by):
    """The card a card of kind posted in the name of `by` follows, so one thing's chain reads as one thread on the
    phone (record 0031 §5), from the run record's entries, oldest first: its id, or None. Only a card the entries show
    posted in by's own name is followed, since Pending You takes `follows` only to a card of the asker's own and
    refuses the post otherwise (briefs.11, read 2026-10-20). A landing raised again follows the bolt's last landing
    card once that is closed, as a defect note holds it; a deploy follows its environment's last deploy card when the
    user declined it, else nothing, never a landing's card, whose landings its face names (briefs.13); a step follows
    the step card raised after its environment's last deploy card, else that card. A proposal, a batch and a record
    follow nothing. A card lost to its owner is followed by none. A kit's landings card follows the kit's last one in
    by's name only once the user answered it and it closed with rows left that can land (rail-cards "The landings card
    closes when nothing waits"), else nothing. thing: a bolt's landing's {bolt}, a kit's landings card's {kit}, a
    deploy's {env, head}, a step's {env, key}."""
    cards = [c for c in posted_cards(entries) if c["state"] != "lost" and c["by"] == by]
    if kind == "land" and "kit" in thing:
        mine = [c for c in cards if c["key"] == f"land/{thing['kit']}"]
        return mine[-1]["card"] if mine and mine[-1]["state"] == "closed" and mine[-1]["rows"] else None

    def landing(bolt):  # a bolt's landing cards, keyed by the bolt, or by its head before record 0031
        return [c for c in cards if c["key"] == f"land/{bolt}" or c["key"].startswith(f"land/{bolt}/")]
    if kind == "land":
        mine = landing(thing["bolt"])
        return mine[-1]["card"] if mine and mine[-1]["state"] else None
    if kind == "deploy":
        mine = [c for c in cards if c["key"] == f"deploy/{thing['env']}"]
        return mine[-1]["card"] if mine and mine[-1]["state"] == "declined" else None
    if kind == "step":
        deploys = [i for i, c in enumerate(cards) if c["key"] == f"deploy/{thing['env']}"]
        if not deploys:
            return None
        steps = [c for c in cards[deploys[-1] + 1:] if c["key"].startswith(f"op/{thing['env']}/") and c["key"] != thing.get("key")]
        return (steps[-1] if steps else cards[deploys[-1]])["card"]
    return None


# ---------------------------------------------------------------------------------------- the act's decisions

ROWS = ((re.compile(r"^proposal/(\d+)$"), "proposal/{}"), (re.compile(r"^batch/(\d+)$"), "batch/{}"),
        (re.compile(r"^land/([a-z0-9][a-z0-9-]*)$"), "bolt/{}"), (re.compile(r"^deploy/([a-z0-9][a-z0-9-]*)$"), "env/{}"),
        (re.compile(r"^op/([a-z0-9][a-z0-9-]*)/\d+$"), "env/{}"),
        (re.compile(r"^record/([a-z0-9][a-z0-9-]*)/(\d{4})(?:/[0-9a-f]{7,40})?$"), "record/{}/{}"))
# What update_request takes of a card crew built. It changes neither a card's kind nor its questions, so a card whose
# kind changed, or one that carries questions, a proposal's rows in lists, is followed by a new card (revision).
CHANGED = ("title", "summary", "context", "artifacts", "approve", "options", "multi", "recommendedIds", "action",
           "rationale", "urgency", "blocking")
DEAD = "An older copy of this card was lost: dismiss it in the app."
# The fewest characters Pending You takes in an idempotencyKey (post_request's schema, pendingyou 0.35.1), and what
# fills a shorter key of crew's out to it: no row key and no revision holds it, so a filled key is no other row's.
KEY_LEAST, FILL = 8, "_"


def row_object(key, kits=()):
    """The run record's object of one of crew's six cards' keys, the row's: a proposal's, a batch's, a kit's for its
    landings card, land/<kit> where kits, the names of the kits the partition's teams build, hold it, else a bolt's for
    its reading or an old landing card of its own, an environment's for its deploy and steps, a record's, under record
    0031's key or the key with the commit after it, record/<kit>/<number>/<commit>, as the design agent posted it
    before; None for any other key."""
    m = re.fullmatch(r"land/([a-z0-9][a-z0-9-]*)", key or "")
    if m and m.group(1) in kits:
        return f"kit/{m.group(1)}"
    for pattern, obj in ROWS:
        m = pattern.match(key)
        if m:
            return obj.format(*m.groups())
    return None


def record_keys(entries, obj, by, kits=()):
    """The keys under which the agent `by` holds a decision record's card open, the record's object obj, in either
    form (row_object, kits as it takes them), in the order of their first post; entries are in the order they were
    written."""
    keys = dict.fromkeys(e["Key"] for e in entries if e.get("Act") == "card.post" and e.get("By") == by and e.get("Key")
                         and row_object(e["Key"], kits) == obj)
    return [k for k in keys if card_under(entries, k, by)]


def adopt_line(card, owner):
    """The line that adopts a card crew posted in no session (briefs.16): the owner's own get_request under its name
    reads the card on the host's connection, and the fleet's wake mod then wakes the owner's idle session on its
    answer."""
    return f"call get_request (requestId {card}, name {owner})"


def told_to(owner, caller):
    """Whom crew tells a card's adopting line (roles.4): its owner when the command that raised it is not the owner's,
    a landing found on another's rail read or the deployer's offer; None when it is, a proposal in the planner's own
    shell."""
    return owner if caller != owner else None


def change_args(card, note):
    """update_request's arguments for a card crew built again, but the card's id, name and version: what it takes of
    the card, and the change note the user sees."""
    return dict({k: card[k] for k in CHANGED if k in card}, changeNote=cut(note, 120))


# The statuses get_request gives a card that waits on nobody any more: picked up or acked (resolved, or closed),
# withdrawn, or expired. An answered card acked reads resolved (Pending You's ack_answer, read 2026-10-19), and
# pendingyou 0.35.1 gives no `closed` (its wake mod's CLOSED).
ENDED = ("resolved", "closed", "cancelled", "expired")
# Of those, the ones whose close the run record keeps as closed rather than withdrawn.
ACKED = ("resolved", "closed")


def ended(got):
    """The state crew records a card in once get_request gives it ended in Pending You by another hand than crew's
    close, so crew can neither change nor close it, and the run record must say it closed: "closed" when it is
    resolved, answered and picked up or acked, or closed, "withdrawn" when it is cancelled or expired, and None for any
    other reply. The
    mac-studio deploy card of 2026-10-19 was resolved by the after-deploy step's card posted following it, refused
    every close and change for six hours after, and no later offer of mac-studio reached the user."""
    status = got.get("status") if isinstance(got, dict) else None
    return None if status not in ENDED else "closed" if status in ACKED else "withdrawn"


def revision(got, kind_changed=False, questions=False, anew=False):
    """How crew puts a changed card before the user, from get_request's answer, whether the card's kind changed,
    whether the card crew built again carries questions, and whether what it asks changed since the user could answer
    it (anew): "change", the card changed in place, while it waits on them; "follow" when its kind changed or it
    carries questions, which update_request never changes (CHANGED): a card changed in place would keep its old
    questions under its new title, as proposal 140's did over proposal 139's rows on 2026-10-18. Once they have
    answered it, which Pending You changes no longer, picked up or acked since or not, "leave", the card left as it
    is, since an answered card is final for what it asked and the act their answer calls for goes on (record 0031 §1
    and §3): a change to what it offers, a reading's link, a preview's addresses, a note on what a yes frees, never
    closes it or asks again; only when what it asks changed, its kind or anew, a head that moved after the answer among
    them (head_anew), "follow", the new card following it (Pending You's guide, "Follow up with a new card"), or
    "ended" when Pending You has ended it already (ended), as it has a card withdrawn or expired unanswered."""
    state = ended(got)
    answered = state == "closed" or isinstance(got, dict) and got.get("status") == "answered"
    if answered and not (kind_changed or anew):
        return "leave"
    if state:
        return "ended"
    return "follow" if answered or kind_changed or questions else "change"


def head_asked(entries, card):
    """The head a card of crew's asks about as the run record's entries hold it, oldest first: the Head of the last
    post or change of the card recorded done, or None when it records none, as one made before crew recorded heads."""
    head = None
    for e in entries:
        if e.get("Act") in ("card.post", "card.update") and e.get("Card") == card and not e.get("Refused"):
            head = e.get("Head")
    return head


def head_anew(entries, card, head):
    """What a landing's or a deploy's card asks anew at head, as row_card_change takes it (anew): None when no card is
    held or it asks about head already, so a card the user answered is left as it is (revision); once the head moved
    since the card they could answer, {"approved": the head it asked about}, "" when the run record holds none, since
    crew then can't tell which head they approved and asks again rather than take their answer for this one (read.1)."""
    if not card:
        return None
    asked = head_asked(entries, card)
    return None if asked == head else {"approved": asked or ""}


def post_key(entries, key, by):
    """The idempotency key crew posts its card under a row's key with, from the run record's entries: the row's key for
    its first card, and for each card after one of `by`'s under it closed (answered and followed, declined, withdrawn or
    lost), the key with that card's revision, <key>:<n>, since Pending You gives a key's card back as long as it keeps
    it and takes one key per question. A card still open under the key keeps its own key, so posting it again gives it
    back. A key shorter than Pending You takes, batch/7 or land/b1, is filled out to KEY_LEAST at its end with FILL,
    batch/7_, the same on every post: its first part is still crew's (plan.crews_key), and a key long enough is sent as
    it always was, so a card open under it is given back (batch 7's card on 2026-10-19, refused "idempotencyKey: Too
    small: expected string to have >=8 characters")."""
    mine = [e for e in entries if e.get("Act") == "card.close" or (e.get("Key") == key and e.get("By") == by)]
    closed = {c["card"] for c in posted_cards(mine) if c["state"]}
    return (f"{key}:{len(closed) + 1}" if closed else key).ljust(KEY_LEAST, FILL)


def posted_again(card):
    """A card posted again under its key once its first copy was lost to its owner: its summary saying so first."""
    return dict(card, summary=prose(f"{DEAD}\n\n{card['summary']}"))


def close_words(got, outcome=None, reason=None):
    """The words a card's close carries, whole, from get_request's answer: for one the user answered, the outcome, or
    the reason; for one still waiting, the reason, or the outcome."""
    first, then = (outcome, reason) if got.get("status") == "answered" else (reason, outcome)
    return first if first is not None else then


def close_call(got, card, name, outcome=None, reason=None, here=False):
    """How crew closes a card, from get_request's answer: one the user answered acked at its version with what was
    done on it, the outcome, or the reason it is withdrawn; one still waiting withdrawn with the reason, or the
    outcome (close_words), or, with here, the user having answered it in a conversation, as a landing said in ops's
    pane is (plan.16), cancelled as answered there (Pending You's answeredHere) and closed. Either is cut to OUTCOME
    characters, since Pending You refuses a longer one (proposal 142's close on 2026-10-18: "outcome: Too big: expected
    string to have <=200 characters"); the run record keeps crew's words whole. The tool, its arguments, and the
    close's state as the run record keeps it."""
    words = close_words(got, outcome, reason)
    said = cut(words, OUTCOME) if isinstance(words, str) else words
    if got.get("status") == "answered":
        return ("ack_answer", {"requestId": card, "name": name, "expectedVersion": version_of(got, card), "outcome": said},
                "closed" if outcome is not None else "withdrawn")
    if here:
        return "cancel_request", {"requestId": card, "name": name, "reason": said, "answeredHere": True}, "closed"
    return "cancel_request", {"requestId": card, "name": name, "reason": said}, "withdrawn"


def declined(got):
    """The user's words declining an approval, as get_request gives a card's answer: "" when they gave none; None when
    the card is no approval they declined."""
    answer = got.get("answer") if isinstance(got, dict) and got.get("turn") == "agent" else None
    if not isinstance(answer, dict) or answer.get("approved") is not False:
        return None
    return text_of(answer.get("note")) or text_of(answer.get("text")) or ""


def declined_outcome(words):
    """A declined approval's close, in the user's words."""
    return f"Declined: {words}" if words else "Declined, with no words"


def upload_of(got, title):
    """The upload URL Pending You gave for the artifact titled so, from a post's or a change's uploads; None when it
    gave none."""
    ups = [u for u in got.get("uploads") or [] if isinstance(u, dict) and isinstance(u.get("uploadUrl"), str)] if isinstance(got, dict) else []
    hit = next((u for u in ups if u.get("title") == title), ups[0] if len(ups) == 1 else None)
    return hit["uploadUrl"] if hit else None


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


def put(url, data, kind):
    """A file put to the upload URL Pending You gave for it, with its content type and crew's own User-Agent: None once
    it is there, else why not, in the words that say so. Pending You's host refuses urllib's own, Python-urllib/3.x,
    as a banned browser signature (403 Forbidden, "error code: 1010"), as every proposal card's picture was refused on
    2026-10-18; curl's and a named agent's are taken."""
    import urllib.error, urllib.request
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method="PUT",
                                                           headers={"Content-Type": kind, "User-Agent": AGENT}),
                                    timeout=CALL) as r:
            return None if 200 <= r.status < 300 else f"its upload answered {r.status}"
    except (OSError, urllib.error.URLError) as e:
        return f"its upload failed: {getattr(e, 'reason', None) or e}"


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

    def answer(self, tool, args):
        """A Pending You tool's answer as an object and None, or None and Pending You's words refusing it; refused as
        unread when it answers with no object."""
        result = self.request("tools/call", {"name": tool, "arguments": args}, tool)
        words = refused_by(result)
        if words is not None:
            return None, words
        got = reply_object(result)
        got is not None or fail(f"Pending You answered {tool} with nothing crew can read. {self.later}")
        return got, None

    def call(self, tool, args):
        """A Pending You tool's answer, as an object; refused in Pending You's words when it refuses, or as unread
        when it answers with no object."""
        got, words = self.answer(tool, args)
        if words is not None and self.held and lost(words):
            fail(lost_said(*self.held, words))
        if words is not None:
            fail(f"Pending You refused {tool}: {words}")
        return got
