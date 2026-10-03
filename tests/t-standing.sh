# A team's conductor and ops live in the bolt it holds: they start in its worktree, and a bolt given to a team that
# is up restarts them there before its conductor is greeted. A team on a Mac has a git tab; one on a box has none.
# Every role crew starts has Claude's folder-trust question answered for it, and no other question.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
launched() { jq -r --arg a "$1" 'select(.agent == $a) | .cwd' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
greetings() { grep "^$box wldn-1 agent prompt swb-1-conductor " "$CREW_TEST_LOG" || true; }

expect_ok crew up swb-1
eq "$(launched swb-1-conductor)" "$k"; eq "$(launched swb-1-ops)" "$k"
ok "a team that holds no bolt starts its conductor and ops in the kit's main checkout"

crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 smoke
eq "$(launched swb-1-conductor)" "$kd/bolts/smoke"; eq "$(launched swb-1-ops)" "$kd/bolts/smoke"
eq "$(greetings | wc -l | tr -d ' ')" "1"
has "$(greetings)" "Your team now holds the bolt smoke. Read where your bolt stands"
has "$out" "swb-1-conductor greeted"
ok "a bolt given to a team that is up restarts its conductor and ops in the bolt's worktree, then greets the conductor once"

expect_ok crew down swb-1
: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew up swb-1
eq "$(launched swb-1-conductor)" "$kd/bolts/smoke"; eq "$(launched swb-1-ops)" "$kd/bolts/smoke"
ok "a team that holds a bolt starts its conductor and ops in the bolt's worktree"

expect_ok crew down swb-1
: > "$CREW_TEST_LOG"
CREW_TEST_TRUST=1 expect_ok crew up swb-1
eq "$(grep -c "^$box wldn-1 agent send-keys w[0-9]*:p[0-9]* down enter" "$CREW_TEST_LOG")" "2"
ok "the folder-trust question is answered for the conductor and for ops"

expect_ok crew down swb-1
: > "$CREW_TEST_LOG"
CREW_TEST_BYPASS=1 expect_ok crew up swb-1
eq "$(grep -c "agent send-keys" "$CREW_TEST_LOG")" "0"
ok "the Bypass Permissions warning is never answered"

kit mac-studio willdan atlas-kit >/dev/null
clone WilldanGroup/willdan-blueprints "$(space mac-studio willdan)/willdan-blueprints/main"
expect_ok crew up atl-1
eq "$(herdr_state mac-studio wldn-5 '[.tabs[].label] | join(",")')" "conductor,git"
eq "$(herdr_state $box wldn-1 '[.tabs[].label] | join(",")')" "conductor"
ok "a team on a Mac has a git tab, and a team on the box has none"
