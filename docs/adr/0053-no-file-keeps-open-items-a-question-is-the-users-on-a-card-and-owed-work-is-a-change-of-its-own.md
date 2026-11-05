---
status: proposed
date: 2026-11-04
decision-makers: the user; the chore docs-architecture-open-md-goes (the record)
---

# 0053. No file keeps open items: a question is the user's on a card, and owed work is a change of its own

Status: proposed. The decision is the user's own words, quoted below; the record is accepted on their yes once they have seen it as a record (`briefs.15`).

Deciders: the user, 2026-11-04, in the brief for the chore `docs-architecture-open-md-goes` on `teamless/deneb`: "We really have to stop maintaining _open.md. That's some made-up file that's been carried forward and is additional context to track, which we don't need. If there's anything in there that we're tracking and don't want to lose, we need to get rid of it." And, of the rules that named it: "A rule that names it as the place for open items says nothing in its place: an open decision is the user's, asked on a Pending You card, and owed work is a change of its own."

Amends: `roles.5` (a stopgap is no longer listed anywhere till it leaves); record 0047's "listed in `_open.md` until it leaves" and its consequence that `_open.md` gains the moves and stopgaps; `docs.7`, proposed, which loses its clause on the file. Sources: the user's words above; the user's capture process, which keeps no file of open items.

## Context and problem statement

`docs/architecture/_open.md` held what was not settled or not built: decisions waiting on the user, record 0047's moves to the tools and its stopgaps, accepted records not built, and code standing against a rule. Every rule page's details pointed at it, `core.md` named it as where the not-built lives, and the constitution skill set one up in every kit. It was written by hand and carried from change to change. Most of what it held had been built or overtaken and was never taken out, and edits to it stopped six landings in three days by conflicting (`docs.7`'s details).

## Considered options

1. Keep `_open.md`, swept now and then.
2. One file per open item under `docs/architecture/open/`, which `docs.7`'s details considered to end the conflicts.
3. No file of open items: what is done goes, a question only the user can answer is asked on one Pending You card, and owed work is a change of its own. Chosen, in the user's words.

Options 1 and 2 keep a list someone has to carry, which the user ruled out.

## Decision outcome

Option 3.

- `_open.md` is deleted. No rule, brief or skill names a place for open items.
- A question only the user can answer goes to them on one Pending You card, saying what it affects.
- Owed work (code against a rule, a spec behind the code, a plan not built) is launched as a change of its own, naming the rule, clause or record it concerns.
- A rule's details may still say what of the rule is not built. They point at no list.

## Consequences

- The chore that deletes the file sorted every item in it and lists the questions and the owed work in its commit message, so they can be put on cards and launched.
- `core.md` and `roles.5` stop naming the file; every rule page's details lose their pointers to it; the constitution skill sets up no such file in a kit.
- Records already accepted and archived changes that name the file stay as they are.
- The file goes on `teamless/deneb` first. main, swancloud, sluice and switchboard-kit each still hold one, which goes in a change of each repository's own.
