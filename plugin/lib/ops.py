#!/usr/bin/env python3
"""crew ops: the operations on a partition's environments, a deploy being one kind (plan.14, ADR 0012).

A deploy is the act of a kit's deployer, or of a hosted CI/CD standing in for it, under each environment's policy; crew
gates a `manual` one on the user's word and records it. Every other operation, a command after a deploy, a restart, a
check, is a step: done by an agent it is handed to or by the user, recorded with its state, and tied to a deploy only
when it names one.

  crew ops offer <env> --label L --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]
      a deploy of a commit, offered for a `manual` environment: a row under *operations* on the rail, deploy/<env>,
      and its card, which crew raises in main-level ops's name and tells it the line that adopts. On its face the
      kit's release notes for the range, --notes, as its changelog tool wrote them, and the range's after-deploy
      steps, --steps, one a line as the deployer gathers them (step <n> <doer> <when> <environments> <why> <text>,
      tab-separated, held among the when words); handed neither, the landings' subjects. The same `to` again
      changes nothing while it is open; a newer one replaces it and changes its card
  crew ops approve <env> --label L --to <sha>
      the user's word for that deploy, given by holding its card, recorded by whoever the user's yes reached; the row
      leaves the rail
  crew ops word <env> --label L
      the commit the user's word was given for, exit 0; exit 1 when there is none. A word is for one deploy: once that
      deploy's end is recorded there is none until the user approves a new offer
  crew ops record <env> --label L --to <sha> --act start|step|end [--from <sha|none>] [--step machine|guests|suite]
                  [--outcome ok|failed|done] [--log <path>] [--rows <json file>]
      a deploy's start, one of its steps, or its end, in the run record as it runs; its end closes the deploy's card
      with each step's outcome, or the step that failed and its log
  crew ops step <env> --label L --key <key> --state waiting|handed|done|failed|declined [--to <sha>]
                [--doer dispatcher|main-ops|user] [--agent <name>] [--when deployed|quiet] [--held] [--text <file>]
                [--changes <a,b>] [--note <text>]
      an operation of its own and its state, after the deploy it names with --to or on its own; one the user is to
      take, or an agent's held for the user's word, that waits is a rail row with a card, which crew raises one at a
      time on an environment, each following the one before, and closes when the step is marked done or declined.
      Recorded again while its own card is open, the card is changed in place when its words, doer or hold differ,
      and the line that adopts it is printed either way. The text's field lines, `- why:`, `- where:`, `- command:`
      (one a command) and `- done:`, are the card's
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
DOERS = ("dispatcher", "main-ops", "user")
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
    latest entry, {(env, to or "", key): entry}, in the order of each step's first entry."""
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


def numbered(steps):
    """Each step with its number among its environment's steps, counted in the order each was first recorded, so a
    step's number never changes when another's state does: [(n, (env, to, key), latest entry)]."""
    n, out = {}, []
    for k, e in steps.items():
        n[k[0]] = n.get(k[0], 0) + 1
        out.append((n[k[0]], k, e))
    return out


def held(e):
    """Whether a step is held for the user's word: held among its when words, as the deployer marks it."""
    return "held" in (e.get("When") or "").split()


def waits_on_user(e):
    """Whether a step's latest entry waits on the user: theirs to take, or an agent's held for their word."""
    return e.get("State") == "waiting" and (e.get("Doer") == "user" or held(e))


def rows(fleet, label, es):
    """The rail's rows for the partition's operations, from its entries: each open deploy offer, deploy/<env>,
    answered by crew ops approve; and each step that waits on the user, theirs to take or an agent's held for their
    word, op/<env>/<n>, its n counting the environment's steps in the order they were first recorded, answered by
    marking it done or declined. Each row's card is raised by crew in main-level ops's name (briefs.11)."""
    offers, _, steps = state(es)
    out = []
    for env, e in sorted(offers.items()):
        to, base = e["Head"], e.get("Base") or "none"
        what = [f"deploy {env} ({label}) to {to[:7]}, from {base[:7] if base != 'none' else 'nothing deployed'}: "
                f"crew raises its card in {label}-ops's name, and holding it is the word to deploy"]
        out.append(dict(group="operations", label=label, key=f"deploy/{env}", at=e["At"], what=what,
                        cmds=[("answer", f"crew ops approve {env} --to {to} --label {label}")]))
    for n, (env, to, key), e in numbered(steps):
        if not waits_on_user(e):
            continue
        after = f"after the deploy of {env} to {to[:7]}" if to else f"on {env}"
        whose = "yours to do" if e.get("Doer") == "user" else f"{e.get('Agent') or e.get('Doer')}'s, held for your word"
        what = [f"an operation {after} ({label}), {whose}: {e.get('Text') or key}"]
        to_arg = f" --to {to}" if to else ""
        cmds = [(s, f"crew ops step {env}{to_arg} --key {key} --state {'done' if s == 'done' else 'declined'} --label {label}")
                for s in ("done", "decline")]
        out.append(dict(group="operations", label=label, key=f"op/{env}/{n}", at=e["At"], what=what, cmds=cmds))
    return out


WAITING = ("waiting", "handed", "failed")  # a step in one of these states is an operation still waiting


def landings(es):
    """The partition's landings, from its bolt.land entries not refused, oldest first: each {bolt, units, at, by, repo,
    head}, the kit it landed on and the commit that kit's main held afterwards, None where the entry has none."""
    out = []
    for e in es:
        bolt = next((o[5:] for o in e["On"] if o.startswith("bolt/")), None) if e.get("Act") == "bolt.land" and not e.get("Refused") else None
        if bolt:
            out.append(dict(bolt=bolt, units=[o[5:] for o in e["On"] if o.startswith("unit/")], at=e["At"], by=e.get("By"),
                            repo=e.get("Repo"), head=e.get("Head")))
    return out


def carried(to, frm, lands):
    """The bolts a deploy from frm to to carried, from the landings (oldest first): the landings on the kit whose main
    one of them left at to, after the one that left it at frm, up to that one; every one up to it when frm is none,
    nothing having been deployed. ([bolts], None), or (None, why) when the record holds no landing at to or at frm, so
    which landings the deploy carried can't be read from it (read.1)."""
    at = next((i for i, l in enumerate(lands) if l["head"] and l["head"] == to), None)
    if at is None:
        return None, f"{to[:7]} is no landing's commit in the record"
    mine = [l for l in lands[:at + 1] if l["repo"] == lands[at]["repo"]]
    if frm in (None, "", "none"):
        return [l["bolt"] for l in mine], None
    start = next((i for i, l in enumerate(mine) if l["head"] == frm), None)
    if start is None:
        return None, f"{frm[:7]} is no landing's commit in the record"
    return [l["bolt"] for l in mine[start + 1:]], None


def environments(es, since=None):
    """Each environment's deploys and the operations waiting on it, from the partition's entries (es, oldest first),
    as the board's Operation lane and the page's deploys view show them (plan.14, state.4): {env: {"deploys": [...],
    "waiting": [...]}}, by environment.

    A deploy is one commit offered or deployed until its deploy ends: its to and from, when it was offered, the user's
    word (who held its card, and when), its answer (approved; waiting on the word; replaced, an unanswered offer a newer
    one replaced, or an approved one not started when the user's word went to another commit, as state reads the word;
    or unasked, a deploy started with no offer in the record, an auto environment's), when it started
    and ended and its outcome, each of its steps with its outcome, the suite's checks (the rows of its last step that
    has them), the bolts it carried or why the record can't tell, every after-deploy step recorded against its commit
    with its doer and latest state, its rail row while it waits on the word, and when it last moved; newest first,
    those that last moved before since left out unless still open. Waiting are the operations whose latest state is
    waiting, handed or failed, each with whether it is held for the user's word and its rail row when it waits on the
    user."""
    lands = landings(es)
    _, _, steps = state(es)
    envs = {}
    for e in es:
        env, act, to = env_of(e), e.get("Act") or "", e.get("Head")
        if not env or not act.startswith("ops.") or act == "ops.step" or not to:
            continue
        E = envs.setdefault(env, {"deploys": [], "open": {}})

        def new(frm, offered, answer):
            d = {"to": to, "from": frm, "offered": offered, "word": None, "answer": answer, "started": None, "ended": None, "outcome": None,
                 "steps": [], "checks": None, "at": e["At"]}
            E["deploys"].append(d)
            E["open"][to] = d
            return d
        d = E["open"].get(to)
        if act == "ops.offer":
            for o in [o for o in E["open"].values() if o["to"] != to and o["answer"] == "waiting" and not o["started"]]:
                o.update(answer="replaced", at=e["At"])
                del E["open"][o["to"]]
            d or new(e.get("Base"), e["At"], "waiting")
        elif act == "ops.approve" and d and not e.get("Refused"):
            for o in [o for o in E["open"].values() if o["to"] != to and o["answer"] == "approved" and not o["started"]]:
                o.update(answer="replaced", at=e["At"])
                del E["open"][o["to"]]
            d.update(word={"at": e["At"], "by": e.get("By")}, answer="approved", at=e["At"])
        elif act == "ops.deploy":
            phase = e.get("Phase")
            if phase == "start":
                d = d or new(e.get("Base"), None, "unasked")
                d.update({"started": e["At"], "from": e.get("Base") or d["from"], "at": e["At"]})
            elif d and phase == "step":
                d["steps"].append({"step": e.get("Step"), "outcome": e.get("Outcome"), "at": e["At"]})
                try:
                    d["checks"] = json.loads(e["Rows"]) if e.get("Rows") else d["checks"]
                except ValueError:
                    pass
                d["at"] = e["At"]
            elif d and phase == "end":
                d.update(ended=e["At"], outcome=e.get("Outcome"), at=e["At"])
                del E["open"][to]
    out = {}
    for env in sorted(set(envs) | {k[0] for k in steps}):
        E = envs.get(env, {"deploys": [], "open": {}})
        deploys = []
        for d in reversed(E["deploys"]):
            if since and d["at"] < since and not any(d is o for o in E["open"].values()):
                continue
            bolts, why = carried(d["to"], d["from"], lands)
            after = [{"key": key, "state": x.get("State"), "doer": x.get("Doer"), "agent": x.get("Agent"), "at": x["At"], "note": x.get("Note")}
                     for (en, t, key), x in steps.items() if en == env and t == d["to"]]
            row = f"deploy/{env}" if d["answer"] == "waiting" else None
            deploys.append(dict(d, bolts=bolts, bolts_why=why, after=after, row=row))
        waiting = [{"key": key, "to": t or None, "state": x.get("State"), "doer": x.get("Doer"), "agent": x.get("Agent"), "at": x["At"],
                    "text": next((l.strip() for l in (x.get("Text") or "").splitlines() if l.strip()), None), "note": x.get("Note"),
                    "held": held(x), "row": f"op/{env}/{n}" if waits_on_user(x) else None}
                   for n, (en, t, key), x in numbered(steps) if en == env and x.get("State") in WAITING]
        out[env] = {"deploys": deploys, "waiting": waiting}
    return out


# ----------------------------------------------------------------- the deploy's and the step's cards (record 0031)

RELEASE = re.compile(r"^##\s+\[?([^\]\s(]+)", re.M)  # a release's heading in git-cliff's Markdown: ## v0.3.0 (date)
FIELD = re.compile(r"(?:^|\s)[-*]\s+(why|where|command|done):\s*", re.I)  # a field of a step's text, on a line or flattened
CARRIED = ("ok", "done")  # a deploy's end that left its environment running its commit


def doer_of(doer, agent, label, env):
    """Who does a step, as a card names them: the user, the agent it is handed to, or its doer's crew name."""
    return agent or {"main-ops": f"{label}-ops", "dispatcher": f"{label}-dispatch-{env}"}.get(doer, doer)


def handed_steps(text, env, label):
    """The after-deploy steps a deployer hands crew ops offer --steps, one a line, tab-separated, as its
    after-deploy.awk prints them: step <n> <doer> <when> <environments> <why> <text>, held among the when words. Those
    for env, or for every environment when they name none, in the order handed, each {n, text, doer, held}, its doer
    as a card names it: ([steps], None), or (None, why) naming the first line crew can't read (read.1)."""
    out = []
    for i, line in enumerate((text or "").splitlines(), 1):
        if not line.strip():
            continue
        f = line.split("\t", 6)
        if len(f) != 7 or f[0] != "step" or f[2] not in DOERS or not f[6].strip():
            return None, (f"line {i} is no step crew reads: step <n> <doer> <when> <environments> <why> <text>, "
                          f"tab-separated, the doer {', '.join(DOERS[:-1])} or {DOERS[-1]}")
        envs = [x.strip() for x in f[4].split(",") if x.strip()]
        if envs and env not in envs:
            continue
        out.append(dict(n=f[1].strip(), text=f[6].strip(), doer=doer_of(f[2], None, label, env), held="held" in f[3].split()))
    return out, None


def release_of(notes):
    """The release the notes are for, from git-cliff's heading of it; None when they hold none, or several."""
    names = RELEASE.findall(notes or "")
    return names[0] if len(names) == 1 else None


def deploy_facts(env, offer, es, notes=None, steps=None, unread=None):
    """The facts of the deploy's card for env's open offer (cards.deploy_card, plan.14), from the partition's entries
    (es, oldest first: the main level's ops entries and every landing): the environment, the head and the commit it
    runs, None when nothing is deployed; the landings it carries by bolt, from the landing that left main at what it
    runs up to the one at the head, or why they can't be read, naming each host whose record did not answer (unread,
    {host: why}); the notes as handed, their release, and the steps as handed; the environments whose deploy of the
    head has ended done, which it comes after. The deployer hands no order of its environments, so none comes after."""
    to, base = offer["Head"], offer.get("Base")
    base = None if base in (None, "", "none") else base
    bolts, why = carried(to, base or "none", landings(es))
    if bolts is None and unread:
        why += "; " + "; ".join(f"{h} did not answer" for h in sorted(unread))
    before = sorted({env_of(e) for e in es if e.get("Act") == "ops.deploy" and e.get("Phase") == "end" and e.get("Head") == to
                     and e.get("Outcome") in CARRIED and env_of(e) not in (None, env)})
    return dict(env=env, head=to, base=base, landings=[{"pr": None, "subject": b} for b in bolts or []], landings_why=why,
                notes=notes or None, release=release_of(notes), steps=list(steps or []), before=before, after=[])


def deploy_move(es, env, held_card):
    """What the deploy's card of env does now (record 0031 §3), from the partition's ops entries and whether main-level
    ops holds a card under deploy/<env>: ("post", None) when it holds none; ("change", the change note) when the card
    asks for an older offer still unanswered, the note naming the head offered now and the one it replaces; (None,
    why) when nothing is offered, or when the card asks for a deploy the user approved, which closes at that deploy's
    end, the open offer's card raised then."""
    offers, words, _ = state(es)
    offer = offers.get(env)
    if not offer:
        return None, f"no deploy of {env} is offered"
    if not held_card:
        return "post", None
    if env in words:
        return None, (f"its card asks for the deploy of {words[env]['Head'][:7]}, approved, and the offer of "
                      f"{offer['Head'][:7]} is raised once that deploy ends")
    was = [e["Head"] for e in es if e.get("Act") == "ops.offer" and env_of(e) == env and e is not offer and e["Head"] != offer["Head"]
           and (e["At"], e["Id"]) < (offer["At"], offer["Id"])]
    return "change", f"Now offering {offer['Head'][:7]}" + (f", which includes {was[-1][:7]}" if was else "")


def deploy_outcome(es, env, to, outcome, log=None):
    """What the deploy's card closes with at the deploy's end (record 0031 §1): each step of its run with its outcome,
    or the step that failed and its log, from the partition's ops entries since its start."""
    mine = [e for e in es if e.get("Act") == "ops.deploy" and env_of(e) == env and e.get("Head") == to]
    starts = [i for i, e in enumerate(mine) if e.get("Phase") == "start"]
    ran = [e for e in mine[starts[-1] if starts else 0:] if e.get("Phase") == "step" and e.get("Step")]
    failed = next((e for e in ran if e.get("Outcome") == "failed"), None)
    if failed or outcome == "failed":
        at = f" at {failed['Step']}" if failed else ""
        where = (failed or {}).get("Log") or log
        return f"The deploy of {to[:7]} to {env} failed{at}" + (f"; its log: {where}" if where else "") + "."
    return f"Deployed {to[:7]} to {env}" + (": " + ", ".join(f"{e['Step']} {e.get('Outcome') or 'done'}" for e in ran) if ran else "") + "."


def step_words(text):
    """A step's text as the deployer hands it, read as its card's: its words, all it says before its first field, each
    run of spaces one; and its fields, `- why:`, `- where:`, `- command:` (one a command, in order) and `- done:`, each
    running to the next. Read alike from the file's lines and from the run record's one line of it."""
    parts = FIELD.split(" ".join((text or "").split()))
    fields = {"commands": []}
    for name, value in zip(parts[1::2], parts[2::2]):
        if name.lower() == "command":
            fields["commands"].append(value.strip())
        else:
            fields[name.lower()] = value.strip()
    return parts[0].strip(), fields


def step_facts(env, n, e, label, working=None):
    """The facts of a step's card (cards.step_card) from its latest entry: its environment and number, its words and
    fields as its text gives them (step_words), its doer as a card names it, whether it is held, and for a held step
    what doing it now cuts: working, the stage agents working on its host as the card is raised, or why crew could not
    tell (a string)."""
    words, fields = step_words(e.get("Text"))
    doer = "user" if e.get("Doer") == "user" else doer_of(e.get("Doer"), e.get("Agent"), label, env)
    f = dict(env=env, n=n, text=words or e.get("Key"), doer=doer, held=held(e), why=fields.get("why"), where=fields.get("where"),
             commands=fields["commands"], done=fields.get("done"))
    if f["held"]:
        if isinstance(working, str):
            now = f"It runs at once, whatever is working on {env}: crew could not tell what is ({working})"
        elif working:
            now = f"It runs at once, cutting the {'stage' if len(working) == 1 else 'stages'} of {', '.join(working)}"
        else:
            now = f"It runs at once; no stage is working on {env} now"
        f["consequences"] = {"now": now}
    return f


def step_due(es, entries, env):
    """The step on env whose card crew raises now, one at a time (record 0031 §5): the first, by its number, of the
    environment's steps that wait on the user and have had no card under their key, while no step card of the
    environment is open, from the partition's ops entries and this host's card entries (entries, oldest first).
    ((n, (env, to, key), latest entry), None); (None, the open card's key) while one is open; (None, None)."""
    import cards  # its decisions only: what the run record shows posted and closed
    mine = [c for c in cards.posted_cards(entries) if c["key"].startswith(f"op/{env}/")]
    open_ = next((c["key"] for c in mine if c["state"] is None), None)
    if open_:
        return None, open_
    had = {c["key"] for c in mine}
    _, _, steps = state(es)
    due = next(((n, k, e) for n, k, e in numbered(steps) if k[0] == env and waits_on_user(e) and f"op/{env}/{n}" not in had), None)
    return due, None


def step_point(es, entries, key):
    """Whether the point of the step card keyed op/<env>/<n> has come (record 0031 §5): its step waits on the user,
    and it is the card open on its environment, to be raised again, or the next due there while none is open, from
    the partition's ops entries and this host's card entries. ((n, (env, to, key), latest entry), None), or (None,
    why not)."""
    env, n = key.split("/")[1], int(key.split("/")[2])
    due, open_ = step_due(es, entries, env)
    if open_ and open_ != key:
        return None, f"card {open_} is open: this step's card is raised when it closes"
    if open_ == key:
        mine = next((x for x in numbered(state(es)[2]) if x[0] == n and x[1][0] == env and waits_on_user(x[2])), None)
        return (mine, None) if mine else (None, "its step no longer waits on the user")
    if due and due[0] == n:
        return due, None
    return None, "its step waits on no one, or another's card comes first"


# What a step's card shows of it, by what a change note names: its words and fields, its doer, its hold.
SHOWN = (("its words", ("text", "why", "where", "commands", "done")), ("its doer", ("doer",)), ("its hold", ("held",)))


def step_again(es, entries, k, label):
    """What becomes of the open card of the step k, (env, to, key), recorded again waiting on the user (record 0031 §3),
    from the partition's ops entries (es) and this host's entries in the order written (entries): (its card's key,
    its id, the change note or None, whether its kind changed); None when the step's own card is not open. The card
    shows the step's latest entry before the card's last post or change, and is changed when its words, its doer or
    its hold differ from the step as recorded now (step_facts, but for what a held step cuts, read as it is raised),
    the note naming which; its kind, a `do` for the user's step and a choice for an agent's held, changes when its doer
    changes between the user and an agent. A card whose step's entry this host's record no longer reaches before it is
    changed to the step as recorded, since what it shows can't be read (read.1)."""
    import cards  # its decisions only: what the run record shows posted and closed
    steps = state(es)[2]
    n = next((n for n, x, _ in numbered(steps) if x == k), None)
    env = k[0]
    key = f"op/{env}/{n}"
    card = cards.card_under(entries, key, f"{label}-ops") if n else None
    if not card:
        return None
    latest, shown = None, None
    for e in entries:
        if e.get("Act") == "ops.step" and (env_of(e), e.get("Head") or "", e.get("Key")) == k:
            latest = e
        elif e.get("Act") in ("card.post", "card.update") and not e.get("Refused") and (e.get("Card"), e.get("Key")) == (card, key):
            shown = latest
    if shown is None:
        return key, card, "Recorded again", False
    was, now = step_facts(env, n, shown, label), step_facts(env, n, steps[k], label)
    what = [w for w, fields in SHOWN if any(was[f] != now[f] for f in fields)]
    note = "Recorded again: " + cards.joined(what) + " changed" if what else None
    return key, card, note, (was["doer"] == "user") != (now["doer"] == "user")


def word_stands(key, es):
    """Whether a row's card under key outlives its row: a deploy's, deploy/<env>, once the user's word for it is given
    and its deploy's end not yet recorded, which closes it with the outcome (record 0031 §1), from the partition's
    entries; the rail's sweep leaves it, and lists it as no stray."""
    kind, _, env = (key or "").partition("/")
    return kind == "deploy" and env in state(es)[1]


def kept(label, env, to):
    """Where an offer keeps the files it was handed, on the main level's host, so its card is built again the same:
    never in the run record (record.3)."""
    return record.ROOT / label / "ops" / env / to


def kept_text(path):
    try:
        return path.read_text()
    except OSError:
        return None


def ops_where(fleet, label):
    """Where main-level ops's cards are asked from and filed: the partition's blueprints checkout, its own place."""
    import plan
    p = crew.partition_of(fleet, label)
    return plan.card_where({"main": p["checkout"], "repo": p["blueprints"][0]})


def raise_deploy(fleet, row, acts=None):
    """Raise the deploy's card of the rail row deploy/<env> of row["label"] (record 0031 §1, plan.14): posted in
    main-level ops's name, following the card follows_of names, or changed in place when the card ops holds asks for
    an older offer still unanswered, posted again when Pending You no longer finds it; built from the open offer, the
    files it was handed and the partition's run record. None, saying why, when no offer waits on a card; the offer's
    own call and the rail's sweep alike. A card not posted or changed is said and recorded, and the offer stands.
    The card's id, or None."""
    import cards, plan
    acts = acts or plan.CardActs(fleet)
    label, key = row["label"], row["key"]
    env, owner = key.split("/", 1)[1], f"{label}-ops"
    es = entries(label)
    move, said = deploy_move(es, env, cards.card_under(acts.entries(label), key, owner))
    if not move:
        print(f"card {key}: {said}")
        return None
    offer = state(es)[0][env]
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=DAYS)).isoformat()
    gathered, unread = record.gather(fleet, [label], since)
    lands = sorted({e["Id"]: e for e in es + [e for e in gathered if e.get("Act") == "bolt.land"]}.values(), key=lambda e: (e["At"], e["Id"]))
    d = kept(label, env, offer["Head"])
    steps, _ = handed_steps(kept_text(d / "steps.txt"), env, label)
    facts = deploy_facts(env, offer, lands, kept_text(d / "notes.md"), steps, unread)
    facts["follows"] = cards.follows_of("deploy", {"env": env, "head": offer["Head"]}, gathered)
    return plan.row_card_change(fleet, label, owner, cards.deploy_card, facts, said or "Raised again", ops_where(fleet, label), acts)


def stages_working(fleet, env):
    """The stage agents working on env's host, a list; or why crew could not tell, a string. An environment that is
    no host of the fleet runs no team."""
    out = []
    for t in sorted((t for t in fleet["teams"].values() if t["machine"] == env), key=lambda t: t["name"]):
        for n in range(1, t["units"] + 1):
            agent, unread = crew.read_agent(fleet, f"{t['name']}-unit-{n}")
            if unread:
                return f"{t['name']}-unit-{n}: {unread}"
            if agent and agent.get("agent_status") == "working":
                out.append(f"{t['name']}-unit-{n}")
    return out


def raise_step(fleet, row, acts=None, note="Raised again", kind_changed=False):
    """Raise the card of the rail row op/<env>/<n> of row["label"], a step that waits on the user, one at a time
    (record 0031 §5): posted in main-level ops's name, following the deploy's card or the step card before it, once its
    point has come (step_point), and posted again when Pending You no longer finds it; while its card is open, changed
    with note, or followed by a new card when its kind changed (step_again). None, saying why, before then; the step's
    own call and the rail's sweep alike. The card's id, or None."""
    import cards, plan
    acts = acts or plan.CardActs(fleet)
    label, key = row["label"], row["key"]
    env, mine = key.split("/")[1], acts.entries(label)
    step, why = step_point(entries(label), mine, key)
    if not step:
        print(f"card {key}: {why}")
        return None
    n, _, e = step
    facts = step_facts(env, n, e, label, stages_working(fleet, env) if held(e) else None)
    facts["follows"] = cards.follows_of("step", {"env": env, "key": key}, mine)
    return plan.row_card_change(fleet, label, f"{label}-ops", cards.step_card, facts, note, ops_where(fleet, label), acts, kind_changed)


def raise_next_step(fleet, label, env, k=None):
    """Raise the card of the step on env that waits on the user next, unless a step card of env is open (step_due).
    The step k, (env, to, key), just recorded waiting on the user while its own card is open, has that card changed
    when what it shows differs (step_again), and the line that adopts it printed either way, as a raise prints it."""
    import plan
    acts = plan.CardActs(fleet)
    es, mine = entries(label), acts.entries(label)
    again = step_again(es, mine, k, label) if k else None
    if again:
        key, card, note, kind_changed = again
        if not note:
            print(f"card {key}: {card} shows the step as recorded, so it is not changed")
        new = raise_step(fleet, {"label": label, "key": key}, acts, note, kind_changed) if note else None
        if new in (None, card):
            plan.card_heard(acts, key, card, f"{label}-ops")
        return new or card
    due, open_ = step_due(es, mine, env)
    if open_:
        print(f"card {open_} is open: the next step's card is raised when it closes")
    return raise_step(fleet, {"label": label, "key": f"op/{env}/{due[0]}"}, acts) if due else None


def emit(label, act, env, why, refused=None, **fields):
    eid = record.emit(label, act, [f"env/{env}"], why=f"ops({env}): {why}", refused=refused, **fields)
    eid or fail(f"the operation's {act} could not be recorded in {label}'s run record")


def handed(path, what):
    """A file the deployer hands an offer, as text; refused naming it when it can't be read, nothing offered (read.1)."""
    try:
        return pathlib.Path(path).read_text()
    except (OSError, UnicodeDecodeError) as e:
        fail(f"the {what} file {path} can't be read: {getattr(e, 'strerror', None) or e}; nothing is offered")


def offer(fleet, a):
    notes = handed(a.notes, "release notes") if a.notes else None
    steps = handed(a.steps, "steps") if a.steps else None
    _, why = handed_steps(steps, a.env, a.label)
    why is None or fail(f"the steps file {a.steps} can't be read: {why}; nothing is offered")
    offers, _, _ = state(entries(a.label))
    if offers.get(a.env, {}).get("Head") == a.to:
        return
    d = kept(a.label, a.env, a.to)
    try:
        d.mkdir(parents=True, exist_ok=True)
        for name, text in (("notes.md", notes), ("steps.txt", steps)):
            (d / name).unlink(missing_ok=True)
            text is None or (d / name).write_text(text)
    except OSError as e:
        fail(f"crew can't keep what the offer was handed in {d}: {e.strerror or e}; nothing is offered")
    emit(a.label, "ops.offer", a.env, f"offer a deploy of {a.to[:7]}", Head=a.to, Base=getattr(a, "from"))
    raise_deploy(fleet, {"label": a.label, "key": f"deploy/{a.env}"})


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
    _, words, _ = state(entries(a.label))
    emit(a.label, "ops.deploy", a.env, f"deploy {a.to[:7]}: {a.act}" + (f" {a.step}" if a.step else ""), Head=a.to,
         Base=getattr(a, "from"), Phase=a.act, Step=a.step, Outcome=a.outcome, Log=a.log, Rows=rows_)
    if a.act != "end":
        return
    import plan
    es = entries(a.label)
    if words.get(a.env, {}).get("Head") == a.to:
        plan.row_card_close(fleet, a.label, f"{a.label}-ops", f"deploy/{a.env}", outcome=deploy_outcome(es, a.env, a.to, a.outcome, a.log))
    if state(es)[0].get(a.env):
        raise_deploy(fleet, {"label": a.label, "key": f"deploy/{a.env}"})


CLOSED = {"done": "Done.", "declined": "Skipped."}  # what a step's card closes with when the step is marked so


def step(fleet, a):
    text = None
    if a.text:
        try:
            text = pathlib.Path(a.text).read_text()
        except OSError as e:
            fail(f"the step's text {a.text} can't be read: {e.strerror or e}")
    emit(a.label, "ops.step", a.env, f"{a.key} {a.state}", Head=a.to, Key=a.key, State=a.state, Doer=a.doer, Agent=a.agent,
         When=" ".join(w for w in (a.when, "held" if a.held else None) if w), Text=text, Changes=a.changes, Note=a.note)
    if a.state in CLOSED:
        import cards, plan
        owner, n = f"{a.label}-ops", next(n for n, k, _ in numbered(state(entries(a.label))[2]) if k == (a.env, a.to or "", a.key))
        if cards.card_under(plan.CardActs(fleet).entries(a.label), f"op/{a.env}/{n}", owner):
            plan.row_card_close(fleet, a.label, owner, f"op/{a.env}/{n}", outcome=CLOSED[a.state])
    if a.state in CLOSED or a.state == "waiting" and (a.doer == "user" or a.held):
        raise_next_step(fleet, a.label, a.env, (a.env, a.to or "", a.key) if a.state == "waiting" else None)


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
    p.add_argument("--notes")
    p.add_argument("--steps")
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
    p.add_argument("--doer", choices=DOERS)
    p.add_argument("--agent")
    p.add_argument("--when", choices=("deployed", "quiet"))
    p.add_argument("--held", action="store_true")
    p.add_argument("--text")
    p.add_argument("--changes")
    p.add_argument("--note")
    p = cmd("steps", to=False)
    p.add_argument("--json", action="store_true", required=True)
    cmd("quiet", to=False)
    return ap


def args_refusal(fleet, a):
    """Why crew ops refuses what it was given, or None: an environment's name, a partition of the teams file, a
    commit as a sha in hex (--from none for nothing deployed), a step key crew takes, and --held only on an agent's
    step, since a user's waits on the user already."""
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
    if getattr(a, "held", False) and a.doer in (None, "user"):
        return "--held marks an agent's step held for the user's word: give its --doer, dispatcher or main-ops"
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
