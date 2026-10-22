## ADDED Requirements

### Requirement: A team builds one bolt and may hold one more that waits to land
A team SHALL build one bolt at a time, and MAY hold one more that is proven and waits to land. A bolt SHALL be proven for this when it holds at least one unit or chore, every one of them has merged, and sluice's verdict at its head is green; a fix in flight on it SHALL NOT make it unproven. The bolt a team builds SHALL be the one it was given last, read from the run record's gives; while it holds one bolt, that one. The proven bolt SHALL keep of the team only what its landing needs: a fix's slot when its landing or a forecast conflicts with main, and the team's ops. The conductor SHALL serve both bolts, and the team SHALL never have more than `units` units, chores and fixes in flight across them. The landing SHALL still run on the user's yes, by main-level ops. When a merge leaves the team free to take a bolt and a bolt of its kits is planned that no team holds, crew SHALL tell the partition's dispatchers that are up, as it does when a bolt lands.

#### Scenario: The emergency bolt starts
- **WHEN** swc-1 holds bolt `doctor-rows`, whose three units have merged and whose verdict is green at its head while its landing card waits on the user, and the dispatcher runs `crew bolt give swc-1`
- **THEN** swc-1 holds `doctor-rows` and the next planned bolt, the new bolt's branch is made from main, and its units start in swc-1's free slots

#### Scenario: A carrying fix on the waiting bolt
- **WHEN** swc-1 builds `ssh-fix` in three slots and holds `doctor-rows`, whose landing main-level ops says conflicts with main
- **THEN** the conductor starts a fix on `doctor-rows` in the fourth slot, and a fifth piece of work of either bolt waits for a slot

#### Scenario: A merge frees the team
- **WHEN** the last unit of swc-1's only bolt merges, sluice is green at its head, and the plan holds a bolt of swc-1's kit no team holds
- **THEN** each of the partition's dispatchers that is up is told that swc-1 can take its next bolt

#### Scenario: Two bolts, the newer still building
- **WHEN** swc-1 holds `doctor-rows`, proven, and `ssh-fix`, given after it, with a unit in code
- **THEN** swc-1 builds `ssh-fix`, and `crew status swc-1` names both bolts, `doctor-rows` as waiting to land

### Requirement: A give to a team holding a waiting bolt restarts its roles at their next stop
A give to a team that holds a proven bolt SHALL restart neither its conductor nor its ops at once: each SHALL be restarted at its next stop, once idle, as an agent whose team's bolt changed under it is, the conductor fresh and ops with its conversation. The conductor's greeting at that restart SHALL name the bolt it now builds, the bolt that waits to land, the landing card it holds for that bolt with the line that adopts it, and each fix in flight on it. A give to a team that holds no bolt SHALL restart both at once, as before.

#### Scenario: A give while the conductor waits on its landing card
- **WHEN** `crew bolt give swc-1` gives `ssh-fix` while swc-1-conductor runs `crew card wait land/doctor-rows` in the background and is otherwise idle
- **THEN** the conductor is restarted fresh once idle, and its first message says it builds `ssh-fix`, that `doctor-rows` waits to land, and how to adopt its landing card `land/doctor-rows`

## MODIFIED Requirements

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. While the team holds two bolts, a new fix SHALL name its bolt with `--bolt <bolt>`, one the team holds, and SHALL be refused without it, naming both; a fix in flight SHALL be found by its name among the team's bolts, and a name in flight on both SHALL be refused without `--bolt`. It SHALL start a fresh code agent there in a free slot with the words given, whether or not the place could be made ready: when a step of its readying failed, the agent SHALL be told the step and its last lines with the fix's words, since a fix is how a bolt is repaired, and the command SHALL say so. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the fix's bolt. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit, by a submission. `crew fix <team> <name> --drop` SHALL end a fix that is not wanted, whether a slot holds it or only its branch or place stands: its slot SHALL be freed and its agent ended when one is up, a working agent only with `--force`, and its place and branch SHALL go as a dropped unit's do, its branch kept and named when it holds commits whose patch the bolt lacks. A fix that has merged into its bolt SHALL NOT be dropped, and a drop refused SHALL be recorded. A fix SHALL have no OpenSpec change and no plan record. A landing that conflicts with main SHALL be taken by a fix whose agent merges main into its place, resolving the conflict, and which merges into the bolt like any fix; nothing of crew's SHALL move the bolt's branch.

#### Scenario: A red suite on the bolt
- **WHEN** a unit's or fix's submission to the bolt fails a check the kit's policy requires
- **THEN** nothing lands, the bolt is where it was, and the agent fixes the cause in its own place and submits again

#### Scenario: Two teams name a fix the same
- **WHEN** two teams that build in one kit checkout each start a fix named `bolt-takes-main` on their own bolts
- **THEN** each fix has its own branch made from its own team's bolt, `fix/<bolt>/bolt-takes-main`, in its own place, `places/fix-<bolt>--bolt-takes-main`, and each team's status shows only its own fix

#### Scenario: A fix on the bolt that waits to land
- **WHEN** swc-1 holds `doctor-rows`, proven, and `ssh-fix`, and the conductor runs `crew fix swc-1 take-main "Take main into the bolt: README.md" --bolt doctor-rows`
- **THEN** the fix is made on `fix/doctor-rows/take-main` from `bolt/doctor-rows` in a free slot, and `crew fix swc-1 take-main --merge` submits it to `bolt/doctor-rows`

#### Scenario: A new fix that names no bolt while two are held
- **WHEN** swc-1 holds `doctor-rows` and `ssh-fix` and the conductor runs `crew fix swc-1 gap "<words>"`
- **THEN** crew refuses, naming both bolts and `--bolt`, takes no slot and starts no agent

#### Scenario: A fix name already in use on the bolt
- **WHEN** a team starts a fix whose branch or place already exists, and none of its slots holds that fix
- **THEN** crew refuses it, naming the place, takes no slot and starts no agent, and records the refusal

#### Scenario: A fix in flight is run again
- **WHEN** a team starts a fix that one of its slots already holds
- **THEN** the fix's agent starts again in that fix's own place, on its own branch

#### Scenario: A place that is not the fix's own
- **WHEN** a fix's place is on a branch other than the fix's own, or its branch was made from another bolt than the fix's
- **THEN** crew refuses to start the fix's agent there, naming the place and the branch or bolt it is on

#### Scenario: A fix that adds commits merges
- **WHEN** a fix's branch holds a commit of its own beyond the bolt, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, as for a unit, and its agent submits it to the bolt

#### Scenario: A fix takes main into the bolt
- **WHEN** a bolt's landing conflicted with main on `README.md`, a fix's agent merged main into the fix's place resolving it, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, its agent submits it to the bolt, and once sluice lands it the bolt holds main and the landing can be submitted again

#### Scenario: A bolt whose toolchain fails
- **WHEN** a team starts a fix and the bolt's declared toolchain or its runner's setup fails in the fix's new place
- **THEN** the fix's agent starts there, its prompt holding the fix's words, the step that failed and its last lines, and the start is recorded with no refusal

#### Scenario: A fix not wanted is dropped
- **WHEN** the conductor runs `crew fix <team> <name> --drop` on a fix a slot holds, whose agent is idle and whose branch holds nothing beyond the bolt
- **THEN** its slot is freed and its agent ended, its place and branch are removed through the kit's `wt remove`, and the drop is recorded

#### Scenario: A fix whose agent is working
- **WHEN** the conductor drops a fix whose agent is working, without `--force`
- **THEN** crew refuses, saying the agent is working and that `--force` ends it anyway, records the refusal, and frees nothing

#### Scenario: A fix standing with no slot
- **WHEN** a fix's branch and place stand with no slot holding them, the branch holding a commit of its own, and the conductor drops it
- **THEN** its place is removed, and its branch is kept, named with the commit it is at and how many commits of its own it holds

#### Scenario: A merged fix
- **WHEN** the conductor drops a fix that has merged into its bolt
- **THEN** crew refuses, saying it has merged and that a new fix undoes it, and records the refusal

### Requirement: A bolt lands on main on the user's word
A bolt whose verification is green SHALL be landed by the partition's main-level ops, on the user's approval of its landing card, by one procedure: `crew bolt submit <bolt>` submits `bolt/<bolt>` to main through sluice and waits for its outcome, main-level ops pushes main without force, and then runs `crew bolt land`; it deploys nothing. `crew bolt submit` SHALL be refused while the kit's main on its host is behind GitHub's, SHALL submit from a short-lived worktree on the bolt's branch at `<kit>/places/land-<bolt>` on the team's host, in the name of whoever asked, SHALL remove that worktree after, and SHALL bring the kit's main checkout level with what landed. The bolt's branch SHALL then be removed, and the team SHALL no longer hold that bolt, keeping any other it holds; `crew bolt land` SHALL say which bolt the team still builds, or that it holds none. A worktree that is kept SHALL NOT stop the landing. When the submission conflicts with main or fails main's checks, nothing SHALL land and nothing SHALL move, and main-level ops SHALL tell the bolt's conductor sluice's words, for the team to take main into the bolt by a fix.

#### Scenario: The bolt lands
- **WHEN** the user approves swb-1's landing card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on main as a merge commit, the landing's worktree is gone, the kit's main checkout holds what landed with nothing modified, and after the push and `crew bolt land` GitHub's main holds it too, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: The waiting bolt lands while the team builds another
- **WHEN** swc-1 holds `doctor-rows`, proven, and builds `ssh-fix`, and `crew bolt land doctor-rows` runs
- **THEN** swc-1 holds `ssh-fix` alone, the command says swc-1 builds `ssh-fix`, and the conductor's and ops's restart is not made due by the landing, since the branch they carry is `bolt/ssh-fix`

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's main on the team's host lacks a commit GitHub's main has
- **THEN** it is refused, saying how far behind main is, and nothing is submitted

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command fails with sluice's words, main and the bolt's branch are where they were, the landing's worktree is gone, and the conductor is told to take main into the bolt by a fix

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team no longer holds it, and crew says the worktree is kept with its branch because it has uncommitted changes

### Requirement: A team's next bolt needs no edit and no deploy
Giving a team its next bolt SHALL be `crew bolt give <team>`, once every bolt it holds is proven and it holds fewer than two. A team's base branch SHALL come from the bolt it builds, never from the teams file.

#### Scenario: swb-1 finishes a bolt
- **WHEN** swb-1's bolt has landed and the dispatcher runs `crew bolt give swb-1`
- **THEN** swb-1 holds the next planned bolt in switchboard-kit, its bolt branch exists, and nothing was deployed

#### Scenario: swb-1's bolt is proven and waits to land
- **WHEN** every unit of swb-1's bolt has merged, sluice is green at its head, and the dispatcher runs `crew bolt give swb-1`
- **THEN** swb-1 holds the next planned bolt in switchboard-kit beside the one waiting to land, and nothing was deployed

### Requirement: A conductor carries its bolt for sluice
A team's conductor and ops that crew starts while the team holds a bolt SHALL have `SLUICE_BRANCH` in its environment set to the branch of the bolt the team builds, the one given last, and its herdr pane SHALL carry the token `sluice_branch` with the same value, reported from the source `crew` with no time to live. The token SHALL be reported again when herdr resumes the agent, and cleared when the team no longer holds a bolt, set to the other's branch when the bolt it names lands or is dropped while the team holds another; a conductor or ops whose session then carries the old branch SHALL be restarted at its next stop, as an agent an update made due is, told why. A unit slot SHALL carry neither.

#### Scenario: A conductor starts on a bolt
- **WHEN** crew starts `swb-1-conductor` in `/workspace/switchboard-kit/main` while team swb-1 holds bolt `b7`
- **THEN** its environment holds `SLUICE_BRANCH=bolt/b7`, and `herdr pane list` shows `"sluice_branch": "bolt/b7"` in its pane's `tokens`

#### Scenario: A team holding two bolts
- **WHEN** crew starts `swb-1-conductor` while swb-1 holds `b7`, proven and waiting to land, and `b8`, given after it
- **THEN** its environment holds `SLUICE_BRANCH=bolt/b8`, and its pane's token is `bolt/b8`

#### Scenario: herdr restarts
- **WHEN** herdr's server restarts and resumes `swb-1-conductor` without crew's environment
- **THEN** its pane's `tokens` hold `"sluice_branch": "bolt/b7"` again

#### Scenario: The bolt lands
- **WHEN** `crew bolt land b7` closes swb-1's only bolt
- **THEN** the conductor's and ops's panes carry no `sluice_branch` token, and once each is idle it is restarted without `SLUICE_BRANCH`, the conductor fresh and ops with its conversation, told that its team no longer holds `bolt/b7`

#### Scenario: A unit
- **WHEN** crew starts `swb-1-unit-2` in its own worktree
- **THEN** its environment has no `SLUICE_BRANCH` and its pane no `sluice_branch` token
