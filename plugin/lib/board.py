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
  crew _views <label>                the rail tab's refresh: one read, the rail printed as crew rail prints it, the
                                     card sessions of closed cards and gone rows ended as crew rail ends them, and
                                     the board's data written for the board tab, with each agent's view of it for
                                     the band crew's mod draws above that agent's prompt
  crew _board <label> [--once]       the board tab: the latest board the rail tab's loop wrote, drawn at the pane's
                                     width whenever it or the pane changes

Read from the plan, the proposals, the moves, the signals, the kits and the run record, in one read that also makes the
rail (plan.rail_read); no state is written, only the frames the rail tab hands the board tab and the agents' mods, in
crew's cache, each one redraw and not state (state.4). The rail tab's refresh, as it prints the rail, ends the card
sessions whose card is closed or whose row is gone, as crew rail does; crew board ends nothing. The board answers
nothing and prints no command: the rail and its shell are where things are answered."""
import argparse, datetime, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew, ops, plan, record, sites  # noqa: E402
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
# The frame the rail tab's loop writes for the board tab, by label.
FRAMES = pathlib.Path.home() / ".cache/crew/board"
STALE = 90  # seconds: three of the rail tab's periods
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
    """The text of each path at tip in crew's cache of the repo, in one git cat-file --batch: {path: text}, a path
    that is not there left out."""
    if not paths:
        return {}
    r = subprocess.run(["git", "-C", str(plan.cache(repo)), "cat-file", "--batch"], input="".join(f"{tip}:{p}\n" for p in paths).encode(),
                       capture_output=True, env=plan.gitenv())
    r.returncode == 0 or fail(f"git cat-file in crew's cache of {repo} failed: {r.stderr.decode(errors='replace').strip()}")
    out, data, i = {}, r.stdout, 0
    for p in paths:
        nl = data.index(b"\n", i)
        head, i = data[i:nl], nl + 1
        if head.endswith((b" missing", b" ambiguous")):
            continue
        _, kind, size = head.rsplit(b" ", 2)
        if kind == b"blob":
            out[p] = data[i:i + int(size)].decode("utf-8", "replace")
        i += int(size) + 1
    return out


def signals_at(repo, tip, home, moved):
    """Each signal at tip whose id has no move, with its capture's captured_by (its source when it has none) and when
    the capture was made (its at, else its event_date, which is what a signal's age counts from, as stamp gives it),
    its kind and the first line of its body."""
    sigs = [m.groups() for m in map(SIGNAL.match, plan.git(repo, "ls-tree", "-r", "--name-only", tip, "--", "signals/").splitlines()) if m]
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

def marker(r, cards, label):
    """A rail row as a marker: its group, its card key, its glyph, when it began to wait, and its card, open or None."""
    card = [c for c in cards if (c["label"], c["key"]) == (label, r["key"])]
    return {"group": r["group"], "key": r["key"], "glyph": GLYPH[r["group"]], "at": r.get("date") or iso(r["at"]),
            "card": {"by": card[-1]["by"], "host": card[-1]["host"], "at": iso(card[-1]["at"])} if card else None}


def markers(rows, cards, label, group, obj):
    """The rail's rows for an object, as markers."""
    return [marker(r, cards, label) for r in rows if r["label"] == label and r["group"] == group and r["key"].split("/")[1] == obj]


def keyed(rows, cards, label, key):
    """The rail's row with that card key, as a marker, when there is one: an operation's, whose key names the deploy or
    the step itself."""
    return [marker(r, cards, label) for r in rows if key and r["label"] == label and r["key"] == key]


def environments(fleet, label, teams, entries, rows, cards, since):
    """The partition's environments for the Operation lane: each one's deploys that moved since since or are still open,
    and the operations waiting on it, as ops.environments reads them from the run record (plan.14, state.4), each
    deploy and operation with its rail row's marker; and the teams on that host, which is what the page narrows by."""
    return [{"env": env, "teams": [t["team"] for t in teams if t["host"] == env],
             "deploys": [dict(d, markers=keyed(rows, cards, label, d["row"])) for d in v["deploys"]],
             "waiting": [dict(w, markers=keyed(rows, cards, label, w["row"])) for w in v["waiting"]]}
            for env, v in ops.environments(entries, iso(since)).items()]


def board_data(fleet, labels, read, now):
    """The board of each label as data, the fields the page reads (`crew board --json`). Each partition lists its teams,
    and each object of its lanes says the teams it belongs to, which is what the page narrows by: a held bolt and a
    landing, its team; a signal, the team whose agent captured it; a proposal, the teams holding the bolts it names
    and those building the repository of a bolt no team holds, of a bolt it makes or of a queued unit; anything else,
    every team building its repository. A ledger's units, chores and fixes are its own; each unit or chore says its kind."""
    here = crew.this_host()
    rows, cards, sv = read["rows"], read["cards"], read["sv"]
    since = plan.utc(record.when(None)[1])
    parts = []
    for l in labels:
        p = crew.partition_of(fleet, l)
        found = next(((repo, tip, pl) for x, repo, tip, pl in read["found"] if x == l), None)
        repo, tip, pl = found or (plan.state_of(fleet, l)[0], None, None)
        unread = read["unread"].get(l, {})
        teams = [{"team": t, "kit": fleet["teams"][t]["kit"]["name"], "host": fleet["teams"][t]["machine"]} for t in p["teams"]]

        def building(repo):
            return [t["team"] for t in teams if repo and t["kit"] == repo]

        def ordered(ts):
            return [t for t in p["teams"] if t in ts]
        asked = set(crew.partition_hosts(fleet, l))
        hosts = {}
        for h in sorted(asked | (set(record.hosts_of(fleet, l)) if l in read["unread"] else set())):
            v = sv.get(h)
            why = ([f"its kits: {v['error']}"] if h in asked and v and not v["ok"] else []) + ([f"its run record: {unread[h]}"] if h in unread else [])
            hosts[h] = "; ".join(why) or True
        attention = [{"what": "host", "name": h, "why": v} for h, v in hosts.items() if v is not True]
        attention += [{"what": "plan", "name": n, "why": why} for n, why in unread.items() if n not in fleet["hosts"]]
        attention += [{"what": "plan", "name": n, "why": why} for n, why in read["errors"].items() if n.startswith(f"{l}/main of ") or n == f"the plan of {l}"]
        if found and not tip:
            attention.append({"what": "plan", "name": f"{l}/main of {repo}", "why": "not started, so there is no plan to read"})
        sigs, sunread = read["signals"].get(l, ([], {}))
        attention += [{"what": "signals", "name": n, "why": why} for n, why in sunread.items()]

        explorations = []
        for kit in dict.fromkeys(fleet["teams"][t]["kit"]["name"] for t in sorted(p["teams"])):
            for t in (fleet["teams"][x] for x in sorted(p["teams"]) if fleet["teams"][x]["kit"]["name"] == kit):
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
                      "waiting": d["waiting"], "markers": markers(rows, cards, l, "proposals", str(d.get("first") or d["proposal"])), "teams": proposal_teams(d)}
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
                ledger = {"bolt": b.name(), "repo": b.get("Repo"), "goal": b.get("Goal"), "team": b.get("Team"), "host": t["machine"] if t else None,
                          "state": state, "url": url(k.get("bolts", {}).get(b.name(), {}).get("worktree")),
                          "markers": markers(rows, cards, l, "land", b.name()), "teams": [b.get("Team")], "units": [], "fixes": []}
                for u in units:
                    s = st.of(u.name())
                    ledger["units"].append({"unit": u.name(), "kind": plan.kind_of(u), "stage": s["stage"], "tasks": s["tasks"],
                                            "slot": slot(plan.kind_of(u), u.name()),
                                            "worktree": s["worktree"], "url": url(s["worktree"])})
                ledger["fixes"] = [{"fix": f["fix"], "merged": f["merged"], "slot": slot("fix", f["fix"]), "worktree": f["path"], "url": url(f["path"])}
                                   for f in k.get("fixes", []) if f["bolt"] == b.name()]
                construction.append(ledger)
                if state == "landed":
                    attention.append({"what": "landed", "name": b.name(), "why": "every unit has landed on main, and the bolt is still in the plan"})
            queue = [{"unit": u.name(), "kind": plan.kind_of(u), "repo": u.get("Repo"), "sources": u.all("Source"), "teams": building(u.get("Repo"))}
                     for u in pl.queue()]
        operation = [{"bolt": x["bolt"], "at": iso(x["at"]), "by": x["by"], "units": x["units"], "team": read["gives"].get((l, x["bolt"])),
                      "teams": [read["gives"][(l, x["bolt"])]] if read["gives"].get((l, x["bolt"])) else []}
                     for x in sorted(read["landings"], key=lambda x: x["at"], reverse=True) if x["label"] == l and x["at"] and x["at"] >= since]
        envs = environments(fleet, l, teams, read.get("ops", {}).get(l, []), rows, cards, since)
        parts.append({"label": l, "plan": tip, "hosts": hosts, "teams": teams,
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
    return [("no card open" if not m["card"] else f"card open, asked by {m['card']['by']}", None) for m in ms]


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
    """Where a deploy stands, as the board says it: waiting on the user's word, replaced unanswered, its outcome and
    when it ended, at the step that failed, deploying, or approved and not yet deployed."""
    if d["answer"] == "waiting":
        return "waits on the user's word"
    if d["answer"] == "replaced":
        return "replaced by a newer offer, unanswered"
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
    """An operation waiting on an environment: its key, who has it, and its first line or note."""
    said = {"handed": f"handed to {w['agent'] or w['doer']}", "failed": "failed"}.get(w["state"]) or (
        "waits on the user" if w["doer"] == "user" else f"waits for {w['agent'] or w['doer'] or 'its doer'}")
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
        line([(f"{p['label']} board, as of {read_at.astimezone():%H:%M:%S}" + (f" ({stale} ago: the rail tab has not refreshed it since)" if stale else "")
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
                        "" if b["state"] == "active" else b["state"]), gutter(b["markers"], b["state"] == "landed"), 0, b["markers"])
            for u in b["units"]:
                line(fields(u["unit"], stage_of(u), u["slot"] or "", u["url"] or ""), " ", 2)
            for f in b["fixes"]:
                line(fields(f["fix"], "fix merged" if f["merged"] else "fix", f["slot"] or "", f["url"] or ""), " ", 2)
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


def bolt_row(b, team=None):
    """A held bolt on one line, led by its product, the repository it builds, and, when given, the team holding it,
    dim; then its pips, its name, its state unless active and how many of its units have merged; its landing's marker
    in the gutter, or attention once every unit has landed."""
    return row(fields(b["repo"] or "", (team, "dim") if team else "", pips(b["units"]), b["bolt"], "" if b["state"] == "active" else b["state"],
                      merged(b)), gutter(b["markers"], b["state"] == "landed"), 0, b["markers"])


def ledger_rows(b):
    """A held bolt as its conductor reads it: the bolt, then a unit to a line, its pip, stage and slot, then each fix."""
    return ([bolt_row(b)]
            + [row(fields(PIP.get(u["stage"], "?"), u["unit"], stage_of(u), u["slot"] or ""), " ", 2) for u in b["units"]]
            + [row(fields(f["fix"], "fix merged" if f["merged"] else "fix", f["slot"] or ""), " ", 2) for f in b["fixes"]])


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


def design_view(p):
    """The design agent's: the signals no move has taken, counted by who captured them, and the explorations on each
    kit's main, the first few named and the rest counted; and what keeps the signals or the plan from being read."""
    inc, groups = p["inception"], {}
    for s in inc["signals"]:
        groups.setdefault(s["captured_by"], []).append(s)
    es = inc["explorations"]
    head = row(fields((f"{p['label']} inception", "bold"), many(len(inc["signals"]), "signal not moved", "signals not moved"),
                      many(len(es), "exploration", "explorations")))
    return ([head]
            + [row(fields(f"signals captured by {who or 'no one named'}", f"{len(mine)} not moved"), " ") for who, mine in groups.items()]
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
    approve = (sum(len(d["markers"]) for d in bp["proposals"]) + sum(len(b["markers"]) for b in p["construction"])
               + sum(len(x["markers"]) for e in envs for x in e["deploys"] + e["waiting"]))
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
    """Main-level ops's: the partition's operations in brief, then, environment by environment, each deploy waiting on
    the user's word with its card, each approved and not yet deployed, each running, and each operation step waiting,
    handed or failed, with the deploy it comes after and its doer; and what keeps a host or the plan from being read."""
    pending = [(e["env"], d) for e in p.get("environments", []) for d in e["deploys"] if not d["ended"] and d["answer"] != "replaced"]
    steps = [(e["env"], w) for e in p.get("environments", []) for w in e["waiting"]]
    word = sum(d["answer"] == "waiting" for _, d in pending)
    running = sum(bool(d["started"]) for _, d in pending)
    head = row(fields((f"{p['label']} operations", "bold"), many(word, "deploy waits on the user's word", "deploys wait on the user's word"),
                      many(running, "deploy running", "deploys running"), many(len(steps), "operation waiting", "operations waiting")))
    out = [head]
    for e in p.get("environments", []):
        for d in (d for env, d in pending if env == e["env"]):
            out.append(row(fields(e["env"], f"deploy {d['to'][:7]}", deploy_state(d)), gutter(d["markers"]), 0, d["markers"]))
        for w in (w for env, w in steps if env == e["env"]):
            doer = (w["doer"] or "no doer named") + (f", {w['agent']}" if w["agent"] else "")
            out.append(row(fields(e["env"], w["key"], (f"after {w['to'][:7]}", "dim") if w["to"] else "", w["state"], f"doer {doer}"),
                           gutter(w["markers"]), 0, w["markers"]))
    return out + attention_rows(p, lambda a: a["what"] in ("host", "plan"))


def agent_views(data):
    """Each crew agent's view of its partition's board, by the agent's name, for the band crew's mod draws above its
    prompt (plugin/hooks/status.js): each team's conductor's, the planner's, the design agent's, main-level ops's and
    each host's operator's, every line a list of (text, style) segments. Any other agent has no view, and its mod draws nothing.
    With them, the line the mod adds once the frame is stale_after_ms old: when it was read, and that the rail tab has
    not refreshed it since.

    A change to what crew models (bolts, units, stages, proposals, explorations and elaborations, cards, rail rows)
    changes these views and plugin/hooks/status.js with it, each with its cases (code.8)."""
    views = {}
    for p in data["partitions"]:
        views.update({f"{t['team']}-conductor": conductor_view(p, t["team"]) for t in p["teams"]})
        views.update({f"{p['label']}-planner": planner_view(p), f"{p['label']}-design": design_view(p), f"{p['label']}-ops": ops_view(p)})
        views.update({f"{p['label']}-operator-{h}": operator_view(p) for h in p["hosts"]})
    return {"read_at": data["read_at"], "stale_after_ms": STALE * 1000,
            "stale": row([(f"read at {plan.utc(data['read_at']).astimezone():%H:%M}; the rail tab on {data['from']} has not refreshed it since", "dim")]),
            "views": views}


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
    return (f"No board for {label} yet: the rail tab's loop writes it each time it refreshes, and has not written one. A rail tab "
            f"opened before crew board existed draws no board: close the operator workspace's rail tab and run "
            f"crew operator up {label}, which opens the rail tab and this board tab afresh.")


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


# ------------------------------------------------------------------------------------------------- commands

def main(argv):
    plan.need_recutils()
    sub, argv = (argv[0], argv[1:]) if argv else ("board", [])
    sub in ("board", "_views", "_board") or fail(f"board.py runs crew board, _views or _board, not {sub}")
    ap = argparse.ArgumentParser(prog=f"crew {sub}")
    fleet = crew.load()
    if sub == "_board":
        ap.add_argument("label")
        ap.add_argument("--once", action="store_true")
        a = ap.parse_args(argv)
        follow(crew.partition_of(fleet, a.label)["label"], a.once)
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
            write_frame(labels[0], agent_views(data), agents_path(labels[0]))
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
