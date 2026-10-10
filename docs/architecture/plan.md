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
- **[plan.6]** A unit that has merged or landed is never amended, split, moved or dropped; a unit marked `Amended` reads amended, then construct, and its code, verify and merge are refused until its construct has committed again, with no approval asked.
- **[plan.7]** A unit's name is its OpenSpec change's name, refused when the kit's main already holds a change by that name, open or archived.
- **[plan.8]** A bolt is cut from GitHub's main fetched at that moment, meets main only at its landing, which rebases it onto main in its own worktree through the kit's hooks, and a landing is refused while the kit's main on its host is behind GitHub's; when the landing's rebase conflicts nothing lands, the team's fix carries the bolt's commits onto main with the conflict resolved, crew makes that the bolt's head, and no agent moves a bolt's branch by hand.
- **[plan.9]** crew removes only worktrees it made, directly under `<kit>/bolts/` or `<kit>/places/` on a `bolt/`, `unit/` or `fix/` branch, once their work is finished, and removes each through the kit's own worktree tool so the kit's remove hooks run and what the kit stood up for that worktree goes with it, a hook that fails keeping the worktree, named; a worktree with modified or non-ignored untracked files, a locked one, the main checkout and a hand-made one are never removed, and nothing is removed while a plan the kit's work goes in cannot be read.
- **[plan.10]** A branch holding commits whose patch the bolt or main lacks, judged by `git cherry`, is kept and named when its worktree goes; a branch holding nothing beyond its target is removed.
- **[plan.11]** A chore is planned maintenance built inside a bolt by code, verify and merge, with no construct and no review, and changes nothing a spec says must be true.
- **[plan.12]** A command reads each kit once and fetches the state branch once, however many steps it has, and stage facts read without `openspec` agree with openspec's on the same worktree.
- **[plan.13]** `After` names a unit whose code the dependent builds on, a contour that exists only once that unit's code exists, or a unit a forecast conflict between the two put it after; the dependent's construct starts only once each has finished construct, never waiting on a merge, and the dependent merges only after each has merged into the bolt; `After` is never set by hand for shared files or for product order, which is the file's.
- **[plan.14]** A landing records the sha main holds afterwards and deploys nothing; a deploy is one act by the kit's deployer under the environment's policy, to one environment, over every landing since that environment's last deployed state, recorded in the run record as it runs with its contents, the kit's after-deploy checks and their outcomes, and every after-deploy step of the landings it carries with its doer and state; a `manual` environment's deploy is a rail row with a card held to approve, a step that is the user's is a rail row with a card until the user marks it done, and promotion to the next environment is a deploy to it.

## Details

**[plan.1]** Rules out: a write that skips `recfix`; a precondition checked once before the replay loop. Source: `plan.py` 263–328, 390–406, 488–500. `land` checks every file a commit holds, the carried `runs/<host>/` files among them; a signal's or capture's markdown is checked by its frontmatter, read as one record.

**[plan.2]** Rules out: a commit with no trailer; two acts in one commit with one entry. Source: `flywheel-state` spec "A commit names its run-record entry"; `plan.py` 449–535.

**[plan.3]** Rules out: a proposal as prose; `bolt give` in a `Do`; a half-applied approval. Source: `plan-proposals` spec; design "Each plan command becomes three parts"; `plan.py` 1122–1165, 1797–1845.

**[plan.4]** Rules out: editing `proposals.rec`; reusing a number; approving over a missing agreement. Source: `plan-proposals` spec; `plan.py` 1498–1510, 1710–1774.

**[plan.5]** Rules out: an `--unblocks` unit in the queue. Source: fix 902336e; `plan-proposals` spec "Work a bolt in flight needs to land goes into that bolt".

**[plan.6]** Rules out: `unit split` on a unit in code; construct on a merged unit; an amended unit held for the user's approval. Source: `bolt-plan` spec; unit-amendments design; ADR 0014 (D5); `plan.py` 1328–1330, 1409, 1449. The code holds an amended unit for `crew unit approve` until `concurrent-units` lands: `_open.md`.

**[plan.7]** Rules out: a unit named after an archived change. Source: `plan.py` 808–817.

**[plan.8]** Rules out: a bolt cut from a stale clone; a landing onto a main behind GitHub; `git reset` or `git branch -f` on a bolt's branch by an agent; a fix that replays main's commits over the bolt; the carrying fix judged by `git cherry`, which compares patches and so never sees a resolved commit as the bolt's. A fix carries the bolt when it sits on a commit main holds and `git range-diff` pairs each of the bolt's commits beyond its base with one of the fix's, equal or changed, none unpaired. Source: fix 04daa5d; `plan.py` 846–879, 976–981; ADR 0015 as restated 2026-10-09 (signal 2026-10-09-crw-1-conductor-47d11d45/01; crw-2's construct's reading). The fix merge moves no bolt until `a-fix-carries-the-bolt-onto-main` lands: `_open.md`.

**[plan.9]** Rules out: tidying `main`; removing a dirty worktree; removing anything when a plan is unreadable; `git worktree remove` on a kit whose `.config/wt.toml` has a `[pre-remove]` or `[post-remove]` hook (swb-3-ops, 2026-10-09: switchboard-kit's hook tears down the worktree's ministack and its Frontegg Development objects, and three fix worktrees' stood after crew removed them, signal 2026-10-09-swb-3-ops-401c8aa3/01 on wldn/main). Read the same day: `wt remove` runs pre-remove hooks with the worktree's files still there, post-remove after, and deletes the branch only when merged, with `--no-delete-branch` to leave it to `plan.10`'s judgment; crew's and swancloud's kits have merge hooks only. Source: worktrees-go-with-their-work; `plan.py` `tidy` 2752; `tests/t-tidy.sh`.

**[plan.10]** Rules out: `git branch -D` on a branch with unmerged patches; judging by ancestry across a rebase. Source: ADR 0003. The code deletes outright and judges by ancestry until `a-drop-keeps-unmerged-work` lands: `_open.md`.

**[plan.11]** Rules out: a construct stage for a chore; a chore that writes a spec. Source: ADR 0001. Not built: `_open.md`.

**[plan.12]** Rules out: a second `gather` in one command; a stage fact that disagrees with openspec. The direct reading knows openspec's own spec-driven schema; a change of any other schema, of a spec-driven its kit or user redefines, or with metadata crew does not read, is read through `openspec`. Source: `openspec/explorations/command-cost/reading.md`; ADR 0008; a-command-reads-the-kits-once; `plan.py` `Reading`, `fetch`, `land`, `survey`; `gather.py` `tasks_of`, `planned`; `tests/t-stage-facts.sh`, `tests/t-reads-once.sh`.

**[plan.13]** Rules out: `After` set by hand between units that only touch the same files; a dependent's construct before its dependency's change is committed; a dependent's construct held for its dependency's merge; a dependent merged before its dependency; `After` as sequencing. Not ruled out: the `After` a conductor sets on a forecast conflict between two unmerged units (`teams.12`). Source: ADR 0011; ADR 0014 (D1 to D3); `bolt-plan` spec "The file's order and dependencies are the plan". The code holds construct until the dependency merges until `concurrent-units` lands: `_open.md`.

**[plan.14]** Rules out: a deploy implied by `crew bolt land`; a deploy whose contents are remembered rather than read; main-ops running a deploy; a `manual` deploy approved anywhere but its card; an after-deploy list of what a check could assert; a step for the user that lives only in a pane. Source: ADR 0012 as amended 2026-10-08 and 2026-10-09; `main-level` spec; swancloud ADR 0018, 0019; the versions statement on channels. Not built: `_open.md`.
