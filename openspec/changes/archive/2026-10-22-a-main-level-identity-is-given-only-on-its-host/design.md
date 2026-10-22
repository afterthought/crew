# Design

## Context

See proposal.md for why. Today nothing ties a main-level agent's identity to a host:

- `crew-role <label> <role>` runs `crew.py launch`, whose `launch_shell` builds the start from the teams file wherever it runs. For a partition's standing roles and the reviewer, `launch` reads the main level's folders off `p["machine"]` but never compares that with `this_host()`; only the dispatcher's start reads the host, through `dispatch_place`.
- `plugin/hooks/session-start`, for a session that starts without `CREW_AGENT` but has a record in `~/.local/state/crew/sessions/<id>`, rewrites the record's load lines, writes `CREW_AGENT`, `CREW_LABEL` and `SLUICE_AGENT` to `CLAUDE_ENV_FILE`, renames the herdr pane after the agent and, at a compaction, gives the brief back (`crew.brief_due`, `crew.brief_role`). It reads no teams file for any of this but the brief.

So a pane herdr's session restore replays on a host that once ran a main level, as deneb's swancloud-1 did on 2026-10-16 (swancloud `herdr.10`, as read on 2026-10-20), comes back as that main level's agent wherever the main level runs now. The teams file is what names the main level's host (`main-level` spec "Partitions are declared in the teams file"), and every command about a main level goes to that host before touching state (`code.3`). Today the main level of swancloud and madswan is on deneb, so mac-studio is where the stale records and saved panes are.

Rules this design rests on: `code.3` (a main level's host is the teams file's), `read.1` (what crew can't read gives nothing), `code.7` (the decisions are functions of facts), `code.2` (a refusal through `fail`), `read.4` (crew takes over nothing it did not make for the work in hand), `roles.2` (crew records who ran what: a session with no identity runs crew as the user, see Risks), `code.8` (nothing the views draw moves). It departs from `teams.6`'s words "a session herdr resumes without that environment gets its name and identity back at its start": a main level's agent now gets them back only on its main level's host. That is the decision swancloud's `herdr.10` records ("crew refuses it an identity off the teams file's host"); `teams.6` itself is the design agent's to amend (`docs.7`). Pages whose area the change touches: `teams.md` (`plugin/bin/crew-role`, `plugin/lib/crew.py`), `docs.md` (README), `tests.md` (`tests/`).

## Goals / Non-Goals

**Goals:**
- A main level's design agent, planner, ops, operator or reviewer is started by `crew-role` only on its main level's host.
- A session herdr resumes elsewhere under one of those names gets no identity, no pane name and no brief, its record left alone, and is told why and where the main level is.

**Non-Goals:**
- A team's agents and the dispatchers. A dispatcher's name carries its host, and a team's place is its own `machine`; the same hazard may hold for them, but it is not this unit's intent.
- Making crew refuse the commands of a session that has no identity. With no `CREW_AGENT`, crew takes the caller for the user at that host (`record.who`); this unit tells the session to run nothing of crew's and does not change who crew takes a caller for.
- Stopping herdr from replaying the pane, which is swancloud's (`herdr.10`).
- A session started by hand with `CREW_AGENT` already set: crew-role is the one way crew starts an agent with it.

## Decisions

### 1. Which agents: read from the record alone

A recorded session is a main level's agent when its record's `CREW_AGENT` is `<CREW_LABEL>-<role>` for `role` one of `design`, `planner`, `ops`, `operator`, `reviewer` (`MAIN_STANDING` and the reviewer). This needs no teams file, so every other session, a team's agent, a dispatcher, a record whose label is empty, is handled as today without reading the fleet, and `tests/t-session-hook.sh`, which runs with no teams file, is unchanged. A dispatcher, `<label>-dispatch-<host>`, does not match.

`main_named(name, label)` (the coder may name it) returns the role or None, and starts no process (`code.7`).

### 2. Where: the teams file, against this host

For such a session the hook loads the fleet and reads the partition's `machine`, then compares it with `crew.this_host()`. The same host gives the identity back exactly as today. Another host, or a teams file crew can't read (a `Refusal` from `load` or `partition_of`), gives none (`read.1`).

`identity_withheld(name, label, here, main, unread=None)` returns None when `main == here` and nothing was unread, else the words the session is told. Its words, the crew-role refusal's sentence in them:

- elsewhere: `[crew] This session was <name>, and crew gives it no identity here: <label>'s main level runs on <main>, not <here>, and crew starts <name> only there. In this session you are no agent of crew's: run no crew command, which crew would record as the user's, write nothing to the plan, a kit, a card or another agent, and wait for the user.`
- unread: `[crew] This session was <name>, and crew gives it no identity here: it can't tell where <label>'s main level runs, <the refusal's words>.` followed by the same second sentence.

`main_elsewhere_said(name, label, main, here)` gives the shared sentence, `<label>'s main level runs on <main>, not <here>, and crew starts <name> only there`, which crew-role's refusal is.

### 3. The hook's off-host path

In `session-start`, after the session is found to have a record naming an agent and before anything is written: when `main_named` matches, read where its main level runs and decide (Decision 2). When the decision withholds:

- write nothing to the record, the env file or the pane, and give no brief;
- print the words as the hook's `additionalContext` for `SessionStart`, at every source (`startup`, `resume`, `compact`, `clear`), since a compaction or a clear drops what it was told before;
- return.

The question mark's removal at the top of `main()` stays for every session. The path where `CREW_AGENT` is in the hook's environment, a start crew-role made, is unchanged. The hook still never fails a start: an exception anywhere is said on stderr, as now, and since it comes before the identity is written, a session whose host crew couldn't read gets none.

### 4. crew-role's start

`launch_shell`, `crew-role`'s path into crew.py, refuses before it reads the last conversation when the scope is a partition, the role is a standing one or the reviewer, and the partition's `machine` is not `this_host()`: `fail(main_elsewhere_said(...))` (`code.2`). `crew-role` already exits 2 on the refusal with its words on stderr, so the pane says where the main level runs and no Claude starts. The check is not in `launch` itself, which `launch_now` reads to tell whether an update makes an agent due, and that must answer wherever it is asked.

`Agents.start` reaches the same refusal only if a main level's start ran off its host, which forwarding prevents (`code.3`).

### 5. The documents

README's resume paragraph: crew's SessionStart hook gives a resumed agent its name and identity back, a main level's only on the host the teams file names for it, where any other host tells the session it is no agent of crew's there and which host is. `crew-role`'s usage comment says a main level's role starts only on its main level's host. `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage name no `crew-role` behaviour this changes (`docs.2`). Nothing under `docs/architecture/` or `docs/adr/` (`docs.7`).

### 6. The agents' views

Nothing the board or the bands draw changes (`code.8`'s "not ruled out").

## Risks / Trade-offs

- [The session still runs crew as the user] → a session told it is no agent of crew's could still run `crew`, which records it as the user at that host (`record.who`) and lets it do what the user may (`roles.1`, `roles.2`). This unit withholds the identity and tells the session not to; a check that refuses such a session's commands is a decision for the design agent (Non-Goals).
- [A main level moves back to a host with stale records] → the records are left untouched, so `crew resume` there picks the newest as before; the move is the user's and `crew main up` restarts the roles through crew.
- [Each host reads its own teams file] → a host whose teams file is behind the fleet's configuration decides by it, as every crew command there does (`code.5`).

## After deploy

A landing of crew is live on every host once main is pulled there; the logic and end-to-end tiers prove the behaviour on stub hosts. One step reads the real hosts' files, which no test can hold:

- **mac-studio, the team's ops, once the landing reaches mac-studio's checkout:** pick a session record under `~/.local/state/crew/sessions/` there whose `CREW_AGENT` is a swancloud main-level agent, and pipe `{"session_id":"<its id>","source":"clear"}` to `plugin/hooks/session-start` with `CLAUDE_ENV_FILE` set to an empty scratch file and `HERDR_ENV` unset: the scratch file stays empty, the record is unchanged, and the printed context names deneb. Then `crew-role swancloud planner` on mac-studio, in a scratch shell, refuses naming deneb.

## Task notes

**1.1** In `crew.py` beside `brief_due`: `main_named(name, label)`, `main_elsewhere_said(name, label, main, here)` and `identity_withheld(name, label, here, main, unread=None)` as Decisions 1 and 2. Cases in `tests/py/test_teams.py`, a class beside `TestBriefBack`: each of `wldn-design`, `wldn-planner`, `wldn-ops`, `wldn-operator`, `wldn-reviewer` under label `wldn` is named; `swb-1-conductor`, `wldn-dispatch-chuck-herdr-alpha`, `madswan-planner` under `wldn`, and any name under an empty label are not; the same host withholds nothing; another host's words name the agent, both hosts and "no agent of crew's"; unread words carry the refusal's text.

**1.2** In `launch_shell`, before `resolve`, the refusal of Decision 4. Cases in `tests/t-roles.sh`: `expect_fail "wldn's main level runs on chuck-herdr-alpha, not mac-studio"` for `as mac-studio crew-role wldn planner` and for `wldn design resume`, with the stub claude's log empty after them; the existing starts on chuck-herdr-alpha and `madswan` on mac-studio still pass.

**1.3** In `session-start`, the path of Decision 3. Cases in `tests/t-roles.sh` (it has the world's teams file and hosts; `t-session-hook.sh` has none): start `wldn planner` on chuck-herdr-alpha, copy its session record into mac-studio's home, and run the hook as mac-studio without crew's environment, with `CLAUDE_ENV_FILE`, `HERDR_ENV=1` and a stub pane: for `resume`, the env file empty, the pane's name unchanged, the record byte for byte as copied, and the context naming chuck-herdr-alpha; for `compact`, no brief and the same words. With mac-studio's teams file moved aside, `resume` gives no identity and words saying crew can't tell where wldn's main level runs. Run as chuck-herdr-alpha, the same record's `compact` still gives the brief back (the existing case). `t-roles.sh`'s opening comment says what it now proves; its `# Reads:` already has `plugin/hooks/`.

**2.1** README's resume paragraph and `crew-role`'s usage comment as Decision 5, proved by `tests/suite docs`.
