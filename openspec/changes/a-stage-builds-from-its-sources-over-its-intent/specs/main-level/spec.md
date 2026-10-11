## ADDED Requirements

### Requirement: A signal names where what its words point at lives
An agent recording a signal whose words point at something made elsewhere (another conversation, a page or prototype, an artifact, files in another repo, a spike) SHALL find it and name in the signal's sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a branch, or an artifact's link. A conversation's id alone SHALL NOT stand for what the conversation made. The excerpt SHALL stay the words as said.

#### Scenario: The user pastes a conversation's id
- **WHEN** the user asks the planner for work and pastes the id of a conversation, held in another repo, that wrote the design pages and published the artifact the work rests on
- **THEN** the signal the planner records quotes the user's words, id and all, and its sentence names those pages by repo and path and the artifact by its link

### Requirement: A unit made from a signal names what the signal points at
A unit the planner proposes from a signal, or the design agent queues from one, SHALL name with `--source` what the signal points at, beside the signal itself.

#### Scenario: Work queued from a signal that names a page
- **WHEN** the planner proposes a unit from a signal whose sentence names a page in another repo
- **THEN** the unit's sources are the signal and that page, and the construct's prompt carries both
