from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PieceDef:
    label: str


@dataclass(frozen=True)
class ConnectionDef:
    piece_label: str
    numero: int
    tipo: str


@dataclass(frozen=True)
class LinkDef:
    piece_a: str
    conn_a: int
    piece_b: str
    conn_b: int


@dataclass(frozen=True)
class PuzzleDef:
    puzzle_id: str
    nombre: str
    marca: str
    material: str
    tematica: str
    total_piezas: int
    piezas: list[PieceDef]
    conexiones: list[ConnectionDef]
    enlaces: list[LinkDef]
