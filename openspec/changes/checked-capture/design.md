# Design

## Context

See proposal.md for why. The current state, after `state-repository`:

- `crew signal <slug> "<what it asserts>" [--kind K] [--subject a,b] [--excerpt "<text>"]` (`plan.py signal`) writes, on main of the partition's first blueprints repo, `signals/<date>-<agent>/capture.md` and `signals/<date>-<agent>/NN-<slug>.md`: one capture per agent and day, `source: crew`, `status: read`, no pointer to any source, the excerpt optional and unchecked.
- The shape of a capture and a signal is the blueprints' `signals/README.md` (read it in `WilldanGroup/willdan-blueprints`): a directory per capture with `capture.md` and one markdown file per signal; a signal has frontmatter (`signal`, `kind`, `who`, `subject`, `claims`), one or two sentences of assertion, and the excerpt as a blockquote with its position. Raw material is never committed (`.raw/` is gitignored); the capture cites its source so that anyone with access re-fetches it.
- The daily pass (`signals/bin/sweep` and the `signal-capture` skill, in the blueprints repo) writes meeting captures and signals there, by committing in a checkout. It is not touched by this change.
- A flywheel's state is the branch `<label>/main` of its state repository, written by `plan.py`'s `write`, several files in one commit, with the run record carried.
- crew can find an agent's Claude session from herdr and its transcript on the host, as `crew status` and `run-record` do: `~/.claude*/projects/*/<session id>.jsonl`. The glob matters: accounts keep their own directories (`~/.claude-sub-<name>/`).
- `crew tell` and `greet` type their text into the agent's pane through herdr, so in the recipient's transcript they are indistinguishable from the user's typing.

What is known of the transcript's format, from zoetrope's study of it (`furkankly/zoetrope`, `docs/DESIGN.md`), which calls it undocumented and liable to change: one JSON object per line; records the session received have a top-level `type` of `user`, with `message.content` either a string (typed text) or a list of blocks, among them `text` blocks and `tool_result` blocks whose `content` is a string or a list; assistant records hold `tool_use` blocks with the command in `input`; most records carry `uuid` and `timestamp`.

## Goals / Non-Goals

**Goals:**
- A signal always carries the words it rests on, and crew says honestly how well it checked them.
- The check can only ever refuse a paraphrase. Anything crew cannot read lowers a grade.
- The source can be read again by whoever can reach the host, and none of it but the excerpt enters git.
- The user's words to an agent stay out of the design repository.

**Non-Goals:**
- A reader that turns a long exchange into several signals later. The capturing agent writes the signal, because it is the only reader that holds the source.
- Changing the daily pass or the home of meeting signals.
- Curation, the agenda, or what becomes of a signal. Agents still tell the planner about a finding until `curation-and-agenda` changes their briefs.
- Keeping transcripts. Claude Code removes old ones; the banked record is what lasts.

## Decisions

### The check, and how it degrades

`crew signal` runs on the agent's own host (it is a `plan.py` command, never forwarded), so the transcript is local.

1. **The session.** `CREW_SESSION`, else herdr's session id for `CREW_AGENT`. None: grade `unverified`, reason "herdr names no session".
2. **The file.** The first match of `~/.claude*/projects/*/<id>.jsonl`. None: `unverified`, "no transcript for session <id>".
3. **The lines.** Each complete line is parsed as JSON; a trailing partial line is ignored. Any other line that fails: `unverified`, "the transcript is not JSON lines".
4. **The canary.** Some string anywhere in some line contains both `crew signal` and the slug: the command that is running. Not found: `unverified`, "crew could not find its own command in the transcript".
5. **The search.** The excerpt and every string in every line are compared after collapsing whitespace runs to one space. Strings that contain `crew signal` are skipped: they are the command itself and its echoes. Lines whose top-level `type` is `assistant` are skipped: they are what the agent wrote itself, its reply and its reasoning, where a paraphrase is usually composed before it is run. With `--excerpt-file`, lines that name the file are skipped: they are the writing of it, whose tool output holds the agent's own words. The search walks the whole JSON value of each line and knows no field names.
6. **The verdict.**
   - A match in a line whose top-level `type` is `user`: `verified`. The latest such line is the source record. Its `uuid` and `timestamp` are recorded when present.
   - A match only in other lines: `found`. The latest is the source record.
   - No match: **refused**: "the excerpt is not in your session's transcript: quote the words as you received them, from the user or from a tool's output".

crew knows two facts about Claude Code's format: a top-level `type` of `user` marks a record the session received, which only the `verified` verdict uses, and one of `assistant` a record the agent wrote, which the search skips. Steps 3 to 5 need only JSON besides. If the format changes so that `type` moves, grades fall from `verified` to `found`, and words the agent had already written in its own record are found rather than refused; if lines stop being JSON or crew cannot see its own command, grades fall to `unverified`; nothing is refused that is not a paraphrase, and nothing stops a capture.

Who asserted it (`asserted_by`), for a `verified` record, read as far as crew can; for `found` and `unverified`, `unknown`:
- the record holds a `tool_result` block: `tool`;
- the typed text begins `[crew tell from <name>]`: `agent:<name>`, or `user` when `<name>` is `<user>@<host>`;
- it begins `[crew]`: `crew`;
- otherwise: `user`.

`--excerpt-file <path>` reads the excerpt from a file, for words the shell would mangle; the canary then looks for `crew signal` and the slug alone, and the lines that name the file are not searched.

The first build task is a probe on a real session, on a Mac and on the box, that the running command is in the transcript by the time `crew signal` reads it. If it is not (Claude Code might write the record after the tool returns), every capture would be `unverified`; the fallback, decided then, is to take the canary from the previous record of the session, and the grades are otherwise unchanged.

*Alternatives:* refusing whatever cannot be verified would turn a format change into a day with no captures. No check at all is today's behavior. A stricter parse of the transcript (pairing `tool_use` with `tool_result`, as zoetrope does) buys nothing the grade needs.

This reads one fact of a format that crew already reads for `crew status`, with a fallback. Writing transcripts for another tool to read was rejected in the findings-to-design proposal for the opposite reason: every field a foreign parser trusts would have to be right, and kept right.

### The capture's identity

| Grade | Key | Directory |
|---|---|---|
| `verified` | `session/<session id>/<record uuid>` | `<date>-<agent>-<first 8 of the uuid>` |
| `found` | `session/<session id>/line-<sha256 of the line, 16>` | `<date>-<agent>-<first 8 of that hash>` |
| `unverified` | `unverified/<agent>/<sha256 of the excerpt, 16>` | `<date>-<agent>-<first 8 of that hash>` |
| the user's note | `operator/<user>@<host>/<sha256 of the text, 16>` | `<date>-<user>-<host>-<first 8>` |

`<date>` is the record's UTC date when it has a timestamp, else today's. `<agent>` is the agent's name, lowercased, other characters as dashes, as today. Inside the write, crew looks for `signals/<directory>/capture.md` at the tip: absent, it writes the capture with the signal as `01`; present with the same key, it adds the next signal and rewrites the capture's `signals` count; present with the same key and a signal of the same slug and excerpt, it writes nothing and prints that signal's id. A directory name that exists in the blueprints' `signals/` is refused, which the shapes of the two names make impossible in practice.

### The files

`signals/<capture>/capture.md` on the flywheel's branch:

```markdown
---
capture: 2026-10-05-swb-2-conductor-9f2c1a7e
source: crew-session
key: session/3f0c2d1e-…/9f2c1a7e-…
captured_by: swb-2-conductor
host: chuck-herdr-alpha
session: 3f0c2d1e-…
record: 9f2c1a7e-…
at: 2026-10-05T14:21:07Z
excerpt: verified
asserted_by: user
where: team swb-2, bolt smoke-2, unit cfn-lint-treefmt
raw: chuck-herdr-alpha:~/.local/state/crew/wldn/raw/2026-10-05-swb-2-conductor-9f2c1a7e.jsonl
event_date: 2026-10-05
imported: 2026-10-05
status: read
signals: 1
---

# swb-2-conductor, 2026-10-05 14:21Z

One record of swb-2-conductor's session, captured with crew signal.
```

An `unverified` capture has `unverified: <reason>` and no `record`, `at` or `raw`. The user's note has `source: operator`, `excerpt: own`, `asserted_by: user` and no session.

`where` is read without asking the agent: the team from the agent's name; the bolt that team holds, from the plan; the unit a slot agent's slot holds, from the team's slots file. A main-level agent's is `main level`; the operator agent's, `operator session`.

`signals/<capture>/NN-<slug>.md`:

```markdown
---
signal: 2026-10-05-swb-2-conductor-9f2c1a7e/01-cfn-nag-templates
kind: ask
who: user
subject: [cloudformation, security]
---

The user wants a security check on Switchboard's CloudFormation templates beside cfn-lint's validity check.

> "<the excerpt, verbatim>" — 14:21:07Z
```

`who` is the asserter: `user`; the capturing agent for a tool's output, since the agent is asserting what the output shows; the sending agent for a tell. The position after the quotation is the record's time, `line <n>` for `found`, and `unverified` when there is none. `--kind` keeps its five values and its default, `constraint`, for an agent; the user's note defaults to `ask`.

The capture and the signal are one `write` on the flywheel's branch, one commit, subject `signals(<id>): <slug> (<agent>)`, entry `capture` with `On: signals/<id>`.

### The raw record

For `verified` and `found`, the source line is appended, byte for byte, to `~/.local/state/crew/<label>/raw/<capture>.jsonl` on the host, before the write; a second signal from the same record finds it there already. The capture's `raw` is `<host>:<that path>`. It is one line, not the exchange around it; the transcript, while it lasts, is the context, and `host` and `session` point at it.

### Looking a signal up

`signals/<id>` is resolved as `signals/<id>.md` on the flywheel's branch, then on main of the partition's first blueprints repo. `crew signal move`, `crew unit add --signal` and `crew signal show` use the one lookup. `crew signal show <id>` prints the signal file, its capture's frontmatter in plain lines, and its move when it has one.

The two signals of 2026-10-03 and every meeting signal stay where they are and read as they stand; nothing is converted.

### Marking what crew sends

`crew.py tell` sends `[crew tell from <sender>] <text>`, the sender being `CREW_AGENT` or `<user>@<host>`. `greet` and the notices `notify` sends (a plan write's subject, a proposal that touches a bolt) send `[crew] <text>`. Every brief gains one sentence beside its roster: a message that begins `[crew tell from <agent>]` is from that agent and one that begins `[crew]` is from crew; anything else in the pane is the user.

### Briefs

`conductor.md`, `ops.md`, `main-ops.md`, `design.md`, `planner.md` and `operator.md` each say how to record a finding: `crew signal <slug> "<what it asserts, in a sentence>" --excerpt "<the exact words the user said or the tool printed>" --kind …`; the excerpt is copied, never reworded, and a refusal means the words were reworded. Who they tell afterwards is unchanged here.

### What must not break

- `crew signal move` and `crew unit add --signal` work for signals in either home.
- The daily pass and its signals are untouched, and so is the blueprints' main.
- A capture is never blocked by a transcript crew cannot read.
- Tests that assert on the text a stub `herdr` was sent expect the prefixes.

## Risks / Trade-offs

- [The running command is not yet in the transcript when crew reads it] → the probe in the first task; the fallback above.
- [An excerpt spans two records, or the user's message was edited by the terminal] → the agent quotes a shorter run of words; the refusal says so.
- [Agents learn to quote tool output that says little, to pass the check] → the grade is honest about what was checked, not about whether the signal is good; that is curation's judgment, and the excerpt is in front of it.
- [The user's words enter a repository] → the excerpt always did, by design; it is the evidence. The state repository is not the design repository, and the agent chooses an excerpt without names or client detail it does not need, as the daily pass's reader does.
- [Prefixes change what agents see] → one sentence in each brief; the prefix also tells an agent plainly who is speaking, which the briefs' "never prompt an agent the user is talking to" rule already cares about.
- [Two homes for signals] → one lookup function, state first. The user has an open question on whether meeting signals should follow.

## Migration Plan

Pull on every host and restart the standing agents for the new briefs. An agent on an old brief that runs `crew signal` without an excerpt is refused with a message that says what to add. Nothing is migrated: signals already written stay where they are. Rollback is reverting the commit; signals written to the state stay readable there by hand.
