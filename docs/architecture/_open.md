# Open items

What is still open now that every page is written. A working file: an item leaves when it is decided or fixed, and the file is deleted when it is empty.

## Decisions waiting

- **Where meeting signals live** (daily-pass-through-crew, decision D7): the blueprints, or the flywheel's branch with an agent's signals.
- **Who is told about a finding outside a bolt**: the conductor and main-ops briefs say the planner, the ops brief the conductor, the planner brief the design agent; curation-and-agenda, approved and placed, settles it as "a noticing agent captures and tells nobody" when it lands.
- **`gitenv()` for every git call**: used for the cache and the tidy, not for `stage_ends` or `gather.py`.

## Accepted, not built

Each is a queued or placed unit; the rule stands and the code catches up.

- `plan.10`: a drop keeps a branch with unmerged patches, judged by `git cherry`; `tidy()` deletes with `git branch -D` and `gather.fix_merged` judges by ancestry (`a-drop-keeps-unmerged-work`, fix-places).
- `plan.11`: the chore kind (`chores-beside-units-and-fixes`, curation-and-holds).
- `plan.12`: one kit read and one fetch per command (`a-command-reads-the-kits-once`).
- `teams.4`: a stage ends at its deliverable; `crew unit wait` ends at herdr's settle (`a-stage-ends-at-its-deliverable`).
- `tests.5`: the merge gate and the moon tasks (`a-merge-is-gated-by-the-suite`, `the-suite-runs-as-moon-tasks`); crew has no `.config/wt.toml` and no moon, while the coder brief already says `wt merge` checks the branch.
- `briefs.7`: the glyph list (`test-results-are-a-glyph-list`).
- ADR 0006: a change archived at its merge (`a-merged-change-is-archived`); the coder brief has no archive step and ops reads the proof from the open change.
- ADR 0005: cards (`the-rail-is-answered-through-cards`, after the rail).

## Code against a rule

- `record.3`: a refused proposal's entry embeds its whole `Do` line, intent included (`plan.py` 1527–1534, 3047–3053); only verify's refusal strips typed text through `recorded`. A fix.
- `plan.1`: the `runs/<host>/*.rec` files carried in a write are added after the `recfix` loop and never checked, and `signals/*.md` never are. A fix.
- `tests.6`: the brief fixes 21d82af, ec593d5, 63bab58, e3d75cb and 902336e added no phrase to `t-briefs.sh`. A chore.
- `teams.6`: `openspec/config.yaml` says every agent runs on Opus 5.5; the design agent and planner run on Fable 5.1. Fixed with this file. README's Roles table names models as documentation of the frontmatter, which the `agent-models` spec's "nowhere else" should allow; amend the spec at its next delta.
- Specs lagging built code, to fix at archive: `bolt-teams` (fix naming `fix/<bolt>/<name>` at `places/fix-<bolt>--<name>`; the git tab only on a Mac; a slot freed when its unit leaves the bolt); `main-level` and `bolt-plan` (an agent's signals on the flywheel's branch; "one plan per blueprints repo"); `plan-proposals` (`unit amend` as a proposable command); `run-record` (a move's commit is the state branch's); `operator-agent` (the operator writes the teams file on the user's word).
- Five changes built and landed but not archived, each an archive chore: a-decision-is-shown-whole, fix-place-names-its-bolt, rulings-rest-on-readings-and-intents-name-outcomes, what-waits-on-the-user-is-one-list, worktrees-go-with-their-work. checked-capture (12/16) and unit-amendments (10/12) are nearly there.
- Stale comments: `plan.rec`'s header ("Written only by `crew bolt` and `crew unit`"; approve and `state init` write it too); `transcript.py`'s docstring (it reads `uuid`, `timestamp` and `tool_result`); `gather.py`'s docstring (with `sites` it also runs `devurl` and `portless`); `crew.py`'s usage omits `greet`.
- The findings-to-design exploration (`brief.md`, `proposal.md`, `roadmap.md`) is partly stale: review in plannotator, the transcript canary, and the roadmap covers only its own nine changes; each now says in its first line what it is.
