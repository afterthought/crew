# Proposal

## Why

A partition's design agent and planner are both Fable. With one session for the whole main level they draw on one Claude account. The user, on their card req_3da02d33 on 2026-10-20: a main-level role may run in a session of its own, so the two sit in two sessions on two accounts; and in their session the same day, of wldn: "i want to split wldn main as well".

## What Changes

- A partition's `roles.<role>` in the teams file may name a `session`, a session of the main level's machine in the partition; the role runs there, and the reviewer, named none, beside the planner. A dispatcher's session can't be named.
- `crew main up`, `down`, `status`, `crew review` and `crew revive` place and find each role in its session: a `<label>` workspace in each, its state in `<label>-main` for the main level's own session and `<label>-main-<session>` for another.
- `crew main up` refuses while a role's agent still runs in a session it no longer stands in, and `crew main down` ends it there.
- An agents' state folder records its session; panes recorded in another are set aside and said, never taken for this session's.
- Every main-level brief names where each role runs and on which account.

## Capabilities

### Modified Capabilities

- `main-level`: the teams file may name a session per main-level role; the main level is a workspace in each of its sessions.

## Impact

`plugin/lib/crew.py` (`roles_of`, `load`, `role_session`, `main_sessions`, `main_state`, `mains`, `main_holding`, `Agents.ensure`, `moved_said`, `Agents.panes`, `main_tokens`), `plugin/lib/plan.py` (`main_cmd`, `moved_role`, `review_cmd`, `revive_cmd`); swancloud's `lib/crew-teams.nix` and `herdr.3` name the sessions.
