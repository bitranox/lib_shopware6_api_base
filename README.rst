lib_shopware6_api_base
======================


Version v1.2.0 as of 2021-12-29 see `Changelog`_

|build_badge| |license| |pypi| |black|

|codecov| |better_code| |cc_maintain| |cc_issues| |cc_coverage| |snyk|



.. |build_badge| image:: https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/python-package.yml/badge.svg
   :target: https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/python-package.yml


.. |license| image:: https://img.shields.io/github/license/webcomics/pywine.svg
   :target: http://en.wikipedia.org/wiki/MIT_License

.. |jupyter| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/bitranox/lib_shopware6_api_base/master?filepath=lib_shopware6_api_base.ipynb

.. for the pypi status link note the dashes, not the underscore !
.. |pypi| image:: https://img.shields.io/pypi/status/lib-shopware6-api-base?label=PyPI%20Package
   :target: https://badge.fury.io/py/lib_shopware6_api_base

.. |codecov| image:: https://img.shields.io/codecov/c/github/bitranox/lib_shopware6_api_base
   :target: https://codecov.io/gh/bitranox/lib_shopware6_api_base

.. |better_code| image:: https://bettercodehub.com/edge/badge/bitranox/lib_shopware6_api_base?branch=master
   :target: https://bettercodehub.com/results/bitranox/lib_shopware6_api_base

.. |cc_maintain| image:: https://img.shields.io/codeclimate/maintainability-percentage/bitranox/lib_shopware6_api_base?label=CC%20maintainability
   :target: https://codeclimate.com/github/bitranox/lib_shopware6_api_base/maintainability
   :alt: Maintainability

.. |cc_issues| image:: https://img.shields.io/codeclimate/issues/bitranox/lib_shopware6_api_base?label=CC%20issues
   :target: https://codeclimate.com/github/bitranox/lib_shopware6_api_base/maintainability
   :alt: Maintainability

.. |cc_coverage| image:: https://img.shields.io/codeclimate/coverage/bitranox/lib_shopware6_api_base?label=CC%20coverage
   :target: https://codeclimate.com/github/bitranox/lib_shopware6_api_base/test_coverage
   :alt: Code Coverage

.. |snyk| image:: https://img.shields.io/snyk/vulnerabilities/github/bitranox/lib_shopware6_api_base
   :target: https://snyk.io/test/github/bitranox/lib_shopware6_api_base

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

this is a basic API client for shopware6 which can be used on windows, Linux, MacOs.
It supports all available authorisation types to the Admin and Storefront API.
Paginated requests are supported.

This is only the basic abstraction layer, to enjoy higher level functions, check out "lib_shopware6_api"


On github it can be only tested on linux, because we can not run a docker shopware container service on MacOS or Windows.

----

automated tests, Travis Matrix, Documentation, Badges, etc. are managed with `PizzaCutter <https://github
.com/bitranox/PizzaCutter>`_ (cookiecutter on steroids)

Python version required: 3.6.0 or newer

tested on recent linux with python 3.6, 3.7, 3.8, 3.9, 3.10.0, pypy-3.8 - architectures: amd64

`100% code coverage <https://codecov.io/gh/bitranox/lib_shopware6_api_base>`_, flake8 style checking ,mypy static type checking ,

----

- `Usage`_
- `Usage from Commandline`_
- `Installation and Upgrade`_
- `Requirements`_
- `Acknowledgements`_
- `Contribute`_
- `Report Issues <https://github.com/bitranox/lib_shopware6_api_base/blob/master/ISSUE_TEMPLATE.md>`_
- `Pull Request <https://github.com/bitranox/lib_shopware6_api_base/blob/master/PULL_REQUEST_TEMPLATE.md>`_
- `Code of Conduct <https://github.com/bitranox/lib_shopware6_api_base/blob/master/CODE_OF_CONDUCT.md>`_
- `License`_
- `Changelog`_

----



Usage
-----------

- `configuration`_
- `methods`_
- `Store API`_
- `Admin API`_
- `Query Syntax`_
- `Filters`_
    - `EqualsFilter`_
    - `EqualsAnyFilter`_
    - `ContainsFilter`_
    - `RangeFilter`_
    - `NotFilter`_
    - `MultiFilter`_
    - `PrefixFilter`_
    - `SuffixFilter`_


configuration
-------------

    the configuration is passed to the client as a configuration object of the type "ConfShopware6ApiBase"
    simply copy the Class definition of "ConfShopware6ApiBase" and create Your own configuration file, for instance "my_shop_config.py"

.. code-block:: python

    import attrs
    from attrs import validators


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
        setup at admin/settings/system/itegrations: "access_id" and "access_secret"
        """
        # the client ID, set up at setup at admin/settings/system/itegrations/access_id
        client_id: str = ""
        # the client secret, set up at setup at admin/settings/system/itegrations/access_secret
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

now You can use this configuration:

.. code-block::

    from lib_shopware6_api_base import Shopware6AdminAPIClientBase
    from my_shop_config import ConfShopware6ApiBase

    my_conf = ConfShopware6ApiBase()
    my_api_client = Shopware6AdminAPIClientBase(config=my_conf)
    ...

- test configuration

for testing we use the dockware docker container,
see : `dockware <https://developer.shopware.com/docs/guides/installation/dockware>`_


on github actions the dockware docker test container is installed as a service and is available
for communication on localhost

You can start the dockware container locally with the command : sudo docker run -d --rm -p 80:80 --name dockware dockware/dev:latest

now You can test against that container with :

.. code-block::

    my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
    ...


methods
-------

please note, that on github actions the test configuration is used automatically,
therefore on all examples no configuration is passed on purpose.

methods which take the parameter 'payload', the payload is of following type :

PayLoad = Union[None, Dict[str, Any], Criteria]

Store API
---------

.. code-block:: python

    class Shopware6StoreFrontClientBase(object):
        def __init__(self, config: Optional[ConfShopware6ApiBase] = None, use_docker_test_container: bool = False) -> None:
            """
            the Shopware6 Storefront Base API

            :param config:  You can pass a configuration object here.
                            If not given and github actions is detected, or use_docker_test_container == True:
                                conf_shopware6_api_docker_testcontainer.py will be loaded automatically
                            If not given and no github actions is detected:
                                conf_shopware6_api_base_rotek.py will be loaded automatically

            :param use_docker_test_container:   if True, and no config is given, the dockware config will be loaded

            >>> # Test to load automatic configuration
            >>> my_storefront_client = Shopware6StoreFrontClientBase()

            >>> # Test pass configuration
            >>> if _is_github_actions():
            ...     my_config = _load_config_for_docker_test_container()
            ...     my_storefront_client = Shopware6StoreFrontClientBase(config=my_config)

            """

- Store API Get

.. code-block:: python

        def request_get(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            make a get request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
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

- Store API Get List

.. code-block:: python

        def request_get_list(self, request_url: str, payload: PayLoad = None) -> List[Dict[str, Any]]:
            """
            make a get request, expecting a list of dictionaries as result

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
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

- Store API Patch

.. code-block:: python

        def request_patch(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a patch request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

- Store API Post

.. code-block:: python

        def request_post(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            make a post request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
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

- Store API Put

.. code-block:: python

        def request_put(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            make a put request

            parameters:
                http_method: get, post, put, delete
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

- Store API Delete

.. code-block:: python

        def request_delete(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            make a delete request

            parameters:
                http_method: get, post, put, delete
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

Admin API
---------

.. code-block:: python

    class Shopware6AdminAPIClientBase(object):
        def __init__(self, config: Optional[ConfShopware6ApiBase] = None, use_docker_test_container: bool = False) -> None:
            """
            the Shopware6 Admin Base API

            :param config:  You can pass a configuration object here.
                    If not given and github actions is detected, or use_docker_test_container == True:
                        conf_shopware6_api_docker_testcontainer.py will be loaded automatically
                    If not given and no github actions is detected:
                        conf_shopware6_api_base_rotek.py will be loaded automatically

            :param use_docker_test_container:   if True, and no config is given, the dockware config will be loaded

            >>> # Setup
            >>> my_api_client = Shopware6AdminAPIClientBase()

            """

- Admin API GET

.. code-block:: python

        def request_get(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a get request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
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

- Admin API GET Paginated

.. code-block:: python

        def request_get_paginated(self, request_url: str, payload: PayLoad = None, limit: int = 100) -> Dict[str, Any]:
            """
            get the data paginated - metadata 'total' and 'totalCountMode' will be updated
            if You expect a big number of records, the paginated request reads those records in junks of limit=100 for performance reasons.

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary
                limit : the junk size

            :returns
                response_dict: dictionary with the response as dict

            >>> # Setup
            >>> my_api_client = Shopware6AdminAPIClientBase()

            >>> # test read product
            >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', limit=3)
            >>> # we have got more then 3 items - so pagination is working
            >>> assert len(my_response_dict['data']) > 3

            """

- Admin API PATCH

.. code-block:: python

        def request_patch(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a patch request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

- Admin API POST

.. code-block:: python

        def request_post(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a post request

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

- Admin API POST PAGINATED

.. code-block:: python

        def request_post_paginated(self, request_url: str, payload: PayLoad = None, limit: int = 100) -> Dict[str, Any]:
            """
            post the data paginated - metadata 'total' and 'totalCountMode' will be updated
            if You expect a big number of records, the paginated request reads those records in junks of limit=100 for performance reasons.

            parameters:
                request_url: API Url, without the common api prefix
                payload : a dictionary
                limit : the junk size

            :returns
                response_dict: dictionary with the response as dict

            """

- Admin API PUT

.. code-block:: python

        def request_put(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a put request

            parameters:
                http_method: get, post, put, delete
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

- Admin API DELETE

.. code-block:: python

        def request_delete(self, request_url: str, payload: PayLoad = None) -> Dict[str, Any]:
            """
            makes a delete request

            parameters:
                http_method: get, post, put, delete
                request_url: API Url, without the common api prefix
                payload : a dictionary

            :returns
                response_dict: dictionary with the response as dict

            """

Query Syntax
------------

The querying syntax closely resembling the one from the internal DAL.
If you're familiar with Shopware 6 DAL syntax and how to retrieve it,
you might see the examples are predictable and straightforward

a search criteria follows the following schema:

.. code-block:: python

    @attrs.define()
    class Criteria:
        """
        see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries

        structure of Criteria:

        parameter:
        associations                not implemented at the moment
        includes                    not implemented at the moment
        ids                         not implemented at the moment
        total-count-mode            not implemented at the moment
        page    integer
        limit   integer
        filter  List[Filter]
        post-filter                 not implemented at the moment
        query                       not implemented at the moment
        term                        not implemented at the moment
        sort    List[Sort]
        aggregations                not implemented at the moment
        grouping                    not implemented at the moment

        >>> # Test shorthand set filters
        >>> my_criteria = Criteria()
        >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]

Filters
-------

EqualsFilter
------------

.. code-block:: python

    @attrs.define
    class EqualsFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Equals filter allows you to check fields for an exact value.
        The following SQL statement is executed in the background: WHERE stock = 10.

        :parameter:
            field: str
            value: str  # todo check ! type is str, really ? on examples it seems it can be also int

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test
        >>> my_filter = EqualsFilter('stock', 10)
        >>> pp(attrs.asdict(my_filter))
        {'field': 'stock', 'type': 'equals', 'value': 10}
        """

EqualsAnyFilter
---------------

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test
        >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
        >>> pp(attrs.asdict(my_filter))
        {'field': 'productNumber',
         'type': 'equals',
         'value': ['3fed029475fa4d4585f3a119886e0eb1',
                   '77d26d011d914c3aa2c197c81241a45b']}

        """

ContainsFilter
---------------

.. code-block:: python

    @attrs.define
    class ContainsFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Contains Filter allows you to filter a field to an approximate value, where the passed value must be contained as a full value.
        The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight%'.

        :parameter:
            field: str
            value: List[str]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test
        >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'field': 'productNumber', 'type': 'contains', 'value': 'Lightweight'}


        """

RangeFilter
---------------

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test (pass range type as string)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
        >>> pp(attrs.asdict(my_filter))
        {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

        >>> # Test (pass range type from 'range_filter' object)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.gte: 20, range_filter.lte: 30})
        >>> pp(attrs.asdict(my_filter))
        {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

        >>> # Test (wrong range)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
        Traceback (most recent call last):
            ...
        ValueError: "less" is not a valid range

        """

NotFilter
---------------

.. code-block:: python

    @attrs.define
    class NotFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Not Filter is a container which allows to negate any kind of filter.
        The operator allows you to define the combination of queries within the NOT filter (OR and AND).
        The following SQL statement is executed in the background: WHERE !(stock = 1 OR availableStock = 1):

        :parameter:
            operator: 'or' | 'and'
            queries: List[Filter]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test (pass operator as string)
        >>> my_filter = NotFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'operator': 'or',
         'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                     {'field': 'availableStock', 'type': 'equals', 'value': 10}],
         'type': 'not'}


        >>> # Test (pass operator from 'not_filter_operator' object)
        >>> my_filter = NotFilter(not_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'operator': 'or',
         'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                     {'field': 'availableStock', 'type': 'equals', 'value': 10}],
         'type': 'not'}

        >>> # Test unknown operator
        >>> my_filter = NotFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        Traceback (most recent call last):
            ...
        ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

        """

MultiFilter
---------------

.. code-block:: python

    @attrs.define
    class MultiFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Multi Filter is a container, which allows to set logical links between filters.
        The operator allows you to define the links between the queries within the Multi filter (OR and AND).
        The following SQL statement is executed in the background: WHERE (stock = 1 OR availableStock = 1)

        :parameter:
            operator: 'or' | 'and'
            queries: List[Filter]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test (pass operator as string)
        >>> my_filter = MultiFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'operator': 'or',
         'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                     {'field': 'availableStock', 'type': 'equals', 'value': 10}],
         'type': 'multi'}


        >>> # Test (pass operator from 'not_filter_operator' object)
        >>> my_filter = MultiFilter(multi_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'operator': 'or',
         'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                     {'field': 'availableStock', 'type': 'equals', 'value': 10}],
         'type': 'multi'}

        >>> # Test unknown operator
        >>> my_filter = MultiFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        Traceback (most recent call last):
            ...
        ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

        """

PrefixFilter
---------------

.. code-block:: python

    @attrs.define
    class PrefixFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Prefix Filter allows you to filter a field to an approximate value, where the passed value must be the start of a full value.
        The following SQL statement is executed in the background: WHERE name LIKE 'Lightweight%'.

        :parameter:
            field: str
            value: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test
        >>> my_filter = PrefixFilter('name', 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'field': 'name', 'type': 'prefix', 'value': 'Lightweight'}

        """

SuffixFilter
---------------

.. code-block:: python

    @attrs.define
    class SuffixFilter:
        """
        see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
        The Suffix Filter allows you to filter a field to an approximate value, where the passed value must be the end of a full value.
        The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight'.

        :parameter:
            field: str
            value: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter().pprint

        >>> # Test
        >>> my_filter = SuffixFilter('name', 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'field': 'name', 'type': 'suffix', 'value': 'Lightweight'}

        """

Usage from Commandline
------------------------

.. code-block::

   Usage: lib_shopware6_api_base [OPTIONS] COMMAND [ARGS]...

     python3 base API client for shopware6

   Options:
     --version                     Show the version and exit.
     --traceback / --no-traceback  return traceback information on cli
     -h, --help                    Show this message and exit.

   Commands:
     info  get program informations

Installation and Upgrade
------------------------

- Before You start, its highly recommended to update pip and setup tools:


.. code-block::

    python -m pip --upgrade pip
    python -m pip --upgrade setuptools

- to install the latest release from PyPi via pip (recommended):

.. code-block::

    python -m pip install --upgrade lib_shopware6_api_base

- to install the latest version from github via pip:


.. code-block::

    python -m pip install --upgrade git+https://github.com/bitranox/lib_shopware6_api_base.git


- include it into Your requirements.txt:

.. code-block::

    # Insert following line in Your requirements.txt:
    # for the latest Release on pypi:
    lib_shopware6_api_base

    # for the latest development version :
    lib_shopware6_api_base @ git+https://github.com/bitranox/lib_shopware6_api_base.git

    # to install and upgrade all modules mentioned in requirements.txt:
    python -m pip install --upgrade -r /<path>/requirements.txt


- to install the latest development version from source code:

.. code-block::

    # cd ~
    $ git clone https://github.com/bitranox/lib_shopware6_api_base.git
    $ cd lib_shopware6_api_base
    python setup.py install

- via makefile:
  makefiles are a very convenient way to install. Here we can do much more,
  like installing virtual environments, clean caches and so on.

.. code-block:: shell

    # from Your shell's homedirectory:
    $ git clone https://github.com/bitranox/lib_shopware6_api_base.git
    $ cd lib_shopware6_api_base

    # to run the tests:
    $ make test

    # to install the package
    $ make install

    # to clean the package
    $ make clean

    # uninstall the package
    $ make uninstall

Requirements
------------
following modules will be automatically installed :

.. code-block:: bash

    ## Project Requirements
    attrs
    click
    cli_exit_tools
    lib_detect_testenv
    oauthlib
    requests
    requests_oauthlib

Acknowledgements
----------------

- special thanks to "uncle bob" Robert C. Martin, especially for his books on "clean code" and "clean architecture"

Contribute
----------

I would love for you to fork and send me pull request for this project.
- `please Contribute <https://github.com/bitranox/lib_shopware6_api_base/blob/master/CONTRIBUTING.md>`_

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

---

Changelog
=========

- new MAJOR version for incompatible API changes,
- new MINOR version for added functionality in a backwards compatible manner
- new PATCH version for backwards compatible bug fixes

v1.2.0
--------
2021-12-28:
    - add Criteria, Filters

v1.1.0
--------
2021-12-27:
    - add Store Api DELETE/GET/GET LIST/PATCH/PUT methods

v1.0.0
--------
2021-12-26: initial release

