> A reading (2026-10-12): whether crew's Pending You cards would be more robust through Pending You's API than through its MCP server; it decides nothing, and its recommendation waits on the user's word.

# Pending You through its API rather than its MCP server?

The user, 2026-10-12: "Would our Pending You integration be more robust if we used the API directly and didn't use the MCP server?" Read that day by the `pendingyou` workstream agent, on mac-studio, from pendingyou.com/docs/api, /docs/webhooks, /docs/skill, /docs/api/herdr and /v1/openapi.json (version 2026-10-05), the fleet's `pendingyou` 0.28.0 and its wake mod as installed, crew at `fd0d3d8`, and the signals on `refs/crew/swancloud/main`. Nothing was posted to Pending You and no tool of its was called.

## The answer in short

- **Pending You has no API for asking.** The "person API" at /docs/api is for an app that acts *as the user*: it reads the cards their assistants ask and answers one when the user presses a key (Herdr's plugin is its first app). Its 13 routes read, answer, write to the asker, snooze and delegate; none posts or closes a card, and it "never may ... answer on a timer, from a model's decision". The one other door for posting is an **incoming webhook**, which makes a notice from a service, not a question from an agent, and sends answers only to a public HTTPS receiver.
- **The direct route that exists is crew speaking MCP itself.** A crew command can call Pending You's MCP endpoint (`https://www.pendingyou.com/mcp`) with the host's sign-in. Pending You's own command line does exactly this for its permission cards. Each call opens a short session of its own, so a card no longer depends on whether the agent's Claude Code session still has its tools.
- **Recommendation: build that, and keep MCP in the agent's session only for the wake.** crew's command would post, change, close and read every crew agent's card, building the card from the row itself, and record it in the run record from the reply it got. Agents keep the server for one thing: hearing answers. No new secret, no service, no new app. Do not build a webhook receiver or a person-API app.
- **This reverses a ruling.** ADR 0005 as amended 2026-10-09 says "crew carries no Pending You client of its own and goes around nothing", after the user doubted crew "going around the Pending You functionality that's built into Claude Code" (signal 2026-10-09-swancloud-planner-b0d57593/01). The queued unit `a-card-reaches-the-user-when-the-tools-drop` already states this route in its intent ("the owner posts and closes the row's card through crew ... with the computer's sign-in"), so it contradicts the ADR as amended. Only the user can settle that.

## What Pending You offers the asking side

### The person API: answering, not asking

- **Purpose.** "Build an app that works as the person who signs it in: it shows their cards, answers one when they press something in it." It may "see the cards the person's assistants ask them". It "never may" act on a high-stakes card, answer "on a timer, from a model's decision, or for a card the person hasn't seen", or touch the user's assistants.
- **Routes.** `GET /v1/me`, `GET /v1/cards` (with filters `status`, `area`, `assistant`, `agent`, `app` and `machine`), `GET /v1/cards/{id}`, `POST .../answer|undo|messages|later|back|delegate|take-back`, `GET /v1/changes`, `GET /v1/assistants`, `POST /v1/presence`. The OpenAPI document lists the same 13 paths and no path that creates a card. A card closes only when "its assistant picked the answer up, withdrew it, or it ran out".
- **Sign-in.** The app is registered by the user in Settings › Developers. It works at once for the user and up to 10 testers; others need review. It signs in once per computer by device code, which needs a machine attestation (`pendingyou machine attest`, from the key `npx pendingyou init` made) and the user's approval on the phone. Tokens are DPoP-bound to an ES256 key, with a new proof per request and server nonces. Access tokens last 15 minutes, and "refresh tokens change with every use".
- **Robustness features.** A version pin (`Pending-You-Version: 2026-10-05`); "/v1 only adds"; RFC 9457 problems with stable codes; `Idempotency-Key` on every change, kept for 24 hours; ETags; `version` on an answer (409 `version_conflict`); and a change feed. The feed (`GET /v1/changes?wait=25`) carries `card.created`, `card.answered`, `card.changed` and `card.closed`. It still asks the app to re-read `/v1/cards` "on start and every 10 minutes".
- **Limits.** Per sign-in each minute: 300 reads, 60 writes, 30 answers and 6 waits. Per person: 1,200 a minute.

For crew, the person API could only *read* card state, for example so the rail shows a card the user answered or dismissed in the app. The MCP endpoint's `get_request` and `list_pending` already read that under the host's existing sign-in. The person API's sign-in would also cost crew three things:
- an app registered by the user;
- a device sign-in per host, approved on the user's phone;
- ES256 signing, which Python's standard library lacks. `code.1` allows crew nothing outside it, and devenv only jq, moon, python3 and recutils.

Its refresh token rotates on every use, so concurrent crew commands on one host would race to write it.

### Incoming webhooks: notices from a service

- **The address.** `POST https://www.pendingyou.com/in/pyin_…` with JSON. "The address is the password", and it is shown once. Each webhook has one name and one area, and its cards read "<webhook name> · <from>", not as an assistant's.
- **Fields.** `title` ≤ 140, `summary` ≤ 400, `url`, `dedupeKey`, `status` open|resolved, `severity`, `from`, `intent` (heads_up, do, decide, approve, tell), `options` (2 to 5, `decide` only), `recommendedIds`, `rationale`, `action`, `text`, `approve` {action, command, risk, reversible}, `highStakes`, `urgency` and `blocking`. There are no grouped `questions`, no `multi`, no `context.background`, no artifacts or image upload, and no `askedFirst` or `follows`. Unknown fields are ignored and over-long text is cut, not refused.
- **Answers.** "decide, approve and tell ... are taken only once it has" a *Send answers to* address, a public HTTPS one. Answers come signed: `x-pendingyou-signature: t=<time>,v1=<HMAC-SHA256 of "t.body">` under a signing secret shown once. They arrive after the 5-second undo, and are retried on anything but 2xx with the same `x-pendingyou-delivery` id. The only event named is `card.answered`. The page does not say the retry count or schedule, the timestamp tolerance, the timeout or the ordering.
- **Repeats and limits.** A repeated `dedupeKey` adds to the open card. "Once you tap Got it, or it's resolved, the next notice with that key is a new card", and `"status": "resolved"` on a question withdraws it with no answer sent. Each webhook takes 60 deliveries a minute and holds 50 open notices, with what is over "counted, not shown".

### The MCP server: what the fleet runs now

- **The server.** `https://www.pendingyou.com/mcp` has 24 tools, among them `post_request`, `get_request`, `update_request`, `ack_answer`, `cancel_request`, `list_pending`, `whoami`, `match_area` and `create_area`. "Tool descriptions come fresh from Pending You on every connection", and "the fields are validated on every call". Its guide is revision 2.53. Nothing is version-pinned for an MCP client.
- **Its idempotency.** `post_request` takes `idempotencyKey`: "a retry never makes a second card". The key belongs to the host's connection, as ADR 0005 read on 2026-10-11.
- **The fleet's wiring.** The fleet (swancloud's `lib/pending-you.nix`) wires each Claude Code session to it:
  - `~/.config/pendingyou/signin/.claude.json` declares `pendingyou` as `type: http` with `headersHelper` `~/.config/pendingyou/bin/pendingyou-mcp-headers`.
  - That helper runs `pendingyou mcp-headers`, which prints `{"Authorization": "Bearer <token>"}` from the host's *connection* sign-in and refreshes it when it is stale.
  - Hooks hand answers in: `pickup` at session start and `handoff` with the next message.
  - The Stop check is off when `CREW_AGENT` is set.
  - The **wake mod** (`~/.config/pendingyou/mod`) "learns the cards the session posts to Pending You, checks them through the session's own Pending You connection" (`$.mcp.call(card.server, 'get_request', …)` in `register.js`), and starts a turn when an answer comes.
- **The command line does the same outside a session.** `pendingyou mcp --app <app>` is "a stdio MCP server for an agent that can't run a headers helper". The CLI's permission cards (`dist/permission.js` `post`) call `whoami`, `post_request`, `get_request` and `update_request` through its own MCP client (`dist/bridge.js`). That client sends `initialize` with protocol `2025-06-18`, `notifications/initialized`, then `tools/call` with the bearer token, keeps `mcp-session-id`, and re-runs the helper once on a 401.
- **Undocumented CLI endpoints.** `hold`, `pickup` and `watch` read `/mcp/cli/requests/<id>?wait=` and `/mcp/cli/answers`. No page documents them, so crew should not build on them (`read.2`).
- **Learning a card from a hold.** The wake mod learns a card the session did not post from `pendingyou hold <req_…>` run in the session. It answers that command itself ("no hold is needed in this session"), so nothing waits in the background (`answerHold` in `register.js`).

## How crew uses it now

- **Posting.** Agents call the MCP tools in their own sessions. The briefs' *Cards* sections, filled by `crew.py` `cards_how` and `lost_card_how`, tell them to call `whoami` and `list_pending` at the start, then `match_area`, and `create_area` under `create-area:<owner>/<kit>`. They post under the row's key taken from `crew rail`, close with `ack_answer` or `cancel_request`, and hear answers by the wake.
- **The hook before.** `plugin/hooks/cards --before` runs as a PreToolUse hook on `post_request`, `create_area` and `update_request`. It refuses a key that is not the agent's own (`plan.card_refusal`, read through `CardReads`). It also refuses a row's card in another form (`FORMS`, `form_refusal`, and `proposal_form` against `plan.card_model`).
- **The hook after.** As a PostToolUse hook it writes `card.post`, `card.update` or `card.close` to the run record. It parses the tool's result through `result_object`, which handles three shapes Claude Code has given, and ends the card's plannotator session (`crew card session|end|sweep`).
- **The rail.** Its card lines come from those run-record entries alone.

## What has gone wrong, and what each route would have done

| What went wrong | Cause | crew speaking MCP | Webhook | Person API |
|---|---|---|---|---|
| Sessions lost the tools for good on 2026-10-09; reviews reached the user with no card (signals fa4348e4, 6d65f646/01–02) | The server timed out from 21:16Z to 21:52Z; Claude Code never fetches tools again after a reconnection whose `tools/list` fails | Posting survives: each command opens a fresh session, fails loudly during an outage and posts again later under the same key. The wake still rides the session's connection | Posting survives, as notices | Cannot post |
| No landing card can post (`_open.md`; signals 27bc8685, 81759830, 46974ab9) | crew's form demanded `highStakes`; the service wants `approve.risk` on an approval | Same drift is possible: crew's form is still crew's. The service's refusal comes back to crew's command, which records it, so the rail shows the refusal instead of an empty row | Webhook `approve` has `risk` too; same drift | — |
| A posted card recorded with no card id (signal 02c7ce29) | The after-hook parses Claude Code's rendering of the result | Gone: crew reads the reply it got | Gone: the reply is crew's | — |
| Cards orphaned after a new sign-in (signal 291133cb; ADR 0005, 2026-10-11) | Cards and keys belong to the host's connection | Unchanged: same connection | Cards belong to the webhook; replacing its address orphans nothing open | Unchanged |
| Answers do not wake (signals c47708c4, f97c5978) | The wake needs `mcp__pendingyou` allowed in the session | Unchanged for the wake | No wake at all: answers go to the receiver | No wake |

A side observation: this reading's own session, under `CLAUDE_CONFIG_DIR=~/.claude-sub-madswan`, lists the `pendingyou` server with only `authenticate` and `complete_authentication`. A session has the tools only when its config wires the server to the helper; why this one is not wired was not read. A crew command uses the host's helper, whichever account the session runs on.

## The routes compared

| | Today: agents call MCP | crew's command speaks MCP | Webhook in, receiver out | Person API |
|---|---|---|---|---|
| Can post a crew card | yes | yes | only as a notice from the webhook's name; no grouped questions or `multi`, so not a proposal card (ADR 0018); no image upload | **no** |
| Tools dropping from a session | the card is lost until the session restarts (ADR 0005's restart, unbuilt) | posting and closing unaffected; hearing falls back to `crew card read` | n/a | n/a |
| Schema drift | the agent shapes the JSON; the hook checks crew's idea of the form; the service refuses the rest | crew shapes the JSON from the row; a doctor check can diff `tools/list`'s input schema against crew's forms; server-side rules still surface only on a post, but synchronously and recorded | unknown fields ignored and long text cut silently: drift goes unseen | versioned and pinned; irrelevant, since it cannot post |
| Validation | before (hook) and at the service | crew builds a card right by construction, then the service; the hook only refuses an agent posting around crew | the service's 422 names the field | — |
| Credentials | host's connection sign-in (`pendingyou-signin`), token by the headers helper | the same, through the same helper; crew stores nothing | a `pyin_` address per webhook and a signing secret per receiver, both shown once, both the user's to create and store | an app registration, a device sign-in per host approved on the phone, a DPoP key and a rotating refresh token per host |
| Audit in the run record | after-hook, only when the result parses; nothing when the user closes a card in the app | written by the command from its own reply, refusals too; `crew card read` can record an answer and who gave it (`by`) | every answer arrives at the receiver | change feed of every change |
| Idempotency | `idempotencyKey` = row key, per connection | the same | `dedupeKey`; after an answer the same key makes a **new** card | `Idempotency-Key` for 24 h on its own acts |
| Agents still need MCP for | everything | the wake only (and thread replies, if crew does not read them) | nothing, but nothing wakes them | everything but reads |
| Cost to build | — | about two units (below) | a hosted service (below) and MCP still for proposals | an app, sign-ins and non-stdlib crypto, and MCP still for posting |

## A webhook needs a receiver, and crew runs no service

`state.4` rules out a daemon: crew's state is plain files, and every view is computed with nothing running. A webhook's *Send answers to* needs a public HTTPS endpoint, up whenever the user answers, so crew alone can post only heads-ups and to-dos, never a decide, approve or tell card. That rules out every row's card but the batch's. The same holds for `set_wake_webhook`.

A receiver would need five things:
1. a swancloud host serving HTTPS on a public name;
2. the signing secret (the user's to create and store), with the HMAC checked over `t.body` and repeats dropped by `x-pendingyou-delivery`;
3. a crew there that writes each answer to the partition's run record as one commit (`state.1`), so it needs push access to crew-state;
4. a `crew tell` to the owning agent on its team's host (`roles.4`, `code.3`), since Pending You's wake would no longer reach it;
5. its own uptime, monitoring and doctor row.

Cards would also stop being the agent's. They would read as the webhook's name, so Herdr's per-pane badge (it maps an agent's card to its pane) would show nothing. Each kit's area would need its own webhook and address. And 50 open cards per webhook is a ceiling a busy partition could reach. That is a service, a new class of secret and a new way to fail, to replace a door that already works.

## What building the recommended route changes

- **One command for cards.** `crew card post <key> [--words <file>]`, `crew card change <key>`, `crew card close <key> --outcome|--reason` and `crew card read <key>`.
  - **Who may post.** `card_refusal` decides it unchanged.
  - **Building the card.** The card is built from the row: `crew plan card` for a proposal, `FORMS` turned from refusals into builders for a landing (its `approve` of risk high, not reversible, `because` irreversible), a verify report and a batch. The agent supplies only the words its brief asks for. Each builder is a function of facts, tested in the logic tier (`code.7`).
  - **The area.** crew finds it, or makes it under `create-area:<owner>/<kit>`.
  - **The call.** The command speaks MCP to Pending You's endpoint with the token from the fleet's `pendingyou-mcp-headers`. It could instead go through the fleet's `pendingyou mcp --app claude-code` bridge, which needs no HTTP or SSE code in crew but starts node on each call. Either way the client is the standard library (`code.1`), and a decision never makes the call (`code.7`).
  - **Recording.** The command writes `card.post`, `card.update` or `card.close` itself, and a refused post records the service's words.
- **The hook.** `plugin/hooks/cards --before` shrinks to refusing a crew agent's own `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area`, naming the `crew card` command to use. By `roles.3` one path is enforced, not described. The after-hook and `result_object` go. The user's own sessions are untouched.
- **The briefs.** `cards_how` and `lost_card_how` lose `whoami`, `list_pending`, `match_area`, `create_area`, `post_request`, `ack_answer` and `cancel_request` in favour of the `crew card` commands. Hearing becomes: crew's post prints the card's id, and the agent runs `pendingyou hold <id>`, which the wake mod answers itself and from which it learns the card. When the wake is down, the agent runs `crew card read <key>` at its breakpoints. That reverses ADR 0005's "never runs `hold`", whose reason was that nothing runs from npm; with the fleet's binary and the mod, nothing runs. A lost card is posted again by crew under the same rule.
- **The rail.** It still reads card lines from the run record. Optionally, `crew card read` lets it show a card answered or dismissed in the app, which ADR 0005 notes it misses today. That is a network read in a view: allowed, and named when it fails (`read.3`).
- **The record and the rules.**
  - ADR 0005: amended, with the 2026-10-09 clause reversed.
  - `briefs.9`, `briefs.11` and `briefs.13` details: amended.
  - A rule: "a crew agent's card is posted, changed and closed only through crew's command" in `briefs.md`.
  - `a-card-reaches-the-user-when-the-tools-drop`: rewritten as the command unit, its intent already this route.
  - `a-landing-cards-stakes-are-its-approvals-risk`: lands first and on its own. It is today's outage, and its form becomes the landing builder.
- **Size.** Two units:
  1. The command, its client and its record, with a stub MCP endpoint for the end-to-end tier.
  2. The builders, the briefs and the hook's refusal.
  The rail's read is a third, optional unit.

## What only a real card can show

These were read in code, not watched. A short spike, with test cards posted with the user's consent in the *Getting started* area, would settle them before any unit:

1. A card crew's command posts under an agent's name (`session.label`) shows on that agent's pane in Herdr.
2. `pendingyou hold <id>` in the agent's session makes its wake mod adopt the card, and the answer starts a turn.
3. A session whose tools dropped can still be woken through the mod's `$.mcp.call`, or cannot. If it cannot, polling with `crew card read` is the whole fallback.

## Decisions for the user

1. **Should crew's own command be the one path for crew agents' cards?** It would speak Pending You's MCP endpoint under the host's existing sign-in, and it reverses ADR 0005's "crew carries no Pending You client of its own". Recommended: yes. Pending You's own CLI posts this way, and it ends the card loss when tools drop.
2. **May an agent post three test cards to you for the spike above?** Recommended: yes, before the units are queued.
3. **Should webhooks and the person API be ruled out for crew's cards?** Recommended: yes. The person API cannot ask, and a webhook needs a hosted receiver, new secrets and cards that are no agent's. The person API's change feed is worth another look only if the rail must show cards closed in the app and `get_request` proves not enough.
4. **Should `a-landing-cards-stakes-are-its-approvals-risk` land first, whatever is decided here?** Recommended: yes. It is independent, and no landing card posts without it.
