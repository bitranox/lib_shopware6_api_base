"""Strictly-typed wrappers for rich_click decorators with partially-unknown types.

rich_click ships ``py.typed`` but re-exports click's decorators, whose
``ParamType[Unknown]`` parameters make pyright (strict mode) report
``reportUnknownMemberType`` at every call site. Wrapping the affected decorators
here behind explicit, fully-known signatures keeps the rest of the code
strict-clean without disabling the rule. This module is the single boundary that
touches the untyped surface, so the only ``# pyright: ignore`` for this gap lives here.
"""

from collections.abc import Callable
from typing import Any

import rich_click as click

_CommandDecorator = Callable[[Callable[..., Any]], Callable[..., Any]]


def option(*param_decls: str, **attrs: Any) -> _CommandDecorator:
    """Typed wrapper over :func:`rich_click.option`. See module docstring."""
    return click.option(*param_decls, **attrs)  # pyright: ignore[reportUnknownMemberType]


def version_option(*param_decls: str, **attrs: Any) -> _CommandDecorator:
    """Typed wrapper over :func:`rich_click.version_option`. See module docstring."""
    return click.version_option(*param_decls, **attrs)  # pyright: ignore[reportUnknownMemberType]


def argument(*param_decls: str, **attrs: Any) -> _CommandDecorator:
    """Typed wrapper over :func:`rich_click.argument`. See module docstring."""
    return click.argument(*param_decls, **attrs)  # pyright: ignore[reportUnknownMemberType]


__all__ = ["argument", "option", "version_option"]
