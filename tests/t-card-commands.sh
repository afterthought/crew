# crew card post, change, close and read on the stub pendingyou (the rail-cards spec, briefs.16, ADR 0005 as amended
# 2026-10-12), each command's wiring once: a conductor's card posted as the asking assistant through `pendingyou mcp`,
# whoami first, filed in its kit's area made under the kit's key, under the card key with its session, and recorded
# from Pending You's reply; posted again, the same card; a key not the conductor's refused by the card hook's check
# with nothing sent; Pending You's refusal and a host with no sign-in refused in their words, the first recorded; a
# change at the version Pending You reports; the user's answer read; a close by outcome and a withdrawal by reason,
# each recorded; and after the host signs in again, a card read as lost, and posted again under its key. Which card a key names, what crew sets on a card, the area, and how a reply, a refusal and an answer
# read are logic cases (tests/py/test_card_commands.py); whose key and what form, test_cards.py.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
stub=$(home_of $box)/.stub-pendingyou
v1=verify/v1/20261012-1000
entries() {
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$1"
}
# The conductor's worktree: a checkout whose origin is switchboard-kit's on GitHub, where its card commands run.
wd=$T/conductor-work; git init -q "$wd"; git -C "$wd" remote add origin git@github.com:WilldanGroup/switchboard-kit.git
# card <command...>: crew card as swb-1-conductor on the box, in its worktree, standard input passed on
card() { (export CREW_TEST_HOST=$box CREW_AGENT=swb-1-conductor HOME; HOME=$(home_of $box); cd "$wd" && "$CREW/plugin/bin/crew" card "$@"); }
py_calls() { grep " pendingyou " "$CREW_TEST_LOG" | cut -d' ' -f3- || true; }

# The plan, by hand: b1 holds v1, and swb-1 holds b1.
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
p.insert(plan.Rec("Bolt", [("Bolt", "b1"), ("Repo", "switchboard-kit"), ("Goal", "Goal of b1.")]))
p.insert(plan.Rec("Unit", [("Unit", "v1"), ("Repo", "switchboard-kit"), ("Bolt", "b1"), ("Intent", "Unit v1.")]))
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
crew bolt give swb-1 b1 >/dev/null 2>&1

choice='{"kind": "choice", "title": "Which fix for v1?", "summary": "Two findings.", "blocking": false, "urgency": "today",
  "options": [{"id": "a", "label": "Fix both"}, {"id": "b", "label": "Fix the first"}]}'
: > "$CREW_TEST_LOG"
out=$(card post $v1 <<<"$choice")
eq "$out" "card $v1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area create_area post_request "
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "swb-1-conductor"}'
has "$(py_calls | sed -n 2p)" '"remote": "github.com/WilldanGroup/switchboard-kit"'
has "$(py_calls | sed -n 3p)" '"group": "wldn", "idempotencyKey": "create-area:WilldanGroup/switchboard-kit", "name": "switchboard-kit"'
posted=$(py_calls | sed -n 4p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .areaId, .session, .kind, (.options | length)]' <<<"$posted")" \
  "[\"$v1\",\"prj_stub-1\",{\"cwd\":\"$wd\",\"label\":\"swb-1-conductor\",\"machine\":\"$box\"},\"choice\",2]"
eq "$(entries card.post | jq -r '[(.On | join(" ")), .Card, .Key, .By] | join(" ")')" "unit/v1 req_stub-1 $v1 swb-1-conductor"
ok "crew card post posts a conductor's card as it, whoami first, in its kit's area made under the kit's key, under the card key with its session, and records it from Pending You's reply"

: > "$CREW_TEST_LOG"
eq "$(card post $v1 <<<"$choice")" "card $v1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
eq "$(jq 'length' "$stub/cards.json")" "1"
ok "posted again, the card comes back under its key, filed in the area that now matches, and no second card is made"

: > "$CREW_TEST_LOG"
expect_fail "swb-1-conductor posts a card only under a rail row's key of its own" card post proposal/9 <<<"$choice"
eq "$(py_calls)" ""
refused_key=$out
ok "a key that is not the conductor's is refused by the card hook's own check, and nothing reaches Pending You"

echo "post_request Approve requests give their risk in approve.risk." > "$stub/refuse"
expect_fail "Pending You refused post_request: Approve requests give their risk in approve.risk." card post verify/v1/20261012-1100 <<<"$choice"
eq "$(entries card.post | jq -r 'select(.Refused) | [(.On | join(" ")), .Refused] | join(" ")')" \
  "proposal/9 $(sed -n 1p <<<"$refused_key")
unit/v1 Pending You refused post_request: Approve requests give their risk in approve.risk."
: > "$stub/refuse"
touch "$stub/signed-out"
expect_fail "this host can't ask through Pending You: Claude Code on this computer isn’t signed in to Pending You (https://www.pendingyou.com). The user signs it in with pendingyou-signin. Post it again later." \
  card post verify/v1/20261012-1100 <<<"$choice"
lacks "$out" "npx"
mv "$stub/signed-out" "$stub/signed-out.was"
ok "a refusal, crew's or Pending You's in its words, is recorded as the post refused, and a host with no sign-in is refused saying whose it is to sign in, never npx"

: > "$CREW_TEST_LOG"
eq "$(card change $v1 <<<'{"changeNote": "A third option", "options": [{"id": "a", "label": "Fix both"}, {"id": "b", "label": "Fix the first"}, {"id": "c", "label": "Fix neither"}]}')" \
  "card $v1: req_stub-1 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.requestId, .expectedVersion, .name]')" '["req_stub-1",1,"swb-1-conductor"]'
eq "$(entries card.update | jq -r '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/v1 req_stub-1 $v1"
ok "crew card change changes the conductor's card at the version Pending You reports, and records it"

eq "$(card read $v1)" "card $v1: req_stub-1, pending, waiting on the user
  https://www.pendingyou.com/app/r/req_stub-1"
mkdir -p "$stub/answered"; echo '{"answer": {"choiceIds": ["a"], "note": {"text": "Fix both, and add a test."}}}' > "$stub/answered/req_stub-1.json"
eq "$(card read $v1)" "card $v1: req_stub-1, answered, your turn: the user has answered
  picked: a
  note: Fix both, and add a test.
  https://www.pendingyou.com/app/r/req_stub-1"
eq "$(card read $v1 --json | jq -r .version)" "3"
eq "$(entries card.read)" ""
ok "crew card read prints where the card stands, the user's answer and words once they answer, records nothing"

: > "$CREW_TEST_LOG"
eq "$(card close $v1 --outcome "Fixed both, with a test.")" "card $v1: req_stub-1 closed
no session was running for $v1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.expectedVersion, .outcome]')" '[3,"Fixed both, with a test."]'
eq "$(entries card.close | jq -r '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/v1 req_stub-1 $v1"
expect_fail "swb-1-conductor holds no open card under $v1 on $box: post one with crew card post $v1" card read $v1
ok "crew card close acks the answer at its version, records the close, ends no session that was not running, and the key then names no card"

v2=verify/v1/20261012-1200
card post $v2 <<<"$choice" >/dev/null
: > "$CREW_TEST_LOG"
eq "$(card close $v2 --reason "Verify ran again." | head -1)" "card $v2: req_stub-2 withdrawn"
eq "$(py_calls | sed -n 2p)" 'cancel_request {"name": "swb-1-conductor", "reason": "Verify ran again.", "requestId": "req_stub-2"}'
eq "$(entries card.close | jq -r .Card | tr '\n' ' ')" "req_stub-1 req_stub-2 "
ok "crew card close --reason withdraws the card with why, and records it"

# The host signs in to Pending You again: every card posted before reads "not found" to its owner.
v3=verify/v1/20261012-1300
card post $v3 <<<"$choice" >/dev/null
mv "$stub/cards.json" "$stub/cards.before-sign-in.json"
expect_fail "card req_stub-3 under $v3 is lost to its owner (Pending You: \"Not found: request:req_stub-3.\")" card read $v3
has "$out" "post its card again with crew card post $v3, its summary saying an older copy is dead"
eq "$(card post $v3 <<<"$choice")" "card $v3: req_stub-4 https://www.pendingyou.com/app/r/req_stub-4"
eq "$(card read $v3 | head -1)" "card $v3: req_stub-4, pending, waiting on the user"
ok "after the host signs in again a card reads as lost to its owner, saying to post the row's card again, and posted again under its key it is the key's card"
