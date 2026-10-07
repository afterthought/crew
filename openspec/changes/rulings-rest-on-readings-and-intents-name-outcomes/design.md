# Design

## Context

See proposal.md for why. The rules are decided in `docs/adr/0004-rulings-rest-on-readings-and-intents-name-outcomes.md`; this change puts them into the three briefs that every partition's agents load at a fresh start. Nothing in `crew`, `plan.py` or the plan's checks changes.

What the briefs say today:

- `plugin/roles/design.md`, *Answering a conductor*: answer from the design as written; where it makes no decision, make the one a careful designer would, record it, commit, and answer with the pages or commits it rests on. Nothing about reading the thing itself, a ruling's documentation, sequence versus outcome, or linked questions. *Queuing work*: `unit add <unit> "<what must be true, in a sentence>" … --source <the page or decision record it comes from>`, which is already close to the planner's rule.
- `plugin/roles/planner.md`, *Proposals* and *Changing what a unit builds*: the `unit add` and `unit amend` rows take `"<intent>"`, with nothing on what an intent may say, and nothing on when to propose an amendment.
- `plugin/roles/conductor.md`, *The building loop* (last paragraph) and *What is not in your bolt*: a design question goes to the design agent in the words of whoever asked, one `tell` each, and a design answer comes back verbatim. Nothing on carrying questions together or on the reading.

The construct's brief (`plugin/roles/construct.md`) already asks a construct to check a vendor's real API before writing a task and to name the reading it needs for the team's ops, so the construct already brings its own reading; it does not change.

`tests/t-briefs.sh` prints each brief through `crewpy brief` and checks phrases with `has`; it is how a brief's text is held.

## Goals / Non-Goals

**Goals:**
- Each rule the ADR records is said once, in the brief of the agent it governs, where that agent looks when it does the thing the rule is about.
- The briefs keep their style: plain sentences, the rule first, the command after.

**Non-Goals:**
- Any check by crew of what an intent or a ruling says. These are rules of judgment; crew cannot tell a mechanism from an outcome.
- Removing the kit-level rule wldn wrote in switchboard-kit, or the agents' memories. That is wldn's, in another repository.
- The construct's, coder's, ops' or main-level ops' briefs.

## Decisions

### Each rule goes where the agent acts on it

- **Design agent.** *Answering a conductor* gains the four ruling rules, in the ADR's order: name what it rests on; read the thing itself first; rule outcome and constraints, not the sequence; answer linked questions together. *Queuing work* says the intent names the outcome and `--source` the records that govern it, never the mechanism. *Talking design with the user* is left alone: a ruling made with the user is still a ruling, and the first rule says so whoever asked, so the rules are written to apply to any ruling, not only a conductor's.
- **Planner.** A short paragraph after the proposal table says what an intent names, since every `unit add` and `unit amend` writes one. *Changing what a unit builds* gains the batching rule.
- **Conductor.** The design-question line in *What is not in your bolt* says linked questions go together, and the stopped-short paragraph in *The building loop* says the answer goes back with its reading.

*Alternative:* one shared section repeated in all three briefs. Each agent would read rules that aren't its own, and the ADR assigns each rule to one role.

### Who gets a reading the design agent lacks

The ADR says the design agent "asks ops for the reading" and doesn't say which ops. A construct's question comes through its conductor, whose brief already sends every fact about a live system to its team's ops, and that ops has the bolt's accounts. So for a question a conductor carried, the design agent tells that conductor which reading it needs, and the conductor asks its ops and sends the reading back with the questions. For a question that came from no team (the user in the design agent's pane, or its own elaboration), the design agent asks the partition's main-level ops (`{{MAIN_OPS}}`, already filled in the design brief). This is a reading, which main-level ops' care rules already allow ("read before you write"); it changes nothing live.

*Alternative:* the design agent always asks main-level ops. Its accounts are main's, not the bolt's, and the team's ops is the one that knows the bolt's dev.

### How the planner knows a construct has settled

Batching needs a moment to propose, and nothing tells the planner when a construct settles: the conductor's `crew unit wait` does. So when the planner holds a correction to a unit in construct, it tells that unit's conductor once, and the conductor, which sees the stage settle, tells the planner. Then the planner proposes one `unit amend` carrying every correction it holds. "Under construction" is a unit whose stage `crew bolts` reads as `construct` (or `amended`, waiting on construct again). A correction "blocks the team now" when the construct, or another unit of the bolt, cannot go on without it; that one is proposed at once, with what else is held for the unit. The planner holds corrections in its own context, as it holds any work in hand; it writes no tracking file.

*Alternative:* the planner polls `crew bolts`. It has nothing to wake it, so it would propose only at its next turn, which may be hours later.

### Wording

The briefs use the ADR's words where they are already plain ("names what it rests on", "read the thing itself", "the outcome and the constraints, not the sequence", "outcome and the records that govern it, not the mechanism"). `tests/t-briefs.sh` checks a phrase from each rule, so the coder keeps those phrases exactly as Task notes give them.

## Risks / Trade-offs

- [A rule in a brief is followed only as well as the agent reads it] → it is placed in the section the agent is in when it acts, and stated as a rule, not a hint. Nothing better is available without a check crew can't make.
- [Holding corrections delays a correction the user would have wanted at once] → anything that blocks the team goes at once; the rest waits only until the construct settles, which is when the user would review anyway.
- [A held correction is lost if the planner is restarted before proposing it] → accepted: a construct runs for minutes to an hour, and the planner is restarted only when the user asks. Whoever sent the correction still holds it.
- [The briefs grow] → each rule is one or two sentences; the planner's and design agent's briefs grow by under a tenth.

## Migration Plan

Land, then pull on every host. Each partition's design agent, planner and conductors take the rules at their next fresh start, or when told what changed. Rollback: revert.

## Proof on real work

Once the bolt has landed and every host has pulled, and the agents have started fresh:

1. The next design question any conductor carries about a live service gets an answer that names the documentation page or reading it rests on, and says what must be true rather than a sequence of steps.
2. The next `unit add` or `unit amend` the planner proposes, and the next unit the design agent queues, has an intent that says what becomes true, with the governing records as its sources, and no service call, command or step in the intent.
3. The next time two corrections to one unit arrive during its construct, the user sees one amendment proposal for them, after the construct settles.

## Task notes

**1.1** `plugin/roles/design.md`, *Answering a conductor*. Keep what is there; after "Answer from the design as written;" and before the `tell` command, add as a short list:
- **A ruling names what it rests on.** A ruling about how a service or a system behaves names, in the message that carries it, the documentation page or the reading it rests on.
- **Read the thing itself.** Before ruling about something that exists, read it with the credentials you have: the live configuration, the stack, the policy, the code on main. Where you have neither the documentation nor a reading, say so and ask for the reading before the ruling reaches any unit: from the conductor whose question it is, who gets it from its team's ops, or from `{{MAIN_OPS}}` when no conductor asked. Rule on that point only once it is back.
- **Rule the outcome and the constraints, not the sequence.** Say what must be true and what must not change, and leave the steps to the construct, which brings its own reading back. A sequence ruled from belief breaks one step per fact.
- **Answer linked questions together.** A construct's related questions are answered as one, after reading, not one at a time as they arrive.

Lead the list with one sentence saying these hold for every ruling, the user's included. In *Queuing work*, change `"<what must be true, in a sentence>"` to `"<the outcome, in a sentence>"` and add: "An intent names the outcome and `--source` the records that govern it, never the mechanism: the how lives in the records, so a changed mechanism changes no intent." `tests/t-briefs.sh`: in the `wldn design` checks, `has` "names, in the message that carries it, the documentation page or the reading it rests on", "Read the thing itself", "not the sequence", "Answer linked questions together", "never the mechanism".

**1.2** `plugin/roles/planner.md`. After the paragraph below the proposal table ("A drop removes the worktrees…"), add: "**An intent names the outcome and the records that govern it**, never the mechanism. Write what becomes true, for whoever uses it, and name the records with `--source`; the how lives in those records, which the construct reads, so a changed mechanism changes no intent." In *Changing what a unit builds*, add a paragraph: "**Corrections to a unit under construction are batched.** While a unit's construct is running, hold each correction to what it builds, and tell its conductor once that you hold some; the conductor tells you when the construct settles, and you then propose one `unit amend` that carries them all. A correction without which the construct, or another unit of the bolt, cannot go on blocks the team: propose it at once, with whatever else you hold for that unit." `tests/t-briefs.sh`: in the `wldn planner` checks, `has` "An intent names the outcome and the records that govern it", "never the mechanism", "Corrections to a unit under construction are batched", "blocks the team".

**1.3** `plugin/roles/conductor.md`. Change the design-question line in *What is not in your bolt* to: "**A design question**, from you or a stage: the partition's design agent. Send linked questions together, in one message: a stage's questions about the same thing, or your units' questions that turn on one thing. `{{TEAM_CMD}} tell {{DESIGN_AGENT}} "<the questions, in the words of whoever asked>"`; the answer comes back to you. When the design agent asks for a reading before it rules, get it from `{{OPS}}` and send it back with the questions it was for." In *The building loop*'s stopped-short paragraph, change "a design answer comes from the design agent verbatim" to "a design answer comes from the design agent verbatim, with the documentation or reading it names". Add a sentence there: "When the planner tells you it holds corrections to a unit in construct, tell `{{PLANNER}}` when that construct settles." `tests/t-briefs.sh`: in the `swb-1 conductor` checks, `has` "Send linked questions together", "with the documentation or reading it names", "holds corrections to a unit in construct". The existing check "tell wldn-design" must still pass.
