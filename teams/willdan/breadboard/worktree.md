```
wt merge --no-squash --no-remove
```

`--no-squash` keeps your per-task commits, which the conductor reads; `--no-remove` keeps the worktree for the change's next group. The gate is `devenv shell -- suite-verify`. Never add `--no-hooks` or `--yes`. After the merge your branch and main are the same commit, and the next group carries on from there.

Your dev sites get their own ports and names in this worktree (`dev-servers`), so another coder's servers never collide with yours.
