from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.models import ProducedObject, PSystem, Rule


class JsonLoaderError(ValueError):
    """Raised when a JSON P system definition is invalid."""


class JsonLoader:
    """Build PSystem instances from JSON files."""

    REQUIRED_MEMBRANES = {"1", "2", "3"}

    def load(self, path: str | Path) -> PSystem:
        json_path = Path(path)
        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise JsonLoaderError(f"invalid JSON in {json_path}: {exc.msg}") from exc
        except OSError as exc:
            raise JsonLoaderError(f"cannot read JSON file {json_path}: {exc}") from exc

        return self.load_data(data)

    def load_data(self, data: Mapping[str, Any]) -> PSystem:
        document = self._expect_mapping(data, "root")

        alphabet = self._parse_alphabet(self._required(document, "alphabet", "root"))
        initial_objects = self._parse_membranes(
            self._required(document, "membranes", "root")
        )
        rules = self._parse_rules(self._required(document, "rules", "root"))
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
        if not isinstance(value, list):
            raise JsonLoaderError("alphabet must be a list of strings")
        if not value:
            raise JsonLoaderError("alphabet must contain at least one symbol")

        alphabet: set[str] = set()
        for index, symbol in enumerate(value):
            if not isinstance(symbol, str) or not symbol.strip():
                raise JsonLoaderError(f"alphabet[{index}] must be a non-empty string")
            if symbol in alphabet:
                raise JsonLoaderError(f"duplicated alphabet symbol {symbol!r}")
            alphabet.add(symbol)
        return alphabet

    def _parse_membranes(self, value: Any) -> dict[int, Counter[str]]:
        membranes = self._expect_mapping(value, "membranes")
        if set(membranes) != self.REQUIRED_MEMBRANES:
            raise JsonLoaderError("membranes must contain exactly keys '1', '2' and '3'")

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
        if not isinstance(value, list):
            raise JsonLoaderError("rules must be a list")

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
        if not isinstance(value, list):
            raise JsonLoaderError(f"{rule_context}.rhs must be a list")
        if not value:
            raise JsonLoaderError(f"{rule_context}.rhs must contain at least one item")

        produced_objects: list[ProducedObject] = []
        for index, item in enumerate(value):
            context = f"{rule_context}.rhs[{index}]"
            item_mapping = self._expect_mapping(item, context)
            symbol = self._required(item_mapping, "object", context)
            count = self._parse_required_int(item_mapping, "count", context)
            target = self._required(item_mapping, "target", context)
            if not isinstance(target, str):
                raise JsonLoaderError(f"{context}.target must be a string")

            try:
                produced_objects.append(ProducedObject(symbol, count, target))
            except ValueError as exc:
                raise JsonLoaderError(f"{context}: {exc}") from exc

        return produced_objects

    def _parse_counter(self, value: Any, context: str) -> Counter[str]:
        mapping = self._expect_mapping(value, context)
        counter: Counter[str] = Counter()
        for symbol, count in mapping.items():
            if not isinstance(symbol, str) or not symbol.strip():
                raise JsonLoaderError(f"{context} contains an invalid symbol")
            if type(count) is not int or count <= 0:
                raise JsonLoaderError(f"{context}[{symbol!r}] must be a positive integer")
            counter[symbol] = count
        return counter

    def _parse_required_int(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        context: str,
    ) -> int:
        value = self._required(mapping, field_name, context)
        if type(value) is not int:
            raise JsonLoaderError(f"{context}.{field_name} must be an integer")
        return value

    def _parse_optional_int(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        default: int | None,
    ) -> int | None:
        if field_name not in mapping:
            return default
        value = mapping[field_name]
        if value is None:
            return None
        if type(value) is not int:
            raise JsonLoaderError(f"{field_name} must be an integer")
        return value

    def _required(
        self,
        mapping: Mapping[str, Any],
        field_name: str,
        context: str,
    ) -> Any:
        if field_name not in mapping:
            raise JsonLoaderError(f"{context}.{field_name} is required")
        return mapping[field_name]

    def _expect_mapping(self, value: Any, context: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise JsonLoaderError(f"{context} must be an object")
        return value

