from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.models import Configuration, PSystem, Rule
from src.models._validation import validate_non_negative_int
from src.simulator.simulation_mode import SimulationMode


@dataclass(frozen=True)
class ProducedMove:
    """Describe el movimiento de un objeto producido."""

    symbol: str
    count: int
    target: str
    target_membrane_id: int


@dataclass(frozen=True)
class AppliedRule:
    """Resume una aplicacion concreta de una regla."""

    rule_id: str
    membrane_id: int
    consumed: dict[str, int]
    produced: tuple[ProducedMove, ...]


@dataclass(frozen=True)
class StepResult:
    """Contiene el resultado de un paso de simulacion."""

    step: int
    applied_rules: tuple[AppliedRule, ...]
    halted: bool = False


class Simulator:
    """Ejecuta la evolucion de un sistema P."""

    def __init__(self, psystem: PSystem, mode: SimulationMode | str) -> None:
        """Inicializa el simulador y su historial."""
        self.psystem = psystem
        self.mode = SimulationMode.from_value(mode)
        self.current_configuration = psystem.initial_configuration()
        self.history: list[Configuration] = [self.current_configuration.clone()]

    def step(self) -> StepResult:
        """Ejecuta un paso segun el modo seleccionado."""
        if self.mode is SimulationMode.SEQUENTIAL:
            return self._step_sequential()
        if self.mode is SimulationMode.MAXIMAL_PARALLEL:
            return self._step_maximal_parallel()
        raise NotImplementedError(f"modo de simulación no compatible: {self.mode}")

    def _step_sequential(self) -> StepResult:
        """Ejecuta una unica regla aplicable."""
        selected_rule = self._find_first_applicable_rule()
        if selected_rule is None:
            return StepResult(
                step=self.current_configuration.step,
                applied_rules=(),
                halted=True,
            )

        next_configuration, applied_rules = self._apply_rule_applications([selected_rule])
        self.current_configuration = next_configuration
        self.history.append(next_configuration.clone())

        return StepResult(
            step=next_configuration.step,
            applied_rules=applied_rules,
            halted=False,
        )

    def _step_maximal_parallel(self) -> StepResult:
        """Ejecuta un conjunto maximal de reglas aplicables."""
        selected_rules = self._select_ordered_maximal_parallel_rules()
        if not selected_rules:
            return StepResult(
                step=self.current_configuration.step,
                applied_rules=(),
                halted=True,
            )

        next_configuration, applied_rules = self._apply_rule_applications(selected_rules)
        self.current_configuration = next_configuration
        self.history.append(next_configuration.clone())

        return StepResult(
            step=next_configuration.step,
            applied_rules=applied_rules,
            halted=False,
        )

    def run(self, max_steps: int) -> list[StepResult]:
        """Ejecuta pasos hasta parada o limite."""
        validate_non_negative_int(max_steps, "max_steps")

        results: list[StepResult] = []
        for _ in range(max_steps):
            if self.is_halted():
                break
            results.append(self.step())
        return results

    def is_halted(self) -> bool:
        """Indica si no queda ninguna regla aplicable."""
        return self._find_first_applicable_rule() is None

    def get_history(self) -> list[Configuration]:
        """Devuelve copias del historial de configuraciones."""
        return [configuration.clone() for configuration in self.history]

    def _find_first_applicable_rule(self) -> Rule | None:
        """Busca la primera regla aplicable en orden estable."""
        for membrane_id in sorted(self.psystem.membranes):
            membrane = self.current_configuration.get_membrane(membrane_id)
            for rule in self.psystem.get_rules(membrane_id):
                if rule.is_applicable(membrane.objects):
                    return rule
        return None

    def _select_ordered_maximal_parallel_rules(self) -> list[Rule]:
        """Selecciona reglas maximales reservando objetos."""
        selected_rules: list[Rule] = []

        for membrane_id in sorted(self.psystem.membranes):
            available_objects = self.current_configuration.objects_in(membrane_id)
            membrane_rules = self.psystem.get_rules(membrane_id)

            while True:
                selected_rule = self._find_first_applicable_in_rules(
                    membrane_rules,
                    available_objects,
                )
                if selected_rule is None:
                    break

                selected_rules.append(selected_rule)
                available_objects.subtract(selected_rule.consumed_objects())
                available_objects = +available_objects

        return selected_rules

    def _find_first_applicable_in_rules(
        self,
        rules: list[Rule],
        available_objects: Counter[str],
    ) -> Rule | None:
        """Busca la primera regla aplicable en una lista."""
        for rule in rules:
            if rule.is_applicable(available_objects):
                return rule
        return None

    def _apply_rule_applications(
        self,
        rules: list[Rule],
    ) -> tuple[Configuration, tuple[AppliedRule, ...]]:
        """Aplica simultaneamente las reglas seleccionadas."""
        next_configuration = self.current_configuration.clone(
            step=self.current_configuration.step + 1
        )
        applied_rules = tuple(self._build_applied_rule(rule) for rule in rules)

        for rule in rules:
            source_membrane = next_configuration.get_membrane(rule.membrane_id)
            source_membrane.remove_objects(rule.consumed_objects())

        for applied_rule in applied_rules:
            for produced_move in applied_rule.produced:
                target_membrane = next_configuration.get_membrane(
                    produced_move.target_membrane_id
                )
                target_membrane.add_object(produced_move.symbol, produced_move.count)

        return next_configuration, applied_rules

    def _build_applied_rule(self, rule: Rule) -> AppliedRule:
        """Construye el resumen de una regla aplicada."""
        produced_moves: list[ProducedMove] = []
        for produced_object in rule.rhs:
            target_membrane_id = self.psystem.target_membrane_id(
                rule.membrane_id,
                produced_object.target,
            )
            produced_moves.append(
                ProducedMove(
                    symbol=produced_object.symbol,
                    count=produced_object.count,
                    target=produced_object.target,
                    target_membrane_id=target_membrane_id,
                )
            )

        return AppliedRule(
            rule_id=rule.id,
            membrane_id=rule.membrane_id,
            consumed=dict(sorted(rule.consumed_objects().items())),
            produced=tuple(produced_moves),
        )
