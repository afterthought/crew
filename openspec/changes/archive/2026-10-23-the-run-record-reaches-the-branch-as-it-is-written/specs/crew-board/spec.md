## MODIFIED Requirements

### Requirement: The attention line names what is wrong
The board SHALL end with an attention line, each item marked !, naming each host that did not answer for its kits, never for its run record, which is read from the partition's branch; each plan or signals home it could not read, with why, the branch among them when its run record could not be read; and each bolt a team holds whose every unit has landed but which is still in the plan. A ledger whose bolt is in that state SHALL also carry ! on its head line. With nothing to name, the attention line SHALL say none.

#### Scenario: A host down
- **WHEN** the box holding swb-1 does not answer
- **THEN** the attention line names the box and why, and swb-1's ledger shows its units from the plan with their stages unknown

#### Scenario: An operator host asleep
- **WHEN** macbook-pro, which holds a wldn operator session and runs no team, does not answer
- **THEN** the attention line does not name macbook-pro, and the landings, batches and cards read from `wldn/main` are drawn whole

#### Scenario: Landed but still in the plan
- **WHEN** every unit of a held bolt has landed on main and `crew bolt land` has not run
- **THEN** its ledger's head carries ! and the attention line names the bolt as landed and still in the plan
