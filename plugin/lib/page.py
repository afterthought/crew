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
import argparse, datetime, html, json, math, os, pathlib, sys, tempfile

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

def fleet_data(fleet, bd, logs, usage, now):
    """The fleet page's data: every partition of the teams file in its order, from the board of all of them (bd, as
    board.board_data gives it), each partition's run-record entries (logs, by label), the use the hosts published (usage,
    as usage_files reads it) and the time. The record is read in its window, the board's (WINDOW). Each partition is
    where it runs, its kits and their mains, its teams and how busy each is, and what needs attention; each subscription
    its use, who read it and how long ago, and the sessions and partitions on it; and each published file crew could not
    read, with why: each with the words the page says of it; nothing here reads (code.7)."""
    since = board.iso(now - WINDOW)
    by = {p["label"]: p for p in bd["partitions"]}
    parts = [fleet_partition(fleet, by[l], bd["unread"], sorted((e for e in logs.get(l, []) if e["At"] >= since), key=lambda e: (e["At"], e["Id"])), since)
             for l in fleet["partitions"] if l in by]
    readings, unread = usage_checked(usage)
    read = [h for h in usage if h not in {u["host"] for u in unread}]
    said = ("no host has published any use" if not usage else f"as published by {', '.join(read)}" if read else "no published use could be read")
    return {"made": {"at": board.iso(now), "since": since},
            "subscriptions": {"said": said, "items": subscriptions(fleet, readings, {t["team"]: t for p in parts for t in p["teams"]}, now)},
            "unread_usage": unread, "partitions": parts}


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
    placed = agents_in(fleet, label)
    out = []
    for h in sorted(set(asked) | {p["machine"]}):
        agents = {s: v for (x, s), v in placed.items() if x == h}
        known = fleet["hosts"].get(h, {}).get("sessions", {})
        v = asked.get(h)
        answered = None if h not in asked else v is True
        out.append({"host": h, "answered": answered, "why": None if answered in (True, None) else v,
                    "said": "answered" if answered else "not asked: no team of it runs there" if answered is None else f"did not answer ({v})",
                    "sessions": [{"session": s, "agents": agents[s], "account": known.get(s, {}).get("account") or None,
                                  "account_said": account_said(known.get(s, {}).get("account"))}
                                 for s in dict.fromkeys(list(known) + list(agents)) if s in agents]})
    return out


def agents_in(fleet, label):
    """Which of a partition's agents crew starts in which session, {(host, session): [agent]}: its teams, each in its
    host's session, then its main level's standing roles in theirs on its host, then its dispatcher on each host its
    teams run on (crew.dispatch_place)."""
    p = fleet["partitions"][label]
    out = {}
    for t in p["teams"]:
        out.setdefault((fleet["teams"][t]["machine"], fleet["teams"][t]["session"]), []).append(t)
    for r in crew.MAIN_STANDING:
        out.setdefault((p["machine"], p["sessions"][r]), []).append(f"{label}-{r}")
    for h in crew.partition_hosts(fleet, label):
        out.setdefault((h, crew.dispatch_place(fleet, label, h)), []).append(f"{label}-dispatch-{h}")
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
    address the dock keeps), and each subscription's partitions the same link as their blocks; none where links is
    None."""
    for p in d["partitions"]:
        p["link"] = links[p["label"]] if links else None
        for t in p["teams"]:
            t["link"] = f"{p['link']}#dock=team:{t['team']}" if p["link"] else None
    for s in d["subscriptions"]["items"]:
        for p in s["partitions"]:
            p["link"] = links[p["label"]] if links else None


# ------------------------------------------------------------------------------------------------- the subscriptions

# A reading's windows, under Claude Code's own names for its /usage data (rate_limits), each with the page's name for it:
# the two every reading shows, then the weekly ones by model, model_scoped's after them under the server's own names.
USE = (("five_hour", "five-hour"), ("seven_day", "seven-day"))
MODELS = (("seven_day_opus", "Opus"), ("seven_day_sonnet", "Sonnet"))


def usage_files(folder):
    """The use the hosts published, one *.json file in folder (a Path) for each host, named for it, by host: {host:
    {file, data}} for a file parsed, {host: {file, why}} for one that could not be opened or is not JSON. A folder that
    is not there holds no file."""
    out = {}
    for f in sorted(folder.glob("*.json")):
        try:
            out[f.stem] = {"file": str(f), "data": json.loads(f.read_text())}
        except OSError as e:
            out[f.stem] = {"file": str(f), "why": f"it could not be opened: {e.strerror or e}"}
        except ValueError as e:
            out[f.stem] = {"file": str(f), "why": f"it is not JSON: {e}"}
    return out


def shown(v):
    """A value as a reason quotes it, cut short."""
    text = json.dumps(v, ensure_ascii=False)
    return text if len(text) <= 40 else text[:39] + "…"


def is_time(at):
    return isinstance(at, str) and "T" in at and board.when(at) is not None


def window_wrong(w):
    """What is wrong with a window, or None: absent or null, or an object whose utilization is a number or null and
    whose resets_at is an ISO time or null."""
    if w is None:
        return None
    if not isinstance(w, dict):
        return f"is not a window: {shown(w)}"
    u = w.get("utilization")
    if u is not None and (isinstance(u, bool) or not isinstance(u, (int, float)) or not math.isfinite(u)):
        return f"has a utilization that is not a number: {shown(u)}"
    if w.get("resets_at") is not None and not is_time(w["resets_at"]):
        return f"has a resets_at that is not an ISO time: {shown(w['resets_at'])}"
    return None


def reading_wrong(r):
    """What is wrong with a reading, or None: an account crew takes as a name (code.4), an at that is an ISO time, and
    either the host's words for why it could not read (unread) or its windows, each absent, null or a window, and
    model_scoped a list of windows each with its display_name."""
    if not isinstance(r, dict):
        return f"it is not an object: {shown(r)}"
    if not isinstance(r.get("account"), str) or not crew.NAME.fullmatch(r["account"]):
        return f"its account is not a name crew takes: {shown(r.get('account'))}"
    if not is_time(r.get("at")):
        return f"its at is not an ISO time: {shown(r.get('at'))}"
    if r.get("unread") is not None and not (isinstance(r["unread"], str) and r["unread"].strip()):
        return f"its unread is not the host's words: {shown(r['unread'])}"
    for k, _ in USE + MODELS:
        why = window_wrong(r.get(k))
        if why:
            return f"its {k} {why}"
    ms = r.get("model_scoped")
    if ms is not None and not isinstance(ms, list):
        return f"its model_scoped is not a list: {shown(ms)}"
    for m in ms or []:
        if not isinstance(m, dict) or not isinstance(m.get("display_name"), str) or not m["display_name"].strip():
            return f"its model_scoped holds a window with no display_name: {shown(m)}"
        why = window_wrong(m)
        if why:
            return f"its model_scoped window {m['display_name']} {why}"
    return None


def file_wrong(host, data):
    """What is wrong with a host's published file, or None: an object whose host is the file's name and whose readings
    are a list, each of the shape (reading_wrong)."""
    if not isinstance(data, dict):
        return f"it is not an object: {shown(data)}"
    if data.get("host") != host:
        return f"its host is {shown(data.get('host'))}, not {host}, the file's name"
    if not isinstance(data.get("readings"), list):
        return f"its readings are not a list: {shown(data.get('readings'))}"
    for i, r in enumerate(data["readings"], 1):
        why = reading_wrong(r)
        if why:
            return f"reading {i}: {why}"
    return None


def usage_checked(files):
    """The published use checked against its shape before any of it is used (read.2), from the files read (usage_files):
    a file that could not be read or is not of the shape is unread as a whole, named with what is wrong, and the other
    files' readings kept (read.3). Returns (readings [{host, account, at, unread, windows}], unread [{host, file, why}]),
    by host, each reading's at in UTC and its windows under their own names, None where the reading gives none."""
    readings, unread = [], []
    for host, f in files.items():
        why = f.get("why") or file_wrong(host, f["data"])
        if why:
            unread.append({"host": host, "file": f["file"], "why": why})
            continue
        readings += [{"host": host, "account": r["account"], "at": board.iso(board.when(r["at"])), "unread": r.get("unread"),
                      "windows": {k: r.get(k) for k in [k for k, _ in USE + MODELS] + ["model_scoped"]}}
                     for r in f["data"]["readings"]]
    return readings, unread


def age_said(at, now):
    """How long before now a reading was made, in whole minutes, hours and minutes past sixty."""
    m = int((now - board.when(at)).total_seconds() // 60)
    if m < 1:
        return "under a minute ago"
    h, m = divmod(m, 60)
    return (f"{h} h " if h else "") + (f"{m} min " if m or not h else "") + "ago"


def reset_said(at, now):
    """When a window resets, in the page's own form: its time alone on the page's day, else with its date."""
    t = board.when(at).astimezone(datetime.timezone.utc)
    return t.strftime("%H:%MZ" if t.date() == now.astimezone(datetime.timezone.utc).date() else "%Y-%m-%d %H:%MZ")


def window(key, name, w, now):
    """A window as published: its percentage rounded to a whole number and when it resets, or that it is not given when
    the reading leaves it out or gives no figure; pct, its number for the bar alone, clamped to 0 to 100."""
    u, resets = (w or {}).get("utilization"), (w or {}).get("resets_at")
    if u is None:
        return {"window": key, "name": name, "utilization": None, "pct": None, "resets_at": resets, "said": f"{name} not given"}
    return {"window": key, "name": name, "utilization": u, "pct": max(0, min(100, u)), "resets_at": resets,
            "said": f"{name} {math.floor(u + 0.5)}%" + (f", resets {reset_said(resets, now)}" if resets else "")}


def figures(r, now):
    """A made reading's figures: the five-hour and seven-day windows, always; then by model Opus, Sonnet and each of
    model_scoped in its order, each only where the reading gives it."""
    w = r["windows"]
    return {"windows": [window(k, n, w[k], now) for k, n in USE],
            "models": [window(k, n, w[k], now) for k, n in MODELS if w[k] is not None]
                      + [window("model_scoped", m["display_name"], m, now) for m in w["model_scoped"] or []]}


def reading_said(r, now):
    return (f"{r['host']} could not read {age_said(r['at'], now)}: {r['unread']}" if r["unread"]
            else f"{r['host']} read {age_said(r['at'], now)}")


def subscriptions(fleet, readings, teams, now):
    """Every Claude subscription, by name: each account a session of the hosts file names and each a reading is of
    (usage_checked). Each shows the figures of its newest reading made, which host read it and how long before now; each
    other reading, its host's and how long ago, or the host's words for why it could not read; else that its use could
    not be read, or that no host has published it. Nothing is made of the figures but their words (record 0038 §5)."""
    named = {s["account"] for h in fleet["hosts"].values() for s in h.get("sessions", {}).values() if s.get("account")}
    out = []
    for a in sorted(named | {r["account"] for r in readings}):
        mine = sorted((r for r in readings if r["account"] == a), key=lambda r: (-board.when(r["at"]).timestamp(), r["host"]))
        shown = next((r for r in mine if not r["unread"]), None)
        if shown:
            state, said = "read", f"read by {shown['host']} {age_said(shown['at'], now)}"
        else:
            state, said = ("unread", "its use could not be read") if mine else ("none", "no host has published its use")
        out.append(dict({"account": a, "state": state, "said": said, "host": shown and shown["host"], "at": shown and shown["at"]},
                        **(figures(shown, now) if shown else {"windows": [], "models": []}),
                        others=[{"host": r["host"], "at": r["at"], "unread": r["unread"], "said": reading_said(r, now)} for r in mine if r is not shown],
                        **on_subscription(fleet, a, teams)))
    return out


def on_subscription(fleet, account, teams):
    """The sessions and partitions on a subscription, beside its use and computed from nothing of it: each session the
    hosts file gives account, by host and on each in the file's order, with crew's agents in it across every partition
    (agents_in), teams first, then main levels' roles, then dispatchers, and each team's slots at work and its
    conductor's wait as its partition's block says them (teams, by name, as fleet_team gives them); and the partitions
    with an agent in one of them, in the teams file's order, each linked as its block is (linked)."""
    labels = list(fleet["partitions"])
    placed = {l: agents_in(fleet, l) for l in labels}
    sessions, on = [], set()
    for h in sorted(fleet["hosts"]):
        for s, v in fleet["hosts"][h].get("sessions", {}).items():
            if v.get("account") != account:
                continue
            here = [(l, a) for l in labels for a in placed[l].get((h, s), [])]
            here.sort(key=lambda x: 0 if x[1] in fleet["teams"] else 2 if x[1] == f"{x[0]}-dispatch-{h}" else 1)
            agents = [a for _, a in here]
            on |= {l for l, _ in here}
            sessions.append({"host": h, "session": s, "agents": agents, "said": ", ".join(agents) or "runs no crew agent",
                             "teams": [{"team": t, "at_work_said": teams[t]["at_work_said"], "waits_said": teams[t]["waits"]["said"]}
                                       for t in agents if t in teams]})
    return {"sessions": sessions, "sessions_said": None if sessions else "no session of herdr-hosts is on it",
            "partitions": [{"label": l, "link": None} for l in labels if l in on],
            "partitions_said": None if on else "no partition's agents run on it"}


# ------------------------------------------------------------------------------------------------- the docks

# A lineage node's kind as a dock's key names it, a chore's a unit's (plan.11); an agenda item has no dock.
DOCK = {"signals": "signal", "proposal": "proposal", "unit": "unit", "chore": "unit", "bolt": "bolt"}
# A lineage node's kind as a dock names it in a row.
KIND = {"signals": "signal", "agenda": "agenda item", "proposal": "proposal", "unit": "unit", "chore": "chore", "bolt": "bolt"}


def key_of(node):
    """A lineage node's id as the key of its dock (signals/x to signal:x, chore/x to unit:x), or None for a kind that
    has none, an agenda item's. The key names the item, not where the page draws it."""
    kind, _, name = node.partition("/")
    return f"{DOCK[kind]}:{name}" if kind in DOCK and name else None


def deploy_key(env, x):
    """A deploy's key: its environment, its commit and when it was offered or started, which ops.environments gives
    every deploy one of and never changes once set, since one commit can be offered to an environment more than once."""
    return f"deploy:{env}/{x['to']}/{x['offered'] or x['started']}"


def fix_name(bolt, fix):
    """A fix's own name, its branch fix/<bolt>/<name> without the part its key already says."""
    return fix[len(f"fix/{bolt}/"):] if fix.startswith(f"fix/{bolt}/") else fix


def dock(kind, title, tail=(), form=None, facts=(), markers=(), parts=(), history=(), attention=None):
    """A dock's page, plain data the page's script draws whatever its kind: its head's form and line of what it is, its
    facts [label, text] and [label, text, key] for one that opens another dock, its markers as the board's, its parts
    {title, rows [{text, key?}]} and its history, entry ids oldest first. A fact or part the data does not hold is left
    out, and nothing is said blank (read.2)."""
    return {"kind": kind, "form": form, "title": title, "tail": " · ".join(t for t in tail if t),
            "facts": [[f[0], f[1]] + ([f[2]] if len(f) > 2 and f[2] else []) for f in facts if f[1] not in (None, "")],
            "markers": list(markers or []), "attention": attention,
            "parts": [{"title": t, "rows": [r if r.get("key") else {"text": r["text"]} for r in rows]} for t, rows in parts if rows],
            "history": list(history)}


def word_said(x):
    """The user's word on a deploy, as the deploys view says it."""
    if x["answer"] == "waiting":
        return "waits on your word: hold its card to deploy"
    by = (x["word"] or {}).get("by") or "no one named"
    if x["answer"] == "replaced":
        return (f"approved by {by}, {x['word']['at']}, then the word went to a newer offer before it was deployed" if x["word"]
                else "not answered, and replaced by a newer offer")
    if x["answer"] == "unasked":
        return "deployed with no word asked in the record (an auto environment's, or offered before its window)"
    return f"approved by {by}, {x['word']['at']}" if x["word"] else None


def deploy_said(x):
    """Where a deploy stands, in the words of its stamp on the board."""
    if x["answer"] == "waiting":
        return "waits on your word"
    if x["answer"] == "replaced":
        return "replaced, never deployed" if x["word"] else "replaced, unanswered"
    if x["ended"]:
        return x["outcome"] or "ended"
    return "deploying" if x["started"] else "approved"


def wait_said(w):
    """Where an operation waiting on an environment stands, as the board's Operation lane says it."""
    return (f"handed to {w['agent'] or w['doer']}" if w["state"] == "handed" else "failed" if w["state"] == "failed"
            else "waits on you" if w["doer"] == "user" else f"waits for {w['agent'] or w['doer'] or 'its doer'}")


def docks(d, fleet, label):
    """Every item of the page's board and deploys, and every team, given the key of its dock, {key: page}: a signal, a
    proposal, a planned or held bolt and each of its units, a held bolt's fixes, a queued unit, a landing, a deploy and
    an operation waiting on an environment; a team, from the strip; and the Claude account of each team's session, a
    subscription, from the team's dock. Each page is made from the page's data, its lineage and the fleet crew already
    loaded, and nothing else; an item it names is a link only where it has a dock (record 0038, S27, S28). Every page
    names, as its `to`, the agent a word from its dock goes to (word_to)."""
    B, p = d["board"], crew.partition_of(fleet, label)
    nodes = {n["id"]: n for n in d["nodes"]}
    read_at = plan.utc(B["read_at"])

    # Every item's key first, so a page links only what has a dock.
    for s in B["inception"]["signals"]:
        s["dock"] = f"signal:{s['signal']}"
    for x in B["bolt_plan"]["proposals"]:
        x["dock"] = f"proposal:{x['proposal']}"
    for b in B["bolt_plan"]["planned"] + B["construction"]:
        b["dock"] = f"bolt:{b['bolt']}"
        for u in b["units"]:
            u["dock"] = f"unit:{u['unit']}"
        for f in b.get("fixes", []):
            f["dock"] = f"fix:{b['bolt']}/{fix_name(b['bolt'], f['fix'])}"
    for u in B["bolt_plan"]["queue"]:
        u["dock"] = f"unit:{u['unit']}"
    for o in B["operation"]:
        o["dock"] = f"landing:{o['bolt']}"
    # A deploy is one dock from the Operation lane and from the deploys view: its release notes are the view's, its
    # markers the lane's.
    deps, waits = {}, {}
    for e in B.get("environments", []) + d["deploys"]:
        for x in e["deploys"]:
            x["dock"] = deploy_key(e["env"], x)
            deps.setdefault(x["dock"], {"env": e["env"], "markers": []}).update({k: v for k, v in x.items() if k != "markers"})
            deps[x["dock"]]["markers"] = x.get("markers") or deps[x["dock"]]["markers"]
        for w in e["waiting"]:
            w["dock"] = f"operation:{e['env']}/{w['key']}"
            waits.setdefault(w["dock"], {"env": e["env"], "markers": []}).update({k: v for k, v in w.items() if k != "markers"})
            waits[w["dock"]]["markers"] = w.get("markers") or waits[w["dock"]]["markers"]
    sessions = {}
    for t in B["teams"]:
        t["dock"] = f"team:{t['team']}"
        ft = fleet["teams"][t["team"]]
        account = fleet["hosts"].get(ft["machine"], {}).get("sessions", {}).get(ft["session"], {}).get("account")
        sessions[t["team"]] = (ft["machine"], ft["session"], account)
    keys = {x["dock"] for x in walk(B, d["deploys"])} | {f"subscription:{a}" for _, _, a in sessions.values() if a}

    def link(key):
        return key if key in keys else None

    def named(node):
        """A lineage node as a row: its kind, its name and its label, a link where it has a dock."""
        n = nodes[node]
        return {"text": f"{KIND[n['kind']]} {n['name']}" + (f" · {n['label']}" if n.get("label") else ""), "key": link(key_of(node))}

    def joined(node, way):
        """The rows of what the lineage joins to a node: those it leads to, those it came from, or both."""
        return [named(e["to"] if e["from"] == node else e["from"]) for e in d["edges"]
                if (e["from"] == node and way in ("out", "both")) or (e["to"] == node and way in ("in", "both"))]

    def unit_row(u):
        """A unit in a bolt's dock, as its link in the ledger's chain: its stage, and its tasks while coded or verified."""
        tasks = f" {u['tasks'][0]}/{u['tasks'][1]}" if u.get("tasks") and u.get("stage") in ("code", "verify") else ""
        return {"text": ("chore " if u.get("kind") == "chore" else "") + f"{u['unit']} · {stage_said(u.get('stage'))}{tasks}", "key": link(u["dock"])}

    def deploy_row(x):
        return {"text": f"deploy {x['to'][:7]} to {x['env']}", "key": link(x["dock"])}

    def carrying(bolt):
        return [deploy_row(x) for x in deps.values() if bolt in (x.get("bolts") or [])]

    landings = {o["bolt"]: o for o in B["operation"]}
    out = {}
    for s in B["inception"]["signals"]:
        node = f"signals/{s['signal']}"
        age = plan.age(board.when(s["at"]), read_at) if board.when(s["at"]) else None
        who = s["captured_by"] or "no one named"
        out[s["dock"]] = dock("signal", words(s["first"] or s["signal"]), (s["kind"], f"captured by {who}", age and f"{age} ago"),
                              facts=[("signal", s["signal"]), ("kind", s["kind"]), ("captured by", who), ("captured", s["at"]),
                                     ("home", s["home"])],
                              parts=[("assertion", [{"text": nodes[node]["label"]}] if nodes.get(node, {}).get("label") else
                                      [{"text": s["first"]}] if s["first"] else []),
                                     ("linked", joined(node, "both") if node in nodes else []),
                                     ("teams", [{"text": t, "key": link(f"team:{t}")} for t in s.get("teams", [])])],
                              history=d["histories"].get(node, []))
    for x in B["bolt_plan"]["proposals"]:
        node = f"proposal/{x['proposal']}"
        out[x["dock"]] = dock("proposal", x["case"] or f"proposal {x['proposal']}",
                              (f"proposal {x['proposal']}", x["by"] and f"by {x['by']}", x["opened"] and f"opened {x['opened']}"), form="sheet",
                              facts=[("waiting on", ", ".join(f"{t}-conductor" for t in x["waiting"]))], markers=x["markers"],
                              parts=[("teams", [{"text": t, "key": link(f"team:{t}")} for t in x["teams"]]),
                                     ("units and bolts", joined(node, "out") if node in nodes else [])],
                              history=d["histories"].get(node, []))
    for b in B["bolt_plan"]["planned"] + B["construction"]:
        held = "team" in b
        run = (f"{b['team']} on {b['host']}" if b["host"] else b["team"]) if held else "planned, no team"
        landed = landings.get(b["bolt"])
        out[b["dock"]] = dock("bolt", b["bolt"], (b["repo"], run, held and stage_said(b["state"])), form="ledger",
                              facts=[("goal", b["goal"]), ("repository", b["repo"]), ("team", b.get("team"), link(f"team:{b.get('team')}")),
                                     ("host", b.get("host")), ("state", stage_said(b["state"]) if held else "planned"), ("server", b.get("url"))],
                              markers=b.get("markers"),
                              attention="every unit has landed, and the bolt is still in the plan" if held and b["state"] == "landed" else None,
                              parts=[("units", [unit_row(u) for u in b["units"]]),
                                     ("fixes", [{"text": f"{f['fix']} · {'merged' if f['merged'] else 'not merged'}", "key": link(f["dock"])}
                                                for f in b.get("fixes", [])]),
                                     ("landed", [{"text": f"landed {landed['at']}" + (f" by {landed['by']}" if landed["by"] else ""),
                                                  "key": link(landed["dock"])}] if landed else []),
                                     ("carried by", carrying(b["bolt"]))],
                              history=d["histories"].get(f"bolt/{b['bolt']}", []))
        for u in b["units"]:
            out[u["dock"]] = unit_dock(u, b, nodes, d["histories"], link, f"in {b['bolt']}" if held else f"planned in {b['bolt']}")
        for f in b.get("fixes", []):
            out[f["dock"]] = dock("fix", f["fix"], (f"fix of {b['bolt']}",),
                                  facts=[("state", "merged" if f["merged"] else "not merged"), ("slot", f["slot"]), ("worktree", f["worktree"]), ("server", f["url"])],
                                  parts=[("bolt", [{"text": b["bolt"], "key": link(b["dock"])}])])
    for u in B["bolt_plan"]["queue"]:
        out[u["dock"]] = unit_dock(u, None, nodes, d["histories"], link, "queued")
    for o in B["operation"]:
        out[o["dock"]] = dock("landing", o["bolt"], ("landed " + o["at"] + (f" by {o['by']}" if o["by"] else ""),), form="record",
                              facts=[("bolt", o["bolt"], link(f"bolt:{o['bolt']}")), ("landed", o["at"]), ("by", o["by"]),
                                     ("team", o["team"], link(f"team:{o['team']}"))],
                              parts=[("units", [{"text": n, "key": link(f"unit:{n}")} for n in o["units"]]), ("carried by", carrying(o["bolt"]))],
                              history=[e["Id"] for e in sorted(d["entries"].values(), key=lambda e: (e["At"], e["Id"]))
                                       if e.get("Act") == "bolt.land" and f"bolt/{o['bolt']}" in e["On"] and not e.get("Refused")])
    for key, x in deps.items():
        out[key] = deploy_dock(x, link)
    for key, w in waits.items():
        out[key] = dock("operation", w["key"], (f"on {w['env']}", wait_said(w)), form="record",
                        facts=[("state", wait_said(w)), ("environment", w["env"]), ("commit", w["to"]), ("held", "for the user's word" if w.get("held") else None),
                               ("gate", w.get("gate")), ("at", w["at"])],
                        markers=w["markers"], parts=[("text", [{"text": w["text"]}] if w["text"] else []), ("note", [{"text": w["note"]}] if w["note"] else [])])
    for t in B["teams"]:
        host, session, account = sessions[t["team"]]
        mine = [b for b in B["construction"] if b.get("team") == t["team"]]
        out[t["dock"]] = dock("team", t["team"], (f"{t['kit']} on {t['host']}",),
                              facts=[("kits", ", ".join(t["kits"])), ("host", host), ("session", session),
                                     ("account", account or NO_ACCOUNT, link(f"subscription:{account}") if account else None)],
                              parts=[("bolts held", [{"text": b["bolt"], "key": link(b["dock"])} for b in mine] or [{"text": "holds no bolt"}]),
                                     ("landings", [{"text": f"{o['bolt']} · landed {o['at']}", "key": link(o["dock"])} for o in B["operation"] if o["team"] == t["team"]]),
                                     ("signals captured", [{"text": words(s["first"] or s["signal"]), "key": link(s["dock"])}
                                                           for s in B["inception"]["signals"] if t["team"] in s.get("teams", [])]),
                                     (f"environment {host}", [deploy_row(x) for x in deps.values() if x["env"] == host]
                                      + [{"text": f"{w['key']} · {wait_said(w)}", "key": link(k)} for k, w in waits.items() if w["env"] == host])])
    for account in sorted({a for _, _, a in sessions.values() if a}):
        rows = [{"text": f"{t} · {h} session {s}", "key": link(f"team:{t}")} for t, (h, s, a) in sessions.items() if a == account]
        rows += [{"text": f"{label}-{role} · {p['machine']} session {s}"} for role, s in p["sessions"].items()
                 if fleet["hosts"].get(p["machine"], {}).get("sessions", {}).get(s, {}).get("account") == account]
        out[f"subscription:{account}"] = dock("subscription", account, ("Claude account",), parts=[("sessions on it", rows)])
    for key, pg in out.items():
        pg["to"] = word_to(key, d, label)
    return out


def word_to(key, d, label):
    """The agent a dock's word goes to, by its item's kind (crew.ROLE_OF, record 0038 §3): for a bolt, a unit or a fix,
    the conductor of the team holding the bolt it is or belongs to as the board gives it, else the partition's operator;
    for any other kind, its role's agent of the partition."""
    kind, _, name = key.partition(":")
    role = crew.ROLE_OF.get(kind, "operator")
    if role != "conductor":
        return f"{label}-{role}"
    B = d["board"]
    team = next((b.get("team") for b in B["bolt_plan"]["planned"] + B["construction"]
                 if (kind == "bolt" and b["bolt"] == name) or (kind == "fix" and b["bolt"] == name.partition("/")[0])
                 or (kind == "unit" and any(u["unit"] == name for u in b["units"]))), None)
    return f"{team}-conductor" if team else f"{label}-operator"


def walk(B, deploys):
    """Every item of the board and the deploys view that has a dock, each once for each place it is drawn."""
    yield from B["inception"]["signals"]
    yield from B["bolt_plan"]["proposals"]
    for b in B["bolt_plan"]["planned"] + B["construction"]:
        yield b
        yield from b["units"]
        yield from b.get("fixes", [])
    yield from B["bolt_plan"]["queue"]
    yield from B["operation"]
    for e in B.get("environments", []) + deploys:
        yield from e["deploys"]
        yield from e["waiting"]
    yield from B["teams"]


def words(text, most=64):
    """A text's first words, cut at a word under most characters, as a dock's title."""
    text = " ".join((text or "").split())
    return text if len(text) <= most else text[:most].rsplit(" ", 1)[0] + "…"


def stage_said(stage):
    """A stage as a dock says it: one crew could not read, or none, is unknown (read.1)."""
    return stage if stage and stage != "unknown" else "unknown"


def unit_dock(u, b, nodes, histories, link, where):
    """A unit's or chore's dock: in a held bolt's ledger, planned in one no team holds, or queued, its head a slip's."""
    kind = "chore" if u.get("kind") == "chore" else "unit"
    node = f"{kind}/{u['unit']}"
    return dock(kind, u["unit"], (kind, where), form="slip" if b is None else None,
                facts=[("bolt", b and b["bolt"], b and link(b["dock"])), ("repository", (b or u).get("repo")),
                       ("stage", stage_said(u.get("stage")) if b else "queued"),
                       ("tasks", f"{u['tasks'][0]} of {u['tasks'][1]} tasks" if u.get("tasks") else None), ("slot", u.get("slot")),
                       ("worktree", u.get("worktree")), ("server", u.get("url")), ("sources", ", ".join(u.get("sources") or []))],
                parts=[("intent", [{"text": nodes[node]["label"]}] if nodes.get(node, {}).get("label") else [])],
                history=histories.get(node, []))


def deploy_dock(x, link):
    """A deploy's dock, as the deploys view says it: its commits, the user's word, its steps and checks, its outcome, the
    bolts it carried with their changes' proposals as its release notes, and the steps after it."""
    if x.get("bolts") is None:
        carried = [{"text": f"can't be read: {x['bolts_why']}"}]
    else:
        carried = []
        for n in x.get("notes") or [{"bolt": b, "proposals": []} for b in x["bolts"]]:
            carried.append({"text": f"bolt {n['bolt']}", "key": link(f"landing:{n['bolt']}") or link(f"bolt:{n['bolt']}")})
            carried += [{"text": f"proposal {q['proposal']}" + (f" · {q['label']}" if q["label"] else ""), "key": link(f"proposal:{q['proposal']}")}
                        for q in n["proposals"]]
        carried = carried or [{"text": "no landing"}]
    return dock("deploy", f"deploy {x['to'][:7]}", (f"on {x['env']}", deploy_said(x)),
                form="record",
                facts=[("environment", x["env"]), ("to", x["to"]), ("from", x["from"] if x["from"] not in (None, "", "none") else "nothing deployed"),
                       ("word", word_said(x)), ("offered", x["offered"]), ("started", x["started"]), ("ended", x["ended"]), ("outcome", x["outcome"])],
                markers=x["markers"],
                parts=[("steps", [{"text": " ".join(s for s in (s["step"], s["outcome"]) if s)} for s in x["steps"]]),
                       ("checks", [{"text": " ".join(t for t in (c.get("name"), c.get("state"), c.get("verdict") and f"({c['verdict']} than before)",
                                                                  c.get("detail")) if t)} for c in x.get("checks") or []]),
                       ("carried", carried),
                       ("after the deploy", [{"text": " · ".join(t for t in (a["key"], a["doer"], a["state"], a["note"]) if t)} for a in x.get("after") or []])])


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
    d["docks"] = docks(d, fleet, label)
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
    into the fleet page with the use the hosts published in this host's ~/.local/state/crew/usage/, and written whole to
    --out or beside the partitions' pages; its path printed, then as of when and which commit of each plan, each host or
    plan of a partition that did not answer, that the partitions are not linked when the file's name gives no layout,
    each published file that could not be read, and that no use is published when the folder holds none. Nothing is
    refused for a silent host or an unreadable file (read.3)."""
    labels = list(fleet["partitions"])
    read = board.flow_read(fleet, labels)
    now = datetime.datetime.now(datetime.timezone.utc)
    bd = board.board_data(fleet, labels, read, now)
    folder = record.ROOT / "usage"
    usage = usage_files(folder)
    d = fleet_data(fleet, bd, read.get("logs", {}), usage, now)
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
    for u in d["unread_usage"]:
        print(f"the use published in {u['file']} could not be read: {u['why']}")
    if not usage:
        print(f"no subscription's use is published in {folder}")


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
