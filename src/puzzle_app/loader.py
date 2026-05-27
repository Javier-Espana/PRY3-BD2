from __future__ import annotations

from pathlib import Path

from .db import PuzzleRepository
from .parser_txt import parse_puzzle_txt


def import_puzzle_from_txt(repo: PuzzleRepository, txt_path: str | Path) -> str:
    puzzle = parse_puzzle_txt(txt_path)
    repo.upsert_puzzle(puzzle)
    return puzzle.puzzle_id
