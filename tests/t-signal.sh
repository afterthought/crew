# A finding recorded through crew is a capture and its signal on the flywheel's branch of its state repository,
# pushed and replayed when the branch moved, the blueprints repo untouched; and every move, curation's and the
# route, written through crew to moves.rec on that branch, never merged.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
main=$(git --git-dir "$wb" rev-parse main)
id_of() { sed -n 's/^signal \([^: ]*\)[: ].*/\1/p' <<<"$1"; }

before=$(git --git-dir "$ws" rev-parse wldn/main)
HOST=chuck-herdr-alpha CREW_AGENT=swb-1-ops expect_ok crew signal waf-counts-instead-of-blocking \
  "The shared WAF counts the probes it should block; the bolt does not own the WAF." --kind constraint --subject "waf, security" --excerpt "action: COUNT on rule AWSManagedRulesCommonRuleSet"
waf=$(id_of "$out")
[[ $waf == "$(date -u +%F)-swb-1-ops-"*"/01-waf-counts-instead-of-blocking" ]] || fail "unexpected id $waf"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v '^runs/')" "signals/$waf.md"$'\n'"signals/${waf%/*}/capture.md"
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
sigtext=$(git --git-dir "$ws" show "wldn/main:signals/$waf.md")
has "$sigtext" "signal: $waf"; has "$sigtext" "kind: constraint"; has "$sigtext" "who: swb-1-ops"
has "$sigtext" "subject: [waf, security]"; has "$sigtext" "> \"action: COUNT"
has "$(git --git-dir "$ws" show "wldn/main:signals/${waf%/*}/capture.md")" "signals: 1"
eq "$(git --git-dir "$wb" rev-parse main)" "$main"
ok "a finding becomes a signal file and its capture, committed on the flywheel's branch, and the blueprints repo is untouched"

# Another host writes the branch while the next signal is in flight: it is applied again on the new tip.
race WilldanGroup/crew-state mac-studio atl-1-ops signal atlas-tiles-are-cached "Atlas caches tiles a day." --kind constraint --excerpt "Cache-Control: max-age=86400"
HOST=chuck-herdr-alpha CREW_AGENT=swb-1-ops expect_ok crew signal env-probe-absent "The env probe is absent from the IIS logs." --kind question --excerpt "0 matches for /env-probe"
env=$(id_of "$out")
has "$(cat "$T/race.log")" "atlas-tiles-are-cached"
atlas=$(id_of "$(grep '^signal ' "$T/race.log")")
eq "$(git --git-dir "$ws" log --format=%s "$before"..wldn/main | grep -c '^signals(')" "3"
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
has "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "env-probe-absent (swb-1-ops)"
git --git-dir "$ws" cat-file -e "wldn/main:signals/$env.md" || fail "no second signal"
git --git-dir "$ws" cat-file -e "wldn/main:signals/$atlas.md" || fail "the racing signal was lost"
eq "$(git --git-dir "$wb" rev-parse main)" "$main"
ok "a push refused because the branch moved is replayed on the new tip"

# Curation's moves go through crew, one per signal.
CREW_AGENT=wldn-design expect_ok crew signal move "$atlas" answered --target "books/atlas-kit/src/tiles.md" --reason "the book already says a day"
has "$out" "wldn/main"; has "$out" "signals($atlas): answered (wldn-design)"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v "^runs/")" "moves.rec"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "signals($atlas): answered (wldn-design)"
CREW_AGENT=wldn-design expect_fail "already has its move: answered" crew signal move "$atlas" drop --reason "twice"
CREW_AGENT=wldn-design expect_fail "no signal 2026-01-01-x/01-y on wldn/main of WilldanGroup/crew-state or on main of WilldanGroup/willdan-blueprints" crew signal move 2026-01-01-x/01-y drop --reason "none"
CREW_AGENT=wldn-design expect_fail "a drop gives its reason (--reason)" crew signal move "$env" drop
CREW_AGENT=wldn-design expect_fail "a attach move names its target" crew signal move "$env" attach
CREW_AGENT=wldn-design expect_fail "invalid choice: 'route'" crew signal move "$env" route
ok "crew signal move records one move per signal, with its target or reason"

# A route written on the box while curation writes a drop on mac-studio: both land, one after the other, unmerged.
echo refs/heads/wldn/main > "$T/race.ref"
race WilldanGroup/crew-state mac-studio wldn-design signal move "$env" drop --reason "a duplicate of the WAF finding"
tip=$(git --git-dir "$ws" rev-parse wldn/main)
HOST=chuck-herdr-alpha expect_ok crew unit add the-waf-blocks "The WAF blocks what its rules say." --repo switchboard-kit --signal "$waf"
[[ ! -f $T/race ]] || fail "the competing move never ran"
eq "$(git --git-dir "$ws" log --format=%s "$tip"..wldn/main)" "plan(queue): add the-waf-blocks ($me@chuck-herdr-alpha)"$'\n'"signals($env): drop (wldn-design)"
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"
recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
eq "$(recsel -C -t Move -P Move "$T/moves.rec" | tr '\n' ' ')" "answered drop route "
eq "$(git --git-dir "$wb" show main:signals/moves.rec | recsel -t Move -c)" "0"
ok "a route on the box and a drop on mac-studio both land unmerged on the branch, and moves.rec passes recfix --check"
