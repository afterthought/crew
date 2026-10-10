#!/usr/bin/env python3
"""board.py: the board of a partition's flow, read from crew's state.

  crew board [--label L] [--json]    the flow as four lanes stacked one above the other, one object to a line:
                                     Inception (the signals no move has taken, by who captured them, and the
                                     explorations on each kit's main), Bolt plan (the open proposals, the planned
                                     bolts and the queue), Construction (each held bolt as a ledger of its units and
                                     fixes) and Operation (the bolts landed in the last seven days); every rail row a
                                     marker on its object, and what needs attention at the foot
  crew _views <label>                the rail tab's refresh: one read, the rail printed as crew rail prints it, and
                                     the board's data written for the board tab
  crew _board <label> [--once]       the board tab: the latest board the rail tab's loop wrote, drawn at the pane's
                                     width whenever it or the pane changes

Read from the plan, the proposals, the moves, the signals, the kits and the run record, in one read that also makes the
rail (plan.rail_read); nothing is written but the frame the rail tab hands the board tab, in crew's cache, which is one
redraw and not state (state.4). The board answers nothing and prints no command: the rail and its shell are where
things are answered."""
import argparse, datetime, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew, plan, record, sites  # noqa: E402
from crew import Refusal, fail  # noqa: E402

# Flywheel Next's glyph for the decision a rail row asks (S17): an approval, held on the card's button, or an answer
# in the user's own words.
GLYPH = {"proposals": "✓", "land": "✓", "verify": "✎"}
ATTENTION = "!"
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


def flow_read(fleet, labels):
    """One read of the labels' flow, which makes both the rail and the board: the rail's read with every team of the
    labels surveyed, its dev servers, slots and explorations too (plan.rail_read), and the signals of each label whose
    plan was read; a plan that could not be read leaves its moves unknown, and is named already."""
    read = plan.rail_read(fleet, labels, board=True)
    read["signals"] = {l: signals(fleet, l, tip) for l, _, tip, _ in read["found"]}
    return read


# ------------------------------------------------------------------------------------------------- the data

def markers(rows, cards, label, group, obj):
    """The rail's rows for an object, as markers: each with its group, its card key, its glyph, when its row began to
    wait, and its card, open or None."""
    out = []
    for r in rows:
        if r["label"] != label or r["group"] != group or r["key"].split("/")[1] != obj:
            continue
        card = [c for c in cards if (c["label"], c["key"]) == (label, r["key"])]
        out.append({"group": group, "key": r["key"], "glyph": GLYPH[group], "at": r.get("date") or iso(r["at"]),
                    "card": {"by": card[-1]["by"], "host": card[-1]["host"], "at": iso(card[-1]["at"])} if card else None})
    return out


def board_data(fleet, labels, read, now):
    """The board of each label as data, the fields the page reads (`crew board --json`)."""
    here = crew.this_host()
    rows, cards, sv = read["rows"], read["cards"], read["sv"]
    since = plan.utc(record.when(None)[1])
    parts = []
    for l in labels:
        p = crew.partition_of(fleet, l)
        found = next(((repo, tip, pl) for x, repo, tip, pl in read["found"] if x == l), None)
        repo, tip, pl = found or (plan.state_of(fleet, l)[0], None, None)
        unread = read["unread"].get(l, {})
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
                    explorations += [{"kit": kit, "name": e["name"], "first": e["first"]} for e in k["explorations"]]
                    break

        proposals = [{"proposal": d["proposal"], "by": d["by"], "opened": d["opened"], "case": (d["case"] or "").splitlines()[0] if d["case"] else None,
                      "waiting": d["waiting"], "markers": markers(rows, cards, l, "proposals", str(d["proposal"]))}
                     for d in read["props"] if d["label"] == l]
        planned, queue, construction = [], [], []
        if pl:
            st = plan.Stages(fleet, pl, sv)
            for b in pl.bolts():
                units = pl.units_of(b.name())
                if not b.get("Team"):
                    planned.append({"bolt": b.name(), "repo": b.get("Repo"), "goal": b.get("Goal"),
                                    "units": [{"unit": u.name(), "stage": st.of(u.name())["stage"]} for u in units]})
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
                          "markers": markers(rows, cards, l, "land", b.name()), "units": [], "fixes": []}
                for u in units:
                    s = st.of(u.name())
                    ledger["units"].append({"unit": u.name(), "stage": s["stage"], "tasks": s["tasks"], "slot": slot("unit", u.name()),
                                            "worktree": s["worktree"], "url": url(s["worktree"]),
                                            "markers": markers(rows, cards, l, "verify", u.name())})
                ledger["fixes"] = [{"fix": f["fix"], "merged": f["merged"], "slot": slot("fix", f["fix"]), "worktree": f["path"], "url": url(f["path"])}
                                   for f in k.get("fixes", []) if f["bolt"] == b.name()]
                construction.append(ledger)
                if state == "landed":
                    attention.append({"what": "landed", "name": b.name(), "why": "every unit has landed on main, and the bolt is still in the plan"})
            queue = [{"unit": u.name(), "repo": u.get("Repo"), "sources": u.all("Source")} for u in pl.queue()]
        operation = [{"bolt": x["bolt"], "at": iso(x["at"]), "by": x["by"], "units": x["units"], "team": read["gives"].get((l, x["bolt"]))}
                     for x in sorted(read["landings"], key=lambda x: x["at"], reverse=True) if x["label"] == l and x["at"] and x["at"] >= since]
        parts.append({"label": l, "plan": tip, "hosts": hosts,
                      "inception": {"signals": sorted(sigs, key=lambda s: (when(s["at"]) is None, when(s["at"]) or now, s["signal"])),
                                    "explorations": explorations},
                      "bolt_plan": {"proposals": proposals, "planned": planned, "queue": queue},
                      "construction": construction, "operation": operation, "attention": attention})
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


def board_text(data, width=None, color=False, stale=None):
    """The board as text: for each partition a header, the four lanes in order, each a bold heading with its objects
    under it or none, then attention. A marker sits in a two-column gutter at the left of its object's line, its card
    said at the line's end. Each line is cut to width when that is given; bold and dim only with color. stale, when
    given, is how long ago the board was read, said in its header."""
    out = []
    read_at = plan.utc(data["read_at"])

    def line(segs, gutter=None, indent=0, ms=()):
        """One line: a header or heading at the left edge, or, with a gutter, an object, its marker in the gutter."""
        segs = ([(gutter.ljust(2) + " " * indent, None)] if gutter is not None else []) + segs
        for c in card_of(ms):
            segs += [("  ", None), c]
        text, n = "", 0
        for s, style in segs:
            if width is not None:
                s = s[:max(0, width - n)]
            n += len(s)
            text += f"{STYLES[style]}{s}\033[0m" if color and style and s else s
        out.append(text.rstrip())

    def heading(name):
        line([(name, "bold")])

    def gutter(ms, attention=False):
        return ATTENTION if attention else (ms[0]["glyph"] if ms else " ")

    def stage(u):
        return u["stage"] + (f" {u['tasks'][0]}/{u['tasks'][1]}" if u["stage"] in ("code", "verify") and u["tasks"] else "")
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
                line(fields(u["unit"], u["stage"]), " ", 2)
        for u in sorted(bp["queue"], key=lambda u: u["repo"] or ""):
            line(fields(named(u["repo"], u["unit"]), "queued", ", ".join(u["sources"])), " ")
        if not (bp["proposals"] or bp["planned"] or bp["queue"]):
            line([("none", None)], " ")

        heading("Construction")
        for b in p["construction"]:
            line(fields(named(b["repo"], b["bolt"]), f"{b['team']} on {b['host']}" if b["host"] else b["team"],
                        "" if b["state"] == "active" else b["state"]), gutter(b["markers"], b["state"] == "landed"), 0, b["markers"])
            for u in b["units"]:
                line(fields(u["unit"], stage(u), u["slot"] or "", u["url"] or ""), gutter(u["markers"]), 2, u["markers"])
            for f in b["fixes"]:
                line(fields(f["fix"], "fix merged" if f["merged"] else "fix", f["slot"] or "", f["url"] or ""), " ", 2)
            if b["url"]:
                line(fields("server", b["url"]), " ", 2)
        if not p["construction"]:
            line([("none", None)], " ")

        heading("Operation")
        for o in p["operation"]:
            line(gutter=" ", segs=fields(o["bolt"], f"landed {plan.utc(o['at']).astimezone():%Y-%m-%d %H:%M}" + (f" by {o['by']}" if o["by"] else ""),
                               o["team"] or "", ", ".join(o["units"])))
        if not p["operation"]:
            line([("none", None)], " ")

        heading("attention")
        for a in p["attention"]:
            said = {"host": f"{a['name']} did not answer ({a['why']})", "plan": f"the plan, {a['name']}: {a['why']}",
                    "signals": f"the signals on {a['name']}: {a['why']}", "landed": f"bolt {a['name']}: {a['why']}"}[a["what"]]
            line([(said, None)], ATTENTION)
        if not p["attention"]:
            line([("none", None)], " ")
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------- the board tab

def frame_path(label):
    return FRAMES / f"{label}.json"


def write_frame(label, data):
    """The board's data for the board tab, written whole: a temporary file in the same folder, then moved over the
    last one, so the tab never reads half of one."""
    FRAMES.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=FRAMES, prefix=f".{label}.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(data, indent=1) + "\n")
        os.replace(tmp, frame_path(label))
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
    read = flow_read(fleet, labels)
    now = datetime.datetime.now(datetime.timezone.utc)
    data = board_data(fleet, labels, read, now)
    if sub == "_views":
        print(plan.rail_text(fleet, labels, read, now))
        try:
            write_frame(labels[0], data)
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
