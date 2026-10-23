## ADDED Requirements

### Requirement: A split bolt takes no merge
A bolt is split when its host's own `bolt/<bolt>` has a tip whose policy names a remote for the bolt and the bolt's branch on that remote, read after a fetch, does not hold that tip. A unit's, chore's or fix's merge into a split bolt SHALL be refused before anything is submitted, naming both commits, the merges the remote's copy lacks, and the bolt's landing as the way on. A landing SHALL NOT be refused for it.

#### Scenario: A merge into a split bolt
- **WHEN** a unit's merge starts on bolt `b`, whose host's tip names `origin` for it, while `origin`'s `bolt/b`, after a fetch, stands at an older commit that lacks two merges the host holds
- **THEN** the merge is refused before anything is submitted, naming the host's tip, `origin`'s commit, the two merges, and `crew bolt submit b` as the way on, whose push makes the two one

#### Scenario: A chore's or a fix's merge into a split bolt
- **WHEN** a chore's merge stage or `crew fix merge` starts on that bolt
- **THEN** it is refused in the same words, naming the chore or the fix

#### Scenario: GitHub's copy holds the host's tip
- **WHEN** a merge starts on a bolt whose host's tip names `origin`, and `origin`'s `bolt/b` is that tip or holds it
- **THEN** the merge starts as before

#### Scenario: A bolt whose tip names no remote
- **WHEN** a merge starts on a bolt made on its host before gives went through sluice, whose tip's policy names no remote for it
- **THEN** the merge starts as before and nothing is fetched for it

#### Scenario: GitHub has no copy
- **WHEN** a merge starts on a bolt whose host's tip names `origin` while `origin` has no `bolt/b`
- **THEN** crew refuses nothing, and sluice's own refusal of a submission to a bolt its remote lacks stands, dropping nothing

#### Scenario: GitHub's copy cannot be read
- **WHEN** a merge starts on a bolt whose host's tip names `origin` and the read or fetch of `origin`'s `bolt/b` fails
- **THEN** the merge is refused, naming the bolt and git's words, since crew cannot tell whether it is split
