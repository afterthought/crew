## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
`crew card session <key> [<unit>]` SHALL start a plannotator review of the document the rail row with that card key asks the user to read: the proposal's page for `proposal/<n>` and, for `batch/<n>`, the batch's folder: the reviewer's summary whole and every unit's whole change as read at its commit. A batch card posted before one card per batch was built, keyed `batch/<n>-<k>`, SHALL keep one session for each unit it holds, on that unit's whole change, its Markdown files given as one review and never its folder, started with the unit named, on the host the teams file names for the unit's team. A `batch/<n>` card's session SHALL run on the partition's main level's host; every other session on the host the command runs on. The session SHALL offer an Approve button and SHALL NOT open a browser on the host, and the command SHALL print the session's link. A verify report has no row, so `verify/<unit>/<stamp>` starts no session.

#### Scenario: A batch card's session
- **WHEN** the planner runs `crew card session batch/3` on the main level's host, for a batch of `x` and `z` from two teams' hosts
- **THEN** one plannotator session is running there on the batch's summary and both units' changes, no browser has opened, and the command prints a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A unit named with a batch's key
- **WHEN** the planner runs `crew card session batch/3 x`
- **THEN** it is refused, saying a batch has one reading session, on the whole batch, and no session is started

#### Scenario: A batch card posted under an old key
- **WHEN** the planner runs `crew card session batch/2-2 x` for an open card of batch 2 posted under that key, and `x` is among its units
- **THEN** a session on `x`'s change is running on `x`'s team's host, given each of its Markdown files as its own path, proposal first, and not its folder, and its link is printed

#### Scenario: A proposal card's session
- **WHEN** the planner runs `crew card session proposal/4`
- **THEN** a session is running on proposal 4's page as `crew plan proposed 4` prints it, and its link is printed

#### Scenario: A review card's session
- **WHEN** swb-1-conductor runs `crew card session review/x/abc1234`
- **THEN** it is refused as not a card key, since there is no review row, and no session is started

#### Scenario: A verify report's key
- **WHEN** swb-1-conductor runs `crew card session verify/x/20261013-1200`
- **THEN** it is refused, saying no row of the rail has that key, and no session is started
