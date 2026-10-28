#!/usr/bin/env python3
"""board.py: the board of a partition's flow, read from crew's state.

  crew board [--label L] [--json]    the flow as four lanes stacked one above the other, one object to a line:
                                     Inception (the signals no move has taken, by who captured them, and the
                                     explorations on each kit's main), Bolt plan (the open proposals, the planned
                                     bolts and the queue), Construction (each held bolt as a ledger of its units and
                                     fixes) and Operation (the bolts landed in the last seven days, then each
                                     environment's deploys of that week and those still open, and the operations
                                     waiting on it); every rail row a marker on its object, and what needs attention
                                     at the foot
  crew _views <label>                one partition's read as the host's follower makes it: the rail printed as crew
                                     rail prints it, the card sessions of closed cards and gone rows ended as crew rail
                                     ends them, and the board's data written for the board tab, with each agent's view
                                     of it for the band crew's mod draws above that agent's prompt
  crew _follow [--once]              the host's follower with no tab, the command a job of the host's runs: one read in
                                     its own process for every partition with an operator session here, fetching once a
                                     minute on its clock and showing this host's writes within seconds, checking first
                                     what moved and reading only that, each kit's queue followed through sluice's
                                     overview watch; the due restarts handed out once crew's checkout or the teams file
                                     moved (crew _update), and each partition's rail, board and agents' views written as
                                     frames, stale after three minutes; it waits for the host's follower lock while a
                                     rail tab holds it. --once makes one tick, with no watch, and ends
  crew _rail <label> [--once]        the rail tab: the latest rail the host's follower wrote, drawn whenever it
                                     changes, headed with its age once stale; while no one holds the host's follower
                                     lock, it takes it and follows itself. --once draws once and follows nothing
  crew _board <label> [--once]       the board tab: the latest board the host's follower wrote, drawn at the pane's
                                     width whenever it or the pane changes

Read from the plan, the proposals, the moves, the signals, the kits and the run record, in one read that also makes the
rail (plan.rail_read); no state is written, only the frames the host's follower hands the rail and board tabs and the
agents' mods, in crew's cache, each one redraw and not state (state.4). A host has one follower, holding its lock while
it follows: swancloud's job running crew _follow, or, where none runs, a rail tab's own loop. Its refresh, as it prints
the rail, ends the card sessions whose card is closed or whose row is gone, as crew rail does; crew board ends nothing.
The board answers nothing and prints no command: the rail and its shell are where things are answered."""
import argparse, contextlib, datetime, fcntl, io, json, os, pathlib, re, shlex, shutil, signal, subprocess, sys, tempfile, time

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew, gather, ops, plan, record, sites  # noqa: E402
from crew import Refusal, fail  # noqa: E402

# Flywheel Next's glyph for the decision a rail row asks (S17): an approval, held on the card's button. An operation's
# card, a deploy's word or a step marked done or declined, is held too.
GLYPH = {"proposals": "✓", "land": "✓", "operations": "✓"}
ATTENTION = "!"
# A unit's stage as one pip, filling as it goes: not begun, being designed, coded, every task ticked, merged; a stage
# crew could not read is "?". A bolt is its units' pips in the plan's order.
PIP = {"queued": "○", "waiting": "○", "ready": "○", "amended": "◔", "construct": "◔", "planned": "◔", "code": "◑", "verify": "◕",
       "merged": "●", "landed": "●"}
# How many explorations an agent's view names before it counts the rest.
SHOWN = 6
# The frames the host's follower writes for the rail and board tabs and the agents' mods, by label.
FRAMES = pathlib.Path.home() / ".cache/crew/board"
STALE = 3 * record.PERIOD  # seconds: three of the follower's periods
SIGNAL = re.compile(r"^signals/([^/]+)/([0-9]{2}-[^/]+)\.md$")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
STYLES = {"bold": "\033[1m", "dim": "\033[2m"}


def iso(t):
    return t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def when(at):
    """A time the board was handed, an ISO time or a date alone, as an aware datetime, one without a zone taken as UTC
    (a date as its midnight there); None when it is neither."""
    try:
        t = datetime.datetime.fromisoformat(at.replace("Z", "+00:00")) if at else None
    except ValueError:
        return None
    return t if not t or t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def stamp(at):
    """A capture's time as the board's data holds it: a date alone as it is, a time in UTC whatever zone it was
    written in; None when it is neither. The board's text says it in the reader's own time."""
    t = when(at)
    return None if not t else at if DATE.fullmatch(at) else iso(t)


# ------------------------------------------------------------------------------------------------- the read

def texts(repo, tip, paths):
    """The text of each path at tip in crew's cache of the repo, {path: text}, a path that is not there left out: in one
    git cat-file --batch, or from the follower's kept blobs when it reads (plan.Kept)."""
    files = plan.kept_listing(repo, tip)
    if files is not None:
        got = {p: plan.READ.follower.text(repo, files[p]) for p in paths if p in files}
    else:
        got = dict(zip(paths, plan.cat_file(repo, [f"{tip}:{p}" for p in paths])))
    return {p: t for p, t in got.items() if t is not None}


def signals_at(repo, tip, home, moved):
    """Each signal at tip whose id has no move, with its capture's captured_by (its source when it has none) and when
    the capture was made (its at, else its event_date, which is what a signal's age counts from, as stamp gives it),
    its kind and the first line of its body."""
    sigs = [m.groups() for m in map(SIGNAL.match, plan.paths_at(repo, tip, "signals/")) if m]
    sigs = [(c, n) for c, n in sigs if f"{c}/{n}" not in moved]
    got = texts(repo, tip, sorted({f"signals/{c}/capture.md" for c, _ in sigs}) + [f"signals/{c}/{n}.md" for c, n in sigs])
    out = []
    for c, n in sigs:
        cap, text = got.get(f"signals/{c}/capture.md"), got.get(f"signals/{c}/{n}.md")
        body = re.sub(r"^---\n.*?\n---\n", "", text or "", count=1, flags=re.S)
        out.append({"signal": f"{c}/{n}", "home": home, "captured_by": plan.field(cap, "captured_by") or plan.field(cap, "source") or None,
                    "at": stamp(plan.field(cap, "at") or plan.field(cap, "event_date")), "kind": plan.field(text, "kind") or None,
                    "first": next((l.strip() for l in body.splitlines() if l.strip()), None)})
    return out


def signals(fleet, label, tip):
    """The label's signals no move has taken, in both homes: the flywheel's branch at the tip the plan was read from
    (None when the branch is not started, so nothing is moved), and main of the partition's first blueprints repo;
    and each home that could not be read, {what: why}. When the branch's signals and moves can't be read, which
    signals are moved can't be known, and none is listed (read.1)."""
    repo, ref = plan.state_of(fleet, label)
    try:
        moved = {m.get("Signal") for m in plan.Plan(plan.show(repo, tip, "moves.rec") or "").recs("Move")} if tip else set()
        out = signals_at(repo, tip, "branch", moved) if tip else []
    except Refusal as e:
        return [], {f"{ref} of {repo}": str(e)}
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    try:
        btip = plan.fetch(srepo, "main")
        out += signals_at(srepo, btip, "blueprints", moved) if btip else []
    except Refusal as e:
        return out, {f"main of {srepo}": str(e)}
    return out, {}


def flow_read(fleet, labels, sweep=False):
    """One read of the labels' flow, which makes both the rail and the board: the rail's read with every team of the
    labels surveyed, its dev servers, slots and explorations too (plan.rail_read), and the signals of each label whose
    plan was read; a plan that could not be read leaves its moves unknown, and is named already. With sweep, the rail
    tab's, the read ends the card sessions of closed cards and gone rows, as crew rail's does."""
    read = plan.rail_read(fleet, labels, board=True, sweep=sweep)
    read["signals"] = {l: signals(fleet, l, tip) for l, _, tip, _ in read["found"]}
    return read


# ------------------------------------------------------------------------------------------------- the data

def marker(r, cards, label, logs):
    """A rail row as a marker: its group, its card key, its glyph, when it began to wait, its card, open or None, and,
    when none is open, the words of Pending You's refusal of the last post under its key, as the rail's card line gives
    them (plan.last_refusal), or None; logs are the label's run-record entries the rail read."""
    card = [c for c in cards if (c["label"], c["key"]) == (label, r["key"])]
    return {"group": r["group"], "key": r["key"], "glyph": GLYPH[r["group"]], "at": r.get("date") or iso(r["at"]),
            "card": {"by": card[-1]["by"], "host": card[-1]["host"], "at": iso(card[-1]["at"])} if card else None,
            "refused": None if card else plan.last_refusal(logs, r["key"])}


def markers(rows, cards, label, group, obj, logs):
    """The rail's rows for an object, as markers: a held bolt's landing row is its kit's, land/<kit>, which names it
    among its bolts (record 0031 as amended 2026-10-23); any other row is the object's by its key."""
    return [marker(r, cards, label, logs) for r in rows if r["label"] == label and r["group"] == group
            and (obj in [b["bolt"] for b in r.get("bolts", [])] if group == "land" else r["key"].split("/")[1] == obj)]


def keyed(rows, cards, label, key, logs):
    """The rail's row with that card key, as a marker, when there is one: an operation's, whose key names the deploy or
    the step itself."""
    return [marker(r, cards, label, logs) for r in rows if key and r["label"] == label and r["key"] == key]


def records_proposed(entries, cards):
    """The decision records proposed and not yet accepted or rejected, from the record.<status> entries crew record
    writes on record/<kit>/<number>, oldest first: each {kit, number, at, settled}, settled when the user's yes was
    given in the pane, and its card, {by, card, at} while one is open under the record's key, as record 0031 keys it or
    with the commit after it as it was keyed before, else None."""
    out = {}
    for e in entries:
        m = re.fullmatch(r"record\.(proposed|accepted|rejected)", e.get("Act") or "")
        obj = next((o for o in e.get("On") or [] if re.fullmatch(r"record/[a-z0-9][a-z0-9-]*/[0-9]{4}", o)), None)
        if not m or not obj or e.get("Refused"):
            continue
        out.pop(obj, None)
        if m.group(1) == "proposed":
            out[obj] = {"kit": obj.split("/")[1], "number": obj.split("/")[2], "at": e["At"], "settled": e.get("State") == "settled in the pane"}
    for obj, r in out.items():
        open_ = [c for c in cards if c["key"] and (c["key"] == obj or c["key"].startswith(obj + "/"))]
        r["card"] = {"by": open_[-1]["by"], "card": open_[-1]["card"], "at": iso(open_[-1]["at"])} if open_ else None
    return list(out.values())


def environments(fleet, label, teams, entries, rows, cards, since, logs):
    """The partition's environments for the Operation lane: each one's deploys that moved since since or are still open,
    and the operations waiting on it, as ops.environments reads them from the run record (plan.14, state.4), each
    deploy and operation with its rail row's marker; and the teams on that host, which is what the page narrows by."""
    return [{"env": env, "teams": [t["team"] for t in teams if t["host"] == env],
             "deploys": [dict(d, markers=keyed(rows, cards, label, d["row"], logs)) for d in v["deploys"]],
             "waiting": [dict(w, markers=keyed(rows, cards, label, w["row"], logs)) for w in v["waiting"]]}
            for env, v in ops.environments(entries, iso(since)).items()]


def board_data(fleet, labels, read, now):
    """The board of each label as data, the fields the page reads (`crew board --json`). Each partition lists its teams,
    and each object of its lanes says the teams it belongs to, which is what the page narrows by: a held bolt and a
    landing, its team; a signal, the team whose agent captured it; a proposal, the teams holding the bolts it names
    and those building the repository of a bolt no team holds, of a bolt it makes or of a queued unit; anything else,
    every team building its repository. A ledger's units, chores and fixes are its own; each unit or chore says its kind,
    and each of them its merge standing in sluice's queue, as the ledger its landing standing on its kit's main and why
    the queue can't be read on its team's host when it can't (plan.submission_rows, teams.22).
    Each partition lists too its open cards, oldest first, each with whose it is and what it is, a row's, a decision
    record's or a question (plan.card_kind), and the decision records proposed and not yet accepted or rejected, which
    the design agent's band shows (records_proposed)."""
    here = crew.this_host()
    rows, cards, sv = read["rows"], read["cards"], read["sv"]
    since = plan.utc(record.when(None)[1])
    parts = []
    for l in labels:
        p = crew.partition_of(fleet, l)
        found = next(((repo, tip, pl) for x, repo, tip, pl in read["found"] if x == l), None)
        repo, tip, pl = found or (plan.state_of(fleet, l)[0], None, None)
        unread, logs = read["unread"].get(l, {}), read.get("logs", {}).get(l, [])
        teams = [{"team": t, "kit": fleet["teams"][t]["kit"]["name"], "kits": [k["name"] for k in crew.kits_of(fleet["teams"][t])],
                  "host": fleet["teams"][t]["machine"]} for t in p["teams"]]

        def building(repo):
            return [t["team"] for t in teams if repo and repo in t["kits"]]

        def ordered(ts):
            return [t for t in p["teams"] if t in ts]
        hosts = {}  # each host asked for its kits, never for its run record, which is read from the branch (read.5)
        for h in sorted(crew.partition_hosts(fleet, l)):
            v = sv.get(h)
            hosts[h] = f"its kits: {v['error']}" if v and not v["ok"] else True
        attention = [{"what": "host", "name": h, "why": v} for h, v in hosts.items() if v is not True]
        attention += [{"what": "plan", "name": n, "why": f"its run record: {why}"} for n, why in unread.items()]
        attention += [{"what": "plan", "name": n, "why": why} for n, why in read["errors"].items() if n.startswith(f"{l}/main of ") or n == f"the plan of {l}"]
        if found and not tip:
            attention.append({"what": "plan", "name": f"{l}/main of {repo}", "why": "not started, so there is no plan to read"})
        sigs, sunread = read["signals"].get(l, ([], {}))
        attention += [{"what": "signals", "name": n, "why": why} for n, why in sunread.items()]

        explorations = []
        for kit in dict.fromkeys(k["name"] for t in sorted(p["teams"]) for k in crew.kits_of(fleet["teams"][t])):
            for t in (crew.with_kit(fleet["teams"][x], kit) for x in sorted(p["teams"]) if crew.builds(fleet["teams"][x], kit)):
                k = (sv.get(t["machine"]) or {}).get("kits", {}).get(t["kit"]["main"]) or {}
                if k.get("ok") and "explorations" in k:
                    explorations += [{"kit": kit, "name": e["name"], "first": e["first"], "teams": building(kit)} for e in k["explorations"]]
                    break

        def proposal_teams(d):
            """The teams of each bolt a proposal's changes name, the team holding it or else those building its
            repository; and, where a change makes a bolt or names the queue, those building that bolt's repository or
            the unit's. A change that names no repository adds none."""
            bolts = {b.name(): (b.get("Team"), b.get("Repo")) for b in pl.bolts()}
            units = {u.name(): u.get("Repo") for u in pl.work()}
            out = []
            for c in d["changes"]:
                a = plan.do_args(l, c["do"])
                key = ("unit" if a.cmd == "chore" else a.cmd, a.sub)  # a chore's command reaches teams as the unit's
                if key == ("bolt", "new"):
                    bolts.setdefault(a.bolt, (None, a.repo))
                elif key == ("unit", "add"):
                    units[a.unit] = a.repo or bolts.get(a.bolt, (None, None))[1]
                for n, _ in getattr(a, "into", None) or []:
                    units[n] = units.get(a.unit)
                for b in c["bolts"]:
                    team, repo = bolts.get(b, (None, None))
                    out += [team] if team else building(repo)
                # a move that touches fewer than two bolts leaves or joins the queue; any other change touching none
                # is a bolt it makes or a queued unit
                if len(c["bolts"]) < (2 if key == ("unit", "move") else 1):
                    out += building(bolts.get(a.bolt, (None, None))[1] if a.cmd == "bolt" else units.get(a.unit))
            return ordered(out)

        def captured(s):
            kind, of = plan.role(fleet, s["captured_by"])
            return [of] if kind in ("conductor", "team") and of in p["teams"] else []
        proposals = [{"proposal": d["proposal"], "by": d["by"], "opened": d["opened"], "case": (d["case"] or "").splitlines()[0] if d["case"] else None,
                      "waiting": d["waiting"], "markers": markers(rows, cards, l, "proposals", str(d.get("first") or d["proposal"]), logs), "teams": proposal_teams(d)}
                     for d in read["props"] if d["label"] == l]
        planned, queue, construction = [], [], []
        if pl:
            st = plan.Stages(fleet, pl, sv)
            for b in pl.bolts():
                units = pl.work_of(b.name())
                if not b.get("Team"):
                    planned.append({"bolt": b.name(), "repo": b.get("Repo"), "goal": b.get("Goal"), "teams": building(b.get("Repo")),
                                    "units": [{"unit": u.name(), "kind": plan.kind_of(u), "stage": st.of(u.name())["stage"]} for u in units]})
                    continue
                t = fleet["teams"].get(b.get("Team"))
                k, _ = st.kit(b) if t else (None, None)
                k = k or {}
                held = k.get("slots", {}).get(b.get("Team"), [])

                def url(path):
                    return sites.url_of(fleet, here, t["machine"], k.get("sites", {}).get(path, {}), k.get("routes"))[0] if path and k else None

                def slot(kind, name):
                    return next((s["slot"] for s in held if s.get("kind") == kind and s.get("name") == name), None)
                state = st.bolt_state(b) if t else "unknown"
                fixes = [f for f in k.get("fixes", []) if f["bolt"] == b.name()]
                unread = k.get("submissions_error")
                subs, landing = plan.submission_rows(None if unread else k.get("submissions"), b.name(),
                                                     [(u.name(), plan.kind_of(u)) for u in units] + [(f["fix"], "fix") for f in fixes])
                ledger = {"bolt": b.name(), "repo": b.get("Repo"), "goal": b.get("Goal"), "team": b.get("Team"), "host": t["machine"] if t else None,
                          "state": state, "url": url(k.get("bolts", {}).get(b.name(), {}).get("worktree")),
                          "markers": markers(rows, cards, l, "land", b.name(), logs), "teams": [b.get("Team")], "units": [], "fixes": [],
                          "landing": landing, "submissions_error": unread}
                for u in units:
                    s = st.of(u.name())
                    ledger["units"].append({"unit": u.name(), "kind": plan.kind_of(u), "stage": s["stage"], "tasks": s["tasks"],
                                            "slot": slot(plan.kind_of(u), u.name()), "submission": subs.get(u.name()),
                                            "worktree": s["worktree"], "url": url(s["worktree"])})
                ledger["fixes"] = [{"fix": f["fix"], "merged": f["merged"], "slot": slot("fix", f["fix"]), "submission": subs.get(f["fix"]),
                                    "worktree": f["path"], "url": url(f["path"])} for f in fixes]
                construction.append(ledger)
                if state == "landed":
                    attention.append({"what": "landed", "name": b.name(), "why": "every unit has landed on main, and the bolt is still in the plan"})
            queue = [{"unit": u.name(), "kind": plan.kind_of(u), "repo": u.get("Repo"), "sources": u.all("Source"), "teams": building(u.get("Repo"))}
                     for u in pl.queue()]
        operation = [{"bolt": x["bolt"], "at": iso(x["at"]), "by": x["by"], "units": x["units"], "team": read["gives"].get((l, x["bolt"])),
                      "teams": [read["gives"][(l, x["bolt"])]] if read["gives"].get((l, x["bolt"])) else []}
                     for x in sorted(read["landings"], key=lambda x: x["at"], reverse=True) if x["label"] == l and x["at"] and x["at"] >= since]
        envs = environments(fleet, l, teams, read.get("ops", {}).get(l, []), rows, cards, since, logs)
        mine = sorted((c for c in cards if c["label"] == l), key=lambda c: (c["at"], c["card"]))
        parts.append({"label": l, "plan": tip, "hosts": hosts, "teams": teams,
                      "cards": [{"key": c["key"], "card": c["card"], "by": c["by"], "host": c["host"], "at": iso(c["at"]),
                                 "kind": plan.card_kind(c["key"])} for c in mine],
                      "records": records_proposed(logs, mine),
                      "inception": {"signals": sorted((dict(s, teams=captured(s)) for s in sigs),
                                                      key=lambda s: (when(s["at"]) is None, when(s["at"]) or now, s["signal"])),
                                    "explorations": explorations},
                      "bolt_plan": {"proposals": proposals, "planned": planned, "queue": queue},
                      "construction": construction, "operation": operation, "environments": envs, "attention": attention})
    return {"read_at": iso(now), "from": here, "partitions": parts, "unread": read["errors"]}


# ------------------------------------------------------------------------------------------------- the text

def fields(*xs):
    """Segments joined by two spaces, an empty one left out: each a string, (string, style), or a list of those."""
    out = []
    for x in xs:
        x = x if isinstance(x, list) else [x if isinstance(x, tuple) else (x, None)]
        if any(t for t, _ in x):
            out += ([("  ", None)] if out else []) + x
    return out


def named(repo, name):
    """A bolt's or a queued unit's name with its repository dim before it (S14)."""
    return [(repo, "dim"), (" ", None), (name, None)] if repo else [(name, None)]


def card_of(ms):
    """What each marker of a line says of its card at the line's end: open and who asked it, none open, or none open
    because Pending You refused its row's last post, which the row then owes."""
    return [(f"card open, asked by {m['card']['by']}" if m["card"] else
             "no card open, its post refused" if m.get("refused") else "no card open", None) for m in ms]


def row(segs, gutter=None, indent=0, ms=()):
    """One line as segments: a header or heading at the left edge, or, with a gutter, an object, its marker in the
    gutter and its card said at the line's end."""
    segs = ([(gutter.ljust(2) + " " * indent, None)] if gutter is not None else []) + segs
    for c in card_of(ms):
        segs += [("  ", None), c]
    return segs


def gutter(ms, attention=False):
    return ATTENTION if attention else (ms[0]["glyph"] if ms else " ")


def stage_of(u):
    """A unit's stage with its tasks, a chore's with `chore` before it (plan.11), in the board and each agent's view."""
    return (("chore " if u.get("kind") == "chore" else "") + u["stage"]
            + (f" {u['tasks'][0]}/{u['tasks'][1]}" if u["stage"] in ("code", "verify") and u["tasks"] else ""))


def local(at):
    return f"{plan.utc(at).astimezone():%Y-%m-%d %H:%M}"


def deploy_state(d):
    """Where a deploy stands, as the board says it: waiting on the user's word, replaced unanswered or once the word
    went to another commit, its outcome and when it ended, at the step that failed, deploying, or approved and not yet
    deployed."""
    if d["answer"] == "waiting":
        return "waits on the user's word"
    if d["answer"] == "replaced":
        return "approved, then the word went to a newer offer" if d["word"] else "replaced by a newer offer, unanswered"
    if d["ended"]:
        failed = next((x["step"] for x in d["steps"] if x["outcome"] == "failed"), None)
        return f"{d['outcome'] or 'ended'} {local(d['ended'])}" + (f" at the {failed}" if failed else "")
    if d["started"]:
        return f"deploying since {local(d['started'])}"
    return "approved, not yet deployed"


def deploy_fields(env, d):
    """A deploy on one line: its environment, the commit and the one it comes from, where it stands, whose word it was
    deployed on, and the bolts it carries, or why the record can't tell."""
    frm = "from nothing deployed" if d["from"] in (None, "", "none") else f"from {d['from'][:7]}"
    carries = (f"carrying {', '.join(d['bolts'])}" if d["bolts"] else "carrying no landing") if d["bolts"] is not None else f"carrying what can't be read: {d['bolts_why']}"
    return fields(env, f"deploy {d['to'][:7]} {frm}", deploy_state(d), f"approved by {d['word']['by']}" if d["word"] and d["word"]["by"] else "",
                  (carries, "dim"))


def waiting_fields(env, w):
    """An operation waiting on an environment: its key, who has it, held for the user's word or not, a deploy waiting
    at its gate for the user (plan.14), and its first line or note."""
    said = {"handed": f"handed to {w['agent'] or w['doer']}", "failed": "failed"}.get(w["state"]) or (
        "waits at its gate for the user" if w.get("gate") else
        "waits on the user" if w["doer"] == "user" else
        f"held for the user's word, for {w['agent'] or w['doer'] or 'its doer'}" if w.get("held") else
        f"waits for {w['agent'] or w['doer'] or 'its doer'}")
    return fields(env, w["key"], said, w["text"] or w["note"] or "")


def board_text(data, width=None, color=False, stale=None):
    """The board as text: for each partition a header, the four lanes in order, each a bold heading with its objects
    under it or none, then attention. A marker sits in a two-column gutter at the left of its object's line, its card
    said at the line's end. Each line is cut to width when that is given; bold and dim only with color. stale, when
    given, is how long ago the board was read, said in its header."""
    out = []
    read_at = plan.utc(data["read_at"])

    def line(segs, gutter=None, indent=0, ms=()):
        """One line: a header or heading at the left edge, or, with a gutter, an object, its marker in the gutter."""
        segs = row(segs, gutter, indent, ms)
        text, n = "", 0
        for s, style in segs:
            if width is not None:
                s = s[:max(0, width - n)]
            n += len(s)
            text += f"{STYLES[style]}{s}\033[0m" if color and style and s else s
        out.append(text.rstrip())

    def heading(name):
        line([(name, "bold")])
    for i, p in enumerate(data["partitions"]):
        if i:
            out.append("")
        answered = [h for h, v in p["hosts"].items() if v is True]
        line([(f"{p['label']} board, as of {read_at.astimezone():%H:%M:%S}" + (f" ({stale} ago: the host's follower has not refreshed it since)" if stale else "")
                      + f", read from {', '.join(answered) or 'no host'}", None)])

        heading("Inception")
        sigs, groups = p["inception"]["signals"], {}
        for s in sigs:
            groups.setdefault(s["captured_by"], []).append(s)
        for who, mine in groups.items():
            oldest = next((s["at"] for s in mine if when(s["at"])), None)
            said = "" if not oldest else f", the oldest captured {oldest}" if len(oldest) == 10 else f", the oldest captured {plan.age(when(oldest), read_at)} ago"
            line(gutter=" ", segs=fields(f"signals captured by {who or 'no one named'}", f"{len(mine)} not moved{said}"))
            for s in mine:
                line(fields(s["kind"] or "-", s["first"] or "", (s["signal"], "dim")), " ", 2)
        for e in p["inception"]["explorations"]:
            line(fields("exploration", named(e["kit"], e["name"]), e["first"] or ""), " ")
        if not sigs and not p["inception"]["explorations"]:
            line([("none", None)], " ")

        heading("Bolt plan")
        bp = p["bolt_plan"]
        for d in bp["proposals"]:
            line(fields(f"proposal {d['proposal']} by {d['by']}", d["case"] or "",
                        "waiting on " + ", ".join(f"{t}-conductor" for t in d["waiting"]) if d["waiting"] else ""), gutter(d["markers"]), 0, d["markers"])
        for b in bp["planned"]:
            line(fields(named(b["repo"], b["bolt"]), b["goal"] or ""), " ")
            for u in b["units"]:
                line(fields(u["unit"], stage_of(u)), " ", 2)
        for u in sorted(bp["queue"], key=lambda u: u["repo"] or ""):
            line(fields(named(u["repo"], u["unit"]), "chore queued" if u.get("kind") == "chore" else "queued", ", ".join(u["sources"])), " ")
        if not (bp["proposals"] or bp["planned"] or bp["queue"]):
            line([("none", None)], " ")

        heading("Construction")
        for b in p["construction"]:
            line(fields(named(b["repo"], b["bolt"]), f"{b['team']} on {b['host']}" if b["host"] else b["team"],
                        state_said(b["state"]), landing_said(b), queue_said(b, True)), gutter(b["markers"], b["state"] == "landed"), 0, b["markers"])
            for u in b["units"]:
                line(fields(u["unit"], stage_of(u), merge_said(u), u["slot"] or "", u["url"] or ""), " ", 2)
            for f in b["fixes"]:
                line(fields(f["fix"], "fix merged" if f["merged"] else "fix", merge_said(f), f["slot"] or "", f["url"] or ""), " ", 2)
            if b["url"]:
                line(fields("server", b["url"]), " ", 2)
        if not p["construction"]:
            line([("none", None)], " ")

        heading("Operation")
        for o in p["operation"]:
            line(gutter=" ", segs=fields(o["bolt"], f"landed {local(o['at'])}" + (f" by {o['by']}" if o["by"] else ""),
                               o["team"] or "", ", ".join(o["units"])))
        envs = p.get("environments", [])
        for e in envs:
            for d in e["deploys"]:
                line(deploy_fields(e["env"], d), gutter(d["markers"]), 0, d["markers"])
            for w in e["waiting"]:
                line(waiting_fields(e["env"], w), gutter(w["markers"]), 0, w["markers"])
        if not p["operation"] and not any(e["deploys"] or e["waiting"] for e in envs):
            line([("none", None)], " ")

        heading("attention")
        for a in p["attention"]:
            line([(attention_text(a), None)], ATTENTION)
        if not p["attention"]:
            line([("none", None)], " ")
    return "\n".join(out)


def attention_text(a):
    """What needs attention, as the board says it."""
    return {"host": f"{a['name']} did not answer ({a['why']})", "plan": f"the plan, {a['name']}: {a['why']}",
            "signals": f"the signals on {a['name']}: {a['why']}", "landed": f"bolt {a['name']}: {a['why']}"}[a["what"]]


# ------------------------------------------------------------------------------------------------- the agents' views

def many(n, one, more):
    return f"{n} {one if n == 1 else more}"


def pips(units):
    """Units' stages as pips, one to a unit in the plan's order."""
    return "".join(PIP.get(u["stage"], "?") for u in units)


def merged(b):
    return f"{sum(u['stage'] in ('merged', 'landed') for u in b['units'])} of {len(b['units'])} merged"


def held(p, team):
    return [b for b in p["construction"] if b["team"] == team]


def state_said(state):
    """A held bolt's state as a line draws it: nothing while active, "waits to land" once proven (teams.16), else the
    state."""
    return "" if state == "active" else "waits to land" if state == "waits" else state


def merge_said(x):
    """A unit's, chore's or fix's merge standing in sluice's queue, as its line says it: `#<n> <state>` (plan.standing_said),
    or nothing while none stands (teams.22)."""
    return plan.standing_said(x["submission"]) if x.get("submission") else ""


def landing_said(b):
    """A held bolt's landing standing in sluice's queue on its kit's main, as its head line says it: `landing #<n>
    <state>`, or nothing while none stands (teams.22)."""
    return f"landing {plan.standing_said(b['landing'])}" if b.get("landing") else ""


def queue_said(b, why=False):
    """That a held bolt's submissions can't be read, said once on its head line, with why when asked (read.1), so no
    line of it shows a number or says it has none; nothing when they were read."""
    return (f"submissions can't be read: {b['submissions_error']}" if why else ("submissions can't be read", "dim")) if b.get("submissions_error") else ""


def bolt_row(b, team=None):
    """A held bolt on one line, led by its product, the repository it builds, and, when given, the team holding it,
    dim; then its pips, its name, its state unless active (state_said), its landing standing in sluice (landing_said),
    that its submissions can't be read when they can't (queue_said), and how many of its units have merged; its
    landing's marker in the gutter, or attention once every unit has landed."""
    return row(fields(b["repo"] or "", (team, "dim") if team else "", pips(b["units"]), b["bolt"], state_said(b["state"]),
                      landing_said(b), queue_said(b), merged(b)), gutter(b["markers"], b["state"] == "landed"), 0, b["markers"])


def ledger_rows(b):
    """A held bolt as its conductor reads it: the bolt, then a unit to a line, its pip, stage, its merge standing in
    sluice (merge_said) and slot, then each fix with its merge."""
    return ([bolt_row(b)]
            + [row(fields(PIP.get(u["stage"], "?"), u["unit"], stage_of(u), merge_said(u), u["slot"] or ""), " ", 2) for u in b["units"]]
            + [row(fields(f["fix"], "fix merged" if f["merged"] else "fix", merge_said(f), f["slot"] or ""), " ", 2) for f in b["fixes"]])


def team_rows(p):
    """Each team of the partition, product by product: the bolt it holds on one line, or its product and that it holds
    none."""
    out = []
    for t in sorted(p["teams"], key=lambda t: t["kit"]):
        out += [bolt_row(b, t["team"]) for b in held(p, t["team"])] or [row(fields(t["kit"], (t["team"], "dim"), ("holds no bolt", "dim")), " ")]
    return out


def proposal_row(d, team=None):
    """An open proposal: who made it, its case, and the conductors it waits on, to a conductor whether it waits on
    its own agreement; its marker in the gutter."""
    if team:
        waits = "waits on your agreement" if team in d["waiting"] else ""
    else:
        waits = "waiting on " + ", ".join(f"{t}-conductor" for t in d["waiting"]) if d["waiting"] else ""
    return row(fields(f"proposal {d['proposal']} by {d['by']}", d["case"] or "", waits), gutter(d["markers"]), 0, d["markers"])


def next_rows(p, team=None):
    """What comes after the work in hand, for one team or the whole partition: for each product, the repository it
    builds, its first planned bolt, the rest counted, then the queued units counted by product."""
    bp = p["bolt_plan"]
    planned = [b for b in bp["planned"] if team is None or team in b["teams"]]
    queued = [u for u in bp["queue"] if team is None or team in u["teams"]]
    out = []
    for repo in dict.fromkeys(b["repo"] for b in planned):
        mine = [b for b in planned if b["repo"] == repo]
        out.append(row(fields(repo or "", ("next", "dim"), mine[0]["bolt"], f"and {len(mine) - 1} more planned" if len(mine) > 1 else ""), " "))
    counts = {}
    for u in queued:
        counts[u["repo"] or "no repository"] = counts.get(u["repo"] or "no repository", 0) + 1
    return out + ([row(fields(("queued", "dim"), ", ".join(f"{n} in {r}" for r, n in counts.items())), " ")] if counts else [])


def attention_rows(p, keep=lambda a: True):
    return [row([(attention_text(a), None)], ATTENTION) for a in p["attention"] if keep(a)]


def conductor_view(p, team):
    """A conductor's: the bolt its team holds as a ledger, or that it holds none; the open proposals that name its
    team; what is planned and queued for it; and what needs attention there: its host not answering, a bolt of its
    still in the plan once landed, or the plan not read."""
    host = next(t["host"] for t in p["teams"] if t["team"] == team)
    mine = held(p, team)
    out = [r for b in mine for r in ledger_rows(b)] or [row(fields(f"{team} holds no bolt"), " ")]
    out += [proposal_row(d, team) for d in p["bolt_plan"]["proposals"] if team in d["teams"] or team in d["waiting"]]
    return out + next_rows(p, team) + attention_rows(p, lambda a: a["what"] in ("plan", "signals") or (a["what"] == "host" and a["name"] == host)
                                                    or (a["what"] == "landed" and a["name"] in {b["bolt"] for b in mine}))


def planner_view(p):
    """The planner's: the plan in brief, each team's bolt, the open proposals, what is planned next and queued, and
    what needs attention."""
    bp = p["bolt_plan"]
    head = row(fields((f"{p['label']} plan", "bold"), f"{len(p['construction'])} held", f"{len(bp['planned'])} planned",
                      f"{len(bp['queue'])} queued", many(len(bp["proposals"]), "proposal open", "proposals open")))
    return [head] + team_rows(p) + [proposal_row(d) for d in bp["proposals"]] + next_rows(p) + attention_rows(p)


def record_row(r):
    """A decision record proposed and not yet accepted or rejected, as the design agent reads it: the kit, dim, and the
    record's number, when it was proposed, and its card, open or none, or that the user's yes was given in the pane, so
    it has none."""
    ms = [] if r["settled"] else [{"glyph": "✓", "card": r["card"]}]
    return row(fields(named(r["kit"], f"record {r['number']}"), f"proposed {local(r['at'])}", "settled in the pane" if r["settled"] else ""),
               gutter(ms), 0, ms)


def design_view(p):
    """The design agent's: the signals no move has taken, counted by who captured them, the decision records proposed
    and not yet accepted or rejected with their cards, and the explorations on each kit's main, the first few named and
    the rest counted; and what keeps the signals or the plan from being read."""
    inc, groups, records = p["inception"], {}, p.get("records", [])
    for s in inc["signals"]:
        groups.setdefault(s["captured_by"], []).append(s)
    es = inc["explorations"]
    head = row(fields((f"{p['label']} inception", "bold"), many(len(inc["signals"]), "signal not moved", "signals not moved"),
                      many(len(records), "record proposed", "records proposed") if records else "",
                      many(len(es), "exploration", "explorations")))
    return ([head]
            + [row(fields(f"signals captured by {who or 'no one named'}", f"{len(mine)} not moved"), " ") for who, mine in groups.items()]
            + [record_row(r) for r in records]
            + [row(fields(named(e["kit"], e["name"]), e["first"] or ""), " ") for e in es[:SHOWN]]
            + ([row(fields(("and " + many(len(es) - SHOWN, "more exploration", "more explorations"), "dim")), " ")] if len(es) > SHOWN else [])
            + attention_rows(p, lambda a: a["what"] in ("plan", "signals")))


def environment_row(e):
    """An environment in brief: its latest deploy, where it stands, and how many operations wait on it; the marker of a
    deploy or an operation of it waiting on the user in the gutter."""
    ms = [m for d in e["deploys"] for m in d["markers"]] + [m for w in e["waiting"] for m in w["markers"]]
    d = e["deploys"][0] if e["deploys"] else None
    return row(fields(e["env"], f"deploy {d['to'][:7]}  {deploy_state(d)}" if d else "",
                      many(len(e["waiting"]), "operation waiting", "operations waiting") if e["waiting"] else ""), gutter(ms))


def operator_view(p):
    """An operator's: the partition's board in brief, a line to each lane with each team's bolt under Construction and
    each environment with a deploy or an operation waiting under Operation, the rail's rows waiting on the user counted,
    and what needs attention."""
    inc, bp, lands, envs = p["inception"], p["bolt_plan"], p["operation"], [e for e in p.get("environments", []) if e["deploys"] or e["waiting"]]
    approve = (sum(len(d["markers"]) for d in bp["proposals"]) + len({m["key"] for b in p["construction"] for m in b["markers"]})
               + sum(len(x["markers"]) for e in envs for x in e["deploys"] + e["waiting"]))  # a kit's landing row once, whatever it names
    last = f"the last {lands[0]['bolt']}, {plan.utc(lands[0]['at']).astimezone():%a %H:%M}" if lands else ""
    return ([row(fields((f"{p['label']} board", "bold"), f"read from {', '.join(h for h, v in p['hosts'].items() if v is True) or 'no host'}")),
             row(fields(("Inception", "bold"), many(len(inc["signals"]), "signal not moved", "signals not moved"),
                        many(len(inc["explorations"]), "exploration", "explorations"))),
             row(fields(("Bolt plan", "bold"), many(len(bp["proposals"]), "proposal open", "proposals open"), f"{len(bp['planned'])} planned",
                        f"{len(bp['queue'])} queued")),
             row([("Construction", "bold")])]
            + team_rows(p)
            + [row(fields(("Operation", "bold"), f"{len(lands)} landed in seven days", last))]
            + [environment_row(e) for e in envs]
            + ([row(fields(("waits on the user", "bold"), f"✓ {approve} to approve"))] if approve else [])
            + attention_rows(p))


def ops_view(p):
    """Main-level ops's: the partition's operations in brief; each kit's landing row, its landings card ops's, naming
    the bolts that wait on its main in the plan's order, each with its landing standing in sluice when one stands
    (landing_said), with its card, and each held bolt whose landing stands on no such row; then, environment by
    environment, each deploy
    waiting on the user's word with its card, each approved and not yet deployed, each running, and each operation step
    waiting, handed or failed, with the deploy it comes after, or whose gate it is, and its doer; and what keeps a host
    or the plan from being read."""
    pending = [(e["env"], d) for e in p.get("environments", []) for d in e["deploys"] if not d["ended"] and d["answer"] != "replaced"]
    steps = [(e["env"], w) for e in p.get("environments", []) for w in e["waiting"]]
    word = sum(d["answer"] == "waiting" for _, d in pending)
    running = sum(bool(d["started"]) for _, d in pending)
    head = row(fields((f"{p['label']} operations", "bold"), many(word, "deploy waits on the user's word", "deploys wait on the user's word"),
                      many(running, "deploy running", "deploys running"), many(len(steps), "operation waiting", "operations waiting")))
    out = [head]
    lands = {}
    for b in p.get("construction", []):
        for m in b["markers"]:
            if m["group"] == "land":
                lands.setdefault(m["key"], (m, []))[1].append(b["bolt"])
    landing = {b["bolt"]: f"{b['bolt']} {landing_said(b)}" for b in p.get("construction", []) if b.get("landing")}
    for key, (m, bolts) in lands.items():
        out.append(row(fields(key, ", ".join(landing.get(x, x) for x in bolts), "wait to land" if len(bolts) > 1 else "waits to land"),
                       gutter([m]), 0, [m]))
    rowed = {x for _, bolts in lands.values() for x in bolts}
    out += [row(fields(b["repo"] or "", b["bolt"], landing_said(b)), " ") for b in p.get("construction", [])
            if b.get("landing") and b["bolt"] not in rowed]
    for e in p.get("environments", []):
        for d in (d for env, d in pending if env == e["env"]):
            out.append(row(fields(e["env"], f"deploy {d['to'][:7]}", deploy_state(d)), gutter(d["markers"]), 0, d["markers"]))
        for w in (w for env, w in steps if env == e["env"]):
            doer = (w["doer"] or "no doer named") + (f", {w['agent']}" if w["agent"] else "") + (", held for the user's word" if w.get("held") else "")
            of = (f"gate of {w['to'][:7]}" if w["to"] else "gate") if w.get("gate") else f"after {w['to'][:7]}" if w["to"] else ""
            out.append(row(fields(e["env"], w["key"], (of, "dim") if of else "", w["state"], f"doer {doer}"),
                           gutter(w["markers"]), 0, w["markers"]))
    return out + attention_rows(p, lambda a: a["what"] in ("host", "plan"))


def card_line(c, now):
    """An open card of an agent's own, as its band shows it above its view: its question or the row's card, its key,
    its id, dim, and how long it has been open."""
    what = {"question": "your question", "record": "your record's card"}.get(c["kind"], "your card")
    return row(fields(what, c["key"] or "", (c["card"], "dim"), f"open {plan.age(when(c['at']), now)}"), " ")


def agent_views(data):
    """Each crew agent's view of its partition's board, by the agent's name, for the band crew's mod draws above its
    prompt (plugin/hooks/status.js): each team's conductor's, the planner's, the design agent's, main-level ops's and
    the partition's operator's, every line a list of (text, style) segments. With what this host's agents run of crew
    (data's `here`, here_read), each standing agent here with a recorded start has the crew it started on at the end of
    its view's first line, or as its one line when it has no view, a team's ops and a dispatcher, with the version it is
    restarted on at its next stop once an update made it due; and while this host is held every view opens with the
    hold (teams.19). Any other agent has no view, and its mod draws nothing.
    Beside them, cards: each of those agents' open cards, oldest first, its questions among them, by the agent's name,
    the lines the mod draws above its view. With them, the line the mod draws in place of the view and the cards once
    the frame is stale_after_ms old, so a band names no bolt that has landed since, nor a card closed since (read.1):
    the day and time it was read, since a frame a restart or a follower that stopped left can be days old, and that the
    host's follower has not refreshed it since.

    A change to what crew models (bolts, units, stages, proposals, explorations and elaborations, cards, rail rows)
    changes these views and plugin/hooks/status.js with it, each with its cases (code.8)."""
    views, cards, now = {}, {}, plan.utc(data["read_at"])
    for p in data["partitions"]:
        views.update({f"{t['team']}-conductor": conductor_view(p, t["team"]) for t in p["teams"]})
        views.update({f"{p['label']}-planner": planner_view(p), f"{p['label']}-design": design_view(p), f"{p['label']}-ops": ops_view(p)})
        views[f"{p['label']}-operator"] = operator_view(p)
        for c in p.get("cards", []):
            cards.setdefault(c["by"], []).append(card_line(c, now))
    here = data.get("here")
    if here:
        for name, f in here["agents"].items():
            said = [(crew_said(f, here["version"]), "dim")]
            views[name] = [views[name][0] + [("  ", None)] + said] + views[name][1:] if views.get(name) else [row(said)]
        if here["held"]:
            views = {name: [held_row(here["host"], here["held"])] + v for name, v in views.items()}
    return {"read_at": data["read_at"], "stale_after_ms": STALE * 1000,
            "stale": row([(f"crew: the board was last read at {local(data['read_at'])}, too long ago to show; crew's follower on "
                           f"{data['from']} has not refreshed it since", "dim")]),
            "views": views, "cards": {a: lines for a, lines in cards.items() if a in views}}


def crew_said(f, now):
    """The crew an agent runs, as its band says it (teams.19): the version it started on, or that it started on a crew
    older than crew's versions in its bands; and once an update made it due a restart, the version it is restarted on
    at its next stop."""
    was = f"crew {f['version']}" if f["version"] else "an older crew"
    return f"{was} \u2192 {now or 'crew as it now is'} at its next stop" if f["due"] else was


def held_row(host, h):
    """The line every band on a held host opens with (teams.19): who held it, since when, and why."""
    since = f" since {h['at']}" if h.get("at") else ""
    return row([(f"{host} is held", "bold"), (f" by {h['by']}{since}: {h['why']}. Start nothing new; crew go {host} lifts it", None)])


def here_read(fleet, label):
    """What this host's agents of a partition run of crew, for their bands (agent_views): this host, its crew's
    version, its hold, and each standing agent of the partition here with a recorded start, by name: the version it
    started on, and whether an update has made it due a restart (crew.due_of)."""
    commit, version = crew.crew_version()
    started, agents = crew.starts(), {}
    for name in crew.agents_here(fleet, label):
        if name in started:
            due, _, _ = crew.due_of(fleet, name, started[name], commit)
            agents[name] = {"version": started[name]["version"], "due": due}
    return {"host": crew.this_host(), "version": version, "held": crew.held(), "agents": agents}

# ------------------------------------------------------------------------------------------------- the board tab

def frame_path(label):
    return FRAMES / f"{label}.json"


def agents_path(label):
    """The agents' views beside the board's frame, which crew's mod reads (plugin/hooks/status.js)."""
    return FRAMES / f"{label}.agents.json"


def write_frame(label, data, path=None):
    """The board's data for the board tab, or the agents' views for their mods at path, written whole: a temporary
    file in the same folder, then moved over the last one, so no reader ever reads half of one."""
    FRAMES.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=FRAMES, prefix=f".{label}.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(data, indent=1) + "\n")
        os.replace(tmp, path or frame_path(label))
    except OSError:
        os.unlink(tmp)
        raise


def no_frame(label):
    return (f"No board for {label} yet: the host's follower writes it each time it refreshes, swancloud's job or the console's "
            f"rail tab, which crew console up {label} opens while no job runs.")


def frame_text(label, data, width, color, now):
    if data is None:
        return no_frame(label)
    read_at = plan.utc(data["read_at"])
    stale = plan.age(read_at, now) if (now - read_at).total_seconds() > STALE else None
    return board_text(data, width, color, stale)


def read_frame(label):
    try:
        data = json.loads(frame_path(label).read_text())
        return data if isinstance(data, dict) and plan.utc(data.get("read_at")) and isinstance(data.get("partitions"), list) else None
    except (OSError, ValueError, AttributeError):
        return None


def follow(label, once=False):
    """The board tab: the latest frame drawn at the pane's width, again whenever the frame, the pane's size or how
    stale the frame is changes; checked once a second."""
    tty = sys.stdout.isatty()
    color = tty and not os.environ.get("NO_COLOR")
    seen, data, mtime = None, None, False
    while True:
        try:
            m = frame_path(label).stat().st_mtime_ns
        except OSError:
            m = None
        if m != mtime:
            mtime, data = m, read_frame(label) if m is not None else None
        now = datetime.datetime.now(datetime.timezone.utc)
        width = shutil.get_terminal_size().columns if tty else None
        text = frame_text(label, data, width, color, now)
        if (text, width) != seen:
            seen = (text, width)
            sys.stdout.write(("\033[H\033[2J" if tty else "") + text + "\n")
            sys.stdout.flush()
        if once:
            return
        time.sleep(1)


# ------------------------------------------------------------------------------------------------- the host's follower

def lock_path():
    """The host's follower lock, beside the frames the follower writes."""
    return FRAMES / "follower.lock"


def lock_follower(kind, label=None, wait=True):
    """The host's follower lock taken for a follower of kind job (crew _follow) or tab (a rail tab, of label): an OS lock
    on the open file, which the caller keeps open for as long as it follows, so the OS lifts it when the follower ends,
    however it ends, and nothing is left to go stale (state.4). Once taken, the file says who holds it, `job <pid>
    <time>` or `tab <label> <pid> <time>`. With wait it waits for the lock, reading nothing meanwhile; without, None
    when another holds it. A follower started again as crew moved (Follower.again) adopts the lock it held, its open
    file handed on across the exec, so the host is never without its follower between the two."""
    held = os.environ.pop("CREW_FOLLOWER_LOCK", None)
    if held:
        try:
            return os.fdopen(int(held), "a+")
        except (OSError, ValueError):
            pass
    FRAMES.mkdir(parents=True, exist_ok=True)
    f = open(lock_path(), "a+")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | (0 if wait else fcntl.LOCK_NB))
    except BlockingIOError:
        f.close()
        return None
    f.truncate(0)
    f.write(" ".join([kind] + ([label] if kind == "tab" else []) + [str(os.getpid()), iso(datetime.datetime.now(datetime.timezone.utc))]) + "\n")
    f.flush()
    return f


def follower_of(line, free):
    """Who follows on the host, from the lock's line and whether the lock was free: none when it was free, job or tab
    as the line says, and unknown when the line is neither, as one read between a holder's lock and its write would be
    (read.1)."""
    if free:
        return "none"
    words = (line or "").split()
    if words[:1] == ["job"] and len(words) == 3:
        return "job"
    if words[:1] == ["tab"] and len(words) == 4 and re.fullmatch(r"[a-z0-9][a-z0-9-]*", words[1]):
        return "tab"
    return "unknown"


def follower_here():
    """Who follows on this host (follower_of): the lock tried without waiting, and released at once when it was free;
    when it is held, the holder's line read."""
    FRAMES.mkdir(parents=True, exist_ok=True)
    with open(lock_path(), "a+") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            f.seek(0)
            return follower_of(f.readline(), False)
        fcntl.flock(f, fcntl.LOCK_UN)
        return follower_of(None, True)


def labels_here(fleet, host):
    """The partitions with an operator session on the host, which its follower refreshes: each label whose session of
    that name there is in its partition, as crew.operator_session reads it, in the teams file's order."""
    sessions = fleet["hosts"].get(host, {}).get("sessions", {})
    return [l for l, p in fleet["partitions"].items() if (sessions.get(l) or {}).get("partition") == p["partition"]]


def rail_path(label):
    """The rail's frame beside the board's: the rail as the follower's last round printed it, which the rail tab draws."""
    return FRAMES / f"{label}.rail.json"


def read_rail(label):
    try:
        data = json.loads(rail_path(label).read_text())
        return data if isinstance(data, dict) and plan.utc(data.get("read_at")) and isinstance(data.get("text"), str) else None
    except (OSError, ValueError, AttributeError):
        return None


def rail_frame_text(label, data, now):
    """The rail tab's text: the rail as the follower's last round printed it, with what handing out the due restarts
    said when that round did; headed with its age once it is older than STALE; and, when there is none, that the host's
    follower writes it."""
    if data is None:
        return (f"No rail for {label} yet: the host's follower writes it each time it refreshes, swancloud's job or the "
                f"console's rail tab, which crew console up {label} opens while no job runs.")
    read_at = plan.utc(data["read_at"])
    head = (f"{label}'s rail as read at {read_at.astimezone():%Y-%m-%d %H:%M:%S}, {plan.age(read_at, now)} ago: the host's follower"
            f"{' on ' + data['from'] if data.get('from') else ''} has not refreshed it since\n\n") if (now - read_at).total_seconds() > STALE else ""
    return head + data["text"] + (f"\n\n{data['updated']}" if data.get("updated") else "")


def moved(kept, now):
    """What moved between the stamps the follower's last read was made at (kept) and the stamps now (now), each
    {"crew": (crew's head, the teams file's bytes), "state": {label: tip}, "blueprints": {label: tip}, "kits": {(host,
    main): stamp}, "readings": {host: stamp}, "cards": cards_stamp's, "queues": {(host, main): queue_stamp's}}, a tip ""
    for a branch the cache does not hold: whether crew's checkout or the teams file moved, the labels whose state and
    whose blueprints tip moved, the kits that moved, the hosts whose card readings folders moved, whether the cards
    moved, the kits whose queue moved, whether anything the read rests on moved (read: a tip, a kit or crew), and
    whether anything did. A stamp None, which could not be read, counts as moved, as does one either side lacks
    (read.1); with no kept read, everything has moved. A decision on plain facts (code.7)."""
    if kept is None:
        return {"crew": True, "state": set(now["state"]), "blueprints": set(now["blueprints"]), "kits": set(now["kits"]),
                "readings": set(now.get("readings", {})), "cards": True, "queues": set(now.get("queues", {})), "read": True, "any": True}

    def apart(a, b):
        return {k for k in a.keys() | b.keys() if a.get(k) is None or b.get(k) is None or a[k] != b[k]}
    out = {"crew": None in kept["crew"] or None in now["crew"] or tuple(kept["crew"]) != tuple(now["crew"]),
           "state": apart(kept["state"], now["state"]), "blueprints": apart(kept["blueprints"], now["blueprints"]),
           "kits": apart(kept["kits"], now["kits"]), "readings": apart(kept.get("readings", {}), now.get("readings", {})),
           "cards": kept.get("cards") != now.get("cards"), "queues": apart(kept.get("queues", {}), now.get("queues", {}))}
    read = bool(out["crew"] or out["state"] or out["blueprints"] or out["kits"])
    return dict(out, read=read, any=read or bool(out["readings"]) or out["cards"] or bool(out["queues"]))


def cards_stamp(found, why, left, tick, listed=None):
    """What the follower's check compares of the cards (Decisions 3 and 8 of a-rail-refresh-after-no-change-reads-nothing):
    of each card Pending You was asked after at the clock's tick (plan.cards_fetched, found {card: (got, words)}),
    whether it answered it lost, the fact the card sweep acts on, [[card, lost]], and of each asker herdr was asked
    about on that tick (plan.askers_listed, listed {name: (listed, why)}), whether its pane holds an agent, [["asker",
    name, listed]]; but the tick itself, ["again", tick], when the tick's bridge failed (why) or the last card sweep
    left a card, its act not gone through (left), so the cards count as moved at each tick until the sweep acts, and
    only at a tick, never at each refresh. A decision on plain facts (code.7)."""
    if why is not None or left:
        return ["again", tick]
    return sorted([card, plan.cards.lost(words)] for card, (_, words) in found.items()) + sorted(
        ["asker", name, here] for name, (here, _) in (listed or {}).items())


def card_left(swept):
    """Whether a card sweep (plan.sweep_cards) left a card or a partition unswept, its act not gone through: what the
    clock's next tick tries again (cards_stamp)."""
    return bool(swept) and (any(d["did"] == "left" for d in swept["done"]) or bool(swept["unswept"]))


def queue_key(doc):
    """What of an overview's document the follower compares: all of it but its time (at), as text; None for none."""
    return json.dumps({k: v for k, v in doc.items() if k != "at"}, sort_keys=True) if isinstance(doc, dict) else None


def queue_moved(kept, doc):
    """Whether a line an overview watch printed, its document (doc), moves the kit's queue from the one kept: a document
    that differs from it but for its time, as sluice prints the document again at each change (sluice ADR 0023). A
    decision on plain facts (code.7)."""
    return queue_key(kept) != queue_key(doc)


def queue_stamp(state):
    """What the follower's check compares of a kit's queue (Decision 7 of a-rail-refresh-after-no-change-reads-nothing):
    the document its watch or the clock's ask last read, its time aside, or why it can't be read."""
    return ["read", queue_key(state["doc"])] if "doc" in state else ["unread", state["why"]]


def queue_of(state):
    """A kit's queue as its rows carry it, (submissions, why), from what its watch or the clock's ask last read: the
    document's standing submissions (gather.submissions_of), or none and why it can't be read (read.1)."""
    return gather.submissions_of(state["doc"]) if "doc" in state else (None, state["why"])


def queue_kits(kits):
    """The kits whose queue the follower's read shows, by (host, main): each the read asked bolts of and read (gather.kit
    reads sluice's queue for those alone), of the kept answers, {host: {main: (request, answer)}}."""
    return {(host, m) for host, ks in kits.items() for m, (req, answer) in ks.items() if req.get("bolts") and (answer or {}).get("ok")}


def watch_plan(kits, watching, refused, ended, tick):
    """The follower's overview watches at a refresh (Decision 7 of a-rail-refresh-after-no-change-reads-nothing), from the
    kits whose queue its read shows (kits), those with a watch running (watching), the hosts whose sluice refused
    --watch (refused), the kits whose watch ended or could not start (ended), and whether its clock ticks: a watch
    opened for each kit shown with none, but on a refused host and, between ticks, one whose watch ended; one closed for
    each kit no longer shown; and, at a tick alone, the overview asked once of each kit no watch follows, on a refused
    host or whose watch ended, which the tick opens again. {open, close, ask}, each sorted. A decision on plain facts
    (code.7)."""
    kits, watching = set(kits), set(watching)
    return {"open": sorted(k for k in kits - watching if k[0] not in refused and (tick or k not in ended)),
            "close": sorted(watching - kits),
            "ask": sorted(k for k in kits if k[0] in refused or k in ended) if tick else []}


def watch_refused(code, said):
    """Whether an overview watch's end says its host's sluice has no --watch (clap's refusal of an argument it does
    not know, exit 2), so the follower asks that host's overviews on its clock for the rest of its life."""
    return code == 2 and "--watch" in said


def routes_moved(kits, asked):
    """The hosts whose portless routes the clock's tick read (asked, {host: routes}) differ from those a kit answer of the
    kept read holds there (kits, {host: {main: (request, answer)}}): their routes are drawn again with nothing
    gathered (Decision 8 of a-rail-refresh-after-no-change-reads-nothing). A decision on plain facts (code.7)."""
    return {h for h, r in asked.items() if any(a.get("routes") != r for _, a in kits.get(h, {}).values() if (a or {}).get("ok"))}


def moved_at():
    """What says crew's code or the teams file has moved since a refresh: the checkout's commit, read from its files
    (crew.head_here), and the teams file's bytes, each None when it can't be read."""
    try:
        teams = crew.TEAMS.read_bytes()
    except OSError:
        teams = None
    return (crew.head_here(), teams)


PERIOD = record.PERIOD  # seconds: the follower's clock, on which it fetches the state and blueprints caches (plan.12)
BURST = 2  # seconds: a look that sees a write waits this long for what follows, so a burst of writes is one refresh


def look(fleet, labels):
    """What the follower's look reads each second, with no process (plan.12): crew's checkout and the teams file
    (moved_at), each partition's state and blueprints tips as this host's caches hold them (plan.tip_here), and this
    host's card readings folders (gather.readings_stamp), so a reading sent back here is swept within seconds."""
    return {"crew": moved_at(), "state": {l: plan.tip_here(*plan.state_of(fleet, l)) for l in labels},
            "blueprints": {l: plan.tip_here(crew.partition_of(fleet, l)["blueprints"][0], "main") for l in labels},
            "readings here": gather.readings_stamp(readings_hosts(fleet, labels).get(crew.this_host(), []))}


def wake(now, tick_at, seen, looked):
    """What the follower does at a look (Decision 3 of a-rail-refresh-after-no-change-reads-nothing): "tick" once its
    clock's tick is due, when it fetches and then refreshes; "refresh" when what the look reads now (looked) is not what
    its last refresh rested on (seen), a write on this host having moved a cache, crew or the teams file; else None,
    and it reads nothing. A decision on plain times and tips (code.7)."""
    if now >= tick_at:
        return "tick"
    return "refresh" if looked != seen else None


def refresh_plan(m, kept, crew_read=True):
    """What a refresh does, from what moved since its last read (moved), whether it kept one, and whether crew's checkout
    and the teams file could be read then and now (crew_read): "read" with none kept, its first, or when a tip or a kit
    moved, reading only what moved and running every sweep; "update" once crew's checkout or the teams file moved, the
    due restarts handed out and the follower started again as the new crew, but a read when either can't be read, which
    hands out nothing on a guess (read.1); "sweep" when only a host's card readings folder, the cards, a kit's queue or a
    host's routes moved, reading nothing, taking the queue or the routes into the kept read and running against it only
    the sweeps of what moved (sweeps_after); "render" when nothing
    moved, the frames written again from the kept read and the card sessions swept only on the hosts the last refresh
    could not check (plan.sessions_unchecked). A decision on plain facts (code.7)."""
    if not kept:
        return "read"
    if m["crew"]:
        return "update" if crew_read else "read"
    if m["read"]:
        return "read"
    return "sweep" if m["any"] else "render"


def sweeps_after(m, readings, unchecked):
    """The sweeps a refresh that reads nothing runs against its kept read (Decision 5 of
    a-rail-refresh-after-no-change-reads-nothing): the card sweep when the cards moved, with the clock's last answers;
    and the card session sweep on each host whose card readings folder moved, for each partition swept there
    (readings, {host: labels}), which is where a reading sent back is told to its owner, and on each host the last
    refresh could not check (unchecked, plan.sessions_unchecked), {label: hosts}; none other. A decision on plain facts
    (code.7)."""
    only = plan.sessions_unchecked(unchecked)
    for h in m["readings"]:
        for l in readings.get(h, ()):
            only.setdefault(l, set()).add(h)
    return {"cards": bool(m["cards"]), "sessions": only}


def readings_hosts(fleet, labels):
    """The hosts whose card readings folders the follower stamps, with the partitions of each, {host: [labels]}: each
    partition's main machine and every host its teams run on, where its card sessions are swept (plan.sweep_sessions)."""
    out = {}
    for l in labels:
        for h in sorted({crew.partition_of(fleet, l)["machine"], *crew.partition_hosts(fleet, l)}):
            out.setdefault(h, []).append(l)
    return out


def stamps_now(fleet, kits, readings, overviews=None, routes=False):
    """The follower's check of the hosts (plan.stamped): each kit's stamp now (gather.stamp), of the kits the last read
    surveyed, {host: {main: (request, answer)}}, by (host, main), and each host's card readings folders' stamp
    (gather.readings_stamp), of the partitions readings names for it, by host: in this process on this host, in one ssh
    to each other. Every stamp of a host that did not answer is None, which moved() takes as moved (read.1). At the
    clock's tick, in the same request: each kit overviews names, {host: [main]}, its overview read once, by (host,
    main), {"doc": document} or {"why": why}, a host that did not answer saying so; and with routes, the portless
    routes of each host whose kits were surveyed, by host, one that did not answer left out."""
    out, overviews = {"kits": {}, "readings": {}, "overviews": {}, "routes": {}}, overviews or {}
    for host in sorted(set(kits) | set(readings) | set(overviews)):
        ks = kits.get(host, {})
        got, why = plan.stamped(fleet, host, [req for req, _ in ks.values()], readings.get(host, ()), overviews.get(host, ()),
                                routes and bool(ks))
        out["kits"].update({(host, m): ((got or {}).get("kits") or {}).get(m) for m in ks})
        if host in readings:
            out["readings"][host] = (got or {}).get("readings")
        for m in overviews.get(host, ()):
            doc, said = ((got or {}).get("overviews") or {}).get(m) or (None, f"{host} did not answer ({why})" if why else "it was not read")
            out["overviews"][(host, m)] = {"why": said} if said else {"doc": doc}
        if got is not None and "routes" in got:
            out["routes"][host] = got["routes"]
    return out


def kept_stamps(kits):
    """The stamp each kit the last read used was read at, by (host, main), None for one whose host did not answer."""
    return {(host, m): (answer or {}).get("stamp") for host, ks in kits.items() for m, (_, answer) in ks.items()}


def here_key(head):
    """What here_read rests on besides the partition: crew's checkout and the teams file (moved_at), and the size and
    time of each agent's start record and of the host's hold file, read with no process; here_read is read again only
    when it moves."""
    try:
        starts = sorted((e.name, e.stat().st_size, e.stat().st_mtime_ns) for e in os.scandir(crew.SESSIONS))
    except FileNotFoundError:
        starts = []
    try:
        st = crew.HOLD.stat()
        hold = (st.st_size, st.st_mtime_ns)
    except FileNotFoundError:
        hold = None
    return json.dumps([head[0], head[1].decode(errors="replace") if head[1] else None, starts, hold])


def label_errors(errors, label):
    """The plans' errors of one partition's read: its branch's, named <label>/main of <repo>, or its plan's."""
    return {k: v for k, v in errors.items() if k.startswith(f"{label}/main of ") or k == f"the plan of {label}"}


class Watches:
    """The follower's overview watches (Decision 7 of a-rail-refresh-after-no-change-reads-nothing): one `sluice overview
    --json --watch` for each kit whose queue its read shows, in the kit's main checkout, a child on this host and one ssh
    to another (code.3), each read at the follower's look without blocking; and what last read each kit's queue, its
    watch's last line or the clock's ask, {"doc": document} or {"why": why it can't be read}. sluice prints the document
    at once and again at each change but its time, so a running watch costs nothing until the queue moves. crew reads no
    folder of sluice's: this is how it learns the queue moved."""

    WATCH = ["sluice", "overview", "--json", "--watch"]

    def __init__(self):
        self.running, self.states, self.ended, self.refused = {}, {}, set(), set()

    def sync(self, fleet, kits, tick):
        """The watches made to match the kits whose queue the read shows (watch_plan): the kits no longer shown let go,
        and those to ask the overview of once now, at a tick, returned by host."""
        p = watch_plan(kits, self.running, self.refused, self.ended, tick)
        for key in p["close"]:
            self.close(key)
        for key in set(self.states) - set(kits):
            del self.states[key]
        self.ended &= set(kits)
        for host, main in p["open"]:
            self.open(fleet, host, main)
        asks = {}
        for host, main in p["ask"]:
            asks.setdefault(host, []).append(main)
        return asks

    def open(self, fleet, host, main):
        self.ended.discard((host, main))
        here = host == crew.this_host()
        argv = self.WATCH if here else ["ssh", "-o", "BatchMode=yes", fleet["hosts"][host]["ssh"], f"cd {shlex.quote(main)} && exec {shlex.join(self.WATCH)}"]
        try:
            proc = subprocess.Popen(argv, cwd=main if here else None, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as e:
            self.end((host, main), f"sluice overview --watch could not start on {host}: {e.strerror or e}")
            return
        for pipe in (proc.stdout, proc.stderr):
            os.set_blocking(pipe.fileno(), False)
        self.running[(host, main)] = {"proc": proc, "out": b"", "err": b""}

    def poll(self):
        """What each watch printed since the last look, read without blocking: its last whole line taken as the kit's
        queue, and a watch whose output ended taken as ended, its queue unread with why until the next tick."""
        for key, w in list(self.running.items()):
            done = False
            for name in ("out", "err"):
                pipe = getattr(w["proc"], "std" + name)
                while True:
                    try:
                        chunk = os.read(pipe.fileno(), 65536)
                    except BlockingIOError:
                        break
                    if not chunk:
                        done = done or name == "out"
                        break
                    w[name] = (w[name] + chunk)[-65536:] if name == "err" else w[name] + chunk
            *lines, w["out"] = w["out"].split(b"\n")
            line = next((l for l in reversed(lines) if l.strip()), None)
            if line is not None:
                try:
                    doc = json.loads(line)
                except ValueError:
                    doc = None
                self.states[key] = {"doc": doc} if isinstance(doc, dict) else {"why": "sluice overview --watch printed a line that is no JSON document"}
            if done:
                code = w["proc"].wait()
                said = gather.sluice_said("sluice overview --watch", code, "", w["err"].decode(errors="replace"))
                if watch_refused(code, said):
                    self.refused.add(key[0])
                del self.running[key]
                self.end(key, f"{said}, on {key[0]}" if key[0] != crew.this_host() else said)

    def end(self, key, why):
        self.ended.add(key)
        self.states[key] = {"why": f"its overview watch ended ({why}), and is opened again at the follower's next tick"}

    def seed(self, kits):
        """Each watched kit nothing has read the queue of yet takes the overview its gather read (gather.kit's
        overview), so the watch's first line, the same but for its time, moves nothing: a kit's queue is read once.
        Whether any did."""
        new = {key: {"doc": answer["overview"]} for host, ks in kits.items() for m, (_, answer) in ks.items()
               if (key := (host, m)) in self.running and key not in self.states and isinstance((answer or {}).get("overview"), dict)}
        self.states.update(new)
        return bool(new)

    def took(self, asked):
        """The overviews the clock's tick asked (stamps_now), each the kit's queue now."""
        self.states.update(asked)

    def stamp(self):
        return {key: queue_stamp(s) for key, s in self.states.items()}

    def close(self, key):
        w = self.running.pop(key, None)
        if w:
            w["proc"].terminate()
            try:
                w["proc"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                w["proc"].kill()
                w["proc"].wait()

    def close_all(self):
        for key in list(self.running):
            self.close(key)


class Follower:
    """The host's follower once it holds the lock (lock_follower): on its clock, every PERIOD seconds, it fetches each
    partition's state branch and blueprints main and refreshes; between ticks it looks each second at what this host's
    caches hold, crew's checkout, the teams file and this host's card readings folders, with no process, and refreshes
    within seconds when one moved. A refresh is one read, in this process, for every partition with an operator
    session on the host (labels_here), kept between refreshes (plan.Kept, state.4): it checks first whether anything
    the refresh acts on moved (moved) and then reads nothing when nothing did, or only what moved, running only the
    sweeps of what moved when no tip or kit did (sweeps_after); each partition's rail, board and agents' views are
    written from it. On each tick, and only then, it asks Pending You after the cards its card sweep would act on, in one
    bridge, none when there are none, and every sweep judges with those answers until the next tick. It follows each
    kit's queue through sluice's overview watch (Watches), with watch, and a new line is the queue's move, taken into
    the kept read with nothing gathered; a kit no watch follows has its overview asked once at each tick. SIGUSR1 makes
    the next tick now."""

    def __init__(self, lock, period=PERIOD, watch=True):
        self.lock, self.period, self.kept, self.last = lock, period, plan.Kept(), None
        self.labels, self.fleet_, self.tick_at, self.seen, self.unfetched, self.here = [], None, 0.0, None, {}, {}
        # the overview watches, None for a follower that keeps none (crew _follow --once), whose gathers read the queues
        self.watches = Watches() if watch else None
        # the partitions a refresh found a batch due for, by the state tip its read held and whether the tell went
        # through (plan.batch_told)
        self.told = {}
        # the clock's ticks, whether the last card sweep left a card, and the cards' stamp (cards_stamp) as of the last tick
        self.ticks, self.left, self.cards = 0, False, None
        # what handing out the restarts said before the follower started again as the new crew (again)
        self.updated = json.loads(os.environ.pop("CREW_FOLLOWER_UPDATED", "") or "{}")

    def fleet(self):
        """The teams file and the hosts file read afresh, not as this process first read them, and the partitions
        followed with them."""
        crew.load.cache_clear()
        try:
            self.fleet_ = crew.load()
            self.labels = labels_here(self.fleet_, crew.this_host())
        except Refusal as e:
            print(f"crew's follower keeps the partitions it had ({', '.join(self.labels) or 'none'}): {e}", file=sys.stderr)
        return self.fleet_

    def tick_now(self):
        self.tick_at = 0.0

    def fetch(self, fleet):
        """The clock's fetch: each partition's state branch and blueprints main, once each, into this host's caches;
        what could not be fetched is said in each partition's frames until a fetch of it lands."""
        self.unfetched, done = {}, {}
        for l in self.labels:
            for repo, ref in (plan.state_of(fleet, l), (crew.partition_of(fleet, l)["blueprints"][0], "main")):
                if (repo, ref) not in done:
                    try:
                        plan.fetch(repo, ref, fresh=True)
                        done[(repo, ref)] = None
                    except Refusal as e:
                        done[(repo, ref)] = " ".join(str(e).split())
                if done[(repo, ref)]:
                    self.unfetched.setdefault(l, {})[f"{ref} of {repo}"] = done[(repo, ref)]

    def ask(self, fleet):
        """The clock's ask of Pending You after the cards the kept read's card sweep would act on (plan.cards_asked), in
        one bridge and none when it names none (plan.cards_fetched), and of herdr after the panes of the questions'
        askers (plan.askers_listed); the answers kept for every card sweep until the next tick, and the cards' stamp
        taken from them. With no read kept, the tick's read asks itself (plan.rail_read)."""
        self.ticks += 1
        read = (self.last or {}).get("read")
        if read is None:
            self.kept.cards = self.kept.listed = None
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        found, why = plan.cards_fetched(fleet, plan.cards_asked(fleet, read, crew.this_host(), now))
        self.kept.cards, self.kept.listed = (found, why), plan.askers_listed(fleet, plan.askers_asked(fleet, read, crew.this_host(), now))
        self.cards = cards_stamp(found, why, self.left, self.ticks, self.kept.listed)

    def tick(self):
        """The clock's tick: the caches fetched, the cards asked after, and a refresh, which asks the overviews no watch
        follows; a tick whose read asked nothing, failing before its sweep, leaves the sweeps until the next with no
        answer to judge by, rather than ask between."""
        fleet = self.fleet()
        self.fetch(fleet)
        self.ask(fleet)
        self.refresh(tick=True)
        if self.kept.cards is None:
            self.kept.cards = ({}, None)

    def once(self):
        """One tick, waiting for nothing: crew _follow --once, for the tiers."""
        self.tick()

    def look(self, fleet):
        """What the look reads (look), with each kit's queue as its watch last read it, read now without blocking."""
        if self.watches is None:
            return look(fleet, self.labels)
        self.watches.poll()
        return dict(look(fleet, self.labels), queues=self.watches.stamp())

    def step(self, most=None):
        """A look: the clock's tick when it is due, a refresh when a cache, crew, the teams file or a kit's queue moved,
        else nothing; then a wait of a second, or of most seconds when that is less."""
        how = wake(time.monotonic(), self.tick_at, self.seen, self.look(self.fleet_) if self.fleet_ else None)
        if how == "tick":
            self.tick_at = time.monotonic() + self.period
            self.tick()
        elif how == "refresh":
            time.sleep(BURST)
            self.refresh()
        time.sleep(1 if most is None else min(1, most))

    def refresh(self, tick=False):
        fleet = self.fleet()
        kept = self.last if self.last and self.last["read"] is not None else None
        kits = self.kept.kits if kept else {}
        asks = self.watches.sync(fleet, queue_kits(kits), tick) if self.watches is not None else {}
        now = stamps_now(fleet, kits, readings_hosts(fleet, self.labels), asks, routes=tick)
        if self.watches is not None:
            self.watches.took(now["overviews"])
        looked = self.look(fleet)
        stamps = dict(looked, kits=now["kits"], readings=now["readings"], cards=self.cards)
        self.seen = looked
        m = moved(kept and kept["stamps"], stamps)
        routes = routes_moved(kits, now["routes"])  # read on the clock's tick alone (Decision 8)
        m = dict(m, routes=routes, any=m["any"] or bool(routes))
        how = refresh_plan(m, kept is not None, None not in looked["crew"] and None not in (kept["stamps"]["crew"] if kept else ()))
        if how == "update":
            self.again(fleet)
            how = "read"
        if how == "read":
            self.read(fleet, looked, stamps)
        else:
            self.render(fleet, m, stamps, tick)
        if self.last["read"] is not None:
            self.reroute(routes, now["routes"])
        if self.watches is not None and self.last["read"] is not None:
            self.requeue(m.get("queues", ()))
            self.watches.sync(fleet, queue_kits(self.kept.kits), tick=False)
            if self.watches.seed(self.kept.kits):  # the overviews the read's gathers made, each new watch's first line
                self.last["stamps"] = dict(self.last["stamps"], queues=self.watches.stamp())
                self.seen = dict(self.seen, queues=self.watches.stamp())
        self.write(fleet)

    def reroute(self, hosts, routes):
        """Each host whose portless routes the tick read moved has them in every kit answer kept of it, the board's dev
        servers drawn from them with nothing gathered (Decision 8)."""
        for host in hosts:
            for _, answer in self.kept.kits.get(host, {}).values():
                if (answer or {}).get("ok"):
                    answer["routes"] = routes[host]

    def requeue(self, moved_):
        """Each kit whose queue moved has its kept answer's submissions remade from what its watch or the clock's ask
        last read (queue_of), the read's rows and frames drawn from it with nothing gathered (Decision 7)."""
        for host, main in moved_:
            state, (_, answer) = self.watches.states.get((host, main)), self.kept.kits.get(host, {}).get(main, (None, None))
            if state is None or not (answer or {}).get("ok"):
                continue
            answer["submissions"], why = queue_of(state)
            answer.pop("submissions_error", None)
            if why:
                answer["submissions_error"] = why

    def read(self, fleet, looked, stamps):
        """A read of what moved: the tips this host's caches hold handed in (no fetch), each unmoved kit served from what
        was kept, and every sweep run; what the read said on standard error kept for the rail's frames."""
        plan.READ.memory.clear()
        for l in self.labels:
            for (repo, ref), tip in ((plan.state_of(fleet, l), looked["state"][l]),
                                     ((crew.partition_of(fleet, l)["blueprints"][0], "main"), looked["blueprints"][l])):
                if tip is not None:
                    plan.READ.keep_tip(repo, ref, tip)
        self.kept.stamps, plan.READ.follower, said, asked = stamps["kits"], self.kept, io.StringIO(), self.kept.cards is None
        self.kept.queued = {k: list(queue_of(s)) for k, s in (self.watches.states if self.watches is not None else {}).items() if "doc" in s}
        try:
            with contextlib.redirect_stderr(said):
                read = flow_read(fleet, self.labels, sweep=True)
        except Exception as e:  # a read that fails is said in the frames, and the follower goes on
            print(f"crew's follower could not read: {e}" if isinstance(e, Refusal) else
                  f"crew's follower could not read: {type(e).__name__}: {e}", file=said)
            read = None
        finally:
            plan.READ.follower = None
            self.kept.settle()
        if asked and self.kept.cards is not None:  # the read's sweep made the tick's ask
            self.cards = cards_stamp(*self.kept.cards, False, self.ticks, self.kept.listed)
        if read is not None:
            self.left = card_left(read.get("swept"))
            self.told = {l: (tip, read["told"][l]) for l, _, tip, _ in read["found"] if l in (read.get("told") or {})}
            self.last = {"read": read, "stamps": dict(looked, kits=kept_stamps(self.kept.kits), readings=stamps["readings"], cards=self.cards),
                         "said": said.getvalue().strip()}
        else:
            self.last = {"read": None, "stamps": None, "said": said.getvalue().strip()}

    def render(self, fleet, m, stamps, tick=False):
        """Nothing the read rests on moved: the kept read stands, its sweeps' acts are not said again, and only the sweeps
        of what moved run against it (sweeps_after, the card-sessions spec): the card sweep with the clock's last answers
        when the cards moved, and the card sessions swept on each host whose readings folder moved and each the last
        refresh could not check; what they did is said, and the stamps they rest on kept. Whatever moved, a batch due by
        the hours is reckoned from the kept read and the time now, reading nothing (plan.reckon_batches), and a partition
        told at its read's tip is not told again, nor one whose tell did not go through before the clock's next tick
        (plan.batch_told)."""
        read = self.last["read"]
        todo = sweeps_after(m, readings_hosts(fleet, self.labels), read.get("unchecked"))
        swept = {"done": [], "unswept": []}
        if todo["cards"]:
            swept = plan.sweep_cards(fleet, read, answers=self.kept.cards, listed=self.kept.listed)
            read = dict(read, cards=plan.swept_cards(read["cards"], swept, crew.this_host(), datetime.datetime.now(datetime.timezone.utc),
                                                     {l: plan.partition_kits(fleet, l) for l, *_ in read["found"]}))
            self.left = card_left(swept)
        ended, unchecked = plan.sweep_sessions(fleet, read["found"], read["sv"], read["rows"], read["cards"], read["unread"],
                                               read.get("batched") or {}, todo["sessions"]) if todo["sessions"] else ([], [])
        said = io.StringIO()
        with contextlib.redirect_stderr(said):
            told = plan.reckon_batches(fleet, read["found"], read, plan.batch_told(self.told, read["found"], tick))
        self.told.update({l: (tip, told[l]) for l, _, tip, _ in read["found"] if l in told})
        self.last = dict(self.last, said=said.getvalue().strip(), read=dict(read, swept=swept, moved={"raised": [], "unread": []}, ended=ended, unchecked=unchecked),
                         stamps=dict(self.last["stamps"], readings=stamps["readings"], cards=self.cards, queues=stamps.get("queues", {})))

    def again(self, fleet):
        """crew's checkout or the teams file moved: each partition's agents here that it made due a restart are handed
        theirs (crew _update, teams.19), and the follower starts again as the new crew, its lock handed on and what the
        update said with it; the kept read goes with this process. When it can't start again it reads afresh here."""
        cmd = ["bash", str(crew.HOME / "plugin/bin/crew")]
        updated = {l: subprocess.run(cmd + ["_update", "--label", l], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout.strip() or None
                   for l in self.labels}
        if self.watches is not None:
            self.watches.close_all()
        try:
            os.set_inheritable(self.lock.fileno(), True)
            sys.stdout.flush()
            os.execve(sys.executable, [sys.executable, str(LIB / "board.py"), *sys.argv[1:]],
                      dict(os.environ, CREW_FOLLOWER_LOCK=str(self.lock.fileno()), CREW_FOLLOWER_UPDATED=json.dumps(updated)))
        except OSError as e:
            print(f"crew's follower could not start again as the new crew ({e.strerror or e}); it reads afresh as it is", file=sys.stderr)
            self.updated, self.last = updated, None

    def write(self, fleet):
        """Each partition's frames from the one read, as of now: its rail, with what the read said and what could not be
        read or fetched; its board; and its agents' views, with what this host's agents run of crew."""
        now = datetime.datetime.now(datetime.timezone.utc)
        last = self.last or {"read": None, "said": ""}
        for l in self.labels:
            read, unfetched = last["read"], self.unfetched.get(l, {})
            if read is None:
                text = last["said"] or f"crew's follower on {crew.this_host()} has no read of {l}"
                data = None
            else:
                read = dict(read, errors={**read["errors"], **{k: f"could not fetch it, so it is shown as this host last fetched it: {v}"
                                                               for k, v in unfetched.items() if k.startswith(f"{l}/main of ")}})
                sigs, sunread = read["signals"].get(l, ([], {}))
                read["signals"] = dict(read["signals"], **{l: (sigs, {**sunread, **{k: f"could not fetch it: {v}" for k, v in unfetched.items()
                                                                                       if not k.startswith(f"{l}/main of ")}})})
                errors = label_errors(read["errors"], l)
                text = "\n".join([plan.rail_text(fleet, [l], read, now)] + ([last["said"]] if last["said"] else []) + list(errors.values()))
                data = dict(board_data(fleet, [l], read, now), unread=errors)
            try:
                write_frame(l, {"read_at": iso(now), "from": crew.this_host(), "text": text, "updated": self.updated.get(l)}, rail_path(l))
                if data is not None:
                    key = here_key(self.seen["crew"])
                    if self.here.get(l, (None,))[0] != key:
                        self.here[l] = (key, here_read(fleet, l))
                    write_frame(l, data)
                    write_frame(l, agent_views(dict(data, here=self.here[l][1])), agents_path(l))
            except OSError as e:
                print(f"crew could not write {l}'s frames in {FRAMES}: {e.strerror or e}", file=sys.stderr)
        self.updated = {}

    def close(self):
        if self.watches is not None:
            self.watches.close_all()
        self.lock.close()


def run_follow(once=False):
    """crew _follow: the host's follower with no tab, the command a job of the host's runs (swancloud's): it waits for
    the lock while another follows, reading nothing, then follows every partition with an operator session here."""
    lock = lock_follower("job", wait=True)
    f = Follower(lock, int(os.environ.get("CREW_TEST_PERIOD") or PERIOD), watch=not once)
    signal.signal(signal.SIGUSR1, lambda *_: f.tick_now())
    try:
        if once:
            f.once()
            for l in f.labels:
                print(f"{l}'s rail, board and agents' views written on {crew.this_host()}")
            return
        print(f"crew's follower on {crew.this_host()} follows its partitions' rails and boards", flush=True)
        while True:
            f.step()
    finally:
        f.close()


def rail_follow(label, once=False):
    """The rail tab: the latest rail frame drawn whenever it changes, or how stale it is does; checked once a second.
    Each second, while no one follows on the host, it takes the follower lock without waiting and is the host's
    follower itself, for every partition with an operator session here, on the follower's clock and look (Follower); so a
    tab drawing the job's frames follows itself within a second of the job ending. With once, one draw, following
    nothing."""
    tty = sys.stdout.isatty()
    seen, data, mtime, follower = None, None, False, None
    try:
        while True:
            try:
                m = rail_path(label).stat().st_mtime_ns
            except OSError:
                m = None
            if m != mtime:
                mtime, data = m, read_rail(label) if m is not None else None
            text = rail_frame_text(label, data, datetime.datetime.now(datetime.timezone.utc))
            if text != seen:
                seen = text
                sys.stdout.write(("\033[H\033[2J" if tty else "") + text + "\n")
                sys.stdout.flush()
            if once:
                return
            if follower is None:
                lock = lock_follower("tab", label, wait=False)
                follower = Follower(lock) if lock else None
                if follower:
                    signal.signal(signal.SIGUSR1, lambda *_: follower.tick_now())
            if follower:
                follower.step(1)
            else:
                time.sleep(1)
    finally:
        if follower:
            follower.close()


def ended_by_signal():
    """A follower told to end, by its job's manager or its pane's close, ends its follows and lets go of its lock."""
    for s in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, lambda *_: sys.exit(0))


# ------------------------------------------------------------------------------------------------- commands

def main(argv):
    plan.need_recutils()
    sub, argv = (argv[0], argv[1:]) if argv else ("board", [])
    sub in ("board", "_views", "_board", "_rail", "_follow") or fail(f"board.py runs crew board, _views, _board, _rail or _follow, not {sub}")
    ap = argparse.ArgumentParser(prog=f"crew {sub}")
    fleet = crew.load()
    if sub in ("_board", "_rail"):
        ap.add_argument("label")
        ap.add_argument("--once", action="store_true")
        a = ap.parse_args(argv)
        if sub == "_rail":
            ended_by_signal()
        (follow if sub == "_board" else rail_follow)(crew.partition_of(fleet, a.label)["label"], a.once)
        return
    if sub == "_follow":
        ap.add_argument("--once", action="store_true")
        a = ap.parse_args(argv)
        ended_by_signal()
        run_follow(a.once)
        return
    if sub == "_views":
        ap.add_argument("label")
        a = ap.parse_args(argv)
        labels = [crew.partition_of(fleet, a.label)["label"]]
    else:
        ap.add_argument("--label")
        ap.add_argument("--json", action="store_true")
        a = ap.parse_args(argv)
        label = plan.default_label(fleet, a)
        labels = [label] if label else list(fleet["partitions"])
    read = flow_read(fleet, labels, sweep=sub == "_views")
    now = datetime.datetime.now(datetime.timezone.utc)
    data = board_data(fleet, labels, read, now)
    if sub == "_views":
        print(plan.rail_text(fleet, labels, read, now))
        try:
            write_frame(labels[0], data)
            write_frame(labels[0], agent_views(dict(data, here=here_read(fleet, labels[0]))), agents_path(labels[0]))
        except OSError as e:
            print(f"crew could not write the board's frame in {FRAMES}: {e.strerror or e}", file=sys.stderr)
    elif a.json:
        print(json.dumps(data, indent=1))
    else:
        tty = sys.stdout.isatty()
        print(board_text(data, shutil.get_terminal_size().columns if tty else None, tty and not os.environ.get("NO_COLOR")))
    if read["errors"]:
        sys.exit("\n".join(read["errors"].values()))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
