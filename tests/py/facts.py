"""Facts for the logic tier, built as crew's readers return them, so a case reads as its scenario."""
import hashlib

ALICE = ("Alice", "alice@example.com")


def commit(subject, author=ALICE, body="", sha=None):
    """A commit as plan.commits_beyond reads it: sha, short sha, subject, and who (author name, email, message).
    Two commits with the same subject, author and body are the same commit replayed; give each its own sha."""
    message = subject + ("\n\n" + body if body else "") + "\n"
    sha = sha or hashlib.sha1(f"{subject}{author}{body}{id(message)}".encode()).hexdigest()
    return {"sha": sha, "short": sha[:7], "subject": subject, "who": (author[0], author[1], message)}


def replayed(c, subject=None, author=None):
    """The commit replayed with a new sha: the same message and author unless reworded or re-authored."""
    return commit(subject or c["subject"], author or c["who"][:2])


import datetime
import pathlib

START = datetime.datetime(2026, 10, 12, 10, 0, 0, tzinfo=datetime.timezone.utc)
BEFORE, AFTER = START - datetime.timedelta(minutes=1), START + datetime.timedelta(minutes=1)


def owed(stage, name="a", slot="unit-1", obj="", start=START, team="swb-1"):
    """A stage crew owes an end, as plan.Owed reads its line in the team's stages file; its start entry's id begins with
    the start's second, or holds none when start is None."""
    import plan
    eid = (start.strftime("%Y%m%dT%H%M%SZ") + "-mac-studio-1-1") if start else "unreadable"
    return plan.Owed({"name": team}, [slot, name, stage, eid, obj])


def saved(name):
    """A report or proof file saved since the stage began, as newest_saved returns it."""
    return pathlib.Path("/reports") / name


def plan_of(bolts=None, units=None):
    """A plan.rec as plan.Plan reads it: bolts as {bolt: team or None}, units as {unit: bolt or None}, in order."""
    import plan
    text = "%rec: Bolt\n\n" + "".join(f"Bolt: {b}\n" + (f"Team: {t}\n" if t else "") + "\n" for b, t in (bolts or {}).items())
    text += "%rec: Unit\n\n" + "".join(f"Unit: {u}\n" + (f"Bolt: {b}\n" if b else "") + "\n" for u, b in (units or {}).items())
    return plan.Plan(text)


def at(minutes):
    """A run-record time, minutes after START."""
    return (START + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def constructed(unit, sha, minutes=0):
    """A run-record entry: unit's construct delivered its change at sha."""
    return {"Act": "stage.end", "Ended": "delivered", "On": [f"stage/{unit}/construct", f"unit/{unit}"],
            "Delivered": f"unit/{unit}@{sha}", "At": at(minutes)}


def reviewed(n, units, minutes=0):
    """A run-record entry: batch n delivered, holding each (unit, team, sha)."""
    return {"Act": "review.batch", "Batch": str(n), "Units": " ".join(f"{u}:{t}@{s}" for u, t, s in units), "At": at(minutes), "On": []}


def card_closed(key, card, minutes=0, state="closed", refused=None):
    """A run-record entry: the card under key closed, as crew records it once the user answered it ("closed"), sent its
    reading session ("withdrawn"), or as Pending You lost it to its owner ("lost"); refused, a close Pending You refused."""
    return {"Act": "card.close", "Key": key, "Card": card, "State": None if refused else state, "Refused": refused, "At": at(minutes),
            "On": [key]}


def told(minutes=0):
    """A run-record entry: the planner was told a batch is due."""
    return {"Act": "batch.due", "At": at(minutes), "On": []}


FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio", "review": {"every": 5, "hours": 4}, "teams": ["swb-1", "swb-2"]}},
         "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": "chuck-herdr-alpha"},
                   "swb-2": {"name": "swb-2", "label": "wldn", "machine": "chuck-herdr-alpha"}},
         "hosts": {}}


KITS = ("switchboard-kit", "breadboard-kit")


def plan_text(bolts=(), units=()):
    """plan.rec text with its descriptors: bolts as (name, repo, team or None), units as (name, repo, bolt or None,
    [after...]), in order, a fifth "chore" making it a chore, whose words are "Chore <name>."."""
    text = "%rec: Bolt\n%key: Bolt\n\n" + "".join(
        f"Bolt: {b}\nRepo: {r}\nGoal: Goal of {b}.\n" + (f"Team: {t}\n" if t else "") + "\n" for b, r, t in bolts)
    text += "%rec: Unit\n%key: Unit\n\n" + "".join(
        f"Unit: {u}\nRepo: {r}\n" + (f"Bolt: {b}\n" if b else "") + ("Kind: chore\n" if kind else "")
        + (f"Intent: Chore {u}.\n" if kind else f"Intent: Unit {u}.\n") + "".join(f"After: {x}\n" for x in after) + "\n"
        for u, r, b, after, *kind in units)
    return text


class FactsWrite:
    """A plan.Write over a plan in memory: its files given, each host's runner as given (runners, {host: its reading as
    runner.host_read gives it}), and a refusal for a missing bolt or unit that reads no git for the commit that
    removed it."""

    def __new__(cls, text, files=None, runners=None, label="wldn"):
        import plan
        import runner

        class W(plan.Write):
            def text(self, path):
                return self.files.get(path)

            def gone(self, kind, name, word=None):
                plan.fail(f"no {word or kind.lower()} {name} in {self.label}/main")

            def runner_of(self, host):
                return runner.of_host(runners or {}, self.label, host)
        w = W(None, label, None, plan.Plan(text))
        w.files = dict(files or {})
        return w


def known(w, stages=None, taken=(), n=None, chores_taken=(), fleet=None):
    """A plan command's reads as a logic case gives them (plan.Reads): each unit's or chore's stage as given, else ready;
    a name free unless the kit's main holds a change (taken) or a chore (chores_taken) by it; work a held bolt needs
    ahead of its first unit or chore not merged."""
    import plan

    class Known(plan.Proposed):
        direct = n is None

        def of(self, name):
            st = (stages or {}).get(name, "ready")
            return {"stage": st, "worktree": f"/kit/places/{name}" if st not in ("ready", "waiting", "unknown") else None,
                    "open": [], "head": None, "why": "its host did not answer" if st == "unknown" else None}

        def stages(self, p, bolts):
            return self

        def stage(self, p, name):
            return self.of(name)

        def free(self, label, kit, names):
            for x in names:  # by the decision name_free makes, on the changes and chores the kit's main is given to hold
                why = plan.name_taken(kit, x, taken, chores_taken)
                not why or plan.fail(why)

        def first_open(self, p, bolt):
            return next((u.name() for u in p.work_of(bolt) if self.of(u.name())["stage"] not in ("merged", "landed")), None)

        def kit(self, kit):
            kit in KITS + tuple(k["name"] for t in (fleet or FLEET)["teams"].values() for k in t.get("kits", [])) or plan.fail(
                f"no team of {self.label} builds {kit}, so no plan holds its work")
            return self.label
    return Known(fleet or FLEET, w.label, w, n)


def apply(w, *dos, ctx=None):
    """Each Do line, as a proposal holds it, built and applied in order to the write's plan, then crew's own rules
    checked: what plan.apply_all and check_ops do, without recfix's process."""
    import plan
    for do in dos:
        a = plan.do_args(w.label, do)
        plan.OPS[(a.cmd, a.sub)](ctx or known(w, n=1), a).change(w)
    plan.check(w.plan)
    return w


def units_of(w, bolt=None, repo=None):
    """The plan's units and chores in a bolt, or in a repo's queue, in order."""
    return [u.name() for u in w.plan.work() if (u.get("Bolt") == bolt if bolt else not u.get("Bolt") and u.get("Repo") == repo)]


CREW_KIT = {"name": "crew", "repo": "afterthought/crew"}


def crossed_fleet(**settings):
    """The fleet of madswan's teams on deneb building crew (afterthought/crew), each with its Flume setting: crw-4
    crossed in stream madswan unless given otherwise, crw-5 on today's path."""
    settings = dict({"crw-4": "madswan", "crw-5": False}, **settings)
    return {"partitions": {"madswan": {"label": "madswan", "teams": sorted(settings)}}, "hosts": {},
            "teams": {n: {"name": n, "flume": f, "label": "madswan", "machine": "deneb", "kit": CREW_KIT, "kits": [CREW_KIT]}
                      for n, f in settings.items()}}


def crossed_fleet_read(**settings):
    """madswan's fleet (crossed_fleet), crew's kit with its main checkout on deneb, so a kit read there (crew_read) can
    say what main and a bolt hold."""
    fleet = crossed_fleet(**settings)
    for t in fleet["teams"].values():
        t["kit"] = dict(CREW_KIT, main="/crew/main", dir="/crew")
        t["kits"] = [t["kit"]]
    return fleet


def crew_read(main=(), chores=(), bolts=None):
    """A survey of deneb (plan.survey's answer) holding crew's kit as read there: main's changes and chores, and each
    bolt in bolts, {bolt: its facts over a bolt holding nothing yet, its head d…d with no verdict}."""
    empty = {"exists": True, "at": "origin/bolt/x", "changes": [], "archived": [], "open": {}, "chores": [], "worktree": None,
             "head": "d" * 40, "head_at": "2026-10-31T12:00:00Z", "verdict": ""}
    k = {"ok": True, "main": list(main), "chores": list(chores), "places": {}, "chore_places": {}, "fixes": [],
         "bolts": {b: dict(empty, at=f"origin/bolt/{b}", **facts) for b, facts in (bolts or {}).items()}}
    return {"deneb": {"ok": True, "kits": {"/crew/main": k}}}


def flume_plan(bolts=(), work=()):
    """madswan's plan.rec text, every bolt and piece of work in crew: bolts as (name, team or None, Path or None), work as
    (name, bolt or None, [after], kind, [sources]), kind "chore" or "unit", each in order and intended `Build <name>.`."""
    out = "%rec: Bolt\n%key: Bolt\n\n" + "".join(
        f"Bolt: {b}\nRepo: crew\nGoal: Goal of {b}.\n" + (f"Team: {t}\n" if t else "") + (f"Path: {p}\n" if p else "") + "\n"
        for b, t, p in bolts)
    return out + "%rec: Unit\n%key: Unit\n\n" + "".join(
        f"Unit: {u}\nRepo: crew\n" + (f"Bolt: {b}\n" if b else "") + ("Kind: chore\n" if kind == "chore" else "")
        + f"Intent: Build {u}.\n" + "".join(f"After: {x}\n" for x in after) + "".join(f"Source: {x}\n" for x in sources) + "\n"
        for u, b, after, kind, sources in work)


FLUME = pathlib.Path(__file__).parent / "flume-0.3.6"


def ran(launched=None, held=(), host="deneb", label="madswan"):
    """A host's runner as crew reads it from its branch (runner.host_read): each launch in launched, {request's number:
    the flume 0.3.6 status fixture its place stands at (tests/py/flume-0.3.6/<name>.json)}, answered launched and
    carried in places.rec at the fixture's own place, and each in held answered held."""
    import json
    import plan
    import runner
    answers, places = "", ""
    for n, name in (launched or {}).items():
        status = json.loads((FLUME / f"{name}.json").read_text())
        where = status["status"]["places"][0]["place"].split("@")[0]
        answers += f"\nRequest: {n}\nOutcome: launched\nPlace: {where}\nAt: 2026-10-31T12:01:00Z\n"
        places += f"\nRequest: {n}\nPlace: {where}\nAt: 2026-10-31T12:02:00Z\nStatus: {json.dumps(status)}\n"
    answers += "".join(f"\nRequest: {n}\nOutcome: held\nAt: 2026-10-31T12:01:00Z\n" for n in held)
    files = {"runner.rec": plan.Plan(runner.RUNNER + f"\nHost: {host}\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n"),
             "answers.rec": plan.Plan(runner.ANSWERS + answers), "places.rec": plan.Plan(runner.PLACES + places)}
    return {host: runner.host_read(label, host, "5e1f0c2a" + "0" * 32, files, {})}


def launched(bolts, work=(), team="crw-4", fleet=None, held=()):
    """madswan's plan (flume_plan) with each bolt in bolts given to team through Flume and its work launched as a give
    launches it (plan.reach_places), and each of held, (bolt, its team), given to that team on today's path: (the plan,
    requests.rec's records as the writes leave them). The requests name their writer: set CREW_AGENT first."""
    import plan
    import runner
    fleet = fleet or crossed_fleet()
    w = FactsWrite(flume_plan([(b, None, None) for b in [*bolts, *(b for b, _ in held)]], work), label="madswan")
    for b, t in held:
        w.plan.bolt(b).set("Team", t)
    for b in bolts:
        w.plan.bolt(b).set("Team", team)
        w.plan.bolt(b).set("Path", "flume", after="Team")
        plan.reach_places(fleet, w, b, fleet["teams"][team])
    return w.plan, plan.Plan(w.files.get("requests.rec") or runner.REQUESTS).recs("Request")
