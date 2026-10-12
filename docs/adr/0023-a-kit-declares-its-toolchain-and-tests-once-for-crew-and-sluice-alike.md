---
number: 23
title: A kit declares its toolchain and tests once, for crew and sluice alike
status: proposed
date: 2026-10-12
decision-makers:
- Chuck Swanberg
---

# A kit declares its toolchain and tests once, for crew and sluice alike

Deciders: the user, whose rulings in sluice's session 37713ae2 (2026-10-11 and 12) set the split this record applies to crew, and who ruled on this record's first draft the same day; proposed by the toolchain workstream, and accepted only on the user's yes.
Amends: the `bolt-teams` design (2026-10-05), whose new worktrees run the kit's `crew-prepare`; record 0015, on what a carrying fix moves, for point 7; record 0008, on crew's moon, for point 5.
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
- `wt merge bolt/x --no-squash --no-remove` from a unit's worktree moves `bolt/x` when no worktree holds it; a worktree on a branch tracking `bolt/x` then reads `behind 1`, and `git merge --ff-only bolt/x` there brings it level.
- crew's tests run on devenv's Python 3.14.7, while every host runs crew on its own `python3`, 3.13.15 on mac-studio. proto offers 3.13.15.
- The box enables nix-ld (swancloud's `modules/workspace-box/prebuilt.nix`), so binaries proto installs run there.

## Decision drivers

- crew assumes neither moon nor devenv, and names no kit's script.
- A kit says once how its tools are set up and its checks run, and crew and sluice read the same words, so flywheel-next can later compose sluice in crew's place without a kit changing anything.
- crew's tests run on what crew runs on.
- Nothing crew holds breaks when sluice moves a bolt's branch.

## Decision outcome

1. **The split, as sluice has it.** devenv holds the system tools, proto among them. proto holds the application tools a kit pins in `.prototools`, moon among them, and `.moon/toolchains.yml` reads the pins moon runs tasks with. devenv's shell runs `proto install` and activates the pins, with `PROTO_HOME` and `MOON_HOME` of the kit's own under its git common dir. `MOON_TOOLCHAIN_FORCE_GLOBALS` goes.

2. **One declaration, sluice's.** A kit declares its toolchain and its test runner once, in the `[tests]` table of `.config/sluice.toml`, with sluice's keys and meanings: `toolchain`, the command that prints the kit's toolchain as shell code; `runner`, `"moon"` or `"command"` (with `command`); and, for point 7, the bolt branches' `required` checks under `[branches."bolt/*"]`. crew reads that file from the worktree in hand and reads nothing else of it. A kit that does not merge through sluice writes the same tables; sluice protects a branch only once it runs in the kit, which crew's `sluice = true` flag in `.config/crew.toml` still decides (`teams.5`). A kit with no file, or none of these keys, declares nothing, and crew does nothing for it. A file crew cannot read refuses, naming the file and the key (`read.1`).

3. **Two adapters in crew, shaped as sluice's.** crew's toolchain adapter and test adapter are a port of the half of sluice's check profile that runs before and around a run, in one module of crew's, with the same four steps:
   - **toolchain**: run `toolchain` in the worktree, on the team's host, with stdin closed and an environment cleaned as sluice cleans it (`PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `LANG`, `TERM`, `PROTO_HOME`, `MOON_HOME` and `LC_*`; nothing of `GIT_*`, `MOON_*`, `DEVENV_*`, `DIRENV_*`, `CREW_*` or a Claude session's), and keep what it prints in the worktree's git directory, outside its tree;
   - **in the toolchain**: run any later command in the worktree as `bash -c 'source "$0" >&2; exec "$@"' <script> <command>`, by the `bash` on PATH;
   - **setup**, the test adapter's: `moon setup` in the toolchain for `runner = "moon"`, refusing a moon below 2.6; nothing for `"command"`;
   - **run and read**, the test adapter's: for `"moon"`, the required tasks by tag through `moon query tasks`, `moon exec` of them with `--on-failure continue`, and each task's outcome from `.moon/cache/runReport.json`; for `"command"`, `sh -c <command>` as one check.
   When flywheel-next composes sluice, it calls sluice's profile for the same four steps, on the same declaration; crew's module is what it replaces.

4. **A worktree is made ready by the kit's declaration.** When crew makes a bolt's, unit's or fix's worktree, it runs the toolchain step and then the test adapter's setup there, on the team's host, before any agent starts; sluice's steps in sluice's order, which for sluice's own declaration are `devenv print-dev-env` (whose shell entry runs `proto install`, moon among the pins) and then `moon setup`. It runs them again when it finds the worktree already there, so a command run again after a failure sets it up. Dependencies install as the kit's moon config says, before the first task that needs them. `crew-prepare` goes; switchboard moves its `bun install` into its moon config and writes its declaration.

5. **crew on proto.** crew's devenv carries proto 0.63.1, jq and recutils. crew's `.prototools` pins `moon = "2.6.1"`, `python = "3.13.15"`, the hosts' minor, and `uv`; `.moon/toolchains.yml` pins proto and reads the Python and uv pins through moon's `unstable_python` and `unstable_uv`; `tests/pyproject.toml` holds pytest in its dev group, locked in `tests/uv.lock`, and moon syncs it into `tests/.venv` before the first task. crew declares its own toolchain like any kit, `toolchain = ["devenv", "print-dev-env"]` and `runner = "moon"`, so crew's own worktrees are made ready through crew's adapters. `code.1` is amended to say so.

6. **`SLUICE_AGENT`** is set for every agent crew starts, the same as `CREW_AGENT`: crew-role sets it, and the session-start hook gives it back on a resume (built; `teams.6`).

7. **No worktree holds a bolt's branch.** `bolt/<bolt>` is where units and fixes merge, through `wt merge` or `wt submit`, and no worktree ever has it checked out. The bolt's checkout, `<kit>/bolts/<bolt>`, is on `land/<bolt>`, a branch crew makes beside it and that tracks it; crew brings it level with `git merge --ff-only bolt/<bolt>` in the checkout whenever it reads that the bolt moved, before a proof, and when a landing begins. `land/<bolt>` is what lands: the landing rebases it onto main through the kit's hooks, as `plan.8` has the bolt's branch rebased now, and a carrying fix becomes `land/<bolt>`'s head by crew's move. In a kit that does not merge through sluice, crew verifies the bolt's head after each merge through the kit's test adapter, on the bolt's required checks; in one that does, sluice's landing is the verification, since sluice lands only a tree whose required checks passed. Built as its own change, after the one-process refactor, since both rework the same commands. What it breaks, and the answer to each:
   - **The landing and the carry** (`plan.8`, `teams.5`, record 0015): what lands, and what a carrying fix moves, is `land/<bolt>`, never `bolt/<bolt>`, so the protected branch is never rebased or reset. Once a fix has carried the bolt, the bolt's line for later fixes is `land/<bolt>`: they branch from it and merge into it.
   - **worktrunk's post-merge hooks**, which run in the target branch's worktree and, with none, in the kit's main checkout. swancloud's `flake-gate verify` and switchboard's `post-merge-verify` check the branch of the worktree they run in, so after a merge into a bolt they would check main. Each kit's post-merge verification becomes main's only; crew's own `bolt-verify.sh` and `bolt-status.sh` go, and crew's verification through its declaration replaces them. A kit with no declaration has no bolt verification from crew until it writes one.
   - **Tidying** (`plan.9`): crew knows a bolt's checkout by `<kit>/bolts/<folder>` on `land/<folder>`, a branch crew made, and removes it as now; `bolt/<bolt>` goes when the bolt is gone and main holds it (`plan.10`), and a delete sluice's hook refuses, while a submission to the bolt is still queued, is kept and named.
   - **The briefs**: the conductor's, ops's and main-ops's say the bolt's checkout is on `land/<bolt>`, kept at the bolt's head by crew, and that nobody checks out or commits to `bolt/<bolt>`.
   - **Kit tooling that names a worktree by its branch** (worktrunk's `{{ branch }}`, switchboard's dev-server names): the bolt's checkout is named `land-<bolt>` where it was `bolt-<bolt>`; it is still a branch, so nothing reads a detached HEAD.

Not decided here: how crew's agents come to work inside their kit's toolchain. The user held it for an elaboration ("i'm not sure about this. seems like it's wrong. but i am probably missing something"); `openspec/explorations/agents-in-the-toolchain/reading.md` sets out what it needs.

### Consequences

- crew names no kit script and reads no kit's profile. A kit gets nothing from crew until it declares its toolchain or its runner, and moves to devenv, proto and moon when it chooses.
- A kit's declaration is sluice's policy file even before the kit merges through sluice, so adopting sluice later changes only the file's gates.
- A new worktree costs the kit's toolchain step in crew's command: for a devenv toolchain, about 20 s cold, which sluice plans to cache per revision of the toolchain's files (its piece 11).
- crew's tests run on Python 3.13.15, the hosts' minor, from proto; pytest comes from a lock file, synced per worktree by moon, which needs the network once per host.
- moon 2.6.1 calls its Python toolchains `unstable_`: a moon upgrade may rename them in crew's config.

## Considered options

For where the declaration lives:
- **crew reads sluice's file** (chosen): one declaration, read by both, in sluice's schema; crew follows sluice's keys as they change.
- **A file of its own both read** (`.config/toolchain.toml`): neutral, but sluice reads its whole policy from one file at the target branch's revision (sluice ADR 0007), so this changes sluice.
- **The same keys in crew's `.config/crew.toml`**: no coupling, and two declarations that drift in every kit on sluice.
- **crew calls sluice** for the steps (a sluice command that prepares a place): one implementation, once sluice is installed on every host crew runs on, which it is not yet.

For making a worktree ready:
- Keep `crew-prepare`: the user's "bad design".
- `moon setup` in the worktree's devenv shell, crew's first draft: assumes moon and devenv.
- worktrunk's `pre-start` hook, run by crew: the kit's own words, but each host approves each kit's hooks, and `--yes` is what crew's rules keep from agents.

For crew's Python:
- devenv's Python pinned to 3.13, the first draft: the user ruled for proto.
- proto's Python with pytest installed into it by pip: a shared interpreter changed outside any lock.

For the bolt's checkout:
- Detached at the bolt's head, the first draft: kit tooling that names a worktree by its branch reads a detached HEAD, and the landing still needs a branch.
- Keep `bolt/<bolt>` checked out and bring it level after each move: crew stays inside sluice's control, and the landing's rebase is refused by sluice's protection.
- sluice lands the bolt onto main as a merge commit, conflicts resolved by merging main into the bolt: no rebase and no carry, a departure from `plan.8` and record 0015 for when main itself goes through sluice.
