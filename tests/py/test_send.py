"""crew send (briefs.10, record 0035, the operator-agent spec "Anything sent to another team or partition reaches its
operator", the run-record spec "A send is one entry in the receiving partition's record"): crew.send_door for where a
send goes, from the teams file alone, and crew.send for what it types and records. That the command reaches the
operator's pane on its host is the main level's journey's (t-journey-main)."""
import pytest

import crew
import facts
import record

FLEET = {**facts.FLEET, "partitions": {**facts.FLEET["partitions"],
                                       "swancloud": {"label": "swancloud", "machine": "mac-studio"}},
         "teams": {**facts.FLEET["teams"], "crw-5": {"name": "crw-5", "label": "swancloud", "machine": "mac-studio"}}}


class TestDoor:
    """A team or a partition's label resolves to its partition's operator; nothing else is placed."""

    def test_a_team_goes_to_its_partitions_operator(self):
        assert crew.send_door(FLEET, "swb-1", "crw-5-unit-1") == ("wldn", "wldn-operator", "swb-1")

    def test_a_partition_goes_to_its_operator_by_its_label(self):
        assert crew.send_door(FLEET, "wldn", "user@mac-studio") == ("wldn", "wldn-operator", None)

    def test_a_team_of_the_senders_own_partition_goes_through_its_operator_too(self):
        assert crew.send_door(FLEET, "swb-2", "swb-1-conductor") == ("wldn", "wldn-operator", "swb-2")

    def test_an_agents_name_is_refused_naming_the_teams_and_partitions(self):
        with pytest.raises(crew.Refusal, match=r"crew send takes a team or a partition, not 'swb-1-conductor': "
                                               r"teams crw-5 swb-1 swb-2; partitions swancloud wldn"):
            crew.send_door(FLEET, "swb-1-conductor", "crw-5-unit-1")

    def test_an_unknown_name_is_refused(self):
        with pytest.raises(crew.Refusal, match="not 'nosuch'"):
            crew.send_door(FLEET, "nosuch", None)

    def test_the_door_sending_to_its_own_team_is_refused(self):
        with pytest.raises(crew.Refusal, match=r"you are wldn's door: carry it on with `crew tell <agent>`"):
            crew.send_door(FLEET, "swb-1", "wldn-operator")

    def test_the_door_sending_to_its_own_label_is_refused(self):
        with pytest.raises(crew.Refusal, match="you are wldn's door"):
            crew.send_door(FLEET, "wldn", "wldn-operator")

    def test_another_partitions_operator_may_send(self):
        assert crew.send_door(FLEET, "wldn", "swancloud-operator") == ("wldn", "wldn-operator", None)
