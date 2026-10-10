# Design

## Context

See proposal.md for why. The rule is `briefs.7` (`docs/architecture/briefs.md`): test, check and proof results reach the user as one bullet per suite or proof before any prose, ✅ passed, ❌ failed with the count and a one-line cause, ⏳ not yet run. `_open.md` lists it as accepted, not built.

What is built today:

- A brief is `plugin/roles/<role>.md`, its `{{TOKENS}}` filled by `brief()` in `plugin/lib/crew.py` from `team_tokens()` (conductor, ops, construct, coder, verify) or `main_tokens()` (design, planner, main-ops, dispatcher, operator). Text the same in several briefs is built once there and filled in each: `SENDERS` (who speaks in a pane), `signal_how()` behind `{{SIGNAL}}`, `cards_how()` behind `{{CARDS}}`. That is the pattern this change follows.
- None of the six briefs says how to report results. The conductor tells the user "in plain English" what a verify reported; ops writes each proof result to `/tmp/ops-proof-<bolt>.md`; main-ops and the coder end with "a short message in plain English"; verify ends its reply with the report's path; construct runs `openspec validate` and ends with a short message.
- `/opsx:verify` writes its own report (a scorecard over Completeness, Correctness and Coherence, with CRITICAL, WARNING and SUGGESTION issues), and the verify brief saves it unchanged.
- `tests/t-briefs.sh` pins each brief rule by a phrase (`tests.6`).

Rules this relies on: `briefs.7` (the rule built), `briefs.8` (plain English), `tests.6` (a brief rule is pinned by a phrase), `code.1` (standard library only), `read.2` (a count is read from the tool, never made up), `docs.5`. Pages whose area the change touches: `briefs.md`, `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/t-briefs.sh`), `docs.md`.

## Goals / Non-Goals

**Goals:**
- The six roles that report results all carry one section, word for word the same, saying how.
- The section is the first thing in any report of results, in the agent's reply, a file it writes them to, or a message to another agent that passes them on.

**Non-Goals:**
- The format of `/opsx:verify`'s own report. The verify brief keeps saving it unchanged; the list goes in verify's reply, before the path.
- The design agent, planner, dispatcher and operator agent. They report no results of their own; the intent names six roles.
- Any check by crew that refuses a reply without the list. crew does not read agents' replies, and `roles.3` asks for a check only once a stated rule has been broken.
- What `tests/run`, `wt merge` or `bolt-status.sh` print.

## Decisions

### One section, built once in crew and filled in six briefs

`crew.py` gains a module constant, `RESULTS`, beside `SENDERS`: the whole section, its heading included, and both `team_tokens()` and `main_tokens()` set `"RESULTS": RESULTS`. Each of the six briefs carries `{{RESULTS}}` on a line of its own. Because the heading is in the token, the six briefs cannot drift apart, and a seventh role gains it by one line.

*Alternative:* the same paragraph written into each brief. Six copies drift, which is why `SENDERS`, `{{SIGNAL}}` and `{{CARDS}}` exist.

*Alternative:* a heading in each brief with only the body in the token. It works, but six headings can still be worded six ways; the intent asks for one shared section.

### What the section says

The coder writes it in the briefs' own voice; this is its content, which `tests/t-briefs.sh` pins by phrase:

```
## Test, check and proof results

Whenever you report how tests, checks or proofs went (a suite you ran, a merge's checks, the bolt's verification,
an `openspec validate`, a verify's checks, each item of a Proof in dev list), list them first, before any prose,
one bullet per suite, check or proof:

- ✅ <what ran>: passed, with its counts where the tool gave them (`46 passed`)
- ❌ <what ran>: failed, with how many failed and one line on why (`2 of 46 failed: t-briefs lacks "open nothing"`)
- ⏳ <what ran>: not yet run, or still running, and what it waits on

Never say a result only in a sentence ("they all passed"), and never fold several suites into one bullet. Take every
count from what the tool printed; where it printed none, give none. What you would do about a failure, and anything
else you have to say, comes after the list. Use the same list wherever the results go: your reply, a file you write
them to, or a message to another agent that will pass them on. When you pass on results another agent reported,
show its list as it is, first.
```

Choices inside it:

- **Three glyphs, no fourth.** A check skipped on purpose, or one this role never runs (a coder doesn't run the merge's gate itself), is ⏳ with what it waits on. A check that is red on purpose, as a kit's CLAUDE.md may list, is still ❌, its line saying it is red on purpose.
- **Verify's checks** are the dimensions of its scorecard: a dimension with a CRITICAL issue is ❌ with the count, one with only warnings or suggestions is ✅ with those counts, and a skipped one is ⏳ with the reason the report gives.
- **A file counts.** Ops writes proof results to `/tmp/ops-proof-<bolt>.md`; the same list opens it, so the conductor and the user read one shape.
- **A message to another agent counts.** The conductor passes on what ops and verify report; when their list arrives as a list, it reaches the user unchanged.

### Where each brief carries it

- `conductor.md`: its own section, before *Talking to the user*.
- `ops.md`, `main-ops.md`: before *Talking to the user*, after "End each piece of work with a short message".
- `coder.md`, `construct.md`: before *Talking to the user*.
- `verify.md`: after "You change nothing", before the paragraph that saves the report, so its reply opens with the list and still ends with the path.

No other line of the six briefs changes: the section governs every place they report results, and the plain-English lines that follow a list stay true.

### The rule's record

`briefs.7` already says the rule. Its *Details* line loses "Not built: `_open.md`." and gains `crew.py` `RESULTS` and `tests/t-briefs.sh` as sources; its line in `_open.md`'s *Accepted, not built* goes. The rule's sentence is unchanged: "still running" and "counts where known" sit inside what it rules in, so no new rule id is needed (`docs.5`).

## Risks / Trade-offs

- [An agent follows a brief only as well as it reads it] → the section is the same in every brief, sits beside where each agent ends its work, and `t-briefs.sh` pins it.
- [Every brief grows by a section] → about a hundred words, once per role.
- [A herdr pane or a Pending You card may show the glyphs poorly] → they are plain Unicode emoji, which both already show in agents' messages; if one didn't, the word after each glyph still says passed, failed or not yet run.

## Migration Plan

Land, then pull on every host. Each of the six roles takes the section at its next fresh start; stage agents are fresh for every stage, so units take it at once. Rollback: revert.

## Proof in dev

None: crew has no dev environment, and the bolt's proof is its verification.

## Proof on real work

Once the bolt has landed, every host has pulled and the agents have started fresh:

1. The next coder's summary opens with one bullet per suite it ran, each with ✅ or ❌ and the counts `tests/run` printed.
2. The next time ops reports a bolt's verification, its message opens with a glyph bullet for that run before any prose.
3. The next verify a conductor relays reaches the user with verify's checks as the list, first.

## Task notes

### 1.1

`RESULTS` sits beside `SENDERS` with a one-line comment in the same voice ("How an agent reports results, the same in every brief that reports them."). Add `"RESULTS": RESULTS` to both token dicts. The text is the section above, heading included, ending without a trailing newline so the brief's own blank lines frame it.

### 1.2

Place `{{RESULTS}}` where *Where each brief carries it* says, with a blank line on each side. `t-briefs.sh`'s first block already fails any token left unfilled.

### 1.3

In `tests/t-briefs.sh`, one new block: for `swb-1` conductor, ops, construct, coder and verify, and `wldn` main-ops, `has` the heading `## Test, check and proof results`, each of the three glyph lines' opening (`- ✅`, `- ❌`, `- ⏳`), "before any prose" and "Never say a result only in a sentence". Then cut the section out of each brief (from its heading to the next `## ` or the end) and fail unless all six cuts are identical and each brief holds the heading exactly once. End with `ok "the six roles that report results carry one glyph-list section, the same in each"`.

### 1.4

`docs/architecture/briefs.md` *Details* for `briefs.7`: "Rules out: "they all passed" in a sentence. Source: signal `…`; unit `test-results-are-a-glyph-list`; `crew.py` `RESULTS`; `tests/t-briefs.sh`." Remove the `briefs.7` bullet from `_open.md`.
