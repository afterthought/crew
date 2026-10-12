# crew records its agents' Pending You cards: the run record takes a card's id (Card) and its rail row's key (Key),
# in a day's file begun before those fields were allowed as well as after, and carries both to the branch. crew's
# PostToolUse hook writes an entry for each card a crew agent posts, updates, withdraws or closes, naming its row, its
# card and its key and nothing written on the card, from each shape of a tool's result; a card with no row key is on
# its agent. An error, another server's tool and a session crew didn't start write nothing; a session herdr resumed is
# known by what session-start recorded; and the hook never fails a tool call. A keyed card's withdrawal or close ends
# the plannotator session crew started for its key; an unkeyed card's ends nothing, nor does a key's close end a
# session crew did not start, and a card posted under a key that is no longer a row's closes under it. When
# plannotator's list can't be read, a withdrawal ends nothing, keeps the key's session and tells the agent so. Run as
# `cards --before`, before a card is posted or an area made, the hook refuses a crew agent's card under any key but a
# rail row's of its own, the planner's open proposal or batch card or its conductor's bolt and units, and an area under
# any key but create-area: and a kit of its own, naming the key to use; a team's ops and slots and the main level's
# other agents own no card key; a call crew can't check is refused naming what it could not read; and a session crew
# didn't start, another server's tool and the other card tools are not checked for their key. Each refusal scenario of
# the rail-cards spec. A row's card of the agent's own, posted or changed, the hook then refuses in another form than
# its row's, naming the form: a landing card that is a step, not high stakes, or has options or a step that lands it; a
# verify card with no options; a proposal card not as `crew plan card` prints it, checked against the proposal: one
# that makes no unit new to a bolt is an approval with no options, steps or questions, and one with new units asks
# `plan` and its new units each once, a lone one as a choice, never a text question, so a card missing a unit, asking
# for words, or posted as a plain approval is refused, and so is one for a proposal crew can't draw; and a change that
# clears a landing's high stakes or gives a card options or steps its row's has not; a batch card's form is not checked. A card under no row's key is refused for its key, not its form; a change to a card posted on no row's
# key here, a session crew didn't start and another server's tool pass unchecked; what it can't check, its own input
# among it, is refused, while the record half never fails.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
ws=$(remote WilldanGroup/crew-state)
day=$(date -u +%F)
runs=$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio
emit() { as mac-studio python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@"; }

# A day's file begun under the descriptor from before Card and Key, as a host that ran an older crew today has it.
mkdir -p "$runs"
as mac-studio python3 -c 'import re, sys; sys.path.insert(0, sys.argv[1]); import record
sys.stdout.write(re.sub(r" Card Key[^\n]*\n", "\n", record.DESCRIPTOR))' "$CREW/plugin/lib" > "$runs/$day.rec"
lacks "$(cat "$runs/$day.rec")" "Card"
crew state init wldn >/dev/null
CREW_AGENT=swb-1-conductor CREW_LABEL=wldn emit --act card.post --on unit/x --field Card=req_old-1 --field Key=verify/x/20261007-1400 >/dev/null
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key,On "$runs/$day.rec")" $'req_old-1\nverify/x/20261007-1400\nunit/x'
expect_ok crew events --push --label wldn
carried=$(git --git-dir "$ws" show "wldn/main:runs/mac-studio/$day.rec")
printf '%s\n' "$carried" > "$T/carried.rec"
recfix --check "$T/carried.rec" || fail "the carried file fails recfix --check"
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key "$T/carried.rec")" $'req_old-1\nverify/x/20261007-1400'
has "$(crew events --label wldn)" "card.post     swb-1-conductor"
has "$(crew events --label wldn)" "unit/x (card verify/x/20261007-1400 req_old-1)"
ok "a day's file begun before Card and Key takes an entry with them, and is carried under the descriptor that allows them"

rm "$runs/$day.rec"
CREW_AGENT=swb-1-conductor CREW_LABEL=wldn emit --act card.post --on unit/y --field Card=req_new-1 --field Key=verify/y/20261007-1500 >/dev/null
recfix --check "$runs/$day.rec" || fail "a new day's file fails recfix --check"
eq "$(recsel -t Entry -e "Act = 'card.post'" -P Card,Key "$runs/$day.rec")" $'req_new-1\nverify/y/20261007-1500'
ok "a day's file begun now allows Card and Key"

# The hook, fed as Claude Code feeds it after a Pending You tool.
rm "$runs/$day.rec"
cards() { as mac-studio python3 "$CREW/plugin/hooks/cards"; }
# call <server> <tool> <input> <response> [session]: the hook's input for one tool call
call() { jq -nc --arg t "mcp__$1__$2" --argjson i "$3" --argjson r "$4" --arg s "${5:-sid-1}" \
  '{session_id: $s, hook_event_name: "PostToolUse", cwd: "/work", tool_name: $t, tool_input: $i, tool_response: $r}'; }
# entries [act]: the card entries on mac-studio, one JSON object per line
entries() {
  as mac-studio python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"].startswith("card.") and e["Act"].startswith(sys.argv[2]):
            print(json.dumps(e))' "$CREW/plugin/lib" "${1:-card.}"
}
pick() { entries "$1" | tail -1 | jq -r "$2"; }
export CREW_AGENT=swb-1-conductor CREW_LABEL=wldn
asked='{"name": "swb-1-conductor", "title": "Review x ZQXTITLE", "summary": "ZQXSUMMARY", "options": [{"label": "ZQXOPTION"}], "areaId": "area_1"}'
post() { jq -c --arg k "$1" '. + {idempotencyKey: $k}' <<<"$asked"; }

call pendingyou post_request "$(post verify/x/20261007-1400)" \
  '{"content": [{"type": "text", "text": "Posted."}], "structuredContent": {"requestId": "req_abc-1", "status": "pending", "version": 1}}' | cards
eq "$(pick card.post '[.Act, .By, .Session, (.On | join(" ")), .Card, .Key] | join(" ")')" \
  "card.post swb-1-conductor mac-studio:sid-1 unit/x req_abc-1 verify/x/20261007-1400"
call pendingyou post_request "$(post verify/x/20261007-1412)" \
  '[{"type": "text", "text": "{\"requestId\": \"req_abc-2\", \"status\": \"pending\", \"version\": 1}"}]' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/x req_abc-2 verify/x/20261007-1412"
call plugin_pendingyou_pendingyou post_request "$(post land/tenant-environments/abc1234)" \
  '{"content": [{"type": "text", "text": "not json"}, {"type": "text", "text": "{\"requestId\": \"req_abc-3\", \"version\": 1}"}]}' | cards
call pendingyou post_request "$(post proposal/4)" '{"structuredContent": {"requestId": "req_abc-4"}}' | cards
eq "$(entries card.post | jq -r '"\(.On[0]) \(.Card) \(.Key)"' | tail -2 | tr '\n' ' ')" \
  "bolt/tenant-environments req_abc-3 land/tenant-environments/abc1234 proposal/4 req_abc-4 proposal/4 "
call pendingyou post_request "$(post batch/3-2)" '{"structuredContent": {"requestId": "req_abc-12"}}' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, .Key] | join(" ")')" "batch/3 req_abc-12 batch/3-2"
# As Claude Code 2.1.292 gives Pending You's result: the text alone, a string of JSON.
call pendingyou post_request "$(post verify/y/20261007-1500)" \
  '"{\"requestId\":\"req_5de3dad46fba41068fba\",\"threadId\":\"req_5de3dad46fba41068fba\",\"status\":\"pending\",\"version\":1}"' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/y req_5de3dad46fba41068fba verify/y/20261007-1500"
ok "a post's entry names its row, its card and its key, a batch card's its batch, from structuredContent, a text block of JSON, a plain string of JSON, or a plugin's server"

call pendingyou update_request '{"name": "swb-1-conductor", "requestId": "req_abc-1", "title": "ZQXTITLE again"}' \
  '{"structuredContent": {"requestId": "req_abc-1", "status": "pending", "version": 2}}' | cards
eq "$(pick card.update '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/x req_abc-1 verify/x/20261007-1400"
call pendingyou ack_answer '{"name": "swb-1-conductor", "requestId": "req_abc-1", "version": 2, "outcome": "ZQXOUTCOME"}' \
  '{"structuredContent": {"status": "resolved"}}' | cards
eq "$(pick card.close '[.By, (.On | join(" ")), .Card, .Key] | join(" ")')" "swb-1-conductor unit/x req_abc-1 verify/x/20261007-1400"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_abc-3", "reason": "ZQXREASON"}' \
  '[{"type": "text", "text": "{\"status\": \"cancelled\"}"}]' | cards
eq "$(pick card.close '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/tenant-environments req_abc-3 land/tenant-environments/abc1234"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_elsewhere-9"}' '{"structuredContent": {"status": "cancelled"}}' | cards
eq "$(pick card.close '[(.On | join(" ")), .Card, (.Key // "")] | join(" ")')" "agent/swb-1-conductor req_elsewhere-9 "
ok "an update, an answer acknowledged and a card withdrawn name the card and the row and key of its post; a card posted elsewhere is on its agent"

call pendingyou post_request "$(post 'my own key ZQXKEY')" '{"structuredContent": {"requestId": "req_abc-5"}}' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, (.Key // "-")] | join(" ")')" "agent/swb-1-conductor req_abc-5 -"
call pendingyou post_request "$(post land/tenant-environments)" '{"structuredContent": {"requestId": "req_abc-10"}}' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, (.Key // "-")] | join(" ")')" "agent/swb-1-conductor req_abc-10 -"
call pendingyou post_request "$(post review/x/abc1234)" '{"structuredContent": {"requestId": "req_abc-11"}}' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, (.Key // "-")] | join(" ")')" "agent/swb-1-conductor req_abc-11 -"
call pendingyou post_request "$(post verify/x/20261007-1400)" '{"content": [{"type": "text", "text": "Posted."}]}' | cards
eq "$(pick card.post '[(.On | join(" ")), (.Card // "-"), .Key] | join(" ")')" "unit/x - verify/x/20261007-1400"
recfix --check "$runs/$day.rec" || fail "the hook's entries fail recfix --check"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
ok "an unkeyed card, one under a bolt's bare land/<bolt> or under a review's key, which is no row's, is on its agent with no Key, a result with no id is a post with no Card, and nothing written on a card is recorded"

# A landing card posted under the bare land/<bolt> by a crew from before landings were keyed by the bolt's head.
emit --act card.post --on bolt/tenant-environments --field Card=req_old-1 --field Key=land/tenant-environments >/dev/null
expect_ok cards <<<"$(call pendingyou ack_answer '{"requestId": "req_old-1", "outcome": "landed"}' '{"structuredContent": {"status": "resolved"}}')"
lacks "$out" "crew cards:"
eq "$(pick card.close '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/tenant-environments req_old-1 land/tenant-environments"
ok "a card posted under a key that is no longer a row's is closed under the key and row of its post, with no session to end"

n=$(entries | wc -l)
call pendingyou post_request "$(post verify/x/20261007-1400)" '{"isError": true, "content": [{"type": "text", "text": "refused"}]}' | cards
call pendingyou ack_answer '{"requestId": "req_abc-2"}' '{"deny": "not yours"}' | cards
call github post_request "$(post verify/x/20261007-1400)" '{"structuredContent": {"requestId": "req_abc-6"}}' | cards
call pendingyou get_request '{"requestId": "req_abc-2"}' '{"structuredContent": {"requestId": "req_abc-2"}}' | cards
CREW_AGENT= CREW_LABEL= cards <<<"$(call pendingyou post_request "$(post verify/x/20261007-1400)" '{"structuredContent": {"requestId": "req_abc-7"}}' sid-none)"
eq "$(entries | wc -l)" "$n"
ok "an error, a denial, another server's tool, a read and a session crew didn't start write nothing"

echo '{"session_id": "sid-9", "source": "startup", "cwd": "/work"}' | as mac-studio python3 "$CREW/plugin/hooks/session-start"
CREW_AGENT= CREW_LABEL= cards <<<"$(call pendingyou post_request "$(post proposal/5)" '{"structuredContent": {"requestId": "req_abc-8"}}' sid-9)"
eq "$(pick card.post '[.By, .Session, .Card, .Key] | join(" ")')" "swb-1-conductor mac-studio:sid-9 req_abc-8 proposal/5"
ok "a session herdr resumed without crew's environment is known by what session-start recorded of it"

expect_ok bash -c "echo 'not json' | CREW_TEST_HOST=mac-studio python3 '$CREW/plugin/hooks/cards'"
has "$out" "crew cards:"
expect_ok bash -c "echo 'not json' | CREW_TEST_HOST=mac-studio python3 '$CREW/plugin/hooks/cards' 2>/dev/null"
eq "$out" ""
n=$(entries | wc -l)
chmod 444 "$runs/$day.rec"
expect_ok cards <<<"$(call pendingyou post_request "$(post proposal/6)" '{"structuredContent": {"requestId": "req_abc-9"}}')"
has "$out" "crew: the run record at $runs/$day.rec could not be written"
chmod 644 "$runs/$day.rec"
eq "$(entries | wc -l)" "$n"
hooks=$(jq -c '.hooks.PostToolUse[0] | [.matcher, .hooks[0].command, .hooks[0].timeout]' "$CREW/plugin/hooks/hooks.json")
eq "$hooks" '["mcp__.*__(post_request|update_request|cancel_request|ack_answer)","python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/cards\"",10]'
ok "input the hook can't read, or a record it can't write, is said and the tool call goes on; the plugin runs it after the four card tools"

# The plannotator session crew card session leaves for a key on mac-studio: session <key> starts a stub plannotator on
# a document of its own and records it as crew does; by_hand starts one crew did not; gone <pid> waits for it to end.
cardsdir=$(home_of mac-studio)/.local/state/crew/cards/wldn
started() {  # started <doc> <result file>: a stub plannotator on the document, in the background; prints its pid once listed
  (export CREW_TEST_HOST=mac-studio HOME=$(home_of mac-studio) PLANNOTATOR_SKIP_BROWSER_OPEN=1 PLANNOTATOR_URL_HOST=auto
   cd "$HOME" && exec plannotator annotate "$1" --gate --json --result-file "$2" >/dev/null 2>&1 </dev/null) &
  local pid=$!
  python3 -c 'import os, sys, time
f, give_up = sys.argv[1], time.monotonic() + 5
while not os.path.exists(f):
    time.sleep(0.05)
    if time.monotonic() > give_up:
        sys.exit("plannotator never listed " + f)' "$(home_of mac-studio)/.stub-plannotator/$pid.json"
  echo "$pid"
}
session() {
  local d=$cardsdir/$1 doc=$T/doc-${1//\//-}.md pid
  mkdir -p "$d"; echo "# $1" > "$doc"
  pid=$(started "$doc" "$d/result.json")
  jq -nc --argjson p "$pid" --arg d "$doc" '{pid: $p, document: $d, url: "http://mac-studio.ts.swancloud.net:19432", started: "2026-10-09T12:00:00Z"}' > "$d/session.json"
  echo "$pid"
}
up() { kill -0 "$1" 2>/dev/null; }
gone() { python3 -c 'import os, sys, time
pid, give_up = int(sys.argv[1]), time.monotonic() + 5
while True:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        break
    if time.monotonic() > give_up:
        sys.exit(f"pid {pid} is still running")
    time.sleep(0.05)' "$1"; }

call pendingyou post_request "$(post verify/x/20261007-1400)" '{"structuredContent": {"requestId": "req_ses-1"}}' | cards
call pendingyou post_request "$(post proposal/7)" '{"structuredContent": {"requestId": "req_ses-2"}}' | cards
s1=$(session verify/x/20261007-1400); s2=$(session proposal/7)
call pendingyou ack_answer '{"name": "swb-1-conductor", "requestId": "req_ses-1", "version": 2, "outcome": "approved"}' \
  '{"structuredContent": {"status": "resolved"}}' | cards
gone "$s1"
[[ ! -e $cardsdir/verify/x/20261007-1400 ]] || fail "the answered card's key was not forgotten"
up "$s2" || fail "closing one card ended another's session"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-2", "reason": "replaced by proposal 8"}' \
  '{"structuredContent": {"status": "cancelled"}}' | cards
gone "$s2"
[[ ! -e $cardsdir/proposal/7 ]] || fail "the withdrawn card's key was not forgotten"
eq "$(pick card.close '.Key')" "proposal/7"
ok "an answered card's close and a withdrawn card each end the plannotator session crew started for its key"

call pendingyou post_request "$(post 'my own key')" '{"structuredContent": {"requestId": "req_ses-3"}}' | cards
call pendingyou post_request "$(post verify/y/20261007-1500)" '{"structuredContent": {"requestId": "req_ses-4"}}' | cards
s3=$(session verify/z/20261007-1600)
mine=$(started "$T/doc-mine.md" "$T/mine.json")
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-3"}' '{"structuredContent": {"status": "cancelled"}}' | cards
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-4"}' '{"structuredContent": {"status": "cancelled"}}' | cards
up "$s3" || fail "an unkeyed card's close ended a session"
up "$mine" || fail "a keyed card's close ended a session crew did not start"
[[ -e $cardsdir/verify/z/20261007-1600/session.json ]] || fail "another key's session was forgotten"
ok "an unkeyed card's close ends nothing, and a keyed card's close ends no session crew did not start for its key"

call pendingyou post_request "$(post verify/z/20261007-1600)" '{"structuredContent": {"requestId": "req_ses-5"}}' | cards
chmod 555 "$cardsdir/verify/z"
expect_ok cards <<<"$(call pendingyou ack_answer '{"requestId": "req_ses-5", "outcome": "done"}' '{"structuredContent": {"status": "resolved"}}')"
chmod 755 "$cardsdir/verify/z"
has "$out" "crew cards:"
eq "$(pick card.close '[.Card, .Key] | join(" ")')" "req_ses-5 verify/z/20261007-1600"
up "$s3" || fail "a session was ended while its key could not be forgotten"
kill "$s3" "$mine"
ok "a session the hook can't end is said, the close is still recorded, and the tool call goes on"

call pendingyou post_request "$(post proposal/9)" '{"structuredContent": {"requestId": "req_ses-6"}}' | cards
s4=$(session proposal/9)
mkdir -p "$T/broken"; printf '#!/usr/bin/env bash\necho "plannotator: its registry is locked" >&2\nexit 1\n' > "$T/broken/plannotator"
chmod +x "$T/broken/plannotator"
said=$(call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-6", "reason": "replaced by proposal 10"}' \
  '{"structuredContent": {"status": "cancelled"}}' | PATH="$T/broken:$PATH" cards)
eq "$(jq -r '.hookSpecificOutput | [.hookEventName, .additionalContext] | join(": ")' <<<"$said")" \
  "PostToolUse: crew can't read plannotator's sessions (plannotator sessions: plannotator: its registry is locked): it ended nothing, and keeps proposal/9 to end later"
up "$s4" || fail "a session was ended while plannotator's list could not be read"
[[ -e $cardsdir/proposal/9/session.json ]] || fail "the withdrawn card's session was forgotten while plannotator's list could not be read"
eq "$(pick card.close '[.Card, .Key] | join(" ")')" "req_ses-6 proposal/9"
call pendingyou post_request "$(post verify/w/20261007-1700)" '{"structuredContent": {"requestId": "req_ses-7"}}' | cards
s5=$(session verify/w/20261007-1700)
eq "$(call pendingyou ack_answer '{"requestId": "req_ses-7", "outcome": "done"}' '{"structuredContent": {"status": "resolved"}}' | cards)" ""
gone "$s5"
kill "$s4"
ok "a withdrawal while plannotator's list can't be read ends nothing, keeps the key's session and tells the agent so; a close that ends its session says nothing"

# Before a card is posted or an area made: a team holds a bolt with units, another team holds another, and the
# partition has a proposal open and one closed.
unset CREW_AGENT
export CREW_LABEL=wldn
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
for u in x checked; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew unit add z "Unit z." --bolt console-pages >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
crew bolt give swb-2 console-pages >/dev/null 2>&1
printf '%s\n' 'Case: The queue gets a unit.' 'Do: unit add queued "Queued." --repo switchboard-kit' > "$T/p1.rec"
printf '%s\n' 'Case: The queue gets another.' 'Do: unit add later "Later." --repo switchboard-kit' > "$T/p2.rec"
crew plan propose "$T/p1.rec" >/dev/null 2>&1; crew plan propose "$T/p2.rec" >/dev/null 2>&1
crew plan drop 2 "not now" >/dev/null
# A batch of seven, as the run record holds one: two cards, the second closed.
units7=$(for u in a b c d e f g; do printf '%s:swb-1@abc1234 ' "u$u"; done)
CREW_AGENT=wldn-reviewer emit --act review.batch --on batch/1 --field Batch=1 --field "Units=$units7" >/dev/null
CREW_AGENT=wldn-planner emit --act card.close --on batch/1 --field Card=req_b-1 --field Key=batch/1-2 >/dev/null
# The hook, run as the plugin runs it before a Pending You tool.
check() { as mac-studio python3 "$CREW/plugin/hooks/cards" --before; }
# pre <server> <tool> <input> [session]: the hook's input before one tool call, as Claude Code gives it
pre() { jq -nc --arg t "mcp__$1__$2" --argjson i "$3" --arg s "${4:-sid-1}" \
  '{session_id: $s, hook_event_name: "PreToolUse", cwd: "/work", tool_name: $t, tool_input: $i}'; }
# gate <agent> <tool> <key> [fields]: what the hook prints before that agent's call under that key, with the fields given
gate() {
  local f=${4-'{}'}
  CREW_AGENT=$1 check <<<"$(pre pendingyou "$2" "$(jq -nc --arg k "$3" --argjson f "$f" '{name: "x", title: "ZQXTITLE", idempotencyKey: $k} + $f')")"
}
# denied <agent> <tool> <key>: the reason the call is denied with; fails when it is let through
denied() {
  local o; o=$(gate "$@")
  eq "$(jq -r '.hookSpecificOutput | [.hookEventName, .permissionDecision] | join(" ")' <<<"$o")" "PreToolUse deny"
  jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$o"
}
n=$(entries | wc -l)

why=$(denied swb-1-ops post_request land/tenant-environments/abc1234)
has "$why" "swb-1-ops owns no card key, since a team's cards are its conductor's"
has "$why" "in your proof file, under Left for the user"
why=$(denied swb-1-ops post_request 'gateway check ZQXKEY')
has "$why" "swb-1-ops owns no card key"
why=$(denied swb-1-unit-2 post_request verify/x/20261007-1412)
has "$why" "swb-1-unit-2 owns no card key, since a team's cards are its conductor's"
has "$why" "/plugin/bin/crew needs"
ok "a team's ops and its unit slots are refused a card under any key: a team's cards are its conductor's"

eq "$(gate swb-1-conductor post_request land/tenant-environments/abc1234 '{"kind": "approve", "highStakes": true}')" ""
eq "$(gate swb-1-conductor post_request verify/checked/20261007-1412 '{"kind": "choice", "options": [{"id": "fix", "label": "Fix it"}]}')" ""
card1=$(crew plan card 1 | jq -c .card)
eq "$(gate wldn-planner post_request proposal/1 "$card1")" ""
ok "a conductor's own landing and verify keys, and the planner's open proposal, go through"

rows="land/tenant-environments/<head> or verify/<unit>/<stamp> for unit x or checked, the head or stamp from the \`card:\` line under its row in \`$CREW/plugin/bin/crew rail --label wldn\`"
why=$(denied swb-1-conductor post_request gateway-check-tenant-environments)
eq "$why" "crew refuses a card under gateway-check-tenant-environments: swb-1-conductor posts a card only under a rail row's key of its own: $rows."
why=$(denied swb-1-conductor post_request verify/z/20261007-1412)
has "$why" "swb-1-conductor posts a card only under a rail row's key of its own: $rows"
has "$(denied swb-1-conductor post_request land/console-pages/abc1234)" "$rows"
has "$(denied swb-1-conductor post_request review/x/abc1234)" "$rows"
has "$(denied swb-1-conductor post_request land/tenant-environments)" "$rows"
has "$(denied brd-1-conductor post_request land/tenant-environments/abc1234)" "brd-1 holds no bolt"
ok "a conductor's key of its own making, a review's key, which is no row's, a bolt's bare land/<bolt>, and another team's row, are refused naming the keys that are its own"

why=$(denied wldn-planner post_request proposal/2)
eq "$why" "crew refuses a card under proposal/2: wldn-planner posts a card only under proposal/<n> for a proposal of wldn open now, or batch/<n>-<k> for a card of one of its batches open now, proposal/1 or batch/1-1, from the \`card:\` line under its row in \`$CREW/plugin/bin/crew rail --label wldn\`."
eq "$(gate wldn-planner post_request batch/1-1 '{"questions": [{"id": "which", "kind": "multi", "title": "Which need notes?"}, {"id": "notes", "kind": "text", "title": "The notes"}]}')" ""
has "$(denied wldn-planner post_request batch/1-2)" "proposal/1 or batch/1-1"
has "$(denied swb-1-conductor post_request batch/1-1)" "swb-1-conductor posts a card only under a rail row's key of its own"
has "$(denied wldn-design post_request proposal/1)" "wldn-design owns no card key, since only the planner, the conductors and main-level ops post cards"
has "$(denied wldn-ops post_request land/tenant-environments/abc1234)" "operations"
ok "the planner is refused a closed proposal's or batch card's key, naming the open ones, and passes under an open batch card's, whose form is not checked; a conductor is refused a batch's key, and the main level's other agents own no key"

why=$(denied swb-1-conductor create_area area:swb-1-conductor)
eq "$why" "crew refuses an area under area:swb-1-conductor: swb-1-conductor makes a kit's area only under create-area:WilldanGroup/switchboard-kit."
eq "$(gate swb-1-conductor create_area create-area:WilldanGroup/switchboard-kit)" ""
eq "$(gate wldn-planner create_area create-area:WilldanGroup/atlas-kit)" ""
has "$(denied wldn-planner create_area create-area:agentplot/flywheel-next)" \
  "only under create-area:WilldanGroup/atlas-kit, create-area:WilldanGroup/breadboard-kit or create-area:WilldanGroup/switchboard-kit"
has "$(denied swb-1-conductor create_area create-area:WilldanGroup/atlas-kit)" "create-area:WilldanGroup/switchboard-kit"
ok "an area is let through only under create-area: and a kit of the agent's team, or of its partition's teams for the main level"

mv "$ws" "$ws.away"
why=$(denied swb-1-conductor post_request land/tenant-environments/abc1234)
mv "$ws.away" "$ws"
has "$why" "crew could not check this card: could not fetch wldn/main of WilldanGroup/crew-state"
has "$why" ". Post it again later."
why=$(CREW_AGENT=swb-1-conductor check <<<"$(pre pendingyou post_request '{"name": "x"}')" | jq -r '.hookSpecificOutput.permissionDecisionReason')
eq "$why" "crew refuses a card with no idempotencyKey."
why=$(CREW_LABEL= denied swb-1-conductor post_request land/tenant-environments/abc1234)
eq "$why" "crew could not check this card: swb-1-conductor's session has no CREW_LABEL, so crew can't tell its partition."
has "$(CREW_LABEL= denied swb-1-conductor create_area create-area:WilldanGroup/switchboard-kit)" "crew could not check this area: swb-1-conductor's session has no CREW_LABEL"
ok "a card crew can't check is refused, naming the branch it could not read, and so is one with no key or no CREW_LABEL"

eq "$(CREW_AGENT= CREW_LABEL= check <<<"$(pre pendingyou post_request '{"idempotencyKey": "anything"}' sid-none)")" ""
eq "$(CREW_AGENT= CREW_LABEL= check <<<"$(pre pendingyou create_area '{"idempotencyKey": "area:mine"}' sid-none)")" ""
eq "$(CREW_AGENT=swb-1-ops check <<<"$(pre github post_request '{"idempotencyKey": "anything"}')")" ""
eq "$(CREW_AGENT=swb-1-ops check <<<"$(pre pendingyou update_request '{"requestId": "req_abc-1"}')")" ""
eq "$(entries | wc -l)" "$n"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
hooks=$(jq -c '.hooks.PreToolUse[1] | [.matcher, .hooks[0].command, .hooks[0].timeout]' "$CREW/plugin/hooks/hooks.json")
eq "$hooks" '["mcp__.*__(post_request|create_area|update_request)","python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/cards\" --before",30]'
ok "a session crew didn't start, another server's tool and any other card tool are not checked for their key, nothing is recorded before a call, and the plugin runs the check, with --before, before the three"

# The hook, fed as Claude Code feeds it before a Pending You tool: a row's card, or a change to one, in another form
# than its row's is refused with the form to use, and the call is never made.
# The cards are swb-1-conductor's, under keys of its own, and the planner's for its open proposal.
export CREW_AGENT=swb-1-conductor
# card <key> <fields>: a post's input under the key, with the fields given
card() { jq -nc --arg k "$1" --argjson f "$2" '{name: "swb-1-conductor", title: "ZQXTITLE", idempotencyKey: $k} + $f'; }
refused() {  # refused <tool> <input> <phrase>...: the call is refused before it is made, its reason holding each phrase
  local tool=$1 input=$2; shift 2
  expect_ok check <<<"$(pre pendingyou "$tool" "$input")"
  denial "$@"
}
denial() {  # denial <phrase>...: $out is the deny object, its reason holding each phrase
  local p why
  eq "$(jq -r '.hookSpecificOutput | "\(.hookEventName) \(.permissionDecision)"' <<<"$out")" "PreToolUse deny"
  why=$(jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$out")
  for p in "$@"; do has "$why" "$p"; done
}
passes() {  # passes <tool> <input> [server] [session]: the hook prints nothing, and the call goes on
  expect_ok check <<<"$(pre "${3:-pendingyou}" "$1" "$2" "${4:-sid-1}")"
  eq "$out" ""
}
landing='{"kind": "approve", "highStakes": true}'
two='{"options": [{"id": "fix", "label": "Fix both"}, {"id": "merge", "label": "Merge as it is"}]}'
n=$(entries | wc -l)

refused post_request "$(card land/tenant-environments/abc1234 '{"kind": "action", "action": {"steps": [{"text": "Land the bolt", "command": "crew bolt land tenant-environments"}]}}')" \
  "crew refuses card land/tenant-environments/abc1234." "A landing's card is an approval" "marked high stakes" "whose yes has you tell main-level ops to land" \
  'This card is an "action", is not marked high stakes, and has a step that lands the bolt'
refused post_request "$(card land/tenant-environments/abc1234 '{"kind": "approve"}')" "This card is not marked high stakes."
refused post_request "$(card land/tenant-environments/abc1234 '{"kind": "approve", "highStakes": false}')" "This card is not marked high stakes."
passes post_request "$(card land/tenant-environments/abc1234 "$landing")"
refused post_request "$(card land/tenant-environments/abc1234 "$(jq -c '. + {action: {steps: [{text: "Land it", command: "crew bolt land tenant-environments"}]}}' <<<"$landing")")" \
  'has a step that lands the bolt: "Land it crew bolt land tenant-environments"'
refused post_request "$(card land/tenant-environments/abc1234 "$(jq -c '. + {action: {steps: [{text: "Merge the bolt with wt merge main"}]}}' <<<"$landing")")" \
  "has a step that lands the bolt"
passes post_request "$(card land/tenant-environments/abc1234 "$(jq -c '. + {action: {steps: [{text: "Open the gateway on your Mac"}]}}' <<<"$landing")")"
refused post_request "$(card land/tenant-environments/abc1234 "$(jq -c ". + $two" <<<"$landing")")" "This card has options."
ok "a landing card is refused as a step, unmarked high stakes, with options or with a step that lands it, and passes as a high-stakes approval, with steps a proof leaves"

refused post_request "$(card verify/checked/20261007-1412 '{"kind": "approve"}')" \
  "A verify report's card is a choice" 'This card is an "approve", and has no options.'
refused post_request "$(card verify/checked/20261007-1412 '{"kind": "choice"}')" "This card has no options."
passes post_request "$(card verify/checked/20261007-1412 "$(jq -c '{kind: "choice"} + .' <<<"$two")")"
passes post_request "$(card verify/checked/20261007-1412 "$(jq -c '{kind: "multi"} + .' <<<"$two")")"
# Proposal 3 makes no unit new to a bolt; 4 adds two to the queue, 1 one, and 5 one the plan has had since.
printf '%s\n' 'Case: Unit x changes.' 'Do: unit amend x "Unit x, again."' > "$T/p3.rec"
printf '%s\n' 'Case: Two units for the queue.' 'Do: unit add pb "B." --repo switchboard-kit' 'Do: unit add pc "C." --repo switchboard-kit' > "$T/p4.rec"
printf '%s\n' 'Case: One unit for the queue.' 'Do: unit add later5 "Later." --repo switchboard-kit' > "$T/p5.rec"
for f in p3 p4 p5; do CREW_AGENT= crew plan propose "$T/$f.rec" >/dev/null 2>&1; done
CREW_AGENT= crew unit add later5 "Added directly." --repo switchboard-kit >/dev/null
approval="Proposal 3 makes no unit new to a bolt, so its card is an approval, kind \"approve\", with a note for changes or for dropping it"
CREW_AGENT=wldn-planner passes post_request "$(card proposal/3 '{"kind": "approve"}')"
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 '{"kind": "review"}')" "$approval" 'This card is a "review".'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 '{"kind": "fyi"}')" "$approval" 'This card is a "fyi".'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 "$(jq -c '{kind: "approve"} + .' <<<"$two")")" "$approval" "This card has options."
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 '{"kind": "approve", "action": {"steps": [{"text": "Read the change"}]}}')" \
  "This card has steps for the user to take."
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 '{"kind": "action", "action": {"steps": [{"text": "Approve it", "command": "crew plan approve 3"}]}}')" \
  "$approval" 'This card is an "action"'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/3 '{"questions": [{"id": "go", "kind": "approve", "title": "Approve proposal 3?"}]}')" \
  "This card is a grouped card of questions."
grouped="Proposal 4 makes 2 units new to a bolt, so its card asks \`plan\`, an approval, and a question of its new units, of kind \"multi\", as \`$CREW/plugin/bin/crew plan card 4 --label wldn\` prints it"
card4=$(CREW_AGENT= crew plan card 4 | jq -c .card)
CREW_AGENT=wldn-planner passes post_request "$(card proposal/4 "$card4")"
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 "$(jq -c '.questions[1].options |= map(select(.id != "pc"))' <<<"$card4")")" \
  "crew refuses card proposal/4. $grouped" "This card does not ask about pc, new to a bolt in proposal 4."
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 "$(jq -c '.questions += [{id: "notes", kind: "text", title: "Anything to add?"}]' <<<"$card4")")" \
  "the note is the place for words" 'This card asks for words in notes, of kind "text".'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 '{"kind": "approve"}')" "$grouped" "This card asks no questions, as a plain approval."
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 "$(jq -c '.questions[1].options += [{id: "zz", label: "zz"}]' <<<"$card4")")" \
  "This card asks about zz, which proposal 4 does not make new to a bolt."
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 "$(jq -c '.questions[0].kind = "choice"' <<<"$card4")")" \
  'This card does not ask `plan`, of kind "approve", first.'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/4 "$(jq -c '. + {action: {steps: [{text: "Read it"}]}}' <<<"$card4")")" \
  "This card has steps for the user to take."
CREW_AGENT=wldn-planner passes post_request "$(card proposal/1 "$card1")"
CREW_AGENT=wldn-planner refused post_request "$(card proposal/1 "$(jq -c '.questions[1].kind = "multi"' <<<"$card1")")" \
  'This card asks units-1, which is no question of its new units of kind "choice".'
CREW_AGENT=wldn-planner refused post_request "$(card proposal/5 '{"kind": "approve"}')" "crew refuses card proposal/5: " \
  "wldn/main already has unit later5. Proposal 5 no longer applies to the plan as it stands: write the proposal again with \`crew plan propose <file> --replaces 5\`"
lacks "$(jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$out")" "again later"
refused post_request "$(card agent-note-1 '{"kind": "action", "action": {"steps": [{"text": "Land it", "command": "crew bolt land tenant-environments"}]}}')" \
  "crew refuses a card under agent-note-1: swb-1-conductor posts a card only under a rail row's key of its own"
refused post_request "$(card land/y '{"kind": "action"}')" "crew refuses a card under land/y: swb-1-conductor posts a card only under"
ok "a verify card is a choice with options; a proposal card is as crew plan card prints it, an approval, or the approval and each new unit once, never words, and none once its proposal no longer applies; a card under no row's key is refused for its key, not its form"

eq "$(entries | wc -l)" "$n"
ok "a check writes nothing to the run record"

call pendingyou post_request "$(card land/tenant-environments/abc1234 "$landing")" '{"structuredContent": {"requestId": "req_land-1"}}' | cards
CREW_AGENT=wldn-planner call pendingyou post_request "$(card proposal/1 '{"kind": "approve"}')" '{"structuredContent": {"requestId": "req_rev-1"}}' | CREW_AGENT=wldn-planner cards
call pendingyou post_request "$(card agent-note-2 '{"kind": "fyi"}')" '{"structuredContent": {"requestId": "req_own-1"}}' | cards
change() { jq -nc --arg r "$1" --argjson f "$2" '{name: "swb-1-conductor", requestId: $r, expectedVersion: 1, changeNote: "ZQXNOTE"} + $f'; }
refused update_request "$(change req_land-1 '{"highStakes": false}')" \
  "crew refuses this change to card land/tenant-environments/abc1234." "A landing's card is an approval" "This change clears its high stakes."
refused update_request "$(change req_land-1 '{"highStakes": null}')" "This change clears its high stakes."
refused update_request "$(change req_land-1 '{"action": {"steps": [{"text": "Land it", "command": "crew bolt land tenant-environments"}]}}')" \
  "This change gives it a step that lands the bolt"
passes update_request "$(change req_land-1 '{"title": "Land bolt y ZQXTITLE"}')"
passes update_request "$(change req_land-1 '{"highStakes": true}')"
refused update_request "$(change req_rev-1 "$two")" "crew refuses this change to card proposal/1." "This change gives it options."
refused update_request "$(change req_rev-1 '{"action": {"steps": [{"text": "Read it"}]}}')" "This change gives it steps for the user to take."
passes update_request "$(change req_own-1 "$two")"
passes update_request "$(change req_nowhere-1 '{"highStakes": false}')"
ok "a change that clears a landing's high stakes, gives an approval options or steps, or lands the bolt is refused; a card with no post here, or under no row's key, is not checked"

CREW_AGENT= CREW_LABEL= passes post_request "$(card land/tenant-environments/abc1234 '{"kind": "action"}')" pendingyou sid-none
passes post_request "$(card land/tenant-environments/abc1234 '{"kind": "action"}')" github
passes post_request "$(card land/tenant-environments/abc1234 '{"kind": "action"}')" plugin_github_github
refused post_request "$(card land/tenant-environments/abc1234 '{"kind": "action"}')" 'This card is an "action"'
expect_ok check <<<"$(pre plugin_pendingyou_pendingyou post_request "$(card land/tenant-environments/abc1234 '{"kind": "action"}')")"
has "$out" '"permissionDecision": "deny"'
expect_ok check <<<"$(pre pendingyou cancel_request '{"requestId": "req_land-1", "reason": "ZQXREASON"}')"
eq "$out" ""
ok "a session crew didn't start, another server's tool and a withdrawal are not checked; a plugin's Pending You is"

chmod 000 "$runs/$day.rec"
refused update_request "$(change req_land-1 '{"title": "Land bolt y again"}')" "crew could not check this card's form:"
chmod 644 "$runs/$day.rec"
refused update_request '"not an object"' "crew could not check this card's form: its input is not an object"
expect_ok check <<<'not json'
denial "crew could not check this card's form:"
expect_ok check <<<'"a string"'
denial "crew could not check this card's form: the hook's input is not a JSON object"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
ok "a card the hook can't check, its own input not JSON or no object among it, is refused, saying what failed"
