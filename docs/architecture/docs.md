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

## Details

**[docs.1]** Rules out: a rule only in a brief; reasoning only in a commit. Source: ADR 0009; switchboard-kit's `docs/architecture/`.

**[docs.2]** Rules out: a README command absent from the usage. Source: `tests/t-docs.sh`; fixes e413c48, f6988a2.

**[docs.3]** Rules out: a fix that leaves the change's design saying the old behaviour. Source: fixes e1ed1df, 902336e, 147075d.

**[docs.4]** Rules out: editing `openspec/specs/` on main for an unbuilt decision. Source: ADRs 0001–0003 consequences; `roadmap.md`.

**[docs.5]** Rules out: a change design naming no rule. Source: CLAUDE.md §Rules; `openspec/config.yaml`.
