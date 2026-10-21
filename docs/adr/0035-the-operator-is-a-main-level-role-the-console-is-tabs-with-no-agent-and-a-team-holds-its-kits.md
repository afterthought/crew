---
number: 35
title: The operator is a main-level role, the console is tabs with no agent, and a team holds its kits
status: accepted
date: 2026-10-20
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# The operator is a main-level role, the console is tabs with no agent, and a team holds its kits

Status: accepted by the user on 2026-10-20, on their own card in their mac-studio session (req_f9bfab48…, "the console change in two steps"; "we need to make the console change first"), as that session relayed it to the planner; the card's full id and text are quoted here once the operator agent brings them.

Deciders: the user, on their card; written by swancloud-design from the relayed text.
Amends: record 0013 (the door); `briefs.6`, `briefs.10`, `teams.2`; the teams file's shape (`crew.py`, a team's `repos`); `crew operator up`.
Sources: the user's card as relayed by chuck@mac-studio through swancloud-planner, 2026-10-20; record 0013; `plugin/roles/operator.md`; `crew.py` `load` (a team's `repos` "two names, its kit then its partition's blueprints repo"); `openspec/specs/operator-agent/spec.md`, `main-level/spec.md`.

## Context and problem statement

The operator agent runs one per host and partition, `<label>-operator-<host>`, in an operator session of its own, started by `crew operator up <label>`, and the flow, rail and board are its session's tabs. Step 1 of the user's change, swancloud's (`feat/deneb-work-sessions`), moves both main levels and deneb's teams into deneb's work sessions and names sessions `<host>-<session>`; after it the operator sessions on each host are the only sessions with no main level in them. A team holds one kit: its `repos` are its kit then its partition's blueprints repo, so a kit two teams should both build, agentplot/weir for slc-1 and flm-1, needs a team of its own, which the user does not want.

## Decision outcome

The user's step 2, crew's, in three parts, one bolt first among the planned:

1. **The operator is a main-level role.** `<label>-operator`, one per partition, runs in the main level's session beside the design agent, the planner, the reviewer and ops, started and ended by `crew main up` and `crew main down`, its brief and its revive following the main level's. Record 0013's door is that one agent: `crew send` delivers to the partition's operator, and an agent that waits on the user tells it.
2. **The console is tabs with no agent.** `crew operator up <label>` becomes `crew console up <label>`: it opens the flow, rail and board tabs in the host's `<label>` session and starts no agent; `crew console down <label>` closes them. swancloud's operator job runs `crew console up`, a swancloud chore.
3. **A team holds its kits.** A team's `repos` are its kits, one or more, then its partition's blueprints repo; a bolt is of one kit, and a team takes a bolt of any kit it holds. slc-1 and flm-1 both hold agentplot/weir.

With the same landing swancloud bumps sluice to 0.32.0 and Claude Code to 2.1.304 on the user's word, chores of swancloud's, not of this record.

## Consequences

- `briefs.6` and `briefs.10` name the partition's one operator; `teams.2` names `crew main up` and `crew console up` where it named an operator agent's up; record 0013 is amended to the one door. Amended in this commit.
- The teams file loses the operator session's part and takes `repos` of two or more; `crew.py` `load` reads it; `crew operator up` goes, `crew console up <label>` and `crew console down <label>` come; `operator.md` becomes a main-level brief; the `operator-agent` and `main-level` specs change through the units that build this.
- One crew bolt for crw-4, first among the planned; a swancloud chore for the operator job.

## Considered options

- **The operator stays one per host in a session of its own** (today): a session per host with an agent that only carries, after step 1 leaves nothing else in it.
- **The operator goes, the user talks to the planner or the design agent:** record 0013's reason stands, one door for whatever comes from outside, and the planner and the design agent are not for carrying.
- **A main-level role, the console tabs on their own** (chosen, the user's): the door is one agent per partition in the session the main level already has; the tabs a person reads need no agent.
- **For kits: a team per kit** (today), which the user declined for weir; **a team holds its kits** (chosen).

## Amendment, 2026-10-20: a main-level role in a session of its own

The user, on their card req_3da02d33 the same day, asked how to balance the partitions' Fable use: "since designer and planner are both fable, it probably is best to split those between both sessions for a given partition", and answered "Yes, so design and planner sit on two accounts"; and in the fleet-releases session, of wldn, "i want to split wldn main as well". So a partition's `roles.<role>` in the teams file may name a `session` of the main level's machine in the partition, and that role runs there, the reviewer beside the planner unless named apart; a dispatcher's can't be named. The main level is a `<label>` workspace in each of its sessions. swancloud's `herdr.3` is amended with it: a role override is a model, an effort or a session.

The user then asked, of proposal 200 that would have built this record's three parts and the amendment as a crew bolt for crw-4: "i don't want to setup the crew to run one change then have to rebuild it. i want you to fix it and close out that proposal". The fleet-releases session built them outside the plan, as four OpenSpec changes archived with their code, and the planner drops proposal 200 with that reason.

