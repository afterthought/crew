# Design

## Context

See proposal.md, *Why*. This change carries crew's part of the cross-tool design that the user approved on 2026-11-05, Flume's change `a-places-readiness-is-one-design-across-the-tools` and its record 0036. That design is decision 7, "crew (teamless/deneb, records and specs)", and decision 6's crew row: crew stops saying it readies a worktree, and stops its `enterShell` installing pins. It starts nothing new, since its landing worktree is a submitter's.

What crew holds today, on `teamless/deneb` at b57c709d:

- **Code.** Nothing of crew's code readies a worktree.
  - `kit.py` reads of a kit's policy only what gates its bolt branches, where they live and whether it declares a preview. Its docstring says "crew readies no place".
  - `plan.17` was retired on 2026-11-03 with `the-team-machinery-leaves`.
  - crew makes one worktree of its own, a landing's, with `git worktree add --no-checkout` and `read-tree`, and submits from it (`plan.py` `SUBMIT`). sluice's submission reads it as any submitter's, equipping it up to the runner's version check (sluice 147).
- **The record.** It still says crew readies a worktree:
  - Record 0023 has the decision in point 4, the adapters in point 3 and its reading of `[tests]` in point 2.
  - Record 0024 point 4 rests the warm evaluation on crew's readying.
  - Record 0028 point 1 has a fix start in a place crew could not make ready.
  - The `kit-toolchain` spec's three requirements describe crew's adapters.
  - `.config/sluice.toml`'s opening comment says crew reads the policy "when it makes a worktree of crew ready (plugin/lib/kit.py, plan.17)".
- **The shell.** `devenv.nix`'s `enterShell` runs `proto install --config-mode upwards` whenever a pin `.prototools` names is missing from crew's proto home. So the script `devenv print-dev-env` prints, which is the toolchain the policy names, installs as well as activates. On 2026-11-05 on deneb, that script held the line `proto install --config-mode upwards >/dev/null 2>&1 || true`.
- **The neighbours.** flume's, sluice's and Boomdrive's `devenv.nix` install in a devenv task, and their `enterShell` only activates. The kit standard's toolchain.8, in the same design, makes that the rule: "The toolchain `[tests] toolchain` names only activates: sourcing it installs nothing. What `.prototools` pins is installed by sluice's equip in every working copy sluice or flume readies, and by a devenv task on entering the shell for a person's or an agent's command." Its details rule out crew's `enterShell`. It is still the design's words: the kit standard's branch `docs/toolchain-8-the-toolchain-only-activates` holds no commit of it yet.

## Goals / Non-Goals

**Goals:**

- crew's records, spec, policy comment and README say crew readies no worktree, and that a place is equipped by sluice at Flume's asking.
- The toolchain crew's policy names only activates. crew's shell installs a missing pin by a devenv task, and a warm entry costs what it costs today.

**Non-Goals:**

- Any change to the `crew` command. Its code readies nothing already.
- Flume's, sluice's, Boomdrive's and the kit standard's parts, each launched in its own repository.
- crew's landing worktree. The cross-tool design's *Found beside readiness* names its place under Boomdrive's container and its removal by plain `git worktree remove`, which `plan.9` says should be released through sluice first. That is for the orchestrator to carry, and not this change.
- `CLAUDE.md`'s Tests section and `tests.7`'s details. Both say entering the shell installs a missing pin, and that stays true: the entry's task does it.

## Decisions

### 1. Each record gains a line under its title and an amendment at its end

Each record keeps its text and gains two things, as records 0005 and 0035 carry theirs:

- A line under its title: "Superseded in part 2026-11-05 by the amendment below", naming the points it supersedes.
- A section at its end: "Amendment, 2026-11-05: crew readies no worktree; a place is equipped by sluice at Flume's asking".

The amendment quotes the user's approval and decision 7's words, says who owns what, and names each sentence it supersedes. What it does not name stands. Task notes 1.1 to 1.3 give each record's text.

- **Record 0023.** It loses crew's reading of `[tests]` (point 2), the adapters (point 3), the readying (point 4) and crew's own worktrees "made ready through crew's adapters" (point 5). It also loses point 1's "devenv's shell runs `proto install`", which toolchain.8 now places in a devenv task.
- **Record 0024.** It loses point 4's readying, and point 5's "crew's adapters do the same at readying". The question it left open, whether a devenv kit's `enterShell` keeps running `proto install`, is closed by toolchain.8 and by decision 3 below.
- **Record 0028.** It loses point 1. Whether a stage starts in a place whose equipping failed is Flume's (Flume 12, S16): a first stage waits, or a fix starts with the failed step and its words in its prompt.

The amendments are accepted, not proposed. The user approved the decision on 2026-11-05 in the Plannotator Inbox, "Approve: start its code", on a design whose decision 7 gives these words for crew's records: "Records 0023, 0024 (point 4) and 0028 gain an amendment: crew readies no worktree; a place is equipped by sluice at flume's asking (flume record 0036). Their readiness text is superseded." The one choice in them that is not the user's, the task's status in decision 3, is cheap to change later. It is recorded as the build's, with the path not taken.

**Not taken:** a new record that supersedes the three. The design names an amendment of each, and each record keeps whatever its readiness text does not touch: 0023's one declaration in sluice's file, 0024's per-command shell, and 0028's drop of a fix.

### 2. The `kit-toolchain` spec goes through this change's delta

A spec changes only through a delta in the change that builds it (`docs.4`). The delta removes all three requirements, each with its reason and where its subject now lives (Flume 11, 12, S16; sluice 147, C.2). Removing a capability's last requirement needs the change to retire the capability: `retire_capabilities: true` in `.openspec.yaml`, beside its schema. With it, `openspec archive` deletes `openspec/specs/kit-toolchain/spec.md`. A scratch copy of this checkout was archived with openspec 1.15.0 on 2026-11-05: without the flag the archive refused, "Spec must have at least one requirement"; with it, the spec was retired and `test-suite`'s requirement updated. The archive is the verify stage's, as Flume's change kind runs it, and not a task here.

`tests/py/test_kit.py`'s docstring cites the `kit-toolchain` spec for "crew readies no place". After the archive no spec says that, so the docstring cites Flume's record 0036. `SCRIPT`, a toolchain script path no case reads, goes with it: it is a leftover of the adapters.

### 3. A devenv task installs, skipped while every pin is installed

`enterShell` keeps three things: moon's cache link, the homes (`PROTO_HOME`, `MOON_HOME` in the git common dir, toolchain.4) and `proto activate`. The install moves into a task, `crew:proto:install`, named as flume's `flume:proto:install` is:

- `before = [ "devenv:enterShell" ]`, so the pins exist before they are activated.
- `status` is the read `enterShell` does today, moved whole: it exits 0 when every `<tool> = "<version>"` line of `.prototools` names a directory `tools/<tool>/<version>` under the proto home, or when there is no `.prototools`, and 1 at the first pin that is missing. devenv skips the task's `exec` while its status exits 0.
- `exec` changes to the checkout's root and runs `proto install --config-mode upwards` with the homes set, ending 0 whatever proto did, as `enterShell`'s `|| true` does today. So an install that fails, offline for instance, does not keep the shell from being entered, and the command that needs the missing tool fails for want of it (`tests.7`).

The homes are defined once and used by `enterShell`, the task's status and its exec. A task runs before `enterShell` and has none of its exports.

The script `devenv print-dev-env` prints holds `enterShell` and none of the tasks, so the toolchain sluice and Flume source installs nothing. `devenv shell -- <command>` runs the task, then `enterShell`, so a person's or an agent's command still installs a missing pin. That command is what crew's agents run (`tests.7`), as are `tests/suite` and `tests/run`.

**Not taken:**

- **flume's task as it stands, with no status.** Every entry would run `proto install`. One that finds every pin installed took 2.8 of a warm entry's 3.2 seconds (mac-studio, 2026-10-13, `devenv.nix`'s own comment), and an agent enters the shell for each command it runs (record 0024). The cross-tool design cites those 2.8 seconds against an `enterShell` that installs. crew's never paid them on a warm entry, because it installs only for a missing pin, and the status keeps it so. A warm entry measured 0.8 to 1.7 seconds on deneb at a load of 34 on 2026-11-05, with today's `enterShell`.
- **`execIfModified = [ ".prototools" ]`.** devenv keeps that per checkout. A new worktree would run the install once though the shared home holds every pin, and a pin gone from the home would go unnoticed. The status reads the home itself.

### 4. One contract case proves the toolchain only activates

The `test-suite` delta adds the scenario "The toolchain crew's policy names only activates". Its check is a new case in `tests/contract/test_toolchain.py`, the contract file that pins what crew assumes of its own toolchain (`tests.11`). The case:

1. reads `[tests] toolchain` from `.config/sluice.toml`;
2. runs that command in crew's checkout;
3. asserts the printed script holds `proto activate` and no `proto install`.

On today's `devenv.nix` it fails, since the script holds `enterShell`'s install. On deneb on 2026-11-05 the command printed its script in 0.07 seconds warm, both nested in crew's shell, as `tests/suite` runs it, and with the environment cleared to sluice's kept list, as sluice runs a check. It reads `.config/sluice.toml`, so the contract task takes that file as an input (`tests.10`): `tests/moon-tasks` names it among the contract tier's inputs, and `tests/moon.yml` is written again.

The task's status has no case. Whether the install is skipped is a matter of cost, not of what a run holds. A timing check would rest on the host's load (`tests.8`). The existing case `test_moon_is_protos_from_crews_own_home_at_the_version_prototools_pins` still proves what the install must leave: moon at its pin from crew's proto home, inside the shell and inside sluice's run alike.

**Not taken:** a case that reads `devenv.nix`'s text for `proto install` in `enterShell`. It would pin the file's wording, where the printed script is what sluice sources.

### 5. The words say it, and `t-docs` holds the README and the policy to it

These say crew readies no worktree and that sluice equips a place at Flume's asking:

- `.config/sluice.toml`'s opening comment;
- `README.md`'s line on places (line 18);
- `kit.py`'s docstring, which says the same thing as that line.

The policy's comment and the README's line also name `sluice equip`. The texts are in Task notes 3.1.

`tests/t-docs.sh` already pins the README's statements of crew's process by phrase. It pins these two as well:

- the README says crew readies no worktree and names `sluice equip`;
- the policy's comment, everything above its first table, names `sluice equip` and not `plan.17`.

Its `# Reads:` line gains `.config/sluice.toml`, and `tests/moon.yml` is written again.

### Rules relied on

- **`roles.5`.** crew is the wrapper and builds no mechanism another tool holds. Readiness is sluice's and Flume's.
- **`code.1`.** devenv declares only jq, proto, recutils and git-cliff, with convco. The task adds no package.
- **`code.6`.** Commits are Conventional Commits, staged by path.
- **`tests.5`.** sluice gates the landing on `check-full`.
- **`tests.7`.** Tools run through the shell per command, and the host carries no application tool, so a missing pin fails loudly.
- **`tests.10`.** The contract task's and `t-docs`'s inputs follow what they read.
- **`tests.11`.** The contract tier pins crew's assumptions about its toolchain.
- **`docs.1`, `docs.4`, `docs.5` and `docs.6`.** These govern where each part is written.

The pages whose areas this touches are `docs.md` (README, `openspec/`, `docs/`) and `tests.md` (`tests/`, `devenv.nix`, `.config/`). No rule changes. `plan.17`, the one rule about readying, was retired on 2026-11-03.

### Departures

- **`docs.7`, which is proposed and not accepted.** It says a change's construct and code never edit `docs/adr/`. This change's code stage writes three records' amendments, because the approved design names them as crew's part and the brief asks for them. Nothing of it reaches main, where the design agent stays the records' one writer.
- **`openspec/config.yaml`'s tasks rule**, that each task's check is in crew's tiers. Tasks 1.1 to 1.3 check the records with `grep`, and task 2.1 checks the change with `openspec validate --strict`, because no tier reads a record or a change's own deltas.

## Risks / Trade-offs

- **[deneb's Flume, 0.6.4, readies a crew place by the toolchain and `moon setup` alone. It holds neither #96's install, which no release carries yet, nor `sluice equip`. With the toolchain no longer installing, a place whose pin is missing from crew's proto home would fail at `moon setup`, as deneb's place did on 2026-11-05.]** → Every place, sluice run and checkout of crew on deneb is a worktree of one clone, `crew.git`, with one proto home (toolchain.4). That home holds moon, Python and uv today. Every pin on `teamless/deneb` reached it through sluice's gate, whose candidate run installs what the candidate's `.prototools` pins (sluice 0.66.0 on deneb; sluice 147, C.2). So the pin is in the home before any place cut from the branch needs it. Only a fresh clone of crew, on a host whose Flume predates #96, would fail. deneb is the one host on `teamless/deneb`. Flume's release with #96, and then its build of `sluice equip`, close it.
- **[A person who enters by direnv.]** → The script `devenv direnv-export` prints holds `enterShell` and no task (read 2026-11-05, devenv 2.4.0), so direnv's entry installs nothing. A missing pin then waits for the next `devenv shell`, `tests/suite` or sluice's equip, all of which install into the one home. A moon it lacks fails loudly (`tests.7`). Accepted: toolchain.8 names a devenv task on entering the shell, and direnv's entry only activates.
- **[The status reads proto's layout]**, `tools/<tool>/<version>` under the home, as `enterShell` reads it today (proto 0.63.1). → A proto that moved its layout would fail the status every time, so every entry would install: slower, never wrong. proto's version is `devenv.nix`'s, so such a move comes with a change to this file.
- **[A contract case that runs devenv.]** → It evaluates `devenv.nix` inside a moon task. Warm, that took 0.07 seconds. In a place sluice runs the check in, sluice's equip has evaluated it there first. Cold, by `tests/suite` in a fresh worktree, it costs one evaluation, which the shell's own entry has already paid.

## Migration Plan

1. The change lands on `teamless/deneb` through sluice, and on no other branch.
2. A checkout of crew takes the new `devenv.nix` at its next command (`tests.7`). One with the older file keeps installing in its entry, which harms nothing.
3. Rollback is a revert of the landing on `teamless/deneb`.

## After deploy

None. Nothing of this runs on a host but `devenv.nix`, which every checkout reads at its next command, and its outcome is the contract case's. crew's plugin code is untouched, so no agent restarts for it.

## Task notes

Never run `wt submit --help` (CLAUDE.md), and submit nothing. A task that changes what a test reads runs `tests/moon-tasks` and commits `tests/moon.yml` in the same commit (`tests.10`).

**1.1** Record 0023, `docs/adr/0023-a-kit-declares-its-toolchain-and-tests-once-for-crew-and-sluice-alike.md`. Add a line below the H1 title, before *Deciders*:

> Superseded in part 2026-11-05 by the amendment below: crew readies no worktree, and a place is equipped by sluice at Flume's asking (Flume record 0036). Point 2's reading of `[tests]` by crew, point 3's adapters, point 4, point 5's words on crew's own worktrees, point 1's install on the shell's entry, and the consequence on what a new worktree costs, stand only as that amendment says. The rest stands.

At the record's end, after *Considered options*, add:

> ## Amendment, 2026-11-05: crew readies no worktree; a place is equipped by sluice at Flume's asking
>
> Accepted by the user on 2026-11-05 in the Plannotator Inbox ("Approve: start its code"). The user was approving the design of Flume's change `a-places-readiness-is-one-design-across-the-tools`, with Flume's record 0036. That design's decision 7 names this amendment as crew's part: "Records 0023, 0024 (point 4) and 0028 gain an amendment: crew readies no worktree; a place is equipped by sluice at flume's asking (flume record 0036). Their readiness text is superseded." Built by crew's change `crew-readies-no-worktree-a-place-is-equipped-by-sluice` on `teamless/deneb`.
>
> 1. **Who readies a working copy.**
>    - The kit declares which tools a working copy needs: `[tests] toolchain` and `[tests] runner` in `.config/sluice.toml`, the pins in `.prototools`, and moon's toolchains in `.moon/toolchains.yml`.
>    - sluice owns how a working copy is equipped. It equips every working copy it runs in by one sequence, and a working copy it did not make by the same sequence as `sluice equip`. The sequence is the toolchain, then the runner's install of the pins, its check of its own version (refusing a moon below 2.6), and its setup, each outside its executor (sluice 147, agentplot/blueprints 9f1f0fd).
>    - Flume owns when a place is equipped: at its launch, at the revision the launch read, and at the retry of a first stage whose readiness failed. It also owns what a failure does (Flume 11, 12, S16).
>    - crew readies no worktree, and runs nothing of a kit's toolchain or runner.
> 2. **What this supersedes.**
>    - Point 2's "crew reads that table from the worktree in hand". crew reads no `[tests]`. Of a kit's policy it reads only what gates its bolt branches, where they live and whether it declares a preview (`plugin/lib/kit.py`). The declaration stays one, in sluice's file, as point 2 decided, and sluice alone reads its `[tests]`.
>    - Point 3's adapters. crew has none, and it never ported their run and read.
>    - Point 4, whole. A unit's, chore's and fix's place is Flume's, equipped by sluice. crew's one worktree, a landing's, is a submitter's, which sluice's submission equips up to the runner's check of its version (sluice 147).
>    - Point 5's "so crew's own worktrees are made ready through crew's adapters". crew's declaration is what sluice equips crew's working copies with.
>    - Point 1's "devenv's shell runs `proto install` and activates the pins". The toolchain a kit's policy names only activates, and sourcing it installs nothing. crew's shell installs a missing pin by a devenv task that runs before its entry (the kit standard's toolchain.8; record 0024's amendment).
>    - The consequence "A new worktree costs the kit's toolchain step in crew's command". A place's equipping is sluice's, at Flume's launch.

**1.2** Record 0024, `docs/adr/0024-an-agent-runs-its-kits-tools-through-the-shell-per-command-and-the-host-is-the-container.md`. Add a line below the H1 title, before *Status*:

> Superseded in part 2026-11-05 by the amendment below: point 4's readying by crew, point 5's "crew's adapters do the same at readying and for the test runner's setup", and the question left open under *Not decided here*, whether a devenv kit's `enterShell` should keep running `proto install`. The rest stands.

At the record's end, after *Considered options*, add:

> ## Amendment, 2026-11-05: crew readies no worktree; a place is equipped by sluice at Flume's asking
>
> Accepted as record 0023's amendment of the same day, on the same approval and the same words. Built by crew's change `crew-readies-no-worktree-a-place-is-equipped-by-sluice` on `teamless/deneb`.
>
> 1. **Point 4.** No crew command readies a worktree. A place's toolchain is run before any agent starts in it by sluice's equip at Flume's launch (sluice 147; Flume record 0036). So the evaluation cache is still warm, and an agent's first wrapped command still costs what a warm entry costs: the cold evaluation stays before the agent, and is sluice's.
> 2. **Point 5.** sluice and the gate are unchanged. sluice prints a kit's toolchain, and sources it for each step of its equip and for every command of a run, outside any session. crew has no adapters.
> 3. **The question left open is closed.** A devenv kit's `enterShell` installs nothing on any entry. It only activates, so the script `devenv print-dev-env` prints, which sluice and Flume source, installs nothing (the kit standard's toolchain.8). What `.prototools` pins is installed by sluice's equip in a working copy sluice or Flume readies, and by a devenv task before the shell's entry for a person's or an agent's command.
>
>    crew's task, `crew:proto:install`, runs `proto install` only while a pin is missing from crew's proto home. An install that found every pin installed took 2.8 of a warm entry's 3.2 seconds (mac-studio, 2026-10-13), and an agent enters the shell for every command it runs (point 2). That status is the build's choice. Not taken: an install on every entry, as flume's task has it, and devenv's `execIfModified`, which is kept per checkout and so cannot see the home every worktree shares.

**1.3** Record 0028, `docs/adr/0028-a-fix-starts-in-a-place-that-could-not-be-made-ready-and-a-fix-is-dropped.md`. Add a line below the H1 title, before *Status*:

> Superseded in part 2026-11-05 by the amendment below: point 1, and the drivers and consequences that rest on crew readying a fix's or a unit's place. Points 2 and 3 are not readiness and are not amended here.

At the record's end, after *Considered options*, add:

> ## Amendment, 2026-11-05: crew readies no worktree; a place is equipped by sluice at Flume's asking
>
> Accepted as record 0023's amendment of the same day, on the same approval and the same words. Built by crew's change `crew-readies-no-worktree-a-place-is-equipped-by-sluice` on `teamless/deneb`.
>
> crew readies no worktree. A fix's, unit's and chore's place is Flume's, equipped by sluice at Flume's launch (sluice 147; Flume record 0036). So point 1 is not crew's to decide. Whether a stage starts in a place whose equipping failed is Flume's: a first stage waits, or a fix starts with the failed step and its words in its prompt (Flume 12, S16). Point 1's appeal to record 0023's point 4 goes with that point (record 0023's amendment).

Each record's check is two greps: one finds its `Superseded in part 2026-11-05` line, and one finds its `## Amendment, 2026-11-05: crew readies no worktree` heading. Run them from the checkout's root:

```
for r in 0023 0024 0028; do
  grep -c '^Superseded in part 2026-11-05' docs/adr/$r-*.md
  grep -c '^## Amendment, 2026-11-05: crew readies no worktree' docs/adr/$r-*.md
done
```

Each prints 1.

**2.1** The delta and `.openspec.yaml` are written: `retire_capabilities: true` sits beside `schema` and `created`. Check that they still validate after any edit. In `tests/py/test_kit.py`:

- the module docstring's second line becomes "crew readies no place: Flume has sluice equip it (Flume record 0036; sluice 147).";
- `SCRIPT` goes, since nothing reads it.

Then `git grep -n kit-toolchain -- plugin tests README.md CLAUDE.md docs/architecture` prints nothing. Records and archived changes keep their history.

**3.1** The texts:

- **`.config/sluice.toml`.** Its opening comment's first sentence becomes:

  ```
  # crew's policy for sluice, read from each branch's own revision: what crew's toolchain and tests are, with which sluice
  # equips every working copy of crew it runs in, and a Flume place of crew's at Flume's asking (`sluice equip`, sluice's
  # clause 147; Flume's record 0036), crew readying none: the toolchain only activates, and sluice's equip installs what
  # .prototools pins (the kit standard's toolchain.8); and what gates a merge into a bolt and a landing on main.
  ```

  The rest of the comment and every table are unchanged.
- **`README.md` line 18.** Its first sentence becomes:

  > A unit's, chore's and fix's places are Flume's: Flume makes each and has sluice equip it at the revision its launch read, `sluice equip`, with the tools the kit declares in its `.config/sluice.toml` and `.prototools`, as sluice equips every working copy it runs in (Flume's record 0036; sluice's clause 147). What runs there is said by the kind and the kit's own files, its `CLAUDE.md`, its `openspec/config.yaml` and its `.config/flume.toml`. crew readies no worktree, its landing's included, which sluice's submission equips as any submitter's.

  The sentence on what crew reads of the policy follows, unchanged.
- **`plugin/lib/kit.py`.** Its docstring's "crew readies no place: a unit's, chore's and fix's places are Flume's, readied by its kind and the kit's own files." becomes "crew readies no place: a unit's, chore's and fix's places are Flume's, which has sluice equip each at its launch (`sluice equip`; Flume record 0036, sluice 147)."
- **`tests/t-docs.sh`.**
  - Add one check. It fails unless the README holds both "crew readies no worktree" and "`sluice equip`". It also fails unless `.config/sluice.toml`'s lines above its first table hold `sluice equip` and do not hold `plan.17`. It ends in one `ok` naming both.
  - Its opening comment says what the check proves.
  - Its `# Reads:` line gains `.config/sluice.toml`.
  - Run `tests/moon-tasks` and commit `tests/moon.yml`.

**4.1** Write the contract case first and see it fail on today's `devenv.nix`. Then change `devenv.nix`.

- **The case**, in `tests/contract/test_toolchain.py`: `test_the_toolchain_crews_policy_names_only_activates`.
  - It reads `.config/sluice.toml` with `tomllib` from crew's root (`pathlib.Path(__file__).resolve().parents[2]`) and runs its `tests.toolchain` list there with `subprocess.run(..., capture_output=True, text=True, check=True)`.
  - It gives the run a limit that holds on a loaded host (`tests.8`): a cold evaluation is seconds, so allow ten minutes, as `tests/lib.sh`'s waits do.
  - It asserts the output holds `proto activate` and no `proto install`. Each assertion's message names the toolchain command.
  - Its docstring names what assumes it: sluice's equip and Flume's readiness source the script this prints, sluice's inside its executor (sluice 147, C.2), and the kit standard's toolchain.8 says sourcing it installs nothing.
- **The module docstring.** Its "crew's own choice (plan.17)" becomes "crew's own choice (record 0023, point 5)", since `plan.17` is retired. Add a sentence for the new case.
- **`tests/moon-tasks`.** The contract tier's extra inputs in `TIERS`, today `[]`, become `["/.config/sluice.toml"]`. The docstring's account of the tiers' inputs says the contract tier also takes crew's policy, whose toolchain it runs. Run `tests/moon-tasks` and commit `tests/moon.yml`.
- **`devenv.nix`, as Decision 3 has it.**
  - Define the homes once in the `let`. A suitable shape is a shell fragment that sets `_crew_common` from `git -C "${config.devenv.root}" rev-parse --path-format=absolute --git-common-dir` and exports `PROTO_HOME="$_crew_common/proto"` and `MOON_HOME="$_crew_common/moon-home"` when it can. `enterShell` keeps using `_crew_common` for moon's cache link.
  - Add `tasks."crew:proto:install"`:
    - `before = [ "devenv:enterShell" ]`.
    - `status`: the homes, then the `.prototools` read loop moved from `enterShell`, ending `exit 1` at the first missing pin and `exit 0` otherwise, `exit 0` too when there is no `.prototools`.
    - `exec`: `cd "${config.devenv.root}"`, the homes, then `${proto}/bin/proto install --config-mode upwards || true`.
  - `enterShell` loses the read loop and the install, and keeps the cache link, the homes and `proto activate`.
  - The comments move with the code:
    - The paragraph on the 2.8 seconds goes to the task, with why the task has a status.
    - The task's comment also says why it is a task: the script `devenv print-dev-env` prints holds `enterShell` and no task, so the toolchain sluice and Flume source only activates (the kit standard's toolchain.8).
    - The comment above `enterShell` says it only activates.
- **After the change:**
  - `devenv shell -- moon --version` prints `moon 2.6.1`.
  - `devenv print-dev-env | grep -c 'proto install'` prints 0, a reading to make once before `tests/suite contract`, which holds it.

**5.1** Run `tests/suite --affected` once, with uncommitted edits counted. It compares against `main`, moon's default branch. Every task is affected either way: each takes crew's toolchain files, `devenv.nix` among them, and `teamless/deneb` differs from main in them already. sluice runs the same tasks again at the landing.
