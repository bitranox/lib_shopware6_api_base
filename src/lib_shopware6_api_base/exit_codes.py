"""Exit codes for the CLI application.

Exit codes follow UNIX conventions:
- 0: Success
- 1-127: Application errors
- 128+N: Signal N received (e.g., 130 = 128 + SIGINT(2))
"""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for lib_shopware6_api_base CLI."""

    SUCCESS = 0
    GENERIC_ERROR = 1
    CONFIGURATION_ERROR = 2
    API_ERROR = 3
    INVALID_ARGUMENT = 22  # EINVAL

    # Signal-based exit codes (128 + signal number)
    SIGINT = 130  # Ctrl+C (128 + 2)
    SIGPIPE = 141  # Broken pipe (128 + 13)
    SIGTERM = 143  # Terminated (128 + 15)
