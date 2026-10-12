# crew card: the plannotator session a card's owner starts on what its card asks the user to read. A proposal's and a
# verify report's key each start one on the host it runs on, on the row's document, with an Approve
# button and no browser, and print its link; the same key again gives the same link and starts nothing; a landing's
# key, a key whose row is gone, a document on another host and a link only the host can open are refused with nothing
# left running. crew card wait gives each decision with the user's words as they are, a decision made before it began
# at once, and a session that ended or was ended; crew card end ends only a session plannotator lists on the document
# crew recorded, and forgets the key whether or not it ended one, but when plannotator's list can't be read it ends
# nothing, says so and keeps the key's session for a later end. Each scenario of the card-sessions spec.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
crew state init wldn >/dev/null
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
box=chuck-herdr-alpha
now=$(date +%s)
at() { echo "@$((now - $1 * 60)) +0000"; }
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "$2"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE=$(at "$1") git -C "$2" commit -qm "$3"; }
real() { (cd "$1" && pwd -P); }
# rec <host> <key> <jq>: what crew recorded of the key's session; stub <host> <pid> <jq>: what the stub registered
rec() { jq -r "$3" "$(home_of "$1")/.local/state/crew/cards/wldn/$2/session.json"; }
stub() { jq -r "$3" "$(home_of "$1")/.stub-plannotator/$2.json"; }
# listed <host>: the pids plannotator lists there, in order
listed() { as "$1" plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
# settle file|gone <path|pid>: wait up to five seconds for a file to be there, or a process to be gone
settle() {
  python3 - "$1" "$2" <<'EOF'
import os, sys, time
kind, what = sys.argv[1:]
def done():
    if kind == "file":
        return os.path.exists(what)
    try:
        os.kill(int(what), 0)
    except ProcessLookupError:
        return True
    return False
give_up = time.monotonic() + 5
while not done():
    if time.monotonic() > give_up:
        sys.exit(f"still waiting: {kind} {what}")
    time.sleep(0.05)
EOF
}
# decide <host> <key> <json>: the user's decision in the key's session, as plannotator writes it once they decide
decide() {
  local pid; pid=$(rec "$1" "$2" .pid)
  printf '%s\n' "$3" > "$(home_of "$1")/.stub-plannotator/$pid.decision"
  settle file "$(home_of "$1")/.local/state/crew/cards/wldn/$2/result.json"; settle gone "$pid"
}

crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in x checked; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
px=$(place "$k" tenant-environments x); change "$px" x 2 2; commit_at 60 "$px" "feat(x): done"
pc=$(place "$k" tenant-environments checked); change "$pc" checked 2 2; commit_at 120 "$pc" "feat(checked): done"
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
report() { local f="$reports/verify-$1-$(shown "$2" %Y%m%d-%H%M).md"; echo "# Verify $1" > "$f"; touch -t "$(shown "$2" %Y%m%d%H%M.%S)" "$f"; echo "$f"; }
rc=$(report checked 100); vk=verify/checked/$(shown 100 %Y%m%d-%H%M)
rx=$(report x 50); vx=verify/x/$(shown 50 %Y%m%d-%H%M)

: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew card session "$vx"; url=$out
[[ $url =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the box's tailnet name: $url"
rx=$(real "$reports")/$(basename "$rx"); pid=$(rec $box "$vx" .pid)
eq "$(listed $box)" "$pid"
eq "$(stub $box "$pid" .target)" "$rx"
eq "$(stub $box "$pid" '.argv | join(" ")')" \
  "annotate $rx --gate --json --result-file $(real "$(home_of $box)")/.local/state/crew/cards/wldn/$vx/result.json"
eq "$(stub $box "$pid" '[.skip_browser, .remote] | map(tostring) | join(" ")')" "true true"
eq "$(rec $box "$vx" '[.url, .document] | join(" ")')" "$url $rx"
lacks "$(calls)" "opened a browser"
ok "a verify card's session is on the unit's report, on the team's host, with an Approve button and no browser, and its link names the host on the tailnet"

HOST=$box expect_ok crew card session "$vx"
eq "$out" "$url"
eq "$(listed $box)" "$pid"
ok "run again while its session runs, the same key gives the same link and starts nothing"

printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-pages "The console lists them." --repo switchboard-kit' > "$T/proposal.rec"
crew plan propose "$T/proposal.rec" >/dev/null
expect_ok crew card session proposal/1; purl=$out
[[ $purl =~ ^http://mac-studio\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on mac-studio's tailnet name: $purl"
ppid=$(rec mac-studio proposal/1 .pid); page=$(stub mac-studio "$ppid" .target)
eq "$page" "$(real "$(home_of mac-studio)")/.local/state/crew/cards/wldn/proposal/1/proposal-1.md"
eq "$(cat "$page")" "$(crew plan proposed 1)"
eq "$(stub mac-studio "$ppid" .skip_browser)" "true"
ok "a proposal's session is on its page as crew plan proposed prints it, on the host the planner runs on"

HOST=$box expect_ok crew card session "$vk"; vurl=$out
vpid=$(rec $box "$vk" .pid)
eq "$(stub $box "$vpid" .target)" "$(real "$reports")/$(basename "$rc")"
[[ $vurl != "$url" ]] || fail "two sessions share the link $url"
eq "$(listed $box)" "$(printf '%s\n' "$pid" "$vpid" | sort -n | tr '\n' ' ' | sed 's/ $//')"
lacks "$(calls)" "opened a browser"
ok "another verify card's session is on its own report, beside the first, each on its own port"

before=$(listed $box)
expect_fail "a landing card has no document to read" crew card session land/tenant-environments/abc1234
expect_fail "is not a card key" crew card session land/tenant-environments
expect_fail "is not a card key" crew card session verify/x/HEAD
expect_fail "is on chuck-herdr-alpha, not mac-studio" crew card session "$vx"
CREW_LABEL= expect_fail "runs as the card's partition" crew card session proposal/1
eq "$(listed $box)" "$before"
eq "$(listed mac-studio)" "$ppid"
ok "a landing's key, a key that is not a card's, a document on another host and a partition not named are refused"

echo more >> "$px/more"; commit_at 30 "$px" "fix(x): a finding"
HOST=$box expect_fail "no row of wldn's rail has the card key $vx: its row is gone" crew card session "$vx"
rx2=$(report x 20); vx2=verify/x/$(shown 20 %Y%m%d-%H%M)
(unset PLANNOTATOR_URL_HOST; HOST=$box expect_fail "plannotator gave $vx2's session the link http://localhost:" crew card session "$vx2"
 has "$out" "so crew ended it")
eq "$(listed $box)" "$before"
[[ ! -e $(home_of $box)/.local/state/crew/cards/wldn/$vx2/session.json ]] || fail "a refused session was recorded"
ok "a key whose row is gone, after code ran again, and a link only the host could open are refused, with no session left running"

HOST=$box expect_fail "no session was started for card $vx2: crew card session $vx2 starts one" crew card wait "$vx2"
ok "a wait for a key with no session is refused"

HOST=$box crew card wait "$vx" > "$T/wait.out" 2>&1 & waiting=$!
decide $box "$vx" '{"decision": "approved", "feedback": "Ship it — the \"tenant\" part reads well."}'
wait "$waiting" || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(cat "$T/wait.out")" "$vx: approved
Ship it — the \"tenant\" part reads well."
ok "a wait running when the user approves returns approved, with the user's notes as they wrote them"

notes=$'# Annotations\n\n1. On "Design", line 3: `z` is wrong.\n   > z\n   Say what z is: $HOME stays literal.\n\n2. On tasks 1.2: split it.\n\nOverall: almost.'
HOST=$box expect_ok crew card session "$vk"; eq "$out" "$vurl"
decide $box "$vk" "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f}')"
HOST=$box expect_ok crew card wait "$vk"
eq "$out" "$vk: annotated
$notes"
ok "annotations sent as feedback are returned as annotated, every annotation and the user's words verbatim"

decide mac-studio proposal/1 '{"decision": "approved", "feedback": ""}'
expect_ok crew card wait proposal/1
eq "$out" "proposal/1: approved"
expect_ok crew card wait proposal/1
eq "$out" "proposal/1: approved"
eq "$(crew card session proposal/1 2>/dev/null)" "$purl"
expect_ok crew card session proposal/1
has "$out" "the user decided in proposal/1's session before it ended: crew card wait proposal/1 gives the decision"
eq "$(listed mac-studio)" ""
ok "a decision made while nobody waited is returned at once by the next wait, and a session run again keeps it for the wait"

HOST=$box expect_ok crew card session "$vx2"; r2=$out; p2=$(rec $box "$vx2" .pid)
decide $box "$vx2" '{"decision": "dismissed"}'
HOST=$box expect_ok crew card wait "$vx2"
eq "$out" "$vx2: closed in plannotator with no decision"
HOST=$box expect_ok crew card session "$vx2"; p3=$(rec $box "$vx2" .pid)
[[ $p3 != "$p2" ]] || fail "no new session was started after the user closed the last"
dir=$(home_of $box)/.local/state/crew/cards/wldn/$vx2
[[ ! -e $dir/result.json ]] || fail "the closed session's result was left for the new one"
eq "$(jq -r .decision "$dir"/result.*.json)" "dismissed"
kill "$p3"; settle gone "$p3"
HOST=$box expect_ok crew card wait "$vx2"
eq "$out" "$vx2: the session ended with no decision"
eq "$(ls "$dir" | grep -c '^result')" "1"
HOST=$box expect_ok crew card session "$vx2"; p4=$(rec $box "$vx2" .pid)
eq "$(listed $box)" "$p4"
ok "a session the user closed undecided is said so and started again with its result moved aside, and one killed ends with no decision and is started again"

looked() { grep -c . "$T/plannotator-sessions.log" 2>/dev/null || true; }
n=$(looked)
HOST=$box crew card wait "$vx2" > "$T/wait.out" 2>&1 & waiting=$!
python3 - "$T/plannotator-sessions.log" "$n" <<'EOF2'
import sys, time
give_up = time.monotonic() + 10
while sum(1 for _ in open(sys.argv[1])) <= int(sys.argv[2]):
    if time.monotonic() > give_up:
        sys.exit("the wait never looked at plannotator's sessions")
    time.sleep(0.05)
EOF2
HOST=$box expect_ok crew card end "$vx2"
eq "$out" "ended $vx2's session, plannotator pid $p4"
settle gone "$p4"
wait "$waiting" || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(cat "$T/wait.out")" "$vx2: crew ended its session, as its card closed or crew card end was run"
[[ ! -e $dir ]] || fail "the ended key's folder is still there"
eq "$(listed $box)" ""
HOST=$box expect_ok crew card end "$vx2"
eq "$out" "no session was running for $vx2"
ok "crew card end ends the key's session and forgets it, a wait on it hears so, and a key with no session ends nothing"

HOST=$box expect_ok crew card end "$vk"
HOST=$box expect_ok crew card session "$vk"; v2=$(rec $box "$vk" .pid)
HOST=$box expect_ok crew card session "$vx2"; p5=$(rec $box "$vx2" .pid)
f=$(home_of $box)/.local/state/crew/cards/wldn/$vx2/session.json
jq -c --argjson p "$v2" '.pid = $p' "$f" > "$f.new" && mv "$f.new" "$f"
HOST=$box expect_ok crew card end "$vx2"
eq "$out" "plannotator lists no session of pid $v2 on $(real "$reports")/$(basename "$rx2"): crew ended nothing, and $vx2 is forgotten"
eq "$(listed $box)" "$(printf '%s\n' "$p5" "$v2" | sort -n | tr '\n' ' ' | sed 's/ $//')"
[[ ! -e $(dirname "$f") ]] || fail "the key was not forgotten"
kill "$p5"; settle gone "$p5"
HOST=$box expect_ok crew card end "$vk"
eq "$(listed $box)" ""
ok "a recorded pid plannotator lists on another document is not killed, and the key is forgotten"

HOST=$box expect_ok crew card session "$vk"; v3=$(rec $box "$vk" .pid)
mkdir -p "$T/broken"; printf '#!/usr/bin/env bash\necho "plannotator: its registry is locked" >&2\nexit 1\n' > "$T/broken/plannotator"
chmod +x "$T/broken/plannotator"
HOST=$box PATH="$T/broken:$PATH" expect_ok crew card end "$vk"
eq "$out" "crew can't read plannotator's sessions (plannotator sessions: plannotator: its registry is locked): it ended nothing, and keeps $vk to end later"
kill -0 "$v3" 2>/dev/null || fail "a session was ended while plannotator's list could not be read"
eq "$(rec $box "$vk" .pid)" "$v3"
HOST=$box expect_ok crew card end "$vk"
eq "$out" "ended $vk's session, plannotator pid $v3"
settle gone "$v3"
eq "$(listed $box)" ""
ok "when plannotator's list can't be read, crew card end ends nothing, says so and keeps the key's session, which a later end ends"
