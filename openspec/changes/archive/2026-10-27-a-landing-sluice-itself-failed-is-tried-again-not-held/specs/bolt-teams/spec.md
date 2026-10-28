## ADDED Requirements

### Requirement: A landing that did not land is the bolt's only for its own content
When `crew bolt submit` ends with a bolt not on main, crew SHALL judge it the bolt's only when sluice's record of the landing's own submission has it in conflict, or blamed for a check that ran and failed or that its time limit cut off; never by sluice's exit or words alone. The bolt's SHALL be recorded refused at the head submitted.

#### Scenario: A conflict is the bolt's
- **WHEN** `crew bolt submit z` waits on its submission and sluice's record has it in conflict on `README.md`
- **THEN** the command fails, saying `z` did not land and that its team takes main into it, and the run record's `bolt.submit` for `z` carries `Refused` and the head submitted

#### Scenario: A check that ran and failed
- **WHEN** sluice's record has the submission failed with `tests:logic` holding a failing result
- **THEN** the landing is the bolt's and recorded refused, as for a conflict

### Requirement: A landing stopped by sluice or its host is recorded stopped
Any end of `crew bolt submit` with the bolt not on main that is not the bolt's SHALL be recorded as stopped at the head submitted, with what stopped it and no refusal, and crew's words SHALL say nothing of the bolt's stopped it and tell ops to submit it again once that is cleared, with no new word of the user's.

#### Scenario: Checks the host could not run
- **WHEN** sluice's record has the submission failed, every failed check left without a result and none cut off by a time limit
- **THEN** the command fails, saying `z` did not land, that nothing of the bolt's stopped it, which checks could not run, and that ops submits it again once the host can run them, with no new word; and the `bolt.submit` for `z` carries no `Refused`, its `Outcome` stopped, its `Why` those words and its `Head`

#### Scenario: sluice itself fails
- **WHEN** sluice exits 3, main does not hold the bolt, and crew's waits again end with sluice's record of the submission still standing, or no record of it
- **THEN** the landing is recorded stopped at the head submitted, in sluice's last words, and crew says ops submits it again once sluice is cleared

#### Scenario: A refusal at once with no record of a conflict
- **WHEN** sluice answers the submission at once with exit 2 and records no submission of the head in conflict
- **THEN** the landing is recorded stopped, in sluice's words, and holds nothing
