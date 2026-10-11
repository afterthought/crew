# Design

Relies on `roles.2` (a landing and a push to main run only on the user's word), `state.3` (main changes only by
main-level ops's landing through the kit's hooks), `plan.8` (a landing rebases the bolt onto a main not behind
GitHub's), `plan.14` (a landing deploys nothing) and `briefs.11` (who posts which card). Touches the pages
`plan.md` and `briefs.md`.

**One procedure, one place.** The steps are main-ops's brief; `plan.16` states the procedure in one sentence and every
other brief, README and CLAUDE.md points to it rather than repeating it.

**The word.** The landing card is a rail row of the conductor's bolt, so it is the conductor's (`briefs.11`), and its
approval is the user's word. The conductor tells main-level ops; the user may also say it in ops's pane. The planner
and the rail row's appearing are no word.

**The push.** A landing is not done until GitHub's main holds it: every other host pulls GitHub's. The user's word to
land covers the push (`roles.2`), so ops pushes in the landing, never with force, after fetching. For crew, whose
checkout is live on each host, ops then fast-forwards each host's checkout (CLAUDE.md, *After landing*).

**Deploys.** `plan.14` holds: the landing deploys nothing. Until a kit's deployer records its deploys through crew
(`a-deploy-is-approved-and-recorded-through-crew`), main-level ops deploys a kit with no such deployer, swancloud
today, only on the user's word for that deploy, through the kit's runbook: a departure from `plan.14`'s "main-ops
running a deploy", which the user ruled on 2026-10-11 and which ends when the deployer records deploys.
