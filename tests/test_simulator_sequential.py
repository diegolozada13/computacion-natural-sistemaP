from __future__ import annotations

from collections import Counter
import unittest

from src.models import ProducedObject, PSystem, Rule
from src.simulator import SimulationMode, Simulator


class SequentialSimulatorTest(unittest.TestCase):
    def test_step_applies_first_applicable_rule_once(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b"},
            initial_objects={2: {"a": 2}},
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
        simulator = Simulator(psystem, SimulationMode.SEQUENTIAL)

        result = simulator.step()

        self.assertEqual(result.step, 1)
        self.assertFalse(result.halted)
        self.assertEqual(result.applied_rules[0].rule_id, "r1")
        self.assertEqual(result.applied_rules[0].consumed, {"a": 1})
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"a": 1, "b": 1}))
        self.assertEqual(len(simulator.get_history()), 2)

    def test_production_is_deferred_until_next_step(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b", "c"},
            initial_objects={2: {"a": 1}},
            rules={
                2: [
                    Rule("r1", 2, Counter({"a": 1}), [ProducedObject("b")]),
                    Rule("r2", 2, Counter({"b": 1}), [ProducedObject("c")]),
                ]
            },
        )
        simulator = Simulator(psystem, SimulationMode.SEQUENTIAL)

        first_result = simulator.step()

        self.assertEqual(first_result.applied_rules[0].rule_id, "r1")
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"b": 1}))

        second_result = simulator.step()

        self.assertEqual(second_result.applied_rules[0].rule_id, "r2")
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"c": 1}))

    def test_respects_here_out_and_in_targets(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b", "c", "d"},
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
                    Rule(
                        "send_out",
                        3,
                        Counter({"c": 1}),
                        [ProducedObject("d", target="out")],
                    )
                ],
            },
        )
        simulator = Simulator(psystem, SimulationMode.SEQUENTIAL)

        first_result = simulator.step()
        second_result = simulator.step()

        self.assertEqual(first_result.applied_rules[0].produced[0].target_membrane_id, 3)
        self.assertEqual(second_result.applied_rules[0].produced[0].target_membrane_id, 2)
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"d": 1}))
        self.assertEqual(simulator.current_configuration.objects_in(3), Counter({"b": 1}))

    def test_run_stops_when_halted(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a", "b"},
            initial_objects={2: {"a": 1}},
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
        simulator = Simulator(psystem, SimulationMode.SEQUENTIAL)

        results = simulator.run(max_steps=10)

        self.assertEqual(len(results), 1)
        self.assertTrue(simulator.is_halted())
        self.assertEqual(simulator.current_configuration.objects_in(2), Counter({"b": 1}))

    def test_step_reports_halted_without_changing_history(self) -> None:
        psystem = PSystem.create_standard(
            alphabet={"a"},
            initial_objects={2: {"a": 1}},
            rules={},
        )
        simulator = Simulator(psystem, SimulationMode.SEQUENTIAL)

        result = simulator.step()

        self.assertTrue(result.halted)
        self.assertEqual(result.applied_rules, ())
        self.assertEqual(result.step, 0)
        self.assertEqual(len(simulator.get_history()), 1)


if __name__ == "__main__":
    unittest.main()

