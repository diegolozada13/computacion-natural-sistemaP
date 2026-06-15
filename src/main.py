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


class SpanishArgumentParser(argparse.ArgumentParser):
    """Muestra la ayuda y los errores de argumentos en español."""

    def format_usage(self) -> str:
        """Traduce el encabezado de uso."""
        return super().format_usage().replace("usage:", "uso:", 1)

    def format_help(self) -> str:
        """Traduce el encabezado de uso dentro de la ayuda."""
        return super().format_help().replace("usage:", "uso:", 1)

    def error(self, message: str) -> None:
        """Finaliza con un mensaje genérico en español."""
        self.exit(
            2,
            f"Error: argumentos no válidos. Usa '{self.prog} --help' para ver la ayuda.\n",
        )


def main() -> int:
    """Ejecuta el simulador desde la linea de comandos."""
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
        print("Configuración de parada alcanzada.")
    else:
        print(f"Límite de pasos alcanzado ({args.max_steps}).")

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construye el analizador de argumentos del CLI."""
    parser = SpanishArgumentParser(
        add_help=False,
        description="Ejecuta un sistema P de transición desde un fichero JSON.",
    )
    parser._positionals.title = "argumentos posicionales"
    parser._optionals.title = "opciones"
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Muestra esta ayuda y termina.",
    )
    parser.add_argument("json_path", type=Path, help="Ruta del fichero JSON del sistema P.")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in SimulationMode],
        default=SimulationMode.MAXIMAL_PARALLEL.value,
        help="Modo de simulación.",
    )
    parser.add_argument(
        "--max-steps",
        type=positive_int,
        default=DEFAULT_MAX_STEPS,
        help=f"Número máximo de pasos a ejecutar. Por defecto: {DEFAULT_MAX_STEPS}.",
    )
    return parser


def positive_int(value: str) -> int:
    """Convierte un texto en un entero positivo."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("debe ser un entero positivo") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("debe ser un entero positivo")
    return parsed


def print_step_result(step_result: StepResult) -> None:
    """Imprime el resultado de un paso."""
    print(f"Paso {step_result.step}")
    if step_result.halted:
        print("  Sin reglas aplicables.")
        return

    print("  Reglas aplicadas:")
    for applied_rule in step_result.applied_rules:
        print(f"  - {format_applied_rule(applied_rule)}")


def print_configuration(configuration: Configuration) -> None:
    """Imprime una configuracion completa."""
    print(f"Configuración {configuration.step}")
    for membrane_id, objects in configuration.to_dict().items():
        print(f"  Membrana {membrane_id}: {format_multiset(objects)}")
    print()


def format_applied_rule(applied_rule: AppliedRule) -> str:
    """Formatea una regla aplicada para consola."""
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
    """Formatea un multiconjunto como texto."""
    if not objects:
        return "{}"
    return "{" + ", ".join(f"{symbol}:{count}" for symbol, count in objects.items()) + "}"


if __name__ == "__main__":
    raise SystemExit(main())
