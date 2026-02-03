"""Static package metadata surfaced to CLI commands and documentation.

Purpose
-------
Expose the current project metadata as simple constants. These values are kept
in sync with ``pyproject.toml`` by development automation (tests, push
pipelines), so runtime code does not query packaging metadata.

Contents
--------
* Module-level constants describing the published package.
* :func:`print_info` rendering the constants for the CLI ``info`` command.

System Role
-----------
Lives in the adapters/platform layer; CLI transports import these constants to
present authoritative project information without invoking packaging APIs.
"""

from __future__ import annotations

import sys

#: Distribution name declared in ``pyproject.toml``.
name = "pyproject"
#: Human-readable summary shown in CLI help output.
title = "pyproject"
#: Current release version pulled from ``pyproject.toml`` by automation.
version = "3.0.0"
#: Repository homepage presented to users.
homepage = "https://github.com/bitranox/lib_shopware6_api_base"
#: Author attribution surfaced in CLI output.
author = "bitranox"
#: Contact email surfaced in CLI output.
author_email = ""
#: Console-script name published by the package.
shell_command = "lib-shopware6-api-base"

#: Vendor identifier for lib_layered_config paths (macOS/Windows)
LAYEREDCONF_VENDOR: str = "bitranox"
#: Application display name for lib_layered_config paths (macOS/Windows)
LAYEREDCONF_APP: str = "Pyproject"
#: Configuration slug for lib_layered_config Linux paths and environment variables
LAYEREDCONF_SLUG: str = "lib-shopware6-api-base"


def print_info() -> None:
    """Print the summarised metadata block used by the CLI ``info`` command.

    Why
        Provides a single, auditable rendering function so documentation and
        CLI output always match the system design reference.

    Side Effects
        Writes to ``stdout``.

    Examples
    --------
    >>> print_info()  # doctest: +ELLIPSIS
    Info for pyproject:
    ...
    """

    fields = [
        ("name", name),
        ("title", title),
        ("version", version),
        ("homepage", homepage),
        ("author", author),
        ("author_email", author_email),
        ("shell_command", shell_command),
    ]
    pad = max(len(label) for label, _ in fields)
    lines = [f"Info for {name}:", ""]
    lines.extend(f"    {label.ljust(pad)} = {value}" for label, value in fields)
    sys.stdout.write("\n".join(lines) + "\n")
