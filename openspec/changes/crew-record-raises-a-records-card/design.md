# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give a record's card its two forms and the act that sends it; this change adds the command at whose turns it is raised, changed and closed. It relies on `briefs.15` as record 0031 amends it (a record is accepted only on the user's yes, given in the pane or on its one card), `briefs.13`, `briefs.16`, `code.2`, `code.4`, `code.5` (the kit is checked against the teams file alone), `code.7`, `read.1`, `record.1`, `record.3` and `state.4`. It touches the areas of `plan.md`, `record.md` and `teams.md`.

## Goals / Non-Goals

Goals: a record's status recorded through crew at each turn; one card per record, raised only when the record was not settled in the pane, changed in place on a revision, closed with the status; a rule-decided record put to the user as one choice.

Non-goals: the record's forms, which `crew-builds-every-card-from-its-facts` builds; the design agent's brief, which `only-crew-raises-a-rows-card` rewrites; the board's design band, which `the-rail-shows-and-sweeps-every-card` draws from the entries this command writes.

## Decisions

### 1. `crew record`

New: `crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane]`, run by the design agent in its worktree at each turn of a record's status. It records `record.<status>` in the run record with the kit, the number and the commit, and with `--proposed` raises the record's card unless `--settled-in-pane` is given, which records the user's yes as given in the pane and raises nothing. `--accepted` and `--rejected` close the card with the commit. The record's status is read from the file at the commit; a mismatch (`--accepted` on a file still `proposed`) is refused.

| Event | Command | Act |
|---|---|---|
| a record proposed, not settled in the pane | `crew record <kit> <n> --proposed` | post `record/<kit>/<n>` |
| revised | `crew record … --proposed` again at a new commit | change |
| accepted, rejected | `crew record … --accepted\|--rejected` | close |

`raise_record`, the record's raise, reads `record_facts` at the commit, the record's number, title, opening sentences, the user's quoted words and the Markdown, and the alternatives file when one is handed, and calls the act after the status's entry is written, so a status stands whether its card posted or not.

### 2. One key per record

A record's card key is the record's, `record/<kit>/<number>`, not the commit's: `RECORD_KEY` drops the commit, and the card hook's `KEYS` line and the design agent's branch of `card_refusal` follow it, so a post the design agent makes under its brief until the last change rewrites it is checked against the record's key. A revision changes the one card, "Revised: …", naming the new commit.

### 3. A record a rule decided

`crew record … --proposed --alternatives <file>` takes that Markdown from the design agent, which writes it; the design agent's brief says a rule-decided choice is named, never settled silently. Record 0031 §5 is amended to say so. A file the command cannot read is refused, naming it, and nothing is raised.

The card trials' note for the builder, in the recovery session's words: `crew record <kit> <n> --proposed --alternatives <file>` makes a choice card: loosen as drafted / accept as ruled / send back. The design brief gets a rule: "a rule-decided choice is named, never settled silently".

## Risks / Trade-offs

- Until `only-crew-raises-a-rows-card` rewrites the design agent's brief, it still tells the agent to post the record's card itself; the hook checks that post against `record/<kit>/<number>`, the key crew's card was raised under.
