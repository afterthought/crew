# Design

## Context

See proposal.md for why.

### How a card is posted today

- **The agent's own tools.** A crew agent calls Pending You's MCP tools in its own session: `whoami`, `match_area`, `create_area`, `post_request`, `update_request`, `ack_answer` and `cancel_request`.
- **The hook before.** `plugin/hooks/cards --before` refuses a key that is not the agent's (`plan.card_refusal`) and a row's card in another form (`form_refusal`, `proposal_refusal`).
- **The hook after.** The PostToolUse half records `card.post`, `card.update` or `card.close`, reading the card's id from Claude Code's rendering of the tool's result (`result_object`). It ends a closed card's plannotator session (`plan.end_session`).

### What Pending You gives an assistant outside a session

Read on 2026-10-12 (the reading `openspec/explorations/pending-you-api/reading.md`, and Pending You's CLI 0.28.0 as installed):
- **The bridge.** `pendingyou mcp --app <app>` is "a stdio MCP server for an agent that can't run a headers helper: it passes each message on to Pending You with that agent's sign-in here".
  - Each line on standard input is one JSON-RPC message, and each reply one line on standard output.
  - The sign-in's token, its refresh, the MCP session id and the server's event streams stay inside it.
  - A failure of its own is a JSON-RPC error: code -32001 when the computer is not signed in or its sign-in has ended, -32000 when Pending You can't be reached. It also says so on standard error, after `pendingyou mcp: `.
- **The CLI's own client.** Pending You's permission cards post through the same client (`dist/permission.js`, `dist/bridge.js`):
  - The handshake is `initialize` (protocol `2025-06-18`), then `notifications/initialized`.
  - Every session's first call is `whoami` with the asker's name.
  - A result is read as its `structuredContent`, else as its first text block that parses as a JSON object.
  - A refusal is a result with `isError` true, whose first text block, cut to 300 characters, is Pending You's words.
  - An area is `match_area`'s first suggestion's `areaId` (`prj_…`) unless its `decision` is `create`; otherwise `create_area`, read back the same way.
- **The tools' inputs** are on pendingyou.com/docs/skill:
  - `post_request`: `idempotencyKey`, `areaId` and `session` {label, machine, cwd} beside the card's own fields.
  - `update_request`: `requestId`, `name`, `expectedVersion`, `changeNote` and the fields that change.
  - `ack_answer`: `requestId`, `name`, `expectedVersion`, `outcome`.
  - `cancel_request`: `requestId`, `name`, `reason`.
  - `get_request`: `requestId`, `name`. It returns `status`, `turn`, `version`, `answer` and `messages`.
- **The sign-in.** On mac-studio the host has had none since 2026-10-10 (ADR 0005 as amended 2026-10-12, `_open.md`), so the bridge answers -32001 there today. No reply in this design was read from the live endpoint. The stub is drawn from the CLI's code and the docs above, and is checked against the live endpoint by the three test cards once the host is signed in.

### Rules this rests on

- `briefs.16`: the one path; this change builds the commands it names.
- `briefs.11` and `briefs.13`: whose key, and in what form; checked as the hook checks them.
- `roles.3`: the command refuses what the hook refuses, so the new path is no way round a rule.
- `read.1`: what crew cannot read, it refuses and names.
- `read.2`: Pending You's replies are read by the facts above, and an absent field never becomes text.
- `code.1`: the standard library only.
- `code.2`: every refusal is a `Refusal`.
- `code.7`: each decision is a function of facts, the bridge thin around them.
- `state.4`: nothing runs between commands.
- `tests.4`, `tests.10` and `tests.11`: logic cases for the decisions, one end-to-end test for the wiring on a stub, and the moon tasks.
- `docs.2`: usage, README and skill together.

Areas touched:
- `plan.md` (`plugin/lib/plan.py`);
- `record.md` (the acts recorded);
- `tests.md` (`tests/`);
- `docs.md` (README, the skill and this change).

`plugin/lib/cards.py` is new and on no area's page; the decisions it holds are the card rules of `briefs.md`.

## Goals / Non-Goals

**Goals:**
- An agent whose session has lost Pending You's tools, or never had them, posts, changes, closes and reads its card with one crew command.
- The card is recorded from Pending You's own reply.
- The command refuses exactly what the hook refuses, plus what Pending You refuses, in their words.

**Non-Goals:**
- Moving the briefs to the commands, refusing an agent's own Pending You calls, and building a row's card from its row: `every-crew-card-goes-through-crew`, after the test cards.
- Hearing an answer: the wake stays the agent's session's, and `crew card read` is how an agent with no wake reads its answer.
- The rail reading Pending You.
- A Pending You client over HTTP in crew, a person-API app or a webhook (the reading, ADR 0005).

## Decisions

**crew speaks to Pending You through the fleet's `pendingyou mcp --app claude-code`, over its standard input and output.**
- What stays Pending You's: token handling, refresh, the session id and event streams.
- What crew holds: a short client that writes lines and reads lines.
- The binary is the fleet's `pendingyou` on the path: nothing of Pending You runs from npm (ADR 0005).
- Tests use a stub in `tests/stubs/`, as for herdr and plannotator.
- Considered: speaking HTTP to `https://www.pendingyou.com/mcp` with the token the fleet's headers helper prints. Rejected because crew would then parse event streams, carry the session id and run the helper again on a 401, all of which the bridge does already.

**One bridge session per command, whose first call is `whoami` with the agent's crew name.**
- The command starts the bridge, sends `initialize` and `notifications/initialized`, introduces the agent, does its act and closes the bridge's input.
- Nothing is kept between commands. A command that fails leaves nothing behind for the next to inherit, which is the point against a session's lost tools.
- Pending You's session memory wants an assistant to introduce itself before it acts (signal 2026-10-11-swancloud-planner-291133cb/01).

**Each call waits at most 60 seconds for its reply.** That is the timeout Claude Code's own transport used on 2026-10-09. Past it crew ends the bridge and refuses: "Pending You did not answer <tool> within 60 seconds", with "post it again later" for a post (`read.1`).

**A reply is read as the CLI reads it.**
- The object: `structuredContent` when it is an object, else the first text block that parses as a JSON object.
- A refusal: `isError` true, refused in Pending You's own words (the first text block, cut to 300 characters).
- An error from the bridge: refused in the bridge's words, with -32001 named as the sign-in.
- An id: read only when it has its prefix (`req_` for a card, `prj_` for an area). A reply without one is refused as unread, never taken as empty.

**crew sets `idempotencyKey`, `areaId` and `session`, and refuses a card that gives any of them.**
- The idempotency key is the card key, so a retry gives Pending You's card back and never posts a second.
- The session is {label: the agent's crew name, machine: this host, cwd: the folder the command runs in}, as the card discipline has agents give it today.
- A card naming one of the three is refused rather than overwritten, since the agent meant something crew would not do.

**The area is matched from the folder's git remote, or the kit's made under its key.**
- crew reads `git remote get-url origin` in the command's folder and normalises it as Pending You's CLI does (`github.com/<owner>/<repo>`).
- It calls `match_area` with the folder, the remote and the agent's name. Its first suggestion's area is the card's unless the decision is `create`.
- Otherwise crew makes the kit's area: `create_area` under `create-area:<owner>/<repo>`, named for the repo, in the group the partition's label names, with `match_area`'s proposed tint (sky when none), and the remote linked. `plan.card_refusal` first refuses an area the agent may not make, as the hook does.
- A folder with no git remote names no kit, so the post is refused saying so.

**The key and form checks are the hook's own.**
- `cards.py` loads `plugin/hooks/cards` as a module and asks its `refusal` with the input Claude Code gives the hook before `post_request` or `update_request`: the tool's name, the card as its input, no session id.
- So the agent's identity is read from `CREW_AGENT` and `CREW_LABEL`, and the proposal, batch and landing checks are the same code on both paths.
- `every-crew-card-goes-through-crew` replaces the checks with builders, and the load goes with them.
- Considered: moving the checks into `cards.py` now. Rejected because `a-landing-cards-stakes-are-its-approvals-risk`, in a held bolt, changes them in the hook, and moving them would set that bolt against this one for nothing.

**The card a key names is the agent's newest post under it that nothing closed, read from this host's run record.**
- An owner posts from its own host, so its entries are here before they reach the branch.
- `card_under(entries, key, by)` is a function of the entries.
- No such card is refused, naming the key, since there is nothing to change, close or read.

**`close` acks or withdraws, and ends the card's session as the hook does.**
- `--outcome` reads the card's version and calls `ack_answer` with it.
- `--reason` calls `cancel_request`. A card that has no answer is withdrawn, never acked.
- Then the plannotator session for the key is ended (`plan.end_session`): on this host for a row's key, or by `crew card end` started apart for an old batch key. A record key has none.
- When the session's list cannot be read, the command says so in `end_session`'s words and keeps the session for the rail to sweep (`read.1`).

**Each act is one run-record entry, written after Pending You's reply.**
- The entries are `card.post`, `card.update` and `card.close`, as the hook writes them: the row's object in On (the hook's `keyed`), the card's id in Card and the key in Key.
- A refused act is the same act with `Refused` and crew's or Pending You's words, through `plan.refused`, as every refused act that moves work is.
- `crew card read` records nothing (run-record "A command that only reads").

**`read` prints what the user said.**
- It prints the card's status and whose turn it is.
- When the turn is the agent's, it also prints the answer: the options picked, the approval, the text or the step that failed, and the user's note.
- It then prints each message after the newest the user wrote, and `--json` prints Pending You's object whole.
- What `get_request` leaves out is left out (`read.2`).

## Risks / Trade-offs

- [The stub answers as the CLI's code and Pending You's docs say, not as the live endpoint was seen to] → the three test cards check it once the host is signed in, before `every-crew-card-goes-through-crew`; a difference changes the stub and the client together (`read.2`, `tests.4`).
- [`pendingyou mcp` is in the CLI's usage, not on pendingyou.com/docs] → it is the CLI's own client, the one its permission cards use; the doctor's Pending You row is where a change in it would show.
- [mac-studio has no host sign-in today, so the commands refuse there until the user signs it in] → said in the bridge's words: "Claude Code on this computer isn't signed in to Pending You". Nothing is posted twice.
- [A card posted by `crew card post` is on the host's connection, which an agent's session on Claude Code's own sign-in cannot see] → no agent is told to use the command until the test cards have read the wake with the host signed in (`every-crew-card-goes-through-crew`).

## Proof in dev

Nothing to deploy. The logic cases and `tests/t-card-commands.sh` prove the commands on the stub.

On real work, with the user's consent of 2026-10-12, three test cards are posted through `crew card post` to the user once mac-studio is signed in, and the reading records what each showed:
1. whether a card crew posts shows on its agent's herdr pane;
2. whether `pendingyou hold <id>` in the agent's session lets its wake adopt the card;
3. whether a session that has lost its tools is still woken.

## Task notes

### 1.1
`cards.Bridge`:
- **Process.** `subprocess.Popen(["pendingyou", "mcp", "--app", "claude-code"])` with pipes, in binary mode. Replies are read line by line from the raw descriptor with `select`, so a deadline holds.
- **Replies.** A reply is matched by its id. Notifications and other ids are skipped.
- **Ending.** `close()` ends the input and waits five seconds before killing.
- **Errors.** Every failure is a `Refusal`.

### 1.2
These take no process:
- `remote_of(url)`, as the CLI's `remoteOf`;
- `reply_object(result)`;
- `refused_by(result)`;
- `post_args(card, key, name, machine, cwd, area)`, which refuses a card giving crew's fields;
- `area_of(matched)`, returning the area id or None for create;
- `create_area_args(remote, label, matched)`;
- `card_under(entries, key, by)`;
- `answer_lines(got)`.

### 2.1–2.4
In `plan.py`:
- The parsers sit beside `card session|wait|end|sweep`.
- The commands are `card_post`, `card_change`, `card_close` and `card_read`.
- `ACTS` gains `("card", "post"): "card.post"`, `("card", "change"): "card.update"` and `("card", "close"): "card.close"`.
- The label is `--label`, else `CREW_LABEL`; a command with neither is refused.

### 3.1
`tests/stubs/pendingyou` answers `mcp --app claude-code` and nothing else.
- **State.** Its cards live in `$HOME/.stub-pendingyou/cards.json` and its areas in `areas.json`.
- **Log.** Each call is logged as `<host> pendingyou <tool> <arguments as JSON>` in `$CREW_TEST_LOG`.
- **Answers.** It gives a known key's card back. It refuses in Pending You's way, `isError` with text, what a test names in `$HOME/.stub-pendingyou/refuse` (`<tool> <words>`). It answers -32001 for every request when `$HOME/.stub-pendingyou/signed-out` exists.
- **Shape.** Its replies are text blocks of JSON, the form the CLI reads when `structuredContent` is absent.
- **A test's levers.** A test answers a card by writing `answered/<id>.json`.

`tests/run` adds `pendingyou` to the commands its stubs must shadow.

### 3.2
`tests/t-card-commands.sh` uses the world `t-journey-review.sh` builds, with one bolt, one unit and a verify report, so the conductor holds a row key. It covers:
- a post, with what Pending You was called with and the entry recorded;
- a retry under the key;
- a key and a form crew refuses, with nothing sent;
- Pending You's refusal, recorded;
- a signed-out host;
- a change with the version read;
- a read before and after an answer;
- a close by outcome and by reason, its session ended.
