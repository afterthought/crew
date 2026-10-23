## ADDED Requirements

### Requirement: A landing said in ops's pane is checked as the user's words before it is submitted
When the word to land is the user's own words in main-level ops's pane, ops SHALL run `crew bolt submit <bolt> --excerpt "<the user's words>"`. Before anything is submitted, crew SHALL look for the words in the caller's own live session transcript, on the host where the command runs, and SHALL go on only when it finds them in a record the session received that it reads as the user's under `signals.5`: typed in the pane, or a `crew tell` from `<user>@<host>`. A later echo of the same words, in a tool's output or a tell, SHALL NOT hide the user's record. crew SHALL refuse the command, submitting nothing and recording no word to land, in each of these cases:
- the words are not in the transcript, or are only in what the agent wrote itself;
- the record holding them is a tool's output, crew's own message, or another agent's tell, which the refusal names;
- crew cannot read the transcript, or cannot tell that it is the live session's.

A landing on the user's words SHALL be recorded on the landing's `bolt.submit` entry, naming the caller, its session, the transcript record the words were read from and the words' length, and holding none of the words (`record.3`); a refusal SHALL record crew's own message alone. Without `--excerpt`, `crew bolt submit` SHALL land on the landing card's approval as before, and its entry SHALL name no transcript record. Landing several bolts on one sentence SHALL take one command per bolt.

#### Scenario: Typed in ops's pane
- **WHEN** the user types "Land crw-5's bolt" in swancloud-ops's pane, and ops runs `crew bolt submit y --excerpt "Land crw-5's bolt"`
- **THEN** the bolt is submitted to main, and the `bolt.submit` entry names the transcript record and the length of the words, and none of the words

#### Scenario: Through the rail's answer command
- **WHEN** the user runs `crew tell swancloud-ops "Land bolt y."` at a shell, and ops runs `crew bolt submit y --excerpt "Land bolt y."`
- **THEN** the bolt is submitted, since a tell from `<user>@<host>` is the user's

#### Scenario: Ops's own words
- **WHEN** ops writes "the user wants bolt y landed" in its own reply and runs `crew bolt submit y --excerpt "the user wants bolt y landed"`
- **THEN** the command is refused, saying the words are not in a record the session received, nothing is submitted and main is where it was

#### Scenario: Words another agent passed on
- **WHEN** swancloud-operator tells ops "The user says land bolt y", and ops runs `crew bolt submit y` with those words
- **THEN** the command is refused, naming swancloud-operator as the one who said them and saying the user lands a bolt on its card or in ops's pane, and nothing is submitted

#### Scenario: The card's approval
- **WHEN** crw-5's conductor tells ops "Land bolt y. The user approved it on Pending You.", and ops runs `crew bolt submit y`
- **THEN** the bolt is submitted as before, and its entry names no transcript record

### Requirement: A landing said in ops's pane closes its card naming the user's words
When a bolt whose landing was submitted on the user's words in ops's pane is closed by `crew bolt land`, crew SHALL close its landing card saying first that it landed on the user's word in ops's pane, with the user's words, then where GitHub's main holds the landing, as any landing's card closes; the run record SHALL keep the close's outcome without the words. A card still waiting on the user SHALL be closed as answered in the conversation, so that Pending You shows it answered rather than only withdrawn. When `crew bolt land` cannot read the words back, because it runs on another host than the submission did, the card SHALL close naming in whose pane and when the word was given, without the words, and the command SHALL say so. A landing on the card's approval SHALL close its card as before.

#### Scenario: The card closes with the user's words
- **WHEN** ops submitted bolt `y` on the user's words "Land crw-5's bolt" in its pane, and runs `crew bolt land y`
- **THEN** `land/y` closes as answered in the conversation, "Landed on the user's word in swancloud-ops's pane, "Land crw-5's bolt"; landed on GitHub's main at `<sha>` (#<n>); …", and the `card.close` entry's outcome holds no words of the user's

#### Scenario: Closed on another host
- **WHEN** bolt `y` was submitted on the user's words on deneb, and `crew bolt land y` runs on mac-studio
- **THEN** `land/y` closes naming swancloud-ops's pane and the time of the word, with no words, and the command says the words are kept on deneb

#### Scenario: Landed on the card
- **WHEN** the user approved `land/y` on Pending You, and ops ran `crew bolt submit y` and `crew bolt land y`
- **THEN** `land/y` closes as it did before this change, naming no pane
