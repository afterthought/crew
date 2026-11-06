## MODIFIED Requirements

### Requirement: A step's card is the user's do
A step whose doer is the user SHALL be a `do` card with the step's words, where it is done, each command whole as an action step, what is seen when it worked, and the options Done, Skip and Later. A step an agent runs on its own SHALL have no card. When a deploy ends with more than one step for a card, crew SHALL raise one card at a time: the first following the deploy's card, each next one following the one before, raised when crew closes it. Only another step's open card SHALL hold a step's card back: a step recorded again while its own card is open changes that card, as a row's card changes when its thing changes.

Each action step's words SHALL hold to Pending You's budget for a step, which crew keeps in the one table of Pending You's budgets beside a title's and a summary's; a command SHALL be carried whole, never cut, a step whose command is past the budget saying "Run this command.". A step's words SHALL reach the user whole, never cut, whatever their length: a step with no commands whose words are past the budget SHALL have one action step holding its first whole sentences that fit, or its first sentence cut at whole words, and its title SHALL hold the words cut at whole words to the title's budget; where neither its title, its action step nor its summary holds the words whole, its face SHALL carry them whole as inline Markdown titled "The step". A card changed in place SHALL carry no face its new version lacks.

#### Scenario: Two steps after one deploy
- **WHEN** srv's deploy ends with a step that is the user's and a step held for the user's word
- **THEN** one card is open, following the deploy's card, and the second is raised following the first when the first is closed

#### Scenario: A password only the user can rotate
- **WHEN** the deployer records a step with doer user and two commands
- **THEN** the card keyed `op/srv/1` is a `do` with both commands whole, where to run them, when it is done, and Done, Skip and Later

#### Scenario: A step an agent runs on its own
- **WHEN** the deployer records a step with doer main-ops, when quiet, not held
- **THEN** no card is raised, and the step runs at the quiet moment

#### Scenario: The Herdr re-sign-in, 370 characters with no command
- **WHEN** deneb's step `op/deneb/20` is the user's, its words 370 characters with no command and a why, and Pending You refuses a step's words of 300 characters or more
- **THEN** its card is posted: its one action step is the words' first sentence, its title the words cut at whole words within the title's budget, its summary the why, and its face the words whole as Markdown

#### Scenario: A long step whose summary holds its words
- **WHEN** a user's step with no command and no why has words past a step's budget and within a summary's
- **THEN** its summary holds the words whole and its card carries no face

#### Scenario: A command longer than a step holds
- **WHEN** a user's step has a command past a step's budget
- **THEN** its action step says "Run this command." and carries the command whole

#### Scenario: A long step recorded again short
- **WHEN** `op/srv/1`'s card carries a step's words on its face and the step is recorded again with words its title holds whole
- **THEN** the card is changed with no face

### Requirement: A held step's card is a choice of when
A step an agent can do that the change marked held for the user's word SHALL be a choice between now, when the host is quiet (recommended) and skip, each with its consequence; the agent SHALL do it at once or at the quiet moment as the user picks, or record it declined on skip. Its title SHALL end with its question, ", now or when the host is quiet?", within the title's budget, the step's words before it cut at whole words; where they are cut, its face SHALL carry them whole as inline Markdown titled "The step".

#### Scenario: A restart held for the user's word
- **WHEN** the deployer records a step with doer main-ops marked held
- **THEN** the card is a choice of now, when quiet and skip, when quiet recommended with "no stage is cut", now with the stages it cuts, and the step runs when the user picks

#### Scenario: A held step whose words are past the title
- **WHEN** a held step's words are 370 characters
- **THEN** its title is within the title's budget and ends "…, now or when the host is quiet?", and its face carries the words whole

### Requirement: A deploy waiting at its gate has the user's do card with the gate's link
A step that is the user's whose words are one link alone SHALL be read as a deploy waiting at its gate. Its card, keyed `op/<env>/<n>` and raised by crew in main-level ops's name as every step's card is, SHALL be a `do` asking the user to approve the deploy at its gate, naming the environment and, when the step names one, the commit; its one step and its *where* SHALL be the gate's link, and it SHALL say the approval at the gate is the word to deploy. A link past Pending You's budget for a step's words SHALL stay its *where*, its one step saying to open the gate at the card's link and approve the deploy there.

#### Scenario: swb-4's break-glass stand at dev's gate
- **WHEN** the step `gate-38612817613` on dev, for the commit `4f2a9c1`, is recorded waiting with doer user and the text `https://github.com/WilldanGroup/switchboard-kit/actions/runs/38612817613`
- **THEN** crew raises the card `op/dev/<n>` in wldn-ops's name, a `do` titled "Approve the deploy of 4f2a9c1 to dev at its gate", its one step and its *where* that link, its summary saying the approval at the gate is the word to deploy and nothing else asks for it, with Done, Skip and Later

#### Scenario: A gate whose step names no commit
- **WHEN** the gate's step is recorded with no commit
- **THEN** its card is titled "Approve the deploy to dev at its gate"

#### Scenario: A gate with a why
- **WHEN** the gate's text is its link followed by a `- why:` line
- **THEN** the card's summary gives the why after saying what waits

#### Scenario: A user's step whose words are more than a link
- **WHEN** a step that is the user's says "Open https://example.com and rotate the key"
- **THEN** it is an after-deploy step, and its card is the user's `do` as before

#### Scenario: An agent's step whose words are a link
- **WHEN** a step whose doer is main-ops, held for the user's word, has a link alone as its words
- **THEN** it is no gate: its card is the choice of when, as for every held step

#### Scenario: A gate's link past a step's budget
- **WHEN** the gate's link is longer than a step's words may be
- **THEN** its card's *where* is the link and its one step says "Open the gate at this card's link and approve the deploy there."

### Requirement: A card's document is inline Markdown
A document's substance shown on a crew card beyond its words SHALL be inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an uploaded file or HTML: a record's card carries the record whole so, a proposal's its new units' paragraphs, a batch's the reviewer's summary, a deploy's the kit's release notes, a step's card the step's words when nothing else on it holds them whole. The only artifacts a crew card carries SHALL be such a picture, such Markdown, a list as text (a landing's units, a deploy's steps, a proposal's change), a link as a `url` artifact (sluice's pull request, a batch's reading), and a step's commands as action steps.

#### Scenario: A document's substance on a card
- **WHEN** crew raises record 32's card
- **THEN** its one artifact is the record as Markdown, its lines the record's text, and no file is attached

#### Scenario: A card with nothing to show
- **WHEN** crew raises a landing card
- **THEN** its artifacts are the units that land as text and, when sluice opened one, the pull request's link, and it carries no reading session
