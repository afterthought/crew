"""A kit's policy, as sluice reads it, and what crew reads of a kit's main and its bolts (plan.18, plan.19).

A kit says what gates its branches, where each branch lives and whether it declares a preview once, in sluice's words:
the policy file DECLARATION, read at the revision in hand. crew readies no place: a unit's, chore's and fix's places
are Flume's, readied by its kind and the kit's own files. sluice stands on its own, and flywheel will use sluice's SDK
for these same reads; the file becomes flywheel.toml then, and DECLARATION is the one name that changes.

These are the decisions, each a function of plain facts (code.7); plan.py runs their reads on the team's host."""
import base64
import binascii
import re
import tomllib

import crew
import gather

DECLARATION = ".config/sluice.toml"


def previewed(text, where=DECLARATION):
    """Whether a kit's DECLARATION, as a revision holds it, declares a preview of that revision, as sluice reads it
    there (sluice record 0021): True when its TOML holds a [preview] table, False when there is no file or no table.
    Refused, naming the file, when it is not TOML or `preview` is not a table (read.1)."""
    if text is None:
        return False
    try:
        preview = tomllib.loads(text).get("preview")
    except tomllib.TOMLDecodeError as e:
        crew.fail(f"{where} is not TOML, so crew can't read whether the kit declares a preview: {e}")
    if preview is not None and not isinstance(preview, dict):
        crew.fail(f"{where}: [preview] is a table, not {type(preview).__name__}")
    return preview is not None


# How a landing sluice made names its verdict: a trailer on its merge commit (sluice record 0006), as
# `Sluice-Result: passed (9 run, 0 replayed)`. sluice lands nothing that did not pass.
VERDICT = "Sluice-Result"


# How a policy's branches are matched, as sluice matches them: gather's, since gather.py is sent to hosts on its own
# and reads where each bolt lives (gather.bolt_read).
branch_table = gather.branch_table


def bolt_checks(text, kit, where=DECLARATION, branch="bolt/a-bolt", ref="main"):
    """The checks a kit's policy requires of its bolt branches (teams.5, record 0026): the `required` list of the
    [branches."<pattern>"] table whose pattern matches a bolt's branch, the most specific first, as sluice matches it,
    in the policy as the kit's main holds it now (ref, origin/main for a kit on GitHub, plan.18). Refused, naming the
    file and the ref, when the kit has none, it is not TOML, or no table names bolt branches with a check: a kit merges
    and lands only through sluice, so crew starts none of its bolts until its policy says what gates one."""
    if text is None:
        crew.fail(f"{kit} merges only through sluice, and has no {where} on {ref}: write one whose "
                  f"[branches.\"bolt/*\"] names the checks a bolt's merges must pass, then start the bolt again")
    try:
        branches = tomllib.loads(text).get("branches", {})
    except tomllib.TOMLDecodeError as e:
        crew.fail(f"{kit}'s {where} is not TOML, so crew can't read what gates its bolt branches: {e}")
    table = branch_table(branches, branch)
    required = table.get("required") if table else None
    if not (isinstance(required, list) and required and all(isinstance(r, str) and r for r in required)):
        crew.fail(f"{kit} merges only through sluice, and its {where} names no checks for its bolt branches: give "
                  f"[branches.\"bolt/*\"] a `required` list of the checks a bolt's merges must pass, then start the bolt again")
    return required


def bolt_remote(text, branch="bolt/a-bolt", where=DECLARATION):
    """The remote a kit's policy names for a branch, as sluice routes it (plan.19, its rule core.15): the `remote` of the
    [branches."<pattern>"] table that matches the branch, the most specific first, as bolt_checks matches it, when it is
    a non-empty string; None for no policy (text None), no matching table or no remote, which sluice reads as a branch
    kept in the host's own refs. Refused, naming the file, when it is not TOML (read.1)."""
    try:
        return gather.policy_remote(text, branch)
    except ValueError as e:
        crew.fail(f"{where} is not TOML, so crew can't read where sluice keeps {branch}: {e}")


def takes_pulls(text, where=DECLARATION):
    """Whether a kit's policy takes pull requests into main, as sluice reads it: True when the [branches."<pattern>"]
    table that matches main, the most specific first, holds a `pull_requests` table, so a landing opens a pull request
    from the bolt's branch that sluice's intake submits while it is out of draft; False for no policy (text None) or no
    such table. Refused, naming the file, when it is not TOML or `pull_requests` is not a table (read.1)."""
    if text is None:
        return False
    try:
        branches = tomllib.loads(text).get("branches", {})
    except tomllib.TOMLDecodeError as e:
        crew.fail(f"{where} is not TOML, so crew can't read whether its main takes pull requests: {e}")
    table = branch_table(branches, "main")
    pulls = table.get("pull_requests") if table else None
    if pulls is not None and not isinstance(pulls, dict):
        crew.fail(f"{where}: [branches.main.pull_requests] is a table, not {type(pulls).__name__}")
    return pulls is not None


# What crew reads of a pull request, as `gh pr list --json number,isDraft,headRefOid,url` prints each (gh 2.102.0,
# read 2026-10-22 on afterthought/crew), and the key crew keeps it under.
PULL_FIELDS = (("number", int, "number"), ("isDraft", bool, "draft"), ("headRefOid", str, "head"), ("url", str, "url"))


def pull_said(code, out, err, repo, bolt):
    """The one open pull request from bolt/<bolt> into main on GitHub's repo, from what `gh pr list` printed and its
    exit: {number, draft, head, url}, or None when there is none. Refused, naming the repository and gh's words, when gh
    exited non-zero; and when what it printed is not a list of pull requests with those fields, or lists more than one,
    since crew can't tell which is the landing's (read.1, read.2)."""
    import json
    what = f"{repo}'s open pull request from bolt/{bolt} into main"
    if code != 0:
        said = ((err or "").strip() or (out or "").strip()).splitlines()
        crew.fail(f"crew can't read {what}: gh exited {code}: {said[-1].strip() if said else 'gh said nothing'}")
    try:
        doc = json.loads(out or "")
    except ValueError:
        doc = None
    sha = re.compile(r"[0-9a-f]{40,64}")
    ok = lambda p: (isinstance(p, dict) and all(isinstance(p.get(k), t) and (t is bool or not isinstance(p.get(k), bool))
                                                 for k, t, _ in PULL_FIELDS)
                    and sha.fullmatch(p["headRefOid"]) and p["url"].startswith("https://"))
    if not (isinstance(doc, list) and all(ok(p) for p in doc)):
        crew.fail(f"crew can't read {what} from what gh printed: {(out or '').strip()[:200] or 'nothing'}")
    if len(doc) > 1:
        crew.fail(f"crew can't tell {what}: gh lists {len(doc)}, " + " and ".join(p["url"] for p in doc))
    return {key: doc[0][k] for k, _, key in PULL_FIELDS} if doc else None


def pull_marked(code, out, err):
    """What PULL_MARK said of `gh pr ready`: (gh's exit, gh's last line), or, when it did not run there, (the host's
    exit, its own words), so a non-zero exit is never read as marked (read.2)."""
    f = said_of(out)
    try:
        if code == 0:
            return int(f["RC"]), " ".join(base64.b64decode(f["SAID"], validate=True).decode(errors="replace").split())
    except (KeyError, ValueError, binascii.Error):
        pass
    said = ((err or "").strip() or (out or "").strip()).splitlines()
    return (code or 1), (said[-1].strip() if said else f"exit {code}")


def give_remote(text, kit, where=DECLARATION, branch="bolt/a-bolt", ref="origin/main"):
    """The remote a start has sluice make a bolt's branch on (plan.19): the one the kit's policy at its main now names
    for its bolt branches (bolt_remote). Refused, naming the file and the key, when it names none, since crew gives
    bolts only on GitHub and writing the key is the kit's own change (plan.17)."""
    return bolt_remote(text, branch, where) or crew.fail(
        f"{kit} starts bolts only on GitHub, and its {where} on {ref} names no remote for its bolt branches: its "
        f"[branches.\"bolt/*\"] needs `remote = \"origin\"`, which is the kit's own change (plan.17), then start the bolt again")


# The first sluice with `branch create` and `branch delete` (sluice ADR 0026, v0.20.0), which a start and a land need.
SLUICE_BRANCHES = (0, 20, 0)


def sluice_version(out):
    """The version `sluice --version` printed, as (major, minor, patch), or None when it printed nothing crew can read as
    `sluice X.Y.Z` (sluice 0.36.4 prints `sluice 0.36.4`, tests/py/sluice-0.36.4/version.txt)."""
    m = re.fullmatch(r"sluice (\d+)\.(\d+)\.(\d+)", (out or "").strip())
    return tuple(int(n) for n in m.groups()) if m else None


def sluice_refusal(out, host):
    """Why a start can't go through the host's sluice, or None (plan.19, read.1): its version is below SLUICE_BRANCHES,
    which has no `branch create`, or `sluice --version` printed nothing crew can read; naming the version needed and
    the host's own words."""
    v = sluice_version(out)
    if v is not None and v >= SLUICE_BRANCHES:
        return None
    said = " ".join((out or "").split())[:120] or "nothing"
    return (f"a bolt is started through sluice 0.20.0 or later, which has `branch create`, and sluice --version on {host} "
            f"said: {said}")


def branch_said(out, code):
    """What sluice's `branch create` or `branch delete` said with --json (read.2, as sluice 0.36.4 says it,
    tests/py/sluice-0.36.4/): (the commit it made the branch at or removed it from, None) for its document of a branch
    made or removed, exit 0; (None, its message) for its refusal, {"error": {"kind", "message"}}, exit 1 when the
    branch or the one it is made from is not there, 2 when it refused, 3 on its own failure. Refused, naming what it
    said, on anything else."""
    import json
    try:
        doc = json.loads(out or "")
    except ValueError:
        doc = None
    sha = re.compile(r"[0-9a-f]{40,64}")
    if code == 0 and isinstance(doc, dict) and isinstance(doc.get("branch"), str):
        made = doc.get("created", doc.get("deleted"))
        if isinstance(made, str) and sha.fullmatch(made):
            return made, None
    err = doc.get("error") if isinstance(doc, dict) else None
    if code in (1, 2, 3) and isinstance(err, dict) and isinstance(err.get("message"), str) and err["message"]:
        return None, err["message"]
    crew.fail(f"crew can't read what sluice's branch command said (exit {code}): {(out or '').strip()[:200] or 'nothing'}")


def bolt_lives(said, bolt):
    """Where a bolt's branch lives, as sluice routes it (plan.19): the remote the policy at the host's own bolt/<bolt>
    names for it, or at origin/bolt/<bolt> when the host has no branch of its own; None for a bolt made before gives
    went through sluice, kept in its host's refs. said is what BOLT_AT printed in the kit's main checkout: LOCAL and
    TRACKED, the commit of each ref or -, and AT_LOCAL and AT_TRACKED, the policy at each, base64, or - when that
    revision holds none. Refused when the host has neither ref, or the output is not BOLT_AT's (read.1, read.2)."""
    f = said_of(said)
    if not {"LOCAL", "TRACKED", "AT_LOCAL", "AT_TRACKED"} <= set(f):
        crew.fail(f"crew can't read where bolt/{bolt} lives from: {(said or '').strip()[:200] or 'nothing'}")
    where = "LOCAL" if f["LOCAL"] != "-" else "TRACKED" if f["TRACKED"] != "-" else None
    where or crew.fail(f"crew can't tell where bolt/{bolt} lives: this host has neither bolt/{bolt} nor origin/bolt/{bolt}")
    at = f[f"AT_{where}"]
    try:
        text = None if at == "-" else base64.b64decode(at, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError) as e:
        crew.fail(f"crew can't read bolt/{bolt}'s {DECLARATION} as it was sent: {e}")
    return bolt_remote(text, f"bolt/{bolt}", f"{DECLARATION} at bolt/{bolt}")


def bolt_home(said, bolt):
    """Where a bolt lives (bolt_lives) and the remote the policy at its kit's main now names for its bolt branches
    (bolt_remote), from what BOLT_HOME printed: (the bolt's remote or None, main's remote or None). Refused as
    bolt_lives refuses, and when AT_MAIN is not there or can't be read (read.2)."""
    lives = bolt_lives(said, bolt)
    at = said_of(said).get("AT_MAIN")
    at is not None or crew.fail(f"crew can't read the policy at main from: {(said or '').strip()[:200] or 'nothing'}")
    try:
        text = None if at == "-" else base64.b64decode(at, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError) as e:
        crew.fail(f"crew can't read main's {DECLARATION} as it was sent: {e}")
    return lives, bolt_remote(text, f"bolt/{bolt}", f"{DECLARATION} at main")


def place_base(said, bolt):
    """The ref a new place of a bolt is cut from and tracks, from where the bolt lives (bolt_lives, plan.19):
    origin/bolt/<bolt> for a bolt on GitHub, which PLACE fetches first, so the place holds every merge sluice landed
    there from any host; the host's own bolt/<bolt> for a bolt made before gives went through sluice."""
    return f"origin/bolt/{bolt}" if bolt_lives(said, bolt) else f"bolt/{bolt}"


def land_copies(said, bolt):
    """What LAND_COPIES printed of a bolt's two copies for its landing (plan.19), as {"own", "there", "remote", "held",
    "ahead", "lacks", "beyond", "read"}: read, git's words when origin could not be asked or fetched, the rest None;
    there "-" when the kit has no origin or origin has no bolt/<bolt>; else there, origin's commit, and remote, what the
    policy at it names for the bolt's branch (bolt_remote), or None; own, the host's commit, or "-" when it has none;
    held "yes" or "no", whether origin's holds the host's, "yes" when the host has none; ahead "yes" or "no", whether
    the host's holds origin's; and lacks and beyond, how many merges the host's holds beyond origin's and origin's
    beyond the host's; ahead, lacks and beyond None when the host has no copy. Refused, naming what was printed, on
    anything else (read.2), and when the policy at origin's copy is not TOML."""
    f = said_of(said)
    none = dict(own=None, there=None, remote=None, held=None, ahead=None, lacks=None, beyond=None, read=None)
    if "READ" in f:
        return {**none, "read": f["READ"].strip() or "git said nothing"}
    if f.get("THERE") == "-":
        return {**none, "there": "-"}
    sha = re.compile(r"[0-9a-f]{40,64}")
    own, at = f.get("OWN") or "", f.get("AT_THERE") or ""
    mine = own != "-"
    count = (lambda v: (v or "").isdigit()) if mine else (lambda v: v == "-")
    if not (sha.fullmatch(f.get("THERE") or "") and (sha.fullmatch(own) or not mine) and at
            and f.get("HELD") in (("yes", "no") if mine else ("yes",))
            and f.get("AHEAD") in (("yes", "no") if mine else ("-",)) and count(f.get("LACKS")) and count(f.get("BEYOND"))):
        crew.fail(f"crew can't read bolt/{bolt}'s copies for its landing from: {(said or '').strip()[:200] or 'nothing'}")
    try:
        text = None if at == "-" else base64.b64decode(at, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError) as e:
        crew.fail(f"crew can't read origin/bolt/{bolt}'s {DECLARATION} as it was sent: {e}")
    return dict(own=own, there=f["THERE"], remote=bolt_remote(text, f"bolt/{bolt}", f"{DECLARATION} at origin/bolt/{bolt}"),
                held=f["HELD"], ahead=f["AHEAD"] if mine else None, lacks=int(f["LACKS"]) if mine else None,
                beyond=int(f["BEYOND"]) if mine else None, read=None)


def bolt_found(said, bolt):
    """What BOLT_FOUND printed of a bolt's branch sluice refused to make (plan.19), as {"own", "there", "main", "read"}:
    read, git's words when the remote could not be asked, the rest None; else own, the host's own bolt/<bolt>, and
    there and main, the remote's bolt/<bolt> and main, each a commit or None where there is no such branch. Refused,
    naming what was printed, on anything else (read.2)."""
    f = said_of(said)
    if "READ" in f:
        return dict(own=None, there=None, main=None, read=f["READ"].strip() or "git said nothing")
    sha = re.compile(r"[0-9a-f]{40,64}")
    keys = ("OWN", "THERE", "MAIN")
    if not all(f.get(k) == "-" or sha.fullmatch(f.get(k) or "") for k in keys):
        crew.fail(f"crew can't read bolt/{bolt} as sluice found it from: {(said or '').strip()[:200] or 'nothing'}")
    return dict(read=None, **{k.lower(): None if f[k] == "-" else f[k] for k in keys})


def delete_ran(said):
    """sluice's document and exit as BOLT_DELETE printed them, SAID, base64, and RC (read.2): (document, exit). Refused,
    naming what was printed, when they are not there."""
    f = said_of(said)
    try:
        return base64.b64decode(f["SAID"]).decode(), int(f["RC"])
    except (KeyError, ValueError, UnicodeDecodeError):
        crew.fail(f"crew can't read what sluice's branch delete said from: {(said or '').strip()[-200:] or 'nothing'}")


def verification(head, result):
    """A bolt's verification (tests.5, record 0025): sluice's verdict on the bolt's last landing, read from its head's
    VERDICT trailer, as (state, words): "green" when the head is a landing sluice made, which it makes only on a pass;
    "none" when its head is no landing of sluice's (nothing has landed on the bolt since it was cut, or a commit came
    another way); "unknown" when there is no head to read. Never green on anything but sluice's own trailer."""
    if not head:
        return "unknown", "no head crew can read"
    result = (result or "").strip()
    if not result:
        return "none", f"its head {head[:7]} is no landing of sluice's, so it has no verdict"
    if result.split()[0] == "passed":
        return "green", f"sluice's verdict on its last landing, {head[:7]}: {result}"
    return "unknown", f"its head {head[:7]} carries a verdict crew does not read as a pass: {result}"


def said_of(out):
    """The KEY=value lines a script printed, as {key: value}."""
    return dict(line.split("=", 1) for line in (out or "").splitlines() if "=" in line)


def main_now(out, kit, host):
    """Which of a kit's mains is its main now, from what MAINS read in its main checkout on its host (plan.18): (ref,
    sha, None), or (None, None, why). A kit with an origin remote has its main on GitHub, where sluice lands every
    branch and which the host's own main lags on every host that did not land, so main now is origin/main after the
    command's one fetch, and a fetch that failed or an origin with no main refuses (read.1); a kit with no origin
    remote has no GitHub to lag, so its own main is main now. What is not MAINS's words refuses too (read.2)."""
    said = said_of(out)
    sha = re.compile(r"[0-9a-f]{40,64}")
    origin, fetched, github, own = said.get("ORIGIN"), said.get("FETCHED"), said.get("GITHUB"), said.get("OWN")
    if origin not in ("yes", "no") or not all(v == "-" or (v and sha.fullmatch(v)) for v in (github, own)):
        return None, None, f"crew can't read what {kit}'s main on {host} holds: {(out or '').strip()[:200] or 'nothing was said'}"
    if origin == "yes":
        if fetched != "ok":
            return None, None, f"cannot fetch {kit} from GitHub on {host}, so cannot read its main now: {(fetched or 'no word').strip()}"
        return ("origin/main", github, None) if github != "-" else (None, None, f"{kit}'s GitHub has no main, fetched on {host}")
    return ("main", own, None) if own != "-" else (None, None, f"{kit}'s main checkout on {host} has no branch main and no origin")


def policy_said(out, kit, host):
    """What POLICY printed of a kit's policy at its main now (main_now): (the policy text, or None when that main holds
    none; the ref, origin/main or main; the commit). Refused when main now can't be told or the output is not POLICY's
    (read.1, read.2)."""
    ref, sha, why = main_now(out, kit, host)
    if why:
        crew.fail(why)
    text = said_of(out).get("AT_GITHUB" if ref == "origin/main" else "AT_OWN")
    if text is None:
        crew.fail(f"crew can't read what {kit}'s main holds of {DECLARATION} from: {(out or '').strip()[:200] or 'nothing'}")
    if text == "-":
        return None, ref, sha
    try:
        return base64.b64decode(text).decode(), ref, sha
    except (binascii.Error, UnicodeDecodeError) as e:
        crew.fail(f"crew can't read {kit}'s {DECLARATION} as it was sent: {e}")
