from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field

from src.models._validation import (
    counter_contains,
    normalize_counter,
    validate_positive_int,
    validate_symbol,
)


@dataclass
class Membrane:
    """Representa una region delimitada por una membrana."""

    id: int
    parent: Membrane | None = field(default=None, repr=False, compare=False)
    children: list[Membrane] = field(default_factory=list, repr=False, compare=False)
    objects: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        """Valida y normaliza la membrana."""
        validate_positive_int(self.id, "membrane id")
        self.objects = normalize_counter(self.objects, "objects")
        children = list(self.children)
        self.children = []
        for child in children:
            self.add_child(child)

    def add_child(self, child: Membrane) -> None:
        """Añade una membrana hija."""
        if child is self:
            raise ValueError("a membrane cannot be its own child")
        if self.has_child(child.id):
            return
        if child.parent is not None and child.parent is not self:
            raise ValueError(f"membrane {child.id} already has a parent")

        child.parent = self
        self.children.append(child)

    def has_child(self, membrane_id: int) -> bool:
        """Comprueba si existe una hija con el identificador dado."""
        return any(child.id == membrane_id for child in self.children)

    def get_child(self, membrane_id: int) -> Membrane | None:
        """Obtiene una membrana hija por identificador."""
        return next((child for child in self.children if child.id == membrane_id), None)

    def child_ids(self) -> set[int]:
        """Devuelve los identificadores de las membranas hijas."""
        return {child.id for child in self.children}

    def add_object(self, symbol: str, count: int = 1) -> None:
        """Añade objetos al multiconjunto de la membrana."""
        validate_symbol(symbol)
        validate_positive_int(count, "count")
        self.objects[symbol] += count

    def add_objects(self, objects: Mapping[str, int] | Counter[str]) -> None:
        """Añade un multiconjunto de objetos."""
        self.objects.update(normalize_counter(objects, "objects"))

    def remove_object(self, symbol: str, count: int = 1) -> None:
        """Elimina objetos si hay multiplicidad suficiente."""
        validate_symbol(symbol)
        validate_positive_int(count, "count")
        if self.objects[symbol] < count:
            raise ValueError(
                f"membrane {self.id} has {self.objects[symbol]} occurrences of {symbol!r}"
            )

        self.objects[symbol] -= count
        if self.objects[symbol] == 0:
            del self.objects[symbol]

    def remove_objects(self, objects: Mapping[str, int] | Counter[str]) -> None:
        """Elimina un multiconjunto de objetos."""
        normalized = normalize_counter(objects, "objects")
        if not self.contains(normalized):
            raise ValueError(f"membrane {self.id} does not contain the required objects")

        self.objects.subtract(normalized)
        self.objects = +self.objects

    def multiplicity(self, symbol: str) -> int:
        """Consulta la multiplicidad de un simbolo."""
        validate_symbol(symbol)
        return self.objects[symbol]

    def contains(self, objects: Mapping[str, int] | Counter[str]) -> bool:
        """Comprueba la disponibilidad de un multiconjunto."""
        normalized = normalize_counter(objects, "objects")
        return counter_contains(self.objects, normalized)

    def objects_copy(self) -> Counter[str]:
        """Devuelve una copia del multiconjunto de objetos."""
        return Counter(self.objects)

    def to_dict(self) -> dict[str, int]:
        """Convierte los objetos en un diccionario ordenado."""
        return dict(sorted(self.objects.items()))
