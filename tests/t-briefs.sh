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
