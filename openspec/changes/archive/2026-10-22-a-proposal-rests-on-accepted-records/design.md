# Design

## Context

`crew plan propose` (`plan.py` `plan_propose`) checks a proposal by applying its `Do` lines in order to a copy of the plan at the tip (`check_ops`, `plan.3`). Then it writes the proposal open and raises its card in the planner's name. Nothing in that check reads a decision record. Records live in each kit's `docs/adr/`. Only `crew record` reads their status today (`record_status`, `record_facts`). It reads the frontmatter's `status:`, and an accepted record with a paragraph still marked "Status: proposed" past its own status line counts as proposed.

The design agent's brief already says to queue no unit from a proposed record or amendment, and to cite none as a unit's source (`briefs.15`; `design.md`, *Decision records*). The planner's brief says nothing about it. Proposal 161 cited records 0033 and 0034 while both were still proposed. On main today both read `status: rejected`.

This change touches the area of `plan.md` (`plugin/lib/plan.py`) and of `docs.md` (README). It relies on `roles.3`, `briefs.15`, `plan.3`, `plan.12`, `plan.18`, `read.1`, `read.2`, `code.2` and `code.7`, and departs from none.

## Goals / Non-Goals

**Goals:**
- No proposal is written, and so no card raised, whose new bolts or new units rest on a record the user has not accepted (`roles.3`, applied to `briefs.15`).
- `crew record` and the proposal check read a record's status in one way, from one function.

**Non-Goals:**
- The design agent's direct `crew unit add` into a queue is not checked here. Its brief governs it, and the intent covers proposals only. A unit queued that way is still read when a proposal moves it into a bolt.
- Approval does not read records again. A record accepted when the proposal was written does not become unaccepted. Amending or rejecting an accepted record is the design agent's turn, and a proposal on it waits on the user anyway.
- Records named only in words ("record 0026 point 4") are not read. There is no grammar that ties such words to a kit.
- No change to the briefs, the board's views (`code.8`: nothing crew models changes) or the plan's schema.

## Decisions

### 1. The check runs when the proposal is written, from the checked copy

The check runs inside `plan_propose`'s `change(w)`, after `check_ops` has returned the copy of the plan as the proposal's commands leave it, and before `open_proposal` takes a number. So a refusal writes nothing and raises no card, like every other refusal of a proposal (`plan.3`). It is also recorded the same way.

The work read is every bolt a `bolt new` creates and every unit or chore `cards.new_units` names: the ones the proposal adds, to a bolt or the queue, and the ones it moves into a bolt. Those are the units the card asks the user about, the first the user hears of them. Their sources are read from the checked copy. That covers a `unit add` sourced in the same proposal and a moved unit sourced long ago, and leaves `--signal`'s prepended `signals/…` source as it is, a source that names no record.

*Alternatives:* checking at approval as well, which would read every kit again for a status that cannot go back to proposed. Checking every unit the proposal touches, which would refuse a reorder of units the user approved long ago.

### 2. A record is recognised by its path

A source names a record wherever it holds `docs/adr/` followed by four digits, which is how every record cited in the partitions' plans is written today (read 2026-10-22 on `swancloud/main` and `madswan/main` of crew-state): `docs/adr/0033-….md`, `docs/adr/0032`, `docs/adr/0029 (accepted 2026-10-14); …`. An `<owner>/<name>` right before it, followed by `:` or a space, names the repository (`afterthought/crew:docs/adr/0010-….md`, `agentplot/sluice docs/adr/0026`). Otherwise the record belongs to the kit of the bolt or unit, its `Repo`. That kit's repository is read from the teams file (`kit_teams`, the team's `kit["repo"]`, `code.5`).

This is a pure function from a source's text and the item's kit to the records it names (`code.7`).

*Alternative:* also reading "record NNNN" in prose. Rejected, because "wldn record 0069" and "sluice's record 0017" appear in crew's own sources, and crew cannot tell from the words alone whose record they mean.

### 3. A record is read on GitHub's main through crew's cache

For each repository named, crew fetches `main` over https into its bare cache (`fetch(repo, "main")`, `url`, `cache`), lists `docs/adr/` at that tip and shows the one file numbered so. This is the same way it reads the state repository and the signals repository's main. `READ` holds each tip for the command, so a repository is fetched once however many sources name it, and replays of the write fetch nothing again (`plan.12`).

A proposal's check is a decision of the moment, so it reads main now after a fetch (`plan.18`). That way a record the design agent has just landed accepted is seen at once, without waiting for the timer to move a host's anchor.

*Alternatives:* the team host's `gather`, which already runs for a new unit's name check (`name_free`). It reads `origin/main` only as the host last fetched it, it cannot reach a repository no team builds (such as `agentplot/sluice`), and adding records to it would mean a second shape for `gather.py`, which older crews on the hosts also run. The other alternative is `crew record`'s read of the kit's checkout on the main level's host. A proposal is not bound to that host: the user may propose from any shell.

### 4. One reading of a record's status

`record_facts`'s inner `split` and `held` move out to module level as `record_status_held(md)`. It returns the frontmatter's status and whether an amendment is still marked proposed. `record_facts` calls it, unchanged in behaviour. The proposal check calls it too. A record is accepted only when its status is `accepted` and no amendment is marked proposed. Otherwise main's words for it are those `crew record` already prints: "proposed", "rejected", "accepted, with an amendment still marked proposed", "no status in its frontmatter".

An accepted record with an amendment still proposed refuses the proposal, whichever part of the record a source cites. The design agent's brief rules out citing a proposed amendment, and `crew record` already treats such a file as proposed. A unit citing an accepted part waits only as long as the amendment does.

### 5. What the refusal says

One refusal names every record not accepted, one line for each, so the planner sees them all at once (`code.2`):

```
crew refuses the proposal: it rests on records the user has not accepted.
  unit a-bolts-unblocker-is-built-whatever-slots-its-team-has names record 0033 of crew: crew's main holds it rejected
  bolt a-team-of-one-slot-lands-its-bolt names record 0034 of crew: crew's main holds it rejected
Propose it once each record is accepted on its kit's main.
```

Main holding no file by that number says "crew's main holds no record 0040 in docs/adr/". Two files say "crew's main holds 2 records numbered 0040: …". A fetch that fails, or a main GitHub does not have, refuses with git's words and the repository's name (`read.1`). A file that cannot be decoded as text refuses naming the file (`read.2`).

## Risks / Trade-offs

- [The first proposal naming a kit's record fetches that kit's whole history into crew's cache, on that host] → It happens once per host, and later fetches are incremental. crew's and swancloud's histories fetch in seconds over https. A kit large enough to come near the two minutes an agent's shell gives a command (`code.9`) would show here first, and the fetch could then be narrowed with a blob filter.
- [A record cited in words is not checked] → The design agent and the planner both cite records by path. The words form is used only for other partitions' and other tools' records, which crew cannot resolve anyway.
- [A record under a path other than `docs/adr/`] → Every kit's records are in `docs/adr/` (`docs.1`; the design agent's brief). A kit that kept them elsewhere would not be checked. That would be a change to `docs.1`, not to this check.

## Migration Plan

None. Open proposals stay open. The check applies to every proposal written after the change reaches a host, `--replaces` rewrites among them.

## After deploy

None. Every scenario is proved by the logic and end-to-end tiers, and nothing about a live host is assumed beyond GitHub over https, which every plan read already depends on.

## Task notes

**1.1** `plugin/lib/plan.py`: move `record_facts`'s inner `split` and `held` to module level, `record_split(md)` and `record_status_held(md)`, the latter returning `(status, marked)` as `held` does now. Add `record_says(status, marked)`, giving the words `record_facts`'s `says` gives, and `record_accepted(status, marked)`. `record_facts` keeps every refusal and its words. Its cases in `tests/py/test_cards.py` (`record_facts`, around line 1466) pass unchanged, which is the proof.

**1.2** `plugin/lib/plan.py`: `record_refs(source, kit_repo)`, a pure function, returns `[(repo, number)]` in the order they appear, each once. It uses the regex `(?:(?<![\w./-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)[:\s])?(?<![\w./-])docs/adr/(\d{4})(?!\d)`, where the repository is group 1 when present and `kit_repo` otherwise. The lookbehinds keep a path's tail from being read as a repository, or `other/docs/adr/` as a record. Cases in `tests/py/test_proposals.py`, class `TestRecordSources`: a path with its file name; a bare `docs/adr/0032`; `docs/adr/0029 (accepted …); docs/architecture/core.md read.5` naming only 0029; `docs/architecture/core.md docs/adr/0001` naming 0001 of the kit, not of a repository `architecture/core.md`; `afterthought/crew:docs/adr/0010-….md` and `agentplot/sluice docs/adr/0026 (branch create and delete)` naming their repositories; `record 0026 point 4`, `docs/architecture/plan.md plan.16` and `signals/…` naming none; two records in one source.

**1.3** `plugin/lib/plan.py`: `unaccepted(items, held)`, a pure function. `items` is `[(kind, name, kit, repo, number)]`. `held` maps `(repo, number)` to `{"files": [...], "status": s, "marked": bool}`, or to `{"why": text}` when it could not be read. It returns the refusal's text, as Decision 5 shows, or `None` when every record is accepted. A `why` entry, a missing file and two files each give their own line. Cases in `tests/py/test_proposals.py`, class `TestRestsOnAccepted`: proposed, rejected, accepted with a marked amendment, no status, no file, two files and could-not-read, each refused with its words; all accepted gives `None`; a unit and a bolt naming the same record are both named; the kit is named by its name, and the repository by `<owner>/<name>` when it is not the item's kit.

**1.4** `plugin/lib/plan.py`: `proposal_records(fleet, label, scratch, argvs)`. It collects the items from `argvs` (`bolt new` bolts, then `cards.new_units(argvs)`), reads each one's `Repo` and `Source` from `scratch.plan`, maps the kit to its repository with `kit_teams(fleet, kit, label)`, and the records with `record_refs`. Then come the thin reads (`code.7`): for each repository, `fetch(repo, "main")`, where `None` gives the why "<repo> has no main on GitHub" and a `Refusal` gives its words; `git(repo, "ls-tree", "--name-only", tip, "docs/adr/")` filtered by `docs/adr/<n>-*.md`; and `show` of the one file, with its status read by `record_status_held`. A decode failure gives a why naming the file. It returns `held` for `unaccepted`. `plan_propose`'s `change(w)` keeps the copy `check_ops` returns and calls `fail(unaccepted(...))` when it says something, before `open_proposal`. The logic is proven by 1.2 and 1.3. The wiring is proven by 1.5.

**1.5** `tests/t-journey-plan.sh`, after the first proposal's steps: commit to the switchboard-kit's origin (the bare remote `kit` made, by a clone and push in the test's scratch) `docs/adr/0001-a-record.md` with `status: proposed`. Propose `unit add rests-on-a-record "…" --repo switchboard-kit --source docs/adr/0001-a-record.md` and expect a refusal that names `rests-on-a-record`, `record 0001 of switchboard-kit` and `holds it proposed`, with the tip of `wldn/main` unchanged and no card posted. Then push the record as `status: accepted`, propose again, and expect `is open`. The test reads no new path, so `tests/moon.yml` is unchanged. Run `tests/suite t-journey-plan`.

**2.1** `README.md`, the `crew plan propose` bullet under *Proposals*: one sentence after "…nothing is written." saying that a proposal is also refused when a bolt it creates, or a unit or chore it adds or moves into a bolt, names as a source a decision record (`docs/adr/<number>`, of its kit or of `<owner>/<name>:`) that its main on GitHub does not hold accepted, naming each record and what main holds. `tests/t-docs.sh` holds README's commands to the usage, and no command or flag changes, so the usage and `plugin/skills/crew/SKILL.md` stay as they are (`docs.2`). Run `tests/suite t-docs`.
