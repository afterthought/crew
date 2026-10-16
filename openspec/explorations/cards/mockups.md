# Cards in crew's process: where each one belongs, and what it looks like

An exploration, for the card elaboration of 2026-10-14, each mockup redrawn on 2026-10-15 as the card stood on the user's phone when they said it was right: a walk of crew's process saying at each point whether the user's word is needed and so whether a card goes out, and one mockup per card, to settle the list and the look before anything is built. It draws from crew's design (the rules, the records, the briefs), not from what today's code happens to do. The numbers and the history are in `reading.md` beside it.

**How to read a mockup.** Each box is a card as the phone shows it, drawn by hand; Pending You decides the exact layout, and what is ours is the words and the fields it is built from. Pending You's fields, as its tools take them today: a title (the question, read cold); a summary of one or two sentences; an *approve* block with a risk (low, medium, high) and whether it can be undone, answered by holding a button; or *options*, two to five, each with a line of detail and a consequence, one recommended; or two to four grouped *questions* on one card; a *rationale*; a *background* and a *trace* that fold open; links; artifacts (a picture, Markdown, a code block, a link, a path); a *fallback*, what the asker does if nobody answers, with when; *follows*, the card this one continues; and a note the user can write on any card. A card closes when its asker records what it did with the answer, in one line, or withdraws it with a reason. Changing a card in place carries a change note the user sees.

## 1. The process, and where the user's word is in it

crew's flywheel, from an idea to a machine running it. At each point: who acts, what is the user's, and whether a card is how it reaches them.

| # | Point in the process | Who acts | The user's part | Card |
|---|---|---|---|---|
| 1 | An idea, a signal or a finding is thought through | the design agent, with the user in its pane, or alone from the signals | thinks it through in the pane when they are there | none while they are in the pane |
| 2 | A decision is recorded (a record or an amendment) | the design agent | says yes, no, or what to change | **record**, only when the record was not settled with them in the pane |
| 3 | Work is queued from a record or a signal | the design agent | none | none: the proposal that puts it in a bolt is where they first meet it |
| 4 | The plan is changed: a bolt, units in it, moves, drops, amendments, chores | the planner, by a proposal | approves, leaves new units out, or sends it back with a note | **proposal** |
| 5 | A bolt is given to a team | the dispatcher | none (the plan's order is already theirs) | none |
| 6 | A unit is built: construct, code, verify, fix round, merge into the bolt through sluice | the team, stage by stage | none per unit: verify asks nobody (record 0027), merge needs no approval | none |
| 7 | Changes written or rewritten since the last batch reach the user | crew, at the batch clock (N changes or T hours) | reads, writes notes; approves nothing | **batch** |
| 8 | The user's notes go back | the planner to each unit's conductor; construct runs again | none | none: the next batch shows the rewrite |
| 9 | A bolt is proven: every unit merged, every change batched, sluice green at its head | crew reads it from the bolt | approves the landing | **landing** |
| 10 | The bolt lands on main | main-level ops, through sluice | none | none: the landing card's outcome says it landed, and every host took it |
| 11 | A `manual` environment is behind main | the kit's deployer offers it | approves the deploy | **deploy** |
| 12 | An `auto` environment is behind main | the deployer deploys it | none (the policy was their word, given once) | none |
| 13 | A deploy runs and ends, or fails | the deployer; ops watches | none | none: the deploy card's outcome says what happened, a failure with its step and log |
| 14 | After a deploy, a step that no check can be | the user when only they can; an agent when they say | does it, or says when | **step** |
| 15 | main is broken by a landing | the planner proposes a fix bolt, first in the plan | approves the proposal, then the landing | the **proposal** and **landing** above |
| 16 | A stage stops short, a team is stuck, a choice has no answer in the records | the chain of command below | answers | **question**, when the chain decides it is theirs |
| 17 | The teams change: a team added, moved, resized | the operator agent in its pane, on the user's word | says so in the pane | none |
| 18 | Something happened the user would want to know, with nothing to decide | — | — | none: it is the outcome on the card that asked, or the board |

So the deterministic cards are six: **record, proposal, batch, landing, deploy, step**, each raised by crew itself at its point, in the name of the role whose row it is, with no agent shaping it. The seventh, the **question**, is the open one: an agent asks it, and the only thing crew decides is who may.

### The chain of command for a question

```
   coder / construct / verify / reviewer / a team's ops
            │  stops short and says what it needs (crew needs)
            ▼
        conductor ──────── asks ──────▶ design agent   (a design question)
            │                       ▶ main-level ops  (hosts, landings, deploys)
            │                       ▶ planner         (the plan, another bolt)
            │   answered from the records, the bolt, or by one of them
            │
            │  not answerable there, and the choices make noticeably different products
            ▼
          the user, on a card, in the asker's own name
```

- Four roles may put a question before the user: a **conductor**, the **planner**, **main-level ops** and the **design agent**, each in its own name. A stage agent never does; its conductor asks, or answers. The operator agent never does: the user is in its pane. The dispatcher asks through the planner.
- The test for "theirs to ask" is Pending You's own, which the briefs already carry: what only they can decide, know or do, in their name, their money, their plans, public or hard to undo; not what is cheap to change later. Plus crew's: the records do not settle it, and the choices lead to noticeably different products. A conductor that can decide "what a careful product designer would" decides, and says so in one sentence.
- Nothing is refused by ruling. What crew checks is who posts (one of the four, in its own name), that a question already on a card gets no second card, and that a question whose asker is gone is withdrawn.

## 2. The mockups

Each card: the box, then when it goes out, what changes it, what closes it, and where the detail is when the box is not enough.

### A. Proposal

```
┌──────────────────────────────────────────────┐
│ swancloud · planner                  approve │
│                                              │
│ Plan change to a-deploy-holds-at-a-failure:  │
│ 1 unit dropped, 3 new                        │
│                                              │
│ The planner proposes: drop retry-on-every-   │
│ run and add three units, so the deployer     │
│ holds every environment after a failure      │
│ instead of retrying over it. Each row below  │
│ is set as proposed; flip any and send.       │
│                                              │
│ [x] Add a-failed-step-holds-its-environment  │
│     A failed step leaves its environment     │
│     failed and holds every one after it.     │
│ [x] Add the-doctor-names-the-failed-step     │
│     The doctor's deployer row names the      │
│     step that failed and its log.            │
│ [x] Add a-retry-is-offered-not-run           │
│     A retry over a failure is offered on a   │
│     card, never run on its own.              │
│ [ ] Keep retry-on-every-run (proposed: drop) │
│     Why dropped: a retry over a failure hid  │
│     it twice.                                │
│                                              │
│ Why: srv failed on 10-12 and the Macs were   │
│ deployed over it; the doctor shows nothing   │
│ until the next run.                          │
│                                              │
│ ▸ The 3 new units (Markdown: intent and      │
│   direction, one paragraph each)             │
│ ▸ The change, once approved (picture, 2x)    │
│ ▸ The change, in text                        │
│                                              │
│ Note ______________________________________  │
│                                     [ Send ] │
└──────────────────────────────────────────────┘
```

- **Goes out** the moment the planner's proposal is accepted into the plan, built by crew from the plan and the proposal; the planner writes the case and the `Do` lines, each new unit's direction among them, nothing of the card.
- **Changes in place** when the planner rewrites it after a note (change note: "Rewritten after your note: …"), and when a conductor agrees ("No longer waits on crw-2"). One card per proposal, however many times it is rewritten.
- **Closes** when crew has applied what was sent, with the outcome ("Applied: 3 units added, 1 dropped; a-retry-is-offered-not-run left out"), or when the planner drops it, with the user's reason.
- **The form**: one checkbox list and nothing else to tap; every row of the change is a box set as proposed, so leaving a new unit out, keeping a dropped one or an amendment's old words is a tap, and Send applies the boxes as they stand. No approve button inside the card (the user, 2026-10-15: "when you click it, it doesn't do anything and then you still have to click Send Answers"). A proposal with no unit rows is a hold-to-approve. A box list with nothing ticked asks for a note before it sends: Pending You's limit.
- **Detail**: the card holds the proposal whole: a paragraph per new unit on its face, the picture by crew's drawer at twice the pixel density, and the text. Only a proposal with more than fifteen new units links a reading session.

### B. Decision record

A plain record, and a record whose decision a rule of the user's made between alternatives.

```
┌──────────────────────────────────────────────┐
│ crew · design                        approve │
│                                              │
│ Accept record 0030 in crew: every crew card  │
│ is raised by crew at its point               │
│                                              │
│ Six cards are crew's own, raised at a fixed  │
│ point each; an agent's question is the one   │
│ open card, asked by four roles in their own  │
│ name.                                        │
│                                              │
│ Your own words, recorded as your decision    │
│ "I don't want to have to jump into pane      │
│  constantly"                                 │
│                                              │
│ ▸ The record (Markdown, 60 lines)            │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │        Hold to accept · low risk         │ │
│ └──────────────────────────────────────────┘ │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ wldn · design                         decide │
│                                              │
│ Record 0032: switchboard runs GitHub's       │
│ workflows itself, or a CodeBuild fleet as    │
│ your rules say                               │
│                                              │
│ Your rules decided this one: ops.3 (prefer   │
│ managed services) and ops.7 (no custom       │
│ runner) chose a CodeBuild fleet over         │
│ switchboard running the workflows itself,    │
│ which is what the design had meant. One      │
│ decision: the record as ruled, or loosen the │
│ rules as drafted and take the other path.    │
│                                              │
│ (•) Loosen ops.3 and ops.7 as drafted;       │
│     switchboard runs the workflows           │
│     a simpler GitHub side, more custom setup │
│     in the app; the rules say so from now on │
│ ( ) Accept the record as ruled: a fleet      │
│ ( ) Send it back with a note                 │
│                                              │
│ ▸ Where your rules decided, and the rules    │
│   loosened (Markdown)                        │
│ ▸ The record (Markdown)                      │
│                                              │
│ Note ______________________________________  │
│                                     [ Send ] │
└──────────────────────────────────────────────┘
```

- **Goes out** when the design agent commits a record or an amendment as proposed and the user was not in its pane to settle it. A record settled with the user in the pane takes their yes there and raises no card.
- **Changes in place** when the design agent revises it after a note (change note: "Revised: …", the new commit named). One card per record.
- **Closes** on yes, with the accepting commit as the outcome; on no, with the user's words; on "loosen", the design agent rewrites the record and amends the rules in one commit, and runs `crew record … --accepted` with it.
- **The second form** is for a record whose decision a rule made between alternatives: the design agent writes the alternatives, the rules that decided and each rule as it would read loosened, and hands them with `crew record … --proposed --alternatives <file>`; the card asks once (the user, 2026-10-15: "That should all be one decision: go with my plan or loosen the rules, and here's what the loosened rules would look like"; on the card: "I like the choices that worked well").
- **Detail**: the record whole, as Markdown on the card. No reading session: a record is short by design.

### C. Batch

```
┌──────────────────────────────────────────────┐
│ swancloud · planner                  one tap │
│                                              │
│ The deployer holds at a failure, and         │
│ questions and cards reach you (batch 7)      │
│                                              │
│ 4 changes to read, nothing to approve. The   │
│ changes written or rewritten since batch 6,  │
│ already being built. Read them for notes;    │
│ they go on building whatever you do with     │
│ this card. Notes go in the reading or in     │
│ this card's note, naming the unit; each      │
│ reaches its team as your words.              │
│                                              │
│ ▸ Open the reading   (plannotator, 1 session)│
│                                              │
│ The reviewer's summary (Markdown)            │
│ swc-1 · the-doctor-names-the-failed-step     │
│   The doctor's deployer row names the step   │
│   that failed and its log, instead of        │
│   "failed". …                                │
│ swc-2 · a-failed-step-holds-its-environment  │
│   A failed step leaves its environment       │
│   failed and holds every one after it. …     │
│ crw-3 · a-question-reaches-the-user          │
│   A conductor's question …                   │
│ crw-3 · a-card-closes-at-its-event           │
│   …                                          │
│                                              │
│ Note ______________________________________  │
│                                   [ Got it ] │
└──────────────────────────────────────────────┘
```

- **Goes out** at the batch clock, when crew finds a batch due: N changes across the partition's teams, or T hours, whichever first. In the planner's name, since the batches are its rows; the planner writes none of it.
- **Changes**: never. A batch is the changes as they stood when it was cut.
- **Closes** on the tap, or when the reading session is sent with its annotations, whichever comes first; one act is enough. Its notes go to each unit's conductor as the user's words.
- **The title** says what the batch is about, from its units' subjects; the count and "nothing to approve" open the body (the user, 2026-10-15: "I would prefer that a statement like '4 changes to read, nothing to approve' show in the body and that the title summarize what the batch is about").
- **Detail**: the reviewer's summary rides the face as inline Markdown, so the user decides whether to open the reading at all; the session holds the summary whole and every unit's whole change as one review. What the card is held to is the session: "it stays running, it closes when it's supposed to once we're done, it's accessible"; access over the tailnet "has been opening pretty reliably".

### D. Landing

```
┌──────────────────────────────────────────────┐
│ crew · crw-2 conductor         approve · HIGH│
│                                              │
│ Land the bolt a-deploy-holds-at-a-failure on │
│ crew's main                                  │
│                                              │
│ Six units land, every one merged and read in │
│ a batch (6 and 7). sluice is green at        │
│ 4581216, its pull request #23 linked below.  │
│ main has moved 1 landing since the bolt was  │
│ cut.                                         │
│                                              │
│ What lands: 6 units, no chores               │
│   the-deployer-records-each-step             │
│   a-failed-step-holds-its-environment        │
│   the-doctor-names-the-failed-step           │
│   a-retry-is-offered-not-run                 │
│   the-doctor-shows-the-hosts-sign-in         │
│   a-deploy-ends-with-its-outcome             │
│                                              │
│ ▸ Pull request #23 on GitHub, opened by      │
│   sluice                                     │
│                                              │
│ After it lands: main-level ops lands it      │
│ through sluice and every host takes it;      │
│ srv's deploy will be offered on a card.      │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │   Hold to approve · high · not undone    │ │
│ └──────────────────────────────────────────┘ │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘
```

- **Goes out** the moment crew reads the bolt proven: every unit merged, every change batched, sluice's verdict green at the head. In the conductor's name; the conductor writes none of it.
- **Changes in place** when the head moves while it is open, as when a fix lands in the bolt (change note: "Head is now 9ab12cd after the fix …"). One card per bolt, not one per head.
- **Closes** on the landing, with the outcome ("Landed as #24 at 14:02; mac-studio and the box are level"). A note naming a defect withdraws it ("Held for a fix: …") and it goes out again, following this one, when the bolt is green again. A no withdraws it with the user's words.
- **The face**: the units as a list, one a line, never a comma run in the detail (the user, 2026-10-15: "It needs to be scannable"); sluice's pull request linked when its submission has one ("It would also be nice if the 'Pull request opened in GitHub, created by Sluice' text were a link in here"). Settled: "ok. good enough for now."
- **Detail**: nothing to read; the units were read in their batches. The board has the bolt. Left for the design agent: the approval as the act that takes the pull request out of draft, and a link to the bolt's preview environment once sluice's previews exist (record 0031 §5 and §9).

### E. Deploy

```
┌──────────────────────────────────────────────┐
│ swancloud · ops                approve · HIGH│
│                                              │
│ Deploy main e5b83229 to swancloud-srv        │
│                                              │
│ Four landings since srv's last deploy        │
│ (50987b39): three fixes and two secrets      │
│ chores, release swancloud-srv-v0.3.0 below.  │
│ The box (auto) follows on its own; mac-      │
│ studio is offered after srv. After the       │
│ deploy: 2 steps, one yours.                  │
│                                              │
│ What's in it: swancloud-srv-v0.3.0 (Markdown)│
│ ## swancloud-srv-v0.3.0 (2026-10-15)         │
│ ### Fixes                                    │
│ - deployer: crew reaches the boxes with the  │
│   peer key, not the deployer's (e5b8322)     │
│ - deployer: read the install unit's script   │
│   though ExecStart ends in a space (6d58344) │
│ - cache: deploy a NixOS pusher's token to    │
│   its machine (4749797)                      │
│ ### Chores                                   │
│ - secrets: fix vars for chuck-herdr-alpha    │
│ - secrets: fix vars for swancloud-srv        │
│                                              │
│ After the deploy: 2 steps, one yours         │
│ 1  rotate the kanidm admin password          │
│    you; a card comes when srv is up          │
│ 2  restart crew's teams on mac-studio        │
│    ops, held for your word                   │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │   Hold to approve · high · not undone    │ │
│ └──────────────────────────────────────────┘ │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘
```

- **Goes out** when the deployer offers a `manual` environment a deploy, `crew ops offer <env> <sha> --notes <file> --steps <file>`, following the landing card that put the head on main. In ops's name; ops writes none of it, and crew writes none of the notes: they are the kit's changelog for exactly the range, as the deployer hands them (the user, 2026-10-15: "I want to be able to easily see a summary of what's in it from the release notes … or include a better summary of what will happen after the deploy").
- **Changes in place** when the deployer offers a newer head before the user answered ("Now offering 9ab12cd, which includes c882cff").
- **Closes** when the deploy ends, with its outcome ("Deployed at 14:20: machine ✅ guests ✅ suite ✅"), or when it fails ("Failed at guests, 14:12: ~/.local/state/swancloud/deployer/logs/…; the next run offers it again"). A no withdraws it with the user's words; the next head is a new card that follows this one.
- **Detail**: the landings' subjects, and how the deploy runs; a kit that hands no notes has the subjects on the face instead.

### F. Step

Two steps on one deploy, drawn as two cards. The first only the user can do; the second an agent can do, but not on its own. They are raised one at a time: the first follows the deploy's card, the second follows the first and is raised when crew closes it, since the phone shows one follower of a card until it is answered (the user, 2026-10-15: "only saw the one follows").

```
┌──────────────────────────────────────────────┐
│ swancloud · ops                           do │
│                                              │
│ After srv's deploy: rotate the kanidm admin  │
│ password                                     │
│                                              │
│ Only you can: the password is in your vault, │
│ and no check can tell it was done.           │
│                                              │
│ Where: a terminal on mac-studio              │
│ 1  clan vars generate swancloud-srv          │
│      --generator kanidm-admin --regenerate   │
│                                    [ copy ]  │
│ 2  clan machines update swancloud-srv        │
│                                    [ copy ]  │
│ Done when: kanidm's login page takes the new │
│ password.                                    │
│                                              │
│ ( ) Done     ( ) Skip it     ( ) Later       │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ swancloud · ops                       decide │
│                                              │
│ After mac-studio's deploy: restart crew's    │
│ teams, now or when the host is quiet?        │
│                                              │
│ ops can do it. It ends swc-1's code stage    │
│ mid-unit, which runs again from its start;   │
│ swc-2 and crw-3 are idle. Held for your      │
│ word.                                        │
│                                              │
│ (•) When the host is quiet   recommended     │
│     no stage is cut; could be hours          │
│ ( ) Now                                      │
│     swc-1's stage starts again, ~20 min lost │
│ ( ) Skip it                                  │
│     the teams keep the old crew until their  │
│     next restart                             │
│                                              │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘
```

- **Goes out** when a deploy ends and the deployer gathers the after-deploy steps of what it deployed: one card per step whose doer is the user, and one per step the change marked as held for the user's word, one at a time as above. A step an agent runs on its own (`when: deployed` or `quiet`, not held) raises no card.
- **Changes**: never.
- **Closes** on Done or Skip, recorded; on "Now" or "When quiet", when the agent has done it, with the outcome. Later leaves it open.
- **Detail**: the commands, whole, with a copy button; a step's words say what is done when. Both shapes stood on the phone as drawn.

### G. Question

```
┌──────────────────────────────────────────────┐
│ swancloud · crw-3 conductor           decide │
│                                              │
│ Unit a-failed-step-holds-its-environment:    │
│ hold the Macs too, or only the environments  │
│ after srv in the auto policy?                │
│                                              │
│ The design says "every environment after     │
│ it". The Macs come after srv but deploy on   │
│ their own word. The coder stopped here; the  │
│ design agent says record 0018 does not       │
│ settle it.                                   │
│                                              │
│ (•) Hold everything after srv   recommended  │
│     one rule, no special case for the Macs   │
│ ( ) Hold only the auto environments          │
│     a Mac's card still comes, with a warning │
│ ( ) Something else: say it in the note       │
│                                              │
│ If no answer by tomorrow 09:00: builds the   │
│ recommended one and says so in the unit's    │
│ summary.                                     │
│                                              │
│ ▸ Tried · the records read · the unit        │
│                                              │
│ Note ______________________________________  │
└──────────────────────────────────────────────┘
```

- **Goes out** when one of the four decides it is the user's, in its own name, shaped by the asker: title, summary, options with a recommendation, a fallback when it is not blocking. Guidance, not a form: the asker says what it tried and what the records say, offers the answers it can see, and names what it will do if nobody answers.
- **Changes in place** by the asker when it learns more ("New option: …").
- **Closes** when the asker acts on the answer, with the outcome. A question whose asker's session ended before an answer is withdrawn by crew ("crw-3's conductor ended; ask again if it still matters"), so nothing waits on a session that is gone.
- **Detail**: the asker's own: a diff, a file, a link, as Pending You allows. Stood on the phone as drawn (the user, 2026-10-15: "I think the last question card looks fine").

## 3. The two ways an agent can raise a question

Both keep the six deterministic cards crew's own. They differ only in how the seventh is posted.

| | **Pending You's tools, directly** | **`crew card ask`** |
|---|---|---|
| The asker shapes | everything Pending You offers: options, grouped questions, artifacts, fallback, follows | what the command takes: a title, words, options, a recommendation, a fallback, files; the rest crew fills |
| crew's part | a hook that records the card on the rail, refuses a poster outside the four, and withdraws a question whose asker ended | the same, plus the shape |
| Hears the answer | the session's own wake, as any Pending You user does | the same, once crew prints the id and the session adopts it |
| Sign-in | the session's, which under the host's sign-in is the one connection | the host's, through crew |
| Risk | an agent reads Pending You's guide its own way: the forms drifted this way before (`reading.md` §3) | a narrower card than the agent wanted |

Recommended: **Pending You's tools, directly**, for the question alone. The drift came from agents building crew's *rows'* cards by hand; those are crew's now. A question is the asker's, and the guide Pending You gives every session is better at a question than a form of ours. The naming question goes with it: no `crew card post` and no `crew plan card` for anyone, since crew's cards have no command; the agent-facing family shrinks to `crew card read`, for a card's state at a restart, and nothing else.

## 4. The sign-in, in plain words

You did sign in on the host, and it worked: the sessions took the host's sign-in 338 times through the morning of 10-10. What you saw as hiccups on 10-08 were Pending You refusing the host's token for a moment in one session, twice at 19:00Z; Claude Code then showed that session's Pending You as needing sign-in, and you signed it in through Claude Code's own browser login. That login did not touch the host's sign-in. On 10-10 at 04:57Z Pending You refused to refresh the host's sign-in and at 09:05Z the `pendingyou` command erased its own credential file, as its code does on a second refusal; from 11:55Z every session fell back, silently, to the Claude Code login of its account folder. So your logins did not cause the break. They are why nobody saw it for two days, and why cards posted since live on different connections and read "not found" to each other.

What makes it right, once: `pendingyou-signin` on mac-studio at a quiet moment (every open card is lost to its asker after it), then the same on the box when wldn's teams return; remove the Claude Code logins from the account folders so a dead host sign-in fails loudly instead of falling back; and swancloud's doctor shows the host's sign-in so a change is seen the day it happens. Those last two are swancloud's.

## 5. What to settle on this document

1. **The list.** Six cards of crew's own and one question. Anything missing: a failed deploy, a stuck team, a teams change? (Recommended: none; a failure is the deploy card's outcome and a signal, a stuck team is its conductor's question.)
2. **The question.** Pending You's tools directly, by the four roles, with crew recording and withdrawing; or `crew card ask`. (Recommended: directly.)
3. **One card, changed in place**, for a proposal rewritten, a landing whose head moved, a deploy whose head moved, a record revised; never a second card under a new key. (Recommended: yes.)
4. **A record's card** only when it was not settled in the pane. (Recommended: yes.)
5. **The batch's reading**: the plannotator link as it is, or the summary folded on the card and the link only for the changes. (Recommended: both.)
6. **Held steps**: a change can mark an after-deploy step as held for your word, with the agent as its doer. (Recommended: yes; the shape is swancloud's `openspec/config.yaml`'s to carry.)
7. **No heads-up cards**: an outcome goes on the card that asked, and the rest is the board. (Recommended: yes.)
