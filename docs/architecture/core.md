# Core rules

The rules every change to crew holds to, wherever it is made. A rule that binds one area is on that area's page in this directory, which loads when a file under its paths is read. The reasoning behind a rule that came from a decision is in the record its details name, under `docs/adr/`. What is accepted but not yet built, and the code that stands against a rule today, is in `_open.md`.

| Page | Loads for |
|---|---|
| `plan.md` | `plugin/lib/plan.py`, `plugin/lib/gather.py`: the plan, proposals, stages and every write to a flywheel's branch |
| `teams.md` | `plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/crew.py`: teams, slots, stages, panes, tells |
| `record.md` | `plugin/lib/record.py`: the run record |
| `signals.md` | `plugin/lib/transcript.py` and the signal commands in `plan.py` |
| `briefs.md` | `plugin/roles/`, `plugin/skills/`: what each role may and may not do |
| `tests.md` | `tests/`, `devenv.nix`, `.config/`, `.claude/`, `.envrc` |
| `docs.md` | `README.md`, `openspec/`, `docs/`, `CLAUDE.md` |

## Rules

State

- **[state.1]** Every write to a flywheel's branch is one commit made by a crew command that fetches the tip into crew's bare cache, applies its change there, checks the result with `recfix --check` and crew's own rules, commits only its own paths through a temporary index, and pushes without force; a refused push is applied again to the new tip, and nothing is ever merged.
- **[state.2]** The plan holds only intent and the marks on it; every stage is read from the kits, and nothing records by hand how far work has got.
- **[state.3]** A kit's main changes only when the partition's main-level ops lands a proven bolt on the user's word through the kit's merge hooks, or fixes a landing that broke main, on the user's word, through the same hooks; nothing else of a kit's code or specs is committed to a main, but the user's own commits and the design agent's records under `docs/`, which its brief has it commit there.
- **[state.4]** crew runs no service: state is recutils files any clone reads with `recsel`, and every view is computed from those files and the run record with nothing running and nothing written.
- **[state.5]** Nothing crew runs, and nothing a brief tells an agent to run, pushes with force; crew's only pushes go to `<label>/main` of a state repository.

Roles

- **[roles.1]** The planner changes the plan only by a proposal the user approves, and crew itself refuses any direct plan write by an agent outside the role table: a conductor splits, orders and sets `After` within its own bolt and agrees to proposals, the design agent queues, a dispatcher gives bolts, main-level ops lands them, the user writes anything.
- **[roles.2]** An approval, a landing, a push to a main or a change to the teams is run only on the user's word, never on an agent's own judgment; a deploy runs on the environment's policy, `auto` given once by the user or `manual` given per deploy through the rail's card, never by an agent; crew records who ran or approved it and in which session, and does not refuse it by caller.
- **[roles.3]** When an agent breaks a rule its brief already states, the fix adds a check in crew that refuses the act, not only firmer wording in the brief.
- **[roles.4]** Every message crew or an agent sends another agent goes through `crew tell`, and everything crew types into a pane is marked, `[crew tell from <sender>]` or `[crew]`; a stage's own prompt is the one unmarked text, recognised by its form.

Reading

- **[read.1]** When crew cannot read something a decision depends on, it refuses, or removes nothing, and names what it could not read; it never falls back to a default or a guess, and a stage it cannot tell is `unknown`, never another stage.
- **[read.2]** crew reads another tool's output only by facts checked against the tool as it is now, and guards an absent field so a missing value never becomes text.
- **[read.3]** A command that reads several hosts names each host that does not answer and still shows everything else.
- **[read.4]** crew never takes over something it did not make for the work in hand: an existing place or branch, a pane whose agent still runs, or a worktree outside its own layout is refused or left alone.
- **[read.5]** The run record is read from the flywheel's branch alone: every entry reaches the branch as it is written, as its own commit from the host that wrote it, and no decision reads a host over ssh for the record; a host is read over ssh only for the stages of its own kits' worktrees, and a host that does not answer hides only the work on it, never another host's landing nor the partition's batch clock. (Proposed 2026-10-11, put to the user on a card as `briefs.15` has it; accepted only on their yes.)

Code

- **[code.1]** crew's Python imports nothing outside the standard library and its own modules; `gather.py` imports only the standard library, since it is piped to hosts whose crew may be older; devenv declares only jq, moon, python3 and recutils, and pytest for the tests.
- **[code.2]** A refusal is a `Refusal` raised through `fail()`, turned into `sys.exit(<message>)` at each entry point, never a traceback.
- **[code.3]** Every bash command about a team, main level or slot forwards to the host the teams file names before touching any state, carrying the asker's `CREW_AGENT`, `CREW_LABEL` and `CREW_SESSION`; every ssh crew runs passes `-o BatchMode=yes`.
- **[code.4]** Every name crew mints or accepts matches `^[a-z0-9][a-z0-9-]*$`.
- **[code.5]** crew reads `teams.json` (version 2) and `herdr-hosts.json`, checks every entry before any is used, and never writes either; no field has a default.
- **[code.6]** Every commit is a Conventional Commit, staged by path; `git add -A`, `git stash` and `git reset` are never used.
- **[code.7]** A decision of crew's is a function of plain facts that starts no process and calls no tool; the reads that feed it and the acts that follow it stay thin around it, and a decision in `plugin/bin/crew`'s bash moves to Python when its test is converted.
- **[code.8]** A change to what crew models, its bolts, units, stages, proposals, explorations and elaborations, cards and rail rows, updates in the same change, each with its cases, the agents' views of it, `board.agent_views`, and the mod that draws them above each agent's prompt, `plugin/hooks/status.js`.

## Details

**[state.1]** Rules out: a checkout of the state branch; a merge of two appended records; `merge=union`; a push with `+`. Source: `bolt-plan` spec "Writes go through crew and are never merged"; `flywheel-state` spec; `plan.py` `land`, 318–389; ADR 0003 for what "held" means.

**[state.2]** Rules out: a `Stage` or `Date` field in `plan.rec`; a status file beside the plan. Not ruled out: the marks `Amended` and, once built, `Hold`. Source: `bolt-plan` spec "A unit's stage is read from the kits"; `plan.py` 71–94.

**[state.3]** Rules out: a unit, chore or archive committed straight to main by an agent; a landing with `--no-hooks`. Not ruled out: a fix on main after a landing broke it, which main-level ops lands on the user's word through the hooks and never writes: the planner proposes it as a bolt of its own, first among the planned, for the team the user and the planner choose (the `main-level` spec; `main-ops.md`, "never edit the code yourself"; swancloud-ops, 2026-10-11, on the landing-card check); the user's own commits, among them the archive sweep of 2026-10-10 (crew a3caf5b to 94e31e3, swancloud 4fee795 to 54f849f, run on the user's word, nothing pushed), which `roles.1` already allows; the design agent's records, as its brief says. Source: `bolt-teams` spec "A bolt lands on main on the user's word"; `main-level` spec; ADR 0006 drivers; `main-ops.md`.

**[state.4]** Rules out: a daemon; a view that commits or appends on refresh. Source: `openspec/config.yaml`; `flywheel-state` spec "plain files"; ADR 0002; `tests/py/test_rail.py`, `tests/py/test_board.py`, `tests/t-journey-review.sh`, `tests/t-journey-board.sh`.

**[state.5]** Rules out: `git push --force` anywhere in `plugin/` or a brief; a push to a blueprints repo or a kit's remote. Source: fix 04daa5d; `plan.py` 383, 569.

**[roles.1]** Rules out: `crew unit add --bolt` from the design agent; `unit move` from a conductor; `bolt give` or `bolt land` inside a proposal. Source: `plan-proposals` spec; `plan.py` `may_write` 1068–1117, `OPS` 1122–1165; `tests/py/test_plan_roles.py`.

**[roles.2]** Rules out: a conductor approving a proposal on its own reading; an operator or main-ops deploying unasked; a `manual` environment moved by a timer. Not ruled out: `crew plan approve` open to any caller, by design; a batch's feedback, which is the user's word on a card and approves nothing (ADR 0014); a kit's deployer moving an `auto` environment. Source: plan-proposals design "Who may write what directly"; fixes a2ea85e, 63bab58, 04daa5d; ADR 0012 as amended 2026-10-08.

**[roles.3]** Rules out: a second brief-only fix for the same broken rule. Source: plan-proposals design; fix-place-names-its-bolt proposal; fix 902336e.

**[roles.4]** Rules out: `herdr agent prompt` from one agent to another; an unmarked notice. Not ruled out: `run_stage`'s `/opsx:…`, `Fix: …` and merge prompts, which a slash command cannot prefix; a quote of one is asserted by the conductor that ran the stage. Source: checked-capture design "Marking what crew sends"; `crew.py` 217–224; `transcript.py` `asserter`.

**[read.1]** Rules out: a default partition; a stage guessed from a missing host; a tidy that removes when a plan can't be read; a stage start crew could not read taken as never started (`run_stage`, 2026-10-11, crw-1's construct that went to work while crew recorded it refused: `teams.15` details). Source: fixes f734f28, d9c8a11, e413c48; bolt-teams design; `plan.py` 686–690.

**[read.2]** Rules out: a field read from a transcript without a probe; a "null" path printed from a missing value. Source: fixes 0aa835d, e1ed1df, 5a481ae; checked-capture design.

**[read.3]** Rules out: a listing that stops at the first dead host. Source: `bolt-plan` spec "What is in flight can be read from anywhere"; `crew-sites` spec; `run-record` spec; `tests/t-journey-board.sh`, where crew bolts, board, sites and page each name a host that does not answer.

**[read.4]** Rules out: starting a role over a running agent; a fix adopting an existing place; tidying a hand-made worktree. Source: fixes 499cd3b, 5e11de2, f6d7b11; worktrees-go-with-their-work.

**[read.5]** Rules out: a landing on mac-studio refused because macbook-pro, which runs no team, is off the tailnet (crw-3, 2026-10-11: crew main held units-build-at-once-and-are-reviewed-in-batches at 26e22a4 and `crew bolt land` refused to close it, "crew can't tell which changes have been in a batch: macbook-pro did not answer"; the user: "Hmm this seems like a design issue that we need to talk about. The laptop isn't going to be on most of the time", signal 2026-10-11-crw-3-conductor-883e3042/01); a run record gathered over ssh from the hosts because entries wait in a local file until that host's next write carries them (`plan.2`), which the user named as against the design (2026-10-11: "it seems intrusive to be reaching across the hosts over SSH when the design is that we should be looking in Git"); a decision that reads part of the record. Not ruled out: `read.3`'s listing of stages, which asks every host for its kits and names the silent ones. Source: `state.1`, `state.4`, `read.1`; `record.gather`, which reads the branch and then every host of the partition for its uncarried entries, so `batch_due` and the landing's guard refuse when any is silent: the fix is `the-run-record-reaches-the-branch-as-it-is-written`, queued once the rule is accepted: `_open.md`.

**[code.1]** Rules out: `import yaml`; `gather.py` importing `crew`. Source: `plan.py` 57–65; `gather.py` 13–15; `devenv.nix`; ADR 0008, for moon.

**[code.2]** Rules out: a bare `raise` reaching the user; `sys.exit(1)` with no message. Source: `crew.py` 38–43, 662–666; `plan.py` 3072–3076.

**[code.3]** Rules out: a team command acting on local slot files for a remote team; an ssh that can prompt. Source: `plugin/bin/crew` 76–135; `crew.py` 178–184, 287–292.

**[code.4]** Rules out: a unit named with a slash or a capital. Source: `crew.py` 31, 114, 138; `plan.py` 81, 89.

**[code.5]** Rules out: crew editing the teams file; a version-1 file accepted. Source: `bolt-teams` spec "Teams are fixed in the teams file"; `crew.py` 100–161.

**[code.6]** Rules out: `git add -A` in a brief or a script; an agent moving a bolt's branch by `git reset`. Not ruled out: crew moving a branch it made, `UNREBASE`'s undo of its own rebase and the bolt's move to a fix that carries it (ADR 0015), which move a branch and discard nothing. Source: `openspec/config.yaml`; every brief's committing section.

**[code.7]** Rules out: a `subprocess`, `kit_git`, `on_machine` or `crew.tell` call inside a decision; a decision only bash can make. Not ruled out: the reads and acts themselves, proved by the contract and end-to-end tiers. Source: ADR 0022; `tests.11`. Not built: decisions come out of `plan.py` and `plugin/bin/crew` as their tests convert: `_open.md`.

**[code.8]** Rules out: a new stage, object or field the board reads that the agents' bands leave out or draw wrong; a change to the views file's shape that `status.js` does not follow, which the logic tier fails (`tests/py/test_board.py`, the case pinning every key the mod reads). Not ruled out: a change that moves nothing the views draw. Source: the user, 2026-10-12: "We need to make sure we have some context in the right spot so that agents know that, as we make changes to crew (especially to any of the modeling parts, like elaborations), these mods need to be updated."; `openspec/explorations/agent-status-mods/reading.md`.
