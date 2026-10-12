# A deploy is approved and recorded through crew

## Why

swancloud's deployer is built and has waited since 2026-10-09 on crew's deploy commands: until crew answers them it
offers, deploys and records nothing, its doctor row warns, and the fleet is deployed by hand. ADR 0012 and `plan.14`
decided the shape: a landing deploys nothing; a deploy is one act by the kit's deployer under the environment's
policy; a `manual` environment's deploy waits on the user's word given through a rail row's card; every act and every
after-deploy step is in the run record.

## What Changes

- `crew ops offer|approve|word|record|step|steps|quiet`, the operations on an environment, a deploy being one kind (the
  user, 2026-10-11: a command after a deploy is an operation, not a deployment), which swancloud's adapter (`crew.sh`) calls,
  run where the partition's main level runs, as the one asking, on that host's run record (`ops.*` entries).
- An offer is a rail row under a new group, *operations*, keyed `deploy/<env>/<sha>`, whose card main-level ops posts;
  holding it is the user's word, recorded with `crew ops approve`; `crew ops word` gives it to the deployer for
  one deploy.
- Every other operation is a step, after the deploy it names or on its own; one the user is to take that waits is a
  rail row of its own, `op/<env>/<n>`.
- crew's card hook lets main-level ops post under an open deploy row's key, and no other.
- main-ops's brief posts the deploy cards and records the word; the dispatcher's takes after-deploy steps the deployer
  hands it.

## Touches

```
plugin/lib/ops.py
plugin/lib/plan.py
plugin/lib/record.py
plugin/bin/crew
plugin/roles/main-ops.md
plugin/roles/dispatcher.md
plugin/skills/crew/SKILL.md
README.md
docs/architecture/plan.md
docs/architecture/briefs.md
docs/architecture/_open.md
openspec/specs/main-level/spec.md
openspec/specs/crew-rail/spec.md
tests/t-ops.sh
tests/t-rail.sh
tests/t-batches.sh
tests/t-cards.sh
tests/t-briefs.sh
tests/moon-tasks
tests/moon.yml
```
