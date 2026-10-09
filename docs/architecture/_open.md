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
- `plan.14`: a landing records its sha and a deploy is one act over the landings since the last, every after-deploy step on its record with doer and state, the user's a rail row with a card (ADR 0012, `a-deploy-is-approved-and-recorded-through-crew` as amended); `crew bolt land` records no sha, main-ops deploys at every landing, and `construct.md` knows one proof list.
- ADR 0006: a change archived at its merge (`a-merged-change-is-archived`); the coder brief has no archive step and ops reads the proof from the open change.
- ADR 0005: cards (`the-rail-is-answered-through-cards`, after the rail).
- `plan.14`, `roles.2` as amended: `deploy.*` run-record entries, the deploy's approval, the rail row and held card for a `manual` environment, the board's Operation lane rows per environment (`a-deploy-is-approved-and-recorded-through-crew`), and the lineage page's deploys view (`the-page-shows-the-deploys`, record 0010); the `main-level` spec and `main-ops.md` step 4 still have main-ops deploying.
- Record 0010's board view: the page draws the lanes in the mockup's forms, side by side or stacked, narrowed to a team, with every partition one step away (`the-page-shows-the-board`, after the text board and the page); nothing draws lanes today.
- `plan.8`, `teams.5` as amended (ADR 0015): a fix that carries the bolt onto main becomes its head by crew's move, the bolt's checks run and ops proves it again (`a-fix-carries-the-bolt-onto-main`); the fix merge only merges, the main-ops brief sends a landing's conflict to a fix that cannot carry it, and the user moves the branch by hand.
- `docs.6`: what a change holds, in `construct.md` and `openspec/config.yaml` (`a-change-holds-what-is-true-and-what-is-proved`).
- `signals.6`: a program's captures landed on the flywheel's branch (`machine-captures-land-on-the-flywheels-branch`, after `daily-pass-lands-through-crew`).
- `signals.7`: curation on a cadence (`curation-runs-on-a-cadence`, after `curate-into-agenda`).
- `briefs.9` as amended: a card's words carry the document's substance with the link first (`a-card-reads-whole-at-a-glance`); `cards_how` puts the link only as an artifact and the conductor's brief asks for two or three sentences.
- `briefs.11`: a team's cards are its conductor's, and crew refuses a crew agent's card or area under any other key (`a-teams-cards-are-its-conductors`); `ops.md` has no card rule, the landing card asks no step, and the hook records any key.
- `plan.6`, `plan.13`, `teams.5`, `teams.12`, `teams.13`, `teams.14`, `briefs.1`, `briefs.2`, `briefs.4`, `briefs.9`, `briefs.12` as record 0014 has them: changes written in waves, a dependent built on its After units' work and merged after them, no review gate, Touches read and checked, conflicts forecast and reaching the later unit, the settle stage, the partition's batch review and the landing guard, `wt submit` where a kit opts into sluice (`concurrent-units`, after unit-amendments is archived; the batch setting in swancloud's `lib/crew-teams.nix`); `run_check` holds construct for `After` merges and code for `crew unit approve`, and `conductor.md` builds overlapping units one after the other.
- `briefs.10`: the operator agent as the partition's front door, in every roster (`a-partitions-operator-agent-is-its-front-door`).

## Code against a rule

- `tests.6`: the brief fixes 21d82af, ec593d5, 63bab58, e3d75cb and 902336e added no phrase to `t-briefs.sh`. A chore.
- `teams.6`: `openspec/config.yaml` says every agent runs on Opus 5.5; the design agent and planner run on Fable 5.1. Fixed with this file. README's Roles table names models as documentation of the frontmatter, which the `agent-models` spec's "nowhere else" should allow; amend the spec at its next delta.
- Specs lagging built code, to fix at archive: `bolt-teams` (fix naming `fix/<bolt>/<name>` at `places/fix-<bolt>--<name>`; the git tab only on a Mac; a slot freed when its unit leaves the bolt); `main-level` and `bolt-plan` (an agent's signals on the flywheel's branch; "one plan per blueprints repo"); `plan-proposals` (`unit amend` as a proposable command); `run-record` (a move's commit is the state branch's); `operator-agent` (the operator writes the teams file on the user's word).
- Five changes built and landed but not archived, each an archive chore: a-decision-is-shown-whole, fix-place-names-its-bolt, rulings-rest-on-readings-and-intents-name-outcomes, what-waits-on-the-user-is-one-list, worktrees-go-with-their-work. checked-capture (12/16) and unit-amendments (10/12) are nearly there.
- Stale comments: `plan.rec`'s header ("Written only by `crew bolt` and `crew unit`"; approve and `state init` write it too); `transcript.py`'s docstring (it reads `uuid`, `timestamp` and `tool_result`); `gather.py`'s docstring (with `sites` it also runs `devurl` and `portless`).
- The findings-to-design exploration (`brief.md`, `proposal.md`, `roadmap.md`) is partly stale: review in plannotator, the transcript canary, and the roadmap covers only its own nine changes; each now says in its first line what it is.
