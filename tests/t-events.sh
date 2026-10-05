# crew events gathers the run record of every host a partition runs on, in time order, and names a host that doesn't
# answer; --about narrows it to one object, --json gives it to a program, --follow prints entries as they are written.
# crew trace prints one object's history through what it came from and what came from it, from the entries alone.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=chuck-herdr-alpha
emit() { local h=$1; shift; as "$h" python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@" >/dev/null; }
acts() { awk '{print $3}' <<<"$1" | tr '\n' ' '; }
export CREW_LABEL=wldn

emit $box --act unit.add --on unit/a --on queue/switchboard-kit --why "plan(queue): add a"
/bin/sleep 1
emit mac-studio --act tell --on agent/wldn-planner --field Chars=12 --why "tell wldn-planner"
/bin/sleep 1
emit $box --act unit.drop --on unit/b --on queue/switchboard-kit --why "plan(queue): drop b"
expect_ok crew events --label wldn
eq "$(acts "$out")" "unit.add tell unit.drop "
has "$(sed -n 1p <<<"$out")" "$box"; has "$(sed -n 2p <<<"$out")" "mac-studio"; has "$(sed -n 2p <<<"$out")" "(12 characters)"
has "$(sed -n 1p <<<"$out")" "unit/a queue/switchboard-kit"
expect_ok crew events --label wldn --about unit/b
eq "$(acts "$out")" "unit.drop "
expect_ok crew events --label wldn --json
eq "$(jq -r '[.entries[].Act] | join(" ")' <<<"$out")" "unit.add tell unit.drop"
eq "$(jq -r '.entries[0].On | join(" ")' <<<"$out")" "unit/a queue/switchboard-kit"
expect_ok crew events --label wldn --since "$(date -u -v+1d +%F 2>/dev/null || date -u -d tomorrow +%F)"
eq "$out" ""
echo "$box" > "$T/down"
expect_ok crew events --label wldn
eq "$(acts "$(grep -v 'did not answer' <<<"$out")")" "tell "
has "$(tail -1 <<<"$out")" "$box did not answer"
rm "$T/down"
ok "events prints both hosts' entries in time order, narrows to one object, gives JSON, and names a host that does not answer"

( export CREW_TEST_HOST=mac-studio HOME=$(home_of mac-studio); cd "$HOME" && exec "$CREW/plugin/bin/crew" events --follow --label wldn ) > "$T/follow" 2>&1 &
fpid=$!
/bin/sleep 2
emit $box --act stage.start --on stage/a/construct --on unit/a --why "unit(a): start construct"
for _ in $(seq 50); do grep -q "stage.start" "$T/follow" && break; /bin/sleep 0.2; done
kill "$fpid"; wait "$fpid" 2>/dev/null || true
has "$(cat "$T/follow")" "stage.start"
has "$(cat "$T/follow")" "stage/a/construct unit/a"
lacks "$(cat "$T/follow")" "unit.add"
/bin/sleep 1
pgrep -f "tail -q -n 0 -F .*$T/hosts" >/dev/null && fail "a tail outlived crew events --follow"
ok "events --follow prints an entry another host writes while it runs, and leaves no tail behind"

day=2026-10-05; sig=$day-swb-2-conductor/01-cfn-nag; u=cfn-nag-security-check
fixture() {  # fixture <host> <records>: a run-record file of $day on the host
  local f; f=$(home_of "$1")/.local/state/crew/wldn/runs/$1/$day.rec; mkdir -p "$(dirname "$f")"
  printf '%%rec: Entry\n%%key: Id\n\n%s\n' "$2" > "$f"
}
fixture $box "$(cat <<EOF
Id: 20261005T100000Z-$box-1-1
At: ${day}T10:00:00Z
Host: $box
By: swb-2-conductor
Session: $box:sid-c2
Act: capture
On: signals/$sig
Commit: WilldanGroup/willdan-blueprints@aaaaaaaa11
Why: signals($sig): cfn-nag

Id: 20261005T100500Z-$box-1-2
At: ${day}T10:05:00Z
Host: $box
By: swb-2-conductor
Act: capture
On: signals/$day-swb-2-conductor/02-other

Id: 20261005T110000Z-$box-2-1
At: ${day}T11:00:00Z
Host: $box
By: swb-1-conductor
Session: $box:sid-9
Act: stage.start
On: stage/$u/construct
On: unit/$u
On: agent/swb-1-unit-1

Id: 20261005T113000Z-$box-3-1
At: ${day}T11:30:00Z
Host: $box
By: swb-1-conductor
Act: stage.end
On: stage/$u/construct
On: unit/$u
On: agent/swb-1-unit-1
Result: review
Head: bbbbbbb

Id: 20261005T120000Z-$box-4-1
At: ${day}T12:00:00Z
Host: $box
By: chuck@mac-studio
Act: unit.approve
On: unit/$u
Commit: WilldanGroup/switchboard-kit@cccccccc22

Id: 20261005T121000Z-$box-5-1
At: ${day}T12:10:00Z
Host: $box
By: swb-1-conductor
Act: stage.start
On: stage/$u/merge
On: unit/$u
On: agent/swb-1-unit-1

Id: 20261005T122000Z-$box-5-2
At: ${day}T12:20:00Z
Host: $box
By: swb-1-conductor
Act: stage.end
On: stage/$u/merge
On: unit/$u
On: agent/swb-1-unit-1
Result: merged

Id: 20261005T123000Z-$box-6-1
At: ${day}T12:30:00Z
Host: $box
By: swb-1-conductor
Act: stage.start
On: stage/other-unit/construct
On: unit/other-unit
On: agent/swb-1-unit-2
EOF
)"
fixture mac-studio "$(cat <<EOF
Id: 20261005T103000Z-mac-studio-1-1
At: ${day}T10:30:00Z
Host: mac-studio
By: wldn-planner
Act: unit.add
On: unit/$u
On: queue/switchboard-kit
From: signals/$sig

Id: 20261005T103001Z-mac-studio-1-2
At: ${day}T10:30:01Z
Host: mac-studio
By: wldn-planner
Act: signal.move
On: signals/$sig
On: unit/$u

Id: 20261005T104000Z-mac-studio-2-1
At: ${day}T10:40:00Z
Host: mac-studio
By: wldn-planner
Act: unit.move
On: unit/$u
On: bolt/b1
From: queue/switchboard-kit

Id: 20261005T104100Z-mac-studio-3-1
At: ${day}T10:41:00Z
Host: mac-studio
By: wldn-planner
Act: unit.add
On: unit/other-unit
On: bolt/b1

Id: 20261005T104200Z-mac-studio-4-1
At: ${day}T10:42:00Z
Host: mac-studio
By: wldn-dispatch-$box
Act: bolt.give
On: bolt/b1
On: team/swb-1
EOF
)"
expect_ok crew trace "signals/$sig"
from_signal=$out
eq "$(acts "$out")" "capture unit.add signal.move unit.move stage.start stage.end unit.approve stage.start stage.end "
lacks "$out" "02-other"; lacks "$out" "other-unit"; lacks "$out" "bolt.give"
has "$(grep 'stage.start' <<<"$out" | head -1)" "zoe sid-9 on $box"
has "$(grep 'capture' <<<"$out")" "aaaaaaa"
expect_ok crew trace "unit/$u"
eq "$out" "$from_signal"
expect_ok crew trace "$u"
eq "$out" "$from_signal"
expect_fail "no entry names unit/nope" crew trace unit/nope
ok "a signal's trace and its unit's are the same chain, in order, each line with its session to open; nothing else comes in"
