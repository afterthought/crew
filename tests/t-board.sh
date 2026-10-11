# crew board: the flow of a partition as four lanes in order (Inception, Bolt plan, Construction, Operation) and the
# attention line, one object to a line; every rail row a marker on its object with its card, never a line of its own;
# the same board as JSON; read from the plan, the proposals, the moves, the signals, the kits and the run record, and
# writing nothing. Each scenario of the crew-board spec, the board tab among them: one read of the rail tab's loop
# prints the rail and writes the board's frame, which the board tab draws, fresh, stale or not yet written.
# Reads: tests/stubs-sites/ plugin/lib/board.py plugin/lib/sites.py
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
export PATH="$TESTS/stubs-sites:$PATH"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
crew state init wldn >/dev/null
export CREW_LABEL=wldn
box=chuck-herdr-alpha
tip() { git --git-dir "$ws" rev-parse wldn/main; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
# Times are set, as in t-rail: at <minutes ago> as git takes it, shown <minutes ago> <format>, commit_at <minutes ago>
# <dir> <message>.
now=$(date +%s)
at() { echo "@$((now - $1 * 60)) +0000"; }
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "${2:-%Y-%m-%d %H:%M}"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE=$(at "$1") git -C "$2" commit -qm "$3"; }
# lane <board> <heading>: the lines of one lane, up to the next heading; line_of <text> <words>: the lines holding them
lane() { awk -v g="$2" '$0 == g {on = 1; next} /^[^ !✓✎]/ {on = 0} on' <<<"$1"; }
line_of() { grep -F -- "$2" <<<"$1" || true; }
j() { jq -r "$1" <<<"$json"; }

expect_ok crew board --label wldn
has "$(head -1 <<<"$out")" "wldn board, as of "
has "$(head -1 <<<"$out")" "read from $box, mac-studio"
eq "$(grep -E '^[A-Za-z]' <<<"$out" | tail -n +2 | tr '\n' '|')" "Inception|Bolt plan|Construction|Operation|attention|"
eq "$(grep -c '^  none$' <<<"$out")" "5"
lacks "$out" $'\033'
ok "with nothing in flight, the header and the four lanes in order, each saying none, then attention saying none; plain into a pipe"

CREW_LABEL= expect_ok crew board
eq "$(grep -oE '^[a-z]+ board, as of' <<<"$out" | tr '\n' '|')" "wldn board, as of|madswan board, as of|swancloud board, as of|"
has "$(awk '/^madswan board/ {on = 1} /^swancloud board/ {on = 0} on' <<<"$out")" "! the plan, madswan/main of afterthought/crew-state: not started"
has "$(awk '/^madswan board/ {on = 1} /^swancloud board/ {on = 0} on' <<<"$out")" "! the signals on main of afterthought/blueprints: could not fetch main of afterthought/blueprints"
ok "with no label outside any agent, one board per partition in the teams file, one after another"

# Inception: two signals wldn-planner captured from a meeting, in the blueprints; one note of the user's, on the
# flywheel's branch; an exploration on the kit's main.
w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; cap=2026-10-01-planning; mkdir -p "$w/signals/$cap"
printf -- '---\ncapture: %s\nsource: meeting\ncaptured_by: wldn-planner\nevent_date: 2026-10-01\nsignals: 2\n---\n\nThe planning meeting.\n' "$cap" > "$w/signals/$cap/capture.md"
printf -- '---\nsignal: %s/01-zones\nkind: ask\n---\n\nEvery apex should be a zone of its own.\n\n> "zones" - 00:10\n' "$cap" > "$w/signals/$cap/01-zones.md"
printf -- '---\nsignal: %s/02-tenants\nkind: constraint\n---\n\nTenants never share an environment.\n' "$cap" > "$w/signals/$cap/02-tenants.md"
commit_all "$w" "signals: the planning meeting"; git -C "$w" push -q origin main
note=$(crew signal plans-are-checked "Plans should be checked before they run." | sed -n 's/^signal \([^: ]*\)[: ].*/\1/p')
mkdir -p "$k/openspec/explorations/command-cost"
printf '\n> Reading: what each crew command costs, read 2026-10-01.\n\nMore.\n' > "$k/openspec/explorations/command-cost/reading.md"
commit_all "$k" "docs: a reading"

# Bolt plan: a planned bolt with a unit, and a queued unit.
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null
crew unit add zone-two "Zone two." --repo switchboard-kit --source docs/zones.md >/dev/null

# Construction: swb-1 holds tenant-environments, with unit a in code in a slot and its dev server running, b planned,
# c with a verify report newer than its last commit and a card open, and a fix; swb-2 holds console-pages, whose
# only unit has merged; brd-1 holds board-done, whose only unit has landed on main.
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
pa=$(place "$k" tenant-environments a); change "$pa" a 1 2; commit_at 90 "$pa" "feat(a): task 1"
pb=$(place "$k" tenant-environments b); change "$pb" b 0 2; commit_at 80 "$pb" "docs(b): the change"
pc=$(place "$k" tenant-environments c); change "$pc" c 2 2; commit_at 70 "$pc" "feat(c): done"
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
rc=$reports/verify-c-$(shown 60 %Y%m%d-%H%M).md; touch -t "$(shown 60 %Y%m%d%H%M.%S)" "$rc"
fix=$kd/places/fix-tenant-environments--edge; git -C "$k" worktree add -q --track -b fix/tenant-environments/edge "$fix" bolt/tenant-environments
printf 'unit-1 unit a %s\nunit-2 unit b %s\nunit-3 unit c %s\nunit-4 fix fix/tenant-environments/edge %s\n' "$pa" "$pb" "$pc" "$fix" \
  > "$(home_of $box)/.local/state/swb-1-team/slots"
echo $box > "$(home_of $box)/.devurl-label"
printf 'unit-a--switchboard-kit\nbolt-tenant-environments--switchboard-kit\n' > "$(home_of $box)/.portless-routes"
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew unit add page-one "Page one." --bolt console-pages >/dev/null
crew bolt give swb-2 console-pages >/dev/null 2>&1
pp=$(place "$k" console-pages page-one); change "$pp" page-one 2 2; commit_at 50 "$pp" "feat(page-one): done"
GIT_COMMITTER_DATE=$(at 40) git -C "$kd/bolts/console-pages" merge -q --no-ff -m "merge page-one" unit/page-one
bk=$(kit $box willdan breadboard-kit)
crew bolt new board-done "Boards are done." --repo breadboard-kit >/dev/null
crew unit add done-one "Done one." --bolt board-done >/dev/null
crew bolt give brd-1 board-done >/dev/null 2>&1
change "$bk" done-one 2 2; commit_all "$bk" "feat(done-one): done, on main"
# card <host> <agent> <act> <object> <card> [key]: a card entry, written as crew's hook writes it, on the owner's host
card() { CREW_AGENT=$2 as "$1" python3 "$CREW/plugin/lib/record.py" emit --label wldn --act "$3" --on "$4" --field "Card=$5" ${6:+--field "Key=$6"} >/dev/null; }
stamp=$(basename "$rc" .md); stamp=${stamp#verify-c-}
card $box swb-1-conductor card.post unit/c req_ver-1 "verify/c/$stamp"

expect_ok crew board --label wldn; b=$out
inc=$(lane "$b" Inception)
has "$(line_of "$inc" "signals captured by wldn-planner")" "2 not moved, the oldest captured 2026-10-01"
has "$(line_of "$inc" "signals captured by $me@mac-studio")" "1 not moved"
has "$(line_of "$inc" "Every apex should be a zone of its own.")" "    ask  Every apex should be a zone of its own.  $cap/01-zones"
has "$(line_of "$inc" "Tenants never share")" "    constraint  Tenants never share an environment.  $cap/02-tenants"
has "$(line_of "$inc" "Plans should be checked")" "    ask  Plans should be checked before they run.  $note"
eq "$(line_of "$inc" "command-cost")" "  exploration  switchboard-kit command-cost  Reading: what each crew command costs, read 2026-10-01."
ok "Inception lists the signals no move has taken, by who captured them with how many and the oldest, and each exploration on the kit's main with its first line"

crew unit add zone-three "Zone three." --bolt apex-zones --signal "$cap/01-zones" >/dev/null
expect_ok crew board --label wldn; inc=$(lane "$out" Inception)
lacks "$inc" "Every apex should be a zone"
has "$(line_of "$inc" "signals captured by wldn-planner")" "1 not moved"
has "$inc" "Tenants never share an environment."
ok "a signal routed to a unit leaves the board, and its capturer's group counts one fewer"

# Captures another tool wrote on the blueprints' main: one whose at has no zone, read as UTC, and one in +02:00. The
# board's JSON gives both in UTC; its text says their age, read in a zone that is not UTC.
utc_at() { python3 -c 'import datetime, sys; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=int(sys.argv[1]))).astimezone(datetime.timezone(datetime.timedelta(hours=int(sys.argv[2])))).strftime(sys.argv[3]))' "$@"; }
for c in 2026-10-02-otter:"$(utc_at 3 0 %Y-%m-%dT%H:%M:%S)" 2026-10-03-otter:"$(utc_at 5 2 %Y-%m-%dT%H:%M:%S+02:00)"; do
  mkdir -p "$w/signals/${c%%:*}"
  printf -- '---\ncapture: %s\nsource: otter\nat: %s\nsignals: 1\n---\n' "${c%%:*}" "${c#*:}" > "$w/signals/${c%%:*}/capture.md"
  printf -- '---\nsignal: %s/01-said\nkind: ask\n---\n\nSaid in %s.\n' "${c%%:*}" "${c%%:*}" > "$w/signals/${c%%:*}/01-said.md"
done
commit_all "$w" "signals: two otter captures"; git -C "$w" push -q origin main
TZ=Pacific/Honolulu expect_ok crew board --label wldn
has "$(line_of "$(lane "$out" Inception)" "signals captured by otter")" "2 not moved, the oldest captured 5h 0"
expect_ok crew board --label wldn --json; json=$out
eq "$(j '[.partitions[0].inception.signals[] | select(.signal | endswith("-otter/01-said")) | .at[:13]] | join(" ")')" "$(utc_at 5 0 %Y-%m-%dT%H) $(utc_at 3 0 %Y-%m-%dT%H)"
eq "$(j '[.partitions[0].inception.signals[] | select(.signal | endswith("-otter/01-said")) | .at | test("^[0-9-]{10}T[0-9:]{8}Z$")] | all')" "true"
git -C "$w" rm -rq signals/2026-10-02-otter signals/2026-10-03-otter; git -C "$w" commit -qm "signals: the otter captures gone"; git -C "$w" push -q origin main
ok "a capture whose at has no zone is read as UTC, and the board's JSON gives every capture's time in UTC, oldest first"

bp=$(lane "$b" "Bolt plan")
eq "$(line_of "$bp" "apex-zones")" "  switchboard-kit apex-zones  Apexes are zones."
eq "$(line_of "$bp" "zone-one")" "    zone-one  ready"
eq "$(line_of "$bp" "zone-two")" "  switchboard-kit zone-two  queued  docs/zones.md"
lacks "$bp" "tenant-environments"
ok "Bolt plan lists each bolt no team holds with its repository, goal and units with their stages, and the queue with each unit's sources"

con=$(lane "$b" Construction)
eq "$(line_of "$con" "tenant-environments  swb-1")" "  switchboard-kit tenant-environments  swb-1 on $box"
eq "$(line_of "$con" "  a  ")" "    a  code 1/2  unit-1  https://unit-a--switchboard-kit--$box.dev.swancloud.net"
eq "$(line_of "$con" "fix/tenant-environments/edge")" "    fix/tenant-environments/edge  fix  unit-4"
eq "$(line_of "$con" "  server  ")" "    server  https://bolt-tenant-environments--switchboard-kit--$box.dev.swancloud.net"
eq "$(grep -n "" <<<"$con" | grep -E 'tenant-environments  swb-1|  a  code|  b  planned|  c  verify|fix/tenant|server' | cut -d: -f1 | tr '\n' ' ')" "1 2 3 4 5 6 "
ok "Construction shows a held bolt as a ledger: its head, each unit in plan order with its stage, tasks, slot and dev server, its fix, and its own server at the foot"

eq "$(line_of "$con" "  b  ")" "    b  planned  unit-2"
eq "$(line_of "$con" "  c  ")" "✎   c  verify 2/2  unit-3  card open, asked by swb-1-conductor"
eq "$(grep -c verify <<<"$b")" "1"
eq "$(line_of "$con" "console-pages")" "✓ switchboard-kit console-pages  swb-2 on $box  no card open"
eq "$(line_of "$con" "page-one")" "    page-one  merged"
lacks "$(line_of "$con" "  b  ")" "http"; lacks "$(line_of "$con" "  b  ")" "server"
ok "each rail row is a marker on its object's line with its card: a verify report, a bolt to land; and a unit with no server shows none"

eq "$(line_of "$con" "board-done")" "! breadboard-kit board-done  brd-1 on $box  landed"
has "$(lane "$b" attention)" "! bolt board-done: every unit has landed on main, and the bolt is still in the plan"
ok "a held bolt whose every unit has landed carries ! on its head, and the attention line names it"

expect_ok crew plan propose "$(proposal 'Case: The console gets a bolt of its own.' 'Do: bolt new console-two "The console, again." --repo switchboard-kit')"
card mac-studio wldn-planner card.post proposal/1 req_prop-1 proposal/1
expect_ok crew board --label wldn; b=$out
eq "$(line_of "$(lane "$b" "Bolt plan")" "proposal 1")" "✓ proposal 1 by $me@mac-studio  The console gets a bolt of its own.  card open, asked by wldn-planner"
ok "an open proposal is listed with its number, who proposed it and its case, its marker saying whose card is open"

ak=$(kit mac-studio willdan atlas-kit)
crew bolt new atlas-maps "Atlas draws maps." --repo atlas-kit >/dev/null
crew unit add map-one "Map one." --bolt atlas-maps >/dev/null
crew bolt give atl-1 atlas-maps >/dev/null 2>&1
change "$ak" map-one 2 2; commit_all "$ak" "feat(map-one): done, on main"
crew bolt land atlas-maps >/dev/null 2>&1
landed=$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"))')
old=$(python3 -c 'import datetime; t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=8); print(t.strftime("%Y-%m-%d"), t.strftime("%Y-%m-%dT%H:%M:%SZ"))')
printf 'Id: old-landing\nAt: %s\nHost: mac-studio\nBy: wldn-ops\nAct: bolt.land\nOn: bolt/old-maps\nOn: unit/old-map\n\n' "${old#* }" \
  >> "$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio/${old% *}.rec"
expect_ok crew board --label wldn; op=$(lane "$out" Operation)
eq "$(grep -c . <<<"$op")" "1"
has "$op" "  atlas-maps  landed "
has "$op" " by $me@mac-studio  atl-1  map-one"
lacks "$op" "old-maps"
ok "Operation lists a bolt landed this week with when, by whom, its team and its units, and not one landed eight days ago"

records() { cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/*/*.rec "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null | wc -l || true; }
before=$(tip); n=$(records)
expect_ok crew board --label wldn
lacks "$out" "crew plan approve"; lacks "$out" "crew unit approve"; lacks "$out" "crew tell"
crew board --label wldn --json >/dev/null; HOST=$box crew board --label wldn >/dev/null
eq "$(tip)" "$before"; eq "$(records)" "$n"
eq "$(git -C "$k" status --porcelain)" ""
ok "the board answers nothing: no approving or telling command in it, the flywheel's branch and the run record as they were"

expect_ok crew board --label wldn --json; json=$out
eq "$(j 'keys | join(" ")')" "from partitions read_at unread"
eq "$(j '.partitions[0] | keys | join(" ")')" "attention bolt_plan construction hosts inception label operation plan teams"
eq "$(j '.partitions[0].plan')" "$(tip)"
eq "$(j '.partitions[0].inception.signals[0] | keys | join(" ")')" "at captured_by first home kind signal teams"
eq "$(j '.partitions[0].inception.explorations[0] | "\(.kit) \(.name)"')" "switchboard-kit command-cost"
eq "$(j '.partitions[0].bolt_plan.proposals[0] | keys | join(" ")')" "by case markers opened proposal teams waiting"
eq "$(j '.partitions[0].bolt_plan.planned[0] | keys | join(" ")')" "bolt goal repo teams units"
eq "$(j '.partitions[0].bolt_plan.queue[0] | keys | join(" ")')" "repo sources teams unit"
te='.partitions[0].construction[] | select(.bolt == "tenant-environments")'
eq "$(j "$te | keys | join(\" \")")" "bolt fixes goal host markers repo state team teams units url"
eq "$(j "$te | .team")" "swb-1"
eq "$(j "$te | .units[0] | keys | join(\" \")")" "markers slot stage tasks unit url worktree"
eq "$(j "$te | .units[] | select(.unit == \"c\") | .markers[0] | \"\(.group) \(.key) \(.glyph) \(.card.by)\"")" "verify verify/c/$stamp ✎ swb-1-conductor"
eq "$(j "$te | .units[] | select(.unit == \"a\") | \"\(.tasks | join(\"/\")) \(.markers | length)\"")" "1/2 0"
eq "$(j "$te | .fixes[0] | keys | join(\" \")")" "fix merged slot url worktree"
eq "$(j '.partitions[0].operation[0] | "\(.bolt) \(.team) \(.units | join(","))"')" "atlas-maps atl-1 map-one"
eq "$(j '.partitions[0].attention[0] | keys | join(" ")')" "name what why"
eq "$(j '.partitions[0].hosts | to_entries | map("\(.key)=\(.value)") | join(" ")')" "$box=true mac-studio=true"
ok "the board's JSON holds each lane's objects, the ledger's team, each marker's group, card key and card, the attention items and the hosts"

# Whose each object is: a held bolt and a landing, its team; a planned bolt, a queued unit, an exploration and a
# proposal for a new bolt, every team building its repository; the user's note and a planner's signals, none; a
# signal a team's agent captured, its team; a proposal adding to a held bolt, the team holding it.
eq "$(j '.partitions[0].teams | map("\(.team) \(.kit) \(.host)") | join("|")')" \
  "swb-1 switchboard-kit $box|swb-2 switchboard-kit $box|brd-1 breadboard-kit $box|atl-1 atlas-kit mac-studio"
eq "$(j "$te | .teams | join(\" \")")" "swb-1"
eq "$(j '.partitions[0].construction[] | select(.bolt == "board-done") | .teams | join(" ")')" "brd-1"
eq "$(j '.partitions[0].operation[0].teams | join(" ")')" "atl-1"
eq "$(j '.partitions[0].bolt_plan.planned[] | select(.bolt == "apex-zones") | .teams | join(" ")')" "swb-1 swb-2"
eq "$(j '.partitions[0].bolt_plan.queue[] | select(.unit == "zone-two") | .teams | join(" ")')" "swb-1 swb-2"
eq "$(j '.partitions[0].inception.explorations[0].teams | join(" ")')" "swb-1 swb-2"
eq "$(j ".partitions[0].inception.signals[] | select(.signal == \"$note\") | .teams | length")" "0"
eq "$(j '[.partitions[0].inception.signals[] | select(.captured_by == "wldn-planner") | .teams | length] | map(tostring) | join(" ")')" "0"
eq "$(j '.partitions[0].bolt_plan.proposals[0].teams | join(" ")')" "swb-1 swb-2"
mkdir -p "$w/signals/2026-10-04-ledger"
printf -- '---\ncapture: 2026-10-04-ledger\nsource: pane\ncaptured_by: swb-1-conductor\nat: 2026-10-04\nsignals: 1\n---\n' > "$w/signals/2026-10-04-ledger/capture.md"
printf -- '---\nsignal: 2026-10-04-ledger/01-heads\nkind: ask\n---\n\nLedgers name their heads.\n' > "$w/signals/2026-10-04-ledger/01-heads.md"
commit_all "$w" "signals: one swb-1's conductor captured"; git -C "$w" push -q origin main
expect_ok crew plan propose "$(proposal 'Case: Tenants get a unit d.' 'Do: unit add d "Unit d." --bolt tenant-environments')"
expect_ok crew board --label wldn --json; json=$out
eq "$(j '.partitions[0].inception.signals[] | select(.signal == "2026-10-04-ledger/01-heads") | .teams | join(" ")')" "swb-1"
eq "$(j '.partitions[0].bolt_plan.proposals[] | select(.proposal == 2) | .teams | join(" ")')" "swb-1"
git -C "$w" rm -rq signals/2026-10-04-ledger; git -C "$w" commit -qm "signals: the ledger capture gone"; git -C "$w" push -q origin main
expect_ok crew plan drop 2 "Not now."
ok "the board's JSON lists the partition's teams with their kits and hosts, and gives each object the teams it belongs to"

echo $box > "$T/down"
expect_ok crew board --label wldn; b=$out
has "$(head -1 <<<"$b")" "read from mac-studio"
has "$(lane "$b" attention)" "! $box did not answer (its kits: "
has "$(lane "$b" attention)" "its run record: "
con=$(lane "$b" Construction)
eq "$(line_of "$con" "tenant-environments  swb-1")" "  switchboard-kit tenant-environments  swb-1 on $box  unknown"
eq "$(line_of "$con" "  a  ")" "    a  unknown"
has "$(lane "$b" "Bolt plan")" "proposal 1"
rm "$T/down"
ok "a host that does not answer is named in the attention line, its ledgers' units from the plan with their stages unknown, and the rest shown"

# The board tab: the rail tab's loop runs crew _views each refresh, one read that prints the rail and writes the
# board's frame; the board tab runs crew _board, which draws the latest frame.
frame=$(home_of mac-studio)/.cache/crew/board/wldn.json
expect_ok crew _board wldn --once
has "$out" "No board for wldn yet: the rail tab's loop writes it each time it refreshes"
has "$out" "close the operator workspace's rail tab and run crew operator up wldn"
[[ ! -e $frame ]] || fail "a board tab wrote a frame"
ok "with no frame, the board tab says the rail tab's loop writes it and how to open both tabs afresh"

# mask: a rail's lines with each row's age left out, since a minute can turn between two reads
mask() { sed -E 's/^(  [0-9]{4}-.{11}  ).{7}/\1AGE    /'; }
expect_ok crew _views wldn; views=$out
expect_ok crew rail --label wldn
has "$views" "verify/c/"; has "$views" "land/console-pages/"
eq "$(tail -n +2 <<<"$views" | mask)" "$(tail -n +2 <<<"$out" | mask)"
eq "$(jq -S 'del(.read_at)' "$frame")" "$(crew board --label wldn --json | jq -S 'del(.read_at)')"
ls -A "$(dirname "$frame")" | grep -v '^wldn.json$' && fail "a temporary frame was left"
ok "one refresh of the rail tab prints what crew rail prints and writes, whole, the board crew board --json prints"

expect_ok crew _board wldn --once; drawn=$out
eq "$(tail -n +2 <<<"$drawn")" "$(crew board --label wldn | tail -n +2)"
lacks "$(head -1 <<<"$drawn")" " ago"
read_at=$(python3 -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
jq --arg t "$read_at" '.read_at = $t' "$frame" > "$frame.new" && mv "$frame.new" "$frame"
expect_ok crew _board wldn --once
has "$(head -1 <<<"$out")" "wldn board, as of $(python3 -c 'import datetime, sys; print(datetime.datetime.fromisoformat(sys.argv[1].replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S"))' "$read_at") (5m ago: the rail tab has not refreshed it since)"
eq "$(tail -n +2 <<<"$out")" "$(tail -n +2 <<<"$drawn")"
printf '{"read_at": ' > "$frame"
expect_ok crew _board wldn --once; has "$out" "No board for wldn yet"
ok "the board tab draws the latest frame as crew board does, a frame read five minutes ago headed with its age, and half a frame as none"

# Shims ahead of the real git and python3 log, per host, each fetch of the state branch and each gather.py run.
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@" that logs <what>> <what>
  printf '#!/usr/bin/env bash\nif %s; then echo "${CREW_TEST_HOST:-?} %s" >> %q; fi\nexec %q "$@"\n' "$2" "$3" "$T/reads.log" "$(command -v "$1")" > "$T/shim/$1"
  chmod +x "$T/shim/$1"
}
shim git '[[ " $* " == *" fetch "*refs/crew/wldn/main* ]]' fetch
shim python3 '[[ ${1:-} == - ]]' gather
reads() { grep -c "^$1 $2\$" "$T/reads.log" || true; }
: > "$T/reads.log"
PATH="$T/shim:$PATH" expect_ok crew _views wldn
eq "$(reads mac-studio fetch) $(reads mac-studio gather) $(reads $box gather) $(reads $box fetch)" "1 1 1 0"
ok "one refresh fetches the state branch once and reads each host's kits once, for the rail and the board"

# A plan that can't be read: the board says so, lists no signal as unmoved, since which are moved can't be known, and
# exits non-zero once it has printed everything else.
st=$T/state; git clone -q -b wldn/main "$ws" "$st"; printf '\nBolt: broken\n' >> "$st/plan.rec"
commit_all "$st" "a plan recfix refuses"; git -C "$st" push -q origin wldn/main
expect_fail "wldn/main of WilldanGroup/crew-state" crew board --label wldn
has "$(lane "$out" attention)" "! the plan, wldn/main of WilldanGroup/crew-state: "
eq "$(lane "$out" Inception)" "  exploration  switchboard-kit command-cost  Reading: what each crew command costs, read 2026-10-01."
eq "$(lane "$out" Construction)" "  none"
ok "a plan that can't be read is named in the attention line, no signal is listed as unmoved, and the exit is non-zero"
