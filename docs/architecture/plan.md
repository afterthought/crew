---
paths:
  - "plugin/lib/plan.py"
  - "plugin/lib/gather.py"
---

# Plan rules

The rules for the plan, proposals, stages, worktrees and every write to a flywheel's branch. `core.md` binds here too; the how-to is README's The plan, Proposals and State sections. Why a drop keeps unmerged work is record 0003; why a change is archived at merge is 0006.

## Rules

- **[plan.1]** Every write runs `recfix --check` on each `.rec` file it changed and crew's own rules (a unit's bolt in the same repo, `After` within one bolt, no cycle) before committing, and its change function re-checks every precondition against the tip it is applied to, since it replays.
- **[plan.2]** Every commit on a flywheel's branch has a subject ending ` (<agent>)` and a `Crew-Entry:` trailer naming its run-record entry, and carries the host's uncarried run record; a carry-only commit names no entry.
- **[plan.3]** A proposal holds only the plan commands a proposal may hold, parsed by the command line's own grammar and applied by the same functions as a direct run; it is checked by applying each `Do` in order to a copy at the tip, one refusal refuses the whole, and approval applies every `Do` in order at the tip and closes the proposal in one commit, or changes nothing.
- **[plan.4]** A proposal is numbered once, never removed, its `Do` lines never changed; it closes only as approved or dropped, and one that touches a held bolt is approved only after that bolt's conductor has agreed.
- **[plan.5]** Work a held bolt needs before it can be proven or land is placed in that bolt ahead of its first unmerged unit, marked `--unblocks`; a proposal that marks a unit so and places it elsewhere is refused.
- **[plan.6]** A unit that has merged or landed is never amended, split, moved or dropped; a unit marked `Amended` reads amended, then construct, then review, and its code, verify and merge are refused until the user approves again.
- **[plan.7]** A unit's name is its OpenSpec change's name, refused when the kit's main already holds a change by that name, open or archived.
- **[plan.8]** A bolt is cut from GitHub's main fetched at that moment, and a landing is refused while the kit's main on its host is behind GitHub's.
- **[plan.9]** crew removes only worktrees it made, directly under `<kit>/bolts/` or `<kit>/places/` on a `bolt/`, `unit/` or `fix/` branch, once their work is finished; a worktree with modified or non-ignored untracked files, a locked one, the main checkout and a hand-made one are never removed, and nothing is removed while a plan the kit's work goes in cannot be read.
- **[plan.10]** A branch holding commits whose patch the bolt or main lacks, judged by `git cherry`, is kept and named when its worktree goes; a branch holding nothing beyond its target is removed.
- **[plan.11]** A chore is planned maintenance built inside a bolt by code, verify and merge, with no construct and no review, and changes nothing a spec says must be true.
- **[plan.12]** A command reads each kit once and fetches the state branch once, however many steps it has, and stage facts read without `openspec` agree with openspec's on the same worktree.

## Details

**[plan.1]** Rules out: a write that skips `recfix`; a precondition checked once before the replay loop. Source: `plan.py` 261–313, 375–389, 478–488. The carried `runs/` files and `signals/*.md` are not checked today: `_open.md`.

**[plan.2]** Rules out: a commit with no trailer; two acts in one commit with one entry. Source: `flywheel-state` spec "A commit names its run-record entry"; `plan.py` 449–535.

**[plan.3]** Rules out: a proposal as prose; `bolt give` in a `Do`; a half-applied approval. Source: `plan-proposals` spec; design "Each plan command becomes three parts"; `plan.py` 1122–1165, 1797–1845.

**[plan.4]** Rules out: editing `proposals.rec`; reusing a number; approving over a missing agreement. Source: `plan-proposals` spec; `plan.py` 1498–1510, 1710–1774.

**[plan.5]** Rules out: an `--unblocks` unit in the queue. Source: fix 902336e; `plan-proposals` spec "Work a bolt in flight needs to land goes into that bolt".

**[plan.6]** Rules out: `unit split` on a unit in code; construct on a merged unit. Source: `bolt-plan` spec; unit-amendments design; `plan.py` 1328–1330, 1409, 1449.

**[plan.7]** Rules out: a unit named after an archived change. Source: `plan.py` 808–817.

**[plan.8]** Rules out: a bolt cut from a stale clone; a landing onto a main behind GitHub. Source: fix 04daa5d; `plan.py` 846–879, 976–981.

**[plan.9]** Rules out: tidying `main`; removing a dirty worktree; removing anything when a plan is unreadable. Source: worktrees-go-with-their-work; `plan.py` 2537–2596; `tests/t-tidy.sh`.

**[plan.10]** Rules out: `git branch -D` on a branch with unmerged patches; judging by ancestry across a rebase. Source: ADR 0003. The code deletes outright and judges by ancestry until `a-drop-keeps-unmerged-work` lands: `_open.md`.

**[plan.11]** Rules out: a construct stage for a chore; a chore that writes a spec. Source: ADR 0001. Not built: `_open.md`.

**[plan.12]** Rules out: a second `gather` in one command; a stage fact that disagrees with openspec. Source: `openspec/explorations/command-cost/reading.md`; ADR 0008. Not built: `_open.md`.
