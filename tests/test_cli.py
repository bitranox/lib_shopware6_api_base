"""Comprehensive tests for CLI functionality in lib_shopware6_api_base_cli.py."""

from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import sys

import pytest
from click.testing import CliRunner

logger = logging.getLogger()
os.environ["PYTEST_IS_RUNNING"] = "True"  # to be able to detect pytest when running the cli command

# Set PYTHONPATH for subprocess calls to find the src layout package
_src_path = pathlib.Path(__file__).resolve().parent.parent / "src"
_env = os.environ.copy()
_env["PYTHONPATH"] = str(_src_path) + os.pathsep + _env.get("PYTHONPATH", "")


def call_cli_command(commandline_args: str = "") -> bool:
    """Helper function to call CLI commands via subprocess."""
    args = [sys.executable, "-m", "lib_shopware6_api_base"] + commandline_args.split()
    try:
        subprocess.run(args, check=True, env=_env, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    return True


def get_cli_output(commandline_args: str = "") -> str:
    """Helper function to get CLI output as string."""
    args = [sys.executable, "-m", "lib_shopware6_api_base"] + commandline_args.split()
    result = subprocess.run(args, env=_env, capture_output=True, text=True)
    return result.stdout + result.stderr


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


# Keep the original test for backward compatibility
def test_cli_commands() -> None:
    """Original test function for CLI commands."""
    assert not call_cli_command("--unknown_option")
    assert call_cli_command("--version")
    assert call_cli_command("-h")
    assert call_cli_command("info")
    assert call_cli_command("--traceback info")
