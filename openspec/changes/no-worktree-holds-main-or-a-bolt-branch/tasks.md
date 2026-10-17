# Tasks

Parts in build order; each part is its own unit and lands on its own. Parts 2 to 4 go after the card series' fourth change lands and before crw-1 is brought back; parts 1 and 5 after swancloud bumps sluice on the fleet; part 6 once sluice's `holds_queued_branch` is on the host; part 7 with swancloud's `crew/live` and mode.

## Part 2. Legacy bolt worktrees

- [x] 2.1 `tidy` detaches a `<kit>/bolts/<bolt>` worktree on `bolt/<bolt>` at the bolt's tip when it is clean, saying so, and names it as kept when dirty; the decision is a function of the worktree's branch and cleanliness. Logic: `tests/py/test_tidy.py`, the two scenarios of "crew removes only its own worktrees" for a legacy worktree. Contract: `tests/contract/test_wt.py`, a clean worktree detached and a dirty one left (`plan.9`, `plan.18`, `read.4`).

## Part 3. The landing folder, the levelling step, the unit refusal

- [x] 3.1 `LANDING` keeps `places/land-<bolt>` on `bolt/<bolt>`, passes sluice's checkout warning through, levels the main checkout only while it is on branch `main` and prints nothing when it is detached; `landing_said` is unchanged. Logic: `tests/py/test_landing.py`, "The anchor is detached". Contract: `tests/contract/test_git.py`, a landing against a detached checkout leaves it untouched. Journey: `tests/t-journey-land.sh` (`plan.16`, `plan.18`).
- [ ] 3.2 `unit_run` refuses a construct, code or merge start on a bolt whose landing is submitted and not yet landed or refused, naming the landing; the decision reads the land rows. Logic: `tests/py/test_bolt_commands.py`, "A unit during a queued landing". Journey: `tests/t-journey-land.sh` (`plan.8` as amended).

## Part 4. Main is read by ref

- [ ] 4.1 `POLICY`, `MAIN`, `main_held`, `BOLT_BRANCH`, `change_folder`, `ONTO` and `landed_at` read `origin/main` after one fetch per command; the behind-GitHub refusal goes and `main_held` refuses only a fetch that fails; the landing record's head is `origin/main`'s. Logic: `tests/py/test_landing.py` "The host's main lags GitHub's", `tests/py/test_kit.py` the policy read by ref, `tests/py/test_bolt_commands.py`. Contract: `tests/contract/test_git.py` against a bare remote whose main is ahead of the local branch (`plan.8`, `plan.18`, `read.1`).
- [ ] 4.2 `bolt_land` closes the landing card with "landed on GitHub's main at `<sha>` (#<n>); every host's folder follows by swancloud's timer within minutes". Logic: `tests/py/test_landing.py`, the card's close. Journey: `tests/t-journey-land.sh` on the stub pendingyou (`plan.16`).
- [x] 4.3 `main-ops.md` *Landing a bolt* loses the push, the levelling and the box's pull; `coder.md`'s fix merges `origin/main`; `design.md` and `operator.md` cut their branch from `origin/main`, blueprints included, and `design.md` loses the `read-tree` step; `conductor.md` says the bolt is read by ref. Journey: `tests/t-briefs.sh` pins the words (`briefs.11`, `state.3` as amended).
- [ ] 4.4 README, `plugin/skills/crew/SKILL.md` and `crew`'s usage header say a landing pushes nothing and levels no host. Journey: `tests/t-docs.sh` (`docs.2`).

## Part 5. The overview

- [x] 5.1 `stage_wait` reads `sluice overview --json` on each poll beside the refs, reads nothing more while every branch's `version` is unchanged, learns the `from.path` of each submission `submissions[]` lists, asks `sluice status <id> --json` once of a `conflict` or `blamed` line since the stage began whose `id` it has not learned, since sluice records a conflict within seconds of its submission, reports a line whose submission came from the stage's place to the conductor in sluice's words, and goes on by refs alone, saying so once, when the overview cannot be read; every field is read by a fact checked against sluice v0.18.0. Logic: `tests/py/test_stage_wait.py` on overview and status documents recorded from sluice v0.18.0. Journey: `tests/t-journey-units.sh` with a stub sluice (`read.2`, `code.9`).

## Part 6. A stray checkout is named

- [ ] 6.1 `crew status` lists each overview `sessions[]` entry carrying `holds_queued_branch` as a worktree holding a branch sluice lands on, with the detached checkout to use instead, and fixes nothing; `board.agent_views` carries it for the conductor's band and `status.js` draws it. Logic: `tests/py/test_slots.py` (the status read), `tests/py/test_board.py` (the views' keys). Mod: `plugin/tests/` through `tests/mod` (`read.4`, `code.8`).

## Part 1. Bolts on GitHub

- [ ] 1.1 `bolt_give` reads `[branches."bolt/*"].remote` from `origin/main`'s policy and refuses without it, naming the file and the key; refuses, naming the version, when the host's sluice lacks `branch create` or its version cannot be read; otherwise runs `sluice branch create bolt/<bolt> --from origin/main` on the team's host and records the give. Logic: `tests/py/test_bolt_commands.py`, the three refusals and the create. Contract: `tests/contract/test_kit.py`, the policy's remote read. Journey: `tests/t-journey-teams.sh` with a stub sluice (`plan.19`, `plan.17`, `read.1`).
- [ ] 1.2 `make_place` and `PLACE` cut every unit, chore and fix from `origin/bolt/<bolt>` after a fetch, tracking it. Contract: `tests/contract/test_git.py`, a place cut from a remote bolt ahead of the local branch. Journey: `tests/t-journey-units.sh` (`plan.19`, `teams.3`).
- [ ] 1.3 `bolt_land` runs `sluice branch delete bolt/<bolt>` after the plan write, names a refusal with sluice's words and keeps the local branch as `plan.9` has it. Logic: `tests/py/test_landing.py`, "A delete sluice refuses". Journey: `tests/t-journey-land.sh` (`plan.19`).
- [ ] 1.4 A team read finds a bolt of the kit that is local only while the policy names a remote, runs the create at its tip and says so. Logic: `tests/py/test_tidy.py`. Journey: `tests/t-journey-teams.sh` (`plan.19`).
- [ ] 1.5 `tests/lib.sh` `kit()` gives each scratch kit a bare remote standing for GitHub with its bolt policy naming `remote = "origin"`, and the stub sluice answers `branch create`, `branch delete` and `overview`. Journey: every `t-journey-*.sh` on the new fixture (`tests.10`), `tests/moon-tasks` run and `tests/moon.yml` committed.

## Part 7. How crew reaches a host

- [ ] 7.1 CLAUDE.md's "This checkout is live" becomes "How crew reaches a host": `crew/main` is an anchor nobody works in, and a host loads crew's plugin live from `crew/live/plugin` or released from swancloud's catalog; the after-landing steps go; `main-ops.md` loses its crew-specific pull. Journey: `tests/t-docs.sh`, `tests/t-briefs.sh` (`plan.19`, `docs.2`).
