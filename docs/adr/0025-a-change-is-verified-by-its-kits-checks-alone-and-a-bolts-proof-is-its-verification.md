---
number: 25
title: A change is verified by its kit's checks alone, which is each kit's own rule, and a bolt's proof is its verification
status: accepted
date: 2026-10-13
decision-makers:
- Chuck Swanberg
---

# A change is verified by its kit's checks alone, which is each kit's own rule, and a bolt's proof is its verification

Status: accepted by the user on 2026-10-13, in the elaboration session ("Yes, accept"), on the words quoted under *Decision outcome* and *Whose rule it is*.

Deciders: the user, in the elaboration session of 2026-10-12 and 13, whose words below are the decision; written by the elaboration session.
Amends: `docs.6`, `briefs.3`, `briefs.1`, `briefs.11` and `plan.16`; record 0012, point 3; record 0006, its consequence on ops's proof; the `bolt-teams`, `main-level` and `rail-cards` specs through the units that build this (`docs.4`).
Sources: `openspec/explorations/what-a-change-holds/reading.md`; OpenSpec 1.14.1's `spec-driven` schema, read from the installed tool; swancloud's `testing.6` and record 0019; sluice's `phase-1-integrations.md` section 3; crew's record 0022; `construct.md`, `ops.md`, `main-ops.md`; the counts of 2026-10-12 in the reading.

## Context and problem statement

A crew change has carried four kinds of verification: the tests its tasks run locally; the kit's suite at the merge gate and as the bolt's verification, outside the change; a *Proof in dev* list in its design, hand steps for the team's ops on a deployed bolt before landing, which `briefs.3` and `construct.md` require and `ops.md` works on `crew prove`; and, for crew itself, which has nothing to deploy, a *Proof on real work* list for main-level ops after landing. Record 0012 moved what must be true after a deploy into code in the change (a doctor row, a service's test) and left the design an *After deploy* list of steps no check can be code, each with a doer. *Proof in dev* came from switchboard's bolts deployed to a dev environment; swancloud's record 0019 since made every deploy a reconcile of main, so its 33 archived lists were hand steps on live hosts, and crew's coder once copied a *Proof on real work* list into the tasks, holding a code stage at 14 of 15.

OpenSpec's own schema says a task "MUST state how to verify completion (a test, command, observable behavior, or delivered artifact)" and tracks only "verification work that can be completed before archive"; a spec's scenarios are ones "that can be tested or explicitly validated". The user, reading the plan's bolt `changes-say-what-is-true-and-what-is-proved` and record 0006: "the ADR talks about "dev proof" and i personally think "dev proof" has no place in an openspec change. openspec is about building functionality. verification should be part of it, but verification should be grounded in what the project does. for my projects that is unit tests run by moon/sluice. this could include integration tests. but proving on dev is outside of the scope of openspec".

**Whose rule it is.** crew's briefs run in every kit: `construct.md` tells each kit's construct "Its tasks carry no proof in dev … listed under *Proof in dev* in its `design.md`", with a task's shape and a *Task notes* section besides, and `briefs.3` is the rule behind it. So a swancloud or switchboard change gets its shape from crew. The user: "I'm confused whether these are Crew's own rules for its open spec or rules that Crew is applying to other projects. I don't know why the fuck we need to get involved in the business of other projects and their open spec". OpenSpec already hands a construct the kit's own `openspec/config.yaml` through `/opsx:propose` and a coder through `/opsx:apply`; swancloud's says how its *After deploy* steps are written, crew's says to cite its rules.

## Decision drivers

- What a change holds is each kit's own rule, said in its `openspec/config.yaml` and its rule pages, which OpenSpec hands its agents; crew reads of a change only what its machinery needs.
- A change's verification should be what the kit itself can run: its checks, in its tiers, through its runner (moon, sluice, the flake check).
- A hand list beside the checks is proof nobody can replay, and it has leaked into tasks.
- crew and flywheel are generic over kits: swancloud deploys a fleet, switchboard a service; a revision may be deployed from main or from a bolt, and the design should not care.
- What a live environment shows is observation, which crew already models as captures and signals.

## Decision outcome

The user: yes, "the kit's checks only"; yes, "the verification is the proof"; yes, "archive at merge". And: "We're thinking about crew and flywheel generically so there could be deployments for swancloud or another system like Switchboard. These deployments could be from main or from a bolt and it really doesn't matter. The point is that a bolt's verifications are things that the kit can verify. The idea of ops tasks might be relevant for both main and a bolt branch and it should be designed so it really doesn't matter." And: "A capture adapter would be connecting to and pulling in operations things. If we had a test environment off of a bolt branch, we would automatically have capture adapters pull in those other operations tasks."

1. **Whose rule.** Points 2 and 3 are crew's rule for crew's own changes, `docs.6` on crew's docs page. Every other kit says in its own `openspec/config.yaml` and rule pages what its changes hold, and OpenSpec's commands hand that to the kit's construct and coder; crew's briefs say nothing of a change's content. crew reads of any kit's change only what its machinery needs: the change's name, which is the unit's (`plan.7`); its tasks' tick boxes, which the stages read; the proposal's `## Touches` block, for forecasts (`teams.12`); and the archive at its merge (record 0006).
2. **What a crew change holds.** Its spec delta says what becomes true, as requirements with scenarios. Its tasks say what the coder builds, and each task names the check that proves it, in the kit's own tiers (a logic or unit test, a contract test, an integration test, an end-to-end test, a doctor row), as OpenSpec's schema asks. Its design says how and why, and lists under *After deploy* only the steps no check can be code, each with its environments and its doer (record 0012, point 3, as it stands). A change holds no proof list of any other name: no *Proof in dev*, no *Proof on real work*.
3. **In a crew change, a scenario no check proves is a missing check, not a hand step.** The change adds the check; swancloud's `testing.6` says the same for swancloud, in swancloud's own words. What no check can do, a reboot, a key only the user can make, is an *After deploy* step with a doer, recorded by the kit's deployer on the deploy. Nothing is worked by ops from the bolt before landing.
4. **A bolt's proof is its verification.** The kit's checks green at the bolt's head: the suite after the last merge, or sluice's verdict on the landing it made. `crew prove`, ops's proof report and its *Left for the user* go; the conductor offers the landing when the verification is green and every unit's latest change has been in a batch (`briefs.12`; amended 2026-10-19 by the user's answer on card req_5ff4d31dc54241c29da8, "Wait for my answer on the batch card": a batch whose card the user has answered); main-level ops reads the verification at the head, not a proof file; the landing card asks only for the landing. A step only the user can do or check is an *After deploy* step on the deploy's card (`plan.14`), never a question on the landing card.
5. **Where a revision is deployed from does not matter.** A deploy is of a revision to an environment the kit gives it, main's head or a bolt's; the kit's after-deploy checks run after any such deploy, and the *After deploy* steps of the changes it carries apply to it and are recorded on it, whichever branch they came from. crew's design says neither that a bolt is deployed before landing nor that it is not; that is the kit's and its deployer's.
6. **What a live environment shows is a capture.** A failed deploy, a red doctor row, a release, anything an environment reports, main's or a bolt's test environment's, reaches crew as a capture through the kit's capture adapters (`signals.6`; swancloud's record 0019 on a failed deploy), lands as a signal and is curated; it is never a proof list someone works.
7. **Archive at merge stands** (record 0006) on its two reasons that remain, a later unit reads true specs and nothing lands open; its consequence that ops reads the proof from the archived change is struck.

### Consequences

- `docs.6` says what a crew change holds, crew's own rule; `briefs.3` says a crew brief names nothing of a change's content beyond what crew's machinery reads, so `construct.md` loses its proof, task-shape and *Task notes* paragraphs and crew's own conventions move to crew's `openspec/config.yaml`, where OpenSpec hands them to crew's agents; `briefs.1` has ops edit no code, deploy nothing and prove nothing; `briefs.11` sends a user's step to the deploy's card; `plan.16` has the conductor post the landing card on the verification. Amended with this record and standing accepted.
- Record 0012, point 3, loses *Proof in dev* and gains point 4's branch neutrality; record 0006 loses its proof consequence. Both amended in this commit.
- The plan's bolt `changes-say-what-is-true-and-what-is-proved` and its unit `a-change-holds-what-is-true-and-what-is-proved` are reworded to this record and gain a second unit, `a-bolts-proof-is-its-verification`: `crew prove` and the proof report go from the command, `ops.md`, `main-ops.md` step 1, `conductor.md`'s landing words, CLAUDE.md's *Proving and landing a bolt*, and the `bolt-teams` ("A bolt is deployed and tested from its branch"), `main-level` and `rail-cards` specs through deltas. `a-merged-change-is-archived` loses "ops's proof reads the archived change" from its intent.
- swancloud and every other kit: nothing of crew's reaches their changes. swancloud's `openspec/config.yaml` and `testing.6` already say its shape; whether to drop *Proof in dev* from its own changes is its design agent's, told of this record.
- Flywheel Next: a claim's scenarios say "how one would know it holds", and a verdict holds evidence; this record is the same stance for crew, that the evidence is the kit's checks.

## Considered options

- **crew's briefs keep telling every kit what a change holds** (today): one shape for kits that differ in what they deploy and how they check; the user's "why the fuck we need to get involved in the business of other projects".
- **Keep *Proof in dev* as prose where a check cannot be code** (`docs.6` before this record): a list nobody can replay, worked by hand from a bolt that record 0019's kits no longer deploy; it leaked into tasks; the user: "dev proof has no place in an openspec change".
- **Tasks name checks, and a short hand list stays for what checks cannot reach:** keeps a proof outside the project's checks for the hard cases; those cases are either a missing check, which the change adds, or an operation, which record 0012 already models as an *After deploy* step.
- **The kit's checks alone** (chosen): the change's verification is what the kit can run and replay; a bolt's proof is the same checks green at its head; operations are steps and captures, not proof.
- **For the archive:** at merge (chosen, record 0006); at landing, which commits on main outside the landing's merge (`state.3`); as chores, a proposal per archive for something with no decision in it.
