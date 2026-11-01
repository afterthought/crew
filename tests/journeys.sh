# The journeys' world, which each sources after lib.sh: a bolt world whose kit's GitHub another clone pushes to,
# wldn's blueprints on mac-studio and atlas-kit there; and the helpers the journeys read it with.
bolt_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
clone WilldanGroup/willdan-blueprints "$(space mac-studio willdan)/willdan-blueprints/main"
kit mac-studio willdan atlas-kit >/dev/null
# The kit's GitHub, which kit made, and another clone that pushes to it.
r=$(remote WilldanGroup/switchboard-kit)
other=$T/elsewhere; git clone -q "$r" "$other"
pushed() { git -C "$other" pull -q --rebase origin main; echo "$1" > "$other/$1"; commit_all "$other" "feat: $1"; git -C "$other" push -q origin main; }
# field <host> <act> <field> [object]: a field of that host's last entry of the act naming the object
field() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and (len(sys.argv) < 4 or sys.argv[3] in e["On"])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" ${4:+"$4"} | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
count() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null' | grep -c "^Act: $2\$" || true; }
launched() { jq -r --arg a "$1" 'select(.agent == $a) | "\(.cwd) \(.argv | index("--resume") as $i | if $i then "resumed" else "fresh" end)"' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
greetings() { grep -c "^$1 $2 agent prompt $3 '\[crew\]" "$CREW_TEST_LOG" || true; }
