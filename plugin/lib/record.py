#!/usr/bin/env python3
"""record.py: crew's run record, what crew did, written where it did it.

Every crew command that moves work appends one entry per act, after the act is done, to a recutils file on the host
where it ran: ~/.local/state/crew/<label>/runs/<host>/<YYYY-MM-DD>.rec, one file per UTC day. An entry names who asked
and the Claude session behind them, the act, the objects acted on (On) and those they came from (From), the commit
written if any, and the subject crew composed from the names of things: never text anyone typed. A failed append is
said on standard error and never changes what the command does or how it exits.

Each write to a flywheel's branch of its state repository also carries the host's entries there, to the same path
under runs/<host>/: the branch's file becomes the union by Id of what it had and what the host has, so a host only
ever adds to its own files and a host that is asleep or rebuilt loses nothing it had carried. Reading takes the
branch first, then whatever each host it can reach has not yet carried.

  record.py emit --label L --act A [--on X]... [--from X]... [--commit C]... [--why W] [--refused R] [--field K=V]...
                [--id I]                  append one entry, with the id a commit already names if given; prints its id
  record.py session                       the caller's Claude session as <host>:<id>, what a forwarded command carries
  record.py events [--label L] [--about <object>] [--since <time>] [--follow] [--json]
                                          the entries of the partition's branch and of every host it runs on, in time order
  record.py events --push [--label L]     carry this host's entries to the branch now, in a commit of their own
  record.py trace <object> [--label L]    one bolt's, unit's or signal's history, read from the entries alone

An object is a typed name: unit/<unit>, bolt/<bolt>, queue/<kit>, signals/<id>, team/<team>, agent/<name>,
stage/<unit>/<stage>, fix/<bolt>/<name>, plan/<label>, proposal/<n>."""
import argparse, datetime, getpass, json, os, pathlib, queue, re, signal, subprocess, sys, tempfile, threading

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
from crew import Refusal, fail  # noqa: E402

ROOT = pathlib.Path.home() / ".local/state/crew"
DESCRIPTOR = """\
# crew's run record: one entry per act of crew's that moved work, appended by crew on this host and never
# rewritten. Read it with recsel, or with crew events and crew trace.

%rec: Entry
%key: Id
%mandatory: Id At Host By Act
%allowed: Id At Host By Session Act On From Commit Why Refused Result Tasks Head Observed Chars Amended

"""
# Fields beyond the common ones: a stage.end's Result, Tasks, Head and Observed, a tell's Chars, and the Amended of
# a construct's start that marked its unit amended.
EXTRA = ("Result", "Tasks", "Head", "Observed", "Chars", "Amended")
LISTS = ("On", "From", "Commit")
# Objects a trace prints but never follows: following them would pull in everything a team or a kit ever did.
UNFOLLOWED = ("agent/", "team/", "queue/", "plan/")
KINDS = ("unit/", "bolt/", "queue/", "signals/", "team/", "agent/", "stage/", "fix/", "plan/", "proposal/")

_count = 0
_session = ...  # resolved once per process


def who():
    """Who asked: the agent crew started, else the user at this host."""
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
        host, sess = crew.place_of_agent(crew.load(), name)
    except Refusal:
        return None
    if host != crew.this_host():
        return None
    try:
        r = subprocess.run(["herdr", "--session", sess, "agent", "get", name], capture_output=True, text=True, timeout=10)
        sid = json.loads(r.stdout)["result"]["agent"]["agent_session"]["value"] if r.returncode == 0 else None
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
        sid = None
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


def new_id():
    """A new entry's id: the time, the host, the process and a count, unique without a lock. A write makes its
    entry's id before its commit, so the commit can name the entry its message describes."""
    global _count
    _count += 1
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{now.strftime('%Y%m%dT%H%M%SZ')}-{crew.this_host()}-{os.getpid()}-{_count}"


def emit(label, act, on=(), frm=(), commit=(), why=None, refused=None, eid=None, **extra):
    """Append one entry to the label's run record on this host, in one write; its id, or None when it could not be
    written, which is said on standard error and nothing more. eid is an id made ahead with new_id."""
    if not label:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    host = crew.this_host()
    eid = eid or new_id()
    fields = [("Id", eid), ("At", now.strftime("%Y-%m-%dT%H:%M:%SZ")), ("Host", host), ("By", who())]
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
    return eid


# ------------------------------------------------------------------------------------- carried to the branch

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
    """Where this host notes the newest entry it has carried for the label."""
    return ROOT / label / "runs" / ".carried"


def carry(label, at_branch):
    """The host's run-record files of the label as its branch must hold them, {path on the branch: text}, and the
    newest id among the entries looked at. A day's file on the branch becomes the union by Id of the branch's entries
    and the host's, in Id order, and is left out when the branch already holds every entry the host has. Days before
    the newest carried one are not looked at. at_branch(path) reads a file at the branch's tip, or None."""
    host = crew.this_host()
    d = ROOT / label / "runs" / host
    try:
        done = mark(label).read_text().strip()
    except OSError:
        done = ""
    since = f"{done[0:4]}-{done[4:6]}-{done[6:8]}" if len(done) >= 8 else ""
    out, newest = {}, None
    for f in sorted(d.glob("*.rec")) if d.is_dir() else []:
        if f.stem < since:
            continue
        mine = blocks(f.read_text())
        if not mine:
            continue
        newest = max([newest or "", *mine])
        path = f"runs/{host}/{f.name}"
        have = blocks(at_branch(path) or "")
        if set(mine) <= set(have):
            continue
        union = {**mine, **have}
        out[path] = DESCRIPTOR + "\n".join(union[k] for k in sorted(union))
    return out, newest


def mark_carried(label, newest):
    """After a push carried entries up to newest, start the next carry from that day."""
    if not newest:
        return
    try:
        mark(label).parent.mkdir(parents=True, exist_ok=True)
        mark(label).write_text(newest + "\n")
    except OSError as e:
        print(f"crew: could not note what was carried at {mark(label)}: {e.strerror or e}", file=sys.stderr)


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


def hosts_of(fleet, label):
    """The hosts a partition runs on: its teams', its main level's, and each holding an operator session named for it."""
    p = crew.partition_of(fleet, label)
    hosts = {p["machine"]} | {fleet["teams"][t]["machine"] for t in p["teams"]}
    hosts |= {h for h, v in fleet["hosts"].items() if (v.get("sessions") or {}).get(label, {}).get("partition") == p["partition"]}
    return sorted(hosts)


READ = r"""since=$1; shift
for l in "$@"; do
  for f in "$HOME/.local/state/crew/$l"/runs/*/*.rec; do
    [ -f "$f" ] || continue
    n=$(basename "$f" .rec)
    [[ $n < $since ]] && continue
    cat "$f"; echo
  done
done
"""


def on_branch(fleet, label, since_day):
    """The entries carried to the label's branch of its state repository, from since_day on."""
    import plan  # plan.py imports this module; its git layer is only needed here
    repo, ref = plan.state_of(fleet, label)
    tip = plan.fetch(repo, ref)
    if not tip:
        return []
    out = []
    for path in plan.git(repo, "ls-tree", "-r", "--name-only", tip, "--", "runs/").splitlines():
        if path.endswith(".rec") and pathlib.PurePath(path).stem >= since_day:
            out += parse(plan.show(repo, tip, path) or "")
    return out


def gather(fleet, labels, since_day):
    """Every entry of the labels' run records from since_day on: what each label's branch holds, then what each
    host has not yet carried, one call per host, duplicates dropped by Id and sorted by time then Id; and what did
    not answer, with why. A host that does not answer is shown as far as it had carried."""
    by_host = {}
    for l in labels:
        for h in hosts_of(fleet, l):
            by_host.setdefault(h, []).append(l)
    entries, missing = {}, {}
    for l in labels:
        try:
            for e in on_branch(fleet, l, since_day):
                entries.setdefault(e["Id"], e)
        except Refusal as err:
            missing[f"{l}/main"] = str(err)
    for h, ls in sorted(by_host.items()):
        r = crew.on_machine(fleet, h, ["bash", "-c", READ, "crew", since_day, *ls])
        if r.returncode:
            missing[h] = (r.stderr.strip().splitlines() or [f"exit {r.returncode}"])[-1]
            continue
        for e in parse(r.stdout):
            entries.setdefault(e["Id"], e)
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
    if e.get("Result"):
        s += f" → {e['Result']}" + (f" {e['Tasks']}" if e.get("Tasks") not in (None, "", "-") else "") + (f" at {e['Head']}" if e.get("Head") else "")
    if e.get("Observed"):
        s += f" (observed {e['Observed']})"
    if e.get("Chars"):
        s += f" ({e['Chars']} characters)"
    if e.get("Amended"):
        s += " (amended)"
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


def names(e, obj):
    return obj in e["On"] or obj in e["From"]


def events(fleet, a):
    labels = labels_for(fleet, a.label)
    if a.push:
        import plan
        for l in labels:
            plan.carry_now(fleet, l)
        return
    if a.follow:
        return follow(fleet, labels, a.about)
    day, stamp = when(a.since)
    found, missing = gather(fleet, labels, day)
    found = [e for e in found if e["At"] >= stamp and (not a.about or names(e, a.about))]
    if a.json:
        print(json.dumps({"entries": found, "unreachable": missing}, indent=1))
        return
    for e in found:
        print(line(e))
    for h, why in missing.items():
        print(f"{h} did not answer: {why}")


def follow(fleet, labels, about):
    """Each entry of the labels on every reachable host as it is appended, one tail per host, until interrupted. The
    files are named by the UTC date, so the tails start again when it changes."""
    lines = queue.Queue()
    procs = []

    def stop(*_):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)

    def read(p):
        buf = []
        for raw in p.stdout:
            if raw.strip():
                buf.append(raw.rstrip("\n"))
                continue
            if buf:
                lines.put("\n".join(buf))
            buf = []

    def start(day):
        tomorrow = (datetime.date.fromisoformat(day) + datetime.timedelta(days=1)).isoformat()
        by_host = {}
        for l in labels:
            for h in hosts_of(fleet, l):
                by_host.setdefault(h, []).append(l)
        for h, ls in sorted(by_host.items()):
            files = " ".join(f'"$HOME/.local/state/crew/{l}/runs/{h}/{d}.rec"' for l in ls for d in (day, tomorrow))
            cmd = f"exec tail -q -n 0 -F {files} 2>/dev/null"
            argv = ["bash", "-c", cmd] if h == crew.this_host() else ["ssh", "-o", "BatchMode=yes", fleet["hosts"][h]["ssh"], cmd]
            p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            procs.append(p)
            threading.Thread(target=read, args=(p,), daemon=True).start()

    try:
        day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        start(day)
        while True:
            try:
                text = lines.get(timeout=5)
            except queue.Empty:
                now = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
                if now != day:
                    for p in procs:
                        p.terminate()
                    procs.clear()
                    day = now
                    start(day)
                continue
            for e in parse(text):
                if not about or names(e, about):
                    print(line(e), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            p.terminate()


def followed(obj):
    return not obj.startswith(UNFOLLOWED)


def trace(fleet, a):
    """One object's history: every entry naming it, the entries of what it came from (an entry's From) and of what
    came from it (the On of an entry whose From names it), until nothing is added. A bare name is tried as a unit,
    then a bolt, then a signal."""
    found, missing = gather(fleet, labels_for(fleet, a.label), "0000-00-00")
    candidates = [a.object] if a.object.startswith(KINDS) else [f"{k}{a.object}" for k in ("unit/", "bolt/", "signals/")]
    start = next((c for c in candidates if any(names(e, c) for e in found)), None)
    if start is None:
        for h, why in missing.items():
            print(f"{h} did not answer: {why}", file=sys.stderr)
        sys.exit(f"no entry names {' or '.join(candidates)}" + (" (some hosts did not answer)" if missing else ""))
    objs, chosen = {start}, {}
    while True:
        before = (len(objs), len(chosen))
        for e in found:
            if any(names(e, o) for o in objs):
                chosen[e["Id"]] = e
        for e in list(chosen.values()):
            # What it came from. Where a unit moved from says where it was, not what it came from.
            objs.update(f for f in e["From"] if followed(f) and not (e.get("Act") == "unit.move" and f.startswith("bolt/")))
            # What came from it. A proposal reached from one of its changes is that change's origin: the rest of what
            # it applied is its siblings' history, so a proposal is followed forward only when the trace starts there.
            if any(f in objs and (not f.startswith("proposal/") or f == start) for f in e["From"]):
                objs.update(o for o in e["On"] if followed(o))
        if (len(objs), len(chosen)) == before:
            break
    for e in sorted(chosen.values(), key=lambda e: (e["At"], e["Id"])):
        print(line(e, zoe=True))
    for h, why in missing.items():
        print(f"{h} did not answer: {why}")


# ------------------------------------------------------------------------------------------------- command

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
    x.add_argument("--about")
    x.add_argument("--since")
    x.add_argument("--follow", action="store_true")
    x.add_argument("--push", action="store_true")
    x.add_argument("--json", action="store_true")
    x = sub.add_parser("trace")
    x.add_argument("object")
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
