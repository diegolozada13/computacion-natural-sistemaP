from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from src.models._validation import validate_positive_int, validate_symbol
from src.models.configuration import Configuration
from src.models.membrane import Membrane
from src.models.rule import Rule


STANDARD_MEMBRANE_IDS = {1, 2, 3}


@dataclass
class PSystem:
    """Representa un sistema P de transicion normalizado."""

    alphabet: set[str]
    membranes: dict[int, Membrane]
    rules: dict[int, list[Rule]] = field(default_factory=dict)
    output_membrane: int = 1
    seed: int | None = None

    def __post_init__(self) -> None:
        """Normaliza y valida la definicion del sistema."""
        self.alphabet = set(self.alphabet)
        self.membranes = dict(self.membranes)
        self.rules = {
            membrane_id: list(membrane_rules)
            for membrane_id, membrane_rules in self.rules.items()
        }
        for membrane_id in self.membranes:
            self.rules.setdefault(membrane_id, [])

        self.validate()

    @classmethod
    def create_standard(
        cls,
        alphabet: Iterable[str],
        initial_objects: Mapping[int, Mapping[str, int] | Counter[str]] | None = None,
        rules: Mapping[int, Iterable[Rule]] | None = None,
        output_membrane: int = 1,
        seed: int | None = None,
    ) -> PSystem:
        """Crea un sistema con la estructura fija de tres membranas."""
        initial_objects = initial_objects or {}

        membrane_1 = Membrane(1, objects=Counter(initial_objects.get(1, {})))
        membrane_2 = Membrane(2, objects=Counter(initial_objects.get(2, {})))
        membrane_3 = Membrane(3, objects=Counter(initial_objects.get(3, {})))
        membrane_1.add_child(membrane_2)
        membrane_2.add_child(membrane_3)

        return cls(
            alphabet=set(alphabet),
            membranes={1: membrane_1, 2: membrane_2, 3: membrane_3},
            rules={key: list(value) for key, value in (rules or {}).items()},
            output_membrane=output_membrane,
            seed=seed,
        )

    def validate(self) -> None:
        """Valida todas las invariantes del sistema."""
        self._validate_alphabet()
        self._validate_membrane_structure()
        self._validate_rules()

    def is_valid(self) -> bool:
        """Indica si la definicion del sistema es valida."""
        try:
            self.validate()
        except ValueError:
            return False
        return True

    def get_membrane(self, membrane_id: int) -> Membrane:
        """Obtiene una membrana por identificador."""
        try:
            return self.membranes[membrane_id]
        except KeyError as exc:
            raise KeyError(f"unknown membrane {membrane_id}") from exc

    def get_rules(self, membrane_id: int) -> list[Rule]:
        """Devuelve las reglas asociadas a una membrana."""
        self.get_membrane(membrane_id)
        return list(self.rules.get(membrane_id, []))

    def add_rule(self, rule: Rule) -> None:
        """Valida y añade una regla al sistema."""
        rule.validate_against(self.alphabet, self.membranes.keys())
        self._validate_rule_targets(rule)
        self.rules.setdefault(rule.membrane_id, []).append(rule)

    def all_rules(self) -> list[Rule]:
        """Devuelve todas las reglas en orden de membrana."""
        return [
            rule
            for membrane_id in sorted(self.rules)
            for rule in self.rules[membrane_id]
        ]

    def initial_configuration(self) -> Configuration:
        """Construye una copia de la configuracion inicial."""
        return Configuration(self.membranes, step=0).clone()

    def valid_targets_for(self, membrane_id: int) -> set[str]:
        """Calcula los destinos validos para una membrana."""
        membrane = self.get_membrane(membrane_id)
        targets = {"here"}
        if membrane.parent is not None:
            targets.add("out")
        targets.update(f"in_{child.id}" for child in membrane.children)
        return targets

    def target_membrane_id(self, source_membrane_id: int, target: str) -> int:
        """Resuelve un destino al identificador de membrana final."""
        source = self.get_membrane(source_membrane_id)
        if target == "here":
            return source.id
        if target == "out":
            if source.parent is None:
                raise ValueError(f"membrane {source.id} has no parent for target 'out'")
            return source.parent.id
        if target.startswith("in_"):
            target_id = int(target.removeprefix("in_"))
            if source.get_child(target_id) is None:
                raise ValueError(
                    f"membrane {target_id} is not a direct child of membrane {source.id}"
                )
            return target_id
        raise ValueError(f"unknown target {target!r}")

    def _validate_alphabet(self) -> None:
        """Valida los simbolos del alfabeto."""
        if not self.alphabet:
            raise ValueError("alphabet must contain at least one symbol")
        for symbol in self.alphabet:
            validate_symbol(symbol, "alphabet symbol")

    def _validate_membrane_structure(self) -> None:
        """Valida la estructura fija de tres membranas."""
        if set(self.membranes) != STANDARD_MEMBRANE_IDS:
            raise ValueError("a normalized P system must contain membranes 1, 2 and 3")

        for membrane_id, membrane in self.membranes.items():
            if membrane.id != membrane_id:
                raise ValueError(
                    f"membrane key {membrane_id} does not match membrane id {membrane.id}"
                )

        membrane_1 = self.membranes[1]
        membrane_2 = self.membranes[2]
        membrane_3 = self.membranes[3]

        if membrane_1.parent is not None:
            raise ValueError("membrane 1 must not have a parent")
        if membrane_2.parent is not membrane_1 or membrane_3.parent is not membrane_2:
            raise ValueError("membrane structure must be [1 [2 [3]3 ]2 ]1")
        if membrane_1.child_ids() != {2} or membrane_2.child_ids() != {3}:
            raise ValueError("membrane structure must be [1 [2 [3]3 ]2 ]1")
        if membrane_3.children:
            raise ValueError("membrane 3 must not have children")
        if self.output_membrane not in self.membranes:
            raise ValueError(f"unknown output membrane {self.output_membrane}")

        for membrane in self.membranes.values():
            unknown_symbols = set(membrane.objects) - self.alphabet
            if unknown_symbols:
                raise ValueError(
                    f"membrane {membrane.id} contains symbols outside the alphabet: "
                    f"{sorted(unknown_symbols)}"
                )

    def _validate_rules(self) -> None:
        """Valida las reglas y sus membranas asociadas."""
        unknown_rule_membranes = set(self.rules) - set(self.membranes)
        if unknown_rule_membranes:
            raise ValueError(
                f"rules reference unknown membranes: {sorted(unknown_rule_membranes)}"
            )

        for membrane_id, membrane_rules in self.rules.items():
            for rule in membrane_rules:
                if rule.membrane_id != membrane_id:
                    raise ValueError(
                        f"rule {rule.id!r} is stored under membrane {membrane_id} "
                        f"but references membrane {rule.membrane_id}"
                    )
                rule.validate_against(self.alphabet, self.membranes.keys())
                self._validate_rule_targets(rule)

    def _validate_rule_targets(self, rule: Rule) -> None:
        """Valida los destinos de comunicacion de una regla."""
        valid_targets = self.valid_targets_for(rule.membrane_id)
        invalid_targets = rule.targets - valid_targets
        if invalid_targets:
            raise ValueError(
                f"rule {rule.id!r} has invalid targets for membrane {rule.membrane_id}: "
                f"{sorted(invalid_targets)}"
            )
