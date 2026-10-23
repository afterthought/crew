# Design

## Context

See proposal.md, Why. The rule is `plan.19`, as read on 2026-10-23 for crw-6's signal: a legacy bolt split between the host's tip and a stale copy on GitHub takes no merge once its tip names origin, its next move is its landing, and crew refuses a submission into a bolt so split, naming the split and the landing. Record 0032's amendment of 2026-10-22 says why the split drops work: sluice routes a branch by the policy at the branch's own local revision, so once a legacy bolt's tip names `origin`, sluice reads the bolt on GitHub, where it is absent (sluice refuses) or stands at an older push (sluice forms the merge there). `roles.3` asks for the check in crew.

What crew has today:

- `BOLT_AT` (`plan.py`) prints the host's `bolt/<bolt>` (`LOCAL`), the tracking ref `origin/bolt/<bolt>` as last fetched (`TRACKED`), and the policy at each; `kit.bolt_lives` reads from it the remote the policy at the host's own branch names, or `None`. `BOLT_LIVES` runs it in the kit's main checkout.
- A merge starts in three places, each handing the agent `merge_command(bolt)`, `sluice submit bolt/<bolt> --no-wait --json`: `run_check`'s merge stage for a unit, `chore_check`'s for a chore, and `fix_cmd`'s `merge` mode. Each is already gated by refusals that run before it (`landing_refusal`, `merge_carries`, `own_place`).
- `bolt_submit`, the landing, submits from `<kit>/places/land-<bolt>` on `bolt/<bolt>`; sluice pushes that head to GitHub under the branch's name (`plan.19`'s reading of 2026-10-22), which is what makes a split bolt whole.

Pages whose areas this touches: `plan.md` (`plugin/lib/plan.py`, `plugin/lib/kit.py`), `tests.md` (`tests/`). Rules relied on: `plan.19`, `plan.18` (a decision of the moment fetches once per command), `roles.3`, `read.1`, `read.2`, `code.2`, `code.7`, `state.5`, `teams.5` (a merge is a submission to sluice).

## Goals / Non-Goals

**Goals:** no merge into a bolt is handed to an agent while the bolt is split; the refusal says what is split and that the landing is the way on; what crew can't read refuses.

**Non-Goals:**

- The landing is not checked; it is the remedy.
- A bolt GitHub has no copy of is left to sluice, which refuses the submission itself and drops nothing.
- Where a new place of such a bolt is cut from: `kit.place_base` follows `bolt_lives`, which, once the tip names `origin`, cuts from `origin/bolt/<bolt>`, the stale copy. That is a separate hazard, outside this change's intent (see the final message to the planner).
- A merge stage already running, or an agent submitting by hand: crew refuses at the stage's start and at `crew fix merge`, the points it owns.
- Nothing of sluice's: forming a merge on a remote tip its own records' last landing does not reach is sluice's finding (`plan.19`).

## Decisions

### 1. Split means the remote's copy lacks the host's tip

The bolt is split when the host has its own `bolt/<bolt>`, the policy at that tip names a remote, the remote has `bolt/<bolt>`, and the host's tip is not an ancestor of it. That is exactly when a merge sluice forms on the remote's copy leaves out work the host holds. Equal, or the remote ahead (merges sluice landed there for a bolt on GitHub whose local ref lags), is not split: nothing would be dropped. This also covers a bolt given on GitHub whose host's branch somehow moved alone, which the refusal rightly holds.

Considered: "the two commits differ". Rejected: a bolt on GitHub whose host ref lags GitHub's after sluice lands there would be refused on every merge.

### 2. Read the remote at the merge's start, fetching once

The remote's copy is a fact of the moment, so the read fetches once per command (`plan.18`), not from the tracking ref as last fetched: the box's older push or a refused landing's pull request may have moved it since. One script, `BOLT_SPLIT`, runs on the team's host in the kit's main checkout only after `BOLT_LIVES` has said the host's tip names a remote, so a legacy bolt whose tip names none fetches nothing. It asks `git ls-remote --exit-code <remote> refs/heads/bolt/<bolt>` first (exit 2: absent), then fetches that ref into `refs/remotes/<remote>/bolt/<bolt>`, then answers whether the host's tip is held and how many merges the host has beyond the remote's copy. A failure of either git command is printed with git's words.

Considered: reading `TRACKED` from `BOLT_AT` as last fetched. Rejected: the signal's split came from a push the host had not fetched in the sense that matters, and a stale read here lets the drop through.

### 3. A pure decision, three thin call sites

`kit.split_remote(said, bolt)` decides from `BOLT_AT`'s output which remote to read, or `None` when the host has no `bolt/<bolt>` of its own or its tip names no remote; `split_refusal(kind, name, bolt, host, remote, facts)` in `plan.py` takes the parsed facts and returns the refusal's words or `None` (`code.7`); `kit.bolt_split(said, bolt)` parses `BOLT_SPLIT`'s output, refusing what it can't read (`read.2`). `bolt_split_check(fleet, t, bolt)` in `plan.py` runs the reads around them and returns `(remote, facts)` or `None` when there is nothing to check. The unit's and chore's merge stages call it after `landing_refusal` and before the place is made again or `merge_carries` reads the branch; `fix_cmd`'s merge mode calls it after `own_place`, inside its `try`, so the refusal is recorded as `fix.merge` like the others. Refused through `fail` (`code.2`).

### 4. The words

Split: `bolt/<bolt> is split: its tip on <host>, <local7>, names <remote> for it, so sluice would form <kind> <name>'s merge on <remote>'s bolt/<bolt> at <there7>, which lacks <n> merge(s) <host> holds, and drop them. The bolt takes no merge until it lands: its landing (crew bolt submit <bolt>, main-level ops's on the user's word) pushes <host>'s tip to <remote> and makes the two one`. With `n` of 0 (the host's tip holds commits but no merges beyond), "which lacks <host>'s tip" instead of the count.

Unreadable: `crew can't tell whether bolt/<bolt> is split, so <kind> <name>'s merge waits: <git's words>`.

## Risks / Trade-offs

- [A fetch at every merge start costs a round trip to GitHub] → only for a bolt whose host tip names a remote; one fetch per command, as `plan.18` allows for decisions of the moment.
- [GitHub unreachable holds every merge of such a bolt] → that is `read.1`: a merge crew can't judge safe is not handed out, and the words name why.
- [A split bolt's units wait until the landing] → that is the rule; the landing is the user's word through main-level ops, and the refusal names it.

## After deploy

None: the refusal is code, proved in the logic and contract tiers, and needs no step on a live host.

## Task notes

**1.1** In `plan.py`, beside `BOLT_LIVES`, add `BOLT_SPLIT` (args: main checkout, bolt, remote): `cd` into the main checkout; `l` the host's `refs/heads/bolt/$bolt` commit; `git ls-remote --exit-code "$remote" "refs/heads/bolt/$bolt"` — exit 2 prints `THERE=-` and stops; another non-zero prints `READ=<git's words on one line>` and stops; then `git fetch -q "$remote" "+refs/heads/bolt/$bolt:refs/remotes/$remote/bolt/$bolt"`, a failure printed as `READ=` likewise; then `LOCAL=$l`, `THERE=<the fetched commit>`, `HELD=yes|no` from `git merge-base --is-ancestor "$l" "$there"`, `MERGES=$(git rev-list --count --merges "$there..$l")`. In `kit.py` add `bolt_split(said, bolt)` returning a dict `{"local", "there", "held", "merges", "read"}` from those lines (`said_of`), refused through `crew.fail` when neither `READ` nor `THERE` is there, or when `THERE` names a commit and `LOCAL`, `HELD` or `MERGES` is missing or malformed (`read.2`).

**1.2** In `plan.py`, `split_refusal(kind, name, bolt, host, remote, f)`: `None` when `f["there"] == "-"` or `f["held"] == "yes"`; Decision 4's unreadable words when `f["read"]`; else Decision 4's split words. Cases in `tests/py/test_bolt_commands.py`, a class `TestSplitBolt` beside `TestQueuedLanding`: split with two merges (exact words), split with the tip lacking but no merges, a chore and a fix named, held, equal (`held` yes), absent, unreadable.

**1.3** In `kit.py`, `split_remote(said, bolt)`: `None` when `said_of(said)["LOCAL"]` is `-`, else `bolt_lives(said, bolt)`. `tests/py/test_kit.py`, beside `bolt_lives`'s cases and with its `at` helper: no host branch gives `None`; a host tip whose policy names `origin` gives `"origin"`; one naming no remote gives `None`, whatever the tracking ref's policy says. And `bolt_split` reads a split, a held, an absent and an unreadable output, and refuses an output that is none of these.

**1.4** `tests/contract/test_git.py`: with a scratch repository and a bare remote, run `plan.BOLT_SPLIT` with `bash -c` as crew does: the host's `bolt/b` two merges ahead of the remote's prints `HELD=no` and `MERGES=2`; the remote at the host's tip or ahead of it prints `HELD=yes`; no `bolt/b` on the remote prints `THERE=-` (pinning `ls-remote --exit-code`'s exit 2); a remote URL that does not resolve prints `READ=`. Each case names `split_refusal` as what assumes it.

**2.1** `bolt_split_check(fleet, t, bolt)`: run `BOLT_LIVES` on `t["machine"]` (`host_run`), return `None` when `kit.split_remote` gives none; else run `BOLT_SPLIT` with that remote and return `(remote, kit.bolt_split(...))`. In `run_check`'s merge branch and `chore_check`'s, before `make_place` and `merge_carries`, and in `fix_cmd`'s merge mode after `own_place`: when it gives facts, `why = split_refusal(...)`, `not why or fail(why)`. The kind is "unit", "chore" or "fix", the name the unit's, chore's or fix's. The decisions are proved by 1.2 and 1.3; the wiring, by `tests/suite --affected` running every end-to-end test that starts a merge, none of whose bolts is split, so each must still merge.
