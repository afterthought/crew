## ADDED Requirements

### Requirement: A bolt carrying another bolt's work does not land
Another bolt's work is a commit on that bolt's first-parent line beyond main, read from branches as GitHub holds them. `crew bolt submit` SHALL submit nothing of a bolt whose head, read after a fetch, holds such a commit that main lacks and that is off its own first-parent line, naming each bolt and its landings. The bolt whose work was carried SHALL NOT be held for it. A head crew can't read SHALL be refused, naming why.

#### Scenario: A bolt built on another bolt's landing is refused at its submit
- **WHEN** bolt `popover`'s branch on GitHub holds bolt `deleting`'s landing `f5e67f35`, which main lacks, and ops runs `crew bolt submit popover`
- **THEN** nothing of `popover` is submitted and sluice is asked for nothing, and the refusal names bolt `deleting` and its landing `f5e67f3`, recorded with no head

#### Scenario: The bolt whose work was carried lands
- **WHEN** `popover` carries `deleting`'s landing, and ops runs `crew bolt submit deleting`
- **THEN** `deleting` is not refused for it, since it holds nothing on `popover`'s first-parent line

#### Scenario: Main holds the carried work
- **WHEN** `deleting` has landed on main, and ops runs `crew bolt submit popover`
- **THEN** `popover` carries nothing main lacks, and is submitted as any bolt

#### Scenario: What a head carries can't be read
- **WHEN** the fetch `crew bolt submit` makes to read what the head carries fails
- **THEN** nothing is submitted, and the refusal says git's words

### Requirement: A merge carries no other bolt's work
crew SHALL refuse a unit's, chore's or fix's merge into its bolt before its submission while its branch holds another bolt's landing that main and its own bolt lack, read after one fetch. The refusal SHALL name that bolt and its landings, and say to take that work out of the branch, building it on its own bolt where it lives, or to merge once main holds that work.

#### Scenario: A unit's branch holds another bolt's landing
- **WHEN** `unit/pop` of bolt `popover` was rebased onto bolt `deleting`'s landing, which main and `bolt/popover` lack, and its conductor runs `crew unit run pop merge`
- **THEN** the merge is refused before its submission, naming bolt `deleting`, its landing, and the way on

#### Scenario: A unit built on its own bolt alone merges
- **WHEN** `unit/own`'s branch holds only its own commits on `origin/bolt/popover`
- **THEN** its merge is not refused for another bolt's work

### Requirement: A place's work starts at its own bolt alone
A unit's place SHALL be cut from its own bolt on GitHub after a fetch, whatever the slot that builds it last built. The coder's brief SHALL name its bolt as the one its branch tracks, and say no other bolt's branch is its to rebase onto, merge, test against or take work from. A unit moved to another bolt SHALL be rebased from the bolt it leaves onto the one it joins, each read where it lives after a fetch.

#### Scenario: A slot builds a unit of one bolt, then one of another
- **WHEN** slot `brd-2-unit-1` built a unit of bolt `deleting`, its place holding `deleting`'s landing, and then starts the construct of a unit of bolt `popover`
- **THEN** the second unit's place is cut from `origin/bolt/popover` after a fetch, tracks it, and holds nothing of `deleting`'s landing

#### Scenario: The coder is told its bolt
- **WHEN** crew starts a coder for a unit's stage
- **THEN** its brief names its bolt as the one its branch tracks, `git rev-parse --abbrev-ref @{upstream}`, and says no other bolt's branch is its to build on

#### Scenario: A unit moves off a bolt whose host copy lags
- **WHEN** a unit whose place was cut from GitHub's `bolt/b`, which holds a landing the host's own `bolt/b` lacks, is moved to bolt `cp`
- **THEN** only the unit's own commits go onto `origin/bolt/cp`, and nothing of `bolt/b`'s landing

### Requirement: crew bolts says a bolt carries another bolt's work
`crew bolts` SHALL say under a bolt whose kit's read says it carries another bolt's work that main lacks that its landing is held, naming that bolt and its landings, and SHALL give it in its JSON as `carries`, or why it can't be read as `carries_error`.

#### Scenario: crew bolts shows a bolt carrying another's work
- **WHEN** the kit's read says bolt `y` carries bolt `x`'s landing `f5e67f35`
- **THEN** `crew bolts` shows under `y` "landing: held: carries bolt x's work, its landing f5e67f3, which main lacks", and its JSON gives `carries`
