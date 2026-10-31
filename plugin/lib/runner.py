"""crew's side of the runner's interface (flywheel-runner core.2): how a team crosses to Flume, one team at a time
(record 0050 parts 2 and 3, roles.8), and the decisions over a crossed team's work.

A team's path is read from its setting in teams.json (crew.load's `flume`, False or a Flume stream) and the bolts the
plan gives it, a bolt given while the team was crossed marked `Path: flume`: today's, crossed or due (team_path). A due
team is given no new bolt (due_refusal); its bolts go on as they were given until each lands or is dropped, and the
landing or drop that leaves it holding none of its old path makes its path its setting's. A crossed team runs no
standing agent and has no slots: its conductor and ops are due an end (cross_due), and every standing-agent or slot
command of it is refused (crossed_refusal).

Each is a function of plain facts (code.7); plan.py, crew.py and hold.py read the facts and act on what they decide.
This module imports nothing outside the standard library and crew's own modules (code.1)."""

# How a bolt was given, by its Path on the plan's Bolt record, as crew says it.
GIVEN = {"flume": "through Flume", None: "on today's path"}


def team_path(setting, held):
    """A team's path (Decision 2 of teams-cross-to-flume-as-their-bolts-land), from its setting (crew.load's `flume`,
    False or a stream's name) and the Path of each bolt the plan gives it ("flume", or None for one given on today's
    path): ("today", None) while its setting is off and it holds no bolt given through Flume; ("crossed", None) while
    its setting names a stream and it holds no bolt given on today's path, or none at all; and ("due", "cross") or
    ("due", "back") while the setting and a bolt it holds disagree, due to cross while the setting names a stream and
    due back while it is off."""
    if setting is False:
        return ("due", "back") if "flume" in held else ("today", None)
    return ("due", "cross") if any(p != "flume" for p in held) else ("crossed", None)


def path_of(plan, t):
    """A team's path (team_path) as a plan has it: t's setting and the Path of each bolt the plan gives t."""
    return team_path(t["flume"], [b.get("Path") for b in plan.bolts() if b.get("Team") == t["name"]])


def due_refusal(team, path, held):
    """Why a give hands a due team no bolt (Decision 2), or None for a team that is not due: held is each bolt the team
    holds as (name, its Path), each named with the path it was given on, and the give is refused until those of its old
    path have landed or been dropped, since nothing moves a bolt from one path to the other and a team crosses empty."""
    kind, way = path
    if kind != "due":
        return None
    groups = {}
    for name, p in held:
        groups.setdefault(p, []).append(name)
    holds = " and ".join(f"{' and '.join(names)}, given {GIVEN[p]}" for p, names in groups.items())
    old = groups.get(None if way == "cross" else "flume", [])
    towards = "due to cross to Flume" if way == "cross" else "due back to today's path"
    return (f"{team} is {towards}, so it is given no bolt now: it holds {holds}, and is given its next bolt once "
            + " and ".join(old) + (" has" if len(old) == 1 else " have") + " landed or been dropped")


def cross_due(path, up):
    """What a team's crossing owes its standing agents (Decision 3), from facts: its path (team_path) and its standing
    roles that are up. Returns (the roles due an end, whether the crossing is whole): once it has crossed, every role
    up is due an end, never a restart, and the crossing is whole once none is up, when the act that ended the last
    closes its workspaces and records team.cross. A team not crossed owes nothing."""
    if path[0] != "crossed":
        return [], False
    return list(up), not up


def crossed_refusal(team, path, stream, host, what):
    """What crew says refusing crew <what> of a team (Decision 15), or None when the team has not crossed: a crossed
    team runs no conductor, ops or slot, its work running in Flume places on its host, which crew bolts shows."""
    if path[0] != "crossed":
        return None
    return (f"{team} has crossed to Flume: its work runs in Flume places on {host}, in stream {stream}, and crew bolts shows "
            f"them; it runs no conductor, ops or slot, so crew {what} has nothing of it to act on")
