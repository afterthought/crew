# Design

## Context

See proposal.md for why. Today, per `the-rail-is-answered-through-cards` and `a-card-links-a-plannotator-session` (both built, neither archived):

- `rail_rows()` in `plugin/lib/plan.py` offers a land row for a held bolt once every unit has merged and not all have landed, keyed `land/<bolt>`, waiting from the bolt's head time (`k["bolts"][b]["head_at"]`, from `gather.py`). A review row is keyed `review/<unit>/<head7>` from its place's head, which `gather.py` already reads.
- `gather.py` answers, for each bolt branch, `exists`, `changes`, `worktree` and `head_at`, but not the head's commit.
- The card hook (`plugin/hooks/cards`) knows the rail's four key forms by pattern, the landing's `^land/([a-z0-9][a-z0-9-]*)$`; a card under any other key is recorded on `agent/<agent>` with no `Key`. `CARD_KEYS` in `plan.py`, "as crew's card hook reads them", is the same four for `crew card session|wait|end`, and `card_session()` refuses any `land/` key, which has nothing to read.
- `lost_rows()` and the notices it feeds name rows, not keys (`land/<bolt>`, `review/<unit>`), so the owner finds the card among its own; `stray_cards()` matches a card to its unit or bolt by the key's prefix `(review|verify|land)/<name>`.
- The conductor's brief keys the landing card `land/<bolt>` (*Cards*) and, after a fix carries the bolt onto main, says to post the landing card again once proven (*Fixes*). The card discipline both briefs share (`cards_how()` in `crew.py`) takes every key from the rail's `card:` line.
- Pending You's `idempotencyKey` returns the card already made under that key, whatever its state: the signal's reading is the post answered `"status":"resolved","version":3` for a new landing card under the old key.

Rules this rests on: `briefs.11` as amended on main (a re-proved bolt's landing is never asked under the failed landing's key) and ADR 0005 as amended 2026-10-09; `read.1` and `read.2` (a row whose head can't be read gets no key, and an absent field never becomes text); `code.1` (`gather.py` stays standard library only); `state.4` (the rail writes nothing); `docs.2` and `docs.4` (README with the behaviour; the specs only by delta). Pages whose area it touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`crew.py`), `briefs.md` (`plugin/roles/`), `tests.md` (`tests/`), `docs.md` (`README.md`, `openspec/`). It departs from no rule.

## Goals / Non-Goals

**Goals:**

- A bolt proven again on a new head has a new landing key, so its conductor's landing card is a new card.
- The rail, the hook, `crew card` and the briefs all read the one key form.

**Non-Goals:**

- No new notice from crew when a fix moves a bolt's head. The landing card is usually already closed by then (the user approved it and the conductor acknowledged it before the landing failed); when it is still open, the conductor ran the fix itself and its brief says to close it, and the rail lists a card left under an old head with the tell that asks its owner to close it.
- `proposal/<n>` and `verify/<unit>/<stamp>` are unchanged: each is asked once.
- `docs/architecture/` is not edited here: `briefs.11` already says it on main, and the line in `_open.md` that lists it as unbuilt is on main, not on this branch (see *Migration Plan*).

## Decisions

### The key is the bolt's branch head, seven characters

`land/<bolt>/<head7>`, the first seven characters of `bolt/<bolt>`'s commit, the same width and source as a review's. The head is what the proof proved and what main-ops lands, so a new head is a new question exactly when the bolt is proven again. Alternatives: a counter of landings (state crew would have to keep, against `state.2`); the proof file's stamp (a proof run again on the same head would make a second card for one question).

### `gather.py` reads the head beside its time

Each bolt's answer gains `head`, the commit of `refs/heads/bolt/<bolt>`, or `null` when there is no branch. `gather.py` is piped from the caller's crew to each host, so the field is there whenever the caller's `rail_rows()` reads it. The land row needs the head as it needs the head's time: a bolt whose head can't be read gets no land row (`read.1`, `read.2`), as today with no `head_at`.

### Rows are named as before; only keys change

`lost_rows()`, the close notices and `stray_cards()` read a row by its prefix, `land/<bolt>`, which the new key still starts with, so none of them changes. A notice still says "Close any Pending You card you have open for … land/y", and the owner finds it among its own.

### The bare `land/<bolt>` stops being a row key

The hook's and `CARD_KEYS`'s landing pattern becomes `^land/([a-z0-9][a-z0-9-]*)/[0-9a-f]{7}$`. A card posted under a bare `land/<bolt>` after this lands is recorded on `agent/<agent>` with no key, as any key that is not a row's. A card posted under it before is still in the run record with that key; it matches no row, so the rail lists it as a card whose row is gone, with the tell to close it, and the hook still finds its key from its post when it is closed. `crew card session land/y` is now refused as not a card key; `land/y/<head>` is refused as a landing.

### The card discipline says what a changed key means

One sentence in `cards_how()`, so the planner and the conductor hold it alike: a row's key changes when what it asks changes, a unit built again or a bolt a fix moved; close the card under the old key with what changed, unless it is already closed on its answer, and post under the new key when the row asks again; never post again under a key whose card was answered, since Pending You gives that card back. The conductor's brief names the landing key `land/<bolt>/<head>` and, under *Fixes*, says a fix merged into the bolt or carrying it onto main changes the landing key.

## Risks / Trade-offs

- [A unit that refuses a card by its key (`a-teams-cards-are-its-conductors`) is built on the old pattern] → It reads the same `KEYS` in the hook; whichever merges second takes the other's pattern. Named in *Touches*.
- [The rail-cards and card-sessions specs are not yet in `openspec/specs/`] → Each `MODIFIED` delta archives only after the change that writes its spec; `openspec validate` says so now as information.
- [A landing card open under a bare `land/<bolt>` when this lands] → Listed by the rail as having no row, with the tell to its owner; closed as any card is.

## Migration Plan

Nothing to migrate: keys are derived on every read. Once the bolt lands, the line in `docs/architecture/_open.md` that lists the landing key as unbuilt (added on main in beebcc1) is removed, by the design agent or the bolt's carrying fix, whichever holds main's text.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled, with the conductors started fresh:

- The next crew bolt whose landing fails and is proven again: `crew rail` shows its land row under `land/<bolt>/<new head>` with no card open; its conductor posts the landing card, and the user sees a new card in Pending You, not the answered one; any landing card still open under the old head is closed by the conductor with what changed, or is listed by the rail as having no row until it is.

## Task notes

### 1.1

In `gather.py`'s bolt loop, add `"head": (run(["git", "rev-parse", "--verify", "-q", f"refs/heads/bolt/{b}^{{commit}}"], main) or "").strip() or None if exists else None` beside `head_at`, and say so in the module's docstring ("its head and the head's time"). Standard library only (`code.1`).

### 1.2

In `rail_rows()`, read `head = k["bolts"].get(b.name(), {}).get("head")`, offer the land row only when it is there as well as `head_at`, and key it `f"land/{b.name()}/{head[:7]}"`. Leave `lost_rows()`, `notify()` and `stray_cards()` as they are (*Rows are named as before*). In `tests/t-rail.sh`, the bolt `apex-zones` row's card line becomes `land/apex-zones/<the bolt's head, --short=7>`, read from `$kd/bolts/apex-zones`; add a block in which a landing card under `land/apex-zones/0000000` is recorded open and the rail shows the land row with no card open and lists that card after the groups with `crew tell <owner> "Close your Pending You card land/apex-zones/0000000: its row is gone."`, then a card under the current key shows open on the row. Keep the earlier stray count true: close the earlier stray card first, or count both.

### 1.3

In `plugin/hooks/cards`, the landing entry of `KEYS` becomes `^land/([a-z0-9][a-z0-9-]*)/[0-9a-f]{7}$`, still `bolt/{}`. In `plan.py`, `CARD_KEYS`'s landing pattern becomes `land/[a-z0-9][a-z0-9-]*/[0-9a-f]{7}`, and `card_of()`'s refusal names `land/<bolt>/<head>`. In `tests/t-cards.sh`, post the landing card under `land/tenant-environments/abc1234` and expect that key on `bolt/tenant-environments` in its post and its close; add a post under the bare `land/tenant-environments` recorded on `agent/swb-1-conductor` with no `Key`. In `tests/t-card-session.sh`, the landing refusal runs on `land/tenant-environments/abc1234`, and `land/tenant-environments` is refused as "is not a card key".

### 2.1

In `cards_how()`, after the sentence that takes the key from the rail's `card:` line, add what a changed key means, as *The card discipline says what a changed key means* puts it, in the discipline's plain words. In `plugin/roles/conductor.md` *Cards*, the bolt's bullet is keyed `land/<bolt>/<head>`, the bolt's head as the rail's `card:` line shows it. In *Fixes*, after the first paragraph's merge sentence, say that a fix merged into the bolt moves its head, so a landing card you have open is closed with what the fix changed and the landing card is posted again, under the key the rail then shows, once ops has proved the bolt again; in the carry paragraph, "post the landing card again" becomes "post the landing card again, under the bolt's new head". In `tests/t-briefs.sh`, the conductor's check reads "keyed \`land/<bolt>/<head>\`, marked high stakes", and the planner's and the conductor's briefs both hold the new discipline sentence (check a phrase of it in each).

### 2.2

In README's paragraph on Pending You cards, the rail's keys are `proposal/<n>`, `review/<unit>/<head>`, `verify/<unit>/<stamp>` and `land/<bolt>/<head>`, and one sentence says a review's and a landing's key carry the head of the branch they ask about, so a unit built again or a bolt proven again on a new head is a new card, and its owner closes the card under the old key with what changed. `plugin/skills/crew/SKILL.md` and the usage header name no key form, so neither changes (`docs.2`).
