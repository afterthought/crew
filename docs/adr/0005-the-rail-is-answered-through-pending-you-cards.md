---
number: 5
title: The rail is answered through Pending You cards
status: accepted
date: 2026-10-07
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# The rail is answered through Pending You cards

Deciders: the user ("yes, let's do it in a subsequent bolt so we can release the rail first"); swancloud-design.
Sources: `docs/adr/0002` (the rail); recordplane/herdr-pendingyou (the Herdr plugin, 0.2.0) and the `pendingyou` CLI (0.27.0) with the Pending You skill at pendingyou.com/docs/skill, read on 2026-10-07.

## Context and problem statement

The rail (`crew rail`) lists what waits on the user, derived from the plan, the proposals and the kits, so nothing kept goes stale. It is a list to read and a shell to paste into; it does not reach the user's phone, and it does not ping. Pending You is a hosted queue of cards that agents post with their own sign-in and the user answers on a phone or, through its Herdr plugin, in a popup with one key, which wakes the agent. Its cards are kept, not derived: only the agent that posted a card can update or withdraw it, and its skill makes that the agent's duty ("a card means it's their turn now; the moment it isn't, withdraw it or change it", `update_request`, `cancel_request`, one `idempotencyKey` per question).

The user's concern: a card is shown, the plan is rewritten, and the card no longer applies.

## Decision drivers

- The rail's truth comes from state and must stay there; a second kept list is the staleness the user named.
- Every change that makes a card stale passes through crew: propose and replace, approve, drop, unit approve, construct again, merge, land.
- The user wants to be reached and to answer with a key, on the Mac or the phone.
- Client content on a third-party service is the user's call per partition.

## Considered options

1. Cards as the rail's surface: the agent that owns a decision posts one card per rail row, keyed by the row's id, and updates or withdraws it on the crew event that changes the row; the rail reconciles.
2. Cards as the rail: every decision lives only as a card.
3. No cards: the rail and the operator's notifications only.

## Decision outcome

Option 1, built after the rail has landed, and tried on swancloud before any client partition.

- **One card per rail row, by its owner.** The planner posts a card for each proposal it writes, keyed `proposal/<n>`; a conductor posts one for a unit in review, one for a verify report to decide, and one for a bolt ready to land, keyed by the unit's or bolt's name and the stage. The card shows the row's words and the link to what the user would read, opened as a plannotator session on it: the proposal's page, the unit's whole change (proposal, design, specs, tasks), the report. The owner starts the session when it posts the card, without opening a browser on its host, since the link on the card is how the user reaches it; the link opens from any device on the tailnet where the card is answered, a Mac or the phone; the user's verdict and annotations in that session reach the owner as the card's answer, the same as a note on the card, and the session ends when the card closes. Its options are the row's answers. (Amended 2026-10-08 on the user's word after swc-2's review card: "I would like it to include a link to a running Planetator session for the proposal and the design, since it's asking me to approve a unit. When we start Planetator, we don't need to launch it in a browser since we'll have a link to it in pendingyou.", signal 2026-10-08-swancloud-design-0f348337/01; before that the card carried the files as artifacts and the change folder's path. Read the same day on mac-studio: `plannotator annotate <folder> --gate --json --result-file <path>` publishes the reviewer's decision to a file the owner reads; `--tailscale` cannot serve HTTPS on the Headscale tailnet, and `PLANNOTATOR_REMOTE=1` gives `http://<host>.ts.swancloud.net:<port>`, reachable on the tailnet; once srv tunnels in, swancloud's record 0001 gives the session a `dev.swancloud.net` name.)
- **A card is updated or withdrawn on the crew event that changes its row.** A replaced proposal withdraws the old card and posts the new; an approval, a drop, a rerun of construct, a merge or a landing withdraws the card for the row it removes, with a one-line outcome. crew's notice to the owning agent on each such write names the card to update or withdraw, so the agent acts on it as it does on any `[crew]` notice.
- **The rail reconciles.** `crew rail` shows, per row, whether a card is open for it, and names open cards that have no row, with the agent that owns each, so a forgotten card is seen within one refresh. crew cannot withdraw another agent's card; it tells the owner.
- **An answer wakes the owner, which acts on the user's word.** Approve wakes the planner, which runs `crew plan approve <n>`; the conductor runs `crew unit approve` or construct again with the user's note. Pending You records the answer as given in Herdr on that computer, and crew's run record records who ran the command, as it does today.
- **Landing a bolt is high stakes.** Its card is marked so, and is answered in the Pending You app with hold-to-approve, never with a key in the popup. A row's card has the row's form (2026-10-09, the user, on wldn's brd-2: "The one from the BRD2 conductor is pretty poor. It's showing me a command I can run to manually land the build and then giving me a Done button. The whole point is telling the agent to land the build, and the one from the operator does give me an Approve button", signal 2026-10-09-swancloud-operator-mac-studio-47cdc78c/01): a landing's card is an approval whose yes has the conductor tell main-ops to land, never a step with the landing's command for the user to run; a proposal's an approval; a review's an approval with a note for changes; a verify report's the conductor's options. The conductor's brief said so already, so by `roles.3` crew refuses a row's card in another form. The same reading: wldn's operator agent posted its own approve card for that landing, and does for every wait a conductor tells it of, because Pending You's prompt hook says anything needed from the person goes on a card; its brief says a notification. The operator agent posts no card: a team's wait that has a card is already before the user, and the conductor sends no tell for it; a wait with no card, a question in a pane, is shown as a notification, as this record says above.
- **Where a card sits.** Pending You has no tags; it has areas, groups above them, and the asking assistant's name on every card. A card's area is its kit, named for the repository and linked to its git remote, so any agent in any worktree of the kit finds it by `match_area`; the first agent to post in a kit creates the area with the key `create-area:<owner>/<kit>`, and nobody creates one by hand. The area's group is the partition (`wldn`, `madswan`, `swancloud`), so the app separates the partitions as crew does. The asking assistant's name is the agent's crew name (`swb-1-conductor`, `swancloud-planner`), with the host and the worktree, so a card says which team asked; and a card's title names the object and its bolt ("Approve proposal 3: rollout-remainder", "Review the-rail-lists-what-waits-on-the-user, bolt decisions-shown-whole"). In Herdr a card shows on its agent's row, which sits in the team's workspace already (the user, 2026-10-07: "use tagging/areas to keep my different crew teams and/or herdr workspaces separated", signal `2026-10-07-swancloud-planner-97e1d612/01-cards-tagged-by-team-or-workspace`).
- **A card reads whole at a glance, and its link is in its words.** (2026-10-09, the user, on crw-1's two review cards: "the pending you isn't showing me enough detail about the OpenSpec proposal. I expect the \"For\" (what it shows me) to be glanceable, and for \"Pending You\" to include a link to a running Planitator", signal 2026-10-09-swancloud-operator-mac-studio-351110ee/01.) Read that day through swancloud-operator-mac-studio: both cards carried a two-sentence summary and the plannotator link only as an attached artifact of kind `url`, which is where the card discipline put it; the session answered on its port, so the link worked but sat where the user does not look. Pending You's card today has a title, a summary of at most 400 characters, a context with a background, links, a trace and files touched, options, and artifacts (the tool's schema, read 2026-10-09). So a card's words carry what the user decides from, and the link to read more is in those words, first, and also among the card's links, never only as an artifact. A review card says, in the change's own words, what the unit makes true and what it changes (the proposal's Why and What changes, cut to the card's budget), and names the bolt; a proposal card says the case and each change in a line; a verify card says each finding in a line with what the conductor would do. No card carries a path.
- **A team's cards are its conductor's, and a crew agent's card is always a rail row's.** (2026-10-09, the user: "I had both the conductor and the ops agent send me the same thing in pending. Could you analyze the session and figure out how crew might need to be updated to avoid this?", signal 2026-10-09-swancloud-operator-mac-studio-9539e922/01.) Read that day from the transcripts on chuck-herdr-alpha (session eb4bb726, brd-2, wldn), through swancloud-operator-mac-studio: at 15:39:31Z ops told the conductor its proof passed with one item open for the user, a gateway check green on a Mac; at 15:39:52Z ops posted its own card for it under a key of its own; at 15:39:55Z the conductor, on that tell, posted another under another key; and within a second each created the kit's area under its own key, not `create-area:<owner>/<kit>`, so Pending You could dedupe neither. `ops.md` carries no card rule, the conductor's brief says only rows get cards, and the card hook records a card under any other key as the agent's own without refusing it. So: a team speaks to the user with one voice, its conductor's; ops and every stage agent post no card, and what a proof leaves that only the user can do or check goes in ops's proof file and its one line to the conductor. The conductor asks it on the bolt's landing card, keyed `land/<bolt>`, as the step before approval, posted when the proof is clean or clean but for that step, so one card carries the user's step and their word to land. By `roles.3` the fix is a check, not firmer words: crew refuses a card a crew agent posts under any key but a rail row's of its own, and an area made under any key but `create-area:<owner>/<kit>`, naming the key to use. A duplicate area already made is removed in the app by the user.
- **A pane's badge is the card's.** The Herdr plugin shows each waiting agent's card on its row, and the operator agent's herdr notification for a review, a report or a landing is no longer needed; its tell for a question in a pane stays, since that has no row and no card.

### What it needs outside crew

- Pending You set up on every host that runs crew agents, declared in swancloud: the `pendingyou` command line and its agent setup, the Herdr plugin from the fleet's catalog, and a sign-in per computer that the user grants; Claude Code 2.1.287 or later for the wake. A unit in swancloud.
- The user's decision, per partition, whether its proposals and diffs may sit on Pending You; swancloud first.

Two rulings on that setup, from swc-2's verify of it (2026-10-07; the CLI's own text in `dist/hold.js`, `dist/pickup.js` and `dist/remote.js` tells an agent to run `npx pendingyou hold <id>` and a user to run `npx pendingyou login`; init's hook list in swancloud's `lib/pending-you.nix`):

- **Nothing of Pending You runs from npm on a fleet host, by an agent or by the user.** The fleet's `pendingyou` is the one on the path. An agent crew starts hears an answer by the wake mod and never runs `hold`; the card discipline in the briefs says so, and crew's card unit teaches it. The user's sign-in on a fleet host is the fleet's `pendingyou-signin`, which makes the connection the agents' hooks use; a plain `pendingyou login` makes one that only hears. CLAUDE.md names `pendingyou-signin`, and the doctor's row says which kind of sign-in a computer holds and names `pendingyou-signin` as the fix for the hear-only kind. The upstream text that says `npx pendingyou …` stays as upstream's words; it is not rewritten.
- **The Stop check is off for an agent crew started.** Pending You's Stop hook turns what a session "left only in chat" into a card. A crew agent's last words in a pane are for its conductor, the user or another agent, and a card for them would be unkeyed and beside the rail's keyed cards, which this record forbids: one card per row, by its owner, and a question in a pane has no card. So in a session with `CREW_AGENT` set the Stop check, and any reminder it leaves for the next message, does nothing; in the user's own sessions of the same partitions it runs as Pending You ships it. The hooks that hand answers in (pickup at session start, handoff with the next message) and presence stay on for every session.

### Consequences

- One unit in crew after the rail's two: the card discipline in the planner's and conductor's briefs, crew's notices naming cards, and the rail's card column.
- One more unit, `a-rows-card-has-the-rows-form` (2026-10-09): crew's refusal of a row's card in another form, and the operator agent's brief posting no card.
- One more unit, `a-card-reads-whole-at-a-glance` (2026-10-09): the card's words carry the decision's substance in the document's own words with the link first, in the card discipline crew fills into the briefs.
- One more unit, `a-teams-cards-are-its-conductors` (2026-10-09): the ops brief's no-card rule, the landing card carrying the proof's step for the user, and crew's refusal of a card or an area under a key that is not the rule's.
- One more unit, `a-card-links-a-plannotator-session` (2026-10-08): the session started by the card's owner without a browser, its link on the card, its decision read as the card's answer, in the briefs and the card discipline crew fills into them.
- The rail stays complete without cards; a host or partition without Pending You loses pings, not decisions.

## Pros and cons of the options

### Option 1: cards as the surface

- Good: the phone and a one-key answer; staleness bounded by crew's own events and shown by the rail; the truth never leaves state.
- Bad: two places to look until the rail shows card state; a card lingers when its owner is down until it is restarted or the user clears it in the app.

### Option 2: cards as the rail

- Bad: every decision kept by hand, which is the staleness the user named; nothing can be derived or reconciled; a card's owner down means a decision lost from view.

### Option 3: no cards

- Good: nothing hosted, nothing to keep.
- Bad: no reach to the phone, and every ping stays a pane notification the user may be watching nothing of.
