# A finding written as a signal in the partition's first blueprints repo, by path on main, pushed and replayed
# when main moved.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
today=$(date +%F); cap=$today-swb-1-ops
export CREW_LABEL=wldn
before=$(git --git-dir "$wb" rev-parse main)

HOST=chuck-herdr-alpha CREW_AGENT=swb-1-ops expect_ok crew signal waf-counts-instead-of-blocking \
  "The shared WAF counts the probes it should block; the bolt does not own the WAF." --kind constraint --subject "waf, security" --excerpt "action: COUNT on rule AWSManagedRulesCommonRuleSet"
has "$out" "signal $cap/01-waf-counts-instead-of-blocking"
eq "$(git --git-dir "$wb" diff-tree --no-commit-id --name-only -r main)" $"signals/$cap/01-waf-counts-instead-of-blocking.md"$'\n'"signals/$cap/capture.md"
eq "$(git --git-dir "$wb" rev-list --count "$before"..main)" "1"
sigtext=$(git --git-dir "$wb" show "main:signals/$cap/01-waf-counts-instead-of-blocking.md")
has "$sigtext" "signal: $cap/01-waf-counts-instead-of-blocking"; has "$sigtext" "kind: constraint"; has "$sigtext" "who: swb-1-ops"
has "$sigtext" "subject: [waf, security]"; has "$sigtext" "> action: COUNT"
has "$(git --git-dir "$wb" show "main:signals/$cap/capture.md")" "signals: 1"
ok "a finding becomes a signal file and its capture, committed by path on main"

# Another host pushes to main while the next signal is in flight: it is applied again on the new tip.
race WilldanGroup/willdan-blueprints mac-studio atl-1-ops signal atlas-tiles-are-cached "Atlas caches tiles a day." --kind constraint
HOST=chuck-herdr-alpha CREW_AGENT=swb-1-ops expect_ok crew signal env-probe-absent "The env probe is absent from the IIS logs." --kind question
has "$(cat "$T/race.log")" "atlas-tiles-are-cached"
eq "$(git --git-dir "$wb" log --format=%s "$before"..main | wc -l | tr -d ' ')" "3"
eq "$(git --git-dir "$wb" rev-list --merges main | wc -l | tr -d ' ')" "0"
has "$(git --git-dir "$wb" log -1 --format=%s main)" "env-probe-absent (swb-1-ops)"
has "$(git --git-dir "$wb" show "main:signals/$cap/capture.md")" "signals: 2"
git --git-dir "$wb" cat-file -e "main:signals/$cap/02-env-probe-absent.md" || fail "no second signal"
git --git-dir "$wb" cat-file -e "main:signals/$today-atl-1-ops/01-atlas-tiles-are-cached.md" || fail "the racing signal was lost"
ok "a push refused because main moved is replayed on the new tip"
