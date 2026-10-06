# The run record: every command that moves work appends one entry per act, after the act, to a recutils file of the
# day on the host where it ran, naming who asked and their Claude session, what it acted on and came from, and the
# commit it wrote. A refusal of a write is an entry; a read is not. No entry holds text anyone typed, and a record
# that can't be written changes nothing about the command.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=chuck-herdr-alpha
wb=$(blueprints WilldanGroup/willdan-blueprints); ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
clone WilldanGroup/willdan-blueprints "$(space chuck-herdr-alpha willdan)/willdan-blueprints/main"
runs() { ls "$(home_of "$1")"/.local/state/crew/"${2:-wldn}"/runs/*/*.rec 2>/dev/null || true; }
emit() { local h=$1; shift; as "$h" python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@"; }
# last <host> <act> [label]: the last entry of the act on the host, as JSON ({} when there is none)
last() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/%s/runs/*/*.rec" % sys.argv[3])))
      for e in record.parse(open(f).read()) if e["Act"] == sys.argv[2]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" "${3:-wldn}"
}
field() { last "$1" "$2" "${4:-wldn}" | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'; }
count() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/'"${3:-wldn}"'/runs/*/*.rec 2>/dev/null' | grep -c "^Act: $2\$" || true; }
tip() { git --git-dir "$ws" rev-parse "$1"; }

emit $box --act test.one --on unit/a >/dev/null & emit $box --act test.two --on unit/b >/dev/null & wait
f=$(runs $box)
eq "$(wc -l <<<"$f" | tr -d ' ')" "1"
eq "$f" "$(home_of $box)/.local/state/crew/wldn/runs/$box/$(date -u +%F).rec"
recfix --check "$f" || fail "the run record fails recfix --check"
eq "$(recsel -C -t Entry -P Act "$f" | sort | tr '\n' ' ')" "test.one test.two "
eq "$(recsel -C -t Entry -e "Act = 'test.one'" -P On,Host "$f")" $'unit/a\n'"$box"
[[ $(recsel -t Entry -e "Act = 'test.one'" -P Id "$f") == *"-$box-"* ]] || fail "an entry's id names its host"
ok "two entries written at once are both whole, in the day's file on the host, and the file passes recfix --check"

st=$(home_of mac-studio)/.local/state/crew; mkdir -p "$st"; chmod 555 "$st"
out=$(crew state init wldn 2>"$T/err") || fail "state init failed when its record could not be written"
eq "$out" "wldn/main of WilldanGroup/crew-state $(tip wldn/main | cut -c1-7): started an empty plan; added moves.rec with 0 moves of WilldanGroup/willdan-blueprints at $(git --git-dir "$wb" rev-parse --short main)"
eq "$(wc -l < "$T/err" | tr -d ' ')" "2"
eq "$(grep -c "crew: the run record at $st/wldn/runs/mac-studio/.* could not be written" "$T/err")" "2"
chmod 755 "$st"
ab=$(blueprints afterthought/blueprints); blueprints agentplot/blueprints >/dev/null; as=$(remote afterthought/crew-state)
crew state init madswan >/dev/null
eq "$(field mac-studio state.init On madswan)" "plan/madswan"
eq "$(field mac-studio state.init Commit madswan)" "afterthought/crew-state@$(git --git-dir "$as" rev-parse madswan/main)"
ok "a record that can't be written is said in one line per entry, and the command's output and exit are unchanged; a flywheel's start is entries"

p=$(as $box herdr --session wldn-3 workspace create --cwd / --label wldn | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$p" wldn-planner
CREW_AGENT=wldn-planner emit $box --act test.agent >/dev/null
eq "$(field $box test.agent By)" "wldn-planner"
eq "$(field $box test.agent Session)" "$box:sid-$p"
emit $box --act test.user >/dev/null
eq "$(field $box test.user By)" "$(python3 -c 'import getpass; print(getpass.getuser())')@$box"
eq "$(field $box test.user Session)" ""
CREW_AGENT=wldn-design emit $box --act test.nosession >/dev/null
eq "$(field $box test.nosession By)" "wldn-design"
eq "$(field $box test.nosession Session)" ""
CREW_SESSION=mac-studio:sid-elsewhere CREW_AGENT=wldn-planner emit $box --act test.carried >/dev/null
eq "$(field $box test.carried Session)" "mac-studio:sid-elsewhere"
ok "an agent's entry names its session as herdr reports it; the user's and an agent herdr doesn't know have none; a carried session wins"

export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments ZQXA." --repo switchboard-kit >/dev/null
eq "$(field mac-studio bolt.new On)" "bolt/tenant-environments"
eq "$(field mac-studio bolt.new Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
eq "$(field mac-studio bolt.new Why)" "plan(tenant-environments): add the bolt"
eq "$(field mac-studio bolt.new By)" "$me@mac-studio"
crew bolt new apex-zones "Apex zones ZQXB." --repo switchboard-kit >/dev/null
crew bolt order apex-zones --first >/dev/null
eq "$(field mac-studio bolt.order On)" "bolt/apex-zones"
eq "$(field mac-studio bolt.order Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
crew unit add a "Unit a ZQXC." --bolt tenant-environments >/dev/null
eq "$(field mac-studio unit.add On)" "unit/a bolt/tenant-environments"
crew unit add b "Unit b ZQXD." --bolt tenant-environments >/dev/null
crew unit add q "Queued ZQXE." --repo switchboard-kit >/dev/null
eq "$(field mac-studio unit.add On)" "unit/q queue/switchboard-kit"
eq "$(field mac-studio unit.add Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
crew unit split q "Narrowed ZQXF." --into q2 "The rest ZQXG." >/dev/null
eq "$(field mac-studio unit.split On)" "unit/q unit/q2"
eq "$(field mac-studio unit.split From)" "unit/q"
crew unit order b --first >/dev/null
eq "$(field mac-studio unit.order On)" "unit/b bolt/tenant-environments"
crew unit after a b >/dev/null
eq "$(field mac-studio unit.after On)" "unit/a bolt/tenant-environments"
crew unit move q2 tenant-environments >/dev/null
eq "$(field mac-studio unit.move On)" "unit/q2 bolt/tenant-environments"
eq "$(field mac-studio unit.move From)" "queue/switchboard-kit"
crew unit drop q2 "No longer wanted ZQXH." >/dev/null
eq "$(field mac-studio unit.drop On)" "unit/q2 bolt/tenant-environments"
eq "$(field mac-studio unit.drop Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
crew bolt drop apex-zones "Not now ZQXI." >/dev/null
eq "$(field mac-studio bolt.drop On)" "bolt/apex-zones"
eq "$(field mac-studio bolt.drop Why)" "plan(apex-zones): drop the bolt"
ok "each plan write is one entry naming its act, its objects and the plan's commit, written where it ran"

id_of() { sed -n 's/^signal \([^: ]*\)[: ].*/\1/p' <<<"$1"; }
sig=$(id_of "$(CREW_AGENT=swb-1-conductor crew signal the-banner-flickers "The banner flickers ZQXJ." --kind ask --excerpt "banner repaints ZQXR")")
eq "$(field mac-studio capture On)" "signals/$sig"
eq "$(field mac-studio capture Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
eq "$(field mac-studio capture By)" "swb-1-conductor"
CREW_AGENT=wldn-design crew signal move "$sig" drop --reason "Noise ZQXK." >/dev/null
eq "$(field mac-studio signal.move On)" "signals/$sig"
eq "$(field mac-studio signal.move Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
sig2=$(id_of "$(CREW_AGENT=swb-1-conductor crew signal cfn-nag "Add a security check ZQXL." --kind ask --excerpt "no security check ZQXS")")
crew unit add cfn-nag-security-check "A security check ZQXM." --repo switchboard-kit --signal "$sig2" >/dev/null
eq "$(field mac-studio unit.add On)" "unit/cfn-nag-security-check queue/switchboard-kit"
eq "$(field mac-studio unit.add From)" "signals/$sig2"
eq "$(field mac-studio signal.move On)" "signals/$sig2 unit/cfn-nag-security-check"
eq "$(field mac-studio unit.add Commit)" "$(field mac-studio signal.move Commit)"
eq "$(field mac-studio signal.move Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
ok "a capture, a curation move, and a unit queued from a signal with its route each name the signal and the commit"

crew bolt give swb-1 >/dev/null 2>&1
eq "$(field mac-studio bolt.give On)" "bolt/tenant-environments team/swb-1"
eq "$(field mac-studio bolt.give Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
pl=$(place "$k" tenant-environments b); change "$pl" b 0 2; commit_all "$pl" "docs(b): the change"
CREW_AGENT=swb-1-conductor crew unit approve b >/dev/null
eq "$(field mac-studio unit.approve On)" "unit/b"
eq "$(field mac-studio unit.approve Commit)" "WilldanGroup/switchboard-kit@$(git -C "$k" rev-parse unit/b)"
crew bolt new solo "One unit ZQXN." --repo switchboard-kit >/dev/null
crew unit add solo-one "Solo ZQXO." --bolt solo >/dev/null
crew bolt give swb-2 solo >/dev/null 2>&1
change "$k" solo-one 3 3; commit_all "$k" "feat: solo-one"; git -C "$kd/bolts/solo" merge -q --ff-only main
crew bolt land solo >/dev/null
eq "$(field mac-studio bolt.land On)" "bolt/solo unit/solo-one"
eq "$(field mac-studio bolt.land Commit)" "WilldanGroup/crew-state@$(tip wldn/main)"
ok "a give is recorded with the team once its worktree exists, an approval with the kit's commit, a landing with its units"

before=$(count mac-studio state.init)
crew state init wldn >/dev/null
eq "$(count mac-studio state.init)" "$before"
before=$(count mac-studio unit.drop)
crew unit drop a "Gone ZQXP." >/dev/null
crew unit drop a "Gone again ZQXQ." >/dev/null 2>&1 && fail "the second drop was not refused"
eq "$(count mac-studio unit.drop)" "$((before + 2))"
eq "$(field mac-studio unit.drop On)" "unit/a"
has "$(field mac-studio unit.drop Refused)" "no unit a in the plans of wldn"
n=$(cat $(runs mac-studio) | grep -c '^Id:')
crew bolts nope >/dev/null 2>&1 || true
crew bolts >/dev/null 2>&1 || true
eq "$(cat $(runs mac-studio) | grep -c '^Id:')" "$n"
ok "a refused write is one entry with crew's reason; a read writes nothing"

all=$(cat $(runs mac-studio) $(runs $box) 2>/dev/null)
for typed in ZQXA ZQXB ZQXC ZQXD ZQXE ZQXF ZQXG ZQXH ZQXI ZQXJ ZQXK ZQXL ZQXM ZQXN ZQXO ZQXP ZQXQ ZQXR ZQXS; do
  [[ $all != *"$typed"* ]] || fail "the run record holds typed text ($typed)"
done
ok "no entry holds an intent, a goal, a reason, an assertion or an excerpt"
