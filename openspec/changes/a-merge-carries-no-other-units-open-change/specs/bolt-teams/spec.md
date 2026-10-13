## ADDED Requirements

### Requirement: A merge carries no other unit's open change
crew SHALL refuse a unit's or chore's merge before it starts while its branch holds another unit's change of the plan open that its bolt does not hold archived, naming each such change, and saying to take out of the branch the work of a unit that comes after the merging one and to merge any other first. The merging unit's own change, a change the bolt holds archived and a change no unit of the plan has SHALL NOT count.

#### Scenario: A dependency holding its dependent's work
- **WHEN** unit `s`'s branch holds unit `d`'s change open, `d` comes after `s`, and the bolt does not hold `d`'s change archived
- **THEN** `crew unit run s merge` is refused, naming `d` and saying to take its work out of `unit/s`

#### Scenario: A unit it does not come after
- **WHEN** a chore's branch holds unit `x`'s change open, and the bolt does not hold it archived
- **THEN** `crew chore run <chore> merge` is refused, saying to merge `x` first

#### Scenario: A dependent's place holding what it took
- **WHEN** unit `d`'s place took `s`'s work, and `s` has since merged with its change archived on the bolt
- **THEN** `d`'s merge is not refused for it

#### Scenario: A change main has long held open
- **WHEN** every branch holds a change open that main has held since before archives, which no unit of the plan has
- **THEN** no merge is refused for it
