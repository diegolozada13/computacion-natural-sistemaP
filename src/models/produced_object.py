from __future__ import annotations

from dataclasses import dataclass

from src.models._validation import validate_positive_int, validate_symbol


VALID_TARGETS = frozenset({"here", "out", "in_2", "in_3"})


@dataclass(frozen=True)
class ProducedObject:
    """Representa un objeto producido y su destino."""

    symbol: str
    count: int = 1
    target: str = "here"

    def __post_init__(self) -> None:
        """Valida el objeto producido."""
        validate_symbol(self.symbol)
        validate_positive_int(self.count, "count")
        if self.target not in VALID_TARGETS:
            raise ValueError(
                f"target must be one of {sorted(VALID_TARGETS)}, got {self.target!r}"
            )

    @property
    def is_local(self) -> bool:
        """Indica si el objeto permanece en la membrana actual."""
        return self.target == "here"

    @property
    def is_out(self) -> bool:
        """Indica si el objeto se envia a la membrana padre."""
        return self.target == "out"

    @property
    def target_membrane_id(self) -> int | None:
        """Obtiene el identificador del destino interno."""
        if not self.target.startswith("in_"):
            return None
        return int(self.target.removeprefix("in_"))
