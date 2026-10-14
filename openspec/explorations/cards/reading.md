> A reading (2026-10-14): crew's Pending You cards as they really are, what is broken, the five strands of work that touch them, and the questions one design must settle. It decides nothing. The design agent for the card elaboration wrote it for the user, on the recovery branch `recovery/cards`, from main at c882cff, the run records on the state branches, the sessions' MCP logs on mac-studio, the fleet's `pendingyou` 0.28.0 and its wake mod, and record 0005.

# Cards: the whole picture

**The short of it.** crew has posted 281 cards in six days, up to 98 a day, and almost half of them were kinds that no longer exist. Since 2026-10-10 the Mac Studio has had no Pending You sign-in of its own, so every agent has been posting through Claude Code's own login instead, one login per account folder, and crew's own `crew card` command, built on 10-12, cannot post at all. Nothing that is wrong needs a new service or a new sign-in method. It needs: one sign-in on the host, one list of cards crew posts at known points in its own code, crew building and closing those cards itself, and one card any agent can raise for a question of its own. The rest of this says why, with the numbers, and ends with the questions you settle.

Words used here, once: a **row** is one thing on crew's **rail**, the list of what waits on you (a proposal to approve, a batch of changes to read, a bolt ready to land, a deploy to hold). A **key** is the name a card is posted under, so a retry gives the same card back. A **connection** is one sign-in at Pending You; a card belongs to the connection that posted it. The **wake mod** is Pending You's plugin inside a Claude session that watches the cards that session knows and starts a turn when you answer one.

## 1. Today's cards, by the numbers

Read from the run record on the state branches (`refs/crew/<label>/main`, `runs/<host>/<date>.rec`) of swancloud, madswan and wldn, plus the 20 entries the Mac Studio has not yet carried to wldn's branch. Each entry is one act crew's hook recorded in an agent's session: a post, a change or a close.

| | |
|---|---|
| card acts recorded | 580 (281 posts, 36 changes, 263 closes) |
| posts by partition | swancloud 250, wldn 25, madswan 6 |
| posts per day, 10-08 to 10-13 | 51, 98, 52, 67, 9, 4 |
| busiest hour | 21 cards (10-11, 14:00Z); 20 (10-09, 17:00Z) |
| posts with no card id recorded | 25 (the hook could not read Claude Code's rendering of the reply) |

Posts by kind, and who posted them:

| kind | posts | still a kind of card today? |
|---|---|---|
| proposal (planner's) | 82 | yes |
| verify report (conductor's) | 71 | no: gone with record 0027 on 10-13 |
| review of one unit (conductor's) | 50 | no: gone with record 0014 on 10-11, replaced by batches |
| no key at all | 40 | no: the hook records them as the agent's own |
| landing (conductor's) | 31 | yes |
| batch (planner's) | 7 | yes |

So 121 of 281 posts were review or verify cards, kinds the design has since removed. Of the 40 cards with no key, 20 were wldn's operator agent on one afternoon (10-09, 16:17Z to 20:17Z), posting a card for every wait a conductor told it of; 13 were the design agent's record cards on 10-11, before the record key existed; 2 were swancloud's operator. Only one unkeyed card came from a conductor.

Who posted: swancloud-planner 84, crw-1-conductor 42, swc-1-conductor 40, swc-2-conductor 32, crw-2-conductor 28, wldn-operator-mac-studio 20, swancloud-design 13, crw-3-conductor 6, madswan-planner 5, and seven agents with one or two each.

**How long a card stayed open** before its close was recorded: median 6 minutes for a landing or a verify card, 8 for a review, 14 for an unkeyed one, 35 for a proposal, 2 h 50 for a batch. No card was open more than 17 hours when it closed. You answer fast; the cards that linger are the ones nobody closes.

**Duplicates.** Nine keys were posted under more than once: proposal 17 four times, landing `a-board-over-the-flow` at one head three times, and seven keys twice. Two causes: a card lost to a new connection and posted again (proposal 17, proposal 99), and a landing refused by the service and tried again.

**Open now, per the record (no close recorded):** 10 cards. The planner's proposals 17 and 99 (lost to the old connection on 10-11), madswan's proposals 3 and 4 (10-10), swc-1's review of mac-cleanup-runs-clean (a kind that no longer exists), crw-2's three verify cards of 10-12 (same), swb-1's verify card of 10-13 (same), and one unkeyed card of wldn's operator. Every one is dead to its owner once the host signs in again, and only you can dismiss them in the app. The recovery plan's list of stale cards adds crw-1's landing card for a-teams-cards-are-its-conductors and batch 6, which the record shows closed on 10-12; what the app shows is yours to read.

**Plannotator sessions running on the Mac Studio now:** 8. Six are for cards that are closed or dead: proposals 17, 83 and 101 (from a scratch folder, started by hand), madswan's proposals 3 and 4, and record 0019 from 10-11. Two are live, for swancloud's proposals 130 and 131. Record 0005 found eleven on 10-10. The unit that ends them on every rail read is built on main and never archived (`a-cards-session-ends-with-its-card`); the hook ends a session only when the card's owner closes it through Pending You's tools in its own session.

## 2. What goes out today, and from where

Every card today is written by the agent itself, as JSON, in its own Claude session, through Pending You's own tools. crew checks it before it goes (the key, the form) and records it after. The cards the design allows, and their deterministic points in crew, are:

| card | posted by | the event in crew | what closes it today |
|---|---|---|---|
| a proposal, `proposal/<n>` | the planner | `crew plan propose` opens one | the planner, after `crew plan approve` or a drop or a replacement; crew tells it to |
| a batch of changes to read, `batch/<n>` | the planner | `crew review --wait` records the batch | the planner, when you tap the card |
| a bolt ready to land, `land/<bolt>/<head>` | the team's conductor | every unit merged and sluice's verdict green | the conductor, after it tells ops to land |
| a deploy to hold, `deploy/<env>/<sha>` | main-level ops | the fleet's deployer runs `crew ops offer` | ops, after `crew ops approve` or a decline |
| a step only you can do, `op/<env>/<n>` | main-level ops | the deployer records a user's after-deploy step | ops, when you say done or decline |
| a decision record, `record/<kit>/<n>/<commit>` | the design agent | it commits a proposed record | the design agent, on your yes or no |

Everything else is refused by crew's hook before it reaches Pending You. That includes any question an agent has for you that is not one of these rows: a stuck stage, a hand step, a merge-or-redo choice, a conflict at a landing. Your word of 10-11 undid that restriction in the rules (`briefs.11`, record 0005), and crw-3's half-built unit was carrying it into the code; the hook on main still refuses.

Not one of these cards has ever been posted through `crew card post`, the command built on 10-12 that speaks to Pending You as the agent, from outside its session, under the host's sign-in. It cannot: the host has no sign-in, so it answers "this host can't ask through Pending You: it is not signed in".

## 3. What is broken

Ranked by what it costs you.

1. **No landing card can post.** crew's own form check demands a `highStakes` flag that Pending You refuses on an approval ("Approve requests give their risk in approve.risk"). Since 10-11 every bolt has waited for your word in a pane. The fix is built and verified in crw-3's bolt (`a-landing-cards-stakes-are-its-approvals-risk`), its merge owed since the team stopped.

2. **The host's sign-in is gone, and the agents did not notice.** Details in section 4. The upshot: since 10-10 09:05Z every card has gone out under whichever Claude Code login the agent's account folder happened to have, cards split across connections, the wake could not see cards posted elsewhere, "not found" errors made duplicates, and crew's own command is dead in the water. Accounts never logged in that way (sluice, willdan, flywheel-web, agentplot's blueprints) have no Pending You tools at all: "Authentication required" in 17 session logs.

3. **A question with no row cannot reach you.** Your 10-11 words: "My goal isn't to only have cards for the review. Fuck twisting everything I say. I don't want to have to jump into pain constantly." The rule is amended; the code is not (crw-3's unit, 6 of 14 tasks, built on the agent-writes-JSON path).

4. **Agents shape the card and crew checks a copy of Pending You's rules.** Twice crew's idea of a form drifted from the service's and every card of that kind was refused: the landing's flag, and the proposal card's missing approve block (crw-3, 10-11). Each was found by an agent failing to post, not by a test.

5. **The record depends on Claude Code's rendering of a tool result.** 25 posts recorded with no card id, so their closes could not be matched and the rail showed them as open or missed them.

6. **Cards nobody closes, sessions nobody ends.** Closing a card is the owner's duty on a `[crew]` notice; a landing, a drop, a replaced proposal and your own dismiss in the app all leave it to an agent that may be gone. Ten open cards and six dead plannotator sessions now; eleven sessions on 10-10, about 600 MB.

7. **Volume.** 98 cards on 10-09; 23 proposals in one day; 20 operator cards in one afternoon doubling what conductors had already asked. The operator agent's cards are already ruled out (10-09); review and verify cards are gone (10-11, 10-13). What is left on a busy day is proposals and landings, plus batches.

8. **The link on a card is slow.** Record 0005 measured plannotator's page at 23.7 MB, 8 to 15 s over the tailnet, 0.08 s on the host. That is upstream's page size, not the sessions. Fewer links, not faster ones, is what crew can do: a proposal card already holds its proposal whole (your 10-11 word), and a batch has one session for the whole batch.

## 4. The sign-in: your question, answered from the files

**Can the command-line sign-in be what the Claude Code sessions use?** Yes. It is the fleet's design, and it worked. `pendingyou-signin` signs the computer in as a *connection* (one that may ask, not only hear) and writes the credential to `~/.config/pendingyou/credentials.json`; every session the fleet starts is given the `pendingyou` server with a `headersHelper`, `pendingyou-mcp-headers`, which reads that credential and hands the session a token. One sign-in, every account folder, every partition. The sessions' logs show the helper handing out a token 338 times from 10-08 to 10-10, failing 13 times in those two days when the service refused a token or a refresh did not come in time, and failing on every start since the credential was gone, over 200 times.

**What happened, in order** (the files on mac-studio; `~/.config/pendingyou/helper.json`, `credentials.json`, the sessions' logs under `~/Library/Caches/claude-cli-nodejs/*/mcp-logs-pendingyou/`, and the CLI's `dist/api.js`):

| when | what |
|---|---|
| 10-08 19:00Z | In a crew bolt's session, Pending You answered a fresh helper token with 401 twice. Claude Code gave up on the helper for that session ("needs-auth"). At 19:15Z someone, you, logged that session in through Claude Code's own browser login. From then that account folder (and each other one you did this in) had a second connection of its own, used whenever the helper fails. |
| 10-10 04:57Z | The helper judged the host's sign-in stale: the service would not refresh it. |
| 10-10 09:05Z | The CLI cleared the credential. That is its own code: when a refresh is refused a second time it writes an empty credential and says "this computer's sign-in has ended" (`api.js`, the 401 branch). No command of yours did it; the service ended the connection, for a reason no file on the host records. |
| 10-10 11:55Z on | Every session's log: "headersHelper for MCP server 'pendingyou' did not return a valid value", then Claude Code's own OAuth token for that account, in 204 session logs since. That minted the connection record 0005 saw on 10-11, under which proposals 17 and 99 read "not found". |
| 10-12 | `crew card post` built, speaking as the agent through `pendingyou mcp --app claude-code` under the host's sign-in. It refuses with "not signed in" on every call. |
| now | `pendingyou status`: "Sign-in: not signed in". Eleven account folders, none with a Pending You login recorded in its own config; Claude Code keeps those tokens in the keychain, one per folder. |

**Did logging everyone in through Claude Code cause the mess?** It did not end the host's sign-in: the service did, and the CLI erased the file. But it is why nobody saw it for two days and why the cards split. With a Claude Code login behind the helper, a session that loses the helper carries on silently on its own connection. A card posted there is "not found" to the host's connection and to every other account folder; its wake sees only its own; a re-post under the key makes a duplicate. Without those logins, every agent would have lost its tools at once on 10-10 and the host sign-in would have been redone that morning. So: the logins are a fallback that hides the failure. They should go, and the fleet should make a helper failure loud (the doctor's row, swancloud's unit).

One more thing the logs show: on 10-08 the helper's token was refused while the credential still stood, and the helper waits at most 7 s for a refresh. Under a load of 386 (10-11), 7 s is not much. The fleet's part is to make a session with a dead helper fail visibly rather than fall back.

**Which connection owns crew's cards?** The host's, and only the host's. That is already ruled (record 0005, 10-11 and 10-12) and is what `crew card` does. For an agent to *hear* an answer, its session must be on the same connection (the wake mod checks a card through its own session's MCP server), and its settings must allow `mcp__pendingyou` (swc-1's conductor, 10-11: "to hear answers here, allow mcp__pendingyou in /permissions"; swancloud's `agents.1`, unit `crew-sessions-hear-their-cards-answers`). The mod learns a card its session did not post when the agent runs `pendingyou hold <id>`; the mod answers that command itself, so nothing waits (its `answerHold`). Whether that works end to end is what the three test cards were to read; they wait on the sign-in.

**What you must do, once, per host:** run `pendingyou-signin` on the Mac Studio at a moment with few cards open (every open card is lost to its owner afterwards), approving the code on your phone; the same on the box when wldn's teams return, since the box's own crew posts there. Then nothing: crew's command and every session use that sign-in. Redoing the sign-in is yours and rare; the fleet should show it in the doctor so a change is seen the day it happens.

## 5. The five strands, and what stands

| strand | state | what the design should say |
|---|---|---|
| crw-3's bolt `a-crew-agents-questions-reach-the-user-on-cards` | landing-stakes unit built and verified, merge owed; question-card unit 6 of 14, built on the agent-writes-JSON path | Your 10-13 worry is right: its intent is the right outcome on the wrong path. The landing form becomes crew's landing builder; the question card becomes `crew card ask`. The half-built unit's tests and brief words are a source for the builder, not code to finish. |
| `every-crew-card-goes-through-crew`, written 10-12, 0 of 5, in no bolt | the right shape: crew builds a row's card from its row, agents give only words, the hook refuses an agent's own tool calls | Becomes the core of the one change. Its open points (how an agent hears) are settled here. |
| swancloud's `pending-you-works-on-every-host` (2 units, planned) | idea | Stays swancloud's: allow `mcp__pendingyou` in every crew session's settings; the doctor's row names the host's connection and when it changed. Add: a helper failure is loud, and the box gets a host sign-in. |
| five card changes built on main, never archived | all tasks ticked: batch card as one notice with one session; lost card posted again; sessions end with their card; proposal card whole with units to leave out; image uploaded | Archive them (a chore, already in the backlog) so the specs show what is built. The new change's deltas build on them. |
| record 0005, 23 dated clauses | accepted, amended daily since 10-07 | Superseded on cards by a new record that states the whole, so the next reader does not reconstruct it from amendments. 0005 keeps the history. |

Also standing from 0005, unchanged: a card asks for a yes, never for a command to run; no card asks a question in words (Pending You makes it required); one voice per team; a card's area is its kit, its group the partition; an image is uploaded, a document is inline Markdown, a file is never attached; a landing is approved only by holding the button.

## 6. What the design must settle

Each has my recommendation marked. Mark them up as a whole.

**Q1. The list.** Every card crew posts, each at a point in crew's own code, and nothing else.

Recommended: six kinds. (1) A proposal, posted by `crew plan propose` itself when the write lands, in the form `crew plan card` already draws, whole on the card. (2) A batch, posted by `crew review --wait` when the reviewer delivers, one card, one reading session. (3) A landing, posted by the conductor's wait when the bolt's verification turns green at its head. (4) A deploy offer, posted by `crew ops offer`. (5) A user's step, posted by `crew ops step` when a step whose doer is the user is recorded. (6) A decision record, posted by the design agent's `crew card post record/...` on its commit. And the one open-ended kind: (7) **a question**, `crew card ask "<title>" ...`, from a conductor, the planner, main-level ops or the design agent, under `ask/<agent>/<slug>`, holding options or an approval the agent names. A stage agent or ops still asks through its conductor (`crew needs`), the dispatcher through the planner, the operator agent never: you are in its pane.

Alternative: leave posting to the agents, crew only building the JSON (the 10-12 change as written). It keeps a card hostage to the agent remembering; the numbers above say agents forget to close more than they forget to post.

**Q2. Volume, without telling agents not to ask.**

- *One card per question, one key.* Already the rule for rows; `ask/<agent>/<slug>` makes it the rule for questions too. A retry is the same card.
- *Replace, never add.* Recommended: when a row changes while its card is open (a landing's head moves after a fix, a proposal is amended), crew changes the card in place with a change note, same card; only an answered card is a new question. Today a new head is a new key and a new card.
- *Close on the event.* Recommended: crew closes a card at the event that ends its row, inside the same command, as the asking agent, under the host's connection: `crew plan approve` closes the proposal's card, `crew bolt land` the landing's, a drop its unit's. No notice to an owner, no owner needed; the rail stops listing "cards whose row is gone" because there are none. This is the one new thing the host's connection makes possible and the old design could not do.
- *One voice.* Stands: a team's cards are its conductor's; the operator agent posts none.
- *Batching.* Batches already cover changes to read. Proposals were 29% of posts and 23 on one day. Recommended: leave proposals one card each; a proposal is one decision, and the planner can propose less often. Alternative: a daily proposals card. Your call.
- *Expected volume after this:* on a day like 10-09 (98 cards), the same work would be about 23 proposals, 3 or 4 landings, 1 or 2 batches and whatever questions agents raise: around 30, none of them duplicates or doubles.

**Q3. What a card looks like.**

| card | kind | holds | link |
|---|---|---|---|
| proposal | approve, with a question per five new units to leave any out | the proposal whole: picture, text, case (built, 10-11) | none; a session only over fifteen new units |
| batch | notice, one tap | what it is, every unit and team, the reviewer's opening lines as prose | one plannotator session on the whole batch |
| landing | approve, risk high, not reversible | the bolt, its units, the verification's verdict | none |
| deploy offer | approve, risk high, not reversible | the environment, the commit, the landings it carries, one line each | none |
| user's step | action with the step's words | what to do, where | a link only when the step names one |
| decision record | approve, risk low, reversible | the record's decision, your quoted words, the record as inline Markdown | none |
| question | choice, multi or approve, as the asker names; never a words question | the question, its options, what the agent will do on each | a plannotator session only when the question is about a document |

Plannotator stays for one thing: reading a batch (and the rare long proposal). Sessions end when crew closes the card, in the same command, and the rail's sweep stays as the backstop. The slowness is upstream's page; crew's part is to link rarely.

**Q4. Sign-in.** Settled above, by the files, not by design: the host's connection owns every crew card; a session hears by the wake mod on the same connection with `mcp__pendingyou` allowed, learning crew's card by `pendingyou hold <id>` printed by `crew card post`; a session that cannot hear reads with `crew card read` at its breakpoints and when crew's notice names the card. The three test cards confirm the hold and the badge, after your sign-in, before the briefs change. Claude Code's own Pending You logins in the account folders go, so a dead helper fails loud.

**Q5. The strands.** As section 5 says: one change in crew supersedes the 10-12 change and crw-3's unit; crw-3's landing-stakes unit is absorbed by the landing builder, so its bolt can be closed rather than landed; the five built changes are archived; swancloud's two units stay swancloud's with two lines added; a new record states the whole and names what in 0005 it supersedes. The ten open cards and the dead sessions: yours to dismiss in the app after the sign-in, and crew's sweep ends the sessions.

**Q6. Ops cards, which you want to start testing soon.** The deploy offer and the user's step are already rows with keys and main-level ops's cards; they are built in `crew ops` and the deployer, and have never posted either, for the same two reasons as everything else. Recommended: they are two of the six kinds, built by the same builder, and the first real test of the whole after your sign-in is a deploy offer from swancloud's deployer reaching your phone.

## What follows

On your notes: one decision record (0029) stating every card and why, superseding record 0005's card clauses; one OpenSpec change for crew, `every-crew-card-is-crews-own`, or a name you prefer, with its tasks each naming their check; a note to swancloud's planner for the sign-in and the doctor. The recovery session lands the branch on your word.
