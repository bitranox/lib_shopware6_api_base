#!/usr/bin/env python3
"""Project automation dispatcher - calls scripts modules."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts package is importable
sys.path.insert(0, str(Path(__file__).parent))

from scripts import cli


def main() -> None:
    """Dispatch to scripts CLI with all arguments."""
    cli.main()


if __name__ == "__main__":
    main()
