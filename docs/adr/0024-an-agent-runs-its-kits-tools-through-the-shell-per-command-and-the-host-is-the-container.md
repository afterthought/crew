---
number: 24
title: An agent runs its kit's tools through the kit's shell per command, and the host is the container
status: proposed
date: 2026-10-12
decision-makers:
- Chuck Swanberg
---

# An agent runs its kit's tools through the kit's shell per command, and the host is the container

Status: proposed to the user on 2026-10-12, in the elaboration session; accepted only on their yes.

Deciders: the user, in the elaboration session of 2026-10-12, whose words below are the decision; written by the elaboration session. It closes the first point record 0023 held for an elaboration.
Amends: record 0023, its first held point; `tests.7` and `tests.1`; the ask of signal `2026-10-08-swancloud-planner-0ca5793d/01`, withdrawn by the user below; the `dev-shell` spec, through the unit that builds this (`docs.4`).
Sources: `openspec/explorations/agents-in-the-toolchain/reading.md` (the cases), `invariants.md` (what the user asked a solver to hold) and `proposal.md` (the solver's design for launching inside the toolchain, which the user read before deciding); Claude Code's hooks and tools references as read on 2026-10-12; herdr's `add-herdr-support`, `socket-api` and `session-state` pages at v0.9.3; sluice's `phase-1-integrations.md`, sections 3 and 4; swancloud's `modules/home-shell.nix` and `lib/claude-account-tools.nix`; crew's `.claude/hooks/devenv-shell`, `tests/run`, `tests/suite`, `.config/wt.toml`.

## Context and problem statement

On 2026-10-08 the user asked that a crew agent be "launched inside the shell" rather than wrap each command in `devenv shell --`. The unit `agents-work-inside-crews-devenv-shell` built it for crew and swancloud as a SessionStart hook committed in each repository, which enters the checkout's devenv shell once at a session's start and writes the shell's variables to the file Claude Code sources before each Bash command; `tests.7` ruled out the shell entered by `crew-role` or by crew's plugin. Every other kit has no hook: an agent there wraps a command or runs the host's tools. Record 0023 then had each kit declare its toolchain once and crew run it when it makes a worktree ready, and held how an agent comes to work inside that toolchain for this elaboration, on the user's doubt: "i'm not sure about this. seems like it's wrong. but i am probably missing something."

The elaboration read the cases (the reading), wrote the invariants a solution would have to hold, and had a fresh solver propose one: crew's launcher entering the declared toolchain and starting Claude inside it, Claude Code's FileChanged hooks keeping a session's commands on the worktree's files as they change, a keyed cache per worktree, and herdr's self-reported resume command once herdr can take it without the pane's lifecycle authority. It holds the invariants, and it costs: a launcher, two plugin hooks, a cache crew and sluice must agree on, a herdr feature, a devenv feature, and an agent's long-lived session that goes stale when the shell's files change under it unless the hooks refresh it.

## Decision drivers

- An agent's own edit to the shell's files, or a rebase that changes them, should reach its next command with nothing to rebuild.
- The gate and sluice already run every check in a toolchain printed fresh for the run, outside any session; an agent's loop can be looser than the gate.
- The failure that matters is silent: a host tool shadowing the pinned one when a wrap is forgotten (mac-studio's moon 1.41.7 in `~/.bun/bin`; a bun 1.3.13 where 1.2.23 was pinned; the Macs' older secretspec).
- Fewer moving parts in crew; nothing that depends on the fleet's `claude` shim or on a herdr or Claude Code feature that does not exist.

## Decision outcome

The user, on reading the solver's proposal: "I'm now having second thoughts about the original intent of trying to have Claude Code run inside the shell because that's not the way it runs now. The agents do a good job of using devenv, Moon, and everything like that. Maybe the idea is that agents use those tools directly so they can make changes and those changes get picked up automatically. … There is a chicken-and-egg problem: where do devenv and [nix] come from? Clearly I'm on my machine and I've got that as a prerequisite. I can ensure that any machine running my Claude in my project has devenv so it becomes a host-level requirement. You could think of the host as a container. I think I kind of like the idea of backing off this intent. … I think for [sluice] I would keep the intent, though. I would want [sluice] to be running in a predictable environment and toolchain." Asked to back off with the host as the container, and to remove crew's and swancloud's startup scripts: yes to both.

1. **No session is entered into a kit's shell at its start.** Not by crew's launcher, not by crew's plugin, not by a hook the kit commits. crew's `.claude/hooks/devenv-shell` and its entry in `.claude/settings.json` go, with `tests/t-dev-shell.sh` and the `dev-shell` spec; swancloud's generated hook goes by swancloud's own unit.
2. **An agent runs a kit's application tools through the kit's shell, per command,** in the form the kit's CLAUDE.md names: `devenv shell -- <command>` for a devenv kit. Each run evaluates the shell as the worktree's files stand, so an agent's edit to `devenv.nix` or `.prototools`, or a rebase that changes them, reaches its next command. The kit's own entry points enter the shell themselves when started outside it: crew's `tests/suite` and `tests/run` run themselves under `devenv shell --` rather than refusing (`tests.1`), as worktrunk's merge hooks already do (`.config/wt.toml`). A hook, an MCP server or a language server a kit configures carries its wrap in its own configuration, once; no agent remembers it for them.
3. **The host is the container.** A host carries the system tools every kit needs to be entered and crew needs to run: nix, devenv, git, herdr, wt, openspec, claude and crew's own `python3`. It carries no application tool on an agent session's path: no moon, bun, node, cargo or proto of the user's own. A command run outside the shell then fails for want of the tool rather than running the host's copy; the gate stays the backstop. The fleet owns the path (swancloud's `modules/home-shell.nix` puts `~/.bun/bin` on it today), so the rule is the fleet's to keep, by its own unit and, if its design agent chooses, a doctor row.
4. **The cold evaluation stays where record 0023 put it.** Readying a worktree runs the kit's declared toolchain command before any agent starts, so the evaluation cache under the worktree is warm and the agent's first wrapped command costs what a warm entry costs, about half a second in crew; a changed shell file pays one evaluation at the next command.
5. **sluice and the gate are unchanged.** sluice prints a kit's toolchain and sources it for every command of a run, outside any session, and crew's adapters do the same at readying and for the test runner's setup (record 0023, point 3). The user keeps that intent: the checks run in a predictable environment, whatever the agent's session has.

Not decided here: a kit-neutral per-command runner in crew, which this deliberately does not add, since each kit's shell has its own and the kit's CLAUDE.md names it; whether a devenv kit's `enterShell` should keep running `proto install` on every entry, which the unit measures and sets by the number.

### Consequences

- `tests.7` says the above; `tests.1` has `tests/run` enter the shell itself. Both are amended in this commit, marked proposed until the user's yes.
- One unit in crew: the hook, its settings entry, its test and its spec go; `tests/suite` and `tests/run` enter the shell themselves; CLAUDE.md's Tests section says how an agent runs crew's tools, and the briefs say nothing of it. The affected end-to-end tests and `tests/t-merge-gate.sh` follow.
- One unit in swancloud, for its design agent to queue: its generated SessionStart hook goes; `~/.bun/bin` and any other application tool leave an agent session's path; `testing.4` ("entering a worktree enters it") is read against this record.
- A kit's CLAUDE.md names its per-command form; switchboard's and breadboard's already do.
- Record 0023's first held point is closed by this record; its second, a bolt's branch under sluice, stays held.
- `openspec/explorations/agents-in-the-toolchain/` stays as the record of what was weighed: the cases, the invariants, and the solver's design for launching inside, which is the design to return to if an agent's session ever has to carry the toolchain itself.

## Considered options

- **Launch inside the declared toolchain and follow the files** (the solver's proposal): holds every invariant; the launcher, two plugin hooks, a per-worktree cache, a herdr feature request and a devenv feature request; a long-lived session is refreshed by hooks rather than by the next command. The user: not how the agents run now, and more than the problem needs.
- **crew's plugin enters every session's devenv shell** (record 0023's first draft): assumes devenv in crew; changes the user's own sessions in every kit; the user's original doubt.
- **A hook committed in each kit** (what crew and swancloud have today): a copy per kit; a session stale until restart when the shell's files change; a kit without one leaves its agents on the host's tools.
- **The fleet's `claude` shim enters the shell before starting Claude:** covers every start including herdr's bare resume, but makes crew's correctness rest on the fleet's wrapper, where crew and flywheel are meant to launch Claude themselves.
- **Per command, with the host as the container** (chosen): the agent's loop matches the gate's shape; a changed shell file reaches the next command; a forgotten wrap fails loudly; nothing new in crew but the removal.
