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


def told(minutes=0):
    """A run-record entry: the planner was told a batch is due."""
    return {"Act": "batch.due", "At": at(minutes), "On": []}
