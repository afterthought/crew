# Design

## Context

See proposal.md for why. What shapes the approach:

- crew starts every role and stage agent with `claude` in a crew checkout: a stage in its unit's or fix's place, the conductor and ops in the bolt's worktree or the kit's main (`crew.py` 378, 383). Nothing puts that session in crew's devenv shell, so CLAUDE.md (Tests, line 21; Proving and landing, line 28) and the README (Needs) tell the agent to wrap commands in `devenv shell --`.
- swancloud solved the same problem (swancloud's record 0003, "The shell"; its CLAUDE.md, "swancloud's shell is devenv"; commit 7a1c87e). The fleet keeps direnv's hook off in Claude sessions and herdr panes, so a `.envrc` alone never reaches an agent. Instead, a SessionStart hook in the repository's committed `.claude/settings.json` runs `.claude/hooks/devenv-shell`, which enters the checkout's devenv shell once, has it dump its environment as JSON to a temporary file, and appends an `export` to `CLAUDE_ENV_FILE` for each variable the shell set or changed. It is live in every swancloud worktree, crew-started stages among them.
- Claude Code's hooks reference (code.claude.com/docs/en/hooks, read for this change): `CLAUDE_ENV_FILE` is given to SessionStart hooks, and the `export` lines written to it apply to every later Bash command of the session; hooks append to it so they keep each other's lines. SessionStart fires on `startup`, `resume`, `clear`, `compact` and `fork`. `CLAUDE_PROJECT_DIR` is the project root the session started in. Hooks in `.claude/settings.json` are the project's, committable. A command hook's default timeout is 600 seconds.
- crew's plugin already has a SessionStart hook (`plugin/hooks/session-start`) that appends `CREW_AGENT` and `CREW_LABEL` to the same file when herdr resumes an agent. The two hooks append independently; neither truncates.
- devenv sets `DEVENV_ROOT` to the checkout inside its shell (checked in this worktree: `DEVENV_ROOT`, `DEVENV_PROFILE`, `DEVENV_STATE` under `.devenv/`). Its first entry in a fresh worktree takes about 20 s, later ones under a second (`openspec/explorations/command-cost/reading.md`).
- `.devenv/`, `.direnv/` and `.envrc` are ignored on mac-studio only by the user's global git ignore, not by crew's `.gitignore`. A host without that ignore would see `.devenv/` as untracked, and an untracked file keeps a worktree (`worktrees-go-with-their-work`).
- `.config/wt.toml` runs the gate as `devenv shell -- env CREW_TEST_LIVE= tests/run` and the verification as `devenv shell -- sh .config/hooks/bolt-verify.sh {{ target }}`. worktrunk runs them for whoever merges, and the user's approval is keyed to each command's exact text.

Rules relied on: `tests.1` (amended here: the runner also refuses outside a devenv shell), `tests.2` and `tests.3` (the new test's guard line and fixtures), `tests.4` (the stand-in devenv behaves as devenv does for what the hook reads: it runs the command after `shell --` in the checkout, with `DEVENV_ROOT` set), `tests.5` (the gate is unchanged), `code.1` (the hook is standard-library Python; devenv declares no new package), `code.6` (`.envrc` is staged by path), `roles.3` (the rule is held by a check in the suite, not by wording alone), `read.1` (a shell that can't be entered is named, never guessed), `docs.5` (a new rule, `tests.7`, and `tests.1` amended in the same commit). Areas touched: `tests.md` (`tests/**`, `.config/**`, and the paths this change adds to it), `docs.md` (`README.md`, `CLAUDE.md`, `docs/`, `openspec/`).

Departure: `tests.1`'s text changes (it gains the shell check). And this change's own coder works in a session that started before the hook existed in this worktree, so it runs the suite once as `devenv shell -- tests/run` (Task notes 4.1); every stage after it starts inside the shell.

## Goals / Non-Goals

**Goals:**
- Every Claude session in a crew checkout runs every command inside that checkout's devenv shell, from its first command, on every start.
- No document an agent reads tells it to wrap a command in `devenv shell --`, and the suite fails if one does.
- `tests/run` never runs a test with the host's tools in place of the shell's.

**Non-Goals:**
- Which tests an agent runs, and the moon tasks: `the-suite-runs-as-moon-tasks`.
- Putting `wt`, `openspec`, `moon` or `herdr` in crew's devenv: they stay the host's, on the shell's path after its own (`code.1`; `moon` is the moon unit's to pin).
- Changing the merge hooks' commands, which would ask the user for approval again on every host for no gain.
- Any other kit's shell, and crew's plugin hooks: the hook is crew's repository's, not the plugin's, so it reaches only sessions in crew checkouts.
- wtenv (one evaluation shared across worktrees): a spike, per record 0008.

## Decisions

### The repository's SessionStart hook, as swancloud's

`.claude/settings.json`, committed by hand, holds one SessionStart hook: `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/devenv-shell"`, timeout 600. No matcher, so it runs on every source. The file is written by hand rather than generated by `devenv.nix` as swancloud's is: crew has no other project settings to generate, and a generated file would still need committing, since a session opens in a fresh worktree before devenv has run there.

`.claude/hooks/devenv-shell` is swancloud's hook with crew's words. It:

- does nothing when `CLAUDE_ENV_FILE` is unset;
- takes the checkout as the real path of `CLAUDE_PROJECT_DIR`, or of the directory two above the script;
- does nothing when `DEVENV_ROOT` already names that checkout (a session started from a terminal already in the shell);
- runs `devenv shell -- <its own python> -c <dump> <tmpfile>` in the checkout, stdin closed, devenv's stdout sent to the hook's stderr, under a 570-second limit, and reads the JSON it wrote;
- appends `export NAME=<shell-quoted value>` for each variable whose value differs from the hook's own environment, skipping `PWD`, `OLDPWD`, `SHLVL`, `_`, `TMP`, `TMPDIR`, `TEMP`, `TEMPDIR`, `NIX_BUILD_TOP`, `DEVENV_CMDLINE` and any name that isn't a shell identifier; variables the shell dropped are left alone;
- prints nothing when it succeeds; when devenv is missing, fails, times out or writes nothing readable, or anything else goes wrong, it writes nothing to the file and prints the one line below to stdout, which Claude Code gives the session as context. It never exits non-zero.

The line: "This session is not in crew's devenv shell: devenv could not be entered when it started. crew's tests and merge gate need that shell; say so rather than going on without it." It names no workaround. The cause goes to stderr.

Why a hook and not crew's plugin: the plugin is loaded by every session in every kit, and what the shell is belongs to the checkout. Why not `devenv shell -- claude` in crew-role: it would put the shell in crew's start command for every kit, would not survive a herdr resume (a bare `claude --resume`), and would hold a pane's start for the evaluation.

### What enters the shell, and what doesn't

Every agent command runs in the shell because the session does. worktrunk's two hooks keep entering it themselves: they run for whoever merges, main-level ops included, and their text is what the user approved. An agent already in the shell entering it again for the gate costs under a second. Only the comments in `.config/wt.toml` and `bolt-verify.sh` change, so no approval is asked again.

### The runner refuses outside a shell

`tests/run` checks `DEVENV_ROOT` first, before the stubs and tools: unset or empty, it prints how to enter the shell and exits 2. It checks only that a devenv shell is in force, not which checkout's, since the bolt's verification runs it from an archived copy with the bolt's worktree as `DEVENV_ROOT`.

### The checkout is clean after the shell

crew's `.gitignore` gains `.devenv/` and `.direnv/`, and `!.envrc`, so the tracked `.envrc` is not hidden by a global ignore. `.envrc` holds swancloud's two lines, `eval "$(devenv direnvrc)"` and `use devenv`.

### The check that holds the rule

`tests/t-dev-shell.sh` fails when `devenv shell --` appears in `CLAUDE.md`, `README.md`, anything under `plugin/roles/` or `plugin/skills/`. A new rule, `tests.7`, says so.

## Risks / Trade-offs

- [A fresh place's first session waits about 20 s for devenv before its first command] → The hook runs inside Claude Code after it is up, so a pane shows its agent at once; it is the cost swancloud already pays, and wtenv is where it would shrink.
- [devenv missing or broken on a host] → The session starts and is told in one line; the runner refuses rather than running on the host's tools; the box is checked in the proof below.
- [Two SessionStart hooks write to one file] → Both append; the shell's hook exports only what devenv changed, so `CREW_AGENT` and `CREW_LABEL` from crew's hook are never overwritten with another value.
- [A session resumed with a stale environment line] → Every start re-enters the shell and appends afresh; later lines win when the file is sourced.

## Proof on real work

Items 1 to 3 hold once this unit has merged into its bolt, in places branched from the bolt after it; 4 to 6 once the bolt has landed and every host has pulled.

1. The next stage crew starts in a crew place after this merge: its first Bash command shows `DEVENV_ROOT` naming that place and `command -v recsel` under a devenv profile, with no line about the shell in its first context.
2. That stage ran the project hook without a trust or permission prompt (crew's stages start unattended), and `git status --porcelain` in its place showed nothing from devenv.
3. A crew agent herdr resumed in a crew place has its crew name and its shell (`CREW_AGENT` and `DEVENV_ROOT` both set).
4. This unit's own merge, and the next, ran the gate from a session already inside the shell, and the gate ran and reported as before.
5. On mac-studio, a new session in crew's main checkout is in the shell.
6. On the box, a new session in a crew place or `/workspace/crew/main` is in the shell, or shows the one line if devenv can't be entered there; either way `git status` there shows no `.devenv/`.

## Task notes

**1.1** `.claude/settings.json`, new: `{"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/devenv-shell\"", "timeout": 600}]}]}}`, formatted with two-space indents. `.claude/hooks/devenv-shell`, new, executable, from swancloud's (`~/Code/github_afterthought/swancloud/main/.claude/hooks/devenv-shell`) as Decisions give it: rewrite its docstring for crew (crew's shell, why the hook is the repository's, that crew's plugin hook appends to the same file), use crew's failure line, and keep its constants and structure. Standard library only (`code.1`).

**1.2** `.envrc`, new, as Decisions give it; stage it by path (`code.6`). `.gitignore`: add `.devenv/`, `.direnv/` and `!.envrc`.

**1.3** `tests/run`: before the stub check, `[[ -n ${DEVENV_ROOT:-} ]] || { echo "<message>" >&2; exit 2; }`. The message: "tests/run runs inside crew's devenv shell: a Claude session in a crew checkout is in it from its start; from a terminal, enter it with devenv shell, or direnv with the checkout's .envrc". Extend the opening comment by one sentence.

**2.1** `tests/t-dev-shell.sh`, new, with the guard line and an opening comment (`tests.2`). It needs no `world`. A stand-in `devenv` in `$T/bin`, first on `PATH`, as `t-merge-gate.sh` writes one: it refuses anything but `shell -- <command>`, logs each call to `$T/devenv.log`, exits 1 when `$T/devenv-fails` exists, and otherwise runs the command with `DEVENV_ROOT=$PWD`, `DEVENV_PROFILE=$T/profile`, `PATH=$T/profile/bin:$PATH`, `CREW_SHELL_PROBE='a b'` and a changed `TMPDIR`. Run the hook as `env -u DEVENV_ROOT CLAUDE_PROJECT_DIR=$T/repo CLAUDE_ENV_FILE=$T/env python3 "$CREW/.claude/hooks/devenv-shell" </dev/null` (the suite itself runs inside the shell, so `DEVENV_ROOT` must be cleared). Show:
- entered: stdout empty; a line already in `$T/env` is kept; sourcing `$T/env` in a fresh `bash` gives `DEVENV_ROOT` the real path of `$T/repo`, `CREW_SHELL_PROBE` as `a b`, and `PATH` starting `$T/profile/bin`; no `export TMPDIR`, `PWD` or `HOME` line;
- no `CLAUDE_ENV_FILE`: nothing written, no call logged;
- `DEVENV_ROOT` already the checkout: the file unchanged, no call logged;
- devenv fails, and devenv absent from `PATH`: the file unchanged, exit 0, and stdout exactly one line holding "not in crew's devenv shell" and not "devenv shell --";
- `.claude/settings.json` parses (with `python3 -c`) and its one SessionStart command names `.claude/hooks/devenv-shell` with timeout 600;
- `env -u DEVENV_ROOT TMPDIR=$T/tmp "$CREW/tests/run" t-docs` (with `$T/tmp` made empty) exits 2, prints "devenv shell", and leaves `$T/tmp` empty;
- no `devenv shell --` in `$CREW/CLAUDE.md`, `$CREW/README.md`, or any file under `$CREW/plugin/roles` and `$CREW/plugin/skills` (`grep -rF`), naming each file that holds it;
- `$CREW/.envrc` holds `use devenv`, and `$CREW/.gitignore` holds `.devenv/`, `.direnv/` and `!.envrc` (read as files, not through git, so the check holds in the verification's archived copy).

**3.1** `CLAUDE.md`. Under "Tests", first bullet: "Run them only as `tests/run [name...]` from the worktree's root", the rest as it is. Add a bullet before it: crew's shell is devenv (`devenv.nix`); a Claude session in any crew checkout enters it at start through the SessionStart hook in `.claude/settings.json` (`.claude/hooks/devenv-shell`), so every Bash command runs in it, with devenv's tools first and the host's (herdr, wt, openspec, git) after; a session that could not enter it is told so in one line, and says so rather than going on; no agent wraps a command in `devenv shell --`, and only the merge hooks in `.config/wt.toml` enter the shell themselves; `tests/run` refuses outside it; from a terminal, `devenv shell`, or direnv with the checkout's `.envrc`. Under "Proving and landing a bolt": "run it again there with `sh .config/hooks/bolt-verify.sh`". `README.md`, Needs: the tests paragraph ends "Run it in crew's devenv shell, which a Claude session in a crew checkout is in from its start; a terminal enters it with `devenv shell`, or direnv with the checkout's `.envrc`." in place of ": `devenv shell -- tests/run`". `.config/wt.toml`: the comment's last sentence becomes "ops runs a bolt's verification again with `sh .config/hooks/bolt-verify.sh` from the bolt's worktree, in the shell its session is in.", plus one sentence that the hooks enter the shell themselves because worktrunk runs them for whoever merges; the two commands stay byte for byte. `.config/hooks/bolt-verify.sh`: the usage line in its opening comment becomes `sh .config/hooks/bolt-verify.sh`.

**3.2** `docs/architecture/tests.md`: add `.claude/settings.json`, `.claude/hooks/**` and `.envrc` to `paths`. Amend `tests.1` to say the runner also refuses to start outside a devenv shell. Add `[tests.7]`: "A Claude session in a crew checkout works inside crew's devenv shell, entered at its start by the checkout's SessionStart hook; no CLAUDE.md, README, brief or skill tells an agent to wrap a command in `devenv shell --`, and only worktrunk's merge hooks enter the shell themselves." Its details: Rules out `devenv shell -- tests/run` in CLAUDE.md; a brief telling an agent to wrap a command; the shell entered by crew-role or by the plugin. Source: signal `2026-10-08-swancloud-planner-0ca5793d/01-agents-run-inside-the-shell-and-only-affected-tests`; swancloud's record 0003, "The shell"; this change; `tests/t-dev-shell.sh`. `docs/architecture/core.md`: the `tests.md` row's "Loads for" adds `.claude/`, `.envrc`.

**4.1** This coder's session began before the hook was in this worktree, so it is not in the shell: run the suite once as `devenv shell -- tests/run` and it must print `0 failed`. That is the last time an agent wraps it; the verify and merge stages start fresh, inside the shell.
