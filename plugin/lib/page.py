#!/usr/bin/env python3
"""page.py: a flywheel's page, one HTML file: its board, its lineage and its deploys, drawn from its run record; and
the fleet page, every partition at once.

  crew page <label> [--out <file>] [--since <time>]
                                     the partition's board, as crew board reads it, which the page opens on; the
                                     flywheel's signals, agenda items, proposals, units and bolts as columns, a line for
                                     each link between two of them, a timeline of the entries beneath, and each
                                     object's history; and its deploys, a timeline by environment, each deploy with
                                     the commit it moved from and to, the user's word on it, its steps, checks and
                                     outcome, and the bolts it carried with their changes' proposals as its release
                                     notes; written whole to ~/.local/state/crew/<label>/page.html on this host, or to
                                     --out, and its path printed with what it was made from
  crew page --fleet [--out <file>]   the fleet page: every partition of the teams file at once, a block to each, from
                                     one read of all of them, the one crew board makes: where it runs, each host and
                                     the herdr sessions its agents run in with each one's Claude account; its kits,
                                     each main's last landing and what is queued for it; its teams, each one's bolt,
                                     slots and what its conductor waits on; and what needs attention; each partition
                                     a link to its page and each team to its dock there, in the layout of the file:
                                     <label>.html beside index.html, <label>/page.html beside page.html, none, said
                                     so, for any other name; written whole to ~/.local/state/crew/page.html, beside
                                     the partitions' folders, or to --out

The board is the one read crew board makes (board.flow_read), of the one partition. Which objects the lineage holds,
how they are linked and each one's history are read from the run record's entries alone, by the walk crew trace makes
(record.lineage), so the page and the trace cannot disagree. Labels and present status are read from the plan and kits
the board read, at the commit the entries were read at, which a command fetches once (plan.12); no entry holds them
(record.3). The deploys are the ops entries of the main level's host and the landings, as ops.environments reads them
(plan.14), a deploy's release notes the proposals the lineage joins to each bolt it carried. The fleet page is the
board of every partition from the one read crew board makes of them all, each slot's stage read from the starts and
ends the run record holds in the board's window (read.5), and each session's account from the hosts file (code.5).
Each file holds its data, style and script, and loads nothing. Nothing reads it, it is never committed, and making it
appends no entry (state.4, record.1)."""
import argparse, datetime, html, json, os, pathlib, sys, tempfile

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import board, crew, ops, plan, record  # noqa: E402
from crew import Refusal, fail  # noqa: E402

TEMPLATE = LIB / "page.html"
FLEET = LIB / "fleet.html"
DATA = "/*{{DATA}}*/"
# The run record's window on the fleet page: record.when's default, the board's.
WINDOW = datetime.timedelta(days=7)
NO_ACCOUNT = "no account named in herdr-hosts"
# What starts a stage in a slot, and the stage a fix's start is; a unit's or chore's names its stage.
STARTS = {"stage.start": None, "fix.start": "code", "fix.merge": "merge"}
PARTITIONS = "<!--{{PARTITIONS}}-->"
# The page's columns, in the flow's order; a chore stands in the units' column (plan.11).
COLUMNS = ("signals/", "agenda/", "proposal/", ("unit/", "chore/"), "bolt/")
# Present status, as the page colours it: open, in flight, done or dropped; None when it can't be told.
UNIT = {"queued": "open", "waiting": "open", "ready": "open", "construct": "flight", "amended": "flight", "planned": "flight",
        "code": "flight", "verify": "flight", "merged": "done", "landed": "done"}
BOLT = {"planned": "open", "active": "flight", "waits": "flight", "landed": "done"}
PROPOSAL = {"open": "open", "approved": "done", "dropped": "dropped"}
ITEM = {"open": "open", "planned": "done", "decided": "done", "dropped": "dropped"}
# What a unit or bolt the plan no longer holds became, from the act that took it out.
GONE = {"unit.drop": "dropped", "chore.drop": "dropped", "bolt.drop": "dropped", "bolt.land": "done"}


def column(obj):
    return next((i for i, k in enumerate(COLUMNS) if obj.startswith(k)), None)


# ------------------------------------------------------------------------------------------------- the data

def data(entries, since=None):
    """The page's objects from the entries at or after since (an ISO stamp; all of them without it): nodes, every
    object of the five kinds an entry names in On or From; edges, for each entry the objects of those kinds it names
    joined in the flow's order, each to those of the next column it names, so no line skips a column the entry names,
    a unit.move's From bolt left out, since that is where the unit was, and an entry on a proposal joining only the
    proposal to what it names, since it names everything the proposal touches and which unit went to which bolt is
    its changes' own entries; histories, each node's entries as crew trace walks them, by Id; and entries, one table
    by Id."""
    entries = sorted((e for e in entries if not since or e["At"] >= since), key=lambda e: (e["At"], e["Id"]))
    nodes, edges = {}, {}
    for e in entries:
        named = [o for o in dict.fromkeys(e["On"] + e["From"]) if column(o) is not None]
        for o in named:
            kind, name = o.split("/", 1)
            nodes.setdefault(o, {"id": o, "kind": kind, "name": name, "first": e["At"]})["last"] = e["At"]
        linked = [o for o in named if not (e.get("Act") in ("unit.move", "chore.move") and o.startswith("bolt/") and o in e["From"] and o not in e["On"])]
        cols = sorted({column(o) for o in linked})
        hub = next((o for o in e["On"] if o.startswith("proposal/")), None)
        for a, b in zip(cols, cols[1:]):
            for x in (o for o in linked if column(o) == a):
                for y in (o for o in linked if column(o) == b):
                    if hub in (None, x, y):
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
        sv = plan.survey(fleet, [(b.get("Team"), b.name(), b.get("Repo")) for b in pl.bolts() if b.get("Team")])
    labelled(d, pl, plan.Stages(fleet, pl, sv), proposals, items, moves, lambda name: plan.signal_text(fleet, label, name)[0])
    return {h: f"its kits: {v['error']}" for h, v in sv.items() if not v["ok"]}


def labelled(d, pl, st, proposals, items, moves, assertion_of):
    """Each node of the page's data labelled from the state read: the plan (pl), each unit's and bolt's stage (st), the
    proposals, agenda items and moves by their keys, and a signal's assertion (assertion_of(id), None for one no home
    holds); a node the state no longer holds is labelled from its entries (from_entries)."""
    entries = list(d["entries"].values())
    for n in d["nodes"]:
        kind, name, n["facts"] = n["kind"], n["name"], []
        if kind == "signals":
            assertion = assertion_of(name)
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
        elif kind == "unit" and pl.unit(name) or kind == "chore" and pl.chore(name):
            stage = st.of(name)["stage"]
            stage = None if stage == "unknown" else stage
            n.update(label=pl.item(name).get("Intent"), status=UNIT.get(stage), stage=stage, facts=[stage] if stage else [])
        elif kind == "bolt" and pl.bolt(name):
            b = pl.bolt(name)
            state = st.bolt_state(b)
            state = None if state == "unknown" else state
            n.update(label=b.get("Goal"), status=BOLT.get(state), team=b.get("Team"), facts=[x for x in (b.get("Team"), state) if x])
        else:
            from_entries(n, entries)


def release_notes(d, bolt):
    """A carried bolt's release notes: the proposals the lineage joins to it, through its units or straight, each with
    its number and its label, the first line of its case, in their order."""
    into = {}
    for e in d["edges"]:
        into.setdefault(e["to"], []).append(e["from"])
    seen, todo = set(), [f"bolt/{bolt}"]
    while todo:
        for x in into.get(todo.pop(), []):
            if x not in seen:
                seen.add(x)
                todo.append(x)
    by = {n["id"]: n for n in d["nodes"]}
    props = sorted((x for x in seen if x.startswith("proposal/")), key=lambda x: (not x[9:].isdigit(), int(x[9:]) if x[9:].isdigit() else 0, x))
    return [{"proposal": by[x]["name"], "label": by[x].get("label")} for x in props if x in by]


def deploys(d, entries, machine, since=None):
    """The deploys view: each environment's deploys that moved since since or are still open, and the operations waiting
    on it, from the ops entries the partition's main level's host wrote and the landings (ops.environments), each
    carried bolt with its release notes from the page's lineage: [{env, deploys, waiting}], by environment."""
    mine = [e for e in entries if ((e.get("Act") or "").startswith("ops.") and e.get("Host") == machine) or e.get("Act") == "bolt.land"]
    return [{"env": env, "waiting": v["waiting"],
             "deploys": [dict(x, notes=[{"bolt": b, "proposals": release_notes(d, b)} for b in x["bolts"] or []]) for x in v["deploys"]]}
            for env, v in ops.environments(sorted(mine, key=lambda e: (e["At"], e["Id"])), since).items()]


# ------------------------------------------------------------------------------------------------- the fleet

def fleet_data(fleet, bd, logs, now):
    """The fleet page's data: every partition of the teams file in its order, from the board of all of them (bd, as
    board.board_data gives it), each partition's run-record entries (logs, by label) and the time. The record is read in
    its window, the board's (WINDOW). Each partition is where it runs, its kits and their mains, its teams and how busy
    each is, and what needs attention, each with the words the page says of it; nothing here reads (code.7)."""
    since = board.iso(now - WINDOW)
    by = {p["label"]: p for p in bd["partitions"]}
    return {"made": {"at": board.iso(now), "since": since},
            "partitions": [fleet_partition(fleet, by[l], bd["unread"], sorted((e for e in logs.get(l, []) if e["At"] >= since), key=lambda e: (e["At"], e["Id"])), since)
                           for l in fleet["partitions"] if l in by]}


def fleet_partition(fleet, part, unread, entries, since):
    """One partition's block: its label and name, the commit its plan was read at and what could not be read, where it
    runs, its kits, its teams and its attention in the board's words, with how many of its cards are open."""
    l, p = part["label"], fleet["partitions"][part["label"]]
    attention = [board.attention_text(a) for a in part["attention"]]
    mine = {n: why for n, why in unread.items() if n.startswith(f"{l}/main of ") or n == f"the plan of {l}"}
    return {"label": l, "partition": p["partition"], "plan": part["plan"], "unread": mine,
            "commit": f"{l}/main " + (part["plan"][:7] if part["plan"] else "not read" if mine else "not started"),
            "hosts": where(fleet, l, part["hosts"]), "kits": fleet_kits(part, entries, since),
            "teams": [fleet_team(fleet, part, t, entries) for t in p["teams"]],
            "attention": attention, "attention_said": attention or ["nothing needs attention"], "cards": len(part["cards"]),
            "cards_said": board.many(len(part["cards"]), "card open", "cards open")}


def account_said(account):
    return f"account {account}" if account else NO_ACCOUNT


def where(fleet, label, asked):
    """Each host the partition runs on, by name: those the board asked (asked, {host: True or why it did not answer})
    and its main level's, marked answered, not, or not asked when no team of it runs there; under each, in the hosts
    file's order, each session an agent of the partition runs in, the agents in it, its teams, then its main level's
    standing roles, then its dispatcher there, and the account the hosts file gives the session, said when it names
    none (read.2). A session no agent of the partition runs in is left out."""
    p = fleet["partitions"][label]
    ran = crew.partition_hosts(fleet, label)
    out = []
    for h in sorted(set(asked) | {p["machine"]}):
        agents = {}
        for t in p["teams"]:
            if fleet["teams"][t]["machine"] == h:
                agents.setdefault(fleet["teams"][t]["session"], []).append(t)
        if p["machine"] == h:
            for r in crew.MAIN_STANDING:
                agents.setdefault(p["sessions"][r], []).append(f"{label}-{r}")
        if h in ran:
            agents.setdefault(crew.dispatch_place(fleet, label, h), []).append(f"{label}-dispatch-{h}")
        known = fleet["hosts"].get(h, {}).get("sessions", {})
        v = asked.get(h)
        answered = None if h not in asked else v is True
        out.append({"host": h, "answered": answered, "why": None if answered in (True, None) else v,
                    "said": "answered" if answered else "not asked: no team of it runs there" if answered is None else f"did not answer ({v})",
                    "sessions": [{"session": s, "agents": agents[s], "account": known.get(s, {}).get("account") or None,
                                  "account_said": account_said(known.get(s, {}).get("account"))}
                                 for s in dict.fromkeys(list(known) + list(agents)) if s in agents]})
    return out


def fleet_kits(part, entries, since):
    """Each kit the partition's teams build, once, in the order the board takes them (teams by name, each team's kits in
    order), with the teams building it; its main's last landing in the window, the newest bolt.land not refused whose
    Repo is the kit, or none since the window's start; and what is queued for that main: its held bolts that wait to
    land, each with its landing's card open or none, those in construction, and its planned bolts and queued units,
    counted."""
    out = []
    for kit in dict.fromkeys(k for t in sorted(part["teams"], key=lambda t: t["team"]) for k in t["kits"]):
        land = next((e for e in reversed(entries) if e.get("Act") == "bolt.land" and not e.get("Refused") and e.get("Repo") == kit), None)
        landing = land and {"bolt": next((o[5:] for o in land["On"] if o.startswith("bolt/")), None), "head": land.get("Head"), "at": land["At"], "by": land.get("By")}
        mine = [b for b in part["construction"] if b["repo"] == kit]
        waits = [{"bolt": b["bolt"], "card": next((m["card"] for m in b["markers"] if m["card"]), None)} for b in mine if b["state"] == "waits"]
        building = [{"bolt": b["bolt"], "state": b["state"]} for b in mine if b["state"] != "waits"]
        planned = sum(b["repo"] == kit for b in part["bolt_plan"]["planned"])
        queued = sum(u["repo"] == kit for u in part["bolt_plan"]["queue"])
        said = ([f"{w['bolt']} waits to land, " + ("its card open" if w["card"] else "no card open") for w in waits]
                + ([", ".join(b["bolt"] + (f" ({board.state_said(b['state'])})" if board.state_said(b["state"]) else "") for b in building) + " in construction"] if building else [])
                + ([board.many(planned, "bolt planned", "bolts planned")] if planned else [])
                + ([board.many(queued, "unit queued", "units queued")] if queued else []))
        out.append({"kit": kit, "teams": [t["team"] for t in part["teams"] if kit in t["kits"]], "landing": landing, "since": since,
                    "waits": waits, "building": building, "planned": planned, "queued": queued,
                    "said": [landed_said(landing, since), "; ".join(said) or "nothing queued"]})
    return out


def landed_said(landing, since):
    if not landing:
        return f"no landing since {since[:10]}"
    return (f"last landed {landing['bolt']}" + (f" at {landing['head'][:7]}" if landing["head"] else "")
            + f", {landing['at'][:10]} {landing['at'][11:16]}Z" + (f" by {landing['by']}" if landing["by"] else ""))


def running(entries, team):
    """The stages running in a team's slots, {slot: {stage, kind, name, since}}: each slot's newest start not refused,
    a unit's or chore's stage.start or a fix's fix.start or fix.merge naming agent/<team>-<slot>, with no stage.end
    after it, not refused, naming the same stage/ object, or for a fix the same fix/ object, and the same agent. A stage
    started before the entries begin is not seen."""
    out = {}
    for i, e in enumerate(entries):
        act = e.get("Act")
        agent = next((o[6:] for o in e["On"] if o.startswith(f"agent/{team}-")), None)
        if act not in STARTS or e.get("Refused") or not agent:
            continue
        if act == "stage.start":
            obj = next((o for o in e["On"] if o.startswith("stage/")), None)
            if not obj:
                continue
            _, name, stage = obj.split("/", 2)
            kind = "chore" if f"chore/{name}" in e["On"] else "unit"
        else:
            obj = next((o for o in e["On"] if o.startswith("fix/")), None)
            if not obj:
                continue
            name, stage, kind = obj, STARTS[act], "fix"
        ended = any(x.get("Act") == "stage.end" and not x.get("Refused") and obj in x["On"] and f"agent/{agent}" in x["On"] for x in entries[i + 1:])
        slot = agent[len(team) + 1:]
        out.pop(slot, None)
        if not ended:
            out[slot] = {"stage": stage, "kind": kind, "name": name, "since": e["At"]}
    return out


def work_named(s):
    return ("chore " if s["kind"] == "chore" else "") + s["name"]


def fleet_team(fleet, part, name, entries):
    """A team: its host, session and account, its kits; each bolt it holds with its pips, how many units have merged
    and its state; each slot at work on a stage (running), holding a unit, chore or fix of its bolt with no stage
    running, or free; how many are at work; and what its conductor waits on: the stages running, else a bolt that waits
    to land, on the user's word, with its landing's card open or none, else nothing."""
    t = fleet["teams"][name]
    account = fleet["hosts"].get(t["machine"], {}).get("sessions", {}).get(t["session"], {}).get("account") or None
    bolts = [b for b in part["construction"] if b["team"] == name]
    run, held = running(entries, name), {}
    for b in bolts:
        for u in b["units"]:
            if u["slot"]:
                held.setdefault(u["slot"], {"kind": u["kind"], "name": u["unit"], "stage": u["stage"]})
        for f in b["fixes"]:
            if f["slot"]:
                held.setdefault(f["slot"], {"kind": "fix", "name": f["fix"], "stage": "merged" if f["merged"] else None})
    slots = []
    for n in range(1, t["units"] + 1):
        s = f"unit-{n}"
        if s in run:
            slots.append(dict(run[s], slot=s, state="work", said=f"{s} at work: {run[s]['stage']} of {work_named(run[s])}"))
        elif s in held:
            h = held[s]
            slots.append(dict(h, slot=s, state="held", said=f"{s} holding {work_named(h)}" + (f" ({h['stage']})" if h["stage"] else "") + ", no stage running"))
        else:
            slots.append({"slot": s, "state": "free", "said": f"{s} free"})
    work = [s for s in slots if s["state"] == "work"]
    landing = next((b for b in bolts if b["state"] == "waits"), None)
    if work:
        waits = {"on": "stages", "stages": [f"{s['stage']} of {work_named(s)}" for s in work]}
        waits["said"] = f"waits on {board.many(len(work), 'stage', 'stages')}: " + ", ".join(waits["stages"])
    elif landing:
        card = next((m["card"] for m in landing["markers"] if m["card"]), None)
        waits = {"on": "landing", "bolt": landing["bolt"], "card": card,
                 "said": "waits on the landing, on the user's word, " + ("its card open" if card else "no card open")}
    else:
        waits = {"on": "nothing", "said": "waits on nothing"}
    return {"team": name, "host": t["machine"], "session": t["session"], "account": account, "account_said": account_said(account),
            "kits": [k["name"] for k in crew.kits_of(t)],
            "bolts": [{"bolt": b["bolt"], "repo": b["repo"], "state": b["state"], "pips": board.pips(b["units"]), "merged": board.merged(b),
                       "said": " · ".join(x for x in (f"{board.pips(b['units'])} {b['bolt']}", board.merged(b), board.state_said(b["state"])) if x)}
                      for b in bolts],
            "holds": "" if bolts else "holds no bolt", "slots": slots, "at_work": len(work),
            "at_work_said": f"{len(work)} of {t['units']} slots at work", "waits": waits}


def fleet_links(path, labels):
    """Where each partition's page is from the fleet page written to path (a PurePath), in the layout of its own file:
    index.html, as swancloud's board serves it beside the partitions' pages, puts each at <label>.html; page.html,
    crew's own, at <label>/page.html. None for any other name, since crew cannot tell where the pages are (read.1)."""
    layout = {"index.html": "{}.html", "page.html": "{}/page.html"}.get(path.name)
    return {l: layout.format(l) for l in labels} if layout else None


def linked(d, links):
    """Each partition of the fleet's data given its page's link, and each team its dock there (#dock=team:<name>, the
    address the dock keeps); none where links is None."""
    for p in d["partitions"]:
        p["link"] = links[p["label"]] if links else None
        for t in p["teams"]:
            t["link"] = f"{p['link']}#dock=team:{t['team']}" if p["link"] else None


# ------------------------------------------------------------------------------------------------- the file

def header(made):
    """As of when and which commit the page was drawn from; both commits, the run record's and the plan's, should the
    board's read have found the branch at another (read.1)."""
    plan_tip = made.get("plan")
    return (f"as of {made['at'][:10]} {made['at'][11:16]}Z · {made['label']}/main {made['commit'][:7]}"
            + (f" for the run record, {plan_tip[:7]} for the board and labels" if plan_tip and plan_tip != made["commit"] else ""))


def beside(path, label, other):
    """Where other's page is from this one, written to path (a PurePath), in the layout of this page's own file: its
    folder named label (crew's, <label>/page.html) puts other's in ../<other>/, its file named label (<label>.html, as
    swancloud's board serves them) names other's <other> with the same suffix, and both swap both. None when neither
    names label, since crew cannot tell where the other pages are (read.1)."""
    folder, named = path.parent.name == label, path.stem == label
    if not (folder or named):
        return None
    return (f"../{other}/" if folder else "") + (f"{other}{path.suffix}" if named else path.name)


def fleet_back(path, label):
    """Where the fleet page is from this partition's page, written to path (a PurePath), in the layout of its own file:
    index.html beside a page whose file alone is named label, as swancloud's board serves them; ../page.html from a
    page.html in a folder named label, crew's own. None for any other layout, since crew cannot tell where the fleet
    page is (read.1)."""
    folder, named = path.parent.name == label, path.stem == label
    if named and not folder:
        return "index.html"
    if folder and path.name == "page.html":
        return "../page.html"
    return None


def nav(labels, label, path):
    """A link to the fleet page in the layout of this page's file, path (fleet_back), where it can be told; then the
    partitions in the teams file's order, this page's marked current and each other a link to its page in that layout
    (beside), or named without a link when that layout names no partition."""
    def part(l):
        if l == label:
            return f'<span class="part" aria-current="page">{html.escape(l)}</span>'
        link = beside(path, label, l)
        return f'<a class="part" href="{html.escape(link)}">{html.escape(l)}</a>' if link else f'<span class="part">{html.escape(l)}</span>'
    back = fleet_back(path, label)
    return (f'<a class="part fleet" href="{html.escape(back)}" title="every partition">fleet</a>' if back else "") + "".join(part(l) for l in labels)


def embedded(d):
    """The data as JSON a script block can hold, every < escaped so nothing in it can end the block."""
    text = json.dumps(d, separators=(",", ":"), ensure_ascii=False)
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def template(path, *marks):
    """A template's text, refused unless it holds each placeholder once."""
    text = path.read_text()
    for mark in marks:
        text.count(mark) == 1 or fail(f"{path} must hold its placeholder {mark} once")
    return text


def render(d, path):
    """The page to be written to path: the template with the partitions' links in their placeholder, and the data in
    its own (embedded)."""
    return template(TEMPLATE, DATA, PARTITIONS).replace(PARTITIONS, nav(d["partitions"], d["label"], path)).replace(DATA, embedded(d))


def render_fleet(d):
    """The fleet page: its template with the fleet's data in its placeholder (embedded)."""
    return template(FLEET, DATA).replace(DATA, embedded(d))


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
    d["deploys"] = deploys(d, entries, fleet["partitions"][label]["machine"], stamp)
    d["partitions"], d["label"] = list(fleet["partitions"]), label
    if a.json:
        print(json.dumps(d, indent=1))
        return
    out = pathlib.Path(a.out).expanduser().absolute() if a.out else record.ROOT / label / "page.html"
    write(out, render(d, out))
    print(out)
    print(header(d["made"]))
    if any(beside(out, label, l) is None for l in d["partitions"] if l != label):
        print(f"the other partitions are not linked: {out} is neither named {label}.html nor in a folder {label}")
    if not d["entries"]:
        print("nothing has been recorded" + (f" since {stamp}" if stamp else ""))
    for h, why in missing.items():
        print(f"{h} did not answer: {why}")


def fleet_page(fleet, a):
    """crew page --fleet: one read of every partition in the teams file, the read crew board makes of all of them, made
    into the fleet page and written whole to --out or beside the partitions' pages; its path printed, then as of when
    and which commit of each plan, each host or plan of a partition that did not answer, and that the partitions are
    not linked when the file's name gives no layout. Nothing is refused for a silent host (read.3)."""
    labels = list(fleet["partitions"])
    read = board.flow_read(fleet, labels)
    now = datetime.datetime.now(datetime.timezone.utc)
    bd = board.board_data(fleet, labels, read, now)
    d = fleet_data(fleet, bd, read.get("logs", {}), now)
    out = pathlib.Path(a.out).expanduser().absolute() if a.out else record.ROOT / "page.html"
    links = fleet_links(out, labels)
    linked(d, links)
    if a.json:
        print(json.dumps(d, indent=1))
        return
    write(out, render_fleet(d))
    print(out)
    for p in d["partitions"]:
        print(f"as of {d['made']['at'][:10]} {d['made']['at'][11:16]}Z · {p['commit']}")
    for p in bd["partitions"]:
        for x in p["attention"]:
            if x["what"] in ("host", "plan", "signals"):
                print(f"{p['label']}: {board.attention_text(x)}")
    if links is None:
        print(f"the partitions are not linked: {out} is named neither index.html nor page.html")


def main(argv):
    plan.need_recutils()
    sub, argv = (argv[0], argv[1:]) if argv else (None, [])
    sub == "page" or fail(f"page.py runs crew page, not {sub}")
    ap = argparse.ArgumentParser(prog="crew page")
    ap.add_argument("label", nargs="?")
    ap.add_argument("--fleet", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--since")
    ap.add_argument("--json", action="store_true", help=argparse.SUPPRESS)  # the page's data, for tests: nothing is written
    a = ap.parse_args(argv)
    if a.fleet:
        a.label is None or fail(f"crew page takes a partition's label or --fleet, not both: {a.label} and --fleet")
        a.since is None or fail("crew page --fleet takes no --since: the fleet page reads the run record in the board's window")
        return fleet_page(crew.load(), a)
    a.label or fail("crew page takes a partition's label, or --fleet for every partition")
    page(crew.load(), a)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
