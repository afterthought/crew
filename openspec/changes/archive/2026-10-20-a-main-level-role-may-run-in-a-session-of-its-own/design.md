# Design

Rules relied on: `code.5` (the teams file is checked before use, no default), `teams.2` (never a role over a running agent, nor a pane taken for another's), `teams.6` (a role's override lives under `roles.<role>` in the teams file), `teams.9` (state files replaced whole), `read.1` (say what can't be read), `code.3` (a main-level command runs on the main level's host). Pages touched: `teams.md`.

1. The session lives beside model and effort under `roles.<definition>`, as swancloud's `herdr.3` amendment names it, so the teams file's shape gains one key and no new section. It is checked against the hosts file at load: a session of the main level's machine, in the partition.
2. A role apart stays on the main level's machine, so every main-level command still forwards to one host (`code.3`), and the role's folder is the main level's checkout, reached by its absolute path whatever the session's space.
3. The main level's own session keeps the state folder it always had, `<label>-main`, so a main level that names no session apart reads its panes as before; a session apart has its own.
4. A state folder records the session its panes are in (`where`): pane ids mean nothing in another session, and a main level moved to another session took another agent at the same pane id for its own on deneb on 2026-10-20. Panes recorded in another session are set aside under `stale/`; a folder from before `where` is taken as the current session's.
5. A role moved while its agent runs would be started twice: up refuses, naming the agent, its session and pane; down ends every agent a main state's panes file names, so the move is `crew main down`, then `crew main up`.
