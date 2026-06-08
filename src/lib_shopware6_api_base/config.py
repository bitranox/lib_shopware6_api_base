"""Layered configuration loading via ``lib_layered_config``.

All configuration for this package — both the Shopware connection settings
(``[shopware]``) and logging (``[lib_log_rich]``) — is loaded through
``lib_layered_config``, which merges, in increasing precedence:

    defaults (bundled) → app → host → user → ``.env`` → environment variables

The vendor / app / slug identifiers (see :mod:`__init__conf__`) determine the
platform-specific config file locations and the environment-variable prefix.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from lib_layered_config import Config, read_config

from . import __init__conf__

__all__ = ["get_config", "get_default_config_path"]


def get_default_config_path() -> Path:
    """Return the path to the bundled ``defaultconfig.toml`` shipped with the package."""
    return Path(__file__).parent / "defaultconfig.toml"


@lru_cache(maxsize=4)
def get_config(*, profile: str | None = None, start_dir: str | None = None) -> Config:
    """Load the merged, layered configuration.

    Args:
        profile: Optional profile name for environment isolation (inserts a
            ``profile/<name>/`` subdirectory into all config paths).
        start_dir: Optional directory that seeds ``.env`` discovery (defaults to cwd).

    Returns:
        An immutable :class:`lib_layered_config.Config`. Sections are read with
        ``config.get("<section>", default={})``.
    """
    return read_config(
        vendor=__init__conf__.LAYEREDCONF_VENDOR,
        app=__init__conf__.LAYEREDCONF_APP,
        slug=__init__conf__.LAYEREDCONF_SLUG,
        profile=profile,
        default_file=get_default_config_path(),
        start_dir=start_dir,
    )
