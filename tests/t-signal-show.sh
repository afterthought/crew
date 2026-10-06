# crew signal show <id>: the signal, its capture's provenance in plain lines (the excerpt's grade, who captured it,
# where, when, the session and the raw record on its host) and its move, read from the branches alone, so a host
# that holds no team answers for a signal captured on the box; and a meeting's signal in the blueprints, which has
# none of the new fields, reads as it stands.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new smoke-2 "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt give swb-2 smoke-2 >/dev/null 2>&1
# laptop: a host with crew's files and nothing of any team's
mkdir -p "$(home_of laptop)"; gitconfig "$(home_of laptop)"; cp -R "$(home_of mac-studio)/.config" "$(home_of laptop)/"

transcript $box s-1 >/dev/null <<'EOF'
{"type":"user","uuid":"9f2c1a7e-5b6d-4c3e-8f00-112233445566","timestamp":"2026-10-05T14:21:07Z","message":{"role":"user","content":"Could we get a security check on the CloudFormation templates too?"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"crew signal cfn-nag-templates ..."}}]}}
EOF
HOST=$box CREW_AGENT=swb-2-conductor CREW_SESSION=$box:s-1 crew signal cfn-nag-templates "The user wants a security check on the templates." \
  --excerpt "a security check on the CloudFormation templates" --kind ask >/dev/null
cap=2026-10-05-swb-2-conductor-9f2c1a7e; id=$cap/01-cfn-nag-templates

HOST=laptop expect_ok crew signal show "$id"
has "$out" "signals/$id, on wldn/main of WilldanGroup/crew-state"
has "$out" $'kind: ask\nwho: user\n---\n\nThe user wants a security check on the templates.\n\n> "a security check on the CloudFormation templates" — 14:21:07Z'
has "$out" "Its capture, signals/$cap/capture.md:"
for want in "captured_by: swb-2-conductor" "host: $box" "session: s-1" "at: 2026-10-05T14:21:07Z" "excerpt: verified" "asserted_by: user" \
  "where: team swb-2, bolt smoke-2" "raw: $box:~/.local/state/crew/wldn/raw/$cap.jsonl"; do
  has "$out" "  $want"
done
has "$out" "No move yet in wldn."
lacks "$(calls)" "laptop ssh"
ok "from a host with no team, a signal captured on the box is shown with its grade, session, where and raw record"

HOST=laptop CREW_LABEL= crew unit add templates-get-a-security-check "Templates get a security check." --repo switchboard-kit --signal "$id" --label wldn >/dev/null
HOST=laptop CREW_LABEL= expect_ok crew signal show "$id"
has "$out" "Its move in wldn: route unit/templates-get-a-security-check, by $me@laptop on $(date +%F)"
ok "its move is shown once it has one, with no partition named"

w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; msig=2026-09-30-standup/01-tiles-load-slowly
mkdir -p "$w/signals/${msig%/*}"
printf -- '---\ncapture: 2026-09-30-standup\nsource: meeting\nevent_date: 2026-09-30\nstatus: read\nsignals: 1\n---\n\n# Standup\n' > "$w/signals/${msig%/*}/capture.md"
printf -- '---\nsignal: %s\nkind: reaction\nwho: scott\n---\n\nTiles load slowly on the map.\n\n> "the map takes ages" — 00:04:12\n' "$msig" > "$w/signals/$msig.md"
commit_all "$w" "signals: a standup"; git -C "$w" push -q origin main
CREW_AGENT=wldn-design crew signal move "$msig" drop --reason "fixed by the tile cache" >/dev/null
HOST=laptop expect_ok crew signal show "$msig"
has "$out" "signals/$msig, on main of WilldanGroup/willdan-blueprints"
has "$out" $'Tiles load slowly on the map.\n\n> "the map takes ages" — 00:04:12'
has "$out" $'Its capture, signals/2026-09-30-standup/capture.md:\n  capture: 2026-09-30-standup\n  source: meeting\n  event_date: 2026-09-30\n  status: read\n  signals: 1'
lacks "$out" "excerpt:"
has "$out" "Its move in wldn: drop, by wldn-design on $(date +%F): fixed by the tile cache"
ok "a meeting's signal in the blueprints, without crew's capture fields, is shown as it stands, with its move"

HOST=laptop expect_fail "no signal 2026-01-01-x/01-y on the branches of wldn/main or on main of their first blueprints repos" crew signal show 2026-01-01-x/01-y
HOST=laptop expect_fail "the following arguments are required: id" crew signal show
ok "an id in neither home is refused, and show needs an id"
