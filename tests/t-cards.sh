# crew records its agents' Pending You cards: the run record takes a card's id (Card) and its rail row's key (Key),
# in a day's file begun before those fields were allowed as well as after, and carries both to the branch. crew's
# PostToolUse hook writes an entry for each card a crew agent posts, updates, withdraws or closes, naming its row, its
# card and its key and nothing written on the card, from either shape of a tool's result; a card with no row key is on
# its agent. An error, another server's tool and a session crew didn't start write nothing; a session herdr resumed is
# known by what session-start recorded; and the hook never fails a tool call.
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
call plugin_pendingyou_pendingyou post_request "$(post land/tenant-environments)" \
  '{"content": [{"type": "text", "text": "not json"}, {"type": "text", "text": "{\"requestId\": \"req_abc-3\", \"version\": 1}"}]}' | cards
call pendingyou post_request "$(post proposal/4)" '{"structuredContent": {"requestId": "req_abc-4"}}' | cards
eq "$(entries card.post | jq -r '"\(.On[0]) \(.Card) \(.Key)"' | tail -2 | tr '\n' ' ')" \
  "bolt/tenant-environments req_abc-3 land/tenant-environments proposal/4 req_abc-4 proposal/4 "
ok "a post's entry names its row, its card and its key, from structuredContent, a text block of JSON, or a plugin's server"

call pendingyou update_request '{"name": "swb-1-conductor", "requestId": "req_abc-1", "title": "ZQXTITLE again"}' \
  '{"structuredContent": {"requestId": "req_abc-1", "status": "pending", "version": 2}}' | cards
eq "$(pick card.update '[(.On | join(" ")), .Card, .Key] | join(" ")')" "unit/x req_abc-1 review/x/abc1234"
call pendingyou ack_answer '{"name": "swb-1-conductor", "requestId": "req_abc-1", "version": 2, "outcome": "ZQXOUTCOME"}' \
  '{"structuredContent": {"status": "resolved"}}' | cards
eq "$(pick card.close '[.By, (.On | join(" ")), .Card, .Key] | join(" ")')" "swb-1-conductor unit/x req_abc-1 review/x/abc1234"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_abc-3", "reason": "ZQXREASON"}' \
  '[{"type": "text", "text": "{\"status\": \"cancelled\"}"}]' | cards
eq "$(pick card.close '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/tenant-environments req_abc-3 land/tenant-environments"
call pendingyou cancel_request '{"name": "swb-1-conductor", "requestId": "req_elsewhere-9"}' '{"structuredContent": {"status": "cancelled"}}' | cards
eq "$(pick card.close '[(.On | join(" ")), .Card, (.Key // "")] | join(" ")')" "agent/swb-1-conductor req_elsewhere-9 "
ok "an update, an answer acknowledged and a card withdrawn name the card and the row and key of its post; a card posted elsewhere is on its agent"

call pendingyou post_request "$(post 'my own key ZQXKEY')" '{"structuredContent": {"requestId": "req_abc-5"}}' | cards
eq "$(pick card.post '[(.On | join(" ")), .Card, (.Key // "-")] | join(" ")')" "agent/swb-1-conductor req_abc-5 -"
call pendingyou post_request "$(post review/x/abc1234)" '{"content": [{"type": "text", "text": "Posted."}]}' | cards
eq "$(pick card.post '[(.On | join(" ")), (.Card // "-"), .Key] | join(" ")')" "unit/x - review/x/abc1234"
recfix --check "$runs/$day.rec" || fail "the hook's entries fail recfix --check"
eq "$(grep -rl ZQX "$(home_of mac-studio)/.local/state/crew" || true)" ""
ok "an unkeyed card is on its agent with no Key, a result with no id is a post with no Card, and nothing written on a card is recorded"

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
