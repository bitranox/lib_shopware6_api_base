"""Formatted automation help output for Makefile delegation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TextIO

from .target_metadata import iter_help_rows

__all__ = ["render_help", "print_help"]


def render_help(rows: Iterable[tuple[str, str]] | None = None) -> str:
    """Return aligned help text for automation targets."""
    data = tuple(rows or iter_help_rows())
    if not data:
        return "No automation targets declared."
    width = max(len(name) for name, _desc in data)
    lines = [f"{name.ljust(width)}  {desc}" for name, desc in data]
    return "\n".join(lines)


def print_help(stream: TextIO | None = None) -> None:
    """Write the automation help summary to the provided text stream."""
    target_stream = stream if stream is not None else _default_stream()
    target_stream.write(render_help() + "\n")
    target_stream.flush()


def _default_stream() -> TextIO:
    """Return the default output stream (stdout)."""
    import sys

    return sys.stdout


if __name__ == "__main__":  # pragma: no cover
    print_help()
