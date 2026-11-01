# A team's work through Flume, through the crew command on the stubs (record 0050 parts 2 and 3; the change
# teams-cross-to-flume-as-their-bolts-land; Decision 1 of the-team-machinery-leaves): every team runs no conductor, ops
# or slot, so crew up of one is refused at once, naming Flume and crew bolts, with no pane opened. A give to a team
# whose teams file entry names no stream is refused, and to one that names a stream while no runner answers on its
# host, the plan unchanged and no branch made; once a runner answers, sluice makes the bolt's branch, the plan marks the
# bolt Path: flume and requests.rec on the state branch holds a launch of each of its units and chores, and no agent
# starts. Once the runner's record shows a's place stopped short asking, crew answer a appends the retry of that stage
# with the answer's words, and crew fix of the bolt appends a launch of a fix on it. swb-1, holding that bolt, is
# given two more, neither refused for the bolts it holds. The launches, what an answer retries, a fix's launch and drop
# and the refusals' words are logic cases (tests/py/test_cross.py, tests/py/test_fix.py).
# Reads: plugin/hooks/ plugin/roles/ tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

# The teams file at version 3: swb-1's work runs in Flume's stream wldn on its host, and swb-2 names no stream.
edit teams "d['version'] = 3
for t in d['teams']: t['flume'] = False
$(team swb-1)['flume'] = 'wldn'"
crew bolt new next "What comes next." --repo switchboard-kit >/dev/null

: > "$CREW_TEST_LOG"
expect_fail "swb-1's work runs in Flume places on $box, which crew bolts shows; it runs no conductor, ops or slot, so crew up swb-1 has nothing of it to act on" \
  crew up swb-1
grep -q "ssh $box " "$CREW_TEST_LOG" && fail "crew up of a team went to its host"
[[ -e $(home_of $box)/.stub-herdr/wldn-1.json ]] && fail "crew up of a team opened a pane"
ok "crew up of a team is refused at once, naming Flume and crew bolts, and opens no pane"

plan_at=$(act_tip)
expect_fail "swb-2 names no Flume stream in" crew bolt give swb-2 next
eq "$(act_tip)" "$plan_at"
ok "a give to a team whose teams file entry names no stream is refused, the plan unchanged"

crew unit add a "Build a." --bolt next >/dev/null
crew unit add b "Build b on a." --bolt next --after a >/dev/null
crew chore add c "Bump c." --bolt next >/dev/null
plan_at=$(act_tip)
expect_fail "no runner answers on $box: wldn/runner/$box does not exist, so nothing would launch the bolt's work there" \
  crew bolt give swb-1 next
eq "$(act_tip)" "$plan_at"
git --git-dir "$r" rev-parse --verify -q bolt/next >/dev/null && fail "a give with no runner on the host made bolt/next on GitHub"
ok "a give is refused while no runner answers on its team's host, the plan unchanged and no branch made"

# The runner on swb-1's host serves wldn: its own branch on the state repository, which crew reads and never writes.
runner_rec=$(printf '%%rec: Runner\n%%key: Host\n%%type: Since date\n%%mandatory: Host Version Since\n%%allowed: Host Version Since\n\nHost: %s\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n' "$box")
blob=$(printf '%s\n' "$runner_rec" | git --git-dir "$ws" hash-object -w --stdin)
tree=$(printf '100644 blob %s\trunner.rec\n' "$blob" | git --git-dir "$ws" mktree)
git --git-dir "$ws" update-ref "refs/heads/wldn/runner/$box" \
  "$(git --git-dir "$ws" -c user.name=runner -c user.email=runner@example.com commit-tree "$tree" -m "runner: serve wldn on $box")"
: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 next
has "$out" "no agent of swb-1 starts: the runner on $box launches unit/a (request 1), unit/b (request 2), chore/c (request 3) in stream wldn"
git --git-dir "$r" rev-parse --verify -q bolt/next >/dev/null || fail "the give made no bolt/next on GitHub"
eq "$(git --git-dir "$ws" show wldn/main:plan.rec | recsel -t Bolt -e "Bolt = 'next'" -P Team,Path | tr '\n' ' ')" "swb-1 flume "
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -P Act,Work,Kind,Base,Stream,After | grep . | paste -sd ' ' -)" \
  "launch unit/a change bolt/next wldn launch unit/b change bolt/next wldn 1 launch chore/c chore bolt/next wldn"
eq "$(launches)" ""
eq "$(field "$HOST" bolt.give On bolt/next)" "bolt/next team/swb-1"
ok "a give makes its bolt's branch, marks it Path: flume and launches each unit and chore, b after a, starting no agent"

# The runner launched a, and Flume's status of its place, carried on the runner's branch, shows its code stopped short
# asking: the branch gains answers.rec and places.rec beside runner.rec.
answers_rec=$(printf '%%rec: Answer\n%%key: Request\n%%type: Request int\n%%type: Outcome enum held launched done refused\n%%type: At date\n%%mandatory: Request Outcome At\n%%allowed: Request Outcome Place Words At\n\nRequest: 1\nOutcome: launched\nPlace: /flume/places/change--a\nAt: 2026-10-31T12:01:00Z\n')
status='{"status":{"places":[{"place":"/flume/places/change--a","phase":"live","current":"code","stages":[{"name":"code","state":"ended_short","end":{"needs":"needs_answer","words":"Which partition'"'"'s rail?"}}],"waiting_on":{"act":"retry","stage":"code","why":"answer","words":"Which partition'"'"'s rail?"},"stalled":false}]}}'
places_rec=$(printf '%%rec: Place\n%%key: Request\n%%type: Request int\n%%type: At date\n%%mandatory: Request Place At Status\n%%allowed: Request Place At Status\n\nRequest: 1\nPlace: /flume/places/change--a\nAt: 2026-10-31T12:02:00Z\nStatus: %s\n' "$status")
tree=$(for f in runner answers places; do
  v=${f}_rec; printf '100644 blob %s\t%s.rec\n' "$(printf '%s\n' "${!v}" | git --git-dir "$ws" hash-object -w --stdin)" "$f"
done | git --git-dir "$ws" mktree)
git --git-dir "$ws" update-ref "refs/heads/wldn/runner/$box" "$(git --git-dir "$ws" -c user.name=runner -c user.email=runner@example.com \
  commit-tree "$tree" -p "refs/heads/wldn/runner/$box" -m "runner: a's place stopped short")"
expect_ok crew answer a "wldn's"
has "$out" "unit/a's place /flume/places/change--a is asked to run code again with the answer (request 4): the runner on $box retries it"
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -e "Request = 4" -P Act,Work,Of,Stage,Words | grep . | paste -sd ' ' -)" \
  "retry unit/a 1 code wldn's"
eq "$(field "$HOST" stage.answer On)" "unit/a bolt/next"
ok "crew answer of a place the runner shows stopped short asking appends the retry of its stage with the answer's words"

: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew fix next tidy "Tidy the rail's words."
has "$out" "the runner on $box launches fix next--tidy on bolt/next (request 5) in stream wldn"
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -e "Request = 5" -P Act,Work,Kind,Name,Base,Brief | grep . | paste -sd ' ' -)" \
  "launch fix/next/tidy fix next--tidy bolt/next Tidy the rail's words."
eq "$(field "$HOST" fix.start On)" "fix/next/tidy bolt/next"
eq "$(launches)" ""
ok "crew fix of a started bolt appends a launch of a fix on it, starting no agent"

# swb-1 holds next, none of whose work has merged, and is given two bolts more: a give waits on no bolt the team holds,
# neither for its proof nor for holding two.
crew bolt new more "More of it." --repo switchboard-kit >/dev/null
crew bolt new last "The last of it." --repo switchboard-kit >/dev/null
: > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 more
has "$out" "the runner on $box launches nothing, the bolt holding no unit or chore yet"
expect_ok crew bolt give swb-1 last
eq "$(git --git-dir "$ws" show wldn/main:plan.rec | recsel -t Bolt -e "Team = 'swb-1'" -P Bolt,Path | grep . | paste -sd ' ' -)" \
  "next flume more flume last flume"
eq "$(launches)" ""
ok "a team holding a bolt whose work has not merged, and then two, is given another all the same, starting no agent"
