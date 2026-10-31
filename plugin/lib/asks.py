#!/usr/bin/env python3
"""asks.py: what waits on a partition's main-level roles that run as their kinds (record 0047 move 6), decided from
plain facts (code.7).

A role its partition's `flume` names a stream for runs as its kind: no agent of it stands, and each of its runs is a
place the host's runner launches while anything is pending for the role, one at a time. What is pending is each ask
of the role on the partition's flywheel branch, asks.rec's Ask records, and each place the runner's records show
waiting on the role, that no ended turn took. A turn, asks.rec's Turn records, is a run's taking of everything pending
at its start (crew role start), answered by its end (crew role end); a turn still open when the next run starts was a
lost run's, superseded by the new turn, which takes its asks again, and answers nothing. roles.rec holds the record
the runner launches each role's run from, written to match the teams file.

Every function here decides on what it is given, the files' text and the runner's records as plan.py read them: it
starts no process and reads nothing, and imports only the standard library (code.1). plan.py writes what these decide
through land() (state.1)."""
import json
import re

FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*):\s?(.*)$")
# Fields a record may hold more than once, read as lists: each ask or waiting place a turn took.
LISTS = ("Took",)
# Why a place waits on its caller, as Flume's status names it (`waiting_on.why`, flume 0.3.6, read 2026-10-31 at
# agentplot/flume 3a126d4, crates/flume-seams/src/held.rs `Waits`), that makes it wait on the role its launch names as
# its recipient (design Decision 5): a stage that stopped short asking or having found work, one whose agent was lost,
# and a place sent back as often as its kind allows. A submission held for a word is an `on_hold` wait naming no
# stage, and any wait Flume reads stalled, past its bound under no hold's words (`stalled`), is the role's too.
WAITS = ("answer", "lost", "past_bound")


def records(text):
    """recutils text as its records, each (its record set, {field: value}) in file order: a field of LISTS a list, a
    value continued on `+` lines joined by newlines; descriptors and comments left out."""
    out, kind, cur = [], None, []
    for line in (text or "").split("\n") + [""]:
        if line.strip():
            cur.append(line)
            continue
        if any(l.startswith("%rec:") for l in cur):
            kind = next(l[5:].split()[0] for l in cur if l.startswith("%rec:"))
        elif cur and any(FIELD.match(l) for l in cur if not l.startswith(("#", "%"))):
            f: dict = {k: [] for k in LISTS}
            last = None
            for l in cur:
                if l.startswith(("#", "%")):
                    continue
                if l.startswith("+") and last:
                    more = l[2:] if l.startswith("+ ") else l[1:]
                    f[last] = f[last][:-1] + [f[last][-1] + "\n" + more] if last in LISTS else f[last] + "\n" + more
                    continue
                m = FIELD.match(l)
                if m:
                    last = m.group(1)
                    if last in LISTS:
                        f[last].append(m.group(2))
                    else:
                        f.setdefault(last, m.group(2))
            out.append((kind, f))
        cur = []
    return out


def whole(v):
    return isinstance(v, str) and v.isdigit()


def parse(text):
    """asks.rec as (asks, turns), each a dict of its fields: an ask whose Id is no whole number or that names no role,
    and a turn whose number is no whole number or that names no role or run, left out, so a missing value never
    becomes a number or a name (read.2)."""
    asks, turns = [], []
    for kind, f in records(text):
        if kind == "Ask" and whole(f.get("Id")) and f.get("Role"):
            asks.append(f)
        elif kind == "Turn" and whole(f.get("Turn")) and f.get("Role") and f.get("Run"):
            turns.append(f)
    return asks, turns


def parse_roles(text):
    """roles.rec as its Role records, each a dict of its fields; one naming no role left out."""
    return [f for kind, f in records(text) if kind == "Role" and f.get("Role")]


def took_of(ask):
    """How a turn's Took names an ask it took."""
    return f"ask/{ask['Id']}"


def answered(turns, role):
    """What the role's ended turns took: each ask and waiting place they answered. A superseded turn answers nothing,
    and an open one nothing yet."""
    return {x for t in turns if t["Role"] == role and t.get("Ended") for x in t["Took"]}


def pending(asks, waits, turns, role):
    """What is pending for a role (role-runs "A role has at most one run, wanted while anything is pending"): each of its
    asks, oldest first, and each place that waits on it (waits_on), that no turn ended by crew role end took; as
    (asks, waits)."""
    done = answered(turns, role)
    return (sorted((a for a in asks if a["Role"] == role and took_of(a) not in done), key=lambda a: int(a["Id"])),
            [w for w in waits if w[0] not in done])


def wanted(asks, waits, turns, role):
    """Whether the role is wanted: anything is pending for it, so the host's runner keeps a run of it."""
    mine, places = pending(asks, waits, turns, role)
    return bool(mine or places)


def took(asks, waits):
    """A new turn's Took lines for what is pending: each ask, then each waiting place by its key."""
    return [took_of(a) for a in asks] + [w[0] for w in waits]


def open_turns(turns, run):
    """The run's turns neither ended nor superseded, oldest first."""
    return sorted((t for t in turns if t["Run"] == run and not t.get("Ended") and not t.get("Superseded")), key=lambda t: int(t["Turn"]))


def open_turn(turns, run):
    """The run's open turn, the one its end answers: the newest neither ended nor superseded; None when there is none."""
    left = open_turns(turns, run)
    return left[-1] if left else None


def superseded(turns, run):
    """The turns a new start of the run marks superseded: each still open, whose run was lost or retried before its end
    (role-runs "A start takes again what a lost run took")."""
    return open_turns(turns, run)


def keyed(asks, key):
    """The ask already written with this key, or None: an ask with a key the file holds is written once (role-runs "An
    ask with a key is written once"). An ask with no key is never held."""
    return next((a for a in asks if key and a.get("Key") == key), None)


def next_id(asks):
    """The next ask's number: one past the highest on the branch, 1 for the first."""
    return 1 + max((int(a["Id"]) for a in asks), default=0)


def next_turn(turns):
    """The next turn's number: one past the highest on the branch, 1 for the first."""
    return 1 + max((int(t["Turn"]) for t in turns), default=0)


def definition_of(role):
    """The agent definition a role is started from, roles/<definition>.md, which the teams file's `roles` overrides by
    the same name: main-level ops is main-ops."""
    return "main-ops" if role == "ops" else role


def role_record(partition, role, meta):
    """The role record of a role its partition runs as its kind (design Decision 6, role-runs "A role record names its
    run"), from the partition's entry in the teams file as crew reads it and the role's definition's frontmatter, meta:
    its address and run, the main level's host, the partition's first blueprints repo, crew's kinds and the role's, the
    place's name, the stream its `flume` names, priority 0, its intent, and the definition's model and effort after
    the teams file's override (Decision 16). None for a role that stands."""
    stream = partition["flume"][role]
    if stream is False:
        return None
    label, o = partition["label"], (partition.get("roles") or {}).get(definition_of(role), {})
    return {"Role": role, "Address": f"{label}/{role}", "Run": f"{label}-{role}", "Host": partition["machine"],
            "Repository": partition["blueprints"][0], "Kinds": "crew", "Kind": f"crew-{role}", "Name": label, "Stream": stream,
            "Priority": "0", "Intent": f"{label}-{role}", "Model": o.get("model", meta["model"]), "Effort": o.get("effort", meta["effort"])}


def roles_due(records, partition, metas):
    """What the partition's roles.rec is due to match the teams file (role-runs "Role records follow the teams file"):
    (each role record to write, missing from records or differing from what is there, in the order the partition names
    its roles; each role whose record is to go, its partition no longer running it as its kind). records, the Role
    records on the branch (parse_roles); metas, {role: its definition's frontmatter} for each role the partition runs as
    its kind."""
    want = {r: role_record(partition, r, metas[r]) for r, s in partition["flume"].items() if s is not False}
    have = {x["Role"]: x for x in records}
    return [rec for r, rec in want.items() if have.get(r) != rec], [r for r in have if r not in want]


def status_of(status):
    """The place's own facts in Flume's status as the runner carried it, `flume status --json <place>`'s one line, its
    text or as parsed: the one place it holds; None when it holds no one place or is not JSON."""
    if isinstance(status, str):
        try:
            status = json.loads(status)
        except ValueError:
            return None
    if isinstance(status, dict) and isinstance(status.get("status"), dict):
        status = status["status"]
    if isinstance(status, dict) and "places" in status:
        ps = status["places"]
        status = ps[0] if isinstance(ps, list) and len(ps) == 1 else None
    return status if isinstance(status, dict) else None


def waiting(place):
    """How a place waits on its caller, read from its status by the facts of Flume 0.3.6 (read.2): (since when, its
    words) when it waits as WAITS says it waits on the role, else None. A field Flume left out is None, never text."""
    w = place.get("waiting_on")
    if not isinstance(w, dict):
        return None
    why, since, words = w.get("why"), w.get("since"), w.get("words")
    held = why == "on_hold" and w.get("stage") is None  # its submission held for a word
    if why in WAITS or held or place.get("stalled") is True:
        return (since if isinstance(since, int) and not isinstance(since, bool) else None,
                words if isinstance(words, str) and words else None)
    return None


def landed(place):
    """The commit a place landed at, read from its phase as Flume 0.3.6 gives it, `{"over": {"over": {"landed":
    {"commit": ...}}}}`, or gone or tidied after it; "" when it landed and its commit can't be read; None when it has not
    landed."""
    phase = place.get("phase")
    if not isinstance(phase, dict) or len(phase) != 1:
        return None
    body = next(iter(phase.values()))
    over = body.get("over") if isinstance(body, dict) else None
    if not isinstance(over, dict) or not isinstance(over.get("landed"), dict):
        return None
    commit = over["landed"].get("commit")
    return commit if isinstance(commit, str) else ""


def waits_on(address, requests, places):
    """The places that wait on the role at address, <label>/<role> (design Decision 5, role-runs "A place that waits on
    a role is pending for the role"), each a plain tuple (key, request, work, place, words), oldest request first: a
    place whose launch request names address as its Recipient, waiting on its caller as waiting() reads it, keyed
    place/<request>@<since when it waits>, or place/<request> where Flume gives no since; and a place crew role land
    launched for the role, its Work role/<role>/<name>, once it has landed, keyed landed/<request>. requests, the
    Request records of requests.rec; places, each host's places.rec records as the runner wrote them, Request, Place
    and Status. A place delivered and going on through its kind waits on nobody, and one whose status can't be read is
    no wait."""
    launches = {r["Request"]: r for r in requests if r.get("Act") == "launch" and r.get("Recipient") == address and whole(r.get("Request"))}
    out = []
    for p in places:
        r = launches.get(p.get("Request"))
        st = status_of(p.get("Status")) if r is not None else None
        if r is None or st is None:
            continue
        n, work = r["Request"], r.get("Work")
        where = p.get("Place") or (st.get("place") if isinstance(st.get("place"), str) else None)
        w = waiting(st)
        if w is not None:
            since, words = w
            out.append((f"place/{n}@{since}" if since is not None else f"place/{n}", n, work, where, words))
        elif (work or "").startswith("role/"):
            commit = landed(st)
            if commit is not None:
                out.append((f"landed/{n}", n, work, where, f"landed at {commit[:7]}" if commit else "landed"))
    return sorted(out, key=lambda w: int(w[1]))
