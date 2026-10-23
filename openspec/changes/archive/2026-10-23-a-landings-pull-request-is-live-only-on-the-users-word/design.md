# Design

## Context

A bolt lands by main-level ops's `crew bolt submit <bolt>` on the user's word (`plan.16`, `roles.2`). It runs `LANDING` on the team's host, which runs `wt submit main --no-remove` from `<kit>/places/land-<bolt>` on `bolt/<bolt>`. crew's policy for main has a `[branches.main.pull_requests]` table (`.config/sluice.toml`, reviews 0, checks none), so sluice's submit does not land the branch directly: it pushes the head to `bolt/<bolt>` on GitHub and opens a pull request from it into main, ready for review (`draft: false`), or updates the one already open from that branch, leaving its draft state as it is (sluice `crates/sluice/src/profiles/github/pulls.rs` `open`, `rest.rs` `open`, read at sluice 2e98fbd, 0.36.4 on the hosts).

Before each round on main, sluice's intake lists main's open pull requests (`pulls.rs` `take_in`, sluice ADR 0021):

- it withdraws a queued submission whose pull request is closed, back in draft, or on another head;
- a pull request sent back, blamed or conflicting, is submitted again only on a new head, or once a `ready_for_review` event on GitHub is later than its removal (`Reached::Before` in `crates/sluice/src/lib.rs`; `pulls.rs` `retried`);
- every other open pull request out of draft whose conditions hold is submitted; a draft waits ("waiting: a draft").

The pull request's head ref is the bolt's branch itself. Every merge into the bolt, a team's fix for the refusal most of all, moves it, gives the pull request a new head, and intake submits that head to main with no word of the user's, in the submitter's name (signal 2026-10-23-swancloud-ops-31c1ea3d/01: `bolts-live-on-github` landed as 1c75a9f6, its card never answered). The one state intake never submits is a draft. swancloud-ops marked crew's #99 a draft by hand to stop the same thing (signal 2026-10-23-crw-6-conductor-888a3e7c/01; GitHub's timeline for #99 shows `convert_to_draft` by `afterthought` at 02:28:05Z, read 2026-10-22). #99 and #100 are drafts today.

The landing card already follows the user's word: `landing_held` withdraws it "held for a fix" when a fix starts, and `raise_land` raises it again once the bolt reads proven (record 0031 §1, §3). This change makes the pull request follow the same word.

Rules relied on: `plan.16`, `roles.2`, `roles.3` (a check in crew, not words in a brief), `read.1`, `read.2`, `code.1`, `code.3`, `code.7`, `state.5`, `docs.2`, `tests.4`, `tests.10`, `tests.11`. Area pages touched: `plan.md` (`plan.py`, `kit.py`), `teams.md` (`plugin/bin/crew`'s usage), `tests.md` (`tests/`), `docs.md` (README). `code.8`: nothing the agents' views draw changes, since the pull request's state is no field of the board's.

## Goals / Non-Goals

**Goals:**
- A bolt's landing pull request is ready for review only between ops's `crew bolt submit` on the user's word and that submission's outcome.
- No merge into a bolt can start while its landing pull request is ready.
- The next `crew bolt submit` makes the pull request live again, at whatever head the bolt then has.

**Non-Goals:**
- One landings card per kit, its bolts submitted together (record 0031 as amended 2026-10-23, wldn signal 2026-10-23-wldn-ops-658ea7d1/01): that card is its own unit. This change holds whatever the card is: each bolt's pull request is drafted and readied by the same commands either way.
- Naming the head the user approved in `crew bolt submit`: the submit lands the head the bolt has when ops runs it, as today.
- Changing sluice's intake rule, which is sluice's.

## Decisions

### 1. Draft the pull request; don't close it, don't change sluice

crew marks the pull request a draft wherever the user's word no longer stands, and ready where it does. A draft is the one state sluice's intake reads as "not yet", on every host and at every round, with nothing of crew's running.

Alternatives considered:
- **Close the pull request on a refusal.** sluice's next `open` would make a new one, but a closed pull request loses its history, sluice's comments and the card's link, and a reopen is no different from readying.
- **Withdraw only.** `sluice withdraw` ends one submission; intake makes the next on the next head. It does not hold.
- **sluice opens landings as drafts, or submits a sent-back pull request again only once readied.** That is the right shape for sluice, and it is the user's sluice work, not this unit. crew's draft holds today, and stays correct if sluice changes.
- **Ops drafts by hand, as on 2026-10-23.** A brief's words alone are what `roles.3` rules out.

### 2. Where crew drafts and where it readies

- **The landing's outcome.** `bolt_submit`, once `landing_said` reads the bolt not landed, whether refused, failed, withdrawn, stopped, or crew can't tell, drafts the bolt's open pull request into main before it refuses. On "can't tell", drafting is still right: a landed pull request is merged, so it is not open and nothing is marked.
- **A fix's start.** `landing_held` drafts it as it withdraws the card "held for a fix". A failure here is said on standard error and the fix starts all the same, since the fix is how the bolt is repaired; the fix's merge (below) cannot pass it.
- **Every merge's start.** The unit's merge check (`run_check`, stage merge), the chore's (its check, stage merge) and `fix_cmd`'s merge each draft a ready pull request of the bolt's into main first, and refuse the merge's start when they cannot read or mark it (`read.1`). A unit or chore merges into a bolt with a landing open only when the plan added work to a bolt being landed, but the rule is about every merge into the bolt.
- **The landing's start.** `bolt_submit` readies the bolt's draft pull request into main before `LANDING` runs, and refuses, submitting nothing, when it cannot. sluice's `open` leaves a draft a draft, so without this the submit would wait for ever on "waiting: a draft". Where the head is the one sluice sent back, the `ready_for_review` event is later than the removal, so intake tests the same commits again: the user's word for that head, given again.

There is a window of seconds between sluice's refusal and crew's draft, while `LANDING` returns. A fix's merge takes minutes from its start, and its merge check drafts first, so nothing reaches main in it.

### 3. `gh` on the team's host, only where main takes pull requests

GitHub's REST API cannot mark a pull request a draft; GitHub's CLI does both directions through its GraphQL mutations: `gh pr ready <n> -R <repo>` and `gh pr ready <n> -R <repo> --undo` (gh 2.102.0 on deneb, signed in as `afterthought` with `repo` scope, read 2026-10-22). The pull request is found by `gh pr list -R <repo> --head bolt/<bolt> --base main --state open --json number,isDraft,headRefOid,url`, the same branch sluice's `open` finds it by. crew's kit is public, so drafts are available on GitHub's free plan.

The commands run on the team's host through `crew.on_machine`, where `LANDING`, the fix's start and the merges already act (`code.3`). They run only when the kit's policy at main now (`kit.policy_said`) has a `pull_requests` table under `[branches.main]`, read with `tomllib` (`code.1`); a kit with no such table, or no origin, is asked nothing.

### 4. Decisions are functions; the scripts only report and act

Following `code.7`:
- `kit.takes_pulls(text)`: whether a policy's main takes pull requests.
- `kit.pull_said(code, out, err, repo, bolt)`: what `gh pr list` printed, as the one open pull request `{number, draft, head, url}`, or None for none. It refuses, naming the repository and `gh`'s words, on a non-zero exit, output that is not a JSON list of objects with those fields, or more than one open pull request from the branch (`read.1`, `read.2`).
- `plan.pull_act(pull, want)`: `"draft"`, `"ready"` or None, from the pull request and whether the user's word stands (`want` `"live"` or `"held"`). Nothing is marked when there is none, or it is already as wanted.
- `plan.pull_said(bolt, pull, act, done)`: the words crew says, for the landing's outcome and the refusals.

`PULL` lists and `PULL_MARK` marks, each a short bash script run with the repository, the bolt and the number; they decide nothing.

### 5. What the words say

A landing that did not land ends with: "Its pull request <url> is a draft, so no merge into bolt/<bolt> lands it; the next crew bolt submit <bolt>, on the user's word, makes it live again." When crew could not draft it, the landing's refusal says so first, naming the pull request, `gh`'s words, and the command that drafts it, `gh pr ready <n> -R <repo> --undo`, since the next merge into the bolt would land it. The merge's refusal names the pull request and `gh`'s words. Nothing else is printed when nothing was marked.

### 6. The tests' `gh` is a stub

`tests/stubs/gh` answers `pr list` and `pr ready [--undo]` from a file of pull requests in the test's scratch root, which `tests/lib.sh` writes, logging each call to `$CREW_TEST_LOG`; `gh` joins `tests/run`'s list of commands that must be the stubs, so no test reaches GitHub. The stub `wt-submit` keeps landing directly; the journeys seed the pull request file for the cases that need one.

## Task notes

**1.1** `plugin/lib/kit.py`: `takes_pulls(text)`, true when `tomllib.loads(text)["branches"]["main"]["pull_requests"]` is a table, false for no policy text or no such key, refused on a policy that doesn't parse as the other policy reads refuse. `pull_said(code, out, err, repo, bolt)` as Decision 4. Cases in `tests/py/test_kit.py`: crew's own policy (takes pulls), a policy with no table, none at all, a broken one; gh's list with none, one draft, one ready, two (refused), not JSON, a missing field, a non-zero exit with its words.

**1.2** `plugin/lib/plan.py`: `pull_act(pull, want)` and `pull_said(...)` as Decision 4 and 5; `PULL` (`gh pr list … --json number,isDraft,headRefOid,url`, printing its output and `RC=`) and `PULL_MARK` (`gh pr ready "$n" -R "$repo"`, with `--undo` for a draft, printing `RC=` and gh's last line base64, as `LANDING` prints sluice's); `pull_hold(fleet, t, bolt, want)`, which reads the kit's policy at main now on the team's host, returns at once when it takes no pull requests, lists, decides and marks, and returns (pull, act) or raises the refusal. Cases in `tests/py/test_landing.py`, class `TestThePullRequest`: every row of `pull_act`, and the words of `pull_said` for drafted, readied, nothing to mark and could not mark.

**2.1** `bolt_submit`: `pull_hold(…, "live")` before `LANDING`, refusing with nothing submitted when it raises; after `landing_said` reads not landed, `pull_hold(…, "held")`, its words appended to the refusal, a failure to draft named first as Decision 5 has it. Cases in `tests/py/test_landing.py` on what `bolt_submit` says, and in `tests/t-journey-land.sh`: a conflict leaves the seeded pull request a draft and says so; the next submit readies it before `wt submit` runs (the order read from the calls log); a landing that lands marks nothing; a kit without the table runs no `gh`.

**2.2** `landing_held`: `pull_hold(…, "held")` before the card's close, a refusal printed on standard error naming the pull request, the fix going on. `run_check`'s merge branch, the chore check's merge branch and `fix_cmd`'s merge: `pull_hold(…, "held")` before the stage starts, its refusal the merge's. Cases in `tests/py/test_bolt_commands.py` where these are called with facts, and in `tests/t-journey-units.sh`: a merge into a bolt with a ready pull request leaves it a draft before the merge stage's prompt is sent; a merge whose `gh` fails (the stub told to fail) does not start and names the pull request.

**3.1** README's landing paragraph, `plugin/skills/crew/SKILL.md`'s bolt paragraph and `plugin/bin/crew`'s `crew bolt submit` usage line: a landing that does not land leaves its pull request a draft, a fix or merge into the bolt keeps it one, and the next `crew bolt submit` readies it. `tests/t-docs.sh` stays green.

**3.2** `tests/stubs/gh`, `tests/run`'s guard list, `tests/lib.sh`'s pull request file; then `tests/moon-tasks` and `tests/moon.yml`, since the stubs are inputs of every task (`tests.10`).

## Risks / Trade-offs

- [A team's host has no `gh`, or one not signed in for the kit's repository] → every merge into that kit's bolts and every landing refuses, naming `gh`'s words, rather than going on unheld (`read.1`). Only kits whose main takes pull requests are affected: crew's today, and any wldn kit whose policy has the table, whose host, chuck-herdr-alpha, has not been read for `gh`.
- [GitHub's API is down] → merges and landings in such a kit wait, refused with GitHub's words; sluice's own rounds need GitHub then too.
- [The seconds between sluice's refusal and crew's draft] → no merge into the bolt can start in them, since its start drafts first.
- [Someone readies a draft by hand] → the next move of the branch lands the bolt; that is the user's own act, or a broken brief, and outside what crew holds.
- [Readying at the sent-back head tests the same commits again] → that is the user's word given again, which is what a second submit means.

## After deploy

None: every behaviour is code proved by the logic tier and the journeys, and `gh` on each team's host is the fleet's, already there on deneb. #99 and #100, drafts today, are readied by their next `crew bolt submit` with no step of anyone's.
