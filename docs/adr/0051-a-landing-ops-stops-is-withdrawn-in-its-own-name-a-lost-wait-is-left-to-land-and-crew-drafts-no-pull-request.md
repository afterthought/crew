---
status: proposed
date: 2026-10-30
deciders: swancloud-design, on madswan-design's ruling of sluice's side the same day; the user on their card
---

# 0051. A landing ops stops is withdrawn in its own name, a lost wait is left to land, and crew drafts no pull request

Status: proposed to the user on 2026-10-30, as `briefs.15` has it; accepted only on their yes.

## Context and problem statement

A bolt's landing is a pull request sluice opens from `bolt/<bolt>` into main, which sluice takes into main's queue while it is ready for review. Since 2026-10-23 (`a-landings-pull-request-is-live-only-on-the-users-word`) crew has held that pull request by marking it a draft whenever `crew bolt submit` ends with the bolt not on main, when a fix starts on the bolt and before any merge into it, and readied it at the next submit, so that a merge into the bolt could not re-enter the queue without the user's word. crew marks it with the user's GitHub token.

In wldn on 2026-10-30 (alpha's run record 01:43 to 01:48Z; PR 96's timeline) `crew bolt submit` waited three times on #1004 while sluice reported the host could not run the checks, stopped, and drafted PR 96 at 01:48:11Z, recorded as the user's own act; sluice 0.58.0's intake withdrew #1004 on the draft at 01:48:13Z, and ops resubmitted by hand (#1008, #1009). madswan-design's ruling the same day, on sluice's side: a request's draft is the person's withdrawal of their offer, ready after draft is a new submit with a new number (sluice clauses 5, 120, 127, C.5), sluice holds no entry short of landing since a held head would hold every entry behind it (8), and sluice itself marks a withdrawn request as such and readies nothing until the next submit. So crew's draft is not a hold: it is a withdrawal in the user's name, and under 0.60.0 it reads as exactly that.

## Considered options

1. Keep crew's draft as the hold, readied at the next submit.
2. A landing crew means to stop is withdrawn by main-level ops in its own name with `sluice withdraw`; a landing crew does not mean to stop is left to land and read later; crew drafts and readies no pull request. Chosen.
3. Close the pull request and open another at the next submit.

## Decision outcome

Option 2, as madswan-design ruled it and as sluice's own words have it: the hand and the act change, nothing is built in sluice.

- **A landing ops means to stop is withdrawn in ops's own name.** Refused as conflicting with main, so the take-main fix starts (`plan.8`); failed on main's checks, so a fix round starts; or held for a fix starting on the bolt: ops withdraws it with `sluice withdraw`, in its own name, which sluice records and marks on the request (clause 120), and which no merge into the bolt undoes, since sluice readies nothing until the next submit.
- **A landing ops does not mean to stop is left to land.** crew's wait ran out, or sluice said the host could not run the checks: the entry stays in the queue, where sluice tests the combination again, and its outcome is read at the next read, the conductor's or ops's start included (record 0046; sluice record 0068). A wait that ended is no reason to hold what the user already sent (the user, 2026-10-24: an approval stands through taking main in; record 0031 as amended that day).
- **crew drafts and readies no pull request, with any token.** The user's token records the user as the actor, which sluice reads as their own withdrawal; the one hand on a landing's request is ops's, through sluice.
- **The next `crew bolt submit` on the standing word re-enters the head as a new entry**, by sluice's design (clause 120); the landing card's approval stands through it, asked again only when the head moved (record 0031 as amended 2026-10-24).
- **Until the unit lands**, crew drafts as it does today: after a `crew bolt submit` that stopped, ops resubmits on the standing word, as wldn did, and readies no pull request by hand.

Option 1 is ruled out by sluice's design, which reads the draft as a withdrawal and holds nothing; option 3 loses the request's thread and sluice's record of the landing.

## Consequences

- `plan.16` is amended with the three acts, marked proposed.
- The bolt-teams spec's requirement "A landing's pull request is a draft whenever the user's word does not stand" is replaced, by one crew unit on the yes, `a-landing-ops-stops-is-withdrawn-and-crew-drafts-nothing`, queued only once the user says the Flume refactor has started (their word of 2026-10-29); under move 5 the same acts are Flume's launch hold and ops's retry (record 0047, flume record 0023).
- Sources: wldn's run record (`WilldanGroup/crew-state`, `wldn/main`, `runs/chuck-herdr-alpha/2026-10-30.rec`, entries 01:40:23, 01:43:00, 01:44:18, 01:48:12Z); PR 96's timeline; madswan-design's ruling of 2026-10-30, relayed by swancloud-operator; sluice's `using-sluice` verdicts reference, ready; the archived change `2026-10-23-a-landings-pull-request-is-live-only-on-the-users-word` and its design's "Withdraw only" paragraph, written when sluice drafted nothing itself.
