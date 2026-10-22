// crew's mod: each crew agent's view of its partition's board, drawn in the band above its prompt. The views are
// crew's (board.py agent_views): the console's rail tab writes them beside the board's frame each time it
// refreshes (crew _views), and this module finds its own agent's and draws it, deciding nothing itself (code.7). It
// starts no process and costs no tokens: every few seconds it looks at the file's time, and reads the file only when
// that has moved (state.4: a frame is one redraw, not state).
//
// A change to what crew models (bolts, units, stages, proposals, explorations and elaborations, cards, rail rows)
// changes this module and board.agent_views together, each with its cases: tests/py/test_board.py pins every key this
// reads from the views file, and plugin/tests/status.test.ts what it draws (code.8).

// How often the file's time is looked at; the rail tab writes it every 30 seconds and on each run-record entry.
const EVERY_MS = 5000

// Who this session is, where its partition's views are, and what was last read from them.
const live = { agent: undefined, label: undefined, path: undefined, mtime: undefined, frame: undefined, stale: false }

// The session's agent and partition: CREW_AGENT and CREW_LABEL, as crew-role starts every role, or, for a session
// herdr resumed bare without them, the record crew's SessionStart hook keeps of the session (hooks/session-start).
async function identity($, home) {
  const agent = await $.env.get('CREW_AGENT')
  if (agent) return { agent, label: await $.env.get('CREW_LABEL') }
  try {
    const record = await $.fs.read(home + '/.local/state/crew/sessions/' + (await $.session.id()))
    const kv = Object.fromEntries(record.split('\n').filter((l) => l.includes('=')).map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1)]))
    return { agent: kv.CREW_AGENT, label: kv.CREW_LABEL }
  } catch {
    return {}
  }
}

// Reads the views again once the file's time has moved, and has the band drawn again when they, or whether they are
// stale, changed.
async function look($) {
  let mtime = null
  try {
    mtime = (await $.fs.stat(live.path)).mtimeMs
  } catch {
    // no views written on this host yet
  }
  const moved = mtime !== live.mtime
  if (moved) {
    live.mtime = mtime
    try {
      live.frame = mtime === null ? undefined : JSON.parse(await $.fs.read(live.path))
    } catch {
      live.frame = undefined
    }
  }
  const stale = live.frame !== undefined && (await $.clock.now()) - Date.parse(live.frame.read_at) > live.frame.stale_after_ms
  if (moved || stale !== live.stale) {
    live.stale = stale
    $.ui.invalidate('ui.render')
  }
}

// The lines the band shows: the agent's open cards, its questions among them, then its view, with the stale line once
// the views are old; one line while no views are written on this host; nothing for an agent crew gives no view, or a
// session that is no crew agent.
function lines() {
  if (!live.path) return undefined
  if (!live.frame) {
    return [[['crew: no board for ' + live.label + ' on this host yet; its console writes it (crew console up ' + live.label + ')', 'dim']]]
  }
  const view = live.frame.views[live.agent]
  if (!view) return undefined
  const shown = [...((live.frame.cards || {})[live.agent] || []), ...view]
  return live.stale ? [...shown, live.frame.stale] : shown
}

export function register(on) {
  on('session.start', async ($, e, next) => {
    const home = await $.env.get('HOME')
    const { agent, label } = await identity($, home)
    if (agent && label && home) {
      Object.assign(live, { agent, label, path: home + '/.cache/crew/board/' + label + '.agents.json' })
      await look($)
      $.clock.every(EVERY_MS, () => look($))
    }
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const shown = lines()
    // a survey holds the band, and a session with nothing to show leaves it to the mods after this one
    if (!shown || e.props.hasSurvey) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const theirs = await next(e)
    const drawn = shown.map((segs) =>
      Text({
        wrap: 'truncate-end',
        children: segs.map(([text, style]) => (style ? Text({ ...(style === 'bold' ? { bold: true } : { dimColor: true }), children: [text] }) : text)),
      }),
    )
    return Box({ flexDirection: 'column', children: theirs ? [...drawn, theirs] : drawn })
  })
}
