# crew sites: each host's bolts, units and fixes, the URL of each running dev server from the host's portless routes
# matched by devurl's names, the URL rule for where crew runs, and an unreachable host named.
. "$TESTS/lib.sh"
export PATH="$TESTS/stubs-sites:$PATH"
team_world
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
echo chuck-herdr-alpha > "$(home_of chuck-herdr-alpha)/.devurl-label"; echo studio > "$(home_of mac-studio)/.devurl-label"
export CREW_LABEL=wldn CREW_AGENT=wldn-planner
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new atlas-maps "Atlas draws maps." --repo atlas-kit >/dev/null
crew unit add an-installs-apex-is-its-own-zone "An apex is a zone." --bolt tenant-environments >/dev/null
crew unit add quiet-unit "No server." --bolt tenant-environments >/dev/null
crew unit add map-one "Map one." --bolt atlas-maps >/dev/null
crew bolt give swb-1 >/dev/null 2>&1; crew bolt give atl-1 >/dev/null 2>&1
place "$k" tenant-environments an-installs-apex-is-its-own-zone >/dev/null; place "$k" tenant-environments quiet-unit >/dev/null
git -C "$k" worktree add -q --track -b fix/edge-sign-in "$kd/places/fix-edge-sign-in" bolt/tenant-environments
place "$ak" atlas-maps map-one >/dev/null
printf 'unit-an-installs-apex-is-its-own-zone--switchboard-kit\nbolt-tenant-environments--switchboard-kit\n' > "$(home_of chuck-herdr-alpha)/.portless-routes"
printf 'unit-map-one--atlas-kit\n' > "$(home_of mac-studio)/.portless-routes"
j() { jq -r "$1" <<<"$json"; }

: > "$CREW_TEST_LOG"
expect_ok crew sites wldn --json; json=$out
eq "$(grep -c ' ssh chuck-herdr-alpha ' "$CREW_TEST_LOG")" "1"
box='.partitions[0].hosts[] | select(.host == "chuck-herdr-alpha") | .bolts[0]'
eq "$(j "$box | .url")" "https://bolt-tenant-environments--switchboard-kit--chuck-herdr-alpha.dev.swancloud.net"
eq "$(j "$box | .units[] | select(.unit == \"an-installs-apex-is-its-own-zone\") | .url")" "https://unit-an-installs-apex-is-its-own-zone--switchboard-kit--chuck-herdr-alpha.dev.swancloud.net"
eq "$(j "$box | .units[] | select(.unit == \"quiet-unit\") | \"\(.url) \(.worktree)\"")" "null $kd/places/quiet-unit"
eq "$(j "$box | .fixes[0] | \"\(.fix) \(.url)\"")" "fix/edge-sign-in null"
has "$(j '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0].url')" "https://unit-map-one--atlas-kit.local"
ok "from mac-studio: the box's servers by their dev.swancloud.net names, mac-studio's by its local name, none where none runs"

expect_ok crew sites wldn
has "$out" "unit-an-installs-apex-is-its-own-zone--switchboard-kit--chuck-herdr-alpha.dev.swancloud.net"
has "$out" "places/quiet-unit"; has "$out" "no server running"
lacks "$out" "open from a Mac"

HOST=chuck-herdr-alpha expect_ok crew sites wldn --json; json=$out
has "$(j "$box | .units[] | select(.unit == \"an-installs-apex-is-its-own-zone\") | .url")" "https://unit-an-installs-apex-is-its-own-zone--switchboard-kit.local"
eq "$(j '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0] | "\(.url) \(.note)"')" "https://unit-map-one--atlas-kit--studio.dev.swancloud.net open from a Mac"
HOST=chuck-herdr-alpha expect_ok crew sites wldn; has "$out" "unit-map-one--atlas-kit--studio.dev.swancloud.net  (open from a Mac)"
ok "from the box: its own servers by their local names, mac-studio's dev.swancloud.net names marked to open from a Mac"

rm "$(home_of mac-studio)/.devurl-label"
HOST=chuck-herdr-alpha expect_ok crew sites wldn --json; json=$out
eq "$(j '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0] | "\(.url) \(.note)"')" "null running, but mac-studio does not publish its dev servers"
echo studio > "$(home_of mac-studio)/.devurl-label"

echo chuck-herdr-alpha > "$T/down"
expect_ok crew sites wldn --json; json=$out
eq "$(j '.partitions[0].hosts[] | select(.host == "chuck-herdr-alpha") | "\(.reachable) \(.bolts[0].bolt) \(.bolts[0].worktree)"')" "false tenant-environments null"
has "$(j '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0].url')" "unit-map-one--atlas-kit.local"
expect_ok crew sites wldn; has "$out" "chuck-herdr-alpha  did not answer"; has "$out" "    tenant-environments  (swb-1)"
ok "an unreachable host's bolts are listed from the plan, marked, and the other host's sites as usual"
