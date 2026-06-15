from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models import Configuration, PSystem, Rule
from src.parser import JsonLoader, JsonLoaderError
from src.simulator import AppliedRule, SimulationMode, Simulator, StepResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
DEFAULT_MAX_STEPS = 50


def main() -> None:
    """Renderiza la aplicacion principal de Streamlit."""
    st.set_page_config(page_title="Simulador de Sistemas P", layout="wide")
    st.title("Simulador de Sistemas P")

    source_key, psystem = render_system_loader()
    mode = render_mode_selector()
    max_steps = st.sidebar.number_input(
        "Max steps",
        min_value=1,
        max_value=10_000,
        value=DEFAULT_MAX_STEPS,
        step=1,
    )

    if psystem is None:
        st.info("Selecciona o sube un JSON valido para iniciar la simulacion.")
        return

    ensure_simulator(source_key, psystem, mode)
    simulator: Simulator = st.session_state["simulator"]

    render_controls(simulator, max_steps)
    render_status(simulator)
    render_rules(simulator.psystem)
    render_last_step(st.session_state.get("last_step_result"))
    render_history(simulator.get_history())


def render_system_loader() -> tuple[str | None, PSystem | None]:
    """Renderiza la carga de ejemplos o ficheros JSON."""
    st.sidebar.header("Sistema")
    source = st.sidebar.radio("Origen JSON", ["Ejemplo", "Subir archivo"])
    loader = JsonLoader()

    if source == "Ejemplo":
        example_paths = list_example_files()
        if not example_paths:
            return None, None

        selected_name = st.sidebar.selectbox(
            "Ejemplo",
            [path.name for path in example_paths],
        )
        selected_path = EXAMPLES_DIR / selected_name
        try:
            return f"example:{selected_name}", loader.load(selected_path)
        except JsonLoaderError as exc:
            st.error(f"Error al cargar el ejemplo: {exc}")
            return None, None

    uploaded_file = st.sidebar.file_uploader("JSON propio", type="json")
    if uploaded_file is None:
        return None, None

    try:
        file_bytes = uploaded_file.getvalue()
        source_hash = hashlib.sha256(file_bytes).hexdigest()
        data = json.loads(file_bytes.decode("utf-8"))
        return f"upload:{uploaded_file.name}:{source_hash}", loader.load_data(data)
    except (UnicodeDecodeError, json.JSONDecodeError, JsonLoaderError, ValueError) as exc:
        st.error(f"Error al cargar el JSON: {exc}")
        return None, None


def render_mode_selector() -> SimulationMode:
    """Renderiza el selector del modo de simulacion."""
    st.sidebar.header("Ejecucion")
    mode_value = st.sidebar.selectbox(
        "Modo",
        [SimulationMode.SEQUENTIAL.value, SimulationMode.MAXIMAL_PARALLEL.value],
        index=1,
    )
    return SimulationMode.from_value(mode_value)


def ensure_simulator(source_key: str | None, psystem: PSystem, mode: SimulationMode) -> None:
    """Inicializa el simulador cuando cambia la entrada."""
    simulator_key = (source_key, mode.value)
    if st.session_state.get("simulator_key") == simulator_key:
        return

    st.session_state["simulator_key"] = simulator_key
    st.session_state["simulator"] = Simulator(psystem, mode)
    st.session_state["last_step_result"] = None


def render_controls(simulator: Simulator, max_steps: int) -> None:
    """Renderiza los controles de ejecucion."""
    st.subheader("Controles")
    step_col, run_col, reset_col = st.columns(3)

    with step_col:
        if st.button("Ejecutar paso", use_container_width=True):
            st.session_state["last_step_result"] = simulator.step()

    with run_col:
        if st.button("Ejecutar hasta parada", use_container_width=True):
            results = simulator.run(max_steps)
            st.session_state["last_step_result"] = results[-1] if results else None

    with reset_col:
        if st.button("Reiniciar", use_container_width=True):
            st.session_state["simulator"] = Simulator(simulator.psystem, simulator.mode)
            st.session_state["last_step_result"] = None
            st.rerun()


def render_status(simulator: Simulator) -> None:
    """Muestra la configuracion actual y su estado."""
    st.subheader("Configuracion actual")
    configuration = simulator.current_configuration
    cols = st.columns(3)
    for index, membrane_id in enumerate((1, 2, 3)):
        with cols[index]:
            st.metric(f"Membrana {membrane_id}", f"Paso {configuration.step}")
            st.table(multiset_rows(configuration.objects_in(membrane_id)))

    if simulator.is_halted():
        st.success("Configuracion de parada alcanzada.")


def render_rules(psystem: PSystem) -> None:
    """Muestra las reglas definidas en el sistema."""
    st.subheader("Reglas del sistema")
    rows: list[dict[str, Any]] = []
    for membrane_id in sorted(psystem.rules):
        for rule in psystem.get_rules(membrane_id):
            rows.append(
                {
                    "membrana": membrane_id,
                    "id": rule.id,
                    "lhs": format_multiset(rule.consumed_objects()),
                    "rhs": format_rule_rhs(rule),
                }
            )

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("El sistema no tiene reglas definidas.")


def render_last_step(step_result: StepResult | None) -> None:
    """Muestra las reglas aplicadas en el ultimo paso."""
    st.subheader("Ultimo paso")
    if step_result is None:
        st.caption("Todavia no se ha ejecutado ningun paso.")
        return
    if step_result.halted:
        st.info("No habia reglas aplicables.")
        return

    st.dataframe(
        [applied_rule_row(applied_rule) for applied_rule in step_result.applied_rules],
        use_container_width=True,
        hide_index=True,
    )


def render_history(history: list[Configuration]) -> None:
    """Muestra el historial de configuraciones."""
    st.subheader("Historial de configuraciones")
    for configuration in history:
        with st.expander(f"Configuracion {configuration.step}", expanded=False):
            cols = st.columns(3)
            for index, membrane_id in enumerate((1, 2, 3)):
                with cols[index]:
                    st.markdown(f"**Membrana {membrane_id}**")
                    st.table(multiset_rows(configuration.objects_in(membrane_id)))


def list_example_files() -> list[Path]:
    """Lista los ejemplos JSON disponibles."""
    if not EXAMPLES_DIR.exists():
        st.sidebar.warning("No existe la carpeta examples/.")
        return []

    example_paths = sorted(EXAMPLES_DIR.glob("*.json"))
    if not example_paths:
        st.sidebar.warning("No hay ficheros JSON en examples/.")
    return example_paths


def multiset_rows(objects: dict[str, int]) -> list[dict[str, Any]]:
    """Convierte un multiconjunto en filas para una tabla."""
    if not objects:
        return [{"objeto": "-", "multiplicidad": 0}]
    return [
        {"objeto": symbol, "multiplicidad": count}
        for symbol, count in sorted(objects.items())
    ]


def format_multiset(objects: dict[str, int]) -> str:
    """Formatea un multiconjunto como texto."""
    if not objects:
        return "{}"
    return "{" + ", ".join(f"{symbol}:{count}" for symbol, count in objects.items()) + "}"


def format_rule_rhs(rule: Rule) -> str:
    """Formatea el consecuente de una regla."""
    return ", ".join(
        f"{produced.symbol}:{produced.count}->{produced.target}"
        for produced in rule.rhs
    )


def applied_rule_row(applied_rule: AppliedRule) -> dict[str, Any]:
    """Convierte una regla aplicada en una fila de tabla."""
    return {
        "regla": applied_rule.rule_id,
        "membrana": applied_rule.membrane_id,
        "consume": format_multiset(applied_rule.consumed),
        "produce": ", ".join(
            f"{move.symbol}:{move.count}->{move.target} (m{move.target_membrane_id})"
            for move in applied_rule.produced
        ),
    }


if __name__ == "__main__":
    main()
