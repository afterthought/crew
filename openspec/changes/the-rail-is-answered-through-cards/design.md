# Design

## Context

See proposal.md for why. The decision is `docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md`; the rail it builds on is `docs/adr/0002-what-waits-on-the-user-is-shown-whole-and-read-from-state.md` and the `what-waits-on-the-user-is-one-list` change, already on this bolt.

What is there today:

- **The rail.** `rail_rows()` in `plugin/lib/plan.py` makes the four groups' rows from the plans, the proposals, the kits as `survey()` reads them, and, for a proposal's time, the run record through `record.gather()`. `rail_view()` prints them. A unit's place in the survey has its `head` sha and `head_at`; a kit's `reports` has each unit's newest verify report, with its path.
- **Notices.** `write()` in `plan.py` ends every plan write with `notify()`, which tells the conductor of each team holding a touched bolt the write's subject (unless that conductor wrote it, or the command greets it). `plan_drop()` and `plan_agree()` tell the planner through `tell_planner()`. The amend path tells a unit's conductor to run construct again. `plan_approve()` and `unit_approve()` tell no one.
- **The run record.** `record.emit()` appends an entry on the host where it runs, with `By` from `CREW_AGENT`, a `Session`, and the fields in `EXTRA`. An entry holds no text anyone typed (`openspec/specs/run-record/spec.md`).
- **The plugin's hooks.** `plugin/hooks/hooks.json` has one hook, `session-start`, which records each crew agent's session in `~/.local/state/crew/sessions/<session id>` (`CREW_AGENT`, `CREW_LABEL`, `CREW_CWD`), so a session herdr resumes without those variables gets them back. A resumed session's hooks don't see `CREW_AGENT` in their environment; only its Bash commands do, through `CLAUDE_ENV_FILE`.
- **Pending You, as swancloud sets it up** (its `lib/pending-you.nix` and CLAUDE.md, and the `pendingyou` 0.28.0 command line, read on 2026-10-07). Every partition crew runs in gets the `pendingyou` MCP server in its sessions, so its tools are `mcp__pendingyou__<tool>`, and the wake mod. The mod learns the cards a session posts from that session's own tool calls, and starts a turn when the user answers one. The Stop check is quiet for crew's agents. The tools that matter here are `whoami`, `match_area`, `create_area`, `list_pending`, `post_request`, `update_request`, `get_request`, `cancel_request` and `ack_answer` (Pending You's guide 2.44, "Tools"). A card is the asking agent's own, by the `name` it gave `whoami`; another agent on the same sign-in is refused it. `idempotencyKey` makes a retry of a post return the same card. A high-stakes card is refused from Herdr's popup (`high_stakes` in the plugin's `dist/herdr/queue.js`) and approved by holding in the app.
- **What can read cards.** The command line has no command that lists cards. The one list outside an agent's session is the Herdr app's `GET /v1/cards`, behind its own sign-in bound to the computer's key, reached only through the command line's internal SDK. An agent's `list_pending` shows only that agent's cards.

## Goals / Non-Goals

**Goals:**
- One card per rail row, posted and closed by the row's owner, the same way in the planner and the conductor.
- crew names the card a change ends, to its owner.
- The rail shows each row's card and any open card whose row is gone, read from what crew recorded.

**Non-Goals:**
- Setting up Pending You on a host, its sign-ins, the Stop check, or which partitions get it: swancloud's `pending-you-is-set-up-on-every-crew-host` unit.
- Cards for questions asked in a pane, for the design agent's or main-level ops' own waits, or for the agenda's items. A question in a pane keeps its tell.
- crew closing a card itself. Only the agent that posted a card can close it; crew tells that agent.
- Reading card state from Pending You's service.

## Decisions

### crew learns of cards from its agents' own tool calls

A `PostToolUse` hook in crew's plugin, `plugin/hooks/cards`, runs after each Pending You tool call that posts, updates, withdraws or closes a card, in a session crew started. It writes one run-record entry per act: `card.post`, `card.update` or `card.close` (for `cancel_request` and `ack_answer`). Each entry names the row's object in `On` (`proposal/<n>`, `unit/<unit>`, `bolt/<bolt>`), the card's id in a new `Card` field, and the row key in a new `Key` field. The rail reads these entries: a card is open from its `card.post` until a `card.close` with the same `Card`.

This is how the wake mod itself knows a session's cards: from the session's own `post_request` results. A crew agent can't post a card without the hook seeing it, so no discipline is needed for the record to be complete.

*Alternative:* have the rail read the user's open cards from Pending You with the Herdr app's sign-in. That would read Pending You's own truth, including a card the user dismissed. But it would reach into the command line's undocumented internals from python, add node to what crew needs, and borrow the user's app sign-in for a read it was not granted for. Nothing in the ADR asks for it.

*Alternative:* the agent runs a crew command after each post and close. That is the kept-by-hand record ADR 0002 rules out, and a forgotten command is the stale card the ADR is about.

### A row's card key changes when the row is a new decision

The keys are `proposal/<n>`, `review/<unit>/<head7>`, `verify/<unit>/<YYYYMMDD-HHMM>` and `land/<bolt>`. A unit that comes back to review after construct runs again is a new decision with a new head, so it gets a new card rather than the closed one. Pending You's `idempotencyKey` guarantees only that a retry returns the same card, so crew never relies on reposting a key after its card was closed. A proposal's number, a report's stamp and a bolt's landing each happen once.

The rail prints each row's key, so the owner takes it from `crew rail` and never computes it. A card whose key belongs to an older head is then plainly one with no row.

### The notice names the row; the owner finds its card

crew's notices name the row (`review/x`, `verify/x`, `land/y`, `proposal/4`), not the full key. The owner has at most one open card per row and finds it among its own with `list_pending`. That lets crew name the row from what the change itself knows, without reading a kit or the run record at the moment of the change.

Who is told:

- **The owner made the change**, such as the planner approving on the user's word, or the conductor running construct again. The command's output ends with `Close your Pending You card for <row>, if one is open, with what was done.`
- **Someone else made it**, such as the user from the rail's shell, main-level ops landing, or a proposal's approval moving a unit away. crew tells the owner, adding that line to the tell it already sends or sending a new one.

### One shared brief text, `CARDS`

The card discipline is one text, made by `cards_how()` in `plugin/lib/crew.py` and filled as `{{CARDS}}` into the planner's and the conductor's briefs. Like `{{SIGNAL}}`, it keeps both agents doing it the same way. The brief text around it says which rows that agent owns and how it acts on each answer.

### Pending You's presence is the switch

crew holds no per-partition setting for cards. A session that has Pending You's tools posts cards, and one without them doesn't: swancloud decides which partitions get the tools. The conductor's tell to the operator agents stays for every wait in a session without them.

### The rail's card line, and cards with no row

The rail reads each label's run record once per refresh. It reads from 14 days back, or from the day before the oldest open proposal's `Opened` when that is earlier, and both the proposals' times and the cards come from that one read. Each row gets one more labelled line, after its commands:

```
    card:   review/x/abc1234, open, asked by swb-1-conductor
    card:   proposal/4, none open
```

After the four groups, and before any host that didn't answer, the rail lists `open cards with no row:`, but only when there is one. Each such card gets a line with when it was posted, its age, its key and label, and who asked, then an `answer:` command that pastes a `crew tell` to that owner. A card is left out when its row can't be known: its partition's plan wasn't read, or its team's host didn't answer. The four groups keep their shape, so the rail reads the same as before when nothing is stray.

### The landing card goes through the conductor

The conductor posts the landing card once ops reports the proof clean, marked high stakes. When the user approves it, the conductor tells main-level ops, in the words the land row already uses: `Land bolt <bolt>. The user approved it on Pending You.` Main-level ops' brief takes the user's word from the conductor as it takes it from the planner today.

## Risks / Trade-offs

- [The hook can't read the card's id from a tool result of a shape it doesn't know] → It reads the shapes the wake mod reads: `structuredContent`, then JSON in a text block, and the shape Claude Code 2.1.292 actually hands a `PostToolUse` hook for a Pending You tool, the result's text alone as a string of JSON (read on 2026-10-08 from the transcript's `toolUseResult`; every `card.post` of that day was recorded with `Key` and no `Card` until the hook read it, fix eef2084 on crw-1's bolt, signal 2026-10-08-swancloud-operator-mac-studio-d6a5ac99/01). An entry without a `Card` is still written, but the rail can't pair it with a close, so it shows nothing for it. *Proof on real work* checks a real post.
- [A card the user dismisses or lets expire in the app still reads as open until its owner closes it] → The owner is woken for an answer, and closes it with the outcome. Pending You's own `stillTheirs` reminds the owner of a card older than a day. A card that is never closed shows on the rail as one with no row once its row goes.
- [An open card older than 14 days drops out of the rail's read] → Accepted. Pending You's reminders have long since named it to its owner.
- [The rail now reads the run record on every refresh, not only when a proposal is open] → That is one call per partition host, beside the kit reads it already makes.
- [Client content on a third-party service] → Only partitions whose sessions swancloud gives Pending You post cards. The ADR has swancloud tried first.
- [A field name in the briefs differs from the live tool schema] → The briefs name the tools and what to pass in plain words. The agent reads each tool's schema from the server; *Proof on real work* checks the first cards.

## Migration Plan

Land, then pull on every host. The hook runs in each crew session from its next start. The planner and the conductors take the card discipline at their next fresh start, or when told what changed. Cards begin with the next proposal or review after that, and nothing earlier needs a card. Rollback: revert. Cards already open stay open until their owners close them or the user dismisses them in the app.

## Proof on real work

Once the bolt has landed, every host has pulled, and the user has made the `swancloud` group in Pending You:

1. In swancloud, the planner opens a proposal. A card appears on the phone and on the planner's row in Herdr: asked by `swancloud-planner` on its host, in the kit's area within the `swancloud` group, titled with its bolt, carrying the proposal's page. `crew rail --label swancloud` shows `proposal/<n>, open, asked by swancloud-planner`.
2. Approving it on the phone wakes the planner, which runs `crew plan approve <n>` and closes the card with what was applied. The next refresh has no proposal row and no open card with no row.
3. A unit reaches review. Its conductor's card carries the change folder's path. A note asking for changes, sent with Herdr's popup key, has the conductor run construct again with those words and close the card. The rail then shows the new head's key with no card open, until the conductor posts the next one.
4. Approving a unit from the rail's shell with `crew unit approve` tells the conductor, which closes its card. No open card with no row is left after the next refresh.
5. A proven bolt's landing card is refused from Herdr's popup as high stakes. Held to approve in the app, it has the conductor tell main-level ops to land the bolt, and main-level ops lands it.
6. `crew events --label swancloud` shows each card's `card.post` and `card.close` with its `Card` and `Key`, and no card's title or words. If any `card.post` lacks a `Card`, record the tool result's shape for the hook.
7. A conductor restarted while the user answers its card acts on the answer at its start.
8. The same on chuck-herdr-alpha, for a team whose host is the box.

## Task notes

**1.1** `plugin/lib/record.py`. Add `Card` and `Key` to `DESCRIPTOR`'s `%allowed` and to `EXTRA`, as `Amended` was added (commit `001b809`). Check that a day's file begun under the old descriptor still takes an entry with the new fields and is still carried: the carry in `carry()` writes `DESCRIPTOR` afresh, and `recfix` must accept the union. Add a `tests/t-cards.sh` check for that.

**1.2** `plugin/hooks/cards` (new, python3, standard library only, like `session-start`), and a `PostToolUse` entry in `plugin/hooks/hooks.json` with the matcher `mcp__.*__(post_request|update_request|cancel_request|ack_answer)` and a 10-second timeout. The hook:
- reads the hook's JSON on standard input, and acts only when the tool's server, lowercased with everything but letters and digits removed, contains `pendingyou`. That matches `mcp__pendingyou__…` and a plugin's server alike, as the wake mod's `isPendingYou` does;
- acts only for a session crew started: `CREW_AGENT` and `CREW_LABEL` from the environment, else from `~/.local/state/crew/sessions/<session_id>` as `session-start` wrote them. It sets them in its own environment, with `CREW_SESSION=<host>:<session_id>`, before calling `record.emit`, so `By` and `Session` are right in a resumed session;
- writes nothing when the tool result is an error (`isError`, or a `deny`);
- reads the result object as the wake mod's `resultObject` does: `structuredContent`, else the first text block that parses as a JSON object, under `tool_response` as Claude Code gives it;
- `post_request`: `card.post`. `Card` is the result's `requestId` when it matches `^req_[A-Za-z0-9-]{1,40}$`. `Key` is the input's `idempotencyKey` when it matches one of the four keys (`^proposal/\d+$`, `^review/[a-z0-9][a-z0-9-]*/[0-9a-f]{7}$`, `^verify/[a-z0-9][a-z0-9-]*/\d{8}-\d{4}$`, `^land/[a-z0-9][a-z0-9-]*$`). `On` is the key's object (`proposal/<n>`, `unit/<unit>`, `bolt/<bolt>`), or `agent/<CREW_AGENT>` when the key is none of them; such a key is not recorded, since it is text an agent wrote;
- `update_request`: `card.update`. `cancel_request` and `ack_answer`: `card.close`. Each takes `Card` from the input's `requestId`. It finds the card's `Key` and `On` from this host's `card.post` entry for that `Card`, reading the label's run-record files of the last 30 days on this host. When none is found, `On` is `agent/<CREW_AGENT>`;
- never fails a tool call: everything is in a `try`, a failure is one line on standard error, and the exit is 0.

Record no title, summary, option, note or outcome. Update `record.py`'s module docstring with the three acts.

**1.3** `tests/t-cards.sh` (new, with the `TESTS` line every test has). Feed the hook JSON as Claude Code would, with `CREW_AGENT=swb-1-conductor` and `CREW_LABEL=wldn`, and check, with `recsel` or `crew events --json`:
- a post with `structuredContent` gives a `card.post` with `Card`, `Key` and `On: unit/x`, and no title anywhere in the file;
- a post whose result is a text block of JSON gives the same;
- an `ack_answer` for that card gives a `card.close` with the same `Key` and `On`;
- an unkeyed post gives `On: agent/swb-1-conductor` and no `Key`;
- an error result writes nothing; a server named `github` writes nothing; with no `CREW_AGENT` and no session record, nothing is written;
- with no `CREW_AGENT` but a session record from `session-start`, the entry's `By` is the recorded agent.

**2.1** The rail, in `plan.py`. Replace `proposed_at()`'s gather with one `record.gather()` per label whose plan was read, from the earlier of 14 days back and the day before its oldest open proposal's `Opened`. From those entries take both the proposals' times, as now, and the cards. A card is `{label, card, key, on, by, host, at}`, from each `card.post` with a `Card`, less those with a later `card.close` of the same `Card` and label. Give each row in `rail_rows()` its `key`:
- `proposal/<n>`;
- `review/<unit>/<place head[:7]>`;
- `verify/<unit>/<stamp>`, with the stamp from the report's file name (`verify-<unit>-(\d{8}-\d{4})\.md`);
- `land/<bolt>`.

In `rail_view()`, print after each row's commands `    card:   <key>, open, asked by <by>` for each open card whose key and label match, or `    card:   <key>, none open`. Then print the open cards that match no row, as *The rail's card line, and cards with no row* has them, oldest first. Each is `  <time>  <age>  <key, or "an unkeyed card"> (<label>), asked by <by> on <host>`, then `    answer: crew tell <by> "Close your Pending You card <key or id>: its row is gone."`, quoted with `shlex.quote` where needed. Leave out a card of a label whose plan wasn't read, and a review, verify or land card of a unit or bolt whose team's host didn't answer.

**2.2** `tests/t-rail.sh`. Write card entries with `record.py emit --act card.post --on unit/<u> --field Card=req_… --field Key=…`, the way the hook does, then check:
- a review row prints its `review/<u>/<head7>` key with `none open`, then `open, asked by swb-1-conductor` once a card is posted, then `none open` again after its `card.close`;
- a proposal row's key is `proposal/<n>`; a verify row's has the report's stamp; a land row's is `land/<bolt>`;
- a card keyed for an older head is listed under `open cards with no row:` with its `crew tell`;
- with nothing stray there is no such heading, and the first check (four headings, four `none`) holds unchanged;
- with the box down, a stray review card of its team isn't listed;
- `crew rail` still leaves the state branch's tip unchanged and writes no entry.

**3.1** The notices, in `plan.py`, each ending with the line *The notice names the row* gives. `agent()` is who runs the command; the owner of a proposal's row is `<label>-planner` when the proposal's `By` is the planner; the owner of a unit's or bolt's rows is the conductor of the team holding its bolt.
- `plan_propose()`: when the planner writes it, print `Post your Pending You card for proposal/<n>.`, and with `--replaces <m>` first `Close your Pending You card for proposal/<m>, if one is open: proposal <n> replaces it.`
- `plan_approve()`: after applying, the line for `proposal/<n>` is printed when the planner approved, else sent with `tell_planner()` as `Proposal <n> was approved by <agent>. …`.
- `plan_drop()`: the same, adding the line to the tell it already sends.
- `plan_agree()`: add `Update your Pending You card for proposal/<n>: it no longer waits on <team>-conductor.` to its tell to the planner.
- `unit_approve()`: the line for `review/<unit>`, printed when the team's conductor ran it, else told to that conductor as `Unit <unit> was approved by <agent>. …`.
- The amend tell: add `Close any Pending You card you have open for review/<unit> or verify/<unit>.`
- `write()` and `notify()`: before the change, note each unit of a held bolt and its team, and each held bolt and its team. After it, the rows a team lost are `review/<u>` and `verify/<u>` for each unit no longer in a bolt that team holds, and `land/<b>` for each bolt that team no longer holds. Add `Close any Pending You card you have open for <rows>.` to the subject `notify()` tells that conductor. When that conductor wrote it, print the line instead. This covers a landing, a drop, a move, and a split's remainder leaving.

`tests/t-proposals.sh`: approving as the user tells `wldn-planner` with `proposal/<n>` (read the stub herdr's log as its other tell checks do); dropping does too; `plan propose --replaces` as the planner prints both lines. Its existing checks must still pass.

**3.2** `crew unit run`. In `plan.py`'s `run_check()` (the internal `plan _run`), from the unit's stage before the run, the rows it ends are: `review/<unit>` for `construct` on a unit in review, and `verify/<unit>` for `construct`, `code` or `merge` on a unit in verify. Print the line for them to standard error, which `plugin/bin/crew` passes through while it reads the command's output, when the team's conductor runs it. Tell the conductor instead when anyone else does. Print nothing for a stage that ends no row. `tests/t-unit.sh`: construct again on a unit in review prints `review/<unit>`; a first construct prints nothing.

**3.3** `unit_approve()` when someone other than the conductor approves: `tests/t-unit.sh` (or wherever approval is tested today) checks the tell reaches `swb-1-conductor` with `review/<unit>`, and that the conductor approving gets the printed line and no tell.

**4.1** `plugin/lib/crew.py`: `cards_how(cmd, label, kits)` returns the `CARDS` text, put in both `team_tokens()` (with the team's kit) and `main_tokens()` (with every kit of the partition, as `<name>: <owner>/<repo>`). The text, in the briefs' plain style:

"When your session has Pending You's tools, every decision of yours the rail lists gets one card, and only those. A question you ask in your pane gets no card. Take the row's card key from the `card:` line under its row in `{cmd} rail --label {label}`, and post the card with that key as its `idempotencyKey`. That way a retry never makes a second card, and the rail knows the card is the row's. At your start, call `whoami` with your crew name and one line on your role. Then call `list_pending` with that name, and act on any card the user has answered. Post a card for any row of yours that has none open. Ask every card in your crew name, with this host as the session's machine and your worktree as its folder. File it in the area of its kit, found with `match_area` from the kit's git remote. When there is none, create it with `create_area`, named for the kit, in the group `{label}`, with the key `create-area:<owner>/<kit>`. Never make a group: if `{label}` isn't one of the user's groups, the area is left ungrouped, and you say so once. Title it with what you ask and its bolt. Put what the user would read on it, and give it the row's answers as its options, with `blocking` false. You hear an answer by being woken in your pane. Never run `npx pendingyou` or `pendingyou hold`: the `pendingyou` on the path is the fleet's, and the wake needs neither. Act on the user's answer as if they had said it in your pane, then close the card with `ack_answer` and a one-line outcome. When crew tells you, or prints, to close the card for a row, close it with `cancel_request` and the reason, or with `ack_answer` when you acted on its answer. Only your own cards are yours: leave every other card alone. The kits: {kits}."

`tests/t-briefs.sh`: a `wldn planner` and a `swb-1 conductor` check that each brief has `rail --label wldn`, `idempotencyKey`, `create-area:` and `pendingyou hold`. The existing checks must still pass.

**4.2** `plugin/roles/planner.md`. Add `{{CARDS}}` as a short section, *Cards*, after *Proposals*, starting: "The rail's proposal rows are yours: one card per proposal you open, keyed `proposal/<n>`. It carries the page `{{TEAM_CMD}} plan proposed <n>` prints, as a Markdown file, and offers approval, with a note for changes or for dropping it. It is filed in the kit of the first bolt or unit its changes name." In *Proposals*, after step 1, say that on opening a proposal the planner posts its card. Step 3 then reads: "Run `{{TEAM_CMD}} plan approve <n>` only when the user says so in your pane or answers your card, never on your own judgment." It also says a note on the card asking for changes or rejecting it is handled as the user's words. After a replacement or a drop, close the old card. When crew tells you a conductor agreed, update the card.

**4.3** `plugin/roles/conductor.md`. Add *Cards*, after *Review with the user*, with `{{CARDS}}` and which rows are the conductor's:
- a unit in review, keyed `review/<unit>/<head>`, carrying the change folder's path on this host and offering approval, with a note for changes;
- a verify report the user decides on, keyed `verify/<unit>/<stamp>`, carrying the report as a file, with what the conductor would do about each thing it raised as the options;
- the bolt, once ops reports the proof clean, keyed `land/<bolt>`, marked high stakes, offering approval.

Then the answers: approval of a review runs `{{TEAM_CMD}} unit approve <unit>`, and a note runs construct again with its words. A verify answer runs code with the chosen findings, or merge. A landing approval tells `{{MAIN_OPS}}` "Land bolt <bolt>. The user approved it on Pending You." In *Review with the user*, the conductor posts the card when it tells the user a unit is ready. In *Talking to the user*, the tell to the operator agents is limited to a wait with no card: a question in the pane, or any wait when the session has no Pending You tools. In *The building loop*, step 3 posts the verify card, and step 5 posts the landing card.

**4.4** `plugin/roles/main-ops.md`, *Landing a bolt*: "The word to land comes from the user, directly, through the planner, or through the bolt's conductor when the user approved its landing card on Pending You."

**4.5** `README.md`: a paragraph after the rail's that says how each rail row is answered through a Pending You card from its owner. It covers what the card line and the list of open cards with no row show, that crew records card acts from its agents' sessions, and that a partition without Pending You keeps the rail as it is. Add the three card acts wherever the README lists the run record's acts. `plugin/skills/crew/SKILL.md`: add "see whether a rail row's card is open, or a card has no row" | `crew rail`. Run `devenv shell -- tests/run`; `tests/t-docs.sh` checks the README against crew's usage.
