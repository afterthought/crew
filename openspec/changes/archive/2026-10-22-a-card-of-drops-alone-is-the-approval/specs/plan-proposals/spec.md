## MODIFIED Requirements

### Requirement: The card's questions are the approval and the new units
When proposal n makes units or chores new to a bolt or to a kit's queue, its card SHALL ask only those: one `multi` list and nothing else to tap, a box per new unit or chore, ticked, each with its intent as its detail and what clearing it does as its consequence; its intent SHALL be `decide`. What else the proposal changes, a drop, an amendment, a move, an order or a new bolt, SHALL be drawn on the card's face, its picture and its text and SHALL apply with it, and SHALL NOT be a box, and the card's summary SHALL say so. Send SHALL apply the change with the boxes as they stand, a new unit cleared left out, and the planner told which. A proposal of one new unit or chore SHALL be the choice of adding it or leaving it out instead, adding it recommended, since a Pending You list holds two at least. No approve block SHALL sit inside the card and no question SHALL ask for words. A proposal of more than five new units or chores SHALL be grouped into `questions` of at most five boxes each, in the plan's order.

#### Scenario: One dropped, three new
- **WHEN** crew raises the card for a proposal that drops `a` and adds `b`, `c` and `d`
- **THEN** the card is one list of three boxes, `b`, `c` and `d`, every one ticked, with no box for `a`; its face holds a paragraph for `a`'s drop; and sending it as it stands applies the proposal whole, `a` dropped

#### Scenario: How to object to a drop
- **WHEN** the card of a proposal that drops `a` and adds `b`, `c` and `d` is raised
- **THEN** its summary says that what it drops or amends applies with it, and no box on it keeps `a`

#### Scenario: A move alone
- **WHEN** the proposal moves bolt `y` first and changes no unit
- **THEN** the card is a hold-to-approve of risk low

#### Scenario: A new unit left out beside an amendment
- **WHEN** the proposal amends `x` and adds `b` and `c`, and the user clears `c` and sends
- **THEN** `x`'s amendment and `b` are applied, `c` is left out, and the planner is told `c` was left out

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c` and nothing else
- **THEN** the card is the choice of adding `c` or leaving it out, adding `c` recommended, and Send applies the side picked

#### Scenario: One new unit beside a drop
- **WHEN** the proposal drops `a` and adds `c`
- **THEN** the card is the choice of adding `c` or leaving it out, and `a`'s drop applies whichever side is sent

#### Scenario: Seven new units
- **WHEN** crew raises the card for a proposal that adds seven units
- **THEN** the card has two questions of four and three boxes, every one ticked

### Requirement: A card with no new unit, or more than fifteen, is a plain approval
When proposal n makes no unit or chore new to a bolt or the queue, whether it drops, amends, moves or orders units or makes or orders bolts, alone or in any mix, or when it makes more than fifteen new, its card SHALL be a hold-to-approve of low risk, reversible, with no boxes and its change drawn on its face, its picture and its text. Approving it SHALL apply it whole; declining it SHALL apply nothing. The card of a proposal that drops or amends SHALL say that declining with a note keeps what it drops or amends. The card of more than fifteen SHALL say it links the proposal's plannotator session.

#### Scenario: Drops alone
- **WHEN** the proposal drops `a`, `b` and `c` and nothing else
- **THEN** the card is a hold-to-approve with no boxes, its face holds a paragraph for each dropped unit with its why, its summary says declining with a note keeps what it drops, and approving it drops all three

#### Scenario: Drops with an amendment and an order
- **WHEN** the proposal drops `a`, amends `x` and orders `d` first
- **THEN** the card is a hold-to-approve with no boxes, and approving it applies all three

#### Scenario: Keeping a dropped unit
- **WHEN** the user declines a drops-alone card with the note "keep b", and the planner runs `crew plan answer N plan decline --note "keep b"`
- **THEN** nothing is applied, and crew says the user's note is the planner's to act on, writing the proposal again or dropping it

#### Scenario: No new unit
- **WHEN** the proposal only orders a unit first
- **THEN** the card is a hold-to-approve with no boxes, and approving it applies it whole

#### Scenario: Sixteen new units
- **WHEN** the proposal adds sixteen units
- **THEN** the card is a hold-to-approve with no boxes, and says it links the proposal's plannotator session

### Requirement: A card's answers are gathered before the approval
`crew plan answer <n> <question> <answer>...` SHALL record one question's answer of open proposal n's card on the host it runs on, checked against the card crew builds for the proposal: `rows-<k>` with the ids of the boxes the user left ticked, `rows-1` for a card of one list, and for a lone new unit the side picked; or, for a hold-to-approve, `plan` with `approve` or `decline`. Once it holds every question's answer, it SHALL apply the change with the boxes as they stand, each new unit unticked cleared as `crew plan approve <n> --clear` clears it, the approved proposal recording each of those units as cleared, and crew SHALL close the card with what was applied; until then it SHALL apply nothing and name the questions it waits on.

#### Scenario: A card the user split
- **WHEN** proposal N adds seven units, the user sends the card's first list, and the planner runs `crew plan answer N rows-1` with its four boxes
- **THEN** nothing is applied and crew says it waits on `rows-2`; when the planner then runs `crew plan answer N rows-2` with two of its three boxes, the change is applied with the third unit left out

#### Scenario: Declined
- **WHEN** the planner runs `crew plan answer N plan decline` for a hold-to-approve
- **THEN** nothing is applied, the gathered answers are discarded, and crew says the user's note is theirs to act on, writing the proposal again or dropping it

#### Scenario: A box the card no longer asks
- **WHEN** the planner runs `crew plan answer N rows-1 keep:a add:b` for a proposal that drops `a` and adds `b` and `c`
- **THEN** it is refused, naming the boxes `rows-1` holds, `add:b` or `add:c`, and nothing is recorded
