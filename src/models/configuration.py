from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.models._validation import validate_non_negative_int, validate_positive_int
from src.models.membrane import Membrane


@dataclass
class Configuration:
    """Representa el estado completo del sistema en un paso."""

    membranes: dict[int, Membrane]
    step: int = 0

    def __post_init__(self) -> None:
        """Valida los datos de la configuracion."""
        validate_non_negative_int(self.step, "step")
        if not self.membranes:
            raise ValueError("configuration must contain at least one membrane")

        self.membranes = dict(self.membranes)
        for membrane_id, membrane in self.membranes.items():
            validate_positive_int(membrane_id, "membrane id")
            if membrane.id != membrane_id:
                raise ValueError(
                    f"membrane key {membrane_id} does not match membrane id {membrane.id}"
                )

    def get_membrane(self, membrane_id: int) -> Membrane:
        """Obtiene una membrana por su identificador."""
        try:
            return self.membranes[membrane_id]
        except KeyError as exc:
            raise KeyError(f"unknown membrane {membrane_id}") from exc

    def objects_in(self, membrane_id: int) -> Counter[str]:
        """Devuelve una copia de los objetos de una membrana."""
        return self.get_membrane(membrane_id).objects_copy()

    def to_dict(self) -> dict[int, dict[str, int]]:
        """Convierte la configuracion en un diccionario."""
        return {
            membrane_id: self.membranes[membrane_id].to_dict()
            for membrane_id in sorted(self.membranes)
        }

    def clone(self, step: int | None = None) -> Configuration:
        """Crea una copia independiente de la configuracion."""
        cloned_membranes = {
            membrane_id: Membrane(membrane_id, objects=membrane.objects_copy())
            for membrane_id, membrane in self.membranes.items()
        }

        for membrane_id, membrane in self.membranes.items():
            cloned = cloned_membranes[membrane_id]
            if membrane.parent is not None:
                cloned.parent = cloned_membranes[membrane.parent.id]
            cloned.children = [cloned_membranes[child.id] for child in membrane.children]

        return Configuration(
            membranes=cloned_membranes,
            step=self.step if step is None else step,
        )
