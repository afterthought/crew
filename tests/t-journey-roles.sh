# A partition's main-level roles that run as their kinds, through the crew command on the stubs (tests.11, record
# 0022; record 0047 move 6): with madswan's planner and operator named a stream, a tell to the planner with no
# standing agent of it up is an ask of the role from its sender on madswan's flywheel branch, its role record written in
# the same commit, nothing typed into any pane and one ask entry holding the words' length and never their text, which
# crew trace of the run lists; a send to madswan is an ask of its operator carrying whom it was for; and a tell to wldn's
# planner, which stands, is refused as today with nothing asked. What a tell decides and the ask's fields are logic
# cases (tests/py/test_tell_asks.py, test_asks.py); each step here checks a command's wiring once.
# Reads: plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints afterthought/blueprints >/dev/null; blueprints agentplot/blueprints >/dev/null
crew state init madswan >/dev/null
role_stream madswan planner madswan-main; role_stream madswan operator madswan-main
ms=$(remote afterthought/crew-state)
at() { git --git-dir "$ms" show "madswan/main:$1"; }
asks() { at asks.rec | recsel -t Ask "$@"; }

# A tell to the planner, which runs as its kind with no standing agent up: an ask, nothing typed.
: > "$CREW_TEST_LOG"
t0=$(act_tip madswan/main "$ms")
CREW_AGENT=madswan-design expect_ok crew tell madswan-planner "Record 0053 is accepted ZQXR"
has "$out" "asked madswan-planner"
eq "$(asks -p Role,From,What,Words | tr '\n' ' ')" "Role: planner From: madswan-design What: tell Words: Record 0053 is accepted ZQXR "
eq "$(at roles.rec | recsel -t Role -P Address,Stream,Kind,Name,Intent | tr '\n' ' ')" "madswan/planner madswan-main crew-planner madswan madswan-planner "
eq "$(acts_since "$t0" madswan/main "$ms")" "1"
grep -q "agent prompt" "$CREW_TEST_LOG" && fail "a tell to a role that runs as its kind typed into a pane"
expect_ok crew trace agent/madswan-planner --label madswan
has "$out" "agent/madswan-planner (28 characters)"
[[ $(git --git-dir "$ms" log -p madswan/main -- runs/) != *ZQXR* ]] || fail "an ask's words are in the run record"
ok "a tell to a role that runs as its kind is an ask from its sender with its role record in one commit, typing nothing, and its entry holds no words"

# A send to madswan: an ask of its operator, which runs as its kind, carrying whom it was for.
CREW_AGENT=swancloud-planner expect_ok crew send madswan "The zone check fails"
has "$out" "asked madswan-operator"
eq "$(asks -e "Role = 'operator'" -p From,What,Words | tr '\n' ' ')" "From: swancloud-planner What: send Words: (sent to madswan) The zone check fails "
ok "a send to a partition whose operator runs as its kind is an ask of the operator carrying whom it was for"

# wldn's planner stands: a tell to it, not up, is refused as today, and nothing is asked.
blueprints WilldanGroup/willdan-blueprints >/dev/null; crew state init wldn >/dev/null
CREW_AGENT=madswan-design expect_fail "could not tell wldn-planner on chuck-herdr-alpha: it is not up" crew tell wldn-planner "hello"
git --git-dir "$(remote WilldanGroup/crew-state)" show wldn/main:asks.rec >/dev/null 2>&1 && fail "a tell to a role that stands wrote an ask"
ok "a tell to a role that stands is today's, and asks nothing"
