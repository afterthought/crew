## ADDED Requirements

### Requirement: Sites are listed by bolt, with no server for a started bolt's work
`crew sites [<label>] [--json]` SHALL list, for each host that keeps one of the partition's kits, each bolt in flight there. A started bolt SHALL be listed with no place and no dev server, saying its work runs in Flume's places, whose servers crew does not show yet, until the runner reports a place's addresses. A host that does not answer SHALL be named, with its bolts from the plan.

#### Scenario: A started bolt's work shows no server
- **WHEN** `an-installs-apex-is-its-own-zone` is a unit of started bolt `apex-zones`, and `devurl-serve` runs in a worktree of its kit on the box
- **THEN** `crew sites wldn` lists `apex-zones` under the box saying its work runs in Flume's places, whose servers crew does not show yet, with no URL

#### Scenario: A host that does not answer
- **WHEN** the box does not answer
- **THEN** `crew sites wldn` names the box as not answering, with `apex-zones` from the plan, and lists every other host's bolts

## REMOVED Requirements

### Requirement: Sites are listed as bolt, unit and URL
**Reason**: Record 0047 move 5, record 0050 part 3: no team's host to list and no slot's worktree; and a started bolt's places are Flume's, where crew finds no dev server, until the runner reports a place's addresses (the user's ruling of 2026-10-31; `_open.md`).
**Migration**: "Sites are listed by bolt, with no server for a started bolt's work", added by this change.
