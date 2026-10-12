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

expect_ok crewpy brief swb-1 coder; has "$out" "run \`wt merge\` in the background and wait for it to end"
ok "the coder runs a merge, whose checks can outlast a command's time limit, in the background"

expect_ok crewpy brief swb-1 coder; has "$out" "Never run the whole suite by hand: the merge's gate runs it."
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
for want in "open nothing, and recite no command" "open nothing for a batch" "never its number alone"; do has "$out" "$want"; done
for want in "crew card session" "crew card wait" "answeredHere" "Never open a browser for a card" "never run \`plannotator\` yourself" \
  "carrying the link to the plannotator session on the report, not the report as a file" "it has nothing to read, so it carries no link"; do
  has "$out" "$want"
done
ok "a conductor's verify card links the session crew starts on the report, and it opens nothing"
cards_say() {  # the card discipline the planner's and the conductor's briefs share
  for want in "begins with the link to the card's plannotator session, then names the bolt" "in the document's own words" \
    "never reworded" "No card carries a path" "an empty list as its files touched" \
    'one entry in its links, labelled "Read and annotate it in plannotator"' "The link is no artifact" \
    "update its summary, background and links together" \
    "give it the form its row takes, as your brief says" "crew refuses a row's card in another form, and names the form to use"; do
    has "$out" "$want"
  done
  lacks "$out" "as its artifact of kind"; lacks "$out" "row's answers as its options"
}
cards_say
for want in "its words each finding the report raised in a line, with what you would do about it" \
  "it names the bolt, and it has nothing to read, so it carries no link and no path"; do
  has "$out" "$want"
done
lacks "$out" "two or three plain sentences"; lacks "$out" "post its review card"
ok "a conductor's cards say the document's own words, the link and the bolt first, and no path"
for want in "rail --label wldn" "idempotencyKey" "create-area:" "pendingyou hold" "keyed \`verify/<unit>/<stamp>\`" \
  "keyed \`land/<bolt>/<head>\`, marked high stakes" "Land bolt <bolt>. The user approved it on Pending You." "post its verify card" \
  "post its landing card" "Send no such tell for what has a card" "The kits: switchboard-kit: WilldanGroup/switchboard-kit." \
  "A row's key changes when what it asks changes" "Pending You gives that card back" \
  "close a landing card you have open with what the fix changed" "under the key the rail then shows"; do
  has "$out" "$want"
done
for want in "it is a \`choice\` card, or a \`multi\` when the user may pick several findings, whose options are what you would do" \
  "an \`approve\` card with \`highStakes\` true" "never an \`action\` and never a step or command for the user to land it" \
  "since its yes has you tell \`wldn-ops\` to land"; do
  has "$out" "$want"
done
lacks "$out" "offering approval"; lacks "$out" "Looks good"; lacks "$out" "Needs changes"; lacks "$out" "\`review\` card"
ok "the conductor's verify card is a choice of its options, its landing card a high-stakes approval and never a step to land"
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
  "carries the link to the plannotator session on the page" "not the page as a file" \
  "is a Pending You \`approve\` card, with a note for changes or for dropping it"; do has "$out" "$want"; done
lacks "$out" "offers approval"
cards_say
has "$out" "Its words are the proposal's case and each of its changes in a line, as \`"; has "$out" "plan proposed <n>\` words them, with no command."
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
for want in "bolt give <team>" "up <team>" "account ia" "one bolt deploy at a time" "It is the one tell not about a bolt that is yours" "ops step\` command that records it done or failed"; do has "$out" "$want"; done
has "$out" $'The teams here:\n\n- `atl-1` builds Atlas'; has "$out" $'its conductor is `atl-1-conductor`\n\nYou give these teams'
expect_ok crewpy brief wldn main-ops
for want in "wt merge main --no-squash --no-remove" "bolt land <bolt>" "## Deploying main" "the bolt lands either way" \
  "Every agent of clients/willdan lands a bolt this one way" "Nothing else is a word to land" "The word to land is also the word to push main" \
  "git -C <kit>/main push origin main" "A landing deploys nothing (\`plan.14\`)" "A landing is never that word" \
  "ops approve <env> --to <sha> --label wldn" "keyed \`deploy/<env>/<head>\`" "deploy nothing yourself" "keyed \`op/<env>/<n>\`" \
  "run \`wt merge\` in the background and wait for it to end" "through the kit's remove hooks" "never yours to approve or skip"; do has "$out" "$want"; done
expect_fail "no definition 'conductor' for a main level" crewpy brief wldn conductor
ok "every main-level brief prints for wldn with no unfilled token"

expect_ok crewpy brief wldn operator
has "$out" "deployed by the partition's main-level ops, \`wldn-ops\`, on the user's yes for that deploy"; has "$out" "never hand the user a deploy command"
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
expect_ok crewpy brief swb-1 conductor
has "$out" 'prove swb-1`, then wait for its proof with `'
ok "no brief prompts another agent through herdr, and the conductor asks ops for the bolt's proof through crew"

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

# A stage ends at its deliverable (teams.4): the conductor waits for every stage, fix and proof through crew and reads
# no pane for an outcome, takes a stuck stage to the user and runs a stopped-short one again with the answer; the stage
# agents and ops say what they need with crew needs; verify's report and ops's proof file are written once, whole.
expect_ok crewpy brief swb-1 conductor
for want in "unit wait <unit>\` as a background command" "you never read a pane for one" "**Stuck**" \
  "run the stage again or wait again only on the user's word" "fix swb-1 <name> --wait\`" "prove swb-1 --wait\`" \
  "run the stage again with the answer as its words" "prove swb-1 \"<the answer>\""; do
  has "$out" "$want"
done
for gone in "If it is waiting on a question for the user, leave it for the user" "When its agent settles, merge it" "tell swb-1-ops \"Deploy"; do
  lacks "$out" "$gone"
done
for role in construct coder verify ops; do
  expect_ok crewpy brief swb-1 $role
  has "$out" 'needs "<what you tried and what you need>"` and end your turn'
  has "$out" "Never ask in your pane: nobody watches it."
  has "$out" "Ending a turn to wait on something you started in the background is fine"
done
expect_ok crewpy brief swb-1 ops
has "$out" "reports/proof-<bolt>-<YYYYMMDD-HHMM>.md"; has "$out" "once, whole"; has "$out" "crew ends the proof once it is there"
lacks "$out" "/tmp/ops-proof"
expect_ok crewpy brief swb-1 verify
has "$out" "unchanged and whole"; has "$out" "crew ends the stage once it is there"
ok "the conductor waits for every stage through crew and never reads a pane for its outcome; every stage, and ops's proof, stops short with crew needs"

# A landing whose rebase conflicts lands nothing and goes back to the team as a fix that carries the bolt onto main
# (plan.8, teams.5): main-ops aborts it and names the commit and files, the conductor starts the fix and proves the bolt
# again after crew's move, the fix's agent replays the bolt onto main and adds nothing, and ops reads the verification
# the move starts.
expect_ok crewpy brief wldn main-ops
for want in "git rebase --abort" "Tell the bolt's conductor and the user that commit and those files" \
  "for the bolt's head as it is now" "its landing comes back to the user on a new card"; do
  has "$out" "$want"
done
expect_ok crewpy brief swb-1 conductor
for want in "Carry the bolt onto main" "prove the bolt again" "post the landing card again, under the bolt's new head, only once that proof is clean" \
  "fix swb-1 <name> --merge\` as for any fix"; do
  has "$out" "$want"
done
expect_ok crewpy brief swb-1 coder
for want in "Carry the bolt onto main" "git rebase main" "add no commit" "keeping both intents, main's and the bolt's" \
  "under \`openspec/\` too"; do
  has "$out" "$want"
done
expect_ok crewpy brief swb-1 ops
for want in "crew's move of the bolt to a fix that carries it onto main starts one too" "a bolt whose head moved is proven again"; do
  has "$out" "$want"
done
ok "a landing's conflict becomes a fix that carries the bolt onto main, and the bolt is proven again before it lands"

# A team's cards are its conductor's (briefs.11): ops and every stage post no card and make no area, ops writes what
# a proof leaves the user in its proof file, the conductor asks it on the landing card before approval and treats a
# failed step as a fix, and the card discipline the planner and the conductor share says crew refuses any other key.
for role in construct coder verify ops; do
  expect_ok crewpy brief swb-1 $role
  has "$out" "Post no Pending You card and make no area: your team's cards are its conductor's, and crew refuses any other."
done
expect_ok crewpy brief swb-1 ops
for want in "under *Left for the user*" "what they will see when it worked" "Each is ⏳ in the glyph list, waiting on the user." \
  "clean but for the user's steps: the conductor asks them on the bolt's landing card, so you post no card for them"; do
  has "$out" "$want"
done
expect_ok crewpy brief swb-1 conductor
for want in "once ops's proof file reports it clean, or clean but for steps it leaves the user, keyed \`land/<bolt>/<head>\`" \
  "the card asks them first" "the steps are the card's \`action\`" "Approving it then means the user took them, they worked" \
  "A note on the landing card that a step failed is a defect, never a landing" \
  "When the proof is clean, or clean but for the user's steps"; do
  has "$out" "$want"
done
lacks "$out" "ops posts"; lacks "$out" "ops's card"
for brief in "swb-1 conductor" "wldn planner"; do
  expect_ok crewpy brief $brief
  has "$out" "crew refuses a card you post under any key but a rail row's of your own, and an area under any key but \`create-area:<owner>/<kit>\`, and its refusal names the key to use."
done
ok "ops and every stage post no card, the landing card asks the proof's steps for the user first, and the card discipline says crew refuses any other key"

# Units build at once and are reviewed in batches (teams.12 to teams.14, briefs.1, briefs.2, briefs.4, briefs.12): the
# conductor constructs in waves and codes a planned unit with no review, acts on the planner's notes and posts no card for
# a unit; the planner runs the reviewer and posts each batch's cards; construct writes Touches as a block crew reads;
# the coder keeps both intents, settles, corrects only Touches, and submits where the kit uses sluice; verify names what
# was changed and not declared; the reviewer writes its summary and nothing else; main-ops checks the landing row before
# it merges a bolt into main.
expect_ok crewpy brief swb-1 conductor
for want in "Construct in waves" "Start code as soon as" "shows a unit \`planned\`" "with nobody asked to approve it" \
  "You post no card for a unit, and open nothing for a batch" "run construct again with them, word for word" \
  "hold the notes until it settles" "Overlapping *Touches* never hold a unit back" "crew puts the later after the earlier itself" \
  "unit run <unit> settle \"<what reached it>\"" "## Forecasts and settling" "The earlier unit is never changed for it" \
  "the card names them too" "or \`wt submit\` where the kit merges through sluice" "changed and did not declare in its Touches"; do
  has "$out" "$want"
done
for gone in "build them one after the other" "When in doubt, don't" "## Review with the user"; do lacks "$out" "$gone"; done
expect_ok crewpy brief wldn planner
for want in "## Batches" "review wldn\`" "review wldn --wait\`" "card session batch/<n>-<k> <unit> --label wldn" \
  "\"which need notes?\"" "card wait batch/<n>-<k> <unit> --label wldn" "send each picked unit's notes, verbatim, to its team's conductor" \
  "A unit not picked is fine" "you never run a stage" "Never answer a batch card yourself" "keyed \`batch/<n>-<k>\`" "of at most five units"; do
  has "$out" "$want"
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
  "The one part of it you may edit is the \`## Touches\` block" "\`wt submit bolt/<bolt>\`" "A unit you come after, constructed again"; do
  has "$out" "$want"
done
lacks "$out" "the user reviewed and approved it"
expect_ok crewpy brief swb-1 verify; has "$out" "\"changed and not declared\""
expect_ok crewpy brief wldn reviewer
[[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/reviewer.md left ${BASH_REMATCH[0]} unfilled"
for want in "# You are wldn-reviewer, the reviewer of wldn" "Write nothing but this file" "at the commit the prompt names" \
  "**What it does**" "**The decisions it took**" "**Its risks**" "**Its Touches**" "**What the user would likely care about**"; do
  has "$out" "$want"
done
expect_ok crewpy brief wldn design; has "$out" "\`wldn-reviewer\`, started fresh for each batch"
expect_ok crewpy brief swb-1 ops; has "$out" "(construct, code, verify, settle, merge)"
expect_ok crewpy brief wldn main-ops
for want in "plugin/bin/crew rail --label wldn\` carries its answer" \
  "your merge in step 3, not step 5, is what puts it on main" "while a unit's latest change has been in no batch"; do
  has "$out" "$want"
done
ok "the briefs build units in waves, put changes before the user in batches, and resolve conflicts in the later unit"
