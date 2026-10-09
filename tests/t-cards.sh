# crew records its agents' Pending You cards: the run record takes a card's id (Card) and its rail row's key (Key),
# in a day's file begun before those fields were allowed as well as after, and carries both to the branch. crew's
# PostToolUse hook writes an entry for each card a crew agent posts, updates, withdraws or closes, naming its row, its
# card and its key and nothing written on the card, from each shape of a tool's result; a card with no row key is on
# its agent. An error, another server's tool and a session crew didn't start write nothing; a session herdr resumed is
# known by what session-start recorded; and the hook never fails a tool call. A keyed card's withdrawal or close ends
# the plannotator session crew started for its key; an unkeyed card's ends nothing, nor does a key's close end a
# session crew did not start, and a card posted under a key that is no longer a row's closes under it. Before a card is
# posted or an area made, the hook refuses a crew agent's card under any key but a rail row's of its own, the planner's
# open proposal or its conductor's bolt and units, and an area under any key but create-area: and a kit of its own,
# naming the key to use; a team's ops and slots and the main level's other agents own no card key; a call crew can't
# check is refused naming what it could not read; and a session crew didn't start, another server's tool and the other
# card tools are neither checked nor refused. Each refusal scenario of the rail-cards spec.
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

call pendingyou post_request "$(post review/x/abc1234)" \
  '{"content": [{"type": "text", "text": "Posted."}], "structuredContent": {"requestId": "req_abc-1", "status": "pending", "version": 1}}' | cards
eq "$(pick card.post '[.Act, .By, .Session, (.On | join(" ")), .Card, .Key] | join(" ")')" \
  "card.post swb-1-conductor mac-studio:sid-1 unit/x req_abc-1 review/x/abc1234"
call pendingyou post_request "$(post verify/x/20261007-1412)" \
  '[{"type": "text", "text": "{\"requestId\": \"req_abc-2\", \"status\": \"pending\", \"version\": 1}"}]' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/x req_abc-2 verify/x/20261007-1412"
call plugin_pendingyou_pendingyou post_request "$(post land/tenant-environments/abc1234)" \
  '{"content": [{"type": "text", "text": "not json"}, {"type": "text", "text": "{\"requestId\": \"req_abc-3\", \"version\": 1}"}]}' | cards
call pendingyou post_request "$(post proposal/4)" '{"structuredContent": {"requestId": "req_abc-4"}}' | cards
eq "$(entries card.post | jq -r '"\(.On[0]) \(.Card) \(.Key)"' | tail -2 | tr '\n' ' ')" \
  "bolt/tenant-environments req_abc-3 land/tenant-environments/abc1234 proposal/4 req_abc-4 proposal/4 "
# As Claude Code 2.1.292 gives Pending You's result: the text alone, a string of JSON.
call pendingyou post_request "$(post review/y/def5678)" \
  '"{\"requestId\":\"req_5de3dad46fba41068fba\",\"threadId\":\"req_5de3dad46fba41068fba\",\"status\":\"pending\",\"version\":1}"' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/y req_5de3dad46fba41068fba review/y/def5678"
ok "a post's entry names its row, its card and its key, from structuredContent, a text block of JSON, a plain string of JSON, or a plugin's server"

call pendingyou update_request '{"name": "swb-1-conductor", "requestId": "req_abc-1", "title": "ZQXTITLE again"}' \
  '{"structuredContent": {"requestId": "req_abc-1", "status": "pending", "version": 2}}' | cards
eq "$(pick card.update '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/x req_abc-1 review/x/abc1234"
call pendingyou ack_answer '{"name": "swb-1-conductor", "requestId": "req_abc-1", "version": 2, "outcome": "ZQXOUTCOME"}' \
  '{"structuredContent": {"status": "resolved"}}' | cards
eq "$(pick card.close '[.By, (.On | join(" ")), .Card, .Key] | join(" ")')" "swb-1-conductor unit/x req_abc-1 review/x/abc1234"
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
call pendingyou post_request "$(post review/x/abc1234)" '{"content": [{"type": "text", "text": "Posted."}]}' | cards
eq "$(pick card.post '[(.On | join(" ")), (.Card // "-"), .Key] | join(" ")')" "unit/x - review/x/abc1234"
recfix --check "$runs/$day.rec" || fail "the hook's entries fail recfix --check"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
ok "an unkeyed card, or one under a bolt's bare land/<bolt>, is on its agent with no Key, a result with no id is a post with no Card, and nothing written on a card is recorded"

# A landing card posted under the bare land/<bolt> by a crew from before landings were keyed by the bolt's head.
emit --act card.post --on bolt/tenant-environments --field Card=req_old-1 --field Key=land/tenant-environments >/dev/null
expect_ok cards <<<"$(call pendingyou ack_answer '{"requestId": "req_old-1", "outcome": "landed"}' '{"structuredContent": {"status": "resolved"}}')"
lacks "$out" "crew cards:"
eq "$(pick card.close '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/tenant-environments req_old-1 land/tenant-environments"
ok "a card posted under a key that is no longer a row's is closed under the key and row of its post, with no session to end"

n=$(entries | wc -l)
call pendingyou post_request "$(post review/x/abc1234)" '{"isError": true, "content": [{"type": "text", "text": "refused"}]}' | cards
call pendingyou ack_answer '{"requestId": "req_abc-2"}' '{"deny": "not yours"}' | cards
call github post_request "$(post review/x/abc1234)" '{"structuredContent": {"requestId": "req_abc-6"}}' | cards
call pendingyou get_request '{"requestId": "req_abc-2"}' '{"structuredContent": {"requestId": "req_abc-2"}}' | cards
CREW_AGENT= CREW_LABEL= cards <<<"$(call pendingyou post_request "$(post review/x/abc1234)" '{"structuredContent": {"requestId": "req_abc-7"}}' sid-none)"
eq "$(entries | wc -l)" "$n"
ok "an error, a denial, another server's tool, a read and a session crew didn't start write nothing"

echo '{"session_id": "sid-9", "source": "startup", "cwd": "/work"}' | as mac-studio python3 "$CREW/plugin/hooks/session-start"
CREW_AGENT= CREW_LABEL= cards <<<"$(call pendingyou post_request "$(post proposal/5)" '{"structuredContent": {"requestId": "req_abc-8"}}' sid-9)"
eq "$(pick card.post '[.By, .Session, .Card, .Key] | join(" ")')" "swb-1-conductor mac-studio:sid-9 req_abc-8 proposal/5"
ok "a session herdr resumed without crew's environment is known by what session-start recorded of it"

expect_ok bash -c "echo 'not json' | CREW_TEST_HOST=mac-studio python3 '$CREW/plugin/hooks/cards'"
has "$out" "crew cards:"
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

call pendingyou post_request "$(post review/x/abc1234)" '{"structuredContent": {"requestId": "req_ses-1"}}' | cards
call pendingyou post_request "$(post proposal/7)" '{"structuredContent": {"requestId": "req_ses-2"}}' | cards
s1=$(session review/x/abc1234); s2=$(session proposal/7)
call pendingyou ack_answer '{"name": "swb-1-conductor", "requestId": "req_ses-1", "version": 2, "outcome": "approved"}' \
  '{"structuredContent": {"status": "resolved"}}' | cards
gone "$s1"
[[ ! -e $cardsdir/review/x/abc1234 ]] || fail "the answered card's key was not forgotten"
up "$s2" || fail "closing one card ended another's session"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-2", "reason": "replaced by proposal 8"}' \
  '{"structuredContent": {"status": "cancelled"}}' | cards
gone "$s2"
[[ ! -e $cardsdir/proposal/7 ]] || fail "the withdrawn card's key was not forgotten"
eq "$(pick card.close '.Key')" "proposal/7"
ok "an answered card's close and a withdrawn card each end the plannotator session crew started for its key"

call pendingyou post_request "$(post 'my own key')" '{"structuredContent": {"requestId": "req_ses-3"}}' | cards
call pendingyou post_request "$(post review/y/def5678)" '{"structuredContent": {"requestId": "req_ses-4"}}' | cards
s3=$(session review/z/1234567)
mine=$(started "$T/doc-mine.md" "$T/mine.json")
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-3"}' '{"structuredContent": {"status": "cancelled"}}' | cards
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_ses-4"}' '{"structuredContent": {"status": "cancelled"}}' | cards
up "$s3" || fail "an unkeyed card's close ended a session"
up "$mine" || fail "a keyed card's close ended a session crew did not start"
[[ -e $cardsdir/review/z/1234567/session.json ]] || fail "another key's session was forgotten"
ok "an unkeyed card's close ends nothing, and a keyed card's close ends no session crew did not start for its key"

call pendingyou post_request "$(post review/z/1234567)" '{"structuredContent": {"requestId": "req_ses-5"}}' | cards
chmod 555 "$cardsdir/review/z"
expect_ok cards <<<"$(call pendingyou ack_answer '{"requestId": "req_ses-5", "outcome": "done"}' '{"structuredContent": {"status": "resolved"}}')"
chmod 755 "$cardsdir/review/z"
has "$out" "crew cards:"
eq "$(pick card.close '[.Card, .Key] | join(" ")')" "req_ses-5 review/z/1234567"
up "$s3" || fail "a session was ended while its key could not be forgotten"
kill "$s3" "$mine"
ok "a session the hook can't end is said, the close is still recorded, and the tool call goes on"

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
# pre <server> <tool> <input> [session]: the hook's input before one tool call, as Claude Code gives it
pre() { jq -nc --arg t "mcp__$1__$2" --argjson i "$3" --arg s "${4:-sid-1}" \
  '{session_id: $s, hook_event_name: "PreToolUse", cwd: "/work", tool_name: $t, tool_input: $i}'; }
# gate <agent> <tool> <key>: what the hook prints before that agent's call under that key
gate() { CREW_AGENT=$1 cards <<<"$(pre pendingyou "$2" "$(jq -nc --arg k "$3" '{name: "x", title: "ZQXTITLE", idempotencyKey: $k}')")"; }
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
why=$(denied swb-1-unit-2 post_request review/x/abc1234)
has "$why" "swb-1-unit-2 owns no card key, since a team's cards are its conductor's"
has "$why" "/plugin/bin/crew needs"
ok "a team's ops and its unit slots are refused a card under any key: a team's cards are its conductor's"

eq "$(gate swb-1-conductor post_request land/tenant-environments/abc1234)" ""
eq "$(gate swb-1-conductor post_request review/x/abc1234)" ""
eq "$(gate swb-1-conductor post_request verify/checked/20261007-1412)" ""
eq "$(gate wldn-planner post_request proposal/1)" ""
ok "a conductor's own landing, review and verify keys, and the planner's open proposal, go through"

rows="land/tenant-environments/<head> or review/<unit>/<head> or verify/<unit>/<stamp> for unit x or checked, the head or stamp from the \`card:\` line under its row in \`$CREW/plugin/bin/crew rail --label wldn\`"
why=$(denied swb-1-conductor post_request gateway-check-tenant-environments)
eq "$why" "crew refuses a card under gateway-check-tenant-environments: swb-1-conductor posts a card only under a rail row's key of its own: $rows."
why=$(denied swb-1-conductor post_request review/z/abc1234)
has "$why" "swb-1-conductor posts a card only under a rail row's key of its own: $rows"
has "$(denied swb-1-conductor post_request land/console-pages/abc1234)" "$rows"
has "$(denied swb-1-conductor post_request land/tenant-environments)" "$rows"
has "$(denied brd-1-conductor post_request land/tenant-environments/abc1234)" "brd-1 holds no bolt"
ok "a conductor's key of its own making, a bolt's bare land/<bolt>, and another team's row, are refused naming the keys that are its own"

why=$(denied wldn-planner post_request proposal/2)
eq "$why" "crew refuses a card under proposal/2: wldn-planner posts a card only under proposal/<n> for a proposal of wldn open now, proposal/1, from the \`card:\` line under its row in \`$CREW/plugin/bin/crew rail --label wldn\`."
has "$(denied wldn-design post_request proposal/1)" "wldn-design owns no card key, since only the planner and the conductors post cards"
has "$(denied wldn-ops post_request land/tenant-environments/abc1234)" "Tell the partition's operator agents what you wait on"
ok "the planner is refused a closed proposal's key, naming the open one, and the main level's other agents own no key"

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
why=$(CREW_AGENT=swb-1-conductor cards <<<"$(pre pendingyou post_request '{"name": "x"}')" | jq -r '.hookSpecificOutput.permissionDecisionReason')
eq "$why" "crew refuses a card with no idempotencyKey."
why=$(CREW_LABEL= denied swb-1-conductor post_request land/tenant-environments/abc1234)
eq "$why" "crew could not check this card: swb-1-conductor's session has no CREW_LABEL, so crew can't tell its partition."
has "$(CREW_LABEL= denied swb-1-conductor create_area create-area:WilldanGroup/switchboard-kit)" "crew could not check this area: swb-1-conductor's session has no CREW_LABEL"
ok "a card crew can't check is refused, naming the branch it could not read, and so is one with no key or no CREW_LABEL"

eq "$(CREW_AGENT= CREW_LABEL= cards <<<"$(pre pendingyou post_request '{"idempotencyKey": "anything"}' sid-none)")" ""
eq "$(CREW_AGENT= CREW_LABEL= cards <<<"$(pre pendingyou create_area '{"idempotencyKey": "area:mine"}' sid-none)")" ""
eq "$(CREW_AGENT=swb-1-ops cards <<<"$(pre github post_request '{"idempotencyKey": "anything"}')")" ""
eq "$(CREW_AGENT=swb-1-ops cards <<<"$(pre pendingyou update_request '{"requestId": "req_abc-1"}')")" ""
eq "$(entries | wc -l)" "$n"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
hooks=$(jq -c '.hooks.PreToolUse[1] | [.matcher, .hooks[0].command, .hooks[0].timeout]' "$CREW/plugin/hooks/hooks.json")
eq "$hooks" '["mcp__.*__(post_request|create_area)","python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/cards\"",30]'
ok "a session crew didn't start, another server's tool and any other card tool are neither checked nor refused, nothing is recorded before a call, and the plugin runs the check before the two"
