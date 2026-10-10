# Design

## Context

A team's conductor is greeted today by `crew.py`'s `greet(fleet, team, first, wait)`: it waits for the conductor to settle (`idle` or `done`), waits up to five minutes more once if the conductor is `blocked` on a question in its pane, then sends `GREETING` through `tell` marked `[crew]` and records a `greet` entry on `agent/<team>-conductor` and `team/<team>`. `plugin/bin/crew` calls it as `greet_conductor` after `crew up`, `crew rebuild`, `crew restart` (unless `--no-greet`) and `revive` of a team's conductor; `crew bolt give` calls it from `plan.py` with "Your team now holds the bolt …" in front.

Nothing greets an agent started outside a team. `crew main up` starts the design agent, planner and ops with `start_standing` and then runs `crew _dispatch up` on each host the partition's teams run on (locally or over ssh), which starts that host's dispatcher the same way; `crew operator up` starts the operator agent and opens its `flow` and `rail` tabs; `revive` resumes each standing role of a team, main level, dispatcher or operator whose pane came back empty, and greets only a team's conductor. Each of these agents is started with `CREW_LABEL` set (`teams.6`), so `crew bolts`, `crew rail` and `crew plan proposed` read its own partition without `--label`.

The `main-level` spec and `teams.7` already say these agents are greeted; `_open.md` lists this unit as the code catching up. The spec's requirement was amended on main ahead of this build (commit 9f8c4b5), which `docs.4` rules out; this change's delta carries that requirement's text unchanged and adds the scenarios that pin "exactly once per start", so the archive leaves the spec as the design agent wrote it plus those scenarios.

Rules this design relies on: `teams.7` (one greeting per start, marked as crew's), `roles.4` (everything crew types into a pane is marked `[crew]`), `teams.11` (nothing is typed into a question: the greeting waits on a `blocked` agent as the conductor's does), `code.2` (refusals), `code.3` (the dispatcher's greeting runs on the dispatcher's own host, inside the forwarded `_dispatch up`), `state.4` (no greeting outlives the command that sends it: nothing keeps running to greet later), `docs.2` (README, the crew skill and the usage change together). Pages whose areas the change touches: `teams.md` (`plugin/bin/crew`, `plugin/lib/crew.py`), `docs.md` (README, `docs/`, `openspec/`), `tests.md` (`tests/`). The change departs from no rule.

## Goals / Non-Goals

**Goals:**

- Every agent `crew main up`, `crew _dispatch up`, `crew operator up` or `revive` starts outside a team is greeted once, with a greeting for its role.
- An agent that was already up is never greeted by a bring-up that did not start it.
- One agent waiting on a question delays no other agent's greeting.

**Non-Goals:**

- Greeting a team's ops or a unit's stage agent: the ops gets its work from the conductor, and a stage agent gets its prompt from `run_stage`.
- Changing the conductor's greeting or when it is sent.
- Changing any brief. The greetings name commands the briefs already teach; each brief already says what its role carries on with.
- Greeting an agent that `/clear` or a manual `claude` start brought up: crew greets what crew starts.

## Decisions

### 1. One greeting function for every standing agent, with a greeting per role

`greet` is split into a core that greets one agent by name, given the text, the `on` objects, the `why` and what to say when it is not up, and two callers: the conductor's (unchanged in behaviour: `greet(fleet, team, first, wait)`) and one for an agent outside a team, which reads the agent's partition and role from its name (`label_of_agent`, and the name's `-design`, `-planner`, `-ops`, `-dispatch-<host>` or `-operator-<host>` ending) and refuses a team's agent. The wait (settled; a `blocked` agent reported once and waited on up to five minutes; not up or never ready reported with the command that would greet it) is the conductor's, word for word in shape, so the rule is held once.

The greetings live beside `GREETING` in `crew.py`, one per role, filled with the label and, for a dispatcher, the host (Task notes 1.1). Each names the reads its role's brief already teaches and ends "then carry on with what is yours", with the one line of what that is.

*Alternatives considered.* One generic greeting ("read where the partition stands and carry on") for every role: shorter, but it leaves each agent to work out which reads mean "where the partition stands" for it, which is the guess the conductor's greeting was written to remove. A "When you start" section in each brief, with the greeting pointing at it: it puts the reads in the brief where the role's other rules are, but it changes five briefs and `tests/t-briefs.sh`'s pinned phrases for a line the conductor keeps in `crew.py`; holding the main level to the conductor's form is the simpler rule.

### 2. Greet what was started, after it was started, side by side

`crew main up` greets exactly the roles `start_standing` put in `started`, and `crew _dispatch up` its dispatcher only when it started it; `crew operator up` greets only when it started the agent, after its `flow` and `rail` tabs are open, so the greeting can point at the rail it reads. `revive` greets each standing role of a main level, dispatcher or operator it brought back, as it already does a team's conductor. A role already up is neither started nor greeted, which is what makes it once per start.

The greetings of agents started together are sent side by side, each as its own background process the command waits on before it returns, so one agent stopped on a question holds back nobody else's greeting and nothing outlives the command (`state.4`). The dispatcher on each host is greeted by that host's own `crew _dispatch up`, so `crew main up` greets a remote dispatcher without crew reaching across hosts for the wait (`code.3`). `crew main up` starts the dispatcher loop while its own three greetings are under way, and waits on them at the end.

*Alternative considered.* Greeting from `start()` itself: it would greet every start, including a team's ops and a slot's stage agent, which have their own first prompt, and `crew resume` and `crew restart` of a team's ops.

### 3. A greeting that fails does not fail the bring-up

As with the conductor, a greeting that can't be sent is said on standard error with the `crew tell` that would send it, and `crew main up`, `crew operator up` and `crew revive` still succeed: the agents are up, and the user can greet one by hand. A greeting sent is a `greet` entry in the run record of the agent's partition, on `agent/<name>`, with `why` `main(<label>): greet <name>` for the main level and the dispatchers (as their `main.up` entries are) and `operator(<label>): greet <name>` for the operator agent.

## Risks / Trade-offs

- [A main level whose agents all stop on a first run's consent question holds `crew main up` up to five minutes.] → They wait side by side, so it is five minutes, not fifteen, and the command says which agent waits on what as soon as it sees it.
- [A dispatcher host that does not answer over ssh gets no greeting.] → Unchanged from today: `crew main up` already cannot start a dispatcher there, and says so.
- [A greeting tells a revived agent to carry on with work it may already have been in the middle of.] → The greeting asks it to read where things stand first, which is what a resumed conversation needs anyway; a revived conductor is greeted the same way today.

## Proof in dev

After the bolt lands and every host has pulled, on swancloud:

1. The user runs `crew main down swancloud` and then `crew main up swancloud` on mac-studio. `swancloud-design`, `swancloud-planner`, `swancloud-ops` and `swancloud-dispatch-mac-studio` each show one `[crew]` greeting in their pane, answer with a few lines on where swancloud stands, and carry on without the user or the operator agent telling them to (the signal's own case).
2. Run `crew main up swancloud` again: no pane gets a second greeting, and `crew events --label swancloud` shows one `greet` entry per agent from the first bring-up only.
3. The user restarts swancloud's operator session (`crew operator up swancloud` from its supervisor): the operator agent is greeted once and answers from the rail.

## Task notes

### 1.1

In `crew.py`, split `greet` into a core `greet_agent(fleet, name, text, on, label, why, hint, wait=90)` holding today's wait loop (the `blocked` message, the five-minute extension, the not-up and not-ready messages, the `tell(..., record=False)`, the `greet` entry and "<name> greeted"), and keep `greet(fleet, team, first="", wait=90)` calling it with today's text, objects and messages, so `t-greet.sh` and `t-standing.sh` pass unchanged. Add `greet_standing(fleet, name, wait=90)` for an agent outside a team: partition from `label_of_agent`, role from the name's ending; a team's agent or an unknown name is a `Refusal` (`code.2`). Its not-up hint is `crew main up <label> starts and greets it`, or `crew operator up <label> …` for the operator agent. The greetings, `{label}` and `{host}` filled in:

- design: "Read where {label} stands with `crew bolts` and `crew rail`, and the signals waiting for curation, tell me in a few lines, then carry on with what is yours: curate the signals that have no move."
- planner: "Read where {label} stands with `crew bolts` and `crew plan proposed`, tell me in a few lines, then carry on with what is yours: plan what is queued and see each open proposal through."
- ops (main level): "Read where {label} stands with `crew bolts` and `crew rail`, tell me in a few lines, then carry on with what is yours: a bolt lands only on the user's word, so land nothing until it comes."
- dispatcher: "Read where {label} stands on {host} with `crew bolts` and `crew status` for each team here, tell me in a few lines, then carry on with what is yours: give each team here that holds no bolt its next one."
- operator: "Read where {label} stands with `crew rail` and `crew bolts`, and tell me in a few lines what is moving and what waits on me."

Add `greet-agent <name> [--wait <seconds>]` to `main()` beside `greet <team>`, and both to the module's usage (`_open.md` lists `greet` as missing from it).

### 1.2

In `plugin/bin/crew`, a `greet_started` helper that runs `py greet-agent "$(name_of "$r")"` for each role given, each in the background, and a `wait` for them, never failing the command (`|| true` per greeting). `main up`: after `start_standing` and its `record_agents`, start the greetings of `started` in the background, run the dispatcher loop, then wait. `_dispatch up`: greet the dispatcher when `started` holds it. `operator up`: greet after `ensure_flow; ensure_rail`, only when the agent was started. `revive`: collect each role it brought back of a `main`, `dispatch` or `operator` scope and greet them together after the loop; a team's conductor keeps `greet_conductor`. Keep `set -euo pipefail` safe with `wait`.

### 1.3

`tests/t-main.sh`: after `crew main up wldn`, each of `wldn-design`, `wldn-planner`, `wldn-ops`, `wldn-dispatch-chuck-herdr-alpha` and `wldn-dispatch-mac-studio` has exactly one `agent prompt <name> [crew] Read where wldn stands` in `CREW_TEST_LOG` on its host and session, and the output says "<name> greeted" for each; a second `crew main up` adds none; after `crew main down` and `crew main up`, each has one more. A `blocked` planner (`stub status … blocked`, set back to `idle` after a few seconds, as `t-greet.sh` does) is greeted once after it is answered, while the design agent and ops are greeted without waiting on it. An agent that never settles is tested through `crewpy greet-agent <name> --wait 2` on a `working` agent: it says the agent was not ready and names the `crew tell` that would greet it, and sends nothing; `--wait <seconds>` is the one knob added, and `crew main up` never passes it. Each greeting has its `greet` entry in wldn's run record.

### 1.4

`tests/t-operator.sh`: the first `crew operator up madswan` greets `madswan-operator-mac-studio` once, after its `rail` tab exists; the second greets nobody (the test already asserts no `workspace create` or `pane run`; add no `agent prompt`). `tests/t-revive.sh`: the revived `wldn-design` is greeted once, and none of the agents that came back by themselves (`wldn-planner`, `wldn-ops`, the dispatcher, the operator) is; a main level taken down is neither revived nor greeted. `crewpy greet-agent swb-1-ops` and `crewpy greet-agent nobody` are refused.

### 2.1

Usage header of `plugin/bin/crew`: `crew main up|down|status` and `crew operator up` say each agent they start is greeted to read where the partition stands and carry on; `crew revive` that each agent it brings back is greeted. README's main-level paragraph and `plugin/skills/crew/SKILL.md`'s rows say the same in a clause each. Then `tests/suite t-docs`.

### 2.2

`docs/architecture/teams.md`: in `teams.7`'s detail, drop the sentence saying `crew main up`, `crew operator up` and `crew revive` greet nobody until this unit lands, and add `crew.py` `greet_agent` and `tests/t-main.sh` to its sources. `docs/architecture/_open.md`: remove the `teams.7` item under *Accepted, not built*, and drop "`crew.py`'s usage omits `greet`" from the stale comments.
