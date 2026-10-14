## Context

The rule is `briefs.15` (`docs/architecture/briefs.md`): a decision record the design agent writes or amends is committed as proposed and put to the user on one card in the record's own words, accepted only on the user's yes and recorded so; what the user settled in their own words in the design talk is recorded as their decision, and the card says so. Its details rule out a record committed as accepted on the design agent's reading, a rule amended from an unaccepted record as if settled, and a unit queued from one. `_open.md` names this unit as the one that makes `design.md` say it.

What stands today, on crew's main:

- `plugin/roles/design.md` says to record a decision in the kit's `docs/adr/` and commit it, with nothing about the user's yes. The brief carries no card discipline: `{{CARDS}}` is filled only into the planner's and the conductors' briefs.
- `plan.card_refusal` refuses every card from the design agent: "wldn-design owns no card key, since only the planner and the conductors post cards" (`tests/t-cards.sh`).
- The hook (`plugin/hooks/cards`) records a card under a key that is not a row's on `agent/<agent>` with no `Key`, and `crew rail` lists every open card that matches no row under "open cards with no row", with a tell asking its owner to close it.
- The records the design agent has already put to the user, 0019 and 0020, and 0016 put back to proposed, already follow the practice by hand: frontmatter `status: proposed`, a `Status:` line saying it was proposed to the user and is accepted only on their yes, and rules drawn from them marked "(Proposed <date>, record <n>, on the user's card; accepted only on their yes.)" (`teams.16`, `docs.7`, `read.5`).

The sibling unit `any-question-for-the-user-gets-a-card` (crw-3's bolt) leaves this card to this unit: its design names "The design agent's card for a decision record (`briefs.15`): that is `a-record-is-accepted-on-the-users-yes`'s", and has the design agent's other questions go through the planner.

Rules this design relies on: `briefs.15`, `briefs.9` (a card's words are the document's own; a document on a card is inline Markdown), `briefs.11` (one voice; crew refuses a row's card under another owner's key), `briefs.13` (no command for the user; no required words question), `roles.1` (the design agent queues), `roles.2` (an approval only on the user's word), `roles.4`, `state.3` (the design agent's records on main), `state.4` (the rail computed, nothing written), `read.1`, `code.2`, `code.4`, `code.6`, `tests.6` (a brief's rule is pinned in `t-briefs.sh`), `docs.2`. Pages whose area the change touches: `briefs.md` (`plugin/roles/`, `plugin/skills/`), `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/bin/crew`), `tests.md` (`tests/`), `docs.md` (`README.md`). The change edits nothing under `docs/` (`docs.7`, proposed).

## Goals / Non-Goals

**Goals:**

- The design agent's brief makes it propose every record and amendment on one card and accept it only on the user's yes, as `briefs.15` says.
- crew lets the design agent post exactly that card, checks its form, records it, and shows it on the rail as something waiting on the user.

**Non-Goals:**

- A rail row read from the kits' records (a proposed record found on a kit's main): the record's card is the user's way in, and reading every kit's `docs/adr/` on every rail read is more than the rule asks.
- A check that refuses a record committed as accepted without a card: the design agent commits on the kit's main outside crew, where crew has no hook; named for the design agent.
- Any change to how the planner, the conductors or other agents post cards, or to a row's card form.
- Settling records 0016, 0019 and 0020: that is the user's, on the cards the design agent posts.

## Decisions

### D1. The design agent posts the record's card itself

The card's yes is what the design agent records in the record, the card carries the record's words, and a note asking for changes is work for the design agent alone. Sending it through the planner, as the sibling does for the main level's other questions, would add a relay that carries no decision. Record 0019 (proposed) also has the design agent post its own conclusion card. So the record card is the one card the design agent posts, and its brief says so.

Considered: the planner posts it under its question key. Rejected for the relay, and because the planner would then have to tell the design agent the user's words before anything is recorded.

### D2. The key is `record/<kit>/<number>/<commit>`

`<kit>` is the kit's name as the teams file gives it (`kit.name`, matching `code.4`), `<number>` the record's four digits, `<commit>` the first seven hex digits of the kit's main commit that proposed the record or the amendment. The commit plays the part a landing card's head plays (`land/<bolt>/<head>`): a revision after a note is a new commit and so a new key and a new card, and Pending You never hands back the answered card for a new version. The key's object, for the run record, is `record/<kit>/<number>`.

The check reads only the teams file it already holds: the caller is the partition's design agent and the kit is one its partition's teams build. Nothing else is read, so nothing can fail to be read (`read.1`). Every other crew agent posting under a record key is refused as it is today, since the key is no row of its own.

Considered: `ask/<design agent>/<slug>`, the sibling's question key. Rejected: the key would not say which record or which version, so a revision could reuse an answered card's key.

### D3. The card is a low-risk approval in the record's words

Kind `approve`, approve block `{"action": "Accept record <number>: <title>", "risk": "low", "reversible": true}`, no options, no steps, `blocking` false. A record can be amended again, so it is reversible; it neither spends nor goes public. The hook checks this form as it checks a row's (`FORMS`), refusing another kind, a risk other than low, options or steps, and a change that takes the card out of the form.

Its words, by `briefs.9`'s rule that a card says the document's own words and carries no path:

- Title: "Accept decision record <number> in <kit>: <the record's title>?" (an amendment: "Accept the amendment to record <number> in <kit>: <the amendment's lead words>?").
- Summary: the record's opening sentences, whole ones, as many as fit in 400 characters.
- Background: the record's decision as the record words it (for an amendment, the amendment's words), then, when the record quotes the user's words from the design talk, "Your own words, recorded as your decision:" and the quote.
- One artifact: the whole record (or the amended clause) as a `code` artifact of lang `markdown`, which Pending You renders (`briefs.9`, ADR 0005 as amended 2026-10-10).
- No plannotator session: a record is not among what `briefs.9` gives one to, and the card holds it whole.

### D4. What the design agent does on each answer

The brief says, and the card states the yes as accepting:

- **Before the card**: the record is committed with frontmatter `status: proposed` and a `Status:` line, "proposed to the user on <date>, as `briefs.15` has it; accepted only on their yes". A rule drawn from it is written with "(Proposed <date>, record <number>, on the user's card; accepted only on their yes.)". An amendment to an accepted record is marked proposed where it stands in the record, with the same words. No unit is queued from either.
- **Yes**: one commit sets `status: accepted` and the `Status:` line to "accepted by the user on <date>, on their card", with any note quoted, and removes the proposed mark from each rule drawn from it. Then the units it calls for are queued, citing it. The card is closed with `ack_answer` and the commit.
- **A note asking for changes**: the record is revised, still proposed, committed, the card closed with `ack_answer` saying what changed, and a new card posted under the new commit's key.
- **No**: one commit sets `status: rejected` with the user's words and removes each rule drawn from it; the card is closed with `ack_answer`.
- **The user's words from the design talk**: the record's deciders line quotes them as the user's decision, as records 0019 and 0020 do, and the card's background names that part as theirs. The card is still asked: the user's words settle what they said, the record's other words are the design agent's.

At its start the design agent calls `whoami` and `list_pending`, acts on any card the user answered, and posts a card for each proposed record or amendment of its kits that has none open, unless the record says it waits on another record's answer. It files a card in its kit's area, found with `match_area` from the kit's git remote or made with `create_area` under `create-area:<owner>/<kit>`, which `card_refusal` already lets the main level make. It hears an answer by being woken in its pane, never runs `npx pendingyou` or `pendingyou hold`, and leaves every other agent's card alone.

### D5. The rail lists open record cards apart

`crew rail` keeps its four groups as they are. After them, before "open cards with no row", it prints "decision records waiting on you:" with each open card under a record key: when it was posted, how long ago, its key, its partition and who asked it. No command: the card is where it is answered. A record card is never in the stray list. A record card whose host's record did not answer is left out as a stray card is today.

### D6. The brief's words are in `design.md`

The decision-record section and its card discipline go in `plugin/roles/design.md` itself, filled from tokens main levels already have (`{{LABEL}}`, `{{TEAM_CMD}}`, `{{KITS}}`), not in `crew.py`'s shared card discipline, which speaks of rail rows the design agent does not have. The paragraph "When a design picks one approach over named alternatives ... record it as a decision record" gains the proposal; "When the talk settles something, record it and commit" says a record it writes is proposed and put on a card.

## Risks / Trade-offs

- [Overlap with `any-question-for-the-user-gets-a-card`, in crw-3's bolt] Both edit `card_refusal`'s design-agent refusal, the hook, the rail's text, `design.md`, README and `t-cards.sh`. → Whichever lands second carries it. The two agree: the sibling sends the design agent's questions through the planner and names this card as this unit's exception; the design agent's refusal text should then name both the record key and the planner.
- [Overlap within this bolt] `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out` and `a-batch-cards-notes-are-its-note-and-its-sessions` edit the hook's `FORMS` and `t-cards.sh`; `a-cards-session-ends-with-its-card` edits the rail's text in `plan.py`. → The record form is its own entry and the record heading its own block, so the merges are mechanical.
- [The design agent commits a record as accepted anyway] Nothing in crew sees a commit on a kit's main. → The brief says it; a check would be a hook on the kits' mains, named for the design agent.
- [A card lost to a re-sign-in] As for every card (ADR 0005, "A card belongs to the host's sign-in"). → The start-up pass posts a card for each proposed record with none open.

## Migration Plan

Nothing to migrate. Once the bolt lands and hosts pull, the design agent's next fresh start loads the brief, and its start-up pass posts cards for the proposed records with none open.

## Proof in dev

crew has nothing to deploy: these are worked on real work once the bolt has landed and every host has pulled, as crew's CLAUDE.md says.

- The design agent's first record card, under `record/<kit>/<number>/<commit>`, reaches the user in Pending You without being refused, and `crew rail` lists it under the decision-records heading.
- The user's yes on it wakes the design agent, which commits the record as accepted with the date and closes the card; the rail stops listing it.

## Task notes

### 1.1

In `plan.card_refusal`, before the final refusal, handle `kind == "design"`: a key matching `^record/([a-z0-9][a-z0-9-]*)/(\d{4})/([0-9a-f]{7})$` whose kit is among `{fleet["teams"][t]["kit"]["name"] for t in crew.partition_of(fleet, label)["teams"]}` passes with no fetch. Any other key is refused: "crew refuses a card under <key>: <name> posts a card only for a decision record, under record/<kit>/<number>/<commit> for a kit of <label>'s, <kits as `either` lists them>, the commit the one that proposed the record or its amendment." Add a `RECORD_KEY` pattern beside `CARD_KEYS`; it is not a row key. Every other kind keeps its refusal, so a planner's or a conductor's record key is refused naming its own keys. Update the docstring. `t-cards.sh`: replace the `wldn-design ... owns no card key` line with the design agent passing under a record key of a wldn kit, refused under another partition's kit, under a malformed record key and under `proposal/1`, each refusal naming the form; the planner and a conductor refused under a record key.

### 1.2

In `plugin/hooks/cards`: add the record key to what the PostToolUse half recognises, so a card under it is recorded with `Key` and `On` `record/<kit>/<number>` (today `KEYS` formats one group; give the record entry its object from kit and number). Add `FORMS["record"]`: kinds `("approve",)`, no options, no steps, and the approve block's `risk` must be `"low"` (read from the card's `approve`, or the one question's `approve` when the card is grouped), with `says` naming the form in D3's words. A change to a card whose post named a record key is checked the same way. A record card's close ends no plannotator session (none is started for it): make sure the session-ending path skips it without printing a forgotten session. Update the module docstring. `t-cards.sh`: a record card posted and closed is recorded on `record/<kit>/<number>` with its key; a record card of kind `choice`, with risk high, with options or with steps is refused naming the form; a change adding options is refused.

### 2.1

In `rail_text`, after the groups and before the stray block, list open cards whose key matches `RECORD_KEY` under "decision records waiting on you:", oldest first, each line as the stray lines read (posted at, age, key, label, asked by, host) with no answer line. In `stray_cards`, skip a card whose key matches `RECORD_KEY`. Nothing in `rail_rows` changes. The usage header of `crew rail` (`plugin/bin/crew`) gains "the decision records waiting on you", and the crew skill's rail line says the same. `t-rail.sh`: an open record card in the run record is listed under the heading and not among the cards with no row; a closed one is listed nowhere.

### 3.1

`plugin/roles/design.md`: a section, "Decision records", after "Elaboration on main", holding D4 in the brief's plain words, and the card's words of D3: the key, the form, what goes in the title, summary, background and the one artifact, no path, no plannotator session, and the start-up pass with `whoami`, `list_pending`, the area by `match_area` or `create_area` under `create-area:<owner>/<kit>` in the group `{{LABEL}}`, the wake, never `npx pendingyou` or `pendingyou hold`, other agents' cards left alone. The sentence on recording a decision record in "Elaboration on main" and the one on recording what the talk settles in "Talking design with the user" point to the section. Keep the brief's voice: short sentences, plain English, no rule ids in the prose the agent speaks to the user.

### 3.2

`t-briefs.sh`: pin in `crewpy brief wldn design` the phrases that carry the rule (`tests.6`): committed as proposed, the record key `record/<kit>/<number>/<commit>`, accepted only on the user's yes, the user's own words recorded as their decision, no unit queued before the yes, rejected on a no, and the one card the design agent posts. Pin that the planner's and conductors' briefs do not mention the record key.

### 4.1

README's Pending You paragraph: the design agent posts a card for each decision record it proposes, under `record/<kit>/<number>/<commit>`, an approval of low risk, checked by the hook like a row's card, and `crew rail` lists those cards under their own heading after the groups; the sentence that every other crew agent owns no key, and the list of keys the rail prints, say the record key too. The run-record paragraph's card act names `record/<kit>/<number>` as the object of a record card. `t-docs.sh` needs no change unless a command's words change.
