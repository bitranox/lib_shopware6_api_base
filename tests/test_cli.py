"""Comprehensive tests for CLI functionality in lib_shopware6_api_base_cli.py."""

from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import sys

import pytest
from click.testing import CliRunner

from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase

logger = logging.getLogger()
os.environ["PYTEST_IS_RUNNING"] = "True"  # to be able to detect pytest when running the cli command

# Set PYTHONPATH for subprocess calls to find the src layout package
_src_path = pathlib.Path(__file__).resolve().parent.parent / "src"
_env = os.environ.copy()
_env["PYTHONPATH"] = str(_src_path) + os.pathsep + _env.get("PYTHONPATH", "")


def call_cli_command(commandline_args: str = "") -> bool:
    """Helper function to call CLI commands via subprocess."""
    args = [sys.executable, "-m", "lib_shopware6_api_base", *commandline_args.split()]
    try:
        subprocess.run(args, check=True, env=_env, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    return True


def get_cli_output(commandline_args: str = "") -> str:
    """Helper function to get CLI output as string."""
    args = [sys.executable, "-m", "lib_shopware6_api_base", *commandline_args.split()]
    result = subprocess.run(args, env=_env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (result.stdout or "") + (result.stderr or "")


# =============================================================================
# TestCLI - 5 tests
# =============================================================================


class TestCLI:
    """Tests for CLI commands."""

    @pytest.mark.os_agnostic
    def test_cli_unknown_option_fails(self) -> None:
        """Test CLI fails with unknown option."""
        assert not call_cli_command("--unknown_option")

    @pytest.mark.os_agnostic
    def test_cli_version_succeeds(self) -> None:
        """Test CLI --version option succeeds."""
        assert call_cli_command("--version")

    @pytest.mark.os_agnostic
    def test_cli_help_succeeds(self) -> None:
        """Test CLI -h option succeeds."""
        assert call_cli_command("-h")

    @pytest.mark.os_agnostic
    def test_cli_info_command_succeeds(self) -> None:
        """Test CLI info command succeeds."""
        assert call_cli_command("info")

    @pytest.mark.os_agnostic
    def test_cli_traceback_info_succeeds(self) -> None:
        """Test CLI --traceback info command succeeds."""
        assert call_cli_command("--traceback info")


# =============================================================================
# TestCLIIntegration - 3 tests
# =============================================================================


class TestCLIIntegration:
    """Integration tests for CLI using Click's CliRunner."""

    @pytest.mark.os_agnostic
    def test_cli_version_output(self) -> None:
        """Test CLI version output contains expected information."""
        output = get_cli_output("--version")
        # Accept either underscore or dash variant of the package name
        assert "lib_shopware6_api_base" in output or "lib-shopware6-api-base" in output
        assert "version" in output.lower()

    @pytest.mark.os_agnostic
    def test_cli_help_output_contains_commands(self) -> None:
        """Test CLI help output contains expected commands."""
        output = get_cli_output("-h")
        assert "info" in output.lower()
        # Help should show available commands
        assert "Options" in output or "options" in output.lower()

    @pytest.mark.os_agnostic
    def test_cli_info_output(self) -> None:
        """Test CLI info command output."""
        output = get_cli_output("info")
        # The info command should print package information
        assert "Info" in output or "lib_shopware6_api_base" in output


# =============================================================================
# TestCLIClickRunner - Additional tests using Click's CliRunner directly
# =============================================================================


class TestCLIClickRunner:
    """Tests using Click's CliRunner for more detailed CLI testing."""

    @pytest.mark.os_agnostic
    def test_cli_main_with_click_runner(self) -> None:
        """Test CLI main command using CliRunner."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        runner = CliRunner()
        result = runner.invoke(cli_main, ["--help"])
        assert result.exit_code == 0
        assert "info" in result.output.lower()

    @pytest.mark.os_agnostic
    def test_cli_info_with_click_runner(self) -> None:
        """Test CLI info command using CliRunner."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        runner = CliRunner()
        result = runner.invoke(cli_main, ["info"])
        assert result.exit_code == 0

    @pytest.mark.os_agnostic
    def test_cli_traceback_flag(self) -> None:
        """Test CLI --traceback flag is accepted."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        runner = CliRunner()
        result = runner.invoke(cli_main, ["--traceback", "info"])
        assert result.exit_code == 0

    @pytest.mark.os_agnostic
    def test_cli_no_traceback_flag(self) -> None:
        """Test CLI --no-traceback flag is accepted."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        runner = CliRunner()
        result = runner.invoke(cli_main, ["--no-traceback", "info"])
        assert result.exit_code == 0


# =============================================================================
# TestInfoFunction
# =============================================================================


class TestInfoFunction:
    """Tests for the info() function directly."""

    @pytest.mark.os_agnostic
    def test_info_function_runs_without_error(self) -> None:
        """Test info() function executes without error."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import info

        # Should not raise any exception
        info()


# =============================================================================
# TestExitCodeMapping - Tests for _get_exit_code function
# =============================================================================


class TestExitCodeMapping:
    """Tests for _get_exit_code exception mapping function."""

    @pytest.mark.os_agnostic
    def test_configuration_error_returns_configuration_exit_code(self) -> None:
        """Test ConfigurationError maps to CONFIGURATION_ERROR exit code."""
        from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfigurationError
        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = ConfigurationError("test config error")
        assert _get_exit_code(exc) == ExitCode.CONFIGURATION_ERROR

    @pytest.mark.os_agnostic
    def test_shopware_api_error_returns_api_exit_code(self) -> None:
        """Test ShopwareAPIError maps to API_ERROR exit code."""
        from lib_shopware6_api_base.conf_shopware6_api_base_classes import ShopwareAPIError
        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = ShopwareAPIError("test API error")
        assert _get_exit_code(exc) == ExitCode.API_ERROR

    @pytest.mark.os_agnostic
    def test_value_error_returns_invalid_argument_exit_code(self) -> None:
        """Test ValueError maps to INVALID_ARGUMENT exit code."""
        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = ValueError("invalid value")
        assert _get_exit_code(exc) == ExitCode.INVALID_ARGUMENT

    @pytest.mark.os_agnostic
    def test_broken_pipe_error_returns_sigpipe_exit_code(self) -> None:
        """Test BrokenPipeError maps to SIGPIPE exit code."""
        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = BrokenPipeError("pipe broken")
        assert _get_exit_code(exc) == ExitCode.SIGPIPE

    @pytest.mark.os_agnostic
    def test_sigint_interrupt_returns_sigint_exit_code(self) -> None:
        """Test SigIntInterrupt maps to SIGINT exit code."""
        import lib_cli_exit_tools

        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = lib_cli_exit_tools.SigIntInterrupt()
        assert _get_exit_code(exc) == ExitCode.SIGINT

    @pytest.mark.os_agnostic
    def test_sigterm_interrupt_returns_sigterm_exit_code(self) -> None:
        """Test SigTermInterrupt maps to SIGTERM exit code."""
        import lib_cli_exit_tools

        from lib_shopware6_api_base.exit_codes import ExitCode
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = lib_cli_exit_tools.SigTermInterrupt()
        assert _get_exit_code(exc) == ExitCode.SIGTERM

    @pytest.mark.os_agnostic
    def test_generic_exception_delegates_to_lib_cli_exit_tools(self) -> None:
        """Test generic exceptions are delegated to lib_cli_exit_tools."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _get_exit_code

        exc = RuntimeError("generic error")
        exit_code = _get_exit_code(exc)
        # lib_cli_exit_tools returns 1 for generic exceptions
        assert exit_code == 1


# Keep the original test for backward compatibility
def test_cli_commands() -> None:
    """Original test function for CLI commands."""
    assert not call_cli_command("--unknown_option")
    assert call_cli_command("--version")
    assert call_cli_command("-h")
    assert call_cli_command("info")
    assert call_cli_command("--traceback info")


# =============================================================================
# Config / test-connection / get commands
# =============================================================================


class TestCommandHelpers:
    """Unit tests for the pure helpers behind the config commands."""

    @pytest.mark.os_agnostic
    def test_mask_section_masks_secrets(self) -> None:
        """Secret-ish keys are masked; non-secret keys pass through."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _mask_section

        masked = _mask_section(
            {
                "username": "admin",
                "admin_api_url": "http://shop/api",
                "password": "sekret",
                "client_id": "ci",
                "client_secret": "cs",
                "store_api_sw_access_key": "ak",
            }
        )
        assert masked["username"] == "admin"
        assert masked["admin_api_url"] == "http://shop/api"
        assert masked["password"] != "sekret"
        assert masked["client_id"] != "ci"
        assert masked["client_secret"] != "cs"
        assert masked["store_api_sw_access_key"] != "ak"

    @pytest.mark.os_agnostic
    def test_mask_section_keeps_empty_values(self) -> None:
        """An empty secret stays empty (nothing to hide)."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _mask_section

        assert _mask_section({"password": ""})["password"] == ""

    @pytest.mark.os_agnostic
    def test_config_locations_cover_app_host_user(self) -> None:
        """All three lib_layered_config layers are reported; app/user are config.toml, host is under hosts/."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import _config_locations

        locations = dict(_config_locations())
        assert {"app", "host", "user"} <= set(locations)
        assert locations["app"].name == "config.toml"
        assert locations["user"].name == "config.toml"
        assert locations["host"].parent.name == "hosts"


class TestConfigCommands:
    """CliRunner tests for the config sub-commands (no network)."""

    @pytest.mark.os_agnostic
    def test_config_paths_succeeds(self) -> None:
        """`config paths` lists the bundled default and the slug-based locations."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        result = CliRunner().invoke(cli_main, ["config", "paths"])
        assert result.exit_code == 0
        assert "bundled" in result.output
        assert "lib-shopware6-api-base" in result.output

    @pytest.mark.os_agnostic
    def test_config_show_emits_json(self) -> None:
        """`config show` prints a JSON object with the requested section."""
        import json

        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        result = CliRunner().invoke(cli_main, ["config", "show", "--section", "shopware"])
        assert result.exit_code == 0
        assert "shopware" in json.loads(result.output)

    @pytest.mark.os_agnostic
    def test_new_commands_are_registered(self) -> None:
        """The new commands show up in --help."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        output = CliRunner().invoke(cli_main, ["-h"]).output.lower()
        assert "test-connection" in output
        assert "config" in output
        assert "get" in output

    @pytest.mark.os_agnostic
    def test_get_command_help_succeeds(self) -> None:
        """`get -h` is reachable."""
        from lib_shopware6_api_base.lib_shopware6_api_base_cli import cli_main

        result = CliRunner().invoke(cli_main, ["get", "-h"])
        assert result.exit_code == 0


class TestConnectionCommandsIntegration:
    """test-connection / get against the dockware container (config via env vars)."""

    @staticmethod
    def _dockware_env(config: ConfShopware6ApiBase) -> dict[str, str]:
        prefix = "LIB_SHOPWARE6_API_BASE___SHOPWARE__"
        env = _env.copy()
        env.update(
            {
                prefix + "ADMIN_API_URL": config.shopware_admin_api_url,
                prefix + "STOREFRONT_API_URL": config.shopware_storefront_api_url,
                prefix + "USERNAME": config.username,
                prefix + "PASSWORD": config.password,
                prefix + "CLIENT_ID": config.client_id,
                prefix + "CLIENT_SECRET": config.client_secret,
                prefix + "GRANT_TYPE": config.grant_type.name,
                prefix + "STORE_API_SW_ACCESS_KEY": config.store_api_sw_access_key,
            }
        )
        return env

    @pytest.mark.integration
    def test_test_connection_reports_ok(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """test-connection reaches the Admin and Store APIs on dockware."""
        result = subprocess.run(
            [sys.executable, "-m", "lib_shopware6_api_base", "test-connection"],
            env=self._dockware_env(docker_test_config),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "Admin API  OK" in result.stdout
        assert "Store API  OK" in result.stdout

    @pytest.mark.integration
    def test_get_returns_version(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """get _info/version returns the shop version JSON."""
        result = subprocess.run(
            [sys.executable, "-m", "lib_shopware6_api_base", "get", "_info/version"],
            env=self._dockware_env(docker_test_config),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert '"version"' in result.stdout
