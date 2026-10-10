# Design

## Context

See proposal.md for why. What stands today:

- **The card hook only records.** `plugin/hooks/cards` runs after Pending You's `post_request`, `update_request`, `cancel_request` and `ack_answer` (PostToolUse in `plugin/hooks/hooks.json`) and writes `card.post`, `card.update` or `card.close`. It knows a row's card by its key (`KEYS`: `proposal/<n>`, `review/<unit>/<head>`, `verify/<unit>/<stamp>`, `land/<bolt>/<head>`), and finds an update's key from the card's `card.post` entry on this host (`posted()`). Nothing runs before a card is posted, so nothing checks what kind of card it is.
- **The forms are in the briefs, in words.** The conductor's *Cards* says a review card offers "approval, with a note for changes", a verify card offers the conductor's choices as options, and the landing card is "marked high stakes … offering approval". The planner's says a proposal card "offers approval, with a note for changes or for dropping it". The card discipline both briefs share, `cards_how()` in `crew.py`, gives every card "the row's answers as its options". None names a Pending You kind, and nothing refuses a card of another kind. brd-2's landing card was a step with the land command and a Done button.
- **The operator agent's brief** (`plugin/roles/operator.md`, *When an agent waits on the user*) shows a herdr notification for every wait it is told of. It carries no card rule, and Pending You's prompt hook tells every session that anything it needs from the user also goes on a card. That is how wldn's operator agent posted its own approve card for brd-2's landing.
- **Pending You's card, as read on 2026-10-09** (the `post_request` and `update_request` tool schemas in this session; `pendingyou` 0.28.0's Herdr popup, `dist/herdr/answer.js`): a card's `kind` is one of `choice`, `multi`, `approve`, `text`, `review`, `action` and `fyi`, or it is left out for a grouped card of `questions`. `approve` is answered yes or no ("Approved", "Declined"). `review` is answered "Looks good" or "Needs changes". `action` is a list of `steps` the user takes, each with an optional `command`, answered "Done" or "it didn't work". `fyi` is "Got it". Any card takes words through a reply. A card with `highStakes` true is refused from the popup's keys ("answer it in Pending You, where you hold to approve"). `options` are for `choice` and `multi`, two to five. `update_request` cannot change a card's kind, but it can set `highStakes` (to true, false or null), `options` and `action`.
- **Claude Code's hooks:** a PreToolUse hook matched on an MCP tool's name (`mcp__<server>__<tool>`) refuses the call by printing `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<why>"}}` and exiting 0. The agent is shown the reason, and the call never runs.
- **Another bolt checks the key.** `a-teams-cards-are-its-conductors` (bolt of the same name, built, not landed) adds a PreToolUse half to the same hook, matched on `post_request` and `create_area`, that refuses a crew agent's card under any key but one of its own rows (`plan.card_refusal`), the operator agent's card among them. This bolt starts from main without it.

Rules this change rests on: `briefs.13` (the rule it builds), `briefs.11` (the operator agent posts no card; its refusal is the other bolt's), `briefs.6` (a wait the user is told of), `roles.3` (a check, not firmer words), `roles.2` (the landing is run on the user's word, by main-level ops), `read.1` (what can't be checked refuses), `read.2` (the tool's input read by checked fields, an absent one never text), `code.1` (the standard library only), `tests.6` (a brief's rule pinned in `t-briefs.sh`), `docs.4`, `docs.5`. Pages whose area it touches: `briefs.md` (`plugin/roles/`), `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/`), `docs.md` (README, `docs/`, `openspec/`). `plugin/hooks/` has no page; `core.md` binds it.

## Goals / Non-Goals

**Goals:**

- No crew agent can put a row's card before the user in a form that is not the row's, at post or by a later update.
- The user gets one card per row, and the operator agent adds nothing to a wait that has one.

**Non-Goals:**

- Checking the words on a card (title, summary, background, links). `briefs.9` governs them and `a-card-reads-whole-at-a-glance` built them; crew records nothing written on a card and checks none of it, except that a landing card's steps never name the landing.
- Refusing the operator agent's card. That is `briefs.11`'s check, which `a-teams-cards-are-its-conductors` builds for every crew agent that owns no row. Until it lands, the operator agent's no-card rule is its brief's.
- A key that is no row's. Whether an agent may post it is the other bolt's check; this one looks only at cards under a row's key.
- Pending You's own reminder to put things on a card. It is Pending You's, and the operator agent's brief answers it for the operator agent.

## Decisions

### 1. Each row's form, in Pending You's kinds

| Row | Kind | Must | Must not |
|---|---|---|---|
| `proposal/<n>` | `approve` | | options, steps |
| `review/<unit>/<head>` | `review` | | options, steps |
| `verify/<unit>/<stamp>` | `choice` or `multi` | options | steps |
| `land/<bolt>/<head>` | `approve` | `highStakes` true | options; a step naming the landing |

Every row's card names its kind; a card with no kind, or with `questions`, is refused, as is `action`, `fyi` or `text`.

The review card is a `review`, not an `approve`. ADR 0005 has a review as "an approval with a note for changes" and a proposal as "an approval". Pending You's `review` kind is that answer, "Looks good" or "Needs changes", with the note in the user's reply or in the card's plannotator session. A bare `approve` would offer "Declined", which asks nothing a construct can be run again with.

A verify card takes `choice`, or `multi` when the user may pick several findings to fix, since the conductor's brief has "the findings the user chose". Both carry the conductor's options.

The landing card is high stakes by `highStakes: true`, the field the Herdr popup reads to refuse a key. It may still carry `action` steps, because `a-teams-cards-are-its-conductors` has the landing card ask the steps a proof leaves the user before approval (`briefs.11`). A step whose text or command names the landing itself (`bolt land`, `wt merge`) is refused, since that is the act the yes asks main-level ops for.

Alternatives: accepting `approve` for a review too, which loses the difference ADR 0005 draws; accepting `approve.risk` "high" in place of `highStakes`, which Pending You's schema describes for an approval but the popup was not read to honour; refusing all `action` on a landing card, which would refuse the other bolt's proof steps.

### 2. The check runs before the call, in the card hook

The card hook gains a PreToolUse half matched on Pending You's `post_request` and `update_request`. It knows a crew session and Pending You's server as the PostToolUse half does (`identity`, `is_pending_you`); any other session or server passes untouched. The forms are a table beside `KEYS`, keyed by the same row shapes, and the check needs nothing but the tool's input, plus, for an update, the card's key from its `card.post` entry on this host (`posted()`).

- On `post_request`: a key that is a row's is checked against its row's form; any other key passes.
- On `update_request`: the card's recorded key is looked up. A row's card is refused when the update clears a landing's high stakes (`highStakes` false or null), gives `options` to an `approve` or `review` row, or gives `action` steps to any row but a landing, or a landing step that names the landing. A card with no `card.post` entry on this host, or one whose key is no row's, passes: crew checked its form when it was posted, or it is no row's card.

The refusal is written for the agent that reads it: the form the row's card takes, in the table's words, and what was wrong ("a landing's card is an approval marked high stakes, whose yes has you tell main-level ops to land; this card is an `action`"). Any failure in this half, reading the run record among them, refuses with `crew could not check this card's form: <error>` (`read.1`): a card refused is posted again a moment later, and a card wrongly let through can be withdrawn only by its owner. The PostToolUse half keeps its rule that it never fails a call.

**Joining the other bolt's check.** `a-teams-cards-are-its-conductors` adds a PreToolUse half to this same file and an entry to `hooks.json`. Whichever bolt lands second carries itself onto main with one PreToolUse half and one entry, matched on `post_request`, `update_request` and `create_area`. The key check runs first, then the form check, and the first refusal is the one printed. Both are pure functions of the input, so the join is a merge, not a redesign.

Alternatives: a separate hook file, which would split the row shapes across two files; the check in `plan.py`, which needs no plan read and would only add an import.

### 3. The briefs name the form

The conductor's *Cards* gives each row its kind: the review card a `review`, the verify card a `choice` or `multi` of the conductor's options, the landing card an `approve` with `highStakes` true and never an `action` or a command to land. The planner's *Cards* gives the proposal card `approve`. `cards_how()` replaces "give it the row's answers as its options" with the form in one sentence: the kind its row takes, as your brief says, and crew refuses another form, naming the one to use. That keeps the four forms in one place per brief.

### 4. The operator agent posts no card, and adds nothing to a carded wait

*When an agent waits on the user* in `operator.md` becomes:

- The operator agent posts no Pending You card and makes no area, whatever a Pending You reminder in its session says. The team's conductor and the planner ask the user on cards, and the operator agent's part is to make sure the user sees a wait that has none.
- When a wait it is told of is a unit in review, a verify report or a landing, it reads that row's `card:` line in `crew rail --label <label>`. When the card is open, it sends nothing: no notification, and no line to the user unless the user asks what waits.
- A wait with no card, a question asked in a pane, or a row whose card is not open, is shown as today: `herdr notification show …` and one line to the user on what it needs and where.

A conductor with Pending You's tools already sends no tell for a carded wait (`rail-cards`, "The conductor's tell to the operator agents is for what has no card"), so the rail read catches the rest: a conductor whose tools dropped after it posted, or a stale tell.

Alternative: a crew check refusing the operator agent's notification for a carded row. It would need the rail's survey of every host inside a hook. The card the operator might post is refused by the other bolt's key check, so the double card is caught there, and an extra notification is noise, not a second question.

## Risks / Trade-offs

- [Pending You's server may set `highStakes` from `approve.risk` "high" and ignore a bare `highStakes` on an approval] → *Proof in dev* checks that the landing card is hold-to-approve in the app and refused by key in the popup. If it is not, the form changes to the field that works, as a fix.
- [A conductor whose brief is older than the hook posts a review card as `approve`] → the refusal names the form, and the agent posts again in the right one. Briefs are filled at each agent's start, so a running conductor learns it from the refusal.
- [The two bolts' PreToolUse halves meet in one file] → whichever lands second joins them (decision 2). Each is a small function, and both bolts' tests cover the joined hook.
- [An update on another host than the post's isn't checked] → a card is posted and updated by the same session, on one host.

## Proof in dev

Worked after the bolt lands and every host has pulled, on swancloud first:

1. The next bolt a crew team proves: its landing card in Pending You is an approval with no Done button and no land command, it is refused from a key in Herdr's popup, and holding the button in the app has the conductor tell main-level ops to land.
2. The next unit in review: its card answers "Looks good" or "Needs changes", and a note on "Needs changes" reaches the conductor, which runs construct again with it.
3. In a conductor's pane on mac-studio, ask it to post its landing card as an `action`: crew refuses it before Pending You is called, naming the approval form, and `list_pending` holds no new card.
4. The next wait a conductor tells the operator agent of while its card is open: the operator agent shows no notification and posts no card.

## Task notes

### 1.1

In `plugin/hooks/cards`, beside `KEYS`: a `FORMS` table from each row shape to its form (kinds allowed, `highStakes` required, options required or refused, steps refused or allowed), and `form_refusal(key, given, update=False)` returning `None` or the refusal's words. Read every field with an `isinstance` check first (`read.2`): `kind` a string in the row's kinds; `options` a non-empty list counts as options; `action` a dict whose `steps` is a non-empty list counts as steps; `highStakes is True` counts as high stakes; `questions` present refuses. On an update, `kind` is absent and is not checked; a landing card is refused for `highStakes` present and not `True`. A landing step names the landing when its `text` or `command` contains `bolt land` or `wt merge`. Words per decision 2, one for each wrong thing, naming the row's form as the conductor's and planner's briefs word it.

### 1.2

In `plugin/hooks/cards`, `main()`: when `hook_event_name` is `PreToolUse` (read with `.get`), and the tool is Pending You's `post_request` or `update_request`, and the session is crew's (`identity`): for `post_request`, `keyed(tool_input["idempotencyKey"])`, and for `update_request`, `posted(record, label, requestId)`; a row key goes through `form_refusal`. On a refusal print the deny object (Context, Claude Code's hooks) with it as `permissionDecisionReason`; on `None` print nothing. Wrap this half so any exception denies with `crew could not check this card's form: <error>`; leave the PostToolUse half and its never-fail rule as they are. In `hooks.json`, add a `PreToolUse` entry matched on `mcp__.*__(post_request|update_request)` running the same file, `timeout` 10, beside the `AskUserQuestion|ExitPlanMode` entry, and say in the description that crew refuses a row's card in another form. Update the module docstring for both halves.

### 1.3

In `tests/t-cards.sh`, a `pre` helper beside `call` giving `hook_event_name: "PreToolUse"` and no `tool_response`, and cases each asserting the deny object and a phrase of its reason, or empty output: a landing card as `action` with the land command; a landing `approve` without `highStakes`; a landing `approve` with `highStakes` true passing; a landing `approve` with `highStakes` and a step `crew bolt land y` refused, and with a step "Open the gateway on your Mac" passing; a review card as `approve` refused and as `review` passing; a review card with options refused; a verify card as `approve` refused and as `choice` with two options passing; a proposal card as `approve` passing and as `action` refused; a row card with `questions` and no kind refused; a card keyed `agent-note-1` as `action` passing; an update setting `highStakes` false on a landing card recorded by an earlier post refused, and an update of its title passing; an update of a card with no post entry passing; a session crew did not start and another server's tool printing nothing. Update the opening comment. If the test now reads a file it did not, add it to `# Reads:`, run `tests/moon-tasks` and commit `tests/moon.yml`.

### 2.1

`plugin/roles/conductor.md`, *Cards*: in the review line, "offering approval, with a note for changes" becomes a Pending You `review` card, looks good or needs changes, with a note; in the verify line, a `choice`, or a `multi` when the user may pick several findings, whose options are what you would do; in the landing line, an `approve` card with `highStakes` true, never an `action` and never a step or command for the user to land it, since its yes has you tell `{{MAIN_OPS}}` to land. In the answers paragraph, "Needs changes" with its note runs construct again with the note's words. `plugin/roles/planner.md`, *Cards*: the proposal card is a Pending You `approve` card, with a note for changes or for dropping it.

### 2.2

`cards_how()` in `plugin/lib/crew.py`: replace "give it the row's answers as its options" with one sentence in these words or close: "give it the form its row takes, as your brief says, with `blocking` false: crew refuses a row's card in another form, and names the form to use." Leave the rest of the text alone.

### 2.3

`plugin/roles/operator.md`, *When an agent waits on the user*: decision 4, in the brief's plain words. Name `{{TEAM_CMD}} rail --label {{LABEL}}` and its `card:` line; keep the `herdr notification show` command as it is for a wait with no card.

### 2.4

`tests/t-briefs.sh`: pin a phrase of 2.1 in the filled conductor and planner briefs, of 2.2 in both, and of 2.3 in the filled operator brief ("post no Pending You card", and the rail's `card:` line), as the file pins the others (`tests.6`).

### 3.1

`docs/architecture/briefs.md`: in `briefs.13`'s detail, drop the sentence that the hook refuses no form and the operator's brief shows a notification Pending You's prompt hook turns into a card until this unit lands, and name `plugin/hooks/cards` (`form_refusal`), `plugin/roles/operator.md` and `tests/t-cards.sh` among its sources. `docs/architecture/_open.md`: remove the item for `briefs.13` and the operator agent. `README.md`, the cards paragraph: one sentence that each row's card has its row's form, a proposal's and a landing's an approval, the landing's high stakes, a review's a review, a verify report's a choice of the conductor's options, and that crew's hook refuses a row's card in another form before Pending You sees it. No command changes, so the usage and the skill stay as they are (`docs.2`).
