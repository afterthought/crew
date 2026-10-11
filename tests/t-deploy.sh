# crew deploy: what a kit's deployer asks of crew (plan.14), as swancloud's deployer calls it. An offer of a deploy is
# a rail row whose card is main-level ops's, the same offer again writes nothing and a newer one replaces it; the
# user's word, recorded by crew deploy approve for the offer the rail shows and refused for any other, is what
# crew deploy word answers until that deploy's end is recorded; a deploy's start, steps and end are entries of the run
# record as it runs; an after-deploy step's state is recorded, crew deploy steps gives each one's latest, and a user's
# step that waits is a rail row until it is marked; quiet answers whether the environment's host runs a working stage
# or a test; main-level ops may post a card under an open deploy row's key alone; and a deploy command run away from
# the partition's main level runs there.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints afterthought/blueprints >/dev/null; blueprints WilldanGroup/willdan-blueprints >/dev/null
crew state init swancloud >/dev/null; crew state init wldn >/dev/null
box=chuck-herdr-alpha
s1=$(printf 'a%.0s' $(seq 40)); s2=$(printf 'b%.0s' $(seq 40))
runs() { cat "$(home_of "${1:-mac-studio}")/.local/state/crew/${2:-swancloud}/runs/${1:-mac-studio}"/*.rec 2>/dev/null || true; }
acts() { runs "$@" | grep -c "^Act: $3\$" || true; }
dep() { crew deploy "$@" --label swancloud; }

expect_ok crew deploy --help
has "$out" "usage: crew deploy"
ok "crew deploy answers --help, as the deployer's probe reads it"

expect_ok dep offer mac-studio --from none --to "$s1"
expect_ok dep offer mac-studio --from none --to "$s1"
eq "$(acts mac-studio swancloud deploy.offer)" "1"
expect_ok crew rail --label swancloud
has "$out" "deploy mac-studio (swancloud) to ${s1:0:7}, from nothing deployed: swancloud-ops posts its card"
has "$out" "answer: crew deploy approve mac-studio --to $s1 --label swancloud"
has "$out" "card:   deploy/mac-studio/${s1:0:7}, none open"
ok "an offer is a rail row whose card is main-level ops's, and the same offer again writes nothing"

rc=0; out=$(dep word mac-studio 2>&1) || rc=$?
eq "$rc" "1"; has "$out" "no word is given for a deploy of mac-studio"
expect_fail "the deploy of mac-studio offered is to ${s1:0:7}, not ${s2:0:7}" dep approve mac-studio --to "$s2"
has "$(runs)" "Refused: the deploy of mac-studio offered is to ${s1:0:7}, not ${s2:0:7}"
expect_fail "no deploy of macbook-pro is offered" dep approve macbook-pro --to "$s1"
expect_ok dep approve mac-studio --to "$s1"
has "$out" "the deploy of mac-studio to ${s1:0:7} is approved"
expect_ok dep word mac-studio; eq "$out" "$s1"
expect_ok crew rail --label swancloud; lacks "$out" "deploy mac-studio (swancloud)"
ok "there is no word until the user approves the offer the rail shows, which leaves the rail; another commit's approval is refused and recorded"

expect_ok dep offer mac-studio --from none --to "$s2"
expect_ok dep word mac-studio; eq "$out" "$s1"
expect_ok crew rail --label swancloud; has "$out" "deploy mac-studio (swancloud) to ${s2:0:7}"
echo '[{"name":"deployer","state":"ok","detail":"","before":"warn","verdict":"better"}]' > "$T/rows.json"
expect_ok dep record mac-studio --to "$s1" --act start --from none
expect_ok dep record mac-studio --to "$s1" --act step --step suite --outcome ok --log /tmp/suite.log --rows "$T/rows.json"
expect_ok dep word mac-studio; eq "$out" "$s1"
expect_ok dep record mac-studio --to "$s1" --act end --outcome ok
rc=0; dep word mac-studio >/dev/null 2>&1 || rc=$?; eq "$rc" "1"
has "$(runs)" 'Rows: [{"name":"deployer","state":"ok","detail":"","before":"warn","verdict":"better"}]'
eq "$(acts mac-studio swancloud deploy.start) $(acts mac-studio swancloud deploy.step) $(acts mac-studio swancloud deploy.end)" "1 1 1"
expect_ok crew rail --label swancloud; has "$out" "deploy mac-studio (swancloud) to ${s2:0:7}"
ok "a newer offer waits beside an approved one; a deploy's start, step and end are recorded, and its end ends the word"

printf 'Restart the herdr server\nonce the teams are quiet.\n' > "$T/step.txt"
expect_ok dep step mac-studio --to "$s1" --key restart-herdr/1 --state waiting --doer user --text "$T/step.txt"
expect_ok dep step mac-studio --to "$s1" --key restart-teams/1 --state handed --doer dispatcher --agent swancloud-dispatch-mac-studio --when quiet
expect_ok crew rail --label swancloud
has "$out" "after the deploy of mac-studio (swancloud) to ${s1:0:7}, yours to do: Restart the herdr server once the teams are quiet."
has "$out" "done:   crew deploy step mac-studio --to $s1 --key restart-herdr/1 --state done --label swancloud"
lacks "$out" "restart-teams"
expect_ok dep steps mac-studio --json
eq "$(jq -r '[.[] | "\(.key) \(.state) \(.to[:7])"] | join(", ")' <<<"$out")" "restart-herdr/1 waiting ${s1:0:7}, restart-teams/1 handed ${s1:0:7}"
expect_ok dep step mac-studio --to "$s1" --key restart-herdr/1 --state done --note "restarted at 10:02"
expect_ok dep steps mac-studio --json
eq "$(jq -r '[.[] | "\(.key) \(.state)"] | join(", ")' <<<"$out")" "restart-teams/1 handed, restart-herdr/1 done"
eq "$(jq -r '.[] | select(.key == "restart-herdr/1") | .note' <<<"$out")" "restarted at 10:02"
expect_ok crew rail --label swancloud; lacks "$out" "yours to do"
ok "an after-deploy step's states are recorded, steps gives each one's latest, and a user's waiting step is a rail row until marked"

refusal() { as mac-studio python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import crew, plan
print(plan.card_refusal(crew.load(), sys.argv[2], "swancloud", "post_request", sys.argv[3]))' "$CREW/plugin/lib" "$@"; }
eq "$(refusal swancloud-ops "deploy/mac-studio/${s2:0:7}")" "None"
has "$(refusal swancloud-ops "deploy/mac-studio/${s1:0:7}")" "swancloud-ops posts a card only under a deploy row's key of swancloud open now, deploy/mac-studio/${s2:0:7}"
has "$(refusal swancloud-ops land/x/abcdef1)" "deploy row's key"
ok "main-level ops may post a card under an open deploy row's key, and no other"

expect_ok dep quiet mac-studio
slot=$(home_of mac-studio)/.cache/crew/test-slots/slot-0; mkdir -p "$(dirname "$slot")"
python3 -c 'import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDWR | os.O_CREAT); fcntl.flock(fd, fcntl.LOCK_EX); open(sys.argv[2], "w").close(); time.sleep(600)' \
  "$slot" "$T/held" & holder=$!
held() { [[ -e $T/held ]]; }; until_ok held || fail "the test slot was never held"
rc=0; out=$(dep quiet mac-studio 2>&1) || rc=$?
kill "$holder"; wait "$holder" 2>/dev/null || true
eq "$rc" "1"; has "$out" "1 of crew's tests are running on mac-studio"
p=$(as mac-studio herdr --session wldn-5 workspace create --cwd / --label atl-1 | jq -r .result.root_pane.pane_id)
as mac-studio herdr --session wldn-5 stub agent "$p" atl-1-unit-2 >/dev/null
as mac-studio herdr --session wldn-5 stub status atl-1-unit-2 working >/dev/null
rc=0; out=$(dep quiet mac-studio 2>&1) || rc=$?
eq "$rc" "1"; has "$out" "atl-1-unit-2 is working"
ok "quiet answers whether the host's teams have a stage working or a test running"

expect_ok crew deploy offer "$box" --label wldn --from none --to "$s1"
eq "$(acts "$box" wldn deploy.offer)" "1"
eq "$(acts mac-studio wldn deploy.offer)" "0"
expect_fail "no word is given for a deploy of $box" crew deploy word "$box" --label wldn
ok "a deploy command run away from the partition's main level is run there"

expect_fail "--to nothex is no commit" dep offer mac-studio --from none --to nothex
expect_fail "Bad_Env is no environment's name" dep offer Bad_Env --from none --to "$s1"
expect_fail "no partition nolabel" crew deploy word mac-studio --label nolabel
ok "a commit, an environment or a partition crew can't take is refused"
