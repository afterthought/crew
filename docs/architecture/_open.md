# Open items

What is still open now that every page is written. A working file: an item leaves when it is decided or fixed, and the file is deleted when it is empty.

## Decisions waiting

- **Where meeting signals live** (daily-pass-through-crew, decision D7): the blueprints, or the flywheel's branch with an agent's signals.
- **Who is told about a finding outside a bolt**: the conductor and main-ops briefs say the planner, the ops brief the conductor, the planner brief the design agent; curation-and-agenda, approved and placed, settles it as "a noticing agent captures and tells nobody" when it lands.
- **`docs.7`, proposed 2026-10-11 on the user's card**: the design pages have one writer and a unit never edits them; six landings since the 9th conflicted on this page. Once accepted: `a-unit-never-edits-the-design-pages`.
- **`gitenv()` for every git call**: used for the cache and the tidy, not for `stage_ends` or `gather.py`.

- **What minted mac-studio's new Pending You connection** after the headers helper judged the old sign-in stale (2026-10-10 04:57Z) and the credential file was cleared (09:05Z), orphaning every card posted before: unread (ADR 0005 as amended 2026-10-11); swancloud's doctor row will show the next change the day it happens.

## Accepted, not built

Each is a queued or placed unit; the rule stands and the code catches up.

- `plan.10`: a drop keeps a branch with unmerged patches, judged by `git cherry`; `tidy()` deletes with `git branch -D` and `gather.fix_merged` judges by ancestry (`a-drop-keeps-unmerged-work`, fix-places).
- `plan.11`: the chore kind (`chores-beside-units-and-fixes`, curation-and-holds).
- `plan.14`: a landing records its sha and a deploy is one act over the landings since the last, every after-deploy step on its record with doer and state, the user's a rail row with a card (ADR 0012, `a-deploy-is-approved-and-recorded-through-crew` as amended); `crew bolt land` records no sha, main-ops deploys at every landing, and `construct.md` knows one proof list.
- ADR 0006: a change archived at its merge (`a-merged-change-is-archived`); the coder brief has no archive step and ops reads the proof from the open change.
- `plan.14`, `roles.2` as amended: `deploy.*` run-record entries, the deploy's approval, the rail row and held card for a `manual` environment, the board's Operation lane rows per environment (`a-deploy-is-approved-and-recorded-through-crew`), and the lineage page's deploys view (`the-page-shows-the-deploys`, record 0010); the `main-level` spec and `main-ops.md` step 4 still have main-ops deploying.
- Record 0010's board view: the page draws the lanes in the mockup's forms, side by side or stacked, narrowed to a team, with every partition one step away (`the-page-shows-the-board`, after the text board and the page); `crew board` draws them as text.
- `plan.8`, `teams.5` as restated 2026-10-10: the carrying fix judged by its commits, count, order, message and author, not by `git range-diff`'s pairing (`a-carrying-fix-is-judged-by-its-commits`); `plan _carry` judges by range-diff at creation factor 60 and misses a commit whose context main rewrote.
- `plan.15`: an approved amendment runs construct again by its own act and a restarted conductor picks it up (`an-amendment-runs-construct-again-itself`); today the conductor runs it on a notice it can lose.
- `briefs.14`, ADR 0004 as amended: sources govern over an intent's mechanism; no brief says which governs. ADR 0016, a spike beside the design agent, is back to proposed on 2026-10-11 and its bolt `a-spike-runs-beside-the-design-agent` held until the elaboration record is settled with the user.
- ADR 0005 as amended 2026-10-10, the image clause: a screenshot on a card is an uploaded image artifact, never a path (`an-image-on-a-card-is-uploaded`); the card discipline says nothing of images.
- ADR 0005 as amended 2026-10-10: a card's session ended by crew on every rail read once its card is closed or its row gone (`a-cards-session-ends-with-its-card`); today only the owner's hook ends it, and eleven idle servers ran on mac-studio.
- `teams.15`: a stage's prompt taken or sent again, never left typed (`a-stages-prompt-is-taken-or-sent-again`); `run_stage` types and reads nothing back.
- `tests.8`: tests wait on conditions with limits that hold under load (`tests-hold-under-a-loaded-host`); `t-stage-ends` and `t-amend` sleep and time out, and redden under a load of 247.
- `tests.9`: a host's suites bounded by its cores across teams (`suites-on-one-host-share-its-cores`); today each team's moon runs every test at once and two teams loaded mac-studio to 247.
- ADR 0017: `crew usage`, token spend by partition, team, role, agent and model from crew's sessions and the transcripts (`crew-usage-sums-tokens-by-team-role-and-agent`); nothing reports spend today.
- ADR 0018, `plan.3` and `briefs.13` as amended: a proposal's card drawn and in text with a choice per new unit, and the approval of the kept subset (`a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`); today the card is prose and the approval is all or nothing.
- `docs.6`: what a change holds, in `construct.md` and `openspec/config.yaml` (`a-change-holds-what-is-true-and-what-is-proved`).
- `signals.6`: a program's captures landed on the flywheel's branch (`machine-captures-land-on-the-flywheels-branch`, after `daily-pass-lands-through-crew`).
- `signals.7`: curation on a cadence (`curation-runs-on-a-cadence`, after `curate-into-agenda`).
- `plan.6`, `plan.13`, `teams.5`, `teams.12`, `teams.13`, `teams.14`, `briefs.1`, `briefs.2`, `briefs.4`, `briefs.9`, `briefs.12` as record 0014 has them: changes written in waves, a dependent built on its After units' work and merged after them, no review gate, Touches read and checked, conflicts forecast and reaching the later unit, the settle stage, the partition's batch review and the landing guard, `wt submit` where a kit opts into sluice (`units-build-at-once-and-are-reviewed-in-batches`, after unit-amendments is archived; the batch setting in swancloud's `lib/crew-teams.nix`); `run_check` holds construct for `After` merges and code for `crew unit approve`, and `conductor.md` builds overlapping units one after the other.
- ADR 0005 as amended 2026-10-09: a conductor whose session has lost the tools is started afresh on its word and posts its card (`a-card-reaches-the-user-when-the-tools-drop`); today such a row has no card and the user is told only by notification. The landing key carries the bolt's head (`a-landing-card-is-the-heads`); today `land/<bolt>` returns the failed landing's answered card.
- `briefs.13` as amended 2026-10-11: a batch card with no words question, its notes the sessions' annotations and the card's own note (`a-batch-cards-notes-are-its-note-and-its-sessions`); the batch card crw-3's unit built asks one (`planner.md` *Batches*, step 2).
- ADR 0005 as amended 2026-10-11, the sign-in clause: a row's card its owner can no longer reach is posted again with the older copy named dead (`a-card-lost-to-its-owner-is-posted-again`); the card discipline says nothing of a lost card today.
- `briefs.15`: a record proposed on one card and accepted on the user's yes (`a-record-is-accepted-on-the-users-yes`); `design.md` has the design agent record and commit as settled.
- `briefs.10`: the operator agent as the partition's front door, in every roster (`a-partitions-operator-agent-is-its-front-door`).

## Code against a rule

- `briefs.13`, ADR 0005 as amended 2026-10-11: the card hook's landing form demands `highStakes`, which Pending You refuses on an approval ("Approve requests give their risk in approve.risk."), so no landing card posts; `conductor.md` *Cards*, `tests/t-cards.sh` and `tests/t-briefs.sh` say the flag, and `rail-cards`'s scenario "A landing card not marked high stakes" names it. The form is an `approve` of risk high, not reversible, with why, and the check reads the risk (`a-landing-cards-stakes-are-its-approvals-risk`, a bolt of its own first among the planned, landed by ops on the user's word in a pane; signal 2026-10-11-crw-2-conductor-27bc8685/01).
- `briefs.11` as amended 2026-10-11: the card hook refuses every key but a rail row's, so a question with no row cannot go on a card; a conductor's card for any question of its team, under its own key, and crew refusing only a second card (`any-question-for-the-user-gets-a-card`, the user's word, signal 2026-10-11-swancloud-operator-mac-studio-6765d67e/01).
- `tests.6`: the brief fixes 21d82af, ec593d5, 63bab58, e3d75cb and 902336e added no phrase to `t-briefs.sh`. A chore.
- `teams.6`: `openspec/config.yaml` says every agent runs on Opus 5.5; the design agent and planner run on Fable 5.1. Fixed with this file. README's Roles table names models as documentation of the frontmatter, which the `agent-models` spec's "nowhere else" should allow; amend the spec at its next delta.
- Specs lagging built code, to fix at archive: `bolt-teams` (fix naming `fix/<bolt>/<name>` at `places/fix-<bolt>--<name>`; the git tab only on a Mac; a slot freed when its unit leaves the bolt); `main-level` and `bolt-plan` (an agent's signals on the flywheel's branch; "one plan per blueprints repo"); `plan-proposals` (`unit amend` as a proposable command); `run-record` (a move's commit is the state branch's); `operator-agent` (the operator writes the teams file on the user's word).
- Five changes built and landed but not archived, each an archive chore: a-decision-is-shown-whole, fix-place-names-its-bolt, rulings-rest-on-readings-and-intents-name-outcomes, what-waits-on-the-user-is-one-list, worktrees-go-with-their-work. checked-capture (12/16) and unit-amendments (10/12) are nearly there.
- Stale comments: `plan.rec`'s header ("Written only by `crew bolt` and `crew unit`"; approve and `state init` write it too); `transcript.py`'s docstring (it reads `uuid`, `timestamp` and `tool_result`).
- The findings-to-design exploration (`brief.md`, `proposal.md`, `roadmap.md`) is partly stale: review in plannotator, the transcript canary, and the roadmap covers only its own nine changes; each now says in its first line what it is.
