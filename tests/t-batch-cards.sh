# A batch card's sessions: crew card session batch/<n>-<k> <unit> starts one plannotator session for each unit the
# card holds, on that unit's whole change, on the host the teams file names for the unit's team, with no browser; it
# refuses a unit the card does not hold, the key without a unit, and a card that has closed. crew card wait and end take
# the unit the same way, end with no unit ends each unit's session, and a batch card's close through crew's hook ends
# them too. Each scenario of the card-sessions spec on batch cards.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
crew bolt new b1 "One." --repo switchboard-kit >/dev/null
crew bolt new m1 "Maps." --repo atlas-kit >/dev/null
for u in x1 x2; do crew unit add $u "Unit $u." --bolt b1 >/dev/null; done
crew unit add z1 "Unit z1." --bolt m1 >/dev/null
crew bolt give swb-1 b1 >/dev/null 2>&1; crew bolt give atl-1 m1 >/dev/null 2>&1
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
crew main up wldn >/dev/null 2>&1
real() { (cd "$1" && pwd -P); }
build() {  # build <team> <unit> <kit dir>
  CREW_AGENT=$1-conductor crew unit run $2 construct >/dev/null; change "$3/places/$2" $2 0 2; commit_all "$3/places/$2" "docs($2): the change"
  CREW_AGENT=$1-conductor crew unit wait $2 >/dev/null
}
build swb-1 x1 "$kd"; build swb-1 x2 "$kd"; build atl-1 z1 "$akd"
CREW_AGENT=wldn-planner crew review wldn >/dev/null
summary=$(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md; mkdir -p "$(dirname "$summary")"; echo "# Batch 1" > "$summary"
CREW_AGENT=wldn-planner crew review wldn --wait >/dev/null
rec() { jq -r "$3" "$(home_of "$1")/.local/state/crew/cards/wldn/batch/1-1/$2/session.json"; }
stub() { jq -r "$3" "$(home_of "$1")/.stub-plannotator/$2.json"; }
listed() { as "$1" plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
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
export CREW_AGENT=wldn-planner

: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew card session batch/1-1 x1; ux=$out
[[ $ux =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the box's tailnet name: $ux"
px=$(rec $box x1 .pid)
eq "$(stub $box "$px" .target)" "$(real "$kd/places/x1")/openspec/changes/x1"
eq "$(stub $box "$px" .skip_browser)" "true"
HOST=$box expect_ok crew card session batch/1-1 z1; uz=$out
[[ $uz =~ ^http://mac-studio\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on mac-studio's tailnet name: $uz"
pz=$(rec mac-studio z1 .pid)
eq "$(stub mac-studio "$pz" .target)" "$(real "$akd/places/z1")/openspec/changes/z1"
grep -q "^$box ssh mac-studio .*card session batch/1-1 z1 --label wldn" "$CREW_TEST_LOG" || fail "z1's session was not started on its team's host:"$'\n'"$(calls)"
lacks "$(calls)" "opened a browser"
HOST=$box expect_ok crew card session batch/1-1 x1; eq "$out" "$ux"; eq "$(listed $box)" "$px"
ok "a batch card has a session for each unit on that unit's whole change, on its team's host, with no browser, and the same unit again gives the same link"

HOST=$box expect_fail "batch/1-1 holds x1, x2 or z1, not w1: its sessions are its units'" crew card session batch/1-1 w1
HOST=$box expect_fail "a batch card has a session for each of its units: crew card session batch/1-1 <unit>" crew card session batch/1-1
HOST=$box expect_fail "only a batch card's key takes a unit" crew card session proposal/1 x1
eq "$(listed $box)" "$px"; eq "$(listed mac-studio)" "$pz"
ok "a unit the card does not hold, the key without a unit, and a unit with another key are refused, with nothing started"

notes=$'# Annotations\n\n1. Say what z means.'
printf '%s\n' "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f}')" > "$(home_of mac-studio)/.stub-plannotator/$pz.decision"
gone "$pz"
HOST=$box expect_ok crew card wait batch/1-1 z1
eq "$out" "batch/1-1 z1: annotated
$notes"
ok "a wait on a unit's session, run from another host, returns that unit's notes in the user's words"

HOST=$box expect_ok crew card session batch/1-1 x2; p2=$(rec $box x2 .pid)
HOST=$box expect_ok crew card end batch/1-1 x2
eq "$out" "ended batch/1-1 x2's session, plannotator pid $p2"
gone "$p2"
HOST=$box expect_ok crew card end batch/1-1
has "$out" "ended batch/1-1 x1's session, plannotator pid $px"
has "$out" "no session was running for batch/1-1 x2"
gone "$px"; eq "$(listed $box)" ""
ok "crew card end ends one unit's session, or with no unit each unit's, on each unit's host"

# The card's close, through crew's hook, ends its sessions.
HOST=$box expect_ok crew card session batch/1-1 x1; p3=$(rec $box x1 .pid)
call() { jq -nc --arg t "mcp__pendingyou__$1" --argjson i "$2" --argjson r "$3" \
  '{session_id: "sid-1", hook_event_name: "PostToolUse", cwd: "/work", tool_name: $t, tool_input: $i, tool_response: $r}'; }
call post_request '{"name": "wldn-planner", "idempotencyKey": "batch/1-1"}' '{"structuredContent": {"requestId": "req_bat-1"}}' | as $box python3 "$CREW/plugin/hooks/cards"
call ack_answer '{"name": "wldn-planner", "requestId": "req_bat-1", "outcome": "noted"}' '{"structuredContent": {"status": "resolved"}}' | as $box python3 "$CREW/plugin/hooks/cards"
gone "$p3"
eq "$(listed $box)" ""
HOST=$box expect_fail "no row of wldn's rail has the card key batch/1-1: its row is gone" crew card session batch/1-1 x1
ok "a batch card's close through crew's hook ends its sessions, and the closed card starts none"
