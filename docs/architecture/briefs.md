---
paths:
  - "plugin/roles/**"
  - "plugin/skills/**"
---

# Brief rules

The rules every role's brief holds to: what an agent may do, must never do, and how it speaks to the user. `core.md` binds here too, and `roles.1` to `roles.4` there bind every brief. Why rulings cite readings is record 0004; why decisions are shown whole is 0002.

## Rules

- **[briefs.1]** Each role stays in its job: the planner never starts units or drives a team; the design agent never puts a unit into a bolt; a dispatcher never changes a bolt's content; the operator agent writes nothing but the teams file, on the user's word; the conductor writes no design, specs or code; ops edits no code and deploys only what is committed on the bolt, from the bolt's worktree, and main-level ops only main.
- **[briefs.2]** A stage agent writes only within its scope and never pushes: construct commits only under its change; a coder treats the approved change as frozen, ticking tasks in the commit that does them, and a fix's coder touches nothing under `openspec/`; verify changes nothing.
- **[briefs.3]** A change's tasks never hold proof that needs a deploy, a live account, a credential, a vendor console or the user; that goes under *Proof in dev* in the design, and the team's ops works it from the bolt.
- **[briefs.4]** An agent that puts a decision before the user shows it whole, a proposal as `crew plan proposed <n>` prints it and constructed changes as a batch card with each unit's summary and its whole change, asks for the answer in words, and never recites an answering command; the conductor opens nothing for a batch.
- **[briefs.5]** A ruling names the documentation or reading it rests on, is made after reading the thing itself, rules the outcome and constraints rather than the sequence, and answers linked questions together; an intent names the outcome and the records that govern it, never the mechanism; corrections to a unit under construction are batched until its construct settles.
- **[briefs.6]** An agent that stops to wait on the user tells each of the partition's operator agents in one line what it waits for and where, and never asks the user to do what it can do itself.
- **[briefs.7]** Test, check and proof results reach the user as one bullet per suite or proof before any prose: ✅ passed, ❌ failed with the count and a one-line cause, ⏳ not yet run.
- **[briefs.8]** Without the user's word, no agent acts on an agent that is working, or clears, restarts or ends a slot's stage agent; every brief speaks plain English and describes what the user sees and does.
- **[briefs.9]** A card that asks the user to read something, a proposal or a report, carries the link to a plannotator session its owner starts on that document without opening a browser on the host, in the card's own words first and among its links, never only as an attached artifact; the card's words say in the document's own words what the user decides from, a change's Why and What changes, a proposal's case and changes, a report's findings, cut to the card's budget; the session's verdict and annotations are read as the card's answer, and the session ends when the card closes; a batch card instead carries each unit's summary and attaches or links its whole change, read and answered in Pending You, with no session.
- **[briefs.11]** A team's cards are its conductor's, one per rail row of its bolt and none else: ops and every stage agent post no card, what a proof leaves that only the user can do or check is asked on the bolt's landing card before its approval, and crew refuses a card a crew agent posts under any key but a rail row's of its own, and an area made under any key but `create-area:<owner>/<kit>`.
- **[briefs.12]** Constructed and amended changes reach the user as one card per batch, the conductor's, posted every N due changes or T hours, whichever comes first, from a fresh reviewer's summary file, with a question per unit; feedback on an unmerged unit runs construct again with the user's words and the unit goes on with no approval asked, feedback on a merged unit is a fix or new work, and a bolt is offered for landing only once every unit's latest change has appeared in a batch.
- **[briefs.10]** Anything sent to another team or partition is sent with `crew send <team or partition> "<text>"`, which delivers it to that partition's operator agent, on the sender's host when it has one there, else on the partition's main-level host, and records the send; every brief says so in one line, names nothing else to send to, and no agent sends a team's or a partition's business to its conductors.

## Details

**[briefs.1]** Rules out: the planner running `crew unit run`; the operator editing a kit beyond `lib/crew-teams.nix`; ops patching code. Source: `main-level` and `operator-agent` specs; fix 63bab58; the briefs.

**[briefs.2]** Rules out: a coder rewording a task; a push from a stage. Source: `construct.md`, `coder.md`, `verify.md`.

**[briefs.3]** Rules out: a task "deploy to dev and check". Source: `construct.md`; `bolt-teams` spec "A bolt is deployed and tested from its branch".

**[briefs.4]** Rules out: "approve proposal 71"; "run `crew plan approve 71`"; a pane or browser opened by the conductor; a unit put before the user on a card of its own. ADR 0014 (D5) for the batch. Not ruled out: a card's session, started with no browser, which opens nothing. Source: ADR 0002; a-decision-is-shown-whole; `tests/t-briefs.sh`.

**[briefs.5]** Rules out: a ruling from belief; an intent that names a function; a batch's feedback sent into a construct still running. Source: ADR 0004; rulings-rest-on-readings-and-intents-name-outcomes; ADR 0014 (D5).

**[briefs.6]** Rules out: a question left in a pane nobody watches; "please run the suites". Source: fixes 21d82af, ec593d5, e3d75cb.

**[briefs.7]** Rules out: "they all passed" in a sentence. Source: signal `2026-10-07-swancloud-design-c8f7c4bd/01-test-results-are-a-glyph-list`; unit `test-results-are-a-glyph-list`; `crew.py` `RESULTS`; `tests/t-briefs.sh`.

**[briefs.8]** Rules out: a dispatcher restarting a working conductor. Source: `plugin/skills/crew/SKILL.md`; `dispatcher.md`.

**[briefs.9]** Rules out: a card with the files attached and no link; a link only as an artifact (the user, 2026-10-09: "the pending you isn't showing me enough detail about the OpenSpec proposal", signal 2026-10-09-swancloud-operator-mac-studio-351110ee/01); a summary of two sentences standing for a change; a path on a card; a browser opened on the host for a session whose link is on a card; annotations the user wrote that reach nobody. Source: ADR 0005 as amended 2026-10-08; signal 2026-10-08-swancloud-design-0f348337/01; the readings in that record; `crew card session` (`plan.py` `card_session`) and the card hook (`plugin/hooks/cards`), which ends a closed card's session; `tests/t-card-session.sh`, `tests/t-cards.sh`. The card discipline puts the link only as an artifact and says only "what the user would read" until `a-card-reads-whole-at-a-glance` lands: `_open.md`.

**[briefs.11]** Rules out: a card from ops for what its proof left open; two cards for one step; an area keyed by the agent that made it; a card for a question asked in a pane. Not ruled out: a kit's deployer, which is no crew agent, posting a deploy's or a user's step's card under its row key (`plan.14`). Source: ADR 0005 as amended 2026-10-09; signal 2026-10-09-swancloud-operator-mac-studio-9539e922/01; `crew.py` `cards_how`; `plugin/hooks/cards`. `ops.md` has no card rule and the hook refuses nothing until `a-teams-cards-are-its-conductors` lands: `_open.md`.

**[briefs.12]** Rules out: a card per unit for review; code held for a batch's answer; a re-approval after feedback; feedback amending a merged unit; a landing offered while a unit's latest change has been in no batch; a batch answered by an agent. Source: ADR 0014 (D5, D6), and the operator's correction of 2026-10-09 that the batch is read in Pending You itself; `roles.1`, `roles.2`. Not built: `_open.md`.

**[briefs.10]** Rules out: a session offering to send findings to the conductors; a message to a dispatcher that is not about a bolt; an agent working out which operator on which host to tell. Source: ADR 0013; signal 2026-10-08-swancloud-operator-mac-studio-5fda4ef7/01 and the user's requirement on it. Not built: `_open.md`.
