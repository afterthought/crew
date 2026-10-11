---
paths:
  - "README.md"
  - "openspec/**"
  - "docs/**"
  - "CLAUDE.md"
---

# Documentation rules

The rules for where crew's design is written. `core.md` binds here too.

## Rules

- **[docs.1]** A rule lives in `docs/architecture/`, a decision's reasoning in `docs/adr/` as MADR managed by `adrs`, what each capability does in `openspec/specs/`, and the how-to in README and CLAUDE.md; an exploration or a reading says so in its first line.
- **[docs.2]** A change to a command's behaviour updates README, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` together, and every command README names is in the usage.
- **[docs.3]** A fix that changes behaviour an open change describes rewrites that change's proposal, design, spec and tasks in the same commit, and code follows the design where they disagree.
- **[docs.4]** A spec is changed only through a delta in the change that builds it; a record's decision reaches `openspec/specs/` with that build, never ahead of it.
- **[docs.5]** A design or commit that relies on a rule cites its id, one that departs from a rule says which and why, and a decision that changes a rule amends it in the same commit with the next free id in its area.
- **[docs.6]** An OpenSpec change holds, in its spec delta, what becomes true, as requirements with scenarios; in its tasks, what the coder proves locally; in its design, how and why, with *Proof in dev* as prose only where a check cannot be code; what must be true after a deploy is code in the same change by the kit's rules, and a design's *After deploy* lists only the steps no check can be code, saying why, each with its environments and its doer, an agent with the condition it waits for, or the user.
- **[docs.7]** `docs/architecture/` and `docs/adr/` have one writer on main, the design agent: a unit's change never edits them; what a landing builds leaves `_open.md` and the rules' not-built clauses by the design agent's hand after the landing, read from main's log; and a carrying fix that conflicts there takes main's side. (Proposed 2026-10-11, put to the user on a card as `briefs.15` has it; accepted only on their yes.)

## Details

**[docs.1]** Rules out: a rule only in a brief; reasoning only in a commit. Source: ADR 0009; switchboard-kit's `docs/architecture/`.

**[docs.2]** Rules out: a README command absent from the usage. Source: `tests/t-docs.sh`; fixes e413c48, f6988a2.

**[docs.3]** Rules out: a fix that leaves the change's design saying the old behaviour. Source: fixes e1ed1df, 902336e, 147075d.

**[docs.4]** Rules out: editing `openspec/specs/` on main for an unbuilt decision. Source: ADRs 0001–0003 consequences; `roadmap.md`.

**[docs.5]** Rules out: a change design naming no rule. Source: CLAUDE.md §Rules; `openspec/config.yaml`.

**[docs.6]** Rules out: a *Proof after deploy* list of what a doctor row could assert; a task that is a deploy; a task worked only after the landing, which holds the code stage open at its last task (crw-3's coder, 2026-10-11: task 6.1 of units-build-at-once-and-are-reviewed-in-batches, the design's *Proof on real work* list repeated as a task, left code at 14 of 15; unit-amendments' 4.1 was the same and was archived open); a design that is a task list. Source: ADR 0012 point 3 as amended 2026-10-08; swancloud `testing.6`. `construct.md` and `openspec/config.yaml` say it once `a-change-holds-what-is-true-and-what-is-proved` lands: `_open.md`.

**[docs.7]** Rules out: a task that removes a unit's open item or rewrites a rule's details as built; a construct that amends a rule page or a record. Not ruled out: a unit's change to README, the briefs, the skills and the specs, as `docs.2` and `docs.4` have it. Why: from 2026-10-09 to 11 `_open.md` alone stopped six landings, a-command-reads-once, releases-arrive-as-signals, environments-follow-main-by-reconcile, a-teams-cards-are-its-conductors, units-build-at-once-and-are-reviewed-in-batches and a-carrying-fix-is-judged-by-its-commits, each sent back to its team to carry, because the bolt removed its item while the design agent edited the page on main, 36 commits to it since the 9th (swancloud-ops, 2026-10-11: "CONFLICT (content): Merge conflict in docs/architecture/_open.md", signal 2026-10-11-swancloud-ops-3755d04a/01). Considered: one file per open item under `docs/architecture/open/`, which ends the collisions on `_open.md` and leaves them in the rules' details, so one writer instead. Source: that signal; `plan.8`; `state.3`. Not built: the check that refuses a unit's change touching these folders and the briefs' words (`a-unit-never-edits-the-design-pages`), queued once the rule is accepted: `_open.md`.
