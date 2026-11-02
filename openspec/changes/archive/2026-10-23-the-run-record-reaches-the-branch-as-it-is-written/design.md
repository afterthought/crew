# Design

## Context

See proposal.md for why. Today `record.emit` appends an entry to `~/.local/state/crew/<label>/runs/<host>/<day>.rec` and stops there. Every write to the flywheel's branch (`plan.write`, through `plan.carried`) adds the host's uncarried entries to its own commit, `crew events --push` (`plan.carry_now`) does it alone, and a `.carried` mark beside the host's files says the newest entry carried. A write's own entry is written after its push, since it names the write's commit, so it always waits for the host's next write. Reading goes through `record.gather`: the branch first (`on_branch`), then one ssh per host of `record.hosts_of` (teams', main level's and every host holding an operator session of the partition) for what each has not carried, each silent host returned in `missing`. Every caller then refuses or holds back while `missing` is not empty: `plan.partition_entries` (the batch clock, `crew review`, the landing's guard, `given_to`), `plan.rail_record` (due units and unanswered batches set to None, cards judged blind by `unjudged`, the sweep's "did not answer whole"), `board.board_data` (a host named for its run record), `page.page` and `ops`'s deploy card. `record.follow` tails each host's files over ssh.

Rules this rests on: `read.5` (record 0029, accepted 2026-10-14), `state.1` (the one write procedure), `state.4` (no service), `read.1` (refuse, never guess), `read.3` (a listing names a silent host and shows the rest), `record.1`–`record.4` (one entry per act after it, a failed append changes nothing, no typed text, a host writes only its own files, union by Id), `code.7` (decisions are functions of facts), `code.9` (a command answers in time). It departs from `plan.2`'s carry clause ("and carries the host's uncarried run record; a carry-only commit names no entry") by design: record 0029 removes that clause, and the design agent amends `plan.2`, and the carry wording in `record.4`'s text, when this lands (`docs.7`); this change edits no page of `docs/architecture/`. Area pages touched: `record.md` (`plugin/lib/record.py`), `plan.md` (`plugin/lib/plan.py`), `briefs.md` (`plugin/roles/operator.md`, `plugin/skills/crew/SKILL.md`), `docs.md` (README) and `tests.md` (`tests/`).

## Goals / Non-Goals

**Goals:**
- Every entry on the branch within the command that wrote it, as its own commit from its host.
- No read of the record over ssh anywhere in crew, decision or view.
- A host that does not answer hides only the stages of its own kits' worktrees.

**Non-Goals:**
- The reads of a host's own entries from its own files (`cards.host_entries` for the card acts an owner posted here, `ops.entries`, the card hook's read, `plan.py`'s reads of this host's `stage.end` entries). They read no other host and nothing over ssh; whether they too should read the branch is not this change's.
- `read.3`'s listing of stages, which still asks every host for its kits and names the silent ones.
- Any change to what an entry holds.

## Decisions

### 1. The command that writes an entry pushes it

`record.emit` appends as today, then calls `record.reach(label)`, which pushes every entry of the host's record of the label that the branch lacks, oldest first by `Id`, normally the one just written. It runs in the same process, before `emit` returns, on the host that wrote the entry, so a command forwarded to a team's host pushes from there (`code.3`). A thread or a detached process was considered and rejected: the next decision on another host could run before the push, and a process that outlives its command is a service by another name (`state.4`).

### 2. An entry's commit is its own

Each entry pushed is one commit whose only change is `runs/<host>/<day>.rec`: the tip's file with the entry added, the union by `Id` under crew's descriptor that `record.carry` already builds (`record.4`). Its message is `runs(<host>): <act> <first On>` (and ` refused` when the entry is a refusal), ending ` (<agent>)`, with `Crew-Entry: <the entry's Id>`: every commit on the branch names an entry, as `plan.2` will say without its carry clause, and the flywheel-state delta says which. Putting a write's entry in the write's own commit was rejected: the entry names the commit (`record.1`, "An entry names the commit it wrote"), which a commit cannot hold of itself.

### 3. `plan.land` takes a chain

When several entries are pushed at once (after a failed push, or `crew events --push`), each is still its own commit, and the chain goes in one push: `make(tip)` may return a list of `(files, message)`, each committed on the one before, every file checked by `checked`, the last pushed without force, the whole chain made again on a moved tip, up to `REPLAYS` (`state.1`). A single `(files, message)` stays as it is for every other write.

### 4. A push that fails is said, kept and caught up

`reach` catches a `Refusal` from the fleet, the fetch, the check or the push and says once on standard error `crew: entry <id> did not reach <label>/main of <repo>: <why>; <host> keeps it and pushes it with its next entry`, and `emit` returns the id as it would have (`record.2`). The entry stays in the host's file. Since every push takes all the host's entries the branch lacks, the next one pushes it first; the `.carried` mark keeps its meaning, the newest entry the branch holds from this host, and is moved only after a push succeeds, so no day with a missed entry is skipped. A file that fails `recfix --check` refuses the chain, naming the file, and no longer refuses a plan write, which carries nothing now. Leaving a missed entry to `crew events --push` alone was rejected: nobody runs it, and decisions would miss the entry until someone did.

### 5. A write carries nothing

`plan.write` commits only its own files; `carried` goes; its entry, emitted after the push as today, reaches the branch by Decision 1, as the commit right after the write's. `crew events --push` (`carry_now`) becomes `reach` run by hand, saying `<ref>: pushed <n> of <host>'s entries` or `<ref>: nothing of <host>'s run record left to push`.

### 6. Reading is the branch's

`record.gather` reads `on_branch` alone and returns `missing` holding only `<label>/main` when its fetch was refused; `hosts_of` and `READ` go. Every caller keeps its refusal for that case (`read.1`), now naming the branch:
- `plan.partition_entries`: `crew can't tell which changes have been in a batch: <label>/main of <repo> could not be read (<why>)`.
- `plan.rail_record` and `record_reading`: due units and unanswered batches are None only when the branch was not read; the sweep's unswept line says `its run record could not be read from <label>/main, so which cards are open can't be told: <why>`.
- `plan.unjudged`: a card is unjudged only while its partition's record was not read; a silent host (`sv`) no longer hides a card's close, since its close is on the branch.
- `board.board_data`: a host is named for its kits alone; the branch, when unread, is named as a plan item, which the code already does for a name that is not a host.
- `page.page`: `unreachable` names the branch only, and the page names no host for its record.
- `ops`'s deploy card and `crew events`/`crew trace` print `<label>/main did not answer: <why>` only for the branch.

### 7. `--follow` follows the branch

`record.follow` fetches the branch every five seconds and prints each entry it has not printed, in time order, from the day it started; it starts no process on any host. Five seconds keeps the console's flow tab near live at a dozen fetches a minute; a fetch that fails is said once and tried again at the next tick. Its first read prints nothing old, as `tail -n 0` did.

### 8. The logic tier stands in for the push

The logic tier starts no process, and `reach` fetches and pushes. `tests/py/conftest.py` replaces `record.reach` with a stand-in that records the labels it was called with, so every case that emits keeps running and a case can assert the push was asked. The decisions are pulled out as functions of facts (`code.7`): `record.unpushed(mine, at_branch, since)` gives the entries the branch lacks and each one's file in chain order; `record.entry_message(entry, agent)` gives its commit message; `record.fresh(seen, entries)` gives what `--follow` prints next.

## Risks / Trade-offs

- [Every act costs a push to GitHub, a write two] → Accepted by record 0029 ("a commit per entry costs a push"); a push is a second or two, inside what an agent's shell gives a command (`code.9`), and a chain makes a backlog one push.
- [More commits on the branch, one per entry] → The branch's history is the record's; recutils readers read files, not the log, and `crew trace` reads entries.
- [A missed push leaves an entry off the branch until the host's next act] → Said on standard error when it happens; decisions read what the branch holds, as record 0029 accepts ("a reading is as fresh as the last push").
- [An entry cut short in a host's file stops that host's record from reaching the branch] → Said on every attempt, naming the file; nothing is lost, and no plan write is refused for it any more.
- [Two hosts pushing at once] → `state.1`'s fetch, apply and replay, as for every write.

## Migration Plan

Nothing to run. A host's entries carried before this change are on the branch already; those still waiting go with its first entry after it updates, from the day of its `.carried` mark. A host on an older crew keeps carrying them in its writes until it updates, which the union by `Id` makes harmless.

## After deploy

None: every behaviour is proven by crew's tiers in this change, and an older host's carry needs nothing done by hand.

## Task notes

**1.1** `record.py`: `unpushed(label, at_branch)` replacing `carry`: from the `.carried` mark's day, each day file's entries (`blocks`) the tip's file lacks, oldest first, each paired with its day path and the file text after it is added (union of the tip's entries and those before it in the chain, under `DESCRIPTOR`, in `Id` order), and the newest id looked at. `entry_message(text, agent)` from an entry's lines: `runs(<Host>): <Act> <first On>[ refused] (<agent>)\n\nCrew-Entry: <Id>\n`. Cases in `tests/py/test_record.py`: three entries, the tip holding the first, give the other two in order, the second's file holding all three; the tip holding all gives none; a day before the mark is not looked at; the message of an entry with no `On`, and of a refusal.

**1.2** `plan.py` `land`: when `make(tip)` returns a list, commit each on the one before (`commit`), `checked` each, push the last, `update-ref` and keep the tip as today; replay the whole list on a refused push. Case in `tests/contract/test_record.py` against a bare repository standing for GitHub (`plan.url` and `plan.CACHE` monkeypatched to scratch paths): a chain of two entries lands as two commits, each changing its day file alone; another clone's push between the fetch and the push makes it replay and land on top.

**1.3** `record.py` `reach(label)`: `crew.load()`, `plan.state_of`, `plan.fetch`, `unpushed` against `plan.show` at the tip, `plan.land` with the chain (the make re-reads `unpushed` against each tip), then `mark_carried`; any `Refusal` said once on standard error as Decision 4 words it. `emit` calls it after its append when the append succeeded. `tests/py/conftest.py` stands in for `reach`. Cases in `tests/py/test_record.py`: `emit` asks `reach` for its label once; a `reach` that is refused is said once and `emit` still returns the id. Journey `tests/t-journey-state.sh`: a tell's entry is on `wldn/main` when the command returns, in a commit changing `runs/<host>/<day>.rec` alone whose `Crew-Entry` is the entry's id.

**2.1** `plan.py` `write`: drop `carried` and the `newest` it set, and `mark_carried` there; `carry_now` calls `record.reach` and prints Decision 5's lines. Journey `tests/t-journey-state.sh`: a plan write's commit changes `plan.rec` alone and the next commit adds its entry, which names it; with the stub remote refusing pushes, a write's entry is said not to have reached the branch, and once pushes go through again the next entry pushes both, each its own commit; `crew events --push` pushes what is left and then says nothing is left; an entry cut short refuses the record's push, naming the file, while the plan write it followed lands.

**3.1** `record.py` `gather`: the branch only; `hosts_of` and `READ` removed, with every caller. Cases in `tests/py/test_record.py`: `gather` with `on_branch` stood in returns its entries and empty `missing`, and calls no `crew.on_machine` (replaced with one that fails the case); a refused fetch gives `missing == {"wldn/main": why}`.

**3.2** `plan.py` `partition_entries`, `rail_record`, `record_reading`, `unjudged` and the sweep's unswept words, as Decision 6. Cases: `tests/py/test_batches.py`, a batch due reckoned from branch entries with no host asked, and the refusal naming the branch; `tests/py/test_rail.py`, the unswept words, and a card closed on a silent host judged closed; `tests/py/test_landing.py`, the landing guard reading the branch's entries with no host asked. Journey `tests/t-journey-review.sh`: with a partition's operator host not answering, a conductor's wait finds the batch due and `crew review` starts the reviewer on it.

**3.3** `board.py` `board_data`'s hosts loop names a host for its kits alone. Case in `tests/py/test_board.py`: an operator host with no team absent from attention while the record is read; an unread branch named as a plan item. Journey `tests/t-journey-board.sh`: a host that does not answer is named for its kits only.

**3.4** `page.py` `page`: `unreachable` from the branch and `describe` only. Case in `tests/py/test_page.py`: a page made from branch entries names no host for its record.

**3.5** `record.py` `follow`: poll the branch every five seconds through `on_branch` with a fresh fetch, print `fresh(seen, entries)`, say a failed fetch once. `fresh` cases in `tests/py/test_record.py`. Journey `tests/t-journey-state.sh`: `crew events --follow` on mac-studio prints an entry the box pushes, and starts no ssh (the stub ssh logs none for it).

**4.1** README *Seeing what happened* and the state repository's `runs/` line, `plugin/skills/crew/SKILL.md`'s `crew events --push` row, `plugin/bin/crew`'s usage lines for `crew events` and `--push`, `record.py`'s docstring and usage, and `plugin/roles/operator.md`'s "on every host the partition runs on" say the record is read from the partition's branch, each entry pushed as it is written, and `--push` pushes what a failed push left. Journey `tests/t-docs.sh` and `tests/t-briefs.sh` (`docs.2`).
