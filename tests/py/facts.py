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


# Every role of a partition stands, as a teams file below version 4 reads (crew.load).
STANDING = {r: False for r in ("design", "planner", "reviewer", "ops", "operator")}
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio", "review": {"every": 5, "hours": 4}, "teams": ["swb-1", "swb-2"],
                                 "flume": STANDING}},
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
    """A plan.Write over a plan in memory: its files given, and a refusal for a missing bolt or unit that reads no
    git for the commit that removed it."""

    def __new__(cls, text, files=None):
        import plan

        class W(plan.Write):
            def text(self, path):
                return self.files.get(path)

            def gone(self, kind, name, word=None):
                plan.fail(f"no {word or kind.lower()} {name} in {self.label}/main")
        w = W(None, "wldn", None, plan.Plan(text))
        w.files = dict(files or {})
        return w


def known(w, stages=None, taken=(), n=None, chores_taken=()):
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
            kit in KITS or plan.fail(f"no team of {self.label} builds {kit}, so no plan holds its work")
            return self.label
    return Known(FLEET, "wldn", w, n)


def apply(w, *dos, ctx=None):
    """Each Do line, as a proposal holds it, built and applied in order to the write's plan, then crew's own rules
    checked: what plan.apply_all and check_ops do, without recfix's process."""
    import plan
    for do in dos:
        a = plan.do_args("wldn", do)
        plan.OPS[(a.cmd, a.sub)](ctx or known(w, n=1), a).change(w)
    plan.check(w.plan)
    return w


def units_of(w, bolt=None, repo=None):
    """The plan's units and chores in a bolt, or in a repo's queue, in order."""
    return [u.name() for u in w.plan.work() if (u.get("Bolt") == bolt if bolt else not u.get("Bolt") and u.get("Repo") == repo)]
