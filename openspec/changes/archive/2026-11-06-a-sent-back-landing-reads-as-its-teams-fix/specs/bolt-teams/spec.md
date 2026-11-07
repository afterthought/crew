## ADDED Requirements

### Requirement: A landing sluice sent back is its team's fix
A landing sluice sent back for the bolt's own content SHALL be its team's fix until a fix moves the bolt's head: crew SHALL name what failed from sluice's record of the submission, never from a check's words, and SHALL offer the team's `crew fix` and the `crew bolt submit` that lands it once that fix has merged, never a submission again at the head sluice sent back. A later submit at that head that submitted nothing SHALL leave it its team's fix, never a stop of sluice's.

#### Scenario: A check fails
- **WHEN** `crew bolt submit z` waits on `#7` and sluice's record has it failed with `tests:logic`, which ran and failed, tested on main at `db8bc25`
- **THEN** the command fails, saying `z` did not land, that a failed check is the bolt's, `crew fix <team> landing-7 "Mend what sluice sent bolt/z's landing back for: #7 failed tests:logic, tested on main at db8bc25" --bolt z`, and that once that fix has merged into `bolt/z`, `crew bolt submit z` submits the landing again at its new head

#### Scenario: Submitted again at the head sluice sent back
- **WHEN** ops runs `crew bolt submit z` again while `z`'s head is still the one sluice sent back as `#7`
- **THEN** crew reads sluice's record of `#7` on the team's host and submits nothing, runs no `wt submit` and leaves the pull request a draft, refusing in words that name what failed and the team's fix with its command and the submit once it has merged, saying it is its team's fix, not a stop, and `z` stays held on its row

#### Scenario: A submit that submitted nothing
- **WHEN** `z`'s landing was refused at `977138a` and a later `crew bolt submit z` at `977138a` ends with sluice's driver submitting nothing, recorded stopped with no submission
- **THEN** `z` reads as held for its team's fix at `977138a`, on its kit's landings card, the rail and `crew bolts`, and no reader says it was stopped or that ops submits it again as it is

#### Scenario: The fix moves the head
- **WHEN** `z`'s team's fix has merged and `z`'s head is no longer the one sluice sent back
- **THEN** `crew bolt submit z` submits it at its new head as any landing, asking sluice's record of `#7` nothing

#### Scenario: sluice's record can't be read
- **WHEN** `crew bolt submit z` finds `z`'s landing refused at its head and `sluice status 7 --json` fails
- **THEN** it submits nothing, saying the words the refusal was recorded with and why the record can't be read, and offers the team's fix with no command

#### Scenario: crew bolts
- **WHEN** `z`'s landing was refused at its present head
- **THEN** `crew bolts` shows on `z` `landing: sent back at <head>, its team's fix: <sluice's words>; once that fix has merged, crew bolt submit z submits it again`, and its JSON gives `z` `sent_back` with the head, the words and sluice's number
