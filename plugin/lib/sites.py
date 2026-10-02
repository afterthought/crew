#!/usr/bin/env python3
"""sites.py: crew sites [<label>] [--json]

For each host where a partition's teams run, each bolt and its worktrees (the bolt's own, each unit's and each
fix's), with the URL of the dev server running in it, if any. Each host is read once. A server is found among the
host's portless routes and matched to its worktree by the name devurl gives that worktree: swancloud's naming,
never crew's own. The URL is the one to open from where crew runs: the server's local name on its own host; on
another, its dev.swancloud.net name when its host publishes, shown on a box marked to open from a Mac, since a
box cannot resolve those names."""
import argparse, json, os, pathlib, sys

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew, plan  # noqa: E402
from crew import Refusal, fail  # noqa: E402


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
    held = [(b.get("Team"), b.name()) for _, _, _, p in found if p for b in p.bolts() if b.get("Team") in fleet["teams"]]
    sv = plan.survey(fleet, held, sites=True)
    out = {"from": here, "partitions": [], "unread": errors}
    for l in labels:
        hosts = {h: {"host": h, "reachable": True, "error": None, "bolts": []} for h in crew.partition_hosts(fleet, l)}
        for pl, repo, tip, p in found:
            if pl != l or not p:
                continue
            for b in p.bolts():
                t = fleet["teams"].get(b.get("Team"))
                if not t:
                    continue
                h = hosts.setdefault(t["machine"], {"host": t["machine"], "reachable": True, "error": None, "bolts": []})
                entry = {"bolt": b.name(), "team": t["name"], "repo": b.get("Repo"), "worktree": None, "url": None, "note": None,
                         "units": [], "fixes": []}
                h["bolts"].append(entry)
                got = sv.get(t["machine"])
                if not got or not got["ok"]:
                    h.update(reachable=False, error=got["error"] if got else "not read")
                    continue
                k = got["kits"].get(t["kit"]["main"], {})
                if not k.get("ok"):
                    entry["note"] = k.get("error")
                    continue

                def site(path):
                    url, note = url_of(fleet, here, t["machine"], k["sites"].get(path, {}), k.get("routes"))
                    return {"worktree": path, "url": url, "note": note}
                bw = k["bolts"].get(b.name(), {}).get("worktree")
                if bw:
                    entry.update(site(bw))
                for u in p.units_of(b.name()):
                    pl_ = k["places"].get(u.name())
                    if pl_:
                        entry["units"].append(dict(site(pl_["path"]), unit=u.name()))
                for f in k["fixes"]:
                    if f["bolt"] == b.name():
                        entry["fixes"].append(dict(site(f["path"]), fix=f["fix"]))
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
                lines += [f"    {b['bolt']}  ({b['team']})" for b in h["bolts"]]
                continue
            lines.append(f"  {h['host']}" + ("" if h["bolts"] else "  no bolt in flight"))
            for b in h["bolts"]:
                mark = lambda x: show(x) + ("  (open from a Mac)" if x["note"] == "open from a Mac" and x["url"] else "")
                lines.append(f"    {b['bolt']:<38} {rel(b['worktree']):<44} {mark(b) if b['worktree'] else (b['note'] or 'no worktree')}  [{b['team']}]")
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
    label = a.label or os.environ.get("CREW_LABEL")
    labels = [crew.partition_of(fleet, label)["label"]] if label else list(fleet["partitions"])
    data = sites(fleet, labels)
    print(json.dumps(data, indent=1) if a.json else text(data))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
