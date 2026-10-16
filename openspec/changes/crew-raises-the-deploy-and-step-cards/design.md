# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give the deploy's and the step's cards their forms and the act that sends them; this change raises, changes and closes them at the operations' own acts, in `ops.py`. It relies on `plan.14` as amended on main 614cd85 and by record 0031 (a deploy offered by the kit's deployer, its card main-level ops's, the notes the kit's own), `roles.2` (a `manual` deploy runs on the user's word through its card), `briefs.3` (crew reads the kit's notes as text handed to it and makes none), `briefs.11`, `briefs.13`, `record.3` (no entry holds text anyone typed), `code.2`, `code.7`, `code.9` and `state.4`. It touches the areas of `plan.md`, `briefs.md` and `tests.md`.

## Goals / Non-Goals

Goals: one card per environment's open offer, raised and changed by the offer and closed at the deploy's end; one card a step, the user's or held, raised one at a time; the release notes and steps on the deploy's face exactly as the kit hands them.

Non-goals: the cards' forms, which `crew-builds-every-card-from-its-facts` builds; the deployer's side, swancloud's.

## Decisions

### 1. The operations' acts and their cards

| Event | Command | Act |
|---|---|---|
| a deploy offered | `crew ops offer` | post `deploy/<env>`, or change when a newer head is offered |
| the deploy ends or fails | `crew ops record --act end` | close with each step's outcome, or the failed step and its log |
| a step the user's, or held | `crew ops step --state waiting --doer user`, `--held` | post `op/<env>/<n>` |
| done, skipped, done by its agent | `crew ops step --state done\|declined` | close |

`raise_deploy` and `raise_step`, the two kinds' raises, read `deploy_facts` (the environment, the head, the landings since the environment's last deploy, the environments before and after, the steps handed) or the step's words, doer, when, commands and done-when, and call the act after the operation's entry is written, so an offer stands whether its card posted or not. Each asks `follows_of` what it follows: a deploy the landing card that put its head on main, or the declined card of the head before it; a step the deploy's card, or the step card before it.

### 2. What the offer takes from the deployer

crew writes none of the notes: `crew ops offer <env> --to <sha> --from <sha|none> --notes <file> --steps <file>`, with the `--label`, `--to` and `--from` the deployer already passes, takes them from the kit's deployer, the notes file git-cliff's Markdown for the range from the environment's last deployed commit to the offered one, the steps file one step a line in the shape the deployer's `after-deploy.awk` prints (`step <n> <doer> <when> <environments> <why> <text>`, `held` among the when words); an offer with neither flag carries the landings' subjects alone, as a kit that hands no notes. The offer keeps the files it was handed beside its entry in crew's state on the host, so the card is built again the same when a newer head changes it or the rail posts it again; the run record holds none of their text (`record.3`). A file the offer cannot read is refused, naming it, and nothing is offered (`read.1`).

The card trials' note for the builder, in the recovery session's words: `crew ops offer <env> <sha> [--notes <file>] [--steps <file>]`: the notes are git-cliff's Markdown for the range; the steps use after-deploy.awk's `step <n> <doer> <when> <environments> <why> <text>` shape, with `held` among the when words; with neither, the card shows the landings' subjects. This is the interface swancloud's `a-deploy-offer-hands-its-release-notes-and-after-steps` builds to.

A step's card is built from what `crew ops step` is handed: `--doer`, `--agent`, `--when`, and `--held` for an agent's step held for the user's word, recorded as `held` among its when words; and `--text <file>`, the step's words, then any of `- why: <line>`, `- where: <line>`, `- command: <one whole command>` (one a command, in order) and `- done: <what is seen when it worked>`, in the field-line shape `after-deploy.awk` reads. A text with no field lines is the step's words alone.

### 3. One card per environment's offer

The deploy's row and card key is the environment's, `deploy/<env>`, not the head's: `rows`, `environments` and `open_keys` give it, and a newer head's offer changes the one card in place, "Now offering def5678, which includes abc1234". The deployer's offer runs outside any session, so the act tells main-level ops the line that adopts the card, `call get_request (requestId <id>, name <role>)`, with `crew tell`, as `crew-builds-every-card-from-its-facts`'s hearing has it.

### 4. One step card at a time

One step card at a time: the phone shows one follower of a card until it is answered, so when a deploy ends with several steps crew raises the first, following the deploy's card, and raises each next one, following the one before, when crew closes it (the user: "only saw the one follows"). A step an agent runs on its own has no card. A held step's card is a choice of when, quiet recommended, its now naming the stage agents working on the host as it is raised; main-level ops runs it at once or at the quiet moment as the user picks, and records it declined on skip.

`raise_deploy(fleet, row, acts=None)` and `raise_step(fleet, row, acts=None)` take the rail row, `deploy/<env>` or `op/<env>/<n>` of `row["label"]`, read their facts, return `None` when the row's point has not come, and post through `row_card_change`, so a card Pending You no longer finds is posted again: the operation's own call and the rail's sweep (`the-rail-shows-and-sweeps-every-card`) call them alike.

### 5. Main-level ops's brief

`main-ops.md`'s *Deploying main* says crew raises the deploy's card when the deployer offers and a step's card when a step is the user's or held; that ops adopts one with the line `crew tell` brings it; and what it runs on the answer: `crew ops approve` on a held deploy card, the step's `done` or `decline` on a step's, a held step at once or at the quiet moment as the user picked. It posts and closes no deploy or step card. `tests/t-briefs.sh` pins the words (`tests.6`).

## Risks / Trade-offs

- A kit whose deployer hands no notes, every kit until swancloud's change lands, has the landings' subjects on its deploy card, as before.

## After deploy

1. Main-level ops of each partition restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.
