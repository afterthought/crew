---
number: 9
title: Record architecture decisions
status: accepted
date: 2026-10-07
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# Record architecture decisions

## Context and Problem Statement

crew's rules are in `docs/architecture/`: `core.md` binds every change and an area's page binds that area, loaded by path through `.claude/rules/`. A rule says what must be true, not why. Where is a decision's reasoning kept?

## Considered Options

* A decision log in `docs/adr/`, in MADR format, managed by the `adrs` tool, as switchboard-kit and swancloud keep
* Reasoning under each rule in the pages
* Decisions kept in each change's design

## Decision Outcome

Chosen option: the decision log in `docs/adr/`, because it keeps the pages short enough to load into every session, keeps a decision after its change is archived, and keeps a superseded decision readable. Records 0001 to 0008 predate this one and carry its frontmatter.
