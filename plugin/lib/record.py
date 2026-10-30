#!/usr/bin/env python3
"""record.py: crew's run record, what crew did, written where it did it.

Every crew command that moves work appends one entry per act, after the act is done, to a recutils file on the host
where it ran: ~/.local/state/crew/<label>/runs/<host>/<YYYY-MM-DD>.rec, one file per UTC day. An entry names who asked
and the Claude session behind them, the act, the objects acted on (On) and those they came from (From), the commit
written if any, and the subject crew composed from the names of things: never text anyone typed. A failed append is
said on standard error and never changes what the command does or how it exits.

crew's PostToolUse hook (plugin/hooks/cards) appends three acts of its own, one for each Pending You card a crew agent
posts (card.post), updates (card.update), or withdraws or closes (card.close): each names the rail row's object in On,
the card's id in Card and the row's key in Key, and nothing written on the card. crew appends the same three for the
cards it raises itself, with why a card's reading could not be opened in Unread, and a fourth, card.reading, for each
try of a batch's or a long proposal's reading made after its card was raised, by crew card session, the batch's wait or
the rail's read: done when it started the reading, refused with crew's own message when it could not.

Each entry reaches the flywheel's branch of its state repository as it is written: the command that appended it
pushes it there, to the same path under runs/<host>/, as a commit of its own from this host, before it goes on. The
branch's file becomes the union by Id of what it had and what the host has, so a host only ever adds to its own files
and a host that is asleep or rebuilt loses nothing it pushed. A push that is refused is said once and changes nothing
the command does; the entry waits in the host's file and goes first with the host's next. Every read, crew events,
crew trace, the batches, the rail, the board and the page, reads the branch alone and asks no host (read.5).

  record.py emit --label L --act A [--on X]... [--from X]... [--commit C]... [--why W] [--refused R] [--field K=V]...
                [--id I]                  append one entry, with the id a commit already names if given; prints its id
  record.py session                       the caller's Claude session as <host>:<id>, what a forwarded command carries
  record.py events [--label L] [--about <object>] [--since <time>] [--follow] [--json]
                                          the entries on the partition's branch, in time order; --follow reads the
                                          branch as this host's cache holds it each time its tip moves, which this
                                          host's writes move at once, and fetches it once a minute where the host's
                                          follower does not, so another host's entries show within the minute
  record.py events --push [--label L]     push what of this host's entries a refused push left, each a commit of its own
  record.py trace <object> [--label L]    one bolt's, unit's, chore's or signal's history, read from the entries alone

An object is a typed name: unit/<unit>, chore/<chore>, bolt/<bolt>, queue/<kit>, signals/<id>, agenda/<n>, team/<team>,
agent/<name>, stage/<unit or chore>/<stage>, fix/<bolt>/<name>, plan/<label>, proposal/<n>, batch/<n> (a review batch of
the partition), and
what a stage delivered in a file of the team's reports folder: report/<file name> and proof/<file name>. A signal is
named by its full id, <capture>/<NN>-<slug>, or its short one, <capture>/<NN>, which is the one signal of that capture
numbered NN."""
import argparse, datetime, itertools, json, os, pathlib, re, signal, sys
# getpass, tempfile and time are imported where they are used, so a command that writes one entry starts without
# them.

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
from crew import Refusal, fail  # noqa: E402

ROOT = pathlib.Path.home() / ".local/state/crew"
# The clock the host's follower (board.py) and crew events --follow fetch a partition's branch on, never faster
# (plan.12's reading of 2026-10-28); crew's tests set CREW_TEST_PERIOD, so no tick of it falls inside a step (tests.8).
PERIOD = 60
DESCRIPTOR = """\
# crew's run record: one entry per act of crew's that moved work, appended by crew on this host and never
# rewritten. Read it with recsel, or with crew events and crew trace.

%rec: Entry
%key: Id
%mandatory: Id At Host By Act
%allowed: Id At Host By Session Act On From Commit Why Refused Result Tasks Head Ended Delivered Observed Chars Amended Took Heads Paths Reached Forecast Batch Units Count Card Key Unread Base Phase Step Outcome Log Rows State Doer Agent When Text Changes Note Repo After Lifted Settle Form Answer Age Split Submission

"""
# Fields beyond the common ones: a stage.end's Result, Tasks, Head, Ended (delivered, short or stopped), Delivered (what
# it delivered, as an object) and Observed, a tell's or a send's Chars, the Amended of a construct's start that marked
# its unit amended, the After units' heads a construct's place Took and a dependent's rebase left out (a forecast's Took), a
# forecast's Heads (the later unit's and the other's, <name>@<sha>; a bolt's against main, bolt/<bolt>@<sha> main@<sha>
# and #<id> for each submission queued on main it meets, or bolt/<bolt>@<sha> alone when sluice gave none), its
# conflicting Paths and how it Reached the later unit (told, prompt or settle) or the conductor (wait), a slot.free's Paths (the
# place of its slot's work the tidy in its command removed, plan.9), a stage start's Forecast (the forecast entries its prompt carries), a review batch's
# Batch (its number) and Units (each unit as <unit>:<team>@<the commit its change was read at>), a batch due's Count, a
# card act's Card (the Pending You card's id), Key (the rail row's card key) and Unread (why its reading could not open,
# crew's own message, on a card's post or change raised without it), a card's close's Answer (what the user answered
# on it, in crew's words made from names alone, cards.answer_said), a landing's Repo (the kit it landed on),
# Head (the commit that kit's main holds afterwards, plan.14), and, for a bolt a team held, its Age (whole minutes from
# its newest give to its landing) and Split (those minutes by holder, `team 200, kit 12, team-or-kit 13, user 125,
# hold 0, nobody 20`, team-or-kit a submission's stay in sluice crew can't split between queued and under test,
# plan.20), a landing's submission's Submission (sluice's number for it, on its bolt.submit from the moment sluice queued
# it, plan.21), a branch.kept's Head (the commit a unit's, chore's or
# fix's branch the tidy kept is at) and Count (its commits whose patch its bolt, or main, lacks, plan.10), crew's own
# order of two units a forecast found in conflict, the unit.after that puts one After the other or the one that Lifted
# it, with the Settle whose end decided it (plan.13), a record.proposed's State (settled in the pane) and Form
# (alternatives, when its card offered them, none of the file's words), and an operation's (ops.py): a deploy's commit
# as Head and the one it comes from as Base, its Phase (start, step or end), a step's Step and Outcome, its Log and the
# suite's Rows; a step's Key, State, Doer, Agent, When, Text, Changes and Note.
EXTRA = ("Result", "Tasks", "Head", "Ended", "Delivered", "Observed", "Chars", "Amended", "Took", "Heads", "Paths", "Reached",
         "Forecast", "Batch", "Units", "Count", "Card", "Key", "Unread", "Base", "Phase", "Step", "Outcome", "Log", "Rows", "State", "Doer", "Agent",
         "When", "Text", "Changes", "Note", "Repo", "After", "Lifted", "Settle", "Form", "Answer", "Age", "Split", "Submission")
LISTS = ("On", "From", "Commit")
# Objects a trace prints but never follows: following them would pull in everything a team or a kit ever did.
UNFOLLOWED = ("agent/", "team/", "queue/", "plan/")
KINDS = ("unit/", "chore/", "bolt/", "queue/", "signals/", "agenda/", "team/", "agent/", "stage/", "fix/", "plan/", "proposal/", "report/",
         "proof/", "batch/", "env/", "host/")

_ids = itertools.count(1)  # each entry's count in this process, safe from threads
_session = ...  # resolved once per process


def who():
    """Who asked: the agent crew started, else the user at this host."""
    import getpass
    return os.environ.get("CREW_AGENT") or f"{getpass.getuser()}@{crew.this_host()}"


def session():
    """The caller's Claude session as <host>:<id>, once per process. A command run again on another host carries it
    in CREW_SESSION, set even when empty; an agent crew started on this host is asked of herdr; the user has none."""
    global _session
    if _session is not ...:
        return _session
    _session = None
    if "CREW_SESSION" in os.environ:
        _session = os.environ["CREW_SESSION"] or None
        return _session
    name = os.environ.get("CREW_AGENT")
    if not name:
        return None
    try:
        fleet = crew.load()
        host, _ = crew.place_of_agent(fleet, name)
    except Refusal:
        return None
    if host != crew.this_host():
        return None
    try:  # from the listing of its session this command reads (crew.Herdr)
        sid = (crew.agent_get(fleet, name, fresh=False) or {}).get("agent_session", {}).get("value")
    except (OSError, AttributeError):
        sid = None
    sid = sid if isinstance(sid, str) else None
    _session = f"{host}:{sid}" if sid else None
    return _session


def path_for(label, host=None, day=None):
    day = day or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    return ROOT / label / "runs" / (host or crew.this_host()) / f"{day}.rec"


def subject(text):
    """A commit's subject as an entry's Why: its first line, without the trailing (agent) every write adds."""
    first = (text or "").strip().split("\n")[0]
    return re.sub(r"\s*\([^()]*\)$", "", first)


def one_line(v):
    return " ".join(str(v).split())


def entry_id(now, host, pid, n):
    """An entry's id: its second, its microsecond, the host, the process and a count, unique without a lock. The
    microsecond orders the entries of one second as they were made, which the process cannot: a process id says
    nothing of when, and wraps (99891, then 352, on mac-studio on 2026-10-19)."""
    return f"{now.strftime('%Y%m%dT%H%M%SZ')}-{now.microsecond:06d}-{host}-{pid}-{n}"


def new_id():
    """A new entry's id, made now (entry_id). A write makes its entry's id before its commit, so the commit can name
    the entry its message describes."""
    return entry_id(datetime.datetime.now(datetime.timezone.utc), crew.this_host(), os.getpid(), next(_ids))


def emit(label, act, on=(), frm=(), commit=(), why=None, refused=None, eid=None, by=None, **extra):
    """Append one entry to the label's run record on this host, in one write; its id, or None when it could not be
    written, which is said on standard error and nothing more. eid is an id made ahead with new_id; by, the role an
    act of crew's own is in the name of, a card of crew's asked as its row's owner (briefs.16), else who asked."""
    if not label:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    host = crew.this_host()
    eid = eid or new_id()
    fields = [("Id", eid), ("At", now.strftime("%Y-%m-%dT%H:%M:%SZ")), ("Host", host), ("By", by or who())]
    if session():
        fields.append(("Session", session()))
    fields.append(("Act", act))
    fields += [("On", o) for o in on if o] + [("From", f) for f in frm if f] + [("Commit", c) for c in commit if c]
    if why:
        fields.append(("Why", why))
    if refused:
        fields.append(("Refused", refused))
    fields += [(k, extra[k]) for k in EXTRA if extra.get(k) not in (None, "")]
    text = "".join(f"{k}: {one_line(v)}\n" for k, v in fields) + "\n"
    path = path_for(label, host, now.date().isoformat())
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            # The descriptor goes in by a link, so a second process can never append before it: link fails on a
            # file that is there, and the file only ever appears whole.
            import tempfile
            fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".new-")
            try:
                os.write(fd, DESCRIPTOR.encode())
                os.close(fd)
                os.link(tmp, path)
            except FileExistsError:
                pass
            finally:
                os.unlink(tmp)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND)
        try:
            os.write(fd, text.encode())
        finally:
            os.close(fd)
    except OSError as e:
        print(f"crew: the run record at {path} could not be written: {e.strerror or e}", file=sys.stderr)
        return None
    reach(label, eid)
    return eid


# ------------------------------------------------------------------------------------- pushed to the branch

def blocks(text):
    """The entries of run-record text as written, {Id: the entry's lines}, descriptors and comments left out."""
    out, cur = {}, []
    for line in text.split("\n") + [""]:
        if line.strip():
            cur.append(line)
            continue
        if cur and not any(l.startswith(("%", "#")) for l in cur):
            eid = next((l[3:].strip() for l in cur if l.startswith("Id:")), None)
            if eid:
                out[eid] = "\n".join(cur) + "\n"
        cur = []
    return out


def mark(label):
    """Where this host notes the newest entry of the label its branch holds from here."""
    return ROOT / label / "runs" / ".carried"


def unpushed(label, at_branch):
    """The host's entries of the label that its branch lacks, oldest first, each (its id, its lines, its day's path on
    the branch, that file's text once it is added), and the newest id looked at. A day's file on the branch becomes the
    union by Id of the branch's entries and the host's, in Id order (record.4), each entry's file holding the entries
    before it in the chain, so each is a commit of its own on the one before. Days before the newest pushed one are not
    looked at. at_branch(path) reads a file at the branch's tip, or None."""
    host = crew.this_host()
    d = ROOT / label / "runs" / host
    try:
        done = mark(label).read_text().strip()
    except OSError:
        done = ""
    since = f"{done[0:4]}-{done[4:6]}-{done[6:8]}" if len(done) >= 8 else ""
    chain, newest = [], None
    for f in sorted(d.glob("*.rec")) if d.is_dir() else []:
        if f.stem < since:
            continue
        mine = blocks(f.read_text())
        if not mine:
            continue
        newest = max([newest or "", *mine])
        path = f"runs/{host}/{f.name}"
        have = blocks(at_branch(path) or "")
        for eid in sorted(set(mine) - set(have)):
            have[eid] = mine[eid]
            chain.append((eid, mine[eid], path, DESCRIPTOR + "\n".join(have[k] for k in sorted(have))))
    return sorted(chain, key=lambda c: c[0]), newest


def entry_message(text, agent):
    """The message of an entry's own commit on the branch, from its lines: runs(<host>): <act> <first On>, refused
    when it records a refusal, then (<agent>), and the Crew-Entry trailer naming it (plan.2). A field the entry lacks
    is left out."""
    f = {}
    for l in text.splitlines():
        m = FIELD.match(l)
        if m:
            f.setdefault(m.group(1), m.group(2).strip())
    words = " ".join(w for w in (f.get("Act"), f.get("On"), "refused" if f.get("Refused") else None, f"({agent})") if w)
    return ("runs" + (f"({f['Host']})" if f.get("Host") else "") + f": {words}\n\nCrew-Entry: {f.get('Id')}\n")


def reach(label, eid=None):
    """Push each entry of this host's record of the label that its branch lacks, oldest first, normally the one just
    written, each a commit of its own and all in one push, by the write every state write takes (read.5, state.1), on
    this host before the command goes on; then note the newest the branch holds from here. Returns how many were
    pushed. With eid, the entry just written, a push that is refused is said once on standard error, naming it, and
    changes nothing else the command does (record.2): the entry stays in the host's file, and its next push takes it
    first. With none, as crew events --push runs it, the refusal is the command's."""
    import plan  # plan.py imports this module; its git layer is only needed here
    where, seen = f"{label}/main", {"n": 0}
    try:
        repo, ref = plan.state_of(crew.load(), label)
        where = f"{ref} of {repo}"
        tip = plan.fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {label}")

        def make(tip):
            chain, seen["newest"] = unpushed(label, lambda path: plan.show(repo, tip, path))
            seen["n"] = len(chain)
            return [({path: text}, entry_message(lines, who())) for _, lines, path, text in chain]
        if make(tip):
            plan.land(repo, ref, None, make)
    except (Refusal, OSError) as e:
        why = " ".join(str(e).split())  # one line, though git's and recfix's own words may span several
        if eid is None:
            fail(f"nothing reached {where}: {why}")
        print(f"crew: entry {eid} did not reach {where}: {why}; {crew.this_host()} keeps it and pushes it with its next entry", file=sys.stderr)
        return None
    mark_carried(label, seen.get("newest"))
    return seen["n"]


def mark_carried(label, newest):
    """Once the branch holds every entry up to newest, start the next push from that day."""
    if not newest:
        return
    try:
        mark(label).parent.mkdir(parents=True, exist_ok=True)
        mark(label).write_text(newest + "\n")
    except OSError as e:
        print(f"crew: could not note what was pushed at {mark(label)}: {e.strerror or e}", file=sys.stderr)


# ----------------------------------------------------------------------------------------------- reading

FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*):\s?(.*)$")


def parse(text):
    """Entries from run-record text, each a dict: On, From and Commit as lists, the other fields as strings.
    Descriptors and comments are skipped."""
    out, cur = [], []
    for line in text.split("\n") + [""]:
        if line.strip():
            cur.append(line)
            continue
        if cur and not any(l.startswith(("%", "#")) for l in cur):
            e = {k: [] for k in LISTS}
            for l in cur:
                m = FIELD.match(l)
                if m:
                    if m.group(1) in LISTS:
                        e[m.group(1)].append(m.group(2))
                    else:
                        e[m.group(1)] = m.group(2)
            if e.get("Id") and e.get("At"):
                out.append(e)
        cur = []
    return out


def on_branch(fleet, label, since_day, tips=None):
    """The entries the label's branch of its state repository holds, from since_day on. tips, when given, is told the
    commit they were read at, {label: sha}, None for a branch not started."""
    import plan  # plan.py imports this module; its git layer is only needed here
    repo, ref = plan.state_of(fleet, label)
    tip = plan.fetch(repo, ref)
    if tips is not None:
        tips[label] = tip
    if not tip:
        return []
    out = []
    for path in plan.paths_at(repo, tip, "runs/"):
        if path.endswith(".rec") and pathlib.PurePath(path).stem >= since_day:
            out += parse(plan.show(repo, tip, path) or "")
    return out


def gather(fleet, labels, since_day, tips=None):
    """Every entry of the labels' run records from since_day on, read from each label's branch alone, sorted by time
    then Id; and each branch that could not be read, {<label>/main: why}. No host is asked for the record (read.5).
    tips, when given, is told the commit each branch was read at, as on_branch tells it."""
    entries, missing = {}, {}
    for l in labels:
        try:
            for e in on_branch(fleet, l, since_day, tips):
                entries.setdefault(e["Id"], e)
        except Refusal as err:
            missing[f"{l}/main"] = str(err)
    return sorted(entries.values(), key=lambda e: (e["At"], e["Id"])), missing


def when(text):
    """--since as (day, stamp): a date, an ISO time, 'today', or a number of days ('3d'); seven days by default."""
    now = datetime.datetime.now(datetime.timezone.utc)
    if not text:
        t = now - datetime.timedelta(days=7)
    elif text == "today":
        t = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif re.fullmatch(r"[0-9]+d", text):
        t = now - datetime.timedelta(days=int(text[:-1]))
    else:
        try:
            t = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            fail(f"--since takes a date (2026-10-06), a time (2026-10-06T14:00:00Z), 'today' or days ('3d'), not {text}")
        t = t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)
        t = t.astimezone(datetime.timezone.utc)
    return t.date().isoformat(), t.strftime("%Y-%m-%dT%H:%M:%SZ")


def line(e, zoe=False):
    """One entry as one line: time, act, who, host, commit, what it acted on and what that came from."""
    at = e["At"]
    commit = ",".join(c.rsplit("@", 1)[-1][:7] for c in e["Commit"]) or "-"
    s = f"{at[5:10]} {at[11:19]}  {e.get('Act', '?'):<13} {e.get('By', '?'):<20} {e.get('Host', '?'):<17}  {commit:<7}  " + " ".join(e["On"])
    if e["From"]:
        s += " ← " + " ".join(e["From"])
    # A stage's end: what the kit read, then how it ended; what it delivered names the head, so the head is not said twice.
    if e.get("Result"):
        s += f" → {e['Result']}" + (f" {e['Tasks']}" if e.get("Tasks") not in (None, "", "-") else "")
        s += f" at {e['Head']}" if e.get("Head") and not e.get("Delivered") else ""
    if e.get("Ended"):
        s += ("," if e.get("Result") else " →") + f" {e['Ended']}" + (f" {e['Delivered']}" if e.get("Delivered") else "")
    if e.get("Repo") and e.get("Head"):
        s += f" → {e['Repo']} main at {e['Head'][:7]}"
    if e.get("Observed"):
        s += f" (observed {e['Observed']})"
    if e.get("Chars"):
        s += f" ({e['Chars']} characters)"
    if e.get("Amended"):
        s += " (amended)"
    if e.get("Paths") and e.get("Act") == "forecast":
        s += f" (conflict on {e['Paths']}" + (f", {e['Reached']}" if e.get("Reached") else "") + ")"
    elif e.get("Paths"):
        s += f" (removed {e['Paths']})"
    if e.get("Forecast"):
        s += f" (carrying {e['Forecast']})"
    if e.get("Count"):
        s += f" ({e['Count']} due)"
    if e.get("Key") or e.get("Card"):
        s += " (card " + " ".join(x for x in (e.get("Key"), e.get("Card")) if x) + ")"
    if e.get("Refused"):
        s += f"  refused: {e['Refused']}"
    if zoe and e.get("Session") and ":" in e["Session"]:
        host, sid = e["Session"].split(":", 1)
        s += f"  zoe {sid} on {host}"
    return s


def labels_for(fleet, label):
    """The partitions a read covers: the one named, else the caller's own, else all of them."""
    if label:
        crew.partition_of(fleet, label)
        return [label]
    own = os.environ.get("CREW_LABEL")
    return [own] if own in fleet["partitions"] else list(fleet["partitions"])


# A signal's object by its short id, signals/<capture>/<NN>, which names the one signal of that capture numbered NN.
SHORT_SIGNAL = re.compile(r"^signals/[^/]+/[0-9]{2}$")


def objects(e):
    """The objects an entry names: in On or From, or as what a stage delivered."""
    return e["On"] + e["From"] + ([e["Delivered"]] if e.get("Delivered") else [])


def meant(o, obj):
    """Whether o is the object obj names: itself, or for a signal's short id, the signal it numbers."""
    return o == obj or (SHORT_SIGNAL.match(obj) is not None and o.startswith(f"{obj}-"))


def names(e, obj):
    """Whether an entry names the object: in On or From, or as what a stage delivered."""
    return any(meant(o, obj) for o in objects(e))


def events(fleet, a):
    labels = labels_for(fleet, a.label)
    if a.push:
        import plan
        for l in labels:
            plan.push_now(fleet, l)
        return
    if a.follow:
        return follow(fleet, labels, a.about)
    day, stamp = when(a.since)
    found, missing = gather(fleet, labels, day)
    out = events_text(found, missing, stamp, a.about, a.json)
    if out:
        print(out)


def events_text(found, missing, stamp, about=None, as_json=False):
    """crew events: the entries gathered at or after stamp, those naming about alone when given, one line each, then
    each branch that could not be read; or the same as JSON."""
    found = [e for e in found if e["At"] >= stamp and (not about or names(e, about))]
    if as_json:
        return json.dumps({"entries": found, "unreachable": missing}, indent=1)
    return "\n".join([line(e) for e in found] + [f"{h} did not answer: {why}" for h, why in missing.items()])


def fresh(seen, entries):
    """What crew events --follow prints next: the entries read whose Id it has not seen, in time order."""
    return sorted((e for e in entries if e["Id"] not in seen), key=lambda e: (e["At"], e["Id"]))


def follow_fetches(label, followed_here, follower, last, now, period=PERIOD):
    """Whether crew events --follow fetches a partition's branch now (plan.12's reading of 2026-10-28): never while the
    host's follower fetches it, the partition being one it follows (followed_here, board.labels_here) while someone
    holds the host's follower lock (follower, board.follower_here: job, tab, or unknown, a holder whose line is not
    written yet), at its start too; else once its own clock is due, period seconds after its last fetch (last, None
    when it has made none, at its start or since a SIGUSR1). A decision on plain facts (code.7)."""
    if label in followed_here and follower != "none":
        return False
    return last is None or now - last >= period


def changed_files(was, now, day):
    """The run-record files a follow reads again at a moved tip: each of the day the follow began or later whose blob is
    not the one it last read ({path: blob} then and now), in order."""
    return sorted(p for p, b in now.items() if p.endswith(".rec") and pathlib.PurePath(p).stem >= day and was.get(p) != b)


def follow(fleet, labels, about):
    """Each entry of the labels as it reaches their branches, one line each, until interrupted. Each second it reads
    each branch's tip as this host's cache holds it, with no process (plan.tip_here), and when the tip moved, reads
    again only the run-record files of the day the follow began or later whose blob changed (changed_files), printing
    what it has not printed (fresh). It fetches a branch only for a partition the host's follower does not fetch, which
    moves the cache itself, as a write on this host does: at its start and then once a minute (follow_fetches); SIGUSR1
    makes its next fetch now. A branch's first read prints nothing, being what was there before. A branch that
    cannot be read is said once, until it reads again. It asks no host for anything (read.5)."""
    import time
    import board  # board.py imports this module; the host's follower's lock and partitions are its
    import plan  # plan.py imports this module; its git layer is only needed here

    def stop(*_):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)
    tick = {"now": False}
    signal.signal(signal.SIGUSR1, lambda *_: tick.update(now=True))
    period, here = int(os.environ.get("CREW_TEST_PERIOD") or PERIOD), crew.this_host()
    day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    seen, said, tips, files, last = {}, {}, {}, {}, {}
    try:
        while True:
            again, tick["now"] = tick["now"], False
            followed, follower, new = set(board.labels_here(fleet, here)), None, []
            for l in labels:
                repo, ref = plan.state_of(fleet, l)
                try:
                    if l in followed:
                        follower = follower or board.follower_here()
                    if follow_fetches(l, followed, follower, None if again else last.get(l), time.monotonic(), period):
                        last[l] = time.monotonic()
                        plan.fetch(repo, ref, fresh=True)
                    tip = plan.tip_here(repo, ref)
                    tip is not None or fail(f"its tip in crew's cache of {repo} can't be read")
                    if l in seen and tip == tips.get(l):
                        continue
                    listing = plan.blobs_at(repo, tip, "runs/") if tip else {}
                    changed = changed_files(files.get(l, {}), listing, day)
                    got = [e for t in plan.cat_file(repo, [listing[p] for p in changed]) for e in parse(t or "")]
                except Refusal as e:
                    why = " ".join(str(e).split())
                    if said.get(l) != why:
                        print(f"{l}/main did not answer: {why}", file=sys.stderr, flush=True)
                    said[l] = why
                    continue
                said.pop(l, None)
                if l in seen:
                    new += fresh(seen[l], got)
                seen[l], tips[l], files[l] = seen.get(l, set()) | {e["Id"] for e in got}, tip, listing
            for e in fresh((), new):
                if not about or names(e, about):
                    print(line(e), flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def followed(obj):
    return not obj.startswith(UNFOLLOWED)


def named_by(entries):
    """The entries naming each object, {object: [entry]}, as names() reads them: one index for many lineages."""
    out = {}
    for e in entries:
        for o in dict.fromkeys(objects(e)):
            out.setdefault(o, []).append(e)
    return out


def lineage(entries, start, index=None):
    """One object's history, the walk crew trace prints and the lineage page shows: every entry naming it, the entries
    of what it came from (an entry's From) and of what came from it (the On of an entry whose From names it), until
    nothing is added; sorted by time, then Id. index, when given, is named_by(entries), made once for many starts."""
    index = named_by(entries) if index is None else index
    objs, chosen = {start}, {}
    while True:
        before = (len(objs), len(chosen))
        for o in list(objs):
            for e in index.get(o, ()):
                chosen[e["Id"]] = e
        for e in list(chosen.values()):
            # What it came from. Where a unit or chore moved from says where it was, not what it came from.
            objs.update(f for f in e["From"] if followed(f) and not (e.get("Act") in ("unit.move", "chore.move") and f.startswith("bolt/")))
            # What came from it. A proposal reached from one of its changes is that change's origin: the rest of what
            # it applied is its siblings' history, so a proposal is followed forward only when the trace starts there.
            if any(f in objs and (not f.startswith("proposal/") or f == start) for f in e["From"]):
                objs.update(o for o in e["On"] if followed(o))
        if (len(objs), len(chosen)) == before:
            break
    return sorted(chosen.values(), key=lambda e: (e["At"], e["Id"]))


def trace(fleet, a):
    """One object's history, as lineage() walks it. A bare name is tried as a unit, then a chore, then a bolt, then a
    signal."""
    found, missing = gather(fleet, labels_for(fleet, a.label), "0000-00-00")
    start, candidates = trace_start(found, a.object)
    if start is None:
        for h, why in missing.items():
            print(f"{h} did not answer: {why}", file=sys.stderr)
        sys.exit(f"no entry names {' or '.join(candidates)}" + (f" ({' and '.join(missing)} could not be read)" if missing else ""))
    for e in lineage(found, start):
        print(line(e, zoe=True))
    for h, why in missing.items():
        print(f"{h} did not answer: {why}")


def trace_start(found, obj):
    """The object a trace starts from, or None, and the names it was looked for by: a typed one as it is, a bare name
    as a unit, then a chore, then a bolt, then a signal, the first that an entry names; a signal's short id starts from
    the signal it numbers, refused when the entries name more than one."""
    candidates = [obj] if obj.startswith(KINDS) else [f"{k}{obj}" for k in ("unit/", "chore/", "bolt/", "signals/")]
    for c in candidates:
        hits = sorted({o for e in found for o in objects(e) if meant(o, c)})
        len(hits) < 2 or fail(f"{c} names {len(hits)} signals: {', '.join(hits)}; give the full id of one")
        if hits:
            return hits[0], candidates
    return None, candidates


# ------------------------------------------------------------------------------------------------- command

OBJECT = ("a typed name, unit/<unit>, bolt/<bolt>, signals/<id> and the rest, where a signal's <id> is its full id, "
          "<capture>/<NN>-<slug>, or its short one, <capture>/<NN>")


def parser():
    ap = argparse.ArgumentParser(prog="crew", add_help=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("emit")
    x.add_argument("--label", required=True)
    x.add_argument("--act", required=True)
    x.add_argument("--on", action="append", default=[])
    x.add_argument("--from", dest="frm", action="append", default=[])
    x.add_argument("--commit", action="append", default=[])
    x.add_argument("--why")
    x.add_argument("--refused")
    x.add_argument("--field", action="append", default=[], help="K=V, one of " + " ".join(EXTRA))
    x.add_argument("--id")
    sub.add_parser("session")
    x = sub.add_parser("events")
    x.add_argument("--label")
    x.add_argument("--about", metavar="object", help=OBJECT)
    x.add_argument("--since")
    x.add_argument("--follow", action="store_true")
    x.add_argument("--push", action="store_true")
    x.add_argument("--json", action="store_true")
    x = sub.add_parser("trace")
    x.add_argument("object", help=OBJECT + "; a bare name is tried as a unit, then a chore, a bolt and a signal")
    x.add_argument("--label")
    return ap


def main(argv):
    a = parser().parse_args(argv)
    if a.cmd == "emit":
        extra = dict(f.split("=", 1) for f in a.field if "=" in f)
        eid = emit(a.label, a.act, a.on, a.frm, a.commit, a.why, a.refused, eid=a.id, **{k: v for k, v in extra.items() if k in EXTRA})
        if eid:
            print(eid)
        return
    if a.cmd == "session":
        print(session() or "")
        return
    fleet = crew.load()
    (events if a.cmd == "events" else trace)(fleet, a)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
