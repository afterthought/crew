---
paths:
  - "plugin/bin/crew"
  - "plugin/bin/crew-role"
  - "plugin/lib/crew.py"
---

# Team rules

The rules for teams, slots, stages, panes and tells: the bash command, the role launcher and the builder. `core.md` binds here too; the how-to is README's Teams section and `plugin/skills/crew/SKILL.md`. When a stage ends is record 0007.

## Rules

- **[teams.1]** A slot is freed, and its place removed, once its unit or fix has merged, landed, been dropped or left the team's bolt, and its agent has stopped; a team never has more than `units` in flight.
- **[teams.2]** Every unit stage starts as a fresh agent in its slot after the slot's previous agent is ended; crew never starts a role over an agent still running, `stop` fails rather than lies when the agent did not exit, and a working agent is ended, cleared or freed only with `--force`.
- **[teams.3]** A fix is built on `fix/<bolt>/<name>` at `<kit>/places/fix-<bolt>--<name>` from its team's bolt; a fix whose branch or place already exists is refused, and a fix's agent starts or merges only in a worktree on its own branch tracking the bolt.
- **[teams.4]** A stage ends when its deliverable exists in the kit or on the team's host, or when its agent stops short and says what it needs, never when its pane goes quiet; whoever waits learns the end with the deliverable, and a stage quiet past crew's limit is reported stuck.
- **[teams.5]** Code is refused until a unit's change is committed, never for want of a review; verify until every task is ticked; merge until every unit it comes after has merged; and a unit or fix merges into its bolt only through `wt merge bolt/<bolt> --no-squash --no-remove`, or, where the kit opts into sluice by a flag in its config, `wt submit bolt/<bolt>`, whose verdict replaces the merge hooks' suite gate.
- **[teams.6]** A role's model and effort come only from its definition's frontmatter, overridden only under `roles.<role>` in the teams file; `crew-role` starts every role with `CREW_AGENT` and `CREW_LABEL` set and the filled brief appended to the system prompt, in the role's folder, and `crew resume` picks up the agent's last session in the folder it began in.
- **[teams.7]** A conductor, and every agent crew starts outside a team (a main level's design agent, planner and ops, a dispatcher, an operator agent), gets exactly one greeting per start, marked as crew's; a plan write whose own command greets a team does not also notify its conductor.
- **[teams.12]** A unit's Touches is a fenced list of paths or globs under `## Touches` in its proposal, read by crew before code; an overlap with an unmerged unit ahead of it in the plan, and a conflict `git merge-tree` forecasts on the conductor's waits, reach the later unit once, told to its agent when idle, in its next stage's prompt when none runs, or as a settle stage when it waits to merge; a forecast between two unmerged units gives the later `After` on the earlier; overlap orders only merging, never construct, code or verify; a path the unit changed and did not declare is a verify finding.
- **[teams.13]** A conflict between two units, forecast, met at a rebase or met at merge, is resolved in the later unit's place by its agent, handed the other unit's change and the conflicting paths, keeping both intents; the earlier unit is not changed for it.
- **[teams.14]** A settle stage starts, fresh, in the slot of a unit that has delivered its verify and waits to merge, when a forecast or an amended `After` unit reaches it; its deliverable is a commit on the unit's branch made since it began, or its agent stopping short to say nothing needs to change, and the unit then merges.
- **[teams.11]** A tell reaches its agent as a prompt or not at all: an agent that is not up, or waiting on a question in its pane, is reported and the command fails with nothing typed.
- **[teams.8]** A pane crew starts answers only Claude's folder-trust question, never the Bypass Permissions warning.
- **[teams.9]** The panes, layout and slots files change only by writing a new file and moving it over the old; the stages file changes only under `flock`; output that bash evals is shell assignments quoted with `shlex.quote`, and everything else such a command says goes to standard error.
- **[teams.10]** A brief fills every `{{TOKEN}}` from the builder, a token with no builder or no data is a refusal, never blank text, and every brief carries the roster with how to read crew's marks.

## Details

**[teams.1]** Rules out: a slot kept for a requeued unit; a fifth unit on a four-slot team. Not ruled out: the partition's reviewer, a main-level role that takes no slot (ADR 0014). Source: fixes e413c48, f6988a2; `bolt-teams` spec "Units run in slots"; worktrees-go-with-their-work.

**[teams.2]** Rules out: a launch typed into a running Claude; `stop` reporting success on a live agent. Source: fixes 499cd3b, f6988a2; `plugin/bin/crew` 164–181, 411–420.

**[teams.3]** Rules out: `fix/<name>` with no bolt; a merge from another place; adopting an existing place. Source: fixes 5e11de2, f6d7b11, 4fd29d2; fix-place-names-its-bolt.

**[teams.4]** Rules out: `stage.end` at herdr's first idle with no deliverable; a conductor reading a pane for an outcome; a two-hour wait on a stage already done. Source: ADR 0007; `a-stage-ends-at-its-deliverable`; `plan.py` `deliverable`, `stage_wait` (`_wait`), `stage_needs` (`_needs`) and `stage_ends`; `transcript.py` `pending`; `tests/t-stage-ends.sh`.

**[teams.5]** Rules out: `--no-hooks`, `--yes`, a squash; code held for the user's review; a dependent merged ahead of its dependency; `wt submit` for a kit that has not opted into sluice. Source: `bolt-teams` spec; ADR 0014 (D2, D5, D7); sluice record 0002; `plugin/bin/crew` 562; `plan.py` 2463. The code refuses code before `crew unit approve` and knows only `wt merge` until `concurrent-units` lands: `_open.md`.

**[teams.12]** Rules out: Touches as prose compared by eye; two units built one after the other because their Touches overlap; a forecast that moves a ref; the same forecast told twice for the same heads; a forecast lost because no agent of the unit was running; the earlier unit told. Source: ADR 0014 (D3, D8); `concurrent-units` design. Not built: `_open.md`.

**[teams.13]** Rules out: a conflict resolved without the other unit's change in hand; the earlier unit rewritten for a later one's conflict. Source: ADR 0014 (D4); the sluice statement on attributing a conflict to the later entry. Not built: `_open.md`.

**[teams.14]** Rules out: a forecast typed into the idle agent of a stage that has already delivered; a settle stage that ends when its pane goes quiet. Source: ADR 0014 (D3); `teams.2`, `teams.4`; `concurrent-units` design. Not built: `_open.md`.

**[teams.6]** Rules out: a model named in `plugin/lib` or `plugin/bin`; an override for a role the team lacks; a resume in the wrong folder. Source: `agent-models` spec; `crew.py` 32–35, 84–97, 326–335, 567–579; fix 25c300d.

**[teams.7]** Not ruled out: the reviewer, sent its batch as a stage is sent its prompt, and not greeted (ADR 0014). Rules out: a conductor greeted twice; a main level or operator agent that starts and sits idle until someone tells it what to do. Source: fix 5a481ae; `main-level` spec "The main level is one herdr workspace" (the user, 2026-10-08: "They got no initial instructions, though.", signal 2026-10-08-swancloud-operator-mac-studio-c1fb895d/01); `crew.py` `greet_agent`; `tests/t-main.sh`.
**[teams.11]** Rules out: `herdr agent prompt` into a pane whose agent is blocked on a question, where the text lands in the dialog and the agent never receives it (the user, 2026-10-07: "i don't think it got it since it had a userquestion tool open", signal 2026-10-07-swancloud-operator-mac-studio-09fca02b/01). Source: `main-level` spec "Any agent crew starts is reached by name"; `crew.py` `tell`; `plugin/hooks/questions`. herdr reads Claude Code's state from the screen alone and took the 2026-10-07 tell into a dialog it did not see as `blocked`, so the second reading is a mark crew's own PreToolUse hook leaves when an agent opens a question or a plan for the user, open until its transcript holds the call's answer. An agent started before the hook has no mark and relies on herdr's reading alone until its next start, a departure from `read.1` (`a-tell-never-lands-in-a-question` design, decision 5).

**[teams.8]** Rules out: crew pressing through the Bypass warning. Source: `plugin/bin/crew` 192–202.

**[teams.9]** Rules out: an in-place edit of `slots`; a diagnostic on stdout from `env-main`. Source: `plugin/bin/crew` 145–147; `crew.py` 409–415, 578–579; `plan.py` 2612–2638.

**[teams.10]** Rules out: `{{OPERATORS}}` rendering empty. Source: `crew.py` 21–23, 427–514; fixes 21d82af, e3d75cb.
