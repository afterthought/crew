# Who writes the plan directly: the user, everything; the planner, only through proposals; a conductor narrows, orders
# and sets dependencies within the bolt its team holds; the design agent queues; a dispatcher gives bolts; the main
# level's ops lands them. Any other plan write by an agent crew started is refused, naming the planner.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
tip() { git --git-dir "$ws" rev-parse wldn/main; }
refusals() { as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null' | grep -c "^Refused:" || true; }

expect_ok crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew bolt new empty-one "Nothing yet." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew unit add b "Unit b." --bolt tenant-environments >/dev/null
crew unit add c "Unit c." --bolt console-pages >/dev/null
ok "the user writes the plan directly"

r0=$(refusals); before=$(tip)
CREW_AGENT=wldn-planner expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew unit add" \
  crew unit add d "Unit d." --repo switchboard-kit
CREW_AGENT=wldn-planner expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew bolt new" \
  crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit
eq "$(tip)" "$before"
ok "the planner's direct writes are refused, naming crew plan propose"

CREW_AGENT=wldn-dispatch-chuck-herdr-alpha expect_ok crew bolt give swb-1 tenant-environments
CREW_AGENT=swb-1-conductor expect_ok crew unit order b --first
CREW_AGENT=swb-1-conductor expect_ok crew unit after a b
CREW_AGENT=swb-1-conductor expect_ok crew unit split b "Unit b, narrowed." --into b-rest "The rest of b."
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor writes only units of the bolt swb-1 holds, and c is in bolt console-pages: tell wldn-planner" \
  crew unit order c --first
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor does not write the plan with crew unit add --bolt: tell wldn-planner, who proposes it" \
  crew unit add e "Unit e." --bolt tenant-environments
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor does not write the plan with crew unit move: tell wldn-planner" crew unit move c tenant-environments
ok "a dispatcher gives a bolt; a conductor narrows, orders and sets dependencies within its own bolt, and nothing else"

CREW_AGENT=wldn-design expect_ok crew unit add queued "Queued work." --repo switchboard-kit
CREW_AGENT=wldn-design expect_fail "wldn-design does not write the plan with crew unit add --bolt: tell wldn-planner" crew unit add f "Unit f." --bolt console-pages
CREW_AGENT=wldn-design expect_fail "wldn-design does not write the plan with crew bolt new: tell wldn-planner" crew bolt new y "y" --repo switchboard-kit
ok "the design agent queues units, and places none"

CREW_AGENT=swb-1-unit-1 expect_fail "swb-1-unit-1 does not write the plan with crew unit order: tell wldn-planner" crew unit order a --first
CREW_AGENT=wldn-operator-mac-studio expect_fail "wldn-operator-mac-studio does not write the plan with crew unit drop: tell wldn-planner" crew unit drop a "gone"
ok "a unit slot's agent and the operator agent write no plan"

crew bolt give swb-2 empty-one >/dev/null 2>&1
CREW_AGENT=wldn-ops expect_ok crew bolt land empty-one
CREW_AGENT=wldn-ops expect_fail "wldn-ops does not write the plan with crew bolt new: tell wldn-planner" crew bolt new z "z" --repo switchboard-kit
ok "the main level's ops lands a bolt, and writes nothing else"

eq "$(( $(refusals) - r0 ))" "10"
ok "each refusal leaves a Refused entry"
