## MODIFIED Requirements

### Requirement: A proposal is put before the user whole
`crew plan propose` SHALL, once a proposal is accepted into the plan, raise its card itself in the planner's name, keyed `proposal/<n>`, built from the plan and the proposal as record 0018 has it: the counts in the title, a summary, the case as bullets, the change as text and as the picture, what it waits on, an approval and a choice per new unit or chore to leave it out, a reading session's link only when more than fifteen are new. The planner SHALL also show the proposal in its pane or in plannotator when the user is there. `crew plan card` SHALL be no command.

#### Scenario: A proposal with three new units
- **WHEN** the planner's proposal adding three units to a bolt is accepted as number 4
- **THEN** its card is open with the counts, the case, the change drawn and in text, an approval and a question listing the three units ticked

### Requirement: A proposal is dropped with a reason, or replaced
`crew plan drop <n> "<reason>"` SHALL close the proposal as dropped and withdraw its chain's card with the reason. `crew plan propose <file> --replaces <n>` SHALL drop `n` as replaced, accept the new proposal, and change the chain's card in place to the new proposal with the note "Rewritten as proposal <new n> after your note"; the chain's card SHALL stay keyed by its first proposal, and the rail's row for the new proposal SHALL carry it.

#### Scenario: Replaced after a note
- **WHEN** the user notes on `proposal/4`'s card that one unit is too wide and the planner proposes again with `--replaces 4`, accepted as 5
- **THEN** proposal 4 is dropped as replaced, the card keyed `proposal/4` shows proposal 5 with the change note, and the rail has one proposal row, for 5, with that card

#### Scenario: Dropped on the user's no
- **WHEN** the user declines `proposal/4` and the planner runs `crew plan drop 4 "the user: not this quarter"`
- **THEN** the proposal is dropped and the card is withdrawn with those words
