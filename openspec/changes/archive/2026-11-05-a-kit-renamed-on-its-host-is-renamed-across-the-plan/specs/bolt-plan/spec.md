## ADDED Requirements

### Requirement: A kit renamed on its host is renamed across the plan in one act
`crew kit rename <old> <new>` SHALL rewrite the `Repo` of every Bolt and Unit record of the partition's plan that names `<old>`, by its name or its forge address, to `<new>` as given. The rewrite SHALL be one commit with one `kit.rename` entry, and SHALL change nothing else of the plan: no Goal, Intent or Source, and no record added, removed or moved. It SHALL append no request for a runner, and launch, retry or drop nothing. It SHALL be refused, with nothing written, in any of these cases:
- `<old>` is no kit of the partition, neither its plan's nor its landings';
- the partition's main-level host keeps no repository by `<new>` in its spaces, or still keeps one by `<old>`. The refusal names the host and what its spaces keep;
- `<new>` is the name of one of the partition's bolts;
- the plan it leaves fails `recfix --check` or crew's own rules;
- the hosts file can't be read.

A proposal MAY hold it, applied as any of its commands, and the user MAY run it at a shell. The planner's direct run SHALL be refused naming `crew plan propose`, and any other agent crew started SHALL be refused naming the planner.

#### Scenario: The user renames tailrace
- **WHEN** madswan's plan names `tailrace` in 21 records and `flywheel-cloud` in 2, deneb's spaces keep `agentplot/timber` and nothing by `tailrace`, and the user runs `crew kit rename tailrace timber`
- **THEN** the 21 records name `timber`, the other 2 still name `flywheel-cloud`, every other field of every record is as it was, and one commit holds the change

#### Scenario: Not renamed on its host
- **WHEN** deneb's spaces still keep `agentplot/tailrace` and the user runs `crew kit rename tailrace timber`
- **THEN** it is refused naming deneb and `agentplot/tailrace`, and the plan is unchanged

#### Scenario: A new name the host does not keep
- **WHEN** deneb's spaces keep no repository by `timber`
- **THEN** `crew kit rename tailrace timber` is refused naming deneb and `timber`, and the plan is unchanged

#### Scenario: The new name is a bolt's
- **WHEN** madswan's plan holds a bolt named `timber`
- **THEN** `crew kit rename tailrace timber` is refused naming the bolt, and the plan is unchanged

#### Scenario: A kit only its landings name
- **WHEN** madswan's plan names no `tailrace` record and its run record holds a `bolt.land` of `tailrace`
- **THEN** `crew kit rename tailrace timber` renames no record and writes its `kit.rename` entry, and madswan's kits name `timber`

#### Scenario: The planner proposes it
- **WHEN** madswan-planner runs `crew kit rename tailrace timber`
- **THEN** it is refused naming `crew plan propose`, and a proposal holding `kit rename tailrace timber` is checked and, on the user's approval, renames the records in the approval's commit

#### Scenario: Another agent runs it
- **WHEN** madswan-ops runs `crew kit rename tailrace timber`
- **THEN** it is refused naming the planner, and the plan is unchanged

#### Scenario: A started bolt's kit
- **WHEN** `you-sign-in-to-staging` is started, its unit `one-seam-turns-every-credential-into-a-principal` has merged into its branch, and the user renames `flywheel-cloud` to `boomdrive-cloud`
- **THEN** the bolt and its unit name `boomdrive-cloud`, the bolt keeps `Path: flume`, `requests.rec` is unchanged with no request appended, and the unit reads merged as the runner carried it

#### Scenario: The command at a shell
- **WHEN** the user runs `crew kit rename` on the stubs, and the planner proposes a rename the user then approves
- **THEN** the user's run writes one commit and its entry, the planner's direct run is refused, and the proposal's approval renames the records

### Requirement: What crew recorded under a kit's former name is read under its name now
Wherever crew reads a kit's name from a record it never rewrites, it SHALL read the name through the partition's `kit.rename` entries, not refused, in the order they were written. Each entry renames its old name, by name or forge address, to its new. A name no rename names SHALL be read as written. The records this covers are:
- a launch's `Repo` in `requests.rec`;
- an entry's `Repo` in the run record;
- the kit in a fix of main's work, `fix/main/<kit>/<name>`;
- the kit in a card key, `land/<kit>` or `record/<kit>/<n>`;
- the repository of a source that names a decision record.

The renames SHALL be read in the same read of the run record as the landings, once per tip. A partition's kits SHALL be its plan's and its landings' names read so, each once. `crew bolts`, the board, the agents' views, the page, and a kit's landings and its deploys SHALL name a kit by its name now. `requests.rec`, the run record, `proposals.rec`, signals and `moves.rec` SHALL never be rewritten for a rename.

#### Scenario: Landings under the old name
- **WHEN** madswan's run record holds two `bolt.land` entries with `Repo: tailrace` and, after them, a `kit.rename` of `tailrace` to `timber`
- **THEN** madswan's kits name `timber` once and never `tailrace`, and the page's fleet shows `timber`'s last landing from those entries

#### Scenario: A launch made before the rename
- **WHEN** request 1 launched `one-seam-turns-every-credential-into-a-principal` with `Repo: flywheel-cloud`, and `flywheel-cloud` has been renamed `boomdrive-cloud`
- **THEN** request 1 counts among `boomdrive-cloud`'s launches where crew reads where that kit's work runs

#### Scenario: A rename undone
- **WHEN** the run record holds a rename of `a` to `b` and, after it, one of `b` to `a`
- **THEN** both `a` and `b` read `a`

#### Scenario: A chain of renames
- **WHEN** the run record holds a rename of `a` to `b` and, after it, one of `b` to `c`
- **THEN** both `a` and `b` read `c`

#### Scenario: A fix of main under the old name
- **WHEN** the fix of main `fix/main/tailrace/x` waits held and `tailrace` has been renamed `timber`
- **THEN** it is shown on `timber`'s landings row

#### Scenario: A deploy's landings
- **WHEN** a `bolt.land` under `tailrace` lies in an environment's deploy range of `timber`
- **THEN** the deploy carries that landing as `timber`'s

#### Scenario: A source in a renamed repository
- **WHEN** a unit's source names `agentplot/tailrace:docs/adr/0017` and `tailrace` has been renamed `timber`
- **THEN** a proposal resting on it reads record 0017 in the checkout deneb keeps of `timber`

#### Scenario: The board after a rename
- **WHEN** madswan's landings are under `tailrace` and the run record holds its rename to `timber`
- **THEN** the board and the agents' views name `timber` alone, with the views' keys as before

### Requirement: A command given a kit's former name writes its name now
A plan command that names a kit by `--repo`, `bolt new`, `unit add` and `chore add` among them, SHALL write the kit's name now where the partition's renames renamed the name it was given, and SHALL say so in its answer. A proposal's `Do` applied after a rename SHALL write the new name, the `Do` itself unchanged. Where the main-level host keeps a repository by a former name again, a command naming that name SHALL be refused, naming the rename, since crew could not tell the two kits' records apart.

#### Scenario: A proposal approved after the rename
- **WHEN** proposal 400 holds `unit add x "…" --repo tailrace`, the user renames `tailrace` to `timber`, and then approves 400
- **THEN** `x` is queued in `timber`, the approval says `tailrace` is now `timber`, and proposal 400's `Do` still reads `--repo tailrace`

#### Scenario: A former name kept again
- **WHEN** `tailrace` was renamed `timber` and deneb's spaces now also keep a new `agentplot/tailrace`
- **THEN** `crew bolt new y "…" --repo tailrace` is refused naming the rename, and the plan is unchanged
