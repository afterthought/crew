# Design

## Context

See proposal.md for why and record 0023 for the decision; this is how. What shapes it:

- **Making a worktree.** `make_place` in `plan.py` runs `PLACE` on the team's host through `host_run`: `git worktree add` in the kit's main checkout, then `crew-prepare` from `<main>/.devenv/profile/bin` when it is executable there. `PLACE` exits at once when the path exists, so a command run again over an existing worktree prepares nothing. `crew bolt give`, construct and `crew fix` all make their worktrees through it.
- **What moon 2.6.1 does** (record 0023, probes): `moon setup` installs the toolchains `.prototools` pins and no dependencies; the pipeline installs dependencies as an action ahead of the first task that needs them, through the user's shell, so it takes the pinned tool only where proto's directories are on PATH, which a devenv shell that activates proto gives; with no toolchain configured, moon sets nothing up and runs the shell's tools.
- **Entering the shell.** `.claude/hooks/devenv-shell`, run by `.claude/settings.json`, enters crew's checkout's devenv shell once per session start and appends an export to `CLAUDE_ENV_FILE` for each variable the shell set or changed; the plugin's own SessionStart hook (`plugin/hooks/session-start`) appends crew's identity to the same file. Claude Code runs a plugin's hooks for every session that loads the plugin, and every session on crew's hosts loads crew's plugin from the host's crew checkout.
- **crew's shell.** `devenv.nix` declares jq, moon (2.6.1 from moonrepo's release, this branch), `python3.withPackages (ps: [ ps.pytest ])` (3.14.7 at crew's lock) and recutils, and exports `MOON_TOOLCHAIN_FORCE_GLOBALS=true`; `tests/suite` keeps that variable through its clearing of `MOON_*`. Hosts run crew on their own `python3`, 3.13.15 on mac-studio.
- **A bolt's worktree under sluice.** In a kit with `sluice = true` in `.config/crew.toml` (`gather.sluice`), a unit's merge stage runs `wt submit bolt/<bolt>` (`merge_how`, `teams.5`), and sluice lands it by moving `bolt/<bolt>` through gix. The bolt's worktree, on `bolt/<bolt>`, then has HEAD at the new commit and its index and files at the old one: `git status` there shows the landing reversed, staged. A kit with a bare common dir, as crew's kits have, keeps no reflog for the branch, so the old commit is read from the index, not the log.

Rules relied on: `read.1` (a setup that fails, and a worktree crew can't level, refuse in the tool's words), `read.4` (crew levels only the bolt worktree it made, on the bolt's branch), `code.1` (crew's shell declares what its scripts call; amended below), `code.6` (nothing discards: `read-tree -m -u`, never `--reset`), `code.7` (whether a worktree gets set up and how a bolt's worktree is levelled are functions of facts, tested in the logic tier), `roles.3` (crew levels the worktree, not a brief asking the conductor to), `teams.5` (the sluice flag), `teams.6` (amended for `SLUICE_AGENT`, built), `teams.9` (what bash evals is shell assignments), `tests.4`, `tests.10` (`# Reads:` lines), `tests.11` and `tests.12` (each case at its lowest tier), `docs.2` (README with the behaviour). Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `tests.md`, `docs.md`, `core.md`.

Departures: `tests.7` rules out "the shell entered by crew-role or by the plugin"; this change enters it by the plugin, for the reason record 0023 gives, and `tests.7` is amended as below. `code.1` names `python3`; this change pins its minor, and `code.1` is amended as below.

## Goals / Non-Goals

**Goals:**
- crew runs no script a kit names for crew and reads no kit's devenv profile.
- A worktree crew makes in a kit with devenv and moon has the toolchain `.prototools` pins installed before its agent starts.
- Every session in a checkout with `devenv.nix`, any kit's, crew's agents and the user's own alike, runs every command in that checkout's shell from its first.
- crew's tests run on the Python minor crew runs on.
- In a kit on sluice, the bolt's worktree that ops deploys from matches its branch after every landing.

**Non-Goals:**
- No worktree holding a bolt's branch (record 0023, point 6): its own change once the user accepts it, since it rewrites how a bolt lands and is carried (`plan.8`, `plan.9`, `teams.5`, record 0015) and three briefs.
- Changing any kit: switchboard-kit moves its `bun install` into moon and drops `crew-prepare`, and swancloud drops its repository hook, each in its own repository.
- proto in crew's shell, a `.prototools` or a `.moon/toolchains.yml` in crew: crew pins no application tool (record 0023, point 4).
- sluice's runner and its `toolchain` key.

## Decisions

### A new worktree is set up by moon in its own shell

`PLACE` keeps only the worktree's making: it adds the worktree unless the path exists, then prints two shell assignments, `DEVENV=yes|no` and `MOON=yes|no`, from `test -f "$path/devenv.nix"` and `test -f "$path/.moon/workspace.yml"`. A new function decides from them:

```python
def setup_of(devenv, moon):
    """How a worktree crew makes is set up by its kit's toolchain (plan.17): moon setup in its own devenv shell when it
    has both, else nothing."""
    return ["devenv", "shell", "--", "moon", "setup"] if devenv and moon else None
```

`make_place` evals `PLACE`'s output, and when `setup_of` gives a command, runs it in the worktree on the team's host through `host_run` (`cd "$1" && shift && "$@"`). The setup runs whether the worktree is new or was already there, so a command run again after a failed setup sets it up; `moon setup` is a check once the pins are installed. A setup that fails refuses the command through `host_run`, in devenv's or moon's last words, with the worktree left made (`read.1`); the refusal says the worktree is at its path and that running the command again sets it up. Its output goes to the command's standard error, never its standard output (`teams.9`).

Why `devenv shell -- moon setup` and not the main checkout's moon: the worktree's own `devenv.nix` and `.prototools` are the pins its branch holds, and the evaluation it costs is the one the agent's session start then finds warm. Why no dependency install: moon has none outside a task, and its pipeline installs before the first task that needs them, in the agent's shell, with the pinned tool.

### The session's shell is entered by crew's plugin

`.claude/hooks/devenv-shell` moves to `plugin/hooks/devenv-shell` and `.claude/settings.json` goes; `plugin/hooks/hooks.json`'s SessionStart list gains `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/devenv-shell"` with a timeout of 600, beside `session-start`'s. The hook as it is, but for its root and its words:

- The root is the top of the git checkout holding the project directory (`git -C <CLAUDE_PROJECT_DIR> rev-parse --show-toplevel`, standard library `subprocess`); a project directory in no checkout, or a checkout with no `devenv.nix` at its root, is left alone, silently. The hook no longer falls back to its own path's parents, which would be crew's checkout for every session.
- The failure line names no kit: "This session is not in its checkout's devenv shell: devenv could not be entered when it started. The checkout's tests and merge gate need that shell; say so rather than going on without it."
- Its docstring says why the plugin carries it: one entry for every session on the host, in every kit, while what the shell is stays each checkout's `devenv.nix`.

A subagent's SessionStart is left alone, as `session-start` leaves it (`agent_id` in the hook's input): it runs inside its parent's session, whose file already holds the shell. While a kit still carries its own copy of the hook (swancloud's), both run at a start: each appends the same exports, and the cost is a second evaluation, warm.

### crew's shell

`devenv.nix` declares `pkgs.python313.withPackages (ps: [ ps.pytest ])` in place of `pkgs.python3…`, with a comment that crew runs on each host's own `python3`, the fleet's 3.13, so the tests run on that minor and it moves when the fleet's does. `export MOON_TOOLCHAIN_FORCE_GLOBALS=true` and the comment's "moon runs the shell's own tools, never proto's from the home directory" go: with no toolchain configured, moon runs the shell's tools through its `system` toolchain. `tests/suite` keeps only a caller's `MOON_CONCURRENCY` through its clearing of `MOON_*`.

### Every agent carries its name for sluice (built)

`crew-role` exports `SLUICE_AGENT=$NAME` beside `CREW_AGENT` and `CREW_LABEL`; `session-start` writes it with them into `CLAUDE_ENV_FILE` when herdr resumes an agent; `teams.6` names it (4bdc6d0).

### A bolt's worktree follows its branch in a kit on sluice

crew levels the bolt's worktree in two places, only in a kit whose flag is `sluice = true`: when the wait reads that a unit's or a fix's merge stage has delivered (the bolt holds it), and in `crew prove` before ops is told to prove. It reads, on the team's host, in `<kit>/bolts/<bolt>`: the branch it is on, an operation in progress (`IN_PROGRESS`), the index's tree (`git write-tree`), HEAD's tree, and HEAD's first-parent commits back to the merge-base with main, each with its tree. A decision judges them:

```python
def levelling(bolt, on, busy, index_tree, head_tree, history):
    """How the bolt's worktree is brought level with its branch after sluice moved it (teams.17): None when it is
    level; ("level", <old>) with the newest commit of the branch whose tree the index holds; or ("refuse", <why>)."""
```

It refuses when the worktree is not on `bolt/<bolt>`, has an operation in progress, or holds an index whose tree no commit of the branch has (a change staged by hand), each naming the worktree and what to do. For `("level", old)`, crew runs `git read-tree -m -u <old> HEAD` there, the two-way merge `git checkout` does: it brings the index and files to HEAD, keeps untracked files and a local edit to a file the landing did not touch, and refuses, changing nothing, when the landing changes a file with a local edit. A refusal, the decision's or git's, is recorded and told to the conductor with its words; the stage's end and the proof are not held up by it, and the conductor gives ops the paths. crew's run record gains a `bolt.level` entry (`bolt/<bolt>`, from old to HEAD).

Why `read-tree` and not `reset --keep` or `checkout`: HEAD has already moved, so there is no branch to switch and nothing to reset to; `read-tree -m -u <old> HEAD` is the step `checkout` would have taken had it moved the branch itself, and it discards nothing (`code.6`). Why the old commit from the index: the kits' bare common dirs keep no reflog for `bolt/<bolt>`, and sluice's gix moves write none.

## Rules this changes, on acceptance

Written by the design agent once the user accepts record 0023 (`docs.7`); `teams.6` was amended with its build.

- `tests.7`: "Every Claude session in a checkout with `devenv.nix` works inside that checkout's devenv shell, entered at its start by crew's plugin's SessionStart hook; no CLAUDE.md, README, brief or skill tells an agent to wrap a command in `devenv shell --`, and only worktrunk's merge hooks enter the shell themselves." Its details: Rules out a wrapper in crew-role; a copy of the hook in a kit. Source: record 0023.
- `code.1`'s last clause: "devenv declares only jq, moon (from moonrepo's release, at the version sluice pins), recutils, and Python at the minor the fleet runs crew on, with pytest for the tests."
- A new `plan.17`: "crew makes a worktree ready only by its kit's own toolchain, `moon setup` inside the worktree's devenv shell when it holds `devenv.nix` and `.moon/workspace.yml`, and by nothing when it does not; it runs no script a kit names for crew and reads no kit's profile."
- A new `teams.17`: "In a kit that merges through sluice, crew brings the bolt's worktree level with its branch after each merge stage and before each proof, by `git read-tree -m -u` from the commit its index holds, and says what keeps it from doing so."
- `tests.md`'s `paths` lose `.claude/settings.json` and `.claude/hooks/**`; `core.md`'s table row for `tests.md` loses `.claude/`.

## Risks / Trade-offs

- [Every session on a crew host in a devenv checkout waits for its shell, the user's own included] → It runs inside Claude Code after it is up, as crew's and swancloud's hooks already do in their checkouts; a warm shell is under a second.
- [A host whose sessions do not load crew's plugin] → its sessions get no shell; `tests/run` and `tests/suite` still refuse outside one, naming how to enter it.
- [The fleet moves to Python 3.14 and crew's pin stays] → crew's tests run on a minor behind the hosts', as today's are ahead of them; the pin's comment names the fleet's version, and `code.1` holds the two together.
- [A kit with devenv and moon whose setup is slow or needs the network on the box] → the worktree's making waits for it, as `crew-prepare`'s install did; `PROTO_HOME` shared in the kit's common dir, as sluice's devenv sets it, makes it a check after the first.
- [A dependency install that resolves the host's tool] → only outside a shell that activates proto (record 0023's probe); every agent's session is inside one, by the hook.
- [sluice lands twice before crew reads the stage's end] → the index still holds the first old commit, which is on the branch's first-parent history, so one `read-tree` brings it to the newest.

## Proof on real work

Once the bolt has landed and every host has pulled: the next session started in a switchboard-kit or breadboard-kit worktree on the box has `DEVENV_ROOT` naming that worktree at its first command; the next unit crew makes in a kit with devenv and moon (sluice, once its toolchain lands) has its `.prototools` pins installed before its construct agent starts. The conductor or ops that sees each says so; nothing is the user's.

## Task notes

### 1.2

`devenv.nix` as *crew's shell* says. Run `tests/suite --affected` (every task reads `devenv.nix`).

### 2.1

`setup_of` in `plan.py` beside `make_place`, and `tests/py/test_place.py`: both files give the command, either one alone or neither gives `None`.

### 2.2

`PLACE` and `make_place` as *A new worktree is set up by moon in its own shell* says; the `crew-prepare` comment and line go. `tests/units.sh`: the fixture kit gains `devenv.nix` and `.moon/workspace.yml` in its first commit and loses its `crew-prepare` stub and `.prepared` from `.gitignore`; a stand-in `devenv` first on the test's PATH, as `t-dev-shell.sh` writes one, logs `<cwd> <args>` to `$T/devenv.log` and fails when `$T/devenv-fails` exists. `tests/t-journey-units.sh`: in place of the `.prepared` checks, the log holds `<bolt's worktree> shell -- moon setup` after give and `<place> shell -- moon setup` after construct; with `$T/devenv-fails`, a construct is refused naming the place and running it again after removing the file sets the place up. A kit fixture without the two files (t-journey-plan's) gets no call. Run `tests/moon-tasks` when a `# Reads:` line changes.

### 3.1

`git mv .claude/hooks/devenv-shell plugin/hooks/devenv-shell`, edited as *The session's shell is entered by crew's plugin* says; `.claude/settings.json` removed with `git rm`; `hooks.json`'s SessionStart list gains the entry. `tests/t-dev-shell.sh` runs `$CREW/plugin/hooks/devenv-shell`, gains a project directory nested below its checkout's root (entered at the root), a checkout with no `devenv.nix` and a directory in no checkout (both untouched, no call logged), and a subagent's start (untouched); it reads `plugin/hooks/hooks.json` for the entry instead of `.claude/settings.json`, and its `# Reads:` line names `plugin/hooks/` in place of `.claude/`. Run `tests/moon-tasks`.

### 3.2

`CLAUDE.md`, Tests, first bullet: the shell is entered by crew's plugin's SessionStart hook (`plugin/hooks/devenv-shell`), in crew's checkouts and every kit's with a `devenv.nix`. `README.md`, Needs: the same, in one sentence. `.envrc` stays. `t-dev-shell`'s check that no doc wraps a command holds as it is.

### 4.2

`levelling` in `plan.py` and its cases in `tests/py/test_level.py`: level (none), index at an older commit of the branch (that commit), index at a tree on no commit (refused), not on the branch, a rebase in progress. A contract case in `tests/contract/test_git.py` pins what `levelling` relies on: after `git update-ref refs/heads/bolt/x <new>` under a worktree on `bolt/x` holding an untracked file and an edit to a file the move does not touch, `git write-tree` gives the old commit's tree, `git read-tree -m -u <old> HEAD` leaves `git status --porcelain` showing only those two, and with an edit to a file the move changes it exits non-zero and changes nothing. The act after the merge stage's delivered and in `crew prove`, recorded as `bolt.level`; `tests/t-sluice.sh` gains one case, a stand-in landing moving `bolt/<bolt>` by `git update-ref` and the merge stage's end leaving the bolt's worktree clean. `plugin/roles/conductor.md` and `ops.md`: in a kit that merges through sluice crew keeps the bolt's worktree level with its branch and tells the conductor when it can't, with a phrase in `t-briefs.sh` (`tests.6`).
