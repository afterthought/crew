---
status: proposed
date: 2026-11-04
decision-makers: the user (the rename and its names); the chore flywheel-is-renamed-boomdrive (the record, and how crew carries it)
---

# 0054. Flywheel is renamed Boomdrive, and crew's flywheel is a drive

Status: proposed. The rename and its names are the user's decision, in their words below; how crew carries them is the chore's choice, made on the written rules. The record is accepted on the user's yes once they have seen it as a record (`briefs.15`).

Deciders: the user, 2026-11-04, in the brief of the chore `flywheel-is-renamed-boomdrive`, run in every repository at once: "the ecosystem, the org, the branding, the cloud and the opensource runner tool are all boomdrive. There is also a "boom" open source tool that does the claim reconciliation." They approved **drive** for a customer's unit of work, "a Flywheel", as ubiquitous language, the interface's words and the code's the same, and ruled that crew's word for a partition's state branch follows it. They asked that the same pass spell the word enroll, enrolls, enrolled, enrolling and enrollment.

Amends, in names alone and never in what they decide: the rules `state.1`, `state.4`, `roles.5`, `roles.9`, `read.5`, `plan.2`, `plan.11`, `plan.13`, `signals.1` and `signals.6`, each marked with this record; records 0001, 0002, 0006, 0010, 0013, 0016, 0017, 0018, 0019, 0023, 0024, 0025, 0026, 0029, 0038, 0039, 0044, 0045, 0046, 0047 and 0052, the files of 0029 and 0047 renamed with them; the spec `flywheel-state`, now `drive-state`, and every spec that names a flywheel; the open changes, the explorations, README, the briefs, the skill, the usage, the code and the tests. Sources: the user's words above; the names GitHub gives the repositories on 2026-11-04; agentplot/boomdrive's record 0016 and swancloud's record 0048, the same rename in the runner and the fleet.

## Context and problem statement

crew used the word twice. Flywheel was the product crew was meant to become and the model it aligned with: "crew becomes flywheel, which composes sluice's SDK" (record 0026), Flywheel's rail, its chores, its layout. And a partition's **flywheel** was its loop, named by its label, its state the branch `<label>/main` of its state repository: "the flywheel's branch", which every rule on writes, the plan and the run record names. It also named the runner, agentplot/flywheel-runner, whose rules `runner.py` cites, and Tailrace among the tools crew wraps (`roles.5`).

## The names

| was | is |
|---|---|
| Flywheel, the product, brand and ecosystem, and the family of open tools on its sites | Boomdrive |
| Flywheel Cloud, agentplot/flywheel-cloud | Boomdrive Cloud, agentplot/boomdrive-cloud |
| the runner, agentplot/flywheel-runner, its command `flywheel` and its rules `flywheel-runner core.<n>` | Boomdrive, agentplot/boomdrive, `boomdrive` and `boomdrive core.<n>` |
| the runner's file `~/.config/flywheel/config.toml` | `~/.config/boomdrive/config.toml` |
| agentplot/flywheel-web | agentplot/boomdrive-web |
| Tailrace, agentplot/tailrace | Timber, agentplot/timber |
| a Flywheel, a customer's unit of work, and Boomdrive Cloud's Durable Object class `Flywheel` | a drive, drives, and `Drive` in code |
| crew's flywheel, a partition's loop, and the flywheel's branch, `<label>/main` | the drive, and the drive's branch |
| the spec `flywheel-state` | `drive-state` |
| the declaration's future name `flywheel.toml` (record 0023) | `boomdrive.toml` |
| the runner's mark `flywheel:<partition>/<n>` | `boomdrive:<partition>/<n>` |
| enrol, enrolment | enroll, enrollment |

boom keeps its name, and so does anything third-party that says flywheel. agentplot/flywheel, the original, is archived; crew names it nowhere. crew has no class of its own named for the unit and no rule that a class is never renamed, so `Drive` needs nothing here.

## Considered options

For agentplot/flywheel-next and its design, which crew calls Flywheel Next:

1. Keep the name wherever it names that repository or its design, as the runner's record 0016 and swancloud's record 0048 do. Chosen: GitHub still gives it that name, and the rename leaves it as it is.
2. Rename it Boomdrive Next. No repository has that name, so every source cited by it would point nowhere.

For the capability `flywheel-state`:

1. Rename its folder `drive-state`, its requirements' and scenarios' words with it, in place. Chosen.
2. Keep the folder's name and rename only its words, which leaves a live capability named by the retired word.

Renaming a spec in place departs from `docs.4`, which changes a spec only through a delta of the change that builds it: the rename changes no requirement's behaviour, only its names, on the user's word, and this chore renames the code those specs describe in the same commit.

For the records' file names, 0029 and 0047's: renamed with their titles, since records are cited by number and no live file names either file; keeping the old names was the other path.

## Decision outcome

The names are the table's. A product's name becomes Boomdrive wherever crew writes it, Flywheel's rule or rail among them; crew's word for a partition's loop becomes drive wherever crew writes it, in prose, code, test names and fixtures.

- **crew's own words.** `crew state init` commits "start the drive's plan"; a signal landed without a label is refused asking "which partition's drive?"; a start or a fix with no runner to take it names the runner as Boomdrive.
- **Nothing in crew's interface with the runner changes.** crew reads no mark of the runner's and no author of its commits, so the runner's `boomdrive:<id>` and `boomdrive@<host>` need nothing here; `requests.rec`, `<label>/runner/<host>` and every file on the drive's branch keep their names.
- **What keeps its text.** The archived OpenSpec changes, the archived change `machine-captures-land-on-the-flywheels-branch` named among them; the user's own words wherever they are quoted; Flume 0.3.6's answers under `tests/py/flume-0.3.6/`, what Flume printed byte for byte, holding the runner's checkout folder `flywheel-runner`, which the hosts' change keeps, and the words of the runner's tasks; Flywheel Next's own words, `<instance>/flywheel-state` and "which its surfaces call a flywheel"; and the names of other repositories' files and work as they were read: the blueprints' `books/flywheel/` and `.lavish/tailrace-end-state.html`, and the bolt `tailrace-sync-and-serve`.

## Consequences

- A reader of the rules and records reads the new names; the decisions they hold are unchanged, and each changed rule says so.
- The rename lands on `teamless/deneb`, where crew's own work lands until that branch goes back into main (the user, 2026-11-03); main, and the box's release of crew, keep the old words until then.
- No folder on a host moves here: the hosts' checkouts are swancloud's change.
