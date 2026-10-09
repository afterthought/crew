# Design

## Context

Why is in `proposal.md`. What becomes true is in `specs/card-sessions/spec.md` and the `rail-cards` delta.

Today, per `the-rail-is-answered-through-cards` (built, not archived): the planner's card carries the proposal's page as a Markdown file; the conductor's review card carries the change folder's path on its host; its verify card the report as a file. `crew rail` derives each row and its card key (`rail_rows()` in `plan.py`), and crew's PostToolUse hook `plugin/hooks/cards` sees every post, update, withdrawal and close of a crew agent's card and records it, keyed by the row. The card discipline both briefs share is one token, `CARDS`, built by `cards_how()` in `crew.py`.

Readings, all on mac-studio on 2026-10-09 with plannotator 0.28.6 (`plannotator annotate --help`, `plannotator sessions --help`, the binary's own text, and sessions started and answered by hand through its HTTP API):

- `plannotator annotate <folder|file...> --gate --json --result-file <path>` serves one review of a folder or of several files, with an Approve button. On a decision it writes one JSON object to the result file (atomically) and to stdout, and the process exits: `{"decision":"approved","feedback":"<notes>"}` for Approve, `{"decision":"annotated","feedback":"<the annotations and the user's words>"}` for feedback, `{"decision":"dismissed"}` when the user closes the review. A process killed before a decision writes no result file.
- `PLANNOTATOR_SKIP_BROWSER_OPEN=1` returns before any browser is opened (the binary: `if (skipBrowserOpen) return;` ahead of `openBrowser`). `PLANNOTATOR_REMOTE=1` listens on every interface; with swancloud's `PLANNOTATOR_URL_HOST=auto` and `PLANNOTATOR_PORT=19432-19451` the session prints `http://mac-studio.ts.swancloud.net:<port>` on stderr ("Plannotator session ready — open on your device"). swancloud sets those three in `lib/agent-config.nix` for every agent on the Macs and exports them on the workspace boxes (`modules/workspace-box/claude.nix`). `--tailscale` cannot serve HTTPS on the Headscale tailnet (ADR 0005's readings), so it is not used.
- `plannotator sessions --json` lists every running session as `{index, mode, target, url, port, pid, project, label, startedAt}`, which is how crew reads a session's link and checks that a pid is still that session.
- On mac-studio today five sessions run that nobody ends, the oldest a day old (proposal 17's, the-suite-runs-as-moon-tasks's change): why a session must end with its card.

Pending You's `post_request` takes an artifact of kind `url` (`{kind: "url", title, ref}`) and `context.links`; `update_request` replaces `artifacts` with a `changeNote`; `cancel_request` takes `answeredHere` ("they answered in your conversation"); `ack_answer` closes an answered card.

Rules this design rests on: `briefs.9` (what it builds), `briefs.4` (a decision shown whole, the conductor opens nothing), `roles.2` and `roles.3` (the user's word; a rule a brief states gets a check in crew), `read.1` (refuse rather than guess), `read.2` (another tool's output read by checked facts), `read.4` (never take over what crew did not make), `code.1`, `code.2`, `code.4`, `record.1` and `record.3`, `docs.2`, `tests.4` and `tests.6`. Pages whose areas it touches: `plan.md` (`plan.py`), `teams.md` (`crew.py`, `plugin/bin/crew`), `briefs.md` (the roles), `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**

- The card's owner starts the session by naming the card's key, and crew finds the document, so no agent picks a path or a flag.
- The session's decision reaches the owner by the same means every other wait does in crew: a crew command run in the background whose end wakes the agent.
- The session's end follows the card's close in crew itself, not only in the brief (`roles.3`).

**Non-Goals:**

- Answering the card in Pending You for the user. Pending You never answers for the user, and an agent may not; the owner acts on the session's decision and withdraws the card.
- Showing the session's link on the rail. The rail shows the card; the link is on the card.
- HTTPS or a public name for the session. The link is reachable on the tailnet; a `dev.swancloud.net` name waits on swancloud's tunnel (record 0001).
- A session for a landing card, which has nothing to read.

## Decisions

### 1. One crew command, keyed by the card

`crew card session <key>`, `crew card wait <key>` and `crew card end <key>`, in `plan.py` beside the rail, which already derives every row and its key. The session runs as the caller's partition (`CREW_LABEL`, or `--label`), and is refused without one (`read.1`).

- *session* finds the row by its key among `rail_rows()` for the partition and takes its document: for a proposal, the page `plan_proposed` writes (`page(describe(...))`), written into the key's state folder; for a review, `<place>/openspec/changes/<unit>/`; for a verify report, the report's path. A review's or report's document must be on this host (the row's host is the host crew runs on), else it is refused naming the host it is on.
- It starts `plannotator annotate <document> --gate --json --result-file <folder>/result.json` detached from the caller (its own session, stdout and stderr to files in the folder), with `PLANNOTATOR_SKIP_BROWSER_OPEN=1` and `PLANNOTATOR_REMOTE=1` set by crew, and `PLANNOTATOR_PORT` and `PLANNOTATOR_URL_HOST` left as the host gives them. It then reads `plannotator sessions --json` until the started pid is listed (ten seconds at most), takes its `url`, and refuses, ending the process, when the url's host is `localhost` or a loopback address, or when the pid never appears.
- The key's state folder is `~/.local/state/crew/cards/<label>/<key>/`, the key's slashes as folders (each segment already matches `code.4`'s names or is a number or stamp). It holds `session.json` (pid, document, url, started) and, once decided, `result.json`.
- Run again while the recorded pid is listed by plannotator as serving the recorded document, it prints the recorded url and starts nothing. A recorded session that is gone, with no result file, is forgotten and a new one started. A result file left from a decided session is moved aside to `result.<started>.json` when a new session starts, so a wait never returns an old decision for a new session.

Why not have the brief run plannotator itself: the brief would carry the flags, the environment and the path for each kind of row, and nothing would stop a browser opening or a session outliving its card. Why not a separate module: the rows and keys are `plan.py`'s, and `plan.md` already binds the code that reads them.

### 2. The wait is a background command, like every other wait in crew

`crew card wait <key>` polls the key's folder every few seconds. It returns when `result.json` exists, printing the decision and, for `approved` and `annotated`, the feedback text verbatim after it; or when the session's pid is no longer listed and no result exists, printing that it ended with no decision. A `dismissed` result is printed as closed by the user with no decision. It has no timeout: a card can wait days, and the owner's restart runs it again. Run for a key with no `session.json`, it is refused.

The owner reads the printed decision as the card's answer: `approved` is the card's approval, and any notes with it are the user's words with that approval; `annotated` is a note asking for changes, in the user's words; closed or ended with no decision leaves the card open, and the owner starts the session again and updates the card's link when it changed. This is the same wake every crew wait gives (`crew unit wait`, `crew prove --wait`), so an agent needs nothing new to hear it.

Alternative considered: answering the Pending You card from the session's decision with `answer_delegated`. Rejected: that tool is for a question the user handed to another assistant, and Pending You's rule is that it never answers for the user.

### 3. The card hook ends the session; `crew card end` ends one by hand

`plugin/hooks/cards` already resolves a close (`cancel_request`, `ack_answer`) to the card's row key from the run record. After it records `card.close` with a `Key`, it calls the same end `crew card end` runs, for that label and key, on this host. End reads `session.json`; when `plannotator sessions --json` lists the recorded pid with the recorded document as its target, it sends that pid SIGTERM; in every case it removes the key's folder. A pid that is not listed, or is listed for another target, is not killed (`read.4`). The hook never fails a tool call, as now.

A card withdrawn because it is replaced (a review at a new head has a new key) ends the old key's session, so a construct run again never leaves the old change's session open.

### 4. What the card carries, and how the owner closes it

The card carries the session's link as its one artifact to read: `{kind: "url", title: "Read and annotate it in plannotator", ref: <link>}`, in place of today's file or path (`briefs.9` rules out a card with the files and no link). When the owner acts on a decision made in the session, it withdraws the card with `cancel_request`, `answeredHere: true` and the reason "answered in its plannotator session: <outcome>"; when it acts on an answer given on the card, it closes it with `ack_answer` as now. Either close ends the session through the hook.

At its start, after `list_pending`, the owner runs `crew card session <key>` for each of its own open cards that has a document (which gives back the running session's link, or starts a new one) and updates the card's link with a `changeNote` when it differs, then runs `crew card wait <key>` in the background for each.

### 5. `briefs.4` and the conductor opening nothing

`briefs.4` rules out "plannotator opened by the conductor": opening a view at the user unasked. A session started with no browser opens nothing at anyone; it serves a link the user follows when they choose. The detail of `briefs.4` is amended to say so ("a pane or browser opened by the conductor"), and `briefs.9` loses its "Not built" with the `_open.md` line. This is a clarification, not a departure.

### 6. Nothing new in the run record

Starting, waiting on and ending a session move no work (`record.1`): the card's post and close are already recorded by the hook, and what the owner does on the decision (`crew unit approve`, `crew unit run … construct`, `crew plan approve`) is recorded by those commands. A decision's text is the user's words and could not be recorded anyway (`record.3`).

## Risks / Trade-offs

- [The link is plain http on the tailnet] → It opens only on the user's tailnet devices, as every plannotator link in the fleet does today; HTTPS waits on swancloud's tunnel. Pending You's app opening an `http://` link to a tailnet name on the phone is checked under *Proof in dev*.
- [A host reboots with sessions open] → The sessions are gone with no result; the owner's restart finds each `session.json` stale, starts a new session, and updates the card's link.
- [Twenty ports per host] → One session per open card of that host's owners; a team has at most a few. A start that finds no port free is refused with plannotator's own words.
- [The user answers on the card and in the session] → The first the owner acts on wins; it closes the card, which ends the session, and the other answer has nothing left to apply to.
- [`rail-cards` is not yet in `openspec/specs/`] → Its `MODIFIED` delta archives only after `the-rail-is-answered-through-cards` is archived; `openspec validate` says so now as information.

## Proof in dev

After the bolt lands and every host has pulled, on swancloud (the user's partition for trying cards first):

1. A unit reaching review on mac-studio gets a card whose link opens the whole change in plannotator from the user's phone through the Pending You app, with no browser opened on mac-studio.
2. The same on the workspace box (`chuck-herdr-alpha`) for a team there: the link names the box's tailnet name and opens from the Mac and the phone. This also checks that plannotator is on the box's path.
3. The user annotates a passage in that session and sends it: the conductor runs construct again with those words and withdraws the card, and `plannotator sessions` on the host no longer lists the session.
4. The user approves a proposal's card in Pending You without opening the link: the planner approves, closes the card, and the proposal's session is gone.

## Task notes

### 1.1

In `plan.py`, a `card` command with `session`, `wait` and `end`, each taking a key and `--label`. Add to each dict `rail_rows()` returns a `doc`: `None` for a land row, `("page", label, n)` for a proposal, `(host, "<place>/openspec/changes/<unit>/")` for a review, `(host, report path)` for a verify row; `session` reads the rail for the one partition (as `rail_view` does, without the run record: `times` may be `{}`) and finds the row by key. Keys are checked with the hook's four patterns before anything is read; `land/` is refused with "a landing card has no document to read". The proposal's page is `page(describe(fleet, label, w.plan, p), label)` as `plan_proposed` writes it. Start plannotator with `subprocess.Popen(..., start_new_session=True, stdin=DEVNULL)`, stdout and stderr to `out` and `err` in the key's folder. plannotator not on the path is refused naming it (`code.2`). The url check: `urllib.parse.urlsplit(url).hostname` in `localhost`, `127.0.0.1`, `::1`, or starting `127.`.

### 1.2

`wait` polls every 5 seconds; prints `<key>: approved`, `<key>: annotated`, `<key>: closed in plannotator with no decision` or `<key>: the session ended with no decision`, then the feedback text as it is, when there is one. Exit 0 for each of these; refused (non-zero) only for a key with no session.

### 1.3

`end` is a function the hook can import: `end_session(label, key)`. It reads `plannotator sessions --json` once, kills only a pid listed with the recorded target, and removes the folder. `crew card end` prints what it ended, or that no session was running for the key.

### 1.4

`tests/stubs/plannotator` stands in for plannotator: `annotate … --gate --json --result-file <f>` registers itself (pid, target, a url from `PLANNOTATOR_URL_HOST`, defaulting in the stub to `localhost` when unset, and a port) in a file under the test's scratch home, prints the ready line on stderr, and waits until a decision file the test writes appears, then writes it to the result file and exits; `sessions --json` lists the registered sessions whose pid is alive. Per `tests.4` it behaves as the readings above say: the three decision shapes, no result on a kill, no browser. It records in the registry whether `PLANNOTATOR_SKIP_BROWSER_OPEN=1` was set, so the test can assert it.

### 1.5

`tests/t-card-session.sh`: a review, a proposal and a verify key each start a session on the right document; the same key run again gives the same url and one process; a land key, a stale review key, a document on another host and a localhost url are each refused with nothing left running; each of the three decisions and a killed session is what `wait` prints; a decision made before the wait is returned at once; `end` kills only a listed pid with the recorded target. Run `tests/moon-tasks` and commit `tests/moon.yml`.

### 1.6

`plugin/bin/crew` routes `card` to `plan.py`, as it does `rail`, and its usage header names `crew card session|wait|end <key>`; README's cards paragraph says a reading card links a session crew starts and ends with the card; `plugin/skills/crew/SKILL.md` gains a row for it. All three together (`docs.2`); `tests/t-docs.sh` checks the usage.

### 2.1

In `plugin/hooks/cards`, after `record.emit` for `card.close` with a `Key`, import `plan` and call `end_session(label, key)` inside the existing `try`, so a failure is one line on stderr and never fails the tool call. `tests/t-cards.sh` gains: a `cancel_request` and an `ack_answer` on a keyed card each end its session; an unkeyed card's close and a session crew did not start end nothing.

### 3.1

`cards_how()` gains, after the paragraph on posting: for a proposal, review or verify row, run `crew card session <key>` before posting and put its link on the card as a `url` artifact titled "Read and annotate it in plannotator", in place of a file or a path; then run `crew card wait <key>` as a background command. Its end is the session's answer: approved is the card's approval, annotated is the user's note asking for changes in their words, closed or ended with no decision means start the session again and update the card's link if it changed. Having acted on a session's decision, withdraw the card with `cancel_request`, `answeredHere` true and a reason saying it was answered in its session. At your start, for each of your open cards with a document, run the session and the wait again. Never open a browser for a card, and never run `plannotator` yourself for one: crew starts and ends the card's session. Keep it plain English, one paragraph, in the voice of the rest of `cards_how()`.

### 3.2

`planner.md` *Cards*: the proposal's card carries the link to its session, not the page as a file. `conductor.md` *Cards*: the review card carries the link to the session on the unit's change, not the folder's path; the verify card the link to the session on the report; the landing card no link. *Review with the user* keeps "open nothing": the conductor tells the user in words, and the card carries the link. `t-briefs.sh` pins phrases from each, per `tests.6`: "crew card session", "crew card wait", "answeredHere", and "Never open a browser for a card".

### 3.3

`docs/architecture/briefs.md`: drop "Not built: `_open.md`." from `briefs.9`'s detail and add `crew card session` and the card hook as its source; amend `briefs.4`'s detail "plannotator opened by the conductor" to "a pane or browser opened by the conductor; a card's session, started with no browser, opens nothing". `_open.md`: remove the `briefs.9` line.
