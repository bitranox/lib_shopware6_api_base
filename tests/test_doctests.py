"""Execute the module doctests as part of the normal test suite.

Doctests carry no pytest marker, so the marker-based unit/integration split
(``make test`` = ``-m "not integration"``, ``make testintegration`` = ``-m
integration``) cannot route them on its own.  We therefore run them explicitly
through :func:`doctest.testmod`, in two buckets:

* **offline** doctests (Criteria / Filters / Sorting / Aggregations, the pprint
  helper, the config classes and the HTTP helpers) need nothing external and run
  in the unit suite;
* the **Admin / Storefront client** doctests talk to a live Shopware and run in
  the dockware-backed integration suite.

A shared namespace injects :func:`pprint_model` and every public Criteria /
Filter / Sorting / Aggregation class, because the docstrings reference them by
bare name; the live bucket additionally injects ``my_config`` (the dockware
test configuration) used to construct the clients.
"""

from __future__ import annotations

import doctest
import importlib
import time

import pytest

import lib_shopware6_api_base as pkg
from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase
from lib_shopware6_api_base.lib_shopware6_api_base_helpers import pprint_model

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.IGNORE_EXCEPTION_DETAIL

# Names the docstrings use by bare identifier (Criteria, EqualsFilter, ...) plus
# the pretty-printer and ``time`` (used by the admin token-refresh examples).
_DOCTEST_NAMES: dict[str, object] = {name: getattr(pkg, name) for name in dir(pkg) if not name.startswith("_")}
_DOCTEST_NAMES["pprint_model"] = pprint_model
_DOCTEST_NAMES["time"] = time

OFFLINE_MODULES = [
    "lib_shopware6_api_base.lib_shopware6_api_base_criteria",
    "lib_shopware6_api_base.lib_shopware6_api_base_criteria_filter",
    "lib_shopware6_api_base.lib_shopware6_api_base_criteria_sorting",
    "lib_shopware6_api_base.lib_shopware6_api_base_criteria_aggregation",
    "lib_shopware6_api_base.lib_shopware6_api_base_helpers",
    "lib_shopware6_api_base.conf_shopware6_api_base_classes",
    "lib_shopware6_api_base._http_common",
    "lib_shopware6_api_base.__init__conf__",
    "lib_shopware6_api_base.lib_shopware6_api_base_cli",
]

LIVE_MODULES = [
    "lib_shopware6_api_base.lib_shopware6_admin_client",
    "lib_shopware6_api_base.lib_shopware6_storefront_client",
]


def _run_doctests(module_name: str, extra: dict[str, object]) -> None:
    """Run every doctest in ``module_name`` with ``extra`` merged into the namespace."""
    module = importlib.import_module(module_name)
    failed, attempted = doctest.testmod(
        module,
        extraglobs=extra,
        optionflags=OPTIONFLAGS,
        verbose=False,
        report=False,
    )
    assert failed == 0, f"{failed}/{attempted} doctests failed in {module_name}"


@pytest.mark.os_agnostic
@pytest.mark.parametrize("module_name", OFFLINE_MODULES)
def test_offline_doctests(module_name: str) -> None:
    """The pure (no-network) module doctests must pass in the unit suite."""
    _run_doctests(module_name, dict(_DOCTEST_NAMES))


@pytest.mark.integration
@pytest.mark.parametrize("module_name", LIVE_MODULES)
def test_client_doctests(module_name: str, docker_test_config: ConfShopware6ApiBase) -> None:
    """The Admin / Storefront client doctests run against the dockware container."""
    extra = dict(_DOCTEST_NAMES)
    # Hand each module its own copy: a doctest that mutates my_config (e.g. _get_token
    # toggling grant_type) cannot then contaminate the shared session fixture.
    extra["my_config"] = docker_test_config.model_copy()
    _run_doctests(module_name, extra)
