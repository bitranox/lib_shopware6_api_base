"""Centralized pytest fixtures and OS-specific markers for the test suite."""

from __future__ import annotations

import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest
import requests

if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.config import Config
    from _pytest.nodes import Item

# Import all the classes needed for fixtures
from lib_shopware6_api_base import (
    AscFieldSorting,
    AvgAggregation,
    ContainsFilter,
    CountAggregation,
    Criteria,
    DateHistogramAggregation,
    DescFieldSorting,
    EntityAggregation,
    EqualsAnyFilter,
    EqualsFilter,
    FieldSorting,
    FilterAggregation,
    MaxAggregation,
    MinAggregation,
    MultiFilter,
    NotFilter,
    PrefixFilter,
    Query,
    RangeFilter,
    Shopware6AdminAPIClientBase,
    StatsAggregation,
    SuffixFilter,
    SumAggregation,
    TermsAggregation,
)
from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase


def pytest_configure(config: Config) -> None:
    """Register custom markers for OS-specific and integration tests."""
    config.addinivalue_line("markers", "os_agnostic: runs on all operating systems")
    config.addinivalue_line("markers", "os_windows: Windows-specific tests")
    config.addinivalue_line("markers", "os_macos: macOS-specific tests")
    config.addinivalue_line("markers", "os_posix: POSIX (Linux/macOS) tests")
    config.addinivalue_line("markers", "os_linux: Linux-specific tests")
    config.addinivalue_line("markers", "integration: requires external services")


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Auto-skip OS-specific tests on wrong platform."""
    is_windows = sys.platform == "win32"
    is_macos = sys.platform == "darwin"
    is_linux = sys.platform.startswith("linux")
    is_posix = is_linux or is_macos

    for item in items:
        marker_names = [m.name for m in item.iter_markers()]

        if "os_windows" in marker_names and not is_windows:
            item.add_marker(pytest.mark.skip(reason="Windows-only test"))
        if "os_macos" in marker_names and not is_macos:
            item.add_marker(pytest.mark.skip(reason="macOS-only test"))
        if "os_linux" in marker_names and not is_linux:
            item.add_marker(pytest.mark.skip(reason="Linux-only test"))
        if "os_posix" in marker_names and not is_posix:
            item.add_marker(pytest.mark.skip(reason="POSIX-only test"))


# =============================================================================
# Filter Fixtures
# =============================================================================


@pytest.fixture
def equals_filter() -> EqualsFilter:
    """Return an EqualsFilter with field='stock' and value=10."""
    return EqualsFilter(field="stock", value=10)


@pytest.fixture
def equals_filter_none() -> EqualsFilter:
    """Return an EqualsFilter with field='stock' and value=None."""
    return EqualsFilter(field="stock", value=None)


@pytest.fixture
def equals_filter_bool() -> EqualsFilter:
    """Return an EqualsFilter with field='active' and value=True."""
    return EqualsFilter(field="active", value=True)


@pytest.fixture
def equals_filter_string() -> EqualsFilter:
    """Return an EqualsFilter with field='name' and value='test'."""
    return EqualsFilter(field="name", value="test")


@pytest.fixture
def equals_any_filter() -> EqualsAnyFilter:
    """Return an EqualsAnyFilter with field='productNumber' and multiple values."""
    return EqualsAnyFilter(field="productNumber", value=["abc123", "def456"])


@pytest.fixture
def contains_filter() -> ContainsFilter:
    """Return a ContainsFilter with field='name' and value='Lightweight'."""
    return ContainsFilter(field="name", value="Lightweight")


@pytest.fixture
def range_filter() -> RangeFilter:
    """Return a RangeFilter with field='stock' and gte/lte parameters."""
    return RangeFilter(field="stock", parameters={"gte": 20, "lte": 30})


@pytest.fixture
def range_filter_gt_lt() -> RangeFilter:
    """Return a RangeFilter with gt/lt parameters."""
    return RangeFilter(field="price", parameters={"gt": 10, "lt": 100})


@pytest.fixture
def prefix_filter() -> PrefixFilter:
    """Return a PrefixFilter with field='name' and value='Light'."""
    return PrefixFilter(field="name", value="Light")


@pytest.fixture
def suffix_filter() -> SuffixFilter:
    """Return a SuffixFilter with field='name' and value='weight'."""
    return SuffixFilter(field="name", value="weight")


@pytest.fixture
def not_filter(equals_filter: EqualsFilter) -> NotFilter:
    """Return a NotFilter with operator='or' and a single query."""
    return NotFilter(operator="or", queries=[equals_filter])


@pytest.fixture
def multi_filter(equals_filter: EqualsFilter, contains_filter: ContainsFilter) -> MultiFilter:
    """Return a MultiFilter with operator='and' and multiple queries."""
    return MultiFilter(operator="and", queries=[equals_filter, contains_filter])


# =============================================================================
# Sorting Fixtures
# =============================================================================


@pytest.fixture
def field_sorting_asc() -> FieldSorting:
    """Return a FieldSorting with order='ASC' and naturalSorting=True."""
    return FieldSorting(field="name", order="ASC", naturalSorting=True)


@pytest.fixture
def field_sorting_desc() -> FieldSorting:
    """Return a FieldSorting with order='DESC'."""
    return FieldSorting(field="price", order="DESC")


@pytest.fixture
def asc_field_sorting() -> AscFieldSorting:
    """Return an AscFieldSorting with naturalSorting=True."""
    return AscFieldSorting(field="name", naturalSorting=True)


@pytest.fixture
def desc_field_sorting() -> DescFieldSorting:
    """Return a DescFieldSorting with naturalSorting=False."""
    return DescFieldSorting(field="price", naturalSorting=False)


# =============================================================================
# Aggregation Fixtures
# =============================================================================


@pytest.fixture
def avg_aggregation() -> AvgAggregation:
    """Return an AvgAggregation for price field."""
    return AvgAggregation(name="avg-price", field="price")


@pytest.fixture
def count_aggregation() -> CountAggregation:
    """Return a CountAggregation for manufacturerId field."""
    return CountAggregation(name="count-manufacturers", field="manufacturerId")


@pytest.fixture
def max_aggregation() -> MaxAggregation:
    """Return a MaxAggregation for price field."""
    return MaxAggregation(name="max-price", field="price")


@pytest.fixture
def min_aggregation() -> MinAggregation:
    """Return a MinAggregation for price field."""
    return MinAggregation(name="min-price", field="price")


@pytest.fixture
def sum_aggregation() -> SumAggregation:
    """Return a SumAggregation for price field."""
    return SumAggregation(name="sum-price", field="price")


@pytest.fixture
def stats_aggregation() -> StatsAggregation:
    """Return a StatsAggregation for price field."""
    return StatsAggregation(name="stats-price", field="price")


@pytest.fixture
def terms_aggregation() -> TermsAggregation:
    """Return a TermsAggregation for manufacturerId field."""
    return TermsAggregation(name="manufacturer-ids", field="manufacturerId", limit=10)


@pytest.fixture
def terms_aggregation_with_sort(desc_field_sorting: DescFieldSorting) -> TermsAggregation:
    """Return a TermsAggregation with sorting."""
    return TermsAggregation(
        name="manufacturer-ids",
        field="manufacturerId",
        limit=5,
        sort=desc_field_sorting,
    )


@pytest.fixture
def filter_aggregation(equals_filter: EqualsFilter, avg_aggregation: AvgAggregation) -> FilterAggregation:
    """Return a FilterAggregation with a filter and nested aggregation."""
    return FilterAggregation(
        name="active-price-avg",
        filter=[equals_filter],
        aggregation=avg_aggregation,
    )


@pytest.fixture
def entity_aggregation() -> EntityAggregation:
    """Return an EntityAggregation for manufacturers."""
    return EntityAggregation(
        name="manufacturers",
        definition="product_manufacturer",
        field="manufacturerId",
    )


@pytest.fixture
def date_histogram_aggregation() -> DateHistogramAggregation:
    """Return a DateHistogramAggregation for releaseDate field."""
    return DateHistogramAggregation(
        name="release-dates",
        field="releaseDate",
        interval="month",
    )


# =============================================================================
# Criteria Fixtures
# =============================================================================


@pytest.fixture
def empty_criteria() -> Criteria:
    """Return an empty Criteria object."""
    return Criteria()


@pytest.fixture
def criteria_with_limit() -> Criteria:
    """Return a Criteria with limit and page."""
    return Criteria(limit=10, page=1)


@pytest.fixture
def criteria_with_ids() -> Criteria:
    """Return a Criteria with ids."""
    return Criteria(ids=["id1", "id2", "id3"])


@pytest.fixture
def complex_criteria(
    equals_filter: EqualsFilter,
    avg_aggregation: AvgAggregation,
    field_sorting_asc: FieldSorting,
) -> Criteria:
    """Return a Criteria with filter, aggregation, and sorting."""
    return Criteria(
        limit=10,
        page=1,
        filter=[equals_filter],
        aggregations=[avg_aggregation],
        sort=[field_sorting_asc],
    )


@pytest.fixture
def criteria_with_associations(equals_filter: EqualsFilter) -> Criteria:
    """Return a Criteria with nested associations."""
    criteria = Criteria()
    criteria.associations["products"] = Criteria(
        limit=5,
        filter=[equals_filter],
    )
    return criteria


@pytest.fixture
def criteria_with_includes() -> Criteria:
    """Return a Criteria with includes."""
    criteria = Criteria()
    criteria.includes["product"] = ["id", "name", "price"]
    return criteria


@pytest.fixture
def criteria_with_grouping() -> Criteria:
    """Return a Criteria with grouping."""
    return Criteria(limit=5, grouping=["active", "manufacturerId"])


@pytest.fixture
def criteria_with_term() -> Criteria:
    """Return a Criteria with term search."""
    return Criteria(term="searchterm")


# =============================================================================
# Query Fixtures
# =============================================================================


@pytest.fixture
def query_with_contains_filter(contains_filter: ContainsFilter) -> Query:
    """Return a Query with a ContainsFilter."""
    return Query(score=500, query=contains_filter)


@pytest.fixture
def query_with_equals_filter(equals_filter: EqualsFilter) -> Query:
    """Return a Query with an EqualsFilter."""
    return Query(score=100, query=equals_filter)


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def empty_config() -> ConfShopware6ApiBase:
    """Return an empty ConfShopware6ApiBase configuration."""
    return ConfShopware6ApiBase()


@pytest.fixture
def full_config() -> ConfShopware6ApiBase:
    """Return a fully populated ConfShopware6ApiBase configuration."""
    from lib_shopware6_api_base.conf_shopware6_api_base_classes import GrantType

    return ConfShopware6ApiBase(
        shopware_admin_api_url="https://shop.example.com/api",
        shopware_storefront_api_url="https://shop.example.com/store-api",
        username="admin",
        password="secret123",
        client_id="test_client_id",
        client_secret="test_client_secret",
        grant_type=GrantType.USER_CREDENTIALS,
        store_api_sw_access_key="SWSC1234567890ABCDEF",
    )


@pytest.fixture
def resource_owner_config() -> ConfShopware6ApiBase:
    """Return a ConfShopware6ApiBase configured for resource owner grant type."""
    from lib_shopware6_api_base.conf_shopware6_api_base_classes import GrantType

    return ConfShopware6ApiBase(
        shopware_admin_api_url="https://shop.example.com/api",
        client_id="integration_client_id",
        client_secret="integration_client_secret",
        grant_type=GrantType.RESOURCE_OWNER,
    )


# =============================================================================
# Docker Container Fixtures for Integration Tests
# =============================================================================

DOCKER_CONTAINER_NAME = "dockware"
DOCKER_IMAGE = "dockware/dev:latest"
DOCKER_STARTUP_TIMEOUT = 120  # seconds to wait for container to be ready
DOCKER_CHECK_INTERVAL = 5  # seconds between readiness checks
REQUEST_TIMEOUT = 10  # seconds for HTTP requests


def _is_docker_container_active() -> bool:
    """Check if the local docker container is running and responding."""
    try:
        requests.get("http://localhost/admin", timeout=REQUEST_TIMEOUT)
        return True
    except requests.exceptions.ConnectionError:
        return False


def _is_docker_container_running() -> bool:
    """Check if the docker container process is running (even if not yet ready)."""
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", f"name={DOCKER_CONTAINER_NAME}"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _start_docker_container() -> None:
    """Start the dockware docker container."""
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "-p",
            "80:80",
            "--name",
            DOCKER_CONTAINER_NAME,
            DOCKER_IMAGE,
        ],
        check=True,
    )


def _stop_docker_container() -> None:
    """Stop the dockware docker container."""
    if _is_docker_container_running():
        subprocess.run(
            ["docker", "stop", DOCKER_CONTAINER_NAME],
            capture_output=True,
        )


def _wait_for_docker_container_ready() -> bool:
    """Wait for the docker container to be ready to accept connections."""
    start_time = time.time()
    while time.time() - start_time < DOCKER_STARTUP_TIMEOUT:
        if _is_docker_container_active():
            return True
        time.sleep(DOCKER_CHECK_INTERVAL)
    return False


@pytest.fixture(scope="session")
def docker_container() -> Generator[None, None, None]:
    """Ensure docker container is running for integration tests.

    This fixture:
    1. Checks if the docker container is already running
    2. If not, starts the dockware container
    3. Waits for it to be ready
    4. After all tests complete, stops the container
    """
    container_was_started_by_fixture = False

    if not _is_docker_container_active():
        if _is_docker_container_running():
            # Container is running but not ready yet - wait for it
            if not _wait_for_docker_container_ready():
                pytest.skip("Docker container failed to become ready")
        else:
            # Start the container
            _start_docker_container()
            container_was_started_by_fixture = True
            if not _wait_for_docker_container_ready():
                _stop_docker_container()
                pytest.skip("Docker container failed to start")

    yield

    # Only stop if we started it
    if container_was_started_by_fixture:
        _stop_docker_container()


# =============================================================================
# Docker Test Container Helper Functions
# =============================================================================


def _get_docker_test_container_store_access_key(config: ConfShopware6ApiBase) -> str:
    """Get the sales channel accessKey from the docker testcontainer."""
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    response_dict = admin_api_client.request_get("sales-channel")
    return str(response_dict["data"][0]["accessKey"])


def _is_resource_owner_credentials_present(config: ConfShopware6ApiBase) -> bool:
    """Check if resource owner credentials exist."""
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    response_dict = admin_api_client.request_post("search/integration")
    return bool(response_dict["total"])


def _create_docker_test_container_resource_owner_credentials(config: ConfShopware6ApiBase) -> None:
    """Create resource owner credentials if not present."""
    if _is_resource_owner_credentials_present(config):
        return
    payload = {
        "id": "565c4ada878141d3b18d6977dbbd2a13",
        "label": "dockware_integration_admin",
        "accessKey": "SWIACWJOMUTXV1RMNGJUAKTUAA",
        "secretAccessKey": "UkhvUG1qdmpuMjFudGJCdG1Xc0xMbEt2ck9CQ2xDTUtXMUZHRUQ",
        "admin": True,
    }
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    admin_api_client.request_post("integration", payload=payload)


@pytest.fixture
def docker_test_config(docker_container: None) -> ConfShopware6ApiBase:
    """Return the docker test container configuration with full setup.

    This fixture depends on docker_container to ensure the container is running.
    It also sets up the store access key and ensures resource owner credentials exist.
    """
    from conf_test_docker import conf_shopware6_api_base

    config = conf_shopware6_api_base
    # Set up store access key
    config.store_api_sw_access_key = _get_docker_test_container_store_access_key(config)
    # Ensure resource owner credentials exist
    _create_docker_test_container_resource_owner_credentials(config)
    return config
