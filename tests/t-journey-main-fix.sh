# A fix of a red main through the crew command on the stubs (Decision 11 of teams-cross-to-flume-as-their-bolts-land;
# the main-level spec's "A red main's fix is a fix place on main where a crossed team builds the kit", state.3): with
# swb-1 crossed to Flume, building switchboard-kit, and a runner answering on its host, crew main fix appends to
# requests.rec on the state branch a launch of Flume's fix kind on main, its submission held and main-level ops its
# recipient, on swb-1's host and in its stream, and starts no agent. Which team's host, the refusals where no crossed
# team builds the kit or no runner answers, the drop and the role table are logic cases (tests/py/test_main_fix.py).
# Reads: plugin/roles/ tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

# The user turns swb-1's setting on while it holds nothing: the teams file at version 3, every team on today's path but
# swb-1, whose work runs in Flume's stream wldn on its host, so it has crossed.
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

: > "$CREW_TEST_CLAUDE_LOG"
words="tests:logic failed on main after landing smoke: tests/py/test_rail.py reads a fixture that is gone."
expect_ok crew main fix switchboard-kit a-test-reads-its-fixture "$words"
has "$out" "the runner on $box launches fix main--a-test-reads-its-fixture on switchboard-kit's main (request 1) in stream wldn, its submission held"
eq "$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -P Act,Host,Work,Kind,Name,Base,Stream,Intent,Recipient,Hold,Brief | grep . | paste -sd ' ' -)" \
  "launch $box fix/main/switchboard-kit/a-test-reads-its-fixture fix main--a-test-reads-its-fixture main wldn wldn/main/switchboard-kit wldn/ops submission $words"
eq "$(field "$HOST" fix.start On)" "fix/main/switchboard-kit/a-test-reads-its-fixture"
eq "$(launches)" ""
ok "crew main fix of a kit a crossed team builds appends a launch of a fix on main, held for the user's send with ops its recipient, on the team's host and in its stream, starting no agent"
