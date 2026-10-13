> A reading (2026-10-12): what an OpenSpec change holds in crew today, what each rule and record says about proof, what the tool itself says, and what the user objected to. It recommends nothing and decides nothing; it is what an elaboration session needs to settle the question with the user.

# What an OpenSpec change holds

## The question

Three things are tangled in one bolt and one unit of the plan: what the parts of a change are for (its spec delta, design and tasks); what "proof" means and where it lives (a task, a *Proof in dev* list, an *After deploy* list, crew's *Proof on real work*); and whether a change is archived when its unit merges (record 0006). The user, reading the plan: "wtf is this? out of the blue we're talking about archive? i just looked at 0006 and it's about running archive on the unit branch during the merge. i feel like this needs design. the ADR talks about "dev proof" and i personally think "dev proof" has no place in an openspec change. openspec is about building functionality. verification should be part of it, but verification should be grounded in what the project does. for my projects that is unit tests run by moon/sluice. this could include integration tests. but proving on dev is outside of the scope of openspec".

## What OpenSpec itself says a change is

Read from the installed tool (1.14.1), its `spec-driven` schema:

- **proposal**: why, what changes, which capabilities are new or modified. "Focus on the why, not the how."
- **specs**: "a behavior contract, not an implementation plan": requirements with "scenarios that can be tested or explicitly validated". The quick test: "if the implementation can change without changing externally visible behavior, it likely does not belong in the spec."
- **design**: how, when the change is cross-cutting or needs decisions: context, decisions with alternatives, risks, a migration plan ("steps to deploy, rollback strategy, if applicable"), open questions.
- **tasks**: "Each task MUST state how to verify completion (a test, command, observable behavior, or delivered artifact)", "track implementation and verification work that can be completed before archive", and anything that needs the change archived first goes as plain bullets under `## Workflow follow-up`, outside tracked progress.
- **archive** moves the change under `openspec/changes/archive/` and applies its spec deltas to `openspec/specs/`; `--skip-specs` for a change with no deltas.

So the tool already places verification in the tasks, grounded in a test or a command, and keeps what cannot happen before archive out of the tracked tasks.

## What crew says today

- **`docs.6`**: the spec delta holds what becomes true; the tasks what the coder proves locally; the design how and why, "with *Proof in dev* as prose only where a check cannot be code"; what must be true after a deploy is code in the same change by the kit's rules; *After deploy* lists only the steps no check can be code, each with its environments and its doer. Its details rule out a task that is a deploy, and a task worked only after the landing, with the case: crw-3's coder on 2026-10-11 copied the design's *Proof on real work* list in as task 6.1 of `units-build-at-once-and-are-reviewed-in-batches`, which held the code stage at 14 of 15; `unit-amendments` had the same and was archived open. Not built: `construct.md` and `openspec/config.yaml` say it once `a-change-holds-what-is-true-and-what-is-proved` lands.
- **`briefs.3`**: a change's tasks never hold proof that needs a deploy, a live account, a credential, a vendor console or the user; that goes under *Proof in dev* in the design, and the team's ops works it from the bolt.
- **`construct.md`**: "Its tasks carry no proof in dev. Its tasks are what a coder can do and prove locally, ending with the tests its change affects green, not the whole suite, which the merge gate runs. What must be checked in dev once the bolt is deployed … is listed under *Proof in dev* in its `design.md`; the team's ops works that list from the bolt."
- **`ops.md`**: on `crew prove`, ops deploys the bolt from its worktree "the way the runbooks say", then works each unit's *Proof in dev* list in order; a failure is a defect for the conductor; what only the user can check is written under *Left for the user* and asked on the landing card. The bolt's verification, the kit's suite after each merge, is a separate thing ops reads.
- **`main-ops.md`** lands a bolt only when "the team's conductor has said the proof in dev is clean for the bolt's head as it is now".
- **Record 0012, point 3** (amended 2026-10-08 and 09): "What must be true once a state is deployed is code in the change that makes it true, by the kit's own rules (a doctor row, a service's test, a pin's assertion; swancloud `testing.6`), and a deploy's checklist is the kit's after-deploy suite"; a design keeps *Proof in dev* for ops before landing and lists under *After deploy* only the steps no check can be code, with a doer. The user's words there, 2026-10-08: "I'm not sure about each unit carrying proof after deploy. I think we need to decide in our open spec instructions what is appropriate".
- **swancloud `testing.6`** says the same from its side, and its `openspec/config.yaml` gives *After deploy* a shape (doer, when, environments, why) that its flake check `after-deploy-steps` refuses when unreadable; its deployer gathers and records the steps.
- **crew's own case**: crew has nothing to deploy, so its changes write "Proof in dev: none" and a *Proof on real work* list, worked by main-level ops after the landing, since crew's main is live on every host (CLAUDE.md, *After landing*; record 0006's "a kit whose proof on real work needs main").
- **Record 0022**: crew's own checks are three tiers run as moon tasks: logic, contract, end to end on stubs; a coder's edit runs the logic tier, every merge gate all three; "nothing in the suite calls a real agent, posts a real card or reaches another host".

## What the sections hold in practice

Counted on 2026-10-12 in each kit's main checkout, by design files that carry the heading:

| kit | changes open / archived | *Proof in dev* | *After deploy* | *Proof on real work* |
|---|---|---|---|---|
| crew | 21 / 28 | 16 / 12 | 0 / 0 | 6 / 16 |
| swancloud | 16 / 59 | 5 / 33 | 3 / 1 | 0 / 0 |

Two shapes of *Proof in dev*. crew's: "None. crew has nothing to deploy; its proof before landing is the suite on the bolt", followed by a *Proof on real work* list of things to watch once teams run on the landed code (a batch card arriving, a dependent's construct starting). swancloud's (`a-box-keeps-its-tailnet-node-across-deploys`): five numbered live steps for ops, a key landed on main, a Headscale restart on the user's yes, the bolt's doctor built from the worktree, an ssh held open across a `tailscaled` restart, a DNS answer on mac-studio; and beside it a doctor row the change adds. An *After deploy* in swancloud (`syncthing-runs-on-mac-studio`): one step, the user reboots mac-studio once and sees the doctor's row green, with why no check can do it.

Not counted: how many of swancloud's 33 archived *Proof in dev* lists held steps a doctor row or a service test could have asserted instead, and how many held steps that are the kit's operation rather than the change's (a restart, a key rotation).

## Where each kit's verification is

- **crew**: moon tasks tagged `suite` (renamed `check-full` on `recovery/toolchain`), the three tiers; the merge gate and the bolt's verification run them; nothing live.
- **sluice**: each check tagged with its tier in `moon.yml` (`check-fast`, `check-tools`, `check-e2e`); a branch's policy names the tiers it requires (`bolt/*` the fast tier, `main` every tier); the landing commit carries the verdict as trailers (sluice records 0002 and 0006).
- **swancloud**: `nix flake check` as the gate, the doctor's rows and each service's test as the after-deploy proof (`testing.6`, record 0019: "the suite is code, and it is the after-deploy proof"), the deployer running the after-deploy steps.
- **switchboard**: suite scripts and `post-merge-verify`; its dev servers per worktree, the origin of "dev" in crew's words.

"Dev" in crew's briefs comes from switchboard's era, a bolt deployed to a dev environment and checked there; crew itself has no dev, and swancloud's "dev" is the fleet's live hosts.

## What the plan would build

- Bolt `changes-say-what-is-true-and-what-is-proved` (crew, no team): "Every change a construct writes says what becomes true in its spec, what the coder proves in its tasks, and how and why in its design, with what must be true after a deploy as code by the kit's rules." Its unit `a-change-holds-what-is-true-and-what-is-proved` puts `docs.6` into `construct.md` and `openspec/config.yaml`, "with proof in dev as prose only where a check cannot be code". Sources: `docs.md`, record 0012.
- Unit `a-merged-change-is-archived` in bolt `work-that-ends-is-swept`, after `landing-sweeps-what-main-holds`: the merge stage archives the change before the branch merges into the bolt, "so the bolt's specs say what its code does, a merged unit is read from the archive as a landed one is, ops's proof reads the archived change, and nothing lands on main open" (record 0006). Record 0006's reasons: a later unit's construct should read its sibling's requirements from the specs, not an open change; nothing kept by hand; the merge's gate, every task ticked, is what an archive needs. Its one tie to proof is a consequence: ops reads the *Proof in dev* list from the archived change. Fourteen landed changes with every task ticked wait as archive chores meanwhile (record 0001; the recovery plan).
- Flywheel Next, which crew aligns with: a claim is a requirement block with scenarios in the blueprints' specs, "proposed while it sits in its intent's change and standing once the intent's landing has archived it"; a verdict is a stored judgment that a repository satisfies a claim, with evidence; a unit's change cites the claims it serves (requirements 34a). Archive at landing is how a claim becomes standing there.

## What is not known

- What a change's verification should say when the kit's checks cannot reach what the change makes true (a daemon that fails only at boot; a key rotation on a live host): whether that is the kit's operation, owned by its deployer and runbooks, or a gap the change must name.
- Whether ops's "prove the bolt" step has any content left once after-deploy truth is code and *Proof in dev* is gone, and what the landing card then asks the user.
- Whether crew's *Proof on real work* is a proof at all, or an observation plan for main-level ops after a landing, and whether it belongs in the change.
- Whether any kit's checks today can assert what swancloud's *Proof in dev* steps check by hand, or what it would take.
- What `/opsx:verify` checks against: the tasks' own verification lines, per upstream's rule that each task states how to verify.

## What an elaboration could settle

1. Whether a change's verification is only the kit's own checks, in the tiers its runner knows (unit, contract, integration, end to end), so a task names the check that proves each scenario and *Proof in dev* leaves the change; and where what it held goes: the kit's operation (record 0012's after-deploy steps), a check the change must add, or nowhere.
2. What `docs.6`, `briefs.3`, `construct.md` and `openspec/config.yaml` then say, and what the queued bolt `changes-say-what-is-true-and-what-is-proved` builds.
3. What becomes of ops's proof of the bolt, `main-ops.md` step 1, and the landing card's "left for the user".
4. Whether crew's *Proof on real work* stays, moves, or goes.
5. Whether archiving at merge (record 0006) stands on its own reasons once proof is out of the picture, and whether `a-merged-change-is-archived` proceeds as queued.
