// crew's mod (hooks/status.js) on the views the rail tab writes (board.py agent_views): that a crew agent's session
// finds its own view, by its environment or its session record, and draws it above its prompt, its open cards first,
// and only the stale line once the views are old. Each case fails when the mod draws the wrong view. What each view says is crew's logic tier
// (tests/py/test_board.py, code.8). tests/suite runs these as the task mod, through tests/mod.
import { expect, mock, test } from 'claude-code/testing'

const READ_AT = Date.parse('2026-10-12T14:00:00Z')
const VIEWS = {
  read_at: '2026-10-12T14:00:00Z',
  stale_after_ms: 90000,
  stale: [['  ', null], ['crew: the board was last read at 2026-10-12 14:00, too long ago to show; the rail tab on mac-studio has not refreshed it since', 'dim']],
  views: {
    'crw-1-conductor': [
      [['  ', null], ['crew', null], ['  ', null], ['◕◔', null], ['  ', null], ['curation-and-holds', null], ['  ', null], ['0 of 2 merged', null]],
      [['✎   ', null], ['◕', null], ['  ', null], ['a-queued-unit-can-take-a-signal', null], ['  ', null], ['verify 3/3', null]],
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

test('a conductor sees its view above its prompt', async ($, on) => {
  const ui = await band($, on, { env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' } })
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /verify 3\/3/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /has not refreshed/ })).toBeUndefined()
})

// wldn, 2026-10-20: swb-1's and awb-1's bands named bolts that had landed days before, drawn from views the rail tab
// had stopped refreshing, their stale line below the band's rows (signals 2026-10-20-wldn-operator-mac-studio-a4671eb9/01
// and b7a096b6/01 on wldn/main).
test('views older than the rail tab refreshes them name no bolt and no card, only when they were read', async ($, on) => {
  const card = [['  ', null], ['your question', null], ['  ', null], ['req_q1', 'dim'], ['  ', null], ['open 14m', null]]
  const ui = await band($, on, {
    env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' },
    views: { ...VIEWS, cards: { 'crw-1-conductor': [card] } },
    now: READ_AT + 120000,
  })
  expect(await ui.find({ type: 'Text', text: /crew: the board was last read at 2026-10-12 14:00, too long ago to show; the rail tab on mac-studio has not refreshed it since/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: /your question/ })).toBeUndefined()
})

test('a session herdr resumed bare finds its agent in its session record', async ($, on) => {
  const ui = await band($, on, { record: 'CREW_AGENT=crw-1-conductor\nCREW_LABEL=swancloud\nCREW_CWD=/work\n' })
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeDefined()
})

test("an agent's open cards are drawn above its view", async ($, on) => {
  const card = [['  ', null], ['your question', null], ['  ', null], ['req_q1', 'dim'], ['  ', null], ['open 14m', null]]
  const ui = await band($, on, { env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, cards: { 'crw-1-conductor': [card] } } })
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
    [['    ', null], ['◕', null], ['  ', null], ['a-queued-unit-can-take-a-signal', null], ['  ', null], ['verify 3/3', null], ['  ', null], ['#41 under test', null], ['  ', null], ['unit-1', null]],
  ]
  const ui = await band($, on, { env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' }, views: { ...VIEWS, views: { 'crw-1-conductor': ledger } } })
  const lines = (await ui.findAll({ type: 'Text' })).map((t) => t.text)
  expect(lines.findIndex((l) => /^ {2}crew {2}◕◔ {2}curation-and-holds {2}landing #355 queued {2}0 of 2 merged$/.test(l))).toBeGreaterThanOrEqual(0)
  expect(lines.findIndex((l) => /a-queued-unit-can-take-a-signal {2}verify 3\/3 {2}#41 under test {2}unit-1$/.test(l))).toBeGreaterThanOrEqual(0)
})
