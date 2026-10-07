# Spec Delta

## ADDED Requirements

### Requirement: A proposal can be opened in plannotator
`crew plan proposed <n> [--label L] --open` SHALL write the proposal, exactly as `crew plan proposed <n>` prints it, to a file on the host it runs on, and open that file in plannotator for the user to read and annotate: beside the caller with `plannotator-tui herdr open` when it runs in herdr, inline with `plannotator-tui` otherwise. It SHALL read only the flywheel's branch, so it works from any host. It SHALL write nothing to the branch or the run record. `--open` SHALL be refused without `<n>` and with `--json`.

#### Scenario: Opened from the rail's shell
- **WHEN** the user runs `crew plan proposed 3 --label wldn --open` in a herdr pane
- **THEN** plannotator opens beside it with the same text `crew plan proposed 3 --label wldn` prints

#### Scenario: Without a number
- **WHEN** `crew plan proposed --open` is run
- **THEN** it is refused, saying `--open` needs a proposal's number
