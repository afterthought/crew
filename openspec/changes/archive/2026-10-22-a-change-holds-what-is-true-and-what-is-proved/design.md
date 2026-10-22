# Design

## Context

Record 0025 (accepted 2026-10-13) split one question in two: what any kit's change holds, which is the kit's own rule, and what crew's own changes hold, which is `docs.6`. The rules are already amended (`docs.6`, `briefs.3`, `briefs.1`); the second unit of this bolt, `a-bolts-proof-is-its-verification`, has landed and taken `crew prove`, ops's proof and the landing card's *Left for the user* out of crew. What is left is in `_open.md`: `construct.md` still says "Its tasks carry no proof in dev", a task's shape and *Task notes*, and the results section every brief carries still names "a Proof in dev list".

Read on crew's main on 2026-10-22:

- `plugin/roles/construct.md`, *How a unit works*, two bullets: "**Its tasks carry no proof in dev.** … listed under *Proof in dev* in its `design.md`; the team's ops works that list from the bolt." and "**A task is one sentence saying what must be true, plus a pointer** … under *Task notes* in `design.md`, headed by the task's number."
- `plugin/roles/coder.md`: "Every task is yours; what needs dev is not a task."
- `plugin/lib/crew.py` `RESULTS`: "(a suite you ran, a merge's checks, the bolt's verification, an `openspec validate`, a verify's checks, each item of a Proof in dev list)". Every brief that reports results carries it word for word (`briefs.7`; `tests/t-briefs.sh` checks they match).
- `openspec/config.yaml`: a `context` string, one `rules.design` line (cite rules by id), and two `operations.apply.guidance` lines. Nothing on tasks, specs or proof.
- OpenSpec 1.14.3's project config (`dist/core/project-config.d.ts`): `rules` is a map from an artifact id (`proposal`, `specs`, `design`, `tasks` in `spec-driven`) to lines, which `openspec instructions <artifact>` returns as `rules` and `/opsx:propose` applies as constraints; `operations.apply.guidance` is handed to `/opsx:apply` as advisory guidance. Each kit's own config is read; nothing crosses kits.
- crew's changes already keep the shape `docs.6` asks for in practice (`a-team-is-free-once-its-bolt-is-proven`, archived 2026-10-22): each task ends "Verify `<command>` ends with \"0 failed\"", a last task runs `tests/suite --affected`, a *Task notes* section is headed `**1.1**`, and *After deploy* says "None." with why. Only the brief says it today.

Pages of `docs/architecture/` whose area this touches: `briefs.md` (`plugin/roles/`), `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/`), `docs.md` (`openspec/`). Rules relied on: `briefs.3`, `docs.6`, `briefs.7`, `docs.7`, `tests.10`, `tests.11`, `code.6`.

## Goals / Non-Goals

**Goals:**

- No crew brief names a proof list, a task's shape or a design's sections; the construct brief points at the kit's config instead (`briefs.3`).
- crew's own conventions for its changes are in crew's `openspec/config.yaml`, handed to crew's construct and coder by OpenSpec (`docs.6`).
- Tests pin both, so neither drifts back.

**Non-Goals:**

- Any other kit's config, swancloud's included: record 0025 leaves whether it drops *Proof in dev* to its own design agent.
- `docs/architecture/` and `_open.md`: the design agent clears the not-built clauses of `docs.6` and `briefs.3` after the landing (`docs.7`).
- The archived changes that hold *Proof in dev* or *Proof on real work* lists: they are history.
- A checker that refuses a change whose tasks name no check. `docs.6` rules such a task out; the rule reaches crew's agents through the config, and no record asks crew's machinery to read a change's content (`briefs.3` limits it to name, boxes, Touches and archive).

## Decisions

**1. The construct brief says once that a change's content is the kit's.** The two bullets go, and in their place one bullet in *How a unit works*: what the change holds, its proposal, specs, design and tasks, is the kit's, from OpenSpec's schema and the kit's `openspec/config.yaml`, which `/opsx:propose` hands the agent; crew reads of it only its name, its tasks' boxes, its `## Touches` block and its archive at merge. `briefs.3` allows pointing at the schema and the config, since "the stage's command hands" them. The Touches bullet, the vendor bullet, *Writing a change again* (ticked tasks) and *Committing* stay: they are what crew reads, or how construct works, not a change's shape. "Ending with the tests its change affects green, not the whole suite" is a task's shape, so it leaves the brief for crew's config (Decision 3); another kit's CLAUDE.md and config say how its tests run.

*Alternatives:* keep a one-line "tasks carry no proof in dev" as a guard: still a proof term said to every kit, which `briefs.3` rules out. Say nothing in its place: the construct would still follow the config, since `/opsx:propose` applies it, but a reader of the brief would not know where the shape went.

**2. The coder's and the results section's words.** The coder's sentence becomes "Every task is yours." The results section's list drops ", each item of a Proof in dev list"; it keeps its heading "Test, check and proof results", since a bolt's proof is its verification, which the list already names. One string in `crew.py`, so every brief carrying it changes alike. In the `bolt-teams` spec the results requirement is removed and added again as "A team reports each result on a line of its own, with one glyph", with *A submission still running* in place of *Proof in dev*: OpenSpec 1.14.3's validator refuses a MODIFIED block that omits a scenario the current spec has, so a scenario goes only with its requirement.

**3. crew's config says crew's conventions.** `openspec/config.yaml` gains `rules.tasks`, `rules.specs` and two more `rules.design` lines beside the existing one, and one `operations.apply.guidance` line. The lines are in *Task notes* 2.1, word for word; they are `docs.6` in the shape crew's changes already have. `rules` lines are constraints on the artifact the construct writes; apply guidance is advisory to the coder, which is enough for "tick only when its check passes", since the coder's brief already ticks a task in the commit that does it.

*Alternatives:* put them in `context`, which every artifact gets: the per-artifact `rules` put each line before the agent writing that artifact and nowhere else. A `rules.proposal` line: the Touches block is crew's machinery and stays in the construct brief, which every kit's construct needs.

**4. Tests.** `tests/t-briefs.sh` turns its construct assertion around: the construct brief lacks "Proof in dev", "proof in dev", "Task notes", "one sentence saying what must be true" and "ending with the tests its change affects", and has "openspec/config.yaml" and the Touches block; the coder's lacks "what needs dev"; every brief's results section lacks "Proof in dev". `tests/t-docs.sh`, the test of crew's documentation, reads `openspec/config.yaml` (its `# Reads:` line) and checks it carries each convention; `tests/moon-tasks` then regenerates `tests/moon.yml` (`tests.10`). A grep of the file is the check: crew's Python reads no YAML (`code.1`), and OpenSpec is not on the tests' path.

## Risks / Trade-offs

- A crew construct started before the landing still reads the old brief: it writes a *Proof in dev* "None" at worst, which the config, live at the same commit, already tells it not to. crew restarts agents whose brief changed at their next stop (`teams.19`).
- `operations.apply.guidance` is advisory in OpenSpec: a coder could tick a task whose check it did not run. The coder's brief already has it tick in the commit that does the work, and verify reads the tasks against the code; no new refusal is asked by any record.
- Another kit's construct loses the "affected tests, not the whole suite" line. A kit that wants it says it in its own config or CLAUDE.md; swancloud's CLAUDE.md and config already say how its checks run.

## Migration Plan

Nothing is migrated. Open crew changes keep what they hold; the next construct of each reads the config.

## After deploy

None. crew has nothing to deploy: the briefs and the config are live on each host once its checkout is at main, and the restart of agents whose brief changed is crew's own (`teams.19`). Every scenario is proved by `t-briefs` and `t-docs`.

## Task notes

**1.1** In `plugin/roles/construct.md`, *How a unit works*, delete the bullets beginning "**Its tasks carry no proof in dev.**" and "**A task is one sentence saying what must be true, plus a pointer**". After the bullet beginning "**The user reads it in a batch**", add:

> - **What the change holds is the kit's.** OpenSpec's schema and the kit's `openspec/config.yaml`, which `/opsx:propose` hands you, say what its proposal, specs, design and tasks hold: follow them. crew reads of the change only its name, its tasks' boxes, its `## Touches` block and, at merge, its archive.

Leave every other bullet. Then `tests/t-briefs.sh`: replace the line `expect_ok crewpy brief swb-1 construct; has "$out" "ending with the tests its change affects green, not the whole suite, which the merge gate runs"` and the `lacks "$out" "ending with the suite green"` after it with a construct block that has `"openspec/config.yaml"` and `"## Touches"` and lacks `"Proof in dev"`, `"proof in dev"`, `"Task notes"`, `"one sentence saying what must be true"` and `"ending with the tests its change affects"`; the `ok` line after it then names only the coder and verify, and a new `ok` says the construct brief leaves a change's content to the kit's config. Run `tests/suite t-briefs`.

**1.2** In `plugin/roles/coder.md`, "Every task is yours; what needs dev is not a task." becomes "Every task is yours." In `plugin/lib/crew.py` `RESULTS`, "a verify's checks, each item of a Proof in dev list)" becomes "a verify's checks)". In `tests/t-briefs.sh`: the coder's brief lacks `"what needs dev"`; in the results loop (the one cutting `## Test, check and proof results` from six briefs), `lacks "$cut" "Proof in dev"`. Run `tests/suite t-briefs`.

**2.1** `openspec/config.yaml` becomes, beside its `context`, which is unchanged:

```yaml
rules:
  specs:
    - "Each scenario is one a check in crew's tiers proves. A scenario no existing check proves is a check this change adds, in its tasks; never a step done by hand."
  design:
    - "Cite by id the rules in docs/architecture/ that this design relies on, and name each page of docs/architecture/ whose area the change touches. Where the design departs from a rule, name the rule and say why."
    - "A task's full brief goes under a closing *Task notes* section, each headed by its task's number in bold (**1.1**): the files, the functions, the cases."
    - "The design holds no proof list of any name, no *Proof in dev*, no *Proof on real work*. What must be true after a deploy is code in this change. *After deploy* lists only the steps no check can be code, each saying why, with its environments and its doer, an agent with the condition it waits for, or the user; where there are none it says None and why (docs.6)."
  tasks:
    - "Each task is one sentence saying what must be true, a pointer to its reasoning (design, its Decision; Task notes n.n), and the check in crew's tiers that proves it: `Verify <command> ends with \"0 failed\"` or `passes <test file>`, the logic tier (`tests/suite logic`, tests/py/), the contract tier (`tests/suite contract`), an end-to-end test by name (`tests/suite <name>`) or the mod's cases (`tests/suite mod`)."
    - "Every task is one the coder does and proves in its worktree. No task is a deploy, a step on a live host, a step only the user can do, or work done after the landing."
    - "The last task runs the tests the change affects, `tests/suite --affected`, never the whole suite, which sluice runs at the merge."
```

and `operations.apply.guidance` gains, as its first line: `"Tick a task only once the check it names passes, run as the task names it."` Check the config is read whole: `openspec instructions tasks --change a-change-holds-what-is-true-and-what-is-proved --json` shows the three tasks rules under `rules`, with no warning on stderr.

**2.2** `tests/t-docs.sh`: add `openspec/config.yaml` to its `# Reads:` line, and one block reading `$CREW/openspec/config.yaml` that has each of: `"the check in crew's tiers that proves it"`, `"tests/suite --affected"`, `"*Task notes*"`, `"no proof list of any name"`, `"*After deploy* lists only the steps no check can be code"`, `"is a check this change adds"`, `"Tick a task only once the check it names passes"`; then an `ok` naming crew's conventions in its config (`docs.6`). Extend the comment at the top to say so. Run `tests/moon-tasks` and keep the regenerated `tests/moon.yml`; then `tests/suite t-docs`.

**3.1** `tests/suite --affected`.
