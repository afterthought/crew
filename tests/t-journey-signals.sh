# A finding, from its capture to the unit that takes it, through the crew command on the stubs (tests.11, record
# 0022): an agent's crew signal on the box checks its excerpt in its own transcript and writes the capture and its
# signal as one commit on the flywheel's branch, the source record banked on the host and nothing in the blueprints; a
# second signal joins the capture, the same one again writes nothing, and a paraphrase is refused with a refused
# entry; the session is herdr's for the agent; the user's note at a shell is its own excerpt; crew signal show answers
# from a host with no team; curation's move and a route are written to moves.rec, the route in the unit's own commit;
# a meeting's signal in the blueprints is moved and shown as it stands; a proposal shows a signal's excerpt and routes
# it on approval; and crew trace of a signal begins with its capture. How an excerpt is graded and who asserted it, how
# a capture is named and joined, its files, and what show and a proposal say are logic cases (tests/py/test_signals.py,
# test_transcript.py, test_proposal_life.py); recfix's checks of a signal and a move, contract cases
# (tests/contract/test_recfix.py); each step here checks a command's wiring once.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new smoke-2 "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt give swb-2 smoke-2 >/dev/null 2>&1
blueprints_refs=$(git --git-dir "$wb" for-each-ref)
tip() { git --git-dir "$ws" rev-parse wldn/main; }
at() { git --git-dir "$ws" show "wldn/main:$1"; }
changed() { git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v '^runs/'; }
runs() { cat "$(home_of "$1")"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null; }
id_of() { sed -n 's/^signal \([^: ]*\)[: ].*/\1/p' <<<"$1"; }
conductor() { HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-1 "$@"; }
# laptop: a host with crew's files and nothing of any team's
mkdir -p "$(home_of laptop)"; gitconfig "$(home_of laptop)"; cp -R "$(home_of mac-studio)/.config" "$(home_of laptop)/"

# The session's last record, the user's message, written a minute before the agent runs crew signal.
ts=$(ago 1); day=${ts:0:10}; hms=${ts:11:8}
transcript $box s-1 >/dev/null <<EOF
{"type":"user","uuid":"9f2c1a7e-5b6d-4c3e-8f00-112233445566","timestamp":"$ts","message":{"role":"user","content":"Could we get a security check on the CloudFormation templates too, beside cfn-lint's validity check?"}}
EOF
cap=$day-swb-2-conductor-9f2c1a7e; id=$cap/01-cfn-nag-templates
t0=$(tip)
conductor expect_ok crew signal cfn-nag-templates "The user wants a security check on Switchboard's CloudFormation templates beside cfn-lint's." \
  --excerpt "a security check on the CloudFormation templates" --kind ask --subject "cloudformation, security"
eq "$(tail -1 <<<"$out")" "signal $id: excerpt verified, asserted by user"
eq "$(git --git-dir "$ws" rev-list --count "$t0"..wldn/main)" "1"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "signals($id): cfn-nag-templates (swb-2-conductor)"
eq "$(changed)" "signals/$id.md"$'\n'"signals/$cap/capture.md"
has "$(at "signals/$cap/capture.md")" "where: team swb-2, bolt smoke-2"
has "$(at "signals/$id.md")" "> \"a security check on the CloudFormation templates\" — ${hms}Z"
eq "$(git --git-dir "$wb" for-each-ref)" "$blueprints_refs"
raw=$(home_of $box)/.local/state/crew/wldn/raw/$cap.jsonl
eq "$(cat "$raw")" "$(head -1 "$(home_of $box)/.claude/projects/-work/s-1.jsonl")"
git --git-dir "$ws" grep -q -F "validity check?" wldn/main && fail "the branch holds the rest of the source record"
has "$(runs $box)" "Act: capture"$'\n'"On: signals/$id"$'\n'"Commit: WilldanGroup/crew-state@$(tip)"
ok "an agent's verified capture and its signal are one commit on wldn/main, the source record banked on its host, and nothing in the blueprints"

conductor expect_ok crew signal beside-cfn-lint "The check sits beside cfn-lint's, not in place of it." --excerpt "beside cfn-lint's validity check"
eq "$(tail -1 <<<"$out")" "signal $cap/02-beside-cfn-lint: excerpt verified, asserted by user"
has "$(at "signals/$cap/capture.md")" "signals: 2"
t1=$(tip)
conductor expect_ok crew signal beside-cfn-lint "The check sits beside cfn-lint's, not in place of it." --excerpt "beside cfn-lint's validity check"
eq "$out" "signal $cap/02-beside-cfn-lint is recorded already; nothing was written"
conductor expect_fail "the excerpt is not in your session's transcript: quote the words as you received them" \
  crew signal reworded "The templates want a check ZQX2." --excerpt "the user wants every template checked ZQX3"
eq "$(tip)" "$t1"
eq "$(runs $box | grep -c "^Refused: the excerpt is not in your session's transcript")" "1"
[[ $(runs $box) != *ZQX* ]] || fail "the run record holds typed text"
ok "a second signal from the record joins its capture, the same signal again writes nothing, and a paraphrase is refused with a refused entry"

p=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-2 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$p" swb-2-conductor
transcript $box "sid-${p//:/-}" >/dev/null <<EOF
{"type":"user","uuid":"77aa0011-0000-4000-8000-000000000001","timestamp":"$(ago 1)","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"cfn-lint: 0 errors, 4 warnings"}]}}
EOF
HOST=$box CREW_AGENT=swb-2-conductor expect_ok crew signal lint-warns "cfn-lint passes the templates with warnings." --excerpt "0 errors, 4 warnings"
hc=$(id_of "$out"); has "$out" "excerpt verified, asserted by tool"
has "$(at "signals/${hc%/*}/capture.md")" "session: sid-${p//:/-}"
ok "with no session carried, the agent's session is herdr's"

text="Templates should be checked for public buckets"
expect_ok crew signal check-buckets "$text"
note=$(id_of "$out"); has "$out" "excerpt own"
has "$(at "signals/${note%/*}/capture.md")" "source: operator"
has "$(at "signals/$note.md")" $'---\n\n'"$text"$'\n\n> "'"$text"'" — '
ok "the user's note at a shell is its own excerpt"

: > "$CREW_TEST_LOG"
HOST=laptop expect_ok crew signal show "$id"
has "$out" "signals/$id, on wldn/main of WilldanGroup/crew-state"
has "$out" "  excerpt: verified"; has "$out" "No move yet in wldn."
lacks "$(calls)" "laptop ssh"
ok "from a host with no team, crew signal show reads a signal captured on the box from the branch alone"

CREW_AGENT=wldn-design expect_ok crew signal move "$note" answered --target "books/switchboard-kit/src/buckets.md" --reason "the book says so"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "signals($note): answered (wldn-design)"
eq "$(changed)" "moves.rec"
CREW_AGENT=wldn-design expect_fail "already has its move: answered" crew signal move "$note" drop --reason "twice"
expect_ok crew unit add templates-get-a-security-check "Templates get a security check." --repo switchboard-kit --signal "$id"
has "$out" "signal $id routed to unit/templates-get-a-security-check, in the same commit"
eq "$(changed)" $'moves.rec\nplan.rec'
HOST=laptop CREW_LABEL= expect_ok crew signal show "$id"
has "$out" "Its move in wldn: route unit/templates-get-a-security-check, by $me@mac-studio on $(date +%F)"
ok "curation's move and a route are written to moves.rec on the branch, the route in its unit's commit, and a second move is refused"

w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; msig=2026-09-30-standup/01-tiles-load-slowly
mkdir -p "$w/signals/${msig%/*}"
printf -- '---\ncapture: 2026-09-30-standup\nsource: meeting\nevent_date: 2026-09-30\nstatus: read\nsignals: 1\n---\n\n# Standup\n' > "$w/signals/${msig%/*}/capture.md"
printf -- '---\nsignal: %s\nkind: reaction\nwho: scott\n---\n\nTiles load slowly on the map.\n\n> "the map takes ages" — 00:04:12\n' "$msig" > "$w/signals/$msig.md"
commit_all "$w" "signals: a standup"; git -C "$w" push -q origin main; blueprints_refs=$(git --git-dir "$wb" for-each-ref)
CREW_AGENT=wldn-design crew signal move "$msig" drop --reason "fixed by the tile cache" >/dev/null
HOST=laptop expect_ok crew signal show "$msig"
has "$out" "signals/$msig, on main of WilldanGroup/willdan-blueprints"
has "$out" "Its move in wldn: drop, by wldn-design on $(date +%F): fixed by the tile cache"
eq "$(git --git-dir "$wb" for-each-ref)" "$blueprints_refs"
ok "a meeting's signal in the blueprints is moved on the flywheel's branch and shown as it stands"

asked=$(id_of "$(crew signal deploys-are-dry-run "Deploys should be dry-run first.")")
printf 'Case: The user asked for it.\nDo: unit add deploys-dry-run-first "A deploy is dry-run before it runs." --repo switchboard-kit --signal %s\n' "$asked" > "$T/p.rec"
expect_ok crew plan propose "$T/p.rec"
n=$(sed -n 's/^proposal \([0-9]*\) is open.*/\1/p' <<<"$out")
expect_ok crew plan proposed "$n"
has "$out" "From: signals/$asked: \"Deploys should be dry-run first.\""
has "$out" "Excerpt (own): > \"Deploys should be dry-run first.\" — "
expect_ok crew plan approve "$n"
eq "$(changed)" $'moves.rec\nplan.rec\nproposals.rec'
eq "$(at moves.rec | recsel -t Move -e "Signal = '$asked'" -P Move,Target)" "route"$'\n'"unit/deploys-dry-run-first"
ok "a proposal shows a signal's assertion and excerpt with its grade, and its approval routes the signal in its own commit"

expect_ok crew trace "signals/$id"
first=$(head -1 <<<"$out")
has "$first" "capture"; has "$first" "swb-2-conductor"; has "$first" "signals/$id"; has "$first" "zoe s-1 on $box"
ok "crew trace of a signal begins with its capture, naming the capturing agent, its host and its session"
