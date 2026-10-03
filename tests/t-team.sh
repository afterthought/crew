# crew up|down|rebuild|close|restart|resume act on a team's conductor and ops only, in one workspace "<team>"
# with a conductor tab and a git tab, on the team's host. fable, the explorer, the verifier, assign, release
# and opsx are gone.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha

expect_ok crew up swb-1
has "$out" "swb-1-conductor started"; has "$out" "swb-1-ops started"
eq "$(grep -c "^$box wldn-1 workspace create" "$CREW_TEST_LOG")" "1"
grep -q "^mac-studio ssh $box " "$CREW_TEST_LOG" || fail "crew up did not run on the team's host"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
eq "$(herdr_state $box wldn-1 '[.tabs[].label] | join(",")')" "conductor,git"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
eq "$(wc -l < "$CREW_TEST_CLAUDE_LOG" | tr -d ' ')" "2"
eq "$(jq -r .agent "$CREW_TEST_CLAUDE_LOG" | sort | tr '\n' ' ')" "swb-1-conductor swb-1-ops "
eq "$(jq -r .host "$CREW_TEST_CLAUDE_LOG" | sort -u)" "$box"
grep -q "agent prompt swb-1-conductor 'Read where your bolt stands with" "$CREW_TEST_LOG" || fail "the conductor was not greeted"
has "$out" "swb-1-conductor greeted"
[[ -d $(home_of $box)/.local/state/swb-1-team && ! -d $(home_of mac-studio)/.local/state/swb-1-team ]] || fail "the team's state is not on its host"
ok "crew up makes one workspace with a conductor and a git tab, and starts two agents, on the team's host"

expect_fail "swb-1-conductor is already up" crew up swb-1
expect_ok crew status swb-1
has "$out" "swb-1-conductor"; has "$out" "swb-1-ops"; lacks "$out" "fable"; lacks "$out" "verifier"
for n in 1 2 3 4; do has "$out" "swb-1-unit-$n"; done; lacks "$out" "swb-1-unit-5"
eq "$(grep -c ' free ' <<<"$out")" "4"
ok "status lists the conductor, ops and four free slots"

expect_ok crew down swb-1; eq "$(herdr_state $box wldn-1 '.agents | length')" "0"; eq "$(herdr_state $box wldn-1 '.panes | length')" "4"
expect_ok crew resume swb-1; has "$out" "swb-1-conductor resumed"; has "$out" "swb-1-ops resumed"
has "$(tail -1 "$CREW_TEST_CLAUDE_LOG")" '"--resume", "swb-1-'
expect_ok crew restart swb-1 ops; has "$out" "swb-1-ops started"; lacks "$out" "conductor"
expect_fail "no role 'fable' here; roles: conductor ops" crew restart swb-1 fable
expect_ok crew rebuild swb-1
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
expect_ok crew close swb-1; eq "$(herdr_state $box wldn-1 '.workspaces | length')" "0"
ok "down, resume, restart, rebuild and close act on the conductor and ops"

for gone in "assign swb-1 coder-1 x" "release swb-1 coder-1" "opsx swb-1 explorer /opsx:propose x"; do
  if out=$(crew $gone 2>&1); then fail "crew $gone still works"; fi
  has "$out" "A team builds one bolt at a time"
done
lacks "$(crew 2>&1 || true)" "fable"
ok "assign, release and opsx are gone"
