```
wt merge --no-squash --no-remove
```

`--no-squash` keeps your per-task commits, which the conductor reads; `--no-remove` keeps the worktree for the change's next group. The gate is `devenv shell -- suite-verify` and takes about five minutes. Never add `--no-hooks` or `--yes`. After the merge your branch and main are the same commit, and the next group carries on from there.

In this worktree the commit hook is bound to the main checkout's path, so commit with `git -c core.hooksPath=/dev/null commit`; the gate at merge runs the same checks on what lands. Your dev sites get their own ports here (`dev-servers`). The gate is where the emulator-backed suites run, against the main checkout's `devenv up`; merges happen one at a time, so they never share it.
