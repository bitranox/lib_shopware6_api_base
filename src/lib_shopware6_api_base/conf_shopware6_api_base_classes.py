# STDLIB
from enum import Enum
from typing import Any

# EXT
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

# PROJ
from .config import get_config

__all__ = [
    "GrantType",
    "HttpMethod",
    "ShopwareAPIError",
    "ConfigurationError",
    "ShopwareApiResponse",
    "ConfShopware6ApiBase",
    "load_config_from_env",
    "require_config_from_env",
]


class GrantType(str, Enum):
    """OAuth2 grant type for Shopware6 API authentication."""

    USER_CREDENTIALS = "user_credentials"
    RESOURCE_OWNER = "resource_owner"


class HttpMethod(str, Enum):
    """HTTP methods supported by the Shopware6 API."""

    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class ShopwareAPIError(Exception):
    """Exception raised for Shopware API errors."""


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""


class ShopwareApiResponse(BaseModel):
    """Typed envelope for a Shopware Admin API response.

    The envelope metadata is typed, while the entity ``data`` stays dynamic
    (``Any``) — the base client is intentionally entity-agnostic, so the actual
    Shopware entity contents are not modelled. Unknown envelope keys (``links``,
    ``included``, ``extensions``, ``meta``, ...) are preserved via ``extra="allow"``.

    Access the records with ``response.data`` (a list for search/list endpoints,
    a dict for single-entity GETs, ``None`` for empty 204 responses).
    """

    model_config = ConfigDict(extra="allow")

    #: Entity records — list[dict] for search/list, dict for a single GET, or None.
    data: Any = None
    #: Total record count reported by search endpoints.
    total: int | None = None
    #: Aggregation results, when requested via the Criteria (Shopware returns a dict, or
    #: an empty list when there are none) — left dynamic.
    aggregations: Any = None
    #: Error entries returned on a failed request.
    errors: Any = None


class ConfShopware6ApiBase(BaseModel):
    """Configuration for a Shopware6 API connection.

    The values are loaded through ``lib_layered_config`` from the ``[shopware]``
    section (bundled defaults -> app -> host -> user -> ``.env`` -> environment),
    but the model may also be instantiated directly with keyword arguments.

    Environment variables use the ``lib_layered_config`` scheme, e.g.::

        LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL=https://shop.example.com/api

    or, inside a ``.env`` file (no slug prefix)::

        SHOPWARE__ADMIN_API_URL=https://shop.example.com/api
    """

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True, extra="ignore")

    # API Endpoints (TOML keys drop the redundant ``shopware_`` prefix).
    shopware_admin_api_url: str = Field(default="", validation_alias=AliasChoices("admin_api_url", "shopware_admin_api_url"))
    shopware_storefront_api_url: str = Field(
        default="", validation_alias=AliasChoices("storefront_api_url", "shopware_storefront_api_url")
    )

    # User-Credentials grant (with refresh token).
    username: str = ""
    password: str = ""

    # Resource-Owner / Integration grant (no refresh token).
    client_id: str = ""
    client_secret: str = ""

    # Grant type selection.
    grant_type: GrantType = GrantType.USER_CREDENTIALS

    # Storefront API access key.
    store_api_sw_access_key: str = ""

    # Allow plain HTTP (development only); "1" enables it.
    insecure_transport: str = "0"

    # Follow HTTP redirects (may expose auth tokens to redirect targets).
    follow_redirects: bool = False

    # Emit debug logging of all HTTP requests/responses (may expose secrets).
    enable_request_logging: bool = False

    @field_validator("grant_type", mode="before")
    @classmethod
    def parse_grant_type(cls, v: str | GrantType) -> GrantType:
        """Parse grant_type from a string ("USER_CREDENTIALS"/"user_credentials") or enum."""
        if isinstance(v, GrantType):
            return v
        v_upper = v.upper()
        if v_upper in ("USER_CREDENTIALS", "RESOURCE_OWNER"):
            return GrantType(v.lower())
        try:
            return GrantType(v.lower())
        except ValueError:
            pass
        raise ValueError(f"Invalid grant_type: {v!r}. Must be 'USER_CREDENTIALS' or 'RESOURCE_OWNER'")


def _load_shopware_section() -> dict[str, Any]:
    """Return the merged ``[shopware]`` configuration section as a plain dict."""
    raw: Any = get_config().get("shopware", default={})
    return dict(raw) if raw else {}


def load_config_from_env() -> ConfShopware6ApiBase:
    """Load the Shopware configuration via ``lib_layered_config``.

    Reads the ``[shopware]`` section merged across all configuration layers
    (bundled defaults, app/host/user config files, ``.env``, environment).

    Returns:
        ConfShopware6ApiBase: the loaded configuration (fields default to empty
        when nothing is configured).
    """
    return ConfShopware6ApiBase(**_load_shopware_section())


def require_config_from_env() -> ConfShopware6ApiBase:
    """Load the configuration, raising if no Shopware endpoint is configured.

    Raises:
        ConfigurationError: if neither the admin nor the storefront API URL is set.
    """
    config = load_config_from_env()
    if not (config.shopware_admin_api_url or config.shopware_storefront_api_url):
        raise ConfigurationError(
            "No Shopware configuration found.\n\n"
            "Provide a [shopware] section via a config file, a .env file, or environment\n"
            "variables (e.g. LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL=...).\n"
            "See example.env / the README for the full list of settings."
        )
    return config
