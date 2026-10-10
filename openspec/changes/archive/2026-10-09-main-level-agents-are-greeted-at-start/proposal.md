# Proposal

## Why

When the user took swancloud's main level down and brought it back up, its agents started with no first prompt and sat idle until the operator agent told each one what to do: "I just brought down and back up the main swancloud agents. They got no initial instructions, though." (signal `2026-10-08-swancloud-operator-mac-studio-c1fb895d/01-main-level-starts-without-instructions`). A team's conductor is already greeted at every start and carries on with its bolt by itself; the design agent, the planner, the main-level ops, each dispatcher and the operator agent are not. The `main-level` spec and `teams.7` now hold them to the conductor's rule, and `_open.md` lists this unit as what makes the code catch up.

## What Changes

- **Every agent crew starts outside a team is greeted once it is up.** `crew main up` greets the design agent, the planner and the main-level ops it starts, and each dispatcher it starts on every host the partition's teams run on; `crew operator up` greets the operator agent it starts. The greeting is crew's own, marked `[crew]`, like the conductor's.
- **Each greeting fits the role.** It tells the agent to read where its partition stands with the crew commands its brief already names (the bolts, the rail, the open proposals, its host's teams), say so in a few lines, and carry on with what is its own. Main-level ops is told to land nothing without the user's word, as its brief says.
- **Exactly once per start.** An agent that is already up when `crew main up` or `crew operator up` runs again is neither started nor greeted. An agent brought back by `crew revive` after a host restart is greeted once, as a revived conductor is; a main level taken down with `crew main down` stays down through a revive and is greeted when `crew main up` brings it back.
- **One agent waiting on a question holds back nobody else.** An agent stopped on a question in its pane, such as a first run's consent, is greeted once it is answered, as a conductor is, while the others are greeted meanwhile. An agent that never settles is reported with the command that would greet it, and the bring-up still succeeds.
- **Each greeting is in the run record**, as a conductor's is: one `greet` entry naming the agent, in its partition.
- **The rule reads as built.** `teams.7`'s detail and `_open.md` stop saying the main level greets nobody.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: "The main level is one herdr workspace" already requires the greeting; its delta adds the scenarios that pin what "exactly once per start" means: a second `crew main up` greets nobody, a revive greets only what it brought back, and an agent waiting on a question is greeted once it is answered.
- `operator-agent`: "The operator agent starts with its operator session" says the operator agent is greeted when `crew operator up` starts it, and not when it was already up.

## Impact

- `plugin/lib/crew.py`: `greet` generalised from a team's conductor to any standing agent, with a greeting per role.
- `plugin/bin/crew`: `crew main up`, `crew _dispatch up`, `crew operator up` and `revive` greet each agent they start.
- `docs/architecture/teams.md` (`teams.7` detail), `docs/architecture/_open.md`.
- `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`: `crew main up`, `crew operator up` and `crew revive` say they greet what they start (`docs.2`).
- Tests: `tests/t-main.sh`, `tests/t-operator.sh`, `tests/t-revive.sh`, `tests/t-greet.sh`.

## Touches

`plugin/lib/crew.py` (`greet`, `GREETING`, `main`'s `greet` entry), `plugin/bin/crew` (`main up`, `_dispatch up`, `operator up`, `revive`, `greet_conductor`, the usage header), `docs/architecture/teams.md`, `docs/architecture/_open.md`, `README.md`, `plugin/skills/crew/SKILL.md`, `tests/t-main.sh`, `tests/t-operator.sh`, `tests/t-revive.sh`, `tests/t-greet.sh`, `tests/moon.yml` (shared: only if a test's inputs change), `openspec/specs/main-level/spec.md` and `openspec/specs/operator-agent/spec.md` (by delta).
