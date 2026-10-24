## ADDED Requirements

### Requirement: A ticked bolt's approval stands while its own work is unchanged
The user's send on a kit's landings card SHALL stand for each bolt they ticked, at any later head whose own work is the same as at the head they ticked. A bolt's own work SHALL be the non-merge commits its head holds that GitHub's main does not. A bolt whose send stands SHALL be no row of any later landings card, and SHALL land on that send once it reads proven at its new head, with no card asking for it.

#### Scenario: A refused bolt takes main in
- **WHEN** the user sent `land/crew` with `z` ticked at `abc1234`, sluice refused `z` for a conflict with main, and `z`'s team's take-main fix, resolving the conflict in its merge, merged into `z`, which reads proven at `def5678`
- **THEN** no landings card asks for `z`, and `crew card read land/crew` names `z` among the bolts the user's earlier send lands, with the `crew bolt submit` that lands it

#### Scenario: The head moves by taking main in before the landing
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `y` is landing, and a take-main fix moves `z`'s head before ops submits it
- **THEN** the card is left as it is, and once `z` reads proven at its new head it lands on the same send

#### Scenario: The host's copy is brought level
- **WHEN** the user ticked `z` at the host copy's head `abc1234`, and the copy is brought level with GitHub's `def5678`, whose merges bring in only main's commits
- **THEN** the send stands for `z` at `def5678`

#### Scenario: Two take-main fixes in a row
- **WHEN** the user ticked `z` at `abc1234`, and two take-main fixes later `z` reads proven at `0a1b2c3`, holding the same commits of its own as at `abc1234`
- **THEN** the send stands for `z` at `0a1b2c3`

### Requirement: A ticked bolt whose own work changed is asked again, saying what changed
A bolt the user ticked whose head now holds commits of its own the ticked head did not, or lacks some it held, SHALL be a row of the next landings card, and that card SHALL say the head the user sent, the head now, and the subjects of the commits gained and lost, five at most, with how many more. A bolt whose own work crew cannot compare SHALL be asked again the same way, the card saying why crew could not tell.

#### Scenario: A fix adds a commit
- **WHEN** the user ticked `z` at `abc1234`, and a fix that commits `fix: keep the lease` merges into `z`, which reads proven at `def5678`
- **THEN** `z` is a row of the card that follows, and its note says `z`'s head is now `def5678`, with work of its own since the user's send at `abc1234`: `fix: keep the lease`

#### Scenario: A take-main fix that also commits a change
- **WHEN** the user ticked `z` at `abc1234`, and its take-main fix merges main and then commits `test: wait for the new lock`
- **THEN** `z` is asked again, the card naming `test: wait for the new lock`

#### Scenario: crew cannot compare the heads
- **WHEN** the user ticked `z` at `abc1234`, `z` reads proven at `def5678`, and GitHub's main cannot be fetched where the kit's forecasts are made
- **THEN** `z` is asked again, and the card says crew could not tell whether `z`'s own work changed since the send, in git's words

## MODIFIED Requirements

### Requirement: A refused landing is held on its row
A bolt whose submission to main sluice refused, or that failed main's checks, SHALL be held on its row at that head, with no box, the row saying sluice's words and that it waits for its team's fix, while the bolts after it go on. Once its head moves and it reads proven, it SHALL land on the user's send that ticked it when that send still stands for its work, and SHALL otherwise have a box again.

#### Scenario: The second of three is refused
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked, and sluice refuses `z` for a conflict on `plugin/lib/plan.py`
- **THEN** `y` and `w` land, `z` stays on crew's landing row held, saying sluice's words and that it waits for its team's fix, and the next landings card raised carries `z` held with no box

#### Scenario: The fix merges
- **WHEN** `z`'s team's take-main fix merges into `z` and `z` reads proven at its new head, its own work unchanged since the user's send
- **THEN** `z` has no box on any landings card and lands on that send

#### Scenario: A fix that changes the bolt's work merges
- **WHEN** `z` was refused for a failed check, and its team's fix commits a change and merges, and `z` reads proven at its new head
- **THEN** `z` has a box on `land/crew` again, its note naming the fix's commit

### Requirement: The landings card closes when nothing waits
A landings card the user has answered SHALL be left as it is until every bolt they ticked has landed or been held, then closed naming what landed and where GitHub's main holds it, what was held and why, and what was left; a new card SHALL follow it while rows can land. The close SHALL keep the user's send for each ticked bolt that was held and still stands for its work, saying so. A send ticking none SHALL close it, landing nothing. With no row that can land, no card SHALL be open, and the next proven bolt SHALL raise one, following nothing.

#### Scenario: Everything ticked lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked and both land
- **THEN** the card is closed saying `y` and `z` landed and where GitHub's main holds them, and no landings card of crew is open

#### Scenario: One left out
- **WHEN** the user sent `land/crew` with `y` ticked and `z` cleared, and `y` lands
- **THEN** the card is closed saying `y` landed and `z` was left, and a new card follows it with `z` as its one row

#### Scenario: The next proven bolt
- **WHEN** no landings card of crew is open and bolt `w` reads proven
- **THEN** `land/crew` is posted with `w` as its one row, following no card

#### Scenario: A ticked bolt held at the close
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `y` lands and sluice refuses `z`
- **THEN** the card is closed saying `y` landed and `z` was held and why, and that the send stands for `z`: it lands once its team's fix has only taken main in and sluice has proven it, with nothing asked
