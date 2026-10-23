# A landing submits the bolt where it lives

## Why

When ops lands a bolt, crew cuts the landing's worktree from the host's own `bolt/<bolt>`, which for a bolt on GitHub is only sluice's copy and lags GitHub's branch, since sluice 0.36.4 never levels it. Submitting that worktree pushes the stale copy over GitHub's branch and lands it, dropping every merge the copy lacks. On 2026-10-23 wldn's `a-standing-class-takes-a-release-by-break-glass` landed on switchboard-kit's main at db8bc25 from the host's 522b714 while GitHub's branch stood at 8ec587a: main lacked the unit's change and the bolt could not close (signal 2026-10-23-crw-5-conductor-18f7ac7e/01). plan.19's reading of that signal rules it: the landing submits the bolt where it lives, GitHub's head after a fetch, and first levels the host's copy to that head by the one write sluice's guard permits.

## What Changes

- **The landing reads the bolt on GitHub first.** Before it cuts anything, `crew bolt submit` fetches the bolt's branch from the kit's origin on the team's host and reads where the bolt lives, as every other read of a bolt does since `a-bolt-on-github-is-read-where-it-lives`: GitHub's copy when GitHub holds the branch and the policy in it names a remote for it, else the host's own branch.
- **It submits GitHub's head.** For a bolt on GitHub whose host copy is level with GitHub's, behind it, or missing, the head submitted is GitHub's. When the host's copy differs, crew first sets it to GitHub's head with `git update-ref`, guarded by the value it read. sluice's guard lets that write through, since it sets the branch to the value its route already reads. The landing's worktree is then cut as today, holds GitHub's head, and the submission's push moves nothing on GitHub. The command says it levelled the copy, from which commit to which.
- **A copy ahead of GitHub is the split bolt, unchanged.** A legacy bolt whose host tip holds merges GitHub's copy lacks, while GitHub's copy holds nothing the host lacks, is the split `a-split-legacy-bolt-takes-no-merge-once-its-tip-names-origin` refuses merges into. Its landing still submits the host's tip, as the split's refusal says, and that push moves GitHub's branch forward, dropping nothing.
- **A copy that has diverged is refused.** When each side holds merges the other lacks, either submission would drop merges. crew submits nothing and levels nothing, and names both commits and what each lacks.
- **A fetch that fails submits nothing.** crew names git's words and makes no worktree (`read.1`).
- **Unchanged:** a bolt that lives on its host (no origin, GitHub lacks the branch, or GitHub's copy names no remote) is submitted from the host's branch as today. A wait on an earlier submission (`SUBMIT` run again with a submission's number) levels nothing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a bolt lands from its head where it lives, with the host's copy levelled to GitHub's head first. A landing levels no host's checkout but may level the host's copy of the bolt's branch. A split bolt whose two copies have diverged is refused at its landing.

## Impact

- `plugin/lib/plan.py`: a read on the team's host of the bolt's two copies after a fetch (a new script beside `BOLT_SPLIT`); a pure decision of the head a landing submits and whether it levels the copy; `landing_submitted` running both before `SUBMIT`; `SUBMIT` given the head and the copy's value read, levelling with a guarded `update-ref`, bringing an existing landing worktree's files along, and refusing when the worktree's head is not the head chosen; `submit_ran` and `landing_ended` passing the new words.
- `plugin/lib/kit.py`: the parser of that read, beside `bolt_split`.
- Tests: logic cases for the decision and the parser; contract cases running the read and `SUBMIT` against a bare "GitHub" under a stand-in for sluice's guard; `t-journey-land` where the landing's wiring changes.
- `README.md` and the crew skill say the landing submits GitHub's head and levels the host's copy first (`docs.2`).
- Once this lands, a landing needs no hand-levelling by the user, which plan.19 asks for until then.

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
tests/py/test_landing.py
tests/py/test_kit.py
tests/py/test_bolt_commands.py
tests/contract/test_git.py
tests/t-journey-land.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
```
