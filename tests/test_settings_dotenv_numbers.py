"""Digit-only .env values reach every text setting as the text the operator wrote.

lib_layered_config's dotenv and environment layers turn an unquoted value into an int whenever
that number reads back as the same text (``123456`` stays ``123456``). A text setting must
therefore accept such a number and keep its digits; otherwise a numeric password, user name or
client secret in an ordinary ``.env`` line stops the program.

These tests load a real ``.env`` through the real loader, so a change in the library's coercion
shows up here rather than on a deployment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase, load_config_from_env
from lib_shopware6_api_base.config import get_config
from lib_shopware6_api_base.logging_setup import build_runtime_config

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def dotenv_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """A working directory whose ``.env`` the loader discovers, with a fresh config cache."""
    monkeypatch.chdir(tmp_path)
    get_config.cache_clear()
    yield tmp_path
    get_config.cache_clear()


def _write_dotenv(directory: Path, *lines: str) -> None:
    (directory / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.mark.os_agnostic
@pytest.mark.parametrize("attr", ["username", "password", "client_id", "client_secret", "store_api_sw_access_key"])
def test_digit_only_dotenv_value_reaches_a_text_setting_as_its_text(dotenv_dir: Path, attr: str) -> None:
    _write_dotenv(dotenv_dir, f"SHOPWARE__{attr.upper()}=123456")
    # Premise: the library hands the value over as a number. Without it the test proves nothing.
    assert isinstance(get_config().get("shopware", {})[attr], int)

    config = load_config_from_env()

    assert getattr(config, attr) == "123456"


@pytest.mark.os_agnostic
def test_digit_only_url_reaches_the_url_setting_as_its_text(dotenv_dir: Path) -> None:
    _write_dotenv(dotenv_dir, "SHOPWARE__ADMIN_API_URL=2026")
    assert isinstance(get_config().get("shopware", {})["admin_api_url"], int)

    assert load_config_from_env().shopware_admin_api_url == "2026"


@pytest.mark.os_agnostic
@pytest.mark.parametrize("attr", ["service", "environment"])
def test_digit_only_logging_value_reaches_the_runtime_config_as_its_text(dotenv_dir: Path, attr: str) -> None:
    _write_dotenv(dotenv_dir, f"LIB_LOG_RICH__{attr.upper()}=4711")
    config = get_config()
    assert isinstance(config.get("lib_log_rich", {})[attr], int)

    runtime = build_runtime_config(config)

    assert getattr(runtime, attr) == "4711"


@pytest.mark.os_agnostic
def test_a_boolean_is_still_refused_for_a_text_setting() -> None:
    with pytest.raises(ValidationError):
        ConfShopware6ApiBase.model_validate({"password": True})


@pytest.mark.os_agnostic
def test_an_invalid_grant_type_is_still_refused(dotenv_dir: Path) -> None:
    _write_dotenv(dotenv_dir, "SHOPWARE__GRANT_TYPE=12345")
    assert isinstance(get_config().get("shopware", {})["grant_type"], int)

    with pytest.raises(ValidationError):
        load_config_from_env()
