"""CLI for lib_shopware6_api_base."""

# STDLIB
import json
import os
import platform
import socket
import sys
from pathlib import Path
from typing import Any

# OWN
import lib_cli_exit_tools

# EXT
import rich_click as click
from lib_layered_config import is_sensitive

# PROJ
from . import __init__conf__
from .conf_shopware6_api_base_classes import ConfigurationError, ShopwareAPIError, require_config_from_env
from .config import get_config, get_default_config_path
from .exit_codes import ExitCode
from .lib_shopware6_admin_client import Shopware6AdminAPIClientBase
from .lib_shopware6_storefront_client import Shopware6StoreFrontClientBase
from .logging_setup import init_logging, shutdown_logging

# CONSTANTS
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

# Connection-test endpoint: returns {"version": "6.x.y.z", ...} on any reachable shop.
_VERSION_ENDPOINT = "_info/version"

# Secret values are masked in `config show`. lib_layered_config flags most of them
# (password, client_secret); the Store access key and the OAuth client_id are
# credential material it does not catch, so they are masked explicitly.
_MASK = "***REDACTED***"
_EXTRA_SENSITIVE_KEYS = frozenset({"store_api_sw_access_key", "client_id"})


def _get_exit_code(exc: BaseException) -> int:
    """Map exceptions to exit codes, printing the diagnostic the user needs to see.

    run_cli installs this in place of its default exception handler, so it must also
    emit the message the default would have printed - otherwise every error exits with
    a bare code and no output. Signals exit cleanly and quietly (no traceback); all
    other errors print the message (terse, or a full traceback when --traceback is set)
    before the mapped exit code is returned.
    """
    if isinstance(exc, lib_cli_exit_tools.SigIntInterrupt):
        return ExitCode.SIGINT
    if isinstance(exc, lib_cli_exit_tools.SigTermInterrupt):
        return ExitCode.SIGTERM
    if isinstance(exc, BrokenPipeError):
        return ExitCode.SIGPIPE
    lib_cli_exit_tools.print_exception_message()
    if isinstance(exc, ConfigurationError):
        return ExitCode.CONFIGURATION_ERROR
    if isinstance(exc, ShopwareAPIError):
        return ExitCode.API_ERROR
    if isinstance(exc, ValueError):
        return ExitCode.INVALID_ARGUMENT
    # Delegate to lib_cli_exit_tools for standard exceptions
    return lib_cli_exit_tools.get_system_exit_code(exc)


def _mask_section(section: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a config section with non-empty secret values masked."""
    masked: dict[str, Any] = {}
    for key, value in section.items():
        secret = is_sensitive(key) or key in _EXTRA_SENSITIVE_KEYS
        masked[key] = _MASK if secret and value not in ("", None) else value
    return masked


def _config_locations() -> list[tuple[str, Path]]:
    """Return the (layer, file) lookup locations for the current platform.

    Covers the app, host, and user layers that lib_layered_config resolves; the app
    and user directories also take a ``config.d/`` of split files merged in filename
    order, and the host layer is a per-hostname file under ``hosts/``.
    """
    vendor = __init__conf__.LAYEREDCONF_VENDOR
    app = __init__conf__.LAYEREDCONF_APP
    slug = __init__conf__.LAYEREDCONF_SLUG
    hostname = socket.gethostname()
    system = platform.system()
    if system == "Windows":
        system_base = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / vendor / app
        user_base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / vendor / app
    elif system == "Darwin":
        system_base = Path("/Library/Application Support") / vendor / app
        user_base = Path.home() / "Library" / "Application Support" / vendor / app
    else:  # Linux / other POSIX (XDG)
        system_base = Path("/etc/xdg") / slug
        user_base = Path.home() / ".config" / slug
    return [
        ("app", system_base / "config.toml"),
        ("host", system_base / "hosts" / f"{hostname}.toml"),
        ("user", user_base / "config.toml"),
    ]


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


@cli_main.command("test-connection", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
@click.option("--storefront/--no-storefront", default=True, help="also verify the Store API access key")
def cli_test_connection(storefront: bool) -> None:
    """Check that the configured credentials can reach Shopware.

    Authenticates against the Admin API (reporting the grant type and shop
    version) and, unless --no-storefront is given, verifies the Store API
    access key. Reads the configuration from the layered config / .env.
    """
    config = require_config_from_env()

    with Shopware6AdminAPIClientBase(config=config) as admin:
        version = admin.request_get(_VERSION_ENDPOINT).model_dump().get("version", "unknown")
    click.echo(f"Admin API  OK    {config.shopware_admin_api_url}  (grant_type={config.grant_type.name}, shopware {version})")

    if not storefront:
        return
    if config.shopware_storefront_api_url and config.store_api_sw_access_key:
        Shopware6StoreFrontClientBase(config=config).request_get("context")
        click.echo(f"Store API  OK    {config.shopware_storefront_api_url}")
    else:
        click.echo("Store API  SKIP  storefront_api_url / store_api_sw_access_key not configured")


@cli_main.command("get", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
@click.argument("endpoint")
def cli_get(endpoint: str) -> None:
    """Run a read-only Admin API GET and print the JSON response.

    ENDPOINT is the path without the /api prefix, e.g. "currency" or
    "_info/version". Authentication is taken from the layered config / .env.
    """
    config = require_config_from_env()
    with Shopware6AdminAPIClientBase(config=config) as client:
        response = client.request_get(endpoint)
    click.echo(json.dumps(response.model_dump(), indent=2, default=str, sort_keys=False))


@cli_main.group("config", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
def cli_config() -> None:
    """Inspect the layered configuration."""


@cli_config.command("show", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
@click.option(
    "--section",
    type=click.Choice(["shopware", "lib_log_rich", "all"]),
    default="all",
    help="which section to print",
)
def cli_config_show(section: str) -> None:
    """Print the effective merged configuration, with secrets masked."""
    config = get_config()
    sections = ["shopware", "lib_log_rich"] if section == "all" else [section]
    out = {name: _mask_section(dict(config.get(name, default={}) or {})) for name in sections}
    click.echo(json.dumps(out, indent=2, default=str, sort_keys=False))


@cli_config.command("paths", context_settings=CLICK_CONTEXT_SETTINGS)  # type: ignore
def cli_config_paths() -> None:
    """Show where configuration is loaded from on this machine.

    Higher layers override lower ones:
    bundled defaults -> app -> host -> user -> .env -> environment.
    """
    default_path = get_default_config_path()
    click.echo(f"bundled    {default_path}  ({'present' if default_path.exists() else 'missing'})")
    for layer, path in _config_locations():
        marker = "present" if path.exists() else "not present"
        click.echo(f"{layer:10s} {path}  ({marker}; + {path.parent / 'config.d'}/*.toml)")
    dotenv = Path.cwd() / ".env"
    click.echo(f"dotenv     {dotenv}  ({'present' if dotenv.exists() else 'not present'})")
    click.echo("env prefix LIB_SHOPWARE6_API_BASE___<SECTION>__<KEY>")


def main() -> int:
    """Entry point with logging setup and proper signal handling."""
    init_logging()
    # cli_main sets the process-global lib_cli_exit_tools.config.traceback from --traceback;
    # snapshot and restore it so the flag does not leak into later in-process invocations.
    traceback_default = lib_cli_exit_tools.config.traceback
    try:
        return lib_cli_exit_tools.run_cli(
            cli_main,
            exception_handler=_get_exit_code,
            install_signals=True,
        )
    finally:
        lib_cli_exit_tools.config.traceback = traceback_default
        shutdown_logging()


# entry point if main
if __name__ == "__main__":
    sys.exit(main())
