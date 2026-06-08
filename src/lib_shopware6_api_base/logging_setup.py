"""Centralized ``lib_log_rich`` logging setup, configured via ``lib_layered_config``.

The application entry point (the CLI) initializes logging; library modules emit
records through the standard library (``logging.getLogger(__name__)``), which are
bridged into ``lib_log_rich``. The ``[lib_log_rich]`` section of the layered
configuration is mapped directly onto :class:`lib_log_rich.runtime.RuntimeConfig`.
"""

from __future__ import annotations

from typing import Any

import lib_log_rich.config
import lib_log_rich.runtime
from lib_layered_config import Config

from . import __init__conf__
from .config import get_config

__all__ = ["init_logging", "shutdown_logging", "build_runtime_config"]


def build_runtime_config(config: Config) -> lib_log_rich.runtime.RuntimeConfig:
    """Map the ``[lib_log_rich]`` config section onto a ``RuntimeConfig``.

    Unspecified values fall back to ``lib_log_rich`` defaults; ``service`` and
    ``environment`` default to the package name / ``"prod"`` when absent.
    """
    raw: Any = config.get("lib_log_rich", default={})
    settings: dict[str, Any] = dict(raw) if raw else {}
    settings.setdefault("service", __init__conf__.name)
    settings.setdefault("environment", "prod")
    return lib_log_rich.runtime.RuntimeConfig(**settings)


def init_logging(config: Config | None = None) -> None:
    """Initialize the ``lib_log_rich`` runtime exactly once (idempotent).

    Args:
        config: An already-loaded layered :class:`Config`. When omitted, the
            shared :func:`config.get_config` result is used.

    Side Effects:
        Loads ``.env`` overrides, initializes the global ``lib_log_rich`` runtime,
        and bridges stdlib logging into it on first call.
    """
    if lib_log_rich.runtime.is_initialised():
        return
    lib_log_rich.config.enable_dotenv()
    runtime_config = build_runtime_config(config if config is not None else get_config())
    lib_log_rich.runtime.init(runtime_config)
    lib_log_rich.runtime.attach_std_logging()


def shutdown_logging() -> None:
    """Flush and shut down the ``lib_log_rich`` runtime if it was initialized."""
    if lib_log_rich.runtime.is_initialised():
        lib_log_rich.runtime.shutdown()
