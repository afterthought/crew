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
for want in "crew card session" "crew card wait" "answeredHere" "Never open a browser for a card" "never run \`plannotator\` yourself" \
  "it has nothing to read, so it carries no link"; do
  has "$out" "$want"
done
ok "a conductor opens nothing, its landing card carries no link, and the card discipline says how a session is started"
# The words a row's card posted again carries, after its link and its bolt, so the user tells the live copy from the
# dead one (ADR 0005, "A card belongs to the host's sign-in").
lost_card='"An older copy of this card is dead: it can no longer be answered, so dismiss it in the app. Answer this one."'
cards_say() {  # the card discipline the planner's and the conductor's briefs share
  for want in "begins with the link to the card's plannotator session, then names the bolt" "in the document's own words" \
    "never reworded" "No card carries a path" "an empty list as its files touched" \
    'one entry in its links, labelled "Read and annotate it in plannotator"' "The link is no artifact" \
    "update its summary, background and links together" \
    "give it the form its row takes, as your brief says" "crew refuses a row's card in another form, and names the form to use" \
    'kind `image` with `upload: true`' "with its content type" 'Never attach an image as kind `path`' \
    'kind `code` with lang `markdown`' "never an uploaded file and never HTML" "reached through the card's plannotator link" \
    "A proposal's card is what \`$CREW/plugin/bin/crew plan card <n> --label wldn\` prints" "it links no session but when that says so" \
    "a proposal's card carries the picture and the text" "A proposal's card links no session, since it holds the proposal whole" \
    "but for one of more than fifteen new units" "reads \"not found\"" "whenever Pending You has you call \`whoami\` again" \
    "$lost_card" "under the row's key" "posted again by nobody" "The one exception is a lost card"; do
    has "$out" "$want"
  done
  lacks "$out" "something, a proposal, a batch's changes"
  lacks "$out" "as its artifact of kind"; lacks "$out" "row's answers as its options"; lacks "$out" "leave the card's artifacts empty"
}
cards_say
has "$out" "it names the bolt, and it has nothing to read, so it carries no link and no path"
lacks "$out" "two or three plain sentences"; lacks "$out" "post its review card"
ok "a conductor's cards say the document's own words, the link and the bolt first, and no path"
for want in "rail --label wldn" "idempotencyKey" "create-area:" "pendingyou hold" \
  "keyed \`land/<bolt>/<head>\`, marked high stakes" "Land bolt <bolt>. The user approved it on Pending You." \
  "post its landing card" "Send no such tell for what has a card" "The kits: switchboard-kit: WilldanGroup/switchboard-kit." \
  "A row's key changes when what it asks changes" "Pending You gives that card back" \
  "close a landing card you have open with what the fix changed" "under the key the rail then shows"; do
  has "$out" "$want"
done
for want in "an \`approve\` card with \`highStakes\` true" "never an \`action\` and never a step or command for the user to land it" \
  "since its yes has you tell \`wldn-ops\` to land"; do
  has "$out" "$want"
done
lacks "$out" "offering approval"; lacks "$out" "Looks good"; lacks "$out" "Needs changes"; lacks "$out" "\`review\` card"
for gone in "verify/<unit>/<stamp>" "post its verify card" "a \`multi\` when the user may pick several findings" "An answer on a verify card"; do
  lacks "$out" "$gone"
done
ok "the conductor posts no verify card, and its landing card is a high-stakes approval and never a step to land"
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
for want in "crew card session" "crew card wait" "answeredHere" "Never open a browser for a card" \
  "crew plan card <n> --label wldn\` prints, drawn by crew from the plan and the proposal" "every one ticked, each cleared to leave it out" \
  "Post its \`card\` as it is" "upload its picture from \`picture\` as the card discipline says for an image" \
  "A proposal's card links no session" "start one only when \`session\` is true, for a proposal of more than fifteen new units" \
  "crew refuses a proposal's card in any other form" "crew plan answer <n> <question> <answer>... --label wldn" \
  "\`units-<k>\` and the units left ticked" "--note \"<the user's note>\"" "with \`ack_answer\` once crew has applied or declined" \
  "add \`--clear <unit>\` for each of them" "An approval applies the commands the user read and kept" \
  "when a command they kept names a unit they left out"; do has "$out" "$want"; done
lacks "$out" "offers approval"; lacks "$out" "exactly as the user read them"; lacks "$out" "not the page as a file"
cards_say
lacks "$out" "Its words are the proposal's case and each of its changes in a line"
for want in "rail --label wldn" "idempotencyKey" "create-area:" "pendingyou hold" "keyed \`proposal/<n>\`" "or answers your card" \
  "close the old proposal's card" "it no longer waits on that conductor" "The kits: atlas-kit: WilldanGroup/atlas-kit; breadboard-kit" \
  "A row's key changes when what it asks changes" "Pending You gives that card back"; do
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
expect_ok crewpy brief wldn main-ops
for want in "bolt submit <bolt>" "bolt land <bolt>" "## Deploying main" "the bolt lands either way" \
  "Every agent of clients/willdan lands a bolt this one way" "Nothing else is a word to land" "The word to land is also the word to push main" \
  "git -C <kit>/main push origin main" "A landing deploys nothing (\`plan.14\`)" "A landing is never that word" \
  "ops approve <env> --to <sha> --label wldn" "keyed \`deploy/<env>/<head>\`" "deploy nothing yourself" "keyed \`op/<env>/<n>\`" \
  "run it in the background and wait for it to end" "through the kit's remove hooks" "never yours to approve or skip"; do has "$out" "$want"; done
lacks "$out" "wt merge"
for want in "$lost_card" "reads \"not found\"" "under the row's key" "posted again by nobody"; do has "$out" "$want"; done
has "$out" $'A landing is never that word.\n\nA card of yours is lost when it reads'
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
ok "the conductor waits for every stage through crew and never reads a pane for its outcome; every stage stops short with crew needs, and ops tells the conductor"

# A landing that conflicts lands nothing and goes back to the team as a fix that takes main into the bolt (plan.8,
# teams.5, record 0026): main-ops submits the bolt with crew bolt submit and passes on sluice's words, the conductor
# starts the fix and merges it as any fix, its agent merges main in, and nothing but sluice moves a bolt's branch or
# main; the bolt's proof is its verification (record 0025), and ops proves and deploys nothing.
expect_ok crewpy brief wldn main-ops
for want in "tell the bolt's conductor and the user sluice's words" "its landing comes back to the user on a new card" \
  "never merge, rebase, reset or fast-forward main or a bolt's branch by git" "When main is behind GitHub's, crew refuses the landing and names how far: stop and tell the user" \
  "shows every unit merged and the bolt's verification green" "git read-tree -m -u <main's commit before> main" \
  "the checkout is stale after every landing until it is levelled" "nothing of yours or crew's catches it up to GitHub's"; do
  has "$out" "$want"
done
lacks "$out" "git rebase --abort"; lacks "$out" "proof in dev"
expect_ok crewpy brief swb-1 conductor
for want in "Take main into the bolt" "a submission to the bolt like any other" \
  "once the bolt holds it and its verification is green, post the landing card again, under the bolt's new head" \
  "That verification is the bolt's proof"; do
  has "$out" "$want"
done
lacks "$out" "Carry the bolt onto main"; lacks "$out" "proof file"
expect_ok crewpy brief swb-1 coder
for want in "Take main into the bolt" "git merge main" "Never rebase the bolt's commits onto main" "keeping both intents, main's and the bolt's" \
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

# A team's cards are its conductor's (briefs.11): ops and every stage post no card and make no area, the landing card
# asks only for the landing once the bolt's verification is green, a step for the user being a deploy's, a note naming
# a defect is a fix, and the card discipline the planner and the conductor share says crew refuses any other key.
for role in construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  has "$out" "Post no Pending You card and make no area: your team's cards are its conductor's, and crew refuses any other."
done
expect_ok crewpy brief swb-1 ops; has "$out" "post no card: your team's cards are its conductor's, and crew refuses any other"
expect_ok crewpy brief swb-1 conductor
for want in "once every unit and chore has merged and its verification is green, keyed \`land/<bolt>/<head>\`" \
  "The card asks only for the landing" "never a question on this one" \
  "A note on the landing card that names a defect is never a landing" "shows the bolt's verification green"; do
  has "$out" "$want"
done
lacks "$out" "Left for the user"; lacks "$out" "the card asks them first"
lacks "$out" "ops posts"; lacks "$out" "ops's card"
for brief in "swb-1 conductor" "wldn planner"; do
  expect_ok crewpy brief $brief
  has "$out" "crew refuses a card you post under any key but a rail row's of your own, and an area under any key but \`create-area:<owner>/<kit>\`, and its refusal names the key to use."
done
ok "ops and every stage post no card, the landing card asks only for the landing once the verification is green, and the card discipline says crew refuses any other key"

# Units build at once and are reviewed in batches (teams.12 to teams.14, briefs.1, briefs.2, briefs.4, briefs.12): the
# conductor constructs in waves and codes a planned unit with no review, acts on the planner's notes and posts no card for
# a unit; the planner runs the reviewer and posts each batch as one notice, asking nothing, with one reading session on
# the batch, and sends the notes from the session and the card to each unit they speak of (briefs.9, briefs.13);
# construct writes Touches as a block crew reads;
# the coder keeps both intents, settles, corrects only Touches, and submits to sluice; verify names what was changed
# and not declared; the reviewer writes its summary and nothing else, as prose opening each unit with the paragraph the
# card carries; main-ops checks the landing row before it submits a bolt to main.
expect_ok crewpy brief swb-1 conductor
for want in "Construct in waves" "Start code as soon as" "shows a unit \`planned\`" "with nobody asked to approve it" \
  "You post no card for a unit, and open nothing for a batch" "run construct again with them, word for word" \
  "hold the notes until it settles" "Overlapping *Touches* never hold a unit back" "crew puts the later after the earlier itself" \
  "unit run <unit> settle \"<what reached it>\"" "## Forecasts and settling" "The earlier unit is never changed for it" \
  "the card names them too" "The merge stage submits the unit to the bolt, \`wt submit bolt/<bolt>\`" "changed and did not declare in its Touches"; do
  has "$out" "$want"
done
for gone in "build them one after the other" "When in doubt, don't" "## Review with the user"; do lacks "$out" "$gone"; done
expect_ok crewpy brief wldn planner
for want in "## Batches" "review wldn\`" "review wldn --wait\`" "card session batch/<n> --label wldn\`" \
  "card wait batch/<n> --label wldn\`" "keyed \`batch/<n>\`, naming every unit of the batch with its team, however many" \
  "a batch is never split across cards" "The card is a notice, kind \`fyi\`, intent \`heads_up\`" \
  "\"This is batch <n> of wldn: the <count> changes written or rewritten since the last batch, already being built." \
  "Nothing to answer and nothing to approve." "annotate the changes in the reading session and send them there" \
  "or write them in this card's note, naming the change" "Tap once when you're done" \
  "\"Read and annotate the whole batch, its summary and every change: <the link>\"" "the opening paragraph the reviewer wrote for it" \
  "its one link is the session's" "It never offers a choice of units, asks a question, approves anything or attaches the summary" \
  "go at once, word for word, to the conductor of each unit they speak of" \
  "goes to every unit's conductor, saying it named no unit you could tell" "Neither answers or withdraws the card" \
  "its note, if any, goes the same way" "or to every unit's conductor when it names none, saying so" \
  "Never split, reword or summarize the user's words" "you never run a stage" "Never answer a batch card yourself" \
  "one per batch, keyed \`batch/<n>\`: a notice that says what it is, names every unit, asks nothing and links the batch's one reading session" \
  "for a batch card \`batch/<n>\`, one session on the whole batch" \
  "A batch card's session holds the batch's notes, so a decision in it is never the card's answer"; do
  has "$out" "$want"
done
for gone in "of at most five units" "which need notes?" "one in words for the notes" "A unit not picked is fine" \
  "card session batch/<n> <unit>" "card session batch/<n>-<k> <unit>" "send each picked unit's notes" "once for each of its units"; do
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
  "your submission in step 2, not step 4, is what puts it on main" "while a unit's latest change has been in no batch"; do
  has "$out" "$want"
done
ok "the briefs build units in waves, put changes before the user in batches, and resolve conflicts in the later unit"

# A decision record is accepted only on the user's yes (briefs.15): the design agent commits every record and amendment
# as proposed, puts it to the user on its one card, under the record key, in the record's words, records their yes,
# note or no, and queues nothing from it before the yes; the planner and the conductors post no record card.
expect_ok crewpy brief wldn design
for want in "Every decision record you write, and every amendment you make to one, is committed as proposed" \
  "put to the user on one Pending You card in the record's own words" "It is accepted only on the user's yes, and the record says so" \
  "Your own reading never accepts a record" "\`status: proposed\`" "accepted only on their yes.)" \
  "Queue no unit from a proposed record or amendment" "Only then queue the units it calls for" \
  "the record's deciders line quotes those words as the user's decision" "Your own words, recorded as your decision:" \
  "post a new card for the new version, under the new commit's key" \
  "set \`status: rejected\` with the user's words, and take out each rule drawn from it" \
  "The record's card is the one card you post" "\`record/<kit>/<number>/<commit>\`" "one of atlas-kit, breadboard-kit, switchboard-kit" \
  "the commit that proposed the record or the amendment, which reaches the kit's main through sluice" \
  "A kit's main moves only through sluice (\`state.3\`), so you never commit on it" "wt submit main --no-remove" \
  "read-tree -m -u <main's commit before you submitted> main" "Post the card once that commit has landed on main" \
  '"risk": "low", "reversible": true}`, no options, no steps and `blocking` false' \
  "Accept decision record <number> in <kit>: <the record's title>?" "kind \`code\` with lang \`markdown\`" \
  "No card carries a path" "links no plannotator session" \
  "Post a card for each proposed record or amendment of your kits that has none open" "create-area:<owner>/<kit>" \
  "Never run \`npx pendingyou\` or \`pendingyou hold\`" "leave every other card alone" \
  "A record you write or amend is proposed until the user accepts it" "quotes the user's words as their decision"; do
  has "$out" "$want"
done
for brief in "wldn planner" "swb-1 conductor"; do expect_ok crewpy brief $brief; lacks "$out" "record/<kit>"; done
ok "the design agent proposes every record on one card under its record key, accepts it only on the user's yes, and queues nothing before; no other brief posts a record card"

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
  "for each five units or chores the proposal makes new to a bolt" "\`unit add\` or \`chore add\`"; do has "$out" "$want"; done
expect_ok crewpy brief wldn design
has "$out" "is queued the same way as a chore: \`$CREW/plugin/bin/crew chore add <chore> \"<what is done>\" --repo <kit>\`"
ok "the coder, verifier, conductor, planner and design agent each carry what a chore is to them"
