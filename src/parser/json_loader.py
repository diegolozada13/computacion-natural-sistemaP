from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.models import ProducedObject, PSystem, Rule


class JsonLoaderError(ValueError):
    """Indica que una definicion JSON no es valida."""


class JsonLoader:
    """Construye sistemas P desde documentos JSON."""

    REQUIRED_MEMBRANES = {"1", "2", "3"}

    def load(self, path: str | Path) -> PSystem:
        """Carga un sistema P desde un fichero JSON."""
        json_path = Path(path)
        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise JsonLoaderError(
                f"JSON no válido en {json_path}, línea {exc.lineno}, "
                f"columna {exc.colno}"
            ) from exc
        except OSError as exc:
            raise JsonLoaderError(
                f"no se puede leer el fichero JSON {json_path}; "
                "comprueba que exista y que tenga permisos de lectura"
            ) from exc

        return self.load_data(data)

    def load_data(self, data: Mapping[str, Any]) -> PSystem:
        """Construye un sistema P desde datos ya decodificados."""
        document = self._expect_mapping(data, "raíz")

        alphabet = self._parse_alphabet(self._required(document, "alphabet", "raíz"))
        initial_objects = self._parse_membranes(
            self._required(document, "membranes", "raíz")
        )
        rules = self._parse_rules(self._required(document, "rules", "raíz"))
        output_membrane = self._parse_optional_int(document, "output_membrane", 1)
        seed = self._parse_optional_int(document, "seed", None)

        try:
            return PSystem.create_standard(
                alphabet=alphabet,
                initial_objects=initial_objects,
                rules=rules,
                output_membrane=output_membrane,
                seed=seed,
            )
        except ValueError as exc:
            raise JsonLoaderError(str(exc)) from exc

    def _parse_alphabet(self, value: Any) -> set[str]:
        """Valida y convierte el alfabeto."""
        if not isinstance(value, list):
            raise JsonLoaderError("alphabet debe ser una lista de cadenas")
        if not value:
            raise JsonLoaderError("alphabet debe contener al menos un símbolo")

        alphabet: set[str] = set()
        for index, symbol in enumerate(value):
            if not isinstance(symbol, str) or not symbol.strip():
                raise JsonLoaderError(
                    f"alphabet[{index}] debe ser una cadena no vacía"
                )
            if symbol in alphabet:
                raise JsonLoaderError(
                    f"símbolo duplicado en alphabet: {symbol!r}"
                )
            alphabet.add(symbol)
        return alphabet

    def _parse_membranes(self, value: Any) -> dict[int, Counter[str]]:
        """Extrae los multiconjuntos iniciales de las membranas."""
        membranes = self._expect_mapping(value, "membranes")
        if set(membranes) != self.REQUIRED_MEMBRANES:
            raise JsonLoaderError(
                "membranes debe contener exactamente las claves '1', '2' y '3'"
            )

        initial_objects: dict[int, Counter[str]] = {}
        for membrane_key in sorted(membranes, key=int):
            membrane_data = self._expect_mapping(
                membranes[membrane_key], f"membranes[{membrane_key!r}]"
            )
            objects = self._required(
                membrane_data, "objects", f"membranes[{membrane_key!r}]"
            )
            initial_objects[int(membrane_key)] = self._parse_counter(
                objects, f"membranes[{membrane_key!r}].objects"
            )
        return initial_objects

    def _parse_rules(self, value: Any) -> dict[int, list[Rule]]:
        """Convierte la lista JSON de reglas por membrana."""
        if not isinstance(value, list):
            raise JsonLoaderError("rules debe ser una lista")

        rules_by_membrane: dict[int, list[Rule]] = {}
        for index, rule_data in enumerate(value):
            context = f"rules[{index}]"
            rule_mapping = self._expect_mapping(rule_data, context)
            rule_id = self._required(rule_mapping, "id", context)
            membrane_id = self._parse_required_int(rule_mapping, "membrane", context)
            lhs = self._parse_counter(self._required(rule_mapping, "lhs", context), f"{context}.lhs")
            rhs = self._parse_rhs(self._required(rule_mapping, "rhs", context), context)

            try:
                rule = Rule(rule_id, membrane_id, lhs, rhs)
            except ValueError as exc:
                raise JsonLoaderError(f"{context}: {exc}") from exc
            rules_by_membrane.setdefault(membrane_id, []).append(rule)

        return rules_by_membrane

    def _parse_rhs(self, value: Any, rule_context: str) -> list[ProducedObject]:
        """Convierte los objetos producidos por una regla."""
        if not isinstance(value, list):
            raise JsonLoaderError(f"{rule_context}.rhs debe ser una lista")
        if not value:
            raise JsonLoaderError(
                f"{rule_context}.rhs debe contener al menos un elemento"
            )

        produced_objects: list[ProducedObject] = []
        for index, item in enumerate(value):
            context = f"{rule_context}.rhs[{index}]"
            item_mapping = self._expect_mapping(item, context)
            symbol = self._required(item_mapping, "object", context)
            count = self._parse_required_int(item_mapping, "count", context)
            target = self._required(item_mapping, "target", context)
            if not isinstance(target, str):
                raise JsonLoaderError(f"{context}.target debe ser una cadena")

            try:
                produced_objects.append(ProducedObject(symbol, count, target))
            except ValueError as exc:
                raise JsonLoaderError(f"{context}: {exc}") from exc

        return produced_objects

    def _parse_counter(self, value: Any, context: str) -> Counter[str]:
        """Convierte un objeto JSON en un multiconjunto."""
        mapping = self._expect_mapping(value, context)
        counter: Counter[str] = Counter()
        for symbol, count in mapping.items():
            if not isinstance(symbol, str) or not symbol.strip():
                raise JsonLoaderError(f"{context} contiene un símbolo no válido")
            if type(count) is not int or count <= 0:
                raise JsonLoaderError(
                    f"{context}[{symbol!r}] debe ser un entero positivo"
                )
            counter[symbol] = count
        return counter

    def _parse_required_int(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        context: str,
    ) -> int:
        """Obtiene un entero obligatorio."""
        value = self._required(mapping, field_name, context)
        if type(value) is not int:
            raise JsonLoaderError(f"{context}.{field_name} debe ser un entero")
        return value

    def _parse_optional_int(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        default: int | None,
    ) -> int | None:
        """Obtiene un entero opcional."""
        if field_name not in mapping:
            return default
        value = mapping[field_name]
        if value is None:
            return None
        if type(value) is not int:
            raise JsonLoaderError(f"{field_name} debe ser un entero")
        return value

    def _required(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        context: str,
    ) -> Any:
        """Obtiene un campo obligatorio."""
        if field_name not in mapping:
            raise JsonLoaderError(f"{context}.{field_name} es obligatorio")
        return mapping[field_name]

    def _expect_mapping(self, value: Any, context: str) -> Mapping[str, Any]:
        """Valida que un valor JSON sea un objeto."""
        if not isinstance(value, Mapping):
            raise JsonLoaderError(f"{context} debe ser un objeto")
        return value
