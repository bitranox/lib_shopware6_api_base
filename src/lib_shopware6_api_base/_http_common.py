# STDLIB
import json
import logging
import re
from typing import Any
from urllib.parse import urljoin

# EXT
import httpx

from .conf_shopware6_api_base_classes import ShopwareAPIError
from .lib_shopware6_api_base_criteria import Criteria

logger = logging.getLogger(__name__)

# Regex pattern for valid URL path characters (alphanumeric, hyphen, underscore, slash, dot)
# This prevents path traversal and other injection attacks
_VALID_ENDPOINT_PATTERN = re.compile(r"^[a-zA-Z0-9\-_./]+$")

__all__ = [
    # Constants
    "DEFAULT_REQUEST_TIMEOUT",
    "MAX_RETRY_ATTEMPTS",
    "CONTENT_TYPE_JSON",
    "HEADER_SW_ACCESS_KEY",
    "HEADER_SINGLE_OPERATION",
    "REQUEST_TIMEOUT",
    # Header constants
    "HEADER_write_in_separate_transactions",
    "HEADER_write_in_single_transactions",
    "HEADER_index_synchronously",
    "HEADER_index_asynchronously",
    "HEADER_index_disabled",
    "HEADER_fail_on_error",
    "HEADER_do_not_fail_on_error",
    # Type alias
    "PayLoad",
    # Utilities
    "is_type_bytes",
    "is_type_criteria",
    "get_payload_dict",
    "log_request",
    "log_response",
    "validate_endpoint",
    "build_api_url",
]

# Module-level constants for HTTP settings
DEFAULT_REQUEST_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
MAX_RETRY_ATTEMPTS = 2
CONTENT_TYPE_JSON = "json"
HEADER_SW_ACCESS_KEY = "sw-access-key"
HEADER_SINGLE_OPERATION = "single-operation"

# Legacy alias for backward compatibility
REQUEST_TIMEOUT = DEFAULT_REQUEST_TIMEOUT

PayLoad = dict[str, Any] | Criteria | None

# Endpoints like /api/_action/sync require request specific custom headers to manipulate the api behavior
# see : https://shopware.stoplight.io/docs/admin-api/faf8f8e4e13a0-bulk-payloads#performance
# see : https://shopware.stoplight.io/docs/admin-api/0612cb5d960ef-bulk-edit-entities
# You may pass such custom header fields like that :
#       only for python version >= 3.8 :
#      update_header_fields = HEADER_write_in_single_transactions | HEADER_index_asynchronously  # noqa: ERA001
#   or the same written explicitly for python 3.7 :
#      update_heater_fields = {'single-operation': 'true', 'indexing-behavior': 'use-queue-indexing'}  # noqa: ERA001
#   and pass those "update_heater_fields" to the request method (mostly request_post, with "/api/_action/sync")
HEADER_write_in_separate_transactions: dict[str, str] = {"single-operation": "false"}  # default
HEADER_write_in_single_transactions: dict[str, str] = {"single-operation": "true"}
HEADER_index_synchronously: dict[str, str] = {"indexing-behavior": "null"}  # default
HEADER_index_asynchronously: dict[str, str] = {"indexing-behavior": "use-queue-indexing"}
HEADER_index_disabled: dict[str, str] = {"indexing-behavior": "disable-indexing"}
HEADER_fail_on_error: dict[str, str] = {"fail-on-error": "true"}  # default
HEADER_do_not_fail_on_error: dict[str, str] = {"fail-on-error": "false"}


def is_type_bytes(payload: Any) -> bool:
    """True if the passed type is bytes"""
    return isinstance(payload, bytes)


def is_type_criteria(payload: Any) -> bool:
    """True if the passed type is Criteria"""
    return isinstance(payload, Criteria)


def get_payload_dict(payload: PayLoad) -> dict[str, Any]:
    """Return the payload as dictionary"""
    if payload is None:
        payload = {}
    elif is_type_criteria(payload):
        payload = payload.get_dict()  # type: ignore
    return payload  # type: ignore


def handle_json_decode_error(response: httpx.Response) -> dict[str, Any]:
    """Safely decode JSON response, returning empty dict on failure."""
    try:
        return dict(response.json())
    except (json.JSONDecodeError, ValueError) as exc:
        logger.debug("Failed to decode JSON response: %s", exc)
        return {}


def handle_http_error(exc: httpx.HTTPStatusError) -> None:
    """Convert HTTP status errors to ShopwareAPIError with detailed message."""
    detailed_error = f" : {exc.response.text}"
    raise ShopwareAPIError(f"{exc}{detailed_error}") from exc


def log_request(request: httpx.Request) -> None:
    """Log outgoing HTTP request for debugging."""
    logger.debug("Request: %s %s", request.method, request.url)


def log_response(response: httpx.Response) -> None:
    """Log incoming HTTP response for debugging."""
    logger.debug("Response: %s %s", response.status_code, response.url)


def validate_endpoint(endpoint: str) -> str:
    """
    Validate and sanitize an API endpoint path.

    Args:
        endpoint: The endpoint path to validate (e.g., "product", "oauth/token")

    Returns:
        The sanitized endpoint with leading slash removed

    Raises:
        ShopwareAPIError: If the endpoint contains invalid characters

    Examples:
        >>> validate_endpoint("product")
        'product'
        >>> validate_endpoint("/oauth/token")
        'oauth/token'
        >>> validate_endpoint("product/../../../etc/passwd")
        Traceback (most recent call last):
            ...
        ShopwareAPIError: Invalid endpoint path: contains '..' path traversal

    """
    # Strip leading/trailing whitespace and leading slash
    endpoint = endpoint.strip().lstrip("/")

    # Check for empty endpoint
    if not endpoint:
        raise ShopwareAPIError("Invalid endpoint path: endpoint cannot be empty")

    # Check for path traversal attempts
    if ".." in endpoint:
        raise ShopwareAPIError("Invalid endpoint path: contains '..' path traversal")

    # Check for valid characters
    if not _VALID_ENDPOINT_PATTERN.match(endpoint):
        raise ShopwareAPIError(
            f"Invalid endpoint path: '{endpoint}' contains invalid characters. "
            "Only alphanumeric characters, hyphens, underscores, dots, and slashes are allowed."
        )

    return endpoint


def build_api_url(base_url: str, endpoint: str) -> str:
    """
    Safely construct an API URL from a base URL and endpoint.

    Args:
        base_url: The base API URL (e.g., "https://shop.example.com/api")
        endpoint: The endpoint path (e.g., "product", "oauth/token")

    Returns:
        The full URL

    Raises:
        ShopwareAPIError: If the endpoint is invalid

    Examples:
        >>> build_api_url("https://shop.example.com/api", "product")
        'https://shop.example.com/api/product'
        >>> build_api_url("https://shop.example.com/api/", "/oauth/token")
        'https://shop.example.com/api/oauth/token'

    """
    validated_endpoint = validate_endpoint(endpoint)

    # Ensure base_url ends with a slash for proper urljoin behavior
    if not base_url.endswith("/"):
        base_url = base_url + "/"

    return urljoin(base_url, validated_endpoint)
