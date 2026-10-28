## ADDED Requirements

### Requirement: A landing stopped in ops's pane is recorded as the user's words
When the user's own words in main-level ops's pane stop a bolt's landing, ops SHALL run `crew bolt leave <bolt>... --excerpt "<the user's words>"`. Before recording anything, crew SHALL read the words in the caller's own live session transcript as it reads a landing said in ops's pane, and SHALL refuse in the same cases, recording no stop. A stop SHALL be recorded on each bolt as a `bolt.leave` entry naming its head, the caller, its session, the transcript record the words were read from and the words' length, and holding none of the words (`record.3`), and crew SHALL raise the bolt's kit's landings card. A stop SHALL end when the user ticks the bolt on a send of that card, when ops lands it on the user's words, or when its head moves.

#### Scenario: Stopped in the pane
- **WHEN** the user types "Hold the phone bolt, don't land it yet" in swancloud-ops's pane, and ops runs `crew bolt leave builds-reach-the-phone --excerpt "Hold the phone bolt, don't land it yet"`
- **THEN** a `bolt.leave` entry on `bolt/builds-reach-the-phone` is recorded with its head, the transcript record and the words' length, and none of the words, and `land/swancloud` is raised showing it unticked as left

#### Scenario: Words that are not the user's
- **WHEN** ops runs `crew bolt leave builds-reach-the-phone --excerpt "<words>"` with words only another agent's tell holds
- **THEN** crew refuses, naming the tell, and records no stop

#### Scenario: Landed on their words later
- **WHEN** the user later tells ops to land the bolt, and ops runs `crew bolt submit builds-reach-the-phone --excerpt "<their words>"`
- **THEN** the stop ends, and the bolt is no longer left
