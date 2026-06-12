from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models import Configuration
from src.parser import JsonLoader, JsonLoaderError
from src.simulator import AppliedRule, SimulationMode, Simulator, StepResult


DEFAULT_MAX_STEPS = 50


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        mode = SimulationMode.from_value(args.mode)
        psystem = JsonLoader().load(args.json_path)
        simulator = Simulator(psystem, mode)
    except (JsonLoaderError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Sistema: {args.json_path}")
    print(f"Modo: {mode.value}")
    print()
    print_configuration(simulator.current_configuration)

    steps_executed = 0
    while steps_executed < args.max_steps and not simulator.is_halted():
        step_result = simulator.step()
        print_step_result(step_result)
        print_configuration(simulator.current_configuration)
        steps_executed += 1

    if simulator.is_halted():
        print("Configuracion de parada alcanzada.")
    else:
        print(f"Limite de pasos alcanzado ({args.max_steps}).")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta un sistema P de transicion desde un fichero JSON."
    )
    parser.add_argument("json_path", type=Path, help="Ruta del fichero JSON del sistema P.")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in SimulationMode],
        default=SimulationMode.MAXIMAL_PARALLEL.value,
        help="Modo de simulacion.",
    )
    parser.add_argument(
        "--max-steps",
        type=positive_int,
        default=DEFAULT_MAX_STEPS,
        help=f"Numero maximo de pasos a ejecutar. Por defecto: {DEFAULT_MAX_STEPS}.",
    )
    return parser


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("debe ser un entero positivo") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("debe ser un entero positivo")
    return parsed


def print_step_result(step_result: StepResult) -> None:
    print(f"Paso {step_result.step}")
    if step_result.halted:
        print("  Sin reglas aplicables.")
        return

    print("  Reglas aplicadas:")
    for applied_rule in step_result.applied_rules:
        print(f"  - {format_applied_rule(applied_rule)}")


def print_configuration(configuration: Configuration) -> None:
    print(f"Configuracion {configuration.step}")
    for membrane_id, objects in configuration.to_dict().items():
        print(f"  Membrana {membrane_id}: {format_multiset(objects)}")
    print()


def format_applied_rule(applied_rule: AppliedRule) -> str:
    produced = ", ".join(
        f"{move.symbol}:{move.count}->{move.target}"
        f"(m{move.target_membrane_id})"
        for move in applied_rule.produced
    )
    return (
        f"{applied_rule.rule_id} "
        f"[membrana {applied_rule.membrane_id}] "
        f"consume {format_multiset(applied_rule.consumed)} "
        f"produce [{produced}]"
    )


def format_multiset(objects: dict[str, int]) -> str:
    if not objects:
        return "{}"
    return "{" + ", ".join(f"{symbol}:{count}" for symbol, count in objects.items()) + "}"


if __name__ == "__main__":
    raise SystemExit(main())
