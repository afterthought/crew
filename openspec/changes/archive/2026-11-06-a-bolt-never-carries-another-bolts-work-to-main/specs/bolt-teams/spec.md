## ADDED Requirements

### Requirement: A bolt carrying another bolt's work does not land
Another bolt's work is a commit on that bolt's first-parent line beyond main, read from branches as GitHub holds them. `crew bolt submit` SHALL submit nothing of a bolt whose head, read after a fetch that prunes nothing, holds such a commit that main lacks and that is off its own first-parent line, naming each bolt and its landings. The bolt whose work was carried SHALL NOT be held for it. A head crew can't read SHALL be refused, naming why.

#### Scenario: A bolt built on another bolt's landing is refused at its submit
- **WHEN** bolt `popover`'s branch on GitHub holds bolt `deleting`'s landing `f5e67f35`, which main lacks, and ops runs `crew bolt submit popover`
- **THEN** nothing of `popover` is submitted and sluice is asked for nothing, and the refusal names bolt `deleting` and its landing `f5e67f3`, recorded with no head

#### Scenario: The bolt whose work was carried lands
- **WHEN** `popover` carries `deleting`'s landing, and ops runs `crew bolt submit deleting`
- **THEN** `deleting` is not refused for it, since it holds nothing on `popover`'s first-parent line

#### Scenario: Main holds the carried work
- **WHEN** `deleting` has landed on main, GitHub has deleted its branch, and ops runs `crew bolt submit popover`
- **THEN** `popover` carries nothing main lacks, and is submitted as any bolt; the host's tracking ref of `deleting` is not pruned by the read

#### Scenario: What a head carries can't be read
- **WHEN** the fetch `crew bolt submit` makes to read what the head carries fails
- **THEN** nothing is submitted, and the refusal says git's words

### Requirement: crew bolts says a bolt carries another bolt's work
`crew bolts` SHALL say under a bolt whose kit's read says it carries another bolt's work that main lacks that its landing is held, naming that bolt and its landings, and SHALL give it in its JSON as `carries`, or why it can't be read as `carries_error`. A kit's read SHALL leave out a bolt's ref another command removed while it read, and SHALL name a line git can't list.

#### Scenario: crew bolts shows a bolt carrying another's work
- **WHEN** the kit's read says bolt `y` carries bolt `x`'s landing `f5e67f35`
- **THEN** `crew bolts` shows under `y` "landing: held: carries bolt x's work, its landing f5e67f3, which main lacks", and its JSON gives `carries`

#### Scenario: A bolt's ref goes while the kit is read
- **WHEN** a fetch removes `origin/bolt/gone` while a kit's read lists the bolts' lines
- **THEN** `gone` is left out of the lines, and no bolt is read as unreadable for it
