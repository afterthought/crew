---
name: constitution
description: Write a kit's constitution — the falsifiable rules every change to the repository holds to, as an always-loaded core page plus area pages that load by path, with ADRs for the decisions behind them — and wire it into the agents' sessions. Use when asked to write, start, mine, extend or wire in a constitution, core rules, area rules or architecture rules for a repository, or to repeat for another kit what was done for one.
---

# Writing a kit's constitution

A constitution is the set of rules an agent must not break when it changes a repository, written so a reviewer can point at a diff and say which rule it breaks. It sits beside the narrative design (a book or a spec folder) and does not repeat it: the narrative says why and how things work, the constitution says what must stay true.

It lives in the kit:

| Path | What it holds | How it reaches a session |
|---|---|---|
| `docs/architecture/core.md` | The rules that bind wherever a change is made, and an index of the area pages | `CLAUDE.md` imports it, so every session in the kit has it |
| `docs/architecture/<area>.md` | The rules that bind one area, with `paths:` frontmatter | A symlink in `.claude/rules/` loads it when the session reads a file under its paths |
| `docs/architecture/_open.md` | Decisions waiting and code that stands against a rule | Read on demand; deleted when empty |
| `docs/adr/NNNN-<title>.md` | One record (MADR) per decision a rule rests on | Named by the rule's source |
| `openspec/specs/` | What each capability does | OpenSpec, unchanged |

If a sibling kit already has a constitution, read its `docs/architecture/` and `docs/adr/` first. It is the model for layout and wording, and the baseline: mine only what this kit adds or does differently.

## 1. Mine candidates

Run three read-only subagents in parallel, each writing to the scratchpad. Each candidate is one sentence a diff could break, tagged `core` or `area:<name>`, with its sources (commit shas, file and section, change name).

1. **Fix history.** `git log --grep='^fix'` plus active and archived OpenSpec changes whose names state a rule. A fix whose subject generalizes is a candidate; three fixes for the same mistake make it a strong one.
2. **Documents.** `CLAUDE.md` files and their gotchas, the spec folder and its contracts, the kit's book, research notes, principle pages.
3. **Mockups.** The prototype and design mocks, for rules that hold across screens only: naming, what a tab holds, confirmation of destructive acts, empty states, navigation. Detail of one screen stays governed by the mockup.

Merge into one list: deduplicate, fold near-duplicates into the stronger wording, and drop anything the baseline already states unless this kit departs from it. Put the questions the evidence cannot settle (two sources disagree, code against document) in a separate part of the list. Write the merged list to `docs/architecture/_candidates.md` and commit it, so the curation survives a restart.

## 2. Curate with the user

Work area by area. For each candidate: keep, rewrite until it is falsifiable, cut, or move to the area it binds. Settle the open questions with the user, at most two at a time, recommending an answer each time. A settled question whose reasoning would not be obvious later becomes an ADR. Where the code stands against a kept rule, note it in `_open.md`; the rule still stands.

Keep `core.md` to rules that bind wherever an agent is working. A rule that only matters in one part of the tree belongs on that area's page, even if it is important. A rule tied to a topic rather than to paths (naming, process, how vendors are treated) stays in core.

## 3. Write the pages

Every page has a `## Rules` section and a `## Details` section.

- **Rules:** one bullet per rule, `**[<area>.<n>]**` and one sentence, grouped under short plain subheadings.
- **Details:** per id, `Rules out:` the concrete things it forbids (a pattern, a call, a file), optionally `Not ruled out:`, and `Source:` (ADR, document and section, change, fix shas).

Ids are `<area>.<n>`, one number space across core and the area pages, never renumbered. Gaps are fine, since commits and records cite ids. A rule that moves between pages keeps its id.

`core.md` opens with one paragraph on what it is, then a table of the area pages and what each loads for.

An area page opens with frontmatter naming the globs it governs, then one paragraph that names its scope and the `CLAUDE.md` files with the how-to for that area:

```markdown
---
paths:
  - "cdk/**"
  - "cloudformation/**"
---

# Infrastructure rules
```

Make the globs cover the code the rules bind and nothing wider; braces work (`services/{a,b}/**`). Link each page into `.claude/rules/` with a relative symlink and commit it with the page:

```bash
ln -s ../../docs/architecture/<area>.md .claude/rules/<area>.md
```

ADRs use MADR: frontmatter `number`, `title`, `status`, `date`, `decision-makers`; sections *Context and Problem Statement*, *Considered Options*, *Decision Outcome*. `0001-record-architecture-decisions.md` starts the folder.

Delete `_candidates.md` once every candidate is placed, cut or carried into `_open.md`.

## 4. Wire it in

- **`CLAUDE.md`:** a `## Rules` section near the top saying the rules are in `docs/architecture/`, that a design or commit relying on a rule cites its id and one departing from a rule says which and why, and that `docs/architecture/` wins over the narrative docs where they disagree. End it with the line `@docs/architecture/core.md`.
- **`CLAUDE.md` `## Crew` section** (the one the crew briefs point at): list `docs/architecture/` first in the record, and under where design is written, send a rule to `core.md` or its area page with an id, the next free number in its area, amended in the same commit as the decision that changes it.
- **`openspec/config.yaml`:** name `docs/architecture/` in `context`; add under `rules.design`: "Cite by id the rules in docs/architecture/ that this design relies on, and name each page of docs/architecture/ whose area the change touches. Where the design departs from a rule, name the rule and say why." Where `operations.apply.guidance` says which document wins, put `docs/architecture` and `openspec/specs` first.

Commit only the paths you wrote; other agents share the tree.

## 5. Check it loads

From the kit's main checkout, pick a rule that is only on one area page and a file under its paths:

```bash
Q='Answer from your loaded context only. Do you have a rule with id <id>? If yes, quote its first 10 words. If not, answer exactly NOT LOADED. Do not search for it.'
claude -p "First use the Read tool on <file under the page's paths>. Then: $Q" --model haiku --allowedTools=Read
claude -p "First use the Read tool on README.md. Then: $Q" --model haiku --allowedTools=Read
```

The first must quote the rule and the second must answer `NOT LOADED`. Do this for each page whose globs you are unsure of.

## 6. Prove it on real work

Restart the team's fable (`crew restart <team> fable`) so its brief and session pick up the rules. Then watch the next change and the next fix: the change's `design.md` should cite rule ids and fable's review should name a broken rule by id; the fix's commit should hold to the rules without being told. A rule an agent misreads gets rewritten, not explained in a brief.
