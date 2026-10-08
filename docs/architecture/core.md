# Core rules

The rules every change to crew holds to, wherever it is made. A rule that binds one area is on that area's page in this directory, which loads when a file under its paths is read. The reasoning behind a rule that came from a decision is in the record its details name, under `docs/adr/`. What is accepted but not yet built, and the code that stands against a rule today, is in `_open.md`.

| Page | Loads for |
|---|---|
| `plan.md` | `plugin/lib/plan.py`, `plugin/lib/gather.py`: the plan, proposals, stages and every write to a flywheel's branch |
| `teams.md` | `plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/crew.py`: teams, slots, stages, panes, tells |
| `record.md` | `plugin/lib/record.py`: the run record |
| `signals.md` | `plugin/lib/transcript.py` and the signal commands in `plan.py` |
| `briefs.md` | `plugin/roles/`, `plugin/skills/`: what each role may and may not do |
| `tests.md` | `tests/`, `devenv.nix`, `.config/` |
| `docs.md` | `README.md`, `openspec/`, `docs/`, `CLAUDE.md` |

## Rules

State

- **[state.1]** Every write to a flywheel's branch is one commit made by a crew command that fetches the tip into crew's bare cache, applies its change there, checks the result with `recfix --check` and crew's own rules, commits only its own paths through a temporary index, and pushes without force; a refused push is applied again to the new tip, and nothing is ever merged.
- **[state.2]** The plan holds only intent and the marks on it; every stage is read from the kits, and nothing records by hand how far work has got.
- **[state.3]** A kit's main changes only when the partition's main-level ops lands a proven bolt on the user's word through the kit's merge hooks, or fixes a landing that broke main, on the user's word, through the same hooks; nothing else is committed to a main.
- **[state.4]** crew runs no service: state is recutils files any clone reads with `recsel`, and every view is computed from those files and the run record with nothing running and nothing written.
- **[state.5]** Nothing crew runs, and nothing a brief tells an agent to run, pushes with force; crew's only pushes go to `<label>/main` of a state repository.

Roles

- **[roles.1]** The planner changes the plan only by a proposal the user approves, and crew itself refuses any direct plan write by an agent outside the role table: a conductor splits, orders and sets `After` within its own bolt and agrees to proposals, the design agent queues, a dispatcher gives bolts, main-level ops lands them, the user writes anything.
- **[roles.2]** An approval, a deploy, a landing, a push to a main or a change to the teams is run only on the user's word, never on an agent's own judgment; crew records who ran it and in which session, and does not refuse it by caller.
- **[roles.3]** When an agent breaks a rule its brief already states, the fix adds a check in crew that refuses the act, not only firmer wording in the brief.
- **[roles.4]** Every message crew or an agent sends another agent goes through `crew tell`, and everything crew types into a pane is marked, `[crew tell from <sender>]` or `[crew]`; a stage's own prompt is the one unmarked text, recognised by its form.

Reading

- **[read.1]** When crew cannot read something a decision depends on, it refuses, or removes nothing, and names what it could not read; it never falls back to a default or a guess, and a stage it cannot tell is `unknown`, never another stage.
- **[read.2]** crew reads another tool's output only by facts checked against the tool as it is now, and guards an absent field so a missing value never becomes text.
- **[read.3]** A command that reads several hosts names each host that does not answer and still shows everything else.
- **[read.4]** crew never takes over something it did not make for the work in hand: an existing place or branch, a pane whose agent still runs, or a worktree outside its own layout is refused or left alone.

Code

- **[code.1]** crew's Python imports nothing outside the standard library and its own modules; `gather.py` imports only the standard library, since it is piped to hosts whose crew may be older; devenv declares only jq, python3 and recutils.
- **[code.2]** A refusal is a `Refusal` raised through `fail()`, turned into `sys.exit(<message>)` at each entry point, never a traceback.
- **[code.3]** Every bash command about a team, main level or slot forwards to the host the teams file names before touching any state, carrying the asker's `CREW_AGENT`, `CREW_LABEL` and `CREW_SESSION`; every ssh crew runs passes `-o BatchMode=yes`.
- **[code.4]** Every name crew mints or accepts matches `^[a-z0-9][a-z0-9-]*$`.
- **[code.5]** crew reads `teams.json` (version 2) and `herdr-hosts.json`, checks every entry before any is used, and never writes either; no field has a default.
- **[code.6]** Every commit is a Conventional Commit, staged by path; `git add -A`, `git stash` and `git reset` are never used.

## Details

**[state.1]** Rules out: a checkout of the state branch; a merge of two appended records; `merge=union`; a push with `+`. Source: `bolt-plan` spec "Writes go through crew and are never merged"; `flywheel-state` spec; `plan.py` `land`, 318–389; ADR 0003 for what "held" means.

**[state.2]** Rules out: a `Stage` or `Date` field in `plan.rec`; a status file beside the plan. Not ruled out: the marks `Amended` and, once built, `Hold`. Source: `bolt-plan` spec "A unit's stage is read from the kits"; `plan.py` 71–94.

**[state.3]** Rules out: a unit, chore or archive committed straight to main; a landing with `--no-hooks`. Not ruled out: main-level ops's fix on main after a landing broke it, on the user's word (the `main-level` spec). Source: `bolt-teams` spec "A bolt lands on main on the user's word"; `main-level` spec; ADR 0006 drivers; `main-ops.md`.

**[state.4]** Rules out: a daemon; a view that commits or appends on refresh. Source: `openspec/config.yaml`; `flywheel-state` spec "plain files"; ADR 0002; `tests/t-rail.sh`.

**[state.5]** Rules out: `git push --force` anywhere in `plugin/` or a brief; a push to a blueprints repo or a kit's remote. Source: fix 04daa5d; `plan.py` 383, 569.

**[roles.1]** Rules out: `crew unit add --bolt` from the design agent; `unit move` from a conductor; `bolt give` or `bolt land` inside a proposal. Source: `plan-proposals` spec; `plan.py` `may_write` 1068–1117, `OPS` 1122–1165; `tests/t-plan-roles.sh`.

**[roles.2]** Rules out: a conductor approving a proposal on its own reading; an operator deploying unasked. Not ruled out: `crew plan approve` and `crew unit approve` open to any caller, by design. Source: plan-proposals design "Who may write what directly"; fixes a2ea85e, 63bab58, 04daa5d.

**[roles.3]** Rules out: a second brief-only fix for the same broken rule. Source: plan-proposals design; fix-place-names-its-bolt proposal; fix 902336e.

**[roles.4]** Rules out: `herdr agent prompt` from one agent to another; an unmarked notice. Not ruled out: `run_stage`'s `/opsx:…`, `Fix: …` and merge prompts, which a slash command cannot prefix; a quote of one is asserted by the conductor that ran the stage. Source: checked-capture design "Marking what crew sends"; `crew.py` 217–224; `transcript.py` `asserter`.

**[read.1]** Rules out: a default partition; a stage guessed from a missing host; a tidy that removes when a plan can't be read. Source: fixes f734f28, d9c8a11, e413c48; bolt-teams design; `plan.py` 686–690.

**[read.2]** Rules out: a field read from a transcript without a probe; a "null" path printed from a missing value. Source: fixes 0aa835d, e1ed1df, 5a481ae; checked-capture design.

**[read.3]** Rules out: a listing that stops at the first dead host. Source: `bolt-plan` spec "What is in flight can be read from anywhere"; `crew-sites` spec; `run-record` spec.

**[read.4]** Rules out: starting a role over a running agent; a fix adopting an existing place; tidying a hand-made worktree. Source: fixes 499cd3b, 5e11de2, f6d7b11; worktrees-go-with-their-work.

**[code.1]** Rules out: `import yaml`; `gather.py` importing `crew`. Source: `plan.py` 57–65; `gather.py` 13–15; `devenv.nix`.

**[code.2]** Rules out: a bare `raise` reaching the user; `sys.exit(1)` with no message. Source: `crew.py` 38–43, 662–666; `plan.py` 3072–3076.

**[code.3]** Rules out: a team command acting on local slot files for a remote team; an ssh that can prompt. Source: `plugin/bin/crew` 76–135; `crew.py` 178–184, 287–292.

**[code.4]** Rules out: a unit named with a slash or a capital. Source: `crew.py` 31, 114, 138; `plan.py` 81, 89.

**[code.5]** Rules out: crew editing the teams file; a version-1 file accepted. Source: `bolt-teams` spec "Teams are fixed in the teams file"; `crew.py` 100–161.

**[code.6]** Rules out: `git add -A` in a brief or a script. Source: `openspec/config.yaml`; every brief's committing section.
