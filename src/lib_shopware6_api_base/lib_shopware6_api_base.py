# STDLIB
import sys

# Re-export from http common
from ._http_common import (
    CONTENT_TYPE_JSON,
    DEFAULT_REQUEST_TIMEOUT,
    HEADER_SINGLE_OPERATION,
    HEADER_SW_ACCESS_KEY,
    MAX_RETRY_ATTEMPTS,
    REQUEST_TIMEOUT,
    HEADER_do_not_fail_on_error,
    HEADER_fail_on_error,
    HEADER_index_asynchronously,
    HEADER_index_disabled,
    HEADER_index_synchronously,
    HEADER_write_in_separate_transactions,
    HEADER_write_in_single_transactions,
    PayLoad,
    log_request,
    log_response,
)

# Also export utility functions with underscore names for backward compatibility
from ._http_common import (
    get_payload_dict as _get_payload_dict,
)
from ._http_common import (
    is_type_bytes as _is_type_bytes,
)
from ._http_common import (
    is_type_criteria as _is_type_criteria,
)

# This module now serves as a backward-compatible re-export layer.
# The actual implementations have been split into:
# - _http_common.py: Shared constants and utilities
# - lib_shopware6_storefront_client.py: Storefront API client
# - lib_shopware6_admin_client.py: Admin API client
# Re-export from conf
from .conf_shopware6_api_base_classes import (
    ConfigurationError as ConfigurationError,
)
from .conf_shopware6_api_base_classes import (
    ConfShopware6ApiBase as ConfShopware6ApiBase,
)
from .conf_shopware6_api_base_classes import (
    GrantType,
    HttpMethod,
)
from .conf_shopware6_api_base_classes import (
    ShopwareAPIError as ShopwareAPIError,
)
from .conf_shopware6_api_base_classes import (
    load_config_from_env as load_config_from_env,
)
from .conf_shopware6_api_base_classes import (
    require_config_from_env as require_config_from_env,
)
from .lib_shopware6_admin_client import (
    Shopware6AdminAPIClientBase as Shopware6AdminAPIClientBase,
)

# Re-export from criteria
from .lib_shopware6_api_base_criteria import (
    AggregationType as AggregationType,
)
from .lib_shopware6_api_base_criteria import (
    AggregationTypeName as AggregationTypeName,
)
from .lib_shopware6_api_base_criteria import (
    AscFieldSorting as AscFieldSorting,
)
from .lib_shopware6_api_base_criteria import (
    AvgAggregation as AvgAggregation,
)
from .lib_shopware6_api_base_criteria import (
    ContainsFilter as ContainsFilter,
)
from .lib_shopware6_api_base_criteria import (
    CountAggregation as CountAggregation,
)
from .lib_shopware6_api_base_criteria import (
    Criteria,
)
from .lib_shopware6_api_base_criteria import (
    DateHistogramAggregation as DateHistogramAggregation,
)
from .lib_shopware6_api_base_criteria import (
    DescFieldSorting as DescFieldSorting,
)
from .lib_shopware6_api_base_criteria import (
    EntityAggregation as EntityAggregation,
)
from .lib_shopware6_api_base_criteria import (
    EqualsAnyFilter as EqualsAnyFilter,
)
from .lib_shopware6_api_base_criteria import (
    EqualsFilter as EqualsFilter,
)
from .lib_shopware6_api_base_criteria import (
    FieldSorting as FieldSorting,
)
from .lib_shopware6_api_base_criteria import (
    FilterAggregation as FilterAggregation,
)
from .lib_shopware6_api_base_criteria import (
    FilterOperator as FilterOperator,
)
from .lib_shopware6_api_base_criteria import (
    FilterType as FilterType,
)
from .lib_shopware6_api_base_criteria import (
    FilterTypeName as FilterTypeName,
)
from .lib_shopware6_api_base_criteria import (
    MaxAggregation as MaxAggregation,
)
from .lib_shopware6_api_base_criteria import (
    MinAggregation as MinAggregation,
)
from .lib_shopware6_api_base_criteria import (
    MultiFilter as MultiFilter,
)
from .lib_shopware6_api_base_criteria import (
    NotFilter as NotFilter,
)
from .lib_shopware6_api_base_criteria import (
    PrefixFilter as PrefixFilter,
)
from .lib_shopware6_api_base_criteria import (
    Query as Query,
)
from .lib_shopware6_api_base_criteria import (
    RangeFilter as RangeFilter,
)
from .lib_shopware6_api_base_criteria import (
    RangeParam as RangeParam,
)
from .lib_shopware6_api_base_criteria import (
    SortType as SortType,
)
from .lib_shopware6_api_base_criteria import (
    StatsAggregation as StatsAggregation,
)
from .lib_shopware6_api_base_criteria import (
    SuffixFilter as SuffixFilter,
)
from .lib_shopware6_api_base_criteria import (
    SumAggregation as SumAggregation,
)
from .lib_shopware6_api_base_criteria import (
    TermsAggregation as TermsAggregation,
)
from .lib_shopware6_api_base_criteria import (
    aggregation_names as aggregation_names,
)
from .lib_shopware6_api_base_criteria import (
    equal_filter_type as equal_filter_type,
)
from .lib_shopware6_api_base_criteria import (
    multi_filter_operator as multi_filter_operator,
)
from .lib_shopware6_api_base_criteria import (
    not_filter_operator as not_filter_operator,
)
from .lib_shopware6_api_base_criteria import (
    range_filter as range_filter,
)

# Re-export client classes
from .lib_shopware6_storefront_client import (
    Shopware6StoreFrontClientBase as Shopware6StoreFrontClientBase,
)

__all__ = [
    # Re-exports from conf
    "ConfShopware6ApiBase",
    "ConfigurationError",
    "GrantType",
    "HttpMethod",
    "ShopwareAPIError",
    "load_config_from_env",
    "require_config_from_env",
    # Re-exports from criteria
    "AggregationType",
    "AggregationTypeName",
    "AscFieldSorting",
    "AvgAggregation",
    "ContainsFilter",
    "CountAggregation",
    "Criteria",
    "DateHistogramAggregation",
    "DescFieldSorting",
    "EntityAggregation",
    "EqualsAnyFilter",
    "EqualsFilter",
    "FieldSorting",
    "FilterAggregation",
    "FilterOperator",
    "FilterType",
    "FilterTypeName",
    "MaxAggregation",
    "MinAggregation",
    "MultiFilter",
    "NotFilter",
    "PrefixFilter",
    "Query",
    "RangeFilter",
    "RangeParam",
    "SortType",
    "StatsAggregation",
    "SuffixFilter",
    "SumAggregation",
    "TermsAggregation",
    "aggregation_names",
    "equal_filter_type",
    "multi_filter_operator",
    "not_filter_operator",
    "range_filter",
    # Local exports
    "PayLoad",
    # Module constants
    "DEFAULT_REQUEST_TIMEOUT",
    "MAX_RETRY_ATTEMPTS",
    "CONTENT_TYPE_JSON",
    "HEADER_SW_ACCESS_KEY",
    "HEADER_SINGLE_OPERATION",
    "REQUEST_TIMEOUT",  # Legacy alias
    # Logging hooks
    "log_request",
    "log_response",
    # Header constants
    "HEADER_write_in_separate_transactions",
    "HEADER_write_in_single_transactions",
    "HEADER_index_synchronously",
    "HEADER_index_asynchronously",
    "HEADER_index_disabled",
    "HEADER_fail_on_error",
    "HEADER_do_not_fail_on_error",
    # Client classes
    "Shopware6StoreFrontClientBase",
    "Shopware6AdminAPIClientBase",
    # Backward compatibility (internal functions used by tests)
    "_get_payload_dict",
    "_is_type_bytes",
    "_is_type_criteria",
]


if __name__ == "__main__":
    print(b'this is a library only, the executable is named "lib_shopware6_api_base_cli.py"', file=sys.stderr)  # noqa: T201
