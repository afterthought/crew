---
number: 15
title: A bolt meets main at its landing, and a fix carries it there when they conflict
status: superseded
date: 2026-10-09
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A bolt meets main at its landing, and a fix carries it there when they conflict

Superseded 2026-10-13 by record 0026, proposed in the elaboration session: a bolt meets main through sluice, a conflict is taken into the bolt by a submission, and no fix carries a bolt.

Deciders: the user (through crw-1's conductor and swancloud-planner, signal 2026-10-09-crw-1-conductor-47d11d45/01: the bolt a-teams-cards-are-its-conductors cannot land because its landing conflicts with crew's main and a fix cannot carry a rebase into the bolt; for this bolt the user moves the bolt's branch by hand); swancloud-design.
Sources: `plugin/roles/main-ops.md` steps 2 and 3; `plugin/roles/coder.md` on a merge whose rebase conflicts; `docs/architecture/plan.md` plan.8; `teams.md` teams.5; `core.md` code.6, read.4; `plan.py` `REBASE` and `UNREBASE`; `wt merge --help` (rebase, then fast-forward the target; `--no-rebase` requires a fast-forward).

## Context and problem statement

A bolt is cut from GitHub's main and lands by `wt merge main --no-squash --no-remove` from its worktree, which rebases the bolt onto main and fast-forwards main to it. Main moves while a bolt is built, by other landings and by the design agents' commits, so a bolt lands behind main as a rule, and the landing's rebase is where the two meet. When that rebase conflicts, the main-ops brief says the conflict is resolved on the bolt, by its team, as a fix. Read on 2026-10-09 in crew's own kit: bolt `a-teams-cards-are-its-conductors` at df9d985 sits four commits behind main (f4198aa to d323859), and its commit 073ff74 edits the `_open.md` line that main's cc9dfc2 also edits. The team's fix agent built the resolution the brief asks for, the bolt's six commits replayed onto main with the conflict resolved (7d9b98e), and found it cannot reach the bolt: a fix merges only by `wt merge bolt/<bolt>`, which rebases the fix onto the bolt, replaying main's four commits over the bolt's tip, where the same line conflicts again, and would leave the bolt holding its old commits under copies of main's. The bolt's branch must move to the rebased head, a move no agent may make by hand (`code.6`: never `git reset`; `read.4`: crew takes over nothing it did not make, and the bolt's branch is crew's).

## Decision drivers

- A bolt behind main is normal and is nobody's fault; bringing it onto main must be routine, by crew, not a hand move of a branch.
- Resolving a conflict is the team's work, as it is for a unit's merge (the coder's brief: keep both intents), not main-ops's, which never edits the code.
- Nothing lands on main but through the kit's merge hooks, on the user's word (`state.3`); the bolt's checks and ops's proof cover what lands.

## Considered options

1. The team's fix carries the bolt onto main: the fix's branch is the bolt's commits on the kit's main with the conflict resolved, and crew's fix merge moves the bolt to that head when the branch holds every patch of the bolt on main and nothing else.
2. main-ops resolves the conflict in the landing's rebase, in the bolt's worktree, on the user's word.
3. A `crew bolt rebase <bolt>` the conductor runs before landing, which stops on a conflict for a fix agent to resolve in the bolt's worktree.
4. As today: the brief sends the conflict to a fix that cannot carry it, and the user moves the branch by hand.

## Decision outcome

Option 1. A bolt meets main only at its landing. When the landing's rebase conflicts, main-ops aborts it, lands nothing, and tells the conductor the commit and the files. The team resolves it as a fix whose branch is the bolt's own commits replayed onto the kit's main with the conflict resolved keeping both intents, built in the fix's place as any fix is. crew's fix merge, finding that the fix's branch sits on a commit the kit's main holds and that `git range-diff` pairs each of the bolt's commits beyond its base with exactly one of the fix's, in order, equal or changed, with no commit of the fix's unpaired, moves the bolt's branch to the fix's head in the bolt's worktree instead of merging into it, and says so (restated 2026-10-09 on crw-2's construct's reading: `git cherry` judges by patch, and resolving a conflict changes the resolved commit's patch, so `git cherry -v 7d9b98e df9d985` marks 073ff74 as missing from the fix and the twelve others present, and a cherry judgement would merge every carrying fix as a fix; `git range-diff main...df9d985 d323859..7d9b98e` pairs twelve `=` and 073ff74 `!` b515c00 with nothing unpaired; `git cherry` stays `plan.10`'s judge of a branch's unmerged patches. The fix's base is a commit main holds, not main's tip, since the landing rebases again. Restated again 2026-10-10 on crw-1's fix agent's reading, signal 2026-10-10-crw-1-conductor-69720a11/01: `git range-diff` at its default creation factor of 60 would not pair b515c00's replay once main had rewritten every line around what that commit edits, and paired it only at 62, so a judgement that rests on range-diff's heuristic fails for the very case the rule exists for. The judgement is the commits' own: the fix carries the bolt when its range holds as many commits as the bolt's beyond their common base, and in order each is the same commit replayed, the same message and author, its patch equal or changed; crew prints range-diff's view as the reading, never as the judge); the bolt's checks run on the new head as they do after a merge, and ops proves the bolt again before it lands, since its head changed. A fix whose branch holds any other patch, or lacks one of the bolt's, merges as every fix does. No agent moves a bolt's branch by hand; the user may, on their own word, and that is the break-glass, recorded as the landing's reading.

What follows from it:

- `plan.8` gains the landing's rebase and the fix that carries it; `teams.5` gains the one way a fix becomes the bolt's head; `code.6`'s details say crew moving a branch it made is a move, not a discard.
- The main-ops brief's step 3 keeps its words and gains what the fix is; the conductor's and coder's briefs say what a fix that carries the bolt is.
- For `a-teams-cards-are-its-conductors` the user moves the branch to 7d9b98e by hand, as they decided; crw-1's fix `rebase-onto-main` then holds nothing beyond the bolt and goes as a merged fix does, the bolt's checks run, ops proves it again, and it lands.

### Consequences

- One unit in crew, `a-fix-carries-the-bolt-onto-main`.
- Every crew bolt that lands behind a moved main hits this until it lands; the planner places it early.

## Pros and cons of the options

### Option 1: the fix carries the bolt

- Good: the resolution is the team's and is reviewed, checked and proved as its work; the branch moves only by crew; nothing new for the conductor to learn beyond what the fix is.
- Bad: one more rule in the fix merge, and a second proof of the bolt.

### Option 2: main-ops resolves at landing

- Bad: main-ops edits code it did not build, in the bolt's worktree, with no review of the resolution before it is on main; the proof never saw the landed tree.

### Option 3: a bolt rebase command

- Bad: a stage that runs in the bolt's worktree, which crew reserves for merges; a conflict left mid-rebase for an agent to find; the same proof question as option 1 without its review.

### Option 4: as today

- Bad: a brief that names a path that does not exist, and a hand move of a crew branch for every conflicting bolt.
