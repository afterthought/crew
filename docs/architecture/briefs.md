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
- **[briefs.4]** An agent that puts a decision before the user shows it whole, a proposal as `crew plan proposed <n>` prints it and a review as the change's folder, asks for the answer in words, and never recites an answering command; the conductor opens nothing at review.
- **[briefs.5]** A ruling names the documentation or reading it rests on, is made after reading the thing itself, rules the outcome and constraints rather than the sequence, and answers linked questions together; an intent names the outcome and the records that govern it, never the mechanism; corrections to a unit under construction are batched until its construct settles.
- **[briefs.6]** An agent that stops to wait on the user tells each of the partition's operator agents in one line what it waits for and where, and never asks the user to do what it can do itself.
- **[briefs.7]** Test, check and proof results reach the user as one bullet per suite or proof before any prose: ✅ passed, ❌ failed with the count and a one-line cause, ⏳ not yet run.
- **[briefs.8]** Without the user's word, no agent acts on an agent that is working, or clears, restarts or ends a slot's stage agent; every brief speaks plain English and describes what the user sees and does.

## Details

**[briefs.1]** Rules out: the planner running `crew unit run`; the operator editing a kit beyond `lib/crew-teams.nix`; ops patching code. Source: `main-level` and `operator-agent` specs; fix 63bab58; the briefs.

**[briefs.2]** Rules out: a coder rewording a task; a push from a stage. Source: `construct.md`, `coder.md`, `verify.md`.

**[briefs.3]** Rules out: a task "deploy to dev and check". Source: `construct.md`; `bolt-teams` spec "A bolt is deployed and tested from its branch".

**[briefs.4]** Rules out: "approve proposal 71"; "run `crew plan approve 71`"; plannotator opened by the conductor. Source: ADR 0002; a-decision-is-shown-whole; `tests/t-briefs.sh`.

**[briefs.5]** Rules out: a ruling from belief; an intent that names a function. Source: ADR 0004; rulings-rest-on-readings-and-intents-name-outcomes.

**[briefs.6]** Rules out: a question left in a pane nobody watches; "please run the suites". Source: fixes 21d82af, ec593d5, e3d75cb.

**[briefs.7]** Rules out: "they all passed" in a sentence. Source: signal `2026-10-07-swancloud-design-c8f7c4bd/01-test-results-are-a-glyph-list`; unit `test-results-are-a-glyph-list`. Not built: `_open.md`.

**[briefs.8]** Rules out: a dispatcher restarting a working conductor. Source: `plugin/skills/crew/SKILL.md`; `dispatcher.md`.
