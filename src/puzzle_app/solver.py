from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random

from .db import PuzzleRepository


@dataclass(frozen=True)
class SolveResult:
    instructions: list[str]
    order: list[str]
    missing: list[str]
    unreachable: list[str]


def _connection_description(tipo: str) -> str:
    tipo_normalizado = tipo.upper()
    if tipo_normalizado == "MACHO":
        return "MACHO (saliente)"
    if tipo_normalizado == "HEMBRA":
        return "HEMBRA (receptora)"
    return tipo


def _general_instructions() -> list[str]:
    return [
        "Instrucciones generales de armado:",
        "1. Cada pieza se identifica por el numero visible en su anverso.",
        "2. El anverso es la cara donde se lee el numero de la pieza y el numero de cada conexion.",
        "3. Coloca la pieza inicial en posicion correcta, derecha y sin invertirla, de forma que los numeros se lean normalmente.",
        "4. El reverso es la cara opuesta; durante el armado trabaja siempre con el anverso visible.",
        "5. Cada conexion se describe por su numero y su tipo: MACHO (saliente) o HEMBRA (receptora).",
        "6. En cada paso, une una conexion MACHO con una conexion HEMBRA compatibles segun la instruccion indicada.",
    ]


def _format_step(
    step: int,
    origin_label: str,
    origin_conn: int,
    origin_type: str,
    target_label: str,
    target_conn: int,
    target_type: str,
) -> str:
    return (
        f"Paso {step:>3}:\n"
        f"  Toma la pieza {target_label} y orienta su anverso hacia ti.\n"
        f"  Conecta su conexion {target_conn} ({_connection_description(target_type)})\n"
        f"  con la conexion {origin_conn} ({_connection_description(origin_type)})\n"
        f"  de la pieza {origin_label}."
    )


def _format_missing_step(
    step: int,
    origin_label: str,
    origin_conn: int,
    origin_type: str,
    missing_label: str,
    missing_conn: int,
    missing_type: str,
) -> str:
    return (
        f"Paso {step:>3}: [PIEZA FALTANTE]\n"
        f"  La pieza {missing_label}, con la conexion {missing_conn} "
        f"({_connection_description(missing_type)}),\n"
        f"  deberia conectarse a la conexion {origin_conn} "
        f"({_connection_description(origin_type)}) de la pieza {origin_label},\n"
        "  pero no esta disponible."
    )


def _format_component_jump(step: int, next_start: str) -> str:
    return (
        f"Paso {step:>3}:\n"
        "  Se agotaron las conexiones del mini-rompecabezas actual.\n"
        f"  Salta a la pieza {next_start} para continuar con otro grupo disponible."
    )


def solve_puzzle(
    repo: PuzzleRepository,
    puzzle_id: str,
    start_piece: str,
    user_missing_pieces: set[str] | None = None,
) -> SolveResult:
    user_missing_pieces = user_missing_pieces or set()

    pieces = repo.list_pieces(puzzle_id)
    if not pieces:
        raise ValueError("No hay piezas registradas para ese rompecabezas.")

    all_labels = [p["label"] for p in pieces]
    base_availability = {p["label"]: bool(p["disponible"]) for p in pieces}

    if start_piece not in base_availability:
        raise ValueError(f"La pieza inicial '{start_piece}' no existe en el rompecabezas.")

    effective_missing = {label for label, ok in base_availability.items() if not ok}
    effective_missing.update(user_missing_pieces)

    if start_piece in effective_missing:
        raise ValueError(
            f"La pieza inicial '{start_piece}' esta marcada como faltante. Elige otra pieza."
        )

    visited = {start_piece}
    order = [start_piece]
    missing_found: list[str] = []
    missing_set = set()
    instructions: list[str] = _general_instructions()
    instructions.append("")
    step = 1

    queue = deque([start_piece])

    while queue:
        current = queue.popleft()
        neighbors = repo.get_neighbors(puzzle_id, current)

        for n in neighbors:
            label = n["vecino_label"]
            if label in visited or label in missing_set:
                continue

            if label in effective_missing:
                instructions.append(
                    _format_missing_step(
                        step,
                        current,
                        int(n["conex_origen"]),
                        str(n["tipo_origen"]),
                        label,
                        int(n["conex_vecino"]),
                        str(n["tipo_vecino"]),
                    )
                )
                missing_set.add(label)
                missing_found.append(label)
                step += 1
                continue

            instructions.append(
                _format_step(
                    step,
                    current,
                    int(n["conex_origen"]),
                    str(n["tipo_origen"]),
                    label,
                    int(n["conex_vecino"]),
                    str(n["tipo_vecino"]),
                )
            )
            visited.add(label)
            queue.append(label)
            order.append(label)
            step += 1

        if queue:
            continue

        remaining_available = [
            label
            for label in all_labels
            if label not in visited and label not in effective_missing
        ]
        if not remaining_available:
            break

        next_start = random.choice(sorted(remaining_available))
        instructions.append(_format_component_jump(step, next_start))
        step += 1
        visited.add(next_start)
        order.append(next_start)
        queue.append(next_start)

    unresolved = sorted(set(all_labels) - set(order) - set(missing_found))

    return SolveResult(
        instructions=instructions,
        order=order,
        missing=missing_found,
        unreachable=unresolved,
    )
