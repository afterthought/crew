# Every brief prints for its team or partition with no token left unfilled.
. "$TESTS/lib.sh"
world
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "# You are swb-1-"
  lacks "$out" "fable"; lacks "$out" "explorer"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_fail "no definition 'fable' for a team" crewpy brief swb-1 fable
[[ ! -e $CREW/plugin/roles/fable.md && ! -e $CREW/plugin/roles/explorer.md && ! -e $CREW/plugin/roles/verifier.md ]] || fail "a retired role is still there"
ok "every team brief prints with no unfilled token"

expect_ok crewpy brief swb-1 conductor
for want in "unit approve" "review" "tell wldn-design" "signal" "never by hand" "Don't create tracking files" "`plan/wldn` of WilldanGroup/willdan-blueprints"; do
  has "$out" "$want"
done
ok "the conductor takes units through review, asks the design agent, records signals, and writes the plan only through crew"

for role in design planner dispatcher main-ops; do
  expect_ok crewpy brief wldn $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "of wldn"; lacks "$out" "fable"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_ok crewpy brief wldn design
for want in attach challenge new-territory answered drop "unit add" "tell wldn-planner" "tell <conductor>"; do has "$out" "$want"; done
expect_ok crewpy brief wldn planner
for want in "only agent that creates bolts" "--signal" "Agree any change to it with that bolt's conductor" "plan/wldn"; do has "$out" "$want"; done
has "$out" '`swb-1` builds Switchboard in switchboard-kit'; has "$out" "on mac-studio in session wldn-5"
expect_ok crewpy brief wldn dispatcher
for want in "bolt give <team>" "up <team>" "account ia" "one bolt deploy at a time"; do has "$out" "$want"; done
has "$out" $'The teams here:\n\n- `atl-1` builds Atlas'; has "$out" $'its conductor is `atl-1-conductor`\n\nYou give these teams'
expect_ok crewpy brief wldn main-ops
for want in "wt merge main --no-squash --no-remove" "bolt land <bolt>" "Deploy main"; do has "$out" "$want"; done
expect_fail "no definition 'conductor' for a main level" crewpy brief wldn conductor
ok "every main-level brief prints for wldn with no unfilled token"

expect_ok crewpy brief wldn operator
[[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/operator.md left ${BASH_REMATCH[0]} unfilled"
for want in "bolts --label wldn" "status <team>" "sites wldn" "tell <agent>" '`wldn-planner`' '`wldn-design`' "<team>-conductor" "terminal-browser open <url> --split right"; do has "$out" "$want"; done
HOST=chuck-herdr-alpha expect_ok crewpy brief wldn operator
has "$out" "chuck-herdr-alpha is a box, which can't open the dev.swancloud.net names"; lacks "$out" "terminal-browser open"
ok "the operator brief prints for wldn, opening sites on a Mac and giving the Mac URL on a box"
