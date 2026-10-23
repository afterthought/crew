## ADDED Requirements

### Requirement: Every dock takes a word to its item's agent
Every dock SHALL end with a one-line field for a word to the item's agent, a Send control, and a line naming the agent it goes to and saying that a card is answered on the rail. A word SHALL be at most 1000 characters. A dock opened from a page read from disk SHALL say that a word is sent only from the served board, and SHALL send nothing.

#### Scenario: A unit's dock
- **WHEN** the user opens unit a's dock, a in bolt tenant-environments held by swb-1
- **THEN** the dock ends with a field and Send, naming swb-1-conductor as who the word goes to and saying that a card is answered on the rail

#### Scenario: Opened from disk
- **WHEN** the page is opened from a file on disk and the user opens a dock
- **THEN** the dock says a word is sent only from the served board, and its field sends nothing

### Requirement: A word goes to the agent its item's kind names
The agent a dock's word goes to SHALL be decided from the item's kind: a bolt, a unit or chore, or a fix to the conductor of the team holding its bolt; a proposal or a batch to the partition's planner; a signal or a record to its design agent; a landing, a deploy or an operation to its main-level ops; and a team, a subscription, a partition, or a bolt, unit or fix no team holds, to the partition's operator.

#### Scenario: Each kind's agent
- **WHEN** the page is written for wldn with a held bolt of swb-1 with a unit and a fix, a planned bolt with no team, a proposal, a signal, a landing, a deploy, an operation, a team and a subscription
- **THEN** the bolt, unit and fix go to swb-1-conductor, the proposal to wldn-planner, the signal to wldn-design, the landing, deploy and operation to wldn-ops, and the planned bolt, the team and the subscription to wldn-operator

### Requirement: A word reaches its agent as the user's tell from the board, naming the item
Sending a word SHALL post it, with the partition, the item's key and the agent, to the page's own address, whose listener hands it to `crew tell --board` on its standard input. crew SHALL check it and tell the agent `[crew tell from <user>@board] (on <kind> <name>) <text>`, `<user>` being the user the listener runs as, and record the tell with its length and never its text. On delivery it SHALL print `sent to <agent>` and exit zero.

#### Scenario: A word on a unit
- **WHEN** the listener running as chuck pipes `{"label": "wldn", "key": "unit:a", "to": "swb-1-conductor", "text": "Keep the zone check"}` to `crew tell --board`
- **THEN** swb-1-conductor is prompted with `[crew tell from chuck@board] (on unit a) Keep the zone check`, the command prints `sent to swb-1-conductor`, and the run record holds a tell of 31 characters, the length of what was typed after the mark, and not the words

#### Scenario: The agent reads it as the user's
- **WHEN** the conductor's transcript holds that word and it captures a signal from its words
- **THEN** the signal is asserted by the user

### Requirement: A word crew cannot deliver is said in the tell's words
When the tell itself is refused, its agent not up, waiting on a question in its pane, or on a host that does not answer, `crew tell --board` SHALL type nothing and exit non-zero, saying why on standard error in the tell's own words.

#### Scenario: An agent waiting on a question
- **WHEN** a word for swb-1-conductor is posted while swb-1-conductor waits on a question in its pane
- **THEN** nothing is typed, and the command exits non-zero saying swb-1-conductor is waiting on a question in its pane and nothing was sent

### Requirement: A word not of the board's form is refused
`crew tell --board` SHALL type nothing and exit non-zero, saying why on standard error, when the posted word is not one JSON object holding the partition, key, agent and text as strings; names no partition crew knows; has a key of no kind a dock has; names an agent its item's kind does not go to in that partition; or has a text that is empty, longer than 1000 characters or more than one line.

#### Scenario: An agent the kind does not go to
- **WHEN** a word on `proposal:4` is posted for swb-1-conductor
- **THEN** nothing is typed, and the command exits non-zero saying a word on a proposal goes to wldn-planner

#### Scenario: A word of two lines
- **WHEN** the posted text holds a line break
- **THEN** nothing is typed, and the command exits non-zero saying a word from the board is one line

### Requirement: The dock says what became of the word
After Send the dock SHALL say what the listener answered: on delivery, its words, such as `sent to swb-1-conductor`, and the field emptied; otherwise the listener's words, which are crew's refusal, with the word left in the field. When the listener does not answer, or answers with no words, the dock SHALL say the board's listener did not answer and nothing was sent. Send SHALL be disabled while a word is on its way.

#### Scenario: Delivered
- **WHEN** the user sends a word from unit a's dock and the listener answers 200 with `sent to swb-1-conductor`
- **THEN** the dock says `sent to swb-1-conductor` and the field is empty

#### Scenario: Refused
- **WHEN** the listener answers with crew's words that swb-1-conductor is waiting on a question in its pane
- **THEN** the dock shows those words, and the word stays in the field to send again

#### Scenario: No listener
- **WHEN** the post gets no answer
- **THEN** the dock says the board's listener did not answer and nothing was sent

### Requirement: A word from the board answers nothing
Words that reached an agent only in a tell from `<user>@board` SHALL NOT be taken as the user's words for landing a bolt, answering a batch or settling a record in a pane. crew SHALL refuse each, recording nothing, and say the words came from the board, which answers nothing, and where the user answers instead. The same words typed in the pane, or told from `<user>@<host>`, SHALL still be the user's.

#### Scenario: A landing asked from the board
- **WHEN** the user sends "Land bolt y" from bolt y's landing dock, and swancloud-ops runs `crew bolt submit y --excerpt "Land bolt y"`
- **THEN** nothing is submitted, and the command says the words came from the board, which answers nothing, and the user lands a bolt on its card or in the pane

#### Scenario: A batch answered from the board
- **WHEN** the user sends "Batch 14 is fine" from a dock, and the planner runs `crew card answer batch/14 --excerpt "Batch 14 is fine"`
- **THEN** batch 14 is not answered, and the command says the words came from the board

#### Scenario: Typed in the pane after the board
- **WHEN** the user sent "Batch 14 is fine" from a dock and then typed the same words in the planner's pane
- **THEN** `crew card answer batch/14 --excerpt "Batch 14 is fine"` records batch 14 answered

## MODIFIED Requirements

### Requirement: The page stays one self-contained file
With the board view and the dock, the page SHALL still be one file that holds its own data, style and script and loads nothing: no font, script, style or image from anywhere. The one request it SHALL make is a dock's word, posted to the page's own address when the user sends it. It SHALL hold none of the mockup's sample data. Every text it shows from the state, in the lanes and in a dock, and every answer to a word, SHALL be set as text, never as markup.

#### Scenario: Offline
- **WHEN** the page is opened from disk with the network off
- **THEN** the board view and the lineage view draw in full and the browser makes no request

#### Scenario: A dock of typed words
- **WHEN** a signal's assertion holds `</script><b>here</b>` and the user opens its dock
- **THEN** the dock shows those characters as they are, and the page's data block is not ended by them

#### Scenario: Only the word is posted
- **WHEN** the served page is opened, a dock is opened, and a word is sent
- **THEN** the page's only request is one post to its own address's `word`, carrying the partition, key, agent and text
