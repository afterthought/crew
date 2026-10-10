## MODIFIED Requirements

### Requirement: Any agent crew starts is reached by name
`crew tell <agent> "<text>"` SHALL prompt any agent crew starts, by its name alone, in the host and session where it runs. An agent that is not up SHALL be reported and the command SHALL fail, with nothing sent. An agent waiting on a question in its pane SHALL be reported the same way, naming the wait, and nothing SHALL be typed into the question: a tell is delivered as a prompt the agent receives, never as text that lands in a dialog and is lost. An agent is waiting on a question when herdr reports it blocked, or when it has opened a question or a plan for the user's answer in Claude Code and that call has no answer yet in its session, however the dialog looks on screen. When crew cannot read whether the agent is waiting on a question, it SHALL refuse the same way, naming what it could not read, and type nothing. crew's greetings and notices SHALL be delivered on the same terms.

#### Scenario: A conductor asks the design agent
- **WHEN** swb-1's conductor on the box runs `crew tell wldn-design "<question>"`
- **THEN** the design agent in `wldn-2` receives the question

#### Scenario: The agent is waiting on a question
- **WHEN** `crew tell wldn-ops "<text>"` runs while wldn-ops has a question open in its pane
- **THEN** the command fails, says wldn-ops is waiting on a question in its pane, and nothing is typed there; the sender tells it again once the question is answered

#### Scenario: A question herdr does not see
- **WHEN** wldn-ops has a question open in its pane that herdr reports as idle, and `crew tell wldn-ops "<text>"` runs
- **THEN** the command fails the same way, and nothing is typed there

#### Scenario: The question is answered
- **WHEN** the user answers or dismisses wldn-ops' question, and `crew tell wldn-ops "<text>"` runs again
- **THEN** wldn-ops receives the text as a prompt

#### Scenario: crew cannot read whether a question is open
- **WHEN** wldn-ops opened a question and crew cannot read its session to learn whether it has been answered
- **THEN** `crew tell wldn-ops "<text>"` fails naming what it could not read, and nothing is typed there

#### Scenario: A conductor greeted while it waits on a question
- **WHEN** crew greets a conductor that has a question open which herdr reports as idle
- **THEN** the greeting waits until the question is answered, as it does for one herdr reports blocked, and is then sent once
