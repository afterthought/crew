# crew sites on mac-studio against a real dev server: a scratch kit whose place runs devurl-serve, named by the
# real devurl and found among the routes of a real portless proxy. The proxy is one of the test's own, with its
# own state directory on an unprivileged port, so the user's proxy is never touched; it is stopped at the end.
# Opt in with CREW_TEST_LIVE=1, on mac-studio.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
if [[ ${CREW_TEST_LIVE:-} != 1 ]]; then echo "skipped: run with CREW_TEST_LIVE=1 on mac-studio"; exit 0; fi
[[ $(/bin/hostname -s) == mac-studio ]] || fail "the live sites test runs on mac-studio"
for c in devurl devurl-serve portless; do command -v $c >/dev/null || fail "the live sites test needs $c"; done
export PORTLESS_STATE_DIR=$T/portless PORTLESS_LAN=0 PORTLESS_HTTPS=0 PORTLESS_PORT=13557 PORTLESS_SYNC_HOSTS=0
mkdir -p "$PORTLESS_STATE_DIR"
stop() { pkill -f "http.server [0-9]* --bind 127.0.0.1 --directory $T" 2>/dev/null || true; timeout 20 portless proxy stop </dev/null >/dev/null 2>&1 || true; }
trap stop EXIT
timeout 30 portless proxy start --port "$PORTLESS_PORT" --no-tls </dev/null >/dev/null 2>&1 || fail "the test's proxy did not start"

team_world
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
git -C "$ak" remote add origin https://github.com/WilldanGroup/atlas-kit.git
export CREW_LABEL=wldn
crew bolt new atlas-maps "Atlas draws maps." --repo atlas-kit >/dev/null
crew unit add map-one "Map one." --bolt atlas-maps >/dev/null
crew bolt give atl-1 >/dev/null 2>&1
pm=$(place "$ak" atlas-maps map-one)
name=$(cd "$pm" && devurl | awk '$1 == "here" {print $2}' | sed -e 's#^https://##' -e 's#\.[a-z]*$##')
eq "$name" "unit-map-one--atlas-kit"

(cd "$pm" && exec timeout 120 devurl-serve sh -c "exec python3 -m http.server \"\$PORT\" --bind 127.0.0.1 --directory $T" </dev/null > "$T/serve.log" 2>&1) &
for _ in $(seq 60); do portless list 2>/dev/null | grep -q "$name" && break; /bin/sleep 0.5; done
portless list | grep -q "$name" || { cat "$T/serve.log"; fail "devurl-serve's route never appeared"; }

expect_ok crew sites wldn --json; json=$out
eq "$(jq -r '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0].units[0] | "\(.unit) \(.url)"' <<<"$json")" "map-one http://$name.localhost:$PORTLESS_PORT"
eq "$(jq -r '.partitions[0].hosts[] | select(.host == "mac-studio") | .bolts[0] | "\(.worktree) \(.url)"' <<<"$json")" "$akd/bolts/atlas-maps null"
eq "$(jq -r '.partitions[0].hosts[] | select(.host == "chuck-herdr-alpha") | .bolts | length' <<<"$json")" "0"
expect_ok crew sites wldn
has "$out" "map-one"; has "$out" "places/map-one"; has "$out" "http://$name.localhost:$PORTLESS_PORT"
echo "$out"
ok "on mac-studio, a place running devurl-serve is listed under its bolt with its server's URL"
