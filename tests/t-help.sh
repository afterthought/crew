# A help flag shows a command's usage and acts on nothing (code.11), through the crew command on the stubs (tests.11):
# crew needs --help run by a stage's agent leaves its stage begun, records nothing and tells nobody, as atl-1's coder's
# did not on 2026-11-07 ("It needs: --help"); crew fix <team> <name> --help and crew unit run <unit> code --help start
# nothing; every command crew dispatches answers -h or --help among its own arguments with its usage and exits 0, with
# no call to herdr, ssh, sluice or any other tool, no agent started, no entry and no write to the state branch; and a
# word that is not exactly the flag is a word, so crew needs "--help with ..." ends its stage as any needs does.
# Which parser's usage a Python command's arguments ask for is a logic case (tests/py/test_help.py).
# Reads: plugin/hooks/ plugin/lib/board.py plugin/lib/hold.py plugin/lib/ops.py plugin/lib/page.py plugin/lib/sites.py tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "ab"]'
export CREW_AGENT=swb-1-conductor
expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct"

# nothing_done <what>: since the last `before`, no tool was called, no agent started, no entry written on either host
# and the state branch did not move
before() { : > "$CREW_TEST_LOG"; launched=$(launches); recorded="$(record_of $box)$(record_of mac-studio)"; tip=$(git --git-dir "$ws" rev-parse wldn/main); staged=$(cat "$stages"); }
nothing_done() {
  eq "$(calls)" ""
  [[ $(launches) == "$launched" ]] || fail "$1 started an agent"
  [[ "$(record_of $box)$(record_of mac-studio)" == "$recorded" ]] || fail "$1 wrote the run record"
  eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$tip"
  [[ $(cat "$stages") == "$staged" ]] || fail "$1 changed the team's stages"
}

before
for flag in --help -h; do
  HOST=$box CREW_AGENT=swb-1-unit-1 expect_ok crew needs "$flag"
  has "$out" 'crew needs   "<what you need>"'
  lacks "$out" "is ended, stopped short"
done
nothing_done "crew needs --help"
eq "$(field $box stage.end Ended stage/a/construct)" ""
eq "$(told swb-1-conductor)" ""
has "$(cat "$stages")" "unit-1 a construct "
[[ -n $(pane swb-1-unit-1) ]] || fail "crew needs --help ended the stage's agent"
ok "crew needs --help run by a stage's agent prints its usage, and its stage stays begun: nothing recorded, nobody told, its agent left running"

fb=fix/tenant-environments/tidy fp=$kd/places/fix-tenant-environments--tidy
before
expect_ok crew fix swb-1 tidy --help
has "$out" 'crew fix     <team> <name> "<what is wrong>" [--bolt <bolt>]'
has "$out" "crew fix     <team> <name> --merge"
expect_ok crew fix swb-1 tidy "The banner flickers." -h
has "$out" 'crew fix     <team> <name> "<what is wrong>"'
nothing_done "crew fix --help"
[[ ! -e $fp ]] || fail "crew fix --help made the fix's place"
git -C "$k" show-ref --verify --quiet "refs/heads/$fb" && fail "crew fix --help made the fix's branch"
ok "crew fix <team> <name> --help prints the fix's usage and starts nothing"

before
expect_ok crew unit run b code --help
has "$out" 'crew unit run <unit> construct|code|verify|settle|merge ["<words>"]'
lacks "$out" "crew fix"
nothing_done "crew unit run --help"
[[ ! -e $kd/places/b ]] || fail "crew unit run --help made b's place"
ok "crew unit run <unit> code --help prints the stage's usage and starts nothing"

# Every command crew dispatches, each with arguments of its own shape before the flag. The list holds every command
# the dispatch in plugin/bin/crew names, so a command added there without a line here fails below.
commands=$(cat <<'EOF'
list
status swb-1
status
up swb-1
close swb-1
rebuild swb-1
down swb-1
restart swb-1 conductor
resume swb-1 ops
clear swb-1 conductor
unit free b
unit wait b
unit run b construct "Name the tenant."
unit add c --bolt tenant-environments
unit drop b
chore run c code
chore wait c
chore free c
chore add c
fix swb-1 tidy --merge
fix swb-1 tidy --drop
fix swb-1 tidy --wait
needs "I tried the table"
answer tenant-environments--tidy "use the old table"
tell swb-1-conductor "carry on"
tell --board
send wldn "a word"
bolts tenant-environments
bolt give swb-1
bolt submit tenant-environments
bolt land tenant-environments
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
_renew swb-1-conductor
_end-short swb-1 unit-1
_tidy swb-1
_construct-again swb-1 a --by proposal
_preview wldn land/b b bolt/b HEAD
_answered
_card-preview wldn land/b b swb-1
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
_dispatch up wldn
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
expect_ok crew --help; has "$out" "crew needs   \"<what you need>\""; has "$out" "crew console  up|down"
expect_ok crew -h; has "$out" "crew list"
expect_ok "$CREW/plugin/bin/crew-role" swb-1 conductor --help
has "$out" "crew-role <team> conductor|ops [resume]"
nothing_done "crew --help"
ok "every command crew dispatches answers -h or --help with its usage and exits 0, calling no tool, starting no agent, writing no entry and moving no branch"

: > "$CREW_TEST_LOG"
HOST=$box CREW_AGENT=swb-1-unit-1 expect_ok crew needs "--help with which table holds tenants ZQXN"
has "$out" "construct on a is ended, stopped short"
has "$(told swb-1-conductor)" "It needs: --help with which table holds tenants ZQXN"
eq "$(field $box stage.end Ended stage/a/construct)" "short"
ok "a word that is not exactly -h or --help is a word: crew needs \"--help with ...\" ends its stage and tells the conductor"
