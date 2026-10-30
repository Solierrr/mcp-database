"""Versão do release, lida do version.txt que o release-please atualiza."""

from pathlib import Path

VERSION = (
    (Path(__file__).resolve().parent / "version.txt")
    .read_text(encoding="utf-8")
    .strip()
)
