# Tasks

## 1. Landing a capture

- [ ] 1.1 `crew signal land <capture-dir> [--label L]` in `plan.py`: the five checks of design.md, each failure naming the file and writing nothing. Verify with fixture directories: a good read capture, a good unread stub, a capture whose name differs from its directory, a signal with a wrong id, an unknown kind, a missing excerpt in a read capture, an oversized signal file, a stray `.txt`, a wrong count, and a name that exists in the state.
- [ ] 1.2 The write: one `land` on the first blueprints repo's main by the capture's paths; a signal absent is added, identical is skipped, different is refused; `capture.md` is replaced only from `unread` and only in `status`, `signals` and `imported`; nothing to do makes no commit and says "already landed". Verify against the blueprints test remote: a first landing is one commit of exactly those paths; a second writes nothing; an edited signal is refused; an unread stub followed by its read capture lands the signals and replaces `capture.md`; a push raced by another write is applied again and lands.
- [ ] 1.3 Entries: `capture` for the capture when first landed and for each signal added, with the commit and the caller (`CREW_AGENT` when set). Verify `crew trace signals/<id>` for a landed signal that was then moved begins with its capture.
- [ ] 1.4 Document `crew signal land` in `README.md` ("Signals": the two homes and how each is written), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 2. Outside crew

- [ ] 2.1 A decision for the user, before this change is built: meeting signals stay in the blueprints' `signals/`, as this change assumes, or follow an agent's signals to the flywheel's state. If the second, `crew signal land` writes to the flywheel's branch and tasks 1.2 and 2.2 to 2.4 name that target; the checks and entries are unchanged.
- [ ] 2.2 willdan-blueprints, as one reviewed commit: `.gitignore` gains `signals/.work/`; `.claude/skills/signal-capture/SKILL.md` writes each capture under `signals/.work/<capture>/` and no longer commits; `signals/bin/sweep` pulls, runs the sweep phase, lands each stub, runs the read phase, lands each read capture, pulls, and removes landed directories, exporting `CREW_AGENT=signal-sweep` and `CREW_LABEL=wldn`, logging a refused landing and carrying on; `signals/README.md` says signals are landed through crew and that the heartbeat is crew's `signals(<capture>): land …` commits. Verify by running the script by hand on a day with a new meeting: the checkout is clean afterwards and main holds the capture.
- [ ] 2.3 The Mac that runs the launchd job (`com.willdan.signal-sweep.plist`): `crew` on the job's `PATH`, and GitHub credentials that reach willdan-blueprints over https, as crew's other writes use. If swancloud manages that job's environment, the change is there. Verify `crew signal land` succeeds when run from the job's own environment (`launchctl kickstart` the job once).
- [ ] 2.4 Any other blueprints repo that runs a daily pass gets the same commit. Today none does; verify by checking afterthought/blueprints and agentplot/blueprints for a `signals/bin/sweep`.

## 3. Proof on real work

- [ ] 3.1 Let the next morning's daily pass run on its own. Verify willdan-blueprints' main gained `signals(<capture>): land …` commits and no `signals(sweep)` or `signals(read)` commit; the checkout on that Mac is clean; `/tmp/signal-sweep.log` shows each landing; and `crew events --label wldn --since today` shows a `capture` entry for the capture and for each signal, by `signal-sweep`.
- [ ] 3.2 Curate that capture (`crew curate wldn --only <capture>`). Verify `crew trace` of one of its signals shows the landing, then the move, then what the move led to.
