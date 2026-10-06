# Tasks

## 1. Reading a transcript

- [ ] 1.1 Probe, before building: in a real crew agent's session on mac-studio and on the box, run a command that reads the session's own transcript and looks for its own command line. Record in design.md whether the running command is there, and under which account directory the transcript was found. Verify by the probe's output on both hosts; if the command is absent, switch the canary to the session's previous record as design.md says, and say so there.
- [x] 1.2 `plugin/lib/transcript.py`: find a session's file under `~/.claude*/projects/*/`; parse lines as JSON, ignoring a trailing partial line; walk every string of a line; compare with whitespace collapsed; skip strings containing `crew signal`; the canary; the verdict (`verified`, `found`, `unverified` with its reason, or refused) and the source line; `asserted_by` for a `verified` record. Verify with fixture transcripts in `tests/`: typed text, a `tool_result` with string content and with list content, a `[crew tell from …]` message, an excerpt only in an assistant record, an excerpt nowhere, a file with no `type` fields (grades `found`), a file that is not JSON, a file without the command (grades `unverified`), and whitespace differences.

## 2. The capture and the signal

- [x] 2.1 `crew signal` for an agent: `--excerpt` or `--excerpt-file` required; the check; the capture's key and directory by grade; `where` from the agent's name, the plan and the slots file; the raw line appended to `~/.local/state/crew/<label>/raw/<capture>.jsonl`; `capture.md` and the signal file in the shapes of design.md; one write on the flywheel's branch. Verify against the state test remote: a verified capture's files and commit, that the blueprints remote received nothing, and that the raw file holds the source line and no repository does.
- [x] 2.2 A second signal from the same record joins the capture as the next number and updates its count; the same slug and excerpt again writes nothing and prints the id. Verify both, including under a replayed push.
- [x] 2.3 Refusals: no excerpt; an excerpt that is not in a readable transcript. Each leaves a refused `capture` entry holding neither assertion nor excerpt. A transcript crew cannot read writes the capture `unverified` with the reason. Verify with the fixtures of 1.2.
- [x] 2.4 The user's note: with no `CREW_AGENT`, the text is assertion and excerpt, `source: operator`, `excerpt: own`, kind `ask` by default, no transcript read. Verify the files.
- [x] 2.5 The `capture` entry names `signals/<id>` and the commit. Verify `crew trace signals/<id>` begins with it.

## 3. Looking signals up

- [x] 3.1 One lookup, the flywheel's branch then the first blueprints repo's main, used by `crew signal move` and `crew unit add --signal` (direct and inside a proposal). Verify a move and a route for a signal in each home, and the refusal for an id in neither.
- [x] 3.2 `crew signal show <id>`: the signal, its capture's provenance in plain lines, its grade and its move, from any host. Verify from a simulated host that holds no team, for a state signal and for a blueprints signal without the new fields.

## 4. What crew sends

- [x] 4.1 `crew tell` sends `[crew tell from <sender>] <text>`; `greet` and crew's notices send `[crew] <text>`. Update the tests that assert on text sent to the stub `herdr`. Verify a capture whose excerpt is in a tell says that agent asserted it, and one in a `[crew]` notice says crew.
- [x] 4.2 Every role brief gains the sentence on what `[crew tell from <agent>]` and `[crew]` messages are. `conductor.md`, `ops.md`, `main-ops.md`, `design.md`, `planner.md` and `operator.md` say how to record a finding with its excerpt and what a refusal means. Verify every brief prints for its fixture with no unfilled token.
- [ ] 4.3 `README.md` ("Signals": the excerpt, the grades, where signals live, `crew signal show`), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 5. Outside crew

- [ ] 5.1 The blueprints repos' `signals/README.md` (willdan-blueprints first), as a reviewed commit: signals recorded through crew live on the flywheel's branch of the state repository, in this README's shape; the capture fields crew writes (`key`, `host`, `session`, `record`, `at`, `excerpt`, `asserted_by`, `where`, `raw`) and the three grades; the daily pass and its signals are unchanged. Verify the README's example of a crew capture matches one crew wrote.

## 6. Proof on real work

- [ ] 6.1 Pull on every host and restart wldn's agents. In swb-2's conductor's pane, say something about work outside its bolt. Verify the conductor records a signal whose excerpt is your words exactly; `crew signal show <id>` on mac-studio prints `verified`, `asserted_by: user`, the box, the session, the bolt it was working in and the raw path; the commit is on `wldn/main`; and willdan-blueprints' main did not move.
- [ ] 6.2 Ask the conductor to record a finding from a command's output, then ask it to record one "in its own words". Verify the first is `verified` with a tool as its source, and the second is refused, leaves a refused entry in the run record, and writes nothing.
- [ ] 6.3 On the box, read the raw file the first capture points at. Verify it is the one transcript record, and that `zoe <session>` (where installed) opens the session it names.
