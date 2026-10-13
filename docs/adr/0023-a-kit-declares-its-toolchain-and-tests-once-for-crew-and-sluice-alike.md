---
number: 23
title: A kit declares its toolchain and tests once, for crew and sluice alike
status: accepted
date: 2026-10-12
decision-makers:
- Chuck Swanberg
---

# A kit declares its toolchain and tests once, for crew and sluice alike

Deciders: the user, whose rulings in sluice's session 37713ae2 (2026-10-11 and 12) set the split this record applies to crew, and who ruled on this record's drafts the same day, through the main session; written by the toolchain workstream. Two questions it raised are held for an elaboration, below.
Amends: the `bolt-teams` design (2026-10-05), whose new worktrees run the kit's `crew-prepare`; record 0008, on crew's moon, for point 5.
Sources: the user's words quoted below; sluice's `phase-2-git-state` branch as of 2c0db91 (`crates/sluice/src/profiles/checks.rs` and `moon.rs`, `crates/sluice-core/src/policy.rs`, `.prototools`, `.moon/toolchains.yml`, `devenv.nix`, `docs/plans/phase-1-integrations.md` section 4 and `phase-1-pass-2.md`); crew's `plan.py` `PLACE` (5142add); the kit survey and the probes below.

## Context and problem statement

**How a worktree is made ready today.** When crew makes a bolt's, unit's or fix's worktree it runs `<kit>/.devenv/profile/bin/crew-prepare` from the kit's main checkout's devenv profile. crew reaches into another repository's profile for a script named after crew; the user: "this is bad design".

**Where sluice has got to.** The user: "We have a defined separation between Devy and V (the main set of system-level tools) and Proto tools (the application-level things)", and "we should manage moon install via prototools". On sluice's branch now:
- devenv carries the system tools, proto 0.63.1 among them (moonrepo's release build); `.prototools` pins the application tools, `moon = "2.6.1"` and `rust = "1.98.1"`; entering the shell runs `proto install` into a proto home of the repository's own under its git common dir, and activates it; `MOON_HOME` is the repository's too, since moon puts both homes' `bin` ahead of everything on a task's PATH.
- A repository declares its toolchain and its test runner in its policy, `.config/sluice.toml`, under `[tests]`: `toolchain` (a command, as a list, that prints shell code setting the tools up; sluice's own is `["devenv", "print-dev-env"]`) and `runner` (`"moon"`, or `"command"` with a `command`). The branches' gates name their required checks under `[branches."<pattern>"] required`.
- Before a run, outside the executor, sluice runs `toolchain` in the place with a cleaned environment and keeps what it prints; the moon runner then runs `moon setup` inside it, so whatever needs the network or the user's home happens there; every command of the run sources the kept script with the `bash` on the run's PATH (macOS's `/bin/bash` 3.2 cannot parse devenv's script). The moon runner's floor is moon 2.6.
- The user, ruling on this record's first draft: "it is doing the devenv print-env-dir command then using proto to install moon, then moon setup. to do this we need a moon adapter. crew should not assume moon or devenv. it should have a similar toolchain and test adapter like sluice. eventually crew->flywheel-next and flywheel-next will compose sluice".

**What sluice asks of crew.** `SLUICE_AGENT` set to the agent's crew name (sluice's rule core.1 keeps crew's name out of its code; the user agreed the name), and, in the user's words, "we should try to move CREW outside of SLUICE's control to a design where we don't check out the bolt branch as a work tree". A branch sluice moves through gix, while a worktree holds it, leaves that worktree's index and files behind its HEAD; and sluice's branch protection refuses every other move of a protected branch, `git rebase` and `git reset` among them.

**The kits, read 2026-10-12** from mac-studio's checkouts and, for the box's kits, GitHub's main (the box itself not read):

| kit | host | devenv | moon and proto | `crew-prepare` | post-merge hook |
|---|---|---|---|---|---|
| crew | mac-studio | yes | moon 2.6.1 from devenv (this branch) | none | `bolt-verify.sh`, on the target's revision |
| swancloud | mac-studio | yes | none | none | `flake-gate verify`, on the worktree's own branch |
| sluice | mac-studio | yes | proto 0.63.1; moon and Rust in `.prototools` | none | none |
| flywheel-next, flywheel-web | mac-studio | yes | none | none | none |
| paymaster, strategy | mac-studio | no | none | none | none |
| switchboard-kit (f6c0dbfd) | box | yes | moon and proto from nixpkgs-unstable; bun and node from nix | `bun install --frozen-lockfile` | `post-merge-verify`, in the target's worktree |
| breadboard-kit, aws-bootstrap | box | yes | none | none | none |
| atlas-kit (no team) | box | yes | moon 1.41.8 through `.prototools` | none | none |

switchboard is the one kit with a `crew-prepare`, and each of its suite scripts already runs the same install before it starts. No kit has a `.config/sluice.toml` yet.

**Probes on moon 2.6.1, in scratch workspaces:**
- `moon setup` installs what the toolchain config pins and no dependencies. The first task installs them, as an action ahead of it, through the user's shell: with bun pinned to 1.2.23 and proto's directories not on PATH, it ran the host's bun 1.3.13.
- With no toolchain configured, moon sets nothing up and runs the shell's tools, with `MOON_TOOLCHAIN_FORCE_GLOBALS` or without it.
- With `.prototools` pinning `python = "3.13.15"` and `uv = "0.13.0"`, `.moon/toolchains.yml` naming `unstable_python` (`packageManager: uv`) and `unstable_uv`, both `versionFromPrototools`, and a `pyproject.toml` in the project's folder with `pytest` in its dev group: `moon setup` installed both in 5 s; the first task made the project's `.venv`, synced pytest 9.1.1 into it, wrote `uv.lock`, and ran `python3` as `.venv/bin/python3`, 3.13.15. moon 2.6.1 names these two toolchains `unstable_`.
- crew's tests run on devenv's Python 3.14.7, while every host runs crew on its own `python3`, 3.13.15 on mac-studio. proto offers 3.13.15.
- The box enables nix-ld (swancloud's `modules/workspace-box/prebuilt.nix`), so binaries proto installs run there.

## Decision drivers

- crew assumes neither moon nor devenv, and names no kit's script.
- A kit says once how its tools are set up and its checks run, and crew and sluice read the same words. sluice stands on its own; flywheel will use sluice's SDK, and then takes over crew's steps on the same declaration, with no kit changing anything.
- crew's tests run on what crew runs on.

## Decision outcome

1. **The split, as sluice has it.** devenv holds the system tools, proto among them. proto holds the application tools a kit pins in `.prototools`, moon among them, and `.moon/toolchains.yml` reads the pins moon runs tasks with. devenv's shell runs `proto install` and activates the pins, with `PROTO_HOME` and `MOON_HOME` of the kit's own under its git common dir. `MOON_TOOLCHAIN_FORCE_GLOBALS` goes.

2. **One declaration, sluice's file for now.** A kit declares its toolchain and its test runner once, in the `[tests]` table of `.config/sluice.toml`, with sluice's keys and meanings: `toolchain`, the command that prints the kit's toolchain as shell code; and `runner`, `"moon"`, or `"command"` with `command`. crew reads that table from the worktree in hand and nothing else of the file. A kit that does not merge through sluice writes the same table; whether its merges go through sluice is still crew's `sluice = true` flag in `.config/crew.toml` (`teams.5`). A kit with no file, or none of these keys, declares nothing, and crew does nothing for it. A file crew cannot read refuses, naming the file and the key (`read.1`). The user: "use sluice.toml. but really should this all be flywheel.toml? i want sluice to stand on its own and i want flywheel to use the sluice sdk. maybe we use sluice.toml now and then eventually it just becomes flywheel.toml when we have it". So sluice stays a tool of its own, flywheel will use sluice's SDK, and the file becomes `flywheel.toml` then; crew reads it in one place, `plugin/lib/kit.py`'s `DECLARATION`, so the rename is one edit.

3. **Two adapters in crew, shaped as sluice's.** crew's toolchain adapter and test adapter are a port of the steps sluice's check profile runs before and around a run, in one module, `plugin/lib/kit.py`, with the decisions there and the acts in `plan.py`:
   - **toolchain**: run `toolchain` in the worktree, on the team's host, with stdin closed and an environment cleaned as sluice cleans it (`PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `LANG`, `TERM`, `PROTO_HOME`, `MOON_HOME` and `LC_*`; nothing of `GIT_*`, `MOON_*`, `DEVENV_*`, `DIRENV_*`, `CREW_*` or a Claude session's), and keep what it prints in the worktree's git directory, outside its tree;
   - **in the toolchain**: run any later command in the worktree as `bash -c 'source "$0" >&2; exec "$@"' <script> <command>`, by the `bash` on PATH;
   - **setup**, the test adapter's: `moon --version`, refusing a moon below 2.6, then `moon setup`, both in the toolchain, for `runner = "moon"`; nothing for `"command"`;
   - **run and read**, the test adapter's, sluice's too (the required tasks by tag through `moon query tasks`, `moon exec` of them with `--on-failure continue`, each task's outcome from `.moon/cache/runReport.json`; or `sh -c <command>` as one check): crew ports them when it first needs to run a kit's checks itself, which waits on the held bolt question below.
   When flywheel uses sluice's SDK, it calls sluice for these steps on the same declaration; crew's module is what it replaces.

4. **A worktree is made ready by the kit's declaration.** When crew makes a bolt's, unit's or fix's worktree, it runs the toolchain step and then the test adapter's setup there, on the team's host, before any agent starts: sluice's steps in sluice's order, which for sluice's own declaration are `devenv print-dev-env` (whose shell entry runs `proto install`, moon among the pins) and then `moon setup`. It runs them again when it finds the worktree already there, so a command run again after a failure sets it up. Dependencies install as the kit's moon config says, before the first task that needs them. `crew-prepare` goes. switchboard-kit, the one kit that had it, keeps working until it writes its declaration: each of its suite scripts runs `bun install --frozen-lockfile` before it starts.

5. **crew on proto.** crew's devenv carries proto 0.63.1, jq and recutils. crew's `.prototools` pins `moon = "2.6.1"`, `python = "3.13.15"`, the hosts' minor, and `uv = "0.13.0"`; `.moon/toolchains.yml` pins proto and reads the Python and uv pins through moon's `unstable_python` and `unstable_uv`; `tests/pyproject.toml` holds pytest in its dev group, locked in `tests/uv.lock`, and moon syncs it into `tests/.venv` before the first task. crew's test tasks are tagged `check-full`, beside sluice's `check-fast`, in place of `suite`, a name the user called one that says nothing of what it holds. crew declares its own toolchain like any kit, `toolchain = ["devenv", "print-dev-env"]` and `runner = "moon"`, so crew's own worktrees are made ready through crew's adapters. `code.1` says so.

6. **`SLUICE_AGENT`** is set for every agent crew starts, the same as `CREW_AGENT`: crew-role sets it, and the session-start hook gives it back on a resume (`teams.6`).

Held for an elaboration, and not decided here:
- **How crew's agents come to work inside their kit's toolchain.** The user: "i'm not sure about this. seems like it's wrong. but i am probably missing something. i'd want an elaboration session to understand this". `openspec/explorations/agents-in-the-toolchain/reading.md` sets out what it needs. Closed 2026-10-13 by record 0024: no session is entered into the shell at its start; an agent runs the kit's tools through the shell per command, and the host carries no application tool.
- **A bolt's branch when sluice moves it.** A branch sluice moves while a worktree holds it leaves that worktree behind its HEAD, and sluice's protection refuses crew's own moves of it. The user was not persuaded by the designed answer, a checkout on `land/<bolt>` ("isn't it just reversing the decision that bolts don't have branches?"; "won't this just be sluice doing the verification?"). `openspec/explorations/bolt-branches-under-sluice/reading.md` frames it by which kits merge through sluice, and when; the change `no-worktree-holds-a-bolts-branch` is one option there, designed and not decided.

### Consequences

- crew names no kit script and reads no kit's profile. A kit gets nothing from crew until it declares its toolchain or its runner, and moves to devenv, proto and moon when it chooses.
- A kit's declaration is sluice's policy file even before the kit merges through sluice, and becomes `flywheel.toml` with one edit in crew when flywheel has it.
- A new worktree costs the kit's toolchain step in crew's command: for a devenv toolchain, about 20 s cold, which sluice plans to cache per revision of the toolchain's files (its piece 11).
- crew's tests run on Python 3.13.15, the hosts' minor, from proto; pytest comes from a lock file, synced per worktree by moon, which needs the network once per host.
- moon 2.6.1 calls its Python toolchains `unstable_`: a moon upgrade may rename them in crew's config.

## Considered options

For where the declaration lives:
- **crew reads sluice's file** (chosen, until flywheel has `flywheel.toml`): one declaration, read by both, in sluice's schema; crew follows sluice's keys as they change.
- **A file of its own both read** (`.config/toolchain.toml`): neutral, but sluice reads its whole policy from one file at the target branch's revision (sluice ADR 0007), so this changes sluice.
- **The same keys in crew's `.config/crew.toml`**: no coupling, and two declarations that drift in every kit on sluice.
- **crew calls sluice** for the steps: one implementation, once sluice is installed on every host crew runs on, which it is not yet; flywheel, using sluice's SDK, is where this lands.

For making a worktree ready:
- Keep `crew-prepare`: the user's "bad design".
- `moon setup` in the worktree's devenv shell, this record's first draft: assumes moon and devenv.
- worktrunk's `pre-start` hook, run by crew: the kit's own words, but each host approves each kit's hooks, and `--yes` is what crew's rules keep from agents.

For crew's Python:
- devenv's Python pinned to 3.13, the first draft: the user ruled for proto ("Add proto now").
- proto's Python with pytest installed into it by pip: a shared interpreter changed outside any lock.
