# Design

## Context

See proposal.md, Why. The rules this rests on: `plan.19` and its reading of 2026-10-23 ~19:30Z for signal 2026-10-23-crw-5-conductor-18f7ac7e/01 (the landing submits GitHub's head after a fetch, never the host's copy, and levels the copy first by the one write sluice's guard permits; a host copy ahead of GitHub is the split, unchanged), with its ~04:20Z reading (the level is `git fetch origin` then `git update-ref refs/heads/bolt/<bolt> <origin's revision>`, nothing of the branch changed and nothing pushed) and its reading for crw-6's signal 906b7fc5 (the split, and the landing as its way on); `plan.16` (a landing is ops's one procedure, `crew bolt submit`); `plan.18` (every read of main now, and now of a bolt, is GitHub's after a fetch); `state.5` (crew pushes nothing); `read.1` (refuse and name, never guess); `read.2`; `code.6` (no `git reset`; crew may move only a ref it owns, and this write moves nothing of the branch, which is GitHub's); `code.7` (a decision is a function of facts). Record 0026 §3 (a bolt lands only through sluice, nothing of crew's moving a bolt's branch by git) and record 0032 (the bolt's branch lives on GitHub, sluice its one writer). sluice's statement, agentplot/blueprints `design/sluice/requirements.md` clause 124 and S58 (read on that checkout's `main`, which holds dcb59c8): on a branch whose policy names a remote, the remote's revision is the branch and the host's ref is sluice's copy, levelled at each landing sluice reads, which sluice 0.36.4 does not do. sluice's guard, `crates/sluice/src/protect.rs` `hook` (read at sluice's `origin/main`): a write to a protected `refs/heads/<branch>` passes when its new value equals the branch as its route reads it (`seams.branch.read`, which for a branch on a remote fetches it, `pushed_refs.rs`) or when the route reads no branch (a creation); every other write is refused. Pages whose areas this touches: `plan.md` (`plan.py`, `kit.py`), `tests.md` (`tests/`), `docs.md` (README, the skill). `code.8` is not touched: no field the agents' views draw changes.

What the code does today, at crew's `origin/main` e78b254a:

- `landing_submitted` reads main now (`MAIN`, `main_held`), reads sluice's record of main (`SUBMISSIONS`), readies the pull request (`pull_hold(..., "live")`), then runs `SUBMIT` through `submit_ran`.
- `SUBMIT` (`main path bolt agent [id tip]`) refuses when the host has no `refs/heads/bolt/<bolt>`, cuts `<kit>/places/land-<bolt>` with `git worktree add --no-checkout` and `read-tree -m -u HEAD` when it does not stand (which writes no ref, the chore `the-landing-worktree-writes-no-bolt-ref`), takes the worktree's `HEAD` as `TIP`, and runs `wt submit main --no-wait --json --no-remove` there. So `TIP` is the host's copy, and sluice's submit pushes it as `+<head>:refs/heads/bolt/<bolt>` over GitHub's branch.
- `BOLT_SPLIT` and `kit.bolt_split` read the host's tip against the remote's copy after a fetch for `split_refusal`, which refuses a merge into a split bolt and names the landing, whose push makes the two one, as the way on. `gather.bolt_at` and `gather.bolt_read` decide where a bolt is read: GitHub's copy when the host holds it and the policy in it names a remote, else the host's branch.
- The landings card and the bolt's proof already read the bolt at GitHub's copy (`a-bolt-on-github-is-read-where-it-lives`), so the head the user answered the card on is GitHub's head as last fetched.

## Goals / Non-Goals

**Goals:**
- The head a landing submits is the bolt where it lives, read after a fetch in the landing itself.
- A host copy that lags is levelled by crew in the landing, guarded, so no hand is needed and a race refuses rather than submitting a stale head.
- A landing never drops merges either copy holds: a diverged bolt is refused.

**Non-Goals:**
- sluice's own level of its copy at each landing it reads (clause 124). That is madswan's; crew's level here is harmless once sluice makes its own, since the copy then already equals GitHub's and crew writes nothing.
- Checking the submitted head against the head the landing card was answered on. The card already reads GitHub's head, which is now what is submitted; a head that moved after the answer is record 0031's rule for the card, not this change.
- The way on for a diverged bolt. Nothing in the design makes one; it is named for the design agent (see Open Questions). Per `plan.19`'s batch-27 reading, none can arise once a bolt's first landing submission has pushed it.
- The merge refusal for a split bolt (`split_refusal`) stays as built.

## Decisions

### 1. One read of the bolt's two copies, after a fetch: `LAND_COPIES`

A new script beside `BOLT_SPLIT`, run on the team's host in the kit's main checkout with the bolt's name and the policy file (`kit.DECLARATION`). With no `origin` it prints `THERE=-` and fetches nothing. Otherwise it asks `git ls-remote --exit-code origin refs/heads/bolt/<bolt>`: exit 2 prints `THERE=-`, any other failure `READ=<git's words on one line>`; else it fetches `+refs/heads/bolt/<bolt>:refs/remotes/origin/bolt/<bolt>`, its failure `READ=`. Then it prints `OWN` (the host's `refs/heads/bolt/<bolt>` commit, or `-`), `THERE` (the fetched commit), `AT_THERE` (the policy at `THERE`, base64, or `-`, read as `BOLT_AT` reads one), `HELD` (`yes` when `OWN` is an ancestor of `THERE` or `OWN` is `-`), `AHEAD` (`yes` when `THERE` is an ancestor of `OWN`), `LACKS` (merges `OWN` holds beyond `THERE`) and `BEYOND` (merges `THERE` holds beyond `OWN`), each `-` where `OWN` is `-`.

`kit.land_copies(said, bolt)` reads it into `{own, there, remote, held, ahead, lacks, beyond, read}`, `remote` being `gather.policy_remote` of the policy at GitHub's copy for `bolt/<bolt>`; it refuses through `crew.fail`, naming what was printed, on anything else (`read.2`), and on a policy there that is not TOML, as `gather.bolt_read` does.

Why a new script and not `BOLT_SPLIT` widened: `BOLT_SPLIT` starts from the host's tip and the remote its policy names, and is read only when the host has a tip (`split_remote`); the landing starts from GitHub's copy and its own policy, as `gather.bolt_at` does, and must read a host with no copy. Widening `BOLT_SPLIT` would change the merge refusal's input for a case it never sees.

Why `origin`: `gather.bolt_at` reads a bolt on GitHub at `refs/remotes/origin/bolt/<bolt>`, and every kit's policy names `origin` (record 0032); the landing reads the bolt where every other read does.

### 2. One decision of the head: `landing_head(bolt, host, f)`

A pure function of `kit.land_copies`'s facts (`code.7`), returning `{"head", "level", "said"}` or a refusal string:

| Facts | Head submitted | Level | Said |
|---|---|---|---|
| `read` | refused: "bolt/<bolt> was not submitted: crew can't read bolt/<bolt> on GitHub: <git>" | — | — |
| `there` is `-`, or `remote` is None | the host's copy (`head` None: `SUBMIT` takes the copy as today) | no | nothing |
| `own` is `-` | `there` | make the copy at `there` | "made <host>'s copy of bolt/<bolt> at GitHub's <there>" |
| `own == there` | `there` | no | nothing |
| `held` yes (copy behind) | `there` | `own` → `there` | "levelled <host>'s copy of bolt/<bolt> from <own> to GitHub's <there>, <n> merges it lacked" |
| `ahead` yes (copy ahead) | `own` | no | "bolt/<bolt> is split: <host>'s tip <own> holds <n> merges GitHub's <there> lacks; the landing submits that tip, its push moving GitHub's branch forward" |
| neither (diverged) | refused: names both commits, `lacks` and `beyond`, and that either submission would drop merges | — | — |

The first two rows are where the bolt lives on its host (`gather.bolt_at`): a legacy bolt, a stale pre-policy push of one, or a kit with no origin. The ahead row is the split `plan.19` keeps unchanged: the bolt-teams spec says a landing is not refused for it, and `split_refusal` names the landing as its way on; that push is a fast-forward of GitHub's branch and drops nothing. The diverged row departs from the split requirement's "A landing SHALL NOT be refused for it", which this change amends: a diverged bolt is split, and landing either copy drops the other's merges, the very loss this unit ends.

Alternative: refuse the ahead row too, submitting only ever GitHub's head. Ruled out because the split's merge refusal then has no way on, and the spec keeps the split's landing.

### 3. `SUBMIT` levels the copy, guarded, before it cuts

`SUBMIT` takes two more words after the agent, before the wait-again pair: `head`, the commit to submit, empty for the host's copy as it stands; and `from`, the copy's value `LAND_COPIES` read, `-` for none. Its words become `main path bolt agent head from [id tip]`.

- When `head` is given and differs from the copy now, it runs `git update-ref -m "crew: level to GitHub's bolt/<bolt> for its landing" refs/heads/bolt/<bolt> <head> <from, or 40 zeros for none>`, before the worktree is cut. The old value makes git refuse when the copy moved since the read; sluice's guard refuses when GitHub's branch moved since the fetch. Either way it exits 2 with git's or the guard's words on standard error, nothing cut and nothing submitted.
- The host-has-no-branch refusal then reads after the level, so a made copy passes it.
- When the landing's worktree already stood and the level moved the copy, its files are brought along with `git -C "$path" read-tree -m -u <from> HEAD`, which writes no ref; git refusing, for local changes, exits 2 in git's words.
- After the cut, when `head` is given and the worktree's `HEAD` is not it, it exits 2 naming both, nothing submitted.
- It prints `LEVEL=<from>` when it wrote the copy, else `LEVEL=`, beside its other assignments; `submit_ran` requires it.
- Given a submission to wait on again (`id tip`), `head` and `from` are empty and nothing is levelled: the earlier submission's push already made GitHub's branch its tip.

Why `update-ref` with the old value and not `git branch -f` or `fetch` into `refs/heads`: `branch -f` refuses a branch checked out in a worktree and moves nothing more; a fetch into `refs/heads/bolt/<bolt>` is the same transaction with no old-value guard. `update-ref` is the command `plan.19` names.

Why this is no move of the bolt's branch (`code.6`, record 0026 §3, `state.5`): the branch is GitHub's (`plan.19`, clause 124); the write sets sluice's copy to the value the branch already has, the one write the guard passes, and pushes nothing.

### 4. `landing_submitted` reads and decides before it readies the pull request

After main now is read and before `SUBMISSIONS` and `pull_hold`, `landing_submitted` runs `LAND_COPIES` through `crew.on_machine`, reads it with `kit.land_copies`, and decides with `landing_head`. A refusal returns `{bolt, t, refused}` with no `attempted`, so the pull request is left as it was (a draft stays a draft) and the row is held at the head crew read, as any landing refused before submission. Otherwise it prints `said` when there is one and passes `head` and `own` to `submit_ran`, which passes them to `SUBMIT`. `landing_ended`'s wait-again call passes empty words for both. The landing's `bolt.submit` record keeps `Head=TIP`, now GitHub's head.

## Risks / Trade-offs

- [GitHub's branch moves between crew's fetch and the guard's] → the guard refuses the level, nothing is submitted, the command says so; ops runs the landing again on the same word, since nothing landed.
- [sluice later levels its copy itself] → the copy already equals GitHub's, the decision levels nothing, and the command is as before.
- [The guard's own fetch fails while crew's succeeded] → the guard refuses in sluice's words; nothing is submitted.
- [A landing worktree from an earlier attempt holds uncommitted files] → `read-tree -m -u` refuses in git's words, nothing submitted; the place is named as today's tidy names it.
- [A diverged bolt has no way on in crew] → refused and named, never landed short; the design agent is asked for the way on.

## Migration Plan

None. A bolt whose copy the user levelled by hand meanwhile reads level and lands as before.

## After deploy

None: every case is proven by the logic and contract tiers against a bare stand-in for GitHub and a stand-in for sluice's guard, and end to end by `t-journey-land`; the guard's behaviour on an equal value is read from sluice's source above, and a stand-in that judges as it does is what the contract case runs under.

## Open Questions

- The way on for a bolt whose host copy and GitHub copy have diverged: refused here, never landed short. For the design agent; it changes nothing built here.

## Task notes

**1.1** `plugin/lib/plan.py`: `LAND_COPIES` beside `BOLT_SPLIT`, its comment in the style of the scripts around it, saying what it prints. `plugin/lib/kit.py`: `land_copies(said, bolt)` beside `bolt_split`, using `said_of`, a 40-to-64-hex check as `bolt_split` has, and `gather.policy_remote`. Cases in `tests/py/test_kit.py`: each shape `LAND_COPIES` prints read (no origin, absent on GitHub, `READ`, behind, level, ahead, diverged, no host copy, a policy naming no remote, a policy that is not TOML), and output that is none of them refused naming it.

**1.2** `plugin/lib/plan.py`: `landing_head(bolt, host, f)`, beside `split_refusal`, its docstring saying the table in Decision 2 in sentences. Cases in `tests/py/test_landing.py`, one per row, each naming its bolt-teams scenario in its docstring; the refusals' words asserted whole.

**2.1** `plugin/lib/plan.py` `SUBMIT` and its comment block: the two words, the guarded `update-ref`, the made copy, the standing worktree's `read-tree -m -u <from> HEAD`, the head check, `LEVEL`. `submit_ran` gains `head` and `own` (default empty, for the wait-again call) and requires `LEVEL`. Contract cases in `tests/contract/test_git.py`, using `kit_with_github` and `landing`, the latter taking `head` and `from` (or computing them through `LAND_COPIES` and `landing_head` as `landing_submitted` does), under the stand-in guard of `test_a_landings_worktree_is_cut_on_a_split_legacy_bolt_writing_no_bolt_ref`, which already refuses any write of `refs/heads/bolt/b` differing from `refs/remotes/origin/bolt/b`: a copy two merges behind GitHub's is levelled, the guard log showing the one write at GitHub's value, the worktree at GitHub's head, and GitHub's main after the stand-in sluice holds both merges; a host with no copy gets one at GitHub's head; GitHub moved after the read (the bare repo advanced after `LAND_COPIES` ran, the stand-in guard reading the new value after its own fetch) refuses with nothing cut; an ahead legacy copy is submitted at its tip with no write; a standing landing worktree is brought to the new head; the wait-again path writes nothing. Update the existing landing contract cases for `SUBMIT`'s new words.

**2.2** `landing_submitted`: the read and decision placed after `main_held` and before `SUBMISSIONS`, as Decision 4 says; `landing_ended`'s `submit_ran(..., str(n), tip)` call passes empty `head` and `own`. Logic cases in `tests/py/test_landing.py` or `tests/py/test_bolt_commands.py`, on a stand-in `crew.on_machine` as the existing `bolt_submit` cases use: a diverged bolt is refused before `pull_hold` is called and `SUBMIT` never runs; a lagging copy's levelling line is printed and `SUBMIT` is given GitHub's head and the copy's value.

**3.1** `tests/t-journey-land.sh`: the stub world's bolt landed with its host copy behind GitHub's (the stub sluice's switch from `a-bolt-on-github-is-read-where-it-lives` that lands a merge on GitHub and leaves the host's copy behind), and `crew bolt submit` landing GitHub's head, main holding the merge the copy lacked. Run `tests/moon-tasks` and commit `tests/moon.yml` when a test's reads change.

**3.2** `README.md` (the landing paragraph, where it says the command makes a short-lived worktree on the bolt's branch) and `plugin/skills/crew/SKILL.md` (the paragraph that says "a landing pushes nothing and levels no host"): the landing fetches the bolt, submits GitHub's head, levels the host's copy first and says so, refuses a diverged bolt; "levels no host's checkout". `tests/t-docs.sh` proves the usage agrees.
