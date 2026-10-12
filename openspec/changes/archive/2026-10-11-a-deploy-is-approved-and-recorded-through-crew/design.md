# Design

Relies on `plan.14` (a deploy is the deployer's act, a `manual` one on the user's word through the rail's card),
`roles.2` (a deploy runs on the environment's policy, recorded with who approved it), `briefs.11` (main-level ops
posts the deploys' cards), `state.4` (no service: every view reads the run record) and `code.3` (a command forwards to
the host its state lives on). Touches `plan.md`, `briefs.md` and `teams.md`'s area (`plugin/bin/crew`).

**Where the deploys live.** The deployer and main-level ops run where the partition's main level runs, so a deploy's
entries are that host's run record, and every `crew ops` command runs there: run anywhere else, it forwards, as the
one asking (`code.3`). A deploy is never read over ssh from another host: the deployer's `word` reads one host.

**Offer, word and end.** An environment has at most one offer open: the latest offer, until it is approved or a deploy
of it ends. A word is the latest approval until a deploy of its commit ends. So the same offer again writes nothing, a
newer one replaces an unanswered one, a newer offer waits beside an approved one, and an approval of any commit but
the open offer's is refused and recorded.

**The card.** The row's card is main-level ops's (`briefs.11`); crew carries no Pending You client of its own (ADR
0005), so the deployer posts nothing. Holding the card reaches ops's session, which records the word with
`crew ops approve`.

**Quiet.** No stage agent of a team on the environment's host working, read from herdr there, and no test holding one
of that host's test slots (`tests.9`).
