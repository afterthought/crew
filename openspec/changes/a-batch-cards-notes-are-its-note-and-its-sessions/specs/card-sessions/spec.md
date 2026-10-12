# Spec Delta

## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
`crew card session <key> [<unit>]` SHALL start a plannotator review of the document the rail row with that card key asks the user to read: the proposal's page for `proposal/<n>`, the verify report for `verify/<unit>/<stamp>`, and, for `batch/<n>`, the batch's folder: the reviewer's summary whole and every unit's whole change as read at its commit. A batch card posted before one card per batch was built, keyed `batch/<n>-<k>`, SHALL keep one session for each unit it holds, on that unit's whole change, started with the unit named, on the host the teams file names for the unit's team. A `batch/<n>` card's session SHALL run on the partition's main level's host; every other session on the host the command runs on. The session SHALL offer an Approve button and SHALL NOT open a browser on the host, and the command SHALL print the session's link.

#### Scenario: A batch card's session
- **WHEN** the planner runs `crew card session batch/3` on the main level's host, for a batch of `x` and `z` from two teams' hosts
- **THEN** one plannotator session is running there on the batch's summary and both units' changes, no browser has opened, and the command prints a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A unit named with a batch's key
- **WHEN** the planner runs `crew card session batch/3 x`
- **THEN** it is refused, saying a batch has one reading session, on the whole batch, and no session is started

#### Scenario: A batch card posted under an old key
- **WHEN** the planner runs `crew card session batch/2-2 x` for an open card of batch 2 posted under that key, and `x` is among its units
- **THEN** a session on `x`'s change folder is running on `x`'s team's host and its link is printed, as before

#### Scenario: A proposal card's session
- **WHEN** the planner runs `crew card session proposal/4`
- **THEN** a session is running on proposal 4's page as `crew plan proposed 4` prints it, and its link is printed

#### Scenario: A review card's session
- **WHEN** swb-1-conductor runs `crew card session review/x/abc1234`
- **THEN** it is refused as not a card key, since there is no review row, and no session is started

### Requirement: A session is started only where its link can be answered
`crew card session` SHALL refuse, naming why and leaving no session running: a key that matches no rail row of the caller's partition, a `batch/<n>-<k>` key without a unit, a `batch/<n>` key with one, a `batch/<n>` key on any host but the main level's, a `land/<bolt>/<head>` key, a document that is not on the host the session would run on or that crew cannot read whole, and a session whose link names the host only for itself (`localhost` or a loopback address).

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3` after batch 3's card was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A batch's session on another host
- **WHEN** a conductor on the box runs `crew card session batch/3 --label wldn`, and the partition's main level is on mac-studio
- **THEN** it is refused, naming mac-studio, and no session is started

#### Scenario: A unit's change crew cannot read
- **WHEN** the planner runs `crew card session batch/3`, and the host of `z`'s team does not answer
- **THEN** it is refused, naming `z` and its host, and no session is started on the rest of the batch

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y/abc1234`
- **THEN** it is refused: a landing card has no document to read

#### Scenario: A link only the host can open
- **WHEN** plannotator gives the session a link on `localhost`
- **THEN** crew ends that session, refuses, and says the link would open only on this host

### Requirement: One session per card key
While a session started for a key, and for an old batch key a unit, is running, `crew card session` with that key and unit SHALL start nothing and print that session's link again.

#### Scenario: Run again after a restart
- **WHEN** the planner restarts and runs `crew card session batch/3` while the session it started before is still running
- **THEN** the command prints the same link, one session runs for batch 3, and the batch's folder is not written again

### Requirement: The session's decision reaches the owner as the card's answer
`crew card wait <key>` SHALL return when the session for that key has a decision from the user, or has ended without one, and print which: approved, with any notes the user gave; annotated, with the feedback and every annotation the user wrote, word for word; closed by the user with no decision; or ended with no decision. A decision reached while nobody waited SHALL be returned by the next wait for that key. A wait for a key with no session started SHALL be refused. A batch card's session SHALL hold the batch's notes and SHALL NOT be the card's answer: the card stays open after it.

#### Scenario: Approved in the session
- **WHEN** the user opens a verify card's link on the phone and presses Approve
- **THEN** the conductor's `crew card wait verify/x/20261011-1200` returns `approved`, and the conductor acts on it as an approval on the card

#### Scenario: Annotated in the session
- **WHEN** the user annotates two passages of a report and sends them as feedback
- **THEN** the wait returns `annotated` with both annotations and the user's words

#### Scenario: Annotated in a batch's session
- **WHEN** the user annotates a passage of `x`'s design in batch 3's session and sends it
- **THEN** the planner's `crew card wait batch/3` returns `annotated` with the annotation word for word, and batch 3's card is still open

#### Scenario: Decided while the owner was down
- **WHEN** the user approves in the session while the conductor is restarting, and the restarted conductor runs `crew card wait` for that key
- **THEN** the wait returns `approved` at once

#### Scenario: Closed with no decision
- **WHEN** the user closes the session without approving or sending feedback
- **THEN** the wait returns that the session was closed with no decision, and the card is still the user's to answer

## ADDED Requirements

### Requirement: A batch's session opens its summary and every change whole, as one review
A `batch/<n>` card's session SHALL be one plannotator review of several files, in this order: the reviewer's summary, then for each unit in the batch's order its proposal, design, specs and tasks and any other Markdown file of its change, as read at the commit the batch read it at. Each file SHALL be opened whole, as its own path, never through a folder whose files the user must open one by one, and each file's name SHALL carry its unit. crew SHALL write those files into the batch's own folder on the main level's host before it starts the session, and patch nothing of plannotator's.

#### Scenario: Two units from two teams
- **WHEN** batch 3 holds `x` of swb-1, on the box, and `z` of atl-1, on mac-studio, and the planner starts its session on mac-studio
- **THEN** the batch's folder holds `00-summary.md`, then `01-x-proposal.md` and the rest of `x`'s change, then `02-z-proposal.md` and the rest of `z`'s, each as it stood at the commit batch 3 read it at, and plannotator was given those files in that order

#### Scenario: A change's metadata
- **WHEN** a unit's change folder holds `.openspec.yaml` beside its Markdown files
- **THEN** the batch's folder and its session hold the Markdown files only
