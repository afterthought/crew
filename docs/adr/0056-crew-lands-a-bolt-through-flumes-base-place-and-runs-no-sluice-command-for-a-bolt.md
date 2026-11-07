---
status: accepted
date: 2026-11-07
decision-makers: the user (crew no longer submits to sluice); the design agent (what crew asks of Flume and reads from it)
---

# 0056. crew lands a bolt through Flume's base place, and runs no sluice command for a bolt

Status: accepted by the user on 2026-11-07, in agentplot-design's pane: "For 56, yes."

Deciders: the user, 2026-11-07, in agentplot-design's pane, after a bolt's landing card had agentplot-ops run `sluice submit` by hand, relayed by agentplot-design through the operator: "I want to make sure that the changes required to retrofit crew are part of all of that because crew would no longer have to be submitting to sluice". That crew stops submitting to sluice is theirs. What crew asks of Flume in its place, and what it reads, is the design agent's, on Flume's statement as written.

Amends the rules `plan.8` and `plan.19`, each from the release that carries the unit below; `state.5` stands as written, since crew still pushes only to its state branch. Sources: agentplot/blueprints `design/flume/requirements.md` 202 to 204 (a bolt's branch is a base place: Flume asks the merge queue to make it at launch, places are cut from it and land on it, and it is submitted only on its caller's retry naming the submission, the outcome read from the merge queue and delivered to its recipients); agentplot/sluice record 0093 (sluice starts its own host process when work arrives, so nothing waits on a driver); agentplot-design's message of 2026-11-07.

## Context and problem statement

crew makes a bolt's branch with sluice's `branch create`, lands it with `crew bolt submit`, a `sluice submit` of the branch to main, waits on it with `sluice wait`, reads missed outcomes with `sluice inbox`, and ends the branch with `branch delete` (`plan.8`, `plan.19`). Flume now carries a branch that work lands on, and that lands on another, as a base place: it makes the branch through the merge queue, cuts the units' places from it, and submits it on its caller's word. Two tools each driving the same branch's landing is how a landing card ended with an operator running `sluice submit` by hand.

## Decision

1. **The user's: crew runs no sluice command for a bolt.** It makes no bolt branch, submits none, waits on none, reads no sluice inbox for one and deletes none. Flume does each through the merge queue.
2. **A bolt is a base place of Flume's.** Its launch, on main, makes its branch; every unit, chore and fix of the bolt is a place whose base is the bolt's branch. crew reads the bolt's head, its places and its submission from Flume, never from sluice.
3. **A bolt lands on the user's send by Flume's submission of its base place.** Main-level ops's landing asks Flume to submit the bolt's base place (a retry naming the submission), and crew reads the landing, a failure or a conflict from what Flume delivers and holds. A conflict is mended as Flume's statement has it: a place on the bolt takes main in, then the submission is asked again. A landing card, its send and its close follow Flume's outcome alone.
4. **Until the release that carries this, crew lands as it does today.** Nothing in this record is true of a host before its crew carries the unit. That unit is ordered after a Flume release with base places.

## Considered options

- **Flume's base place lands the bolt, crew asks and reads (chosen).**
- **crew keeps submitting the bolt to sluice beside Flume's places.** Not taken: the user's words; and two tools driving one landing is the defect that brought it.
- **crew drives sluice through Flume's places alone, making the bolt's branch itself.** Not taken: the branch would still be crew's sluice command, and Flume's base place already makes it.

## Consequences

- One crew unit, on the user's yes and after the Flume release: `crew bolt submit` and its land path, and main-level ops's landing steps, ask Flume and read Flume, with no sluice command for a bolt (swancloud-planner names it `crew-lands-a-bolt-through-flumes-base-place`).
- Boomdrive's runner carries a bolt as a launch (agentplot/boomdrive's unit `a-bolt-is-a-launch`), so crew's launch of a bolt reaches Flume as any work does.
