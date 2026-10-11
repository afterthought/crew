#!/usr/bin/env python3
"""crew deploy: what a kit's deployer asks of crew, and the user's word for a deploy (plan.14, ADR 0012).

  crew deploy offer <env> --label L --from <sha|none> --to <sha>
      the deployer offers a `manual` environment a deploy of main's green head: a rail row, deploy/<env>/<to>, whose
      card main-level ops posts. The same `to` again changes nothing while it is open; a newer one replaces it
  crew deploy approve <env> --label L --to <sha>
      the user's word for that offer, given by holding its card, recorded by whoever the user's yes reached; the row
      leaves the rail
  crew deploy word <env> --label L
      the commit the user's word was given for, exit 0; exit 1 when there is none. A word is for one deploy: once
      that deploy's end is recorded there is none until the user approves a new offer
  crew deploy record <env> --label L --to <sha> --act start|step|end [--from <sha|none>] [--step machine|guests|suite]
                     [--outcome ok|failed|done] [--log <path>] [--rows <json file>]
      a deploy's start, one of its steps, or its end, in the run record as it runs
  crew deploy step <env> --label L --to <sha> --key <key> --state waiting|handed|done|failed|declined
                   [--doer dispatcher|main-ops|user] [--agent <name>] [--when deployed|quiet] [--text <file>]
                   [--changes <a,b>] [--note <text>]
      an after-deploy step of that deploy and its state; a user's step waiting is a rail row with a card until it is
      marked done or declined
  crew deploy steps <env> --label L --json
      the latest state of every after-deploy step of the environment's deploys: [{to, key, state, by, at, note}]
  crew deploy quiet <env> --label L
      exit 0 when no stage agent of a team on the environment's host is working and no test of crew's runs there;
      exit 1 saying what is

Every command acts on the partition's deploys where its main level runs, on that host's run record: run anywhere
else, it is run there, as the one asking. An environment is a machine of the fleet, named as the deployer names it.
"""
import argparse, datetime, json, pathlib, re, sys

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
import record  # noqa: E402
from crew import Refusal, fail  # noqa: E402

NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SHA = re.compile(r"^[0-9a-f]{7,40}$")
STEP_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]*$")
ACTS = ("start", "step", "end")
STATES = ("waiting", "handed", "done", "failed", "declined")
DAYS = 60  # how far back the deploys are read: an offer or a word older than this has no row


def entries(label, days=DAYS):
    """The deploy entries of the partition's run record on this host, oldest first."""
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=days)).isoformat()
    d = record.ROOT / label / "runs" / crew.this_host()
    out = []
    for f in sorted(d.glob("*.rec")) if d.is_dir() else []:
        if f.stem >= since:
            out += [e for e in record.parse(f.read_text()) if (e.get("Act") or "").startswith("deploy.")]
    return sorted(out, key=lambda e: (e["At"], e["Id"]))


def env_of(e):
    return next((o[7:] for o in e.get("On", []) if o.startswith("deploy/")), None)


def state(es):
    """Each environment's deploys as the record holds them: its offer still open (unanswered, no deploy of it ended),
    {env: entry}; the word the user gave and no deploy has ended since, {env: entry}; and each after-deploy step's
    latest entry, {(env, to, key): entry}."""
    offers, words, steps = {}, {}, {}
    for e in es:
        env, act, to = env_of(e), e["Act"], e.get("Head")
        if not env:
            continue
        if act == "deploy.offer":
            offers[env] = e
        elif act == "deploy.approve":
            words[env] = e
            if offers.get(env, {}).get("Head") == to:
                offers.pop(env)
        elif act == "deploy.end":
            if words.get(env, {}).get("Head") == to:
                words.pop(env)
            if offers.get(env, {}).get("Head") == to:
                offers.pop(env)
        elif act == "deploy.after":
            steps[(env, to, e.get("Key"))] = e
    return offers, words, steps


def rows(fleet, label, es):
    """The rail's rows for the partition's deploys, from its entries: each open offer, deploy/<env>/<to>, answered by
    crew deploy approve; and each after-deploy step the user is to take that waits, deploy-step/<env>/<to>/<n>,
    answered by marking it done or declined. Each row's card is main-level ops's (briefs.11)."""
    offers, _, steps = state(es)
    out = []
    for env, e in sorted(offers.items()):
        to, base = e["Head"], e.get("Base") or "none"
        what = [f"deploy {env} ({label}) to {to[:7]}, from {base[:7] if base != 'none' else 'nothing deployed'}: "
                f"{label}-ops posts its card, and holding it is the word to deploy"]
        out.append(dict(group="deploys", label=label, key=f"deploy/{env}/{to[:7]}", at=e["At"], what=what,
                        cmds=[("answer", f"crew deploy approve {env} --to {to} --label {label}")]))
    for (env, to, key), e in sorted(steps.items(), key=lambda kv: (kv[1]["At"], kv[1]["Id"])):
        if e.get("Doer") != "user" or e.get("State") != "waiting":
            continue
        n = sum(1 for (v, t, _), x in steps.items() if v == env and t == to and x["At"] <= e["At"])
        what = [f"after the deploy of {env} ({label}) to {to[:7]}, yours to do: {e.get('Text') or key}"]
        cmds = [(s, f"crew deploy step {env} --to {to} --key {key} --state {'done' if s == 'done' else 'declined'} --label {label}")
                for s in ("done", "decline")]
        out.append(dict(group="deploys", label=label, key=f"deploy-step/{env}/{to[:7]}/{n}", at=e["At"], what=what, cmds=cmds))
    return out


def open_keys(label):
    """The card keys of the partition's deploy rows open now, on this host."""
    return [r["key"] for r in rows(None, label, entries(label))]


def emit(label, act, env, refused=None, **fields):
    eid = record.emit(label, act, [f"deploy/{env}"], why=f"deploy({env}): {act[7:]}"
                      + (f" {fields['Head'][:7]}" if fields.get("Head") else ""), refused=refused, **fields)
    eid or fail(f"the deploy's {act} could not be recorded in {label}'s run record")


def offer(fleet, a):
    offers, _, _ = state(entries(a.label))
    if offers.get(a.env, {}).get("Head") == a.to:
        return
    emit(a.label, "deploy.offer", a.env, Head=a.to, Base=getattr(a, "from"))


def approve(fleet, a):
    offers, _, _ = state(entries(a.label))
    e = offers.get(a.env)
    if not e or e["Head"] != a.to:
        why = (f"no deploy of {a.env} is offered" if not e else f"the deploy of {a.env} offered is to {e['Head'][:7]}, not {a.to[:7]}")
        emit(a.label, "deploy.approve", a.env, refused=why, Head=a.to)
        fail(f"{why}: crew deploy approve answers the offer the rail shows (crew rail --label {a.label})")
    emit(a.label, "deploy.approve", a.env, Head=a.to)
    print(f"the deploy of {a.env} to {a.to[:7]} is approved: the deployer runs it at its next run")


def word(fleet, a):
    _, words, _ = state(entries(a.label))
    e = words.get(a.env)
    if not e:
        print(f"no word is given for a deploy of {a.env}: the user gives it by holding the offer's card", file=sys.stderr)
        sys.exit(1)
    print(e["Head"])


def record_cmd(fleet, a):
    rows_ = None
    if a.rows:
        try:
            rows_ = json.dumps(json.loads(pathlib.Path(a.rows).read_text()), separators=(",", ":"))
        except (OSError, ValueError) as e:
            fail(f"the rows file {a.rows} can't be read as JSON: {e}")
    emit(a.label, f"deploy.{a.act}", a.env, Head=a.to, Base=getattr(a, "from"), Step=a.step, Outcome=a.outcome, Log=a.log, Rows=rows_)


def step(fleet, a):
    text = None
    if a.text:
        try:
            text = pathlib.Path(a.text).read_text()
        except OSError as e:
            fail(f"the step's text {a.text} can't be read: {e.strerror or e}")
    emit(a.label, "deploy.after", a.env, Head=a.to, Key=a.key, State=a.state, Doer=a.doer, Agent=a.agent, When=a.when,
         Text=text, Changes=a.changes, Note=a.note)


def steps(fleet, a):
    _, _, st = state(entries(a.label))
    print(json.dumps([dict(to=to, key=key, state=e.get("State"), by=e.get("By"), at=e["At"], note=e.get("Note"))
                      for (env, to, key), e in sorted(st.items(), key=lambda kv: (kv[1]["At"], kv[1]["Id"])) if env == a.env]))


# What `quiet` runs on the environment's host: whether any of crew's tests holds a test slot there (tests/slot).
SLOTS = r"""import fcntl, glob, os, sys
busy = 0
for f in glob.glob(os.path.expanduser("~/.cache/crew/test-slots/slot-*")):
    fd = os.open(f, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        busy += 1
    finally:
        os.close(fd)
print(busy)
"""


def quiet(fleet, a):
    """Whether the environment's host is quiet: no stage agent of a team there working, and no test of crew's running."""
    a.env in fleet["hosts"] or fail(f"{a.env} is no host of the fleet's hosts file")
    said = []
    for t in sorted((t for t in fleet["teams"].values() if t["machine"] == a.env), key=lambda t: t["name"]):
        for n in range(1, t["units"] + 1):
            agent, unread = crew.read_agent(fleet, f"{t['name']}-unit-{n}")
            if unread:
                fail(f"crew can't tell whether {t['name']}-unit-{n} is working: {unread}")
            if agent and agent.get("agent_status") == "working":
                said.append(f"{t['name']}-unit-{n} is working")
    r = crew.on_machine(fleet, a.env, ["python3", "-c", SLOTS])
    if r.returncode or not r.stdout.strip().isdigit():
        fail(f"crew can't tell whether a test runs on {a.env}: " + (crew.unanswered(a.env, r) or (r.stderr or "").strip() or "no answer"))
    if int(r.stdout.strip()):
        said.append(f"{r.stdout.strip()} of crew's tests are running on {a.env}")
    if said:
        print("; ".join(said))
        sys.exit(1)


COMMANDS = {"offer": offer, "approve": approve, "word": word, "record": record_cmd, "step": step, "steps": steps, "quiet": quiet}


def parser():
    ap = argparse.ArgumentParser(prog="crew deploy", description="What a kit's deployer asks of crew, and the user's word for a deploy.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def cmd(name, to=True, label=True):
        p = sub.add_parser(name)
        p.add_argument("env")
        p.add_argument("--label", required=label)
        if to:
            p.add_argument("--to", required=True)
        return p
    p = cmd("offer")
    p.add_argument("--from", required=True)
    cmd("approve")
    cmd("word", to=False)
    p = cmd("record")
    p.add_argument("--act", required=True, choices=ACTS)
    p.add_argument("--from")
    p.add_argument("--step", choices=("machine", "guests", "suite"))
    p.add_argument("--outcome", choices=("ok", "failed", "done"))
    p.add_argument("--log")
    p.add_argument("--rows")
    p = cmd("step")
    p.add_argument("--key", required=True)
    p.add_argument("--state", required=True, choices=STATES)
    p.add_argument("--doer", choices=("dispatcher", "main-ops", "user"))
    p.add_argument("--agent")
    p.add_argument("--when", choices=("deployed", "quiet"))
    p.add_argument("--text")
    p.add_argument("--changes")
    p.add_argument("--note")
    p = cmd("steps", to=False)
    p.add_argument("--json", action="store_true", required=True)
    cmd("quiet", to=False)
    return ap


def main(argv):
    a = parser().parse_args(argv)
    fleet = crew.load()
    NAME.match(a.env) or fail(f"{a.env} is no environment's name: lowercase words and dashes")
    a.label in fleet["partitions"] or fail(f"no partition {a.label} in the teams file. partitions: " + " ".join(fleet["partitions"]))
    for f in ("to", "from"):
        v = getattr(a, f, None)
        if v and not (v == "none" and f == "from") and not SHA.match(v):
            fail(f"--{f} {v} is no commit: a sha in hex")
    if getattr(a, "key", None) and not STEP_KEY.match(a.key):
        fail(f"--key {a.key} is no step key crew takes")
    machine = crew.partition_of(fleet, a.label)["machine"]
    if a.cmd != "quiet" and machine != crew.this_host():
        r = crew.on_machine(fleet, machine, crew.crew_argv(fleet, machine, "deploy", *argv))
        sys.stdout.write(r.stdout), sys.stderr.write(r.stderr)
        if r.returncode == 255 and crew.unanswered(machine, r):
            sys.exit(f"{a.label}'s deploys are kept on {machine}, which did not answer: {crew.unanswered(machine, r)}")
        sys.exit(r.returncode)
    COMMANDS[a.cmd](fleet, a)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
