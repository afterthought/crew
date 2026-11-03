// crew's mod (hooks/status.js) on the views the host's follower writes (board.py agent_views), the main-level roles'
// alone (Decision 11 of the-team-machinery-leaves): that a crew agent's session finds its own view, by its environment
// or its session record, and draws it above its prompt, its open cards first, and only the stale line once the views
// are old. Each case fails when the mod draws the wrong view. What each view says is crew's logic tier
// (tests/py/test_board.py, code.8). tests/suite runs these as the task mod, through tests/mod.
import { expect, mock, test } from 'claude-code/testing'

const READ_AT = Date.parse('2026-10-12T14:00:00Z')
const VIEWS = {
  read_at: '2026-10-12T14:00:00Z',
  stale_after_ms: 90000,
  stale: [['  ', null], ["crew: the board was last read at 2026-10-12 14:00, too long ago to show; crew's follower on mac-studio has not refreshed it since", 'dim']],
  views: {
    'swancloud-planner': [
      [['swancloud plan', 'bold'], ['  ', null], ['1 in flight', null]],
      [['  ', null], ['crew', null], ['  ', null], ['◕◔', null], ['  ', null], ['curation-and-holds', null], ['  ', null], ['0 of 2 merged', null]],
      [['    ', null], ['◕', null], ['  ', null], ['a-queued-unit-can-take-a-signal', null], ['  ', null], ['verify 3/3', null]],
    ],
  },
}
const BAND = {
  plugin: 'crew',
  component: 'AbovePrompt',
  viewport: { columns: 100, rows: 30 },
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 95, scroll: { offset: 0, bodyRows: 9 }, view: {} },
} as const

// A session of the given environment, its record and its host's views, started and its band drawn on the terminal.
async function band($, on, { env = {}, record = undefined, views = VIEWS, now = READ_AT + 1000 } = {}) {
  mock.env(on, { HOME: '/home/chuck', ...env })
  mock.clock(on, { now })
  on('session.id', () => ({ value: 'sid-1' }))
  on('fs.stat', ($, e) => (views && e.path === '/home/chuck/.cache/crew/board/swancloud.agents.json' ? { value: { kind: 'file', size: 1, mtimeMs: 1, isLink: false } } : { deny: 'ENOENT' }))
  on('fs.read', ($, e) =>
    views && e.path.endsWith('/swancloud.agents.json') ? { value: JSON.stringify(views) }
      : record && e.path === '/home/chuck/.local/state/crew/sessions/sid-1' ? { value: record }
      : { deny: 'ENOENT' })
  on('session.start', () => ({ cwd: '/work' }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  return $.ui.mount({ ...BAND, surface: 'terminal' })
}

test('the planner sees its view above its prompt, each bolt in flight a ledger', async ($, on) => {
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' } })
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /verify 3\/3/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /has not refreshed/ })).toBeUndefined()
})

// wldn, 2026-10-20: swb-1's and awb-1's bands named bolts that had landed days before, drawn from views the follower
// had stopped refreshing, their stale line below the band's rows (signals 2026-10-20-wldn-operator-mac-studio-a4671eb9/01
// and b7a096b6/01 on wldn/main).
test('views older than the follower refreshes them name no bolt and no card, only when they were read', async ($, on) => {
  const card = [['  ', null], ['your question', null], ['  ', null], ['req_q1', 'dim'], ['  ', null], ['open 14m', null]]
  const ui = await band($, on, {
    env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' },
    views: { ...VIEWS, cards: { 'swancloud-planner': [card] } },
    now: READ_AT + 120000,
  })
  expect(await ui.find({ type: 'Text', text: /crew: the board was last read at 2026-10-12 14:00, too long ago to show; crew's follower on mac-studio has not refreshed it since/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: /your question/ })).toBeUndefined()
})

test('a session herdr resumed bare finds its agent in its session record', async ($, on) => {
  const ui = await band($, on, { record: 'CREW_AGENT=swancloud-planner\nCREW_LABEL=swancloud\nCREW_CWD=/work\n' })
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeDefined()
})

test("an agent's open cards are drawn above its view", async ($, on) => {
  const card = [['  ', null], ['your question', null], ['  ', null], ['req_q1', 'dim'], ['  ', null], ['open 14m', null]]
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, cards: { 'swancloud-planner': [card] } } })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  const at = (pattern) => lines.findIndex((l) => pattern.test(l))
  expect(at(/^ {2}your question {2}req_q1 {2}open 14m$/)).toBeGreaterThanOrEqual(0)
  expect(at(/curation-and-holds/)).toBeGreaterThan(at(/your question/))
})

// crew-board "A merge standing in sluice" and "A landing standing in sluice": the numbers sluice gave the submissions
// are on the ledger's lines as board.py's ledger_rows draws them, and the band shows them as they are (teams.22).
test("a ledger's standing merge and landing are drawn with their numbers", async ($, on) => {
  const ledger = [
    [['  ', null], ['crew', null], ['  ', null], ['◕◔', null], ['  ', null], ['curation-and-holds', null], ['  ', null], ['landing #355 queued', null], ['  ', null], ['0 of 2 merged', null]],
    [['    ', null], ['◕', null], ['  ', null], ['a-queued-unit-can-take-a-signal', null], ['  ', null], ['verify 3/3', null], ['  ', null], ['#41 under test', null]],
  ]
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, views: { 'swancloud-planner': ledger } } })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  expect(lines.findIndex((l) => /^ {2}crew {2}◕◔ {2}curation-and-holds {2}landing #355 queued {2}0 of 2 merged$/.test(l))).toBeGreaterThanOrEqual(0)
  expect(lines.findIndex((l) => /a-queued-unit-can-take-a-signal {2}verify 3\/3 {2}#41 under test$/.test(l))).toBeGreaterThanOrEqual(0)
})

// crew-board "A held bolt's head line shows its age and who held its time": the head line ends with the bolt's age,
// its minutes by holder and who holds it now, as board.py's bolt_row draws it, and the band shows it as it is (plan.20).
test("a ledger's head line is drawn with the bolt's age and who holds it", async ($, on) => {
  const ledger = [
    [['  ', null], ['crew', null], ['  ', null], ['◕◔', null], ['  ', null], ['curation-and-holds', null], ['  ', null], ['0 of 2 merged', null],
      ['  ', null], ['3h 05m: team 2h 10m, kit 12m, user 40m, nobody 3m; user since 14:02, batch/12', null]],
  ]
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, views: { 'swancloud-planner': ledger } } })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  expect(lines.findIndex((l) => /^ {2}crew {2}◕◔ {2}curation-and-holds {2}0 of 2 merged {2}3h 05m: team 2h 10m, kit 12m, user 40m, nobody 3m; user since 14:02, batch\/12$/.test(l))).toBeGreaterThanOrEqual(0)
})

// crew-board "Minutes that can't be split": a head line holding minutes crew can't split between the team and the kit
// names them team or kit, and why, and the band shows it as board.py's bolt_row draws it (plan.20).
test("a ledger's head line holding a team-or-kit share is drawn with why", async ($, on) => {
  const said = '3h 20m: team 2h 10m, team or kit 12m, nobody 58m; team or kit since 14:05, #41; team or kit: sluice keeps no start of its checks'
  const ledger = [
    [['  ', null], ['crew', null], ['  ', null], ['◕◔', null], ['  ', null], ['curation-and-holds', null], ['  ', null], ['0 of 2 merged', null],
      ['  ', null], [said, null]],
  ]
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, views: { 'swancloud-planner': ledger } } })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  expect(lines.indexOf(`  crew  ◕◔  curation-and-holds  0 of 2 merged  ${said}`)).toBeGreaterThanOrEqual(0)
})

// A bolt that landed on main and whose close crew refused (plan.21): main-level ops's band draws its head line in the
// attention gutter with the refusal's words, as its views say it.
test("main-level ops's band draws a landed bolt crew could not close", async ($, on) => {
  const unclosed = [['! ', null], ['crew', null], ['  ', null], ['●', null], ['  ', null], ['doctor-rows', null],
    ['  ', null], ['landed on main, not closed: chore tidy-rows has not landed on main: it is ready', null], ['  ', null], ['1 of 1 merged', null]]
  const views = { ...VIEWS, views: { ...VIEWS.views, 'swancloud-ops': [[['swancloud operations', 'bold']], unclosed] } }
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-ops', CREW_LABEL: 'swancloud' }, views })
  expect(await ui.find({ type: 'Text', text: /^! crew {2}● {2}doctor-rows {2}landed on main, not closed: chore tidy-rows has not landed on main: it is ready/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeUndefined()
})

// crew-board "A question in the planner's band" and "A fix of main in ops's band": the planner's band draws a place that
// stopped short with its question on its line in its bolt's ledger, and main-level ops's a fix of main in flight with
// its stage, as board.py's planner_view and ops_view draw them.
test("the planner's band draws a place's question in its bolt's ledger and the bolt's Flume stream", async ($, on) => {
  const planner = [
    [['swancloud plan', 'bold'], ['  ', null], ['1 in flight', null], ['  ', null], ['1 place waits on an answer', null]],
    [['  ', null], ['crew', null], ['  ', null], ['◑○', null], ['  ', null], ['x', null], ['  ', null], ['in Flume stream swancloud', null], ['  ', null], ['0 of 2 merged', null]],
    [['    ', null], ['◔', null], ['  ', null], ['a', null], ['  ', null], ['needs', null], ['  ', null], ["asks at construct: Which partition's rail?", null]],
  ]
  const ops = [
    [['swancloud operations', 'bold'], ['  ', null], ['1 fix in flight', null]],
    [['  ', null], ['crew', null], ['  ', null], ['fix main--a-test-reads-its-fixture', null], ['  ', null], ['code 2/5', null], ['  ', null], ['on deneb', 'dim']],
  ]
  const views = { ...VIEWS, views: { 'swancloud-planner': planner, 'swancloud-ops': ops } }
  const asked = await band($, on, { env: { CREW_AGENT: 'swancloud-planner', CREW_LABEL: 'swancloud' }, views })
  expect(await asked.find({ type: 'Text', text: /^ {4}◔ {2}a {2}needs {2}asks at construct: Which partition's rail\?$/ })).toBeDefined()
  expect(await asked.find({ type: 'Text', text: /^ {2}crew {2}◑○ {2}x {2}in Flume stream swancloud {2}0 of 2 merged$/ })).toBeDefined()
  expect(await asked.find({ type: 'Text', text: /main--a-test-reads-its-fixture/ })).toBeUndefined()
})

test("main-level ops's band draws a fix of main in flight with its stage", async ($, on) => {
  const ops = [
    [['swancloud operations', 'bold'], ['  ', null], ['1 fix in flight', null]],
    [['  ', null], ['crew', null], ['  ', null], ['fix main--a-test-reads-its-fixture', null], ['  ', null], ['code 2/5', null], ['  ', null], ['on deneb', 'dim']],
  ]
  const ui = await band($, on, { env: { CREW_AGENT: 'swancloud-ops', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, views: { 'swancloud-ops': ops } } })
  expect(await ui.find({ type: 'Text', text: /^swancloud operations {2}1 fix in flight$/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /^ {2}crew {2}fix main--a-test-reads-its-fixture {2}code 2\/5 {2}on deneb$/ })).toBeDefined()
})

// crew-board "A role that runs as its kind has its view" (Decision 15 of roles-run-as-flume-kinds): a role's run, which
// Flume starts with no environment of crew's, finds its view by its run's name from its place, crew-<role>--<label>, and
// draws its turn and the asks that wait above its role's view, as board.py's run_rows draws them.
const RUN = '/home/chuck/.local/state/flume/places/crew-planner--swancloud'
const runView = (waits, took) => [
  [['swancloud-planner run', 'bold'], ['  ', null], ['in stream swancloud-main', null], ['  ', null], ['turn 1 took ' + took.length, null], ['  ', null], [waits, null]],
  ...took.map((t) => [['  ', null], [t, null], ['  ', null], ['tell from swancloud-design', null]]),
  [['swancloud plan', 'bold'], ['  ', null], ['1 in flight', null]],
]

test("a role's run draws its turn and an ask that waits above its role's view, named from its place", async ($, on) => {
  const views = { ...VIEWS, views: { ...VIEWS.views, 'swancloud-planner': runView('1 ask waits, for 4m', ['ask 1', 'ask 2']) } }
  const ui = await band($, on, { env: { FLUME_PLACE: RUN }, views })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  const at = (pattern) => lines.findIndex((l) => pattern.test(l))
  expect(at(/^swancloud-planner run {2}in stream swancloud-main {2}turn 1 took 2 {2}1 ask waits, for 4m$/)).toBeGreaterThanOrEqual(0)
  expect(at(/^ {2}ask 1 {2}tell from swancloud-design$/)).toBeGreaterThan(at(/^swancloud-planner run/))
  expect(at(/^ {2}ask 2 {2}tell from swancloud-design$/)).toBeGreaterThan(at(/^ {2}ask 1/))
  expect(at(/^swancloud plan {2}1 in flight$/)).toBeGreaterThan(at(/^ {2}ask 2/))
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeUndefined()
})

test("a role's run with nothing waiting says so", async ($, on) => {
  const views = { ...VIEWS, views: { 'swancloud-planner': runView('nothing waits', ['ask 1']) } }
  const ui = await band($, on, { env: { FLUME_PLACE: RUN + '/' }, views })
  expect(await ui.find({ type: 'Text', text: /^swancloud-planner run {2}in stream swancloud-main {2}turn 1 took 1 {2}nothing waits$/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /^ {2}ask 1 {2}tell from swancloud-design$/ })).toBeDefined()
})

test("a place of another kind is no role's run and draws no band", async ($, on) => {
  const views = { ...VIEWS, views: { 'swancloud-planner': runView('nothing waits', ['ask 1']) } }
  const ui = await band($, on, { env: { FLUME_PLACE: '/home/chuck/.local/state/flume/places/change--a-unit' }, views })
  expect(await ui.find({ type: 'Text', text: /swancloud-planner run/ })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: /drawn by Claude Code/ })).toBeDefined()
})
