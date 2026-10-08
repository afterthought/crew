# Tasks

## 1. Entering a crew checkout enters crew's shell

- [x] 1.1 A Claude session that starts in a crew checkout runs every command inside that checkout's devenv shell, through a committed SessionStart hook that is silent when it works and gives the session one line, naming no workaround, when it can't (design: Decisions "The repository's SessionStart hook, as swancloud's"; Task notes 1.1).
- [x] 1.2 A person entering a crew checkout with direnv enters the same shell, and devenv's and direnv's working files never show as changes in a checkout (design: Decisions "The checkout is clean after the shell"; Task notes 1.2).
- [x] 1.3 `tests/run` refuses to start outside a devenv shell and says how to enter one (design: Decisions "The runner refuses outside a shell"; Task notes 1.3).

## 2. The suite holds it

- [x] 2.1 `tests/t-dev-shell.sh` shows the hook entering the shell, keeping other hooks' lines, leaving a session already inside alone, and telling a session it could not enter, and fails when any doc an agent reads says `devenv shell --` (design: Decisions "The check that holds the rule"; Task notes 2.1).

## 3. The docs and the rules

- [x] 3.1 CLAUDE.md, the README and the comments in `.config/wt.toml` and `bolt-verify.sh` say agents work inside crew's shell and run the tests and the bolt's verification unwrapped, with the merge hooks' commands unchanged (design: Decisions "What enters the shell, and what doesn't"; Task notes 3.1).
- [x] 3.2 crew's testing rules carry `tests.7` and the amended `tests.1`, and load for the files this change adds (design: Task notes 3.2).

## 4. The suite

- [ ] 4.1 The whole suite prints `0 failed` in this worktree (design: Task notes 4.1).
