## MODIFIED Requirements

### Requirement: A conflict is forecast on the conductor's waits
Each time the conductor waits on a stage or a proof through crew, crew SHALL dry-run, with `git merge-tree`, the merge of each unmerged unit's head with `bolt/<bolt>` and with the head of each unmerged unit ahead of it in the bolt's merge order, writing no ref. A unit SHALL be compared with one ahead of it only on what each adds beyond the newest of that one's work it holds, read from git and never from a commit's words. A unit whose head holds that one's head, by a merge in its place, a settle or anything else, SHALL be forecast nothing against it. A unit that still holds the head of that one its place took SHALL be compared from that head only while that one's line no longer holds it, because its rebase or settle rewrote that work, and the two share nothing newer of that one's work. Any other unit SHALL be compared from their merge base, the newest commit both hold. When git cannot tell what a unit holds, crew SHALL say so, naming the two units, and SHALL forecast nothing for them.

#### Scenario: The dry run moves nothing
- **WHEN** the conductor's wait forecasts the merges of three unmerged units
- **THEN** no branch of the kit has moved

#### Scenario: A dependent carries its After unit's rewritten work
- **WHEN** B, after A, holds A's work as its place took it, A is rebased onto the bolt and its settle revises A's own file, and the conductor's wait runs
- **THEN** B is forecast nothing against A for that file, and a line B's own commit changed that A's settle also changed is forecast

#### Scenario: A unit that merged the one ahead of it in its place
- **WHEN** B's place took A's head, A's code then changed `shared.txt`, B merged A's new head in its place and changed the next line itself, and the conductor's wait runs
- **THEN** B is forecast nothing against A, and no settle starts for it

#### Scenario: The unit ahead moved on from the head the place took
- **WHEN** B's place took A's head and B revised A's design, and A has since added its tasks and changed `other.txt`, which B's own code changes too
- **THEN** B is forecast against A on `other.txt` alone, and not on A's design, which both would change from the bolt

#### Scenario: A newer head merged after the one taken
- **WHEN** B's place took A's first head, B merged A's second in its place and changed the line after A's, and A then changed `other.txt`, which B changes too
- **THEN** B is forecast against A on `other.txt` alone, and not on the line of A's that B already holds
