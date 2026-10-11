# Design

## Context

See proposal.md for why. The rule is decided in `docs/adr/0004-rulings-rest-on-readings-and-intents-name-outcomes.md` (the bullet "The sources govern, and a stage that finds the intent saying more says so", added 2026-10-10) and stated as `briefs.14` in `docs/architecture/briefs.md`, whose details mark it not built. This change builds its first half and makes it bite: the sources reach the construct. The second half of `briefs.14`, the spike beside the design agent, is another unit (`a-spike-runs-beside-the-design-agent`).

What happened on madswan, read from its records:

- Signal `2026-10-10-madswan-planner-f05265a3/01` (on `madswan/main` of afterthought/crew-state) quotes the user asking for an example measurement page and pasting session `55ff2a52-fb91-41f6-981c-3bfe06ab8024`. Its sentence says "the measurement-page idea from the site-design session" and names nothing else.
- That session's transcript is on mac-studio under `~/.claude/projects/-Users-chuck-Code-clients-github-willdan-switchboard-kit-main/`: it ran in switchboard-kit, wrote `agentplot/flywheel-web:docs/site-design.md` and `docs/measurement-roadmap.md` among others, and published the site design and decks as claude.ai artifacts.
- Unit `an-example-measurement-page` in madswan's `plan.rec` names the signal, those two pages and `src/content.config.ts` as its sources; no artifact, and nothing saying what the session made.
- The user, afterwards: "I don't want to build it exactly the way it was in the artifact" (signal `2026-10-10-madswan-planner-a0cf66a9/01`), and on the result (signal `2026-10-10-madswan-design-3d7ef799/01`): "You knew what I wanted: my measurement page was meant to show fleet utilization ... something got lost."

How the references travel today, link by link:

1. **Recording a signal.** Every brief that records one carries the same line, `signal_how` in `plugin/lib/crew.py`: a sentence saying what the signal asserts, the user's words verbatim, a kind. It says nothing of what the words point at. `crew signal` has no field for it (`plan.py`, the `signal` parser), so whatever is named goes in the sentence.
2. **Queuing work from it.** `crew unit add … --signal <id>` puts `signals/<id>` first among the unit's sources (`plan.py` 1420–1421). The planner's brief says "A unit that comes of it names the signal with `--signal`" and that an intent names "the records that govern it" (`briefs.5`); nothing says the records a signal points at are among them. The design agent queues with `--source` the same way (`design.md`, *Queuing work*).
3. **Starting the construct.** `run_check` sends `/opsx:propose <unit> <intent> Sources: <a>; <b>.` with each source as the plan holds it (`plan.py` 2649–2651).
4. **Reading them.** `construct.md`, *Writing the change*: "each is a path in {{BLUEPRINTS_NAME}} (`{{BLUEPRINTS}}`), or `<repo>:<path>` in another repo". An agent's signal is not in the blueprints repo but on the flywheel's branch of the state repository (`signals.1`), read with `crew signal show <id>`; the brief names neither. Nor does it say to follow what a source points at, what to do when it can't open one, or which governs when the intent and the sources differ. And the construct runs in `places/<unit>`, made from the bolt, so a page read by its path in the worktree is main as it was when the bolt was cut, older than a record the design agent landed since.

Rules this design rests on: `briefs.14` (what it builds), `briefs.5` (an intent names the outcome and the records that govern it: the records include what a signal points at), `read.1` (what cannot be read is named and refused, never guessed past), `signals.1` (where an agent's signal lives), `signals.2` (the excerpt stays verbatim; the sentence is the recorder's own), `briefs.2` (a construct commits only under its change; unchanged), `tests.6` (every rule a brief carries is pinned by a phrase in `tests/t-briefs.sh`), `docs.4` (the specs change only through this change's deltas), `roles.3` (a check in crew follows only once an agent breaks a rule its brief already states). Pages whose areas this change touches: `briefs.md` (`plugin/roles/`), `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/t-briefs.sh`), `docs.md` (`openspec/`, `docs/architecture/_open.md`).

## Goals / Non-Goals

**Goals:**
- Each link of the chain passes the references on in a form the next can open: the signal names where things are, the unit names them as sources, the construct reads them and what they point at.
- A construct that cannot open a source, or what one points at, stops and asks; it never builds from the intent in its place.
- Where the intent says more than its sources or says otherwise, the construct builds from the sources and opens its final message with the difference.
- A source is read as it stands on main when the construct starts.
- The briefs keep their style: the rule first, plain sentences, the command after.

**Non-Goals:**
- A field for references on `crew signal`, or `unit add --signal` copying a signal's references into the unit's sources by itself. Either changes the signal's shape, which the blueprints' `signals/README.md` defines; that is a decision for the design agent, named in the construct's final message, not made here.
- crew checking what an agent read or recorded. crew cannot tell whether a signal's words point at something, nor whether a construct opened what a source names; `roles.3` asks for a check only once a stated rule is broken.
- The code and verify stages. They are sent `/opsx:apply` and `/opsx:verify` with no intent and no sources, and build from and check the change the user approved.
- Carrying the difference past the construct's final message: the conductor telling the planner, and the planner proposing the intent corrected, which record 0004 also says. See *Risks*.
- Reading another host's session transcript. A conversation's id is turned into what it made by the agent recording the signal, on the host where the conversation ran, while it can be read there.

## Decisions

### The agent recording a signal resolves what the words point at

Whoever hears the user is best placed to find what the user means: it is on the host where the conversation, the spike or the artifact was made, and it is talking to the user. So the line every recording brief shares gains one sentence: when the words point at something made elsewhere (another conversation, a page or prototype, an artifact, files in another repo, a spike), find it and name in the signal's sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a branch, an artifact's link; a conversation's id alone is not enough, so name what it made. The excerpt stays the user's words verbatim (`signals.2`); the names go in the sentence, which is the recorder's own.

*Alternatives:* leave it to the planner to resolve when it queues the unit: the planner may be hours later, on another host, and a conversation's transcript is on the host it ran on. Leave it to the construct: the furthest link from the user, on a team's host, with only a prompt.

### A unit from a signal names what the signal points at

The planner's and the design agent's briefs say that a unit made from a signal names with `--source` what the signal points at, beside the signal itself, which `--signal` already adds. This is `briefs.5` applied: those are records that govern the unit. The plan then carries them, and `run_check` sends them in the construct's prompt as it sends every source.

### The construct reads everything it is handed and follows it

The construct's brief says how to read each kind of source: a page by `git -C <checkout> show main:<path>` (`{{BLUEPRINTS}}` for the blueprints repo, `{{KIT}}` for the kit, another repo's checkout by its name), a signal (`signals/<id>`) by `{{TEAM_CMD}} signal show <id>`, which reads it from either home. It opens what each source points at: a page or file it names, an artifact's link, a branch. Reading main with `git show` reads it as committed now, whatever the worktree holds and whatever is uncommitted in the main checkout.

*Alternative:* read `{{KIT}}/<path>` from the main checkout's working tree: usually main, but it holds anyone's uncommitted edits, and a record the design agent has not committed has not landed.

### A source it cannot open stops the construct

When a source, or something a source points at, cannot be opened (a path that isn't there, a link that won't load, a bare conversation id), the construct stops and asks through crew (`crew needs`), naming what it could not open and where it was named. It does not write the change from the intent in its place. This is `read.1` for a stage: what cannot be read is named, never guessed past. The conductor gets the words and gets the answer, as for any stop.

*Alternative:* write the change from what could be read and name the gap in the final message. That is the madswan failure: a change the user reviews, built without the material the user meant.

### The sources govern; the intent's outcome still bounds the change

Where the intent says more than its sources (a mechanism, a measure, a step they don't name) or says something they contradict, the construct writes the change from the sources: `briefs.14` as written. The brief's scope rule stands beside it: work neither the intent nor its sources cover stays outside the unit and is named for the planner. An intent that differs from its sources is not a wrong premise: the brief's line that sends a wrong premise through crew is reworded so it covers what the sources describe failing against the world, not a difference between intent and sources, which is built from the sources without stopping.

*Alternative:* stop and ask through crew whenever the two differ. That is what record 0004 replaced: a stop costs the conductor a round trip and the user a wait, and the record already says what the user wants.

### The difference opens the final message

The construct's final message opens with the difference before anything else: what the intent says, what the sources say instead, and which source. Where they agree, it says nothing about it, so a message that opens with a difference always means one. The *Committing* paragraph's list of what the final message holds gains it first.

### `_open.md` keeps only the spike

The `briefs.14` entry under *Accepted, not built* names both this rule and the spike. Once this lands, it names only the spike. `briefs.14`'s details keep "Not built: `_open.md`", which is still true of the spike.

## Risks / Trade-offs

- [A recorder that doesn't see the pointer] → the rule is in the one line every recording brief shares, beside the excerpt it already copies, so it is read at the moment the words are in hand. A signal recorded before this lands names nothing; a construct handed one with a bare id stops on it, which is the point.
- [More constructs stop] → a stop costs a round trip; a change built without the material costs a review, a rebuild and the user's trust. The stop names exactly what is missing, so the answer is one reading.
- [The construct's final message reaches the conductor only if someone reads it] → the conductor's wait answers with the construct's commit, not its words. This is so today for everything the final message already names. The change built is right either way, since it follows the sources; what can be lost is the planner correcting the intent. Named for the design agent, not built here.
- [A team on another host reads a main its host has not pulled] → the design agent commits on the main-level host and pushes only on the user's word. On mac-studio, where the design agent and the teams share checkouts, a record is read the moment it is committed. Named for the design agent, not built here.

## Migration Plan

Nothing to migrate. Each agent loads its brief at its next fresh start; each construct is fresh, so the next construct on any team after the bolt lands and its host pulls follows the rule. Units already queued keep their sources as written; the planner may add what their signals point at by amendment. Rollback: revert the briefs and `signal_how`.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled:
- Tell the planner of a finding that points at a conversation in another repo, by its id. The signal it records names where that conversation's work lives, and a unit it proposes from the signal names those as sources.
- Give a team a unit whose source is a signal naming a page in another repo. Its construct reads the signal with `crew signal show` and the page it names, and cites both.
- Give a team a unit whose source names something that isn't there. Its construct stops through crew, naming it, and commits no change.
- Give a team a unit whose intent names a mechanism its source record does not, and change that record on the kit's main after the bolt is cut, before the construct starts. The construct's change follows the record as main holds it, and its final message opens with the difference, naming the record.

## Task notes

### 1.1

In `plugin/lib/crew.py`, `signal_how`, after the sentence ending "a refusal means the words were reworded.", add: "When the words point at something made elsewhere, such as another conversation, a page or prototype, an artifact, files in another repo or a spike, find it and name in the sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a branch, an artifact's link. A conversation's id alone is not enough: name what it made." The rest of the line is unchanged.

### 1.2

In `plugin/roles/planner.md`, *Signals and queued work*, the sentence "A unit that comes of it names the signal with `--signal`." becomes "A unit that comes of it names the signal with `--signal`, and with `--source` what the signal points at, so the construct is handed it: a signal is not the records that govern the unit, only the way to them."

In `plugin/roles/design.md`, *Queuing work*, after "An intent names the outcome and `--source` the records that govern it, never the mechanism: the how lives in the records, so a changed mechanism changes no intent.", add: "When the work comes of a signal, `--source` also names what the signal points at."

### 1.3

In `plugin/roles/construct.md`, *Writing the change*, replace the "Read the sources first" bullet with three bullets, worded as below (tokens as they are; keep the quoted phrases exactly, which `tests/t-briefs.sh` checks):

- **Read every source first, as it stands on main now, and what each points at.** A page is a path in {{BLUEPRINTS_NAME}} (`{{BLUEPRINTS}}`), or `<repo>:<path>` in another repo, such as {{KIT_NAME}}'s main (`{{KIT}}`): read it with `git -C <its checkout> show main:<path>`, never the copy in this worktree, which holds main as it was when the bolt was cut. A signal, `signals/<id>`, is read with `{{TEAM_CMD}} signal show <id>`. Open what each source points at: a page or file it names, an artifact's link, a branch. Cite the design pages you rest on.
- **A source you cannot open stops you.** When a source, or something one points at, can't be opened (a path that isn't there, a link that won't load, a conversation's id with nothing to say what it made), don't write the change from the intent in its place: ask through crew, as *When you can't finish* says, naming what you could not open and which source named it.
- **The sources govern how the unit is built.** Where the intent says more than its sources, such as a mechanism, a measure or a step they don't name, or says something they contradict, write the change from the sources. Then open your final message with the difference, before anything else: what the intent says, what the sources say instead, and which source. Where they agree, say nothing about it.

Reword the line under *How a unit works* that begins "If the intent can't be built as written" so it reads: "If what the sources describe can't be built because its premise is wrong, don't write around it: say so through crew, as *When you can't finish* says. An intent that differs from its sources is not a wrong premise: build from the sources."

In *Committing*, the sentence "Commit, then end with a short message in plain English: what the change now makes true, …" becomes "Commit, then end with a short message in plain English: first any difference between the intent and its sources, then what the change now makes true, …", the rest unchanged.

### 1.4

In `tests/t-briefs.sh`:

- In the loop over the six briefs that record signals (the one that checks "Copy the excerpt, never reword it"), check with `has`: "When the words point at something made elsewhere" and "A conversation's id alone is not enough".
- Beside the `wldn planner` checks, `has`: "and with \`--source\` what the signal points at". Beside the `wldn design` checks, `has`: "\`--source\` also names what the signal points at".
- Beside the existing `swb-1 construct` checks (the "## Writing a change again" block), `has`: "as it stands on main now, and what each points at", "never the copy in this worktree", "signal show <id>", "A source you cannot open stops you", "don't write the change from the intent in its place", "The sources govern how the unit is built", "write the change from the sources", "open your final message with the difference", "first any difference between the intent and its sources", "An intent that differs from its sources is not a wrong premise"; and `lacks`: "If the intent can't be built as written".

End with an `ok` line saying a signal names where what it points at lives, a unit carries it as a source, and the construct reads it, stops when it can't, and builds from its sources over its intent. The test reads only `plugin/`, so `tests/moon.yml` does not change.

### 1.5

In `docs/architecture/_open.md`, *Accepted, not built*, the entry beginning "`briefs.14`, ADR 0004 as amended, ADR 0016" becomes: "`briefs.14`'s spike clause, ADR 0016: a spike beside the design agent (`a-spike-runs-beside-the-design-agent`); crew has no spike."
