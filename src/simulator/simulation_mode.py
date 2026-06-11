from __future__ import annotations

from enum import Enum


class SimulationMode(str, Enum):
    """Supported simulation execution modes."""

    SEQUENTIAL = "sequential"
    MAXIMAL_PARALLEL = "maximal_parallel"

    @classmethod
    def from_value(cls, value: str | SimulationMode) -> SimulationMode:
        if isinstance(value, cls):
            return value
        return cls(value)

