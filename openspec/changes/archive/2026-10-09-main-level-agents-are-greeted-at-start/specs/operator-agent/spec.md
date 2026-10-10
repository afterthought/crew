## MODIFIED Requirements

### Requirement: The operator agent starts with its operator session
`crew operator up <label>` SHALL start the operator agent, `<label>-operator-<host>`, in a herdr workspace named `operator` in the session named `<label>` on the host it runs on, and greet it once it is up, as the `main-level` spec greets every agent crew starts outside a team: told, in a message marked as crew's, to read where the partition stands and carry on with what is its role's. When the agent is already up, it SHALL do nothing, greet nobody, and succeed. When the session or the partition is unknown, it SHALL exit non-zero, naming what is missing.

#### Scenario: Started by the host
- **WHEN** the `madswan` operator session starts on mac-studio and its supervisor runs `crew operator up madswan`
- **THEN** `madswan-operator-mac-studio` is running in the `operator` workspace of that session, and is greeted once

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs while the agent is up
- **THEN** nothing is started, nobody is greeted, and the command succeeds
