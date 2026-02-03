# STDLIB
import sys

# OWN
import lib_cli_exit_tools

# EXT
import rich_click as click

# PROJ
from . import __init__conf__

# CONSTANTS
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


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
@click.option(
    "--traceback/--no-traceback", is_flag=True, type=bool, default=None, help="return traceback information on cli"
)
def cli_main(traceback: bool | None = None) -> None:
    if traceback is not None:
        lib_cli_exit_tools.config.traceback = traceback


@cli_main.command("info", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
def cli_info() -> None:
    """get program information"""
    info()


# entry point if main
if __name__ == "__main__":
    try:
        cli_main()  # type: ignore
    except Exception as exc:
        lib_cli_exit_tools.print_exception_message()
        sys.exit(lib_cli_exit_tools.get_system_exit_code(exc))
    finally:
        lib_cli_exit_tools.flush_streams()
