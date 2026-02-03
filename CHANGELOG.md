# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-02-03

### Breaking Changes

- **Pydantic Migration**: All data models (Criteria, Filters, Aggregations, Sorting) migrated from `attrs` to Pydantic `BaseModel`
- **HTTP Client Migration**: Replaced `requests`/`requests-oauthlib` with `httpx`/`authlib`
- **OAuth2 Migration**: Replaced `oauthlib` with `authlib` (OAuth 2.1 compliant)
- **Python Version**: Minimum version raised to Python 3.10+
- **API Change**: Filter/Criteria classes now require keyword arguments:
  ```python
  # Old (v2.x): EqualsFilter("stock", 10)
  # New (v3.0): EqualsFilter(field="stock", value=10)
  ```
- **Environment Variables**: All env vars now use `SHOPWARE_` prefix to avoid collision with system variables (e.g., Windows `USERNAME`):
  ```bash
  # Old: USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET, GRANT_TYPE, INSECURE_TRANSPORT, STORE_API_SW_ACCESS_KEY
  # New: SHOPWARE_USERNAME, SHOPWARE_PASSWORD, SHOPWARE_CLIENT_ID, SHOPWARE_CLIENT_SECRET, SHOPWARE_GRANT_TYPE, SHOPWARE_INSECURE_TRANSPORT, SHOPWARE_STORE_API_SW_ACCESS_KEY
  ```

### Added

- `load_config_from_env()` - Load configuration from .env file with auto-discovery
- `require_config_from_env()` - Load configuration, raising error if .env not found
- `ConfigurationError` exception for configuration-related errors
- `ExitCode` enum with standardized CLI exit codes
- HTTP/2 support via httpx
- Docker integration tests with automatic container startup
- Comprehensive test suite with 90%+ coverage

### Changed

- Configuration class `ConfShopware6ApiBase` now uses Pydantic `BaseSettings`
- ~20-30% performance improvement from httpx migration
- Full strict type hints with pyright checking
- Ruff linter replaces flake8/black

### Removed

- `attrs` dependency
- `requests`, `requests-oauthlib`, `oauthlib` dependencies
- Python 3.8 and 3.9 support

## [2.1.9] - 2024-09-29

- Add graalpy tests

## [2.1.8] - 2024-09-29

- Add example for `/search/order` via POST request

## [2.1.7] - 2023-10-18

- Validator for `Criteria.ids` and `Criteria.limit` mutual exclusion
- Prevent simultaneous use of `ids` and `limit` parameters

## [2.1.6] - 2023-10-18

- Fix Filter Aggregation implementation
- Various typo corrections

## [2.1.0] - 2023-06-28

- Add bulk operation header constants
- Remove Python 3.6 support
- Add Python 3.11 tests

## [2.0.0] - 2022-01-04

- Allow None values in filters
- Paginated requests now respect limits

## [1.0.0] - 2021-12-26

- Initial release
