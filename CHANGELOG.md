# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [6.0.1] - 2026-06-08

### Fixed

- **CLI no longer swallows error messages.** `run_cli` was given a custom
  `exception_handler` that returned an exit code but never printed, so every failure
  (bad config, API error, invalid argument) exited non-zero with no diagnostic. The
  handler now prints the message (terse, or a full traceback under `--traceback`)
  for non-signal errors, while signals still exit cleanly and quietly.
- **`--traceback` no longer leaks across invocations.** `main()` snapshots and restores
  the process-global `lib_cli_exit_tools.config.traceback`, so running the CLI once with
  `--traceback` in a long-lived process no longer forces full tracebacks on later commands.

## [6.0.0] - 2026-06-08

### Breaking Changes

- **Removed the backward-compatibility aliases** `equal_filter_type`, `range_filter`,
  `not_filter_operator`, and `multi_filter_operator`. Use `FilterTypeName`, `RangeParam`,
  and `FilterOperator` directly.
- **Removed the `insecure_transport` config field.** It had no effect after the authlib
  removal in 3.1.0 (httpx2 talks to plain-HTTP endpoints without it). The TOML key and the
  `SHOPWARE__INSECURE_TRANSPORT` env var are no longer read.
- **`EqualsAnyFilter.value` is now required** (previously defaulted to an empty list); an
  `equalsAny` without values raises a `ValidationError`.
- **`Criteria.get_dict()` serialization changed.** It now uses
  `model_dump(mode="json", exclude_defaults=True, by_alias=True)`: empty fields are pruned
  recursively (nested associations/aggregations stay clean), and `total_count_mode` /
  `post_filter` serialize as the hyphenated DAL keys `total-count-mode` / `post-filter`.
- **String config fields reject numeric values** instead of silently stringifying them, so a
  mistyped secret surfaces as a `ValidationError` rather than being corrupted.

### Added

- CLI commands for connectivity and config inspection: `test-connection`, `get <endpoint>`
  (read-only Admin GET), `config show` (secrets masked), and `config paths`.
- `init_logging` / `shutdown_logging` are exported from the package so library users can opt
  in to `lib_log_rich` logging (the library stays silent by default; the CLI initialises it).
- `post_filter` is implemented as a real `list[FilterType]` (serialized as `post-filter`).
- `Shopware6AdminAPIClientBase` is now a context manager (`with ...`) and exposes `close()`
  to release its HTTP connection pool.

### Fixed

- **Binary uploads (Admin media upload) were corrupted**: the client sent `str(bytes)` (the
  Python repr) instead of the raw bytes. It now sends the bytes unchanged.
- **`FilterType` / `AggregationType` are discriminated unions**, so re-validating a serialized
  `Criteria` keeps the correct classes (previously a `contains` filter collapsed to `equals`,
  `multi` to `not`, etc.).
- Storefront `request_delete` and other empty (HTTP 204) responses no longer crash on JSON
  decode; they return `{}` / `[]`.
- The Storefront client rejects a binary payload with a clear `ShopwareAPIError` instead of an
  opaque serialization error.
- `RangeFilter.parameters` accepts `str`, so a caller's exact date string is sent verbatim
  (no `'2024-09-29'` -> `'2024-09-29T00:00:00'` rewrite).
- `grant_type` validation raises a clean `ValidationError` (not `AttributeError`) on a
  non-string value.
- `config show` masks `client_id` and the Store API access key.
- `config paths` reports the host configuration layer.

### Changed

- Doctests now run as part of the test suite (`tests/test_doctests.py`): offline doctests in
  `make test`, the Admin/Storefront client doctests in `make testintegration`.
- The `pprint_attrs` helper was renamed to `pprint_model` and reimplemented with idiomatic
  Pydantic (`model_dump(mode="json", exclude_defaults=True, by_alias=True)`).
- README and inline documentation rewritten (plain ASCII), with a layered-config and logging
  guide; refreshed dependency minimums.

## [5.0.0] - 2026-06-08

### Breaking Changes

- **Admin API methods now return a typed `ShopwareApiResponse`** instead of a raw `dict`.
  `request_get` / `request_post` / `request_patch` / `request_put` / `request_delete` and the
  paginated variants return a Pydantic envelope with typed `.total` and dynamic `.data` /
  `.aggregations` / `.errors` (entity contents stay `Any` - the client is entity-agnostic).
  Replace `response["data"]` with `response.data`, `response["total"]` with `response.total`, etc.
  (The Storefront client is unchanged - its responses have no uniform envelope.)

## [4.0.0] - 2026-06-08

### Breaking Changes

- **Configuration is now loaded through `lib_layered_config`.** All settings - the
  `[shopware]` connection settings and the `[lib_log_rich]` logging settings - are merged
  across bundled defaults -> app -> host -> user -> `.env` -> environment variables.
- **Environment variables renamed.** The old single-underscore `SHOPWARE_*` variables are
  no longer read. Use `SHOPWARE__<KEY>` in a `.env` file, or
  `LIB_SHOPWARE6_API_BASE___SHOPWARE__<KEY>` as a real environment variable. See the README
  migration table.
- `ConfShopware6ApiBase` is now a plain Pydantic `BaseModel` (no longer `pydantic-settings`
  `BaseSettings`); the removed helpers `from_env_file` / `from_env_vars` are gone.
  `load_config_from_env()` / `require_config_from_env()` remain and now take no arguments.
- The `OAUTHLIB_INSECURE_TRANSPORT` side effect was removed (authlib is no longer a
  dependency); `insecure_transport` is still accepted as a config field.

### Added

- `lib_log_rich` structured logging, configured via the `[lib_log_rich]` config section and
  initialized by the CLI (`logging_setup.py`). Library modules continue to use stdlib
  `logging`, which is bridged into `lib_log_rich`.
- Bundled `defaultconfig.toml` + `defaultconfig.d/{10-logging,20-shopware}.toml` shipped with
  the package as the lowest-precedence config layer.

### Removed

- `pydantic-settings` dependency.

## [3.1.3] - 2026-06-08

### Fixed

- Docs: reformatted README markdown tables for consistent column alignment (cosmetic; no content change).

## [3.1.2] - 2026-06-08

### Changed

- **Tooling**: project automation converted to the standard BMK `Makefile`; `make test`, `make testintegration`, `make push`, `make release`, and `make bump-*` now run via the `bmk` uv-tool. The vendored `scripts/` package (plus `mk` / `mk.py`) and the dead `tests/local_testscripts/` helpers were removed.
- **Docs**: README gained a "Development" section documenting how to run the unit suite (`make test`) and the dockware-backed integration suite (`make testintegration`), including prerequisites.
- Refreshed dependency minimums to current releases (`pydantic`, `pydantic-settings`, `httpx2`, `lib_cli_exit_tools`, and dev/build tooling) via the bmk dependency update.

### Fixed

- pip-audit: ignore shared dev-venv audit noise (`aiohttp`, `paramiko`, `pyjwt`) - not dependencies of this project and absent from CI's clean env; present only because sibling editable projects share the local venv.

## [3.1.1] - 2026-06-08

### Fixed

- pip-audit: ignore `PYSEC-2026-196` (pip 26.1.1, env-only GHA runner image, fix in pip 26.1.2, awaiting runner bump) - unblocks the scheduled CI vulnerability scan.

## [3.1.0] - 2026-06-01

### Changed

- **HTTP client migrated from `httpx` to `httpx2`** (the Pydantic-stewarded successor); minimum `httpx2>=2.2.0`. Storefront client and shared HTTP helpers swapped over directly (API-compatible surface). Dev tooling (`scripts/dependencies.py`) migrated too.
- Admin API OAuth2 (token fetch, refresh-token flow, Bearer auth, expiry handling) reimplemented directly on `httpx2`, replacing Authlib's `OAuth2Client`. The `self.token` shape is unchanged (`access_token`, `expires_in`, `expires_at`, and `refresh_token` for the password grant); public client APIs are unchanged.

### Removed

- Dropped the `authlib` dependency - OAuth2 token handling is now performed in-library. As a side effect, `insecure_transport` is no longer required to talk to plain-HTTP endpoints (the previous `OAUTHLIB_INSECURE_TRANSPORT` guard is gone); the config field is retained for backward compatibility but is now a no-op.

## [3.0.2] - 2026-05-08

### Changed

- Bumped dev pin `python-multipart` to `>=0.0.27` (CVE-2026-42561)

### Fixed

- pip-audit: ignore `CVE-2026-6357` (pip 26.0.1, env-only, fix in pip 26.1, awaiting GHA runner image bump)

## [3.0.1] - 2026-04-26

### Changed

- Bumped `authlib` minimum to `>=1.6.11` (GHSA-jj8c-mmj3-mmgv)
- Bumped dev pin `python-multipart` to `>=0.0.26` (CVE-2026-40347)
- Updated CI actions: `codecov-action@v6`, refreshed upload/download-artifact actions

### Fixed

- pip-audit: ignore `CVE-2026-3219` (pip 26.0.1, env-only, no upstream fix)

### Removed

- Snyk badge from README
- Stale CVE entries from `tool.pip-audit.ignore-vulns` no longer flagged (kept setuptools CVEs needed by macOS Py 3.10/3.11 runners)

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
