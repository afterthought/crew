## MODIFIED Requirements


### Requirement: A deploy and every operation are approved and recorded through crew
A kit's deployer SHALL ask crew for each deploy of a `manual` environment with `crew ops offer <env> --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]`, the notes file the kit's release notes for the range from the environment's last deployed commit to the offered one as the kit's changelog tool writes them, the steps file the range's after-deploy steps one a line as the deployer gathers them (`step <n> <doer> <when> <environments> <why> <text>`), which SHALL raise the deploy's card in main-level ops's name, keyed `deploy/<env>`, with the notes and the steps on its face and nothing of them written by crew, change it when a newer head is offered, post it again when the commit already offered is offered again with the same files and main-level ops holds no card open under `deploy/<env>`, writing no second offer, and tell main-level ops the line that adopts it, `call get_request (requestId <id>, name <role>)`; the user's word SHALL be holding that card, recorded with `crew ops approve`. `crew ops record --act end` SHALL close the card with the deploy's outcome. `crew ops step` SHALL raise a step's card, keyed `op/<env>/<n>`, when the step's doer is the user or the step is marked held for the user's word, SHALL change it when the step is recorded again while it is open with other words, another doer or another hold, printing the line that adopts it whether it changed it or not, and SHALL close it when the step is recorded done or declined. `crew ops word` SHALL give the commit the word is for until that deploy's end is recorded. Every `crew ops` command SHALL run where the partition's main level runs.

#### Scenario: A deploy offered and approved
- **WHEN** the deployer offers mac-studio a deploy of main's head and the user holds its card
- **THEN** main-level ops runs `crew ops approve`, the row leaves the rail, `crew ops word mac-studio` prints the commit until the deploy's end is recorded, and `crew ops record mac-studio --act end` closes the card with each step's outcome

#### Scenario: An approval for another commit
- **WHEN** `crew ops approve` names a commit other than the open offer's
- **THEN** it is refused, recorded as refused, and no word is given

#### Scenario: An operation the user is to take
- **WHEN** the deployer records a step whose doer is the user as waiting, after a deploy or on its own
- **THEN** the rail shows it under operations with its `do` card until it is recorded done or declined, and `crew ops steps` gives its latest state

#### Scenario: A held step
- **WHEN** the deployer records a step whose doer is main-ops and marked held, after mac-studio's deploy
- **THEN** the rail shows it under operations with a card asking now, when quiet or skip, and the step runs when the user answers

#### Scenario: The same commit offered again after its card was refused
- **WHEN** Pending You refused deneb's deploy card for `ddcf2cb`, and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** crew posts deneb's deploy card under `deploy/deneb`, the run record gains no second `ops.offer` for it, and main-level ops is told the line that adopts the card

#### Scenario: The same commit offered again while its card is open
- **WHEN** swancloud-ops's card for deneb's offer of `ddcf2cb` is open, and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** nothing is written, posted or changed
