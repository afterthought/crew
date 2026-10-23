---
number: 38
title: The board is the one place, with a fleet page, a dock on each item and a word from the dock to the item's agent
status: accepted
date: 2026-10-23
decision-makers:
- Chuck Swanberg
---

# The board is the one place, with a fleet page, a dock on each item and a word from the dock to the item's agent

Status: accepted by the user on 2026-10-23, on their card (req_5ca27717fb15475fa320, "Accept the record as ruled"): the listener is swancloud's and `state.4` stands.

Deciders: the user, who asked for it on 2026-10-23 through the operator (signals 2026-10-23-swancloud-design-40a8b1a4/01 and /02): "I'd like it if we made that interactive so I could send feedback on items on the board to the appropriate agent (ops, design, planner, operation, etc.). One, I'll let you figure out how to do it." and "I want to be able to see, in one place, a nice overview of all of the crews", their list following: partitions, where they are, their repos and statuses, the bolts running, the teams and how busy, which Claude Code subscriptions are active in each, and each subscription's current session and weekly limits, Fable's among them; "a simple prototype to get us going", not Flywheel. Their words settle what is wanted; where it lives and how it works are the design agent's, below, put to them on this record's card.
Extends: record 0010 (the page is the board the user looks at; the board answers nothing).
Sources: `plugin/lib/page.py`, `page.html`, `board.py`, `sites.py`; swancloud's `lib/board.nix`, `packages/swancloud-board/swancloud-board.sh`, `modules/board-server.nix`, `lib/herdr-hosts.nix`, `lib/timers.nix`; the user's board mockup, agentplot/flywheel-next `design/mockups/rail-and-board.html` and its dock, `design/surfaces.md` S27–S28; Claude Code 2.1.307's own bundle (`api/oauth/usage`: `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, `utilization`, `resets_at`); deneb's keychain, read 2026-10-23 (twelve Claude Code sign-ins by name, none read by anything).

## Context and problem statement

The board the user looks at is crew's page: `crew page <label>` writes one file per partition, its data, style and script inline, loading nothing; swancloud's maker on `lib/board.nix`'s host (mac-studio) runs it every thirty seconds and copies it to srv, whose Caddy serves the partitions side by side at `board.swancloud.net/<label>.html` on the tailnet. The page is read-only: nothing on it is clicked into, and nothing sent from it. Its data already holds, per partition, the hosts, the teams with their kits and hosts, each session's Claude account (crew's fleet, from `lib/herdr-hosts.nix`), the bolts with their units, fixes and stages, the cards, the records, the signals, the environments and their deploys, and what needs attention. Nothing in the fleet reads a subscription's limits: Claude Code shows them in `/usage` from `api/oauth/usage` with the sign-in's credential, which each Mac holds in its keychain per account folder.

The user's mockup of a board with a drawer is flywheel-next's rail-and-board, whose dock opens over the board without moving it, from any control on a lane (S27–S28); record 0010 borrowed its forms for the page's lanes and not its file. The user looks up the fleet's facts in many places today and asks for one.

## Decision outcome

1. **The board is the one place.** No second dashboard, no Claude Code or herdr plugin, no Flywheel: what the user asked for is added to crew's page and served where the board is. A **fleet page** at the board's root shows every partition at once: where it runs (hosts and sessions), the kits it builds with each main's state (last landing, what is queued), its teams with their bolts and how busy each is (its slots' stages, idle or at work, and its conductor's wait), which Claude account each session runs on, and the attention items; each partition's page stays as it is, a link away.
2. **A dock on each item.** A click on any item of a page, a signal, a proposal, a bolt, a unit, a fix, a landing, a deploy, an operation, a team or a subscription, opens a dock over the board with the item's details as the page's data and the lineage already hold them, the board not moving (the mockup's dock, S27–S28); the page still loads nothing and is still one file.
3. **A word from the dock reaches the item's agent.** The dock takes a short message and sends it to the agent whose item it is: a bolt, unit or fix to its team's conductor; a proposal or batch to the planner; a signal or record to the design agent; a landing, deploy or operation to main-level ops; a partition or anything else to its operator. It arrives as crew's tell in the user's name from the board, naming the item, so no agent takes it for typing (`[crew tell from <user>@board]`); the board still answers nothing (record 0010): a card is answered on the rail, never here. A word that cannot be delivered is said in the dock in crew's own refusal words.
4. **crew runs no service for it** (`state.4`). The listener that takes the word and runs `crew tell` is swancloud's, a small job on the host that makes the board, as the maker that runs `crew page` is; the page posts to its own address, which srv's Caddy carries to that job over the tailnet, so the word travels only on the tailnet and the board's origin stays one. This is the choice `state.4` decided between a crew daemon, which the user's words name, and swancloud's job; the alternatives are on the card.
5. **Each subscription's use is read where it is signed in.** Every few minutes each Mac reads, for each Claude account signed in on it, what Claude Code's `/usage` reads, the five-hour and seven-day utilization with their resets, by model where given, and publishes the numbers alone where crew's page reads them; the credential never leaves the host. The fleet page shows them per subscription with the sessions and partitions on it and how old the reading is, and marks a reading a host could not make. What the page says of efficiency is those two things side by side: a subscription's use against the work of the sessions on it; nothing is computed beyond that in the prototype.
6. **The board is made on deneb**, with the deployer (record 0019's amendment of 2026-10-23): `lib/board.nix`'s host moves with it, and the listener runs there.
7. **A prototype.** Plain HTML and script in the page's one file, crew's standard library (`code.1`), no framework and no lavish; the dock's forms borrowed from the mockup, never its file.

### Consequences

- crew units on the yes: `the-board-opens-a-dock-on-each-item`; `a-word-from-the-board-reaches-the-items-agent` (the dock's message, its routing to the item's agent and the tell's marking); `the-fleet-page-shows-every-partition-at-once`; `the-fleet-page-shows-each-subscriptions-use`.
- swancloud units on the yes: `the-boards-word-reaches-crew-tell` (the listener on the board's host and Caddy's path to it); `a-mac-publishes-its-sign-ins-usage` (the reader under `lib/timers.nix`, numbers only); and the chore `the-board-is-made-on-deneb` (`lib/board.nix`).
- The held `crew-usage-sums-tokens-by-team-role-and-agent` stays held: limits are read from Claude Code's own reading, not summed from transcripts.
- The page's one-file, loads-nothing shape holds; the fleet page is a second file of the same maker.
- Order: the dock first, then the word, then the fleet page, then the subscriptions; the planner's.

## Considered options

- **Another dashboard**: a second surface built from the same read, where the board already is the one the user looks at (record 0010); rejected.
- **A Claude Code or herdr plugin**: shows one session's or one host's view, where the ask is every partition at once; rejected.
- **lavish**: an artifact made per response for review and feedback, not a standing page refreshed every thirty seconds; rejected, as the user guessed ("it might work best if it was just something simple").
- **A daemon of crew's own** taking the word over a socket, the user's own words: `state.4` rules out a service of crew's; chosen instead, a swancloud job that runs `crew tell`, the same shape as the maker that runs `crew page`. Loosening `state.4` is the other path on the card.
- **Flywheel's dock and rail as built in flywheel-next**: the real thing, which the user set aside for a prototype ("The objective isn't to build the end Flywheel here").
- **The board as the one place, extended** (chosen).
