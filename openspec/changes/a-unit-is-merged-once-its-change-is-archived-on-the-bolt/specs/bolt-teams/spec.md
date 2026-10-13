## ADDED Requirements

### Requirement: A unit carried onto its bolt keeps its own merge
A unit whose change its bolt holds open, carried there inside another unit's merge, SHALL NOT read merged: `crew status` SHALL name it carried by another's merge, its own merge owed, on its slot's line or a line of its own. Its merge stage SHALL make its place again from the bolt when it is gone, and the merge SHALL archive its change there and deliver once the bolt holds it archived.

#### Scenario: Named in the team's status
- **WHEN** unit `d`'s change is open on its bolt, carried there in `s`'s merge, every task ticked, and its slot holds it
- **THEN** `crew status` shows `d  verify 2/2  carried by another's merge, its own merge owed`

#### Scenario: Its place gone
- **WHEN** `d`'s place and branch were removed, and the conductor runs `crew unit run d merge`
- **THEN** `d`'s place is made again on `unit/d` from the bolt, its merge archives the change there and submits, and the stage delivers once the bolt holds the change archived

## MODIFIED Requirements

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once its bolt holds its change archived or it has landed, or no plan has it, never while the bolt holds its change open; a fix's once it has merged into its bolt, or no plan has its bolt. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`.

#### Scenario: A dropped bolt
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** `bolt/<bolt>` is gone from swb-2's host, and so are the places, branches and slots of the bolt's units and fixes

#### Scenario: A leftover from before
- **WHEN** a kit checkout has the worktree of a bolt that no plan has, and a place of a unit that has merged, which no slot holds
- **THEN** the next `crew status` of a team building in that checkout removes both, with their branches

#### Scenario: A bolt branch crew did not make
- **WHEN** a kit checkout has a `bolt/` branch with no mark of crew's, of a bolt no plan has
- **THEN** crew leaves it as it is

#### Scenario: The host does not answer
- **WHEN** a bolt is dropped while its team's host cannot be reached
- **THEN** the plan changes, crew says the host's worktrees were not removed, and the team's next read removes them

#### Scenario: Work dropped with commits of its own
- **WHEN** a removed branch holds commits that neither main nor its bolt has
- **THEN** crew says the commit the branch was at

#### Scenario: A unit carried onto its bolt
- **WHEN** a unit's change is open on its bolt, carried there inside another unit's merge, and the team is read
- **THEN** its worktree, its branch and its slot are kept
