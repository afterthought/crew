---
number: 13
title: A partition's operator agent is its front door for anything sent from outside
status: accepted
date: 2026-10-08
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A partition's operator agent is its front door for anything sent from outside

Deciders: the user, through swancloud-operator-mac-studio ("In Flywheel, the dispatcher is the agent you talk to to send things to. In crew, it's not clear how I should send something between teams", signal 2026-10-08-swancloud-operator-mac-studio-5fda4ef7/01); swancloud-design.
Sources: `plugin/roles/operator.md` (the operator "carries each request to the agent whose job it is"); `openspec/specs/main-level/spec.md` (a dispatcher gives its host's teams their bolts and drives no unit; the design agent elaborates; the planner plans); `plugin/roles/conductor.md` ("Your job is narrow on purpose"); the roster crew fills into every brief (`crew.py`, `ROSTER`); Flywheel Next's dispatcher, per the user.

## Context and problem statement

A session on the box, asked to send findings to swancloud's crew, offered to send them to the conductors. Nothing in the briefs says who receives a message meant for another team or another partition. Conductors are narrow by design; the dispatcher in crew is one per host and partition and is about bolts, not messages; the design agent takes design questions and the planner work. Flywheel Next has one answer, the dispatcher, because its dispatcher is the agent the user talks to.

## Considered options

1. The partition's operator agent: it already works for the user and carries each request to whose job it is.
2. The dispatcher, as in Flywheel.
3. The design agent, since what crosses a partition is mostly findings and questions.
4. The conductors, as the session offered.

## Decision outcome

Option 1. **Anything sent to a partition from outside it, by the user, by a session of another partition or by a team of another partition, goes to that partition's operator agent**, which carries it on: a finding becomes a signal it records, a design question goes to the design agent, work to the planner, a message for a team to its conductor. A partition with operator agents on several hosts is reached through the one on the sender's host when it has one there, else through the one on the partition's main-level host. Every brief's roster names it, so no agent has to guess; the dispatcher keeps its job, bolts on its host, and a conductor is never the door.

Consequences: rule `briefs.10`; one unit, `a-partitions-operator-agent-is-its-front-door`, in the roster crew fills into every brief and in the operator's own brief.
