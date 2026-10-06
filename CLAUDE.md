# crew

crew runs bolt teams of Claude agents in herdr, and each partition's main level. `README.md` says how it works; `openspec/` holds its changes, and `openspec/explorations/findings-to-design/roadmap.md` their order.

## This checkout is live

On every host, the `crew` command and the plugin every Claude session loads run from that host's checkout of crew's `main`: mac-studio's is `~/Code/github_afterthought/crew/main`, the box's `/workspace/crew/main`. A commit on `main` there is live at once for every agent on that host, and a host gets crew's `main` by `git pull`, not a deploy. So work is built in a unit's or bolt's worktree, never in `main`, and a bolt lands only on the user's word.

## Tests

- Run them only as `devenv shell -- tests/run [name...]` from the worktree's root. Never run a `tests/t-*.sh` file with bash: `tests/run` is what puts stub herdr, ssh, claude and hostname first on the path and gives each test a scratch HOME and bare remotes. A test run outside it reaches the real agents, the real plan on GitHub and the real repos. Every test stops on its first line when `TESTS` is unset; a new test keeps that line.
- `tests/run` exits 0 even when a test fails: read its summary line, and only "0 failed" passes.
- Inside devenv's shell `sed` is GNU sed. A test edits a fixture in place with `rewrite` from `tests/lib.sh`, never `sed -i ''`.

## Proving and landing a bolt

- **Before landing:** the full suite on the bolt's head, with "0 failed". That is the bolt's proof; there is nothing to deploy.
- **After landing:** a change's *Proof on real work* section needs the live system, so it is worked once the bolt has landed and every host has pulled: mac-studio's checkout at once, the box's with `git -C /workspace/crew/main pull --ff-only`. Pull every host in the same step: a crew behind the others can refuse what a newer one writes.
- A standing agent loads its brief when it starts. A landing that changes a brief takes effect for each agent at its next fresh start, or by telling it what changed.
