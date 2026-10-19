## ADDED Requirements

### Requirement: A stage begins only when its agent takes its prompt
When crew starts a stage in a slot (construct, code, verify or merge of a unit, a fix, or a fix's merge), it SHALL send the stage's prompt only once the slot's new agent is ready for input: herdr reports it idle or done, it waits on no question in its pane, and herdr names its session. The stage SHALL begin only when the agent's transcript shows that Claude received the prompt after crew sent it, within a short time. Text typed into a pane and not submitted SHALL never be a stage's state.

#### Scenario: The prompt is taken
- **WHEN** `crew unit run a code` starts a fresh agent in a's slot, and the agent's transcript shows `/opsx:apply a` received moments after crew sent it
- **THEN** the command says the slot has a in code, records the stage's start, and owes its end, having sent the prompt once

#### Scenario: The agent never becomes ready
- **WHEN** a fix's fresh agent stays on a question in its pane, and never becomes ready for input within the time crew waits
- **THEN** nothing is typed into its pane, and the command fails saying the fix's stage never started because its agent was waiting on a question

### Requirement: A stage's prompt not taken is sent once more
When the agent's transcript does not show the stage's prompt received within the time, and the agent sits idle or done, crew SHALL clear what was left typed in the agent's input and send the prompt once more, and read the transcript again. crew SHALL never send a prompt again, or press anything in the pane, while the agent is working.

#### Scenario: The prompt is left typed
- **WHEN** `crew unit run a code` sends the prompt and the agent's transcript shows nothing received within the time, while the agent sits idle
- **THEN** crew clears the agent's input, sends the prompt once more, and, when the transcript then shows it received, records the stage's start as for a prompt taken at once

### Requirement: A stage whose prompt is not taken never started
When the second sending is not taken either, or the agent never becomes ready for input, crew SHALL leave nothing typed in the pane, record the stage's start as refused with the reason, owe no end for it, and fail, saying the stage never started and how to run it again. When crew cannot read whether the prompt was taken, it SHALL send nothing more, record the start as refused naming what it could not read, and fail.

#### Scenario: The second sending is not taken either
- **WHEN** neither sending of a's code prompt shows in the agent's transcript within the time
- **THEN** the agent's input is cleared, the command fails saying a's code stage never started and to run `crew unit run a code` again, the run record holds the start as refused, and `crew unit wait a` finds no stage owed

#### Scenario: crew cannot read whether it was taken
- **WHEN** a merge stage's prompt is sent, and the agent's transcript cannot be read, or the agent is working while its transcript shows no prompt received
- **THEN** the prompt is not sent again and nothing is pressed in the pane, and the command fails naming what crew could not read
