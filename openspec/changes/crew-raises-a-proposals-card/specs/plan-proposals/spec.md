## MODIFIED Requirements

### Requirement: A proposal is put before the user whole
`crew plan propose` SHALL, once a proposal is accepted into the plan, raise its card itself in the planner's name, keyed `proposal/<n>`, drawn from the plan and the proposal as record 0018 has it. Any agent that puts one of the planner's proposals before the user in a pane, the planner, a conductor or the operator agent, SHALL show what `crew plan proposed <n>` prints, in its own pane or opened beside it, and SHALL NOT name the proposal by its number alone; the number SHALL follow the words, as a reference. The agent SHALL ask for the user's answer in words, SHALL NOT recite a command for the user to answer with, and SHALL run the answering command only on the user's word.

#### Scenario: The planner proposes
- **WHEN** the planner has written proposal N and `crew plan propose` accepts it
- **THEN** its card is open, and when the user is in the planner's pane the planner shows what `crew plan proposed N` prints and asks them to approve it or say what to change

#### Scenario: The user asks what waits on them
- **WHEN** the operator agent answers where things stand and proposal N is open
- **THEN** its answer shows what `crew plan proposed N` prints, not only that proposal N is open

#### Scenario: The user says yes
- **WHEN** the user tells the agent showing proposal N to approve it
- **THEN** that agent runs `crew plan approve N`, which closes the card with what was applied

#### Scenario: A proposal with three new units
- **WHEN** the planner's proposal adding three units to a bolt is accepted as number 4
- **THEN** its card is open, titled "Plan change to <bolt>: 3 new", with the case, the change drawn and in text, a paragraph per unit, and one list of the three units ticked

### Requirement: A proposal is dropped with a reason, or replaced
`crew plan drop <n> "<reason>"` SHALL close an open proposal as `dropped` with the reason, applying nothing, withdraw its chain's card with the reason, and tell the planner when someone else dropped it. `crew plan propose <file> --replaces <n>` SHALL drop proposal n and write its successor in one commit, the successor naming the one it replaces, and SHALL change the chain's card in place to the successor with the note "Rewritten as proposal <successor> after your note"; the chain's card SHALL stay keyed by its first proposal, and the rail's row for the successor SHALL carry it.

#### Scenario: The user rejects a proposal
- **WHEN** the user drops proposal N with a reason
- **THEN** the proposal is `dropped`, the plan is unchanged, its card is withdrawn with the reason, and the planner is told the reason

#### Scenario: The planner revises
- **WHEN** the planner proposes again with `--replaces N` after the user asked for a different placement
- **THEN** proposal N is `dropped`, proposal N+1 is `open` and names N, agreements given to N do not carry over, and the card keyed `proposal/N` shows N+1 with the change note

### Requirement: The card's questions are the approval and the new units
When proposal n adds, drops or amends units or chores, its card SHALL be one `multi` list and nothing else to tap: a box per row of the change, a new unit or chore ticked, a dropped one unticked as "Keep <unit>", an amended one unticked as "Keep <unit>'s old intent", each with its intent as its detail and what ticking it does as its consequence; its intent SHALL be `approve`; Send SHALL apply the change with the boxes as they stand, a new unit unticked left out, a dropped unit ticked kept, an amendment ticked not applied, and the planner told which. No approve block SHALL sit inside the card and no question SHALL ask for words. A proposal of more than five rows SHALL be grouped into `questions` of at most five rows each, in the plan's order. A proposal with no unit rows, a move, an order or a new bolt alone, SHALL be an `approve` of risk low, reversible.

#### Scenario: One dropped, three new
- **WHEN** crew raises the card for a proposal that drops `a` and adds `b`, `c` and `d`
- **THEN** the card is one list of four boxes, `b`, `c` and `d` ticked and "Keep a" unticked, and sending it as it stands applies the proposal whole

#### Scenario: How to object to a drop
- **WHEN** the user ticks "Keep a" and sends
- **THEN** `a` stays in the bolt, the rest is applied, and the planner is told `a` was kept

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c` and nothing else
- **THEN** the card is one box, `c` ticked, and Send applies it; cleared, Pending You asks for a note before it sends, which is its limit and not crew's

#### Scenario: Seven new units
- **WHEN** crew raises the card for a proposal that adds seven units
- **THEN** the card has two questions of four and three boxes, every one ticked

#### Scenario: A move alone
- **WHEN** the proposal moves bolt `y` first and changes no unit
- **THEN** the card is a hold-to-approve of risk low
