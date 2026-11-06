## MODIFIED Requirements

### Requirement: A landing's session opens what the bolt brings to main, as one review
A `land/<bolt>` card's session SHALL be one plannotator review of several files, in this order: a page naming the bolt, its head, the units and chores that land, and that the reading lands nothing; each unit's change in the plan's order as the head holds it, its Markdown files named for the unit; then the bolt's diff against main, from where the bolt last met main to its head, less the change folders already shown. Each file SHALL open whole, as its own path. The diff SHALL be in as many files as keep each within the most plannotator opens in one file, 2 MB, each holding whole files' changes in git's order, and the page SHALL say how many when there are several. A file whose own change passes that most SHALL be cut nowhere: a line in its place in the diff SHALL name it and its size, and the page SHALL name each such file with its size, how many there are, and where to read them whole, GitHub's compare view of the bolt against main from where it last met main to its head and the git command on the team's host. Nothing of the diff SHALL be left out unnamed.

#### Scenario: A bolt of two units and a chore
- **WHEN** bolt `y` holds units `a` and `b`, both archived on its branch, and chore `c`, and crew raises its landing card at head `def5678`
- **THEN** the session's files are `00-y.md`, then `01-a-proposal.md` and the rest of `a`'s change, then `02-b-proposal.md` and the rest of `b`'s, then the diff of `y` against main as text, which holds `c`'s code and every unit's code and no file under `openspec/changes/`, each as it stands at `def5678`

#### Scenario: A change's metadata
- **WHEN** `a`'s archived change folder holds `.openspec.yaml` beside its Markdown files
- **THEN** the landing's session holds the Markdown files only

#### Scenario: Main moved since the bolt was cut
- **WHEN** main has had two landings since bolt `y` last met it
- **THEN** the diff in `y`'s session holds only what `y` brings, from where `y` last met main to its head, and none of those landings' changes

#### Scenario: A diff past plannotator's limit for one file
- **WHEN** bolt `y`, of chore `c` alone, changes five files by 0.9 MB each, 4.5 MB of diff in all
- **THEN** the session's files are `00-y.md`, then `01-y-diff-1-of-3.txt`, `01-y-diff-2-of-3.txt` and `01-y-diff-3-of-3.txt`, none over 2 MB, holding the five files' changes whole in git's order, two, two and one, and the page says the diff comes in 3 files

#### Scenario: One file's change past plannotator's limit
- **WHEN** bolt `y` changes `README.md` by a few lines and `vendor/bundle.js` by 2.5 MB
- **THEN** the diff holds `README.md`'s change whole and, in `vendor/bundle.js`'s place, a line naming it and its 2.5 MB, and the page names `vendor/bundle.js`, 2.5 MB, as the one file left out, with GitHub's compare view of the kit from the commit the diff is from to `y`'s head and the `git -C <main> diff <base> <head> -- <path>` that reads it on the team's host
