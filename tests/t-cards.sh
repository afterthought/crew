# crew records its agents' Pending You cards: the run record takes a card's id (Card) and its rail row's key (Key),
# in a day's file begun before those fields were allowed as well as after, and carries both to the branch.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
ws=$(remote WilldanGroup/crew-state)
day=$(date -u +%F)
runs=$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio
emit() { as mac-studio python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@"; }

# A day's file begun under the descriptor from before Card and Key, as a host that ran an older crew today has it.
mkdir -p "$runs"
as mac-studio python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import record
sys.stdout.write(record.DESCRIPTOR.replace(" Card Key\n", "\n"))' "$CREW/plugin/lib" > "$runs/$day.rec"
lacks "$(cat "$runs/$day.rec")" "Card"
crew state init wldn >/dev/null
CREW_AGENT=swb-1-conductor CREW_LABEL=wldn emit --act card.post --on unit/x --field Card=req_old-1 --field Key=review/x/abc1234 >/dev/null
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key,On "$runs/$day.rec")" $'req_old-1\nreview/x/abc1234\nunit/x'
expect_ok crew events --push --label wldn
carried=$(git --git-dir "$ws" show "wldn/main:runs/mac-studio/$day.rec")
printf '%s\n' "$carried" > "$T/carried.rec"
recfix --check "$T/carried.rec" || fail "the carried file fails recfix --check"
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key "$T/carried.rec")" $'req_old-1\nreview/x/abc1234'
has "$(crew events --label wldn)" "card.post     swb-1-conductor"
has "$(crew events --label wldn)" "unit/x (card review/x/abc1234 req_old-1)"
ok "a day's file begun before Card and Key takes an entry with them, and is carried under the descriptor that allows them"

rm "$runs/$day.rec"
CREW_AGENT=swb-1-conductor CREW_LABEL=wldn emit --act card.post --on unit/y --field Card=req_new-1 --field Key=review/y/def5678 >/dev/null
recfix --check "$runs/$day.rec" || fail "a new day's file fails recfix --check"
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key "$runs/$day.rec")" $'req_new-1\nreview/y/def5678'
ok "a day's file begun now allows Card and Key"
