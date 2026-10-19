## ADDED Requirements

### Requirement: A deploy waiting at its gate has the user's do card with the gate's link
A step that is the user's whose words are one link alone SHALL be read as a deploy waiting at its gate. Its card, keyed `op/<env>/<n>` and raised by crew in main-level ops's name as every step's card is, SHALL be a `do` asking the user to approve the deploy at its gate, naming the environment and, when the step names one, the commit; its one step and its *where* SHALL be the gate's link, and it SHALL say the approval at the gate is the word to deploy.

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
