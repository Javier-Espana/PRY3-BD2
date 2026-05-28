from __future__ import annotations

from pathlib import Path

from .models import ConnectionDef, LinkDef, PieceDef, PuzzleDef


VALID_TIPOS = {"MACHO", "HEMBRA"}
SECTIONS = {"PUZZLE", "PIEZAS", "CONEXIONES", "ENLACES"}


class PuzzleFormatError(ValueError):
    pass


def _parse_section_header(line: str) -> str | None:
    if line.startswith("[") and line.endswith("]"):
        section = line[1:-1].strip().upper()
        if section not in SECTIONS:
            raise PuzzleFormatError(f"Seccion desconocida: '{section}'")
        return section
    return None


def parse_puzzle_txt(file_path: str | Path) -> PuzzleDef:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    puzzle_fields: dict[str, str] = {}
    piezas: list[PieceDef] = []
    conexiones: list[ConnectionDef] = []
    enlaces: list[LinkDef] = []
    section: str | None = None

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            maybe_header = _parse_section_header(line)
            if maybe_header:
                section = maybe_header
                continue

            if section is None:
                raise PuzzleFormatError("El archivo debe empezar con una seccion [PUZZLE].")

            if section == "PUZZLE":
                if "=" not in line:
                    raise PuzzleFormatError(f"Linea invalida en [PUZZLE]: '{line}'")
                key, value = line.split("=", 1)
                puzzle_fields[key.strip().lower()] = value.strip()
                continue

            if section == "PIEZAS":
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) != 1:
                    raise PuzzleFormatError(f"Linea invalida en [PIEZAS]: '{line}'")
                piezas.append(PieceDef(label=parts[0]))
                continue

            if section == "CONEXIONES":
                parts = [p.strip() for p in line.split("|")]
                if len(parts) != 3:
                    raise PuzzleFormatError(f"Linea invalida en [CONEXIONES]: '{line}'")
                tipo = parts[2].upper()
                if tipo not in VALID_TIPOS:
                    raise PuzzleFormatError(f"Tipo de conexion invalido: '{parts[2]}'")
                try:
                    numero = int(parts[1])
                except ValueError as exc:
                    raise PuzzleFormatError(f"Numero de conexion invalido: '{parts[1]}'") from exc
                conexiones.append(ConnectionDef(piece_label=parts[0], numero=numero, tipo=tipo))
                continue

            if section == "ENLACES":
                parts = [p.strip() for p in line.split("|")]
                if len(parts) != 4:
                    raise PuzzleFormatError(f"Linea invalida en [ENLACES]: '{line}'")
                try:
                    conn_a = int(parts[1])
                    conn_b = int(parts[3])
                except ValueError as exc:
                    raise PuzzleFormatError(f"Conexion invalida en [ENLACES]: '{line}'") from exc
                enlaces.append(
                    LinkDef(piece_a=parts[0], conn_a=conn_a, piece_b=parts[2], conn_b=conn_b)
                )

    required = ["puzzle_id", "nombre"]
    missing_required = [k for k in required if k not in puzzle_fields]
    if missing_required:
        raise PuzzleFormatError(
            f"Faltan campos obligatorios en [PUZZLE]: {', '.join(missing_required)}"
        )

    empty_required = [k for k in required if not puzzle_fields[k].strip()]
    if empty_required:
        raise PuzzleFormatError(
            f"Los campos obligatorios en [PUZZLE] no pueden estar vacios: {', '.join(empty_required)}"
        )

    if not piezas:
        raise PuzzleFormatError("Debe definir al menos una pieza en [PIEZAS].")

    labels = {p.label for p in piezas}
    if len(labels) != len(piezas):
        raise PuzzleFormatError("Hay labels de piezas duplicados en [PIEZAS].")

    conn_map: dict[tuple[str, int], str] = {}
    for c in conexiones:
        if c.piece_label not in labels:
            raise PuzzleFormatError(
                f"La conexion {c.piece_label}|{c.numero} referencia una pieza inexistente."
            )
        key = (c.piece_label, c.numero)
        if key in conn_map:
            raise PuzzleFormatError(
                f"Conexion duplicada en [CONEXIONES]: {c.piece_label}|{c.numero}"
            )
        conn_map[key] = c.tipo

    for e in enlaces:
        key_a = (e.piece_a, e.conn_a)
        key_b = (e.piece_b, e.conn_b)
        if key_a not in conn_map:
            raise PuzzleFormatError(
                f"El enlace referencia conexion inexistente: {e.piece_a}|{e.conn_a}"
            )
        if key_b not in conn_map:
            raise PuzzleFormatError(
                f"El enlace referencia conexion inexistente: {e.piece_b}|{e.conn_b}"
            )
        tipo_a = conn_map[key_a]
        tipo_b = conn_map[key_b]
        if tipo_a == tipo_b:
            raise PuzzleFormatError(
                f"Enlace invalido {e.piece_a}|{e.conn_a} <-> {e.piece_b}|{e.conn_b}: "
                "debe conectar MACHO con HEMBRA."
            )

    total_piezas_raw = puzzle_fields.get("total_piezas")
    if total_piezas_raw is None or not total_piezas_raw.strip():
        total_piezas = len(piezas)
    else:
        try:
            total_piezas = int(total_piezas_raw)
        except ValueError as exc:
            raise PuzzleFormatError(
                f"total_piezas invalido en [PUZZLE]: '{total_piezas_raw}'"
            ) from exc

    return PuzzleDef(
        puzzle_id=puzzle_fields["puzzle_id"],
        nombre=puzzle_fields["nombre"],
        marca=puzzle_fields.get("marca", ""),
        material=puzzle_fields.get("material", ""),
        tematica=puzzle_fields.get("tematica", ""),
        total_piezas=total_piezas,
        piezas=piezas,
        conexiones=conexiones,
        enlaces=enlaces,
    )
