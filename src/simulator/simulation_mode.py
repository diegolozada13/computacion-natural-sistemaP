from __future__ import annotations

from enum import Enum


class SimulationMode(str, Enum):
    """Define los modos de ejecucion disponibles."""

    SEQUENTIAL = "sequential"
    MAXIMAL_PARALLEL = "maximal_parallel"

    @classmethod
    def from_value(cls, value: str | SimulationMode) -> SimulationMode:
        """Convierte un texto o enum en un modo de simulacion."""
        if isinstance(value, cls):
            return value
        return cls(value)
