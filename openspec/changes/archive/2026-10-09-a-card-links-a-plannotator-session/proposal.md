# Proposal

## Why

A Pending You card that asks the user to read something, a proposal, a unit's change in review or a verify report, carries today a Markdown file or a folder's path on the agent's host: the user can't read a whole change from the phone, and can't annotate it from anywhere but a pane beside the agent. The user decided that such a card carries the link to a running plannotator session on that document instead, started by the card's owner without opening a browser on its host, so the user reads and annotates it from wherever the card is answered, and what they decide there reaches the owner as the card's answer (`docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md` as amended 2026-10-08; `briefs.9`; signal `2026-10-08-swancloud-design-0f348337/01-review-card-links-a-plannotator-session-decided`).

## What Changes

- **A card that asks the user to read something links a plannotator session on it.** The planner's proposal card links a session on the proposal's page; the conductor's review card a session on the unit's whole change (proposal, design, specs and tasks); its verify card a session on the verify report. The landing card has nothing to read and links nothing. The link takes the place of the file or folder path the card carries today.
- **crew starts the session, by the card's key, and never opens a browser.** `crew card session <key>` finds the rail row the key belongs to, starts plannotator on that row's document on this host with an Approve button and no browser, and prints the session's link: the host's tailnet name and a port, which opens on the Mac or the phone wherever the card is answered. Run again for a key whose session is still running, it prints the same link and starts nothing. It refuses a key with no row, a landing key, a document not on this host, and a link that would open only on the host itself.
- **What the user decides in the session reaches the owner as the card's answer.** `crew card wait <key>`, run by the owner as a background command, returns when the user decides in the session, and prints the decision and every annotation the user wrote: approved (with any notes) is the card's approval; annotations sent as feedback are the user's note asking for changes, word for word. A session the user closed without deciding, or one that ended some other way, is said so, and the owner starts it again and updates the card's link.
- **The session ends when the card closes.** When a crew agent closes or withdraws a card, crew's card hook ends the session started for that card's key, so no session outlives its card even when the owner forgets. `crew card end <key>` ends one by hand. crew ends only a plannotator process it started for that key.
- **The briefs teach it, in the one card discipline the planner and the conductor share.** Start the session, put its link on the card, wait for its decision in the background, act on it as on the card's answer, then close the card; after a restart, run the session and the wait again for each open card, which gives back the same link. Never open a browser and never run plannotator by hand for a card.

## Capabilities

### New Capabilities

- `card-sessions`: the plannotator session a card's owner starts on the document its card asks the user to read, keyed by the card, reachable wherever the card is answered, whose decision reaches the owner as the card's answer, and which ends when the card closes.

### Modified Capabilities

- `rail-cards`: what a card carries. A proposal's, review's or verify report's card carries the link to its session in place of the page, the folder's path or the report. (`rail-cards` is written by `the-rail-is-answered-through-cards`, built and not yet archived; this delta is archived after it.)

## Impact

- `plugin/lib/plan.py`: the new `crew card session|wait|end` commands, reading the rail's rows for the key's document.
- `plugin/bin/crew`: routes `card` to `plan.py`, and its usage.
- `plugin/hooks/cards`: ends the session for a card's key when the card closes.
- `plugin/lib/crew.py`: `cards_how()`, the card discipline the planner's and conductor's briefs share.
- `plugin/roles/planner.md`, `plugin/roles/conductor.md`: what each card carries.
- `docs/architecture/briefs.md`, `docs/architecture/_open.md`: `briefs.9` is built; `briefs.4`'s detail says a session started without a browser is not an opening.
- `README.md`, `plugin/skills/crew/SKILL.md`.
- Tests: a stub `plannotator`, a new `tests/t-card-session.sh`, and checks in `tests/t-cards.sh` and `tests/t-briefs.sh`.
- Needs, outside crew: plannotator on every host that runs crew's planner or conductors, with swancloud's `PLANNOTATOR_PORT` range and `PLANNOTATOR_URL_HOST=auto`, which swancloud's `lib/agent-config.nix` sets today on the Macs and exports on the workspace boxes.

## Touches

`plugin/lib/plan.py` (a new `card` command; reads `rail_rows()`), `plugin/bin/crew` (the `card` route and usage), `plugin/hooks/cards`, `plugin/lib/crew.py` (`cards_how()`), `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `docs/architecture/briefs.md`, `docs/architecture/_open.md`, `README.md`, `plugin/skills/crew/SKILL.md`, `tests/stubs/plannotator` (new), `tests/t-card-session.sh` (new), `tests/t-cards.sh`, `tests/t-briefs.sh`, `tests/moon.yml` (shared: the new test's task), `openspec/specs/card-sessions/spec.md` (new, by delta) and `openspec/specs/rail-cards/spec.md` (by delta).
