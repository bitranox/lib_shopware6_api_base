# lib_shopware6_api_base

<!-- Badges -->
[![CI](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/cicd_docker.yml/badge.svg)](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/cicd_docker.yml)
[![CodeQL](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/codeql.yml/badge.svg)](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open in Codespaces](https://img.shields.io/badge/Codespaces-Open-blue?logo=github&logoColor=white&style=flat-square)](https://codespaces.new/bitranox/bmk?quickstart=1)
[![PyPI](https://img.shields.io/pypi/v/bmk.svg)](https://pypi.org/project/lib_shopware6_api_base/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/bmk.svg)](https://pypi.org/project/lib_shopware6_api_base/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-46A3FF?logo=ruff&labelColor=000)](https://docs.astral.sh/ruff/)
[![codecov](https://codecov.io/gh/bitranox/lib_shopware6_api_base/graph/badge.svg?token=UFBaUDIgRk)](https://codecov.io/gh/bitranox/bmk)
[![Maintainability](https://qlty.sh/badges/041ba2c1-37d6-40bb-85a0-ec5a8a0aca0c/maintainability.svg)](https://qlty.sh/gh/bitranox/projects/bmk)
[![Known Vulnerabilities](https://snyk.io/test/github/bitranox/lib_shopware6_api_base/badge.svg)](https://snyk.io/test/github/bitranox/bmk)
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
- [Requirements](#requirements)
- [Changelog](CHANGELOG.md)
- [License](#license)

---

## Configuration

Configuration is managed via the `ConfShopware6ApiBase` class (Pydantic-based) which can load settings from:
1. Environment variables
2. A `.env` file
3. Direct instantiation

### Environment File (.env)

Copy `example.env` to `.env` and adjust values for your shop:

```bash
# API Endpoints
SHOPWARE_ADMIN_API_URL="https://shop.example.com/api"
SHOPWARE_STOREFRONT_API_URL="https://shop.example.com/store-api"

# OAuth2 Security (set to "1" only for local HTTP development)
INSECURE_TRANSPORT="0"

# User Credentials Grant (for interactive apps with refresh tokens)
USERNAME="admin@example.com"
PASSWORD="your-password"

# Resource Owner Grant (for automation/CLI - no refresh tokens)
CLIENT_ID="SWIAXXXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET="your-integration-secret"

# Grant type: USER_CREDENTIALS or RESOURCE_OWNER
GRANT_TYPE="RESOURCE_OWNER"

# Storefront API access key (from Sales Channel settings)
STORE_API_SW_ACCESS_KEY="SWSCXXXXXXXXXXXXXXXXXX"
```

#### .env Settings Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SHOPWARE_ADMIN_API_URL` | Admin API endpoint | `https://shop.example.com/api` |
| `SHOPWARE_STOREFRONT_API_URL` | Storefront API endpoint | `https://shop.example.com/store-api` |
| `INSECURE_TRANSPORT` | Allow HTTP (dev only) | `0` (production) or `1` (dev) |
| `USERNAME` | Admin user email | `admin@example.com` |
| `PASSWORD` | Admin user password | `secret` |
| `CLIENT_ID` | Integration Access ID | `SWIA...` |
| `CLIENT_SECRET` | Integration Secret | `...` |
| `GRANT_TYPE` | Auth method | `USER_CREDENTIALS` or `RESOURCE_OWNER` |
| `STORE_API_SW_ACCESS_KEY` | Storefront access key | `SWSC...` |

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

| Parameter | Type | Description |
|-----------|------|-------------|
| `request_url` | `str` | API endpoint (without base URL) |
| `payload` | `dict \| Criteria \| None` | Request body |
| `update_header_fields` | `dict[str, str] \| None` | Custom headers |

Admin API methods also support:

| Parameter | Type | Description |
|-----------|------|-------------|
| `content_type` | `str` | Content type (`json`, `octet-stream`) |
| `additional_query_params` | `dict` | URL query parameters |

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

## Requirements

Automatically installed dependencies:

- `pydantic>=2.0.0` - Data validation
- `pydantic-settings>=2.0.0` - Settings management
- `httpx>=0.28` - HTTP client
- `authlib>=1.6` - OAuth2 authentication
- `rich-click` - CLI formatting
- `orjson` - Fast JSON serialization
- `lib_cli_exit_tools>=2.2.4` - CLI utilities

---

## License

[MIT License](http://en.wikipedia.org/wiki/MIT_License)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
