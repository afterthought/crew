# Design

## Context

See proposal.md for why. The rule is decided in `docs/adr/0004-rulings-rest-on-readings-and-intents-name-outcomes.md` (the bullet "The sources govern, and a stage that finds the intent saying more says so", added 2026-10-10) and stated as `briefs.14` in `docs/architecture/briefs.md`, whose details mark it not built. This change puts its first half into the construct's brief. The second half of `briefs.14`, the spike beside the design agent, is another unit (`a-spike-runs-beside-the-design-agent`).

How a construct gets its sources today:

- `plan.py` `run_check` sends the stage `/opsx:propose <unit> <intent> Sources: <a>; <b>.`, each source as the plan holds it: a path in the partition's first blueprints repo, `signals/<id>` among them, or `<owner>/<name>:<path>` for another repo (`bolt-plan` spec, "A source in a blueprints repo").
- `plugin/roles/construct.md`, *Writing the change*, says "Read the sources first", naming the blueprints checkout (`{{BLUEPRINTS}}`) and the kit's main checkout (`{{KIT}}`), and says nothing about which copy to read or what governs when the intent and the sources differ.
- The construct runs in `places/<unit>`, a worktree on `unit/<unit>` made from `bolt/<bolt>`, which `crew bolt give` made from main when the bolt was cut (`bolt-plan` spec). A file read by its path in the worktree is the bolt's copy, as main held it at the cut. The design agent commits its records on the kit's main and in the blueprints' main (`plugin/roles/design.md`, *Elaboration on main*), so a record it lands after the cut is on main and not in the worktree.
- The construct's final message is where it already names what goes to others: a reading for ops, a gap for the design agent, work outside the unit for the planner, what changed in a revision (*Writing the change*, *Writing a change again*, *Committing*).

Rules this design rests on: `briefs.14` (what it builds), `briefs.2` (a construct commits only under its change; nothing here changes that), `briefs.5` (an intent names the outcome and the records that govern it), `tests.6` (every rule a brief carries is pinned by a phrase in `tests/t-briefs.sh`), `docs.4` (the spec changes only through this change's delta), `roles.3` (a check in crew follows only once an agent breaks a rule its brief already states). Pages whose areas this change touches: `briefs.md` (`plugin/roles/construct.md`), `tests.md` (`tests/t-briefs.sh`), `docs.md` (`openspec/`, `docs/architecture/_open.md`).

## Goals / Non-Goals

**Goals:**
- A construct reads every source from main as it stands when the stage starts, never the bolt's copy in its worktree.
- Where the intent says more than its sources or says otherwise, the construct writes the change from the sources and opens its final message with the difference.
- The brief keeps its style: the rule first, plain sentences, the command after.

**Non-Goals:**
- The code and verify stages. They are sent `/opsx:apply` and `/opsx:verify` with no intent and no sources, and build from and check the change the user approved, which construct wrote from the sources. A record that changes after approval reaches the unit through the conductor and the user, as the design agent's brief already says ("A decision never changes a unit already approved").
- Any change to the prompt `run_check` builds, or a check by crew of what a construct read. crew cannot tell which copy an agent read, nor judge whether an intent says more than a record; `roles.3` asks for a check only once a stated rule is broken.
- Carrying the difference past the construct's final message: the conductor telling the planner, and the planner proposing the intent corrected, which record 0004 also says. The intent of this unit stops at the construct's message; see *Risks*.
- The user's own words on a revision. When construct runs again with what the user asked at review, those words go in as the brief already says; they are the user's, not the intent.
- A fetch before reading. The construct reads the checkouts its host has; see *Risks* for a team on another host.

## Decisions

### Read with `git show main:<path>`, not the worktree's file

The construct reads each source with `git -C <checkout> show main:<path>`, `<checkout>` being `{{KIT}}` for a source in the kit and `{{BLUEPRINTS}}` for one in the blueprints repo (another repo's checkout as its name says), and a directory listing its files the same way. That reads main as committed now, whatever the worktree holds and whatever is uncommitted in the main checkout, which may be someone's edit in progress. "As they stand when it starts" is then exactly main's tip when the construct reads.

*Alternatives:* read `{{KIT}}/<path>` from the main checkout's working tree: it is usually main, but holds anyone's uncommitted edits, and a record the design agent has not committed has not landed. Have `run_check` inline each source's text in the prompt: the prompt would grow by whole records, and `teams.15`'s prompt-typing work and the transcript's reading of the prompt both assume a short command.

### The sources govern; the intent's outcome still bounds the change

Where the intent says more than its sources (a mechanism, a measure, a step they don't name) or says something they contradict, the construct writes the change from the sources. That is `briefs.14` as written. The brief's scope rule stands beside it: work neither the intent nor its sources cover stays outside the unit and is named for the planner. And an intent that differs from its sources is not a wrong premise: the brief's line that sends a wrong premise through crew is reworded so it covers what the sources describe failing against the world, not a difference between intent and sources, which is built from the sources without stopping.

*Alternative:* stop and ask through crew whenever the two differ. That is what record 0004 replaced: a stop costs the conductor a round trip and the user a wait, and the record already says what the user wants.

### The difference opens the final message

The construct's final message opens with the difference before anything else: what the intent says, what the sources say instead, and which source. Where they agree, it says nothing about it, so a message that opens with a difference always means one. The *Committing* paragraph's list of what the final message holds gains it first.

### `_open.md` keeps only the spike

The `briefs.14` entry under *Accepted, not built* names both this rule and the spike. Once this lands, it names only the spike: ADR 0016 and `briefs.14`'s spike clause (`a-spike-runs-beside-the-design-agent`); crew has no spike. `briefs.14`'s details keep "Not built: `_open.md`", which is still true of the spike.

## Risks / Trade-offs

- [The construct's final message reaches the conductor only if someone reads it] → the conductor's wait answers with the construct's commit, not its words, and the conductor reads no pane. This is so today for everything the final message already names (a reading for ops, a gap for the design agent, work for the planner). The change built is right either way, since it follows the sources; what can be lost is the planner correcting the intent. Named for the design agent in the construct's final message, not built here.
- [A team on another host reads a main its host has not pulled] → the design agent commits on the main-level host and pushes only on the user's word, so a construct on the box reads the box's kit checkout as last pulled. On mac-studio, where the design agent and the teams share checkouts, a record is read the moment it is committed. Named for the design agent, not built here.
- [A brief rule is followed only as well as the agent reads it] → it sits in the bullet the construct is in when it reads the sources, and its final-message half is in *Committing*, where the message is written.

## Migration Plan

Nothing to migrate. Each construct is a fresh agent that loads its brief at its start, so the next construct on any team after the bolt lands and its host pulls follows the rule. Rollback: revert the brief.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled:
- Give a team a unit whose intent names a mechanism its source record does not, and land a change to that record on the kit's main after the bolt is cut, before the unit's construct starts. The construct's change follows the record as main holds it, and its final message opens with the difference, naming the record.
- A unit whose intent and sources agree: its construct's final message names no difference.

## Task notes

### 1.1

In `plugin/roles/construct.md`, *Writing the change*, replace the "Read the sources first" bullet with two bullets, worded as below (tokens as they are; keep the quoted phrases exactly, which `tests/t-briefs.sh` checks):

- **Read the sources first, from main as it stands now**: each is a path in {{BLUEPRINTS_NAME}} (`{{BLUEPRINTS}}`), or `<repo>:<path>` in another repo, such as {{KIT_NAME}}'s main (`{{KIT}}`). Read each as committed on that repository's main when you start, with `git -C <its checkout> show main:<path>`, never the copy in this worktree: this worktree was made from the bolt, which holds main as it was when the bolt was cut, and a record the design agent has landed since is the one that governs. Cite the design pages you rest on.
- **The sources govern how the unit is built.** Where the intent says more than its sources, such as a mechanism, a measure or a step they don't name, or says something they contradict, write the change from the sources. Then open your final message with the difference, before anything else: what the intent says, what the sources say instead, and which source. Where they agree, say nothing about it.

Reword the line under *How a unit works* that begins "If the intent can't be built as written" so it reads: "If what the sources describe can't be built because its premise is wrong, don't write around it: say so through crew, as *When you can't finish* says. An intent that differs from its sources is not a wrong premise: build from the sources."

In *Committing*, the sentence "Commit, then end with a short message in plain English: what the change now makes true, …" becomes "Commit, then end with a short message in plain English: first any difference between the intent and its sources, then what the change now makes true, …", the rest unchanged.

### 1.2

In `tests/t-briefs.sh`, beside the existing `swb-1 construct` checks (the "## Writing a change again" block), print the construct's brief and check with `has`: "from main as it stands now", "never the copy in this worktree", "The sources govern how the unit is built", "write the change from the sources", "open your final message with the difference", "first any difference between the intent and its sources", "An intent that differs from its sources is not a wrong premise"; and with `lacks`: "If the intent can't be built as written". End the block with an `ok` line saying the construct reads its sources from main and builds from them over its intent. The test reads only `plugin/`, so `tests/moon.yml` does not change.

### 1.3

In `docs/architecture/_open.md`, *Accepted, not built*, the entry beginning "`briefs.14`, ADR 0004 as amended, ADR 0016" becomes: "`briefs.14`'s spike clause, ADR 0016: a spike beside the design agent (`a-spike-runs-beside-the-design-agent`); crew has no spike."
