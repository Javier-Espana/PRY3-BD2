from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from neo4j import GraphDatabase

from .models import PuzzleDef


def build_connection_settings() -> tuple[str, str, str]:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tu_password")
    return uri, user, password


class PuzzleRepository:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self._driver.close()

    @contextmanager
    def session(self) -> Iterator:
        with self._driver.session() as session:
            yield session

    def ensure_schema(self) -> None:
        with self.session() as s:
            s.run(
                "CREATE CONSTRAINT puzzle_id_unique IF NOT EXISTS "
                "FOR (p:Puzzle) REQUIRE p.puzzle_id IS UNIQUE"
            )
            s.run(
                "CREATE CONSTRAINT piece_id_unique IF NOT EXISTS "
                "FOR (p:Pieza) REQUIRE p.piece_id IS UNIQUE"
            )
            s.run(
                "CREATE CONSTRAINT conex_id_unique IF NOT EXISTS "
                "FOR (c:Conex) REQUIRE c.id IS UNIQUE"
            )

    def list_puzzles(self) -> list[dict]:
        query = """
        MATCH (pu:Puzzle)
        OPTIONAL MATCH (pu)-[:TIENE]->(pi:Pieza)
        RETURN pu.puzzle_id AS puzzle_id,
               pu.nombre AS nombre,
               pu.total_piezas AS total_piezas,
               count(pi) AS piezas_registradas
        ORDER BY pu.nombre ASC, pu.puzzle_id ASC
        """
        with self.session() as s:
            return [r.data() for r in s.run(query)]

    def get_puzzle_info(self, puzzle_id: str) -> dict | None:
        with self.session() as s:
            record = s.run(
                "MATCH (pu:Puzzle {puzzle_id: $puzzle_id}) "
                "RETURN pu.puzzle_id AS puzzle_id, pu.nombre AS nombre, pu.total_piezas AS total_piezas",
                puzzle_id=puzzle_id,
            ).single()
            return record.data() if record else None

    def list_pieces(self, puzzle_id: str) -> list[dict]:
        query = """
        MATCH (:Puzzle {puzzle_id: $puzzle_id})-[:TIENE]->(pi:Pieza)
        RETURN pi.label AS label, pi.disponible AS disponible
        ORDER BY pi.label ASC
        """
        with self.session() as s:
            return [r.data() for r in s.run(query, puzzle_id=puzzle_id)]

    def get_neighbors(self, puzzle_id: str, piece_label: str) -> list[dict]:
        query = """
        MATCH (p:Pieza {piece_id: $piece_id})
        MATCH (p)-[:TIENE_CONEXION]->(c1:Conex)-[:ENLAZA]-(c2:Conex)<-[:TIENE_CONEXION]-(vecino:Pieza)
        RETURN c1.numero AS conex_origen,
               c1.tipo AS tipo_origen,
               vecino.label AS vecino_label,
               vecino.disponible AS vecino_disponible,
               c2.numero AS conex_vecino,
               c2.tipo AS tipo_vecino
        ORDER BY vecino.label ASC, c1.numero ASC, c2.numero ASC
        """
        with self.session() as s:
            return [
                r.data()
                for r in s.run(query, piece_id=f"{puzzle_id}:{piece_label}")
            ]

    def upsert_puzzle(self, puzzle: PuzzleDef) -> None:
        self.ensure_schema()

        with self.session() as s:
            s.run(
                """
                MATCH (pu:Puzzle {puzzle_id: $puzzle_id})-[:TIENE]->(pi:Pieza)-[:TIENE_CONEXION]->(c:Conex)
                DETACH DELETE c
                """,
                puzzle_id=puzzle.puzzle_id,
            )
            s.run(
                """
                MATCH (pu:Puzzle {puzzle_id: $puzzle_id})-[:TIENE]->(pi:Pieza)
                DETACH DELETE pi
                """,
                puzzle_id=puzzle.puzzle_id,
            )
            s.run(
                "MATCH (pu:Puzzle {puzzle_id: $puzzle_id}) DETACH DELETE pu",
                puzzle_id=puzzle.puzzle_id,
            )

            s.run(
                """
                CREATE (:Puzzle {
                    puzzle_id: $puzzle_id,
                    nombre: $nombre,
                    marca: $marca,
                    material: $material,
                    tematica: $tematica,
                    total_piezas: $total_piezas
                })
                """,
                puzzle_id=puzzle.puzzle_id,
                nombre=puzzle.nombre,
                marca=puzzle.marca,
                material=puzzle.material,
                tematica=puzzle.tematica,
                total_piezas=puzzle.total_piezas,
            )

            for piece in puzzle.piezas:
                s.run(
                    """
                    MATCH (pu:Puzzle {puzzle_id: $puzzle_id})
                    CREATE (pi:Pieza {
                        piece_id: $piece_id,
                        puzzle_id: $puzzle_id,
                        label: $label,
                        disponible: $disponible
                    })
                    CREATE (pu)-[:TIENE]->(pi)
                    """,
                    puzzle_id=puzzle.puzzle_id,
                    piece_id=f"{puzzle.puzzle_id}:{piece.label}",
                    label=piece.label,
                    disponible=True,
                )

            for c in puzzle.conexiones:
                conn_id = f"{puzzle.puzzle_id}:{c.piece_label}:{c.numero}"
                s.run(
                    """
                    MATCH (pi:Pieza {piece_id: $piece_id})
                    CREATE (co:Conex {
                        id: $conn_id,
                        puzzle_id: $puzzle_id,
                        piece_label: $piece_label,
                        numero: $numero,
                        tipo: $tipo
                    })
                    CREATE (pi)-[:TIENE_CONEXION]->(co)
                    """,
                    piece_id=f"{puzzle.puzzle_id}:{c.piece_label}",
                    conn_id=conn_id,
                    puzzle_id=puzzle.puzzle_id,
                    piece_label=c.piece_label,
                    numero=c.numero,
                    tipo=c.tipo,
                )

            for e in puzzle.enlaces:
                id_a = f"{puzzle.puzzle_id}:{e.piece_a}:{e.conn_a}"
                id_b = f"{puzzle.puzzle_id}:{e.piece_b}:{e.conn_b}"
                s.run(
                    """
                    MATCH (a:Conex {id: $id_a})
                    MATCH (b:Conex {id: $id_b})
                    CREATE (a)-[:ENLAZA]->(b)
                    """,
                    id_a=id_a,
                    id_b=id_b,
                )
