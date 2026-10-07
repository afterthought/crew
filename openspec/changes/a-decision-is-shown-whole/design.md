# Design

## Context

See proposal.md for why. The decision is `docs/adr/0002-what-waits-on-the-user-is-shown-whole-and-read-from-state.md`, its "Shown whole" part; its "One list, read from state" part, `crew rail` and its tab, is another unit.

What is built today:

- `plugin/roles/conductor.md`, *Review with the user*: the conductor tells the user a unit is ready, where its change is and what it would make true, then opens `proposal.md` in plannotator with `plannotator-tui herdr open …/proposal.md`, waits for annotations, and opens the design, specs and tasks one after another. *The plan* has the conductor read a proposal that touches its bolt with `crew plan proposed <n>` and agree to it; nothing says how to put a proposal before the user.
- `plugin/roles/planner.md`, *Proposals* step 2: the planner shows `crew plan proposed <n>` in its pane or opened beside it. Nothing forbids naming a proposal by number, or reciting `crew plan approve`. *Where things stand* lists open proposals by reading `crew plan proposed`.
- `plugin/roles/operator.md`, *Where things stand*: lists units in review and open proposals, and gives the user `crew unit approve <unit>` and `crew plan approve <n> --label <label>` to answer them with.
- `plugin/lib/plan.py`, `describe()` builds each change's plain lines and already keeps each change's `Do` as `do`; `page()` renders the markdown. `page()` prints no command under a change, and its *Waiting on* section prints `crew plan agree <n> --label <label>` for each conductor and `crew plan approve` / `crew plan drop` for the user.
- `tests/t-briefs.sh` holds the briefs' phrases; `tests/t-proposals.sh` holds the rendering.

## Goals / Non-Goals

**Goals:**
- The user is shown the decision itself: a unit's whole change, opened by the user; a proposal's full rendering, never its number alone.
- The rendering shows the plan commands approval runs, under the words that explain them.
- No agent recites a command for the user to answer a review or a proposal with; the user answers in words.

**Non-Goals:**
- `crew rail`, its tab, and the plannotator command on a unit's rail row. That is the other unit of the ADR.
- The conductor's one-line tell to the operator agents when it stops on the user. It stays as it is.
- The text crew sends a conductor when a proposal touches its bolt, and what `crew plan propose` prints to the planner: both are for agents, not the user.
- The verify report the conductor relays. It is not a review or a proposal, and the brief already has the conductor tell the user in plain English what it would do about each finding.

## Decisions

### At review the conductor speaks and stops

The conductor's message is what it already says (the unit, the folder its change is in, two or three sentences on what it would make true) and one question in words: approve it, or say what to change. It opens nothing. The user opens the folder when they choose, so they see proposal, design, specs and tasks together rather than one file at a time. The folder path stays in the message: until the rail lands it is how the user finds the change, and it is a path, not a command.

The rule that the user's annotations come back as numbered feedback goes with plannotator. Whatever the user sends back, in words or as annotations, the conductor treats as before: approval, or construct again with the user's words.

*Alternative:* the conductor opens the whole folder in plannotator instead of one file. The ADR decides the user opens the change when they choose to read it, and puts the command that opens it on the rail's row for the unit.

### A proposal is shown whole, by whoever shows it

One rule, said in each brief that can put a proposal before the user: the planner when it proposes or answers where things stand, a conductor when it raises a proposal touching its bolt with the user, and the operator agent when it answers where things stand. Each shows what `crew plan proposed <n>` prints, in its pane, or written to a file and opened beside it with `plannotator-tui herdr open <file>` (the planner's brief already offers both). The number follows the words, as a reference.

For the operator, whose answers are kept short, the few sentences come first and each open proposal's rendering after them. Showing every open proposal whole is long only when many are open, and that is when the user most needs to see them.

### Answers are asked for in words

The briefs keep the commands an agent runs, since the agent needs them, but each place an agent asks the user for an answer says to ask in words ("approve it, or tell me what to change") and to run the command on the user's word. The operator's brief loses the two commands it gives the user (`crew unit approve <unit>`, `crew plan approve <n> --label <label>`) and says it runs them on the user's word.

### The rendering shows each change's command, and no answering command

`page()` prints, under the plain lines of each change, one line: `Runs:` and the change's `Do` with `crew ` in front, in a code span. It is the `Do` as the planner wrote it, which is what approval runs, in the proposal's partition; the rendering adds no `--label`, since a pasteable direct command is not what the user is being asked for. A `Do` that already begins with `crew ` is not prefixed twice (`do_args` accepts both). Intents often hold backticks, so the code span's fence is one backtick longer than the longest run of backticks inside the command, with a space inside each end when the command begins or ends with one (CommonMark's rule for code spans).

*Waiting on* keeps naming who the proposal waits on, and says what each would do in words instead of the command: each conductor "to agree, or tell <label>-planner why not", then the conductors that have agreed, then "the user, to approve it or say what to change". This is what makes "show it whole" and "recite no answering command" both true when an agent prints the rendering in its pane. The commands that answer a proposal belong on the rail.

`--json` already carries each change's `do`; it changes nothing.

*Alternative:* keep the answering commands in *Waiting on* until the rail exists. Every agent that showed a proposal whole would then recite them, which is what the user asked to stop.

### The README says what the rendering holds

The README's `crew plan proposed <n>` bullet gains "the command approval runs under each change" and "who it waits on, in words".

## Risks / Trade-offs

- [Until the rail lands, the user has no pasteable command to answer a proposal or open a review] → they answer in words to the agent that showed it, which runs the command, as the briefs already allow; the folder path is in the conductor's message. The rail unit adds the commands where they belong.
- [The operator's answer grows with several proposals open] → accepted; the user asked to see them, and a long list is the signal to work them down.
- [A brief rule is followed only as well as the agent reads it] → each rule sits in the section the agent is in when it acts, and `tests/t-briefs.sh` holds its phrase.

## Migration Plan

Land, then pull on every host. Each partition's conductors, planner and operator agents take the briefs at their next fresh start, or when told what changed; `crew plan proposed <n>` prints the new way at once. Rollback: revert.

## Proof on real work

Once the bolt has landed, every host has pulled and the agents have started fresh:

1. The next unit to reach review: its conductor tells the user it is ready, where its change is and what it would make true, asks for the answer in words, and no plannotator pane opens.
2. The next proposal the planner writes: the planner's pane shows the full rendering, with a `Runs:` line under each change, and asks for the answer without reciting `crew plan approve`.
3. Asked "what waits on me" while a proposal is open, the operator agent shows that proposal's rendering, not only its number.

## Task notes

**1.1** `plugin/roles/conductor.md`, *Review with the user*. Keep the first paragraph, and end it: "Ask for the answer in words, approve it or tell you what to change, and stop: open nothing, and recite no command for the user to answer with. The user opens the whole change, its proposal, design, specs and tasks, when they choose to read it." Delete the second paragraph (the `plannotator-tui herdr open …/proposal.md` paragraph) whole. In the third paragraph, change "When the user's annotations ask for changes" to "When the user asks for changes, in words or as annotations", and the construct argument `"<the user's annotations>"` to `"<the user's words>"`. In *The plan*, after the sentence on reading a proposal with `plan proposed <n>`, add: "When you raise a proposal with the user, show what `{{TEAM_CMD}} plan proposed <n>` prints, never its number alone, and ask for their answer in words." `tests/t-briefs.sh`: replace the line `has "$out" "plannotator-tui herdr open"; has "$out" "openspec/changes/<unit>/proposal.md"` with `lacks "$out" "plannotator"`, and `has` "open nothing, and recite no command", "The user opens the whole change", "never its number alone". The existing "unit approve" check still passes.

**1.2** `plugin/roles/planner.md`, *Proposals* step 2. Make it: "Show the user what `{{TEAM_CMD}} plan proposed <n>` prints: in your pane, or written to a file and opened beside it with `plannotator-tui herdr open <file>`. Never name a proposal by its number alone: the number follows the words, as a reference. It reads as the user would want it, each change in plain words with what it rests on, the goal of the bolt it would join, and the command approval runs. Ask for the answer in words, approve it or say what to change, and recite no command for the user to answer with." In *Where things stand*, add: "Show each open proposal as step 2 does, not only its number." `tests/t-briefs.sh`: in the `wldn planner` checks, `has` "Never name a proposal by its number alone", "recite no command".

**1.3** `plugin/roles/operator.md`, *Where things stand*. Replace the paragraph's list of what waits on the user with: "…and anything waiting on the user: units in review, each with the folder its change is in; the planner's open proposals, each shown as `{{TEAM_CMD}} plan proposed <n> --label {{LABEL}}` prints it, after your few sentences, never by its number alone; or an agent blocked on a question. Ask for the user's answer in words and recite no command for them to answer with. Run either approval only on the user's word, never on your own judgment: a unit with `{{TEAM_CMD}} unit approve <unit>`, a proposal with `{{TEAM_CMD}} plan approve <n> --label {{LABEL}}`." The existing `wldn operator` checks ("plan proposed --label wldn", "plan approve <n> --label wldn", "only on the user's word") still pass; add `has` "never by its number alone", "recite no command".

**2.1** `plugin/lib/plan.py`, `page()`. After the indented plain lines of each change, append `   Runs: <span>` where `<span>` is `crew ` plus `c["do"]` (unprefixed when it already starts with `crew `) in a code span whose fence is one backtick longer than the longest backtick run in it, padded with a space inside each end when it starts or ends with a backtick. Replace the *Waiting on* lines: each waiting conductor `- {t}-conductor, to agree, or tell {label}-planner why not`; the agreed line as it is; the user `- the user, to approve it or say what to change`. `page()`'s docstring drops "in plannotator". `tests/t-proposals.sh`: after `crew plan proposed 1`, `has` `Runs: \`crew bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit\`` and `Runs: \`crew unit move queued-one deploy-checks\``; replace the `crew plan approve 1 --label wldn` check with `has "$out" "the user, to approve it or say what to change"` and `lacks "$out" "crew plan approve"`; after `crew plan proposed 2`, replace the `crew plan agree 2` check with `has "$out" "swb-1-conductor, to agree, or tell wldn-planner why not"` and `lacks "$out" "crew plan agree"`. At the end of the file, so no later proposal's number moves, propose one whose intent holds a backtick (for example ``Do: unit add ticks "The `x` command works." --repo switchboard-kit``) and check `crew plan proposed` of it prints its `Runs:` line fenced with two backticks.

**2.2** `README.md`, the `crew plan proposed` bullet in *Proposals*: after "and what approval sets in motion", add "; under each change, the command approval runs; and, for an open proposal, who it waits on, in words".
