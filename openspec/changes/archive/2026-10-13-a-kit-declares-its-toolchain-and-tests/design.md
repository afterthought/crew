# Design

## Context

See proposal.md for why and record 0023 for the decision; this is how. What shapes it:

- **Making a worktree.** `make_place` in `plan.py` runs `PLACE` on the team's host through `host_run`: `git worktree add` in the kit's main checkout, then `crew-prepare` from `<main>/.devenv/profile/bin` when it is executable there. `PLACE` exits at once when the path exists. `crew bolt give`, construct and `crew fix` all make their worktrees through it.
- **sluice's declaration and steps** (`crates/sluice/src/profiles/checks.rs` and `moon.rs` on sluice's `phase-2-git-state`, 2c0db91): `[tests] toolchain` is a list of strings, the command first; `[tests] runner` is `"moon"` or `"command"`, the latter with `[tests] command`. Before a run, sluice runs `toolchain` in the place with stdin from `/dev/null`, a cleared environment holding only `PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `LANG`, `TERM`, `PROTO_HOME`, `MOON_HOME` and `LC_*`, refuses when it exits non-zero with its stderr, and writes its stdout to the run's directory; every later command is `bash -c 'source "$0" >&2; exec "$@"' <script> <argv>`, with `bash` from PATH because devenv's printed script uses bash 4's `;&`. The moon runner refuses a moon below 2.6, and runs `moon setup` in the toolchain before the run.
- **moon 2.6.1** (record 0023's probes): `moon setup` installs the pinned toolchains and no dependencies; a task's first run installs its project's dependencies; with `unstable_python` (uv) and `unstable_uv` configured and a `pyproject.toml` in a project's folder, moon makes that folder's `.venv`, syncs the dev group into it and runs the project's tasks on `.venv/bin/python3`.
- **crew's shell** declares jq, moon (2.6.1 from moonrepo's release, on this branch), `python3` with pytest (3.14.7) and recutils, and exports `MOON_TOOLCHAIN_FORCE_GLOBALS=true`, which `tests/suite` keeps through its clearing of `MOON_*`. Hosts run crew on their own `python3`, 3.13.15 on mac-studio.
- **crew already reads a kit's TOML**: `gather.sluice` reads `sluice = true` from the main checkout's `.config/crew.toml` with `tomllib`.

Rules relied on: `read.1` (a declaration crew cannot read, and a step that fails, refuse in the file's or the tool's words), `read.4` (crew sets up only a worktree it made), `code.1` (standard library: `tomllib`; amended below), `code.2`, `code.7` (what to run is decided by functions of the declaration, tested in the logic tier), `teams.6` (amended for `SLUICE_AGENT`, built), `teams.9` (what bash evals stays shell assignments; the steps' output goes to standard error), `tests.4`, `tests.10` (new inputs named), `tests.11` and `tests.12`, `docs.2`. Pages whose area this touches: `plan.md`, `teams.md`, `tests.md`, `docs.md`, `core.md`.

Departures: `code.1` names moon and python3 as devenv's; this change moves them to proto, and `code.1` is amended as below.

## Goals / Non-Goals

**Goals:**
- crew assumes neither moon nor devenv of a kit, names no kit script and reads no kit's profile.
- A kit's declaration means the same to crew as to sluice, so flywheel, using sluice's SDK, can take over crew's steps on the same file, then named `flywheel.toml`.
- A worktree crew makes in a kit with a declaration has its toolchain printed and its runner set up before its agent starts.
- crew's tests run on the Python minor the hosts run crew on.

**Non-Goals:**
- How agents come to work inside their kit's toolchain: held for an elaboration.
- The test adapter's run and read: crew ports them when it first runs a kit's checks itself, which waits on the held bolt question (`openspec/explorations/bolt-branches-under-sluice/reading.md`); this change builds its setup.
- Caching a kit's printed toolchain across worktrees (sluice's piece 11).
- Changing any kit: switchboard-kit writes its declaration and drops `crew-prepare` in its own repository; until it does, it keeps working, since each of its suite scripts runs `bun install --frozen-lockfile` before it starts.

## Decisions

### The declaration

`plugin/lib/kit.py`, a new module, standard library only, reads a declaration from the text of a worktree's `.config/sluice.toml`:

```python
def declared(text):
    """A kit's declaration from its .config/sluice.toml (record 0023): {"toolchain": [argv] | None, "runner": "moon" |
    "command" | None, "command": str | None}, or None when there is no file. Refused, naming the key, when the file
    is not TOML, toolchain is not a non-empty list of strings, runner is neither "moon" nor "command", or runner is
    "command" with no command."""
```

It reads only `[tests]`'s `toolchain`, `runner` and `command`; everything else in the file is sluice's. The file's name is `kit.DECLARATION`, the one place crew names it, so its rename to `flywheel.toml` is one edit. A file with no `[tests]` declares nothing. The file is read from the worktree being made ready, on the team's host: the script that makes the worktree prints it after `git worktree add`, between two marker lines so an absent file reads apart from an empty one, and `make_place` parses it in crew's process.

### The adapters

`kit.py` holds the decisions; `plan.py`'s `make_place` runs them on the host.

```python
KEEP = ("PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "TERM", "PROTO_HOME", "MOON_HOME")

def readying(decl):
    """What makes a worktree ready, in order (plan.17): ("toolchain", argv) when the kit declares one, then
    ("setup", ["moon", "setup"]) when its runner is moon; nothing for a kit that declares neither."""

def in_toolchain(script, argv):
    """argv run inside the printed toolchain: sourced by the bash on PATH, its output to stderr."""
    return ["bash", "-c", 'source "$0" >&2; exec "$@"', script, *argv] if script else list(argv)

def moon_floor(version):
    """Why `moon --version`'s output is below the moon runner's floor, 2.6, or None."""
```

On the host, a step runs in the worktree as `env -i <KEEP and LC_* as the host has them> <argv> </dev/null`, from a script `make_place` sends through `host_run`, so the environment of the command that made the worktree (an agent's session, perhaps in another checkout's shell) never reaches the kit's toolchain. The toolchain step's standard output goes to `<worktree's absolute git dir>/crew/toolchain.sh`, which `git worktree remove` takes with the worktree; its standard error goes to the command's. The setup step runs `in_toolchain(script, ["moon", "--version"])` first and refuses through `moon_floor`, then `in_toolchain(script, ["moon", "setup"])`.

A step that fails refuses the command through `fail()`, naming the worktree and the step, with the tool's last lines, and saying that running the command again sets the worktree up (`read.1`, `code.2`). The worktree is left made.

### When a worktree is made ready

`PLACE` keeps the worktree's making and drops `crew-prepare`; `make_place` then reads the declaration and runs `readying`'s steps, whether the worktree is new or was already there, so a run after a failure sets it up. For a kit with no declaration nothing runs and nothing is said.

### crew's own toolchain

- `devenv.nix` declares `proto` (0.63.1 from moonrepo's release, built as sluice's `fromRelease` builds it, hashes pinned), `jq` and `recutils`; moon and Python leave it. `enterShell` sets `PROTO_HOME` to `<git common dir>/proto` and `MOON_HOME` to `<git common dir>/moon-home`, runs `proto install --config-mode upwards` (quiet; where it cannot, what is installed is used), activates the pins with `proto activate bash --export --no-bin --config-mode upwards`, and keeps its link of `.moon/cache/outputs`; `MOON_TOOLCHAIN_FORCE_GLOBALS` goes. A comment says why each home is the repository's: moon puts both homes' `bin` first on a task's PATH, and the user's own moon must never run there.
- `.prototools`: `moon = "2.6.1"`, `python = "3.13.15"`, `uv = "0.13.0"`, with a comment that Python is the minor the hosts run crew on.
- `.moon/toolchains.yml`: `proto.version: '0.63.1'`; `unstable_python` with `versionFromPrototools: true` and `packageManager: uv`; `unstable_uv` with `versionFromPrototools: true`.
- `tests/pyproject.toml`: a project with no dependencies, `requires-python = ">=3.13"`, and `pytest==9.1.1` in its `dev` group; `tests/uv.lock` as moon's first sync writes it, committed; `tests/.venv/` in `.gitignore`.
- `.config/sluice.toml`: `[tests]` with `toolchain = ["devenv", "print-dev-env"]` and `runner = "moon"`, so crew's own worktrees are made ready through crew's adapters like any kit's.
- The tasks' tag is `check-full`, beside sluice's `check-fast`, in place of `suite` (`tests.5`): `tests/moon-tasks` writes it and `tests/suite` targets `tests:#check-full`.
- `tests/moon-tasks`: every task's inputs gain `/.prototools`, `/.moon/toolchains.yml`, `/tests/pyproject.toml` and `/tests/uv.lock`, and the command core gains `/plugin/lib/kit.py`. `tests/suite` keeps `MOON_HOME` and a caller's `MOON_CONCURRENCY` through its clearing of `MOON_*`.
- CLAUDE.md's "`python3 -m pytest tests/py -q` for its output" becomes `moon run tests:logic`, since the shell's `python3` has no pytest and the tests' does.

### Every agent carries its name for sluice (built)

`crew-role` exports `SLUICE_AGENT=$NAME` beside `CREW_AGENT` and `CREW_LABEL`; `session-start` writes it with them when herdr resumes an agent; `teams.6` names it (4bdc6d0).

## Rules this changes

Amended with the build, on the user's acceptance of record 0023; `teams.6` was amended with its own build.

- `code.1`'s last clause: "devenv declares only proto, jq and recutils; `.prototools` pins moon, Python at the minor the hosts run crew on, and uv; pytest, the tests' one dependency, is locked in `tests/uv.lock`."
- A new `plan.17`: "crew makes a worktree ready only through its kit's declaration in `.config/sluice.toml`, by the declared toolchain and then the declared runner's setup, run in the worktree on the team's host with sluice's cleaned environment; a kit that declares nothing gets nothing; crew names no kit script, reads no kit's profile and assumes neither moon nor devenv."
- `tests.5` names the tag `check-full`, and its details the user's word on `suite`.
- `tests.md`'s `paths` gain `.prototools` and `.moon/**`, and `plan.md`'s gain `plugin/lib/kit.py`; `core.md`'s table rows with them.

## Risks / Trade-offs

- [A cold devenv toolchain in a new worktree] → about 20 s in crew's command, as `crew-prepare`'s install cost before it; sluice's piece 11 measures and caches it, and crew's adapter takes that when it lands.
- [moon renames `unstable_python` or `unstable_uv`] → crew's suite fails on the moon upgrade, in crew's own tree, before any landing; the names are pinned beside moon's version in `.prototools`.
- [The hosts move to Python 3.14 and crew's pin stays] → crew's tests run behind the hosts', as they run ahead of them today; `code.1` holds the two together, and the pin's comment names the hosts' version.
- [A kit's declaration names a runner crew does not know] → refused with the key's words; crew follows sluice's runners as they are added.
- [A kit on a branch changes its declaration] → the worktree is made ready from its own tree, which at making is its base's.
- [proto's Python on the box] → a downloaded build, which runs there because the box enables nix-ld.

## Proof on real work

Once the bolt has landed and every host has pulled: the next unit crew makes in a kit that declares its toolchain (crew's own, then sluice's) has its toolchain script in its git directory and its runner set up before its construct agent starts; the next in a kit that declares nothing starts as before. The conductor that sees each says so; nothing is the user's.

## Task notes

### 1.2

As *crew's own toolchain* says. Generate `tests/uv.lock` by running `moon run tests:logic` once in the shell after the files are in place, and commit it. `tests/t-suite.sh` asks for moon 2 from crew's toolchain in its words. `tests/t-dev-shell.sh` gains a case: inside crew's shell `moon --version` is 2.6 or later and `python3 -c 'import sys; print(sys.version_info[:2])'` run as a moon task gives `(3, 13)`. Run `tests/moon-tasks`, then `tests/suite --affected`.

### 2.1

`kit.py` as *The declaration* and *The adapters* say, and `tests/py/test_kit.py`: a full declaration; none (no file); a file with no `[tests]`; each refusal, naming its key; `readying` for moon, command, toolchain alone and nothing; `in_toolchain` with and without a script; `moon_floor` on 2.5.3, 2.6.0 and 2.6.1. `tests/contract/test_kit.py` pins what `in_toolchain` relies on: a script holding a `case` with `;&` sourced through it by the `bash` on PATH runs the command with the script's exports and its prints on stderr; and that `git rev-parse --absolute-git-dir` in a linked worktree names a directory `git worktree remove` takes with it.

### 2.2

`PLACE` and `make_place` as *When a worktree is made ready* says; `crew-prepare`'s comment and line go. `tests/units.sh`: the fixture kit loses its `crew-prepare` stub and `.prepared` from `.gitignore`, and gains a `.config/sluice.toml` declaring `toolchain = ["sh", "tools/print"]` and `runner = "moon"`, with `tools/print` printing `export TOOLCHAIN_FROM=<its cwd>`; a stand-in `moon` first on the test's PATH prints `moon 2.6.1` for `--version` and logs `<cwd> <args> $TOOLCHAIN_FROM` to `$T/moon.log`, failing `setup` when `$T/moon-fails` exists. `tests/t-journey-units.sh`, in place of the `.prepared` checks: the log holds `<bolt's worktree> setup <bolt's worktree>` after give and `<place> setup <place>` after construct; with `$T/moon-fails`, construct is refused naming the place and the setup, and run again without it sets the place up; a kit fixture with no declaration (t-journey-plan's) gets no call. Run `tests/moon-tasks` when a `# Reads:` line changes.

### 3.1

README: a section on what a kit declares for crew, in `.config/sluice.toml`, with sluice's keys, and what crew runs from it when it makes a worktree; that crew runs nothing for a kit that declares nothing. CLAUDE.md: crew's toolchain is proto's pins in devenv's shell, and the how-to for the logic tier's output. `tests/suite --affected` ends with "0 failed".
