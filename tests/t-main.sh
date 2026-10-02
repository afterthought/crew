# crew main up|down|status <label>: the "<label>" workspace with design, planner and ops tabs in the main level's
# session, and a dispatcher in "<label> dispatch" on each host with a team of the partition: in the main level's
# session on its own host, else in the session of the host's first team by name.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"

expect_ok crew main up wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a started"; done
eq "$(herdr_state $box wldn-3 '[.workspaces[].label] | join(",")')" "wldn,wldn dispatch"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | sort | join(",")')" "wldn-design,wldn-dispatch-chuck-herdr-alpha,wldn-ops,wldn-planner"
eq "$(herdr_state mac-studio wldn-5 '[.workspaces[].label] | join(",")')" "wldn dispatch"
eq "$(herdr_state mac-studio wldn-5 '[.agents[].name] | join(",")')" "wldn-dispatch-mac-studio"
[[ ! -e $(home_of $box)/.stub-herdr/wldn-1.json ]] || fail "the main level touched a team's session"
eq "$(jq -r 'select(.agent == "wldn-design") | "\(.host) \(.argv[1]) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "$box claude-fable-5-1 xhigh"
eq "$(jq -r 'select(.agent == "wldn-dispatch-mac-studio") | "\(.host) \(.argv[3]) \(.cwd)"' "$CREW_TEST_CLAUDE_LOG")" "mac-studio medium $(space mac-studio willdan)/willdan-blueprints/main"
ok "the main level comes up in wldn-3 on the box, with a dispatcher on the box and one on mac-studio"

expect_ok crew main up wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a is already up"; done
eq "$(herdr_state $box wldn-3 '.workspaces | length')" "2"
ok "a second main up starts nothing"

expect_ok crew main status wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$(grep "^$a " <<<"$out")" "idle"; done
expect_ok crew main down wldn
eq "$(herdr_state $box wldn-3 '.agents | length')" "0"; eq "$(herdr_state mac-studio wldn-5 '.agents | length')" "0"
expect_ok crew main status wldn; eq "$(grep -c 'not up' <<<"$out")" "5"
ok "main status and down reach every host"

# madswan: its main level and its one team are on mac-studio, so the dispatcher shares the main level's session.
mkdir -p "$(space mac-studio madswan)/blueprints/main"
: > "$CREW_TEST_LOG"
expect_ok crew main up madswan
eq "$(herdr_state mac-studio madswan-1 '[.workspaces[].label] | join(",")')" "madswan,madswan dispatch"
eq "$(herdr_state mac-studio madswan-1 '[.agents[].name] | sort | join(",")')" "madswan-design,madswan-dispatch-mac-studio,madswan-ops,madswan-planner"
grep -q " ssh " "$CREW_TEST_LOG" && fail "madswan's main level needed no other host"
expect_fail "no partition 'nope'" crew main up nope
ok "a dispatcher on the main level's host runs in its session"
