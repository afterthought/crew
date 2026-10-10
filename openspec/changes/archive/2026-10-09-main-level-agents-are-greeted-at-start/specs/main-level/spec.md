## MODIFIED Requirements

### Requirement: The main level is one herdr workspace
`crew main up <label>` SHALL open a herdr workspace named `<label>` in the main level's session. It SHALL hold a `design` tab with the design agent, a `planner` tab with the planner, and an `ops` tab with the main-level ops, and start each. It SHALL then start a dispatcher on every host where the partition's teams run.

Every agent crew starts outside a team, the main level's three, each dispatcher and the operator agent, SHALL be greeted once it is up, exactly once per start, as a team's conductor is: told to read where the partition stands and carry on with what is its role's. The greeting SHALL be marked as crew's. An agent brought back by `crew revive` or `crew main up` after the main level was taken down SHALL be greeted the same way, so none sits idle until someone tells it what to do.

#### Scenario: The main level comes up
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-design`, `wldn-planner` and `wldn-ops` start in the `wldn` workspace, and `wldn-dispatch-chuck-herdr-alpha` starts on the box, and each is greeted once it is up

#### Scenario: The main level comes back
- **WHEN** the user runs `crew main down swancloud` and then `crew main up swancloud`
- **THEN** each of its agents starts and is greeted, and picks up its role from the rail and the bolts without the user or the operator agent telling it to

#### Scenario: Brought up again while it is up
- **WHEN** `crew main up wldn` runs while its agents and dispatchers are up
- **THEN** none is started and none is greeted

#### Scenario: Revived after a restart
- **WHEN** a host restarts, `wldn-design`'s pane comes back with no agent in it, and `crew revive` runs there
- **THEN** `wldn-design` is brought back and greeted once, and no agent that came back by itself is greeted

#### Scenario: An agent waiting on a question
- **WHEN** `crew main up wldn` starts `wldn-planner` stopped on a question in its pane
- **THEN** the design agent and ops are greeted without waiting on it, the command says `wldn-planner` waits on a question and will be greeted once it is answered, and it is greeted once, after the answer

#### Scenario: An agent that never settles
- **WHEN** an agent `crew main up` started is still not ready to greet when crew stops waiting for it
- **THEN** the command says so, names the `crew tell` that would greet it, and still succeeds
