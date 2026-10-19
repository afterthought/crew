"""cards.py: crew's Pending You cards. The six of crew's own, built from the facts of their events (record 0031, briefs.13):
the proposal's, the batch's, the landing's, the deploy's, the step's and the record's, in the words rule's forms, each
following the card its thing follows, and read by its owner through crew card read (briefs.16). plan.py's act,
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
import json, os, re, select, subprocess, time

import picture
from crew import fail
from picture import cut, wrap

BRIDGE = ("pendingyou", "mcp", "--app", "claude-code")
PROTOCOL = "2025-06-18"  # the MCP revision Pending You's CLI opens its sessions with
CALL = 60  # seconds a call waits for its reply: what Claude Code's own transport waited on 2026-10-09
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
LINE = 40  # the most characters a line of a list on a card's face holds: the phone shows it in monospace
CARD_NEW = 15  # the most units new to a bolt a proposal's card takes as boxes; more link its reading session (briefs.9)
BOXES, GROUPS = 5, 4  # Pending You's limits: a question's options, and a card's questions
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


def built(key, title, summary, background="", links=(), artifacts=(), follows=None, urgency="today", picture=None,
          **form):
    """A card of crew's as a builder hands it to the act: its row's key, post_request's arguments but the area and the
    session, which the act sets, and the picture's PNG when it has one. Its title cut to Pending You's budget, its
    summary prose cut at whole sentences, never blocking, following the card its thing follows."""
    card = {"title": cut(title, TITLE), "summary": prose(summary), "context": context(background, links),
            "blocking": False, "urgency": urgency, **form}
    if artifacts:
        card["artifacts"] = list(artifacts)
    if follows:
        card["follows"] = follows
    return {"key": key, "card": card, "picture": picture}


def high(action):
    """The approve block of a card that is not undone, a landing's or a deploy's: risk high, with why, so it is
    approved only by holding the button in the app, never with a key in Herdr's popup, and never highStakes, which
    Pending You refuses on an approval."""
    return {"action": action, "risk": "high", "reversible": False, "because": "irreversible"}


# ---------------------------------------------------------------------------------------- the six builders

def landing_card(f):
    """A bolt's landing card (record 0031 §5): an approval of risk high, the units and chores that land as a list on
    its face, the counts, the batches, sluice's verdict and how far main moved in its summary, what follows as its
    rationale, sluice's pull request linked when the submission has one, and in its details only the batches.
    f: bolt, kit, units, chores, batches ({unit: the batch it was read in}), head, at (sluice's time), moved (landings
    on main since the bolt was cut), pr ({number, url}) or None, offers (the environments whose deploy will be offered
    on a card), follows."""
    units, chores, batches = list(f["units"]), list(f.get("chores") or []), f.get("batches") or {}
    parts = ([plural(len(units), "unit")] if units else []) + ([plural(len(chores), "chore")] if chores else [])
    what = joined(parts) if parts else "nothing"
    read = sorted({batches[u] for u in units if u in batches})
    said = [f"{what[0].upper()}{what[1:]} {'lands' if len(units) + len(chores) == 1 else 'land'}, every one merged"
            + (f" and every unit read in a batch ({joined([str(b) for b in read])})." if read else ".")]
    pr = f.get("pr")
    said.append(f"sluice is green at {f['head'][:7]}" + (f" since {f['at']}" if f.get("at") else "")
                + (f", its pull request #{pr['number']} linked below." if pr else "."))
    moved = f.get("moved") or 0
    said.append(f"main has moved {plural(moved, 'landing')} since the bolt was cut." if moved else
                "main has not moved since the bolt was cut.")
    offers = list(f.get("offers") or [])
    then = ("After it lands: main-level ops lands it through sluice and every host takes it"
            + (f"; {joined(offers)}'s deploy will be offered on a card." if offers else "."))
    lands = text_list(f"What lands: {plural(len(units), 'unit') if units else 'no units'}, "
                      f"{plural(len(chores), 'chore') if chores else 'no chores'}", f"land-{f['bolt']}.txt",
                      units + [f"{c} (chore)" for c in chores])
    counted = [f"batch {b}: {plural(sum(1 for u in units if batches.get(u) == b), 'unit')}" for b in read]
    background = (("Read in its batches:\n" + "\n".join(counted) + "\n\n" if counted else "")
                  + "A note naming a defect holds the landing: crew withdraws this card, and raises it again, "
                    "following this one, once the bolt is green again.")
    pr_title = f"Pull request #{pr['number']} on GitHub, opened by sluice" if pr else None
    return built(f"land/{f['bolt']}", f"Land the bolt {f['bolt']} on {f['kit']}'s main", " ".join(said), background,
                 [(pr_title, pr["url"])] if pr else (), [lands] + ([link(pr_title, pr["url"])] if pr else []),
                 f.get("follows"), kind="approve", intent="approve", approve=high(f"Land {f['bolt']} on {f['kit']}'s main"),
                 recommendedIds=["approve"], rationale=by_words(then, DETAIL))


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
                 kind="approve", intent="approve", approve=high(f"Deploy {head} to {env}"), recommendedIds=["approve"],
                 rationale=f"{env} deploys only on your word, and a deploy is not undone.")


QUIET = {"quiet": ("When the host is quiet", "No stage is cut; it could be hours"),
         "now": ("Now", "It runs at once, whatever is running"),
         "skip": ("Skip it", "It is not done")}


def step_card(f):
    """An after-deploy step's card (record 0031 §5, plan.14): the user's step a `do` with its words, where, each
    command whole and what is seen when it worked, its Done, Skip and Later the app's own; an agent's step held for
    the user's word a choice of when, quiet recommended, now or skip, each with its consequence. f: env, n, text,
    doer ("user" or the agent), held, why, where, commands, done, consequences ({quiet, now, skip}), follows."""
    key, title = f"op/{f['env']}/{f['n']}", f"After {f['env']}'s deploy: {f['text']}"
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


def record_card(f):
    """A decision record's card (record 0031 §5): a plain record's a hold-to-accept of low risk, holding the record
    whole as Markdown, its opening sentences the summary and the user's own words beside them; a record a rule of the
    user's decided between alternatives a choice asked once, loosen the rules as drafted and take the other path,
    accept the record as ruled, or send it back, its face the alternatives, the rules that decided and each loosened,
    then the record. f: kit, number, title, opening, quoted (the user's words it records), text (the record, Markdown),
    alternatives ({rules, other, text, recommended: loosen or accept}) or None, follows."""
    n = f"{int(f['number']):04d}"
    quoted = list(f.get("quoted") or [])
    words = "Your own words, recorded as your decision:\n" + "\n".join(f"“{q}”" for q in quoted) if quoted else ""
    record = markdown(f"Record {n}", f"record-{n}.md", f["text"])
    alt = f.get("alternatives")
    if not alt:
        return built(f"record/{f['kit']}/{n}", f"Accept record {n} in {f['kit']}: {f['title']}",
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
    return built(f"record/{f['kit']}/{n}", f"Record {n} in {f['kit']}: {f['title']}", summary, words, (),
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
    """The rows of a proposal's card from its commands alone, in order, each (is, command): a unit or chore new to a
    bolt, added or moved in, once ("new"); one dropped ("dropped"); one amended ("amended")."""
    new, seen, rows = new_units(argvs), set(), []
    for a in argvs:
        if a.cmd not in ("unit", "chore"):
            continue
        if a.unit in new and a.unit not in seen:
            seen.add(a.unit)
            rows.append(("new", a))
        elif a.sub == "drop":
            seen.add(a.unit)
            rows.append(("dropped", a))
        elif a.sub == "amend":
            rows.append(("amended", a))
    return rows


def proposal_form(argvs):
    """The form of a proposal's card from its commands alone (proposal_card): "approve", a hold-to-approve, when it
    has no unit rows or links its reading session, for more than CARD_NEW new units or more rows than its lists hold;
    "choice" for a lone row; "multi" for one list, BOXES rows at most; "lists" for more, each list a question. Pending
    You's update_request changes neither a card's kind nor its questions, so a rewrite that moves its chain's card from
    one form to another is followed rather than changed (plan.raise_proposal_at)."""
    rows = proposal_rows(argvs)
    if not rows or len(new_units(argvs)) > CARD_NEW or len(rows) > BOXES * GROUPS:
        return "approve"
    return "choice" if len(rows) == 1 else "multi" if len(rows) <= BOXES else "lists"


def proposal_card(f):
    """A proposal's card (record 0031 §5, plan-proposals): titled "Plan change to <bolt>: <counts>", with no number and
    no question; a sentence of what the planner proposes and why, from its case; one checkbox list, every row of the
    change a box set as proposed, a new unit or chore ticked, a dropped one unticked as "Keep <unit>", an amended one
    unticked as "Keep <unit>'s old intent", in groups of five, and nothing else to tap; a lone row the choice of its
    two sides, Pending You's lists holding two at least; a hold-to-approve of low risk when it has no unit rows, or
    more than CARD_NEW new units, which link its reading session; a paragraph per new and dropped unit on its face as
    inline Markdown; the change drawn at twice the density and as text. f: n, first (the first proposal of its
    chain, its key's), state, case, before and after (the plan at the tip and as its commands leave it), argvs (its
    commands, parsed), waiting ([teams whose conductor has yet to agree]), session (the reading session's link) or
    None. Also handed back: the boxes, each {id, unit, is: new, dropped or amended, ticked: as proposed}, and whether
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
    new, units = new_units(argvs), {}
    rows = []
    for is_, a in proposal_rows(argvs):
        if is_ == "new":
            units[a.unit] = a
            moved = a.sub == "move"
            src = d["came_from"].get(a.unit)
            rows.append({"id": f"add:{a.unit}", "unit": a.unit, "is": "new", "ticked": True,
                         "label": f"Move {a.unit} in" if moved else f"Add {a.unit}", "detail": d["intent"].get(a.unit) or "",
                         "consequence": f"Cleared: stays in {'the queue' if src is None else 'bolt ' + src}; the rest still applies"
                         if moved else "Cleared: not added; the rest still applies"})
        elif is_ == "dropped":
            units[a.unit] = a
            rows.append({"id": f"keep:{a.unit}", "unit": a.unit, "is": "dropped", "ticked": False,
                         "label": f"Keep {a.unit}", "detail": f"Proposed: drop. Why: {a.reason}",
                         "consequence": "Ticked: it stays; the rest still applies"})
        else:
            rows.append({"id": f"old:{a.unit}", "unit": a.unit, "is": "amended", "ticked": False,
                         "label": f"Keep {a.unit}'s old intent", "detail": d["amended"].get(a.unit) or "",
                         "consequence": "Ticked: its intent stays as it was; the rest still applies"})
    session = len(new) > CARD_NEW or len(rows) > BOXES * GROUPS
    shape = proposal_form(argvs)

    def option(r):
        return {"id": r["id"], "label": cut(r["label"], LABEL), "detail": by_words(r["detail"], DETAIL),
                "consequence": by_words(r["consequence"], DETAIL)}
    if shape == "approve":
        how = "Hold to apply it whole."
        form = dict(kind="approve", intent="approve", recommendedIds=["approve"],
                    approve={"action": f"Apply the plan change to {to}", "risk": "low", "reversible": True})
    elif shape == "choice":
        r = rows[0]
        how = "Its one row is set as proposed; pick the other side and send to change it."
        other = {"new": f"Leave {r['unit']} out", "dropped": f"Drop {r['unit']}", "amended": f"Amend {r['unit']}"}[r["is"]]
        options = [option(r), {"id": "unticked", "label": cut(other, LABEL)}]
        form = dict(kind="choice", intent="decide", options=options, recommendedIds=[r["id"] if r["ticked"] else "unticked"])
    else:
        how = "Each row below is set as proposed; flip any and send."
        g = -(-len(rows) // BOXES)
        sizes = [len(rows) // g + (1 if k < len(rows) % g else 0) for k in range(g)]
        groups = [rows[sum(sizes[:k]):sum(sizes[:k + 1])] for k in range(g)]
        lists = [{"options": [option(r) for r in grp], "multi": {"min": 0, "max": len(grp)},
                  "recommendedIds": [r["id"] for r in grp if r["ticked"]]} for grp in groups]
        form = (dict(kind="multi", intent="decide", **lists[0]) if g == 1 else
                dict(intent="decide", about={"kind": "other", "title": cut(f"Plan change to {to}", 120)},
                     questions=[dict(id=f"rows-{k}", kind="multi", title=f"The change, part {k} of {g}: each row as proposed", **q)
                                for k, q in enumerate(lists, 1)]))
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
    named = [r["is"] for r in rows if r["is"] in ("new", "dropped")]
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
    """Each card the run record's entries show posted, oldest first: {key, card, state}, its state None while it is
    open, else its close's, closed, withdrawn, declined or lost."""
    out = []
    for e in entries:
        if e.get("Act") == "card.post" and e.get("Card") and not e.get("Refused"):
            out.append({"key": e.get("Key") or "", "card": e["Card"], "state": None})
        elif e.get("Act") == "card.close" and e.get("Card") and not e.get("Refused"):
            for c in out:
                if c["card"] == e["Card"] and c["state"] is None:
                    c["state"] = e.get("State") or "closed"
    return out


def follows_of(kind, thing, entries):
    """The card a card of kind follows, so one thing's chain reads as one thread on the phone (record 0031 §5), from the
    run record's entries, oldest first: its id, or None. A landing raised again follows the bolt's last landing card
    once that is closed, as a defect note holds it; a deploy follows its environment's last card when the user
    declined it, else the landing card of the bolt whose landing left main at the deployed head; a step follows the
    step card raised after its environment's last deploy card, else that card. A proposal, a batch and a record follow
    nothing. A card lost to its owner is followed by none, since Pending You takes only a card of the asker's own.
    thing: a landing's {bolt}, a deploy's {env, head}, a step's {env, key}."""
    cards = [c for c in posted_cards(entries) if c["state"] != "lost"]

    def landing(bolt):  # a bolt's landing cards, keyed by the bolt, or by its head before record 0031
        return [c for c in cards if c["key"] == f"land/{bolt}" or c["key"].startswith(f"land/{bolt}/")]
    if kind == "land":
        mine = landing(thing["bolt"])
        return mine[-1]["card"] if mine and mine[-1]["state"] else None
    if kind == "deploy":
        mine = [c for c in cards if c["key"] == f"deploy/{thing['env']}"]
        if mine and mine[-1]["state"] == "declined":
            return mine[-1]["card"]
        head = thing.get("head") or ""
        bolts = [o[5:] for e in entries if e.get("Act") == "bolt.land" and not e.get("Refused") and head
                 and (e.get("Head") or "")[:7] == head[:7] for o in e.get("On") or [] if o.startswith("bolt/")]
        landed = landing(bolts[-1]) if bolts else []
        return landed[-1]["card"] if landed else None
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
        (re.compile(r"^record/([a-z0-9][a-z0-9-]*)/(\d{4})$"), "record/{}/{}"))
# What update_request takes of a card crew built. It changes neither a card's kind nor its questions, so a card whose
# kind changed, or one that carries questions, a proposal's rows in lists, is followed by a new card (revision).
CHANGED = ("title", "summary", "context", "artifacts", "approve", "options", "multi", "recommendedIds", "action",
           "rationale", "urgency", "blocking")
DEAD = "An older copy of this card was lost: dismiss it in the app."


def row_object(key):
    """The run record's object of one of crew's six cards' keys, the row's: a proposal's, a batch's, a bolt's for its
    landing, an environment's for its deploy and steps, a record's; None for any other key."""
    for pattern, obj in ROWS:
        m = pattern.match(key)
        if m:
            return obj.format(*m.groups())
    return None


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


def revision(got, kind_changed=False, questions=False):
    """How crew puts a changed card before the user, from get_request's answer, whether the card's kind changed and
    whether the card crew built again carries questions: "change", the card changed in place, while it waits on them;
    "follow" once they have answered it, since Pending You changes a card only while it waits and an answered one is
    followed by a new card (its guide, "Follow up with a new card"), and when its kind changed or it carries questions,
    which update_request never changes (CHANGED): a card changed in place would keep its old questions under its new
    title, as proposal 140's did over proposal 139's rows on 2026-10-18."""
    return "follow" if kind_changed or questions or isinstance(got, dict) and got.get("status") == "answered" else "change"


def post_key(entries, key, by):
    """The idempotency key crew posts its card under a row's key with, from the run record's entries: the row's key for
    its first card, and for each card after one of `by`'s under it closed (answered and followed, declined, withdrawn or
    lost), the key with that card's revision, <key>:<n>, since Pending You gives a key's card back as long as it keeps
    it and takes one key per question. A card still open under the key keeps its own key, so posting it again gives it
    back."""
    mine = [e for e in entries if e.get("Act") == "card.close" or (e.get("Key") == key and e.get("By") == by)]
    closed = {c["card"] for c in posted_cards(mine) if c["state"]}
    return f"{key}:{len(closed) + 1}" if closed else key


def posted_again(card):
    """A card posted again under its key once its first copy was lost to its owner: its summary saying so first."""
    return dict(card, summary=prose(f"{DEAD}\n\n{card['summary']}"))


def close_call(got, card, name, outcome=None, reason=None):
    """How crew closes a card, from get_request's answer: one the user answered acked at its version with what was
    done on it, the outcome, or the reason it is withdrawn; one still waiting withdrawn with the reason, or the
    outcome. Either is cut to OUTCOME characters, since Pending You refuses a longer one (proposal 142's close on
    2026-10-18: "outcome: Too big: expected string to have <=200 characters"); the run record keeps crew's words
    whole. The tool, its arguments, and the close's state as the run record keeps it."""
    def said(first, then):
        words = first if first is not None else then
        return cut(words, OUTCOME) if isinstance(words, str) else words
    if got.get("status") == "answered":
        return ("ack_answer", {"requestId": card, "name": name, "expectedVersion": version_of(got, card),
                               "outcome": said(outcome, reason)},
                "closed" if outcome is not None else "withdrawn")
    return "cancel_request", {"requestId": card, "name": name, "reason": said(reason, outcome)}, "withdrawn"


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
    """A file put to the upload URL Pending You gave for it, with its content type: None once it is there, else why
    not, in the words that say so."""
    import urllib.error, urllib.request
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method="PUT", headers={"Content-Type": kind}),
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
