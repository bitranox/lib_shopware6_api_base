"""Entry point for `python -m lib_shopware6_api_base`."""

import sys

import lib_cli_exit_tools

from .lib_shopware6_api_base_cli import cli_main

if __name__ == "__main__":
    try:
        cli_main()
    except Exception as exc:
        lib_cli_exit_tools.print_exception_message()
        sys.exit(lib_cli_exit_tools.get_system_exit_code(exc))
    finally:
        lib_cli_exit_tools.flush_streams()
