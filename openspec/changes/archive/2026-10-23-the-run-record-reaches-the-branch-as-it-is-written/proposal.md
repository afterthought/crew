# The run record reaches the branch as it is written

## Why

Every note crew takes about a run waits on the host that wrote it until that host's next write to the flywheel's branch carries it there. So the decisions that need the whole record, whether a review batch is due, whether a bolt may land, what a review holds, reach every host of the partition over ssh for what it has not carried, and refuse when any host is silent. macbook-pro, an operator host of every partition that runs no team and is asleep most of the time, has held work this way three times in four days: crw-3's landing on mac-studio on 2026-10-11, a wldn conductor's wait on 2026-10-13, and wldn's review on 2026-10-14, which ran no reviewer and returned an old summary. The user: "it seems intrusive to be reaching across the hosts over SSH when the design is that we should be looking in Git". Record 0029, accepted 2026-10-14, settles it as rule `read.5`: the record is read from the branch alone, and every entry reaches the branch as it is written.

## What Changes

- **Every entry is pushed as it is written.** Once crew appends an entry to the host's file, the same command commits it to `runs/<host>/<day>.rec` on the partition's branch and pushes it, by the one write procedure every state write uses (`state.1`): fetched into crew's cache, checked by `recfix --check`, committed through a temporary index, pushed without force and replayed on a moved tip. The commit is the entry's own, naming it in its `Crew-Entry` trailer, and changes nothing but that day's file.
- **A push that fails is said and caught up.** When the entry cannot reach the branch (GitHub out of reach, the branch not started, a file failing its check), the command says so once on standard error and does what it would have done; the entry stays in the host's file, and the host's next entry, or `crew events --push`, pushes it first, each still as its own commit.
- **A plan write carries nothing.** A write to the branch commits only its own files; its entry follows it at once as its own commit. `crew events --push` stays, as the way to push by hand what a failed push left behind.
- **Nothing reads a host for the record.** `crew events`, `crew trace`, `crew page`, the batch clock, a review, a landing's guard, the rail and the board read the record from the branch alone. The only refusal left for the record is the branch itself not being readable, which each names. `crew events --follow` follows the branch rather than tailing each host over ssh.
- **A silent host hides only its own kits' work.** The board names a host for its kits alone, never for its run record; a card's close is judged from the branch whatever host posted it.
- README, the crew skill, `crew`'s usage header, the operator's brief and `record.py`'s usage say the record is read from the branch (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `run-record`: entries pushed as they are written, each its own commit; reading and following from the branch alone; the carry on every write goes.
- `flywheel-state`: an entry's own commit names the entry it adds.
- `review-batches`: the batch clock, a review and a landing's guard read the branch alone, refused only when it cannot be read; the sweep's whole-record case is the branch's.
- `card-sessions`: a session crew can't judge is one whose partition's record could not be read from its branch, not one whose host is silent.
- `crew-board`: the attention line names a host for its kits only.
- `lineage-page`: the page names the branch it read, and no host for its record.

## Impact

- `plugin/lib/record.py` (`emit`, `carry` and `mark_carried` become the push of what the branch lacks, `gather` and `follow` read the branch, `hosts_of` and `READ` go), `plugin/lib/plan.py` (`land` takes a chain of commits, `write` and `carried`, `carry_now`, `partition_entries`, the rail's `unjudged` and sweep words), `plugin/lib/board.py` (the attention's hosts), `plugin/lib/page.py`, `plugin/roles/operator.md`, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage header, README; tests in all three tiers.
- Every act now costs one push to GitHub from the host that did it; a write costs two, its own and its entry's.
- It edits no rule. `plan.2`'s carry clause and the carry wording in `record.4`'s text go by the design agent's amendment when this lands (record 0029); until then the code stands against that clause by design.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`). What the agents' bands draw does not change (`code.8`).

## Touches

```
plugin/lib/record.py
plugin/lib/plan.py
plugin/lib/board.py
plugin/lib/page.py
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/**
```
