# Design

## Context

`plugin/bin/crew` runs a command as several `python3 plan.py _<step>` processes. `crew unit run` runs `_team-of` on the asker's host, forwards, then on the team's host runs `_team-of` again, `_ends`, `_slots`, `_tidy`, `_run` and sometimes `_ended`; `crew status <team>` runs `_ends`, `_slots` twice and `_tidy`. Each step that needs the plan calls `fetch()` (`plan.py` 362), a `git fetch` of the state branch over https into crew's bare cache. Each step that needs stages calls `survey()` (`plan.py` 688), which pipes `gather.py` to the host; `gather.place()` (`gather.py` 113) runs `openspec list --json` and `openspec status --change <unit> --json` in every unit's place. `run_check` even calls `survey()` a second time inside one process, for a waiting unit's `After` units. `deliverable()` (`plan.py` 2836) runs `openspec status` once more for a construct's end, and `ticks()` (`plan.py` 2770) counts a commit's tasks by its own rule, `- [ ]`, `- [x]` or `- [X]` at the start of a stripped line, which is narrower than `openspec`'s.

What the reading measured (`openspec/explorations/command-cost/reading.md`, 2026-10-07): a kit read costs about 0.65 s per unit in flight, nearly all of it `openspec` starting; t-merge made 23 reads and t-units-ws 29; each `plan.py` run pays about 55 ms of fetch.

How `openspec` 1.14.1 decides the two facts, read from its source (`dist/utils/task-progress.js`, `dist/core/artifact-graph/{state,outputs,instruction-loader,resolver}.js`, `dist/utils/change-metadata.js`, and `schemas/spec-driven/schema.yaml` in the package):

- **Tasks** (`openspec list --json`'s `completedTasks`/`totalTasks`): every line of the tracked tasks file matching `^\s*(?:[-*+]|\d{1,9}[.)])\s*\[(?:\s*([^\]\s]?)\s*\](?![([])|\s+\])\s*(.*)`, wherever it sits (inside a code fence too); a task is done only when its marker is `x` or `X`. So `  - [ ] 1.1.1`, `1. [ ]`, `+ [x]`, `- []`, `- [~]` and `- [ x ]` are tasks; `- [design](./design.md)`, `- [A][ref]` and `- [WIP] …` are not. The tracked file is the artifact whose `generates` equals the schema's `apply.tracks` (`tasks.md` for spec-driven); with no file, 0 of 0. CRLF lines still match.
- **Planning complete** (`openspec status --json`'s `isPlanningComplete`): every artifact of the change's schema has at least one existing output file. For spec-driven: `proposal.md`, `design.md`, `tasks.md`, and at least one file matching `specs/**/*.md` (fast-glob, regular files, dot-files not matched). A change whose `.openspec.yaml` parses and says `skip_specs: true` counts the `specs/` artifact complete without files.
- **Which schema**: the change's `.openspec.yaml` `schema:`, else the project's `openspec/config.yaml` (or `.yml`) `schema:`, else `spec-driven`; a name is resolved project first (`<root>/openspec/schemas/<name>/`), then the user's (`$XDG_DATA_HOME/openspec/schemas/<name>/`, else `~/.local/share/openspec/schemas/<name>/`), then the package's. This machine has a dozen user schemas (the `bolt-*` family, `flywheel-intent`), none named spec-driven.

Rules this design rests on: `plan.12` (the rule it builds), `plan.1` and `state.1` (a write re-checks and replays on the tip it lands on), `state.4` (no service, nothing written by a view), `read.1` (never a guess), `read.2` (another tool's output read by checked facts), `code.1` (standard library only; `gather.py` self-contained), `code.2` (refusals), `teams.9` (bash reads only quoted assignments on stdout), `tests.1`, `tests.2` and `tests.4` (the runner, the guard, a stub that behaves like the tool), `docs.5` (rules cited and amended with the decision). Pages whose area this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`plugin/bin/crew`), `tests.md` (`tests/`), `docs.md` (`docs/architecture/`).

## Goals / Non-Goals

**Goals:**

- One kit read and one fetch of the state branch per command on each host it runs on.
- A unit's tasks and planning read without starting `openspec`, agreeing with `openspec` on the same worktree, and a test that fails when they stop agreeing.
- The stub `herdr` cheaper, behaving the same.
- No change to any command's output.

**Non-Goals:**

- Folding a command's `plan.py` runs into one process, or `import plan`'s own cost.
- One forward per host for `crew status` with no team named (it forwards per team).
- The suite as parallel moon tasks (`the-suite-runs-as-moon-tasks`, after this unit).
- `gitenv()` for `gather.py`'s git calls (`_open.md`).

## Decisions

### Stage facts are read from the change's files, by openspec's rules

`gather.py` gets the two facts from the files: a task parser with `openspec`'s pattern, and a planning check that looks for spec-driven's four outputs and honours `skip_specs`. It is used for a place's `tasks` and `open`, for `ticks()` at a commit, and for construct's deliverable, so every reader of the two facts reads them one way. The open tasks keep their descriptions as `openspec` parses them, so `- [~] 1.2 …` is open, as it is for `openspec`.

The direct reading knows spec-driven only, and only spec-driven as the package defines it. When a change resolves to any other schema, when the kit or the user's data folder holds its own `spec-driven`, or when a `.openspec.yaml` or `config.yaml` holds a line crew does not read, that place is read through `openspec`, as now, one place at a time. That is `openspec`'s own answer, not a guess (`read.1`). In a change's `.openspec.yaml` crew reads `schema: <name>`, `created: <date>` and `skip_specs: true|false`, one per line. In the kit's `config.yaml` it reads `schema: <name>`, and reads past the top-level `context`, `rules` and `operations` keys and the lines indented under them: `openspec` uses those only for its instructions, never for a stage, and crew's own kits carry them, so without that every place would go through `openspec`. Anything else in either file hands the place to `openspec`.

Alternative: one `openspec list --json` per kit and `status` per place. It halves the cost but keeps 0.3–0.5 s per place, and the rule's target is the time of one kit read for three units.

### Each command keeps one reading on each host

A **command's reading** is a folder under the host's crew cache, `~/.cache/crew/reads/<unique>/`, made by the outermost `crew` process of a command that runs more than one step, named to every step it starts in `CREW_READ`, and removed by that process's exit trap, whether the command succeeds or is refused. The folder records the host it belongs to; a step on another host ignores it (the test's stub ssh passes the environment through; real ssh does not, and `there` passes only named variables). Within one Python process the same memo is kept in memory, so `run_check`'s second `survey()` reads nothing.

It holds:

- **The state branch's tip, per repository and branch.** `fetch()` returns it when it is there and fetches only when it is not. A branch found missing is not kept, so a later step fetches again. Every push crew makes records what it pushed.
- **Each kit's answer, per host and kit.** `survey()` asks a host's `gather.py` only for kits the reading lacks, and keeps what comes back. A `sites` survey is not kept (`crew sites` is one run).

A step that changes a kit drops that kit's answer: `make_place` after making a worktree, and `tidy` once it has removed one.

A plan write's first attempt starts from the tip the reading holds. Its push without force is refused if the branch has moved, and only then does `land` fetch afresh and replay, its change function re-checking every precondition on that tip (`plan.1`, `state.1`). After a successful push the reading holds the new commit, so a later step in the same command sees its own write. Every other place that pushes (`state init`'s adoption) fetches afresh after it.

A reading kept for a command's steps is not a service and not state: it lives for one command and is gone after (`state.4`). A folder left by a killed command is removed by the next command on that host once it is a day old.

### Every bolt branch of a kit is read

`gather.py` reads every local `bolt/*` branch of a kit, with the bolts a request names that have no branch marked as missing, instead of only the named and tracked ones. One answer then serves every step: `_slots` asks with no bolt and `_run` with the unit's bolt, and a unit merged with its place removed is tracked by no place, so a narrower answer would miss that its bolt holds it. A bolt absent from the answer has no branch. Nothing reads the `exists` field outside `gather.py` today.

### Waits and loops read afresh

`stage_wait` (`_wait`) looks every ten seconds for up to an hour; each look bypasses the reading, in memory and on disk. The rail tab's loop (`crew _rail`) and `crew events --follow` make no reading and remove any `CREW_READ` they inherit, so each refresh is a command of its own. A command bash `exec`s as one `plan.py` run (`crew bolts`, `crew plan`, `crew rail`, …) makes no folder; its in-memory reading is enough.

### The stub herdr

The stub starts Python without site packages (`-S`) and imports `subprocess` and `pathlib` only where a call needs them: about 20 ms a call against 40 ms, measured with `time` before and after. Its state file, log lines and answers are unchanged (`tests.4`).

### How the rule is tested

- `tests/t-stage-facts.sh` builds places whose changes cover each case in *Context*, plus a change naming a user schema and a kit holding its own `spec-driven`, and compares, place by place, `gather.py`'s `tasks`, `planning` and `open` with `openspec list --json` and `openspec status --change <unit> --json` run in the same place, and `ticks()` at a branch with `openspec list` on that commit's checkout. `tests/run` refuses to start without `openspec` on the path, like `recsel` (`tests.1`).
- `tests/t-reads-once.sh` puts logging shims for `git`, `python3` and `openspec` ahead of the real ones (the reading's own method) and counts, per simulated host, state-branch fetches, `gather.py` runs and `openspec` starts: `crew status swb-1` with three units in flight fetches once and gathers once on the box and starts no `openspec`; `crew unit run` does the same before its place is made; a plan write in a command whose tip moved meanwhile replays (`race` in `lib.sh`); and `~/.cache/crew/reads/` is empty after a command and after a refused one.
- The existing waits in `t-stage-ends.sh` and `t-unit-run.sh` prove that a wait sees a tick made while it waits.

## Risks / Trade-offs

- [A command's later steps see the plan as it was when the command began, a few seconds old] → that is what one Python run would see; every write still lands on the current tip, re-checked (`plan.1`), and waits and loops read afresh.
- [`openspec` changes its rules] → the agreement test fails on the next suite run with the machine's `openspec`, naming the case; the direct reading is updated to match. The rules were read from 1.14.1.
- [A kit's change uses a workflow crew doesn't read] → that place costs what it costs today; nothing else does.
- [A step that changes a kit and does not drop its answer] → a stale stage in a later step of the same command. Every step that makes or removes a worktree, or commits in a place and so moves its head, drops the kit's answer: `make_place`, `tidy`, `tidy_after`, `unit_approve`, and `op_unit_move`'s rebase and its undo. A new step that does any of these must drop it too, as `drop_kit`'s docstring says.
- [Reading every bolt branch costs one `git ls-tree` per branch] → a few milliseconds each; `tidy` removes finished bolts' worktrees, and the branch count stays small.

## Migration Plan

Land, then pull on every host in one step. Nothing is stored between commands, so nothing migrates. A host still on the old `crew` pipes the old `gather.py`; an asker on the new crew reads its answer, whose fields are unchanged. Rollback: revert.

## Proof in dev

None: crew has no dev environment, and the bolt's proof is its verification. The verification's suite time at the bolt's head is noted beside the reading's twenty minutes.

## Proof on real work

Once the bolt has landed and every host has pulled:

1. `time crew status <team>` on a team with three units in flight answers in about the time one kit read took before (under 2 s on the box, against the reading's two or three 2 s reads), and its output is what it was.
2. `crew bolts` shows the same stage and task counts for every unit in flight as before the landing.
3. The next full `devenv shell -- tests/run` on mac-studio: its total time, beside the reading's twenty minutes.

## Task notes

### 1.1

In `gather.py`: `TASK = re.compile(...)` with `openspec`'s pattern as given in *Context* (copy it from `dist/utils/task-progress.js` and say in a comment the version it was read from); `tasks_of(text) -> [(done, description)]`, splitting on `\n`; `planned(change_dir, kit_root) -> bool | None`, `None` meaning "read it through `openspec`". `None` when: the change's `.openspec.yaml` has a non-blank, non-comment line other than `schema: spec-driven`, `created: …`, `skip_specs: true|false`; the kit's `openspec/config.yaml` (`.yml` when the `.yaml` is absent) has one other than `schema: spec-driven` and the top-level `context:`, `rules:` and `operations:` keys with the lines indented under them; the resolved schema is not `spec-driven`; or `<kit>/openspec/schemas/spec-driven/` or the user's `openspec/schemas/spec-driven/` exists (`$XDG_DATA_HOME/openspec`, else `~/.local/share/openspec`; read `dist/core/global-config.js` `getGlobalDataDir` for the exact rule on each OS). Otherwise `proposal.md`, `design.md` and `tasks.md` are regular files and either `skip_specs` is true or some regular file under `specs/` whose own name and every directory name below `specs/` does not start with `.` ends in `.md`. `place()` uses both and runs `openspec` only on `None`; `tasks` stays `None` when the change folder is absent, as `openspec list` gives no entry.

### 1.2

`plan.py` `ticks()` counts with `gather.tasks_of` on the commit's text; `deliverable()`'s construct branch uses `gather.planned` on the place, falling back to `openspec status` on `None`, as `place()` does. `place()`'s `open` becomes the descriptions of tasks not done.

### 1.3

`gather.kit()`: list `refs/heads/bolt/` with `git for-each-ref --format=%(refname:short)`, and read each as it reads a named bolt now; a requested bolt with no branch keeps `{"exists": False, ...}`. `survey()` no longer needs to merge bolts per kit beyond what it asks.

### 1.4

`plan.py`: a small reading module-level object (`READ`) with `tip(repo, ref)`, `keep_tip`, `kits(host)`, `keep_kits`, `drop_kit(host, main)` and `fresh()` (a context manager that bypasses it). Backed by files in `$CREW_READ` when that is set and its `host` file names this host (`crew.this_host()`), else in memory. Files: `host`, `tip-<sha1 of repo+ref>` holding the sha, `kits-<host>.json` holding `{main: answer}`; write each through a temporary file and `os.replace` so a nested step never reads half a file. `fetch(repo, ref, fresh=False)`; `land` calls `fetch` for the first attempt and `fetch(..., fresh=True)` after a refused push, and `keep_tip` after a successful one. Search every `fetch(` and every `"push"` in `plan.py` and `record.py`: a fetch right after a push is fresh.

### 1.5

`make_place` ends with `READ.drop_kit(t["machine"], t["kit"]["main"])`; `tidy` drops it once it removed any worktree. `place_cmd` (`_place`, a fix's place) goes through `make_place`.

### 1.6

`plugin/bin/crew`: after the argument loop, when `CREW_READ` is unset or names a folder whose `host` is not this host, and the command is not one bash `exec`s, `_rail`, or `events`, make `~/.cache/crew/reads/` and a folder in it with `mktemp -d`, write its `host`, export `CREW_READ`, and `trap 'rm -rf -- "$CREW_READ"' EXIT` (only in the process that made it; check the path is under the reads folder before removing, as `tests/run`'s `unscratch` does). In the same place, remove folders there older than a day. `_rail` and `events` `unset CREW_READ`. `stage_wait` in `plan.py` wraps each look in `READ.fresh()`.

### 1.7

`tests/stubs/herdr`: shebang `#!/usr/bin/env -S python3 -S`; move `subprocess` and `pathlib` imports into the branches that use them (or use `os.path`). Time 50 calls of `herdr --session s workspace list` before and after, and give both numbers in the summary.

### 1.8

`tests/run`: add `openspec` to the `for c in recsel recfix git python3 jq` check, with the same message shape. `tests/t-stage-facts.sh` (with the `TESTS` guard as its first command, `tests.2`): one kit, one place per case, each committed. Cases: `- [ ]`/`- [x]`/`- [X]`; `* [ ]`, `+ [x]`, `1. [ ]`, `2) [x]`; indented sub-tasks; `- []`, `- [~]`, `- [ x ]`; `- [A](u)`, `- [design](./design.md)`, `- [WIP] w`; tasks in a code fence; CRLF; no `tasks.md`; no `specs/`; only `specs/.hidden.md`; `specs/a/b/spec.md`; `skip_specs: true` with no specs; no `design.md`; `.openspec.yaml` naming a schema the test writes under `$XDG_DATA_HOME/openspec/schemas/` (set `XDG_DATA_HOME` into `$T`); a kit with its own `openspec/schemas/spec-driven/`. For each, run `python3 "$CREW/plugin/lib/gather.py" '<request>'` and `openspec list --json` / `openspec status --change <c> --json` in the place, compare `tasks` and `planning`, and fail naming the case. Also `ticks()` at the branch, through `python3 -c 'import sys; sys.path.insert(0, ...); import plan; ...'`, against `openspec list` in the place.

### 1.9

`tests/t-reads-once.sh`: build the shims in `$T/shim` from `command -v git python3 openspec` taken before prepending; each logs `<CREW_TEST_HOST> <what>` to `$T/reads.log` and `exec`s the real one: `git` logs `fetch` when its arguments hold `fetch` and `refs/crew/`; `python3` logs `gather` when its first argument is `-`; `openspec` logs every start. `team_world`, three units of swb-1 in construct with changes, then clear the log and run `crew status swb-1`; assert per host. Then `crew unit run` on a fourth unit; then a write raced with `race` from `lib.sh`; then `ls ~/.cache/crew/reads` on each host is empty, also after an `expect_fail` command.

### 1.10

`docs/architecture/_open.md`: remove the `plan.12` line from *Accepted, not built*. `docs/architecture/plan.md` `[plan.12]` details: drop "Not built: `_open.md`" and add this change and `tests/t-stage-facts.sh`, `tests/t-reads-once.sh` to its sources, and one sentence: the direct reading knows `openspec`'s spec-driven schema; any other is read through `openspec` (`docs.5`).

### 1.11

Run `devenv shell -- tests/run`; it ends with "0 failed". Give its wall time in the summary.
