from __future__ import annotations

from collections import Counter
from collections.abc import Mapping


def validate_positive_int(value: int, field_name: str) -> None:
    """Valida que un valor sea un entero positivo."""
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field_name} tiene que ser un entero positivo")


def validate_non_negative_int(value: int, field_name: str) -> None:
    """Valida que un valor sea un entero no negativo."""
    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} tiene que ser un entero no negativo")


def validate_symbol(symbol: str, field_name: str = "symbol") -> None:
    """Valida un simbolo del alfabeto."""
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError(f"{field_name} tiene que ser una cadena no vacía")


def validate_identifier(value: str, field_name: str = "identifier") -> None:
    """Valida un identificador textual."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} tiene que ser una cadena no vacía")


def normalize_counter(
    values: Mapping[str, int] | Counter[str] | None,
    field_name: str = "multiset",
) -> Counter[str]:
    """Convierte y valida un multiconjunto."""
    counter: Counter[str] = Counter()
    if values is None:
        return counter

    for symbol, count in values.items():
        validate_symbol(symbol, f"{field_name} symbol")
        validate_positive_int(count, f"{field_name}[{symbol!r}]")
        counter[symbol] += count

    return +counter


def counter_contains(available: Counter[str], required: Counter[str]) -> bool:
    """Comprueba si un multiconjunto contiene a otro."""
    return all(available[symbol] >= count for symbol, count in required.items())
