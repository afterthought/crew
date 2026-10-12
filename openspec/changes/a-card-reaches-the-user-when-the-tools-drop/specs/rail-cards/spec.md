## ADDED Requirements

### Requirement: A crew agent's card is posted through crew
`crew card post <key>` SHALL post the card given as one JSON object on its standard input as the asking assistant, through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in, and SHALL print the card's id and its link. crew SHALL set the card's `idempotencyKey` to the key, its session to the agent's crew name, this host and the folder the command runs in, and its area to the one Pending You matches to the folder's git remote, or, when none matches, the kit's area made under `create-area:<owner>/<kit>`. It SHALL refuse a card that gives any of those itself. Before anything reaches Pending You it SHALL refuse a key and a form that crew's card hook refuses, in the hook's words.

#### Scenario: A verify card posted
- **WHEN** swb-1-conductor, whose team holds bolt `b1`, runs `crew card post verify/v1/<stamp>` in its worktree with a choice card on standard input
- **THEN** Pending You is asked, as swb-1-conductor, to post that card under the key `verify/v1/<stamp>`, with swb-1-conductor's name, the host and the worktree as its session and the kit's area, and the command prints the card's id and link

#### Scenario: Posted again
- **WHEN** swb-1-conductor runs the same post a second time
- **THEN** Pending You gives the same card back under the same key, and no second card is made

#### Scenario: A key that is not the agent's
- **WHEN** swb-1-conductor runs `crew card post proposal/9`
- **THEN** the command refuses in the hook's words, naming the keys that are swb-1-conductor's, and Pending You is not called

#### Scenario: A card in another form than its row's
- **WHEN** swb-1-conductor posts a verify card as an approval
- **THEN** the command refuses, naming the form a verify report's card takes, and Pending You is not called

#### Scenario: A card that sets crew's fields
- **WHEN** a card on standard input gives its own `areaId`
- **THEN** the command refuses, saying crew sets `idempotencyKey`, `areaId` and `session` itself

#### Scenario: No kit's area yet
- **WHEN** Pending You matches no area to the worktree's remote `github.com/WilldanGroup/switchboard-kit`
- **THEN** crew makes the area under `create-area:WilldanGroup/switchboard-kit`, named `switchboard-kit`, in the partition's group, and files the card there

### Requirement: A crew agent's card is changed, closed and read through crew
`crew card change <key>` SHALL change the card the agent holds under the key with the fields given on its standard input, at the version Pending You reports, and SHALL refuse a change that takes a row's card out of its form, as the hook does. `crew card close <key>` SHALL close it with `--outcome` once the agent has acted on its answer, or withdraw it with `--reason`, and SHALL then end its plannotator session as a close through Pending You's tools does. `crew card read <key>` SHALL print the card's status, whose turn it is and, when it is the agent's, the user's answer and words, and SHALL record nothing. The card a key names SHALL be the agent's newest card posted under it on this host that no close has closed; with none, each command SHALL refuse, naming the key.

#### Scenario: A change
- **WHEN** swb-1-conductor runs `crew card change verify/v1/<stamp>` with a new option and a change note
- **THEN** Pending You is asked to change that card at the version it last reported, and a `card.update` entry names it

#### Scenario: An answer read
- **WHEN** the user has picked an option on swb-1-conductor's verify card with a note
- **THEN** `crew card read verify/v1/<stamp>` prints that it is the agent's turn, the option picked and the note

#### Scenario: Closed on its answer
- **WHEN** swb-1-conductor runs `crew card close verify/v1/<stamp> --outcome "Fixed both findings"`
- **THEN** Pending You is told the answer was acted on at the card's version, a `card.close` entry names the card, and the card's plannotator session ends

#### Scenario: Withdrawn
- **WHEN** swb-1-conductor runs `crew card close verify/v1/<stamp> --reason "Verify ran again"`
- **THEN** Pending You withdraws the card with that reason, and a `card.close` entry names it

#### Scenario: No card under the key
- **WHEN** swb-1-conductor runs `crew card read verify/v1/<stamp>` and has posted no card under it
- **THEN** the command refuses, saying swb-1-conductor holds no open card under that key

### Requirement: crew's card commands refuse what they cannot do, in the words that say why
A call Pending You refuses SHALL be refused in Pending You's own words and recorded as the act refused. When the host is not signed in to Pending You, or Pending You cannot be reached or does not answer within 60 seconds, the command SHALL refuse saying so and to try again later, and SHALL post nothing. A reply that lacks the card's or the area's id SHALL be refused as unread, never taken as empty.

#### Scenario: Pending You refuses the card
- **WHEN** Pending You refuses a posted card with "Approve requests give their risk in approve.risk."
- **THEN** the command refuses with those words, and the run record has a `card.post` entry with that refusal and no card

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and an agent runs `crew card post`
- **THEN** the command refuses, saying this computer is not signed in to Pending You, and nothing is posted

## MODIFIED Requirements

### Requirement: A crew agent's card acts are in the run record
Each card a crew agent posts, updates, withdraws or closes in Pending You, through Pending You's tools in its session or through `crew card`, SHALL be an entry in its partition's run record, naming the row's object, the card's id in `Card`, and the key in `Key` when it is a row's key. Through `crew card` the card's id SHALL be read from Pending You's own reply. An entry SHALL NOT hold a card's title, summary or any other text written on it.

#### Scenario: A card posted and closed
- **WHEN** swb-1-conductor posts the card `review/x/abc1234` and later closes it
- **THEN** the run record has a `card.post` entry on `unit/x` with that key and the card's id, and a `card.close` entry with the same id

#### Scenario: A card posted through crew
- **WHEN** swb-1-conductor runs `crew card post verify/v1/<stamp>` and Pending You answers with the card `req_v1`
- **THEN** the run record has a `card.post` entry on `unit/v1` with the key `verify/v1/<stamp>` and the card `req_v1`, and nothing written on the card

#### Scenario: The user's own sessions
- **WHEN** a Claude session crew did not start posts a Pending You card
- **THEN** nothing is written to crew's run record
