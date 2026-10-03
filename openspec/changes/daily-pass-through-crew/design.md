# Design

## Context

See proposal.md for why. What exists:

- **The daily pass**, in `WilldanGroup/willdan-blueprints` (read `signals/README.md` and `.claude/skills/signal-capture/SKILL.md` there before building). `signals/bin/sweep` runs at 06:47 from launchd on a Mac and makes two headless Claude runs, because the meeting recorder (Wispr Flow) is reachable only through its MCP server. The **sweep** phase finds recorded meetings with no capture, writes `signals/<date>-<slug>/capture.md` with `status: unread` for each, and banks the transcript in `signals/.raw/<capture>.txt`, which git ignores. The **read** phase reads each unread capture's transcript and writes `NN-<slug>.md` signal files, then sets the capture's `status: read` and its `signals` count. Each phase commits what it wrote in the checkout it runs in. The README treats those commits as the job's heartbeat: "a day with no `signals(sweep)` or `signals(read)` commit is a day the job broke".
- **The shapes.** `capture.md` has frontmatter (`capture`, `source`, `event_date`, `imported`, `status`, `signals`, and source-specific fields such as `wispr:` or `also:`). A signal file has frontmatter (`signal: <capture>/<NN-slug>`, `kind` of `constraint|ask|question|commitment|reaction`, `who`, optional `subject` and `claims`), one or two sentences of assertion, and the excerpt as a blockquote with its position.
- **crew's path.** `plan.py`'s `land(repo, ref, path, make)` writes named paths to a branch through crew's bare cache: fetch over https, commit through a temporary index, push without force, apply again on a refused push. Before `checked-capture`, `crew signal` used it to write an agent's capture to the blueprints' main; that is the path this change reuses.
- **Where signals live.** An agent's on the flywheel's branch of the state repository; a meeting's in the first blueprints repo's `signals/`. crew looks an id up in the state first.
- **The run record.** `capture` is the act of recording a signal.

## Goals / Non-Goals

**Goals:**
- Every signal, whoever wrote it, reaches git by one path and leaves an entry.
- The daily pass keeps its two phases, its skill and its `.raw/` cache; it changes only how its output reaches main.
- What lands is in the shape curation depends on, or is refused with the file named.

**Non-Goals:**
- Reading meetings in crew. The sweep and the read stay the blueprints repo's skill.
- Moving meeting signals to the state repository. That is the user's open question; this design keeps the write target in one place so that the answer changes one line.
- Backfilling entries for the captures already on main. `crew signal show` gives their provenance; their traces begin at their first move.
- Checking excerpts against transcripts. The reader has the transcript; crew has only the files.

## Decisions

### `crew signal land <capture-dir>`

A `plan.py` command, run on the host that has the directory. `--label` or `CREW_LABEL` names the partition; the target is `signals/<capture>/` on main of its first blueprints repo, where `<capture>` is the directory's name.

Checks, before any write, each failure naming the file:

1. `capture.md` exists; its frontmatter's `capture` equals the directory's name; `source` and `event_date` are present; `status` is `unread` or `read`.
2. Every other file is named `NN-<slug>.md`. Anything else (a `.txt`, a `.jsonl`, a subdirectory) is refused: raw material does not enter git.
3. Each signal file's `signal` is `<capture>/<file stem>`; `kind` is one of the five; `who` is present; the body has at least one line of assertion; and, when the capture is `read`, a blockquote. A signal file larger than 8 KiB is refused as copying its source.
4. A `read` capture's `signals` equals the number of signal files.
5. The capture's name is not that of a capture on the flywheel's state branch.

Then one `land` on the blueprints repo's main with a `make` that, at each tip:

- for each signal file: absent on main, it is added; present and byte-identical, it is skipped; present and different, the landing is refused (signals are immutable);
- for `capture.md`: absent, it is added; identical, skipped; different, it is replaced only if main's says `unread` and the difference is confined to `status`, `signals` and `imported`, else refused;
- with nothing to add or replace, no commit is made and the command prints "already landed".

The commit's subject is `signals(<capture>): land <n> signals (<who>)`, or `land the capture, unread`. Entries: `capture` with `On: capture/<capture>` when `capture.md` is first added, and one `capture` with `On: signals/<id>` per signal added, all with the commit. `By` is `CREW_AGENT` when set, else `<user>@<host>`; the sweep script exports `CREW_AGENT=signal-sweep` so its entries say what wrote them.

The partition's role table does not gate this command: it is run by the job, as the user.

*Alternative:* have crew observe new captures on main and write entries after the fact, leaving the pass's commits alone. Rejected: it gives the entries and none of the checks, and leaves a second write path into a shared record.

### The daily pass, outside crew

In each blueprints repo that runs one:

- `.gitignore` gains `signals/.work/`, beside `signals/.raw/`.
- The skill writes a capture's files under `signals/.work/<capture>/`, not `signals/<capture>/`. The `.raw/` cache is unchanged. Its step that lists what is already captured reads `signals/*/capture.md` in the checkout, so the script pulls first.
- `signals/bin/sweep` becomes: `git pull --ff-only`; the sweep phase; `crew signal land signals/.work/<capture>` for each stub it wrote; the read phase; `crew signal land` again for each capture it read; `git pull --ff-only`; remove the landed directories from `.work/`. It makes no commit of its own. A landing that is refused is logged with crew's message and leaves the directory in `.work/` for a person to look at; the pass carries on with the next capture.
- The README's "the commit is the notification" still holds: the commits are now crew's `signals(<capture>): land …`, one or two per capture, and a day with none is a day the job broke.
- The job's environment has `crew` on its `PATH` and `CREW_LABEL=<label>`.

A read that restates an earlier capture's material still cites the earlier signal in its body, as the skill says; crew does not check citations.

### What must not break

- Signals and captures already on main are untouched and still read.
- An agent's `crew signal` is unchanged.
- The daily pass's two phases, its skill's reading rules and its `.raw/` cache are unchanged.

## Risks / Trade-offs

- [The job's Mac lacks crew or the label] → an outside task with its own check; until it is done the pass fails loudly at the first landing and writes nothing to main.
- [A landing is refused every morning for the same malformed file] → the directory stays in `.work/`, the log names the file, and the rest of the pass proceeds.
- [The checkout and main diverge because someone commits `signals/` by hand] → `--ff-only` fails loudly; the README says signals are landed, not committed.
- [The user moves meeting signals to the state repository later] → the target is one function; the checks, the immutability rule and the entries are the same.

## Migration Plan

1. Land the crew change; `crew signal land` exists and nothing calls it.
2. In willdan-blueprints, as one reviewed commit: the `.gitignore` line, the skill's paths, the script, the README. Run the pass once by hand and check the result before the next morning's run.

Rollback: revert the blueprints commit; the pass commits in its checkout again. crew's command can stay.

## Open Questions

- Which Mac runs the daily pass, and so where `crew` and `CREW_LABEL` must be set for the job. It does not change the design; the rollout names it.
