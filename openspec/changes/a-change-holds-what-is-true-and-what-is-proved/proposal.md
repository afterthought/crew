# Proposal

## Why

crew's construct brief runs in every kit, and it still tells each kit's construct what its change holds: tasks that "carry no proof in dev", a *Proof in dev* list in the design that the team's ops works from the bolt, a task's one-sentence shape and a *Task notes* section. The coder's brief says "what needs dev is not a task", and the results section every brief carries counts "each item of a Proof in dev list". Record 0025, accepted by the user on 2026-10-13, decides that what a change holds is each kit's own rule, said in its `openspec/config.yaml`, which `/opsx:propose` and `/opsx:apply` already hand the kit's agents; that a crew change is verified by crew's checks alone, each task naming its check, with no proof list; and that crew reads of a change only what its machinery needs (`briefs.3`, `docs.6`). The user: "I don't know why the fuck we need to get involved in the business of other projects and their open spec".

## What Changes

- The construct brief loses its paragraphs on proof in dev, a task's shape and *Task notes*. It says instead, once, that what a change holds is the kit's, from OpenSpec's schema and the kit's `openspec/config.yaml`, which `/opsx:propose` hands it. What crew reads of a change stays in it: its name, which is the unit's; its tasks' boxes; its `## Touches` block; and its archive at merge.
- The coder's brief no longer says "what needs dev is not a task".
- The results section every brief carries no longer names a *Proof in dev* list.
- crew's own `openspec/config.yaml` gains crew's conventions for crew's changes, `docs.6` in crew's words: each task one sentence naming the check in crew's tiers that proves it, with a pointer to its reasoning; the tasks ending with the tests the change affects, not the whole suite, which sluice runs; a task's full brief under *Task notes* in the design, headed by its number; no proof list of any name; *After deploy* only for a step no check can be code, with its environments, its doer and why; a scenario no check proves is a check the change adds. `/opsx:apply` is told to tick a task only when the check it names passes.
- The briefs' test and the docs' test pin both: no brief names a proof list, a task's shape or *Task notes*, and crew's config says crew's conventions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a construct's brief says nothing of a change's content beyond what crew reads, and a crew change takes its conventions from crew's `openspec/config.yaml`; the results requirement stands again under a new name without its *Proof in dev* scenario, since OpenSpec drops a scenario only with its requirement.

## Impact

- `plugin/roles/construct.md`, `plugin/roles/coder.md`, `plugin/lib/crew.py` (the `RESULTS` text only).
- `openspec/config.yaml`: new `rules` for `tasks`, `design` and `specs`, and one more `apply` guidance line. Every crew construct and coder reads them from the next stage on; no other kit's agents see them.
- `tests/t-briefs.sh`, `tests/t-docs.sh` and, since `t-docs` comes to read `openspec/config.yaml`, `tests/moon.yml`.
- Every other kit: its construct no longer hears crew's *Proof in dev* or task shape; what its changes hold is its own config's, as swancloud's already says.
- Not here: `docs/architecture/` and `_open.md`, whose not-built clauses for this unit (`docs.6`, `briefs.3`) the design agent clears after the landing (`docs.7`).

## Touches

```
plugin/roles/construct.md
plugin/roles/coder.md
plugin/lib/crew.py
openspec/config.yaml
tests/t-briefs.sh
tests/t-docs.sh
tests/moon.yml
```
