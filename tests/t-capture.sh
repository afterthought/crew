# crew signal by an agent: the excerpt is required and checked against the agent's own Claude transcript, the
# capture is the one record that holds it, banked on the host outside git, and the capture and its signal are one
# commit on the flywheel's branch of its state repository, the blueprints untouched. A second signal from the same
# record joins its capture; the same signal again writes nothing. A paraphrase is refused; a transcript crew can't
# read, or one not written in the last 15 minutes, writes the capture unverified; and the user's note at a shell is
# its own excerpt.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new smoke-2 "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt give swb-2 smoke-2 >/dev/null 2>&1
blueprints_refs=$(git --git-dir "$wb" for-each-ref)
tip() { git --git-dir "$ws" rev-parse wldn/main; }
at() { git --git-dir "$ws" show "wldn/main:$1"; }
hash16() { python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest()[:16])' "$1"; }
runs() { cat "$(home_of "$1")"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null; }
conductor() { HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-1 "$@"; }

# The session's last record, the user's message, written a minute before the agent runs crew signal.
ts=$(ago 1); day=${ts:0:10}; hms=${ts:11:8}
transcript $box s-1 >/dev/null <<EOF
{"type":"user","uuid":"9f2c1a7e-5b6d-4c3e-8f00-112233445566","timestamp":"$ts","message":{"role":"user","content":"Could we get a security check on the CloudFormation templates too, beside cfn-lint's validity check?"}}
EOF
cap=$day-swb-2-conductor-9f2c1a7e; id=$cap/01-cfn-nag-templates
t0=$(tip)
conductor expect_ok crew signal cfn-nag-templates "The user wants a security check on Switchboard's CloudFormation templates beside cfn-lint's." \
  --excerpt "a security check on the CloudFormation templates" --kind ask --subject "cloudformation, security"
has "$out" "signal $id: excerpt verified, asserted by user"
eq "$(git --git-dir "$ws" rev-list --count "$t0"..wldn/main)" "1"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "signals($id): cfn-nag-templates (swb-2-conductor)"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v '^runs/')" "signals/$id.md"$'\n'"signals/$cap/capture.md"
c=$(at "signals/$cap/capture.md")
for want in "capture: $cap" "source: crew-session" "key: session/s-1/9f2c1a7e-5b6d-4c3e-8f00-112233445566" "captured_by: swb-2-conductor" \
  "host: $box" "session: s-1" "record: 9f2c1a7e-5b6d-4c3e-8f00-112233445566" "at: ${ts:0:19}Z" "excerpt: verified" \
  "asserted_by: user" "where: team swb-2, bolt smoke-2" "raw: $box:~/.local/state/crew/wldn/raw/$cap.jsonl" "event_date: $day" \
  "status: read" "signals: 1" "# swb-2-conductor, $day ${hms:0:5}Z"; do
  has "$c" "$want"
done
s=$(at "signals/$id.md")
eq "$s" "---
signal: $id
kind: ask
who: user
subject: [cloudformation, security]
---

The user wants a security check on Switchboard's CloudFormation templates beside cfn-lint's.

> \"a security check on the CloudFormation templates\" — ${hms}Z"
eq "$(git --git-dir "$wb" for-each-ref)" "$blueprints_refs"
raw=$(home_of $box)/.local/state/crew/wldn/raw/$cap.jsonl
eq "$(cat "$raw")" "$(head -1 "$(home_of $box)/.claude/projects/-work/s-1.jsonl")"
for r in "$ws" "$wb"; do
  for ref in $(git --git-dir "$r" for-each-ref --format='%(refname)'); do
    git --git-dir "$r" grep -q -F "validity check?" "$ref" && fail "$r holds the rest of the source record, at $ref"
  done
done
has "$(runs $box)" "Act: capture"$'\n'"On: signals/$id"$'\n'"Commit: WilldanGroup/crew-state@$(tip)"
ok "a verified capture and its signal are one commit on wldn/main, the raw record on the host, and nothing in the blueprints"

race WilldanGroup/crew-state mac-studio "" signal check-groups "Templates should be checked for open security groups" --label wldn
t1=$(tip)
conductor expect_ok crew signal beside-cfn-lint "The check sits beside cfn-lint's, not in place of it." --excerpt "beside cfn-lint's validity check"
[[ ! -f $T/race ]] || fail "the competing write never ran"
has "$out" "signal $cap/02-beside-cfn-lint: excerpt verified"
eq "$(git --git-dir "$ws" log --format=%s "$t1"..wldn/main | sed 's/: .*//' | sort | tr '\n' ' ')" \
  "$(printf '%s\n' "signals($cap/02-beside-cfn-lint)" "signals($(date -u +%F)-${me//[^a-z0-9]/-}-mac-studio-$(hash16 "Templates should be checked for open security groups" | cut -c1-8)/01-check-groups)" | sort | tr '\n' ' ')"
has "$(at "signals/$cap/capture.md")" "signals: 2"
has "$(at "signals/$cap/02-beside-cfn-lint.md")" "> \"beside cfn-lint's validity check\" — ${hms}Z"
eq "$(grep -c . "$raw")" "1"
t2=$(tip)
conductor expect_ok crew signal beside-cfn-lint "The check sits beside cfn-lint's, not in place of it." --excerpt "beside cfn-lint's validity check"
eq "$out" "signal $cap/02-beside-cfn-lint is recorded already; nothing was written"
eq "$(tip)" "$t2"
ok "a second signal from the record joins its capture as 02, applied again to a tip that moved; the same signal again writes nothing"

race WilldanGroup/crew-state $box swb-2-conductor signal cfn-lint-stays "cfn-lint keeps its place." --excerpt "cfn-lint's validity check" --label wldn
t3=$(tip)
conductor expect_ok crew signal cfn-lint-stays "cfn-lint keeps its place." --excerpt "cfn-lint's validity check"
[[ ! -f $T/race ]] || fail "the competing write never ran"
eq "$out" "signal $cap/03-cfn-lint-stays is recorded already; nothing was written"
eq "$(git --git-dir "$ws" log --format=%s "$t3"..wldn/main)" "signals($cap/03-cfn-lint-stays): cfn-lint-stays (swb-2-conductor)"
has "$(at "signals/$cap/capture.md")" "signals: 3"
ok "the same signal landing first while a push is in flight leaves one signal, and the replay writes nothing"

t4=$(tip)
conductor expect_fail 'a signal quotes the words that show it: add --excerpt' crew signal no-words "The templates want a check ZQX1."
conductor expect_fail "a signal says what it asserts, in a sentence" crew signal says-nothing " " --excerpt "a security check"
conductor expect_fail "the excerpt is not in your session's transcript: quote the words as you received them" \
  crew signal reworded "The templates want a check ZQX2." --excerpt "the user wants every template checked ZQX3"
eq "$(tip)" "$t4"
eq "$(runs $box | grep -c '^Refused: a signal quotes the words that show it')" "1"
eq "$(runs $box | grep -c "^Refused: the excerpt is not in your session's transcript")" "1"
for typed in ZQX1 ZQX2 ZQX3; do [[ $(runs $box; runs mac-studio) != *"$typed"* ]] || fail "the run record holds typed text ($typed)"; done
ok "no excerpt, and words the session never received, are refused, each a refused entry holding neither assertion nor excerpt"

HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-gone expect_ok crew signal edge-drifts "The edge stack drifts." --excerpt "drift detected on stack edge"
has "$out" "excerpt unverified (no transcript for session s-gone)"
h=$(hash16 "drift detected on stack edge"); ucap=$(date -u +%F)-swb-2-conductor-${h:0:8}
c=$(at "signals/$ucap/capture.md")
for want in "key: unverified/swb-2-conductor/$h" "session: s-gone" "excerpt: unverified" "unverified: no transcript for session s-gone" \
  "asserted_by: unknown" "where: team swb-2, bolt smoke-2"; do has "$c" "$want"; done
for gone in "record:" "at:" "raw:"; do lacks "$c" "$gone"; done
has "$(at "signals/$ucap/01-edge-drifts.md")" "> \"drift detected on stack edge\" — unverified"
[[ ! -e $(home_of $box)/.local/state/crew/wldn/raw/$ucap.jsonl ]] || fail "an unverified capture banked a raw record"
transcript $box s-old >/dev/null <<EOF
{"type":"user","uuid":"0ld00000-0000-4000-8000-000000000009","timestamp":"$(ago 30)","message":{"role":"user","content":"drift detected twice on stack edge"}}
EOF
HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-old expect_ok crew signal drifts-twice "The edge stack drifts twice." --excerpt "drift detected twice"
has "$out" "excerpt unverified (session s-old's transcript has not been written for 30 minutes: crew may be reading another session's)"
HOST=$box CREW_AGENT=swb-2-ops expect_ok crew signal no-session "The edge stack drifts again." --excerpt "drift detected again"
has "$out" "excerpt unverified (herdr names no session)"
ok "a transcript crew can't find, one not written for 15 minutes, and no session each write the capture unverified, with the reason"

f=$(transcript $box s-f <<'EOF'
{"payload":{"text":"stack edge drifted twice overnight"}}
{"payload":{"command":"crew signal drift-found --excerpt 'drifted twice'"}}
EOF
)
HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-f expect_ok crew signal drift-found "The edge stack drifts at night." --excerpt "drifted twice overnight"
lh=$(head -1 "$f" | tr -d '\n' | python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest()[:16])')
fcap=$(date -u +%F)-swb-2-conductor-${lh:0:8}
has "$out" "signal $fcap/01-drift-found: excerpt found"
c=$(at "signals/$fcap/capture.md")
for want in "key: session/s-f/line-$lh" "record: line 1" "excerpt: found" "asserted_by: unknown" "raw: $box:~/.local/state/crew/wldn/raw/$fcap.jsonl"; do has "$c" "$want"; done
has "$(at "signals/$fcap/01-drift-found.md")" "> \"drifted twice overnight\" — line 1"
eq "$(cat "$(home_of $box)/.local/state/crew/wldn/raw/$fcap.jsonl")" "$(head -1 "$f")"
ok "an excerpt in a line crew can't classify is found: named by the line's hash, placed by its number, the line banked"

p=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-2 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$p" swb-2-conductor
ts=$(ago 1); hc=${ts:0:10}-swb-2-conductor-77aa0011
transcript $box "sid-$p" >/dev/null <<EOF
{"type":"user","uuid":"77aa0011-0000-4000-8000-000000000001","timestamp":"$ts","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"cfn-lint: 0 errors, 4 warnings"}]}}
EOF
HOST=$box CREW_AGENT=swb-2-conductor expect_ok crew signal lint-warns "cfn-lint passes the templates with warnings." --excerpt "0 errors, 4 warnings"
has "$out" "signal $hc/01-lint-warns: excerpt verified, asserted by tool"
has "$(at signals/$hc/01-lint-warns.md)" "who: swb-2-conductor"
has "$(at signals/$hc/capture.md)" "session: sid-$p"
ok "the session is herdr's for the agent, and a tool's output is asserted by the agent that ran it"

mkdir -p "$(home_of $box)/.local/state/swb-2-team"
echo "unit-1 unit cfn-lint-treefmt $kd/places/cfn-lint-treefmt" > "$(home_of $box)/.local/state/swb-2-team/slots"
ts=$(ago 1)
transcript $box s-u >/dev/null <<EOF
{"type":"user","uuid":"c0ffee00-0000-4000-8000-000000000002","timestamp":"$ts","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"treefmt: cfn-lint exits 4 on a warning"}]}}
EOF
HOST=$box CREW_AGENT=swb-2-unit-1 CREW_SESSION=$box:s-u expect_ok crew signal treefmt-fails-on-warnings "treefmt fails on cfn-lint's warnings." --excerpt "cfn-lint exits 4 on a warning"
has "$(at signals/${ts:0:10}-swb-2-unit-1-c0ffee00/capture.md)" "where: team swb-2, bolt smoke-2, unit cfn-lint-treefmt"
ok "a stage agent's capture names its team, the bolt the team holds, and the unit its slot holds"

ts=$(ago 1); pd=${ts:0:10}
transcript $box s-p >/dev/null <<EOF
{"type":"user","uuid":"aaaa0001-0000-4000-8000-000000000003","timestamp":"$ts","message":{"role":"user","content":"[crew tell from swb-2-conductor] smoke-2 needs a security check before it can land."}}
{"type":"user","uuid":"aaaa0002-0000-4000-8000-000000000004","timestamp":"$ts","message":{"role":"user","content":"[crew] plan(smoke-2): add cfn-lint-treefmt ($me@mac-studio)"}}
{"type":"user","uuid":"aaaa0003-0000-4000-8000-000000000005","timestamp":"$ts","message":{"role":"user","content":"[crew tell from $me@mac-studio] Keep the security check out of smoke-2."}}
EOF
planner() { HOST=$box CREW_AGENT=wldn-planner CREW_SESSION=$box:s-p "$@"; }
planner expect_ok crew signal needs-a-check "smoke-2 can't land without a security check." --excerpt "smoke-2 needs a security check before it can land."
has "$out" "asserted by agent:swb-2-conductor"
has "$(at signals/$pd-wldn-planner-aaaa0001/01-needs-a-check.md)" "who: swb-2-conductor"
has "$(at signals/$pd-wldn-planner-aaaa0001/capture.md)" "where: main level"
planner expect_ok crew signal plan-noticed "cfn-lint-treefmt was added to smoke-2." --excerpt "add cfn-lint-treefmt"
has "$out" "asserted by crew"; has "$(at signals/$pd-wldn-planner-aaaa0002/01-plan-noticed.md)" "who: crew"
planner expect_ok crew signal keep-it-out "The user keeps the security check out of smoke-2." --excerpt "Keep the security check out of smoke-2."
has "$out" "asserted by user"; has "$(at signals/$pd-wldn-planner-aaaa0003/01-keep-it-out.md)" "who: user"
ok "an excerpt in another agent's tell is that agent's, in crew's notice crew's, and in the user's own tell the user's"

text="Templates should be checked for public buckets"
h=$(hash16 "$text"); ncap=$(date -u +%F)-${me//[^a-z0-9]/-}-mac-studio-${h:0:8}
expect_ok crew signal check-buckets "$text" --label wldn
has "$out" "signal $ncap/01-check-buckets: excerpt own"
c=$(at "signals/$ncap/capture.md")
for want in "source: operator" "key: operator/$me@mac-studio/$h" "captured_by: $me@mac-studio" "host: mac-studio" "excerpt: own" "asserted_by: user"; do
  has "$c" "$want"
done
for gone in "session:" "record:" "raw:" "where:"; do lacks "$c" "$gone"; done
s=$(at "signals/$ncap/01-check-buckets.md")
has "$s" "kind: ask"; has "$s" "who: user"; has "$s" $'---\n\n'"$text"$'\n\n> "'"$text"'" — '
ok "the user's note at a shell is its own excerpt, asserted by the user, kind ask, with no session"

expect_ok crew trace "signals/$id"
first=$(head -1 <<<"$out")
has "$first" "capture"; has "$first" "swb-2-conductor"; has "$first" "$box"; has "$first" "signals/$id"; has "$first" "zoe s-1 on $box"
ok "crew trace of a signal begins with its capture, naming the capturing agent, its host and its session"
