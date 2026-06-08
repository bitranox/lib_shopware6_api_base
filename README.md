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

A Python base API client for Shopware 6, supporting Windows, Linux, and macOS.
Supports all OAuth2 authentication methods for both Admin API and Storefront API.
Paginated requests are fully supported.

This is the base abstraction layer. For higher-level functions, see [lib_shopware6_api](https://github.com/bitranox/lib_shopware6_api).

**Python 3.10+** required.

---

### v3.0.0 (2026-02-03) - complete overhaul

**Breaking Changes:**
- Migrated from `attrs` to `Pydantic` for all data models (Criteria, Filters, Aggregations, Sorting)
- Migrated HTTP client from `requests`/`requests-oauthlib` to `httpx`/`authlib`
- Migrated OAuth2 from `oauthlib` to `authlib` (OAuth 2.1 compliant)
- Minimum Python version raised to 3.10+
- Filter/Criteria classes now require keyword arguments: `EqualsFilter(field="x", value=1)` instead of `EqualsFilter("x", 1)`
- **Environment variables use `SHOPWARE_` prefix** to avoid collision with system variables (e.g., Windows `USERNAME`).

**New Features:**
- `load_config_from_env()` and `require_config_from_env()` for .env file loading
- `ConfigurationError` exception for configuration issues
- `ExitCode` enum for CLI exit codes
- HTTP/2 support via httpx
- ~20-30% performance improvement from httpx

---

## Table of Contents

- [Configuration](#configuration)
  - [Environment File (.env)](#environment-file-env)
  - [Loading Configuration](#loading-configuration)
- [API Clients](#api-clients)
  - [Admin API](#admin-api)
  - [Storefront API](#storefront-api)
- [Request Methods](#request-methods)
  - [Custom Headers](#custom-headers)
- [Query Syntax (Criteria)](#query-syntax-criteria)
  - [Filters](#filters)
  - [Sorting](#sorting)
  - [Aggregations](#aggregations)
  - [Associations](#associations)
- [CLI Usage](#cli-usage)
- [Installation](#installation)
- [Development](#development)
  - [Running tests](#running-tests)
  - [Integration tests](#integration-tests)
- [Requirements](#requirements)
- [Changelog](CHANGELOG.md)
- [License](#license)

---

## Configuration

Configuration is managed via the `ConfShopware6ApiBase` class (Pydantic) and loaded
through [`lib_layered_config`](https://github.com/bitranox/lib_layered_config), which
merges, in increasing precedence:

```
bundled defaults  ->  app  ->  host  ->  user  ->  .env  ->  environment variables
```

You can also instantiate `ConfShopware6ApiBase(...)` directly with keyword arguments.

> **⚠️ Breaking change in 4.0.0 — env vars renamed.** Configuration moved to
> `lib_layered_config`, so the old single-underscore `SHOPWARE_*` variables are **no
> longer read**. Rename them to the `[shopware]` section form:
>
> | Old (≤ 3.x)                        | New — `.env` file              | New — environment variable                              |
> |------------------------------------|--------------------------------|---------------------------------------------------------|
> | `SHOPWARE_ADMIN_API_URL`           | `SHOPWARE__ADMIN_API_URL`      | `LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL`      |
> | `SHOPWARE_STOREFRONT_API_URL`      | `SHOPWARE__STOREFRONT_API_URL` | `LIB_SHOPWARE6_API_BASE___SHOPWARE__STOREFRONT_API_URL` |
> | `SHOPWARE_<NAME>`                  | `SHOPWARE__<NAME>`             | `LIB_SHOPWARE6_API_BASE___SHOPWARE__<NAME>`             |
>
> i.e. in a `.env` file replace the single `_` after `SHOPWARE` with `__`; as a real
> environment variable also add the `LIB_SHOPWARE6_API_BASE___` slug prefix.

### Environment File (.env)

Copy `example.env` to `.env` and adjust values for your shop:

```bash
# API Endpoints
SHOPWARE__ADMIN_API_URL="https://shop.example.com/api"
SHOPWARE__STOREFRONT_API_URL="https://shop.example.com/store-api"

# Transport (set to "1" only for local HTTP development)
SHOPWARE__INSECURE_TRANSPORT="0"

# User-Credentials grant (interactive apps with refresh tokens)
SHOPWARE__USERNAME="admin@example.com"
SHOPWARE__PASSWORD="your-password"

# Resource-Owner grant (automation/CLI - no refresh tokens)
SHOPWARE__CLIENT_ID="SWIAXXXXXXXXXXXXXXXXXXXX"
SHOPWARE__CLIENT_SECRET="your-integration-secret"

# Grant type: USER_CREDENTIALS or RESOURCE_OWNER
SHOPWARE__GRANT_TYPE="RESOURCE_OWNER"

# Storefront API access key (from Sales Channel settings)
SHOPWARE__STORE_API_SW_ACCESS_KEY="SWSCXXXXXXXXXXXXXXXXXX"
```

#### `[shopware]` Settings Reference

In a `.env` file use the `SHOPWARE__<KEY>` form; as a real environment variable prefix
with `LIB_SHOPWARE6_API_BASE___`. The same keys can be set in a TOML config file under
`[shopware]` (dropping the `SHOPWARE__` prefix).

| `.env` key                         | Description             | Example                                |
|------------------------------------|-------------------------|----------------------------------------|
| `SHOPWARE__ADMIN_API_URL`          | Admin API endpoint      | `https://shop.example.com/api`         |
| `SHOPWARE__STOREFRONT_API_URL`     | Storefront API endpoint | `https://shop.example.com/store-api`   |
| `SHOPWARE__INSECURE_TRANSPORT`     | Allow HTTP (dev only)   | `0` (production) or `1` (dev)          |
| `SHOPWARE__USERNAME`               | Admin user email        | `admin@example.com`                    |
| `SHOPWARE__PASSWORD`               | Admin user password     | `secret`                               |
| `SHOPWARE__CLIENT_ID`              | Integration Access ID   | `SWIA...`                              |
| `SHOPWARE__CLIENT_SECRET`          | Integration Secret      | `...`                                  |
| `SHOPWARE__GRANT_TYPE`             | Auth method             | `USER_CREDENTIALS` or `RESOURCE_OWNER` |
| `SHOPWARE__STORE_API_SW_ACCESS_KEY`| Storefront access key   | `SWSC...`                              |

### Loading Configuration

```python
from lib_shopware6_api_base import (
    ConfShopware6ApiBase,
    load_config_from_env,
    require_config_from_env,
    Shopware6AdminAPIClientBase,
)

# Option 1: Auto-find .env in current or parent directories
config = load_config_from_env()

# Option 2: Require .env file (raises ConfigurationError if not found)
config = require_config_from_env()

# Option 3: Load from specific file
config = load_config_from_env("/path/to/my.env")

# Option 4: Direct instantiation
config = ConfShopware6ApiBase(
    shopware_admin_api_url="https://shop.example.com/api",
    username="admin",
    password="secret",
)

# Use the config
client = Shopware6AdminAPIClientBase(config=config)
```

---

## API Clients

### Admin API

```python
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria

client = Shopware6AdminAPIClientBase(config=config)

# GET request
response = client.request_get("currency")

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

### Storefront API

```python
from lib_shopware6_api_base import Shopware6StoreFrontClientBase, Criteria

client = Shopware6StoreFrontClientBase(config=config)

# GET request (returns dict)
response = client.request_get("context")

# GET request (returns list)
currencies = client.request_get_list("currency")

# POST request with criteria
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

Admin API methods also support:

| Parameter                 | Type   | Description                           |
|---------------------------|--------|---------------------------------------|
| `content_type`            | `str`  | Content type (`json`, `octet-stream`) |
| `additional_query_params` | `dict` | URL query parameters                  |

### Custom Headers

For bulk operations, use predefined header constants:

```python
from lib_shopware6_api_base import (
    HEADER_write_in_single_transactions,  # {"single-operation": "true"}
    HEADER_write_in_separate_transactions,  # {"single-operation": "false"}
    HEADER_index_synchronously,  # {"indexing-behavior": "null"}
    HEADER_index_asynchronously,  # {"indexing-behavior": "use-queue-indexing"}
    HEADER_index_disabled,  # {"indexing-behavior": "disable-indexing"}
    HEADER_fail_on_error,  # {"fail-on-error": "true"}
    HEADER_do_not_fail_on_error,  # {"fail-on-error": "false"}
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

# Match any of values
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

The library provides specific exception classes for different error scenarios:

```python
from lib_shopware6_api_base import (
    ShopwareAPIError,
    ConfigurationError,
    Shopware6AdminAPIClientBase,
    load_config_from_env,
)

# Handle configuration errors
try:
    config = load_config_from_env("/path/to/missing.env")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle missing or invalid configuration

# Handle API errors
try:
    client = Shopware6AdminAPIClientBase(config=config)
    response = client.request_get("product/invalid-id")
except ShopwareAPIError as e:
    print(f"API error: {e}")
    # Handle API errors (404, 401, 500, etc.)
```

### Exception Types

| Exception            | When Raised                                     |
|----------------------|-------------------------------------------------|
| `ConfigurationError` | Missing .env file, invalid configuration values |
| `ShopwareAPIError`   | HTTP errors from the API (4xx, 5xx responses)   |

---

## CLI Usage

```
Usage: lib_shopware6_api_base [OPTIONS] COMMAND [ARGS]...

  Python base API client for Shopware 6

Options:
  --version                     Show version and exit
  --traceback / --no-traceback  Show traceback on errors
  -h, --help                    Show this message and exit

Commands:
  info  Show program information
```

---

## Installation

### Via uv (recommended)

```bash
# One-shot run
uvx lib_shopware6_api_base --help

# Install as CLI tool
uv tool install lib_shopware6_api_base

# Install as dependency
uv pip install lib_shopware6_api_base
```

### Via pip

```bash
pip install lib_shopware6_api_base
```

---

## Development

Project automation runs through a `Makefile` that delegates to [`bmk`](https://pypi.org/project/bmk/)
(installed automatically as a persistent `uv` tool on first use). Run `make help` to list all targets.

### Running tests

```bash
make test               # lint (ruff), type-check (pyright), import-linter,
                        # bandit, pip-audit, and the unit test suite with coverage
make testintegration    # integration tests only (see prerequisites below)
```

`make test` runs the full quality gate but **excludes** the integration tests
(`pytest -m "not integration"`). `make testintegration` runs **only** the
integration suite (`pytest -m integration`).

### Integration tests

The integration tests exercise the Admin and Storefront clients against a real
Shopware instance using the [dockware](https://developer.shopware.com/docs/guides/installation/dockware)
container. The test harness starts and stops the container automatically — no
manual setup or credentials are required (`tests/docker.env` ships the dockware
defaults).

Prerequisites:

- **Docker** installed and running, with a **Linux** container engine
  (`docker info --format '{{.OSType}}'` → `linux`). If Docker is unavailable or
  not Linux, the integration tests are **skipped** (not failed).
- **Port 80** free — the container is published on `-p 80:80`.
- First run pulls `dockware/dev:latest` (a few GB), so it takes a while.

Tip: for fast repeated runs, start the container once and leave it up — the
harness reuses a running container (and only tears down one it started itself):

```bash
docker run -d --rm -p 80:80 --name dockware dockware/dev:latest
make testintegration    # reuses the running container, finishes in seconds
```

CI runs the unit and integration suites as separate jobs across Linux, macOS,
and Windows for Python 3.10–3.14.

---

## Requirements

Automatically installed dependencies:

- `pydantic>=2.0.0` - Data validation
- `pydantic-settings>=2.0.0` - Settings management
- `httpx2>=2.2.0` - HTTP client
- `rich-click` - CLI formatting
- `orjson` - Fast JSON serialization
- `lib_cli_exit_tools>=2.2.4` - CLI utilities

---

## License

[MIT License](http://en.wikipedia.org/wiki/MIT_License)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
