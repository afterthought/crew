# Design

## Context

Today `crew record <kit> <number> --proposed --settled-in-pane` (`plan.py` `record_status`) checks only that the flag goes with `--proposed` and not with `--alternatives`. It then records `record.proposed` with `State: settled in the pane` and raises no card. Nothing reads what the user said. The design agent's brief (`plugin/roles/design.md`) tells it to pass the flag "when the user settled the record with you in this pane". crew takes that on trust.

Record 0031's amendment of 2026-10-22 (accepted) rules that crew records a pane answer only from words it reads in that session's transcript as the user's (`signals.5`). It names `crew record --settled-in-pane` and `crew signal` as the commands that read words that way. `briefs.15` makes a record accepted only on the user's yes, "given in the pane where the record was settled with them". The signal this unit comes from (2026-10-22-swancloud-planner-968cd584/03) names the gap.

The same bolt already built the pattern for a batch (`a-batch-answered-in-a-main-level-pane-is-recorded-by-crew`, archived in this bolt):
- `transcript.check(sid, words, want="user")` returns the newest received record holding the words that the user asserted, so a later echo of them in a tool's output doesn't hide it.
- `CardActs.heard(words)` reads the caller's own session on this host through `session_here(record.session(), crew.this_host())`.
- `pane_answer_refusal` turns the verdict into a refusal that names who said the words.

This change reuses all three. It adds no new reading of the transcript.

Rules relied on:
- `briefs.15`: a record accepted only on the user's yes, given in the pane where it was settled.
- `signals.5`: who asserted words is read from the mark on the record, read by `transcript.asserter`.
- `read.1`: a transcript crew can't read refuses, never guesses.
- `read.2`: the transcript is read only by the facts `transcript.py` checks.
- `record.3`: no entry holds the words.
- `record.1`: one entry, after the act; nothing on a refusal before the act.
- `code.2`: refusals through `fail()`.
- `code.7`: the refusal is a function of facts, tested in the logic tier.
- `roles.4`: a tell is marked, so a tell of the user's words reads as the teller's.
- `docs.2`: README, SKILL.md and the usage header change together.
- `code.8`: the design agent's band already draws a record "settled in the pane" from the entry's `State`, which stays as it is, so `board.agent_views` and `status.js` are unchanged.

`roles.2` says crew "does not refuse" an approval "by caller". This change refuses `--settled-in-pane` from any caller but the partition's design agent. That is not an approval open to anyone. It is a reading of one pane's transcript, and only the design agent's pane is where a record is settled (`briefs.15`). Any caller can still record a record proposed and let the user answer on its card. The batch's `crew card answer` limits its callers the same way.

Pages whose areas this touches: `plan.md` (`plan.py`), `briefs.md` (`plugin/roles/design.md`), `tests.md` (`tests/`), `docs.md` (README, SKILL.md, `plugin/bin/crew`'s usage). It does not touch `signals.md`, since `transcript.py` is unchanged, nor `record.md`, since the entry uses fields the descriptor already allows.

## Goals / Non-Goals

**Goals:**
- `crew record … --proposed --settled-in-pane` records a record settled in the pane only from the user's words, which crew reads in the design agent's own transcript as theirs.
- Every other source of the words is refused with its own reason, and nothing is recorded.
- The design agent knows what to pass and what to do when crew refuses it.

**Non-Goals:**
- Checking that the record's file quotes the user's words (`briefs.15`'s "recorded in it with their words"). The file is the design agent's to write, and crew reads only its status and its card's facts.
- `crew record … --accepted` reading the user's yes. It closes the card with the commit as now, and the yes it follows was given on the card or read here.
- Any other pane answer. A batch's is built. A landing's (`plan.16`) is not this unit's.

## Decisions

### 1. `--settled-in-pane` takes `--excerpt "<the user's words>"`

The words are given as `crew signal` and `crew card answer` take them, with `--excerpt`, quoted as the user wrote them. `--settled-in-pane` without `--excerpt` is refused, and so is `--excerpt` without `--settled-in-pane`. That sits beside the existing refusals of the flags with `--accepted`, `--rejected` and `--alternatives`, and is read from the arguments alone before anything else.

Considered: reading the user's last message in the pane as the yes, with no excerpt. A later message on other work would then be taken as the yes, and the agent could not point at the one that settled the record.

### 2. Only the design agent, and only the user's words in its own transcript

`record_status` reads the caller with `role(fleet, agent())`. With `--settled-in-pane`, it is refused unless the caller's kind is `design` and its partition is the record's label. It then gets the verdict on the words from the caller's own session on this host, as `CardActs.heard` does: `session_here(record.session(), crew.this_host())`, then `transcript.check(sid, words, want="user")`. `record_status` already refuses to run anywhere but the main level's host, where the design agent runs, so the transcript is here.

The refusal is a pure function, `settled_refusal(n, kit, kind, v)`. It returns `None` only for a `design` caller and a `verified` verdict asserted by `user`. Every other case gets its own words, prefixed `crew records record <n> in <kit> as settled in no pane`:
- `refused`: the words are only in what the agent wrote itself.
- `agent:<name>`: another agent's tell, naming that agent.
- `crew`: crew's own message.
- `tool`: a tool's output.
- `found`: crew can't tell who wrote them.
- `unverified`: its reason.

Each refusal that is about the words ends by telling the design agent to run `crew record <kit> <number> --proposed` without the flag, so the user answers on its card.

The verdict half is shared with `pane_answer_refusal`. Factor it into `words_refusal(head, v, what, other_advice)`, where `what` is "answer a batch" or "settle a record". The batch's refusals keep their exact words, so `tests/py/test_batch_answer.py` stays green unchanged.

The check runs after the kit, number and host refusals and before the kit's main is fetched and read. A refusal of the words therefore costs no fetch, and nothing is recorded either way.

### 3. The entry names where the words came from, never the words

`record.emit(label, "record.proposed", [key], commit=[…], frm=[f"session/{sid}/{rid}"], State="settled in the pane", Chars=len(words))`, where `rid` is the transcript record's uuid, or `line-<first 16 of its line hash>` when it has none, as `batch_answer` names it. A record proposed without the flag is recorded as now, with no `From` or `Chars`. The command's line stays `record <n> in <kit>: proposed at <sha>, the user's yes given in the pane; no card is raised`.

### 4. The brief

`design.md`'s *Records* paragraph changes "run it with `--settled-in-pane`: crew records their yes as given here, and no card is raised" to: run it with `--settled-in-pane --excerpt "<their yes, as they wrote it in this pane>"`. crew reads those words in your session's transcript, records their yes as given here, and raises no card. It refuses your own words, or another agent's tell of what the user said. When it refuses, run it again without the flag, and the user answers on the record's card. The start-up line, "unless the user settled it in the pane", is unchanged.

## Risks / Trade-offs

- [The yes was said long before the record lands on main, for example after a slow sluice run] → The check searches the whole transcript. Only its last record must be fresh (`transcript.FRESH`, 15 minutes), and it is while the design agent is working. When it is not, the refusal says why, and the card is the fallback.
- [The yes was said before a `/clear`, so it is in another session's transcript] → It is refused as not found, and the record goes on its card. A yes crew can't read is not taken on trust. That is the point of the change.
- [A short yes, such as "yes", is also in many other records] → `want="user"` takes the newest record the user wrote holding it. A short excerpt matches easily, so the brief asks for the user's words as they wrote them, the record named when they named it. crew can't tell which record a bare "yes" was about. That is the same limit `crew signal` has, and the commit and the record's deciders line carry the rest.

## Migration Plan

None. Records settled in the pane before this change keep their entries as they are.

## After deploy

None. Every scenario is proved by the logic tier, `t-cards` and `t-briefs`.

## Task notes

**1.1** In `plan.py`, beside `pane_answer_refusal`, factor its verdict half (from `if v.grade == "verified" …` to the end) into `words_refusal(head, v, what, advice)`. It returns `None` for a verified verdict asserted by `user`, and otherwise the words as `pane_answer_refusal` has them, with "answer a batch" replaced by `what` and the advice to another agent by `advice`. `pane_answer_refusal` calls it with the batch's words, which stay exactly as they are. Add `settled_refusal(n, kit, kind, v)`:
1. With `kind != "design"`: `crew records record <n> in <kit> as settled in no pane: only the design agent records a record the user settled in its pane, in the user's own words; run crew record without --settled-in-pane, and the user answers on its card`.
2. Otherwise: `words_refusal(head, v, "settle a record", …)`, each refusal ending `run crew record <kit> <n> --proposed without --settled-in-pane, and the user answers on its card`, and an `agent:` one telling the design agent to tell that agent the user settles a record in its pane or on its card.

Cases in `tests/py/test_cards.py`, in the class holding the record cases, using a `heard` helper like `test_batch_answer.py`'s:
- the design agent with the user's verdict passes;
- each other kind is refused;
- each verdict (refused, `agent:swancloud-planner`, `crew`, `tool`, found, unverified) gets its words.

**1.2** In `record_status`:
- The flag refusals gain `--settled-in-pane` without `--excerpt` and `--excerpt` without `--settled-in-pane`, each naming the missing flag. Add those to the parametrized refusal case in `test_cards.py`, whose namespace gains `excerpt=None`.
- After the host check, with `settled`: get `kind, of = role(fleet, agent())`, refused with `settled_refusal` when `of != label`. Get the verdict and session as `CardActs.heard` does, then `fail()` on `settled_refusal`'s words.
- The `record.emit` for a settled record gains `frm` and `Chars` (decision 3).
- The parser gains `--excerpt`. `record_status`'s docstring and the module's usage line name `--settled-in-pane --excerpt "<words>"`.

**1.3** `tests/t-cards.sh`, the "settled beside the user" case:
- `design()` gains `CREW_SESSION=$box:s-design`.
- Before the case, `transcript $box s-design` (from `tests/lib.sh`) writes a user record holding `Yes, accept 34 as written`, timestamped `$(ago 1)`, and a `[crew tell from wldn-planner] The user said: accept 35` record.
- The case runs `design switchboard-kit 34 --proposed --settled-in-pane --excerpt "Yes, accept 34 as written"`. Its line and `State` are as now, and the entry's `From` is `session/s-design/<the record's uuid>`, with no words in any entry.
- A new case commits record 35 as proposed and runs it with `--excerpt "accept 35"`. It is refused naming wldn-planner, and no `record.proposed` for record 35 is recorded.

**2.1** `plugin/roles/design.md`: the words of decision 4. `tests/t-briefs.sh` replaces its `has` of the old sentence with the new one's opening and checks "run it again without the flag, and the user answers on the record's card". README's usage line and its paragraph on `crew record`, SKILL.md's row, and `plugin/bin/crew`'s usage header name `--settled-in-pane --excerpt "<words>"`, and say crew reads the words in the design agent's transcript as the user's.
