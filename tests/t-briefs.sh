# Every brief prints for its team or partition with no token left unfilled.
# Reads: plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "# You are swb-1-"
  lacks "$out" "fable"; lacks "$out" "explorer"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_fail "no definition 'fable' for a team" crewpy brief swb-1 fable
[[ ! -e $CREW/plugin/roles/fable.md && ! -e $CREW/plugin/roles/explorer.md && ! -e $CREW/plugin/roles/verifier.md ]] || fail "a retired role is still there"
ok "every team brief prints with no unfilled token"

expect_ok crewpy brief swb-1 coder; has "$out" "run \`wt submit\` in the background and wait for it to end"
has "$out" "wt submit bolt/<bolt> --no-remove"; lacks "$out" "wt merge"; lacks "$out" "--no-hooks"
ok "the coder merges by a submission to sluice, whose checks can outlast a command's time limit, in the background"

# sluice 0.3.1's `wt submit --help` removes the worktree it ran in as if the submission had landed (teams.5's
# details), so every brief that names `wt submit` says never to run it, and where the usage is read instead.
named=()
for brief in "swb-1 conductor" "swb-1 ops" "swb-1 construct" "swb-1 coder" "swb-1 verify" \
  "wldn design" "wldn planner" "wldn dispatcher" "wldn main-ops" "wldn operator"; do
  expect_ok crewpy brief $brief
  [[ $out == *"wt submit"* ]] || continue
  named+=("${brief#* }")
  has "$out" "Never run \`wt submit --help\` in a worktree: with sluice 0.3.1 it prints its help and then removes the worktree it ran in as if the submission had landed; read the usage from \`sluice submit --help\` or \`wt --help\`, which remove nothing."
done
[[ ${named[*]} == "conductor coder design main-ops operator" ]] || fail "the briefs naming wt submit are ${named[*]}"
ok "every brief that names wt submit says never to run wt submit --help in a worktree, and to read sluice submit --help or wt --help"

expect_ok crewpy brief swb-1 coder; has "$out" "Never run the whole suite by hand: sluice runs it."
has "$out" "run the tests of what you changed, as the kit's CLAUDE.md says"; lacks "$out" "moon run"
expect_ok crewpy brief swb-1 verify; has "$out" "If the check runs tests, it runs only those the change affects"
has "$out" "never the whole suite, which the merge gate runs"
expect_ok crewpy brief swb-1 construct; has "$out" "ending with the tests its change affects green, not the whole suite, which the merge gate runs"
lacks "$out" "ending with the suite green"
ok "the coder, verify and construct run only the tests a change affects, and leave the whole suite to the merge gate"

expect_ok crewpy brief swb-1 conductor
for want in "tell wldn-design" "signal" "never by hand" "Don't create tracking files" "`wldn/main` of WilldanGroup/crew-state"; do
  has "$out" "$want"
done
lacks "$out" "plannotator-tui"; lacks "$out" "unit approve"; lacks "$out" "review/<unit>"
for want in "open nothing for a batch" "never its number alone"; do has "$out" "$want"; done
has "$out" "You post, change and close no landing card"
for gone in "crew card session" "crew card wait" "answeredHere" "plannotator"; do lacks "$out" "$gone"; done
ok "a conductor opens nothing, posts no landing card and starts no card's session"
# The question discipline each of the four that ask carries (record 0031, briefs.11): who asks and after whom, Pending
# You's test for what is the user's, a question's fields and its key of its own, how its answer is heard, and every
# row's card as crew's.
asks_say() {
  for want in "A question of yours for the user reaches them on a Pending You card you ask yourself; every other card on the rail is crew's." \
    "Four ask the user: a team's conductor, the planner, main-level ops and the design agent." \
    "the dispatcher asks through the planner; and crew refuses a card from any of them" \
    "\`$CREW/plugin/bin/crew tell\`: \`wldn-design\` for the design, \`wldn-ops\` for a live system or a deploy, \`wldn-planner\` for the plan" \
    "in their name, their money, their plans, public or hard to undo" "when its choices lead to noticeably different products" \
    "decide what a careful product designer would, and say so" "its options, with the one you recommend" \
    "\`blocking\` false and the fallback you take meanwhile" "what you tried, in its \`tried\`" \
    "\`ask/<your crew name>/<what it is about>\`, a key of your own" "Pending You gives that card back" \
    "a new card under a new key, following the one answered" \
    "\`proposal/\`, \`batch/\`, \`land/\`, \`deploy/\`, \`op/\` or \`record/\`, is crew's" "refuses your post, change or close of one" \
    "call \`whoami\` with your crew name" "\`create-area:<owner>/<kit>\`: crew refuses an area under any other key" \
    "Never run \`npx pendingyou\` or \`pendingyou hold\`" "close your question's card with \`ack_answer\` and a one-line outcome" \
    "ask it again if it still matters, under the same key, saying in it that an older copy is dead" "leave every other card alone"; do
    has "$out" "$want"
  done
  for gone in "rail row's of your own" "the form its row takes" "plan card" "begins with the link to the card's plannotator session" \
    "No card carries a path" "kind \`image\`" "An older copy of this card is dead" "posted again by nobody" \
    "The one exception is a lost card" "card session <key>" "answeredHere" "Never open a browser for a card"; do
    lacks "$out" "$gone"
  done
}
asks_say
has "$out" "which crew raises itself, in your name, once the bolt reads proven"
lacks "$out" "two or three plain sentences"; lacks "$out" "post its review card"
ok "a conductor asks the user its own questions under a key of its own, once the chain of command has not answered them"
for want in "idempotencyKey" "create-area:" "pendingyou hold" \
  "keyed \`land/<bolt>\`, which crew raises itself" "Land bolt <bolt>. The user approved it on Pending You." \
  "crew raises its landing card, and the merge's wait that found the bolt proven prints the line that adopts it" \
  "Send no such tell for what has a card" "The kits: switchboard-kit: WilldanGroup/switchboard-kit." "Pending You gives that card back" \
  "Starting a fix withdraws the bolt's landing card, held for the fix" "\`call get_request (requestId <id>, name swb-1-conductor)\`" \
  "start a fix on the bolt in the note's words, which withdraws the card"; do
  has "$out" "$want"
done
for want in "It is an approval of the landing alone, risk high" "withdraws it when you start a fix on the bolt" \
  "raises it again, following the one the fix held"; do
  has "$out" "$want"
done
for gone in "highStakes" "land/<bolt>/<head>" "post its landing card" "A row's key changes when what it asks changes"; do lacks "$out" "$gone"; done
lacks "$out" "offering approval"; lacks "$out" "Looks good"; lacks "$out" "Needs changes"; lacks "$out" "\`review\` card"
for gone in "verify/<unit>/<stamp>" "post its verify card" "a \`multi\` when the user may pick several findings" "An answer on a verify card"; do
  lacks "$out" "$gone"
done
ok "the conductor posts no verify card, and crew raises its landing card, an approval of risk high, withdraws it for a fix and raises it again"
ok "the conductor keeps its units moving, asks the design agent, records signals, and writes the plan only through crew"

for role in design planner dispatcher main-ops; do
  expect_ok crewpy brief wldn $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "of wldn"; lacks "$out" "fable"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_ok crewpy brief wldn design
for want in attach challenge new-territory answered drop "unit add" "tell wldn-planner" "tell <conductor>"; do has "$out" "$want"; done
for want in "names, in the message that carries it, the documentation page or the reading it rests on" "Read the thing itself" \
  "not the sequence" "Answer linked questions together" "never the mechanism"; do has "$out" "$want"; done
has "$out" "\`--source\` also names what the signal points at"
expect_ok crewpy brief wldn planner
for want in "only agent that proposes bolts" "--signal" "plan propose <file>" "plan proposed <n>" "--replaces <n>" "--unblocks <bolt>" \
  "plan agree <n>" "only when the user says so" "wldn/main" "is refused while a unit of the bolt has a worktree, since a queued unit has none"; do
  has "$out" "$want"
done
for gone in "bin/crew bolt new" "bin/crew unit add" "bin/crew unit move" "bin/crew unit drop" "Agree any change to it"; do lacks "$out" "$gone"; done
has "$out" "and with \`--source\` what the signal points at"
for want in 'unit amend <unit> "<new intent>"' "never a drop and a new unit" "why the unit changes rather than being replaced" \
  "A unit that has merged is not amended"; do has "$out" "$want"; done
for want in "An intent names the outcome and the records that govern it" "never the mechanism" \
  "Corrections to a unit under construction are batched" "blocks the team"; do has "$out" "$want"; done
for want in "Never name a proposal by its number alone" "recite no command"; do has "$out" "$want"; done
for want in "crew card session" "crew card wait" \
  "crew raises a proposal's card itself, in your name, when \`$CREW/plugin/bin/crew plan propose\` accepts the proposal" \
  "changes it when you rewrite the proposal with \`--replaces\`, in place while it waits on the user and as a new version following the one they answered" "closes it with what was applied when the proposal is approved" \
  "You post, change and close no proposal card." \
  "call get_request (requestId req_…, name wldn-planner)" "crew raises its card in your name" \
  "a dropped one unticked as \"Keep <unit>\"" "a lone row is the choice of its two sides" \
  "so each new unit's \`Do\` carries its direction" "crew plan answer <n> <question> <box>... --label wldn" \
  "\`rows-<k>\` and the ids of the boxes the user left ticked" "--note \"<the user's note>\"" \
  "applies the change with the boxes as they stand, a new unit unticked left out, a dropped one ticked kept, an amendment ticked not applied" \
  "you close no proposal card" \
  "add \`--clear <unit>\` for each of them" "An approval applies the commands the user read and kept" \
  "when a command they kept names a unit they left out"; do has "$out" "$want"; done
for gone in "Post its \`card\` as it is" "crew refuses a proposal's card in any other form" "close the old proposal's card" \
  "\`units-<k>\` and the units left ticked" "update its card to say"; do lacks "$out" "$gone"; done
lacks "$out" "offers approval"; lacks "$out" "exactly as the user read them"; lacks "$out" "not the page as a file"
asks_say
lacks "$out" "Its words are the proposal's case and each of its changes in a line"
for want in "idempotencyKey" "create-area:" "pendingyou hold" "keyed \`proposal/<n>\` of the first proposal it was rewritten from" \
  "or answers your card" "it no longer waits on that conductor" "The kits: atlas-kit: WilldanGroup/atlas-kit; breadboard-kit" \
  "Pending You gives that card back"; do
  has "$out" "$want"
done
has "$out" '`swb-1` builds Switchboard in switchboard-kit'; has "$out" "on mac-studio in session wldn-5"
expect_ok crewpy brief swb-1 conductor
for want in "plan proposed <n>" "plan agree <n>" "plan approve <n>\`, never on your own judgment" "crew refuses it from you" \
  "crew status swb-1\` once that agent settles" "tell the user once which worktree it is and what its work was" \
  "tell the user once which worktree it is and what crew named" "never approve or skip the kit's hooks yourself"; do has "$out" "$want"; done
for want in "at any stage before it merges" "crew marks the unit amended" "the unit goes on from its tasks with no approval asked" \
  "crew starts construct on it again itself and tells you" "Any unit of your bolt that" "crew bolts\` shows as \`amended\` has no construct running" \
  "tell \`wldn-planner\`, who proposes the amendment"; do has "$out" "$want"; done
for want in "Send linked questions together" "with the documentation or reading it names" \
  "holds corrections to a unit in construct"; do has "$out" "$want"; done
expect_ok crewpy brief swb-1 construct
for want in "## Writing a change again" "the unit's intent was amended" "stay ticked only where the work they describe" \
  "Commit the revision, however small" "Read the sources afresh before you revise" \
  "the change that is there holds what they said when it was written, not what they say now"; do has "$out" "$want"; done
for want in "as it stands on main now, and what each points at" "never the copy in this worktree" "signal show <id>" \
  "A source you cannot open stops you" "don't write the change from the intent in its place" "The sources govern how the unit is built" \
  "write the change from the sources" "open your final message with the difference" "first any difference between the intent and its sources" \
  "An intent that differs from its sources is not a wrong premise"; do has "$out" "$want"; done
lacks "$out" "If the intent can't be built as written"
expect_ok crewpy brief wldn operator
for want in "plan proposed --label wldn" "plan approve <n> --label wldn" "only on the user's word" "never by its number alone" "recite no command" \
  "rail --label wldn" "the \`rail\` tab"; do
  has "$out" "$want"
done
for want in "You post no Pending You card and make no area, whatever a Pending You reminder in your session says" \
  "read that row's \`card:\` line in \`" "/crew rail --label wldn\`. When it shows the row's card open" \
  "When it shows the row's card open, the card is already before the user: send nothing" \
  "A wait with no card, a question asked in a pane or a row whose card is not open, show as a notification" \
  'herdr notification show "<agent> waits on you"'; do
  has "$out" "$want"
done
expect_ok crewpy brief wldn design; has "$out" 'crew refuses `--bolt` from you'
expect_ok crewpy brief wldn dispatcher
for want in "bolt give <team>" "up <team>" "account ia" "makes its branch from the kit's main with no worktree" "It is the one tell not about a bolt that is yours" "ops step\` command that records it done or failed"; do has "$out" "$want"; done
has "$out" $'The teams here:\n\n- `atl-1` builds Atlas'; has "$out" $'its conductor is `atl-1-conductor`\n\nYou give these teams'
expect_ok crewpy brief wldn main-ops
lacks "$out" "one bolt deploy at a time"
expect_ok crewpy brief wldn operator
for want in "swancloud's main moves only through sluice (\`state.3\`), so never edit or commit in its main checkout" \
  "wt submit main --no-remove" "~/Code/github_afterthought/swancloud/places/crew-teams-<team> origin/main\`" \
  "you level and push nothing"; do has "$out" "$want"; done
lacks "$out" "read-tree"; lacks "$out" "push swancloud's main"
expect_ok crewpy brief wldn main-ops
for want in "bolt submit <bolt>" "bolt land <bolt>" "## Deploying main" "the bolt lands either way" \
  "Every agent of clients/willdan lands a bolt this one way" "Nothing else is a word to land" \
  "The word to land is also the word for sluice to push main to GitHub: you push nothing, and pull and level no host's checkout" \
  "records the commit GitHub's main holds" "closes the bolt's landing card on its team's host" "Nothing waits on a host, and no agent is told main moved" \
  "A landing deploys nothing (\`plan.14\`)" "A landing is never that word" \
  "ops approve <env> --to <sha> --label wldn" "keyed \`deploy/<env>\`" "deploy nothing yourself" "keyed \`op/<env>/<n>\`" \
  "run it in the background and wait for it to end" "through the kit's remove hooks" "never yours to approve or skip"; do has "$out" "$want"; done
lacks "$out" "wt merge"; lacks "$out" "push origin main"; lacks "$out" "/workspace/crew/main"
for want in "crew raises its card in your name, with those notes and steps on its face" "you post, change and close no deploy card" \
  "\`call get_request (requestId <id>, name wldn-ops)\`: run it" "crew closes the card at the deploy's end with its outcome" \
  "card read deploy/<env> --label wldn" "a step an agent can do that is held for the user's word" \
  "one at a time on an environment, each following the one before" "you post and close no step card" \
  "ops quiet <env> --label wldn\` exits 0" "when they pick skip, run the row's \`decline\` command"; do has "$out" "$want"; done
for gone in "Post its card under that key" "and close the card"; do lacks "$out" "$gone"; done
asks_say
has "$out" $'A landing is never that word.\n\n## Asking the user\n\nA question of yours for the user'
expect_fail "no definition 'conductor' for a main level" crewpy brief wldn conductor
ok "every main-level brief prints for wldn with no unfilled token"

expect_ok crewpy brief wldn operator
has "$out" "the deployer offers that host's deploy under *operations* on swancloud's rail"; has "$out" "never ask \`wldn-ops\` to deploy it"
has "$out" "never hand the user a deploy command"; has "$out" "deploys by hand only a kit with no deployer"
[[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/operator.md left ${BASH_REMATCH[0]} unfilled"
for want in "bolts --label wldn" "status <team>" "sites wldn" "tell <agent>" '`wldn-planner`' '`wldn-design`' "<team>-conductor" "terminal-browser open <url> --split right"; do has "$out" "$want"; done
for want in "/crew page wldn\`" "open the file it prints in terminal-browser beside your pane" \
  "on a box, give the user the path and say it opens from a Mac" "say as of when the page is, and name any host it could not read"; do has "$out" "$want"; done
HOST=chuck-herdr-alpha expect_ok crewpy brief wldn operator
has "$out" "chuck-herdr-alpha is a box, which can't open the dev.swancloud.net names"; lacks "$out" "terminal-browser open"
ok "the operator brief prints for wldn, opening sites and the lineage page on a Mac and giving the Mac URL or the page's path on a box"

# Every brief says who is speaking in the agent's pane; the six that record findings say how, with the excerpt, and
# where crew writes the signal.
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  has "$out" 'A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent'
  has "$out" 'one that begins `[crew]` is crew'"'"'s own; anything else typed there is the user.'
done
for role in design planner main-ops dispatcher operator; do
  expect_ok crewpy brief wldn $role
  has "$out" 'A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent'
done
for brief in "swb-1 conductor" "swb-1 ops" "wldn main-ops" "wldn design" "wldn planner" "wldn operator"; do
  expect_ok crewpy brief $brief
  has "$out" 'signal <slug> "<what it asserts, in a sentence>" --excerpt "<the exact words the user said or the tool printed>"'
  has "$out" "Copy the excerpt, never reword it"; has "$out" "a refusal means the words were reworded"
  has "$out" "When the words point at something made elsewhere"; has "$out" "A conversation's id alone is not enough"
  has "$out" '`signals/` on `wldn/main` of WilldanGroup/crew-state'
  lacks "$out" "signal in WilldanGroup/willdan-blueprints"
done
expect_ok crewpy brief wldn design; lacks "$out" "crew writes signals straight to"; has "$out" "signal show <signal id>"
expect_ok crewpy brief wldn planner; has "$out" "signal show <signal id>"
has "$out" "Never pass on a word to land, and never tell \`wldn-ops\` to land or deploy"
ok "every brief says who speaks in its pane, and the six that record findings quote the words and say what a refusal means"
ok "a signal names where what it points at lives, a unit carries it as a source, and the construct reads it, stops when it can't, and builds from its sources over its intent"

# Every message an agent sends another goes through crew tell, marked: no brief prompts an agent through herdr.
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role; lacks "$out" "herdr agent prompt"
done
for role in design planner main-ops dispatcher operator; do
  expect_ok crewpy brief wldn $role; lacks "$out" "herdr agent prompt"
done
expect_ok crewpy brief swb-1 conductor; lacks "$out" "prove swb-1"
ok "no brief prompts another agent through herdr"

# The plan and the moves live on the flywheel's branch of its state repository: no brief names a plan/<label>
# branch or a moves.rec in the blueprints, and the design agent and the planner name the state repository.
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role; lacks "$out" "plan/wldn"; lacks "$out" "signals/moves.rec"
done
for role in design planner main-ops dispatcher operator; do
  expect_ok crewpy brief wldn $role; lacks "$out" "plan/wldn"; lacks "$out" "signals/moves.rec"
done
expect_ok crewpy brief wldn design; has "$out" "\`moves.rec\` on \`wldn/main\` of WilldanGroup/crew-state"
lacks "$out" "route moves straight to"
expect_ok crewpy brief wldn planner; has "$out" "\`wldn/main\` of WilldanGroup/crew-state"
ok "every brief names the flywheel's branch for the plan and the moves, and none names plan/<label>"

# Test, check and proof results reach the user as a glyph list (briefs.7): the six roles that report results carry
# one section, built once in crew, word for word the same in each.
first=""
for brief in "swb-1 conductor" "swb-1 ops" "swb-1 construct" "swb-1 coder" "swb-1 verify" "wldn main-ops"; do
  expect_ok crewpy brief $brief
  n=$(grep -c '^## Test, check and proof results$' <<<"$out")
  [[ $n == 1 ]] || fail "the $brief brief holds the results heading $n times"
  cut=$(awk '/^## Test, check and proof results$/ {on = 1; print; next} on && /^## / {exit} on' <<<"$out")
  for want in "## Test, check and proof results" "- ✅" "- ❌" "- ⏳" "before any prose" "Never say a result only in a sentence"; do
    has "$cut" "$want"
  done
  [[ -z $first ]] && first=$cut
  [[ $cut == "$first" ]] || fail "the $brief brief's results section differs from the swb-1 conductor's:"$'\n'"$cut"
done
ok "the six roles that report results carry one glyph-list section, the same in each"

# A stage ends at its deliverable (teams.4): the conductor waits for every stage and fix through crew and reads no pane
# for an outcome, takes a stuck stage to the user and runs a stopped-short one again with the answer; the stage agents
# say what they need with crew needs, and ops, which runs no stage, tells the conductor; verify's report is written once,
# whole.
expect_ok crewpy brief swb-1 conductor
for want in "unit wait <unit>\` as a background command" "you never read a pane for one" "**Stuck**" \
  "run the stage again or wait again only on the user's word" "fix swb-1 <name> --wait\`" \
  "run the stage again with the answer as its words"; do
  has "$out" "$want"
done
for gone in "If it is waiting on a question for the user, leave it for the user" "When its agent settles, merge it" "tell swb-1-ops \"Deploy"; do
  lacks "$out" "$gone"
done
has "$out" "a wait may also say what sluice recorded of the stage's submission: \`<stage> on <unit>: sluice says of <agent>'s submission to <branch>: conflict #<n> on <its paths>; the wait goes on until the stage ends\`"
has "$out" "It is no answer: the stage's agent has sluice's outcome too and takes it in the stage"
for role in construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  has "$out" 'needs "<what you tried and what you need>"` and end your turn'
  has "$out" "Never ask in your pane: nobody watches it."
  has "$out" "Ending a turn to wait on something you started in the background is fine"
done
expect_ok crewpy brief swb-1 ops
has "$out" 'tell swb-1-conductor "<what you wait on, and why>"`'; lacks "$out" "needs \"<what you tried"; lacks "$out" "proof-<bolt>"
expect_ok crewpy brief swb-1 verify
has "$out" "unchanged and whole"; has "$out" "crew ends the stage once it is there"
ok "the conductor waits for every stage through crew, takes sluice's word on a submission as no answer and never reads a pane for an outcome; every stage stops short with crew needs, and ops tells the conductor"

# A landing that conflicts lands nothing and goes back to the team as a fix that takes main into the bolt (plan.8,
# teams.5, record 0026): main-ops submits the bolt with crew bolt submit and passes on sluice's words, the conductor
# starts the fix and merges it as any fix, its agent merges main in, and nothing but sluice moves a bolt's branch or
# main; the bolt's proof is its verification (record 0025), and ops proves and deploys nothing.
expect_ok crewpy brief wldn main-ops
for want in "tell the bolt's conductor and the user sluice's words" "its landing comes back to the user on a new card" \
  "never merge, rebase, reset or fast-forward main or a bolt's branch by git" "A host's own main lagging GitHub's stops nothing" \
  "shows every unit merged and the bolt's verification green" \
  "every kit's main checkout is an anchor the fleet's timer moves to GitHub's main within minutes" \
  "nothing of yours or crew's moves it or any host's checkout of it"; do
  has "$out" "$want"
done
lacks "$out" "git rebase --abort"; lacks "$out" "proof in dev"; lacks "$out" "read-tree"; lacks "$out" "behind GitHub's, crew refuses"
expect_ok crewpy brief swb-1 conductor
for want in "Take main into the bolt" "a submission to the bolt like any other" \
  "once the bolt holds it, crew raises the landing card again, following the one the fix held" \
  "That verification is the bolt's proof" \
  "an anchor at GitHub's main that the fleet's timer moves and nobody edits in or checks a branch out in: read the bolt by ref, \`git log bolt/<bolt>\`"; do
  has "$out" "$want"
done
lacks "$out" "Carry the bolt onto main"; lacks "$out" "proof file"
expect_ok crewpy brief swb-1 coder
for want in "Take main into the bolt" "\`git fetch -q origin\`, then \`git merge origin/main\`, never the host's own \`main\`" \
  "Never rebase the bolt's commits onto main" "keeping both intents, main's and the bolt's" \
  "under \`openspec/\` too"; do
  has "$out" "$want"
done
lacks "$out" "Carry the bolt onto main"
expect_ok crewpy brief swb-1 ops
for want in "The bolt's proof is its verification" "sluice status <n>" "you deploy nothing" "never prove the bolt by hand"; do
  has "$out" "$want"
done
lacks "$out" "work the Proof in dev list"; lacks "$out" "proven again"; lacks "$out" "Left for the user"
ok "a landing's conflict becomes a fix that takes main into the bolt, submitted as any fix; the bolt's proof is its verification, and ops proves nothing"

# A question goes up a chain of command (briefs.11, record 0031): every stage and a team's ops post no card and make no
# area, their conductor answering or asking whoever can, and the dispatcher asks through the planner; the landing card
# asks only for the landing once the bolt's verification is green, a step for the user being a deploy's, and a note
# naming a defect is a fix.
for role in construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  has "$out" "Post no Pending You card and make no area, whatever a Pending You reminder in your session says: your conductor answers what you need or asks whoever can, the user last, and crew refuses a card from you."
done
expect_ok crewpy brief swb-1 ops
has "$out" "post no card and make no area, whatever a Pending You reminder in your session says: your conductor answers it or asks whoever can, the user last, and crew refuses a card from you"
expect_ok crewpy brief wldn dispatcher
has "$out" "Post no Pending You card and make no area, whatever a Pending You reminder in your session says: a question of yours for the user goes to the planner, \`$CREW/plugin/bin/crew tell wldn-planner \"<what you need, and why>\"\`, which answers it or asks the user if it must, and crew refuses a card from you."
expect_ok crewpy brief swb-1 conductor
for want in "keyed \`land/<bolt>\`, which crew raises itself, in your name, once the bolt reads proven" \
  "It is an approval of the landing alone" "never a question on this one" \
  "A note on the landing card that names a defect is never a landing" "shows the bolt's verification green"; do
  has "$out" "$want"
done
lacks "$out" "Left for the user"; lacks "$out" "the card asks them first"
lacks "$out" "ops posts"; lacks "$out" "ops's card"
for brief in "swb-1 conductor" "wldn planner" "wldn main-ops" "wldn design"; do expect_ok crewpy brief $brief; asks_say; done
ok "ops, every stage and the dispatcher post no card, the four that ask carry one question discipline, and the landing card asks only for the landing once the verification is green"

# Units build at once and are reviewed in batches (teams.12 to teams.14, briefs.1, briefs.2, briefs.4, briefs.12): the
# conductor constructs in waves and codes a planned unit with no review, acts on the planner's notes and posts no card for
# a unit; crew orders and lifts its own forecast orders, which neither the conductor nor the planner asks anyone to lift
# (plan.13); the planner runs the reviewer, whose summary has crew raise the batch's one card in the planner's name with
# one reading session on the batch, posts and closes no batch card, and sends the notes the card's wait prints from the
# session and the card to each unit they speak of (briefs.9, briefs.12, briefs.13);
# construct writes Touches as a block crew reads;
# the coder keeps both intents, settles, corrects only Touches, and submits to sluice; verify names what was changed
# and not declared; the reviewer writes its summary and nothing else, as prose opening each unit with the paragraph the
# card carries; main-ops checks the landing row before it submits a bolt to main.
expect_ok crewpy brief swb-1 conductor
for want in "Construct in waves" "Start code as soon as" "shows a unit \`planned\`" "with nobody asked to approve it" \
  "You post no card for a unit, and open nothing for a batch" "run construct again with them, word for word" \
  "hold the notes until it settles" "Overlapping *Touches* never hold a unit back" "orders neither by itself" \
  "when the later unit's settle takes the earlier's work, crew puts the later after the earlier itself, as your write" \
  "when that settle finds nothing to change, crew lifts an order of its own" \
  "Never ask the planner or the user to lift an order crew wrote from a forecast" \
  "no proposal and no card asks the user to undo one" \
  "unit run <unit> settle \"<what reached it>\"" "## Forecasts and settling" "The earlier unit is never changed for it" \
  "the card waits for them: crew makes a batch due for them at once" "submits the unit to the bolt, \`wt submit bolt/<bolt>\`" "changed and did not declare in its Touches" \
  "ahead of it in the bolt's merge order, which is \`After\` first" "so a unit's dependents are never ahead of it"; do
  has "$out" "$want"
done
for gone in "build them one after the other" "When in doubt, don't" "## Review with the user" \
  "A forecast between two unmerged units puts the later after the earlier"; do lacks "$out" "$gone"; done
expect_ok crewpy brief wldn planner
for want in "## Batches" "review wldn\`" "review wldn --wait\`" \
  "Never propose lifting an \`After\` crew wrote from a forecast: crew lifts its own." \
  "crew records the batch, starts its one reading session, the summary and every unit's whole change as one review, and raises its one card in your name, keyed \`batch/<n>\`" \
  "naming every unit of the batch with its team and the paragraph the reviewer opened it with, however many" \
  "a batch is never split across cards" "\`call get_request (requestId req_…, name wldn-planner)\`" \
  "card wait batch/<n> --label wldn\`" "when the user sends the card back with a tap or sends the reading session, whichever comes first" \
  "prints the card's note and every annotation the user sent, word for word; crew then closes the card and ends the session" \
  "card session batch/<n> --label wldn\` prints the session's link again" \
  "You start no session for a batch, and post, change and close no batch card: crew does." \
  "at once, word for word, to the conductor of each unit it speaks of" \
  "go to every unit's conductor, saying they named no unit you could tell" \
  "Never split, reword or summarize the user's words" "you never run a stage" "Never answer a batch card yourself" \
  "posted before crew raised one card per batch, is yours as it was" \
  "one per batch, keyed \`batch/<n>\`, which crew raises in your name with the batch's one reading session when the reviewer's summary is delivered, and closes when the user sends it back"; do
  has "$out" "$want"
done
for gone in "of at most five units" "which need notes?" "one in words for the notes" "A unit not picked is fine" \
  "card session batch/<n> <unit>" "card session batch/<n>-<k> <unit>" "send each picked unit's notes" "once for each of its units" \
  "post the batch's one card" "The card is a notice, kind \`fyi\`" "First start its one reading session" \
  "Close the card with \`ack_answer\`, its outcome naming the units" "for a batch card \`batch/<n>\`, one session on the whole batch" \
  "a decision in it is never the card's answer" "a batch card's summary says first what it is"; do
  lacks "$out" "$gone"
done
lacks "$out" "the user reviews the change written for the new intent"
expect_ok crewpy brief swb-1 construct
for want in "End the proposal with \`## Touches\`" "one fenced block listing every path or glob" "refuses code without it" \
  "The revised change goes into the next batch" "The user reads it in a batch, while it is built"; do
  has "$out" "$want"
done
lacks "$out" "Two units are built side by side only when"; lacks "$out" "back in review"
expect_ok crewpy brief swb-1 coder
for want in "Settle <unit>: <what reached it>" "keeping both changes' intents" "The earlier unit is never changed for it" \
  "The one part of it you may edit is the \`## Touches\` block" "wt submit bolt/<bolt> --no-remove" "A unit you come after, constructed again"; do
  has "$out" "$want"
done
lacks "$out" "the user reviewed and approved it"
expect_ok crewpy brief swb-1 verify; has "$out" "\"changed and not declared\""
# A verify is one round with no card (teams.17, record 0027): it checks the code against the change as written, and its
# report marks each finding fix or leave; the conductor takes the marks as they stand and runs one fresh coder on what is
# marked fix, taking nothing to the planner; the coder fixes those alone, and a unit's merge archives its change first.
expect_ok crewpy brief swb-1 conductor
for want in "run verify, once" "Its recommendations are taken as they stand: post no card for it, ask the user nothing about it, take nothing of it to the planner, and choose no findings yourself" \
  "unit run <unit> code \"Fix every finding the verify report at <path> marks fix.\"" "Once that delivers, the unit goes on to merge, with no verify again" \
  "A finding marked leave is left" "A fix round that stops short, is stuck or is no longer running is a stuck stage" \
  "Its merge stage archives the unit's change first" "run its verify, once, and act on its report as for a unit"; do
  has "$out" "$want"
done
lacks "$out" "the user decides with you what is fixed"; lacks "$out" "marked amend"
expect_ok crewpy brief swb-1 verify
for want in "You check the code against the unit's change as it is written, its proposal, specs, design and tasks" \
  "\`## What to do\`" "starting **fix** or **leave**" "A CRITICAL finding is never left." "\"Nothing to do.\"" \
  "nothing verifies the fixes again, and the unit merges" "end it with *What to do* as below"; do
  has "$out" "$want"
done
lacks "$out" "decides with the user"; lacks "$out" "**amend**"
expect_ok crewpy brief swb-1 coder
for want in "you are the unit's one round of fixes after its verify" "marks fix, and only those" "No verify runs after you" \
  "\`openspec archive <unit> --yes\`" "crew reads the merge as delivered only once the bolt holds the change archived" \
  "A chore or a fix has no change to archive"; do
  has "$out" "$want"
done
lacks "$out" "When the prompt carries findings from a verify"; lacks "$out" "leave or amend"
ok "a verify is one round with no card, grounded in the change as written: the report marks each finding fix or leave, one fresh coder fixes what it marks fix, nothing goes to the planner, and the merge archives the change first"
expect_ok crewpy brief wldn reviewer
[[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/reviewer.md left ${BASH_REMATCH[0]} unfilled"
for want in "# You are wldn-reviewer, the reviewer of wldn" "Write nothing but this file" "at the commit the prompt names" \
  "Each section opens with a paragraph of a few sentences saying what the change does and what the user would most care about" \
  "the planner puts that paragraph on the batch's card as you wrote it" "**The decisions it took**" "**Its risks**" \
  "**Its Touches**: what the change edits, named in words" "never as paths" "**What the user would likely care about**" \
  "paragraphs and plain lists that wrap on a phone, with no code block and no table" "the planner posts the batch's one card from it"; do
  has "$out" "$want"
done
for gone in "**What it does**" "the paths it declares" "the batch's cards"; do lacks "$out" "$gone"; done
expect_ok crewpy brief wldn design; has "$out" "\`wldn-reviewer\`, started fresh for each batch"
expect_ok crewpy brief swb-1 ops; has "$out" "(construct, code, verify, settle, merge)"
expect_ok crewpy brief wldn main-ops
for want in "plugin/bin/crew rail --label wldn\` carries its answer" \
  "your submission in step 2, not step 3, is what puts it on main" "while a unit's latest change has been in no batch"; do
  has "$out" "$want"
done
ok "the briefs build units in waves, put changes before the user in batches, and resolve conflicts in the later unit"

# A decision record is accepted only on the user's yes (briefs.15): the design agent commits every record and amendment
# as proposed, runs crew record at each turn of its status once it is on the kit's main, which raises, changes and closes
# the record's one card in its name, adopts the card by the line crew record prints, names a rule-decided choice in an
# alternatives file, never settled silently, and queues nothing before the yes; it posts and closes no record card, and
# the planner and the conductors post none.
expect_ok crewpy brief wldn design
for want in "Every decision record you write, and every amendment you make to one, is committed as proposed" \
  "put to the user on one Pending You card in the record's own words, which crew raises for it through \`crew record\`" \
  "It is accepted only on the user's yes, given in this pane or on that card, and the record says so" \
  "Your own reading never accepts a record" "\`status: proposed\`" "accepted only on their yes.)" \
  "Queue no unit from a proposed record or amendment" "Only then queue the units it calls for" \
  "the record's deciders line quotes those words as the user's decision" \
  "At each turn of a record's status, once the commit that holds it has landed on the kit's main, run \`$CREW/plugin/bin/crew record <kit> <number> --proposed|--accepted|--rejected\`" \
  "the kit one of atlas-kit, breadboard-kit, switchboard-kit" "refuses a status the file there does not hold" \
  "\`record/<kit>/<number>\`, one card however often the record is revised" \
  "adopt it with the line the command prints, \`call get_request (requestId <id>, name wldn-design)\`" \
  "run it with \`--settled-in-pane\`: crew records their yes as given here, and no card is raised" \
  "You post and close no record card yourself: crew does both" \
  "a rule-decided choice is never settled silently" "the rules that decided and each rule as it would read loosened" \
  "\`crew record … --proposed --alternatives <file>\`" "loosen the rules as drafted and take the other path, accept the record as ruled, or send it back" \
  "run \`crew record … --proposed\` again: the card you were answered on is closed, naming the new commit, and the revised record goes on a new card that follows it" \
  "run \`crew record … --accepted\`, which closes the card" "run \`crew record … --rejected\`, which closes the card" \
  "set \`status: rejected\` with the user's words, and take out each rule drawn from it" \
  "A kit's main moves only through sluice (\`state.3\`), so you never commit on it" "wt submit main --no-remove" \
  "<the kit's folder>/places/design-<topic> origin/main\`" "you level nothing" "then \`git merge origin/main\`" \
  "once its \`.config/sluice.toml\` names a policy for main" \
  "Run \`crew record … --proposed\` for each proposed record or amendment on your kits' main that has none open" \
  "At your start, once you have called \`whoami\` and \`list_pending\` as *Asking the user* says, read \`$CREW/plugin/bin/crew rail --label wldn\`" \
  "Never run \`npx pendingyou\` or \`pendingyou hold\`" "leave every other card alone" \
  "A record you write or amend is proposed until the user accepts it" "quotes the user's words as their decision"; do
  has "$out" "$want"
done
for gone in "record/<kit>/<number>/<commit>" "The record's card is the one card you post" "post a new card for the new version" \
  "Close the card with \`ack_answer\`" "Accept decision record <number>"; do
  lacks "$out" "$gone"
done
for brief in "wldn planner" "swb-1 conductor"; do expect_ok crewpy brief $brief; lacks "$out" "record/<kit>"; done
ok "the design agent runs crew record at each turn of a record's status, which raises, changes and closes its one card, names a rule-decided choice, accepts a record only on the user's yes and queues nothing before; no brief posts a record card"

# A chore (plan.11): planned maintenance with no change, no construct and no review, its every commit carrying its trailer.
expect_ok crewpy brief swb-1 coder
for want in "## A chore" "Your worktree is on \`chore/<name>\`, and the prompt starts \`Chore <name>:\`" "Do exactly what they say" \
  '--trailer "Chore: <name>"' "crew refuses its merge while a commit beyond the bolt lacks it" \
  "Touch nothing under \`openspec/\` but the archive of a change whose every task is ticked" "\`openspec archive <change> --yes\`" \
  "A chore never grows" "the change it would archive has a task open"; do has "$out" "$want"; done
expect_ok crewpy brief swb-1 verify
for want in "## A chore" "\`Verify chore <name>: <its words>\`" "\`git log @{upstream}..HEAD\`" "carries the trailer \`Chore: <name>\`" \
  "nothing under \`openspec/\` changed but the archive" "You change nothing here either" "\`verify-<chore>-<YYYYMMDD-HHMM>.md\`"; do has "$out" "$want"; done
expect_ok crewpy brief swb-1 conductor
for want in "A bolt may also hold **chores**" "with no construct, no change and no review" "chore run <chore> code" "chore run <chore> verify" \
  "chore run <chore> merge" "chore wait <chore>" "chore order" "chore after" "A chore takes its turn in the plan's order with the units" \
  "has no construct and no batch" "until its verify has delivered, every commit of its own carries its trailer and everything it comes after has merged" \
  "A unit that comes after a chore is constructed once the chore's code has delivered" "never waiting on a merge: its place takes their work as it stands" "each holding one unit, chore or fix in flight"; do
  has "$out" "$want"
done
expect_ok crewpy brief wldn planner
for want in "**Unit, fix or chore.**" "chore add <chore> \"<what is done>\" --bolt <bolt>" "A chore is never split or amended" \
  "its words change by a proposal that drops it and adds it again" "A batch of chores" "chore by chore on the card" \
  "a new unit or chore ticked" "\`unit add\` or \`chore add\`"; do has "$out" "$want"; done
expect_ok crewpy brief wldn design
has "$out" "is queued the same way as a chore: \`$CREW/plugin/bin/crew chore add <chore> \"<what is done>\" --repo <kit>\`"
ok "the coder, verifier, conductor, planner and design agent each carry what a chore is to them"
