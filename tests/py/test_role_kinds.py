"""The kinds crew's release carries for the main-level roles (role-runs; design Decisions 1 and 2): plugin/flume/kinds.toml
read as Flume reads a launch's own declaration, `flume launch --kinds <file>`, and plugin/flume/turn.md filled as Flume
fills a stage's prompt. Flume's format as read on 2026-10-31 at agentplot/flume 3a126d4: its guides/kinds.mdx and
reference/prompt-parts.md, crates/flume-core/src/prompt.rs `render`, and the kind fields weir-kinds names at the
revision Flume pins (0b6eb5a, crates/weir-kinds/src/kinds.rs and quiet.rs). One kind for each role a partition's
`flume` can name, each one stage, `turn`, that lands nothing and ends at its report in the place's own folder; and
nothing in the file a launch or an account gives instead: a model, instructions or an environment."""
import pathlib
import re
import tomllib

import pytest

import crew

FLUME = pathlib.Path(crew.__file__).resolve().parent.parent / "flume"
KINDS = FLUME / "kinds.toml"
DECLARED = tomllib.loads(KINDS.read_text())["kinds"]
TURN = (FLUME / "turn.md").read_text()

# The fields weir-kinds names for a kind and for a stage; Flume ignores every other key, so one misspelt is lost.
KIND_FIELDS = {"version", "branch", "starts_unready", "lands", "agents", "stages"}
STAGE_FIELDS = {"name", "prompt", "deliverables", "conversation", "agents", "makes", "wait", "quiet", "on_fail",
                "max_send_backs", "repeat"}
# Every prompt part Flume knows (flume-seams PromptPart), and those it fills for a stage of these kinds: a report
# deliverable fills {{report}}; the runner's launch gives no brief, the stage makes nothing and does not repeat, and
# the partition's blueprints repo need bind no change tool, so {{brief}}, {{made}}, {{group}}, {{notes}} and
# {{change}} would each refuse the stage and start no agent.
PARTS = {"brief", "name", "kind", "stage", "branch", "base", "place", "change", "report", "words", "unready", "needs",
         "made", "group", "notes"}
FILLED = {"name", "kind", "stage", "branch", "base", "place", "report", "unready", "needs"}
OPEN, CLOSE = "{{#words}}", "{{/words}}"


def render(template, words):
    """flume-core's prompt.rs `render`: the words section kept only with words, then each part Flume knows filled,
    raising KeyError for one it has nothing for; text in braces naming no part is left as written."""
    out, rest = "", template
    while OPEN in rest:
        before, after = rest.split(OPEN, 1)
        if CLOSE not in after:
            break
        inside, rest = after.split(CLOSE, 1)
        out += before + (inside if words else "")
    out += rest
    fill = {p: f"<{p}>" for p in FILLED} | ({"words": words} if words else {})
    return re.sub(r"\{\{(.*?)\}\}", lambda m: fill[m[1]] if m[1] in PARTS else m[0], out)


def quiet(text):
    """weir-kinds' quiet.rs: one whole number followed by one unit, s, m or h."""
    return re.fullmatch(r"[0-9]+[smh]", text) is not None


def keys(value):
    """Every key in a TOML value, however deep."""
    if isinstance(value, dict):
        return set(value) | {k for v in value.values() for k in keys(v)}
    if isinstance(value, list):
        return {k for v in value for k in keys(v)}
    return set()


def test_it_declares_one_kind_for_each_role_a_partition_can_run_as_its_kind():
    assert set(DECLARED) == {f"crew-{role}" for role in crew.KIND_ROLES}


@pytest.mark.parametrize("name", sorted(DECLARED))
class TestFlumesFormat:
    """Each kind as Flume reads it: refused for a field of the wrong type, a stage with no agent or several, or a
    deliverable it cannot read, and silent on a key it does not name."""

    def test_every_field_is_one_the_format_names(self, name):
        kind = DECLARED[name]
        assert set(kind) <= KIND_FIELDS
        assert all(set(stage) <= STAGE_FIELDS for stage in kind["stages"])

    def test_it_has_one_stage_with_one_agent_one_deliverable_and_a_quiet_time(self, name):
        [stage] = DECLARED[name]["stages"]
        assert isinstance(stage["name"], str) and stage["name"]
        assert isinstance(stage["agents"], list) and len(stage["agents"]) == 1 and isinstance(stage["agents"][0], dict)
        [deliverable] = stage["deliverables"]
        assert deliverable.startswith("report:") and deliverable != "report:"
        assert quiet(stage["quiet"])

    def test_its_prompt_is_a_file_beside_the_declaration(self, name):
        [stage] = DECLARED[name]["stages"]
        assert (KINDS.parent / stage["prompt"]).is_file()


@pytest.mark.parametrize("role", crew.KIND_ROLES)
def test_each_kind_is_one_turn_that_lands_nothing_and_ends_at_its_report_in_the_places_own_folder(role):
    """Decision 2: the report lies outside the worktree, so a turn commits nothing and its branch holds no commit;
    the quiet time is long, since a turn the user opened lasts as long as their conversation."""
    kind = DECLARED[f"crew-{role}"]
    assert kind["lands"] is False
    assert kind["branch"] == f"crew-{role}"
    assert kind["stages"] == [{"name": "turn", "prompt": "turn.md", "deliverables": ["report:{{state}}/turn.md"],
                               "quiet": "4h", "agents": [{}]}]


def test_nothing_names_a_model_instructions_or_an_environment():
    """The model comes with the launch from the role's definition, the brief from the run's start, and the
    environment from the pool's account; an `env` would refuse the launch."""
    assert not keys(DECLARED) & {"model", "instructions", "env"}


class TestThePrompt:
    """turn.md, the one prompt the five kinds share."""

    @pytest.mark.parametrize("words", [None, "The question: crew role start refused.\n\nThe answer: try again."])
    def test_flume_fills_every_part_it_asks_for_with_words_and_without(self, words):
        text = render(TURN, words)
        assert "{{" not in text and "}}" not in text
        assert (words in text) if words else ("started again" not in text)

    def test_its_words_section_is_closed_and_holds_the_only_words_part(self):
        outside = re.sub(re.escape(OPEN) + ".*?" + re.escape(CLOSE), "", TURN, flags=re.S)
        assert TURN.count(OPEN) == TURN.count(CLOSE) == 1
        assert "{{words}}" not in outside

    def test_it_asks_for_no_brief_since_the_brief_is_read_at_the_start(self):
        assert "{{brief}}" not in TURN

    def test_it_names_who_the_run_is(self):
        assert all(part in TURN for part in ("{{kind}}", "{{name}}", "{{place}}"))

    def test_the_turn_starts_with_crew_role_start_and_ends_with_crew_role_end_writing_its_report(self):
        start, end = TURN.index("`crew role start`"), TURN.index('`crew role end --report {{report}} "<what was done>"`')
        assert start < end

    def test_it_places_needs_in_the_sentence_that_asks_on_a_card_and_stops_short_only_on_a_refused_start(self):
        """Flume appends {{needs}} to a prompt that does not place it; placed here, it follows the sentence."""
        assert TURN.count("{{needs}}") == 1
        sentence = TURN[TURN.rindex("\n\n", 0, TURN.index("{{needs}}")):TURN.index("{{needs}}")]
        assert "ask on a card" in sentence and "Stop short only when `crew role start` refuses" in sentence
