# After a restart, crew revive brings back each standing agent of this host whose pane came back with no agent in
# it: from its last conversation, or fresh when it never had one, as for a main level never spoken to. Agents that
# came back are left alone, a revived conductor is greeted, and a team or main level taken down stays down.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha
clone WilldanGroup/willdan-blueprints "$(space mac-studio willdan)/willdan-blueprints/main"
export CREW_LABEL=wldn
gone() {  # gone <session> <agent>: the agent's pane comes back from a restart with no agent in it
  local p; p=$(as $box herdr --session "$1" agent get "$2" | jq -r .result.agent.pane_id)
  as $box herdr --session "$1" agent prompt "$p" /exit >/dev/null
}
launched() { jq -r --arg a "$1" 'select(.agent == $a) | .argv | if index("--resume") then "resumed" else "fresh" end' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
starts() { jq -r --arg a "$1" 'select(.agent == $a) | .agent' "$CREW_TEST_CLAUDE_LOG" | wc -l | tr -d ' '; }
greetings() { grep -c "^$box wldn-1 agent prompt swb-1-conductor " "$CREW_TEST_LOG" || true; }

crew up swb-1 >/dev/null
HOST=$box CREW_TEST_NO_MESSAGE=1 crew main up wldn >/dev/null
HOST=$box crew operator up wldn >/dev/null
crew up swb-2 >/dev/null; crew down swb-2 >/dev/null
gone wldn-1 swb-1-conductor; gone wldn-3 wldn-design
: > "$CREW_TEST_CLAUDE_LOG"; : > "$CREW_TEST_LOG"
HOST=$box expect_ok crew revive
has "$out" "swb-1-conductor resumed"; eq "$(launched swb-1-conductor)" "resumed"; eq "$(greetings)" "1"
has "$out" "wldn-design has no conversation to resume; starting it fresh"; eq "$(launched wldn-design)" "fresh"
for a in swb-1-ops wldn-planner wldn-ops wldn-dispatch-$box wldn-operator-$box; do eq "$(starts $a)" "0"; done
has "$out" "swb-2 was taken down; it stays down"; eq "$(starts swb-2-conductor)" "0"
ok "revive brings back the agents whose panes came back empty, resumed or fresh, and leaves the rest alone"

: > "$CREW_TEST_CLAUDE_LOG"
HOST=$box expect_ok crew revive
eq "$(wc -l < "$CREW_TEST_CLAUDE_LOG" | tr -d ' ')" "0"
ok "revive starts nothing when every agent is up"

crew resume swb-2 >/dev/null; gone wldn-1 swb-2-ops
HOST=$box expect_ok crew revive
has "$out" "swb-2-ops resumed"
HOST=$box crew main down wldn >/dev/null
: > "$CREW_TEST_CLAUDE_LOG"
HOST=$box expect_ok crew revive
has "$out" "wldn was taken down; it stays down"; eq "$(starts wldn-design)" "0"
ok "a team brought back up is revived again, and a main level taken down stays down"
