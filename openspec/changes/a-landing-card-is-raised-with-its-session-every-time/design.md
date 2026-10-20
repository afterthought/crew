# Design

## Context

See proposal.md, *Why*. A landing card's reading is started inside the act that builds the card. `raise_land` reads the landing (`land_facts`) and hands it to `row_card_change`, which calls `card_built`. `card_built` asks `CardActs.session` → `reading_open` → `session_open` for the link. On a `Refusal` it prints one line to standard error and builds the card through `unopened`, which says "Its reading could not be opened on the tailnet" and puts why first in the details. Nothing records why. Every path that raises or changes a landing card goes through `raise_land` or `row_card_change`: the merge's end (`landing_after_merge`), the rail's sweep (`RAISES["land"]`), a preview's end (`preview_changed`), and `crew card session land/<bolt>` relinking an open card (`land_session`). `crew card wait land/<bolt>` refuses at once when `card_recorded` finds no session: "no session was started for card land/<bolt>: crew card session land/<bolt> starts one".

The incident shows the cost. crw-2's card was posted at 02:45:03Z and changed at 02:45:27Z, by the preview's end as far as the times show, both without a session and with no reason anywhere anyone can read. `crew card session` opened the reading by hand minutes later. So whatever stopped the raise had passed by then: plannotator not listing within `CARD_START`'s ten seconds on a loaded host, a read the raise made too early, or something in the raising process's environment. This change does not guess which. It makes the raise try a second time the way `crew card session` succeeded, it keeps the reason, and it lets the conductor's own wait recover.

Rules this rests on:

- `briefs.9`: one reading session per landing card, its link in the card's words. Its details say what this unit holds to.
- `briefs.13`: no command on a card for the user to run that an agent can run.
- `briefs.11` and `briefs.16`: crew raises and changes the card itself, in the conductor's name.
- `read.1`: what can't be read is named, never guessed past.
- `plan.18`: main is read as `origin/main` after a fetch.
- `record.1`: one entry per act, done or refused.
- `record.3`: an entry holds crew's own message, never typed text.
- `code.2`: refusals go through `fail()`.
- `code.7`: decisions are functions of facts.
- `code.9`: a long wait is the wait command's own.
- `state.4`, `docs.2`, `docs.6`, `docs.7`.

Pages whose areas this touches: `plan.md` (`plan.py`), `record.md` (`record.py`), `briefs.md` (`conductor.md`, the crew skill), `teams.md` (`plugin/bin/crew`'s usage), `tests.md`, `docs.md` (README, the spec). `code.8` is not engaged: no stage, object or field the agents' views draw changes.

## Goals / Non-Goals

**Goals:**
- Every raise and change of a landing card tries its reading twice before it gives up.
- A card without its reading says why and names the command that starts it.
- The run record keeps why.
- The conductor's wait starts a missing reading instead of stopping.

**Non-Goals:**
- The batch's and the long proposal's sessions. They keep `card_built`'s one try and today's words. Naming that for the planner is enough.
- Finding the incident's cause. It was not kept, and from now on the record keeps it.
- Any change to the card's approval, its face, the preview, or who lands it (`plan.16`).
- A sweep that starts missing readings on its own. The intent settles on `crew card session` and the conductor's wait as the way to start one.

## Decisions

**1. The landing's reading is opened by the raise, twice if it must be, before the card is built.** `raise_land` opens the reading itself through a new `landing_opened` before it calls `row_card_change`.

- **First try:** `acts.reading(label, key, facts)`.
- **On a `Refusal`:**
  1. Fetch the kit's main on the team's host, `kit_git(…, main, "fetch", "-q", "origin")` for a kit with an origin (`plan.18`; MAINS does the same). A failed fetch is said and the try goes on.
  2. Read the landing afresh with `land_facts` under `READ.fresh()`.
  3. If it still reads proven, open the reading again with the fresh facts, and those facts are the card's.
- **When the fresh read finds the bolt not proven:** the raise posts and changes nothing, as `raise_land` already does for a bolt that does not read proven. A fix that started in between withdraws the card through `landing_held`.
- **When the fresh read itself refuses:** the first facts and the first reason stand.

The result goes into the facts as the link (`link`) or as the reason (`unread`). `card_built` changes so that facts which already carry the reading's link or its reason are used as they are, with nothing started. So `row_card_change` and `card_posted` stay one path for every card.

This puts the retry in front of every path that raises or changes a landing card:

- the merge's end, the rail's sweep and a preview's end all go through `raise_land`;
- `land_session` opens the reading itself, as now, and its relink's `row_card_change` gives the running session again.

What to do after the first refusal is a small function of facts with its cases: (first reason, fresh landing or why it could not be read) → try again with these facts / raise nothing / stand on the first reason.

*Considered:* the retry inside `card_built` for every kind. A batch's or a proposal's facts can't be read afresh there, and those cards are not this unit's. *Considered:* a pause before the second try. Nothing read says how long, and the second start already waits its own `CARD_START`. *Considered:* raising `CARD_START`. Nothing shows the start was slow, so a longer timeout would be a guess (`read.1`).

**2. The card names `crew card session` as the conductor's act.** For a `land/` key, `unopened` says the following after the summary's first paragraph: "Its reading could not be opened on the tailnet: the bolt's conductor starts it with crew card session land/<bolt>, and this card then carries its link." The summary is cut to Pending You's budget as now. The details open, as now, with "The reading could not be opened on the tailnet: <why>". The batch's and the proposal's words are unchanged.

The command is written as what the conductor does, and the user is asked to run nothing (`briefs.13`). The user who sees it can tell the conductor through a note on the card. `land_session`'s relink already changes the card to carry the link once the reading opens (`RELINKED`).

**3. Why goes into the run record, on the card's own entry.** `unopened` keeps the reason on the built card (`b["unread"]`). Then:

- `card_posted`'s `card.post` entry records it as `Unread: <crew's message>`;
- `row_card_change`'s `card.update` entry records it the same way, and so does its post when it posts.

`record.py`'s descriptor `%allowed` and `EXTRA` gain `Unread`. The value is crew's own refusal message, which may end with the last line plannotator printed, as `Refused` already carries a tool's words (`record.3`). There is one entry per act, as before (`record.1`). The fact that the reading did not open belongs to the post or the change, so it is not an act of its own. The raising command prints "card land/<bolt>: its reading could not be opened on the tailnet: <why>; crew card session land/<bolt> starts it". This is on standard error as now, so the conductor's merge wait shows it.

*Considered:* a separate `card.session` entry. It would be one more act to read for one fact about a post. *Considered:* reusing `Refused`. That would mark the post itself refused, which the rail's sweep reads (`refused_lately`), and the post was made. *Considered:* a file in the key's card folder. The record is what every host and the signals read, and a host's folder is not (`read.5`).

**4. The conductor's wait starts a missing reading.** `card_wait` for a `land/` key, when `card_recorded` finds no session:

- **The team's conductor holds an open card under the key on this host** (`cards.card_under`): the wait calls `land_session(fleet, label, key)`, which opens the reading as `crew card session` does, prints its link and changes the card in place while it waits on the user. The wait then waits on that session as now.
- **`land_session` refuses:** the wait is refused, "land/<bolt>'s reading could not be opened: <why>; crew card session land/<bolt> starts it once that is mended".
- **No card held:** "no session was started for card land/<bolt>, and no landing card of <bolt> is held on this host".

This covers the raise that could not open the reading. It also covers the wait run again after it printed a decision and forgot the session, which the brief tells the conductor to do and which today finds nothing. Choosing among those three outcomes is a function of facts (session recorded, card held, start refused) with its cases.

*Considered:* a refusal that only quotes the raise's recorded reason. The conductor would still have to run a second command, and the wait it was told to keep running would keep stopping.

**5. Briefs and docs.** `conductor.md`'s landing paragraph says three things:

- the wait starts the reading when none runs and changes the card to carry its link;
- when the wait says the reading could not be opened, the card says so too, and `{{TEAM_CMD}} card session land/<bolt>` starts it once what the wait named is mended;
- a card raised without its reading names that command.

The crew skill's `crew card wait` row, the usage in `plugin/bin/crew` and `plan.py`, and README's card-session paragraph say the same, together (`docs.2`).

## Risks / Trade-offs

- [The second try fails for the same reason as the first, if the cause lasts longer than one start] → The card says so and names the command, the record keeps why, and the conductor's next wait tries again.
- [A raise now takes up to two of plannotator's starts, about twenty seconds, inside the merge's wait] → That is the wait's own time (`code.9`). A raise whose first start works takes no longer than today.
- [The wait changes the card's link after every decision it prints] → That is the open-again behaviour `land_session` already has (`RELINKED`). The user sees one change note, and the reading stays reachable.
- [A crew without `Unread` in its descriptor, on another host, reads a branch day that holds one] → Every host takes crew's main in the same step (CLAUDE.md, *After landing*), as with every field added before.
- [The batch's and the long proposal's cards still try once and keep no reason] → Out of this unit. Named for the planner.

## After deploy

- The next real landing card raised on mac-studio after this lands carries its reading's link, or the run record's `card.post` entry for its key holds `Unread` with why. The doer is swancloud-ops, once a landing card is raised, reading the entry with `crew events` or `recsel`. No check in crew's tiers reaches a real plannotator on a loaded host.

## Task notes

**1.1** `landing_retry(why, fresh, fresh_why)` or a similar pure function. It takes the first refusal, the landing read afresh (`land_facts`' `(facts, why)`), or the `Refusal` text when that read failed. It returns `("again", facts)`, `("none", None)` (the bolt no longer reads proven) or `("stand", why)`. Cases in `tests/py/test_landing.py`, `TestTheLandingsPoint`.

**1.2** `landing_opened(fleet, label, plan, b, t, card, acts)` in `plan.py` beside `raise_land`, which calls it after `land_facts` and before `row_card_change`. It returns the facts to build from, with `link` or `unread`, or None to raise nothing. The fetch is `kit_git(fleet, t, t["kit"]["main"], "fetch", "-q", "origin")` when `gather.has_origin(main)`, its `Refusal` printed to standard error and passed over. Only `raise_land` uses it. `land_session` keeps its own one open, because a person ran it and sees its refusal at once.

**1.3** `card_built`: when `facts` already carries `READING[kind]` with a value, build from it and start nothing. When it carries `unread`, return `unopened(build(facts), facts["unread"])` and start nothing. `unopened` keeps the reason as `b["unread"]`, and for a `land/` key words its summary sentence as Decision 2 has it. Its printed line names `crew card session <key>` for a `land/` key. Update the cases in `tests/py/test_cards.py`:

- `test_a_landing_whose_reading_could_not_open_is_raised_all_the_same_an_approval_as_before` gets the new words.
- Add a case that facts carrying a link or a reason start no session (`ReadingActs.sessions` stays empty).
- The batch's case is unchanged.

**1.4** `raise_land` through `ReadingActs`: a first refusal then a link makes two `reading` calls and the card carries the link. Two refusals give a card that names `crew card session land/b1` and `unread` set to the second reason. A fresh read that is not proven posts nothing. `ReadingActs` gains a list of refusals given in turn; `refused` stays as the always case. The fetch and `land_facts` are reached through the act or monkeypatched, as `test_landing.py` already does for the kit's reads.

**2.1** `record.py`: `Unread` in `DESCRIPTOR`'s `%allowed` and in `EXTRA`, with its sentence in the comment that lists the extra fields ("a card act's … Unread, why its reading could not open"). `card_posted` and `row_card_change` pass `Unread=b.get("unread")` on their `card.post` and `card.update` emits (`emit` drops an empty one). Cases in `tests/py/test_cards.py` on `ReadingActs.emitted`: a post and a change whose reading failed carry `Unread`, and one whose reading opened does not. If a contract or logic case pins the descriptor's field list, update it.

**3.1** `card_wait` for `land/`, Decision 4: a pure `land_unstarted(recorded, held)` → `"start"` / `"none"`, plus the refusal words when the start refuses, with cases beside `waited`'s in `tests/py/test_cards.py`. Then the wiring: `land_session` is called when the answer is `"start"`, and its `Refusal` is turned into the wait's refusal naming `crew card session` (`code.2`). The wait then reads `card_recorded(d)` again and goes on as now.

**4.1** `conductor.md`'s landing paragraph, Decision 5. Check `tests/t-briefs.sh`'s conductor lines (they want `card wait land/<bolt>` and `card session land/<bolt>` present). Keep them green, adding a want for the new sentence if the file's other paragraphs have one each.

**4.2** `plugin/skills/crew/SKILL.md`'s `crew card wait` row, the `crew card session|wait|end` entry in `plugin/bin/crew`'s usage and `plan.py`'s, and README's card-session paragraph, where it says what the wait does for a landing and what a card whose session could not start says, all together (`docs.2`). `tests/t-docs.sh` stays green.

**5.1** The stub plannotator gains a way for a test to refuse its next starts: a count in `$HOME/.stub-plannotator/refuse-starts`, decremented by each `annotate`, which then exits 1 before registering, printing `stub: refused to start` on stderr. Say it in the stub's docstring. In `tests/t-journey-land.sh`, around the first raise:

- with one refusal set, the merge's end still starts one session and the card carries its link;
- later, before the fix's re-raise, with two refusals set, the re-raised card says its reading could not be opened and names `crew card session land/tenant-environments`, and the box's run record holds a `card.post` for that key with `Unread`;
- the conductor's `crew card wait land/tenant-environments`, run in the background with refusals cleared, starts the session, the card's `update_request` carries the new link, and the wait waits. End it as the test ends other waits.

If the test now reads a file it did not, add it to `# Reads:` and run `tests/moon-tasks`, committing `tests/moon.yml`.

**6.1** Run `tests/suite logic`, then `tests/suite t-journey-land t-briefs t-docs t-cards t-journey-review` by name, then `tests/suite --affected` once at the end. The stub's change makes every end-to-end test affected, since `tests/stubs/` is in every task's inputs.
