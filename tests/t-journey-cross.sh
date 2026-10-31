# A team crossing to Flume through the crew command on the stubs (record 0050 parts 2 and 3; the change
# teams-cross-to-flume-as-their-bolts-land): a team whose setting is turned on while it builds a bolt of today's path
# is due to cross, and a give to it is refused, the plan unchanged and no branch made, its conductor and ops running
# on; the landing of that bolt crosses it: its conductor and ops are ended once idle, never restarted, its workspaces
# closed and team.cross recorded naming its stream; and crew up of it is then refused at once, naming Flume and crew
# bolts, with no pane opened. A give to the crossed team is refused while no runner answers on its host, and once one
# does, sluice makes the bolt's branch, the plan marks the bolt Path: flume and requests.rec on the state branch holds a
# launch of each of its units and chores, and no agent starts. A team's path, the give's refusal, who is due an end,
# the launches and the refusals' words are logic cases (tests/py/test_cross.py, tests/py/test_hold.py).
# Reads: plugin/hooks/ plugin/roles/ plugin/lib/hold.py tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

expect_ok crew up swb-1
crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt new next "What comes next." --repo switchboard-kit >/dev/null
expect_ok crew bolt give swb-1 smoke

# The user turns swb-1's setting on: the teams file at version 3, every team on today's path but swb-1, whose work
# runs in Flume's stream wldn on its host.
edit teams "d['version'] = 3
for t in d['teams']: t['flume'] = False
$(team swb-1)['flume'] = 'wldn'"
plan_at=$(act_tip)
expect_fail "swb-1 is due to cross to Flume, so it is given no bolt now: it holds smoke, given on today's path, and is given its next bolt once smoke has landed or been dropped" \
  crew bolt give swb-1 next
eq "$(act_tip)" "$plan_at"
git --git-dir "$r" rev-parse --verify -q bolt/next >/dev/null && fail "a give to a due team made bolt/next on GitHub"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
ok "a team whose setting is turned on while it builds a bolt of today's path is due to cross: a give to it is refused, the plan unchanged and no branch made, and its conductor and ops run on"

: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt land smoke
# The crossing's last words come after its entry and its tell to the dispatchers, so once they are said all is done.
renewed() { cat "$(home_of $box)"/.local/state/crew/renew/swb-1-*.log 2>/dev/null; }
crossed() { [[ $(renewed) == *"swb-1 has crossed to Flume: its workspaces are closed, and its work runs in Flume places on $box, in stream wldn"* ]]; }
until_ok crossed || fail "swb-1 did not cross: $(renewed)"
eq "$(field $box team.cross State) $(field $box team.cross On)" "wldn team/swb-1"
eq "$(field $box agent.end On agent/swb-1-conductor) / $(field $box agent.end On agent/swb-1-ops)" \
  "team/swb-1 agent/swb-1-conductor / team/swb-1 agent/swb-1-ops"
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" ""
eq "$(launches)" ""
ok "the landing of a due team's last bolt of today's path crosses it: its conductor and ops are ended once idle and never started again, its workspaces closed, and team.cross recorded naming its stream"

: > "$CREW_TEST_LOG"
expect_fail "swb-1 has crossed to Flume: its work runs in Flume places on $box, in stream wldn, and crew bolts shows them; it runs no conductor, ops or slot, so crew up swb-1 has nothing of it to act on" \
  crew up swb-1
grep -q "ssh $box " "$CREW_TEST_LOG" && fail "crew up of a crossed team went to its host"
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
ok "crew up of a crossed team is refused at once, naming Flume and crew bolts, and opens no pane"

crew unit add a "Build a." --bolt next >/dev/null
crew unit add b "Build b on a." --bolt next --after a >/dev/null
crew chore add c "Bump c." --bolt next >/dev/null
plan_at=$(act_tip)
expect_fail "no runner answers on $box: wldn/runner/$box does not exist, so nothing would launch the bolt's work there" \
  crew bolt give swb-1 next
eq "$(act_tip)" "$plan_at"
git --git-dir "$r" rev-parse --verify -q bolt/next >/dev/null && fail "a give with no runner on the host made bolt/next on GitHub"
ok "a give to a crossed team is refused while no runner answers on its host, the plan unchanged and no branch made"

# The runner on swb-1's host serves wldn: its own branch on the state repository, which crew reads and never writes.
runner_rec=$(printf '%%rec: Runner\n%%key: Host\n%%type: Since date\n%%mandatory: Host Version Since\n%%allowed: Host Version Since\n\nHost: %s\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n' "$box")
blob=$(printf '%s\n' "$runner_rec" | git --git-dir "$ws" hash-object -w --stdin)
tree=$(printf '100644 blob %s\trunner.rec\n' "$blob" | git --git-dir "$ws" mktree)
git --git-dir "$ws" update-ref "refs/heads/wldn/runner/$box" \
  "$(git --git-dir "$ws" -c user.name=runner -c user.email=runner@example.com commit-tree "$tree" -m "runner: serve wldn on $box")"
: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 next
has "$out" "swb-1 has crossed to Flume, so no agent of it starts: the runner on $box launches unit/a (request 1), unit/b (request 2), chore/c (request 3) in stream wldn"
git --git-dir "$r" rev-parse --verify -q bolt/next >/dev/null || fail "the give made no bolt/next on GitHub"
eq "$(git --git-dir "$ws" show wldn/main:plan.rec | recsel -t Bolt -e "Bolt = 'next'" -P Team,Path | tr '\n' ' ')" "swb-1 flume "
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -P Act,Work,Kind,Base,Stream,After | grep . | paste -sd ' ' -)" \
  "launch unit/a change bolt/next wldn launch unit/b change bolt/next wldn 1 launch chore/c chore bolt/next wldn"
eq "$(launches)" ""
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
eq "$(field "$HOST" bolt.give On bolt/next)" "bolt/next team/swb-1"
ok "a give to a crossed team makes its bolt's branch, marks it Path: flume and launches each unit and chore, b after a, starting no agent"
