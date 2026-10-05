# A write to an active bolt by anyone other than its conductor sends that conductor the commit's subject.
. "$TESTS/lib.sh"
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
CREW_AGENT=wldn-dispatch-chuck-herdr-alpha crew bolt give swb-1 tenant-environments >/dev/null 2>&1
CREW_AGENT=wldn-dispatch-chuck-herdr-alpha crew bolt give swb-2 console-pages >/dev/null 2>&1
for team in swb-1 swb-2; do  # the conductors, up in the stub herdr on the box
  p=$(as chuck-herdr-alpha herdr --session wldn-1 workspace create --cwd / --label $team | jq -r .result.root_pane.pane_id)
  as chuck-herdr-alpha herdr --session wldn-1 stub agent "$p" $team-conductor
done
prompts() { grep "^chuck-herdr-alpha wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }  # what the stub herdr received

: > "$CREW_TEST_LOG"
crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
eq "$(prompts swb-1)" "chuck-herdr-alpha wldn-1 agent prompt swb-1-conductor 'plan(tenant-environments): add the-deploy-names-its-host-tenant ($me@mac-studio)'"
eq "$(prompts swb-2)" ""
ok "a unit added to swb-1's bolt by someone else sends swb-1's conductor the commit's subject"

crew unit add a-tenant-creates-its-environments "A tenant creates them." --bolt tenant-environments >/dev/null
: > "$CREW_TEST_LOG"
CREW_AGENT=swb-1-conductor crew unit order a-tenant-creates-its-environments --first >/dev/null
eq "$(prompts swb-1)" ""
ok "the conductor's own write sends it nothing"

: > "$CREW_TEST_LOG"
crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null
eq "$(grep -c ' wldn-1 agent prompt ' "$CREW_TEST_LOG" || true)" "0"
ok "a write to a bolt no team holds tells no one"

: > "$CREW_TEST_LOG"
crew unit move a-tenant-creates-its-environments console-pages >/dev/null
has "$(prompts swb-1)" "plan(console-pages): move a-tenant-creates-its-environments from tenant-environments ($me@mac-studio)"
has "$(prompts swb-2)" "plan(console-pages): move a-tenant-creates-its-environments from tenant-environments ($me@mac-studio)"
ok "a move between two teams' bolts tells both conductors"

: > "$CREW_TEST_LOG"
CREW_AGENT=wldn-design expect_ok crew tell swb-1-conductor "The tenant's zone is its own."
grep -q "^chuck-herdr-alpha wldn-1 agent prompt swb-1-conductor 'The tenant'\"'\"'s zone is its own.'" "$CREW_TEST_LOG" || fail "crew tell sent nothing"
expect_fail "could not tell wldn-design on chuck-herdr-alpha" crew tell wldn-design "anyone there?"
expect_fail "no agent somebody: crew starts none by that name" crew tell somebody "hello"
ok "crew tell reaches an agent by name on its host, and says when it is not up"

# The partition's dispatchers hear of a bolt added, and of one landed or dropped that frees a team.
p=$(as chuck-herdr-alpha herdr --session wldn-3 workspace create --cwd / --label "wldn dispatch" | jq -r .result.root_pane.pane_id)
as chuck-herdr-alpha herdr --session wldn-3 stub agent "$p" wldn-dispatch-chuck-herdr-alpha
told() { grep "^chuck-herdr-alpha wldn-3 agent prompt wldn-dispatch-chuck-herdr-alpha " "$CREW_TEST_LOG" || true; }

: > "$CREW_TEST_LOG"
crew bolt new edge-signins "Sign-ins at the edge." --repo switchboard-kit >/dev/null
eq "$(told)" "chuck-herdr-alpha wldn-3 agent prompt wldn-dispatch-chuck-herdr-alpha 'plan(edge-signins): add the bolt ($me@mac-studio). Give a free team its next bolt.'"
grep -q "agent prompt wldn-dispatch-mac-studio" "$CREW_TEST_LOG" && fail "a dispatcher that is not up was told"
ok "a bolt added tells the dispatchers that are up"

crew bolt new later-work "Later." --repo switchboard-kit >/dev/null
: > "$CREW_TEST_LOG"
crew unit add edge-one "Edge one." --bolt edge-signins >/dev/null
eq "$(told)" ""
crew bolt drop later-work "not needed" >/dev/null
eq "$(told)" ""
ok "a unit added, or a dropped bolt no team held, tells no dispatcher"

: > "$CREW_TEST_LOG"
crew bolt drop console-pages "folded into tenant-environments" --requeue >/dev/null
has "$(told)" "plan(console-pages): drop the bolt, its units queued ($me@mac-studio). Give a free team its next bolt."
ok "a dropped bolt a team held tells the dispatchers, since the team is free"
