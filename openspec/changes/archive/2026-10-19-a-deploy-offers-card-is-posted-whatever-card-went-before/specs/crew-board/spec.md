## MODIFIED Requirements

### Requirement: Main-level ops's view shows the operations
Main-level ops (`<label>-ops`) SHALL have a view among the agents' views, drawn above its prompt by crew's mod: a head counting the deploys waiting on the user's word, those running and the operations waiting, then, environment by environment, each deploy waiting on the word with its card, each approved and not yet deployed, each running, and each operation step waiting, handed or failed with the deploy it comes after and its doer.

#### Scenario: A deploy offered and a step handed
- **WHEN** a deploy of mac-studio waits on the user's word with wldn-ops's card open, and a step after the last deploy is handed to the dispatcher
- **THEN** wldn-ops's view counts one deploy waiting on the word and one operation, and shows the deploy with ✓ and its card, and the step as handed with the dispatcher as its doer

#### Scenario: A deploy whose card was refused
- **WHEN** a deploy of deneb waits on the user's word and Pending You refused the last post of its card
- **THEN** swancloud-ops's view shows the deploy with ✓ and says it has no card open, its post refused

### Requirement: Each rail row is a marker on its object
Every row `crew rail` would list for the partition SHALL appear on the board as a marker on the line of its object, and never as a line of its own: ✓ on a proposal's line for an open proposal, ✓ on a unit's line for a unit in review, ✎ on a unit's line for a verify report the user has not answered, and ✓ on a ledger's head line for a bolt waiting to land. Each marker SHALL say whether that row's card is open and who asked it, and, when none is open and the last post under the row's key was refused, that the row owes its card because Pending You refused its post.

#### Scenario: A unit in review
- **WHEN** unit a is in review and swb-1-conductor has a card open under its key
- **THEN** a's line in its ledger carries ✓ and says the card is open, asked by swb-1-conductor, and no other line names a's review

#### Scenario: A bolt to land
- **WHEN** every unit of tenant-environments has merged and none has landed
- **THEN** its ledger's head line carries ✓ and says whether a card is open for it

#### Scenario: A row whose card post was refused
- **WHEN** a deploy of deneb waits on the user's word, no card is open under `deploy/deneb`, and the last post under that key was refused
- **THEN** its line in Operation carries ✓ and says it has no card open, its post refused, and the JSON's marker carries the refusal's words

### Requirement: The board prints its lanes as JSON
`crew board --json` SHALL print the same board as JSON: for each partition, its lanes as lists of objects, each object with its partition, its team where it has one, and its markers, each marker with its rail group, its card key, when its row began to wait, its card, and, when no card is open, the words of Pending You's refusal of the last post under its key, or none, and the attention items; and the hosts that did not answer and the plans not read.

#### Scenario: The page's input
- **WHEN** `crew board --label wldn --json` runs while unit a is in review
- **THEN** the JSON's Construction lane holds tenant-environments with team swb-1, and unit a with a marker of group review and its card key
