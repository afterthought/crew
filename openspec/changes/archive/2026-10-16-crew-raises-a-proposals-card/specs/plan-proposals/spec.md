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
`crew plan drop <n> "<reason>"` SHALL close an open proposal as `dropped` with the reason, applying nothing, withdraw its chain's card with the reason, and tell the planner when someone else dropped it. `crew plan propose <file> --replaces <n>` SHALL drop proposal n and write its successor in one commit, the successor naming the one it replaces, and SHALL change the chain's card to the successor with the note "Rewritten as proposal <successor> after your note", in place while it waits on the user, and once the user's note answered it as a new version following the card they answered; the chain's card SHALL stay keyed by its first proposal, and the rail's row for the successor SHALL carry it.

#### Scenario: The user rejects a proposal
- **WHEN** the user drops proposal N with a reason
- **THEN** the proposal is `dropped`, the plan is unchanged, its card is withdrawn with the reason, and the planner is told the reason

#### Scenario: The planner revises
- **WHEN** the planner proposes again with `--replaces N` after the user asked for a different placement
- **THEN** proposal N is `dropped`, proposal N+1 is `open` and names N, agreements given to N do not carry over, and the card keyed `proposal/N` shows N+1 with the change note

### Requirement: The card's questions are the approval and the new units
When proposal n adds, drops or amends units or chores, its card SHALL be one `multi` list and nothing else to tap: a box per row of the change, a new unit or chore ticked, a dropped one unticked as "Keep <unit>", an amended one unticked as "Keep <unit>'s old intent", each with its intent as its detail and what ticking it does as its consequence; its intent SHALL be `approve`; Send SHALL apply the change with the boxes as they stand, a new unit unticked left out, a dropped unit ticked kept, an amendment ticked not applied, and the planner told which. A proposal of one row SHALL be the choice of its two sides instead, the row as proposed recommended, since a Pending You list holds two at least. No approve block SHALL sit inside the card and no question SHALL ask for words. A proposal of more than five rows SHALL be grouped into `questions` of at most five rows each, in the plan's order. A proposal with no unit rows, a move, an order or a new bolt alone, SHALL be an `approve` of risk low, reversible.

#### Scenario: One dropped, three new
- **WHEN** crew raises the card for a proposal that drops `a` and adds `b`, `c` and `d`
- **THEN** the card is one list of four boxes, `b`, `c` and `d` ticked and "Keep a" unticked, and sending it as it stands applies the proposal whole

#### Scenario: How to object to a drop
- **WHEN** the user ticks "Keep a" and sends
- **THEN** `a` stays in the bolt, the rest is applied, and the planner is told `a` was kept

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c` and nothing else
- **THEN** the card is the choice of adding `c` or leaving it out, adding `c` recommended, and Send applies the side picked

#### Scenario: Seven new units
- **WHEN** crew raises the card for a proposal that adds seven units
- **THEN** the card has two questions of four and three boxes, every one ticked

#### Scenario: A move alone
- **WHEN** the proposal moves bolt `y` first and changes no unit
- **THEN** the card is a hold-to-approve of risk low

### Requirement: A card with no new unit, or more than fifteen, is a plain approval
When proposal n has no unit rows, a move, an order or a new bolt alone, or makes more than fifteen units new to a bolt, its card SHALL be a hold-to-approve of low risk with no boxes, and the card of more than fifteen SHALL say it links the proposal's plannotator session.

#### Scenario: No new unit
- **WHEN** the proposal only orders a unit first
- **THEN** the card is a hold-to-approve with no boxes, and Send applies it whole

#### Scenario: Sixteen new units
- **WHEN** the proposal adds sixteen units
- **THEN** the card is a hold-to-approve with no boxes, and says it links the proposal's plannotator session

### Requirement: A card's answers are gathered before the approval
`crew plan answer <n> <question> <answer>...` SHALL record one question's answer of open proposal n's card on the host it runs on, checked against the card crew builds for the proposal: `rows-<k>` with the ids of the boxes the user left ticked, `rows-1` for a card of one list, and for a lone row the side picked; or, for a hold-to-approve, `plan` with `approve` or `decline`. Once it holds every question's answer, it SHALL apply the change with the boxes as they stand, each new unit unticked cleared as `crew plan approve <n> --clear` clears it, each dropped unit ticked kept in its bolt and each amendment ticked left unapplied, the approved proposal recording each of those units as cleared, and crew SHALL close the card with what was applied; until then it SHALL apply nothing and name the questions it waits on.

#### Scenario: A card the user split
- **WHEN** proposal N adds seven units, the user sends the card's first list, and the planner runs `crew plan answer N rows-1` with its four boxes
- **THEN** nothing is applied and crew says it waits on `rows-2`; when the planner then runs `crew plan answer N rows-2` with two of its three boxes, the change is applied with the third unit left out

#### Scenario: Declined
- **WHEN** the planner runs `crew plan answer N plan decline` for a hold-to-approve
- **THEN** nothing is applied, the gathered answers are discarded, and crew says the user's note is theirs to act on, writing the proposal again or dropping it

### Requirement: An answer the card did not ask is refused
`crew plan answer` SHALL refuse a question the card does not ask, a box its question does not hold, a lone row answered with other than one of its two sides, an answer that differs from one it already holds for that question, and a closed proposal, recording nothing.

#### Scenario: The same question answered twice
- **WHEN** `crew plan answer N rows-1 add:b` runs after `crew plan answer N rows-1 add:b add:c`
- **THEN** it is refused, naming the answer crew already holds

### Requirement: A note beside an approval goes to the planner after it
`crew plan answer <n> <question> <answer>... --note "<text>"` SHALL NOT hold the change for the note. Once the change is applied, crew SHALL print the note to the planner as the user's word, to propose whatever it asks as a new proposal.

#### Scenario: Approved with a note
- **WHEN** the user sends proposal N's boxes with the note "split b in two later" and the planner records them with `--note`
- **THEN** once every answer is in, the change is applied, and crew prints "split b in two later" as the user's word for the planner's next proposal
