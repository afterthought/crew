# Design

## Context

The proposal says why this change is needed. This section records what was read on deneb on 2026-11-05, so the decisions below rest on it.

**The hosts file.** It is `~/.config/swancloud/herdr-hosts.json`, written from swancloud's `lib/herdr-hosts.nix`; the brief's `teams.json` names no repository. On deneb, both agentplot sessions list `agentplot/boomdrive`, `boomdrive-cloud`, `boomdrive-web`, `flywheel`, `flywheel-next` and `timber`. Neither old name is listed. crew reads this file only through `crew.kit_kept`, for the checkout the partition's main-level host keeps of a kit (`plan.main_kit`; drive-state "What comes before a runner takes a kit's work is done on the main-level host").

**madswan's records on afterthought/crew-state** (crew's cache, `refs/crew/madswan/main` at 11885d63):

| Record | What names the old kits | Can crew rewrite it? |
|---|---|---|
| `plan.rec` | `Repo: tailrace` in 21 Bolt and Unit records, `Repo: flywheel-cloud` in 2 (the bolt `you-sign-in-to-staging` and its unit) | Yes: the plan is intent, written through crew (`state.1`, `state.2`) |
| `plan.rec` Sources | `agentplot/tailrace devenv.nix`, `agentplot/tailrace docs/architecture/core.md`, and so on: free words | Words of intent (see Decision 9) |
| `requests.rec` | Request 1, the launch of `one-seam-turns-every-credential-into-a-principal`, `Repo: flywheel-cloud`; request 2, a retry `Of: 1`, which names no kit | No: requests are never changed (`runner.append_refusal`) |
| `runs/` | Two `bolt.land`, one `card.close` and two `tell` entries with `Repo: tailrace` | No: entries are never rewritten (`record.4`) |
| `proposals.rec` | `Do` lines with `--repo tailrace` and `--repo flywheel-cloud`, all applied | No (`plan.4`) |
| `signals/`, `moves.rec` | Words only. No field names a kit | No (`signals.4`) |
| `asks.rec`, `roles.rec` | Neither file names a kit. An ask names its role and record, and a turn names places by request number. A Role's `Repository` is the partition's first blueprints repository, taken from the teams file (`asks.py` `role_record`) | n/a |

**What the runner's branch says** (`refs/crew/madswan/runner/deneb` at 4a3524e5):
- `answers.rec`: request 1 launched, and request 2 done.
- `places.rec`: request 1's place as last carried, at 00:23:12Z. Flume's status there names the place's repository as `/Users/chuck/.local/share/flywheel/repositories/agentplot/flywheel-cloud`. Answers and places are keyed by request number, and no field names a kit.

**What the runner does** (agentplot/boomdrive at c5bff41, `crates/flywheel-crew/src/lib.rs` `pull_partition`, `read.rs` `kept`):
- It takes a launch only when the launch's `Repo` names an address it keeps.
- A launch naming `flywheel-cloud` is passed over (`Kept::No`), so request 1's place is never carried again.
- Its next pass with the new configuration would also clone the new names afresh and delete the old clones, sluice's records of one-seam's landing among them, unless the clones are renamed first. The rename runbook, `/Users/chuck/.claude-sub-ia/jobs/148214aa/tmp/repo-move-runbook.md` §3.5, steps 3 and 6, covers this.

**Why crew cannot land the bolt today.** It reads a started bolt's kit folder from Flume's status of the newest place a runner carried (`runner.where`, `plan.bolt_at`). After the rename that status still names the old folder.

**The family.** The runbook's §4 lists what each tool holds of a repository's name:
- **swancloud:** a repository's entry names its former names (`formerly`), carried to the views, the sluice drivers and the runner's configuration.
- **The runner:** adopt a clone under a former name, and never delete sluice's records.
- **Flume:** an id that is not the path, and a `flume relocate`.
- **sluice:** relative record paths, and a driver that follows its repository.
- **crew:** two items, taken by Decisions 1 and 10.

Each tool gets its own change. *What this change rests on* names what crew needs from them.

**Area pages this change touches:**
- `core.md`: `state.2`, `state.4`, `read.1`, `roles.1`, `roles.5`, `roles.9`, `code.4`, `code.7` and `code.8`.
- `plan.md`: `plan.1`, `plan.3`, `plan.4`, `plan.12` and `plan.16`.
- `record.md`: `record.1`, `record.3` and `record.4`.
- `signals.md`: `signals.4`.
- `teams.md`: `teams.19`.
- `briefs.md`: the planner's brief.
- `tests.md`: `tests/`.
- `docs.md`: README, the skill and the specs.

No rule changes, so none of the pages is edited (`docs.7`).

## Goals / Non-Goals

**Goals:**

- One act of crew's, on the user's word, renames a kit across the plan. Every Bolt and Unit record names the kit by its name now, and nothing of its work is dropped, added again or launched again.
- Whatever crew recorded under a kit's former name reads as that kit's: requests, the run record, the runner's records of those requests, card keys, and a source's repository. Every view and every decision names the kit once, by its name now.
- Where a runner keeps a kit is read from that runner's report of the repositories it keeps, so a renamed clone is found where it now is.
- madswan's started bolt `you-sign-in-to-staging` keeps its merged unit and lands under `boomdrive-cloud`.

**Non-Goals:**

- Rewriting `requests.rec`, the run record, `proposals.rec`, signals or moves. Each is append-only by rule (`state.1`, `record.4`, `plan.4`, `signals.4`).
- Rewriting the plan's words, its Goals, Intents and Sources, for a rename (Decision 9).
- The other tools' changes: the runner's former addresses and its `repositories.rec`, swancloud's `formerly`, and Flume's and sluice's moves. Each is that tool's own change.
- Landing anything on crew's main, which deploys to every host. This change lands on `teamless/deneb` alone.
- Running the rename on madswan's plan. That is the planner's proposal on the user's word, after deploy.

## What this change rests on

crew's part is complete in this change. The started bolt's landing also needs the following from the family:

1. **The runner (agentplot/boomdrive), R1: a launch's repository is read through its configuration's former addresses.**
   - A launch whose `Repo` names a former address or name of a repository the runner keeps is taken as that repository's launch.
   - That includes a launch it answered before the rename and whose work crew still plans.
   - The runner carries the launch's place again until the place is let go.
   - It goes in `read.rs` `kept` and its caller in `lib.rs`, alongside adopting a clone under a former name (runbook §4, the runner's first item).
   - Without R1, request 1 is passed over for good, and one-seam reads at construct as last carried.
2. **The runner, R2: it reports the repositories it keeps.**
   - On each partition's branch it writes `repositories.rec` with crew's descriptor (Decision 6).
   - Each record names one repository its configuration keeps, by forge address, and the folder of its clone, where Flume cuts its places.
   - This is the "repositories kept reported to the control plane" its `core.5` allows, carried as its own answer (`core.11`).
   - Without R2, crew takes a kit's folder from a place's status as today, and the started bolt's landing is refused at the old folder, naming it.
3. **swancloud, S1: a repository's entry names its former addresses** (`formerly`, runbook §4). It writes them into the runner's configuration for R1, and carries them to its own views, sluice drivers and Flume's `[repos]` as it decides. crew reads none of it: its own renames are its run record's (Decision 1).
4. **The runner's clones are renamed in place before the runner's next pass** (runbook §3.5, step 3), or adopted under R1's former addresses. Either way, the sluice records of one-seam's landing in the `flywheel-cloud` clone go with it.
5. **Flume and sluice: nothing.**
   - Flume's stored repository of a place goes stale on a move (runbook §1.2). crew stops reading a kit's folder from it wherever the runner reports its repositories. `flume relocate` stays Flume's own.
   - The proof of a bolt's landing is the `Sluice-Result` trailer of the merge commit at its head on GitHub (record 0025), which a rename does not touch.

## Decisions

### 1. The plan is renamed by an act, and what crew never rewrites is read through that act's record

Both shapes the brief names were weighed. This change takes the first: **an act that rewrites the plan's `Repo` in one commit, on the user's word**. Its record is a `kit.rename` entry in the run record. crew reads what it never rewrites through that record, not through the hosts file. Three reasons:

- **The plan is intent, read alone.** `state.2` and `state.4` say any clone reads the plan with `recsel`. With former names in the hosts file instead, the plan would name a repository by a name nothing in the fleet answers to, for good, and new work would carry the new name beside it.
  - Every check crew makes over the plan's own words would then compare names through a file outside the state repository: `plan.1`'s rule that a unit is in its bolt's repo, the descriptor's `%unique: Repo Goal`, a move only between bolts of one repo, a kit's bolts for its landings card, and `kit_labels`.
  - `plan.py` compares a `Repo` in some thirty places. One comparison missed would give a wrong answer with no refusal (`read.1`).
  - With the act, the plan names each kit once, and those comparisons stay equalities of the plan's own words.
- **A name is read from where it lasts.** The hosts file's repository lists are a fading source. `roles.9` has swancloud stop keeping repositories once a runner keeps every host's, and has crew read where a kit lives from the runner's report alone. A former-names list there would make crew's reading of its own history depend on a file `roles.9` retires.
  - crew's run record lasts as long as the history it explains, and is read from the drive's branch alone (`read.5`). `partition_kits` already reads a partition's kits from the run record's landings (Decision 3 of `the-team-machinery-leaves`), so reading its renames there follows the same pattern.
- **Aliasing is needed under either shape**, since `requests.rec`, the run record and `proposals.rec` are never rewritten. With the act, aliasing is confined to the reads of those records (Decision 3), and the plan is left out of it.

The fleet's former names (S1) remain the one owner for the clones, views and drivers that move with the repository, and for the runner's matching of a launch (R1). crew's rename is checked against the fleet (Decision 2) and recorded as crew's own act. It is no registry: it records an act on the plan, and registers no repository with crew (`roles.9`).

Alternatives considered:

- **The hosts file naming former names, with nothing rewritten.** Rejected for the reasons above. It is also the brief's second shape.
- **Both: rewrite the plan, and read history through the hosts file's former names.** This needs nothing of crew's own for history. Rejected because history would stop resolving when swancloud stops listing repositories (`roles.9`), and because two sources would then name crew's kits.
- **A record of the plan's own, `Kit` with `Formerly`, beside Bolt and Unit.** Rejected. It is a registry record in crew's state, which `roles.9` rules out. The run record's entry records the act without making the plan list repositories.
- **Asking GitHub, which redirects a renamed repository.** Rejected as a read: it puts a network call on every read, and a refusal whenever GitHub does not answer (`read.1`). Nor is it needed as the act's check, since the fleet's hosts file already says the rename has happened.

### 2. `crew kit rename <old> <new>`

**The grammar.** It is a plan command, `kit rename <old> <new>`, with `--label` like every plan command. It joins `PLAN_WRITES`, the ops a proposal may hold (`plan.3`), and `ACTS` as `("kit", "rename"): "kit.rename"`. `<old>` and `<new>` are each a kit's name or `<owner>/<name>`, checked as `bolt new --repo` checks its kit (`code.4`).

**Its checks.** The change function re-checks each one against the tip it is applied to (`plan.1`). It also runs them when a proposal holding it is checked and when it is approved (`plan.3`). Each refusal names what failed and writes nothing:

- `<old>` is one of the partition's kits: its plan's or its landings' names, read through the renames before this one (`partition_kits`, Decision 3). If not, the refusal says the plan names no such kit. A name an earlier rename renamed is refused naming its name now, "tailrace is timber since its rename: crew kit rename timber <new> renames it again".
- The partition's main-level host keeps a repository by `<new>` in its spaces (`crew.kit_kept`) and keeps none by `<old>`. This is the fleet's word that the rename has happened. The refusal names the host and what its spaces keep, say "deneb's spaces still keep agentplot/tailrace, so it is not renamed there", or "deneb's spaces keep no timber". The hosts file is read as `main_kit` reads it; one crew cannot read is a refusal (`read.1`).
- `<new>` is not the name of a bolt of the partition, since `land/<new>` would then name a bolt and not the kit (`kit_named`).
- `<old>` and `<new>` differ by name.
- The plan the rename leaves passes `recfix --check` and crew's own rules (`plan.1`). recutils' `%unique: Repo Goal` holds each of those fields once within a record, so a record left naming its Repo twice is refused before any commit; two bolts of one goal meeting under one name are two records, and pass.

**The write.** One commit sets the `Repo` of every Bolt and Unit record that names `<old>` to `<new>`, as `<new>` is given. A record names `<old>` when it does by name or forge address, compared as `kit_in` compares names. The write moves no record, and touches no other field of any record or any other file.
- The commit's subject is `plan(kit): rename <old> <new> (<agent>)`, with its `Crew-Entry` (`plan.2`).
- The entry is `kit.rename`: `On: kit/<new>`, `From: kit/<old>`, `Repo: <new>`, and `Count` the number of records renamed. `kit/<name>` is the object a kit's landings card already has (`cards.row_object`). The entry holds names alone (`record.3`).
- A rename of a kit that only the landings name, with no work in the plan, renames nothing in the plan and still writes its entry. That is what renames its history.
- The rename appends no request, and launches, retries or drops nothing (Decision 7).

**Who may run it.** It is in the role table (`plan.may_write`, `roles.1`). The planner changes the plan through a proposal, so the planner's direct run is refused, naming `crew plan propose`. The user runs it at a shell. Every other agent's direct run, the design agent's and main-level ops' among them, is refused naming the planner. A proposal holding it is approved by the user on its card, as any proposal is (`roles.2`).

**Its card.** A proposal's card draws the rename as a block of its own, `RENAME KIT`: `<old>` → `<new>`, the bolts and units it renames, and which of the bolts are started. It adds no question: a proposal that adds no unit is a plain approval (plan-proposals "A card with no new unit, or more than fifteen, is a plain approval"). Its picture shows each renamed bolt under its new kit.

**A kit the main-level host does not keep.** `main_kit_said` says what it says today, then adds: "if it was renamed on its host, `crew kit rename <kit> <new>` names it so in the plan". That is the refusal madswan's commands hit today, and it now names the way on.

### 3. One reading of a kit's name now: `kit_now`, over the partition's renames

`kit_now(kit, renames)` is a decision of plain facts (`code.7`) in `plan.py`, beside `kit_in`.
- `renames` is the partition's `kit.rename` entries not refused, as `(old, new)`, in the order they were written (`At`, then `Id`).
- Starting from `kit`, each rename in order whose `old` names the current name, by name as `kit_in` compares it, makes `new` the current name.
- A name no rename names is read as written.
- The order handles a rename and its undoing. With `a`→`b` and then `b`→`a`, both names read `a`. With `a`→`b` and then `b`→`c`, both read `c`.

**The renames are read with the landings, in the same read of `runs/` at a tip.** `landings_at`'s pass also collects the `kit.rename` entries, and the read is kept by its tip (`plan.12`, `READ`). A decision reads them where it reads the plan, at the newest commit whose entry has arrived (`read.5`). So a plan already renamed and its rename's entry are read together, or neither is.

**Where it is read.** Wherever crew reads a kit's name from what it never rewrites, and compares or names it:

| Read | Where it is now | Read through `kit_now` |
|---|---|---|
| A partition's kits | `plan.partition_kits`, the plan's and the landings' `Repo` | Each name, so each kit once by its name now. With it go `kits_at`, `kits_read`, `kit_labels` and `plan_for`, `land_key`, `kit_named`, and the main level's kit folders (`crew.kits_on`) |
| A kit's launches | `plan.kit_at`'s `kit_in(kit, [r.Repo])` over `requests.rec` | The launch's `Repo`, read through the renames where `requests.rec` is read for a run (`launches_now`, in `runner_facts`, `rail_runs` and a write's read), at the same tip |
| A bolt's kit from its launches | `plan.launched_at`, `batch_unit_at` (`mine[-1].get("Repo")`) | The kit named to `kit_of`, the launch's `Repo` as read above |
| A fix of main | `fix/main/<kit>/<name>` works: `runner.main_fixes_waiting`'s `kit`, and every match of a fix of main to its kit's landings row | The kit its launch's `Repo` names, as read above, which crew writes as the work's kit part; a send or drop of the row finds the launch by its name and that kit (`main_fix_work`), its work as launched |
| A kit's landings and deploys | `ops.py`'s landings by `Repo` (the deploys' contents), `page.fleet_kits`'s last landing by `Repo` | The entry's `Repo` |
| Card keys | `land/<kit>` (`cards.row_object`, `plan.land_key`, `row_gone`); `record/<kit>/<n>` (`record_settled`, `record_proposed`, the sweep's record cards) | The key's kit part (Decision 5) |
| A source's repository | `record_refs`'s `<owner>/<name>` before a `docs/adr/NNNN` | The repository, where crew finds its checkout through `main_kit` |
| The runner's repositories | `repositories.rec` (Decision 6) | The kit's name, matched to the reported address |

Everything else of crew's reads a kit from the plan, which after the act names it by its name now. That includes `crew bolts`, the board's ledger, planned and queue rows, the agents' views, a bolt's landing and its `bolt.land` entry. Before the act there are no renames, and every name reads as written, as today.

### 4. A command given a former name writes the name now

A plan command that names a kit is read through the partition's renames before it writes: `bolt new --repo`, `unit add --repo` and `chore add --repo`. The kit's name now is what it writes, and its answer says so: "tailrace is timber since its rename; written as timber".
- This also covers a proposal approved after a rename. Its `Do` lines stay as written (`plan.4`), and applying them, which runs the same functions as a direct run (`plan.3`), writes the new name. An agent that remembers the old name writes the new name the same way.
- A command after a rename in the same proposal reads that rename too, though its entry is written only once the approval lands: the write carries the renames its own commands made.
- **A former name kept again.** The main-level host might keep a repository by a former name again, made after the rename. A command naming that name is then refused, naming the rename and saying the new repository needs another name in crew. crew could not tell the two kits' records apart (`read.1`).

### 5. A kit's landings card, and a record's card, follow the rename

A card open under `land/<old>`, `<old>` now a former name, is closed by the rail's sweep (`row_gone`) with the reason "<old> is renamed <new>: its landings are rows of land/<new>". The sweep raises `land/<new>` for the kit's waiting rows as it raises any row with no card, in main-level ops' name (rail-cards). This keeps `land_key` from reading `land/<old>` as a gone bolt's card, which would close it with "its bolt no longer waits to land".

A decision record's card under `record/<old>/<n>` is read as `record/<new>/<n>`'s, so the design agent's `crew record <new> <n> --accepted` settles it. A Pending You card keeps the words it was posted with.

### 6. Where a runner keeps a kit is that runner's report

Today crew reads a started bolt's kit folder, and a kit's, from Flume's status of the newest place the runner that took the work carried (`runner.where`). That status names where the place was cut from, which is a fact about the place. A clone renamed under it leaves that path stale. Where a host keeps a repository is the runner's fact: it keeps the clones (boomdrive `core.5`). So crew reads it from the runner's report (`roles.9`).

`runner.py` gains the descriptor of the runner's new file, which crew writes no part of (`state.5`):

```
%rec: Repository
%doc: A repository the runner keeps on its host: its forge address as its configuration names it, and the folder of its clone, where Flume cuts its places.
%key: Repository
%mandatory: Repository Folder
%allowed: Repository Folder
```

**Reading it.** `host_read` reads `repositories.rec` beside the other three files. A file recfix refuses, or a record with no address or a repeated one, makes the host's runner unreadable, as the other files do (`read.1`). A file the tip lacks reads as no report.

**Finding a kit's folder.** `where` takes the host from the taker of the newest launch taken, as now. It finds the kit's folder on that host as follows:

- **The runner reports its repositories:** the folder of the repository whose address names the kit's name now (`kit_now`, `kit_in`).
- **It reports repositories, but not the kit:** the kit is unread. The refusal names the host, the kit, what the runner keeps there, and, where one of those might be the kit's new name, `crew kit rename`.
- **It reports two repositories by the kit's name** (two owners of one name): the one at the kit's forge address, where the plan names the kit by it; else the kit is unread, naming both, as `crew.kit_kept` refuses two for the main-level host (`read.1`). Taking the first was not done: it would be a guess.
- **It reports none:** as today, from Flume's status of its newest place naming one.

The stream is still read from Flume's status of a place, since the stream is the place's fact.

`kit_at` and `bolt_at` keep their shape. They reach the folder through `where`.

### 7. The started bolt `you-sign-in-to-staging`

Once deneb's crew carries this change, the runner carries R1 and R2, and its clones are renamed:

1. madswan-planner proposes `kit rename flywheel-cloud boomdrive-cloud` and `kit rename tailrace timber`, and the user approves the card (*After deploy*). The bolt and its unit then name `boomdrive-cloud`. The bolt's `Path: flume`, its branch on GitHub and its unit's merge are untouched, and no request is appended.
2. `requests.rec` still holds request 1 under `flywheel-cloud`. crew reads it as `boomdrive-cloud`'s (Decision 3). It is still the bolt's launch: `bolt_launches` finds launches by their base, `bolt/you-sign-in-to-staging`, which names the bolt, not the kit.
3. The runner's next pass takes request 1 through its configuration's former address (R1), since its work is still in crew's plan. It carries the tidied place's status from Flume: over, landed at 84393d4. crew reads one-seam merged (bolt-plan "A launched place's stage is where Flume's status has it"). It was never launched again, so it stays merged.
4. `where` takes the bolt's folder from deneb's `repositories.rec`: `agentplot/boomdrive-cloud` at its renamed clone (Decision 6). The bolt is read, proven on its head's `Sluice-Result` (record 0025), and put on `land/boomdrive-cloud`.
5. Ops lands it on the user's send by the one procedure (`plan.16`), in that folder. Its `bolt.land` entry names `boomdrive-cloud`.

Steps 1 and 3 can happen in either order. Before the rename, `where` finds the plan's `flywheel-cloud` among none of the runner's reported repositories, so the bolt is refused naming the rename, and nothing is landed or guessed.

### 8. What the runner wrote under the old name

- **`answers.rec` and `places.rec`** are keyed by request number. They are read as they stand: a launch made under a former name keeps its answer and its place.
- **`places.rec`'s Status** is Flume's JSON as Flume gave it. It names the place's repository at its old path, and the place key is a Flume id hashed from the old git directory's path (runbook "What the survey found", point 4). crew matches Status by its place key as the runner carried it. Where the runner reports its repositories, crew no longer takes a kit's folder from Status (Decision 6).
- **Request 1's record** stays as carried at 00:23:12Z, at construct, until the runner carries it again (R1). Until then crew reads one-seam where that record left it. It has no other reading of a launched piece's stage, and builds none, since that stage is Flume's through the runner (`roles.5`; bolt-plan "A started bolt's work reads its stage from the runner's records").
- **`runner.rec`** names the host and the runner, and no kit.

### 9. What a rename does not rewrite, and why

- **The plan's Goals, Intents and Sources** are the planner's words. In them "tailrace" may name the tool, the product, a blueprints folder (`design/tailrace/…`, which has its own rename in agentplot/blueprints) or the repository. A rewrite of prose is a judgment, and so no part of a mechanical act. The planner amends a source or an intent by proposal where it matters. A source's repository is read through the renames where crew reads a record by it (Decision 3).
- **`requests.rec`, the run record, `proposals.rec`, `signals/` and `moves.rec`** are append-only by rule, and are read through the renames where crew reads a kit from them.
- **`asks.rec`** names no kit.
- **`roles.rec`** names the partition's first blueprints repository, which follows the teams file by crew's own matching (role-runs "Role records follow the teams file").
- **A Pending You card's words** stay as they were posted. The card is closed or kept by its key (Decision 5).

### 10. The standing agents' folders follow without new work

The runbook's second crew item says a running session keeps its old `--add-dir` folders until it restarts. crew already rebuilds those folders at each start, from the plan's kits as the host keeps them (`crew.kits_on`). It also makes a standing agent due a restart once its folders change, given at its next stop with its conversation and never on a held host (`teams.19`). The plan's names change at the rename, and `partition_kits` reads its kits by their names now, so the folders change and the restart follows. Nothing is added for it.

### Rules relied on

- **State:** `state.1` (one commit through crew, never merged), `state.2` (the plan is intent alone), `state.4` (views from the files and the run record), `state.5` (crew never writes a runner's branch).
- **Roles:** `roles.1` (the planner by proposal, the user anything), `roles.2` (the approval is the user's), `roles.5` (crew builds no stage reading of its own), `roles.9` (no registry in crew, and where a kit lives is the runner's report).
- **Reading:** `read.1` (refuse, never guess), `read.5` (the run record from the branch alone, and a decision read at the newest commit whose entry has arrived).
- **Code:** `code.4` (names), `code.6` (a Conventional Commit, staged by path), `code.7` (`kit_now` and every reading of it are decisions of plain facts), `code.8` (the views keep their shape, so the mod is untouched).
- **Plan:** `plan.1`, `plan.2`, `plan.3` and `plan.4` (proposals apply by the same functions, and their `Do` lines never change), `plan.12` (one read of `runs/` per tip), `plan.16` (the landing by ops' procedure).
- **Records and signals:** `record.1`, `record.3`, `record.4`, `signals.4`.
- **Teams:** `teams.19`.
- **Docs:** `docs.2`, `docs.4`, `docs.7`.
- **Tests:** `tests.4`, `tests.10`, `tests.11`.

### Departures

None.

## Risks / Trade-offs

- **The started bolt's landing rests on two changes to the runner.** Until R1 is built, request 1 is passed over and one-seam reads at construct, as last carried. Until R2, the bolt's folder is the old clone's path, and its landing is refused there, naming that path. Accepted: each refusal names what is missing. crew's part works with either runner, and nothing is landed on a guess. madswan-planner's card for the rename can go first.
- **A view may read the plan's commit before its entry.** A rail or board refresh that reads the tip between the rename's plan commit and its entry's commit shows the landings under the old name as a kit of their own for one refresh. Accepted: `read.5` has decisions read below the entry's arrival, and the next refresh is whole.
- **The plan's words keep the old name.** Accepted (Decision 9). The planner amends them by proposal where an agent would be misled. GitHub redirects the old address.
- **Two crews.** The box runs main's crew, which has neither `kit rename` nor `kit_now`. madswan's main level runs on deneb, so its plan is written and read there. A read of madswan's state by the box's crew would show its old landings as a kit beside the renamed one. Accepted: nothing of madswan's work is run from the box, and main gains this design when `teamless/deneb` and main are brought together.
- **A former name used again.** A repository the fleet makes under a former name is refused in crew (Decision 4). Accepted: GitHub's redirect breaks the same way, and a third name settles it.

## Migration Plan

1. This change is built on its branch and submitted to its base, `teamless/deneb`. Nothing goes to main.
2. swancloud pins deneb's crew at `teamless/deneb`'s new commit, on the user's word (`plan.19` as `teamless/deneb` departs from it).
3. The runner's R1 and R2 and swancloud's S1 land in their own repositories and are deployed. The runner's clones are renamed before its next pass (runbook §3.5).
4. madswan-planner proposes both renames, and the user approves (*After deploy*).
5. The runner's next pass carries request 1, and the bolt lands under `boomdrive-cloud` (Decision 7).

**Rollback.** `crew kit rename boomdrive-cloud flywheel-cloud` renames the plan back, and `kit_now`'s order reads both names as `flywheel-cloud` again. swancloud's pin of deneb's crew can go back to the commit before this change. A plan already renamed then names a kit that crew reads as written.

## After deploy

- **madswan: propose the two renames.** madswan-planner proposes `kit rename tailrace timber` and `kit rename flywheel-cloud boomdrive-cloud`, in one proposal. It waits for deneb's crew to carry this change: `crew --version`, or the band's crew, names `teamless/deneb`'s commit with it. The user approves the proposal on its card.
  - Why no check can be code: it writes madswan's live plan on afterthought/crew-state. A plan write there is the planner's proposal on the user's word (`roles.1`, `roles.2`), and no test in the coder's worktree reaches that branch.
  - Environment: deneb, partition madswan.

Nothing else. The runner's and swancloud's changes are their own repositories' work (*What this change rests on*), and the landing of `you-sign-in-to-staging` that follows is ops' usual procedure on the user's send (`plan.16`).

## Task notes

These hold for every task:
- A task that adds or removes a test, or changes what one reads, runs `tests/moon-tasks` and commits `tests/moon.yml` in the same commit (`tests.10`).
- Facts for the logic tier go in `tests/py/facts.py` beside the ones there.
- Never run `wt submit --help` (CLAUDE.md), and submit nothing.

**1.1** Add `kit_now(kit, renames)` beside `kit_in` in `plan.py`, as Decision 3 gives it. `tests/py/test_kits.py`, a new `TestKitNow`, covers:
- a name no rename names;
- `tailrace`→`timber` read from `tailrace` and from `agentplot/tailrace`;
- a chain `a`→`b`→`c`;
- a rename and its undoing `a`→`b`→`a`, both names reading `a`;
- two renames out of order, `b`→`c` written before `a`→`b`, so `a` reads `b`;
- an unrelated name, unchanged.

**1.2** Make `landings_at(repo, tip)`'s one pass over `runs/` also collect the `kit.rename` entries not refused. Return them through a `renames_at(repo, tip)` that reads from the same kept read (`READ`, keyed by the tip), so no second read of `runs/` happens (`plan.12`). Sort them by `At`, then `Id`.
- `partition_kits(plan, landings, renames=())` reads every name through `kit_now`, sorted, each once. `kits_at` passes the renames.
- `TestPartitionKits` gains these cases:
  - two `bolt.land` entries under `tailrace` with a later rename to `timber`, read as `timber` once;
  - a plan already naming `timber` and landings under `tailrace`, read as one kit;
  - no renames, read as today.

**1.3** Read the table of Decision 3 through `kit_now`, one row at a time. The renames come from the tip the command's plan was read at, threaded from where `runner_facts` and the run record are read. A command reads them once.
- `kit_at`, `launched_at` and `batch_unit_at`: `TestWhereABoltRuns` gains a launch under `flywheel-cloud` counted as `boomdrive-cloud`'s after a rename.
- `runner.main_fixes_waiting`'s kit, and its consumers' match to a kit's row: `tests/py/test_main_fix.py` gains a fix of main `fix/main/tailrace/x` shown on `timber`'s row.
- `ops.py`'s deploy landings by kit: `tests/py/test_ops.py` gains a landing under the old name counted in the renamed kit's deploy.
- `page.fleet_kits`: `tests/py/test_page.py` gains the renamed kit's last landing read from an entry under its old name.
- `record_refs` and `record_items`: a source naming `agentplot/tailrace:docs/adr/0017` is read in `timber`'s checkout. Its case goes in `tests/py/test_proposals.py`, where the records a proposal rests on are tested.

**1.4** `board.agent_views` and the board read kits from `partition_kits`, so they name the kit by its name now. `tests/py/test_board.py` gains a case: a partition whose landings are under `tailrace`, with a rename to `timber`, shows `timber` alone, and the views' keys are those the case pinning every key the mod reads already pins (`code.8`). `plugin/hooks/status.js` is unchanged.

**2.1** Add `kit rename <old> <new>` to the command line's grammar (`plan.py`'s parser), with `--label`. Add the op to the ops a proposal may hold, `("kit", "rename")` to `PLAN_WRITES`, and `"kit.rename"` to `ACTS`. Add `named` support so a refusal's entry names `kit/<old>`. `tests/py/test_parser.py` gains these cases:
- the command parsed;
- it parsed inside a proposal's `Do`;
- a name failing `code.4` refused.

**2.2** Build the op as Decision 2 has it, in a new `tests/py/test_kit_rename.py` over facts: a plan holding madswan's shape, with 21 `tailrace` records, two `flywheel-cloud` records, a started bolt `Path: flume` and other kits, and a fleet whose main-level host keeps `agentplot/timber` and `agentplot/boomdrive-cloud`. Its cases:
- **The rename itself:**
  - every `tailrace` record named `timber` and nothing else changed, comparing each record field by field;
  - a record naming `agentplot/tailrace` renamed;
  - a kit only the landings name, renaming no record and still writing its entry.
- **Refusals:** each one leaves the plan unchanged and names what it should.
  - the old name no kit of the partition;
  - the main-level host still keeping `agentplot/tailrace`, the refusal naming the host and the kit;
  - the host keeping no `timber`;
  - the new name a bolt's name;
  - old and new the same;
  - the hosts file unreadable.
- **The started bolt:** renaming the started bolt's kit leaves its `Path`, its units and `requests.rec` as they were, and the rename appends no request.

**2.3** `plan.may_write`: the planner's direct run is refused naming `crew plan propose`, and the design agent's and main-level ops' are refused naming the planner. The user's run, and a proposal's application of the op, are allowed. Its cases go in `tests/py/test_plan_roles.py`.

**2.4** The commit's subject and its `Crew-Entry`, and the entry `kit.rename` with `On: kit/<new>`, `From: kit/<old>`, `Repo: <new>` and `Count`. `record.py`'s act list gains the act, with no field outside the descriptor's `%allowed` (`Count` and `Repo` are already there). `tests/contract/test_recfix.py` gains a real `recfix --check` of madswan's shape of plan after the rename, which passes, and of a rename that would break `%unique: Repo Goal`, which fails before any commit.

**2.5** Read `--repo` of `bolt new`, `unit add` and `chore add` through the renames before the write, and say the name now in the answer. A proposal's `Do` approved after a rename writes the new name, with the proposal's text unchanged. A former name the main-level host keeps again is refused, naming the rename. The cases go in `test_kit_rename.py`.

**2.6** `cards.drawn` gains the `RENAME KIT` block: `<old>` → `<new>`, the bolts and units renamed and the started bolts among them. The picture shows each renamed bolt under the new kit, and the proposal stays a plain approval. Its cases go in `tests/py/test_proposal_card.py`.

**2.7** Two parts:
- `row_gone` and `land_key` read a `land/<old>` key whose kit a rename renamed: the card closes with "<old> is renamed <new>: its landings are rows of land/<new>", and the sweep raises `land/<new>` for the kit's waiting rows.
- `record_settled` and `record_proposed` read `record/<old>/<n>` as `record/<new>/<n>`'s.

Their cases go in `tests/py/test_rail.py`, where `row_gone` and the sweep are tested.

**2.8** `main_kit_said` adds the rename's words of Decision 2. `TestBeforeARunnerTookIt` in `test_kits.py` pins them.

**3.1** Add the `REPOSITORIES` descriptor and `"repositories.rec": "Repository"` to `runner.FILES`, and read it in `host_read` into `repositories`, `{address: folder}`.
- A record with no address or a repeated one makes the host unreadable, naming the file.
- A file recfix refuses is read as the other files are.
- An absent file is `None`, which means no report, distinct from an empty report.

Its cases go in `tests/py/test_runner.py`. The partition's fetch of `<label>/runner/*` already brings the file, so nothing changes in the fetch.

**3.2** In `runner.where`, take the kit's folder from the taker's `repositories` by the kit's name now, as Decision 6 has it. That needs the kit and the renames, which `kit_at`, `bolt_at` and `launched_at` pass. Three cases:
- **The runner reports the kit:** the reported folder wins over a place's Status naming the old folder.
- **It reports repositories, not the kit:** the kit is unread, and the refusal names the host, what it keeps and `crew kit rename`.
- **It reports none:** read from the place's Status, as today.

Their cases go in `test_runner.py` and `TestWhereABoltRuns`. Update `drive-state`'s scenario "The runner that took the work" in its test the way the delta words it.

**3.3** The started bolt of Decision 7, end to end over facts, in `test_kit_rename.py`, with madswan's facts as read:
- request 1 under `flywheel-cloud`;
- deneb's answer to it;
- its place's Status once tidied, landed at 84393d4 (a Flume 0.3.6-shaped status from `tests/py/flume-0.3.6/`, edited to `tidied`/landed);
- `repositories.rec` naming `agentplot/boomdrive-cloud` at a renamed folder;
- the rename to `boomdrive-cloud`.

The unit then reads merged, the bolt's landing reads its folder as the renamed clone, its landings card key is `land/boomdrive-cloud`, and no request was appended.

**4.1** In `tests/t-journey-plan.sh`, add steps to the plan journey, each checking one wiring once:
- the user's `crew kit rename` writes one commit renaming the fixture kit's records, with its `kit.rename` entry in the run record;
- the planner's direct run is refused;
- a proposal holding a rename is checked, its card raised and approved, and the approval's commit renames.

The world's hosts file is written by `tests/lib.sh`'s `kit`; give it a renamed repository the way that helper writes one. Update the test's opening comment and its `# Reads:` line if what it reads changes, then run `tests/moon-tasks`.

**4.2** README's The plan section, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header each name `crew kit rename <old> <new>`, what it rewrites and what it does not, and who runs it (`docs.2`). `t-docs` checks that every command README names is in the usage.

**4.3** The planner's brief, `plugin/roles/planner.md`, gains a row in its command table: "rename a kit renamed on its host | `kit rename <old> <new>`". It also gains one sentence: a kit its host renamed is renamed by proposing it, never by dropping and adding its work again. `tests/t-briefs.sh` pins both on the planner's brief, built by its partition as the file builds a main-level brief.

**4.4** Run `tests/suite --affected` once 1.1 to 4.3 are committed, and fix by the rules above until it ends "0 failed".
