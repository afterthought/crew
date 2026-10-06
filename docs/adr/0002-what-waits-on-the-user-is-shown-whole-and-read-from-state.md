# What waits on the user is shown whole, and read from state

- Status: accepted
- Date: 2026-10-06
- Deciders: the user, through swancloud-operator-mac-studio, in their words; swancloud-design
- Sources: the user's message of 2026-10-06; `plugin/roles/conductor.md` (review), `planner.md` (proposals), `operator.md` (where things stand); `openspec/changes/plan-proposals/design.md` ("How a proposal reads"); `openspec/explorations/findings-to-design/proposal.md` section 5, the row on Flywheel Next's rail; `plannotator-tui`'s usage (`herdr open [file.md | folder]`)

## Context and problem statement

The user said three things. At a unit's review the conductor opens only the change's proposal in plannotator, and the user wants to see all of its files. Agents mention the planner's proposals to the user by number, sometimes with a summary, rarely with the proposal itself, where earlier the user saw the sequence of adds and drops. And decisions reach the user from several panes with nothing listing them: "if I could have one place that showed me the list and I could work down through that, it would make it a lot easier", asking for "the simplest thing we can do with our current implementation", noting that such a list "needs to have them go stale".

What is built: a unit in review has its change in `<kit>/places/<unit>/openspec/changes/<unit>/`, and plannotator-tui opens a file or a folder. A proposal is a record on the flywheel's branch that `crew plan proposed <n>` renders in plain words, without the commands it holds. Units' stages are read from the kits, proposals from the branch, and verify reports are files on the team's host. The findings-to-design proposal already decided that Flywheel Next's rail, decisions derived from active states, is in crew `crew plan proposed` and, once built, `crew agenda`.

## Decision drivers

- Nothing kept by hand: every stage is read from the kits and the branch, so a list of what waits on the user must be derived the same way, or it is the thing that goes stale.
- The user decides from the thing itself, not a pointer to it: the words of a proposal, the whole of a change.
- The simplest thing that works today, leaving room for the agenda's design lane and the lineage page, which are already designed.

## Considered options

For the list:

1. A read command that derives what waits on the user from the plan, the proposals, the kits and the team's host, nothing written to make or clear an item.
2. A kept list: a record on the flywheel's branch that agents write to when they wait on the user and clear when answered, numbered as Flywheel's rail is.
3. The operator agent as the one place, answering in chat.

## Decision outcome

### Shown whole

- **A review opens the whole change.** At review the conductor opens the change's folder, `plannotator-tui herdr open <kit>/places/<unit>/openspec/changes/<unit>/`, once, so the proposal, design, specs and tasks are all before the user; it no longer opens the proposal alone and the rest one at a time.
- **A proposal is shown, never only named.** Any agent that puts a proposal before the user, the planner, a conductor, the operator agent, shows what `crew plan proposed <n>` prints, in its pane or opened beside it, and never the number alone. A number is a reference to put after the words.
- **The rendering shows the commands.** Under each change's plain words, `crew plan proposed <n>` prints the command as it will run on approval, so the sequence of adds, moves and drops is visible as it was when the planner wrote the plan directly.

### One list, read from state

Option 1. `crew waiting [--label <label>]` prints, from any host, everything that waits on the user, each with what it is and the command or pane that answers it, in this order:

| what | read from | it leaves the list when |
|---|---|---|
| an open proposal, with whose agreement it still needs | `proposals.rec` on the flywheel's branch | it is approved or dropped |
| a unit in review, with its change's folder | the unit's stage, from the kit | it is approved, or construct runs again |
| a unit in verify whose report is newer than its branch's head, with the report's path and its conductor | the team's host: the unit's stage, the reports folder, the branch | code commits again, or the unit merges |
| a bolt whose every unit has merged and that has not landed, with its team and the main-level ops that lands it | the plan and the kit | it lands |

A host that does not answer is named, as `crew bolts` names one. Items have no numbers of their own: each is named by its id (proposal 3, unit x, bolt y), and nothing is written to put an item on the list or take it off. That is how items go stale: the moment an answer is recorded, in the plan, the branch or the kit, the item is gone.

The operator workspace gets a `waiting` tab beside `flow`, showing the list and refreshing it, and the operator agent answers "what waits on me" from `crew waiting`. The conductor's one-line tell to the operator agents when it stops on the user stays: it covers a question the user must answer in the conductor's pane, which no state records and which the list therefore cannot carry.

### Consequences

- Two units in crew: showing decisions whole (the conductor's, planner's and operator's briefs, and the rendering), and `crew waiting` with its tab.
- When `curation-and-agenda` lands, the agenda's design-lane items join the list, read from `agenda.rec`; when `blocking-findings` lands, held units join it. The lineage page is the same list with its history.
- A question a stage stops on for the user is still in a pane, carried by a tell. If that proves to be the common case, it is the one item that needs a record, and the agenda's design lane is where it would go.

## Pros and cons of the options

### Option 1: derived from state

- Good: nothing to write or clear, so nothing goes stale; it is `crew bolts` and `crew plan proposed` read with one question in mind; it is Flywheel's rule for its rail, decisions derived from active states.
- Bad: a decision with no state behind it, such as a question in a pane, cannot be listed.

### Option 2: a kept list

- Good: carries anything, questions included, with stable numbers.
- Bad: every agent must write an entry when it waits and clear it when answered, and a missed clear is exactly the stale item the user named; it duplicates what the plan and the proposals already say; the agenda, already designed, is that record for what curation and the user put before each other.

### Option 3: the operator agent

- Good: exists today.
- Bad: an answer in chat is not a list to work down; the agent reads the same state the command would, less reliably.
