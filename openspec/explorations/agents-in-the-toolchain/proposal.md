> A proposal (2026-10-12), written by a solver from `invariants.md` in the elaboration session: how every Claude Code agent crew starts, and flywheel after it, comes to work inside its kit's toolchain. It recommends and decides nothing; the user decides. The reading beside it (`reading.md`) holds the cases; record 0023 holds the declaration and the adapter it builds on.

# Agents in their kit's toolchain: the proposal

Words used below. A *kit* is a repository a team builds; a *place* is a worktree crew makes for a bolt, unit or fix; *readying* is what crew does when it makes a place (record 0023, `plan.17`): it runs the kit's declared toolchain command, keeps what it prints, and sets the runner up inside it. The *toolchain adapter* is `plugin/lib/kit.py`. The *launcher* is `plugin/bin/crew-role`, which starts every role crew starts. The *fleet* is swancloud's configuration of the hosts; the *shim* is its `claude`. *sluice* runs a kit's checks and merges outside any session; *flywheel* is what crew becomes, composing sluice's SDK.

## The design in one line

Enter, then start, and watch the files: crew's launcher enters the kit's declared toolchain and starts Claude inside it, so everything the session starts inherits it; Claude Code's own file watcher keeps the session's commands on the worktree's files as they change; and a session that came up some other way is told so in one line and brought back whole by `crew resume`.

```
kit's worktree                      crew                                        the Claude Code session
.config/sluice.toml  ──declares──▶  readying (plan.17): print the toolchain ──▶ <git dir>/crew/toolchain/<key>.sh
devenv.nix, .prototools, …          key = hash(command words, inputs' contents)         │
     │                                                                                 ▼
     │          crew start, crew resume ──▶ crew-role: source <key>.sh </dev/null; export CREW_TOOLCHAIN=<key>; exec claude …
     │                                                 everything inherits: Bash, subagents, MCP, language servers, hooks, `!`
     │                                                                                 │
     └── file changes ──▶ FileChanged / CwdChanged hook (crew's plugin): key(files now) ≠ CREW_TOOLCHAIN?
                           print through the cache, write the difference to CLAUDE_ENV_FILE, one line to the agent
herdr restart ──▶ bare `claude --resume <id>` ──▶ SessionStart hook (source resume): no CREW_TOOLCHAIN → the same
                                                   entry through CLAUDE_ENV_FILE, one line; `crew resume` brings it back whole
```

The one mechanism is the launcher entering before Claude starts, which is how a sandbox or a dev container gives a tool its environment (containers.dev, `userEnvProbe` and `remoteEnv`: the environment is collected once and handed to the tool and its subprocesses). Claude Code's docs name this as the way to persist an environment: "Activate your virtualenv or conda environment before launching Claude Code" (tools reference, *What persists between commands*). The hooks are the second half the same docs supply: `CLAUDE_ENV_FILE` is "populated dynamically by SessionStart, Setup, CwdChanged, and FileChanged hooks" (env vars, `CLAUDE_ENV_FILE`), and CwdChanged "pairs with FileChanged for tools like direnv that manage per-directory environment" (hooks, *CwdChanged*). They do not re-enter the process; they keep its Bash commands current and cover a start crew did not make.

## 1. Each way a session starts (I4)

| start | what happens | rests on | cost |
|---|---|---|---|
| crew starts a role (stage, conductor, ops, main level) | `crew-role` finds the place's print for the key of its files now, prints it when none exists, sources it in the pane's own environment with stdin from `/dev/null`, exports `CREW_AGENT`, `CREW_LABEL`, `SLUICE_AGENT`, `CREW_TOOLCHAIN=<key>`, and execs `claude` | process inheritance; the adapter's `in_toolchain` form (`bash -c 'source "$0" >&2; exec "$@"'`), already crew's and sluice's | 0.05 s to source crew's 83 KB print (measured); the cold print, about 20 s for a devenv kit, is paid at readying before any agent starts, or at this start when the files changed since |
| `crew resume <team> <role>` | the same launcher with `--resume <id>`, in the folder the session began in (`teams.6`) | the same | the same |
| herdr's server restarts | herdr runs a bare `claude --resume <id>` from the pane's saved folder (herdr, *Session state and restore*, "Native agent session restore"); crew's plugin SessionStart hook, which already gives the agent its names back on this path, sees no `CREW_TOOLCHAIN`, enters through `CLAUDE_ENV_FILE` and tells the session in one line that its Bash commands are inside and its MCP and language servers are not until `crew resume` | Claude Code hooks, *Persist environment variables*: "Each Bash command runs the file's contents as shell code before the command itself" | one print (warm, 0.2 s measured) per start; a `crew resume` by ops to make it whole, which ops does after a crash today |
| `/clear`, compaction | the same process, environment kept; SessionStart runs again (`clear`, `compact`) and finds the marker, so it only checks the key | hooks, *SessionStart* matchers | a hash of a few files |
| a hand start in a kit's checkout, or a hand `claude --resume` | not crew's: the checkout's own SessionStart hook enters the kit's shell (crew's and swancloud's `.claude/hooks/devenv-shell`, `tests.7`), through the same declaration if the kit chooses; or the user's own settings run `direnv export bash` into `CLAUDE_ENV_FILE` at SessionStart, CwdChanged and FileChanged, the pairing Claude Code's docs name for direnv, which reads no stdin because "command hooks run in their own session without a controlling terminal" | hooks pages above; direnv man page, `direnv export` "prints the diff in terms of exports" | the kit's or the user's |
| flywheel, through sluice's SDK | the Agent SDK's `env` option "replaces the subprocess environment", so flywheel passes the toolchain's environment and the same plugin hooks (`plugins`, `hooks` options) | Agent SDK TypeScript reference, `Options` | the same as crew's |

The clean answer for herdr's restart is herdr running crew's launcher instead of `claude --resume`. herdr documents it: an agent reports its own resume command, and "it takes precedence over Herdr's built-in resume command for that agent" (socket API, *Agent state reporting*; *Add Herdr support to your agent*). It is not usable today, by facts, not belief: a resume command is kept "only while the same source and agent hold the pane", holding means reporting state with `report-agent`, and a state report replaces herdr's reading of the screen. Probed on 2026-10-12 in a throwaway named session on herdr 0.9.3: a pane whose foreground process carried `HERDR_AGENT=claude` read as `idle` from the screen; after `report-agent --source crew --agent claude --state working -- touch <file>` the pane's `agent_status` was `working` while `agent explain` still read the screen as `idle` (`screen_detection_skipped: false`); `--state unknown` made it `unknown`; the resume command was in the saved `session.json` while held and gone after `release-agent`, and the pane went back to the screen's `idle` within ten seconds. So crew would own the pane's state, which `teams.11` and `teams.15` read from herdr, unless it reported Claude's whole lifecycle itself, and herdr's own guidance is against it: "User hooks that run next to a Herdr-managed integration should use metadata instead of `report-agent`" (*Integrations*, custom status labels). Hence the feature request below. Whether herdr 0.9.3 runs a self-reported command after a restart was not tested: a restore runs "after a client attaches", which this session could not do; the building unit checks it with the doc's own recipe in a named session, with a stub `claude` first on the server's PATH so nothing real starts.

## 2. Following the files, and the cache (I6, I7)

**The key.** The kit's declaration gains one line beside `toolchain`: `toolchain_inputs = ["devenv.nix", "devenv.lock", "devenv.yaml", ".prototools"]`, the files the command reads, in sluice's words (its piece 11 names this list for a devenv kit and found that devenv's own input list is not safe to key on, since it includes the user's overlays and `devenv.local.nix`). The key is a hash of the command's words and each input's contents, an absent input hashed as absent. crew reads it in the adapter beside `toolchain`, so the same one edit moves it to `flywheel.toml`.

**The place.** `<worktree git dir>/crew/toolchain/<key>.sh`, with `current` pointing at the newest: what readying keeps at `<git dir>/crew/toolchain.sh` today, named by key. Readying prints when the key has no file, so a worktree made ready again after a rebase that bumped `.prototools` prints once; a key already printed costs a hash.

**Why per worktree, not per host.** The print is bound to its place: crew's names the worktree seven times (`DEVENV_ROOT`, `DEVENV_DOTFILE`, `DEVENV_STATE`, the `.devenv/run` link, and the `enterShell` lines that use `config.devenv.root`), and devenv's own evaluation cache is per root (sluice: a copied cache "was not used"). A script printed in one place sourced in another would put the kit's hooks and moon cache in the wrong worktree. So I7's "once per revision per host" does not hold for `devenv print-dev-env` as devenv prints it; what holds is once per revision per place, paid at readying before any agent starts, so a start adds under a second, and the host-wide sharing is nix's store, which holds the built shell, so the cold cost is evaluation alone. sluice's candidates are places of their own and pay the same; the key is what crew and sluice share, so both know when a print is stale, and the devenv request below is what would make the print itself shareable.

**Following.** The plugin's SessionStart hook returns `watchPaths` for the session's worktree's inputs (hooks, *SessionStart decision control*). A FileChanged hook, which "runs the hook no matter what changed the file", and a CwdChanged hook run the same script: compute the key from the files now; when it differs from `CREW_TOOLCHAIN`, print through the cache (cold once, inside the hook's timeout) and append the toolchain's difference to `CLAUDE_ENV_FILE`, so the agent's next Bash command, its tests among them, runs on the new toolchain without a restart. The script must be sourced in the session's own environment, never resolved elsewhere: the print begins `PATH=${PATH:-}; nix_saved_PATH="$PATH"` and ends `PATH="$PATH${nix_saved_PATH:+:$nix_saved_PATH}"`, so the host's path follows the kit's only where it is sourced. The agent learns of the change in the words that brought it: a rebase whose diff touches an input says so in crew's rebase words, and the hook's one line says what changed and that MCP and language servers follow at the next start. CwdChanged clears what FileChanged wrote ("until the next CwdChanged event, when Claude Code clears them"); whether it clears SessionStart's lines too is undocumented, so the CwdChanged hook re-asserts both the toolchain and the identity lines, and the design holds either way.

## 3. Who does what (I5)

- **The kit** declares `toolchain` and `toolchain_inputs` once, in `.config/sluice.toml`. Its `enterShell` installs nothing (sluice's rule: the printed script runs again wherever it is sourced). Nothing in its CLAUDE.md tells an agent to wrap a command. A kit that wants hand sessions inside its shell keeps or adds its repository hook; crew's and swancloud's exist.
- **crew** extends readying to the keyed cache; the launcher enters then starts, refusing to start when a declared toolchain cannot be printed (`read.1`); the plugin's SessionStart hook returns `watchPaths`, records `CREW_TOOLCHAIN` in the session record, and on a start without the marker enters through the env file and says so; FileChanged and CwdChanged hooks keep the Bash environment current; `crew bolts` and the agents' views show an agent that herdr brought back outside its toolchain (`code.8`). The adapter also runs `proto install` before `moon --version` when the place has a `.prototools`, as sluice's runner does: a print holds `enterShell` and none of devenv's tasks, so moon is not installed by the print alone.
- **The fleet** changes nothing. Two options are its own: the shim, which already resolves the account for herdr's bare resume, could also enter the toolchain of a crew session it finds in crew's session records, making that path whole without crew; and a user-level direnv hook for the user's own sessions. crew's correctness rests on neither.
- **Nothing has to:** no brief, skill or README wraps a command; sluice changes only by the new key; herdr changes nothing today; the fleet's direnv gate stays off.

## 4. What stays uncovered, and the cost

- **herdr's bare resume** runs MCP servers, language servers and hooks outside the toolchain until `crew resume`; Bash commands are inside at once. Cost: one `crew resume` per agent after a herdr restart, which ops already does; the board says which agents need it. Closed by the herdr request.
- **A change under a running session** reaches Bash commands at once and MCP and language servers at the next start (I6's "at the latest").
- **Subagents and the env file.** Claude Code's docs say the file applies to "Bash commands" and nothing of subagents. Inheritance covers them on every launcher start; after a mid-session change, or on a bare resume, a subagent may run on the start-time environment. How to find out: a hook that writes one variable and a subagent that echoes it, in a test session.
- **A kit that declares nothing** gets nothing (I5). A role in a kit's main checkout or in a folder of several kits gets what that checkout's own hook gives; crew's mechanism is for the places it makes. A role that reaches other kits through `--add-dir` runs on its own worktree's toolchain in every folder, as today.
- **The host's devenv version** is not in the key; a devenv upgrade changes a print only when an input changes.
- **I7's host-wide cache** is per place, for the reasons in section 2.

## 5. `tests.7`, the repository hooks, record 0023's held point

`tests.7` is amended by the record that accepts this: an agent crew starts works inside its kit's declared toolchain, entered by crew's launcher before Claude starts and kept to the worktree's files by crew's plugin's hooks; a session a hand starts in crew's checkout enters crew's shell by the checkout's SessionStart hook; no CLAUDE.md, README, brief or skill wraps a command; worktrunk's merge hooks and sluice enter the shell themselves. Its "rules out" becomes: a launcher that names devenv; the plugin entering a toolchain for a session that is not a crew agent's in a place crew made; a brief that wraps. crew's repository hook stays for hand sessions and can read the same declaration and cache, one code path; it already leaves a session whose `DEVENV_ROOT` is the checkout alone, which is what a launcher start sets, so an agent gets no second entry. swancloud's hook is swancloud's, generated by its `devenv.nix`; the same pattern is open to it. Record 0023's first held point closes with a record of its own, which amends 0023 and `tests.7` in the same commit (`docs.5`, by the design agent, `docs.7`), and `_open.md` takes what is not built: the herdr resume command, sluice's key.

## Alternatives, and why not

- **The plugin enters every session's shell** (reading, A): changes the user's sessions in every kit unasked, which was the user's doubt; Bash only; against `tests.7`'s reason.
- **Each kit's repository hook alone** (B): a copy per kit, Bash only, a kit without one gets nothing; kept for hand sessions, not as the mechanism.
- **`crew-role` runs `devenv shell -- claude`** (C): names devenv; a blank pane for the cold shell; this design is C with the declared print in its place and the cold cost paid at readying.
- **The env file alone** (D): one command at a time, by Claude Code's own account; kept as the refresh and the fallback, not the entry.
- **Per-run sourcing by the agent** (E): the wrapping the user ruled out (I3).
- **herdr's self-reported resume command now:** takes the pane's lifecycle authority (section 1); the request below.
- **`CLAUDE_CODE_SHELL_PREFIX`**, a wrapper Claude Code runs around "Bash tool calls, hook commands, status line commands, and stdio MCP server startup commands" (env vars): wider than the env file and could follow the files per command, sluice's shape, but it is wrapping by another name, leaves language servers and Claude itself outside, and whether a worktree's settings may set it is undocumented. Worth a probe as a stronger fallback for the bare resume.
- **An `env` block in the worktree's local settings:** applies "no matter how `claude` was launched" and is re-applied when the file changes (env vars, *Set variables in settings files*), which would cover every path and I6 in one file; but its values are literal, so the kit's path could not be composed with the pane's at source time, crew would write a file Claude Code also writes, and whether `PATH` is accepted from project and local settings is not stated (the drop list names `HOME`, `TMPDIR`, `XDG_*` and not `PATH`). Rejected on the first point.
- **The shim enters:** fleet-dependent; fine as the fleet's extra, not as crew's mechanism.
- **direnv's, devenv's, mise's or proto's shell hooks on:** prompt-time activation of an interactive shell; Claude's commands run no prompt, and the fleet turned direnv's off because it read the pane's input (I10).
- **moon's toolchain alone:** "moon prepends the executables of each toolchain that the task runs against to `PATH`" for tasks only; a dependency install ran the host's bun (record 0023).
- **Claude Code's `processWrapper`:** covers processes started from Claude's own binary (the background service, agent view), not terminal sessions, and project and local settings may not set it.
- **A container per place:** the pattern this design borrows, beyond the fixed points.

## Feature requests

- **herdr:** a way to attach a resume command without lifecycle authority, for instance `resume_argv` accepted on `pane.report_agent_session` from a source that reports no state, or a per-agent resume template in `config.toml`. With it, herdr's restart runs `crew role <scope> <role> resume` (the first word must be a plain name on PATH; `crew` is, `crew-role` is not) and every start path is the launcher: P3 complete.
- **Claude Code:** state whether `CLAUDE_ENV_FILE` applies to subagents' Bash commands and whether CwdChanged clears SessionStart's lines; both are facts the design works around.
- **devenv:** a relocatable `print-dev-env`, or an evaluation cache keyed by the inputs rather than the root, so one print per revision serves every worktree and every sluice place.
- **sluice:** `[tests] toolchain_inputs` and the key above in its policy, its piece 11.

## The invariants

- **I1** holds: the kit's print is first on the path from the first command, the host's after it.
- **I2** holds on every launcher start by inheritance; on herdr's bare resume, Bash only until `crew resume`.
- **I3** holds: nothing is wrapped by an agent; the gate's `devenv shell --` is worktrunk's and sluice's own.
- **I4** holds for crew's starts and resumes, `/clear` and compaction; herdr's restart is covered with the one gap above; a hand start is the kit's or the user's by the same documented hooks.
- **I5** holds: `toolchain` and `toolchain_inputs` in one file; crew names no tool.
- **I6** holds for Bash commands without a restart, for the rest at the next start, with crew's words saying so.
- **I7** holds for a start's cost; the cache is per place, not per host, and the proposal says why and what would change it.
- **I8** holds: the gate prints fresh and strips a session's variables; `CREW_TOOLCHAIN` is outside sluice's kept list.
- **I9** holds: the launcher sets the names on every path it runs; the SessionStart hook restores them on a bare resume as today.
- **I10** holds: the launcher sources with stdin from `/dev/null`; hooks run without a terminal; crew still types a prompt only once the agent accepts input (`teams.15`).
- **I11** holds: a launcher that cannot print refuses to start; a hook that cannot enter says so in one line and the agent stops; nothing falls back silently.
