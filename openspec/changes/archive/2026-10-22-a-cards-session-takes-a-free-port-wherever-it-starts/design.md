# Design

## Context

Every card's reading session goes through one function, `session_open` in `plugin/lib/plan.py`. That covers `crew card session` by hand (`card_session`), the raise of a batch's, a landing's or a long proposal's card (`reading_open`), a landing's session started again (`land_session`), and a landing wait that starts the reading it finds missing. `session_open` starts `plannotator annotate … --gate --json --result-file …` with the caller's environment plus `PLANNOTATOR_SKIP_BROWSER_OPEN=1` and `PLANNOTATOR_REMOTE=1`. It sets no port.

How plannotator 0.28.26 picks its port. This is read from the binary on deneb, `packages/server/remote.ts` and `packages/shared/port-range.ts` as bundled:

- `PLANNOTATOR_PORT` holding `<a>-<b>` (1 ≤ a ≤ b ≤ 65535) is a range. plannotator tries each port in order and takes the first it can bind. When none is free it exits, saying "Plannotator: every port in PLANNOTATOR_PORT a-b is already in use, most likely by other Plannotator sessions. Finish or close one, or widen the range."
- `PLANNOTATOR_PORT` holding one number is a fixed port. plannotator tries it five times, half a second apart, then exits.
- With `PLANNOTATOR_PORT` unset or unreadable, in remote mode, plannotator uses the fixed port 19432. When that port is held it exits, saying "Plannotator: port 19432 is already in use, most likely by another Plannotator session (remote mode uses a fixed port so it can be forwarded). …". This is the failure in the signal.

swancloud gives every agent `PLANNOTATOR_PORT=19432-19451`, `PLANNOTATOR_REMOTE=1` and `PLANNOTATOR_URL_HOST=auto` through its Claude settings (`lib/agent-config.nix`). A workspace box also exports them to its shells (`modules/workspace-box/claude.nix`). A Mac's shell gets none of them. So crew's card session works inside an agent and on the box, and fails on a Mac's shell as soon as any other remote session holds 19432.

The stub plannotator (`tests/stubs/plannotator`) takes 19432–19451 when `PLANNOTATOR_PORT` is unset. Real plannotator does not, which is why the suite never saw the failure. The end-to-end tests also export the range themselves, as an agent's environment would.

Rules this rests on: `briefs.9` (a reading card carries its session's link), `code.7` (the choice of environment is a decision on plain facts, tested in the logic tier), `tests.4` and `tests.11` (the case goes in the logic tier, and the stub behaves as the tool does), `tests.12` (one end-to-end case for the wiring), `tests.10` (moon tasks), `read.1` (a session that cannot start says why), `read.2` (plannotator's behaviour as read now), `code.1` (nothing new imported), `docs.2` (README follows a command's behaviour), and `docs.6` (what is checked after deploy). Pages whose area this touches: `plan.md` (`plugin/lib/plan.py`), `tests.md` (`tests/`) and `docs.md` (`README.md`, `openspec/`). No rule changes.

## Goals / Non-Goals

**Goals:**
- A card's session gets a free port of the range whatever environment crew runs in.
- The suite fails if crew stops giving the range.

**Non-Goals:**
- The advertised host, `PLANNOTATOR_URL_HOST`. crew already refuses a link only the host can open and says why (`local_link`). On deneb a shell's sessions take `urlHost` from plannotator's own `config.json`. This change does not set the host.
- Any change to swancloud's settings, or exporting `PLANNOTATOR_*` to a Mac's shells.
- How many sessions run at once, or ending stale ones. Ending a closed card's session is the rail's job, as it is today.

## Decisions

### 1. crew gives the range itself, keeping an environment's own range

`session_open` starts plannotator with `PLANNOTATOR_PORT` set by a new decision. That decision takes the caller's environment and returns the environment plannotator starts in. It keeps every variable as given and sets `PLANNOTATOR_SKIP_BROWSER_OPEN=1` and `PLANNOTATOR_REMOTE=1` as today. It keeps `PLANNOTATOR_PORT` when its value is a range plannotator reads (`^\d+-\d+$`, 1 ≤ a ≤ b ≤ 65535, as `parsePortSelection` reads it). In every other case it sets `PLANNOTATOR_PORT` to crew's range, `CARD_PORTS = "19432-19451"`: when the value is unset, when it names one port, and when plannotator could not read it.

Why keep an environment's range: swancloud owns the range its agents use. If swancloud widens it, crew's sessions inside agents follow without a change to crew. Why replace a single port: a card's session is one of several that run at once (a batch's, a landing's for each proven bolt, the agents' own plan reviews). A fixed port allows one, and that is exactly the failure here.

Alternatives considered:
- Always set crew's range, ignoring the environment. Simpler, but then crew and swancloud each hold a range and nothing keeps them equal.
- Pick a free port in crew by binding a socket, then hand plannotator that one port. This races with any other start between crew's check and plannotator's bind, and repeats what plannotator already does.
- `PLANNOTATOR_PORT=0` for a port the system picks. That leaves the ports the agents' sessions use, and a firewall or a forward set up for the range would not cover it.
- Read the range from the agents' Claude settings. That means reading a file Claude Code owns, from a path that varies by account, and crew reads no such file.

crew's range is swancloud's, written once as a constant beside `CARD_START`. Its comment names swancloud's `lib/agent-config.nix` as where the agents' range is set.

### 2. Every port held is the failure crew already reports

This is behaviour the spec already holds, unchanged here. No new path is needed. plannotator exits before it lists the session, `session_open` refuses with "plannotator ended before <name> was ready: <its last line on stderr>", and the raise records that as the card's `Unread` (the existing requirement "A card whose session could not start is raised all the same"). The stub's last line on stderr for an exhausted range is plannotator's own words, so the end-to-end test reads what a user would.

### 3. The stub chooses a port as plannotator 0.28.26 does

`tests/stubs/plannotator` reads `PLANNOTATOR_PORT` the way plannotator does. A range gives the first port no live session holds. One port gives that port, refused when held. Unset or unreadable gives 19432 when `PLANNOTATOR_REMOTE=1`, refused when held, and otherwise a free port of its own choosing. When the stub refuses, it exits 1 before registering, and its last line on stderr is plannotator's message for that case (Context). Its docstring names the version read for ports. Every end-to-end test already exports the range, so none changes behaviour except where it unsets it.

### 4. The documents

README's card-sessions paragraph says the link is "plain http on the tailnet, from swancloud's `PLANNOTATOR_URL_HOST` and `PLANNOTATOR_PORT`". It becomes: the host from swancloud's `PLANNOTATOR_URL_HOST`, and the port the first free one of the environment's range or else crew's own, 19432–19451. The usage headers of `plugin/bin/crew` and `plan.py`, and `SKILL.md`, say nothing of ports and stay as they are (`docs.2`).

### 5. The agents' views

Nothing the board or the bands draw changes (`code.8`).

## Risks / Trade-offs

- [crew's range drifts from swancloud's] → Only sessions started outside an agent use crew's range. A drift would only put those sessions on other ports, and the comment names where swancloud sets its range.
- [Twenty ports run out while stale sessions hold them] → The card says so in plannotator's words ("widen the range"). The rail's sweep ends closed cards' sessions. Neither is changed here.
- [plannotator changes how it reads `PLANNOTATOR_PORT`] → The stub and the decision both cite 0.28.26. A later reading changes both.

## After deploy

A deploy here is crew's landing, which every host takes at once. Under `docs.6` there is one step no check can make into code, because it needs deneb's real plannotator and the user's phone. Its doer is swancloud's main-level ops, once the landing is on deneb's checkout. On deneb, from a plain shell with no `PLANNOTATOR_*` variable, while another plannotator session holds 19432, run `crew card session batch/<n>` for an open batch card. Its link prints on a port above 19432, and it opens from the phone over the tailnet.

## Task notes

### 1.1

Add `CARD_PORTS = "19432-19451"` beside `CARD_START`, with a one-line comment that it is swancloud's agents' range (`lib/agent-config.nix`) and that a card's session takes it when the environment names no range. Add a decision, `session_env(environ)`, near `session_open`. It takes a mapping and returns a new dict as Decision 1 says, and starts no process (`code.7`). Its docstring says what it keeps and what it sets, and cites plannotator 0.28.26's reading of the variable. `session_open` replaces its `dict(os.environ, …)` with `session_env(os.environ)`.

Cases in `tests/py/test_card_commands.py`, in a section of their own that `import plan` already serves:
- unset gives `19432-19451`;
- `19440-19460` is kept;
- `19432` gives crew's range;
- `abc`, `19451-19432` and `0-10` each give crew's range;
- `PLANNOTATOR_REMOTE` and `PLANNOTATOR_SKIP_BROWSER_OPEN` are `"1"` in every case, even when the environment says `"0"`;
- `PLANNOTATOR_URL_HOST` and an unrelated variable pass through unchanged;
- the mapping given is not changed.

Update the module docstring's list of what it covers with one phrase.

### 1.2

Change the stub's port choice and docstring as Decision 3 says. Keep the rest of the stub as it is. The two refusal messages are:
- one port: `Plannotator: port <p> (PLANNOTATOR_PORT) is already in use, most likely by another Plannotator session. Finish or close that session, or set PLANNOTATOR_PORT to a different port.`
- unset: `Plannotator: port 19432 is already in use, most likely by another Plannotator session (remote mode uses a fixed port so it can be forwarded). Finish or close that session, or set PLANNOTATOR_PORT to a different port.`

The exhausted range takes plannotator's message from Context in place of the stub's own.

In `tests/t-cards.sh`, after the batch session cases where a stub session already runs on 19432, add one case. Run `crew card session` for an open batch key in the planner's name with `PLANNOTATOR_PORT` unset (`env -u PLANNOTATOR_PORT`, as line 400 unsets the URL host). It prints a link on a port other than 19432. If no second key fits the journey there, start a stub session by hand on 19432 first, so the case does not depend on the order of earlier cases. Then confirm the case fails without task 1.1: revert `session_open`'s line locally, see the refusal naming port 19432, and restore it. Say so in the summary. Run `tests/moon-tasks`, and commit `tests/moon.yml` only if it changed.

### 2.1

Rewrite the README sentence as Decision 4 gives it, in the paragraph's own style.
