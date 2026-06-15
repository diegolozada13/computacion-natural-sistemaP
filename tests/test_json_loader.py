from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.parser import JsonLoader, JsonLoaderError


class JsonLoaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = JsonLoader()

    def test_loads_minimal_psystem_from_file(self) -> None:
        data = {
            "seed": 42,
            "alphabet": ["a", "b", "c"],
            "membranes": {
                "1": {"objects": {}},
                "2": {"objects": {"a": 2}},
                "3": {"objects": {}},
            },
            "rules": [
                {
                    "id": "r1",
                    "membrane": 2,
                    "lhs": {"a": 1},
                    "rhs": [{"object": "b", "count": 1, "target": "here"}],
                }
            ],
            "output_membrane": 1,
        }

        psystem = self.loader.load(self._write_json(data))

        self.assertEqual(psystem.seed, 42)
        self.assertEqual(psystem.get_membrane(2).multiplicity("a"), 2)
        self.assertEqual(psystem.get_rules(2)[0].id, "r1")
        self.assertTrue(psystem.get_rules(2)[0].is_applicable({"a": 1}))

    def test_rejects_invalid_target_for_membrane_structure(self) -> None:
        data = self._valid_data()
        data["rules"][0]["membrane"] = 1
        data["rules"][0]["rhs"][0]["target"] = "out"

        with self.assertRaisesRegex(JsonLoaderError, "destinos no válidos"):
            self.loader.load_data(data)

    def test_rejects_symbols_outside_alphabet(self) -> None:
        data = self._valid_data()
        data["rules"][0]["rhs"][0]["object"] = "z"

        with self.assertRaisesRegex(JsonLoaderError, "fuera del alfabeto"):
            self.loader.load_data(data)

    def test_rejects_unknown_rule_membrane(self) -> None:
        data = self._valid_data()
        data["rules"][0]["membrane"] = 4

        with self.assertRaisesRegex(JsonLoaderError, "membranas desconocidas"):
            self.loader.load_data(data)

    def test_rejects_format_errors(self) -> None:
        data = self._valid_data()
        del data["rules"][0]["rhs"]

        with self.assertRaisesRegex(JsonLoaderError, "rules\\[0\\].rhs es obligatorio"):
            self.loader.load_data(data)

    def _valid_data(self) -> dict:
        return {
            "alphabet": ["a", "b"],
            "membranes": {
                "1": {"objects": {}},
                "2": {"objects": {"a": 1}},
                "3": {"objects": {}},
            },
            "rules": [
                {
                    "id": "r1",
                    "membrane": 2,
                    "lhs": {"a": 1},
                    "rhs": [{"object": "b", "count": 1, "target": "here"}],
                }
            ],
            "output_membrane": 1,
        }

    def _write_json(self, data: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "system.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
