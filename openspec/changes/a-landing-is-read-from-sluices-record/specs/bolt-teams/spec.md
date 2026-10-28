## MODIFIED Requirements

### Requirement: A bolt lands on main on the user's word
Bolts whose verification is green SHALL be landed by the partition's main-level ops on the user's word, by one procedure: `crew bolt submit <bolt>...` submits each bolt's branch to its kit's main through sluice, in the order given, and each bolt that lands is closed with `crew bolt land`'s own code by the first crew act that reads it after sluice's record has it landed, `crew bolt submit`'s own end among them; it deploys nothing, pushes nothing and levels no host's checkout. Each SHALL be submitted from a short-lived worktree on its branch at `<kit>/places/land-<bolt>` on its team's host, in the name of whoever asked, removed once its outcome is in. A bolt that does not land SHALL move nothing, and the bolts after it SHALL go on. The command SHALL exit non-zero when any bolt did not land, naming each.

#### Scenario: The bolt lands
- **WHEN** the user sends swb-1's bolt ticked on its kit's landings card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on GitHub's main as a merge commit, the landing's worktree is gone, the bolt is closed as `crew bolt land` closes it, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

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
- **WHEN** sluice lands bolt `y` and its close then refuses, its plan unreadable
- **THEN** the command says `y` landed and was not closed, naming why and that crew's next read of the bolt closes it once that is mended, the run record holds a refused `bolt.land` on `bolt/y` with those words, and the command goes on to the next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team no longer holds it, and crew says the worktree is kept with its branch because it has uncommitted changes

## ADDED Requirements

### Requirement: A landing's submission is recorded when sluice queues it
When sluice queues a landing's submission, crew SHALL record it in the run record at once, before any wait on it: a `bolt.submit` entry on the bolt with `Outcome` queued, the submission's number as `Submission`, the head submitted as `Head`, and the kit's main before the submission as `Base`. A landing on the user's words in ops's pane SHALL carry, on that entry, the transcript record the words were read from and their length, never the words. Those words SHALL be kept, at that moment, on the host where they were given.

#### Scenario: The number is recorded before the wait
- **WHEN** main-level ops runs `crew bolt submit z` and sluice queues it as submission 412
- **THEN** the run record holds a `bolt.submit` entry on `bolt/z` with `Outcome: queued`, `Submission: 412`, the head submitted and main before, written before crew waits on 412

#### Scenario: Queued on the user's words in ops's pane
- **WHEN** ops runs `crew bolt submit z --excerpt "<the user's words>"` and sluice queues it
- **THEN** the queued entry names the transcript record the words were read from and their length, and the words are kept on ops's host

### Requirement: A landing's waiter waits from the background a call at a time
Once sluice has queued a landing's submission, crew SHALL leave a waiter running on the team's host, outside any agent's session. The waiter SHALL wait on the submission's number as `teams.5` has an agent wait: `sluice wait <n> --timeout 9m --json`, called again while it exits 5. It SHALL stop calling on any other exit. While it waits, no unit or chore stage starts on the bolt, as `plan.8` has it. When it stops, it SHALL run crew's read of the landing on that host.

#### Scenario: The waiter calls again while sluice is undecided
- **WHEN** a landing's submission is queued and sluice's first two waits on it exit 5, and its third exits 0
- **THEN** the waiter has called `sluice wait <n> --timeout 9m --json` three times, then crew's read of the landing has run, and the landing is recorded landed

#### Scenario: Nothing starts on the bolt while the waiter waits
- **WHEN** a landing's waiter is still calling `sluice wait` and the conductor runs a unit's verify on the bolt
- **THEN** the stage is refused, saying the bolt's landing is in flight

### Requirement: A landing is recorded by whatever reads the bolt after it
Whichever crew act reads a bolt first after sluice's record has its landing's submission out SHALL record the landing's outcome, on any host. The landing's waiter as it stops, `crew bolt submit`'s own end, the team's read on its host, and `crew bolt land` are all such acts. The read SHALL take the number from the bolt's last `bolt.submit` entry with `Outcome` queued, and SHALL read sluice's record of that submission on the team's host. The reads of one bolt SHALL run there one at a time, so a landing's outcome is recorded once. While sluice's record has the submission standing, the read SHALL record nothing. Once it is out, the read SHALL record what `crew bolt submit` records for that outcome: landed, judged by main now as a landing is; refused, for the bolt's own content; or stopped. A landed bolt SHALL then be closed with `crew bolt land`'s own code, with no word asked of whoever ran the act, since the user's word to land was given and the read records sluice's fact (`plan.21`). When sluice's record cannot be read, the read SHALL record nothing and SHALL say why, naming the host. `crew bolt land` run by hand SHALL still close a landed bolt, but it SHALL never be the only way a landing is recorded or closed.

#### Scenario: The submitter is gone before sluice decides
- **WHEN** `crew bolt submit z` queues submission 412 and its process is killed, and sluice then lands 412 on main
- **THEN** the waiter's read records `z` landed at the commit main holds and closes it, and no one runs `crew bolt land`

#### Scenario: The team's read records it
- **WHEN** the waiter on the team's host was stopped before sluice decided 412, and sluice's record later has 412 landed
- **THEN** the conductor's next command on that team records `z` landed and closes it

#### Scenario: Two reads at once
- **WHEN** the waiter's read and `crew bolt submit`'s own end read `z`'s landing at the same moment
- **THEN** the run record holds one `bolt.submit` outcome for 412 and one `bolt.land`, and each says the bolt landed

#### Scenario: Still standing
- **WHEN** a read finds sluice's record of 412 still under test
- **THEN** nothing is recorded, and the bolt's last `bolt.submit` stays queued

#### Scenario: A conflict recorded by a later read
- **WHEN** the submitter is gone and sluice's record has 412 in conflict
- **THEN** the next read records `z`'s landing refused at the head submitted, in sluice's verdict, drafts its pull request, and raises its kit's landings card with `z` held for its team's fix

#### Scenario: sluice's record can't be read
- **WHEN** `sluice status 412 --json` on the team's host fails
- **THEN** the read records nothing, and says it cannot read sluice's record of 412 on that host, with sluice's words

### Requirement: A close crew refuses is said on the bolt's row and in the run record until it is lifted
When a landed bolt's close is refused, crew SHALL record a `bolt.land` entry on the bolt carrying the refusal in crew's words, and SHALL say the same words on standard error. While the plan still holds the bolt, each later read SHALL try the close again. A read SHALL record a new refused entry only when the words differ from the bolt's last refused `bolt.land` since its landing. The bolt's head line SHALL say it landed on main and was not closed, with the words of its last refused close, until a close succeeds.

#### Scenario: A chore still at ready
- **WHEN** `z` lands on main while its chore `tidy-z` is still at ready in the plan
- **THEN** the run record holds a refused `bolt.land` on `bolt/z` saying `tidy-z` has not landed on main, and `z`'s head line says it landed on main and was not closed, with those words

#### Scenario: The same refusal is recorded once
- **WHEN** three team reads in a row find `z`'s close refused for the same reason
- **THEN** the run record holds one refused `bolt.land` for it

#### Scenario: Lifted
- **WHEN** the planner drops `tidy-z` from the plan and the conductor's next command runs the team's read
- **THEN** the read closes `z`, the run record holds its `bolt.land`, and no head line for `z` remains
