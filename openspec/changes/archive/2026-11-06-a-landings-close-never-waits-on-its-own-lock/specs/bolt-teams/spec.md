## MODIFIED Requirements

### Requirement: A landing is recorded by whatever reads the bolt after it
Whichever crew act reads a bolt first after sluice's record has its landing's submission out SHALL record the landing's outcome, on any host. The landing's waiter as it stops, `crew bolt submit`'s own end, the team's read on its host, and `crew bolt land` are all such acts. The read SHALL take the number from the bolt's last `bolt.submit` entry with `Outcome` queued, and SHALL read sluice's record of that submission on the team's host. The reads of one bolt SHALL run there one at a time, so a landing's outcome is recorded once. A read SHALL never wait on itself: the tidy that a read's close of a landed bolt runs on the team's host, which the close waits on while the read holds the bolt's turn, SHALL read no bolt's landing, and the team's next read SHALL read the landings of its other bolts. While sluice's record has the submission standing, the read SHALL record nothing. Once it is out, the read SHALL record what `crew bolt submit` records for that outcome: landed, judged by main now as a landing is; refused, for the bolt's own content; or stopped. A landed bolt SHALL then be closed with `crew bolt land`'s own code, with no word asked of whoever ran the act, since the user's word to land was given and the read records sluice's fact (`plan.21`). When sluice's record cannot be read, the read SHALL record nothing and SHALL say why, naming the host. `crew bolt land` run by hand SHALL still close a landed bolt, but it SHALL never be the only way a landing is recorded or closed. A read that closes a bolt landed on the user's words in ops's pane, on another host than the one that keeps those words, SHALL NOT fetch them from that host: the landing card SHALL close naming ops's pane and the time the word was given, and crew SHALL say which host keeps the words.

#### Scenario: The submitter is gone before sluice decides
- **WHEN** `crew bolt submit z` queues submission 412 and its process is killed, and sluice then lands 412 on main
- **THEN** the waiter's read records `z` landed at the commit main holds and closes it, and no one runs `crew bolt land`

#### Scenario: The team's read records it
- **WHEN** the waiter on the team's host was stopped before sluice decided 412, and sluice's record later has 412 landed
- **THEN** the conductor's next command on that team records `z` landed and closes it

#### Scenario: Two reads at once
- **WHEN** the waiter's read and `crew bolt submit`'s own end read `z`'s landing at the same moment
- **THEN** the run record holds one `bolt.submit` outcome for 412 and one `bolt.land`, and each says the bolt landed

#### Scenario: A close's tidy reads the plan from before the close
- **WHEN** the waiter's read of `z` finds 412 landed and closes `z`, and the tidy the close runs on the team's host reads the plan as it stood before the close, its `bolt.land` entry not yet on the branch, so the plan still holds `z` with every unit landed
- **THEN** the tidy reads no landing, the read ends, and the run record holds one `bolt.submit` outcome for 412 and one `bolt.land`

#### Scenario: Still standing
- **WHEN** a read finds sluice's record of 412 still under test
- **THEN** nothing is recorded, and the bolt's last `bolt.submit` stays queued

#### Scenario: A conflict recorded by a later read
- **WHEN** the submitter is gone and sluice's record has 412 in conflict
- **THEN** the next read records `z`'s landing refused at the head submitted, in sluice's verdict, drafts its pull request, and raises its kit's landings card with `z` held for its team's fix

#### Scenario: The user's words are kept on another host
- **WHEN** ops on mac-studio runs `crew bolt submit z` on the user's words in its pane, `z`'s team runs on deneb, and the waiter's read on deneb finds 412 landed
- **THEN** the read closes `z` and its landing card naming ops's pane and the time the word was given, none of the words, says the words are kept on mac-studio, and reaches no other host for them

#### Scenario: sluice's record can't be read
- **WHEN** `sluice status 412 --json` on the team's host fails
- **THEN** the read records nothing, and says it cannot read sluice's record of 412 on that host, with sluice's words
