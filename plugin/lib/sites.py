#!/usr/bin/env python3
"""sites.py: crew sites [<label>] [--json]

For each of a partition's hosts, its main level's and each its runners answer on (plan.partition_hosts), each started
bolt whose work runs there, as the runner that took it reported (plan.bolt_at), with no dev server, saying so, since its
work runs in Flume's places, until the runner reports a place's addresses (crew-sites, _open.md). Each host is read
once, for whether it answers (read.3).
A server is found among the host's portless routes and matched to its worktree by the name devurl gives that
worktree: swancloud's naming, never crew's own. The URL is the one to open from where crew runs: the server's local
name on its own host; on another, its dev.swancloud.net name when its host publishes, shown on a box marked to open
from a Mac, since a box cannot resolve those names."""
import argparse, json, os, pathlib, sys

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew, plan  # noqa: E402
from crew import Refusal, fail  # noqa: E402


# What crew sites says of a started bolt: its places are Flume's, where crew finds no server, until the runner reports
# a place's addresses from Flume's run record (record 0043; _open.md).
FLUME_PLACES = "its work runs in Flume's places, whose servers crew does not show yet"


def url_of(fleet, here, host, site, routes):
    """(url, note) for a worktree's server, or (None, why) when there is none to open from here."""
    if routes is None:
        return None, "portless did not answer"
    name = (site.get("here") or "").split("://", 1)[-1].rsplit(".", 1)[0] if site.get("here") else None
    if not name:
        return None, site.get("error") or "devurl gave no name"
    running = next((r for r in routes if r["name"] == name), None)
    if not running:
        return None, None
    if host == here:
        return running["url"], None
    if site.get("tailnet"):
        return site["tailnet"], None if fleet["hosts"].get(here, {}).get("kind") == "darwin" else "open from a Mac"
    return None, f"running, but {host} does not publish its dev servers"


def sites(fleet, labels):
    here = crew.this_host()
    found, errors = [], {}
    found = plan.plans(fleet, labels, errors)
    runs = plan.rail_runs(found)
    at = {(l, b.name()): t for l, _, _, p in found if p and l in runs for b in p.bolts() if plan.started(b)
          for t in [plan.known_at(fleet, l, b, runs[l])] if t}
    sv = plan.survey(fleet, [(t, bolt) for (_, bolt), t in at.items()], sites=True)
    out = {"from": here, "partitions": [], "unread": errors}
    for l in labels:
        hosts = {h: {"host": h, "reachable": True, "error": None, "bolts": []} for h in plan.partition_hosts(fleet, l)}
        for pl, repo, tip, p in found:
            if pl != l or not p:
                continue
            for b in p.bolts():
                t = at.get((l, b.name()))
                if not t:
                    continue
                h = hosts.setdefault(t["machine"], {"host": t["machine"], "reachable": True, "error": None, "bolts": []})
                entry = {"bolt": b.name(), "repo": b.get("Repo"), "worktree": None, "url": None, "note": None, "units": [], "fixes": []}
                h["bolts"].append(entry)
                got = sv.get(t["machine"])
                if not got or not got["ok"]:
                    h.update(reachable=False, error=got["error"] if got else "not read")
                    continue
                entry["note"] = FLUME_PLACES
        out["partitions"].append({"label": l, "hosts": [hosts[h] for h in sorted(hosts)]})
    return out


def text(data):
    lines = []
    show = lambda x: x["url"] or (f"({x['note']})" if x["note"] else "no server running")
    rel = lambda path: "/".join(path.split("/")[-2:]) if path else "-"
    for p in data["partitions"]:
        lines.append(p["label"])
        for h in p["hosts"]:
            if not h["reachable"]:
                lines.append(f"  {h['host']}  did not answer ({h['error']}); its bolts, from the plan:")
                lines += [f"    {b['bolt']}  ({b['repo']})" for b in h["bolts"]]
                continue
            lines.append(f"  {h['host']}" + ("" if h["bolts"] else "  no bolt in flight"))
            for b in h["bolts"]:
                mark = lambda x: show(x) + ("  (open from a Mac)" if x["note"] == "open from a Mac" and x["url"] else "")
                lines.append(f"    {b['bolt']:<38} {rel(b['worktree']):<44} {mark(b) if b['worktree'] else (b['note'] or 'no worktree')}  [{b['repo']}]")
                for u in b["units"] + b["fixes"]:
                    lines.append(f"      {u.get('unit') or u.get('fix'):<36} {rel(u['worktree']):<44} {mark(u)}")
    for what, why in data["unread"].items():
        lines.append(f"{what} could not be read: {why}")
    return "\n".join(lines)


def main(argv):
    plan.need_recutils()
    ap = argparse.ArgumentParser(prog="crew sites")
    ap.add_argument("label", nargs="?")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    fleet = crew.load()
    label = a.label or crew.caller_label(fleet)
    labels = [crew.partition_of(fleet, label)["label"]] if label else list(fleet["partitions"])
    data = sites(fleet, labels)
    print(json.dumps(data, indent=1) if a.json else text(data))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
