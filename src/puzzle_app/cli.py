from __future__ import annotations

from pathlib import Path

from .db import PuzzleRepository, build_connection_settings
from .loader import import_puzzle_from_txt
from .parser_txt import PuzzleFormatError
from .solver import solve_puzzle


def _read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Entrada vacia. Intenta de nuevo.")


def _choose_puzzle(repo: PuzzleRepository) -> str | None:
    puzzles = repo.list_puzzles()
    if not puzzles:
        print("No hay rompecabezas cargados en la base de datos.")
        return None

    print("\nRompecabezas disponibles:")
    for idx, p in enumerate(puzzles, start=1):
        print(
            f"  {idx}. {p['nombre']} (id={p['puzzle_id']}, "
            f"total={p['total_piezas']}, piezas_registradas={p['piezas_registradas']})"
        )

    while True:
        raw = _read_non_empty("Elige un rompecabezas por numero: ")
        try:
            idx = int(raw)
        except ValueError:
            print("Debes escribir un numero valido.")
            continue

        if 1 <= idx <= len(puzzles):
            return str(puzzles[idx - 1]["puzzle_id"])

        print("Numero fuera de rango.")


def _read_missing_pieces(valid_labels: set[str], start_piece: str) -> set[str]:
    missing: set[str] = set()

    while True:
        answer = _read_non_empty("Deseas registrar una pieza faltante? (s/n): ").lower()
        if answer in {"n", "no"}:
            break
        if answer not in {"s", "si", "y", "yes"}:
            print("Respuesta invalida. Escribe 's' o 'n'.")
            continue

        label = _read_non_empty("Label de pieza faltante: ")
        if label not in valid_labels:
            print("La pieza no existe en ese rompecabezas.")
            continue
        if label == start_piece:
            print("La pieza inicial no puede marcarse como faltante.")
            continue
        if label in missing:
            print("Esa pieza ya estaba marcada como faltante.")
            continue

        missing.add(label)
        print(f"Pieza {label} marcada como faltante.")

    return missing


def _run_import(repo: PuzzleRepository) -> None:
    path_str = _read_non_empty("Ruta del archivo .txt a importar: ")
    path = Path(path_str)

    try:
        puzzle_id = import_puzzle_from_txt(repo, path)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return
    except PuzzleFormatError as exc:
        print(f"[ERROR] Formato invalido: {exc}")
        return

    print(f"[OK] Rompecabezas importado/actualizado: {puzzle_id}")


def _run_solver(repo: PuzzleRepository) -> None:
    puzzle_id = _choose_puzzle(repo)
    if not puzzle_id:
        return

    info = repo.get_puzzle_info(puzzle_id)
    if not info:
        print("No se encontro informacion del rompecabezas.")
        return

    pieces = repo.list_pieces(puzzle_id)
    piece_map = {p["label"]: bool(p["disponible"]) for p in pieces}

    print("\nPiezas del rompecabezas:")
    for p in pieces:
        status = "disponible" if p["disponible"] else "FALTANTE (registrada en BD)"
        print(f"  - {p['label']} ({status})")

    while True:
        start_piece = _read_non_empty("Pieza inicial: ")
        if start_piece not in piece_map:
            print("Esa pieza no existe.")
            continue
        if not piece_map[start_piece]:
            print("Esa pieza ya esta marcada como faltante en la base de datos.")
            continue
        break

    missing = _read_missing_pieces(set(piece_map.keys()), start_piece)

    if missing:
        for label in missing:
            repo.mark_piece_missing(puzzle_id, label)
        print(f"[BD] Piezas registradas como faltantes en Neo4j: {', '.join(sorted(missing))}")

    try:
        result = solve_puzzle(repo, puzzle_id, start_piece, missing)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return

    print("\n" + "=" * 68)
    print("INSTRUCCIONES DE ARMADO")
    print(f"Puzzle : {info['nombre']} ({puzzle_id})")
    print(f"Inicio : {start_piece}")
    print("=" * 68)
    print(f"\nColoca la pieza {start_piece} frente a ti.\n")

    if result.instructions:
        for line in result.instructions:
            print(line)
    else:
        print("No hay pasos de conexion desde la pieza inicial.")

    print("\n" + "=" * 68)
    if result.missing:
        print("Estado: armado parcial (hay piezas faltantes).")
        print(f"Piezas faltantes detectadas: {', '.join(result.missing)}")
    else:
        print("Estado: armado completo.")

    print(f"Orden de armado: {' -> '.join(result.order)}")

    if result.unreachable:
        print(
            "Piezas no alcanzadas desde la pieza inicial: "
            f"{', '.join(result.unreachable)}"
        )
    print("=" * 68)


def _run_reset(repo: PuzzleRepository) -> None:
    puzzle_id = _choose_puzzle(repo)
    if not puzzle_id:
        return

    confirm = _read_non_empty(
        f"Esto marcara TODAS las piezas de '{puzzle_id}' como disponibles. Confirmar? (s/n): "
    ).lower()
    if confirm not in {"s", "si", "y", "yes"}:
        print("Operacion cancelada.")
        return

    repo.reset_all_pieces(puzzle_id)
    print(f"[OK] Todas las piezas de '{puzzle_id}' restauradas a disponible en Neo4j.")


def run_cli() -> None:
    uri, user, password = build_connection_settings()
    repo = PuzzleRepository(uri=uri, user=user, password=password)

    try:
        while True:
            print("\n=== MENU ROMPECABEZAS (Neo4j) ===")
            print("1. Importar rompecabezas desde TXT")
            print("2. Resolver rompecabezas")
            print("3. Restaurar piezas faltantes a disponible")
            print("4. Salir")

            option = _read_non_empty("Elige una opcion: ")

            if option == "1":
                _run_import(repo)
                continue
            if option == "2":
                _run_solver(repo)
                continue
            if option == "3":
                _run_reset(repo)
                continue
            if option == "4":
                print("Saliendo...")
                return

            print("Opcion invalida.")
    finally:
        repo.close()
