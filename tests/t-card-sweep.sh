# Every rail read ends the card sessions crew started whose card is closed or whose row is gone, on every host of the
# partition, through crew card sweep on each: a proposal approved with its card still open, a card closed while its
# row stays, a dropped unit's verify report, and a batch card closed on the main host, whose units' sessions are on
# their teams' hosts. It ends no session with a card still to come, none crew did not start, and none started under two
# minutes before, which a later read ends. The rail lists each session it ended with its host and why, names each host
# it could not check, and says nothing about sessions when it ended nothing. A team's host that does not answer is
# named, and nothing there is ended, nor any verify session of its units; while a host of the run record does not
# answer, no closed card's and no batch card's session is ended, and a row gone still ends its session. The rail tab's
# refresh sweeps as crew rail does; crew board ends nothing. Each scenario of the card-sessions spec on the rail.
# Reads: plugin/hooks/ plugin/lib/board.py plugin/lib/sites.py
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
now=$(date +%s)
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "$2"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE="@$((now - $1 * 60)) +0000" git -C "$2" commit -qm "$3"; }

# The plan: b1 on swb-1 (the box) holds x1 and x2, batched, and v1 to v3, whose verify reports wait; m1 on atl-1
# (mac-studio) holds z1, batched.
crew bolt new b1 "One." --repo switchboard-kit >/dev/null
crew bolt new m1 "Maps." --repo atlas-kit >/dev/null
for u in x1 x2 v1 v2 v3; do crew unit add $u "Unit $u." --bolt b1 >/dev/null; done
crew unit add z1 "Unit z1." --bolt m1 >/dev/null
crew bolt give swb-1 b1 >/dev/null 2>&1; crew bolt give atl-1 m1 >/dev/null 2>&1
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
crew main up wldn >/dev/null 2>&1
build() {  # build <team> <unit> <kit dir>
  CREW_AGENT=$1-conductor crew unit run $2 construct >/dev/null; change "$3/places/$2" $2 0 2; commit_all "$3/places/$2" "docs($2): the change"
  CREW_AGENT=$1-conductor crew unit wait $2 >/dev/null
}
build swb-1 x1 "$kd"; build swb-1 x2 "$kd"; build atl-1 z1 "$akd"
CREW_AGENT=wldn-planner crew review wldn >/dev/null
summary=$(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md; mkdir -p "$(dirname "$summary")"; echo "# Batch 1" > "$summary"
CREW_AGENT=wldn-planner crew review wldn --wait >/dev/null
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
for u in v1 v2 v3; do
  p=$(place "$k" b1 $u); change "$p" $u 2 2; commit_at 60 "$p" "feat($u): done"
  f=$reports/verify-$u-$(shown 50 %Y%m%d-%H%M).md; echo "# Verify $u" > "$f"; touch -t "$(shown 50 %Y%m%d%H%M.%S)" "$f"
done
s=$(shown 50 %Y%m%d-%H%M)
propose() { printf '%s\n' "Case: The console, take $1." "Do: bolt new console-$1 \"The console, take $1.\" --repo switchboard-kit" > "$T/p$1.rec"
  crew plan propose "$T/p$1.rec" >/dev/null; }
for n in 1 2 3 4; do propose $n; done

cards=.local/state/crew/cards/wldn
# rec <host> <folder> <jq>: what crew recorded of the session kept in that folder of the host's cards
rec() { jq -r "$3" "$(home_of "$1")/$cards/$2/session.json"; }
# aged <host> <folder>: the session there recorded as started ten minutes ago, as a session the rail may judge
aged() {
  local f; f=$(home_of "$1")/$cards/$2/session.json
  jq -c --arg t "$(python3 -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))')" \
    '.started = $t' "$f" > "$f.new" && mv "$f.new" "$f"
}
# emit <host> <agent> <act> <on> <card> <key>: a card's entry in the host's run record, as crew's hook writes it
emit() { CREW_AGENT=$2 as "$1" python3 "$CREW/plugin/lib/record.py" emit --label wldn --act "$3" --on "$4" --field Card="$5" --field Key="$6" >/dev/null; }
up() { kill -0 "$1" 2>/dev/null; }
gone() { python3 -c 'import os, sys, time
pid, give_up = int(sys.argv[1]), time.monotonic() + 10
while True:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        break
    if time.monotonic() > give_up:
        sys.exit(f"pid {pid} is still running")
    time.sleep(0.05)' "$1"; }
# by_hand <host> <doc>: a plannotator crew did not start, on that document; prints its pid once plannotator lists it
by_hand() {
  (export CREW_TEST_HOST=$1 HOME=$(home_of "$1") PLANNOTATOR_SKIP_BROWSER_OPEN=1
   cd "$HOME" && exec plannotator annotate "$2" --gate --json --result-file "$T/by-hand-$RANDOM.json" >/dev/null 2>&1 </dev/null) &
  local pid=$!
  python3 -c 'import os, sys, time
f, give_up = sys.argv[1], time.monotonic() + 5
while not os.path.exists(f):
    time.sleep(0.05)
    if time.monotonic() > give_up:
        sys.exit("plannotator never listed " + f)' "$(home_of "$1")/.stub-plannotator/$pid.json"
  echo "$pid"
}
# swept <rail>: the rail's lines about card sessions
swept() { sed -n '/^card sessions /,/^$/p' <<<"$1" | sed '/^$/d'; }

# The sessions: on the box, proposal 1's and v1's to v3's reports', and x1's of the batch card; z1's on mac-studio.
HOST=$box crew card session proposal/1 >/dev/null; pp1=$(rec $box proposal/1 .pid)
for u in v1 v2 v3; do HOST=$box crew card session verify/$u/$s >/dev/null; done
pv1=$(rec $box verify/v1/$s .pid); pv2=$(rec $box verify/v2/$s .pid); pv3=$(rec $box verify/v3/$s .pid)
HOST=$box crew card session batch/1 x1 >/dev/null; px1=$(rec $box batch/1/x1 .pid)
HOST=$box crew card session batch/1 z1 >/dev/null; pz1=$(rec mac-studio batch/1/z1 .pid)
for f in proposal/1 verify/v1/$s verify/v2/$s verify/v3/$s batch/1/x1; do aged $box $f; done; aged mac-studio batch/1/z1
mine=$(by_hand $box "$(rec $box proposal/1 .document)")
emit $box wldn-planner card.post proposal/1 req_p-1 proposal/1
emit $box swb-1-conductor card.post unit/v2 req_v-2 verify/v2/$s
emit $box wldn-planner card.post batch/1 req_b-1 batch/1

# The planner closes the batch card and the conductor v2's, and the user approves proposal 1, whose card stays open.
emit $box wldn-planner card.close batch/1 req_b-1 batch/1
emit $box swb-1-conductor card.close unit/v2 req_v-2 verify/v2/$s
crew plan approve 1 >/dev/null

echo mac-studio > "$T/down"
HOST=$box expect_ok crew rail --label wldn
eq "$(swept "$out")" "card sessions ended:
  proposal/1 (wldn) on $box: its row is gone; ended proposal/1's session, plannotator pid $pp1
card sessions not checked:
  mac-studio (wldn): did not answer (ssh: connect to host mac-studio port 22: Operation timed out)"
gone "$pp1"
for p in $pv1 $pv2 $pv3 $px1 $pz1 $mine; do up $p || fail "pid $p was ended while a host of the run record did not answer"; done
[[ -e $(home_of $box)/$cards/verify/v2/$s/session.json ]] || fail "v2's closed card's session was forgotten"
ok "while a host of the run record does not answer, a closed card's session and a batch card's are kept, a row gone still ends its session, and the host is named"
up "$mine" || fail "a plannotator crew did not start was ended"
ok "a session crew did not start, on the page of the proposal whose session was ended, is left running"
rm "$T/down"

crew unit drop v1 "Not needed after all." >/dev/null 2>&1
HOST=$box crew card session proposal/2 >/dev/null; pp2=$(rec $box proposal/2 .pid)
crew plan drop 2 "Replaced." >/dev/null
expect_ok crew rail --label wldn
eq "$(swept "$out")" "card sessions ended:
  batch/1 x1 (wldn) on $box: its row is gone; ended batch/1 x1's session, plannotator pid $px1
  verify/v1/$s (wldn) on $box: its row is gone; ended verify/v1/$s's session, plannotator pid $pv1
  verify/v2/$s (wldn) on $box: its card is closed; ended verify/v2/$s's session, plannotator pid $pv2
  batch/1 z1 (wldn) on mac-studio: its row is gone; ended batch/1 z1's session, plannotator pid $pz1"
for p in $px1 $pv1 $pv2 $pz1; do gone $p; done
[[ ! -e $(home_of $box)/$cards/verify/v1 && ! -e $(home_of $box)/$cards/batch && ! -e $(home_of mac-studio)/$cards/batch ]] ||
  fail "an ended session's key was not forgotten"
ok "run on mac-studio, the rail ends a dropped unit's verify session and a closed card's with its row still there, and a batch card closed on the main host ends its units' sessions on each team's host, listing each with its host and why"
up "$pv3" || fail "a session whose card is still to come was ended"
ok "a session whose row is open and whose card is still to come is left running"
up "$pp2" || fail "a session started under two minutes before the read was ended"
ok "a session started under two minutes before the read is left, though its row is gone"

aged $box proposal/2
expect_ok crew board --label wldn
expect_ok crew board --label wldn --json
up "$pp2" || fail "crew board ended a session"
ok "crew board ends nothing"
expect_ok crew rail --label wldn
eq "$(swept "$out")" "card sessions ended:
  proposal/2 (wldn) on $box: its row is gone; ended proposal/2's session, plannotator pid $pp2"
gone "$pp2"
ok "a later read ends the session it left for being young"
expect_ok crew rail --label wldn
eq "$(swept "$out")" ""
lacks "$out" "card sessions"
ok "when it ended nothing and checked every host, the rail says nothing about sessions"

# The box asleep: a session there whose row is gone, and on mac-studio one of a proposal dropped and one of v3's
# earlier report, whose unit's team is on the box.
HOST=$box crew card session proposal/3 >/dev/null; pp3=$(rec $box proposal/3 .pid)
crew card session proposal/4 >/dev/null; pp4=$(rec mac-studio proposal/4 .pid)
crew plan drop 3 "Replaced." >/dev/null; crew plan drop 4 "Replaced." >/dev/null
aged $box proposal/3; aged mac-studio proposal/4
old=verify/v3/20261001-1200; d=$(home_of mac-studio)/$cards/$old; mkdir -p "$d"; echo "# Verify v3, before" > "$T/v3-before.md"
pold=$(by_hand mac-studio "$T/v3-before.md")
jq -nc --argjson p "$pold" --arg d "$T/v3-before.md" \
  '{pid: $p, document: $d, url: "http://mac-studio.ts.swancloud.net:19450", started: "2026-10-01T12:00:00Z"}' > "$d/session.json"
echo $box > "$T/down"
expect_ok crew rail --label wldn
eq "$(swept "$out")" "card sessions ended:
  proposal/4 (wldn) on mac-studio: its row is gone; ended proposal/4's session, plannotator pid $pp4
card sessions not checked:
  $box (wldn): did not answer (ssh: connect to host $box port 22: Operation timed out)"
gone "$pp4"
for p in $pp3 $pv3 $pold; do up $p || fail "pid $p was ended while the box did not answer"; done
ok "a team's host that does not answer is named, nothing there and no verify session of its units elsewhere is ended, and what can be judged on other hosts is"
rm "$T/down"

expect_ok crew _views wldn
has "$(swept "$out")" "  proposal/3 (wldn) on $box: its row is gone; ended proposal/3's session, plannotator pid $pp3"
has "$(swept "$out")" "  $old (wldn) on mac-studio: its row is gone; ended $old's session, plannotator pid $pold"
gone "$pp3"; gone "$pold"
up "$pv3" || fail "v3's session was ended with its row still open"
ok "the rail tab's refresh sweeps as crew rail does, ending what the asleep host kept once it answers"
kill "$pv3" "$mine"
