# crew operator up <label>, run on the host itself: the "operator" workspace in the session named <label>, the agent
# <label>-operator-<host> started in the session's folder, nothing done when it is already up, and a non-zero exit
# naming a missing session or partition.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world

expect_ok crew operator up madswan
has "$out" "madswan-operator-mac-studio started"
eq "$(herdr_state mac-studio madswan '[.workspaces[].label] | join(",")')" "operator"
eq "$(herdr_state mac-studio madswan '[.agents[].name] | join(",")')" "madswan-operator-mac-studio"
eq "$(jq -r '"\(.host) \(.cwd) \(.argv[1]) \(.argv[3]) \(.label)"' "$CREW_TEST_CLAUDE_LOG")" "mac-studio $(space mac-studio madswan) claude-opus-5-5[1m] medium madswan"
grep -q " ssh " "$CREW_TEST_LOG" && fail "operator up left its host"
ok "the operator agent starts in the operator workspace of the session named for its partition"

: > "$CREW_TEST_LOG"
expect_ok crew operator up madswan
has "$out" "madswan-operator-mac-studio is already up"
eq "$(herdr_state mac-studio madswan '.workspaces | length')" "1"
eq "$(wc -l < "$CREW_TEST_CLAUDE_LOG" | tr -d ' ')" "1"
grep -q "workspace create\|pane run" "$CREW_TEST_LOG" && fail "a second operator up made or started something"
ok "run twice, it starts nothing and succeeds"

HOST=chuck-herdr-alpha expect_ok crew operator up wldn; has "$out" "wldn-operator-chuck-herdr-alpha started"
HOST=chuck-herdr-alpha expect_fail "chuck-herdr-alpha has no session named madswan" crew operator up madswan
expect_fail "no partition 'nope'" crew operator up nope
edit hosts "d['hosts']['mac-studio']['sessions']['swancloud']['partition'] = 'business'"
expect_fail "mac-studio's session swancloud is in partition business, not personal" crew operator up swancloud
ok "a missing session or partition is a non-zero exit naming it"
