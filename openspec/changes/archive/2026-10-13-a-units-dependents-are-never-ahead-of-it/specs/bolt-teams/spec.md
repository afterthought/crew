## ADDED Requirements

### Requirement: Ahead in a bolt is its merge order
Where crew tells a unit of the units ahead of it in its bolt, in a code stage's note of overlapping Touches and in the forecasts on a conductor's wait, a unit `a` SHALL be ahead of `b` when `b` comes after `a` through `After` at any depth, or, when neither comes after the other, when the plan lists `a` first. A unit's dependent SHALL never be named ahead of it, nor a unit forecast against one that comes after it.

#### Scenario: A dependent listed first
- **WHEN** unit `d` comes after unit `s`, the plan lists `d` before `s`, and their Touches overlap
- **THEN** `s`'s code is told nothing of `d`, and `d`'s code is told that `s` is ahead of it and not merged

#### Scenario: A forecast between them
- **WHEN** the conductor's wait finds `d`'s and `s`'s heads in conflict
- **THEN** the forecast reaches `d`, against `s`, and no `After` is written, since `d` already comes after `s`

#### Scenario: At any depth
- **WHEN** `c` comes after `b`, which comes after `a`, and the plan lists `c` first
- **THEN** `a` is ahead of `c`, and a forecast between them reaches `c` with no `After` written

#### Scenario: Units neither comes after
- **WHEN** units `x` and `y` share no `After`, and the plan lists `x` first
- **THEN** `x` is ahead of `y`
