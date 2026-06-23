# lib_shopware6_api_base

<!-- Badges -->
[![CI](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/cicd_docker.yml/badge.svg)](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/cicd_docker.yml)
[![CodeQL](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/codeql-analysis.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open in Codespaces](https://img.shields.io/badge/Codespaces-Open-blue?logo=github&logoColor=white&style=flat-square)](https://codespaces.new/bitranox/lib_shopware6_api_base?quickstart=1)
[![PyPI](https://img.shields.io/pypi/v/lib_shopware6_api_base.svg)](https://pypi.org/project/lib_shopware6_api_base/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/lib_shopware6_api_base.svg)](https://pypi.org/project/lib_shopware6_api_base/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-46A3FF?logo=ruff&labelColor=000)](https://docs.astral.sh/ruff/)
[![codecov](https://codecov.io/gh/bitranox/lib_shopware6_api_base/graph/badge.svg?token=UFBaUDIgRk)](https://codecov.io/gh/bitranox/lib_shopware6_api_base)
[![Maintainability](https://qlty.sh/badges/041ba2c1-37d6-40bb-85a0-ec5a8a0aca0c/maintainability.svg)](https://qlty.sh/gh/bitranox/projects/lib_shopware6_api_base)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

`lib_shopware6_api_base` is a thin Python client for Shopware 6's Admin and Store APIs.
It takes care of the fiddly parts - keeping OAuth2 tokens alive, paging through large
result sets, building DAL search queries - and otherwise stays out of your way. If you
want higher-level, entity-aware helpers on top of it, reach for
[lib_shopware6_api](https://github.com/bitranox/lib_shopware6_api).

What it does:

- **Admin API auth that just works.** Both grant types are supported - the password
  grant (for interactive apps that want refresh tokens) and the client-credentials /
  integration grant (for automation). Fetching, refreshing, and expiring tokens is
  handled for you.
- **Store API** authentication via the `sw-access-key`.
- **A typed query builder.** `Criteria` and friends (filters, sorting, aggregations,
  associations, ranking queries) are Pydantic models that mirror Shopware's DAL search
  syntax, so you build queries with real objects instead of hand-rolled dicts.
- **Pagination you don't have to think about.** `request_get_paginated` and
  `request_post_paginated` walk the whole result set for you, a chunk at a time.
- **Typed responses.** Admin API calls hand back a `ShopwareApiResponse` envelope, so
  you read `.data` and `.total` instead of guessing at dict keys.
- **Header constants for bulk operations** - transaction behaviour, indexing mode, and
  fail-on-error are one import away.
- **Configuration through lib_layered_config** (defaults -> app -> host -> user -> .env -> env).
- **Structured logging through lib_log_rich** (wired up by the CLI).
- **Exit codes** handled by lib_cli_exit_tools.
- HTTP/2 over httpx2, JSON over orjson, and a rich-click CLI.
- Runs on Linux, macOS, and Windows; needs **Python 3.10+**.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Clients](#api-clients)
- [Request Methods](#request-methods)
- [Query Syntax (Criteria)](#query-syntax-criteria)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [CLI Usage](#cli-usage)
- [Architecture](#architecture)
- [Development](#development)
- [Further Documentation](#further-documentation)

---

## Installation

**Recommended: install via [uv](https://docs.astral.sh/uv/)** (much faster than pip):

```bash
pip install --upgrade uv
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
uv pip install lib_shopware6_api_base
```

For one-shot runs (`uvx`), CLI-tool installs, pipx, source builds, and system packagers,
see [INSTALL.md](INSTALL.md).

### Python 3.10+ Baseline

- The project targets **Python 3.10 and newer**.
- CI exercises GitHub's rolling runner images across Python 3.10-3.14 on Linux, macOS, and Windows.

---

## Quick Start

```python
from lib_shopware6_api_base import (
    ConfShopware6ApiBase,
    Shopware6AdminAPIClientBase,
    Criteria,
    EqualsFilter,
)

# Configure directly, or use load_config_from_env() to read .env / environment
config = ConfShopware6ApiBase(
    shopware_admin_api_url="https://shop.example.com/api",
    username="admin",
    password="secret",
)

client = Shopware6AdminAPIClientBase(config=config)

# Fetch all active products (auto-pagination), then read the typed envelope
criteria = Criteria(filter=[EqualsFilter(field="active", value=True)])
response = client.request_post_paginated("search/product", payload=criteria)

print(f"{response.total} products")
for product in response.data:
    print(product["name"])
```

---

## Configuration

Configuration is the `ConfShopware6ApiBase` Pydantic model, loaded through
[`lib_layered_config`](https://github.com/bitranox/lib_layered_config), which merges,
in increasing precedence:

```
bundled defaults  ->  app  ->  host  ->  user  ->  .env  ->  environment variables
```

You can also instantiate `ConfShopware6ApiBase(...)` directly with keyword arguments.

Configuration is **read once**: the merged config is loaded on first use and cached for
the process lifetime, so it is treated as static. After changing env vars, a `.env` file,
or a config file, restart (or reload) the process to pick up the new values.

> **⚠️ Breaking change in 4.0.0 - env vars renamed.** Configuration moved to
> `lib_layered_config`, so the old single-underscore `SHOPWARE_*` variables are **no
> longer read**. Rename them to the `[shopware]` section form:
>
> | Old (<= 3.x)                  | New - `.env` file              | New - environment variable                              |
> |-------------------------------|--------------------------------|---------------------------------------------------------|
> | `SHOPWARE_ADMIN_API_URL`      | `SHOPWARE__ADMIN_API_URL`      | `LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL`      |
> | `SHOPWARE_STOREFRONT_API_URL` | `SHOPWARE__STOREFRONT_API_URL` | `LIB_SHOPWARE6_API_BASE___SHOPWARE__STOREFRONT_API_URL` |
> | `SHOPWARE_<NAME>`             | `SHOPWARE__<NAME>`             | `LIB_SHOPWARE6_API_BASE___SHOPWARE__<NAME>`             |
>
> i.e. in a `.env` file replace the single `_` after `SHOPWARE` with `__`; as a real
> environment variable also add the `LIB_SHOPWARE6_API_BASE___` slug prefix.

### Configuration files (TOML)

The package ships its own defaults as the lowest layer: `defaultconfig.toml` plus the
files in `defaultconfig.d/` (`10-logging.toml`, `20-shopware.toml`). You don't edit those
- they live inside the installed package - you override them at a higher layer. Call
`get_default_config_path()` if you want to read the bundled file to see every key.

Each layer overrides the one before it, so you set only the keys you care about:

```
bundled defaults  ->  app (system-wide)  ->  host  ->  user  ->  .env  ->  environment
```

A config file uses the same two sections as the bundled defaults, `[shopware]` and
`[lib_log_rich]`:

```toml
# config.toml
[shopware]
admin_api_url = "https://shop.example.com/api"
username = "admin@example.com"
password = "your-password"
grant_type = "USER_CREDENTIALS"

[lib_log_rich]
console_level = "DEBUG"
environment = "staging"
```

Where each layer's file lives (app `bitranox` / `Lib Shopware6 Api Base`, slug
`lib-shopware6-api-base`):

| Layer             | Linux                                                   | macOS                                                                       | Windows                                                      |
|-------------------|---------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------|
| app (system-wide) | `/etc/xdg/lib-shopware6-api-base/config.toml`           | `/Library/Application Support/bitranox/Lib Shopware6 Api Base/config.toml`  | `C:\ProgramData\bitranox\Lib Shopware6 Api Base\config.toml` |
| host              | `/etc/xdg/lib-shopware6-api-base/hosts/<hostname>.toml` | same dir, `hosts/<hostname>.toml`                                           | same dir, `hosts\<hostname>.toml`                            |
| user              | `~/.config/lib-shopware6-api-base/config.toml`          | `~/Library/Application Support/bitranox/Lib Shopware6 Api Base/config.toml` | `%APPDATA%\bitranox\Lib Shopware6 Api Base\config.toml`      |

You can split any layer into several files with the `.d` pattern: drop
`config.d/10-shopware.toml`, `config.d/20-logging.toml`, and so on next to `config.toml`,
and they are merged in filename order (this is exactly how the package ships its own
defaults). On Linux, `/etc/<slug>/` is also checked when `/etc/xdg/<slug>/` is absent.

### Environment file (.env)

Copy `example.env` to `.env` and adjust the values for your shop:

```bash
# API endpoints
SHOPWARE__ADMIN_API_URL="https://shop.example.com/api"
SHOPWARE__STOREFRONT_API_URL="https://shop.example.com/store-api"

# User-credentials grant (interactive apps, with refresh tokens)
SHOPWARE__USERNAME="admin@example.com"
SHOPWARE__PASSWORD="your-password"

# Resource-owner / integration grant (automation, no refresh tokens)
SHOPWARE__CLIENT_ID="SWIAXXXXXXXXXXXXXXXXXXXX"
SHOPWARE__CLIENT_SECRET="your-integration-secret"

# Grant type: USER_CREDENTIALS or RESOURCE_OWNER
SHOPWARE__GRANT_TYPE="RESOURCE_OWNER"

# Store API access key (from Sales Channel settings)
SHOPWARE__STORE_API_SW_ACCESS_KEY="SWSCXXXXXXXXXXXXXXXXXX"
```

#### `[shopware]` settings reference

In a `.env` file use the `SHOPWARE__<KEY>` form; as a real environment variable prefix
with `LIB_SHOPWARE6_API_BASE___`. The same keys can be set in a TOML config file under
`[shopware]` (dropping the `SHOPWARE__` prefix).

| `.env` key                          | Description           | Example                                |
|-------------------------------------|-----------------------|----------------------------------------|
| `SHOPWARE__ADMIN_API_URL`           | Admin API endpoint    | `https://shop.example.com/api`         |
| `SHOPWARE__STOREFRONT_API_URL`      | Store API endpoint    | `https://shop.example.com/store-api`   |
| `SHOPWARE__USERNAME`                | Admin user name       | `admin@example.com`                    |
| `SHOPWARE__PASSWORD`                | Admin user password   | `secret`                               |
| `SHOPWARE__CLIENT_ID`               | Integration Access ID | `SWIA...`                              |
| `SHOPWARE__CLIENT_SECRET`           | Integration secret    | `...`                                  |
| `SHOPWARE__GRANT_TYPE`              | Auth method           | `USER_CREDENTIALS` or `RESOURCE_OWNER` |
| `SHOPWARE__STORE_API_SW_ACCESS_KEY` | Store API access key  | `SWSC...`                              |

### Loading configuration

```python
from lib_shopware6_api_base import (
    ConfShopware6ApiBase,
    load_config_from_env,
    require_config_from_env,
    Shopware6AdminAPIClientBase,
)

# Load from the layered sources (defaults -> app -> host -> user -> .env -> environment)
config = load_config_from_env()

# Same, but raise ConfigurationError if no Admin/Store API URL is configured
config = require_config_from_env()

# Or instantiate directly
config = ConfShopware6ApiBase(
    shopware_admin_api_url="https://shop.example.com/api",
    username="admin",
    password="secret",
)

client = Shopware6AdminAPIClientBase(config=config)
```

---

## API Clients

### Admin API

Admin API methods return a `ShopwareApiResponse` envelope - read `.data` (entity payload)
and `.total` (record count).

```python
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria

client = Shopware6AdminAPIClientBase(config=config)

# GET request
response = client.request_get("currency")
print(response.total, response.data)

# GET with pagination (fetches all records in chunks)
response = client.request_get_paginated("product", junk_size=100)

# POST request (search)
criteria = Criteria(limit=10)
response = client.request_post("search/product", payload=criteria)

# POST with pagination
response = client.request_post_paginated("search/order", payload=criteria, junk_size=50)

# PATCH request (update)
client.request_patch("product/abc123", payload={"name": "New Name"})

# PUT request (upsert)
client.request_put("tag/xyz789", payload={"id": "xyz789", "name": "My Tag"})

# DELETE request
client.request_delete("tag/xyz789")
```

### Store API

The Store (Storefront) client authenticates with the `sw-access-key` and returns plain
Python data (no envelope).

```python
from lib_shopware6_api_base import Shopware6StoreFrontClientBase, Criteria

client = Shopware6StoreFrontClientBase(config=config)

# GET request (returns dict)
response = client.request_get("context")

# GET request (returns list)
currencies = client.request_get_list("currency")

# POST request with criteria (returns dict)
criteria = Criteria(limit=5)
products = client.request_post("product", payload=criteria)
```

---

## Request Methods

All request methods accept these parameters:

| Parameter              | Type                       | Description                     |
|------------------------|----------------------------|---------------------------------|
| `request_url`          | `str`                      | API endpoint (without base URL) |
| `payload`              | `dict \| Criteria \| None` | Request body                    |
| `update_header_fields` | `dict[str, str] \| None`   | Custom headers                  |

Admin API write methods also support:

| Parameter                 | Type   | Description                           |
|---------------------------|--------|---------------------------------------|
| `content_type`            | `str`  | Content type (`json`, `octet-stream`) |
| `additional_query_params` | `dict` | URL query parameters                  |

### Custom Headers

For bulk operations, use the predefined header constants:

```python
from lib_shopware6_api_base import (
    HEADER_write_in_single_transactions,    # {"single-operation": "true"}
    HEADER_write_in_separate_transactions,  # {"single-operation": "false"}
    HEADER_index_synchronously,             # {"indexing-behavior": "null"}
    HEADER_index_asynchronously,            # {"indexing-behavior": "use-queue-indexing"}
    HEADER_index_disabled,                  # {"indexing-behavior": "disable-indexing"}
    HEADER_fail_on_error,                   # {"fail-on-error": "true"}
    HEADER_do_not_fail_on_error,            # {"fail-on-error": "false"}
)

# Combine headers
headers = HEADER_write_in_single_transactions | HEADER_index_asynchronously
client.request_post("_action/sync", payload=data, update_header_fields=headers)
```

---

## Query Syntax (Criteria)

The `Criteria` class (Pydantic model) mirrors Shopware's DAL query syntax:

```python
from lib_shopware6_api_base import Criteria, EqualsFilter, AscFieldSorting

criteria = Criteria(
    limit=10,
    page=1,
    filter=[EqualsFilter(field="active", value=True)],
    sort=[AscFieldSorting(field="name")],
)
```

### Filters

```python
from lib_shopware6_api_base import (
    EqualsFilter,
    EqualsAnyFilter,
    ContainsFilter,
    RangeFilter,
    PrefixFilter,
    SuffixFilter,
    NotFilter,
    MultiFilter,
    FilterOperator,
    RangeParam,
)

# Exact match
EqualsFilter(field="stock", value=10)

# Match any of the values
EqualsAnyFilter(field="id", value=["abc", "def"])

# LIKE '%value%'
ContainsFilter(field="name", value="Bronze")

# LIKE 'value%'
PrefixFilter(field="name", value="Pro")

# LIKE '%value'
SuffixFilter(field="sku", value="-XL")

# Range filter
RangeFilter(field="price", parameters={RangeParam.GTE: 10, RangeParam.LTE: 100})
# Or with strings: parameters={"gte": 10, "lte": 100}

# NOT filter
NotFilter(operator="or", queries=[
    EqualsFilter(field="stock", value=0),
    EqualsFilter(field="active", value=False),
])

# Multi filter (combine with AND/OR)
MultiFilter(operator="and", queries=[
    EqualsFilter(field="active", value=True),
    ContainsFilter(field="name", value="Premium"),
])
```

### Sorting

```python
from lib_shopware6_api_base import FieldSorting, AscFieldSorting, DescFieldSorting

# Generic sorting
FieldSorting(field="name", order="ASC", naturalSorting=True)

# Shorthand ascending
AscFieldSorting(field="name", naturalSorting=True)

# Shorthand descending
DescFieldSorting(field="price")
```

### Aggregations

```python
from lib_shopware6_api_base import (
    AvgAggregation,
    CountAggregation,
    MaxAggregation,
    MinAggregation,
    SumAggregation,
    StatsAggregation,
    TermsAggregation,
    FilterAggregation,
    EntityAggregation,
    DateHistogramAggregation,
    EqualsFilter,
)

criteria = Criteria(
    aggregations=[
        AvgAggregation(name="avg-price", field="price"),
        TermsAggregation(name="manufacturers", field="manufacturerId", limit=10),
        FilterAggregation(
            name="active-avg",
            filter=[EqualsFilter(field="active", value=True)],
            aggregation=AvgAggregation(name="price", field="price"),
        ),
    ]
)
```

### Associations

Load related entities:

```python
criteria = Criteria()
criteria.associations["manufacturer"] = Criteria()
criteria.associations["categories"] = Criteria(limit=5)
```

---

## Error Handling

Two exception types cover the things that go wrong - a bad configuration and a bad
response from Shopware:

```python
from lib_shopware6_api_base import (
    ShopwareAPIError,
    ConfigurationError,
    Shopware6AdminAPIClientBase,
    require_config_from_env,
)

# Handle configuration errors
try:
    config = require_config_from_env()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # No Admin/Store API URL configured

# Handle API errors
try:
    client = Shopware6AdminAPIClientBase(config=config)
    response = client.request_get("product/invalid-id")
except ShopwareAPIError as e:
    print(f"API error: {e}")
    # HTTP errors (404, 401, 500, ...)
```

### Exception Types

| Exception            | When Raised                                                         |
|----------------------|---------------------------------------------------------------------|
| `ConfigurationError` | `require_config_from_env()` finds no Admin/Store API URL configured |
| `ShopwareAPIError`   | HTTP errors from the API (4xx, 5xx) and invalid endpoint paths      |

---

## Logging

By default the library does not configure logging. Its modules log through the
standard library (`logging.getLogger(__name__)`), so a plain `import` stays quiet
until your application sets logging up. A `logging.basicConfig(level=logging.INFO)`
is enough to see the records.

To switch on `lib_log_rich` (the rich console output, the `[lib_log_rich]` config
section, journald / Graylog, secret scrubbing) opt in explicitly:

```python
import logging
from lib_shopware6_api_base import init_logging, shutdown_logging

init_logging()       # loads the layered config, applies [lib_log_rich],
                     # and bridges stdlib logging into it
try:
    ...              # use the clients; their records now flow through lib_log_rich
finally:
    shutdown_logging()
```

`init_logging()` is idempotent and reads the same layered configuration as the rest
of the package. The CLI calls it for you, so you only need this when using the
package as a library.

---

## CLI Usage

```
Usage: lib-shopware6-api-base [OPTIONS] COMMAND [ARGS]...

  python3 base API client for shopware6

Options:
  --version                     Show the version and exit.
  --traceback / --no-traceback  return traceback information on cli
  -h, --help                    Show this message and exit.

Commands:
  info             Get program information.
  test-connection  Check that the configured credentials can reach Shopware.
  get              Run a read-only Admin API GET and print the JSON response.
  config           Inspect the layered configuration.
```

The connectivity and inspection commands read the same layered configuration as the
library (see [Configuration](#configuration)):

```bash
# Verify the configured credentials reach the shop (Admin + Store API)
lib-shopware6-api-base test-connection
# Admin API  OK    https://shop.example.com/api  (grant_type=USER_CREDENTIALS, shopware 6.4.7.0)
# Store API  OK    https://shop.example.com/store-api

# A read-only Admin GET, printed as JSON (path without the /api prefix)
lib-shopware6-api-base get _info/version
lib-shopware6-api-base get currency

# See the effective config (secrets masked) and where it is loaded from
lib-shopware6-api-base config show
lib-shopware6-api-base config show --section shopware
lib-shopware6-api-base config paths
```

Both `lib-shopware6-api-base` and `lib_shopware6_api_base` are registered on your PATH.

---

## Architecture

The package is a small, layered library. Imports point inward only - the configuration
layer never imports the clients, and the clients sit above the criteria builder, which
sits above the config:

```
lib_shopware6_api_base/
|-- lib_shopware6_api_base.py            # public facade (re-exports)
|-- lib_shopware6_admin_client.py        # Admin API client (OAuth2, ShopwareApiResponse)
|-- lib_shopware6_storefront_client.py   # Store API client (sw-access-key)
|-- lib_shopware6_api_base_criteria*.py  # Criteria / Filters / Sorting / Aggregations
|-- conf_shopware6_api_base_classes.py   # ConfShopware6ApiBase, enums, exceptions
|-- config.py                            # lib_layered_config loading
|-- logging_setup.py                     # lib_log_rich wiring (CLI only)
|-- _http_common.py                      # shared HTTP helpers, header constants
`-- lib_shopware6_api_base_cli.py        # rich-click CLI
```

**Enforced via import-linter:**

```toml
[[tool.importlinter.contracts]]
name = "Configuration layer is independent"
type = "forbidden"
source_modules = ["lib_shopware6_api_base.conf_shopware6_api_base_classes"]
forbidden_modules = [
    "lib_shopware6_api_base.lib_shopware6_api_base",
    "lib_shopware6_api_base.lib_shopware6_storefront_client",
    "lib_shopware6_api_base.lib_shopware6_admin_client",
]

[[tool.importlinter.contracts]]
name = "Clean Architecture layers"
type = "layers"
layers = [
    "lib_shopware6_api_base.lib_shopware6_api_base",
    "lib_shopware6_api_base.lib_shopware6_api_base_criteria",
    "lib_shopware6_api_base.conf_shopware6_api_base_classes",
]
```

---

## Development

Project automation runs through a `Makefile` that delegates to [`bmk`](https://pypi.org/project/bmk/)
(installed automatically as a persistent `uv` tool on first use). Run `make help` to list all targets.

```bash
make test               # ruff, pyright, import-linter, bandit, pip-audit, and the
                        # unit test suite with coverage (pytest -m "not integration")
make testintegration    # integration tests only (pytest -m integration)
```

Doctests run as part of the suite (via `tests/test_doctests.py`): the offline doctests
run in `make test`, and the Admin/Store client doctests run in `make testintegration`.

### Integration tests

The integration tests exercise the Admin and Store clients against a real Shopware
instance using the [dockware](https://developer.shopware.com/docs/guides/installation/dockware)
container. The harness starts and stops the container automatically - no manual setup or
credentials are required (the dockware defaults are built in `tests/conf_test_docker.py`).

Prerequisites:

- **Docker** installed and running with a **Linux** container engine
  (`docker info --format '{{.OSType}}'` -> `linux`). If Docker is unavailable or not Linux,
  the integration tests are **skipped** (not failed).
- **Port 80** free - the container is published on `-p 80:80`.
- The first run pulls `dockware/dev:latest` (a few GB), so it takes a while.

Tip: for fast repeated runs, start the container once and leave it up - the harness reuses
a running container (and only tears down one it started itself):

```bash
docker run -d --rm -p 80:80 --name dockware dockware/dev:latest
make testintegration    # reuses the running container, finishes in seconds
```

CI runs the unit and integration suites as separate jobs across Linux, macOS, and Windows
for Python 3.10-3.14.

---

## Further Documentation

- [Install Guide](INSTALL.md)
- [Contributor Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)
