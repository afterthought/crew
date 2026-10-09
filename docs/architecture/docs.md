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

## Details

**[docs.1]** Rules out: a rule only in a brief; reasoning only in a commit. Source: ADR 0009; switchboard-kit's `docs/architecture/`.

**[docs.2]** Rules out: a README command absent from the usage. Source: `tests/t-docs.sh`; fixes e413c48, f6988a2.

**[docs.3]** Rules out: a fix that leaves the change's design saying the old behaviour. Source: fixes e1ed1df, 902336e, 147075d.

**[docs.4]** Rules out: editing `openspec/specs/` on main for an unbuilt decision. Source: ADRs 0001–0003 consequences; `roadmap.md`.

**[docs.5]** Rules out: a change design naming no rule. Source: CLAUDE.md §Rules; `openspec/config.yaml`.

**[docs.6]** Rules out: a *Proof after deploy* list of what a doctor row could assert; a task that is a deploy; a design that is a task list. Source: ADR 0012 point 3 as amended 2026-10-08; swancloud `testing.6`. `construct.md` and `openspec/config.yaml` say it once `a-change-holds-what-is-true-and-what-is-proved` lands: `_open.md`.
