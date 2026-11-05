# A kit renamed on its host is renamed across the plan in one act

## Why

On 2026-11-05 the user renamed four repositories on GitHub and across the fleet: agentplot/flywheel-cloud became boomdrive-cloud, flywheel-runner became boomdrive, flywheel-web became boomdrive-web, and tailrace became timber. The hosts file crew reads, `~/.config/swancloud/herdr-hosts.json` (swancloud's `lib/herdr-hosts.nix`), now lists `agentplot/timber` and `agentplot/boomdrive-cloud` in deneb's spaces and neither old name. madswan's plan on afterthought/crew-state still names `Repo: tailrace` in 21 records and `Repo: flywheel-cloud` in 2. Those names no longer resolve: a crew command on their work is refused because no space on deneb keeps them.

No crew command renames a kit. A proposal can only drop the work and add it again, which loses each item's history and its signals' links. That way cannot carry the started bolt `you-sign-in-to-staging` either. Its unit `one-seam-turns-every-credential-into-a-principal` has merged into `bolt/you-sign-in-to-staging` (#1, 84393d4), and adding it again would rebuild it from scratch. That bolt is the first through crew and Flume, and it cannot land until its kit resolves.

## What Changes

- **A new plan command, `crew kit rename <old> <new>`.** In one commit it rewrites the `Repo` of every Bolt and Unit record that names `<old>` to `<new>`, and writes one `kit.rename` entry in the run record naming both names and how many records it renamed.
  - A proposal may hold it: the planner proposes it and the user approves it on the proposal's card. The user may also run it at a shell. Any other agent is refused, naming the planner.
  - It is refused when the partition's main-level host keeps no repository by `<new>`, or still keeps one by `<old>`. So the plan follows the fleet and never runs ahead of it.
  - It rewrites nothing else of the plan, appends no request and launches nothing.
- **What crew recorded under a former name is read under the kit's name now.** Some of crew's records are never rewritten:
  - the launches in `requests.rec`;
  - the run record's landings and entries;
  - a fix of main's work name;
  - a landings card's or decision record's card key;
  - a source's repository.

  crew reads each of these through the partition's `kit.rename` entries, in the order they were written. A partition's kits, `crew bolts`, the board, the page and a kit's deploys all name a kit by its name now.
- **A command given a former name writes the name now and says so.** So a proposal approved after the rename applies under the new name. A new repository made under a former name is refused.
- **A kit's landings card follows the rename.** The card under the former name closes saying so, and `land/<new>` is raised for its rows.
- **crew reads where a runner keeps a kit from the runner's own report.** The report is a new file on the runner's branch, `repositories.rec`, naming each repository the runner keeps and its folder, matched by the kit's name now.
  - Today crew takes the folder from a place's status in Flume. After a rename, that status still names the clone's old folder.
  - A runner that reports no repositories is read as today.
  - A runner that reports its repositories but not the kit is named as not keeping it, with the rename as the way on.
- **A refusal for a kit the main-level host does not keep** now names `crew kit rename` as the way on when the kit was renamed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: a kit is renamed across the plan in one act. What crew recorded under a former name is read under the name now. A command given a former name writes the name now.
- `drive-state`: a runner's branch reports the repositories it keeps (`repositories.rec`), and crew reads a kit's folder from that report. The main-level host's refusal for a kit it does not keep names the rename.
- `run-record`: the `kit.rename` entry.
- `rail-cards`: a kit's landings card follows its rename.
- `plan-proposals`: a proposal's card draws a kit's rename.

## Impact

- **Code.** `plugin/lib/plan.py` gets the command, its op, the role table, the renames read with the landings, `kit_now` and the reads that go through it. `plugin/lib/runner.py` reads `repositories.rec`, and `where` takes a kit's folder from it. Also changed: `plugin/lib/cards.py` (the proposal card's block and a card key's kit), `plugin/lib/ops.py`, `plugin/lib/page.py`, `plugin/lib/record.py`'s act list, and `plugin/bin/crew`'s usage.
- **Docs and the brief.** README, `plugin/skills/crew/SKILL.md` and the planner's brief, whose command table gains the command.
- **Tests.** The logic tier, the contract tier's recfix cases and `t-journey-plan`.
- **Untouched.** `docs/architecture/` and `docs/adr/`: no rule changes, and the pages are the design agent's (`docs.7`). The board's views keep their shape, so the mod needs no change (`code.8`).
- **Where it lands.** Only on `teamless/deneb`. Nothing goes to crew's main, which deploys to every host.
- **What the started bolt needs from other tools.** Its landing also rests on two changes to the Boomdrive runner and one to swancloud, named in the design:
  - the runner takes a launch whose `Repo` names a former address of a repository it keeps;
  - the runner writes `repositories.rec`;
  - swancloud gives each repository entry its former addresses.

## Touches

```
plugin/lib/plan.py
plugin/lib/runner.py
plugin/lib/cards.py
plugin/lib/ops.py
plugin/lib/page.py
plugin/lib/record.py
plugin/bin/crew
plugin/roles/planner.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_kit_rename.py
tests/py/test_kits.py
tests/py/test_runner.py
tests/py/test_parser.py
tests/py/test_plan_roles.py
tests/py/test_proposal_card.py
tests/py/test_rail.py
tests/py/test_main_fix.py
tests/py/test_proposals.py
tests/py/test_ops.py
tests/py/test_page.py
tests/py/test_board.py
tests/py/facts.py
tests/contract/test_recfix.py
tests/t-journey-plan.sh
tests/t-briefs.sh
tests/moon.yml
```
