import pytest

# Exclude modules whose doctests require a running docker container (integration tests).
# These doctests are designed to run against a live Shopware6 instance.
# Run them explicitly with: pytest --doctest-modules src/lib_shopware6_api_base/lib_shopware6_api_base.py -m integration
collect_ignore: list[str] = [
    "src/lib_shopware6_api_base/lib_shopware6_api_base.py",
]


def pytest_load_initial_conftests(early_config: pytest.Config, parser: pytest.Parser, args: list[str]) -> None:
    additional_pytest_args: list[str] = []
    args[:] = list(set(args + additional_pytest_args))
