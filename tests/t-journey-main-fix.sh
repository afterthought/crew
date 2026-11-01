# A fix of a red main through the crew command on the stubs (Decision 11 of teams-cross-to-flume-as-their-bolts-land;
# the main-level spec's "A red main's fix is a fix place on main on the kit's host", state.3): with swb-1 building
# switchboard-kit in Flume's stream wldn, wldn's plan naming the kit, and a runner answering on its host, crew main fix
# appends to requests.rec on the state branch a launch of Flume's fix kind on main, its submission held and main-level
# ops its recipient, on swb-1's host and in its stream, and starts no agent. Which team's host, the refusals where no team builds the kit in a
# stream or no runner answers, the drop and the role table are logic cases (tests/py/test_main_fix.py).
# Reads: plugin/roles/ tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

# The teams file at version 3: swb-1's work runs in Flume's stream wldn on its host, and no other team names a stream.
edit teams "d['version'] = 3
for t in d['teams']: t['flume'] = False
$(team swb-1)['flume'] = 'wldn'"

# runner_writes <file>...: wldn/runner/$box on the state repository as the runner on swb-1's host writes it, and crew
# never does, holding each file named from its text in <file>_rec.
runner_writes() {
  local tree parent
  tree=$(for f in "$@"; do
    v=${f}_rec; printf '100644 blob %s\t%s.rec\n' "$(printf '%s\n' "${!v}" | git --git-dir "$ws" hash-object -w --stdin)" "$f"
  done | git --git-dir "$ws" mktree)
  parent=$(git --git-dir "$ws" rev-parse -q --verify "refs/heads/wldn/runner/$box") || parent=
  git --git-dir "$ws" update-ref "refs/heads/wldn/runner/$box" "$(git --git-dir "$ws" -c user.name=runner -c user.email=runner@example.com \
    commit-tree "$tree" ${parent:+-p "$parent"} -m "runner: $*")"
}
runner_rec=$(printf '%%rec: Runner\n%%key: Host\n%%type: Since date\n%%mandatory: Host Version Since\n%%allowed: Host Version Since\n\nHost: %s\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n' "$box")
runner_writes runner

# wldn's plan names switchboard-kit by a bolt planned on it, so the kit is one of wldn's (plan.partition_kits).
expect_ok crew bolt new smoke-follow-up "Smoke's follow-up." --repo switchboard-kit

: > "$CREW_TEST_CLAUDE_LOG"
words="tests:logic failed on main after landing smoke: tests/py/test_rail.py reads a fixture that is gone."
expect_ok crew main fix switchboard-kit a-test-reads-its-fixture "$words"
has "$out" "the runner on $box launches fix main--a-test-reads-its-fixture on switchboard-kit's main (request 1) in stream wldn, its submission held"
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -P Act,Host,Work,Kind,Name,Base,Stream,Intent,Recipient,Hold,Brief | grep . | paste -sd ' ' -)" \
  "launch $box fix/main/switchboard-kit/a-test-reads-its-fixture fix main--a-test-reads-its-fixture main wldn wldn/main/switchboard-kit wldn/ops submission $words"
eq "$(field "$HOST" fix.start On)" "fix/main/switchboard-kit/a-test-reads-its-fixture"
eq "$(launches)" ""
ok "crew main fix of a kit a team builds in a stream appends a launch of a fix on main, held for the user's send with ops its recipient, on the team's host and in its stream, starting no agent"

# The runner launched the fix, and Flume's status of its place, carried on the runner's branch, shows its code
# delivered and its submission held: the branch gains answers.rec and places.rec beside runner.rec.
place=/flume/places/fix--main--a-test-reads-its-fixture
answers_rec=$(printf '%%rec: Answer\n%%key: Request\n%%type: Request int\n%%type: Outcome enum held launched done refused\n%%type: At date\n%%mandatory: Request Outcome At\n%%allowed: Request Outcome Place Words At\n\nRequest: 1\nOutcome: launched\nPlace: %s\nAt: 2026-10-31T12:01:00Z\n' "$place")
status='{"status":{"places":[{"place":"'"$place"'","kind":"fix","phase":"live","current":"code","stages":[{"name":"code","state":"delivered"}],"submission":{"read":"none","submits":0,"send_backs":0,"verdict":null,"waiting":null,"held":true},"waiting_on":{"act":"retry","stage":null,"why":"on_hold","since":1793469348,"words":null},"stalled":true,"holds":[{"on":"submission","since":1793469048}]}]}}'
places_rec=$(printf '%%rec: Place\n%%key: Request\n%%type: Request int\n%%type: At date\n%%mandatory: Request Place At Status\n%%allowed: Request Place At Status\n\nRequest: 1\nPlace: %s\nAt: 2026-10-31T12:20:00Z\nStatus: %s\n' "$place" "$status")
runner_writes runner answers places
expect_ok crew rail --label wldn
has "$out" "switchboard-kit (wldn): 1 fix of main waits to land on its main; wldn-ops lands them"
has "$out" "fix main--a-test-reads-its-fixture on $box: tests:logic failed on main after landing smoke: tests/py/test_rail.py reads a fixture that is gone.; can land: wldn-ops sends it with crew main fix switchboard-kit a-test-reads-its-fixture --send"
has "$out" "crew tell wldn-ops \"Land fix main--a-test-reads-its-fixture.\""
ok "once the runner's record shows the fix's code delivered and its submission held, the kit's landings row carries it, naming ops's command for the user's send"

expect_ok crew main fix switchboard-kit a-test-reads-its-fixture --send
has "$out" "fix main--a-test-reads-its-fixture of switchboard-kit's main is sent on the user's word (request 2): the runner on $box submits it"
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -e "Request = 2" -P Act,Host,Work,Of,Submission | grep . | paste -sd ' ' -)" \
  "retry $box fix/main/switchboard-kit/a-test-reads-its-fixture 1 yes"
eq "$(field "$HOST" fix.merge On)" "fix/main/switchboard-kit/a-test-reads-its-fixture"
expect_ok crew rail --label wldn
has "$out" "fix main--a-test-reads-its-fixture on $box: tests:logic failed on main after landing smoke: tests/py/test_rail.py reads a fixture that is gone.; sent on the user's word (request 2): the runner on $box submits it"
ok "crew main fix --send on the user's word appends the retry of the fix's submission, once, and its row says it is sent"
