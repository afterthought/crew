# Design

Rules relied on: `code.5` (the teams file checked before use, no default), `teams.16` (a team builds one bolt at a time), `teams.5` (a bolt only in a kit whose policy names its checks), `plan.12` (a command reads each kit once), `read.1` (what can't be read is said). Pages touched: `teams.md`, `plan.md`.

1. The bolt's `Repo` in the plan already names its kit, so nothing new is written: crew takes the team's kit from the bolt wherever it holds one (`bolt_team`), and from the bolt the team holds where it has only the team's name (`held_team`, `at_work`), the plan read once for that.
2. A team of one kit is as it was: every helper returns it unchanged, so the teams that hold one kit take no new read of the plan.
3. A survey asked of a team with a bolt reads that bolt's kit, and of a team with none every kit it holds, so a team's status sees its slots wherever they are.
4. The give chooses its bolt before it reads the kit's policy, since the policy is the bolt's kit's; the write gives the same bolt, read again at the tip it replays on (`plan.1`).
