# Design

## Context

crew removes a worktree in one place: `tidy` in `plugin/lib/plan.py`, which every read of a team runs on its host (`crew _tidy`, from `reap`), and which `crew bolt drop`, `crew unit drop` and `crew bolt land` run at once through `tidy_after`. A merged unit's or fix's place and a landed or dropped bolt's worktree all go by it; main-level ops lands with `wt merge main --no-remove`, and a unit or fix merges with `wt merge bolt/<bolt> --no-remove`, so nothing else removes one. Today `tidy` runs `git worktree remove --force <path>` from the kit's main checkout, then `git branch -D <branch>`. Git knows nothing of worktrunk's hooks, so a kit's `[pre-remove]` and `[post-remove]` never run (proposal, Why).

The rule this builds is `plan.9` as amended on 2026-10-09; the branch is `plan.10`'s. Rules relied on: `plan.9`, `plan.10`, `read.1`, `read.2`, `read.4`, `code.2`, `code.3`, `roles.2`. Pages whose areas this touches: `plan.md` (`plan.py`), `briefs.md` (two briefs), `teams.md` (`plugin/bin/crew`'s usage header), `tests.md` (`tests/t-tidy.sh`), `docs.md` (README, `docs/architecture/`). `docs.2` asks README, the skill and the usage header to move together: the skill says nothing of how a worktree goes, so only README and the usage header change.

### What `wt remove` does, read against wt 0.80.0 on mac-studio (2026-10-09)

From `wt remove --help`, `wt hook --help`, and runs in a scratch repo with a scratch HOME:

- `wt -C <main> remove <path> --foreground --no-delete-branch --format json` removes the worktree at `<path>` and leaves its branch; stdout is a JSON array of one object, `{kind, branch, path, branch_outcome, branch_checked_out_at}`, with `branch_outcome` `not_attempted`. Progress and hook output go to stderr. Exit 0.
- The hooks are read from the `.config/wt.toml` of the worktree the command runs in, so with `-C <main>` they are the kit's main's, not the removed worktree's.
- `pre-remove` runs in the worktree being removed, files present, and blocks: when it fails, wt exits 1, removes nothing, and stderr ends `✗ pre-remove command failed: <name>: exit status: <n>` then `↳ To skip pre-remove hooks, re-run with --no-hooks`.
- `post-remove` runs after the worktree is gone, in the background, logged by wt; its outcome does not reach the caller.
- Project hooks run only once approved for the user (`~/.config/worktrunk/approvals.toml`). Unapproved and without a terminal, wt exits 1 and removes nothing; stderr holds `▲ <repo> needs approval to execute <n> commands:`, the commands, `✗ Cannot prompt for approval in non-interactive environment` and a `↳` line advising `--yes`. A config with only merge hooks asks no approval for a remove.
- Ignored files do not stop a removal without `--force`; `--force` also removes a worktree with modified or untracked files.
- Without `--foreground` the removal itself runs in the background and its result is not seen.

## Goals / Non-Goals

**Goals:**
- Every removal `tidy` makes runs the kit's remove hooks, and one wt refuses keeps the worktree and its branch, named on every read until it goes.

**Non-Goals:**
- How the branch is judged. This keeps `tidy`'s branch step as it is; `a-drop-keeps-unmerged-work` replaces its `git branch -D` with `plan.10`'s `git cherry` judgment.
- Tearing down what the three swb-3 fix worktrees left on 2026-10-09: they are gone, and no hook can run for them now.
- Seeing a `post-remove` hook's failure: wt runs it in the background after the worktree is gone, so nothing is left to keep.
- A time limit on a remove hook (Risks).

## Decisions

### One `wt remove`, from the kit's main, with the branch left to crew

`tidy` replaces `git worktree remove --force <path>` with:

```
wt -C <main> remove <path> --foreground --no-delete-branch --force --format json
```

- **`-C <main>`**: the kit's main checkout says which hooks run, the same checkout the kit's merges into main are gated from, and no worktree under removal can change them.
- **`--foreground`**: crew must see the outcome before it decides the branch and names anything; a background removal would report nothing.
- **`--no-delete-branch`**: the branch is crew's (`plan.10`). wt's own judgment ("would add no changes to the default branch") is against main only and differs from `git cherry` against the bolt.
- **`--force`**: crew has already found the worktree clean (`git status --porcelain` empty, not locked) before it calls wt, and that check is the guard `plan.9` names. Passing `--force` keeps a file a kit's own pre-remove hook writes from leaving a worktree half torn down and standing, and keeps git's own refusals, such as submodules, from returning (`worktrees-go-with-their-work`'s note on `--force`). It does not remove a locked worktree, and crew never offers one.
- **`--format json`**: the one form wt documents for a caller to read the branch's fate (`read.2`).
- **Never `--yes`, never `--no-hooks`**: approving a kit's commands is the user's, as for its merge hooks (`roles.2`; CLAUDE.md, the first merge on a host waits for the user's `wt config approvals add`), and skipping them is what this change ends.

Alternatives: running `wt hook pre-remove` and then `git worktree remove` loses the background post-remove and runs hooks outside the tool's own order; `wt remove` without `--no-delete-branch` hands the branch to the tool, which the intent rules out.

The call runs with gitenv's environment minus every `WORKTRUNK_*` variable, so a tidy run from inside a merge hook's shell never writes a `cd` into that shell's directive file (the reason `tests/lib.sh` unsets them).

### Reading what wt said

- **Exit 0 and the worktree still there**: wt exited 0 and left its folder standing, so the worktree and branch are kept, said (`read.1`); crew drops its read of the kit, and the next read tries again.
- **Exit 0 and the JSON readable**: the worktree is removed when the one object's `path` is the worktree's path; `branch_outcome` `not_attempted` means the branch was left to crew, and `tidy` goes on to its branch step as today. Any other `branch_outcome`, an absent field, or JSON crew cannot parse: the worktree is removed and the branch is not touched, said (`read.1`, `read.2`). crew drops its read of the kit either way, as today.
- **Exit non-zero**: the worktree and branch are kept. crew reads wt's stderr: when a line says `Cannot prompt for approval`, the kit's hooks wait for the user's approval; otherwise crew names each line that begins `✗`, and when there is none, the last non-empty line, and when stderr is empty, `wt remove exited <n>`. A line that begins `↳` is never passed on: those advise `--no-hooks` or `--yes`.
- **wt not on the host's path** (`FileNotFoundError`): kept, said.

Nothing is remembered between reads: the next read finds the worktree still there, finished and clean, and calls wt again, as it does for a worktree kept for a lock or a stray file.

### What crew says

With `<over>` the reason its work is over, as `tidy` already words it (`unit x has merged into bolt/y`):

- removed: unchanged, `<path> and <branch> are removed; the branch was at <sha>`, or `<path> is removed, and <branch> is kept: <git's words>`.
- a hook failed: `<path> is kept, and <branch> with it: <over>, and the kit's wt remove refused it: <wt's ✗ lines, joined with "; ">`.
- approval: `<path> is kept, and <branch> with it: <over>, and the kit's remove hooks wait for the user's approval on <host>: wt config approvals add, in <main>`.
- no wt: `<path> is kept, and <branch> with it: <over>, and wt, the kit's worktree tool, is not on <host>'s path`.
- left standing: `<path> is kept, and <branch> with it: <over>, and the kit's wt remove exited 0 and left it there`.
- branch unread: `<path> is removed, and <branch> is kept: crew could not read what wt remove said of the branch`.

The "uncommitted changes" and "locked" messages are unchanged.

## Risks / Trade-offs

- [A slow remove hook makes a team read slow, and a hung one hangs it] → the read waits, once per worktree, since a teardown cut short is worse than a slow read; no limit is set. Named to the design agent.
- [A hook that keeps failing runs again on every read of the team, calling the kit's outside systems each time] → the same rule as a stray file: named every read, retried every read. Named to the design agent.
- [A post-remove hook's failure is never seen] → wt's design; such a hook's log is wt's (`wt config state logs`). Named to the design agent.
- [Remove hooks not yet approved on a host keep every finished worktree of that kit there] → crew says so on every read, naming the approval; the box's approvals are checked in dev.
- [wt's stderr wording changes] → crew still keeps the worktree on a non-zero exit; only the words it names change, and the approval case falls back to naming the `✗` line.
- [wt missing on a host's non-interactive path] → kept and said; checked in dev.

## Migration Plan

None. A kit with no remove hooks sees nothing new. The first read on a host after the bolt lands runs the kit's remove hooks for any finished worktree still there.

## Proof in dev

Once the bolt has landed and every host has pulled:

1. On wldn's box (chuck-herdr-alpha), crew's forwarded commands find wt: `ssh -o BatchMode=yes chuck-herdr-alpha 'command -v wt && wt --version'` names a wt that has `remove --no-delete-branch --format json` (0.80.0 does).
2. On the box, switchboard-kit's remove hooks are approved for the user: `wt -C <switchboard-kit main> hook show` lists `pre-remove`, and the user's approvals cover them (or the user runs `wt config approvals add` in switchboard-kit's main).
3. The next swb fix or unit to merge on the box: after its conductor's next `crew status`, its place is gone, its ministack is down and its Frontegg Development objects are gone, as switchboard-kit's pre-remove hook says.
4. On mac-studio, the next crw unit to merge has no place left after its conductor's next `crew status`, with no approval asked (crew's kit has merge hooks only).

## Task notes

**1.1** In `tidy`, the `git worktree remove --force` call and its error branch become the `wt remove` run in Decisions, read as Decisions says, with the messages in What crew says; the branch step after it runs only when the JSON says `not_attempted`. `this_host()` from `crew` names the host. Keep gitenv for the call, then drop every key that starts `WORKTRUNK_`. Catch `FileNotFoundError` from `subprocess.run` (`code.2`: no traceback). The docstring says the removal goes through the kit's `wt remove`, so its remove hooks run, and that one wt refuses is kept.

**1.2** `tests/t-tidy.sh`, after its present cases (they stand as they are, on a fixture kit with no `.config/wt.toml`, which proves a kit with no remove hooks asks no approval). Commit to `$k`'s main a `.config/wt.toml` whose `[pre-remove]` appends `pre <worktree_name> <files present?>` to a log outside the kit and exits 1 while a marker file `$HOME/fail-{{ worktree_name }}` exists, and whose `[post-remove]` appends `post <worktree_name>` to the same log. Run wt as the box's user (`as $box`), whose HOME is the test's scratch home, so approvals are the test's. Then:
- a finished place before approval: kept with its branch, named with "wait for the user's approval on chuck-herdr-alpha", no `pre` line logged, and `lacks "--yes"`;
- approve with `wt config approvals add --yes` run in `$k` as the box (the test stands in for the user);
- a finished place with the marker: kept with its branch, named with `pre-remove command failed`, `lacks "--no-hooks"`; the next tidy names it again;
- the marker removed: the next tidy removes the place, its `pre` line says the files were present, and its branch goes with crew's own "the branch was at" message;
- a post-remove line appears in the log: wt runs it in the background, so wait for it with a bounded loop (the stubbed `sleep` returns at once, so loop on a count, re-reading the log, and fail after it);
- wt not on the path (run the tidy with a PATH that lacks wt's folder): kept and named with "is not on chuck-herdr-alpha's path".

Run `tests/suite t-tidy t-merge t-fix t-bolt t-unit t-unit-free`: the last five tidy through the real wt on hookless kits.

**2.1** Briefs and docs:
- `plugin/roles/conductor.md`, the paragraph that starts "The planner may drop a unit": a worktree is also kept when the kit's remove hook fails or waits for the user's approval on the host; tell the user once which worktree, and what crew named. Clearing the cause is the user's; crew removes the worktree at its first read after.
- `plugin/roles/main-ops.md` step 5: the bolt's worktree goes through the kit's remove hooks, and is kept, named, when one fails or waits for approval; the bolt lands either way.
- `README.md`, the Teams paragraph's sentence on what keeps a worktree: each removal goes through the kit's `wt remove`, so its remove hooks run, the branch left to crew; a remove hook that fails, or that the user has not approved on that host, keeps the worktree with its branch, named on every read.
- `plugin/bin/crew`'s usage header, the `crew status` lines: "removes, through the kit's wt remove, the worktrees … whose work is over, naming one kept for uncommitted changes or a remove hook".
- `docs/architecture/_open.md`: the `plan.9` bullet goes. `docs/architecture/plan.md`, `plan.9`'s details: its last sentence ("crew removes with `git worktree remove --force` until …") goes.

`tests/t-briefs.sh` and `tests/t-docs.sh` check these texts: run `tests/suite t-briefs t-docs`.
