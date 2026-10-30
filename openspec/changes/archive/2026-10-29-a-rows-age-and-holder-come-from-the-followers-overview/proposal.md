# Proposal

## Why

The unit merged first in this bolt, `a-bolts-row-shows-its-age-and-who-holds-it`, gives every bolt's row its age and who held its time (`plan.20`, record 0044 outcome 5). To count a decided merge's time in the gate, it has each kit's gather run `sluice status <branch> --all --json` once for every held bolt and once more for main, at every gather. That is a sluice process per bolt per gather, beside the one overview watch per kit the host's follower already holds. sluice's overview is a reader's one contract with sluice (sluice ADR 0023), and on one host one process reads a repository's records for everyone watching (sluice clause 129). The design agent ruled on 2026-10-28, reading batch 53, that the follower's recurring read takes only the overview it already holds. Those calls are written into this bolt's crew-board spec, so taking them out is a unit, and this bolt cannot land until it is done.

## What Changes

- A kit's gather runs no `sluice status`, for a held bolt or for main. It reads sluice only through the overview: the line the follower's watch hands in, or one `sluice overview --json` where no watch runs.
- Each submission's facts come from the overview, as it stands and as it leaves:
  - While it stands, the overview gives its number, where it came from, when it was submitted, and, once a candidate tests it, when its checks began. The row has carried the number and the submit time from the submit since record 0046.
  - When it is decided, the watch line that no longer holds it names the decision in the branch's recent events, with its time. The follower takes the decision's time from that line, once, and starts no process for it. A submission that leaves with no event, a withdrawal, is decided at that line's time.
  - The host's follower keeps what it saw of each submission of a held bolt, from its submit to its decision, for as long as the bolt is held. A gather does not throw that away.
- The minutes from a merge's submit to its decision are split as `plan.20` says: the team's while the submission stands queued, the kit's while it is under test. Where crew holds no start of the checks, the split of that stay can't be told. The row then shows those minutes as **team or kit**, with why. It does not count them as the team's under the merge stage, and it does not count them as the kit's for the whole stay, which the merged unit did. A merge that ended before the follower saw its submission, after the follower restarted, is shown the same way for the merge's whole run.
- A read made once at an act stays: the landing still reads sluice's record of the bolt's submissions once on the team's host when its entry is written (`plan.21`), and the landing read still reads its submission's record.
- The landing entry's `Split` names the team-or-kit minutes too, so it still adds up to `Age`.
- The crew-board spec says this in place of the gather's calls. Tests pin a row drawn from the overview, a gather that starts no sluice process, and a decided merge with and without its checks' start.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `crew-board`: the follower's gather of a kit reads sluice only through the overview, and the follower keeps each submission it saw from its submit to its decision. A decided submission's stay is split at its checks' start where crew holds it, and is shown as team-or-kit where it does not. The head line shows those minutes, and the holder rule and its sources say so.
- `run-record`: a bolt's landing entry's `Split` names the team-or-kit minutes.

## Impact

- `plugin/lib/gather.py`: `history`, `status_all` and the gather's call to them go. `status_read` and `decided_of` stay for the landing's one read. A guarded reader of the overview's recent events gives each decided submission's number, where it came from and its decision time.
- `plugin/lib/board.py`: the follower keeps each held bolt's submissions per kit across watch lines and gathers, in place of `kept_gone` and the gather's `history`.
- `plugin/lib/plan.py`: `bolt_time` gains the team-or-kit share and its place in the order, `bolt_facts` reads decided submissions from the follower's kept view and the run record's landing number, and `time_said` and `landing_split` name the new share. `held_time` reads the kept view in place of `history`.
- `plugin/lib/record.py`: the comment on `Split` names the new share.
- `plugin/hooks/status.js` changes only if a case shows the band must draw the new share. `test_board.py`'s case pinning the keys the mod reads covers `time.shares`.
- README's board section and `plugin/skills/crew/SKILL.md`, where they describe the head line and what it reads (`docs.2`).
- Tests in the logic and contract tiers. A recorded overview from the host's current sluice is added beside sluice 0.51.3's, holding a branch's recent events in the form that sluice prints. `tests/moon.yml` is updated if a test's reads change.

## Touches

```
plugin/lib/gather.py
plugin/lib/board.py
plugin/lib/plan.py
plugin/lib/record.py
plugin/hooks/status.js
plugin/tests/**
README.md
plugin/skills/crew/SKILL.md
tests/py/**
tests/contract/test_gather.py
tests/t-journey-board.sh
tests/moon.yml
```
