# lib_shopware6_api_base

<!-- Badges -->
[![CI](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/default_cicd_public.yml/badge.svg)](https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/default_cicd_public.yml)
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


this is a basic API client for shopware6 which can be used on windows, Linux, MacOs.
It supports all available authorisation types to the Admin and Storefront API.
Paginated requests are supported.

This is only the basic abstraction layer, to enjoy higher level functions, check out "lib_shopware6_api"

On github it can be only tested on linux, because we can not run a docker shopware container service on MacOS or Windows.

---

Python version required: 3.10+

---

- [Usage](#usage)
- [Usage from Commandline](#usage-from-commandline)
- [Install - recommended via uv](#install---recommended-via-uv)
- [Requirements](#requirements)
- [Acknowledgements](#acknowledgements)
- [Contribute](#contribute)
- [Report Issues](https://github.com/bitranox/lib_shopware6_api_base/blob/master/ISSUE_TEMPLATE.md)
- [Pull Request](https://github.com/bitranox/lib_shopware6_api_base/blob/master/PULL_REQUEST_TEMPLATE.md)
- [Code of Conduct](https://github.com/bitranox/lib_shopware6_api_base/blob/master/CODE_OF_CONDUCT.md)
- [License](#license)
- [Changelog](#changelog)

---

## Usage

- [configuration](#configuration)
- [methods](#methods)
- [headers](#headers)
- [Store API](#store-api)
- [Admin API](#admin-api)
- [Query Syntax](#query-syntax)
    - [Aggregations](#aggregations)
        - [AvgAggregation](#avgaggregation)
        - [CountAggregation](#countaggregation)
        - [MaxAggregation](#maxaggregation)
        - [MinAggregation](#minaggregation)
        - [SumAggregation](#sumaggregation)
        - [StatsAggregation](#statsaggregation)
        - [TermsAggregation](#termsaggregation)
        - [FilterAggregation](#filteraggregation)
        - [EntityAggregation](#entityaggregation)
        - [DateHistogramAggregation](#datehistogramaggregation)
        - [NestingAggregations](#nestingaggregations)
    - [Associations](#associations)
    - [Filters](#filters)
        - [EqualsFilter](#equalsfilter)
        - [EqualsAnyFilter](#equalsanyfilter)
        - [ContainsFilter](#containsfilter)
        - [RangeFilter](#rangefilter)
        - [NotFilter](#notfilter)
        - [MultiFilter](#multifilter)
        - [PrefixFilter](#prefixfilter)
        - [SuffixFilter](#suffixfilter)
    - [Grouping](#grouping)
    - [ids](#ids)
    - [includes](#includes)
    - [page & limit](#page--limit)
    - [Query](#query)
    - [Sort](#sort)
        - [FieldSorting](#fieldsorting)
        - [AscFieldSorting](#ascfieldsorting)
        - [DescFieldSorting](#descfieldsorting)

### configuration

the configuration is passed to the client as a configuration object of the type "ConfShopware6ApiBase"
simply copy the Class definition of "ConfShopware6ApiBase" and create Your own configuration file, for instance "my_shop_config.py"

```python
import attrs


@attrs.define
class ConfShopware6ApiBase(object):
    # the api url, like : 'https://shop.yourdomain.com/api'
    shopware_admin_api_url: str = ""
    # the storefront api url, like : 'https://shop.yourdomain.com/store-api'
    shopware_storefront_api_url: str = ""

    """
    Admin API:
    for User Credentials Grant Type:
    ==================================
    - with refresh token
    - we recommend to only use this grant flow for client applications that should
      perform administrative actions and require a user-based authentication

    """
    username: str = ""
    password: str = ""

    """
    Admin API:
    for Resource Owner Password Grant Type:
    =======================================
    - no refresh token
    - should be used for machine-to-machine communications, such as CLI jobs or automated services
    see https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
    setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
    or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index
    """
    # the client ID, setup at Web Administration Interface > settings > system > integration > access_id
    client_id: str = ""
    # the client secret, setup at Web Administration Interface > settings > system > integration > access_secret
    client_secret: str = ""

    """
    Admin API:
    Grant Type to use:
    ==================
    which grant type to use - can be either 'user_credentials'- or 'resource_owner'
    """
    grant_type: str = ""

    """
    Store API:
    sw-access-key set in Administration/Sales Channels/API
    """
    store_api_sw_access_key: str = ""
```

now You can use this configuration:

```python
from lib_shopware6_api_base import Shopware6AdminAPIClientBase
from my_shop_config import ConfShopware6ApiBase

my_conf = ConfShopware6ApiBase()
my_api_client = Shopware6AdminAPIClientBase(config=my_conf)
...
```

- test configuration

for testing we use the dockware docker container,
see : [dockware](https://developer.shopware.com/docs/guides/installation/dockware)

on gitHub actions the dockware docker test container is installed as a service and is available
for communication on localhost

You can start the dockware container locally with the command : sudo docker run -d --rm -p 80:80 --name dockware dockware/dev:latest

Test configuration is handled by pytest fixtures in the test suite.

### methods

please note, that on github actions the test configuration is used automatically,
therefore on all examples no configuration is passed on purpose.

methods which take the parameter 'payload', the payload is of following type :

PayLoad = Union[None, Dict[str, Any], Criteria]

for the definition of "Criteria" see [Query Syntax](#query-syntax)

### headers

Endpoints like `/api/_action/sync` require request specific custom headers to manipulate the api behavior

see : [Bulk Payloads Performance](https://shopware.stoplight.io/docs/admin-api/faf8f8e4e13a0-bulk-payloads#performance) and [Bulk edit entities](https://shopware.stoplight.io/docs/admin-api/0612cb5d960ef-bulk-edit-entities) in the Admin API Documentation

You may pass such custom header fields like that :

```python
# only for python version >= 3.8:
update_header_fields = HEADER_write_in_single_transactions | HEADER_index_asynchronously

#   or the same for python 3.7:
update_header_fields: dict = dict()
update_header_fields.update(HEADER_index_asynchronously)
update_header_fields.update(HEADER_write_in_single_transactions)

#   or the same written explicitly for python 3.7:
update_heater_fields = {'single-operation' : 'true', 'indexing-behavior' : 'use-queue-indexing'}

# and pass those "update_heater_fields" to the request method parameter
# (mostly "request_post", with endpoint "/api/_action/sync")
```

following header fields are pre-defined :

```python
HEADER_write_in_separate_transactions: Dict[str, str] = {"single-operation": "false"}  # default
HEADER_write_in_single_transactions: Dict[str, str] = {"single-operation": "true"}
HEADER_index_synchronously: Dict[str, str] = {"indexing-behavior": "null"}  # default
HEADER_index_asynchronously: Dict[str, str] = {"indexing-behavior": "use-queue-indexing"}
HEADER_index_disabled: Dict[str, str] = {"indexing-behavior": "disable-indexing"}
HEADER_fail_on_error: Dict[str, str] = {"fail-on-error": "true"}  # default
HEADER_do_not_fail_on_error: Dict[str, str] = {"fail-on-error": "false"}
```

### Store API

```python
class Shopware6StoreFrontClientBase(object):
    def __init__(self, config: ConfShopware6ApiBase) -> None:
        """
        the Shopware6 Storefront Base API

        :param config: Configuration object with API credentials and URLs.

        >>> from lib_shopware6_api_base import ConfShopware6ApiBase
        >>> my_config = ConfShopware6ApiBase(
        ...     shopware_storefront_api_url="https://shop.example.com/store-api",
        ...     store_api_sw_access_key="SWSC..."
        ... )
        >>> my_storefront_client = Shopware6StoreFrontClientBase(config=my_config)

        """
```

- Store API Get

```python
    def request_get(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_storefront_client = Shopware6StoreFrontClientBase()

        >>> # test GET a dictionary
        >>> my_response = my_storefront_client.request_get(request_url='context')

        >>> # test GET a List
        >>> my_response = my_storefront_client.request_get(request_url='sitemap')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: received a list instead of a dict - You need to use the method request_get_list

        """
```

- Store API Get List

```python
    def request_get_list(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        make a get request, expecting a list of dictionaries as result

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            List[response_dict]: a list of dictionaries

        >>> # Setup
        >>> my_storefront_client = Shopware6StoreFrontClientBase()

        >>> # test GET a List
        >>> my_response = my_storefront_client.request_get_list(request_url='sitemap')

        >>> # test GET a dictionary
        >>> my_response = my_storefront_client.request_get_list(request_url='context')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: received a dict instead of a list - You need to use the method request_get


        """
```

- Store API Patch

```python
    def request_patch(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

- Store API Post

```python
    def request_post(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_storefront_client = Shopware6StoreFrontClientBase()

        >>> # test POST without payload
        >>> my_response = my_storefront_client.request_post(request_url='product')
        >>> assert 'elements' in my_response

        >>> # test POST with payload
        >>> # see : https://shopware.stoplight.io/docs/store-api/b3A6ODI2NTY4MQ-fetch-a-list-of-products
        >>> my_payload = Criteria()
        >>> my_payload.filter.append(EqualsFilter(field='active', value='true'))
        >>> my_response = my_storefront_client.request_post(request_url='product', payload=my_payload)
        >>> assert 'elements' in my_response

        """
```

- Store API Put

```python
    def request_put(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

- Store API Delete

```python
    def request_delete(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

### Admin API

```python
class Shopware6AdminAPIClientBase(object):
    def __init__(self, config: ConfShopware6ApiBase) -> None:
        """
        the Shopware6 Admin Base API

        :param config: Configuration object with API credentials and URLs.

        >>> from lib_shopware6_api_base import ConfShopware6ApiBase
        >>> my_config = ConfShopware6ApiBase(
        ...     shopware_admin_api_url="https://shop.example.com/api",
        ...     username="admin",
        ...     password="secret"
        ... )
        >>> my_api_client = Shopware6AdminAPIClientBase(config=my_config)

        """
```

- Admin API GET

```python
    def request_get(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        makes a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # test resource owner token
        >>> ignore = my_api_client._get_access_token_by_user_credentials()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client.request_get('customer-group')  # noqa

        >>> # test resource owner token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client.request_get('customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        >>> # Test client credentials token
        >>> ignore = my_api_client._get_access_token_by_resource_owner()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client.request_get('customer-group')  # noqa

        >>> # test client credentials token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client.request_get('customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        """
```

- Admin API GET Paginated

```python
    def request_get_paginated(
        self, request_url: str, payload: PayLoad = None, junk_size: int = 100, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        get the data paginated - metadata 'total' and 'totalCountMode' will be updated
        the paginated request reads those records in junks of junk_size=100 for performance reasons.

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        payload "page" will be ignored

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            limit : the junk size
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, no limit
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', junk_size=3)
        >>> assert 3 < len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 2
        >>> my_payload={'limit': 2}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 2 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        >>> # test read product junk_size=10, limit = None
        >>> my_payload=Criteria()
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=10)
        >>> assert 5 < len(my_response_dict['data'])
        """
```

- Admin API PATCH

```python
    def request_patch(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

- Admin API POST

```python
    def request_post(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

- Admin API POST PAGINATED

```python
    def request_post_paginated(
        self, request_url: str, payload: PayLoad = None, junk_size: int = 100, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        post the data paginated - metadata 'total' and 'totalCountMode' will be updated
        if You expect a big number of records, the paginated request reads those records in junks of junk_size=100 for performance reasons.

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        payload "page" will be ignored

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            junk_size : the junk size
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_url = 'search/product'

        >>> # test read product junk_size=10, limit = None
        >>> my_payload=Criteria()
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=10)
        >>> assert 5 < len(my_response_dict['data'])

        >>> # test read product junk_size=10, no limit
        >>> my_payload=None
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=10)
        >>> assert 10 < len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 2
        >>> my_payload={'limit': 2}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=3)
        >>> assert 2 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        >>> # search for orders
        >>> # test https://github.com/bitranox/lib_shopware6_api_base/issues/11
        >>> import pprint
        >>> date_from = '2024-09-29T00:00:00.000Z'
        >>> date_to = '2024-09-29T23:59:59.999Z'
        >>> my_criteria = Criteria()
        >>> my_criteria.filter.append(RangeFilter(field="orderDate", parameters = {'gte': date_from, 'lte': date_to}))
        >>> my_criteria.filter.append(MultiFilter('or', [
        ...     EqualsFilter(field='documents.documentType.technicalName', value='invoice'),
        ...     EqualsFilter(field='documents.documentType.technicalName', value='storno')]))
        >>> pprint_attrs(my_criteria)
        {'limit': None,
         'page': None,
         'filter': [{'type': 'range',
                     'field': 'orderDate',
                     'parameters': {'gte': '2024-09-29T00:00:00.000Z',
                                    'lte': '2024-09-29T23:59:59.999Z'}},
                    {'type': 'multi',
                     'operator': 'or',
                     'queries': [{'type': 'equals',
                                  'field': 'documents.documentType.technicalName',
                                  'value': 'invoice'},
                                 {'type': 'equals',
                                  'field': 'documents.documentType.technicalName',
                                  'value': 'storno'}]}],
         'term': None,
         'total_count_mode': None}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url='search/order', payload=my_criteria)
        >>> pprint.pprint(my_response_dict)
        {'data': []}
        """
```

- Admin API PUT

```python
    def request_put(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

- Admin API DELETE

```python
    def request_delete(
        self,
        request_url: str,
        payload: PayLoad = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
```

## Query Syntax

The querying syntax closely resembling the one from the internal DAL.
If you're familiar with Shopware 6 DAL syntax and how to retrieve it,
you might see the examples are predictable and straightforward

a search criteria follows the following schema:

```python
@attrs.define
class Criteria:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries

    structure of Criteria:

    parameter:

    aggregations  List[Aggregation]                    Specify aggregations to be computed on-the-fly
    associations  Dict['<name>', 'Criteria']           Allows to load additional data to the standard data of an entity
    filter        List[Filter]                         Allows you to filter the result and aggregations
    grouping      List['<fieldname>']                  allows you to group the result over fields
    ids           List['<id>']                         Limits the search to a list of Ids
    includes      Dict['apiAlias', List[<fieldname>]]  Restricts the output to the defined fields
    limit         Optional[int]                        Defines the number of entries to be determined
    page          Optional[int]                        Defines at which page the search result should start
    post-filter                           not implemented at the moment
    query         List[Query]                          Enables you to determine a ranking for the search result
    sort          List[Sort]                           Defines the sorting of the search result
    term          Optional[str]                        text search on all records based on their data model and weighting
                                                       Don't use term parameters together with query parameters.
    total-count-mode    Optional[int]                  Defines whether a total must be determined


    >>> # Test empty
    >>> my_criteria = Criteria()
    >>> pprint_attrs(my_criteria)
    {'limit': None, 'page': None, 'term': None, 'total_count_mode': None}

    >>> # Test Average aggregation
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=1
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> my_criteria.aggregations = [AvgAggregation('average-price', 'price')]
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'page': None,
     'aggregations': [{'name': 'average-price', 'type': 'avg', 'field': 'price'}],
     'includes': {'product': ['id', 'name']},
     'term': None,
     'total_count_mode': None}

    >>> # Test Filter aggregation
    >>> my_criteria = Criteria(limit=1, includes={'product':['id', 'name']},
    ...     aggregations=[FilterAggregation(name='active-price-avg',
    ...                                    filter=[EqualsFilter(field='active', value=True)],
    ...                                    aggregation=AvgAggregation(name='avg-price',field='price'))])
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'page': None,
     'aggregations': [{'name': 'active-price-avg',
                       'type': 'filter',
                       'filter': [{'type': 'equals',
                                   'field': 'active',
                                   'value': True}],
                       'aggregation': {'name': 'avg-price',
                                       'type': 'avg',
                                       'field': 'price'}}],
     'includes': {'product': ['id', 'name']},
     'term': None,
     'total_count_mode': None}

    >>> # Test Association
    >>> my_criteria = Criteria()
    >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter('active', 'true')])
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'associations': {'products': {'limit': 5,
                                   'page': None,
                                   'filter': [{'type': 'equals',
                                               'field': 'active',
                                               'value': 'true'}],
                                   'term': None,
                                   'total_count_mode': None}},
     'term': None,
     'total_count_mode': None}

    >>> # Test append filters
    >>> my_criteria = Criteria()
    >>> my_criteria.page = 0
    >>> my_criteria.limit=1
    >>> my_criteria.filter.append(EqualsFilter('a', 'a'))
    >>> my_criteria.filter.append(EqualsFilter('b', 'b'))
    >>> my_criteria.filter.append(EqualsFilter('d', 'd'))
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'page': 0,
     'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                {'type': 'equals', 'field': 'b', 'value': 'b'},
                {'type': 'equals', 'field': 'd', 'value': 'd'}],
     'term': None,
     'total_count_mode': None}

    >>> # Test set filters
    >>> my_criteria = Criteria()
    >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                {'type': 'equals', 'field': 'b', 'value': 'b'},
                {'type': 'equals', 'field': 'd', 'value': 'd'}],
     'term': None,
     'total_count_mode': None}

    >>> # Test Grouping
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=5
    >>> my_criteria.grouping=['active']
    >>> pprint_attrs(my_criteria)
    {'limit': 5,
     'page': None,
     'grouping': ['active'],
     'term': None,
     'total_count_mode': None}

    >>> # Test ids
    >>> # note that the limit is automatically set to 3, and page to 1, which is for our paginated request
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'ids': ['012cd563cf8e4f0384eed93b5201cc98',
             '075fb241b769444bb72431f797fd5776',
             '090fcc2099794771935acf814e3fdb24'],
     'term': None,
     'total_count_mode': None}

    >>> # Test ids with a limit already set, which should fail
    >>> # You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids
    >>> my_criteria = Criteria()
    >>> my_criteria.limit = 5
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    Traceback (most recent call last):
        ...
    ValueError: You can use either "limit" or "ids", but not both, ...

    >>> # Test to set limit after ids are passed, which should fail
    >>> # You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> my_criteria.limit = 2
    Traceback (most recent call last):
        ...
    ValueError: You can use either "limit" or "ids", but not both, ...

    >>> # Test includes
    >>> my_criteria = Criteria()
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'includes': {'product': ['id', 'name']},
     'term': None,
     'total_count_mode': None}

    >>> my_criteria = Criteria(page=1, limit=5)
    >>> pprint_attrs(my_criteria)
    {'limit': 5, 'page': 1, 'term': None, 'total_count_mode': None}

    >>> # Test Query
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'query': [{'score': 500,
                'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
               {'score': 500,
                'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
               {'score': 100,
                'query': {'type': 'equals',
                          'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}],
     'term': None,
     'total_count_mode': None}

    >>> # Test Sorting
    >>> my_criteria = Criteria(limit=5,
    ...                        sort=[FieldSorting('name', 'ASC', True),
    ...                              DescFieldSorting('active')])
    >>> pprint_attrs(my_criteria)
    {'limit': 5,
     'page': None,
     'sort': [{'field': 'name', 'order': 'ASC', 'naturalSorting': True},
              {'field': 'active', 'order': 'DESC', 'naturalSorting': None}],
     'term': None,
     'total_count_mode': None}

    """
```

### Aggregations

back to [Query Syntax](#query-syntax)

- [AvgAggregation](#avgaggregation)
- [CountAggregation](#countaggregation)
- [MaxAggregation](#maxaggregation)
- [MinAggregation](#minaggregation)
- [SumAggregation](#sumaggregation)
- [StatsAggregation](#statsaggregation)
- [TermsAggregation](#termsaggregation)
- [FilterAggregation](#filteraggregation)
- [EntityAggregation](#entityaggregation)
- [DateHistogramAggregation](#datehistogramaggregation)
- [NestingAggregations](#nestingaggregations)

#### AvgAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class AvgAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The Avg aggregation makes it possible to calculate the average value for a field.
    The following SQL statement is executed in the background: AVG(price).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = AvgAggregation('avg-price', 'price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'avg-price', 'type': 'avg', 'field': 'price'}

    """
```

#### CountAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class CountAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The count aggregation makes it possible to determine the number of entries for a field that are filled with a value.
    The following SQL statement is executed in the background: COUNT(DISTINCT(manufacturerId)).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = CountAggregation('count-manufacturers', 'manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'count-manufacturers', 'type': 'count', 'field': 'manufacturerId'}

    """
```

#### MaxAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class MaxAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The max aggregation allows you to determine the maximum value of a field.
    The following SQL statement is executed in the background: MAX(price).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = MaxAggregation('max-price', 'price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'max-price', 'type': 'max', 'field': 'price'}

    """
```

#### MinAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class MinAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The min aggregation makes it possible to determine the minimum value of a field.
    The following SQL statement is executed in the background: MIN(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = MinAggregation('min-price', 'price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'min-price', 'type': 'min', 'field': 'price'}

    """
```

#### SumAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class SumAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The sum aggregation makes it possible to determine the total of a field.
    The following SQL statement is executed in the background: SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = SumAggregation('sum-price', 'price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'sum-price', 'type': 'sum', 'field': 'price'}

    """
```

#### StatsAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class StatsAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The stats aggregation makes it possible to calculate several values at once for a field.
    This includes the previous max, min, avg and sum aggregation.
    The following SQL statement is executed in the background: SELECT MAX(price), MIN(price), AVG(price), SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = StatsAggregation('stats-price', 'price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'stats-price', 'type': 'stats', 'field': 'price'}

    """
```

#### TermsAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class TermsAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The terms aggregation belongs to the bucket aggregations.
    This allows you to determine the values of a field.
    The result contains each value once and how often this value occurs in the result.
    The terms aggregation also supports the following parameters:
        limit - Defines a maximum number of entries to be returned (default: zero)
        sort - Defines the order of the entries. By default the following is not sorted
        aggregation - Enables you to calculate further aggregations for each key
    The following SQL statement is executed in the background: SELECT DISTINCT(manufacturerId) as key, COUNT(manufacturerId) as count


    :parameter:
        name: str
        field: str
        sort: Optional[SortType]
        limit: Optional[int]
        aggregation: Optional[]

    >>> # Test
    >>> my_aggregation = TermsAggregation(name='manufacturer-ids', limit=3, sort=DescFieldSorting('manufacturer.name'), field='manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'manufacturer-ids',
     'type': 'terms',
     'field': 'manufacturerId',
     'sort': {'field': 'manufacturer.name',
              'order': 'DESC',
              'naturalSorting': None},
     'limit': 3,
     'aggregation': None}

    """
```

#### FilterAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class FilterAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The filter aggregation belongs to the bucket aggregations.
    Unlike all other aggregations, this aggregation does not determine any result, it cannot be used alone.
    It is only used to further restrict the result of an aggregation in a criterion.
    Filters which defined inside the filter property of this aggregation type,
    are only used when calculating this aggregation.
    The filters have no effect on other aggregations or on the result of the search.

    parameter:
        name: str
        sort: SortType
        filter: List of FilterType
        aggregation : AggregationType

    >>> # Test
    >>> my_aggregation = FilterAggregation(
    ...     name='active-price-avg',
    ...     filter=[EqualsFilter(field='active', value=True)],
    ...     aggregation=AvgAggregation(name='avg-price',field='price'))
    >>> pprint_attrs(my_aggregation)
    {'name': 'active-price-avg',
     'type': 'filter',
     'filter': [{'type': 'equals', 'field': 'active', 'value': True}],
     'aggregation': {'name': 'avg-price', 'type': 'avg', 'field': 'price'}}

    """
```

#### EntityAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class EntityAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The entity aggregation is similar to the terms aggregation, it belongs to the bucket aggregations.
    As with terms aggregation, all unique values are determined for a field.
    The aggregation then uses the determined keys to load the defined entity. The keys are used here as ids.

    :parameter:
        name: str
        definition: str
        field: str

    >>> # Test
    >>> my_aggregation = EntityAggregation(name='manufacturers', definition='product_manufacturer', field='manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'manufacturers',
     'type': 'entity',
     'definition': 'product_manufacturer',
     'field': 'manufacturerId'}
    """
```

#### DateHistogramAggregation

back to [Aggregations](#aggregations)

```python
@attrs.define
class DateHistogramAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The histogram aggregation is used as soon as the data to be determined refers to a date field.
    With the histogram aggregation,
    one of the following date intervals can be given: minute, hour, day, week, month, quarter, year, day.
    This interval groups the result and calculates the corresponding count of hits.

    :parameter:
        name: str
        field: str
        interval: str ,  possible values: 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year', 'day'

    >>> # Test
    >>> my_aggregation = DateHistogramAggregation(name='release-dates', field='releaseDate', interval='month')
    >>> pprint_attrs(my_aggregation)
    {'name': 'release-dates',
     'type': 'histogram',
     'field': 'releaseDate',
     'interval': 'month'}

    """
```

#### NestingAggregations

back to [Aggregations](#aggregations)

```python
"""
see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference#nesting-aggregations
"""
```

### Associations

back to [Query Syntax](#query-syntax)

The associations parameter allows you to load additional data to the minimal data set
of an entity without sending an extra request - similar to a SQL Join.
The key of the parameter is the property name of the association in the entity.
You can pass a nested criteria just for that association - e.g. to perform a sort
to or apply filters within the association.

```python
    >>> # Test Association
    >>> my_criteria = Criteria()
    >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter('active', 'true')])
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'associations': {'products': {'limit': 5,
                                   'page': None,
                                   'filter': [{'type': 'equals',
                                               'field': 'active',
                                               'value': 'true'}],
                                   'term': None,
                                   'total_count_mode': None}},
     'term': None,
     'total_count_mode': None}
    >>>
```

### Filters

back to [Query Syntax](#query-syntax)

- [EqualsFilter](#equalsfilter)
- [EqualsAnyFilter](#equalsanyfilter)
- [ContainsFilter](#containsfilter)
- [RangeFilter](#rangefilter)
- [NotFilter](#notfilter)
- [MultiFilter](#multifilter)
- [PrefixFilter](#prefixfilter)
- [SuffixFilter](#suffixfilter)

#### EqualsFilter

back to [Filters](#filters)

```python
@attrs.define
class EqualsFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Equals filter allows you to check fields for an exact value.
    The following SQL statement is executed in the background: WHERE stock = 10.

    :parameter:
        field: str
        value: Union[str, int]      # probably also bool

    >>> # Test
    >>> my_filter = EqualsFilter('stock', 10)
    >>> pprint_attrs(my_filter)
    {'type': 'equals', 'field': 'stock', 'value': 10}

    >>> my_filter = EqualsFilter('stock', None)
    >>> pprint_attrs(my_filter)
    {'type': 'equals', 'field': 'stock', 'value': None}

    """
```

#### EqualsAnyFilter

back to [Filters](#filters)

```python
@attrs.define
class EqualsAnyFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The EqualsAny filter allows you to filter a field where at least one of the defined values matches exactly.
    The following SQL statement is executed in the background:
    WHERE productNumber IN ('3fed029475fa4d4585f3a119886e0eb1', '77d26d011d914c3aa2c197c81241a45b').

    :parameter:
        field: str
        value: List[str]

    >>> # Test Keyword param
    >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pprint_attrs(my_filter)
    {'type': 'equalsAny',
     'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b']}

    >>> # Test positional param
    >>> my_filter = EqualsAnyFilter('productNumber', ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pprint_attrs(my_filter)
    {'type': 'equalsAny',
     'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b']}

    """
```

#### ContainsFilter

back to [Filters](#filters)

```python
@attrs.define
class ContainsFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Contains Filter allows you to filter a field to an approximate value, where the passed value must be contained as a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight%'.

    :parameter:
        field: str
        value: List[str]

    >>> # Test
    >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
    >>> pprint_attrs(my_filter)
    {'type': 'contains', 'field': 'productNumber', 'value': 'Lightweight'}

    """
```

#### RangeFilter

back to [Filters](#filters)

```python
@attrs.define
class RangeFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Range filter allows you to filter a field to a value space. This can work with date or numerical values.
    Within the parameter property the following values are possible:
        gte => Greater than equals  (You might pass 'gte' or range_filter.gte)
        lte => Less than equals     (You might pass 'lte' or range_filter.lte)
        gt => Greater than          (You might pass 'gt' or range_filter.gt)
        lt => Less than             (You might pass 'lt' or range_filter.lt)

    :parameter:
        field: str
        parameters: Dict[str, Union[int, datetime]]

    >>> # Test (pass range type as string)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
    >>> pprint_attrs(my_filter)
    {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

    >>> # Test (pass range type from 'range_filter' object)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.gte: 20, range_filter.lte: 30})
    >>> pprint_attrs(my_filter)
    {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

    >>> # Test (wrong range)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
    Traceback (most recent call last):
        ...
    ValueError: "less" is not a valid range

    """
```

#### NotFilter

back to [Filters](#filters)

```python
@attrs.define
class NotFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Not Filter is a container which allows to negate any kind of filter.
    The operator allows you to define the combination of queries within the NOT filter ("OR" and "AND").
    The following SQL statement is executed in the background: WHERE !(stock = 1 OR availableStock = 1):

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Test (pass operator as string)
    >>> my_filter = NotFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pprint_attrs(my_filter)
    {'type': 'not',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = NotFilter(not_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pprint_attrs(my_filter)
    {'type': 'not',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test unknown operator
    >>> my_filter = NotFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    Traceback (most recent call last):
        ...
    ValueError: ("'operator' must be in ['and', 'or'] (got 'duck')", ...)

    """
```

#### MultiFilter

back to [Filters](#filters)

```python
@attrs.define
class MultiFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Multi Filter is a container, which allows to set logical links between filters.
    The operator allows you to define the links between the queries within the Multi filter ("OR" and "AND").
    The following SQL statement is executed in the background: WHERE (stock = 1 OR availableStock = 1)

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Test (pass operator as string)
    >>> my_filter = MultiFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pprint_attrs(my_filter)
    {'type': 'multi',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = MultiFilter(multi_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pprint_attrs(my_filter)
    {'type': 'multi',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test unknown operator
    >>> my_filter = MultiFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    Traceback (most recent call last):
        ...
    ValueError: ("'operator' must be in ['and', 'or'] (got 'duck')", ...)

    """
```

#### PrefixFilter

back to [Filters](#filters)

```python
@attrs.define
class PrefixFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Prefix Filter allows you to filter a field to an approximate value, where the passed value must be the start of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE 'Lightweight%'.

    :parameter:
        field: str
        value: str

    >>> # Test
    >>> my_filter = PrefixFilter('name', 'Lightweight')
    >>> pprint_attrs(my_filter)
    {'type': 'prefix', 'field': 'name', 'value': 'Lightweight'}

    """
```

#### SuffixFilter

back to [Filters](#filters)

```python
@attrs.define
class SuffixFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Suffix Filter allows you to filter a field to an approximate value, where the passed value must be the end of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight'.

    :parameter:
        field: str
        value: str

    >>> # Test
    >>> my_filter = SuffixFilter('name', 'Lightweight')
    >>> pprint_attrs(my_filter)
    {'type': 'suffix', 'field': 'name', 'value': 'Lightweight'}

    """
```

### Grouping

back to [Query Syntax](#query-syntax)

The grouping parameter allows you to group the result over fields.
It can be used to realise queries such as:

- Fetch one product for each manufacturer
- Fetch one order per day and customer

```python
    >>> # Test Grouping
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=5
    >>> my_criteria.grouping=['active']
    >>> pprint_attrs(my_criteria)
    {'limit': 5,
     'page': None,
     'grouping': ['active'],
     'term': None,
     'total_count_mode': None}
    >>>
```

### ids

back to [Query Syntax](#query-syntax)

If you want to perform a simple lookup using just the ids of records,
you can pass a list of those using the ids field.
Please note that as soon as You use ids, limit and page does not apply anymore !

```python
    >>> # Test ids
    >>> # note that the limit is automatically set to 3, and page to 1, which is for our paginated request
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'ids': ['012cd563cf8e4f0384eed93b5201cc98',
             '075fb241b769444bb72431f797fd5776',
             '090fcc2099794771935acf814e3fdb24'],
     'term': None,
     'total_count_mode': None}

    >>> # Test ids with a limit already set, which should fail
    >>> # You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids
    >>> my_criteria = Criteria()
    >>> my_criteria.limit = 5
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    Traceback (most recent call last):
        ...
    ValueError: You can use either "limit" or "ids", but not both, ...

    >>> # Test to set limit after ids are passed, which should fail
    >>> # You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> my_criteria.limit = 2
    Traceback (most recent call last):
        ...
    ValueError: You can use either "limit" or "ids", but not both, ...

    >>>
```

### includes

back to [Query Syntax](#query-syntax)

The includes parameter allows you to restrict the returned fields.

Transfer only what you need - reduces response payload
Easier to consume for client applications
When debugging, the response is smaller and you can concentrate on the essential fields

```python
    >>> # Test includes
    >>> my_criteria = Criteria()
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'includes': {'product': ['id', 'name']},
     'term': None,
     'total_count_mode': None}

    >>>
```

All response types come with a apiAlias field which you can use to identify the
type in your includes field.

If you only want a categories id, add: "category": ["id"].

For entities, this is the entity name: product, product_manufacturer, order_line_item, ...

For other non-entity-types like a listing result or a line item, check the full response.
This pattern applies not only to simple fields but also to associations.

### page & limit

back to [Query Syntax](#query-syntax)

The page and limit parameters can be used to control pagination. The page parameter is 1-indexed.
Please note that as soon as You use ids, limit and page does not apply anymore !

```python
    >>> my_criteria = Criteria(page=1, limit=5)
    >>> pprint_attrs(my_criteria)
    {'limit': 5, 'page': 1, 'term': None, 'total_count_mode': None}

    >>>
```

### Query

back to [Query Syntax](#query-syntax)

Use this parameter to create a weighted search query that returns a _score for each found entity.
Any filter type can be used for the query. A score has to be defined for each query.
The sum of the matching queries then results in the total _score value.

```python
@attrs.define
class Query:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#query
    Enables you to determine a ranking for the search result
    Use this parameter to create a weighted search query that returns a _score for each found entity.
    Any filter type can be used for the query. A score has to be defined for each query.
    The sum of the matching queries then results in the total _score value.

    parameter
        score   int
        query   FilterType

    >>> # Test
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])

    >>> pprint_attrs(my_criteria)
    {'limit': None,
     'page': None,
     'query': [{'score': 500,
                'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
               {'score': 500,
                'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
               {'score': 100,
                'query': {'type': 'equals',
                          'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}],
     'term': None,
     'total_count_mode': None}

    """
```

### Sort

back to [Query Syntax](#query-syntax)

The sort parameter allows to control the sorting of the result.
Several sorts can be transferred at the same time.

The field parameter defines which field is to be used for sorting.
The order parameter defines the sort direction.
The parameter naturalSorting allows to use a Natural Sorting Algorithm

#### FieldSorting

```python
@attrs.define
class FieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        order : str "ASC" or "DESC"
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = FieldSorting('name', 'ASC', True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

    """
```

#### AscFieldSorting

```python
@attrs.define
class AscFieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = AscFieldSorting('name', True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

    """
```

#### DescFieldSorting

```python
@attrs.define
class DescFieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = DescFieldSorting('name', True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'order': 'DESC', 'naturalSorting': True}

    """
```

## Usage from Commandline

```
Usage: lib_shopware6_api_base [OPTIONS] COMMAND [ARGS]...

  python3 base API client for shopware6

Options:
  --version                     Show the version and exit.
  --traceback / --no-traceback  return traceback information on cli
  -h, --help                    Show this message and exit.

Commands:
  info  get program information
```

## Install - recommended via uv

[uv](https://docs.astral.sh/uv/) is an ultrafast Python package manager written in Rust (10-20x faster than pip/poetry).

### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### One-shot run (no install needed)

```bash
uvx lib_shopware6_api_base@latest --help
```

### Persistent install as CLI tool

```bash
# install the CLI tool (isolated environment, added to PATH)
uv tool install lib_shopware6_api_base

# upgrade to latest
uv tool upgrade lib_shopware6_api_base
```

### Install as project dependency

```bash
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
uv pip install lib_shopware6_api_base
```

For alternative install paths (pip, pipx, source builds, etc.), see
[INSTALL.md](INSTALL.md). All supported methods register both the
`lib_shopware6_api_base` and `lib-shopware6-api-base` commands on your PATH.

## Requirements

following modules will be automatically installed :

```
## Project Requirements
pydantic>=2.0.0
pydantic-settings>=2.0.0
rich-click
lib_cli_exit_tools
oauthlib
orjson
requests
requests-oauthlib
```

## Acknowledgements

- special thanks to "uncle bob" Robert C. Martin, especially for his books on "clean code" and "clean architecture"

## Contribute

I would love for you to fork and send me pull request for this project.
- [please Contribute](https://github.com/bitranox/lib_shopware6_api_base/blob/master/CONTRIBUTING.md)

## License

This software is licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License)

---

## Changelog

- new MAJOR version for incompatible API changes,
- new MINOR version for added functionality in a backwards compatible manner
- new PATCH version for backwards compatible bug fixes

### v2.1.9

2024-09-29:
- add graalpy tests

### v2.1.8

2024-09-29:
- add example for /search/order via post request

### v2.1.7

2023-10-18:
- validator for "Criteria.ids" and "Criteria.limit"
- if "Criteria.ids" are passed, set "limits" to the number of ids
- prevent that "Criteria.limits" and "Criteria.ids" are set simultaneous
- bump up coverage

### v2.1.6

2023-10-18:
- correcting "Filter Aggregation", some typos correction

### v2.1.5

2023-10-18:
- get rid of special pretty printer version "pprint3x" for python 3.7 and below
- correcting type hint for filter "ContainsFilter"

### v2.1.4

2023-10-18:
- correct EqualsAnyFilter, thanks to Patrik Hofmann for finding that bug.

### v2.1.3

2023-07-14:
- add codeql badge
- move 3rd_party_stubs outside the src directory to `./.3rd_party_stubs`
- add pypy 3.10 tests
- add python 3.12-dev tests

### v2.1.2

2023-07-13:
- require minimum python 3.8
- remove python 3.7 tests

### v2.1.1

2023-07-13:
- introduce PEP517 packaging standard
- introduce pyproject.toml build-system
- remove setup.cfg
- remove setup.py
- update black config
- clean ./tests/test_cli.py

### v2.1.0

2023-06-28:
- introduce additional header fields
- update black config
- remove travis config
- remove bettercodehub config
- do not upload .egg files to pypi.org
- update github actions : checkout@v3 and setup-python@v4
- remove "better code" badges
- remove python 3.6 tests
- adding python 3.11 tests
- update pypy tests to 3.9

### v2.0.9

2022-07-04: support additional query parameters for patch, post ,put and delete requests

### v2.0.8

2022-07-04: allow different content-types in order to be able to upload documents as octet-stream

### v2.0.7.3

2022-06-30: specify correct "attr" version in requirements

### v2.0.7.2

2022-06-02: update to github actions checkout@v3 and setup-python@v3

### v2.0.7.1

2022-06-01: update github actions test matrix

### v2.0.7

2022-04-12: retry the request (experimental, but not harmful at all) if failed.
- issue https://github.com/bitranox/lib_shopware6_api/issues/1
- sometimes (seldom, after about 10 minutes connected) we got: "error code: 9, status: 401
  The resource owner or authorization server denied the request, detail: Access token could not be verified."
- it seems to work when retry the request

### v2.0.6

2022-03-29: remedy mypy Untyped decorator makes function "cli_info" untyped

### v2.0.5

2022-02-15: documentation update

### v2.0.4

2022-02-15: documentation update

### v2.0.3

2022-01-18: mypy type adjustments

### v2.0.2

2022-01-09:
- handle dal.Criteria 'ids' correctly
- remove empty lists and dicts from dal.Criteria

### v2.0.1

2022-01-06: correct import for dal.Criteria

### v2.0.0

2022-01-04:
- make it possible to pass None Values to Filters (Bug)
- paginated request now respect limits

### v1.3.2

2022-01-04: improve detection of the dal.Criteria Class

### v1.3.1

2021-12-31: implement testing for python 3.6, 3.7

### v1.3.0

2021-12-29: add Sort, Group, Aggregations, Associations, etc ..

### v1.2.0

2021-12-28: add Criteria, Filters

### v1.1.0

2021-12-27: add Store Api DELETE/GET/GET LIST/PATCH/PUT methods

### v1.0.0

2021-12-26: initial release
