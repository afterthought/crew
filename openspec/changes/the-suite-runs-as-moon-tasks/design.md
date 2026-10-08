# Design

## Context

See proposal.md for why. What shapes the approach:

- **The suite today.** `tests/run [name...]` runs each `tests/t-*.sh` serially, each in its own `mktemp` scratch directory `$T` with a scratch HOME per simulated host, bare remotes under `$T` and stub herdr, ssh, hostname, sleep and claude first on `PATH` (`tests/lib.sh` 1–30). It prints `ok    <name>` or `FAIL  <name>   (scratch kept: …)` with the output's last lines, then `<n> passed, <m> failed`, and exits non-zero on any failure (`tests.1`). It refuses to start outside a devenv shell. There are 48 test files; `t-sites-live` skips itself unless `CREW_TEST_LIVE=1`, and is the only test besides `t-merge-gate` that reads that variable.
- **The gate as built** (`a-merge-is-gated-by-the-suite`): `.config/wt.toml` runs `[pre-merge] suite = "devenv shell -- env CREW_TEST_LIVE= tests/run"` on every `wt merge`, and `[post-merge] verify = "devenv shell -- sh .config/hooks/bolt-verify.sh {{ target }}"`. `bolt-verify.sh` exports the bolt's revision with `git archive` into a `crew-verify.XXXXXX` scratch directory, runs `./tests/run` there, and records `State`, `Failed: <name>` (parsed from `FAIL  <name>` lines) and the log under `<git common dir>/bolt-verify/<bolt>/<rev>.rec`. `tests/t-merge-gate.sh` drives both with the real `wt` against a stand-in suite.
- **What every test reads.** Every command crosses `plugin/lib/plan.py`, so `plugin/**` is an input of every test (the reading's "Found"). Beyond `plugin/`, `tests/run`, `tests/lib.sh` and `tests/stubs/`, four tests read files of crew's: `t-dev-shell` (`.claude/hooks/devenv-shell`, `.claude/settings.json`, `.envrc`, `.gitignore`, `CLAUDE.md`, `README.md`), `t-docs` (`README.md`), `t-merge-gate` (`.config/`), `t-sites` (`tests/stubs-sites/`). Every such read goes through `$CREW/<path>` or `$TESTS/<path>`.
- **What could collide.** Each test's HOME, remotes and logs are under its own `$T`; crew's git cache is `~/.cache/crew/git` under that HOME (`plan.py` 72); `t-merge-gate` and `t-stage-facts` point `XDG_CONFIG_HOME`, `XDG_DATA_HOME` and `TMPDIR` under `$T`. Nothing read shares state outside `$T`, but some tests wait on a bound (`t-merge-gate`'s `until_state`, 200 × 0.1 s) that load could exceed. Python writes `__pycache__` under `plugin/` while tests run.
- **moon 2.5.3**, the version in crew's locked nixpkgs (`devenv.lock`, nixpkgs `c7def046`), checked against its docs and in a scratch lab for this change:
  - A task with no `outputs` is cached: each pass leaves `.moon/cache/outputs/<hash>.tar.gz` holding its stdout and stderr, and the next run with the same hash shows `cached` and replays them. A failed run is never archived, and a task that failed in a checkout runs again there next time even when a passing archive for its hash exists ("Previous run failed, avoiding hydration").
  - The hash is the command and arguments, each input file's content by relative path, the task's declared `env` and `$VAR` inputs, and `.moon/workspace.yml`. It does not depend on the checkout's absolute path, `DEVENV_ROOT` or `PATH`. Linking `.moon/cache/outputs` in a second worktree to the first's archive directory replays the first's passes there.
  - Inputs include git-ignored, untracked and uncommitted files: a `plugin/__pycache__/x.pyc` changed the hash. `hasher.ignorePatterns` in `.moon/workspace.yml` keeps them out.
  - In a directory that is not a git repository (a `git archive` export) moon runs every task with "Caching is disabled", and nothing replays. `git init && git add -A && git commit` in that directory gives exactly the worktree's hashes and replays from the shared archives.
  - `moon run` stops at the first failure and archives nothing still running. `moon exec <targets> --on-failure continue` runs every target and exits 1 when any failed. Statuses (`passed`, `cached`, `failed`) are in `.moon/cache/runReport.json`, per checkout.
  - `moon exec tests:t-a tests:t-b …` and a task-tag target, `tests:#suite`, run tasks in parallel, by default as many as the machine has CPUs (`-c`/`MOON_CONCURRENCY` sets it). `--query` filters projects only. A deps-only aggregate task pulls in all its deps under `--affected`, since `run` follows dependencies.
  - `--affected` alone compares uncommitted changes only; `--affected remote` compares against the merge-base with `vcs.defaultBranch` and adds uncommitted changes; `--base <rev> --head HEAD` compares against a named base and leaves uncommitted changes out. Unaffected tasks are not run at all. `-f`/`--force` bypasses the cache and the affected check.
  - A task inherits the caller's environment, and a task's `env` does not override a value the caller set; `options.envOverride` is rejected by 2.5.3.
  - Nothing auto-discovers tasks. Two moon processes in two checkouts sharing one archive directory ran at once without lock errors. `pipeline.autoCleanCache` (on by default) prunes archives older than seven days from it. moon wrote nothing outside `.moon/cache`, downloaded nothing and ran no daemon; tasks resolved to the system toolchain.
- **switchboard-kit** runs moon this way already (`switchboard-kit/main/.moon/`, `devenv.nix` 818–834, `.moon/scripts/moon-tests.sh`): a link from `.moon/cache/outputs` to `<git common dir>/moon-outputs` made at shell entry, `MOON_TOOLCHAIN_FORCE_GLOBALS=true`, and a script that runs `moon exec … --on-failure continue` and reports from `runReport.json`. This design follows it.
- **What agents are told today.** CLAUDE.md "Tests" says "Run them only as `tests/run [name...]`", and each change's last task has been "`tests/run` prints `0 failed`". The coder's brief already says to run "the tests of what you changed with moon" (`coder.md` 25), true in switchboard-kit and not yet in crew. The construct brief asks for tasks "ending with the suite green" (`construct.md` 17). The verify brief says nothing about tests.

Rules relied on: `tests.5` (this change builds its second half), `tests.1` (each task runs its test through `tests/run`, and `tests/run` is unchanged), `tests.2` (the live test is never run by the suite; every new test keeps the guard line), `tests.3`, `tests.6` (each new brief sentence pinned in `t-briefs.sh`), `tests.7` (no doc tells an agent to wrap a command in `devenv shell --`; only the merge hooks enter the shell), `state.4` (moon's cache is plain files; no service), `read.1` (a test with no task, or a task that doesn't name what its test reads, refuses the run rather than replaying a guess), `read.4` (the verification's git repository is made only inside its own `crew-verify.XXXXXX` copy, never as a worktree of crew's), `code.1` (amended), `code.6`, `docs.5`. Areas touched: `tests.md` (`tests/**`, `devenv.nix`, `.config/**`), `briefs.md` (`plugin/roles/`), `docs.md` (`CLAUDE.md`, `README.md`, `docs/`, `openspec/`).

Departures: `code.1` says devenv declares only jq, python3 and recutils; record 0008 decides moon is pinned in devenv, so this change amends `code.1` to add moon (`docs.5`). Record 0008 lists a task's inputs as `plugin/**`, `tests/lib.sh`, `tests/stubs/**` and the test file; this design adds `tests/run` (the command every task runs), `devenv.nix` and `devenv.lock` (the tools every test runs on) and each test's own declared reads, because the exploration the record rests on requires that "inputs must name everything a check reads", and without them an edit to those files would replay a stale pass.

## Goals / Non-Goals

**Goals:**
- The whole suite in about the time of its longest test plus contention, and in moments on a tree already passed on the host.
- The gate replays the coder's run, and the verification replays the gate's, whenever the tree is the same.
- No stale replay: a task's inputs are everything its test reads, and the suite refuses when they aren't.
- Agents run only what their change affects; the whole suite runs at merges.

**Non-Goals:**
- Narrowing what a change to `plugin/` reruns: every test reads `plan.py`.
- Sharing the cache between hosts: mac-studio and the box each keep their own archives under their own git common dir.
- Changing what any test checks, or how `tests/run` runs one test.
- wtenv, or a cached devenv across worktrees (record 0008, "Kept out").
- Gates for any other kit.

## Decisions

### One project, one task per test file, generated and checked

`.moon/workspace.yml` declares one project, `tests`, at `tests/`, with `vcs` git on `main`, telemetry off, and `hasher.ignorePatterns: ['**/__pycache__/**']`. Its tasks are in `tests/moon.yml`, written by `tests/moon-tasks` from `tests/t-*.sh`, one per file except `t-sites-live`:

```yaml
t-merge:
  command: tests/run t-merge
  inputs: ['/plugin/**/*', '/tests/run', '/tests/lib.sh', '/tests/stubs/**/*', '/devenv.nix', '/devenv.lock', '/tests/t-merge.sh']
  tags: [suite]
  options: { runFromWorkspaceRoot: true }
```

A test that reads files of crew's beyond those names them in one line of its opening comment, `# Reads: README.md CLAUDE.md .claude/**`, and the generator adds each as an input (a directory as `/<dir>/**/*`). The task is named for the file, so `FAIL  t-merge` from `tests/run` and moon's `tests:t-merge` name the same thing.

`tests/moon-tasks --check` writes nothing and exits non-zero, naming each, when a test has no task, a task has no test, a task differs from what the generator would write, or a test refers to `$CREW/<path>` or `$TESTS/<path>` outside its task's inputs. `tests/suite` runs the check before anything else, so a forgotten regeneration refuses the run rather than leaving a test out of the gate, and `t-suite` runs it against fixtures.

Alternatives: one task for the whole suite: no parallelism, and one failure reruns everything (record 0008). One moon project per test: the same hashing at the cost of 47 project folders. Generating `moon.yml` on every run instead of committing it: moon reads its configuration before any script of ours could write it, and a committed file shows what each test is hashed on. Inputs narrower than `plugin/**`: false replays, since every command crosses `plan.py`. Inputs as every tracked file: correct but replays nothing after a doc-only commit, the 49 in 153 commits the reading counted.

### `tests/suite` is the one way to run the suite as tasks

`tests/suite [--affected | --force] [name...]`, from the worktree's root, inside the devenv shell (it refuses outside one, as `tests/run` does):

- no arguments: every task, `moon exec tests:#suite --on-failure continue`;
- names: those tasks, `moon exec tests:t-<name> …`;
- `--affected`: the tasks whose inputs differ from the merge-base with `main`, uncommitted edits included (`--affected remote`); the rest are not run;
- `--force`: every selected task without the cache (`-f`), for a proof or a suspected stale replay.

It sends moon's own output to `.moon/cache/suite.log` and then reports from `.moon/cache/runReport.json`, in `tests/run`'s words: `ok    t-<name>`, with `   (replayed)` on a cached one, `FAIL  t-<name>` followed by that task's output (which ends with `tests/run`'s own `FAIL` line, scratch path and last lines), and `<n> passed (<k> replayed), <m> failed`. It exits 0 only when nothing failed. When moon stops before running any task (a configuration error) it prints the log's tail and exits non-zero. A run of `tests/suite` with nothing selected says so and exits 0.

Its lines match `tests/run`'s, so the gate's output reads the same as before and `bolt-verify.sh` parses `FAIL  <name>` unchanged. `tests/run` stays: each task runs it for one test, a person can still run it, and the collision proof runs it serially.

Alternatives: the gate running `moon exec` directly: a configuration slip would show as moon's raw output, and the verification's `Failed:` fields would need a second parser. `moon run`: stops at the first failure, so the gate would name one failing test of several and the rest would neither run nor be archived. Selecting with `tests:*`: works, but moon's docs don't name it; the task tag is documented. `--affected --base bolt/<bolt>`: exact for a unit, but leaves uncommitted edits out, and `tests/suite` would have to work out which bolt a place belongs to. Against `main`, a bolt that already holds a change to `plugin/` makes every test affected, and those the unit didn't touch replay from the bolt's verification, so the cost of the wider selection is a cache check.

### The archives are shared through the git common dir, made at shell entry

`devenv.nix` gains `pkgs.moon` and an `enterShell` that, as switchboard-kit's does, makes `<git common dir>/moon-outputs`, makes `.moon/cache` a real directory in the checkout, links `.moon/cache/outputs` to the shared directory, and exports `MOON_TOOLCHAIN_FORCE_GLOBALS=true`. Only the archives are shared; the rest of `.moon/cache` holds the checkout's own state and stays per checkout, as moon's CI guide says. `.gitignore` gains `.moon/cache/`. Every worktree of crew on a host and its main checkout then replay each other's passes, and two runs at once in two checkouts write the same archive harmlessly.

Alternatives: making the link in `tests/suite`: the link would exist only for runs through it, and the verification's copy, whose git common dir is its own, would still need it made by hand. A shared `.moon/cache` as a whole: it records each checkout's absolute paths.

### The verification's copy becomes a one-commit git repository

`bolt-verify.sh` still exports the bolt's revision with `git archive` into its own `crew-verify.XXXXXX` directory, so later merges never change files under a run. In that copy it then runs `git init -q`, `git add -A` and one `git commit` that reads no host or user git configuration (Task notes 2.1), links `.moon/cache/outputs` to `<git common dir of the bolt's repository>/moon-outputs` (it already knows that directory), and runs `env CREW_TEST_LIVE= ./tests/suite` there in place of `./tests/run`. The copy's hashes are then the bolt worktree's, so a gate that just passed the same tree is replayed. The repository is crew's own scratch, removed with the copy; it is no worktree of crew's (`read.4`).

Alternatives: run in the bolt's worktree: a later merge would change its files mid-run (the gate's design). Keep the plain export: moon caches nothing there, so every verification would run the whole suite again in full, the twenty minutes record 0008 means to save.

### The gate runs `tests/suite`

`.config/wt.toml`'s gate becomes `suite = "devenv shell -- env CREW_TEST_LIVE= tests/suite"`; emptying `CREW_TEST_LIVE` stays although the live test is no task, so the gate's command still says it never runs live. The file's opening comment says the gate and the verification run the suite as parallel moon tasks and replay what already passed. The hook's command changes, so worktrunk asks every host's user to approve it again (Migration Plan).

### Proving the tests don't collide

One full serial run, `tests/run`, and one full parallel run without the cache, `tests/suite --force`, at moon's default concurrency, both on the same tree, must both print `0 failed`. A test that fails only in parallel is fixed in place: whatever it shares moves under its `$T`, and a wait bounded in time is bounded generously enough for a loaded machine (as long as a minute where a test now waits seconds), never removed. The coder runs the parallel run at least twice, and reports both runs' times.

### Agents run only the tests their change affects

- CLAUDE.md "Tests": while working, run the tests your change affects, `tests/suite --affected`, or the ones you name, `tests/suite <name>…`; `tests/run <name>` shows one test's whole output. Never run the whole suite by hand: every merge's gate runs it and replays what already passed, and the bolt's verification runs it after. After adding or removing a test, or changing what one reads, run `tests/moon-tasks` and commit `tests/moon.yml`. The gate's time becomes "about the longest test, less when it replays".
- `coder.md`, after the sentence on running tests with moon: never run the whole suite by hand; the merge's gate runs it.
- `verify.md`: if the check runs tests, it runs only those the change affects, as CLAUDE.md says, never the whole suite, which the merge gate runs.
- `construct.md`: a unit's tasks end with the tests its change affects green, not the whole suite, which the merge gate runs.

Each is pinned in `t-briefs.sh` (`tests.6`). The three briefs are every kit's; the sentences are true of switchboard-kit, whose gate runs its unit tests the same way.

Alternative: a check in crew that refuses `tests/run` with no names from an agent (`roles.3`): no agent has broken this rule yet, and `roles.3` asks for a check once one does.

### The rules and the record

`core.md` `code.1`: devenv declares only jq, moon, python3 and recutils; its details add record 0008 as a source. `tests.md` `tests.5` keeps its words and drops "Not built: `_open.md`"; `_open.md` drops its `tests.5` line. README's tools line names moon in `devenv.nix`, and its tests paragraph names `tests/suite`.

## Risks / Trade-offs

- [A tool outside the inputs changes — openspec, wt or git on the host — and a stale pass replays] → Tools from devenv are covered by `devenv.lock`; the host's are not. `tests/suite --force` reruns without the cache, and archives older than seven days are pruned anyway. Accepted: hashing host tools would need their versions read on every run.
- [A test reads a file of crew's by a path the check can't see (not through `$CREW` or `$TESTS`)] → None does today; the check covers the form every test uses, and review of a new test covers the rest.
- [Running every test at once loads the machine, and two merges in a row run two suites at once] → moon caps it at the CPU count; contention is accepted by record 0008. A replayed run costs almost nothing.
- [A task that failed in a checkout runs again there even when another checkout has passed the same tree] → It costs one run of that test, only after a failure.
- [moon's seven-day pruning removes an archive another checkout would have replayed] → That test runs again; nothing is wrong, only slower.
- [The coder's `tests/suite --affected` on a bolt holding other work selects every test] → Those it didn't touch replay from the bolt's verification; the selection costs a cache check.
- [The first shell on each host after this lands waits for devenv to evaluate again] → About twenty seconds, once per host.

## Migration Plan

1. Before this unit's merge stage, on mac-studio: the user runs `wt config approvals add` in crew and approves the changed gate command. The unit's own merge is gated by the new command, read from the unit's place.
2. Merge as usual. The gate runs the suite as tasks; the bolt's verification replays it.
3. Before any merge on the box after the bolt lands: the user approves again in `/workspace/crew/main` there.

Rollback: revert the change; the gate and the verification run `tests/run` serially again, and `.moon/cache` directories are left ignored.

## Proof on real work

Once this unit has merged into its bolt (1–4), and once the bolt has landed and every host has pulled (5–6):

1. This unit's merge printed one line per test and `… passed (… replayed), 0 failed` before the bolt moved, in a few minutes rather than twenty.
2. From `bolts/<bolt>` on mac-studio, `sh .config/hooks/bolt-status.sh` read `green` for the bolt's head, and the run's log shows every test replayed, ending within a minute or two of starting.
3. The next unit or fix merged into the bolt: its coder ran `tests/suite --affected` (or named tests) and never the whole suite, and its gate replayed what the coder had passed.
4. A change touching only one test file reran only that test at its gate.
5. main-level ops's landing showed the gate replaying the bolt's verified tree, and main moved after `0 failed`.
6. On the box, after the user's approval there and its first shell, a merge into a bolt was gated and verified the same way.

## Task notes

**1.1** `devenv.nix`: add `pkgs.moon` beside jq, python3 and recutils, and an `enterShell` that makes the archive link as Decisions give it, written after switchboard-kit's `devenv.nix` 818–834 (a stray link at `.moon/cache` itself is removed; an existing real `outputs` directory is replaced by the link). Export `MOON_TOOLCHAIN_FORCE_GLOBALS=true`. Update the file's comment to say why moon is there. `.gitignore`: `.moon/cache/`. Check: a fresh `devenv shell` in this worktree has `moon --version` reading 2.5.x and `.moon/cache/outputs` linking to `<git common dir>/moon-outputs`.

**1.2** `.moon/workspace.yml`: the project, vcs, telemetry and hasher settings as Decisions give them, with a comment saying what moon is for here and that every input a test reads must be named. `tests/moon-tasks`: bash or standard-library Python (`code.1`), no arguments writes `tests/moon.yml` (with a header saying it is generated and by what), `--check` writes nothing. Parse `# Reads:` only from the opening comment block. The reference check: every `$CREW/<path>` and `$TESTS/<path>` in a test (strip a trailing quote or `)`; `$CREW/plugin/…`, `$TESTS/lib.sh`, `$TESTS/stubs/…` and the test's own file are already inputs) must fall under one of its task's inputs. Add `# Reads:` lines to `t-dev-shell.sh`, `t-docs.sh`, `t-merge-gate.sh` and `t-sites.sh` as Context lists. Generate `tests/moon.yml`.

**1.3** `tests/suite`, bash, written for bash 3.2 as `tests/run` is. Refuse outside devenv with `tests/run`'s message; refuse when `moon` or `jq` is missing; run `tests/moon-tasks --check` first. Map names as `tests/run` does (`merge`, `t-merge` and `t-merge.sh` all mean `tests:t-merge`). Read the statuses with jq from `runReport.json` (actions labelled `RunTask(tests:t-…)`, statuses `passed`, `cached`, `failed`, `failed-and-abort`, `timed-out`); remove the report before the run so an old one is never read. A failing task's output is in its state directory under `.moon/cache/states/` (check the path moon 2.5.3 uses); print it whole, since `tests/run` already trims to the last lines. Order the lines by test name.

**1.4** `tests/t-suite.sh`, with the guard line, an opening comment and its own `# Reads:` line. In a scratch repository under `$T` holding crew's `.moon/workspace.yml`, `tests/suite`, `tests/moon-tasks` and a stand-in `tests/run` (it prints `ok    t-x` or `FAIL  t-x` and fails when a file named `red-<name>` exists), with two or three trivial `t-*.sh` files, a `plugin/` file and a scratch outputs directory linked as the shell links it: a first run passes every test with none replayed; a second replays all; a test-only edit reruns that test alone; a `plugin/` edit reruns all; a red test is named on a `FAIL` line, the others still run, and the exit is non-zero; it runs again on the next run; `--affected` on a branch touching one test selects only it; a new `t-*.sh` without regeneration refuses naming it; a test reading `$CREW/README.md` without declaring it refuses naming the file; `t-sites-live.sh` gets no task; a `plugin/__pycache__/` file changes no hash; a second checkout (a `git worktree add` under `$T`) replays the first's passes. Use the shell's real moon.

**2.1** `.config/hooks/bolt-verify.sh`: after the export, make the copy a one-commit repository (`git -c user.name=crew -c user.email=crew@localhost -c commit.gpgsign=false commit -q -m <rev>`, with `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null` so no host hook or signing setting runs), link `$copy/.moon/cache/outputs` to `$common/moon-outputs`, and run `env CREW_TEST_LIVE= ./tests/suite`. Each step's failure is written to the log and records red, as the export's does. Update the header comment. `.config/wt.toml`: the gate's command and the opening comment as Decisions give them.

**2.2** `tests/t-merge-gate.sh`: its stand-in becomes `tests/suite` (keep a stand-in `tests/run` only if the test still needs one). The stand-in's way of telling a copy from a checkout changes, since the copy now holds a `.git` directory: a worktree's `.git` is a file and the main checkout's is crew/main's; use a marker the test controls, such as the copy's path under `$TMPDIR`. Add: the verification's copy is a git repository with one commit whose tree is the bolt's head, and its `.moon/cache/outputs` links to the repository's `moon-outputs`. Update the approval it greps for to the new gate command.

**3.1** Run `tests/run` (serial) and `tests/suite --force` (parallel) in this worktree, then `tests/suite --force` once more; all three print `0 failed`. Fix any test that fails only in parallel, as Decisions say, and name each fix and the three runs' times in the summary.

**4.1** `CLAUDE.md` "Tests" as Decisions give it, keeping the lines on devenv, the stubs and `rewrite`; "Proving and landing a bolt" says the verification replays the gate's pass. README's tools line and tests paragraph. No new text says `devenv shell --` (`tests.7`; `t-dev-shell` checks).

**4.2** The three briefs, one sentence each, as Decisions give them, and their key phrases in `tests/t-briefs.sh` beside the existing brief checks.

**4.3** `docs/architecture/core.md` `code.1` and its details; `tests.md` `tests.5`'s details; `_open.md`'s `tests.5` line removed.

**5.1** `tests/suite --affected` prints `0 failed` in this worktree (it selects every test, since `devenv.nix` is every task's input), and a second run replays every test; give both counts.
