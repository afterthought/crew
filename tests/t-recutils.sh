# Every plan command checks for recutils first, and names the package when it is missing.
. "$TESTS/lib.sh"
world
for c in "bolts" "bolt give swb-1" "plan init WilldanGroup/willdan-blueprints wldn"; do
  expect_fail "install the recutils package" env PATH="$(path_without recsel)" bash -c "$(declare -f as crew home_of); $(declare -p CREW T); HOST=$HOST crew $c"
  has "$out" "recsel is not on PATH"
done
ok "plan commands name recutils when recsel is missing"
