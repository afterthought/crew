# crew reads a unit's tasks and planning the way openspec does (plan.12): on the same worktree, for every case openspec
# treats differently, gather.py's tasks, planning and open tasks are what `openspec list`, `openspec status` and, where
# it lists them, `openspec instructions apply` say there, and ticks() at the unit's branch is what `openspec list` counts. A change
# of openspec's spec-driven workflow is read from its files without starting openspec; one naming another workflow,
# one in a kit that redefines spec-driven, or one whose metadata crew does not read is read through openspec.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
gitconfig "$HOME"
export XDG_DATA_HOME=$T/data
k=$(kit mac-studio work facts); kd=$(dirname "$k")
direct=() handed=()

# begin <case> direct|openspec: the case's place, on unit/<case> from main, holding a change with planning complete
# and two of three tasks ticked, for the case to change; the case is read the way its second word says
begin() {
  p=$kd/places/$1
  git -C "$k" worktree add -q -b "unit/$1" "$p" main
  change "$p" "$1" 2 3
  c=$p/openspec/changes/$1
  if [[ $2 == direct ]]; then direct+=("$1"); else handed+=("$1"); fi
}
done_() { commit_all "$p" "test: ${p##*/}"; }

begin basic direct
printf -- '## 1. Work\n\n- [ ] 1.1 open\n- [x] 1.2 ticked\n- [X] 1.3 ticked big\n' > "$c/tasks.md"; done_
begin markers direct
printf -- '* [ ] star\n+ [x] plus\n1. [ ] numbered\n2) [x] paren\n123456789. [ ] nine digits\n1234567890. [ ] ten digits\n' > "$c/tasks.md"; done_
begin nested direct
printf -- '- [ ] 1.1 parent\n  - [ ] 1.1.1 child\n    - [x] 1.1.1.1 grandchild\n\t- [ ] tabbed\n' > "$c/tasks.md"; done_
begin odd-boxes direct
printf -- '- [] empty\n- [~] tilde\n- [ x ] padded\n- [ ](link) blank box with a link\n- [1] one\n- [x]tight\n' > "$c/tasks.md"; done_
begin links direct
printf -- '- [A](u)\n- [design](./design.md)\n- [WIP] w\n- [A][ref]\n- [ ] a real one\n' > "$c/tasks.md"; done_
begin fenced direct
printf -- '- [x] outside\n\n```\n- [ ] inside a fence\n```\n<!-- - [ ] in a comment -->\n' > "$c/tasks.md"; done_
begin crlf direct
printf -- '## 1. Work\r\n\r\n- [ ] 1.1 a\r\n- [x] 1.2 b\r\n- [ ] 1.3 c  \r\n' > "$c/tasks.md"; done_
begin spaces direct  # a byte-order mark and a no-break space are JavaScript's \s; a file separator is not
printf '\357\273\277- [ ] after a mark\n\302\240- [x] after a no-break space\n-\034[ ] after a file separator\n- [ ]\302\240trailing\302\240\n' > "$c/tasks.md"; done_
begin no-tasks direct
rm "$c/tasks.md"; done_
begin no-specs direct
rm -r "$c/specs"; done_
begin hidden-spec direct
rm -r "$c/specs"; mkdir -p "$c/specs"; echo "# hidden" > "$c/specs/.hidden.md"; done_
begin hidden-dir direct
rm -r "$c/specs"; mkdir -p "$c/specs/.d"; echo "# hidden" > "$c/specs/.d/spec.md"; done_
begin deep-spec direct
rm -r "$c/specs"; mkdir -p "$c/specs/a/b"; echo "# deep" > "$c/specs/a/b/spec.md"; done_
begin not-markdown direct
rm -r "$c/specs"; mkdir -p "$c/specs/x"; echo "# text" > "$c/specs/x/spec.txt"; done_
begin skip-specs direct
rm -r "$c/specs"; printf 'schema: spec-driven\ncreated: 2026-10-08\nskip_specs: true\n' > "$c/.openspec.yaml"; done_
begin skip-false direct
rm -r "$c/specs"; printf 'schema: spec-driven\nskip_specs: false\n' > "$c/.openspec.yaml"; done_
begin no-design direct
rm "$c/design.md"; done_
begin no-change direct
rm -r "$c"
begin config-context direct  # crew's own kits' config: context, rules and operations are read past
cat > "$p/openspec/config.yaml" <<'EOF'
schema: spec-driven

# How the kit is built.
context: |
  Some context.
  schema: not-this-one
rules:
  tasks:
    - Keep each task small.
operations:
  apply:
    guidance:
      - Pause rarely.
EOF
done_

# A workflow of the user's own: proposal and tasks only, which spec-driven's reading would call incomplete.
mkdir -p "$XDG_DATA_HOME/openspec/schemas/lean/templates"
cat > "$XDG_DATA_HOME/openspec/schemas/lean/schema.yaml" <<'EOF'
name: lean
version: 1
description: A proposal and its tasks.
artifacts:
  - id: proposal
    generates: proposal.md
    description: Why.
    template: proposal.md
    requires: []
  - id: tasks
    generates: tasks.md
    description: What.
    template: tasks.md
    requires: [proposal]
apply:
  requires: [tasks]
  tracks: tasks.md
EOF
touch "$XDG_DATA_HOME/openspec/schemas/lean/templates/proposal.md" "$XDG_DATA_HOME/openspec/schemas/lean/templates/tasks.md"
begin user-schema openspec
rm -r "$c/specs" "$c/design.md"; printf 'schema: lean\ncreated: 2026-10-08\n' > "$c/.openspec.yaml"; done_
begin config-yml openspec
rm -r "$c/specs" "$c/design.md"; git -C "$p" rm -q openspec/config.yaml; printf 'schema: lean\n' > "$p/openspec/config.yml"; done_
begin kit-schema openspec  # the kit's own spec-driven, which the user's schema stands in for
rm -r "$c/specs" "$c/design.md"; mkdir -p "$p/openspec/schemas"; cp -R "$XDG_DATA_HOME/openspec/schemas/lean" "$p/openspec/schemas/spec-driven"
rewrite "$p/openspec/schemas/spec-driven/schema.yaml" 's/^name: lean/name: spec-driven/'; done_
begin meta-goal openspec
printf 'schema: spec-driven\ngoal: A goal crew does not read.\n' > "$c/.openspec.yaml"; done_
begin empty-meta openspec
: > "$c/.openspec.yaml"; done_
begin quoted-schema openspec
printf 'schema: "spec-driven"\n' > "$c/.openspec.yaml"; done_

# gather.py reads every place, with an openspec that logs the place it starts in.
real=$(command -v openspec)
mkdir -p "$T/shim"
printf '#!/usr/bin/env bash\necho "$PWD" >> %q\nexec %q "$@"\n' "$T/openspec.log" "$real" > "$T/shim/openspec"; chmod +x "$T/shim/openspec"
: > "$T/openspec.log"
req=$(jq -cn --arg m "$k" --arg d "$kd" '{kits: [{main: $m, dir: $d, bolts: [], reports: []}]}')
PATH="$T/shim:$PATH" python3 "$CREW/plugin/lib/gather.py" "$req" > "$T/gathered.json" || fail "gather.py failed"
cases=("${direct[@]}" "${handed[@]}")
ticks=$(python3 - "$CREW/plugin/lib" "$k" "${cases[@]}" <<'EOF'
import json, sys
sys.path.insert(0, sys.argv[1])
import plan
print(json.dumps({c: list(plan.ticks(sys.argv[2], f"unit/{c}", c)) for c in sys.argv[3:]}))
EOF
) || fail "ticks() failed"

for c in "${cases[@]}"; do
  p=$kd/places/$c
  mine=$(jq -c --arg m "$k" --arg c "$c" '.[$m].places[$c] | {tasks, planning, open}' "$T/gathered.json")
  listed=$(cd "$p" && openspec list --json) || fail "$c: openspec list failed"
  tasks=$(jq -c --arg c "$c" '[.changes[] | select(.name == $c) | [.completedTasks, .totalTasks]] | first' <<<"$listed")
  planning=$( (cd "$p" && openspec status --change "$c" --json 2>/dev/null) | jq '.isPlanningComplete // false' 2>/dev/null) || true
  # The open tasks as openspec's apply step lists them; where it refuses the change, it lists none to compare with.
  if applied=$(cd "$p" && openspec instructions apply --change "$c" --json 2>/dev/null); then
    open=$(jq -c '[.tasks[] | select(.done | not) | .description]' <<<"$applied")
  else
    open=$(jq -c .open <<<"$mine")
  fi
  theirs=$(jq -cn --argjson t "$tasks" --argjson p "${planning:-false}" --argjson o "$open" '{tasks: $t, planning: $p, open: $o}')
  [[ $mine == "$theirs" ]] || fail "$c: crew reads $mine where openspec reads $theirs"
  [[ $tasks == null ]] || eq "$(jq -c --arg c "$c" '.[$c]' <<<"$ticks")" "$tasks"
done
ok "crew's tasks, planning, open tasks and ticks agree with openspec in all ${#cases[@]} cases"

for c in "${direct[@]}"; do
  ! grep -qx "$kd/places/$c" "$T/openspec.log" || fail "$c was read through openspec, not from its files"
done
for c in "${handed[@]}"; do
  grep -qx "$kd/places/$c" "$T/openspec.log" || fail "$c was read from its files, though crew does not read its workflow"
done
ok "${#direct[@]} cases were read from their files, and ${#handed[@]} through openspec"

# The cases that tell the two readings apart: what each says is what openspec says, not what a narrower rule said.
st() { jq -c --arg m "$k" --arg c "$1" ".[\$m].places[\$c].$2" "$T/gathered.json"; }
eq "$(st nested tasks)" "[1,4]"
eq "$(st odd-boxes tasks)" "[2,6]"
eq "$(st links tasks)" "[0,1]"
eq "$(st skip-specs planning)" "true"
eq "$(st user-schema planning)" "true"
eq "$(st kit-schema planning)" "true"
eq "$(st no-change tasks)" "null"
ok "sub-tasks and odd boxes count, links do not, and a workflow of the user's or the kit's is honoured"
