from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from src.models._validation import (
    counter_contains,
    normalize_counter,
    validate_identifier,
    validate_positive_int,
)
from src.models.produced_object import ProducedObject


@dataclass
class Rule:
    """Evolution or communication rule associated with one membrane."""

    id: str
    membrane_id: int
    lhs: Counter[str] = field(default_factory=Counter)
    rhs: list[ProducedObject] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "rule id")
        validate_positive_int(self.membrane_id, "membrane id")
        self.lhs = normalize_counter(self.lhs, "lhs")
        if not self.lhs:
            raise ValueError("lhs must contain at least one object")

        self.rhs = list(self.rhs)
        if not self.rhs:
            raise ValueError("rhs must contain at least one produced object")
        if not all(isinstance(produced, ProducedObject) for produced in self.rhs):
            raise ValueError("rhs must contain only ProducedObject instances")

    @property
    def is_cooperative(self) -> bool:
        return sum(self.lhs.values()) > 1

    @property
    def targets(self) -> set[str]:
        return {produced.target for produced in self.rhs}

    def is_applicable(self, objects: Mapping[str, int] | Counter[str]) -> bool:
        available = normalize_counter(objects, "objects")
        return counter_contains(available, self.lhs)

    def consumed_objects(self) -> Counter[str]:
        return Counter(self.lhs)

    def produced_objects(self, target: str | None = None) -> Counter[str]:
        produced_objects: Counter[str] = Counter()
        for produced in self.rhs:
            if target is None or produced.target == target:
                produced_objects[produced.symbol] += produced.count
        return produced_objects

    def validate_against(
        self,
        alphabet: set[str] | None = None,
        membrane_ids: Iterable[int] | None = None,
    ) -> None:
        if membrane_ids is not None and self.membrane_id not in set(membrane_ids):
            raise ValueError(f"rule {self.id!r} references unknown membrane {self.membrane_id}")

        if alphabet is None:
            return

        unknown_symbols = set(self.lhs) | {produced.symbol for produced in self.rhs}
        unknown_symbols -= alphabet
        if unknown_symbols:
            raise ValueError(
                f"rule {self.id!r} uses symbols outside the alphabet: {sorted(unknown_symbols)}"
            )
