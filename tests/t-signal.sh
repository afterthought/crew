# A finding written as a signal in the partition's first blueprints repo, by path on main, pushed and replayed
# when main moved; and every move, curation's and the route, written through crew to moves.rec on the flywheel's
# branch of its state repository, never merged.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
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

# Curation's moves go through crew, one per signal.
CREW_AGENT=wldn-design expect_ok crew signal move "$today-atl-1-ops/01-atlas-tiles-are-cached" answered --target "books/atlas-kit/src/tiles.md" --reason "the book already says a day"
has "$out" "wldn/main"; has "$out" "signals($today-atl-1-ops/01-atlas-tiles-are-cached): answered (wldn-design)"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v "^runs/")" "moves.rec"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "signals($today-atl-1-ops/01-atlas-tiles-are-cached): answered (wldn-design)"
CREW_AGENT=wldn-design expect_fail "already has its move: answered" crew signal move "$today-atl-1-ops/01-atlas-tiles-are-cached" drop --reason "twice"
CREW_AGENT=wldn-design expect_fail "no signal 2026-01-01-x/01-y in WilldanGroup/willdan-blueprints" crew signal move 2026-01-01-x/01-y drop --reason "none"
CREW_AGENT=wldn-design expect_fail "a drop gives its reason (--reason)" crew signal move "$cap/02-env-probe-absent" drop
CREW_AGENT=wldn-design expect_fail "a attach move names its target" crew signal move "$cap/02-env-probe-absent" attach
CREW_AGENT=wldn-design expect_fail "invalid choice: 'route'" crew signal move "$cap/02-env-probe-absent" route
ok "crew signal move records one move per signal, with its target or reason"

# A route written on the box while curation writes a drop on mac-studio: both land, one after the other, unmerged.
echo refs/heads/wldn/main > "$T/race.ref"
race WilldanGroup/crew-state mac-studio wldn-design signal move "$cap/02-env-probe-absent" drop --reason "a duplicate of the WAF finding"
tip=$(git --git-dir "$ws" rev-parse wldn/main)
HOST=chuck-herdr-alpha CREW_AGENT=wldn-planner expect_ok crew unit add the-waf-blocks "The WAF blocks what its rules say." --repo switchboard-kit --signal "$cap/01-waf-counts-instead-of-blocking"
[[ ! -f $T/race ]] || fail "the competing move never ran"
eq "$(git --git-dir "$ws" log --format=%s "$tip"..wldn/main)" "plan(queue): add the-waf-blocks (wldn-planner)"$'\n'"signals($cap/02-env-probe-absent): drop (wldn-design)"
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"
recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
eq "$(recsel -C -t Move -P Move "$T/moves.rec" | tr '\n' ' ')" "answered drop route "
eq "$(git --git-dir "$wb" show main:signals/moves.rec | recsel -t Move -c)" "0"
ok "a route on the box and a drop on mac-studio both land unmerged on the branch, and moves.rec passes recfix --check"
