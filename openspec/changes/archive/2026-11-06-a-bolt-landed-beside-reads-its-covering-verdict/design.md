# Design: a bolt whose last landing went beside the queue reads the verdict that covers it

## Context

The proposal gives the box's case. Rules this change relies on: `tests.5`, which makes a bolt's verification sluice's verdict on its last landing, read by crew from the landing commit; `read.1`, which says what crew can't read is said and never guessed; `read.2`, which has crew read another tool's output only by facts checked against the tool as it is now; `code.7`, which makes a decision a function of facts; `plan.12`, which keeps a refresh to one read of what moved; and `plan.16`, whose landings card is raised once a bolt reads proven. The change touches the areas of `plan.md` (`plugin/lib/gather.py`, `plugin/lib/kit.py`, `plugin/lib/plan.py`), `tests.md` (`tests/`) and `docs.md` (`README.md`, `openspec/`).

It departs from one sentence of `tests.5`'s details, which says `kit.verification` reads a bolt's verification green only from the `Sluice-Result` trailer starting `passed`. For a landing beside, the verdict on the landing is the one that covers it (sluice core.39), and crew reads it from sluice's record of the submission the landing commit names, not from the trailer. The rule itself holds: the verification is still sluice's verdict on the bolt's last landing, found from the landing commit. The details are the design agent's to amend (`docs.7`). The change also amends crew-board's requirement that a gather runs no `sluice status`, by its delta.

What crew reads of sluice was read at the tags, in agentplot/sluice:

- **The landing commit.** `crates/sluice-core/src/text.rs`. `landing_message` writes `Sluice-Tested` on every landing through the queue, in every release since v0.1.0. `beside_message` never writes it. At v0.68.1 a landing beside's `Sluice-Result` is `landed beside the queue (no required check reads its changes)`. At v0.69.0 it is `passed (0 run, 0 replayed) beside the queue: no required check reads its changes; covered by the result at <revision>, <words>`.
- **The record.** `crates/sluice-core/src/records.rs`, `Submission`. At v0.69.0 a submission landed beside carries `beside: true` and `covered_by`, `{at, result, ran, replayed}` (`crates/sluice-seams/src/lib.rs`, `CoveringVerdict`). `at` is the branch's revision that the covering verdict landed as. `covered_by` is `None` in records written before it. `sluice status <n> --json` prints the record (`crates/sluice/src/lib.rs`, `Command::Status`).
- **The overview.** `crates/sluice-core/src/overview.rs`, `BranchView`. It lists the submissions still in a chain, so not a landed one. Its `recent` lines are the log's `landed` events, `{ids, to, beside}` (`step.rs`, `Event::Landed`), which name no covering verdict. So the overview can't give it.
- **The spec.** `openspec/specs/landing-beside/spec.md` at v0.69.0. Where the branch's state says its revision is covered but names no result, as a sluice before 0.69.0 wrote it, the next submission takes the queue rather than land beside. sluice does not infer a covering verdict from history.

The box runs sluice 0.68.1, the fleet's pin on swancloud's main on 2026-11-06. Its record of #1319, read there that day, has `beside: true` and no `covered_by` (`tests/py/sluice-0.68.1/`).

## Decisions

### Decision 1: a head landed beside is told by its trailers, and its verdict read from sluice's record

`gather.landing_read` reads a bolt head's `Sluice-Result`, `Sluice-Submission` and `Sluice-Tested` in one `git log`. A head with a result, a submission and no `Sluice-Tested` is a landing beside the queue. For it, the gather runs `sluice status <n> --json` in the kit's main checkout and keeps the record's `id`, `branch`, `state`, `landed_as`, `beside` and `covered_by`, or why it could not read it: sluice's own words, a timeout or no JSON (`read.1`). Every other head runs nothing beyond the `git log`, which already ran.

`kit.covering`, a pure decision (`code.7`), reads the record:

- the submission landed as the head, beside, with a covering verdict that passed: **green**, naming that verdict's own run and replay counts and the revision it landed as;
- the record landed as the head through the queue (`beside` not true): the head's own trailer, as any landing's;
- the record unread, not landed, or landed as another commit: **unknown**, saying which;
- no covering verdict: **unknown**, saying sluice records none before 0.69.0 and that the bolt reads proven once a landing on it carries a verdict of its own or names the one that covers it;
- a covering verdict that did not pass, or one crew can't read (an `at` that is no revision, a result that is no word, a count that is no count): **unknown**, naming it (`read.2`).

The trailer's words are never the verdict. 0.69.0's trailer opens `passed`, but its counts are the landing's own, nothing run. Reading its covering words would take a commit message's text for sluice's record (sluice core.11 and core.14: what the core decides is held in its records, readable from every host).

Considered: reading the covering verdict from the overview, which the follower already watches. The overview carries none (Context). Also considered: walking the head's first parents to the nearest landing that carries `Sluice-Tested`, which needs no sluice and would prove the box's `b01e966` today. sluice itself declines that inference (its landing-beside spec, "State that names no covering result"), since a gate changed by a landing, or a branch moved by another hand, leaves no verdict covering the revision. crew guessing where sluice won't would break `read.1`. Also considered: reading the covering verdict's revision from the trailer and checking that commit's own `Sluice-Result`, again with no sluice process. That still takes the link from a landing beside to its verdict from its commit message's words, where sluice holds it in its records (sluice core.11 and core.14), and it would not prove the box's case either, since 0.68.1's trailer names no revision.

### Decision 2: every read of a bolt's verification passes the record

`kit.verification(head, result, beside=None)` reads as before when `beside` is None, so facts from before this change, and every head landed through the queue, read the same. Each caller passes the bolt's `beside` from the gather: `Stages.bolt_state`, `proven_facts` (its tuple gains `beside`, read by `give_refusal`), `landing_unready` (from `land_facts`, which the landings card's rows and a reading take), `bolts_data` (`crew bolts`) and the rail's landing rows. So a landing beside covered by a passed verdict reads proven everywhere a bolt's proof is read, and the bolt reaches its kit's landings card.

### Decision 3: the cost is one `sluice status` per gather of a bolt whose head is a landing beside

crew-board's requirement says a gather runs no `sluice status`. This change has a gather run one for each bolt whose head is a landing beside. That head stays only until the bolt's next landing, and a proven bolt soon lands. The follower gathers only once something has moved (`plan.12`), so an idle host still runs nothing. The record of a landed submission does not change, so a cache kept by the follower could save the call. That would be a derived cache to key and expire for a rare head, so it is left out.

### What the box gets, and what a sluice before 0.69.0 does

With this change, crew on the box reads `b01e966`'s verification as unknown, now saying that sluice's record of #1319 names no covering verdict, as sluice records none before 0.69.0. It reads proven once a landing on the bolt carries a verdict of its own. Under 0.68.1, that is any submission a required check reads. Under 0.69.0, it is the bolt's next submission, which takes the queue because the branch's state names no covering result. After that, each later landing beside names its covering verdict, and crew reads it. Proving the box's bolts with take-main fixes that change only docs needs sluice 0.69.0 on the box, which is swancloud's pin to move.

## After deploy

None. Every case is held by the logic and contract tiers on recorded and derived sluice records, and what the box runs is swancloud's pin, not a step of this change.

## Task notes

**1.1** `plugin/lib/gather.py`: `LANDING_TRAILERS`, `BESIDE_FIELDS` and `landing_read(main, ref)`, called from `kit` for each bolt with a ref, giving `verdict` and `beside`; the module docstring. Contract: `tests/contract/test_gather.py`, `test_a_head_landed_beside_the_queue_is_read_with_sluices_record_of_its_submission`, a stub sluice on the path logging its calls: a head landed through the queue asks nothing; a head landed beside asks `status 1319 --json` once and keeps the record; sluice 0.68.1's record keeps no covering verdict; a refusal is said in sluice's words.

**1.2** `plugin/lib/kit.py`: `verification(head, result, beside=None)` and `covering(head, beside)`. Logic: `tests/py/test_kit.py`, `TestLandedBeside`, on `tests/py/sluice-0.69.0/status-landed-beside.json` and `tests/py/sluice-0.68.1/status-landed-beside.json` through `facts.landed_beside`.

**1.3** `plugin/lib/plan.py`: the callers of Decision 2. Logic: `tests/py/test_rail.py` (a landing beside's row can land on `land/<kit>`; sluice 0.68.1's says why it does not; `crew bolts` shows the covering verdict), `tests/py/test_landing.py` (`landing_unready`, `bolt_state`, `proven_facts`, `give_refusal`), `tests/py/test_bolt_commands.py` (`give_refusal`), and `tests/py/test_chores.py` for the tuple's new member.

**2.1** README's `crew rail` paragraph and the crew skill's verification sentence.
