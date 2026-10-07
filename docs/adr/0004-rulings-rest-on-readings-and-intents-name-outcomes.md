---
number: 4
title: Rulings rest on readings, and intents name outcomes
status: accepted
date: 2026-10-07
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# Rulings rest on readings, and intents name outcomes

Deciders: the user, through swancloud-operator-mac-studio, on an exchange in wldn's operator pane; swancloud-design.
Sources: wldn-operator's account of the boundary takeover (proposals 84, 90, 93, 103, 125 to 128 on `wldn/main`); wldn-design's and wldn-planner's own words there; swancloud's fix-places bolt, which grew from two units to four in a day with units amended in flight; `plugin/roles/design.md`, `planner.md`, `conductor.md`.

## Context and problem statement

On wldn, the design agent ruled on how a takeover of an AWS boundary should work, step by step, from what it believed about CloudFormation and IAM, within minutes of each conductor's question and without reading the service. The construct then met the real behaviour, and each fact that broke a step produced a new ruling and a new proposal for the user to approve: an import works only on the stack itself; the boundary forbids reading IAM; the live policy already allowed nine services the template did not; an import needs a retain-on-delete policy in the template first; a prerelease cannot rebuild dev. Each was one short check against AWS. The planner, for its part, wrote the mechanism into each unit's intent, so a changed mechanism meant an amended intent, and proposed each correction the minute it arrived. On swancloud the same day, fix-places went from two units to four with several amended mid-flight, from intents that named mechanisms.

wldn's agents wrote the fixes into switchboard-kit and their memories. The user wants them in crew, so that every partition's design agent and planner work this way.

## Decision drivers

- A ruling the construct will build on must be as true as what it rules about; a belief is not a reading.
- The user approves every proposal; corrections that arrive one at a time cost the user a review each.
- The record should say what must be true; how is the construct's, read back from the thing itself.

## Decision outcome

The rules below go into the briefs, and so into every partition's agents at their next fresh start.

### The design agent

- **A ruling names what it rests on.** A ruling about a service's or a system's behaviour names, in the message that carries it, the documentation page or the reading it rests on. Where the design agent has neither, it says so and asks ops for the reading before the ruling reaches any unit.
- **Read the thing itself.** Before ruling about something that exists, the design agent reads it with the credentials it has: the live configuration, the stack, the policy, the code on main.
- **Rule the outcome and the constraints, not the sequence.** The design agent says what must be true and what must not change, and leaves the steps to the construct, which brings its own reading back. A sequence ruled from belief breaks one step per fact.
- **Answer linked questions together.** A construct's related questions are answered as one, after reading, not one at a time as they arrive.

### The planner

- **An intent names the outcome and the records that govern it.** Not the mechanism. The how lives in the design's records, which the construct reads, so a changed mechanism changes no intent.
- **Corrections to a unit under construction are batched.** They go into one amendment when its construct settles, unless a change blocks the team now.

### The conductor

- A construct's related questions go to the design agent together, in the words of whoever asked, and the answer comes back to the construct with the reading it names.

### Consequences

- One unit in crew amends `design.md`, `planner.md` and `conductor.md`; the kit-level rule wldn wrote in switchboard-kit can then go, or stay as that kit's restatement.
- The design agents' own intents follow the planner's rule when they queue work: outcome and record, not mechanism.

## Considered options

1. The rules in crew's briefs, for every partition.
2. The rules in each kit's constitution, as wldn did, and in each agent's memory.

Option 1. A kit's constitution governs changes to that kit; how a design agent rules and how a planner writes an intent are crew's roles, the same in every partition, and a memory lasts one agent's life.
