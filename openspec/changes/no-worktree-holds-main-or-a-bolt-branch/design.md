# Design

## Context

Record 0032 (proposed 2026-10-16) rules the whole: no worktree of crew's holds `main` or a bolt branch, a kit's `main` folder is a detached anchor swancloud's timer moves, crew reads by ref, bolts live on GitHub made and ended by sluice, crew follows sluice by its overview, and crew's plugin runs live or released. `openspec/explorations/agent-folders/reading.md` has what was read and what the user settled. This design says how crew does its part and in what order. It relies on `plan.18` and `plan.19` (new), `state.3`, `state.5`, `plan.8`, `plan.9`, `plan.16` and `plan.17` as the record amends them, `read.1` (a worktree crew cannot read is named, not guessed), `read.4` (crew takes over nothing it did not make: an anchor, a stray checkout), `code.7` (each decision a function of facts), `code.9` (no wait without a timeout), `code.8` (the views follow), `docs.2`, `docs.6`, `tests.11`. It touches the areas of `plan.md`, `teams.md`, `briefs.md`, `docs.md` and `tests.md`. It departs from no rule.

## Goals / Non-Goals

Goals: nothing of crew's and no agent works in a folder sluice's landings move; crew moves no anchor and levels no checkout; a landing on any host is seen by every host through GitHub; a bolt's branch has one writer; crew's code reaches a host by a mode the fleet sets, not by the folder it happens to run from.

Non-goals: the timer, the views, the detached clone, the plugin's toggle, `crew/live`, the catalog entry and the release-sources line (swancloud's); `branch create`, `branch delete`, the statement amendment and the refusal's words (sluice's); the `bolt/*` rulesets (the user's, per repository); a shared queue for one bolt across hosts (sluice's records seam, later); moving wldn off `box-hold` (the recovery session's).

## Decisions

### 1. Seven parts, built in this order

| part | what | waits on |
|---|---|---|
| 2 | legacy `bolts/<bolt>` worktrees detached at the bolt's tip when clean, named when dirty | nothing |
| 3 | the landing folder on `bolt/<bolt>`; the levelling step conditional, then gone; no unit starts while the landing is queued | nothing |
| 4 | every "main now" read is `origin/main` after a fetch; the briefs lose `read-tree`, the push and the pull; `plan.8`'s refusal gone; the card closes at the landing; the design agent's and the operator's cuts from `origin/main`, blueprints included | nothing |
| 5 | waits read `sluice overview --json` for conflicts, blames and `version` | swancloud's bump of sluice on the fleet |
| 6 | `crew status` names a worktree holding a queued branch | sluice's `holds_queued_branch` on the host |
| 1 | bolts on GitHub: the policy's `remote` read, `give` through `branch create`, `land` through `branch delete`, every place from `origin/bolt/<bolt>` | the same sluice bump; the rulesets set; swancloud's part 6 beside it |
| 7 | CLAUDE.md's "This checkout is live" rewritten to the modes; `crew/main` an anchor | swancloud's `crew/live` and mode |

Parts 2 to 4 share `plan.py` with the card series and go after its fourth change lands, before crw-1 is brought back. Each part lands on its own; a crew with parts 2 to 4 and no part 1 keeps bolts local as today. Nothing a team holds in a place changes.

### 2. The anchor is read, never moved

`crew.checkout()` keeps returning `<kit>/main`; `launch` keeps starting a conductor and ops there. Every read of "main now" in `plan.py` becomes a read of `origin/main` after one fetch per command (`bolt-plan` "A command reads each kit and the plan once"): `POLICY` reads `git show origin/main:.config/sluice.toml`; `MAIN` prints `origin/main`'s head and drops `ahead behind`, and `main_held` refuses only when the fetch fails (`read.1`); `BOLT_BRANCH` branches from `origin/main` (part 1 replaces it with sluice's create); `change_folder` reads the archive from `git ls-tree origin/main` and `git show`, not the working tree; `ONTO` and `landed_at` read `origin/main`; the coder's fix prompt says `git merge origin/main`; the design agent's and the operator's briefs say `worktree add -b <branch> <place> origin/main`, and the design agent's says the same for blueprints, which gets a sluice policy of its own. The decision which ref to read is a function of the kit's name and the command, pinned in `tests/py/test_landing.py` and `tests/py/test_kit.py`; the reads in `tests/contract/test_git.py` against a bare remote. Nothing of crew's runs `read-tree`, `pull`, `merge --ff-only` or `switch --detach` on an anchor: the timer does, and a timer that has not run yet leaves a stale anchor that crew's reads do not depend on.

### 3. The landing

`LANDING` keeps its short-lived `<kit>/places/land-<bolt>` on `bolt/<bolt>`, runs `wt submit main --no-remove` there and removes it; sluice's warning that the folder holds a queued branch is passed through to ops's output and stops nothing. The levelling step is kept behind its existing condition (`symbolic-ref HEAD` is `main`) and prints nothing when the checkout is detached; it is deleted in a later chore once the fleet's doctor shows every anchor detached. `landing_said` keeps reading exit, old and new. The landing record's head is `origin/main` after the submission's fetch. `bolt_land` closes the landing card with "landed on GitHub's main at `<sha>` (#<n>); every host's folder follows by swancloud's timer within minutes", runs sluice's delete (part 1) and tidies. `main-ops.md` *Landing a bolt* loses step 3's push and the box's pull, and its step 2 says sluice lands on GitHub's main with a lease and no host is levelled.

`unit_run` refuses a construct, code or merge start on a bolt whose landing is queued: the decision reads the land rows (`land/<bolt>/<head7>` with a submission recorded and no landing) and is pinned in `tests/py/test_bolt_commands.py`; the refusal names the landing and says the unit starts once it lands or is refused.

### 4. Legacy bolt worktrees

`tidy` finds a `<kit>/bolts/<bolt>` worktree on `bolt/<bolt>` and, when it is clean, runs `git switch --detach` at the bolt's tip in it and says so; dirty, it names it as kept with its uncommitted changes (`plan.10`). The worktree still goes through the kit's remove hooks when the bolt is over (`plan.9`). The decision, detach or name, is a function of the worktree's branch and cleanliness, in `tests/py/test_tidy.py`; the act in `tests/contract/test_wt.py`.

### 5. The overview

`stage_wait` keeps its ten-second poll of refs on the team's host, which tells a merge landed. Each poll also runs `sluice overview --json` there and reads, by facts checked against sluice v0.18.0, the host's (`read.2`): each `branches[]` entry's `version`, which moves on every write to that branch's records, so a poll whose versions are all unchanged reads nothing more; the `id` and `from.path` of each submission in `branches[].submissions[]`, which the wait learns; and each `conflict` or `blamed` line of `branches[].recent[]` recorded since the stage began. Such a line names its submission's `id` and never where it came from, and a submission leaves `submissions[]` the moment it conflicts or is blamed, so the wait matches the line's `id` to a path it learned, and for an `id` it has not learned asks `sluice status <id> --json` once, which prints the submission with its `from.path` from sluice's records without a fetch. Learning alone would miss most conflicts: sluice records one 0 to 3 seconds after its submission (5 of the 6 in mac-studio's crew, swancloud and sluice logs on 2026-10-17: crew #10, swancloud #40 and #58, sluice #40 and #53; sluice #39 took 14 s), inside one ten-second poll, while a blame comes after the checks' minutes. A line whose path is the stage's place is reported to the conductor once a wait, before the wait's answer, in sluice's words as its own overview says the line (`conflict #2 on shared.txt`, `blamed #3 on 3d44d6b`), in place of today's silence until the merge's end. An overview that cannot be read is named once and the wait goes on by refs alone (`read.1`); a submission `sluice status` cannot give is named and taken as no line of the stage's. `crew status` (part 6) lists each `sessions[]` entry carrying `holds_queued_branch` as "`<worktree>` holds `<branch>`, which sluice lands on; check out `origin/<branch>` detached instead", fixing nothing (`read.4`); `board.agent_views` carries it for the conductor's band and `status.js` draws it (`code.8`). The reads are pinned in `tests/py/test_stage_wait.py` on overview and status documents recorded from sluice v0.18.0.

### 6. Bolts on GitHub

`bolt_give` reads `[branches."bolt/*"].remote` from `origin/main`'s policy and refuses with the file and the key when it is absent, as it refuses a policy with no checks; it then runs `sluice branch create bolt/<bolt> --from origin/main` on the team's host, and refuses, naming the version it needs, when the host's `sluice --version` is below the one that has it (`read.1`: a version it cannot read is a refusal too). `make_place` and `PLACE` cut every unit, chore and fix from `origin/bolt/<bolt>` after a fetch, tracking `origin/bolt/<bolt>` so `wt submit bolt/<bolt>` is unchanged. `bolt_land` runs `sluice branch delete bolt/<bolt>` after the plan write and names sluice's refusal (the tip not in main, a submission queued) as `plan.9` names a kept branch; the local `bolt/<bolt>` and its `branch.bolt/<bolt>.crew` mark go as today. A bolt crew made before part 1, local only, is put on GitHub at its tip, `sluice branch create bolt/<bolt> --from bolt/<bolt>`, by the first team read after, which says so; until then sluice refuses a submission to it with "push it there first", which the read turns into that create. crew pushes nothing (`state.5`), and the `bolt/*` ruleset is app-only, set by the user.

### 7. The plugin's modes

CLAUDE.md's "This checkout is live" becomes "How crew reaches a host": `crew/main` is an anchor like any kit's, nobody works in it, and a landing reaches a host by its mode: live, from `crew/live/plugin`, a detached worktree the timer moves, minutes after the landing; released, from swancloud's catalog at the version a bump chore pinned, after a deploy. The after-landing steps go. `tests/t-docs.sh` pins the words. Nothing in `plugin/` changes for the mode: crew's release Action already tags every landing (`code.10`), and the mode is swancloud's.

## Risks / Trade-offs

- A host in live mode is minutes behind a landing where today mac-studio was level at once. Accepted: an agent reads `origin/main` for anything it needs at once, and no agent works in the moving folder.
- Two hosts can queue landings on one bolt in two sluice queues; the lease keeps every landing safe and the first push wins. Accepted until sluice shares its records.
- A bolt with a landing queued cannot take a new unit; a conductor that needs one waits for the landing or asks ops to withdraw it. Accepted: the user chose the refusal over a second submission.

## After deploy

None: every step is code in this change or another kit's, and a host's anchor, mode and sluice version are the fleet's doctor's to show.
