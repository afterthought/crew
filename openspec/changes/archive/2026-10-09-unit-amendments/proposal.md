# Proposal

## Why

A unit that is already in a bolt sometimes has to change: the user sees something while it is being coded, a stage finds the change was wrong about how to build it, or what the unit should build turns out to be different. crew has one path for this, and only early: while a unit is in review the conductor runs construct again with the user's words. Once the unit is approved or in code, construct is refused, there is no command that changes a unit's intent at all (only `crew unit split`, which narrows it), and nothing makes a rewritten change come back to the user before it is built. The user named this gap when answering the findings-to-design proposal: "we might not even be accounting for the use case of making a change to an existing unit in a bolt."

This change gives a unit in flight two ways to be amended, both ending in the user's review of its change. It is step 4 of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, "Changing a unit already in the plan"; `roadmap.md`), and `blocking-findings` builds on it.

## What Changes

- **Amending a unit's change.** `crew unit run <unit> construct "<the user's words>"` is accepted at any stage before the unit has merged, where today it is refused once the unit is approved. Run on a unit that is approved, in code or in verify, it marks the unit amended in the plan.
- **Amending a unit's intent.** A new plan command, `crew unit amend <unit> "<new intent>"`, replaces a unit's intent. For the planner it exists only inside a proposal, so the user approves it and, for a bolt in flight, the conductor agrees to it first. A unit that has a worktree is marked amended, and crew tells its conductor to run construct again.
- **An amended unit waits for the user.** While a unit is marked amended, its stage reads `amended` until construct has been run again, then `construct` until that stage commits, then `review`; code, verify and merge are refused; and `crew unit approve` clears the mark. So a rewritten change is always reviewed again before it is built, whatever its tasks say.
- **A proposal shows an amendment as before and after**: the intent as it stands and as it would be, the unit's stage, and what approval sets in motion.
- A unit that has merged is not amended: that is a fix, or a new unit.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-plan`: a unit's intent can be amended; an amended unit's stage; the approval that clears the mark.
- `bolt-teams`: construct can be run again on a unit in flight, which then waits for the user's review.
- `plan-proposals`: a proposal can hold `unit amend`, and shows it as before and after.

## Impact

- `plugin/lib/plan.py`: `unit amend` (its checks, change and after-effects), the `Amended` mark in the plan's schema, the stage rule, `run_check` for construct and the refusals for code, verify and merge, `unit approve` clearing the mark, the role table (`unit amend` is the planner's by proposal, the user's directly).
- `plugin/roles/conductor.md` (amending a unit, and an amendment arriving from an approved proposal), `plugin/roles/planner.md` (`unit amend` in a proposal), `plugin/roles/construct.md` (writing a change again for an amended intent).
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/`.
- Depends on `plan-proposals`.

## Touches

`plugin/lib/plan.py`, `plugin/bin/crew`, `plugin/roles/conductor.md`, `plugin/roles/planner.md`, `plugin/roles/construct.md`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`.
