## RENAMED Requirements

- FROM: `### Requirement: A crossed team's give launches its bolt whole`
- TO: `### Requirement: A started bolt's work is launched whole`
- FROM: `### Requirement: A crossed team's launch carries its stream, priority, intent and recipient`
- TO: `### Requirement: A launch carries its repository, priority, intent and recipient`
- FROM: `### Requirement: A crossed team's dependent launches once its After work has landed`
- TO: `### Requirement: A dependent launches once its After work has landed`
- FROM: `### Requirement: Plan writes reach a crossed team's places`
- TO: `### Requirement: Plan writes reach a started bolt's places`
- FROM: `### Requirement: A crossed team's place is answered by a retry`
- TO: `### Requirement: A place is answered by a retry`
- FROM: `### Requirement: A crossed team's fix is a fix place on its bolt`
- TO: `### Requirement: A fix is a fix place on its bolt`
- FROM: `### Requirement: A crossed team's landing that conflicts with main takes main in by a fix place`
- TO: `### Requirement: A landing that conflicts with main takes main in by a fix place`

## ADDED Requirements

### Requirement: A bolt is a branch, and crew's one worktree is a landing's
A bolt SHALL be the branch `bolt/<bolt>` on GitHub, with no worktree, moved only through sluice. A unit's, chore's and fix's places and branches SHALL be Flume's; crew SHALL make, ready and remove none of them. crew's one worktree SHALL be a landing's, `<kit>/places/land-<bolt>` on the bolt's branch, for the minutes its submission takes; a main-level agent SHALL start in the kit's main checkout, the detached anchor at `origin/main`, and read a bolt by ref.

#### Scenario: A landing's worktree
- **WHEN** main-level ops runs `crew bolt submit b`
- **THEN** crew cuts `places/land-b` on `bolt/b` on the kit's host, submits from it, and removes it once the submission's outcome is in

#### Scenario: No place of a unit's is crew's
- **WHEN** crew reads a kit whose `places/` holds a unit's place Flume made
- **THEN** crew neither removes it nor makes it ready

### Requirement: Main-level ops lands bolts on the user's word
Bolts whose verification is green SHALL be landed by main-level ops on the user's word, by `crew bolt submit <bolt>...`: each bolt's branch submitted to its kit's main through sluice in the order given, from a short-lived worktree `<kit>/places/land-<bolt>` on its kit's host, removed once its outcome is in, each that lands closed as `crew bolt land` closes it. It deploys and pushes nothing. A bolt that does not land moves nothing, the rest go on, and the command exits non-zero naming each.

#### Scenario: The bolt lands
- **WHEN** the user sends a bolt ticked on its kit's landings card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on GitHub's main as a merge commit, the landing's worktree is gone, the bolt is closed as `crew bolt land` closes it, and the bolt's records are gone from the plan

#### Scenario: Three bolts queued as one chain
- **WHEN** main-level ops runs `crew bolt submit y z w`, three bolts of one kit
- **THEN** `y` is submitted first, `z` once sluice has queued `y`, and `w` once it has queued `z`, none waiting for the one before to land, so sluice tests them as one chain and lands them in that order

#### Scenario: One refused, the rest go on
- **WHEN** `crew bolt submit y z w` runs and sluice refuses `z` for a conflict with main
- **THEN** `y` and `w` land and are closed, `z` and main are where they were for `z`, the command says `z` did not land in sluice's words, and it exits non-zero

#### Scenario: Bolts of two kits
- **WHEN** `crew bolt submit y w` names a bolt of crew and a bolt of swancloud
- **THEN** it is refused before anything is submitted, saying it lands one kit's bolts at a time

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command says the bolt did not land with sluice's words, main and the bolt's branch are where they were, and the landing's worktree is gone

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's main on the kit's host lacks a commit GitHub's main has
- **THEN** nothing is refused for it, since sluice forms each landing on GitHub's main and pushes it with a lease

#### Scenario: A landed bolt crew could not close
- **WHEN** sluice lands bolt `y` and its close then refuses, its plan unreadable
- **THEN** the command says `y` landed and was not closed, naming why and that crew's next read of the bolt closes it once that is mended, the run record holds a refused `bolt.land` on `bolt/y` with those words, and the command goes on to the next bolt

### Requirement: A bolt whose work is on main lands by its close alone
`crew bolt land` SHALL land a bolt with no merge to make, on the user's word, once its kit's main holds each of its units' changes, open or archived, and each of its chores, read in the checkout the partition's main-level host keeps of its kit, since no runner took any of its work, recording the landing as any landing; it SHALL be refused for such a bolt with no units or chores, whose kit that host keeps no checkout of, or while any unit's change is not on main.

#### Scenario: A bolt built outside its branch
- **WHEN** the plan holds the bolt `deploys-go-through-crew`, nothing has merged into its branch, and each of its units' changes is archived on crew's main
- **THEN** `crew bolt land deploys-go-through-crew` removes it and its units from the plan, and the landing's entry names crew and the commit its main holds

#### Scenario: A unit not yet on main
- **WHEN** one unit of such a bolt has no change on its kit's main
- **THEN** `crew bolt land` is refused, naming the unit and its stage

### Requirement: A crew agent carries its name for sluice
Every agent crew starts SHALL have `SLUICE_AGENT` in its environment, the same as its `CREW_AGENT`, from its start and again when herdr resumes it where crew gives it its identity back; a main level's agent herdr resumes off its main level's host SHALL have neither (`main-level`).

#### Scenario: A main-level agent starts
- **WHEN** crew starts `wldn-ops`
- **THEN** its environment holds `CREW_AGENT=wldn-ops` and `SLUICE_AGENT=wldn-ops`

#### Scenario: herdr resumes an agent
- **WHEN** herdr resumes `wldn-planner`'s session on wldn's main-level host without crew's environment
- **THEN** its commands see `SLUICE_AGENT` back, the same as its `CREW_AGENT`

#### Scenario: herdr resumes a main level's agent on another host
- **WHEN** herdr resumes `swancloud-planner`'s session on a host the teams file does not name for swancloud's main level
- **THEN** its commands see neither `CREW_AGENT` nor `SLUICE_AGENT`

### Requirement: A landed bolt's branch goes only once main holds its work
Once sluice has landed a bolt's submission to main, crew SHALL mark the bolt's branch landed on its kit's host and, once no plan has the bolt and no worktree is on it, judge it against main as crew reads it now, by patch as `git cherry` compares. A branch holding nothing main lacks SHALL go; one holding a commit main lacks, or one git cannot compare, SHALL be kept, named with its commit and count, recorded once, and the user's. `crew bolt land` SHALL print what it removed and kept.

#### Scenario: Everything the bolt left is on main
- **WHEN** a bolt's submission to main has landed and `crew bolt land` runs
- **THEN** the landing's worktree and the bolt's branch are removed, and the command says the bolt's branch went because main holds every commit of it

#### Scenario: The bolt's branch holds a commit main lacks
- **WHEN** a bolt's submission to main has landed, and its branch then holds a commit main does not, and `crew bolt land` runs
- **THEN** the bolt's branch is kept, the command naming it, the commit it is at and that it holds 1 commit whose patch main lacks, a run-record entry names the branch, and no later read removes it

#### Scenario: Commits main holds under the same hashes
- **WHEN** sluice landed the bolt as a merge commit whose second parent is the bolt's head, and crew compares the bolt's branch with main
- **THEN** `git cherry` finds nothing of its own on it, and it goes

### Requirement: A landing that does not land leaves its pull request a draft
In a kit whose sluice policy at main takes pull requests into main, crew SHALL mark the pull request a bolt's landing opened from `bolt/<bolt>` into main a draft, which sluice never takes into main's queue, when `crew bolt submit` ends with the bolt not on main, before it answers, naming its link and saying the next `crew bolt submit` on the user's word makes it live again.

#### Scenario: A refused landing leaves its pull request a draft
- **WHEN** `crew bolt submit` runs on a bolt whose kit takes pull requests into main and sluice refuses it as conflicting with main
- **THEN** nothing lands, the bolt's pull request into main is a draft, and the command's words name its link, say it is a draft, and say the next `crew bolt submit` on the user's word makes it live again

#### Scenario: A failed landing leaves its pull request a draft
- **WHEN** `crew bolt submit` runs and main's checks fail on the bolt
- **THEN** nothing lands and the bolt's pull request into main is a draft

#### Scenario: A landing that lands marks nothing
- **WHEN** `crew bolt submit` runs and the bolt lands on main
- **THEN** no pull request is marked a draft, and the command's words are those of a landing

### Requirement: A landing is recorded by the first act that reads the bolt after it
The first crew act on any host to read a bolt once sluice's record has its landing's submission out SHALL record the outcome: the landing's waiter as it stops, `crew bolt submit`'s end, the rail's sweep on the kit's host, or `crew bolt land`. It SHALL take the number from the bolt's last queued `bolt.submit`, read sluice's record on the kit's host one read at a time, record nothing while the submission stands, and close a landed bolt with no word asked (`plan.21`).

#### Scenario: The submitter is gone before sluice decides
- **WHEN** `crew bolt submit z` queues submission 412 and its process is killed, and sluice then lands 412 on main
- **THEN** the waiter's read records `z` landed at the commit main holds and closes it, and no one runs `crew bolt land`

#### Scenario: The rail's sweep records it
- **WHEN** the waiter on the kit's host was stopped before sluice decided 412, and sluice's record later has 412 landed
- **THEN** the rail's next sweep on that host records `z` landed and closes it

#### Scenario: Two reads at once
- **WHEN** the waiter's read and `crew bolt submit`'s own end read `z`'s landing at the same moment
- **THEN** the run record holds one `bolt.submit` outcome for 412 and one `bolt.land`, and each says the bolt landed

#### Scenario: Still standing
- **WHEN** a read finds sluice's record of 412 still under test
- **THEN** nothing is recorded, and the bolt's last `bolt.submit` stays queued

#### Scenario: A conflict recorded by a later read
- **WHEN** the submitter is gone and sluice's record has 412 in conflict
- **THEN** the next read records `z`'s landing refused at the head submitted, in sluice's verdict, drafts its pull request, and raises its kit's landings card with `z` held on its row

#### Scenario: The user's words are kept on another host
- **WHEN** ops on mac-studio runs `crew bolt submit z` on the user's words in its pane, `z`'s kit is kept on deneb, and the waiter's read on deneb finds 412 landed
- **THEN** the read closes `z` and its landing card naming ops's pane and the time the word was given, none of the words, says the words are kept on mac-studio, and reaches no other host for them

#### Scenario: sluice's record can't be read
- **WHEN** `sluice status 412 --json` on the kit's host fails
- **THEN** the read records nothing, and says it cannot read sluice's record of 412 on that host, with sluice's words

### Requirement: No brief names a proof list
No brief crew gives an agent SHALL name a proof list, a task's shape or a design's sections, and the results section every brief carries SHALL name no proof list.

#### Scenario: The planner's brief
- **WHEN** the planner's brief, or any brief's results section, is printed
- **THEN** it names no *Proof in dev* list, no *Task notes* section and no shape for a task

### Requirement: A landing queued holds its bolt's work
crew SHALL read a bolt's landing from the run record as one of four states, each its own. **Queued** runs from the `bolt.submit` that records sluice's submission queued until an entry records that submission's outcome. **Rejected** holds once sluice refused the bolt's newest submission for the bolt's own content, a conflict or a failed check, recorded refused with the head submitted, until the bolt is submitted again. **Landing again** is queued once more after a rejection. **None** is a bolt never submitted, landed, or stopped by sluice or its host, nothing of the bolt's.

While a bolt's landing is queued or landing again, these SHALL be refused, naming the landing and its number, with nothing written or launched: `crew unit add` and `crew chore add` into the bolt, `crew unit move` and `crew chore move` into it, and `crew fix <bolt> <name>`. That holds whether they run directly or as a proposal's commands, at the proposal's check and at its approval. Each SHALL read the state from the run record at the tip its write is applied to. Once the bolt's landing is rejected, or with none, they SHALL go on as for any started bolt. `crew fix <bolt> <name> --drop`, the take-main fix crew launches on reading a conflict, and a proposal's card as it is drawn SHALL read no state.

`crew bolts`, text and JSON, the rail's line under land and the board's head line SHALL each say the state in words of their own. A landing queued is said with its number. A landing again is said with its number and the submission sluice rejected before it. A rejection is said, while the bolt's head is the one rejected, as the landing rejected and the bolt open for work, with sluice's words. The rail SHALL leave a bolt whose landing is queued or landing again out of the bolts that can land.

#### Scenario: A unit added while the landing is queued
- **WHEN** main-level ops's `crew bolt submit z` has `z`'s landing queued on main as #412, and the user approves the planner's proposal adding unit `b` to `z`
- **THEN** the approval is refused, saying `z` has its landing queued on main as #412, so unit `b` does not join it until sluice decides, and to put it on another bolt; `requests.rec` gains nothing

#### Scenario: A fix while the landing is queued
- **WHEN** main-level ops runs `crew fix z logic "Fix tests:logic."` while #412 is queued
- **THEN** it is refused naming #412, and no fix is launched

#### Scenario: A rejection opens the bolt for work
- **WHEN** sluice rejects #412, blaming `tests:logic`, which ran and failed
- **THEN** `crew bolts`, the rail and the board say `z`'s landing #412 was rejected at its head and the bolt is open for work, in sluice's words, and ops's `crew fix z logic "<sluice's words>"` is launched

#### Scenario: Landing again
- **WHEN** the fix has merged into `z` and ops's `crew bolt submit z` has it queued again as #415
- **THEN** `crew bolts`, the rail and the board say `z` is landing again as #415, after #412 was rejected; a unit added to `z` is refused naming both; and the rail's tell leaves `z` out

#### Scenario: A wait sluice itself failed on
- **WHEN** `crew bolt submit z`'s wait recorded `z`'s landing stopped with no submission named, sluice itself failing each time it waited on #412
- **THEN** `z`'s landing still reads queued as #412, and its work is held until a read records #412's outcome

#### Scenario: Another bolt's landing
- **WHEN** `y`'s landing is queued and the user adds a unit to `z`
- **THEN** the unit is added to `z` and launched

## MODIFIED Requirements

### Requirement: crew removes only its own worktrees
crew SHALL remove only the landing worktrees it cut, `<kit>/places/land-<bolt>` on a `bolt/` branch, and only bolt branches it marked as its own. It SHALL never remove the main checkout, a place of Flume's, a worktree elsewhere, one on another branch or on none, or a locked one, which it names as kept. It SHALL remove nothing when it cannot read every plan the kit's work goes in.

#### Scenario: A worktree made by hand
- **WHEN** a kit checkout has a worktree beside `main` that the user made, on a branch of their own
- **THEN** crew leaves it as it is

#### Scenario: A place of Flume's
- **WHEN** a kit checkout has `places/change--x` on `change/x`, a place Flume made
- **THEN** crew leaves it as it is

#### Scenario: A merge partway through its rebase
- **WHEN** a place is on no branch because a rebase stopped partway
- **THEN** crew leaves it as it is

#### Scenario: A plan that can't be read
- **WHEN** crew lands a bolt while the plan of a partition whose work is in the kit cannot be fetched
- **THEN** no worktree is removed, and crew says why

### Requirement: A landing records the commit main holds
`crew bolt land` SHALL record, in its `bolt.land` entry of the run record, the kit the bolt landed on and the commit that kit's main holds on its kit's host once the bolt has landed, and SHALL be refused when it can't read that commit.

#### Scenario: The landing's commit
- **WHEN** sluice has landed a bolt of switchboard-kit on its main and main-level ops runs `crew bolt land`
- **THEN** the landing's entry names switchboard-kit and the commit its main holds, and crew says the bolt has landed at that commit

### Requirement: A bolt's proof is its verification
A bolt SHALL be proven by its verification alone: sluice's verdict on its last landing, green at its head. Nobody SHALL deploy the bolt or work a list from its changes to prove it; ops SHALL prove and deploy nothing. crew SHALL offer the bolt for landing, as its row on its kit's landings card, once every unit and chore has merged and its verification is green.

#### Scenario: Ready to land
- **WHEN** every unit of a bolt has merged and `crew bolts` shows its verification green
- **THEN** the bolt is a row of its kit's landings card, in main-level ops's name, and no one is asked to prove it

#### Scenario: Not yet green
- **WHEN** every unit of a bolt has merged and its head is no landing of sluice's
- **THEN** the bolt is not offered for landing, and `crew bolts` says what its verification is

### Requirement: A landing is read from GitHub's main
`crew bolt submit` SHALL judge whether a bolt landed by main now, never by sluice's exit alone. For a kit with an origin remote, main now is GitHub's `origin/main` after a fetch. For a kit with no origin, it is the kit's own `main`. Before it submits, crew SHALL read main now on the kit's host, and SHALL refuse, submitting nothing, when it cannot. After sluice's outcome it SHALL read main now again, after a fresh fetch, together with whether it holds the bolt's tip that was submitted. The bolt has landed when main now moved and holds that tip, whatever sluice exited. crew SHALL then say where main holds it, mark the bolt's branch landed, and send ops on to `crew bolt land`. When sluice's exit was not 0, crew SHALL also name the exit and sluice's last words as what came after its push, sluice's to report apart from the landing. crew SHALL say that main is where it was only when main now did not move. When main now moved but does not hold the bolt, crew SHALL say the bolt did not land and name where main now is. When main now cannot be read after the submission, crew SHALL say it cannot tell whether the bolt landed, naming why and sluice's exit, and SHALL mark nothing and say nothing of where main is.

#### Scenario: sluice fails after its push
- **WHEN** main-level ops runs `crew bolt submit <bolt>`, and sluice pushes the bolt's merge to GitHub's main, then fails releasing a place and exits 3, leaving the host's own `main` where it was
- **THEN** the command succeeds, saying the bolt landed on the kit's main at the commit GitHub's main holds, naming sluice's exit 3 and its last words as what came after the push, sluice's to report apart, and saying "now crew bolt land <bolt>"; and the bolt's branch is marked landed

#### Scenario: sluice lands it and exits 0
- **WHEN** sluice lands the bolt and exits 0, and GitHub's main holds the bolt's merge after a fetch
- **THEN** crew says the bolt landed at that commit and "now crew bolt land <bolt>", naming no exit, and marks the branch landed

#### Scenario: GitHub's main did not move
- **WHEN** sluice exits 1 or 2, or any other exit, and GitHub's main after a fetch is at the commit it held before the submission
- **THEN** the command fails, saying the bolt did not land and main is where it was, and the branch is not marked

#### Scenario: Main moved, but not with the bolt
- **WHEN** sluice exits non-zero and GitHub's main after a fetch has moved but does not hold the bolt's submitted tip
- **THEN** the command fails, saying the bolt did not land and naming the commit main is now at; it does not say main is where it was, and the branch is not marked

#### Scenario: GitHub can't be read after the submission
- **WHEN** the fetch after sluice's outcome fails
- **THEN** the command fails, saying crew cannot tell whether the bolt landed, with the fetch's words and sluice's exit; it says neither that the bolt landed nor that main is where it was, and the branch is not marked

#### Scenario: GitHub can't be read before the submission
- **WHEN** `crew bolt submit` runs and the fetch of the kit's origin on the kit's host fails
- **THEN** it is refused with the fetch's words, nothing is submitted, and no landing worktree is made

#### Scenario: A kit with no origin
- **WHEN** a kit with no origin remote is landed and sluice moves its own `main` to a merge holding the bolt
- **THEN** crew reads the kit's own `main` before and after, and says the bolt landed

### Requirement: A kit that takes no pull requests is asked nothing of GitHub
crew SHALL read or mark no pull request on GitHub for a kit whose sluice policy at main has no pull requests table for main.

#### Scenario: A kit that takes no pull requests is asked nothing
- **WHEN** a landing runs in a kit whose sluice policy at main has no pull requests table for main
- **THEN** crew runs no `gh` command, and the landing goes on as before

### Requirement: A landing submits the bolt where it lives
Before it cuts the landing's worktree, `crew bolt submit` SHALL fetch the bolt's branch from the kit's origin on the kit's host. A bolt on GitHub, whose GitHub copy's policy names a remote for it, SHALL be submitted at GitHub's head, never the host's copy. When the host's copy is behind GitHub's head or missing, crew SHALL first set it to GitHub's head, guarded by the value it read, and say so. The worktree SHALL then hold GitHub's head, and its push SHALL move nothing on GitHub.

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
- **THEN** nothing is submitted and no ref is written, and the command says `b` did not land, naming both commits and the merges each lacks, since either submission would drop merges, and that the way on is a fix on the bolt that ops starts, `crew fix b <name> "<words>"`, taking the host's merges in

#### Scenario: A bolt that lives on its host
- **WHEN** `crew bolt submit b` runs on a bolt made on its host before gives went through sluice, whose GitHub copy is absent or names no remote for it, or in a kit with no origin
- **THEN** crew writes no ref and submits the host's `bolt/b` as before

#### Scenario: GitHub's copy cannot be read
- **WHEN** `crew bolt submit b` runs and the read or fetch of `origin`'s `bolt/b` fails
- **THEN** nothing is submitted, no landing worktree is made, and the command says `b` did not land, naming git's words

#### Scenario: A landing worktree that stands from before
- **WHEN** `<kit>/places/land-b` stands on `bolt/b` from an earlier attempt and crew levels the host's copy to GitHub's head
- **THEN** the worktree's files are brought to GitHub's head without writing a ref, and it is submitted clean at that head; when git cannot bring them, nothing is submitted, in git's words

### Requirement: A landing that did not land is the bolt's only for its own content
When `crew bolt submit` ends with a bolt not on main, crew SHALL judge it the bolt's only when sluice's record of the landing's own submission has it in conflict, or blamed for a check that ran and failed or that its time limit cut off; never by sluice's exit or words alone. The bolt's SHALL be recorded refused at the head submitted, and crew's words to ops SHALL say what comes next and name no team or conductor: a conflict with what main has landed is taken in by the fix crew launches on the bolt, ops starting nothing; a conflict with a submission queued on main ahead of it is waited out; and a check that failed is a fix on the bolt that ops starts with sluice's words.

#### Scenario: A conflict is the bolt's
- **WHEN** `crew bolt submit z` waits on its submission and sluice's record has it in conflict on `README.md`
- **THEN** the command fails, saying `z` did not land, that the conflict is the bolt's and that crew launches the fix that takes main into it, naming no team or conductor, and the run record's `bolt.submit` for `z` carries `Refused` and the head submitted

#### Scenario: A check that ran and failed
- **WHEN** sluice's record has the submission failed with `tests:logic` holding a failing result
- **THEN** the landing is the bolt's and recorded refused, as for a conflict, and crew's words tell ops to start a fix on the bolt with sluice's words, `crew fix z <name> "<sluice's words>"`

### Requirement: A submission's number is on its bolt's row from the submit
While a submission stands in sluice's queue, crew SHALL show its number and state on its bolt's row in `crew bolts`, text and JSON, from the first read after the submit, whoever made it, read from sluice's record of the queue on the kit's host: a merge into `bolt/<bolt>` on its unit's, chore's or fix's line, and the bolt's landing on its kit's main, from `bolt/<bolt>` or a pull request opened from it, on the bolt's head line.

#### Scenario: A unit's merge under test
- **WHEN** unit `a`'s merge agent runs `sluice submit bolt/y --no-wait --json` and sluice answers `#41`, which it then tests
- **THEN** the next `crew bolts` shows `a`'s line with `#41 under test`, and its JSON gives `a` a submission of id 41 and state `testing`

#### Scenario: A bolt's landing queued on main
- **WHEN** main-level ops's `crew bolt submit y` has been answered `#355` and sluice has it queued on main
- **THEN** `crew bolts` shows `y`'s head line with `landing #355 queued`

#### Scenario: Read again after the session that submitted it ended
- **WHEN** the session that submitted unit `a`'s merge `#41` has ended, and `#41` stands passed on `bolt/y` with nothing waiting on it
- **THEN** `crew bolts` still shows `a`'s line with `#41 passed, to land next`

#### Scenario: Decided
- **WHEN** sluice lands `#41` on `bolt/y`
- **THEN** `a`'s line shows no submission and reads its stage as merged once the bolt holds its change archived

#### Scenario: sluice's record can't be read
- **WHEN** `sluice overview --json` fails on the kit's host, or prints a document crew does not read
- **THEN** each held bolt of that kit on the host says its submissions can't be read and why, once, and no line shows a number or says it has none

### Requirement: A landing's waiter waits from the background a call at a time
Once sluice has queued a landing's submission, crew SHALL leave a waiter running on the kit's host, outside any agent's session. The waiter SHALL wait on the submission's number as `teams.5` has an agent wait: `sluice wait <n> --timeout 9m --json`, called again while it exits 5. It SHALL stop calling on any other exit. While the run record has the landing queued with no outcome, no work SHALL join the bolt, as `plan.8` has it and "A landing queued holds its bolt's work" says. When it stops, it SHALL run crew's read of the landing on that host.

#### Scenario: The waiter calls again while sluice is undecided
- **WHEN** a landing's submission is queued and sluice's first two waits on it exit 5, and its third exits 0
- **THEN** the waiter has called `sluice wait <n> --timeout 9m --json` three times, then crew's read of the landing has run, and the landing is recorded landed

#### Scenario: Nothing starts on the bolt while the waiter waits
- **WHEN** a landing's waiter is still calling `sluice wait` on `z`'s submission #412, and the user runs `crew unit add b "Build b." --bolt z`
- **THEN** it is refused, saying `z` has its landing queued on main as #412, the plan is unchanged, and nothing is launched

### Requirement: A close crew refuses is said on the bolt's row and in the run record until it is lifted
When a landed bolt's close is refused, crew SHALL record a `bolt.land` entry on the bolt carrying the refusal in crew's words, and SHALL say the same words on standard error. While the plan still holds the bolt, each later read SHALL try the close again. A read SHALL record a new refused entry only when the words differ from the bolt's last refused `bolt.land` since its landing. The bolt's head line SHALL say it landed on main and was not closed, with the words of its last refused close, until a close succeeds.

#### Scenario: A chore still at ready
- **WHEN** `z` lands on main while its chore `tidy-z` is still at ready in the plan
- **THEN** the run record holds a refused `bolt.land` on `bolt/z` saying `tidy-z` has not landed on main, and `z`'s head line says it landed on main and was not closed, with those words

#### Scenario: The same refusal is recorded once
- **WHEN** three of the rail's sweeps in a row find `z`'s close refused for the same reason
- **THEN** the run record holds one refused `bolt.land` for it

#### Scenario: Lifted
- **WHEN** the planner drops `tidy-z` from the plan and the rail sweeps again on the kit's host
- **THEN** the read closes `z`, the run record holds its `bolt.land`, and no head line for `z` remains

### Requirement: A started bolt's work is launched whole
`crew bolt start <bolt>` SHALL check the kit's policy and have sluice make `bolt/<bolt>` from the kit's main, in the checkout the partition's main-level host keeps of the kit, and SHALL be refused while that host keeps none or is held, or no runner answers for the partition. Its one plan write SHALL set `Path: flume` on the bolt, and no `Team`, and append a launch for each of its units and chores in the file's order, cut from `bolt/<bolt>`, in the kit's repository and naming no host or stream, for a runner whose configuration names the repository to take. It SHALL start, restart and greet no agent.

#### Scenario: A bolt of three
- **WHEN** `crew bolt start x` runs, `x` holding units `a` and `b`, `b` after `a`, and chore `c`, and a runner answers for madswan
- **THEN** the plan marks `x` `Path: flume` with no `Team`, `requests.rec` holds three launches of `change`, `change` and `chore` on `bolt/x`, each in crew's repository and naming no host or stream, and no agent starts

#### Scenario: No runner on the host
- **WHEN** `crew bolt start x` runs and madswan's state repository holds no runner's branch
- **THEN** the start is refused naming that no runner answers for madswan, and no branch is made

### Requirement: A launch carries its repository, priority, intent and recipient
Each launch of a started bolt's work SHALL name the kit's repository as the plan names it and no host or stream, a runner whose configuration names the repository taking it, in the stream its host's Flume configuration maps the repository to, the intent `<label>/<bolt>`, the recipient `<label>/planner`, a priority from its bolt's place in the plan, the highest first, and its brief, the work's own words as crew's prompts give them. A write that starts or reorders bolts SHALL append a priority for each launched place whose priority the plan's order changed.

#### Scenario: Two bolts in order
- **WHEN** `x` and then `y` are started, `x` above `y` in the plan
- **THEN** `x`'s launches carry a higher priority than `y`'s, each names crew's repository and no host or stream, intent `madswan/<bolt>` and recipient `madswan/planner`

#### Scenario: A reorder
- **WHEN** `crew bolt order` puts `y` above `x`
- **THEN** `requests.rec` gains a priority for each launched place of `x` and `y` whose priority changed, and none for another

### Requirement: A dependent launches once its After work has landed
A launch of work whose `After` names other work SHALL name those launches, and the runner SHALL launch it only once each of their places has landed on the bolt, answering it held meanwhile, so its place is cut from a bolt that holds their work.

#### Scenario: A dependent held
- **WHEN** `x` is started, `b` after `a`
- **THEN** `b`'s launch names `a`'s as its After, and `b` reads waiting on `a` until `a`'s place has landed on `bolt/x`

### Requirement: Plan writes reach a started bolt's places
Each as the write's own act, in its own commit: a unit or chore added to or moved into a started bolt SHALL be launched as the start launches it; an approved amendment of a unit whose place is launched SHALL be a retry of its construct with the amendment's words, and of one whose launch is held or unanswered a drop of that launch and a new launch carrying the amendment; a unit, chore or bolt dropped SHALL drop each of its launches still standing.

#### Scenario: An amendment of a unit in code
- **WHEN** the user approves an amendment of `a`, whose place on deneb's runner is in code
- **THEN** `requests.rec` gains a retry of `a`'s construct with the amendment's words, in the approval's commit

#### Scenario: A unit dropped
- **WHEN** the user approves dropping `c`, launched on started `x`
- **THEN** `requests.rec` gains a drop of `c`'s launch, in the approval's commit

### Requirement: Launched work keeps its bolt and order
A move out of a started bolt, a split, or a change of `After` on work whose launch is written SHALL be refused, naming its place and drop then add as the way on, since a place's base and order are fixed at its launch.

#### Scenario: A move of launched work
- **WHEN** a proposal moves `a`, launched on started `x`, to bolt `y`
- **THEN** the proposal is refused naming `a`'s place and that it is dropped and added again

### Requirement: A fix is a fix place on its bolt
`crew fix <bolt> <name> "<words>"` SHALL append a launch of the fix kind on `bolt/<bolt>`, in its kit's repository and naming no host or stream, with nothing held; `--drop` SHALL drop it, and `--merge`, `--wait` and `--bolt` SHALL be no options it has. A fix in flight SHALL hold its bolt's landing.

#### Scenario: A review note marked fix
- **WHEN** the planner runs `crew fix x rail-word "Say 'land' for a started bolt"` on a batch's note
- **THEN** `requests.rec` gains a launch of `fix` named `x--rail-word` on `bolt/x`, and `x`'s landing row says it lands once that fix has merged or been dropped

### Requirement: A landing that conflicts with main takes main in by a fix place
When sluice refuses a started bolt at its landing for a conflict with main, the act that reads the refusal SHALL append a launch of a fix on the bolt named `take-main-<main's revision, seven>`, in its kit's repository and naming no host or stream, its brief saying to take `origin/main` into the bolt with sluice's words of the conflict, unless a fix of that name already stands; the bolt's row SHALL say it takes main first.

#### Scenario: A landing refused for a conflict
- **WHEN** main-level ops's `crew bolt submit x` reads sluice refusing `x` for a conflict with main at `4d3d9be`
- **THEN** `requests.rec` gains one launch of `fix` named `x--take-main-4d3d9be` with sluice's conflict words, and `x`'s row says it takes main first

#### Scenario: Read twice
- **WHEN** a later read of the same refusal finds `x--take-main-4d3d9be` standing
- **THEN** no second launch is appended

## REMOVED Requirements

### Requirement: Teams are fixed in the teams file
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team's standing roles are its conductor and ops
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team's next bolt needs no edit and no deploy
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team's commands run on its host
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team is two herdr workspaces
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team taken down starts no stage
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A conductor brought back is told which units wait amended
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team takes a bolt of any kit it holds
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A conductor carries its bolt for sluice
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team builds one bolt and may hold one more that waits to land
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A give to a team holding a waiting bolt restarts its roles at their next stop
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A team reports each result on a line of its own, with one glyph
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: A conductor carries a stage's design questions together
**Reason**: Record 0047 move 5 and record 0050 part 3: teams leave crew, with their conductor and ops, once every team's setting is on.
**Migration**: None: the partitions' main-level roles stand as they do; a bolt's work runs on the crossed path.

### Requirement: Units run in slots
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A unit is built stage by stage, each by a fresh agent
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: The conductor waits for a stage through crew
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A unit in flight goes back through construct and review
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage ends at its deliverable
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: The deliverable of each stage
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage's agent says what it needs through crew
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage quiet too long is reported stuck
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A verify's findings are fixed in one round, with no card
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A unit fixed after its verify waits to merge
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A unit's merge archives its change first
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage begins only when its agent takes its prompt
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage's prompt not taken is sent once more
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage whose prompt is not taken never started
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A bolt's units are constructed in waves
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A dependent builds on its After units' work as it stands
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: A stage's made things are read from its place
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: The conductor's wait keeps a copy of what each stage made
**Reason**: Record 0047 move 5, record 0049 part 4: no unit slot; a unit's, chore's or fix's stages are a Flume kind's, launched and ended through the runner on the crossed path.
**Migration**: The crossed path's requirements (`teams-cross-to-flume-as-their-bolts-land`); `crew unit run|wait|free`, `crew chore run|wait|free` and `crew needs` are gone.

### Requirement: Fixes during a bolt are built beside its units
**Reason**: Record 0047 move 5, record 0049 part 4: the fix slot and the slot lent to a fix leave; a fix is Flume's fix kind, launched on the crossed path.
**Migration**: "A fix is a fix place on its bolt", in this spec; `crew fix <team>` and its slot are gone.

### Requirement: Ahead in a bolt is its merge order
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A unit carried onto its bolt keeps its own merge
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A merge carries no other unit's open change
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A dependent is told when its After unit is amended
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: Touches is a list crew reads
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: Overlapping Touches are told before code
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: Verify names what a unit changed and did not declare
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A conflict is forecast on the conductor's waits
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A forecast reaches the later unit once
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A forecast conflict between two units orders them
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A unit waiting to merge settles
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A conflict is resolved by the later unit's agent
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: The bolt is forecast against main on the conductor's waits
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A waiting bolt's conflict with main tells its conductor the take-main fix
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A wait's forecast conflict with main changes the kit's landings card
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A split bolt takes no merge
**Reason**: Record 0047 move 5: no conductor's wait forecasts, orders or settles units; a submission that fails or conflicts launches the kind's fix stage on the crossed path.
**Migration**: The crossed path's fix stage for a failed or conflicting submission; the landings card's own forecast stays (rail-cards).

### Requirement: A construct reads every source it is handed, and what each points at
**Reason**: Design Decision 7: crew starts no stage agent and gives no stage brief; a stage is briefed by its Flume kind and the kit's own files.
**Migration**: The kit's `CLAUDE.md`, `openspec/config.yaml` and `.config/flume.toml`, which the Flume kind's stage reads.

### Requirement: A construct stops on a source it cannot open
**Reason**: Design Decision 7: crew starts no stage agent and gives no stage brief; a stage is briefed by its Flume kind and the kit's own files.
**Migration**: The kit's `CLAUDE.md`, `openspec/config.yaml` and `.config/flume.toml`, which the Flume kind's stage reads.

### Requirement: A construct builds from its sources where the intent says more or otherwise
**Reason**: Design Decision 7: crew starts no stage agent and gives no stage brief; a stage is briefed by its Flume kind and the kit's own files.
**Migration**: The kit's `CLAUDE.md`, `openspec/config.yaml` and `.config/flume.toml`, which the Flume kind's stage reads.

### Requirement: A verify's report says what to do with each finding
**Reason**: Design Decision 7: crew starts no stage agent and gives no stage brief; a stage is briefed by its Flume kind and the kit's own files.
**Migration**: The kit's `CLAUDE.md`, `openspec/config.yaml` and `.config/flume.toml`, which the Flume kind's stage reads.

### Requirement: A worktree goes when its work is over
**Reason**: Record 0047 move 5: a unit's, chore's or fix's place and branch are Flume's, made and tidied by Flume; crew's one worktree is a landing's.
**Migration**: Flume's tidy; crew removes only its landing worktree ("crew removes only its own worktrees").

### Requirement: Uncommitted changes keep a worktree
**Reason**: Record 0047 move 5: a unit's, chore's or fix's place and branch are Flume's, made and tidied by Flume; crew's one worktree is a landing's.
**Migration**: Flume's tidy; crew removes only its landing worktree ("crew removes only its own worktrees").

### Requirement: A worktree goes through the kit's remove hooks
**Reason**: Record 0047 move 5: a unit's, chore's or fix's place and branch are Flume's, made and tidied by Flume; crew's one worktree is a landing's.
**Migration**: Flume's tidy; crew removes only its landing worktree ("crew removes only its own worktrees").

### Requirement: A remove hook that fails keeps the worktree
**Reason**: Record 0047 move 5: a unit's, chore's or fix's place and branch are Flume's, made and tidied by Flume; crew's one worktree is a landing's.
**Migration**: Flume's tidy; crew removes only its landing worktree ("crew removes only its own worktrees").

### Requirement: The branch is crew's to decide, never the worktree tool's
**Reason**: Record 0047 move 5: a unit's, chore's or fix's place and branch are Flume's, made and tidied by Flume; crew's one worktree is a landing's.
**Migration**: Flume's tidy; crew removes only its landing worktree ("crew removes only its own worktrees").

### Requirement: Work happens in fixed places
**Reason**: Record 0047 move 5: a unit's, chore's and fix's places are Flume's; its scenarios of gives and of crew's places leave with them.
**Migration**: "A bolt is a branch, and crew's one worktree is a landing's", added by this change.

### Requirement: A bolt lands on main on the user's word
**Reason**: Record 0047 move 5: no team holds a bolt; its scenarios of a team's host, a team's next bolt and a legacy bolt worktree leave.
**Migration**: "Main-level ops lands bolts on the user's word", added by this change.

### Requirement: A bolt no team holds lands once its units are on main
**Reason**: Record 0047 move 5: no bolt is held by a team, so this is every bolt with no merge to make.
**Migration**: "A bolt whose work is on main lands by its close alone", added by this change.

### Requirement: Every agent crew starts carries its name for sluice
**Reason**: Record 0047 move 5: crew starts no stage agent and no conductor.
**Migration**: "A crew agent carries its name for sluice", added by this change.

### Requirement: A landing leaves only what main lacks
**Reason**: Record 0047 move 5: a unit's, chore's and fix's branches are Flume's; crew judges the bolt's own branch alone, at its landing.
**Migration**: "A landed bolt's branch goes only once main holds its work", added by this change.

### Requirement: A landing's pull request is a draft whenever the user's word does not stand
**Reason**: Record 0047 move 5: crew starts no fix and no merge into a bolt, so it drafts the pull request at a landing that did not land alone (the rest leaves with record 0051's unit).
**Migration**: "A landing that does not land leaves its pull request a draft", added by this change.

### Requirement: A landing is recorded by whatever reads the bolt after it
**Reason**: Record 0047 move 5: no team's read; the rail's sweep on the kit's host takes its place.
**Migration**: "A landing is recorded by the first act that reads the bolt after it", added by this change.

### Requirement: A brief names nothing of a change's content but what crew reads
**Reason**: Design Decision 7: no construct or coder brief is left to name what crew reads of a change.
**Migration**: "No brief names a proof list", added by this change.

### Requirement: A team's path is today's, due or crossed
**Reason**: Record 0050 part 3, `roles.8`: every team has crossed, and the per-team setting leaves with the teams file's `teams`; a bolt's work has one path, which `crew bolt start` begins.
**Migration**: "A started bolt's work is launched whole", in this spec; a Bolt record's `Path: flume` marks a started bolt.

### Requirement: A team due to cross is given no new bolt
**Reason**: Record 0050 part 3: no team is due, and no bolt is given to a team.
**Migration**: None: `crew bolt give` is gone; a bolt's work starts by `crew bolt start` (bolt-plan "A bolt's work starts by crew bolt start").

### Requirement: A team crosses once its last bolt of today's path has gone
**Reason**: Record 0050 part 3: every team has crossed before this landing, and crew starts no conductor or team ops to end.
**Migration**: None: an agent the old crew left standing is closed after the deploy (design *After deploy*).

### Requirement: A crossed team is closed once neither of its roles is up
**Reason**: Record 0050 part 3: no team's workspaces, slots or roles are left to close, and crew writes no `team.cross` (design Decision 8).
**Migration**: None: design *After deploy*; `crew trace team/<team>` still reads the `team.cross` entries on the branch.

### Requirement: A crossed team runs no standing agent
**Reason**: Record 0047 move 5: the commands it refused for a crossed team, `crew up`, `rebuild`, `restart`, `resume`, `clear`, `down`, `unit run|wait|free`, `chore wait` and `fix --wait`, are gone for every team (design Decision 10).
**Migration**: None: a removed command falls to crew's unknown-command answer, which prints the usage.
