## MODIFIED Requirements

### Requirement: A bolt lands on main on the user's word
Bolts whose verification is green SHALL be landed by the partition's main-level ops on the user's word, by one procedure: `crew bolt submit <bolt>...` submits each bolt's branch to its kit's main through sluice, in the order given, and closes each with `crew bolt land` as it lands; it deploys nothing, pushes nothing and levels no host's checkout. Each SHALL be submitted from a short-lived worktree on its branch at `<kit>/places/land-<bolt>` on its team's host, in the name of whoever asked, removed once its outcome is in. A bolt that does not land SHALL move nothing, and the bolts after it SHALL go on. The command SHALL exit non-zero when any bolt did not land, naming each.

#### Scenario: The bolt lands
- **WHEN** the user sends swb-1's bolt ticked on its kit's landings card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on GitHub's main as a merge commit, the landing's worktree is gone, `crew bolt land` has closed it, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: Three bolts queued as one chain
- **WHEN** main-level ops runs `crew bolt submit y z w`, the three held by teams on one host
- **THEN** `y` is submitted first, `z` once sluice has queued `y`, and `w` once it has queued `z`, none waiting for the one before to land, so sluice tests them as one chain and lands them in that order

#### Scenario: Bolts on two hosts
- **WHEN** main-level ops runs `crew bolt submit y z`, `y` held by a team on deneb and `z` by one on mac-studio
- **THEN** `z` is submitted only once `y`'s submission has ended, so `z` never lands before `y`

#### Scenario: One refused, the rest go on
- **WHEN** `crew bolt submit y z w` runs and sluice refuses `z` for a conflict with main
- **THEN** `y` and `w` land and are closed, `z` and main are where they were for `z`, the command says `z` did not land in sluice's words and that its team takes main into it by a fix, and it exits non-zero

#### Scenario: Bolts of two kits
- **WHEN** `crew bolt submit y w` names a bolt of crew and a bolt of swancloud
- **THEN** it is refused before anything is submitted, saying it lands one kit's bolts at a time

#### Scenario: The waiting bolt lands while the team builds another
- **WHEN** swc-1 holds `doctor-rows`, proven, and builds `ssh-fix`, and `crew bolt submit doctor-rows` lands it
- **THEN** swc-1 holds `ssh-fix` alone, the command says swc-1 builds `ssh-fix`, and the conductor's and ops's restart is not made due by the landing, since the branch they carry is `bolt/ssh-fix`

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command says the bolt did not land with sluice's words, main and the bolt's branch are where they were, the landing's worktree is gone, and the conductor is to take main into the bolt by a fix

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's main on the team's host lacks a commit GitHub's main has
- **THEN** nothing is refused for it, since sluice forms each landing on GitHub's main and pushes it with a lease

#### Scenario: A landed bolt crew could not close
- **WHEN** sluice lands bolt `y` and `crew bolt land y` then refuses, its plan unreadable
- **THEN** the command says `y` landed and was not closed, naming why and `crew bolt land y` as the act that closes it, and goes on to the next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team no longer holds it, and crew says the worktree is kept with its branch because it has uncommitted changes

### Requirement: A split bolt takes no merge
A bolt is split when its host's own `bolt/<bolt>` has a tip whose policy names a remote for the bolt and the bolt's branch on that remote, read after a fetch, does not hold that tip. A unit's, chore's or fix's merge into a split bolt SHALL be refused before anything is submitted, naming both commits, the merges the remote's copy lacks, and the bolt's landing as the way on. A landing SHALL NOT be refused for it while the remote's copy holds nothing the host's tip lacks; one whose two copies have diverged SHALL be refused, as a landing submits the bolt where it lives.

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

## ADDED Requirements

### Requirement: A landing submits the bolt where it lives
Before it cuts the landing's worktree, `crew bolt submit` SHALL fetch the bolt's branch from the kit's origin on the team's host. A bolt on GitHub, whose GitHub copy's policy names a remote for it, SHALL be submitted at GitHub's head, never the host's copy. When the host's copy is behind GitHub's head or missing, crew SHALL first set it to GitHub's head, guarded by the value it read, and say so. The worktree SHALL then hold GitHub's head, and its push SHALL move nothing on GitHub.

#### Scenario: The host's copy lags GitHub's
- **WHEN** `crew bolt submit b` runs while GitHub's `bolt/b`, after a fetch, holds two merges the host's `bolt/b` lacks, and the host's copy holds nothing GitHub's lacks
- **THEN** crew sets the host's `bolt/b` to GitHub's head, which sluice's guard lets through, says it levelled the copy naming both commits, cuts the landing's worktree at GitHub's head, and submits that head, so main holds both merges once it lands

#### Scenario: The host's copy is level with GitHub's
- **WHEN** `crew bolt submit b` runs and the host's `bolt/b` is GitHub's head
- **THEN** crew writes no ref, says nothing of levelling, and submits that head as before

#### Scenario: The host has no copy
- **WHEN** `crew bolt submit b` runs on a host that has no `bolt/b` of its own while GitHub's `bolt/b` names `origin` for it
- **THEN** crew makes the host's `bolt/b` at GitHub's head and submits that head

#### Scenario: GitHub moved after crew read it
- **WHEN** crew levels the host's copy to the head it fetched, and sluice's guard refuses the write because GitHub's branch moved since
- **THEN** nothing is submitted, no landing worktree is made, and the command says the bolt did not land in the guard's words, so ops runs the landing again

#### Scenario: A legacy bolt's host tip is ahead of GitHub's copy
- **WHEN** `crew bolt submit b` runs on a split bolt whose host tip holds a merge GitHub's `bolt/b` lacks, while GitHub's copy holds nothing the host's lacks
- **THEN** crew writes no ref and submits the host's tip, as the split's refusal names the landing as the way on, and its push moves GitHub's branch forward to that tip

#### Scenario: The two copies have diverged
- **WHEN** `crew bolt submit b` runs while GitHub's `bolt/b` holds a merge the host's copy lacks and the host's copy holds one GitHub's lacks
- **THEN** nothing is submitted and no ref is written, and the command says `b` did not land, naming both commits and the merges each lacks, since either submission would drop merges

#### Scenario: A bolt that lives on its host
- **WHEN** `crew bolt submit b` runs on a bolt made on its host before gives went through sluice, whose GitHub copy is absent or names no remote for it, or in a kit with no origin
- **THEN** crew writes no ref and submits the host's `bolt/b` as before

#### Scenario: GitHub's copy cannot be read
- **WHEN** `crew bolt submit b` runs and the read or fetch of `origin`'s `bolt/b` fails
- **THEN** nothing is submitted, no landing worktree is made, and the command says `b` did not land, naming git's words

#### Scenario: A landing worktree that stands from before
- **WHEN** `<kit>/places/land-b` stands on `bolt/b` from an earlier attempt and crew levels the host's copy to GitHub's head
- **THEN** the worktree's files are brought to GitHub's head without writing a ref, and it is submitted clean at that head; when git cannot bring them, nothing is submitted, in git's words
