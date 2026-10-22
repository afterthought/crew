## ADDED Requirements

### Requirement: A brief names nothing of a change's content but what crew reads
No brief crew gives an agent SHALL name a proof list, a task's shape or a design's sections. The construct's brief SHALL say that what a change holds is the kit's, from OpenSpec's schema and the kit's `openspec/config.yaml`, which `/opsx:propose` hands it, and SHALL name of a change only what crew reads: its name, which is the unit's; its tasks' tick boxes; its proposal's `## Touches` block; and its archive at merge. The results section every brief carries SHALL name no proof list.

#### Scenario: Another kit's construct
- **WHEN** crew gives the construct brief to a team whose bolt is of another kit, such as swancloud or switchboard
- **THEN** the brief names no *Proof in dev* list, no *Task notes* section and no shape for a task, and says the change's content is the kit's, from its `openspec/config.yaml` through `/opsx:propose`

#### Scenario: What crew reads stays
- **WHEN** the construct brief is printed for any team
- **THEN** it still says to end the proposal with the `## Touches` block crew reads before code, and to name the change for the unit

#### Scenario: The coder and the results section
- **WHEN** the coder's brief, or any brief's results section, is printed
- **THEN** neither names work that needs dev or a *Proof in dev* list

### Requirement: A crew change's tasks each name their check
crew's `openspec/config.yaml` SHALL hand crew's construct, as rules for `tasks`, that each task is one sentence naming the check in crew's tiers that proves it, with a pointer to its reasoning; that no task is a deploy, a step on a live host or the user's, or work done after the landing; and that the tasks end with the tests the change affects, not the whole suite, which the merge gate runs. Its apply guidance SHALL tell crew's coder to tick a task only once the check it names passes.

#### Scenario: A crew construct asks for the tasks' instructions
- **WHEN** a construct in crew runs `/opsx:propose` and OpenSpec gives it the instructions for `tasks`
- **THEN** their rules say each task names the check that proves it, the tasks end with the tests the change affects, and no task is a deploy or work after the landing

#### Scenario: A crew coder ticks a task
- **WHEN** a crew coder runs `/opsx:apply` on a change
- **THEN** the guidance OpenSpec hands it says to tick a task only once the check the task names passes

#### Scenario: Another kit's agents
- **WHEN** a construct or coder works a change of another kit
- **THEN** OpenSpec hands it that kit's config, and nothing of crew's conventions reaches it

### Requirement: A crew change holds no proof list
crew's `openspec/config.yaml` SHALL hand crew's construct, as rules for `design`, that a task's full brief goes under *Task notes*, headed by the task's number; that a design holds no proof list of any name; and that *After deploy* lists only the steps no check can be code, each saying why, with its environments and its doer. As a rule for `specs`, it SHALL say that a scenario no check proves is a check the change adds (`docs.6`).

#### Scenario: A scenario no check proves
- **WHEN** a crew construct writes a scenario that no existing check proves
- **THEN** its tasks add the check that proves it, and its design lists no hand step for it

#### Scenario: Nothing to do after a deploy
- **WHEN** a crew change has no step that only a person or a live host can do
- **THEN** its design's *After deploy* says none and why, and it has no *Proof in dev* or *Proof on real work* section

### Requirement: A team reports each result on a line of its own, with one glyph
Whenever the conductor, ops, construct, coder or verify reports the results of tests, checks or proofs, it SHALL list them first, before any prose, one bullet per suite, check or proof: ✅ passed, with its counts where the tool gave them; ❌ failed, with how many failed and one line on why; ⏳ not yet run, or still running. It SHALL NOT state a result only in a sentence, nor fold several into one bullet. It SHALL use the same list in a file or a message that carries results.

#### Scenario: A bolt's verification after a merge
- **WHEN** ops reports the bolt's verification and two of its tests failed
- **THEN** its message opens with one ❌ bullet naming the suite, the two failures and one line on why, and only then says what it would do

#### Scenario: A submission still running
- **WHEN** ops reports on a submission to the bolt whose checks sluice is still running
- **THEN** its report opens with one ⏳ bullet naming the submission and what it waits on

#### Scenario: The conductor passes results on
- **WHEN** the conductor tells the user what ops or a verify reported
- **THEN** it shows that agent's list as it is, first, and then says in plain English what it would do about each ❌

#### Scenario: A construct's validation
- **WHEN** a construct agent ends after `openspec validate <unit>` passed
- **THEN** its final message opens with a ✅ bullet for that validation

#### Scenario: Nothing passed in a sentence
- **WHEN** every suite a coder ran passed
- **THEN** its summary still lists each suite with ✅ and its counts, and never says only "the tests all pass"

## REMOVED Requirements

### Requirement: A team reports results as one glyph per line
**Reason**: Its scenario *Proof in dev* has ops work a unit's *Proof in dev* list, which record 0025 takes out of every change, and OpenSpec drops a scenario only with its requirement.
**Migration**: The same requirement stands as "A team reports each result on a line of its own, with one glyph", its other scenarios unchanged and *A submission still running* in place of *Proof in dev*.
