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
- **[teams.5]** Code is refused for a unit the user has not approved, verify until every task is ticked, and a unit or fix merges into its bolt only through `wt merge bolt/<bolt> --no-squash --no-remove`.
- **[teams.6]** A role's model and effort come only from its definition's frontmatter, overridden only under `roles.<role>` in the teams file; `crew-role` starts every role with `CREW_AGENT` and `CREW_LABEL` set and the filled brief appended to the system prompt, in the role's folder, and `crew resume` picks up the agent's last session in the folder it began in.
- **[teams.7]** A conductor gets exactly one greeting per start, and a plan write whose own command greets a team does not also notify its conductor.
- **[teams.8]** A pane crew starts answers only Claude's folder-trust question, never the Bypass Permissions warning.
- **[teams.9]** The panes, layout and slots files change only by writing a new file and moving it over the old; the stages file changes only under `flock`; output that bash evals is shell assignments quoted with `shlex.quote`, and everything else such a command says goes to standard error.
- **[teams.10]** A brief fills every `{{TOKEN}}` from the builder, a token with no builder or no data is a refusal, never blank text, and every brief carries the roster with how to read crew's marks.

## Details

**[teams.1]** Rules out: a slot kept for a requeued unit; a fifth unit on a four-slot team. Source: fixes e413c48, f6988a2; `bolt-teams` spec "Units run in slots"; worktrees-go-with-their-work.

**[teams.2]** Rules out: a launch typed into a running Claude; `stop` reporting success on a live agent. Source: fixes 499cd3b, f6988a2; `plugin/bin/crew` 164–181, 411–420.

**[teams.3]** Rules out: `fix/<name>` with no bolt; a merge from another place; adopting an existing place. Source: fixes 5e11de2, f6d7b11, 4fd29d2; fix-place-names-its-bolt.

**[teams.4]** Rules out: `stage.end` at herdr's first idle with no deliverable; a conductor reading a pane for an outcome; a two-hour wait on a stage already done. Source: ADR 0007. `crew unit wait` still ends at herdr's settle until `a-stage-ends-at-its-deliverable` lands: `_open.md`.

**[teams.5]** Rules out: `--no-hooks`, `--yes`, a squash. Source: `bolt-teams` spec; `plugin/bin/crew` 562; `plan.py` 2463.

**[teams.6]** Rules out: a model named in `plugin/lib` or `plugin/bin`; an override for a role the team lacks; a resume in the wrong folder. Source: `agent-models` spec; `crew.py` 32–35, 84–97, 326–335, 567–579; fix 25c300d.

**[teams.7]** Rules out: a conductor greeted twice. Source: fix 5a481ae.

**[teams.8]** Rules out: crew pressing through the Bypass warning. Source: `plugin/bin/crew` 192–202.

**[teams.9]** Rules out: an in-place edit of `slots`; a diagnostic on stdout from `env-main`. Source: `plugin/bin/crew` 145–147; `crew.py` 409–415, 578–579; `plan.py` 2612–2638.

**[teams.10]** Rules out: `{{OPERATORS}}` rendering empty. Source: `crew.py` 21–23, 427–514; fixes 21d82af, e3d75cb.
