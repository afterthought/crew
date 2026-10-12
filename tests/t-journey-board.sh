# The flow as the user reads it, through the crew command on the stubs (tests.11, record 0022): crew bolts lists every
# bolt and unit with each unit's stage read from its kit, one ssh per host holding a bolt and none for planned work;
# crew sites gives each dev server's URL as it opens from where it is asked; crew board draws the four lanes, an
# environment's deploy among the Operation lane's, and the attention line from one read, writes nothing and ends no
# card session; the rail tab's refresh, in one fetch and one read of each host's kits, prints the rail, sweeps a dead
# card session and writes the board's frame, which the board tab draws; crew page writes the page whole, with the
# deploys, and nothing when the branch can't be read; every view names a host that does not answer and shows the
# rest; and a plan a hand edit broke is refused, named by its commit. What each lane,
# line, URL and node says are logic cases (tests/py/test_board.py, test_page.py, test_rail.py), and what the kit
# reader takes from git, contract cases (tests/contract/test_gather.py); each step here checks a command's wiring once.
# Reads: tests/stubs-sites/ plugin/lib/board.py plugin/lib/sites.py plugin/lib/page.py plugin/lib/page.html
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
lane() { awk -v g="$2" '$0 == g {on = 1; next} /^[^ !✓✎]/ {on = 0} on' <<<"$1"; }
line_of() { grep -F -- "$2" <<<"$1" || true; }
st() { jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first' <<<"$json"; }
records() { cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/*/*.rec "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null | wc -l; }

# The flow: a signal captured from a meeting and an exploration on the kit's main; apex-zones planned and a unit
# queued; swb-1 holding tenant-environments on the box, with a in code in a slot and its dev server running, b at
# construct, c with a verify report and its card open, and a fix; atl-1 holding atlas-maps on mac-studio, its unit's
# server running there.
w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; cap=2026-10-01-planning; mkdir -p "$w/signals/$cap"
printf -- '---\ncapture: %s\nsource: meeting\ncaptured_by: wldn-planner\nevent_date: 2026-10-01\nsignals: 1\n---\n' "$cap" > "$w/signals/$cap/capture.md"
printf -- '---\nsignal: %s/01-zones\nkind: ask\n---\n\nEvery apex should be a zone of its own.\n' "$cap" > "$w/signals/$cap/01-zones.md"
commit_all "$w" "signals: the planning meeting"; git -C "$w" push -q origin main
mkdir -p "$k/openspec/explorations/command-cost"
printf '\n> Reading: what each crew command costs.\n' > "$k/openspec/explorations/command-cost/reading.md"; commit_all "$k" "docs: a reading"
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
eq "$(line_of "$(lane "$b" Operation)" "deploy ${s1:0:7}")" "✓ mac-studio  deploy ${s1:0:7} from nothing deployed  waits on the user's word  carrying what can't be read: ${s1:0:7} is no landing's commit in the record  no card open"
eq "$(grep -E '^[A-Za-z]' <<<"$b" | tail -n +2 | tr '\n' '|')" "Inception|Bolt plan|Construction|Operation|attention|"
has "$(lane "$b" Inception)" "Every apex should be a zone of its own."
has "$(lane "$b" Inception)" "exploration  switchboard-kit command-cost"
eq "$(line_of "$(lane "$b" "Bolt plan")" "zone-one")" "    zone-one  ready"
con=$(lane "$b" Construction)
eq "$(line_of "$con" "  a  ")" "    a  code 1/2  unit-1  https://unit-a--switchboard-kit--$box.dev.swancloud.net"
eq "$(line_of "$con" "  c  ")" "✎   c  verify 2/2  unit-3  card open, asked by swb-1-conductor"
lacks "$b" $'\033'
CREW_LABEL= expect_ok crew board
eq "$(grep -oE '^[a-z]+ board, as of' <<<"$out" | tr '\n' '|')" "wldn board, as of|madswan board, as of|swancloud board, as of|"
expect_ok crew board --label wldn --json; json=$out
eq "$(j 'keys | join(" ")')" "from partitions read_at unread"
eq "$(j '.partitions[0].plan')" "$before"
eq "$(tip) $(records)" "$before $n"; eq "$(git -C "$k" status --porcelain)" ""
ok "crew board draws the lanes from the plan, the signals, the kits, their servers and the cards, one board per partition outside any agent, and writes nothing"

# The board tab and the rail tab's refresh: a proposal's card session, started ten minutes ago, whose row went when
# the proposal was dropped. crew board leaves it; the refresh, one fetch of the state branch and one read of each
# host's kits, prints the rail as crew rail does, ends the session and writes the frame the board tab draws.
printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-two "The console, again." --repo switchboard-kit' > "$T/p.rec"
crew plan propose "$T/p.rec" >/dev/null 2>&1
expect_ok crew card session proposal/1
s=$(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/1/session.json; pid=$(jq -r .pid "$s")
jq -c '.started = "2026-01-01T00:00:00Z"' "$s" > "$s.new" && mv "$s.new" "$s"
crew plan drop 1 "Not now." >/dev/null
expect_ok crew board --label wldn
kill -0 "$pid" 2>/dev/null || fail "crew board ended a card session"
frame=$(home_of mac-studio)/.cache/crew/board/wldn.json
expect_ok crew _board wldn --once; has "$out" "No board for wldn yet: the rail tab's loop writes it each time it refreshes"
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@" that logs <what>> <what>
  printf '#!/usr/bin/env bash\nif %s; then echo "${CREW_TEST_HOST:-?} %s" >> %q; fi\nexec %q "$@"\n' "$2" "$3" "$T/reads.log" "$(command -v "$1")" > "$T/shim/$1"
  chmod +x "$T/shim/$1"
}
shim git '[[ " $* " == *" fetch "*refs/crew/wldn/main* ]]' fetch
shim python3 '[[ ${1:-} == - ]]' gather
reads() { grep -c "^$1 $2\$" "$T/reads.log" || true; }
: > "$T/reads.log"
CREW_TEST_READS=$T/reads.log PATH="$T/shim:$PATH" expect_ok crew _views wldn; views=$out
eq "$(reads mac-studio fetch) $(reads mac-studio gather) $(reads $box gather) $(reads $box fetch)" "1 1 1 0"
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
    time.sleep(0.05)' "$pid" || fail "the refresh did not end the dead card session"
# mask: a rail's lines with each row's age left out, since a minute can turn between two reads
mask() { sed -E 's/^(  [0-9]{4}-.{11}  ).{7}/\1AGE    /'; }
expect_ok crew rail --label wldn; rail=$out
eq "$(head -n "$(wc -l <<<"$rail")" <<<"$views" | tail -n +2 | mask)" "$(tail -n +2 <<<"$rail" | mask)"
eq "$(jq -S 'del(.read_at)' "$frame")" "$(crew board --label wldn --json | jq -S 'del(.read_at)')"
agents=$(home_of mac-studio)/.cache/crew/board/wldn.agents.json
eq "$(jq -r '.read_at' "$agents") $(jq -r '.views | has("swb-1-conductor") and has("wldn-planner")' "$agents")" "$(jq -r '.read_at' "$frame") true"
expect_ok crew _board wldn --once
eq "$(tail -n +2 <<<"$out")" "$(crew board --label wldn | tail -n +2)"
ok "the rail tab's refresh fetches once and reads each host's kits once, prints the rail, ends the dead session crew board left, and writes the frame the board tab draws as crew board does, with each agent's view beside it from the same read"

# crew page: the page written whole under the partition's state folder, its path and header printed, nothing
# appended; a node's history on it is what crew trace prints.
mine=$(home_of mac-studio)/.local/state/crew/wldn
block() { python3 -c 'import re, sys; t = open(sys.argv[1]).read(); m = re.findall(r"<script type=\"application/json\" id=\"data\">(.*?)</script>", t, re.S); print(m[0] if len(m) == 1 else "")' "$1"; }
n=$(records)
expect_ok crew page wldn
eq "$(sed -n 1p <<<"$out")" "$mine/page.html"
[[ $(sed -n 2p <<<"$out") =~ ^as\ of\ [0-9-]{10}\ [0-9:]{5}Z\ ·\ wldn/main\ $(git --git-dir "$ws" rev-parse --short=7 wldn/main)$ ]] || fail "the header line: $out"
json=$(block "$mine/page.html")
eq "$(j .made.commit) $(j '[.board.construction[].bolt] | join(" ")')" "$(tip) tenant-environments atlas-maps"
eq "$(j '.deploys[] | select(.env == "mac-studio") | .deploys[0] | "\(.to[:7]) \(.answer)"') $(j '.board.environments[0].deploys[0].row')" "${s1:0:7} waiting deploy/mac-studio/${s1:0:7}"
eq "$(records)" "$n"
expect_ok crew trace unit/a
eq "$(j '.histories["unit/a"][] as $i | .entries[$i] | "\(.At[5:10]) \(.At[11:19]) \(.Act)"')" "$(awk '{print $1, $2, $3}' <<<"$out")"
ok "crew page writes the page whole, with the board as crew board reads it and the deploys, prints its path and as of which commit, and appends nothing"

# The box asleep: every view names it and shows the rest.
echo $box > "$T/down"
expect_ok crew bolts; has "$out" "$box did not answer"; has "$out" "  map-one"
expect_ok crew board --label wldn
has "$(lane "$out" attention)" "! $box did not answer (its kits: "
eq "$(line_of "$(lane "$out" Construction)" "  a  ")" "    a  unknown"
expect_ok crew sites wldn; has "$out" "$box  did not answer"; has "$out" "unit-map-one--atlas-kit.local"
expect_ok crew page wldn; has "$(sed -n 3p <<<"$out")" "$box did not answer"
rm "$T/down"
ok "a host that does not answer is named by crew bolts, board, sites and page, and the rest is shown"

cp "$mine/page.html" "$T/earlier.html"
mv "$ws" "$ws.away"
expect_fail "no page is written: wldn/main of WilldanGroup/crew-state could not be read" crew page wldn
mv "$ws.away" "$ws"
cmp -s "$mine/page.html" "$T/earlier.html" || fail "the earlier page was changed"
ok "when the branch cannot be read crew page writes nothing and names the branch"

# A hand edit that leaves a duplicated key: crew bolts refuses to read the plan, naming the commit and recfix's
# message; crew board names it in the attention line and exits non-zero.
h=$T/hand; git clone -q -b wldn/main "$ws" "$h"
printf '\nUnit: a\nRepo: switchboard-kit\nIntent: twice\n' >> "$h/plan.rec"; commit_all "$h" "plan: a hand edit"; git -C "$h" push -q origin wldn/main
expect_fail "wldn/main of WilldanGroup/crew-state at $(git -C "$h" rev-parse --short HEAD): plan.rec fails recfix --check" crew bolts
has "$out" "duplicated key"
expect_fail "wldn/main of WilldanGroup/crew-state" crew board --label wldn
has "$(lane "$out" attention)" "! the plan, wldn/main of WilldanGroup/crew-state: "
ok "a plan that fails its schema is refused by crew bolts, naming the commit, and named in the board's attention line"
