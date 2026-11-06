---
status: proposed
date: 2026-11-06
decision-makers: the user (a rename renames the data that names the kit, and no reader is taught a former name); the design agent (which records that is, and how crew carries it)
---

# 0055. A kit's rename renames every record that names it, and no reader maps a former name

Status: proposed to the user on 2026-11-06, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, 2026-11-06 23:35Z, on agentplot's card proposing that Boomdrive's runner read a launch's repository through crew's renames: "This seems like a terrible thing to hardcode into a fucking system. Wouldn't the root cause be that the original rename didn't rename the parts of the data that were necessary? If anything shouldn't the tools expose some sort of rename functionality? I don't want you to be building fucking custom workaround shit". That a rename renames the data, and that no reader learns a former name, is theirs. Which records that is, and how crew carries it, is the design agent's, on the rules as written.

Amends the change `a-kit-renamed-on-its-host-is-renamed-across-the-plan` (archived 2026-11-05 on `teamless/deneb`): its Decision 1, which renamed the plan alone and read everything else through the run record's renames; Decision 3, `kit_now`; Decision 4, a command given a former name writing the name now; Decision 5, the cards read through the renames; and its Non-Goal "rewriting `requests.rec`, the run record, `proposals.rec`, signals or moves". Its Decision 2 stands but for what the rename writes and what `<old>` may be, below; its Decision 6, the runner reporting the repositories it keeps, stands whole. Amends the rule `record.4`, and adds `plan.22`. Source: agentplot's signal on afterthought/crew-state `agentplot/main`, `signals/2026-11-06-agentplot-planner-230ee466/01-a-kit-rename-renames-every-record-naming-it`.

## Context and problem statement

`crew kit rename` rewrote the `Repo` of the plan's Bolt and Unit records and left everything else under the old name: launches in `requests.rec`, the run record's entries, card keys, the sources naming a decision record's repository. Each reader was to map those names through the run record's `kit.rename` entries. crew's own readers did. Boomdrive's runner does not, and was not meant to learn it: the change asked it for former addresses of its own (its R1). In madswan, boomdrive-cloud's fix request 3, written under `flywheel-cloud` before the rename, was never taken by the runner, which keeps only `agentplot/boomdrive-cloud`, from 2026-11-05 until madswan dropped the fix and launched it again. Every reader that matches a kit by name, crew's or another tool's, would need the same map, and each one that lacked it would fail the same silent way.

## Decision

1. **The user's: a rename renames the data, and no reader maps a former name.** After `crew kit rename <old> <new>`, every record any reader matches a kit by names it `<new>`, and no reader, crew's or another tool's, is taught `<old>`. Each tool renames what is its own: crew its records, Flume a place's stored repository (`flume relocate`), the fleet its clones and their views on each host. crew asks Boomdrive's runner for no former addresses (the change's R1 is withdrawn).

2. **What crew renames.** In the one commit of the act, on the drive's branch, crew renames `<old>` to `<new>` wherever a field holds the kit's name, its forge address, or an object built on it:
   - the `Repo` of the plan's Bolt and Unit records;
   - each launch's `Repo` in `requests.rec`, and the kit in a fix of main's work, `fix/main/<old>/<name>`, wherever a request names that work;
   - the run record's entries on the branch: their `Repo`, and any `On` or `From` that is `kit/<old>`, `land/<old>`, `record/<old>/<n>` or `fix/main/<old>/<name>`; but the `From` of `kit.rename` entries, which records the act;
   - a Source's repository where it names a decision record, `<owner>/<old>:docs/adr/<file>`;
   - the open cards whose keys name the kit, `land/<old>` and `record/<old>/<n>`, which the act closes, saying the kit is renamed, and raises again under the name now, each in its owner's name with its words whole.

   An entry a host still holds unpushed under `<old>` reaches the branch under `<new>`. `Count` in the act's entry is the number of records it renamed, all of them together.

3. **What crew leaves as written, and why.** Words no reader looks a kit up from: the plan's Goals and Intents, signals and `moves.rec`, commit messages, and a closed proposal's `Do` lines, which are what the user approved (`plan.4`). A proposal still open whose `Do` names `<old>` refuses the rename, naming the proposal: the user answers it first, or the planner proposes it again, so no card ever changes under the user (`plan.4`). A proposal may hold the rename, and the commands after it in that proposal name `<new>`.

4. **Nothing maps.** `kit_now` and every read through the renames go. A command given `<old>` after the rename is refused as for any kit the partition does not have, naming what the host keeps (`main_kit_said`); it is never written as `<new>` for the caller.

5. **What `<old>` may be.** A name any record above still holds. So a partition renamed before this record is finished by running the same rename again, which renames what the first run left and writes its own entry; the host's spaces must still keep `<new>` and not `<old>`.

6. **The append-only rules keep their purpose.** `requests.rec` and the run record are still written only by appending, but for a rename's rewrite of a kit's name, one commit with its `kit.rename` entry; the commit holds what each record said before (`state.1`), so no history is lost. `record.4` is amended so, and `plan.22` says the rename.

## Considered options

- **Rename the data that names the kit, crew's records and each tool's own (chosen).** The user's.
- **Rename the plan, and read the rest through the run record's renames.** The change as built. Rejected by the user: every reader needs the map, and one without it fails silently, as the runner did.
- **Teach Boomdrive's runner the renames, or former addresses in its configuration.** agentplot's proposal, rejected by the user on its card.
- **Rename every word too: Goals, Intents, signals, closed proposals, commit messages.** Not taken: no reader looks a kit up from them, and a closed proposal's `Do` lines are the words the user approved.
- **Rewrite an open proposal's `Do` lines.** Not taken: the card the user is answering would change under them (`plan.4`); the rename waits for the proposal instead.

## Consequences

- The fix that builds this carries the delta to the specs: `bolt-plan`'s three rename requirements ("renamed across the plan in one act", "read under its name now", "a command given a former name writes its name now"), `run-record`'s "A kit's rename is one entry naming both its names", `rail-cards`' "A kit's landings card follows its rename", and the `RENAME KIT` block of `plan-proposals`, which names the launches and landings it renames beside the bolts and units.
- madswan's earlier renames, `tailrace` to `timber` and `flywheel-cloud` to `boomdrive-cloud`, are run again once this is deployed, on the user's word or the planner's proposal, so no record of madswan's names either former name.
- The runner's own records on its branches are its own (`state.5`): crew renames none of them and reads none through a former name. Where crew matches one by a kit's name, the fix brings that reading to the design agent rather than mapping it.
