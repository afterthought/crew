# Design

## Context

See proposal.md for why. `a-card-reaches-the-user-when-the-tools-drop` gives crew `crew card post|change|close|read`:
- They act as the asking assistant through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in.
- They record each act from Pending You's reply.
- They load the hook's key and form checks.

This change makes them the only path, and moves what the hook checks into what crew builds.

Rules this rests on:
- `briefs.16`: the one path.
- `briefs.11`: whose key.
- `briefs.13`: the row's form, which crew now builds.
- `briefs.9`: what a card's words carry.
- `roles.3`: the rule held by a refusal, not words alone.
- `read.1`: a card crew cannot build is refused, naming what it could not read.
- `read.2`: Pending You's input schema read as it is.
- `code.7`: a builder is a function of the row's facts and the agent's words.
- `tests.4` and `tests.11`.

Areas touched:
- `briefs.md` (`plugin/roles/`);
- `teams.md` (`crew.py`);
- `plan.md` (`plan.py`);
- `tests.md`.

### What the test cards must settle first

ADR 0005 as amended 2026-10-12 leaves three readings, made once mac-studio is signed in again:
1. **The pane.** A card crew posts shows on its agent's herdr pane. The Pending You CLI's herdr tokens (`py_waiting`, `py_card`) are written by the wake mod from the cards its own session knows, so the expectation is: only once the session adopts the card.
2. **The hold.** `pendingyou hold <id>` in the agent's session lets its wake adopt the card. The mod answers the hold itself (`answerHold` in its `register.js`) and checks the card through the session's own connection.
3. **Lost tools.** A session that has lost its tools is still woken, or is not.

## Goals / Non-Goals

**Goals:**
- No crew agent writes a card's JSON.
- No crew agent calls a Pending You tool that posts, changes or closes a card or makes an area.
- Every crew card reaches Pending You through `crew card`.

**Non-Goals:**
- The rail reading card states from Pending You.
- Cards in the user's own sessions.
- Pending You's own permission cards: those are the CLI's, posted for the user's sessions' permission prompts. A crew agent's session runs with permissions bypassed, so it has none.

## Decisions

**A row's card is built from its row and the agent's words.**
- `crew card post <key>` takes on standard input only the words the row asks for:
  - the title;
  - the summary, whose link and bolt crew puts first;
  - the background;
  - a verify card's options;
  - a landing card's proof steps;
  - a lost card's dead-copy line.
- The kind, the `approve` block, `highStakes`, `blocking`, urgency, links and the empty files touched are crew's, by the row's key:
  - `proposal/<n>` is `crew plan card <n>`'s card whole, with nothing from the agent.
  - `land/<bolt>/<head>` is an approval of risk `high`, not reversible, because `irreversible`.
  - `verify/<unit>/<stamp>` is a `choice`, or a `multi` when the agent says several may be picked.
  - `batch/<n>` is a notice naming every unit from the run record, with its one session's link.
  - `record/<kit>/<n>/<commit>` is an approval of risk `low`, reversible.
- **What is refused.** The builder refuses words that break `briefs.9`, such as a path or a code block in a batch summary, as the form checks refuse them today. It also refuses a field the row does not take.
- Considered: keeping the form checks and having agents keep writing the JSON. Rejected because both failures of 2026-10-11 were crew's idea of the form drifting from Pending You's, found by an agent failing to post. A builder puts the form in one place, tested in the logic tier and checked against Pending You's `tools/list` input schema by a doctor row.

**crew's hook refuses a crew agent's own card calls and records nothing.**
- In a session crew started, `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area` are denied before they run, naming `crew card post|change|close` (`roles.3`).
- The reads (`get_request`, `list_pending`, `whoami`) pass, since the wake mod makes them in the agent's session.
- The PostToolUse half goes: no crew agent's card act reaches it.

**How an agent hears its answer follows test card 2.**
- **If the hold adopts the card:** `crew card post` prints the card's id and the line `pendingyou hold <id>`, and the brief has the agent run it at once. The mod answers it and nothing waits. The brief's "never run `pendingyou hold`" goes, since with the mod nothing runs.
- **If the hold does not adopt it:** `crew card post` says to read the answer with `crew card read <key>`. The brief has the agent do so at its breakpoints and whenever crew's notice names the card.
- **If test card 3 shows a session that lost its tools is not woken:** that agent reads with `crew card read` too, and crew's notice of a row's change names the card to read.

**The lost card is crew's to see.**
- `crew card read` and `change` meet a lost card as Pending You's "not found". crew refuses with `lost_card_how`'s words, and the agent posts it again with `crew card post <key> --lost`.
- `--lost` puts the dead-copy line in the summary and is the one post allowed under a key already posted under.

## Risks / Trade-offs

- [Every agent's brief changes at once] → the change lands only after the test cards have read the wake. Each agent takes it at its next fresh start, and an agent still on the old brief has its own calls refused with the command to use, so it cannot go wrong quietly.
- [The host's sign-in is a single point: when it ends, no crew agent on the host can post] → the commands say so in the bridge's words, and swancloud's doctor row shows the sign-in. Today the same sign-in, or Claude Code's per account, is already a single point for every session.

## Proof in dev

Nothing to deploy. The logic cases cover every builder. The end-to-end tests post through the stub and show an agent's own `post_request` refused. On real work, once landed: the next row of each kind a fresh agent owns posts through `crew card post` and reaches the user, and the reading records which.
