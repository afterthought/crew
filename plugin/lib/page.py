#!/usr/bin/env python3
"""page.py: a flywheel's page, one HTML file: its board, and its lineage drawn from its run record.

  crew page <label> [--out <file>] [--since <time>]
                                     the partition's board, as crew board reads it, which the page opens on; and the
                                     flywheel's signals, agenda items, proposals, units and bolts as columns, a line for
                                     each link between two of them, a timeline of the entries beneath, and each
                                     object's history; written whole to ~/.local/state/crew/<label>/page.html on this
                                     host, or to --out, and its path printed with what it was made from

The board is the one read crew board makes (board.flow_read), of the one partition. Which objects the lineage holds,
how they are linked and each one's history are read from the run record's entries alone, by the walk crew trace makes
(record.lineage), so the page and the trace cannot disagree. Labels and present status are read from the plan and kits
the board read, at the commit the entries were read at, which a command fetches once (plan.12); no entry holds them
(record.3). The file holds its data, style and script, and loads nothing. Nothing reads it, it is never committed, and
making it appends no entry (state.4, record.1)."""
import argparse, datetime, json, os, pathlib, sys, tempfile

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import board, crew, plan, record  # noqa: E402
from crew import Refusal, fail  # noqa: E402

TEMPLATE = LIB / "page.html"
DATA = "/*{{DATA}}*/"
# The page's columns, in the flow's order.
COLUMNS = ("signals/", "agenda/", "proposal/", "unit/", "bolt/")
# Present status, as the page colours it: open, in flight, done or dropped; None when it can't be told.
UNIT = {"queued": "open", "waiting": "open", "ready": "open", "construct": "flight", "amended": "flight", "planned": "flight",
        "code": "flight", "verify": "flight", "merged": "done", "landed": "done"}
BOLT = {"planned": "open", "active": "flight", "landed": "done"}
PROPOSAL = {"open": "open", "approved": "done", "dropped": "dropped"}
ITEM = {"open": "open", "planned": "done", "decided": "done", "dropped": "dropped"}
# What a unit or bolt the plan no longer holds became, from the act that took it out.
GONE = {"unit.drop": "dropped", "bolt.drop": "dropped", "bolt.land": "done"}


def column(obj):
    return next((i for i, k in enumerate(COLUMNS) if obj.startswith(k)), None)


# ------------------------------------------------------------------------------------------------- the data

def data(entries, since=None):
    """The page's objects from the entries at or after since (an ISO stamp; all of them without it): nodes, every
    object of the five kinds an entry names in On or From; edges, for each entry the objects of those kinds it names
    joined in the flow's order, each to those of the next column it names, so no line skips a column the entry names,
    a unit.move's From bolt left out, since that is where the unit was; histories, each node's entries as crew trace
    walks them, by Id; and entries, one table by Id."""
    entries = sorted((e for e in entries if not since or e["At"] >= since), key=lambda e: (e["At"], e["Id"]))
    nodes, edges = {}, {}
    for e in entries:
        named = [o for o in dict.fromkeys(e["On"] + e["From"]) if column(o) is not None]
        for o in named:
            kind, name = o.split("/", 1)
            nodes.setdefault(o, {"id": o, "kind": kind, "name": name, "first": e["At"]})["last"] = e["At"]
        linked = [o for o in named if not (e.get("Act") == "unit.move" and o.startswith("bolt/") and o in e["From"] and o not in e["On"])]
        cols = sorted({column(o) for o in linked})
        for a, b in zip(cols, cols[1:]):
            for x in (o for o in linked if column(o) == a):
                for y in (o for o in linked if column(o) == b):
                    edges.setdefault((x, y), []).append(e["Id"])
    index = record.named_by(entries)
    return {"nodes": sorted(nodes.values(), key=lambda n: (column(n["id"]), n["first"], n["id"])),
            "edges": [{"from": x, "to": y, "entries": ids} for (x, y), ids in edges.items()],
            "histories": {o: [e["Id"] for e in record.lineage(entries, o, index)] for o in nodes},
            "entries": {e["Id"]: e for e in entries}}


def from_entries(node, entries):
    """A node the state no longer holds: its label, the Why of its newest entry that has one, and what it became, from
    the newest act on it that took it out of the plan and was not refused, else None. Its entries are those that act
    on it, naming it in On; one that names it only in From is another object's."""
    mine = [e for e in reversed(entries) if node["id"] in e["On"]]
    node["label"] = next((e["Why"] for e in mine if e.get("Why")), None)
    node["status"] = next((GONE[e["Act"]] for e in mine if e.get("Act") in GONE and not e.get("Refused")), None)
    node["gone"] = True


def describe(fleet, label, repo, tip, d, pl=None, sv=None):
    """Each node's label and present status, read from the flywheel's state at tip: a signal's assertion and whether
    a move has taken it; an item's subject, lane and state; a proposal's first line of case and its state; a unit's
    intent and stage, read from its kit as crew bolts reads it; a bolt's goal, team and state. pl and sv, when given,
    are the plan at tip and the survey of its kits another read already made, so neither is read again. Returns the
    hosts whose kits did not answer, {host: why}; their units' and bolts' stages are left blank."""
    pl = pl or plan.read(repo, f"{label}/main", tip)

    def recs(path, kind, key):
        text = plan.show(repo, tip, path)
        return {r.get(key): r for r in plan.Plan(text).recs(kind)} if text else {}
    proposals, items, moves = recs("proposals.rec", "Proposal", "Proposal"), recs("agenda.rec", "Item", "Item"), recs("moves.rec", "Move", "Signal")
    if sv is None:
        sv = plan.survey(fleet, [(b.get("Team"), b.name()) for b in pl.bolts() if b.get("Team")])
    st = plan.Stages(fleet, pl, sv)
    entries = list(d["entries"].values())
    for n in d["nodes"]:
        kind, name, n["facts"] = n["kind"], n["name"], []
        if kind == "signals":
            assertion = plan.signal_text(fleet, label, name)[0]
            if assertion is None:
                from_entries(n, entries)
                continue
            m = moves.get(name)
            n.update(label=" ".join(assertion.split()), status="open" if not m else "dropped" if m.get("Move") == "drop" else "done")
            n["facts"] = [m.get("Move")] if m else []
        elif kind == "agenda" and name in items:
            i = items[name]
            n.update(label=i.get("Subject"), status=ITEM.get(i.get("State")), facts=[x for x in (i.get("Lane"), i.get("State")) if x])
        elif kind == "proposal" and name in proposals:
            p = proposals[name]
            n.update(label=((p.get("Case") or "").strip().splitlines() or [None])[0], status=PROPOSAL.get(p.get("State")), facts=[p.get("State")])
        elif kind == "unit" and pl.unit(name):
            stage = st.of(name)["stage"]
            stage = None if stage == "unknown" else stage
            n.update(label=pl.unit(name).get("Intent"), status=UNIT.get(stage), stage=stage, facts=[stage] if stage else [])
        elif kind == "bolt" and pl.bolt(name):
            b = pl.bolt(name)
            state = st.bolt_state(b)
            state = None if state == "unknown" else state
            n.update(label=b.get("Goal"), status=BOLT.get(state), team=b.get("Team"), facts=[x for x in (b.get("Team"), state) if x])
        else:
            from_entries(n, entries)
    return {h: f"its kits: {v['error']}" for h, v in sv.items() if not v["ok"]}


# ------------------------------------------------------------------------------------------------- the file

def header(made):
    """As of when and which commit the page was drawn from; both commits, the run record's and the plan's, should the
    board's read have found the branch at another (read.1)."""
    plan_tip = made.get("plan")
    return (f"as of {made['at'][:10]} {made['at'][11:16]}Z · {made['label']}/main {made['commit'][:7]}"
            + (f" for the run record, {plan_tip[:7]} for the board and labels" if plan_tip and plan_tip != made["commit"] else ""))


def render(d):
    """The page: the template with the data in its one placeholder, as JSON a script block can hold, every < escaped
    so nothing in it can end the block."""
    text = json.dumps(d, separators=(",", ":"), ensure_ascii=False)
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    page = TEMPLATE.read_text()
    page.count(DATA) == 1 or fail(f"{TEMPLATE} must hold its data placeholder {DATA} once")
    return page.replace(DATA, text)


def write(path, text):
    """The page written whole: a temporary file in its folder, then moved over any earlier one, so a reader never sees
    half of it."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    except OSError as e:
        fail(f"crew could not write the page in {path.parent}: {e.strerror or e}")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        os.unlink(tmp)
        fail(f"crew could not write the page at {path}: {e.strerror or e}")


def page(fleet, a):
    label = a.label
    crew.partition_of(fleet, label)
    repo, ref = plan.state_of(fleet, label)
    day, stamp = record.when(a.since) if a.since else ("0000-00-00", None)
    tips = {}
    entries, missing = record.gather(fleet, [label], day, tips)
    branch = f"{label}/main"
    if branch in missing:
        fail(f"no page is written: {branch} of {repo} could not be read ({missing.pop(branch)}), and the page names the commit it is drawn from")
    tip = tips.get(label) or fail(f"no page is written: {branch} of {repo} is not started, so there is no commit to draw from: crew state init {label}")
    # The board's read, of this partition alone: the branch's tip is the one just fetched, so both views are of one
    # commit. A host, plan or signal home it could not read is in the board's attention, and the page still written.
    read = board.flow_read(fleet, [label])
    now = datetime.datetime.now(datetime.timezone.utc)
    bd = board.board_data(fleet, [label], read, now)
    part = bd["partitions"][0]
    pl = next((f[3] for f in read["found"] if f[0] == label and f[2] == part["plan"]), None)
    d = data(entries, stamp)
    for h, why in describe(fleet, label, repo, part["plan"] or tip, d, pl, read["sv"] if pl else None).items():
        missing.setdefault(h, why)
    d["made"] = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "label": label, "repo": repo, "commit": tip, "plan": part["plan"], "since": stamp,
                 "unreachable": missing}
    d["board"] = dict(part, read_at=bd["read_at"], unread=bd["unread"])
    d["partitions"], d["label"] = list(fleet["partitions"]), label
    if a.json:
        print(json.dumps(d, indent=1))
        return
    out = pathlib.Path(a.out).expanduser().absolute() if a.out else record.ROOT / label / "page.html"
    write(out, render(d))
    print(out)
    print(header(d["made"]))
    if not d["entries"]:
        print("nothing has been recorded" + (f" since {stamp}" if stamp else ""))
    for h, why in missing.items():
        print(f"{h} did not answer: {why}")


def main(argv):
    plan.need_recutils()
    sub, argv = (argv[0], argv[1:]) if argv else (None, [])
    sub == "page" or fail(f"page.py runs crew page, not {sub}")
    ap = argparse.ArgumentParser(prog="crew page")
    ap.add_argument("label")
    ap.add_argument("--out")
    ap.add_argument("--since")
    ap.add_argument("--json", action="store_true", help=argparse.SUPPRESS)  # the page's data, for tests: nothing is written
    page(crew.load(), ap.parse_args(argv))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
