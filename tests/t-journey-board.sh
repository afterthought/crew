# The flow as the user reads it, through the crew command on the stubs (tests.11, record 0022): crew bolts lists every
# bolt and unit with each unit's stage read from its kit, one ssh per host holding a bolt and none for planned work;
# crew sites gives each dev server's URL as it opens from where it is asked; crew board draws the four lanes, an
# environment's deploy among the Operation lane's, and the attention line from one read, writes nothing and ends no
# card session; the host's follower, crew _follow --once with no tab open, in one fetch and one read of each host's kits
# for both partitions on the host, writes the rail's frame, which the rail tab draws as crew rail prints it, sweeps a
# dead card session and writes the board's frame, which the board tab draws, and each agent's view with its open cards;
# running, a tick of its clock with nothing moved reads nothing but the box's stamps, a plan write on its host is
# shown at its next look, with nothing fetched or gathered, a reading sent back on its host has that host's card
# sessions swept at its next look, with nothing gathered, a write to sluice's folder in the box's kit moves nothing, a
# merge queued in sluice is on its unit's row at the next look from the kit's overview watch, with nothing gathered,
# and a dev server started on the box shows after the next tick, with nothing gathered; crew page writes the page
# whole, with the
# deploys, a dock for each item with its history as crew trace walks it, and its partition links in the layout of its
# file, saying so when that names no partition, and nothing when the branch can't be read; crew page --fleet writes
# every partition on one page beside the partitions' folders, its links in the layout of its file, and a partition's
# page served as <label>.html links back to it; every view names a host that does not answer, for its kits alone, and
# shows the rest; and a plan a hand edit broke is refused, named by its commit. What each lane, line, URL and node says
# are logic cases (tests/py/test_board.py, test_page.py, test_fleet.py, test_rail.py), and what the kit reader takes
# from git, contract cases (tests/contract/test_gather.py); each step here checks a command's wiring once.
# Reads: tests/stubs-sites/ plugin/lib/board.py plugin/lib/sites.py plugin/lib/page.py plugin/lib/page.html plugin/lib/fleet.html
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
export PATH="$TESTS/stubs-sites:$PATH"
team_world
box=chuck-herdr-alpha
ak=$(kit mac-studio willdan atlas-kit)
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
now=$(date +%s)
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "$2"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE="@$((now - $1 * 60)) +0000" git -C "$2" commit -qm "$3"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
j() { jq -r "$1" <<<"$json"; }
# lane <board> <heading>: the lines of one lane, up to the next heading; line_of <text> <words>: the lines holding them
lane() { awk -v g="$2" '$0 == g {on = 1; next} /^[^ !✓]/ {on = 0} on' <<<"$1"; }
line_of() { grep -F -- "$2" <<<"$1" || true; }
st() { jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first' <<<"$json"; }
records() { cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/*/*.rec "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null | wc -l; }

# The flow: a signal captured from a meeting and an exploration on the kit's main; apex-zones planned and a unit
# queued; swb-1 holding tenant-environments on the box, with a in code in a slot and its dev server running, b at
# construct, c in verify with its report and a verify card posted before that row went (teams.17), and a fix; atl-1 holding atlas-maps on mac-studio, its unit's
# server running there.
w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; cap=2026-10-01-planning; mkdir -p "$w/signals/$cap"
printf -- '---\ncapture: %s\nsource: meeting\ncaptured_by: wldn-planner\nevent_date: 2026-10-01\nsignals: 1\n---\n' "$cap" > "$w/signals/$cap/capture.md"
printf -- '---\nsignal: %s/01-zones\nkind: ask\n---\n\nEvery apex should be a zone of its own.\n' "$cap" > "$w/signals/$cap/01-zones.md"
commit_all "$w" "signals: the planning meeting"; git -C "$w" push -q origin main
mkdir -p "$k/openspec/explorations/command-cost"
printf '\n> Reading: what each crew command costs.\n' > "$k/openspec/explorations/command-cost/reading.md"; commit_all "$k" "docs: a reading"; push "$k"
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null
crew unit add later "Later." --repo switchboard-kit --source docs/zones.md >/dev/null
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt new atlas-maps "Atlas draws maps." --repo atlas-kit >/dev/null
crew unit add map-one "Map one." --bolt atlas-maps >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1; crew bolt give atl-1 atlas-maps >/dev/null 2>&1
pa=$(place "$k" tenant-environments a); change "$pa" a 1 2; commit_at 90 "$pa" "feat(a): task 1"
pb=$(place "$k" tenant-environments b)
pc=$(place "$k" tenant-environments c); change "$pc" c 2 2; commit_at 70 "$pc" "feat(c): done"
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
rc=$reports/verify-c-$(shown 60 %Y%m%d-%H%M).md; touch -t "$(shown 60 %Y%m%d%H%M.%S)" "$rc"
stamp=$(basename "$rc" .md); stamp=${stamp#verify-c-}
CREW_AGENT=swb-1-conductor as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act card.post --on unit/c \
  --field Card=req_ver-1 --field "Key=verify/c/$stamp" >/dev/null
fix=$kd/places/fix-tenant-environments--edge; git -C "$k" worktree add -q --track -b fix/tenant-environments/edge "$fix" bolt/tenant-environments
printf 'unit-1 unit a %s\nunit-2 unit b %s\nunit-3 unit c %s\nunit-4 fix fix/tenant-environments/edge %s\n' "$pa" "$pb" "$pc" "$fix" \
  > "$(home_of $box)/.local/state/swb-1-team/slots"
place "$ak" atlas-maps map-one >/dev/null
echo $box > "$(home_of $box)/.devurl-label"; echo studio > "$(home_of mac-studio)/.devurl-label"
printf 'unit-a--switchboard-kit\nbolt-tenant-environments--switchboard-kit\n' > "$(home_of $box)/.portless-routes"
printf 'unit-map-one--atlas-kit\n' > "$(home_of mac-studio)/.portless-routes"

: > "$CREW_TEST_LOG"
expect_ok crew bolts --json; json=$out
eq "$(grep -c ' ssh chuck-herdr-alpha ' "$CREW_TEST_LOG")" "1"
eq "$(st a) $(st b) $(st c) $(st map-one) $(st zone-one)" "code construct verify construct ready"
eq "$(j '.partitions[0].plans[0].bolts[] | select(.bolt == "tenant-environments") | "\(.team) \(.host) \(.state) \(.fixes[0].fix)"')" \
  "swb-1 $box active fix/tenant-environments/edge"
eq "$(j '.partitions[0].plans[0].queue[0] | "\(.unit) \(.stage)"')" "later queued"
expect_ok crew bolts
has "$out" "  a                                        code 1/2     places/a"
: > "$CREW_TEST_LOG"; expect_ok crew bolts apex-zones
has "$out" "apex-zones  switchboard-kit  no team  planned"; lacks "$out" "tenant-environments"
eq "$(grep -c ' ssh ' "$CREW_TEST_LOG" || true)" "0"
ok "crew bolts reads each unit's stage from its kit, one ssh for the host holding a bolt, and none for a planned bolt alone"

expect_ok crew sites wldn --json; json=$out
te='.partitions[0].hosts[] | select(.host == "chuck-herdr-alpha") | .bolts[0]'
eq "$(j "$te | .units[] | select(.unit == \"a\") | .url")" "https://unit-a--switchboard-kit--$box.dev.swancloud.net"
eq "$(j "$te | .units[] | select(.unit == \"b\") | .url")" "null"
eq "$(j '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0].url')" "https://unit-map-one--atlas-kit.local"
expect_ok crew sites wldn; has "$out" "places/b"; has "$out" "no server running"
HOST=$box expect_ok crew sites wldn; has "$out" "unit-map-one--atlas-kit--studio.dev.swancloud.net  (open from a Mac)"
ok "crew sites gives each running dev server's URL as it opens from where it is asked, and none where none runs"

s1=$(printf 'a%.0s' $(seq 40))
expect_ok crew ops offer mac-studio --label wldn --from none --to "$s1"
before=$(tip); n=$(records)
expect_ok crew board --label wldn; b=$out
eq "$(line_of "$(lane "$b" Operation)" "deploy ${s1:0:7}")" "✓ mac-studio  deploy ${s1:0:7} from nothing deployed  waits on the user's word  carrying what can't be read: ${s1:0:7} is no landing's commit in the record  card open, asked by wldn-ops"
eq "$(grep -E '^[A-Za-z]' <<<"$b" | tail -n +2 | tr '\n' '|')" "Inception|Bolt plan|Construction|Operation|attention|"
has "$(lane "$b" Inception)" "Every apex should be a zone of its own."
has "$(lane "$b" Inception)" "exploration  switchboard-kit command-cost"
eq "$(line_of "$(lane "$b" "Bolt plan")" "zone-one")" "    zone-one  ready"
con=$(lane "$b" Construction)
eq "$(line_of "$con" "  a  ")" "    a  code 1/2  unit-1  https://unit-a--switchboard-kit--$box.dev.swancloud.net"
eq "$(line_of "$con" "  c  ")" "    c  verify 2/2  unit-3"
lacks "$b" $'\033'
CREW_LABEL= expect_ok crew board
eq "$(grep -oE '^[a-z]+ board, as of' <<<"$out" | tr '\n' '|')" "wldn board, as of|madswan board, as of|swancloud board, as of|"
expect_ok crew board --label wldn --json; json=$out
eq "$(j 'keys | join(" ")')" "from partitions read_at unread"
eq "$(j '.partitions[0].plan')" "$before"
eq "$(tip) $(records)" "$before $n"; eq "$(git -C "$k" status --porcelain)" ""
ok "crew board draws the lanes from the plan, the signals, the kits, their servers and the cards, one board per partition outside any agent, and writes nothing"

# The host's follower and the rail and board tabs: the card session of a proposal of more than fifteen new units,
# started ten minutes ago, whose row went when the proposal was dropped. crew board leaves it; the follower's round,
# with no tab open, one fetch of the state branch and one read of each host's kits, writes the rail as crew rail prints
# it, which the rail tab draws, ends the session and writes the frame the board tab draws.
{ printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-two "The console, again." --repo switchboard-kit'
  for i in $(seq 1 16); do echo "Do: unit add page-$i \"Page $i.\" --bolt console-two"; done; } > "$T/p.rec"
crew plan propose "$T/p.rec" >/dev/null 2>&1
expect_ok crew card session proposal/1
s=$(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/1/session.json; pid=$(jq -r .pid "$s")
jq -c '.started = "2026-01-01T00:00:00Z"' "$s" > "$s.new" && mv "$s.new" "$s"
crew plan drop 1 "Not now." >/dev/null
expect_ok crew board --label wldn
kill -0 "$pid" 2>/dev/null || fail "crew board ended a card session"
frame=$(home_of mac-studio)/.cache/crew/board/wldn.json
expect_ok crew _board wldn --once; has "$out" "No board for wldn yet: the host's follower writes it each time it refreshes"
expect_ok crew _rail wldn --once; has "$out" "No rail for wldn yet: the host's follower writes it each time it refreshes"
# The follower's reads, counted by shims on git (a fetch, or any other git), on python3 piped a request (a host's
# kits gathered, or only stamped) or running a host's card sweep, and in this process for this host's kits
# (CREW_TEST_READS).
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@"> <what it logs> [<test> <what>]...: the first test that holds is logged
  local cmd=$1 cond=if body=""; shift
  while (( $# )); do body+="$cond $1; then echo \"\${CREW_TEST_HOST:-?} $2\" >> $(printf %q "$T/reads.log"); "; cond=elif; shift 2; done
  printf '#!/usr/bin/env bash\n%sfi\nexec %q "$@"\n' "$body" "$(command -v "$cmd")" > "$T/shim/$cmd"
  chmod +x "$T/shim/$cmd"
}
shim git '[[ " $* " == *" fetch "*refs/crew/wldn/main* ]]' fetch '[[ " $* " != *" fetch "* ]]' git
shim python3 '[[ ${1:-} == - && ${2:-} == *\"stamp\":\ true* ]]' stamp '[[ ${1:-} == - ]]' gather '[[ " $* " == *" card sweep "* ]]' sweep
reads() { grep -c "^$1 $2\$" "$T/reads.log" || true; }
: > "$T/reads.log"
CREW_TEST_READS=$T/reads.log PATH="$T/shim:$PATH" expect_ok crew _follow --once
eq "$(reads mac-studio fetch) $(reads mac-studio gather) $(reads $box gather) $(reads $box fetch)" "1 1 1 0"
has "$out" "wldn's rail, board and agents' views written on mac-studio"
has "$out" "swancloud's rail, board and agents' views written on mac-studio"
[[ -s $(home_of mac-studio)/.cache/crew/board/swancloud.rail.json && -s $(home_of mac-studio)/.cache/crew/board/swancloud.agents.json ]] ||
  fail "the follower did not write swancloud's frames beside wldn's"
views=$(jq -r .text "$(home_of mac-studio)/.cache/crew/board/wldn.rail.json")
has "$views" $'card sessions ended:\n  proposal/1 (wldn) on mac-studio: its row is gone; ended proposal/1\'s session, plannotator pid '"$pid"
python3 -c 'import os, sys, time
pid, give_up = int(sys.argv[1]), time.monotonic() + 600
while True:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        break
    if time.monotonic() > give_up:
        sys.exit(f"pid {pid} is still running")
    time.sleep(0.05)' "$pid" || fail "the follower's round did not end the dead card session"
# mask: a rail's lines with each row's age left out, since a minute can turn between two reads
mask() { sed -E 's/^(  [0-9]{4}-.{11}  ).{7}/\1AGE    /'; }
expect_ok crew rail --label wldn; rail=$out
eq "$(head -n "$(wc -l <<<"$rail")" <<<"$views" | tail -n +2 | mask)" "$(tail -n +2 <<<"$rail" | mask)"
expect_ok crew _rail wldn --once
eq "$(head -n "$(wc -l <<<"$rail")" <<<"$out" | tail -n +2 | mask)" "$(tail -n +2 <<<"$rail" | mask)"
eq "$(jq -S 'del(.read_at)' "$frame")" "$(crew board --label wldn --json | jq -S 'del(.read_at)')"
agents=$(home_of mac-studio)/.cache/crew/board/wldn.agents.json
eq "$(jq -r '.read_at' "$agents") $(jq -r '.views | has("swb-1-conductor") and has("wldn-planner")' "$agents")" "$(jq -r '.read_at' "$frame") true"
has "$(jq -r '.cards["swb-1-conductor"][0] | map(.[0]) | join("")' "$agents")" "  your card  verify/c/$stamp  req_ver-1  open "
has "$rail" "verify/c/$stamp (wldn), asked by swb-1-conductor on $box"$'\n'"    left:   a rail read on $box closes it, under that host's sign-in"
expect_ok crew _board wldn --once
eq "$(tail -n +2 <<<"$out")" "$(crew board --label wldn | tail -n +2)"
ok "the host's follower, with no tab open, writes each partition's frames there from one read, one fetch of the state branch and one read of each host's kits, the rail the rail tab draws as crew rail prints it, ends the dead session crew board left, and writes the frame the board tab draws as crew board does, with each agent's view and open cards beside it"

# The follower running: its clock set past the test's length, so only a signal ticks it (tests.8), and each kit's queue
# followed through the stub sluice's overview watch. Its first refresh reads and opens a watch on each kit holding a
# bolt, the box's over ssh, its gathers running no sluice status; a tick with nothing moved fetches and then starts no git and no gather on mac-studio and
# asks the box for its stamps alone; a plan write on mac-studio is shown at the next look, with nothing fetched and no
# kit gathered; a reading's result written on mac-studio, as plannotator writes the one the user sends back, has
# mac-studio's card sessions swept at the next look, the box's not, and nothing gathered; a write to sluice's folder in
# the box's kit moves nothing at the next tick; a merge of unit a queued in sluice, its watch printing a new line, puts
# the submission's number on a's row at the next look, with nothing gathered and no sluice run but the watches; and a
# dev server started on the box shows on b's line after the next tick, with nothing gathered.
written() { python3 -c 'import os, sys; print(os.stat(sys.argv[1]).st_ino)' "$(home_of mac-studio)/.cache/crew/board/wldn.rail.json"; }
rewritten() { [[ $(written) != "$1" ]] && grep -q "^$box \(stamp\|gather\)\$" "$T/reads.log"; }
railtext() { jq -r .text "$(home_of mac-studio)/.cache/crew/board/wldn.rail.json"; }
unit_of() { jq -c --arg u "$1" '.partitions[0].construction[] | select(.bolt == "tenant-environments") | .units[] | select(.unit == $u)' "$frame"; }
only_stamps() { eq "$(grep -c "^$box " "$T/reads.log") $(grep -v ' overview --json --watch' "$CREW_TEST_LOG" | grep -c " ssh $box ")" "$(reads $box stamp) $(reads $box stamp)"; }
at=$(jq -r .read_at "$(home_of mac-studio)/.cache/crew/board/wldn.rail.json"); was=$(written); : > "$T/reads.log"; : > "$CREW_TEST_LOG"
( export CREW_TEST_HOST=mac-studio HOME=$(home_of mac-studio) CREW_TEST_PERIOD=3600 CREW_TEST_READS=$T/reads.log PATH="$T/shim:$PATH"
  cd "$HOME" && exec "$CREW/plugin/bin/crew" _follow ) > "$T/follower" 2>&1 &
fol=$!
until_ok rewritten "$was" || fail "the running follower never refreshed: $(cat "$T/follower")"
eq "$(reads $box gather)" "1"
watching() { grep -q "^$box sluice overview --json --watch in " "$CREW_TEST_LOG" && grep -q "^mac-studio sluice overview --json --watch in " "$CREW_TEST_LOG"; }
until_ok watching || fail "the follower opened no overview watch on each kit: $(cat "$CREW_TEST_LOG")"
! grep -q " sluice status " "$CREW_TEST_LOG" || fail "the follower's read of the kits ran sluice status: $(grep ' sluice status ' "$CREW_TEST_LOG")"
was=$(written); : > "$T/reads.log"; : > "$CREW_TEST_LOG"
kill -USR1 "$fol"
until_ok rewritten "$was" || fail "the follower's tick wrote no frame: $(cat "$T/follower")"
eq "$(reads mac-studio fetch) $(reads mac-studio git) $(reads mac-studio gather) $(reads $box gather) $(reads $box stamp)" "1 0 0 0 1"
only_stamps
[[ ! $(jq -r .read_at "$(home_of mac-studio)/.cache/crew/board/wldn.rail.json") < $at ]] || fail "the tick's frame is older than the last"
printf '%s\n' 'Case: The zones get a second unit.' 'Do: unit add zone-two "Zone two." --bolt apex-zones' > "$T/p2.rec"
: > "$T/reads.log"
crew plan propose "$T/p2.rec" >/dev/null 2>&1
proposed() { railtext | grep -q "The zones get a second unit."; }
until_ok proposed || fail "the follower did not show the proposal: $(cat "$T/follower")"
eq "$(reads mac-studio fetch) $(reads mac-studio gather) $(reads $box gather)" "0 0 0"
sent=$(home_of mac-studio)/.local/state/crew/cards/wldn/batch/9; mkdir -p "$sent"
was=$(written); : > "$T/reads.log"
echo '{"decision": "approved", "feedback": ""}' > "$sent/result.json"
until_ok rewritten "$was" || fail "the follower did not refresh at the reading sent back: $(cat "$T/follower")"
(( $(reads mac-studio sweep) > 0 )) || fail "the reading sent back on mac-studio did not sweep its card sessions: $(cat "$T/reads.log")"
eq "$(reads $box sweep) $(reads mac-studio gather) $(reads $box gather) $(reads mac-studio fetch)" "0 0 0 0"
proposed || fail "the rail lost its words at the sweep: $(railtext)"
records=$(git -C "$k" rev-parse --path-format=absolute --git-common-dir)/sluice; mkdir -p "$records/main/submissions" "$records/bolt/tenant-environments/submissions"
echo 2 > "$records/main/version"; echo '{}' > "$records/bolt/tenant-environments/submissions/41.json"
was=$(written); : > "$T/reads.log"
kill -USR1 "$fol"
until_ok rewritten "$was" || fail "the follower's tick after sluice's write wrote no frame: $(cat "$T/follower")"
eq "$(reads $box gather) $(reads mac-studio gather) $(reads mac-studio git)" "0 0 0"
proposed || fail "the rail lost its words at sluice's write: $(railtext)"
eq "$(unit_of a | jq -c .submission)" "null"
: > "$T/reads.log"; : > "$CREW_TEST_LOG"
jq -n '{schema: "sluice/overview@1", at: "2026-10-28T16:24:41Z", branches: [{branch: "bolt/tenant-environments",
  submissions: [{id: 41, branch: "bolt/tenant-environments", state: "testing", from: {worktree: "unit/a"}}]}]}' > "$T/sluice-overview.json"
queued() { [[ $(unit_of a | jq -c .submission) == '{"id":41,"state":"testing"}' ]]; }
until_ok queued || fail "the watch's new line did not put the submission on a's row: $(unit_of a)"
eq "$(reads mac-studio gather) $(reads $box gather) $(reads mac-studio fetch)" "0 0 0"
eq "$(grep ' sluice ' "$CREW_TEST_LOG" | grep -vc ' overview --json --watch' || true)" "0"
expect_ok crew _board wldn --once; has "$(line_of "$out" "  a  ")" "#41 under test"
was=$(written); : > "$T/reads.log"
eq "$(unit_of b | jq -r .url)" "null"
echo unit-b--switchboard-kit >> "$(home_of $box)/.portless-routes"
kill -USR1 "$fol"
until_ok rewritten "$was" || fail "the follower's tick after the dev server started wrote no frame: $(cat "$T/follower")"
served() { [[ $(unit_of b | jq -r .url) == "https://unit-b--switchboard-kit--$box.dev.swancloud.net" ]]; }
until_ok served || fail "the dev server started on the box is not on b's line: $(unit_of b)"
eq "$(reads mac-studio gather) $(reads $box gather)" "0 0"
proposed || fail "the rail lost its words at the tick: $(railtext)"
kill "$fol"; wait "$fol" 2>/dev/null || true
ok "the running follower's first read runs no sluice status, its tick with nothing moved starts no git and no gather on mac-studio and asks the box for its stamps alone, a plan write on mac-studio is shown at its next look with nothing fetched and no kit gathered, a reading sent back there has mac-studio's card sessions swept and nothing gathered, a write to sluice's folder moves nothing, a merge queued in sluice is on its row from the kit's overview watch with nothing gathered, and a dev server started on the box shows after the next tick with nothing gathered"

# crew page: the page written whole under the partition's state folder, its path and header printed, nothing
# appended; a node's history on it, and its dock's, is what crew trace prints.
mine=$(home_of mac-studio)/.local/state/crew/wldn
block() { python3 -c 'import re, sys; t = open(sys.argv[1]).read(); m = re.findall(r"<script type=\"application/json\" id=\"data\">(.*?)</script>", t, re.S); print(m[0] if len(m) == 1 else "")' "$1"; }
n=$(records)
expect_ok crew page wldn
eq "$(sed -n 1p <<<"$out")" "$mine/page.html"
[[ $(sed -n 2p <<<"$out") =~ ^as\ of\ [0-9-]{10}\ [0-9:]{5}Z\ ·\ wldn/main\ $(git --git-dir "$ws" rev-parse --short=7 wldn/main)$ ]] || fail "the header line: $out"
json=$(block "$mine/page.html")
eq "$(j .made.commit) $(j '[.board.construction[].bolt] | join(" ")')" "$(tip) tenant-environments atlas-maps"
eq "$(j '.deploys[] | select(.env == "mac-studio") | .deploys[0] | "\(.to[:7]) \(.answer)"') $(j '.board.environments[0].deploys[0].row')" "${s1:0:7} waiting deploy/mac-studio"
eq "$(records)" "$n"
expect_ok crew trace unit/a
eq "$(j '.histories["unit/a"][] as $i | .entries[$i] | "\(.At[5:10]) \(.At[11:19]) \(.Act)"')" "$(awk '{print $1, $2, $3}' <<<"$out")"
eq "$(j '.board.construction[] | select(.bolt == "tenant-environments") | .dock') $(j '.docks["bolt:tenant-environments"].title')" \
  "bolt:tenant-environments tenant-environments"
eq "$(j '.docks["unit:a"].history[] as $i | .entries[$i] | "\(.At[5:10]) \(.At[11:19]) \(.Act)"')" "$(awk '{print $1, $2, $3}' <<<"$out")"
ok "crew page writes the page whole, with the board as crew board reads it, the deploys and a dock for each item, prints its path and as of which commit, and appends nothing"

# The partition links follow the page's own file: written as <label>.html, as swancloud's board serves them side by
# side, it links <other>.html; written where its file and folder name no partition, it links none and says so.
parts() { grep -o '<nav class="parts"[^>]*>.*</nav>' "$1"; }
expect_ok crew page wldn --out "$T/served/wldn.html"
nav=$(parts "$T/served/wldn.html"); has "$nav" 'href="madswan.html"'; has "$nav" 'href="swancloud.html"'
lacks "$out" "not linked"
expect_ok crew page wldn --out "$T/served/board.html"
lacks "$(parts "$T/served/board.html")" "<a "
eq "$(sed -n 3p <<<"$out")" "the other partitions are not linked: $T/served/board.html is neither named wldn.html nor in a folder wldn"
ok "a page written as <label>.html links the other partitions' pages beside it, and one whose file and folder name no partition links none and says so"

# crew page --fleet: every partition of the teams file on one page, written beside the partitions' folders, its path
# and each partition's header printed; its links follow its file as the partition page's do, and a partition's page
# served as <label>.html links back to the fleet page as index.html. With no use published yet, it says so and each
# subscription says no host has published its use.
fleet=$(home_of mac-studio)/.local/state/crew/page.html
usage=$(home_of mac-studio)/.local/state/crew/usage
expect_ok crew page --fleet
eq "$(sed -n 1p <<<"$out")" "$fleet"
eq "$(tail -n 1 <<<"$out")" "no subscription's use is published in $usage"
eq "$(sed -n 2,4p <<<"$out" | sed -E 's/^as of [0-9-]{10} [0-9:]{5}Z · //' | tr '\n' '|')" \
  "wldn/main $(git --git-dir "$ws" rev-parse --short=7 wldn/main)|madswan/main not started|swancloud/main not started|"
json=$(block "$fleet")
eq "$(j '[.partitions[].label] | join(" ")')" "wldn madswan swancloud"
eq "$(j '.partitions[0].link') $(j '.partitions[0].teams[] | select(.team == "swb-1") | .link')" "wldn/page.html wldn/page.html#dock=team:swb-1"
eq "$(block "$mine/page.html" | jq -r '.docks["team:swb-1"].title')" "swb-1"
eq "$(j '.partitions[0].kits[] | select(.kit == "switchboard-kit") | .said[1]')" "tenant-environments in construction; 1 bolt planned; 1 unit queued"
eq "$(j '[.subscriptions.items[] | .account + " " + .state] | join(", ")')" "credits none, ia none, madswan none, willdan-alex none"
expect_ok crew page --fleet --out "$T/served/index.html"
eq "$(block "$T/served/index.html" | jq -r '.partitions[0].link')" "wldn.html"
lacks "$out" "not linked"
expect_ok crew page --fleet --out "$T/served/fleet.html"
has "$out" "the partitions are not linked: $T/served/fleet.html is named neither index.html nor page.html"
expect_ok crew page wldn --out "$T/served/wldn.html"
has "$(parts "$T/served/wldn.html")" 'href="index.html"'
expect_fail "crew page takes a partition's label or --fleet, not both" crew page wldn --fleet
eq "$(records)" "$n"
ok "crew page --fleet writes every partition on one page beside their folders, links each in the layout of its file and says when it can't, and a partition's page served beside it links back"

# The use mac-studio's reader published beside the box's file, which is not JSON: ia's figures shown as read by
# mac-studio, credits' reading marked as not made, and the box's file named by the command; the page still written.
mkdir -p "$usage"
at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat > "$usage/mac-studio.json" <<JSON
{"host": "mac-studio", "readings": [
 {"account": "ia", "at": "$at", "five_hour": {"utilization": 34.0, "resets_at": null}, "seven_day": {"utilization": 61.0, "resets_at": null}},
 {"account": "credits", "at": "$at", "unread": "the usage endpoint answered 401"}]}
JSON
echo "not json" > "$usage/$box.json"
expect_ok crew page --fleet
has "$out" "the use published in $usage/$box.json could not be read: it is not JSON: "
lacks "$out" "no subscription's use is published"
json=$(block "$fleet")
eq "$(j '.subscriptions.items[] | select(.account == "ia") | .windows[0].said')" "five-hour 34%"
has "$(j '.subscriptions.items[] | select(.account == "ia") | .said')" "read by mac-studio "
eq "$(j '.subscriptions.items[] | select(.account == "credits") | .state')" "unread"
eq "$(j '.unread_usage[0].file')" "$usage/$box.json"
eq "$(records)" "$n"
ok "crew page --fleet shows the use each host published by subscription, and names a published file it cannot read"

# The box asleep: every view names it and shows the rest.
echo $box > "$T/down"
expect_ok crew bolts; has "$out" "$box did not answer"; has "$out" "  map-one"
expect_ok crew board --label wldn
has "$(lane "$out" attention)" "! $box did not answer (its kits: "; lacks "$(lane "$out" attention)" "run record"
eq "$(line_of "$(lane "$out" Construction)" "  a  ")" "    a  unknown"
expect_ok crew sites wldn; has "$out" "$box  did not answer"; has "$out" "unit-map-one--atlas-kit.local"
expect_ok crew page wldn; has "$(sed -n 3p <<<"$out")" "$box did not answer"
expect_ok crew page --fleet; has "$out" "wldn: $box did not answer (its kits: "
eq "$(block "$fleet" | jq -r --arg h $box '.partitions[0].hosts[] | select(.host == $h) | .answered')" "false"
rm "$T/down"
ok "a host that does not answer is named by crew bolts, board, sites, page and the fleet page, for its kits alone, and the rest is shown"

cp "$mine/page.html" "$T/earlier.html"
mv "$ws" "$ws.away"
expect_fail "no page is written: wldn/main of WilldanGroup/crew-state could not be read" crew page wldn
mv "$ws.away" "$ws"
cmp -s "$mine/page.html" "$T/earlier.html" || fail "the earlier page was changed"
ok "when the branch cannot be read crew page writes nothing and names the branch"

# A hand edit that leaves a duplicated key: crew bolts refuses to read the plan, naming the commit and recfix's
# message; crew board names it in the attention line and exits non-zero.
h=$T/hand; git clone -q -b wldn/main "$ws" "$h"
printf '\nUnit: a\nRepo: switchboard-kit\nIntent: twice\n' >> "$h/plan.rec"; commit_all "$h" "plan: a hand edit"; push_state "$h"
expect_fail "wldn/main of WilldanGroup/crew-state at $(git -C "$h" rev-parse --short HEAD): plan.rec fails recfix --check" crew bolts
has "$out" "duplicated key"
expect_fail "wldn/main of WilldanGroup/crew-state" crew board --label wldn
has "$(lane "$out" attention)" "! the plan, wldn/main of WilldanGroup/crew-state: "
ok "a plan that fails its schema is refused by crew bolts, naming the commit, and named in the board's attention line"
