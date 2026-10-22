## ADDED Requirements

### Requirement: A send is one entry in the receiving partition's record
Each `crew send` that reaches its operator SHALL append one entry, act `send`, to the run record of the partition it was sent to, on the host the command ran on. Its `By` SHALL be the sender, its `On` the operator, `agent/<label>-operator`, and the team, `team/<team>`, when a team was named; its `Why` SHALL be `send <team or partition>`; and its `Chars` the length of the text. It SHALL hold no part of the text, and no separate tell entry SHALL be written for it. A send that types nothing SHALL write no entry, as a tell that types nothing writes none.

#### Scenario: A send to a team
- **WHEN** `crw-5-unit-1` sends 46 characters to `swb-1`, a team of wldn
- **THEN** wldn's run record gains one entry: act `send`, `By: crw-5-unit-1`, `On: agent/wldn-operator`, `On: team/swb-1`, `Why: send swb-1`, `Chars: 46`, and the text appears nowhere in it

#### Scenario: A send that is refused
- **WHEN** a send fails because `wldn-operator` is not up
- **THEN** no entry is written
