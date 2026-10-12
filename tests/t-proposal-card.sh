# crew plan card <n>: a proposal's Pending You card, drawn from the plan and the proposal alone. Its title carries the
# counts, its summary what the proposal is, the unit count before and after and the bolt's goal, its background the
# case and each change; its text artifact is the change in lines of at most forty characters, a block per change and
# the order once approved; its questions are the approval and, for one to fifteen new units, the units shared out in
# questions of at most five, every one recommended, a lone one a choice, and never a text question; the approval's
# rationale says to object by not approving, naming only the drops and amendments the proposal makes, and that a note
# beside an approval changes nothing applied; with none, or more than fifteen, it is a plain approval, the latter
# linking its session. No field holds a path. Its picture is a PNG 780 pixels wide, drawn by crew with nothing
# installed but crew's own tools, its height growing with its rows, a dropped unit and a new one each in its colour.
# A closed proposal, or one that no longer applies, has no card.
# Each scenario of the plan-proposals spec on the card.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
# The user plans a bolt of four units, another of one, and nothing queued.
crew bolt new deploys "Deploys are checked before they run." --repo switchboard-kit >/dev/null
crew bolt new pages "The console has pages." --repo switchboard-kit >/dev/null
for u in a-first b-second c-third d-fourth; do crew unit add $u "Unit $u is built." --bolt deploys >/dev/null; done
crew unit add m-move "The page that moves." --bolt pages >/dev/null
long=a-long-unit-name-that-runs-past-the-width-of-a-phone-line
propose() { CREW_AGENT=wldn-planner crew plan propose "$(proposal "$@")" >/dev/null; }
card() { crew plan card "$1" > "$T/card-$1.json" || fail "crew plan card $1 failed: $(crew plan card "$1" 2>&1)"; cat "$T/card-$1.json"; }
q() { jq -r "$2" "$T/card-$1.json"; }

propose 'Case: The third unit is not needed. The second needs more. Two units finish the bolt.' \
  'Do: unit drop c-third "Not needed now."' \
  'Do: unit amend b-second "The second thing, done better."' \
  'Do: unit add e-fifth "The fifth thing is built." --bolt deploys' \
  "Do: unit add $long \"A unit whose name is longer than a phone's line.\" --bolt deploys --before a-first"
card 1 >/dev/null
eq "$(q 1 .card.title)" "Approve the change to deploys: 1 dropped, 1 amended, 2 new?"
eq "$(q 1 .card.summary)" $'Proposal 1, by wldn-planner\n4 units → 5 once approved: 1 dropped, 1 amended, 2 new.\nGoal: Deploys are checked before they run.'
has "$(q 1 .card.context.background)" $'The third unit is not needed. The second needs more. Two units finish the bolt.\n\nChanges:\nDrop unit c-third\nAmend unit b-second in bolt deploys'
eq "$(q 1 '[.card.context | .trace, .filesTouched, .tried, .links | length] | join(" ")')" "0 0 0 0"
eq "$(q 1 '.card.intent')" "approve"
eq "$(q 1 '.session')" "false"
ok "a proposal that drops, amends and adds: its title carries the counts, its summary the count before and after and the goal"

text=$(q 1 '.card.artifacts[] | select(.kind == "code") | .lines[]')
eq "$(q 1 '.card.artifacts[] | select(.kind == "code") | [.lang, .title, .ref] | join(" ")')" "text The change, in text proposal-1.txt"
(( $(q 1 '[.card.artifacts[] | select(.kind == "code") | .lines[] | length] | max') <= 40 )) || fail "a line of the text is longer than forty characters"
eq "$(head -2 <<<"$text")" $'deploys\n4 units → 5'
has "$text" $'DROP   c-third\n       Not needed now.'
has "$text" $'AMEND  b-second\n       The second thing, done better.'
has "$text" $'ADD    e-fifth\n       The fifth thing is built.'
has "$text" $'ADD    a-long-unit-name-that-runs-past-\n       the-width-of-a-phone-line\n'
has "$text" $'ONCE APPROVED\n 1 + a-long-unit-name-that-runs-past-\n     the-width-of-a-phone-line\n 2   a-first\n 3 ~ b-second\n 4   d-fourth\n 5 + e-fifth'
lacks "$text" " c-third"$'\n 4'
ok "the text is lines of at most forty characters: the bolt and its count, a block per change, a long name wrapped at its hyphens, and the order once approved marked"

eq "$(q 1 '[.card.questions[] | "\(.id):\(.kind)"] | join(" ")')" "plan:approve units-1:multi"
eq "$(q 1 '.card.questions[0].title')" "Approve the change to deploys?"
eq "$(q 1 '.card.questions[0].detail')" $'• The third unit is not needed.\n• The second needs more.\n• Two units finish the bolt.'
eq "$(q 1 '.card.questions[0].rationale')" "To keep the dropped unit or change the amendment, don't approve: say why in a note from ⋯, and the planner writes the proposal again. A note beside an approval changes nothing applied."
eq "$(q 1 '.card.questions[0].approve | [.action, .risk, .reversible] | join(" ")')" "Apply proposal 1, with the new units you keep low true"
eq "$(q 1 '.card.questions[1].title')" "Which new units go in? Clear one to leave it out."
eq "$(q 1 '[.card.questions[1].options[].id] | join(" ")')" "e-fifth $long"
eq "$(q 1 '.card.questions[1].recommendedIds | join(" ")')" "e-fifth $long"
eq "$(q 1 '.card.questions[1].options[0] | [.detail, .consequence] | join(" | ")')" "The fifth thing is built. | Cleared: not added; the rest still applies"
eq "$(q 1 '.card.questions[1].multi | "\(.min) \(.max)"')" "0 2"
eq "$(q 1 '.card.about | "\(.kind) \(.title)"')" "other Proposal 1: deploys"
eq "$(q 1 '[.card.kind, .card.approve] | map(. // "-") | join(" ")')" "- -"
ok "two new units: the approval, its detail the case as bullets, its rationale saying to object to the drop or the amendment by not approving, and one question holding both, each recommended"

# No field is a path: the picture is uploaded by its name, and crew prints where it wrote it beside the card.
eq "$(q 1 '[.card | .. | strings | select(test("^[/~]") or contains("/.local/"))] | length')" "0"
eq "$(q 1 '.card.artifacts[] | select(.kind == "image") | [.title, .ref, .upload] | join(" ")')" "The change, once approved proposal-1.png true"
pic=$(q 1 .picture)
eq "$pic" "$(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/1/proposal-1.png"
ok "no field of the card holds a path; the picture is uploaded by its name, and crew says where it is on this host"

# png <file>: its signature, width and height, and whether it holds the dropped and the new colours
png() { python3 -c 'import struct, sys, zlib
b = open(sys.argv[1], "rb").read()
assert b[:8] == b"\x89PNG\r\n\x1a\n", "no PNG signature"
w, h, depth, kind = struct.unpack(">IIBB", b[16:26])
data, i = b"", 8
while i < len(b):
    n, t = struct.unpack(">I4s", b[i:i + 8])
    if t == b"IDAT":
        data += b[i + 8:i + 8 + n]
    i += 12 + n
raw = zlib.decompress(data)
rows = [raw[y * (3 * w + 1) + 1:(y + 1) * (3 * w + 1)] for y in range(h)]
has = lambda c: any(bytes.fromhex(c) in r for r in rows)
print(w, h, depth, kind, "dropped" if has("e07b4f") else "-", "new" if has("8fb9ae") else "-")' "$1"; }
read -r w h depth kind dropped new <<<"$(png "$pic")"
eq "$w $depth $kind $dropped $new" "780 8 2 dropped new"
ok "the picture is a PNG 780 pixels wide, a dropped unit and a new one each in its colour"

# Drawn with nothing on the path but what crew itself runs: no browser, no renderer.
bin=$T/bare-bin; mkdir -p "$bin"
for t in python3 git recsel recfix bash; do ln -s "$(command -v $t)" "$bin/$t"; done
ln -s "$TESTS/stubs/hostname" "$bin/hostname"
rm "$pic"
expect_ok as mac-studio env PATH="$bin" python3 "$CREW/plugin/lib/plan.py" plan card 1
[[ -f $pic ]] || fail "no picture was drawn with only crew's own tools on the path:"$'\n'"$out"
eq "$(png "$pic" | cut -d' ' -f1)" "780"
ok "run where no browser and no image tool is installed, it writes the picture all the same"

propose 'Case: The first unit changes, and the last goes first.' \
  'Do: unit amend a-first "The first thing, done again."' 'Do: unit order d-fourth --first'
card 2 >/dev/null
eq "$(q 2 .card.title)" "Approve the change to deploys: 1 amended, 1 moved?"
eq "$(q 2 '[.card.kind, (.card.questions // [] | length), .card.recommendedIds[0]] | join(" ")')" "approve 0 approve"
eq "$(q 2 '.card.approve | [.action, .risk, .reversible] | join(" ")')" "Apply proposal 2 low true"
has "$(q 2 '.card.artifacts[1].lines | join("\n")')" $'ONCE APPROVED\n 1 ↕ d-fourth\n 2 ~ a-first'
ok "a proposal that makes no unit new to a bolt is a plain approval, with no question of units"

propose 'Case: One more unit, queued.' 'Do: unit add g-one "One unit for later." --repo switchboard-kit'
card 3 >/dev/null
eq "$(q 3 .card.title)" "Approve the change to the switchboard-kit queue: 1 new?"
eq "$(q 3 '[.card.questions[] | "\(.id):\(.kind)"] | join(" ")')" "plan:approve units-1:choice"
eq "$(q 3 '.card.questions[1].title')" "Does g-one go in?"
eq "$(q 3 '[.card.questions[1].options[] | "\(.id)=\(.label)"] | join(" ")')" "g-one=Add it leave-out=Leave it out"
eq "$(q 3 '.card.questions[1].options[1].consequence')" "Cleared: not added; the rest still applies"
eq "$(q 3 '.card.questions[1].recommendedIds | join(" ")')" "g-one"
eq "$(q 3 '.card.questions[0].rationale')" "To change it, don't approve: say how in a note from ⋯. A note beside an approval changes nothing applied."
ok "one new unit: the second question is a choice between keeping it and leaving it out, keeping it recommended, and the approval's rationale, for a proposal that drops and amends nothing, says to change it by not approving"

adds() { local i; dos=(); for i in $(seq 1 "$2"); do dos+=("Do: unit add $1-$i \"Unit $i.\" --repo switchboard-kit"); done; }
adds s 7; propose 'Case: Seven units for the queue.' "${dos[@]}"
card 4 >/dev/null
eq "$(q 4 '[.card.questions[] | "\(.id):\(.kind):\(.options // [] | length)"] | join(" ")')" "plan:approve:0 units-1:multi:4 units-2:multi:3"
eq "$(q 4 '.card.questions[2].title')" "Which new units go in? Clear one to leave it out. (2 of 2)"
eq "$(q 4 '.card.questions[1].recommendedIds | join(" ")')" "s-1 s-2 s-3 s-4"
eq "$(q 4 '.card.questions[2].recommendedIds | join(" ")')" "s-5 s-6 s-7"
eq "$(q 4 '[.card.questions[] | select(.kind == "text")] | length')" "0"
(( $(png "$(q 4 .picture)" | cut -d' ' -f2) > $(png "$(q 3 .picture)" | cut -d' ' -f2) )) || fail "seven rows drew no taller a picture than one"
ok "seven new units: two questions of four and three, every unit recommended, no text question, and a taller picture"

adds x 16; propose 'Case: Sixteen units for the queue.' "${dos[@]}"
card 5 >/dev/null
eq "$(q 5 '[.card.kind, (.card.questions // [] | length), .session] | join(" ")')" "approve 0 true"
(( $(q 5 '.card.summary | length') <= 300 )) || fail "the summary leaves no room for the session's link"
ok "sixteen new units: a plain approval with no question of units, which says it links the proposal's session"

propose 'Case: The moving page belongs with the deploys.' 'Do: unit move m-move deploys'
card 6 >/dev/null
eq "$(q 6 .card.title)" "Approve proposal 6 to pages and deploys: 1 new, 1 moved?"
eq "$(q 6 '.card.questions[1].options[1].consequence')" "Cleared: stays in bolt pages; the rest still applies"
eq "$(q 6 '.card.questions[1].options[0].label')" "Move it in"
text=$(q 6 '.card.artifacts[1].lines | join("\n")')
has "$text" $'MOVE   m-move\n       from pages to deploys'
has "$text" $'pages\n1 unit → 0'
ok "a move between bolts: each bolt drawn, counted new and moved, the unit moved in kept or left where it is"

propose 'Case: Two units are not needed, and one more is.' 'Do: unit drop c-third "Not needed now."' \
  'Do: unit drop d-fourth "Not needed either."' 'Do: unit add h-one "One more thing is built." --bolt deploys'
card 7 >/dev/null
eq "$(q 7 '.card.questions[0].rationale')" "To keep the dropped units, don't approve: say why in a note from ⋯, and the planner writes the proposal again. A note beside an approval changes nothing applied."
ok "a proposal that drops and adds: the approval's rationale names only the drops, saying to keep them by not approving, and that a note beside an approval changes nothing"

CREW_AGENT= crew plan drop 2 "not now" >/dev/null
expect_fail "proposal 2 is dropped: it is closed, so it has no card" crew plan card 2
CREW_AGENT= crew unit add g-one "Added directly." --repo switchboard-kit >/dev/null
expect_fail '`unit add g-one "One unit for later." --repo switchboard-kit`: wldn/main already has unit g-one' crew plan card 3
ok "a closed proposal, or one that no longer applies, has no card"
