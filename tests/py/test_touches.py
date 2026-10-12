"""A unit's Touches (teams.12): gather.touches reads the list from its proposal, plan.declared refuses code without
one, plan.matches and plan.overlaps compare entries, plan.overlapping words what a unit's code is told of the units
ahead of it, and plan.not_declared what its verify is told it changed and did not declare. That git's first-parent log
leaves a sibling's merged work out is a contract case (tests/contract/test_git.py)."""
import pytest

import gather
import plan
from facts import plan_of


def proposal(*touches, fence="```"):
    return "# Proposal\n\n## Why\n\nx\n\n## Touches\n\n" + fence + "\n" + "".join(t + "\n" for t in touches) + fence + "\n"


class TestRead:
    def test_the_fenced_block_under_the_heading_is_the_list(self):
        assert gather.touches(proposal("plugin/lib/plan.py", "tests/**")) == {"entries": ["plugin/lib/plan.py", "tests/**"]}

    @pytest.mark.parametrize("text, missing", [
        ("# Proposal\n\n## Why\n\nx\n", "its proposal.md has no `## Touches` heading"),
        ("# Proposal\n\n## Touches\n\nplugin/lib/plan.py\n\n## Other\n\n```\nx\n```\n", "its `## Touches` heading holds no fenced block"),
        ("# Proposal\n\n## Touches\n\n```\n\n```\n", "the block under its `## Touches` heading is empty"),
        (None, "it has no proposal.md")])
    def test_what_is_missing_is_said(self, text, missing):
        assert gather.touches(text) == {"missing": missing}

    def test_code_is_refused_saying_what_the_change_must_declare(self):
        k = {"places": {"c": {"touches": gather.touches("# Proposal\n")}}}
        with pytest.raises(plan.Refusal) as e:
            plan.declared(k, "c", "code")
        assert str(e.value) == ("unit c's code is refused: its change must declare what it touches, and its proposal.md has no "
                                "`## Touches` heading; construct ends proposal.md with `## Touches` and a fenced list of paths or globs")


class TestMatch:
    @pytest.mark.parametrize("entry, path, hit", [
        ("plugin/lib/plan.py", "plugin/lib/plan.py", True), ("plugin/lib", "plugin/lib/plan.py", True),
        ("./docs/", "docs/a.md", True), ("plugin/lib", "plugin/library.py", False),
        ("tests/*.sh", "tests/t-x.sh", True), ("tests/*.sh", "tests/sub/t-x.sh", False),
        ("tests/**", "tests/sub/t-x.sh", True), ("docs/?.md", "docs/a.md", True), ("docs/?.md", "docs/ab.md", False)])
    def test_an_entry_matches_a_path(self, entry, path, hit):
        assert plan.matches(entry, path) is hit

    @pytest.mark.parametrize("a, b, hit", [
        ("plugin/lib/plan.py", "plugin/lib/plan.py", True), ("docs/**", "docs/a.md", True), ("docs/**", "docs/*.md", True),
        ("src/a/**", "src/b/**", False), ("tests/**", "plugin/lib/plan.py", False)])
    def test_two_entries_overlap(self, a, b, hit):
        assert plan.overlaps(a, b) is hit


class Stages:
    def __init__(self, **stages):
        self.stages = stages

    def of(self, name):
        return {"stage": self.stages.get(name, "code")}


class TestOverlapping:
    PLAN = plan_of({"t": "swb-1"}, {"a": "t", "b": "t", "c": "t"})
    K = {"places": {"a": {"path": "/kit/places/a", "touches": {"entries": ["plugin/lib/plan.py", "docs/a.md"]}},
                    "b": {"path": "/kit/places/b", "touches": {"entries": ["plugin/lib/plan.py", "tests/**"]}},
                    "c": {"path": "/kit/places/c", "touches": {"entries": ["docs/**"]}}}}

    def test_the_first_unit_overlaps_nothing(self):
        assert plan.overlapping(self.PLAN, Stages(), self.K, "a", ["plugin/lib/plan.py", "docs/a.md"]) == []

    def test_a_later_unit_is_told_each_entry_it_overlaps_and_the_other_units_change(self):
        assert plan.overlapping(self.PLAN, Stages(), self.K, "b", ["plugin/lib/plan.py", "tests/**"]) == [
            "Its Touches overlap those of a, ahead of it in the bolt and not merged, on plugin/lib/plan.py; a's change is "
            "/kit/places/a/openspec/changes/a/."]
        assert plan.overlapping(self.PLAN, Stages(), self.K, "c", ["docs/**"]) == [
            "Its Touches overlap those of a, ahead of it in the bolt and not merged, on docs/** against docs/a.md; a's change "
            "is /kit/places/a/openspec/changes/a/."]

    def test_a_unit_ahead_that_has_merged_is_not_named(self):
        assert plan.overlapping(self.PLAN, Stages(a="merged"), self.K, "b", ["plugin/lib/plan.py"]) == []


class TestNotDeclared:
    CHANGED = ["README.md", "docs/b.md", "openspec/changes/b/tasks.md", "plugin/lib/plan.py", "tests/t-x.sh"]

    def test_names_each_path_its_commits_changed_that_no_entry_matches_its_change_aside(self):
        assert plan.not_declared(self.CHANGED, set(self.CHANGED), "b", ["plugin/lib/plan.py", "tests/**"]) == ["README.md", "docs/b.md"]

    def test_a_path_only_a_siblings_work_changed_is_not_its(self):
        assert plan.not_declared(self.CHANGED, {"README.md"}, "b", ["tests/**"]) == ["README.md"]
