## ADDED Requirements

### Requirement: Ops lands a bolt on a send that still stands
`crew card read land/<kit>` SHALL name each bolt an earlier send of the user's still lands, at its head now, with the `crew bolt submit` that lands it, whether or not a landings card of the kit is open; a bolt whose head now crew cannot read SHALL be named as one it cannot tell of, and left out of the command. Main-level ops SHALL land such a bolt on that send, asking the user nothing, once its conductor says it is proven.

#### Scenario: No card open
- **WHEN** the user's send on `land/crew` ticked `z`, its card closed with `z` held for sluice's refusal, `z`'s take-main fix has merged, and no landings card of crew is open
- **THEN** `crew card read land/crew` by swancloud-ops names `z` as landing on the user's earlier send and prints `crew bolt submit z --label swancloud`, and refuses nothing

#### Scenario: A head crew cannot read
- **WHEN** an earlier send ticked `z`, and `z`'s branch is on no ref crew can read where the kit's forecasts are made
- **THEN** `crew card read land/crew` says it cannot tell whether the send still lands `z`, and why, and the command it prints leaves `z` out

#### Scenario: The brief lands on a standing send
- **WHEN** main-level ops's brief is read
- **THEN** it says a bolt the user ticked whose head moved only by taking main in lands on that send once its conductor says it is proven, with nothing asked, and that the user's words in ops's pane stand the same way
