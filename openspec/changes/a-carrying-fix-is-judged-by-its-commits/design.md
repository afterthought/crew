# Design

## Context

`crew fix <team> <name> --merge` asks `plan _carry <team> <fix> <bolt>` whether the fix carries the bolt onto main, and evals its shell assignments (`teams.9`): `CARRIES=yes` with `OLD`, `NEW`, `COMMITS` and `CHANGED`, or `CARRIES=no` with `WHY`. Today `carry_cmd` in `plugin/lib/plan.py` refuses when a head is missing, says no when the fix holds the bolt's head or either side has no commits beyond main, and otherwise runs `git range-diff --no-color --no-patch main..<bolt> main..<fix>` and parses it with `RANGE` and `pairing()`: carry when every row is `=` or `!` in the same place.

range-diff pairs by cost: a pair is made only when the diff between the two patches is small next to the patches, at a creation factor of 60 by default. A one-line edit whose surrounding lines main rewrote has a replay whose context is all new, so the diff of diffs outweighs the patch and range-diff prints the original as `<` and the replay as `>`. Read on 2026-10-09 with git 2.54.0, in a scratch repository: a bolt commit `feat: ten` changing line 10 of `seq 1 20`, main rewriting lines 7–9 and 11–13, the replay resolved to keep both. range-diff left the pair unpaired at its default and at creation factors 61, 62 and 70, and paired it as `!` at 100. crw-1's real case paired at 62 (signal 2026-10-10-crw-1-conductor-69720a11/01). No factor is right for every case, which is why `plan.8` and record 0015, restated 2026-10-10, take the judgment away from range-diff.

The rules this rests on: `plan.8` (a fix carries the bolt when it sits on a commit main holds, holds as many commits beyond their common base as the bolt, and in order each is the same commit replayed, by message and author, its patch equal or changed; range-diff printed as the reading), `teams.5` (such a fix becomes the bolt's head by crew's move), `teams.9` (only shell assignments on standard output; everything else on standard error), `read.1` (refuse on what crew cannot read, never guess), `read.2` (read another tool's output only by facts checked against it), `code.1` (standard library only), `code.2` (refusals through `fail()`), `code.6` (the move is `reset --keep`, unchanged here), `docs.2` (README, skill and usage header together), `docs.4` (the spec changes only through this delta). Pages whose area this touches: `plan.md`, `teams.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- The carry judgment reads only facts git stores about each commit: which commits lie beyond main, in what order, their messages, authors and patches.
- range-diff's view is still shown, so the conductor and the user can see how the resolution changed each commit.
- The bash side of `--merge`, the move, the checks and the record stay exactly as `a-fix-carries-the-bolt-onto-main` built them.

**Non-Goals:**
- Judging whether the resolution kept both intents: that is the fix agent's work and the bolt's proof, not crew's.
- Author date and committer: a replay keeps the author date unless asked not to, and always changes the committer, so neither is part of "the same commit".
- Changing what a fix that does not carry does; it merges as every fix does.
- The briefs: the coder brief already tells the fix's agent to add no commit, drop none and change nothing else, which covers rewording.

## Decisions

### The judgment is count, order and identity

`carry_cmd` keeps its first checks as they are (heads present, bolt head not in the fix, commits beyond main on both sides) and replaces the range-diff pairing with this:

1. Read each side's commits beyond the kit's main, oldest first: `main..<bolt>` and `main..<fix>`, each commit's sha, author name, author email and whole message. One `git log --reverse` per side, with field and record separators that cannot occur in the output, keeps it to one call per side on a remote host.
2. A commit's identity is its message exactly as git stores it (`%B`) and its author name and email. The fix carries the bolt when both sides hold the same number of commits and the identity at each position is the same.
3. Each pair's patch is compared by `git patch-id --stable` over each side's `git log -p`: equal ids are the same patch, different ids a changed one. `CHANGED` is how many differ. A commit with an empty patch has no id, and two empty patches are equal.

"Sits on a commit main holds" needs no check of its own: `main..<fix>` is every commit the fix has that main lacks, so a fix that also holds commits from elsewhere has more commits, or other identities, than the bolt, and does not carry.

Alternatives considered: range-diff at a higher creation factor (no factor is right for every rewrite, as the reading above shows, and a high one pairs commits that are not the same); `git cherry` (judges by patch, so it sees every resolved commit as missing; `plan.8` rules it out); matching by subject alone (two commits of one bolt can share a subject, and a reworded body is a different commit).

### Why not, in the bolt's commits' terms

When the fix does not carry, `WHY` names commits the way the old pairing did, so the conductor can tell the fix's agent what to undo. Commits are matched by identity, each used once, in order:

- each of the bolt's commits with no match in the fix: "the bolt's commit `<sha7>` (`<subject>`) is not in it", or "the bolt's commits … are not in it";
- each of the fix's commits with no match in the bolt: "its commit `<sha7>` (`<subject>`) is none of the bolt's", or "its commits … are none of the bolt's";
- when every commit matches but not in the same places: "its commits are the bolt's in another order".

Joined with "; ", as today. A reworded or re-authored commit shows as both: the bolt's original is not in it, and the fix's copy is none of the bolt's. The count alone is never the reason given, since naming the commits is what the conductor acts on.

### range-diff is printed, never parsed

Once it has judged (carry or not, with both sides having commits beyond main), `plan _carry` runs `git range-diff --no-color --no-patch main..<bolt> main..<fix>` and writes to standard error a line naming the two ranges and saying crew judges by the commits, then range-diff's lines as git printed them. When range-diff exits non-zero, it writes instead that range-diff could not be read, in git's words. Neither changes the judgment. `--merge` already passes the judgment's standard error on (`cat "$errs" >&2`), so the conductor sees the reading above crew's own line in both outcomes; `--move` prints no reading. `RANGE` and `pairing()` go: nothing in crew parses range-diff any more, so `read.2` no longer applies to it.

### Docs

README's fix paragraph says how the carry is judged and that range-diff is printed as the reading; the usage header's `--merge` line and the skill's sentence on the carrying fix gain "each with its message and author" (`docs.2`). `_open.md` drops the `plan.8`/`teams.5` line. `plan.8`'s details end with what builds it instead of the `_open.md` pointer; `teams.5`'s details cite ADR 0015 as restated 2026-10-09 and 2026-10-10. The rule lines of `plan.8` and `teams.5` already say this and are not changed.

## Risks / Trade-offs

- [A fix whose agent edited a commit message while resolving, or whose rebase's message cleanup altered one (a line beginning `#`)] → it does not carry and merges as a fix, naming that commit both ways; the conductor runs the fix again. Safe: crew never moves a bolt for a fix it cannot show is the bolt.
- [A bolt commit main already holds by patch, which the replay drops as empty] → the fix holds one commit fewer and merges as a fix, naming that commit. Rare, and the same outcome as today.
- [Archive order] → this delta modifies a requirement that `a-fix-carries-the-bolt-onto-main` adds, and that change is not archived yet; `openspec validate` passes and notes archive would refuse it, so `a-fix-carries-the-bolt-onto-main` is archived first.

## Proof in dev

Nothing to deploy: crew's proof before landing is the bolt's verification. On real work, once the bolt has landed and every host has pulled: the next landing that conflicts and is carried by a fix moves the bolt, and its `--merge` output shows the range-diff reading above the move. The conductor that runs it says so; no step is the user's.

## Task notes

### 1.1

In `carry_cmd`, keep the heads, ancestor and empty-range checks and their `WHY` words. Replace the `pairing()` call with the judgment above; drop `RANGE` and `pairing()`. Read through `kit_git` where a call needs no input; `git patch-id` reads the patch text on standard input, so run it with `crew.on_machine(..., input=...)` on the team's host, refusing through `fail()` in git's words when it fails (`read.1`, `code.2`). Print the reading on standard error only (`teams.9`); stdout stays the shell assignments, unchanged in name and meaning. Update `carry_cmd`'s docstring to say how it judges.

### 1.2

`tests/t-fix.sh`, the carry section. The two existing "does not carry" assertions take the new words: the own-commit fix names "its commit `<sha7>` (fix: one of its own) is none of the bolt's"; the drops-one fix names "the bolt's commit `<sha7>` (feat: two) is not in it". Add:

- **A replay whose context main rewrote**: a file of twenty numbered lines that main and the bolt both hold (a carry that has already put the bolt on main gives that), a bolt commit changing line 10, a main commit rewriting lines 7–9 and 11–13, and a fix that replays the bolt resolving the conflict to keep both. Assert the bolt moves to the fix's head, the "N changed by the resolution" count includes it, and the output holds range-diff's `<` and `>` lines for that commit, which shows range-diff did not pair what crew carried.
- **A reworded commit**: a fix that replays the bolt and amends one commit's message; assert no move, a merge stage, and both "is not in it" and "is none of the bolt's" naming that commit.
- **A re-authored commit**: as above with `--author` changed and the message kept.
- **The reading on a merge**: one of the "does not carry" cases asserts the output holds a range-diff line.

The test's inputs do not change, so `tests/moon.yml` stays as it is.

### 2.1

README: in the fix paragraph, after "carries the bolt onto main", say crew judges it by the commits themselves (as many as the bolt's beyond main, in order each the bolt's commit replayed with the same message and author, its patch the same or changed) and prints `git range-diff` of the two as the reading, which judges nothing. `plugin/bin/crew`'s usage header, the `--merge` entry, and `plugin/skills/crew/SKILL.md`'s sentence on the carrying fix: "replayed onto the kit's main, each with its message and author". `docs/architecture/_open.md`: remove the `plan.8`, `teams.5` line. `docs/architecture/plan.md`, `plan.8` details: replace "The fix merge moves no bolt until `a-fix-carries-the-bolt-onto-main` lands: `_open.md`." with what builds it (`plan.py` `carry_cmd`; `tests/t-fix.sh`). `docs/architecture/teams.md`, `teams.5` details: "ADR 0015 as restated 2026-10-09 and 2026-10-10". Rule lines stay as they are.
