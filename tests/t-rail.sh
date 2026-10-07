# crew rail: everything that waits on the user, in four groups in order (proposals, review, verify, land), each row
# with when it began to wait, how long ago that was and the commands that answer it, oldest first; read from the plan,
# the proposals, the kits and the run record, and writing nothing. Each scenario of the crew-rail spec, and opening a
# proposal in plannotator with crew plan proposed <n> --open. Each row has its card key and says whether a Pending You
# card is open for it and whose, and an open card whose row is gone is listed with the tell that asks its owner to
# close it, read from the card entries crew's hook writes in the run record.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
crew state init wldn >/dev/null
export CREW_LABEL=wldn
box=chuck-herdr-alpha
tip() { git --git-dir "$ws" rev-parse wldn/main; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
# Times are set, so the rail's are known: at <minutes ago> as git takes it, shown <minutes ago> [format] as the rail
# prints it (or in the format given, such as touch -t's), and commit_at <minutes ago> <dir> <message>.
now=$(date +%s)
at() { echo "@$((now - $1 * 60)) +0000"; }
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "${2:-%Y-%m-%d %H:%M}"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE=$(at "$1") git -C "$2" commit -qm "$3"; }
# group <rail> <heading>: the lines of one group; line_of <text> <words>: the line holding the words
group() { awk -v g="$2" '$0 == g {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$1"; }
line_of() { grep -F -- "$2" <<<"$1" || true; }

expect_ok crew rail --label wldn
has "$out" "What waits on you (wldn), as of "
eq "$(grep -E '^[a-z]+$' <<<"$out" | tr '\n' ' ')" "proposals review verify land "
eq "$(grep -c '^  none$' <<<"$out")" "4"
lacks "$out" "card:"; lacks "$out" "open cards with no row"
ok "with nothing waiting, the four groups are printed in order, each with none"

crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in early late checked stale; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null
crew bolt give swb-2 apex-zones >/dev/null 2>&1
# Two units in review since 3 hours and 1 hour ago.
pe=$(place "$k" tenant-environments early); change "$pe" early 0 2; commit_at 180 "$pe" "docs(early): the change"
pl=$(place "$k" tenant-environments late); change "$pl" late 0 2; commit_at 60 "$pl" "docs(late): the change"
# Two units in verify: checked's newest report came after its last commit, stale's before it.
pc=$(place "$k" tenant-environments checked); change "$pc" checked 2 2; commit_at 120 "$pc" "feat(checked): done"
ps=$(place "$k" tenant-environments stale); change "$ps" stale 2 2; commit_at 50 "$ps" "feat(stale): done again"
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
report() { local f="$reports/verify-$1-$(shown "$2" %Y%m%d-%H%M).md"; touch -t "$(shown "$2" %Y%m%d%H%M.%S)" "$f"; echo "$f"; }
report checked 150 >/dev/null; rc=$(report checked 100); report stale 70 >/dev/null
# A bolt whose only unit merged 30 minutes ago.
pz=$(place "$k" apex-zones zone-one); change "$pz" zone-one 2 2; commit_at 40 "$pz" "feat(zone-one): done"
GIT_COMMITTER_DATE=$(at 30) git -C "$kd/bolts/apex-zones" merge -q --no-ff -m "merge zone-one" unit/zone-one

expect_ok crew rail --label wldn; r=$out
rv=$(group "$r" review)
eq "$(grep -cE '^  [0-9]' <<<"$rv")" "2"
eq "$(grep -oE 'unit [a-z]+ \(wldn\)' <<<"$rv" | tr '\n' ' ')" "unit early (wldn) unit late (wldn) "
has "$(line_of "$rv" "unit early")" "  $(shown 180)  3h 0"
has "$(line_of "$rv" "unit early")" "unit early (wldn), swb-1 on $box"
has "$(line_of "$rv" "unit late")" "  $(shown 60)  1h 0"
has "$rv" "    answer: crew unit approve early --label wldn"
has "$rv" "    answer: crew unit approve late --label wldn"
ok "units in review are listed oldest first, each with its time, its age and the approval that answers it"

has "$rv" "    open:   ssh -t $box plannotator-tui $kd/places/early/openspec/changes/early/"
HOST=$box expect_ok crew rail --label wldn; rb=$out
has "$(group "$rb" review)" "    open:   plannotator-tui herdr open $kd/places/early/openspec/changes/early/"
lacks "$rb" "ssh -t"
eq "$(grep 'answer:' <<<"$rb")" "$(grep 'answer:' <<<"$r")"
ok "a unit's change opens in plannotator beside the rail on the team's host, and over ssh from any other, with the same rows"

vf=$(group "$r" verify)
eq "$(grep -cE '^  [0-9]' <<<"$vf")" "1"
has "$vf" "  $(shown 100)  1h 4"
has "$vf" "unit checked (wldn), swb-1 on $box: report $rc"
has "$vf" "    open:   ssh -t $box plannotator-tui $rc"
has "$vf" "    answer: crew tell swb-1-conductor \"On checked's verify report: \""
lacks "$vf" "stale"
has "$(HOST=$box crew rail --label wldn)" "    open:   plannotator-tui herdr open $rc"
ok "a unit in verify is listed with its newest report while that is newer than its last commit, and not once code commits again"

ld=$(group "$r" land)
eq "$(grep -cE '^  [0-9]' <<<"$ld")" "1"
has "$ld" "  $(shown 30)  3"
has "$ld" "bolt apex-zones (wldn), swb-2 on $box: every unit merged; wldn-ops lands it"
has "$ld" "    answer: crew tell wldn-ops \"Land bolt apex-zones.\""
ok "a bolt whose every unit has merged waits to land, timed by its last merge, with the tell that asks ops to land it"

expect_ok crew plan propose "$(proposal 'Case: The console gets a bolt of its own.' 'Do: bolt new console-pages "The console lists them." --repo switchboard-kit')"
expect_ok crew rail --label wldn; pr=$(group "$out" proposals)
grep -qE "^  $(date +%Y-%m-%d) [0-9]{2}:[0-9]{2}  (<1m|[0-9]m) +proposal 1 \(wldn\), by $me@mac-studio: The console gets a bolt of its own\.$" <<<"$pr" \
  || fail "proposal 1 is not timed by its entry in the run record:"$'\n'"$pr"
lacks "$pr" "still needs"
has "$pr" "    read:   crew plan proposed 1 --label wldn"
has "$pr" "    open:   crew plan proposed 1 --label wldn --open"
has "$pr" "    answer: crew plan approve 1 --label wldn"
ok "an open proposal is listed at the time it was proposed, with the commands that print it, open it and approve it"

expect_ok crew plan propose "$(proposal 'Case: The late unit goes first.' 'Do: unit order late --first')"
rm "$(home_of mac-studio)"/.local/state/crew/wldn/runs/mac-studio/*.rec  # proposal 2's entry, never carried
expect_ok crew rail --label wldn; pr=$(group "$out" proposals)
grep -qE "^  $(date +%Y-%m-%d) {8}[<0-9]" <<<"$(line_of "$pr" "proposal 2 (wldn)")" || fail "proposal 2 is not timed by its Opened date:"$'\n'"$pr"
eq "$(grep -A1 -F "proposal 2 (wldn)" <<<"$pr" | tail -1 | sed 's/^ *//')" "still needs the agreement of swb-1-conductor"
grep -qE "^  $(date +%Y-%m-%d) [0-9]{2}:[0-9]{2} " <<<"$(line_of "$pr" "proposal 1 (wldn)")" || fail "proposal 1 lost its time:"$'\n'"$pr"
ok "a proposal whose entry can't be found is timed by its Opened date, and one touching a held bolt names the conductor it waits on"

before=$(tip); f=$(home_of mac-studio)/.local/state/crew/proposals/wldn-1.md
: > "$CREW_TEST_LOG"
HERDR_ENV=1 expect_ok crew plan proposed 1 --label wldn --open
eq "$(cat "$f")" "$(crew plan proposed 1 --label wldn)"
grep -qx "mac-studio plannotator-tui herdr open $f" "$CREW_TEST_LOG" || fail "plannotator did not open $f beside the caller:"$'\n'"$(calls)"
: > "$CREW_TEST_LOG"
expect_ok crew plan proposed 1 --label wldn --open
grep -qx "mac-studio plannotator-tui $f" "$CREW_TEST_LOG" || fail "plannotator did not open $f inline:"$'\n'"$(calls)"
expect_fail "--open needs a proposal's number" crew plan proposed --open
expect_fail "--json" crew plan proposed 1 --label wldn --open --json
eq "$(tip)" "$before"
ok "a proposal opens in plannotator, beside the caller in herdr and inline elsewhere, from a file holding what crew plan proposed prints"

# card <host> <agent> <act> <object> <card> [key]: a card entry, written as crew's hook writes it, on the owner's host
card() { CREW_AGENT=$2 as "$1" python3 "$CREW/plugin/lib/record.py" emit --label wldn --act "$3" --on "$4" --field "Card=$5" ${6:+--field "Key=$6"} >/dev/null; }
he=$(git -C "$pe" rev-parse --short=7 HEAD); hl=$(git -C "$pl" rev-parse --short=7 HEAD)
: > "$CREW_TEST_LOG"
expect_ok crew rail --label wldn; r=$out
eq "$(grep -c 'runs/\*/\*.rec' "$CREW_TEST_LOG")" "1"
eq "$(grep -A4 -F "proposal 1 (wldn)" <<<"$r" | tail -1)" "    card:   proposal/1, none open"
has "$(group "$r" proposals)" "    card:   proposal/2, none open"
eq "$(grep -A3 -F "unit early (wldn)" <<<"$r" | tail -1)" "    card:   review/early/$he, none open"
has "$(group "$r" review)" "    card:   review/late/$hl, none open"
has "$(group "$r" verify)" "    card:   verify/checked/$(shown 100 %Y%m%d-%H%M), none open"
eq "$(grep -A2 -F "bolt apex-zones (wldn)" <<<"$r" | tail -1)" "    card:   land/apex-zones, none open"
eq "$(grep -c '^    card:   ' <<<"$r")" "6"
lacks "$r" "open cards with no row"
ok "every row has its card key, after its commands: a proposal's number, a review's head, a verify report's stamp, a bolt's name"

card $box swb-1-conductor card.post unit/early req_rev-1 "review/early/$he"
has "$(group "$(crew rail --label wldn)" review)" "    card:   review/early/$he, open, asked by swb-1-conductor"
card $box swb-1-conductor card.close unit/early req_rev-1 "review/early/$he"
has "$(group "$(crew rail --label wldn)" review)" "    card:   review/early/$he, none open"
card $box swb-1-conductor card.post unit/early req_rev-2 "review/early/$he"
card mac-studio wldn-planner card.post proposal/1 req_prop-1 proposal/1
expect_ok crew rail --label wldn; r=$out
has "$(group "$r" review)" "    card:   review/early/$he, open, asked by swb-1-conductor"
has "$(group "$r" proposals)" "    card:   proposal/1, open, asked by wldn-planner"
has "$(group "$r" proposals)" "    card:   proposal/2, none open"
lacks "$r" "open cards with no row"
ok "a row's card is open from its post until its close, and names who asked it"

card $box swb-1-conductor card.post unit/late req_old-1 review/late/0000000
expect_ok crew rail --label wldn; r=$out
has "$(group "$r" review)" "    card:   review/late/$hl, none open"
stray=$(awk '$0 == "open cards with no row:" {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$r")
eq "$(grep -cE '^  [0-9]' <<<"$stray")" "1"
grep -qE "^  $(date +%Y-%m-%d) [0-9]{2}:[0-9]{2}  (<1m|[0-9]m) +review/late/0000000 \(wldn\), asked by swb-1-conductor on $box$" <<<"$stray" \
  || fail "the card keyed for an older head is not listed:"$'\n'"$r"
has "$stray" '    answer: crew tell swb-1-conductor "Close your Pending You card review/late/0000000: its row is gone."'
ok "a card keyed for an older head has no row, and is listed after the groups with the tell that asks its owner to close it"

crew unit approve early --label wldn >/dev/null
expect_ok crew rail --label wldn
lacks "$(group "$out" review)" "unit early"; has "$(group "$out" review)" "unit late"
stray=$(awk '$0 == "open cards with no row:" {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$out")
eq "$(grep -oE '  review/[a-z]+/[0-9a-f]+ ' <<<"$stray" | tr -d ' ' | tr '\n' ' ')" "review/early/$he review/late/0000000 "
has "$stray" "    answer: crew tell swb-1-conductor \"Close your Pending You card review/early/$he: its row is gone.\""
ok "a unit approved leaves the list at the next read, and a card its conductor left open is listed as one with no row"

records() { cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/*/*.rec "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null | wc -l || true; }
before=$(tip); n=$(records)
crew rail --label wldn >/dev/null; HOST=$box crew rail --label wldn >/dev/null; crew rail >/dev/null
eq "$(tip)" "$before"; eq "$(records)" "$n"
ok "the rail writes nothing: the flywheel's branch and the run record are as they were"

HOST=$box crew events --push --label wldn >/dev/null  # the box's cards, on the branch the rail reads with the box down
card mac-studio atl-1-conductor card.post agent/atl-1-conductor req_free-1
echo $box > "$T/down"
expect_ok crew rail --label wldn
stray=$(awk '$0 == "open cards with no row:" {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$out")
lacks "$stray" "review/"
has "$stray" "an unkeyed card (wldn), asked by atl-1-conductor on mac-studio"
has "$stray" '    answer: crew tell atl-1-conductor "Close your Pending You card req_free-1: its row is gone."'
has "$(group "$out" proposals)" "    card:   proposal/1, open, asked by wldn-planner"
has "$(group "$out" proposals)" "proposal 1 (wldn)"
has "$out" "$box did not answer"; has "$out" "its units and bolts may also wait on you"
eq "$(grep -c '^  none$' <<<"$out")" "3"
rm "$T/down"
ok "a host that does not answer is named, the proposals and their cards are still listed, a stray card of its teams is not, and the exit is zero"
