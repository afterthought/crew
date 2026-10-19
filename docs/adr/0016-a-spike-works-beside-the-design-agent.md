---
number: 16
title: A spike works beside the design agent, outside the bolt flow, and feeds it signals
status: rejected
date: 2026-10-10
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A spike works beside the design agent, outside the bolt flow, and feeds it signals

Deciders: the user (2026-10-10, through madswan-design, signals 2026-10-10-madswan-design-3d7ef799/02 "It's probably a good thing because I really didn't want to go through an OpenSpec process just to do a quick prototype page." and /03 "I also want to potentially be outputting from that spike things that come back as signals to you"); swancloud-design.

Status: rejected by the user on 2026-10-19 with record 0019, which answered it: elaboration, a spike with it, is Sounding's, and crew builds none ("Reject it: elaboration is Sounding's, crew builds none"); `briefs.14`'s spike clause is out with it. Before that: committed as accepted on 2026-10-10 without the user's approval, and put back to proposed on 2026-10-11 on the user's word ("I don't think the design agent really consulted me. I think it just added the ADR"); the user is questioning the spike as its own concept, and this record waits on the elaboration record that answers it.
Sources: `openspec/explorations/` (the board and testing explorations, each a pane beside the design agent whose report became a record); `docs/architecture/signals.md` (an agent's signals land on the flywheel's branch through `crew signal`); `plan.md` plan.9 (crew removes only worktrees it made, never a dirty one); ADR 0001 (chores); ADR 0010 (an exploration's reading became the board's record).

## Context and problem statement

On madswan tonight the user wanted a quick measurement page for the site and got a unit: an intent proposed from an old roadmap, a construct that built an example page, a review card for the wrong thing, while the user had built the sketch themselves in a planner's session. The user does not want the OpenSpec process for a prototype, and wants what a spike learns to come back to the design agent as signals. crew has explorations, run as a pane beside the design agent that reads and reports, but nothing for a session that writes code in a kit without a unit, and nothing that says where such code lives or what becomes of it.

## Decision drivers

- A prototype is a reading made with code: its worth is what it teaches, and that goes to the design agent as signals, not to main as a change.
- Nothing lands on main but a bolt's work through the kit's hooks (`state.3`); a spike's code never becomes product by accident.
- crew removes only worktrees it made and keeps a dirty one (`plan.9`), so a spike's place is crew's to make and the user's to keep.

## Considered options

1. A spike kind: a session the user starts beside the design agent, in a scratch worktree of the kit crew makes under `<kit>/spikes/<name>`, outside bolts and units; it records what it learns with `crew signal`, which the design agent curates; its code never lands but through a unit a signal becomes.
2. A chore (ADR 0001): built in a bolt by code, verify and merge; but a chore changes nothing a spec says must be true and lands on main, which a prototype should not.
3. A unit with a thinner change: still a proposal, a construct and a review for what the user wants to try by hand.

## Decision outcome

Option 1. A spike is started on the user's word beside the design agent, by crew, as an agent in a scratch worktree of the kit (`<kit>/spikes/<name>`, on a `spike/<name>` branch cut from main), with the user's words as its prompt and the design agent's name to tell. It builds what the user asks with no change, no proposal and no review; it records what it learns as signals with `crew signal`, in the user's words where they are the user's and in its own reading otherwise, and tells the design agent once when it ends. Its code lands on main only as the work of a unit that a signal of its becomes; crew never merges or lands a spike branch. Its worktree is crew's to make and to tidy as `plan.9` tidies, kept while it is dirty and removed on the user's word once its signals are recorded.

### Consequences

- One unit in crew, `a-spike-runs-beside-the-design-agent`: `crew spike <kit> <name> "<the user's words>"`, the brief, the place, the signals and the tidy.
- `plan.9`'s layout gains `<kit>/spikes/`; the roster names the spike as a session beside the design agent.

## Pros and cons of the options

- Option 1: good, the user tries things at the speed of a session, and the learning reaches the design through the one path signals take; bad, one more kind of worktree for crew to make and tidy.
- Option 2: bad, a chore lands on main and must change nothing a spec says must be true, neither of which fits a prototype.
- Option 3: bad, the process the user asked not to have.
