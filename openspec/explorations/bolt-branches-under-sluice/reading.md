> An exploration (2026-10-12): what an elaboration session needs to decide how crew holds a bolt's branch in a kit that merges through sluice. It recommends nothing and decides nothing; record 0023 leaves the question held, beside `agents-in-the-toolchain`.

# A bolt's branch when sluice moves it

## The question

crew keeps each bolt's branch, `bolt/<bolt>`, checked out in a worktree of its own, `<kit>/bolts/<bolt>`. In a kit that merges through sluice, sluice moves that branch itself and guards it against everyone else. What should crew hold instead, if anything, and who verifies the bolt?

The user's doubts, on the answer first designed (a checkout on a second branch, `land/<bolt>`): "isn't it just reversing the decision that bolts don't have branches?", and, on crew verifying the bolt: "won't this just be sluice doing the verification?"

## Which kits this is about, and when

- **Today: none.** A kit merges through sluice only with `sluice = true` in its main checkout's `.config/crew.toml` (`teams.5`), and no kit has it. sluice itself is not yet in use: on its branch it lands bolt branches of a scratch repository end to end, and "sluice lands sluice" is the last piece of its plan (`phase-1-pass-2.md`, piece 12).
- **First live case:** most likely sluice's own kit, built by the team `slc-1`, once sluice gates its own bolt branches and that kit sets the flag; then any kit that opts in after.
- **A kit that merges with `wt merge`** is untouched by all of this: worktrunk merges into a branch checked out in another worktree and brings that worktree along, as crew's bolts work today.

So nothing is broken now. The question is what crew does from the first bolt of the first kit that opts in.

## How a bolt works today

- `crew bolt give` makes `bolt/<bolt>` from main and checks it out at `<kit>/bolts/<bolt>`. The conductor and ops start there; ops deploys and proves from it.
- A unit or fix merges into it with `wt merge bolt/<bolt>` (or `wt submit` in a kit on sluice). worktrunk's post-merge hooks run in that worktree; crew's own repository runs its bolt verification there (`bolt-verify.sh`), swancloud runs `flake-gate verify`, switchboard runs `post-merge-verify`.
- main-level ops lands the bolt from that worktree with `wt merge main`, which rebases `bolt/<bolt>` onto main, gates, and fast-forwards main (`plan.8`).
- When that rebase conflicts, a fix replays the bolt onto main, and crew moves `bolt/<bolt>` to the fix's head with `git reset --keep` in that worktree (record 0015).

## What changes once sluice moves the branch

Facts from sluice's `phase-1-integrations.md`, section 2, captured on sluice's branch:

1. **The checkout goes stale.** sluice lands a unit by moving `bolt/<bolt>` through gix. A worktree that has the branch checked out keeps its old index and files under the new HEAD, so `git status` there shows the landing reversed, staged. `git read-tree -m -u <old> HEAD` in that worktree brings it level.
2. **crew's own moves are refused.** sluice installs a hook that refuses every git move of a branch its policy protects: `git merge`, `git commit`, `git reset --hard <other>`, `git rebase`, `git update-ref`, `git branch -f`, `wt merge bolt/<bolt>`. Today's landing rebases `bolt/<bolt>`, and today's carry resets it; both would be refused. Creating a branch, and deleting one with no submission queued, are allowed.
3. **No post-merge hook runs.** sluice's landing is not a `wt merge`, so worktrunk runs no post-merge hook for it.
4. **sluice has already tested what it lands.** Each submission is tested as the exact tree that would land (the bolt plus the unit, merged), against the checks the branch's policy requires, and the landing commit carries the verdict as trailers (`Sluice-Result: pass (<n> run, <m> replayed)`; sluice record 0006).

On verification, then: in a kit on sluice, sluice's check of each landing is the bolt's verification, and crew has nothing to add. crew's own bolt verification matters only for kits not on sluice, where the kit's post-merge hook does it today, and keeps doing it as long as the bolt's branch is checked out.

## The options

### A. Keep the branch checked out; crew levels the worktree after each sluice landing

When crew reads that a unit's merge stage has delivered (the bolt holds the unit), it runs `git read-tree -m -u <old> HEAD` in `<kit>/bolts/<bolt>`, where `<old>` is the commit whose tree the index still holds. This is record 0023's first draft, point 5.

- **Costs:** one step in crew, read from git; it refuses rather than overwrite a local edit, and is told to the conductor.
- **Leaves open:** the landing's rebase and the carry's reset, both refused by sluice's hook. They need one of D or E below, or sluice relaxing its guard for them.
- **Changes for kits not on sluice:** nothing.

### B. The bolt's checkout on a second branch, `land/<bolt>`

`bolt/<bolt>` is never checked out. The checkout sits on `land/<bolt>`, which crew fast-forwards to `bolt/<bolt>` in the checkout whenever the bolt moves. The landing rebases `land/<bolt>`, and a carry moves it, so the guarded branch is never touched. Designed in full as the change `no-worktree-holds-a-bolts-branch`.

- **The user's point holds:** `land/<bolt>` is a checked-out copy of the bolt's branch under another name. What it buys is only that sluice does not guard it.
- **Costs:** a second branch per bolt to keep in step, and, after a carry, a second line for later fixes.
- **Breaks:** worktrunk then runs post-merge hooks for a bolt in the kit's main checkout, so swancloud's and switchboard's verifications would check main; the change answers that by crew verifying bolts itself, which, per the facts above, only kits not on sluice need.

### C. A detached checkout at the bolt's head

No branch checked out: crew moves the checkout with `git switch --detach bolt/<bolt>` when the bolt moves.

- **Costs:** none beyond A's step.
- **Breaks:** kit tooling that names a worktree by its branch (worktrunk's `{{ branch }}`, switchboard's dev-server names) sees a detached HEAD; the landing still needs a branch to rebase.

### D. No bolt checkout at all

The bolt is a branch only, as flywheel-next has it: "the bolt's line is a branch …, the unit's one work item has a place, a worktree of that line", and "the line lands on `main`" (flywheel-next's README). The conductor reads the bolt through git and needs no worktree; ops proves in a place crew makes at the bolt's head for that proof and removes after, as sluice makes a place per candidate; the landing happens from a place made for it.

- **Costs:** a place per proof (a cold toolchain, about 20 s for a devenv kit, until sluice's caching lands); the conductor and ops start in the kit's main checkout.
- **Breaks:** ops's long-lived checkout, where a deployed bolt's dev servers run today; `bolt_place` and the briefs; the post-merge hooks, as in B.
- **Fits:** flywheel's own model, which crew is meant to become.

### E. The bolt lands through sluice too

main-level ops submits the bolt to main (`wt submit main`), and sluice lands it as a merge commit after testing main plus the bolt. A conflict is blamed on the bolt; the team merges main into the bolt by a submission to the bolt.

- **Costs:** none of crew's moves remain: no rebase, no carry.
- **Breaks:** `plan.8`'s rebase at landing and record 0015's carry; main's history gains a merge commit per bolt. It belongs with a kit whose main also goes through sluice.

## What is not known

- Whether sluice will tell a session, or crew, when it lands on a branch, so crew levels or follows at once rather than at its next read.
- Whether sluice's guard could allow a named move (a landing's rebase, a carry) by policy, which would make A enough on its own.
- How ops's proof should work for a kit on sluice: whether ops needs a long-lived checkout at all, or a fresh place per proof (D).
- Which kit opts into sluice first, and when.

## What an elaboration could settle

1. For a kit on sluice: keep the bolt's branch checked out and level it (A), or hold no checkout of it (B, C or D).
2. How a bolt in such a kit lands: rebased by crew from a branch sluice does not guard (B, C, D), or through sluice (E).
3. That bolt verification is sluice's in a kit on sluice and stays the kit's post-merge hook elsewhere, so crew verifies nothing itself; or that crew verifies every kit's bolts the same way.
4. Whether crew moves towards flywheel's lines and places now (D), or keeps its bolt checkout until flywheel takes over.
