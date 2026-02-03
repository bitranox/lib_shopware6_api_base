"""CLI for lib_shopware6_api_base."""

# STDLIB
import sys

# OWN
import lib_cli_exit_tools

# EXT
import rich_click as click

# PROJ
from . import __init__conf__
from .conf_shopware6_api_base_classes import ConfigurationError, ShopwareAPIError
from .exit_codes import ExitCode

# CONSTANTS
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _get_exit_code(exc: BaseException) -> int:
    """Map exceptions to exit codes.

    Custom exceptions get specific exit codes.
    Standard exceptions are delegated to lib_cli_exit_tools.
    """
    if isinstance(exc, ConfigurationError):
        return ExitCode.CONFIGURATION_ERROR
    if isinstance(exc, ShopwareAPIError):
        return ExitCode.API_ERROR
    if isinstance(exc, lib_cli_exit_tools.SigIntInterrupt):
        return ExitCode.SIGINT
    if isinstance(exc, lib_cli_exit_tools.SigTermInterrupt):
        return ExitCode.SIGTERM
    if isinstance(exc, BrokenPipeError):
        return ExitCode.SIGPIPE
    if isinstance(exc, ValueError):
        return ExitCode.INVALID_ARGUMENT
    # Delegate to lib_cli_exit_tools for standard exceptions
    return lib_cli_exit_tools.get_system_exit_code(exc)


def info() -> None:
    """
    >>> info()
    Info for ...

    """
    __init__conf__.print_info()


@click.group(help=__init__conf__.title, context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
@click.version_option(
    version=__init__conf__.version,
    prog_name=__init__conf__.shell_command,
    message=f"{__init__conf__.shell_command} version {__init__conf__.version}",
)
@click.option("--traceback/--no-traceback", is_flag=True, type=bool, default=None, help="return traceback information on cli")
def cli_main(traceback: bool | None = None) -> None:
    """Main CLI entry point."""
    if traceback is not None:
        lib_cli_exit_tools.config.traceback = traceback


@cli_main.command("info", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
def cli_info() -> None:
    """Get program information."""
    info()


def main() -> int:
    """Entry point with proper signal handling."""
    return lib_cli_exit_tools.run_cli(
        cli_main,
        exception_handler=_get_exit_code,
        install_signals=True,
    )


# entry point if main
if __name__ == "__main__":
    sys.exit(main())
