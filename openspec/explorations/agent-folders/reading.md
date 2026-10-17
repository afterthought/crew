# Agent folders: a reading

A reading, not a decision: what is true on crew's main (2d7b87b9, 2026-10-16), what you settled today in the sluice design session (the three handover files under `~/.claude-sub-ia/plans/worktrees-*.md`) and on the pane since, and what crew builds from it. Every fork is settled; record 0032 and the OpenSpec change follow from section 4.

## 1. What you settled today, in plain words

**No folder has `main` or a bolt branch checked out.** Each kit's `<kit>/main` stays where it is, same path, but detached: it points at a commit, not at the branch, so sluice moving the branch leaves it whole instead of half-moved. Nobody works in it. Swancloud's timer (a few minutes) fetches and moves every such folder to GitHub's `origin/main`. Crew never moves one. Sluice only warns when a folder holds a branch it lands on, never refuses a landing and never touches a folder. Crew learns of landings and conflicts by polling `sluice overview --json` (sluice v0.12.0, not on mac-studio yet: installed is 0.11.0 with no `overview`).

**Bolts go to GitHub like main, and sluice makes and ends their branches.** A bolt's branch is only a ref on GitHub; nothing runs for it, and the worktrees come later, cut from it by crew as places. So the words are git's:

```
crew bolt give <b>
   |
   v
sluice branch create bolt/<b> --from origin/main     a push leased on the branch being absent, as sluice's app
   |
   v
crew cuts places from origin/bolt/<b>                 units, chores, fixes, each on its own branch as today
   |
   v
submissions land on bolt/<b>                          sluice's leased push, already built
   |
   v
the bolt lands on main                                sluice, already built
   |
   v
sluice branch delete bolt/<b>                         refused while the branch is not in main, or a submission is queued on it
   |
   v
crew bolt land <b> tidies the plan
```

Why the hand is sluice's: the `bolt/*` ruleset on each kit then names one writer, sluice's app, for create, update and delete, as main's does; the app's key is unattended on every host, where crew's git on a Mac goes through 1Password's agent and asks a person; sluice's records know whether anything is still queued on the branch, so the delete can refuse safely; and `state.5` stands as written, crew pushing nothing to a kit's remote. Sluice's cost is two commands and a statement amendment: its statement has a move expecting a revision, and "expected absent" and a delete are not in it yet. Crew keeps `give` and `land` as its words and calls these underneath. Until sluice ships them and swancloud deploys that sluice to the fleet, bolts stay local as today, and crew refuses a give that needs them, naming the version. The creation-only ruleset check sluice landed today (#15) comes out: `bolt/*` is app-only.

**Crew's plugin has two modes, and the live checkout goes away.** Today every Claude session on a host loads crew's plugin from the `main` checkout folder (swancloud's account tools pass `crew/main/plugin` as `--plugin-dir`), so a landing is live for every agent the moment the folder moves, with nothing versioned or pinned. After, each host is in one of two modes, set in swancloud's hosts file:

```
released

  bolt lands on crew main (sluice, on GitHub)
        |
        v
  crew's release Action tags v0.x.y by git-cliff   .github/workflows/release.yml, on every push
        |                                          to main (code.10; v0.1.0 and v0.1.1 exist today)
        v
  swancloud's release adapter sees the tag  -->  crew signal land
        |
        v
  a bump chore pins crew at v0.x.y in swancloud  -->  sluice lands it
        |
        v
  the deployer deploys  -->  sessions load crew's plugin from the nix store,
                             the path every other plugin in the catalog loads from

live (testing)

  swancloud's timer moves  crew/live        a detached worktree, never on a branch
        |
        v
  --plugin-dir crew/live/plugin             loaded in place; a landing is live minutes later
```

In both modes main lands on GitHub through sluice as today, and the Action tags every landing: a host in live mode loads what its folder holds, whatever the tags say, and a released host loads the version swancloud pins. Released mode needs nothing new in crew; swancloud adds crew to its release sources, its catalog, and the per-host toggle, and makes `crew/live`. `--plugin-dir` takes only a local folder, so the catalog is how a pinned version reaches a host. The box runs the held crew (`box-hold`) on a local branch today; released mode, pinned at a tag, is its way off that, when wldn moves to main.

That replaces the direction my brief started from: no per-agent `<kit>/agents/<agent>` folders, nobody "tells agents main moved", no asking sluice to refuse.

Before and after, one kit on mac-studio:

```
today                                   after
crew/                                   crew/
  crew.git            (bare)              crew.git            (bare)
  main        [main]  <- crew runs here   main        (detached at origin/main; the timer moves it)
  bolts/<b>   [bolt/<b>]  legacy          bolts/<b>   (gone, or detached while a legacy bolt lasts)
  places/<unit>  [unit/<unit>]            places/<unit>  [unit/<unit>]   unchanged
  places/land-<b>  [bolt/<b>] (minutes)   places/land-<b>  [bolt/<b>] (minutes, unchanged)
```

Who works where, after:

| who | folder | on a branch? |
|---|---|---|
| design agent, planner, main ops, dispatch | the partition's blueprints `main` folder, or their own worktree | under the rule, section 3: sluice does not land blueprints, and the design agent and the daily pass commit on its `main` in that folder today |
| each team's conductor and ops | the kit's `main` folder | no, detached; the conductor reads the bolt by ref (`git log bolt/<b>`) |
| a unit, chore or fix stage | `places/<name>` | yes, its own branch, as today |
| the `crew` command and crew's Claude Code plugin (its skills, hooks and the band above each prompt), which every Claude session on a host loads | released mode: the pinned copy in the nix store, deployed by swancloud; live mode: `crew/live/plugin`, a detached folder the timer moves | no; in live mode a crew landing is live for every agent on the host once the timer moves `crew/live`, minutes later; in released mode when swancloud deploys the pinned version |
| swancloud's deployer and releaser | their own detached folders | already so today; nothing to change |

## 2. Crew's handover checked against main

The line numbers hold: nothing under `plugin/`, `tests/lib.sh` or `docs/architecture/` changed between 339379b and 029bea0. What I found beyond the handover:

1. **The deployer and releaser need nothing.** Both already make a detached folder of their own from the bare repository and check it out clean at each run. The handover's "deployer reads main's objects" is done.
2. **Crew's code reaches a host by its mode, not by the landing.** The plugin loads from `crew/main/plugin` today (swancloud's `claude-account-tools.nix`): the landing levels mac-studio's folder at once and ops pulls the box's. After, a host in live mode takes it when the timer moves `crew/live`, minutes later, and a host in released mode when swancloud deploys the pinned version. CLAUDE.md's "This checkout is live" and ops's step 3 are rewritten to say so, and `crew/main` becomes an anchor like any kit's.
3. **Dropping the levelling step cannot go first.** If crew stops running `read-tree` before the timer is deployed, crew's own folder stays on branch `main` and goes stale at the next landing, with nothing moving it. The landing script already tells the two cases apart (it levels only when the folder is on branch `main`). So crew keeps the step while a folder is on the branch, says nothing when it is detached, and the step is deleted once every host's folder is detached. Then crew's part lands in either order with swancloud's.
4. **"Main is behind GitHub's" loses its reason.** Crew refuses a landing while the host's `main` lags GitHub's, because the push would need force. Sluice now lands main by a leased push to GitHub and fetches `origin/main` every round; the host's local `main` lags on every host that did not land, by design. Kept as it is, the refusal would stop landings for nothing; it goes (section 3).
5. **Crew writes nothing into a kit's policy.** The handover has crew's readying "write the remote into a kit's declaration". Crew only reads `.config/sluice.toml` (`plan.17`). Each kit's own change adds `remote = "origin"` under its bolt branches, and crew refuses to give a bolt whose policy lacks it, as it refuses one with no checks today.
6. **Legacy bolt folders before bolts are on GitHub.** The tidy's "detach at `origin/bolt/<b>`" needs part 1 first. Until then it detaches at the local `bolt/<b>`. Crew has two such folders on mac-studio, swancloud one, wldn's eight teams on the box have theirs.
6a. **A bolt crew made before part 1 is local only.** Once part 1 lands, sluice refuses a submission to it until it is on GitHub, so crew's first read of such a bolt asks sluice to create it there at the bolt's local tip (`sluice branch create bolt/<b> --from <tip>`), and says so.
7. **Nothing of crew's reads the landing's branch name.** The bolt's verification reads only the `Sluice-Result` trailer, and the landing's result reads only exit, old and new. So the landing folder stays on `bolt/<b>` with nothing to rename (section 3).
8. **Reads of "main now" become reads of `origin/main` after a fetch**: the policy read, the landing's head, the archive a change folder is read from (today the working tree of the `main` folder), the fix that "takes main into the bolt" (`git merge main` in the coder's brief), the branches the design agent and the operator cut for their own commits, and the bolt branch crew makes. The handover lists most; the design agent's and operator's cuts are the two it names open.
9. **A unit starts on no bolt whose landing is queued.** Sluice lands what was submitted, so a unit landing on the bolt meanwhile is left out of main's landing and `crew bolt land` refuses until a second submission carries it. Crew refuses the unit start instead, naming the queued landing (your word on the pane, 2026-10-16).
10. **Stage waits need no change to learn a landing on this host.** A unit's merge is read from the bolt holding its change archived, re-read every ten seconds from refs on the team's host; that keeps working. The overview gives what refs cannot: a conflict or a blame named to the place it came from, and a cheap "nothing changed" (`version`). With bolts on GitHub, a bolt moved by another host's queue is seen only after a fetch, which sluice's own rounds do on the host that runs the queue.
11. **The box.** wldn's teams run the held crew (`box-hold`, 2c1774c) with its `main` folder on the branch, pulled by ops. Swancloud's timer runs on the box too (a systemd timer, its part 4). Until that deploy, ops's box step stays. The box's move to today's crew is the recovery session's, after.

## 3. What you settled on the pane, 2026-10-16

- **The landing folder keeps `bolt/<b>`** for the minutes the main queue takes. Sluice warns and lands anyway; nothing else lands on the bolt by then. The folder goes once sluice takes a submission by branch name (record 0026 lists it).
- **The landing card closes at the landing**, at `crew bolt land`: "landed on GitHub's main at `<sha>` (#<n>); every host's folder follows by swancloud's timer within minutes." Nothing waits on a host. "Agents told" is gone: none works in a folder that moves.
- **The "main is behind GitHub's" refusal goes** (`plan.8`, set 2026-10-13). It guarded crew's own push of main after a landing; sluice pushes with a lease now, forming every landing on `origin/main`, and a host's local `main` lagging is by design. Crew records the landing's head from `origin/main` after a fetch.
- **Blueprints comes under the rule.** Its folder is detached like every kit's; it gets a sluice policy (`main` with `remote = "origin"`, checks as prose wants, perhaps none); the design agent and the daily pass commit on a branch in a worktree of their own and submit. No checked-out `main` anyone edits directly.
- **Crew's release Action keeps tagging** in live mode. Nothing changes; unused versions tick up until a host goes released.
- **A unit starts on no bolt whose landing is queued** (finding 9).

**On staleness.** Any folder the timer moves is up to minutes behind GitHub, where today a landing levels the kit's folder at once on mac-studio and ops pulls the box's. A session reads its CLAUDE.md at its start either way. Where an agent or crew must read "main now", it reads `origin/main` after a fetch (`git show origin/main:<path>`), which crew's own reads do in part 4 and which the briefs say for a landed rule or record an agent needs at once.

## 4. What the record and the change will say

Record 0032, proposed: *No worktree holds main or a bolt branch; a kit's main folder is a detached anchor the fleet's timer moves, and crew reads by ref.* It amends `state.3`, `state.5`, `plan.8`, `plan.9`, `plan.16`, `teams.3`, `teams.6` and CLAUDE.md's "This checkout is live", and names the sluice ask (warn, `overview`, `branch create` and `branch delete`, refuse a submission to a bolt GitHub lacks, a submission by branch name) and swancloud's part (detached clone, the timer, views, its own bolts on GitHub, the plugin's two modes and the per-host toggle, the release adapter's crew line, the catalog entry).

One OpenSpec change, `no-worktree-holds-main-or-a-bolt-branch`, in seven parts, built in this order:

| part | what | waits on |
|---|---|---|
| 2 | legacy `bolts/<b>` detached when clean, named when dirty | nothing |
| 3 | the landing folder on `bolt/<b>`; the levelling step conditional, then gone; no unit starts while the landing is queued | nothing |
| 4 | every "main now" read is `origin/main` after a fetch; briefs lose `read-tree` and the push; `plan.8` dropped; the card closes at the landing; the design agent's and the daily pass's commits on blueprints from a branch | nothing |
| 5 | waits read `sluice overview --json` for conflicts and blames | swancloud's bump of sluice on the fleet (0.12.0 or later) |
| 6 | `crew status` names a folder holding a queued branch | sluice shipping `holds_queued_branch` in the overview (its handover's part 1, not in 0.12.0) |
| 1 | bolts on GitHub: the policy line, `give` calling sluice's `branch create` and `land` its `branch delete`, every bolt read from `origin/bolt/<b>` | sluice shipping `branch create` and `branch delete` and swancloud's bump of sluice on the fleet; your app-only `bolt/*` rulesets on each kit; swancloud's part 6 beside it |
| 7 | crew's plugin by mode: CLAUDE.md's "This checkout is live" rewritten; `crew/main` an anchor like any kit's | swancloud's toggle, `crew/live`, release-sources line and catalog entry |

Parts 2 to 4 come before crw-1 is brought back; then part 1 together with swancloud's part 6, once sluice ships the two commands, swancloud deploys that sluice and the rulesets are set; part 5 on the same sluice deploy; part 6 once sluice ships the field, built alone; part 7 with swancloud's plugin change, live mode first on every host, released mode once a crew release has been captured and deployed. Nothing a team holds in a place changes, so no team loses work: a unit's place is on its own branch and stays.
