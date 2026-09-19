#!/usr/bin/env python3
"""crew.py: read crew.yaml and answer from it.

  crew.py teams                       every team's name
  crew.py env <team>                  the team's settings as shell assignments
  crew.py brief <team> <role> [name]  the role's brief for that team; name is the agent's own name

A brief is roles/<role>.md with its {{TOKENS}} filled. Every token is built here from the team's
data; a token with no builder, or data a builder needs and the team lacks, is an error, never blank text."""
import json, pathlib, re, shlex, subprocess, sys

LIB = pathlib.Path(__file__).resolve().parent
HOME = LIB.parent.parent
ROLES = ("conductor", "fable", "explorer", "ops", "coder", "verifier", "builder")


def load():
    out = subprocess.run(["yq", "-o=json", ".", str(HOME / "crew.yaml")], check=True, capture_output=True).stdout
    return json.loads(out)


def team_of(data, name):
    for t in data["teams"]:
        if t["name"] == name:
            machine = next((m for m in data["machines"] if m["name"] == t["machine"]), None)
            if machine is None:
                sys.exit(f"team {name} runs on {t['machine']}, which crew.yaml does not define")
            root = machine["org_roots"].get(t["org"]) or sys.exit(f"machine {machine['name']} has no org root for {t['org']}")
            t = dict(t, _machine=machine, _root=root)
            for repo in ("kit", "design"):
                t[repo] = dict(t[repo], abs=f"{root}/{t[repo]['path']}")
            return t
    sys.exit(f"no team '{name}'. teams: " + " ".join(t["name"] for t in data["teams"]))


def names(t):
    n = {r: f"{t['name']}-{r}" for r in ("conductor", "fable", "explorer", "ops", "verifier")}
    n["coders"] = [f"{t['name']}-coder-{i}" for i in range(1, int(t.get("coders", 1)) + 1)]
    return n


def reports(t):
    return f"~/.local/state/{t['name']}-team/reports"


def env(t):
    m, w = t["_machine"], t.get("worktree") or {}
    pairs = {
        "TEAM": t["name"], "SYSTEM": t["system"], "ORG": t["org"], "MACHINE": m["name"], "SSH_TARGET": m.get("ssh") or "",
        "SESSION": t["session"], "CREW_HOME": m["crew_home"], "KIT": t["kit"]["abs"], "KIT_NAME": t["kit"]["name"],
        "DESIGN": t["design"]["abs"], "CODERS": str(int(t.get("coders", 1))), "WORKTREE_PREPARE": w.get("prepare") or "",
        "REPORTS": reports(t),
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items()) + f'\nSTATE="$HOME/.local/state/{t["name"]}-team"'


def place(t, item):
    return f"{t[item['repo']]['name']} `{item['path']}`"


def build_tokens(t, self_name):
    n, kit, design = names(t), t["kit"], t["design"]
    coders = ", ".join(f"`{c}`" for c in n["coders"])
    homes = t["design_homes"]
    tok = {
        "SELF": self_name or "", "TEAM": t["name"], "SYSTEM": t["system"], "KIT": kit["abs"], "KIT_NAME": kit["name"],
        "DESIGN_NAME": design["name"], "CONDUCTOR": n["conductor"], "FABLE": n["fable"], "EXPLORER": n["explorer"],
        "OPS": n["ops"], "VERIFIER": n["verifier"], "CODER_NAMES": coders, "CODERS": str(len(n["coders"])),
        "TEAM_CMD": f"{t['_machine']['crew_home']}/plugin/bin/crew", "REPORTS": reports(t),
        "FULL_SUITE": t["full_suite"], "MERGE": t["merge"],
    }
    tok["ROSTER"] = (
        f"The team: `{n['conductor']}` (Opus) keeps the coders building and reports where things stand; `{n['fable']}` (Fable) owns "
        f"{t['system']}'s design and reviews each change before it is built; `{n['explorer']}` (Opus) writes the OpenSpec changes and the "
        f"backlog in {kit['name']}; the coders ({coders}, Opus) each build one whole change at a time in that change's own worktree; "
        f"`{n['verifier']}` (Opus) is started only to run OpenSpec's verify on a finished change; and `{n['ops']}` (Opus) does everything "
        f"that touches a live system: dev AWS, GitHub, the vendors' consoles and APIs, sign-in, debugging, proofs and the full suite on main.")

    by_repo = {}
    for item in t["record"]:
        by_repo.setdefault(item["repo"], []).append(f"`{item['path']}` ({item['holds']})")
    lines = []
    for repo, items in by_repo.items():
        r = t[repo]
        here = " Its CLAUDE.md says how work is done there. Run `openspec` commands from that directory." if repo == "kit" else ""
        lines.append(f"- {r['name']}, `{r['abs']}`: " + ", ".join(items) + "." + here)
    tok["RECORD"] = "\n".join(lines)

    where = []
    for h in homes:
        r = t[h["repo"]]
        s = f"- {h['holds'][0].upper() + h['holds'][1:]}: the page of `{h['path']}` in {r['name']} (`{r['abs']}`) that covers it"
        if h.get("style"):
            s += f", written the way `{h['style']}` says"
        s += ". Amend the page that already covers it before adding a new one."
        if h.get("only_when"):
            s += f" Change one only when {h['only_when']}."
        where.append(s)
    where.append("- If you edit `context-map/maps/`, run `node context-map/bin/map-check.mjs --write` afterwards.")
    tok["WHERE"] = "\n".join(where)
    tok["FABLE_RECORDS"] = "in " + " and ".join(place(t, h) for h in homes)
    tok["DESIGN_DOCS"] = " or ".join(f"`{h['path']}`" for h in homes)
    tok["CITE"] = f"the pages of `{homes[0]['path']}`"
    tok["DONT_EDIT"] = "Don't edit " + ", ".join(f"`{h['path']}`" for h in homes) + f" or {kit['name']}'s `openspec/` yourself."
    tok["PLAN_EXAMPLE"] = f", such as `{t['plans'][0]}`" if t.get("plans") else ""
    tok["TIER"] = f"the tier it is proven at (`{t['proof_tiers']}`)" if t.get("proof_tiers") else "how it is proven"

    emu, w = t.get("emulator") or {}, t.get("worktree") or {}
    prove = [f"Prove your work in the worktree with the unit tests: `{t['unit_tests']}`." if t.get("unit_tests")
             else "Prove your work in the worktree with the tests beside what you touched."]
    if emu:
        never = " or ".join(f"`{c}`" for c in emu.get("never_from_a_worktree", []))
        prove.append(f"Nothing in a worktree uses {emu['what']}: it is one shared instance owned by {emu['owner']}, so never run {never} here.")
    prove.append(f"The full suite (`{t['full_suite']}`) runs on main after your change has merged, not before.")
    if t.get("dev_servers"):
        prove.append(f"Your dev sites get their own ports and names in this worktree (`{t['dev_servers']}`).")
    prove.append("Never deploy to AWS, touch a real account or change a credential. Start a server only the way CLAUDE.md says "
                 "(`wt step tether`), probe before starting one, and never stop a server you didn't start.")
    text = " ".join(prove)
    for red in t.get("known_red") or []:
        text += (f"\n\nOne line of `{red['check']}` is red on purpose: {red['why']}. That line is not yours to fix. Never remove what it "
                 "reports, patch around it or soften the check to get a green run. Any other red line is a broken build.")
    tok["PROVE"] = text

    merge = f"```\n{t['merge']}\n```\n\nThe merge checks what lands with the unit tests. Never add `--no-hooks` or `--yes`."
    if w.get("commit"):
        merge += f" In a worktree of this repository, commit with `{w['commit']}`: {w['commit_why']}."
    tok["WORKTREE"] = merge

    c = t["console"]
    more = f", and `{c['more_mocks']}` holds further mocks" if c.get("more_mocks") else ""
    truth = c["says_what_is_true"]; truth = f"`{truth}`" if "/" in truth else truth
    tok["CONSOLE"] = (
        f"`{c['mockup']}` is the mockup the console grows out of{more}. The tasks and {truth} say what must be true; the mockup shows how it "
        f"should look and feel. Before building a task that touches the console, open the mockup screen it covers and build to it: layout, "
        f"spacing, type, components, and what happens on a click or a key. Where the user or {truth} describes something differently from "
        f"the mockup, that description wins.\n\nBefore committing console work, screenshot the console your build serves and the same mockup "
        f"screen with headless Chrome (`\"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome\" --headless=new --disable-gpu "
        f"--hide-scrollbars --window-size=1440,900 --screenshot=<file> <url>`), look at both, and fix what differs. Put the screenshot paths "
        f"in your summary so the user can look too.")
    return tok


def brief(t, role, self_name):
    if role not in ROLES:
        sys.exit(f"no role '{role}'. roles: " + " ".join(ROLES))
    tok = build_tokens(t, self_name)
    def fill(m):
        k = m.group(1)
        if k not in tok:
            sys.exit(f"roles/{role}.md needs {{{{{k}}}}} and crew.py builds no such token")
        return tok[k]
    text = (LIB.parent / "roles" / f"{role}.md").read_text()
    for _ in range(2):  # a token's text may itself carry tokens
        text = re.sub(r"\{\{([A-Z_]+)\}\}", fill, text)
    return text


if __name__ == "__main__":
    a = sys.argv[1:]
    data = load()
    if a[:1] == ["teams"]:
        print("\n".join(t["name"] for t in data["teams"]))
    elif a[:1] == ["env"] and len(a) == 2:
        print(env(team_of(data, a[1])))
    elif a[:1] == ["brief"] and len(a) >= 3:
        sys.stdout.write(brief(team_of(data, a[1]), a[2], a[3] if len(a) > 3 else ""))
    else:
        sys.exit(__doc__)
