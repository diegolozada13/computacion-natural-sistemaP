from __future__ import annotations

from collections import Counter
import unittest

from src.models import ProducedObject, PSystem, Rule
from src.simulator import SimulationMode, Simulator


class MaximalParallelSimulatorTest(unittest.TestCase):
    def test_applies_same_rule_multiple_times(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b"},
            initial_objects={2: {"a": 3}},
            rules={
                2: [
                    Rule(
                        "r1",
                        2,
                        Counter({"a": 1}),
                        [ProducedObject("b")],
                    )
                ]
            },
        )
        simulator = Simulator(psystem, SimulationMode.MAXIMAL_PARALLEL)

        result = simulator.step()

        self.assertEqual(len(result.applied_rules), 3)
        self.assertEqual([rule.rule_id for rule in result.applied_rules], ["r1", "r1", "r1"])
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"b": 3}))

    def test_applies_cooperative_rule_and_keeps_set_non_extensible(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b", "c", "d"},
            initial_objects={2: {"a": 2, "b": 1}},
            rules={
                2: [
                    Rule("cooperative", 2, Counter({"a": 1, "b": 1}), [ProducedObject("c")]),
                    Rule("remaining", 2, Counter({"a": 1}), [ProducedObject("d")]),
                ]
            },
        )
        simulator = Simulator(psystem, SimulationMode.MAXIMAL_PARALLEL)

        result = simulator.step()

        self.assertEqual([rule.rule_id for rule in result.applied_rules], ["cooperative", "remaining"])
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"c": 1, "d": 1}))

    def test_resolves_object_conflict_by_deterministic_rule_order(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b", "c"},
            initial_objects={2: {"a": 1}},
            rules={
                2: [
                    Rule("first", 2, Counter({"a": 1}), [ProducedObject("b")]),
                    Rule("second", 2, Counter({"a": 1}), [ProducedObject("c")]),
                ]
            },
        )
        simulator = Simulator(psystem, SimulationMode.MAXIMAL_PARALLEL)

        result = simulator.step()

        self.assertEqual(len(result.applied_rules), 1)
        self.assertEqual(result.applied_rules[0].rule_id, "first")
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"b": 1}))

    def test_communicates_between_membranes_with_deferred_production(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b", "c", "d", "e"},
            initial_objects={2: {"a": 1}, 3: {"c": 1}},
            rules={
                2: [
                    Rule(
                        "send_in",
                        2,
                        Counter({"a": 1}),
                        [ProducedObject("b", target="in_3")],
                    )
                ],
                3: [
                    Rule("would_use_b", 3, Counter({"b": 1}), [ProducedObject("e")]),
                    Rule(
                        "send_out",
                        3,
                        Counter({"c": 1}),
                        [ProducedObject("d", target="out")],
                    ),
                ],
            },
        )
        simulator = Simulator(psystem, SimulationMode.MAXIMAL_PARALLEL)

        result = simulator.step()

        self.assertEqual([rule.rule_id for rule in result.applied_rules], ["send_in", "send_out"])
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"d": 1}))
        self.assertEqual(simulator.current_configuration.objects_in(3), Counter({"b": 1}))


if __name__ == "__main__":
    unittest.main()
