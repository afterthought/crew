# A command reads each kit once and fetches the state branch once on each host it runs on, however many steps it has
# (plan.12): crew status with three units in flight fetches once and gathers once on the team's host and starts no
# openspec, and so does crew unit run before it makes the unit's place. A write whose push finds the branch moved
# fetches it afresh and applies itself again. Nothing a command kept for its steps is left once it ends, refused or
# not, and a reading a killed command left goes once it is a day old.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c d; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
for u in a b c; do crew unit run $u construct >/dev/null; done
change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
change "$kd/places/b" b 0 3; commit_all "$kd/places/b" "docs(b): the change"
change "$kd/places/c" c 0 3; rm "$kd/places/c/openspec/changes/c/design.md"; commit_all "$kd/places/c" "docs(c): the change, no design yet"
rewrite "$kd/places/b/openspec/changes/b/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'; commit_all "$kd/places/b" "feat(b): task 1"

# Shims ahead of the real git, python3 and openspec log, per host, each fetch of a state branch into crew's cache,
# each gather.py run, and each openspec start.
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@" that logs <what>> <what>
  printf '#!/usr/bin/env bash\nif %s; then echo "${CREW_TEST_HOST:-?} %s" >> %q; fi\nexec %q "$@"\n' "$2" "$3" "$T/reads.log" "$(command -v "$1")" > "$T/shim/$1"
  chmod +x "$T/shim/$1"
}
shim git '[[ " $* " == *" fetch "*refs/crew/* ]]' fetch
shim python3 '[[ ${1:-} == - ]]' gather
shim openspec true openspec
export PATH="$T/shim:$PATH"
reads() { grep -c "^$1 $2\$" "$T/reads.log" || true; }
left() { ls -A "$(home_of "$1")/.cache/crew/reads" 2>/dev/null || true; }

: > "$T/reads.log"
expect_ok crew status swb-1
has "$out" "swb-1-unit-1"
has "$(grep swb-1-unit-1 <<<"$out")" "a  planned"
has "$(grep swb-1-unit-2 <<<"$out")" "b  code 1/3"
has "$(grep swb-1-unit-3 <<<"$out")" "c  construct"
eq "$(reads $box fetch) $(reads $box gather) $(reads $box openspec)" "1 1 0"
eq "$(reads mac-studio fetch) $(reads mac-studio gather) $(reads mac-studio openspec)" "0 0 0"
eq "$(left $box)$(left mac-studio)" ""
ok "crew status with three units in flight fetches once and gathers once on the team's host, and starts no openspec"

: > "$T/reads.log"
expect_ok crew unit run d construct
has "$out" "swb-1-unit-4 has d: construct"
eq "$(reads $box fetch) $(reads $box gather) $(reads $box openspec)" "1 1 0"
eq "$(reads mac-studio fetch) $(reads mac-studio gather)" "1 0"
eq "$(left $box)$(left mac-studio)" ""
ok "crew unit run fetches once and reads the kit once on the team's host before it makes the place"

# Construct run again on b, in code, marks it amended: a write whose push finds another write landed meanwhile.
race WilldanGroup/crew-state mac-studio "" unit add raced "A raced unit." --bolt tenant-environments
: > "$T/reads.log"
expect_ok crew unit run b construct
[[ ! -f $T/race ]] || fail "the competing write never ran"
log=$(git --git-dir "$ws" log -2 --format='%s' wldn/main)
eq "$log" "plan(tenant-environments): b amended, construct runs again ($me@mac-studio)"$'\n'"plan(tenant-environments): add raced ($me@mac-studio)"
eq "$(reads $box fetch)" "2"
eq "$(left $box)$(left mac-studio)" ""
ok "a write that finds the branch moved since its command fetched it fetches afresh and lands on the new tip"

expect_fail "unit d is in construct" crew unit run d code
eq "$(left $box)$(left mac-studio)" ""
ok "a refused command leaves no reading"

stale=$(home_of $box)/.cache/crew/reads
mkdir -p "$stale/OLDOLDOL" "$stale/NEWNEWNE"; echo $box > "$stale/OLDOLDOL/host"; touch -t 202601010000 "$stale/OLDOLDOL"
expect_ok crew status swb-1
eq "$(left $box)" "NEWNEWNE"
ok "a reading a killed command left goes once it is a day old"
