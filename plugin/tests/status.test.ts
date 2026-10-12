// crew's mod (hooks/status.js) on the views the rail tab writes (board.py agent_views): what each session draws above
// its prompt. What each view says is crew's logic tier (tests/py/test_board.py); this checks only that the mod finds
// its agent's view and draws it. Run by hand: claude plugin test plugin
import { expect, mock, test } from 'claude-code/testing'

const READ_AT = Date.parse('2026-10-12T14:00:00Z')
const VIEWS = {
  read_at: '2026-10-12T14:00:00Z',
  stale_after_ms: 90000,
  stale: [['  ', null], ['read at 14:00; the rail tab on mac-studio has not refreshed it since', 'dim']],
  views: {
    'crw-1-conductor': [
      [['  ', null], ['◕◔', null], ['  ', null], ['crew', 'dim'], [' ', null], ['curation-and-holds', null], ['  ', null], ['0 of 2 merged', null]],
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

test('views older than the rail tab refreshes them say when they were read', async ($, on) => {
  const ui = await band($, on, { env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' }, now: READ_AT + 120000 })
  expect(await ui.find({ type: 'Text', text: /read at 14:00; the rail tab on mac-studio has not refreshed it since/ })).toBeDefined()
})

test('a session herdr resumed bare finds its agent in its session record', async ($, on) => {
  const ui = await band($, on, { record: 'CREW_AGENT=crw-1-conductor\nCREW_LABEL=swancloud\nCREW_CWD=/work\n' })
  expect(await ui.find({ type: 'Text', text: /curation-and-holds/ })).toBeDefined()
})

test('with no views written on the host, one line says what writes them', async ($, on) => {
  const ui = await band($, on, { env: { CREW_AGENT: 'crw-1-conductor', CREW_LABEL: 'swancloud' }, views: null })
  expect(await ui.find({ type: 'Text', text: /no board for swancloud on this host yet.*crew operator up swancloud/ })).toBeDefined()
})

test('an agent crew gives no view draws nothing of crew\'s', async ($, on) => {
  const unit = await band($, on, { env: { CREW_AGENT: 'crw-1-unit-1', CREW_LABEL: 'swancloud' } })
  expect(await unit.find({ type: 'Text', text: /curation-and-holds/ })).toBeUndefined()
  expect(await unit.find({ type: 'Text', text: 'drawn by Claude Code' })).toBeDefined()
})

test('a session that is no crew agent draws nothing of crew\'s', async ($, on) => {
  const ui = await band($, on)
  expect(await ui.find({ type: 'Text', text: /crew/ })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'drawn by Claude Code' })).toBeDefined()
})
