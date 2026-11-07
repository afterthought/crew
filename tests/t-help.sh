# A help flag shows a command's usage and acts on nothing (code.11), through the crew command on the stubs (tests.11):
# crew tell <agent> --help prints tell's usage and asks or tells nobody, where it was taken as the words of a tell, as
# main's crew needs --help was on the Willdan box on 2026-11-07 ("It needs: --help"); crew fix <bolt> <name> --help
# launches nothing; every command crew dispatches answers -h or --help among its own arguments with its usage and
# exits 0, with no call to herdr, ssh, sluice or any other tool, no agent started, no entry and no write to the state
# branch; and a word that is not exactly the flag is a word, so crew tell <agent> "--help with ..." is a tell. Which
# parser's usage a Python command's arguments ask for is a logic case (tests/py/test_help.py).
# Reads: plugin/lib/board.py plugin/lib/hold.py plugin/lib/ops.py plugin/lib/page.py plugin/lib/sites.py tests/journeys.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/journeys.sh"
flume_world
role_stream wldn planner wldn-main
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }

# nothing_done <what>: since the last `before`, no tool was called, no agent started, no entry written on either host
# and the state branch did not move
before() { : > "$CREW_TEST_LOG"; launched=$(launches); recorded="$(record_of $box)$(record_of mac-studio)"; tip=$(git --git-dir "$ws" rev-parse wldn/main); }
nothing_done() {
  eq "$(calls)" ""
  [[ $(launches) == "$launched" ]] || fail "$1 started an agent"
  [[ "$(record_of $box)$(record_of mac-studio)" == "$recorded" ]] || fail "$1 wrote the run record"
  eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$tip"
}

before
for flag in --help -h; do
  CREW_AGENT=wldn-design expect_ok crew tell wldn-planner "$flag"
  has "$out" 'crew tell     <agent> "<text>"'
  lacks "$out" "asked wldn-planner"; lacks "$out" "crew send"
done
nothing_done "crew tell --help"
ok "crew tell <agent> --help prints tell's usage and asks or tells nobody: no ask on the state branch, nothing typed, no entry"

before
expect_ok crew fix tenant-environments tidy --help
has "$out" "usage: crew fix"
expect_ok crew fix tenant-environments tidy "The banner flickers." -h
has "$out" "usage: crew fix"
nothing_done "crew fix --help"
ok "crew fix <bolt> <name> --help prints the fix's usage and launches nothing"

# Every command crew dispatches, each with arguments of its own shape before the flag. The list holds every command
# the dispatch in plugin/bin/crew names, so a command added there without a line here fails below.
commands=$(cat <<'EOF'
bolts tenant-environments
bolt start tenant-environments
bolt submit tenant-environments
bolt land tenant-environments
unit add c --bolt tenant-environments
unit drop b
chore add c
kit rename switchboard-kit switchboard
fix tenant-environments tidy --drop
answer tenant-environments--tidy "use the old table"
tell wldn-planner "carry on"
tell --board
send wldn "a word"
signal a-finding "it asserts" --excerpt "the words"
signal move x attach
signal show x
state init wldn
plan approve 3
plan answer x q
rail
card read land/tenant-environments
record switchboard-kit 1 --accepted
role start
role open nobody
events
trace unit/a
page wldn
sites wldn
ops offer dev
board
_views wldn
_board wldn
_rail wldn
_follow
hold chuck-herdr-alpha "a restart"
hold status
go chuck-herdr-alpha
update
_hold set
_go
_update
_renew wldn-planner
_sweep wldn switchboard-kit --dir /k
_preview wldn land/b b bolt/b HEAD
_answered
_card-preview wldn land/b b
_preview-release wldn land/b
_made wldn a
_batch-card wldn 1
_land-row wldn tenant-environments
_land-card wldn switchboard-kit
_landing-read wldn tenant-environments
main up wldn
main fix switchboard-kit red "main is red"
review wldn --wait
review delivered
revive
console up wldn rail
operator up wldn
EOF
)
dispatched=$(sed -n '/^# -* commands$/,/^esac$/p' "$CREW/plugin/bin/crew" | sed -n 's/^  \([a-z_][a-z_ |-]*\)).*/\1/p' | tr '|' '\n' | tr -d ' ')
for c in $dispatched; do
  grep -q "^$c\( \|$\)" <<<"$commands" || fail "crew $c is dispatched and has no line here"
done
before
while IFS= read -r line; do
  eval "set -- $line"
  for flag in --help -h; do
    out=$(crew "$@" "$flag" 2>&1) || fail "crew $line $flag did not exit 0:"$'\n'"$out"
    want="crew $1"; [[ $1 == operator ]] && want="crew console"
    has "$out" "$want"
  done
  nothing_done "crew $line --help"
done <<<"$commands"
expect_ok crew --help; has "$out" 'crew tell     <agent> "<text>"'; has "$out" "crew console  up|down"
expect_ok crew -h; has "$out" "crew bolts [<bolt>]"
expect_ok "$CREW/plugin/bin/crew-role" wldn planner --help
has "$out" "crew-role <label> design|planner|ops|reviewer|operator [resume]"
nothing_done "crew --help"
ok "every command crew dispatches answers -h or --help with its usage and exits 0, calling no tool, starting no agent, writing no entry and moving no branch"

CREW_AGENT=wldn-design expect_ok crew tell wldn-planner "--help with which table holds tenants ZQXN"
has "$out" "asked wldn-planner"
eq "$(git --git-dir "$ws" show wldn/main:asks.rec | recsel -t Ask -P Words | grep ZQXN)" "--help with which table holds tenants ZQXN"
ok "a word that is not exactly -h or --help is a word: crew tell <agent> \"--help with ...\" is a tell, an ask of the planner that runs as its kind"
