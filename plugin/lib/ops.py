#!/usr/bin/env python3
"""crew ops: the operations on a partition's environments, a deploy being one kind (plan.14, ADR 0012).

A deploy is the act of a kit's deployer, or of a hosted CI/CD standing in for it, under each environment's policy; crew
gates a `manual` one on the user's word and records it. Every other operation, a command after a deploy, a restart, a
check, is a step: done by an agent it is handed to or by the user, recorded with its state, and tied to a deploy only
when it names one.

  crew ops offer <env> --label L --to <sha> --from <sha|none>
      a deploy of a commit, offered for a `manual` environment: a row under *operations* on the rail,
      deploy/<env>/<to>, whose card main-level ops posts. The same `to` again changes nothing while it is open; a
      newer one replaces it
  crew ops approve <env> --label L --to <sha>
      the user's word for that deploy, given by holding its card, recorded by whoever the user's yes reached; the row
      leaves the rail
  crew ops word <env> --label L
      the commit the user's word was given for, exit 0; exit 1 when there is none. A word is for one deploy: once that
      deploy's end is recorded there is none until the user approves a new offer
  crew ops record <env> --label L --to <sha> --act start|step|end [--from <sha|none>] [--step machine|guests|suite]
                  [--outcome ok|failed|done] [--log <path>] [--rows <json file>]
      a deploy's start, one of its steps, or its end, in the run record as it runs
  crew ops step <env> --label L --key <key> --state waiting|handed|done|failed|declined [--to <sha>]
                [--doer dispatcher|main-ops|user] [--agent <name>] [--when deployed|quiet] [--text <file>]
                [--changes <a,b>] [--note <text>]
      an operation of its own and its state, after the deploy it names with --to or on its own; one the user is to
      take that waits is a rail row with a card until it is marked done or declined
  crew ops steps <env> --label L --json
      the latest state of every step on the environment: [{to, key, state, by, at, note}], to empty for a step that
      names no deploy
  crew ops quiet <env> --label L
      exit 0 when no stage agent of a team on the environment's host is working and no test of crew's runs there;
      exit 1 saying what is

Every command acts on the partition's operations where its main level runs, on that host's run record, as ops.*
entries on env/<env>: run anywhere else, it is run there, as the one asking. An environment is a machine of the fleet,
named as the deployer names it.
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
DAYS = 60  # how far back the operations are read: an offer, a word or a step older than this has no row


def entries(label, days=DAYS):
    """The ops entries of the partition's run record on this host, oldest first."""
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=days)).isoformat()
    d = record.ROOT / label / "runs" / crew.this_host()
    out = []
    for f in sorted(d.glob("*.rec")) if d.is_dir() else []:
        if f.stem >= since:
            out += [e for e in record.parse(f.read_text()) if (e.get("Act") or "").startswith("ops.")]
    return sorted(out, key=lambda e: (e["At"], e["Id"]))


def env_of(e):
    return next((o[4:] for o in e.get("On", []) if o.startswith("env/")), None)


def state(es):
    """Each environment's operations as the record holds them: its deploy offer still open (unanswered, no deploy of
    it ended), {env: entry}; the word the user gave and no deploy has ended since, {env: entry}; and each step's
    latest entry, {(env, to or "", key): entry}."""
    offers, words, steps = {}, {}, {}
    for e in es:
        env, act, to = env_of(e), e["Act"], e.get("Head")
        if not env:
            continue
        if act == "ops.offer":
            offers[env] = e
        elif act == "ops.approve" and not e.get("Refused"):
            words[env] = e
            if offers.get(env, {}).get("Head") == to:
                offers.pop(env)
        elif act == "ops.deploy" and e.get("Phase") == "end":
            if words.get(env, {}).get("Head") == to:
                words.pop(env)
            if offers.get(env, {}).get("Head") == to:
                offers.pop(env)
        elif act == "ops.step":
            steps[(env, to or "", e.get("Key"))] = e
    return offers, words, steps


def ordered(steps):
    return sorted(steps.items(), key=lambda kv: (kv[1]["At"], kv[1]["Id"]))


def rows(fleet, label, es):
    """The rail's rows for the partition's operations, from its entries: each open deploy offer, deploy/<env>/<to>,
    answered by crew ops approve; and each step the user is to take that waits, op/<env>/<n>, its n counting the
    environment's steps, answered by marking it done or declined. Each row's card is main-level ops's (briefs.11)."""
    offers, _, steps = state(es)
    out = []
    for env, e in sorted(offers.items()):
        to, base = e["Head"], e.get("Base") or "none"
        what = [f"deploy {env} ({label}) to {to[:7]}, from {base[:7] if base != 'none' else 'nothing deployed'}: "
                f"{label}-ops posts its card, and holding it is the word to deploy"]
        out.append(dict(group="operations", label=label, key=f"deploy/{env}/{to[:7]}", at=e["At"], what=what,
                        cmds=[("answer", f"crew ops approve {env} --to {to} --label {label}")]))
    n = {}
    for (env, to, key), e in ordered(steps):
        n[env] = n.get(env, 0) + 1
        if e.get("Doer") != "user" or e.get("State") != "waiting":
            continue
        after = f"after the deploy of {env} to {to[:7]}" if to else f"on {env}"
        what = [f"an operation {after} ({label}), yours to do: {e.get('Text') or key}"]
        to_arg = f" --to {to}" if to else ""
        cmds = [(s, f"crew ops step {env}{to_arg} --key {key} --state {'done' if s == 'done' else 'declined'} --label {label}")
                for s in ("done", "decline")]
        out.append(dict(group="operations", label=label, key=f"op/{env}/{n[env]}", at=e["At"], what=what, cmds=cmds))
    return out


def open_keys(label):
    """The card keys of the partition's operations rows open now, on this host."""
    return [r["key"] for r in rows(None, label, entries(label))]


def emit(label, act, env, why, refused=None, **fields):
    eid = record.emit(label, act, [f"env/{env}"], why=f"ops({env}): {why}", refused=refused, **fields)
    eid or fail(f"the operation's {act} could not be recorded in {label}'s run record")


def offer(fleet, a):
    offers, _, _ = state(entries(a.label))
    if offers.get(a.env, {}).get("Head") == a.to:
        return
    emit(a.label, "ops.offer", a.env, f"offer a deploy of {a.to[:7]}", Head=a.to, Base=getattr(a, "from"))


def approve(fleet, a):
    offers, _, _ = state(entries(a.label))
    why = approve_refusal(offers, a.env, a.to)
    if why:
        emit(a.label, "ops.approve", a.env, f"approve a deploy of {a.to[:7]}", refused=why, Head=a.to)
        fail(f"{why}: crew ops approve answers the offer the rail shows (crew rail --label {a.label})")
    emit(a.label, "ops.approve", a.env, f"approve a deploy of {a.to[:7]}", Head=a.to)
    print(f"the deploy of {a.env} to {a.to[:7]} is approved: the deployer runs it at its next run")


def approve_refusal(offers, env, to):
    """Why the user's approval of a deploy of env to to is refused, or None: it answers only the offer open now."""
    e = offers.get(env)
    if not e:
        return f"no deploy of {env} is offered"
    return None if e["Head"] == to else f"the deploy of {env} offered is to {e['Head'][:7]}, not {to[:7]}"


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
    emit(a.label, "ops.deploy", a.env, f"deploy {a.to[:7]}: {a.act}" + (f" {a.step}" if a.step else ""), Head=a.to,
         Base=getattr(a, "from"), Phase=a.act, Step=a.step, Outcome=a.outcome, Log=a.log, Rows=rows_)


def step(fleet, a):
    text = None
    if a.text:
        try:
            text = pathlib.Path(a.text).read_text()
        except OSError as e:
            fail(f"the step's text {a.text} can't be read: {e.strerror or e}")
    emit(a.label, "ops.step", a.env, f"{a.key} {a.state}", Head=a.to, Key=a.key, State=a.state, Doer=a.doer, Agent=a.agent,
         When=a.when, Text=text, Changes=a.changes, Note=a.note)


def steps(fleet, a):
    _, _, st = state(entries(a.label))
    print(json.dumps([dict(to=to, key=key, state=e.get("State"), by=e.get("By"), at=e["At"], note=e.get("Note"))
                      for (env, to, key), e in ordered(st) if env == a.env]))


# What `quiet` runs on the environment's host: how many of crew's tests hold a test slot there (tests/slot).
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
    ap = argparse.ArgumentParser(prog="crew ops", description="The operations on a partition's environments, a deploy being one kind.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def cmd(name, to=True):
        p = sub.add_parser(name)
        p.add_argument("env")
        p.add_argument("--label", required=True)
        p.add_argument("--to", required=to)
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
    p = cmd("step", to=False)
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


def args_refusal(fleet, a):
    """Why crew ops refuses what it was given, or None: an environment's name, a partition of the teams file, a
    commit as a sha in hex (--from none for nothing deployed), and a step key crew takes."""
    if not NAME.match(a.env):
        return f"{a.env} is no environment's name: lowercase words and dashes"
    if a.label not in fleet["partitions"]:
        return f"no partition {a.label} in the teams file. partitions: " + " ".join(fleet["partitions"])
    for f in ("to", "from"):
        v = getattr(a, f, None)
        if v and not (v == "none" and f == "from") and not SHA.match(v):
            return f"--{f} {v} is no commit: a sha in hex"
    if getattr(a, "key", None) and not STEP_KEY.match(a.key):
        return f"--key {a.key} is no step key crew takes"
    return None


def main(argv):
    a = parser().parse_args(argv)
    fleet = crew.load()
    why = args_refusal(fleet, a)
    why is None or fail(why)
    machine = crew.partition_of(fleet, a.label)["machine"]
    if a.cmd != "quiet" and machine != crew.this_host():
        r = crew.on_machine(fleet, machine, crew.crew_argv(fleet, machine, "ops", *argv))
        sys.stdout.write(r.stdout), sys.stderr.write(r.stderr)
        if r.returncode == 255 and crew.unanswered(machine, r):
            sys.exit(f"{a.label}'s operations are kept on {machine}, which did not answer: {crew.unanswered(machine, r)}")
        sys.exit(r.returncode)
    COMMANDS[a.cmd](fleet, a)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
