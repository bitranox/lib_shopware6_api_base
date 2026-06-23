"""Tests for the layered-config loader and the lib_log_rich logging setup."""

from __future__ import annotations

import lib_log_rich.runtime
import pytest

from lib_shopware6_api_base.config import get_config, get_default_config_path
from lib_shopware6_api_base.logging_setup import build_runtime_config, init_logging, shutdown_logging


class TestConfigLoader:
    @pytest.mark.os_agnostic
    def test_default_config_path_exists(self) -> None:
        path = get_default_config_path()
        assert path.name == "defaultconfig.toml"
        assert path.exists()

    @pytest.mark.os_agnostic
    def test_get_config_returns_config(self) -> None:
        get_config.cache_clear()
        config = get_config()
        # The bundled defaults provide both sections.
        assert config.get("shopware", default=None) is not None
        assert config.get("lib_log_rich", default=None) is not None


class TestLoggingSetup:
    @pytest.mark.os_agnostic
    def test_build_runtime_config_defaults_service(self) -> None:
        get_config.cache_clear()
        runtime_config = build_runtime_config(get_config())
        assert runtime_config.service == "lib_shopware6_api_base"
        assert runtime_config.environment

    @pytest.mark.os_agnostic
    def test_init_and_shutdown_logging(self) -> None:
        # Ensure a clean starting state, then verify the idempotent lifecycle.
        shutdown_logging()
        assert lib_log_rich.runtime.is_initialised() is False
        try:
            init_logging()
            assert lib_log_rich.runtime.is_initialised() is True
            # second call is a no-op
            init_logging()
            assert lib_log_rich.runtime.is_initialised() is True
        finally:
            shutdown_logging()
        assert lib_log_rich.runtime.is_initialised() is False
