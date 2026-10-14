---
number: 29
title: The run record is read from the flywheel's branch alone
status: accepted
date: 2026-10-14
decision-makers:
- Chuck Swanberg
---

# The run record is read from the flywheel's branch alone

Status: accepted by the user on 2026-10-14 on the record's card (req_ff5d13bda68149289b6b, approved 20:07Z), as `briefs.15` has it. Proposed by swancloud-design the same day, carrying rule `read.5` as proposed on 2026-10-11 (00a0569).

Deciders: the user. Written by swancloud-design.
Amends: `read.5`, from proposed to accepted; at acceptance, `plan.2`'s carry (a flywheel-branch commit carries the host's uncarried run record), which has nothing left to carry, and the reading over ssh in `read.5`'s details.
Sources: signals 2026-10-11-crw-3-conductor-883e3042/01 (a landing on mac-studio refused because macbook-pro did not answer), 2026-10-13-swancloud-planner-2e461542/01 (a wldn conductor's wait could not tell whether a batch was due) and 2026-10-14-swancloud-planner-d0449d0b/01 (`crew review wldn` on chuck-herdr-alpha ran no reviewer and returned an old summary, and three conductors' waits saw the same); `plugin/lib/record.py` `gather` and `hosts_of`; `batch_due` and the landing's guard in `plugin/lib/plan.py`; the user's words of 2026-10-11 quoted below.

## Context and problem statement

A host writes each run-record entry to a local file, and the entries reach the flywheel's branch only when that host's next write to the branch carries them (`plan.2`). So a decision that needs the whole record, the partition's batch clock and a landing's guard among them, reads every host of the partition over ssh for its uncarried entries (`record.gather`), counting a host for holding an operator session alone (`record.hosts_of`), and `read.1` makes it refuse when any host is silent: "crew can't tell which changes have been in a batch: macbook-pro did not answer".

macbook-pro is an operator host of every partition, runs no team, and is asleep or off most of the time. The refusal has held work three times in four days: crw-3's landing on mac-studio on 2026-10-11; a wldn conductor's wait on 2026-10-13, when `crew review wldn` run by hand on the box found the batch due; and on 2026-10-14 wldn's review on chuck-herdr-alpha, which ran no reviewer and returned batch 20's old summary while three conductors' waits said the same. Each time the work was on a host that answered, and the host that did not held nothing the decision depended on.

The user, 2026-10-11: "Hmm this seems like a design issue that we need to talk about. The laptop isn't going to be on most of the time", and "it seems intrusive to be reaching across the hosts over SSH when the design is that we should be looking in Git".

## Decision drivers

- `read.1`: crew refuses rather than guesses, so a host that may be silent must not stand in the path of a decision that does not depend on it.
- `state.1` and `state.4`: the flywheel's state is its branch, read by any clone with nothing running; the record is state.
- An operator host sleeps most of the time; a team's host answers while its team runs. A decision's reach should follow what it depends on, not who is in the partition.
- A reading is as fresh as the last push; a commit per entry costs a push, an ssh per decision costs a host that is awake.

## Decision outcome

`read.5` as written on 2026-10-11: the run record is read from the flywheel's branch alone; every entry reaches the branch as it is written, as its own commit from the host that wrote it; no decision reads a host over ssh for the record; a host is read over ssh only for the stages of its own kits' worktrees, and a host that does not answer hides only the work on it, never another host's landing nor the partition's batch clock.

Plainly: every note crew takes about a run goes to Git the moment it is written, so nothing crew decides needs to call another computer, and a computer that is off hides only its own unfinished work.

`the-run-record-reaches-the-branch-as-it-is-written` is queued in crew on the acceptance, and `plan.2`'s carry clause goes with its build.

## Consequences

- A landing, a batch's reckoning and a review read one branch, on any host, with the laptop asleep.
- The flywheel's branch takes one commit per entry; `state.1`'s fetch, apply and push-without-force absorbs two hosts writing at once, as it does today for every other write.
- `read.3`'s listing still asks every host for the stages of its kits' worktrees and names the silent ones; a silent host's own work reads `unknown` there, never another stage (`read.1`).
- Until it is built, a review or landing stalls while macbook-pro sleeps, and the hand around it is waking the laptop or running `crew review` once it answers.

## Considered options

- **The branch alone, every entry pushed as it is written.** Chosen: it is what the design already says about state, and it takes the silent host out of every decision that does not depend on it.
- **Ask only the hosts the decision depends on, team hosts and not operator hosts.** Rejected: it still reaches across hosts over ssh, which the user named as against the design; an operator session's own entries, the user's approvals among them, would be hidden while the laptop sleeps; and the set of hosts a decision depends on changes with every placement, so the rule would move with the plan.
- **Decide with a silent host's entries taken as absent.** Rejected by `read.1`: it is a guess, and a landing or a batch reckoned without a host's entries would be wrong the moment that host wakes.
- **A service that holds the record.** Rejected by `state.4`: crew runs no service, and the branch is the one place every clone can read.
