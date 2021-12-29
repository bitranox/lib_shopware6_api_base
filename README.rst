lib_shopware6_api_base
======================


Version v1.3.0 as of 2021-12-30 see `Changelog`_

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

tested on recent linux with python 3.8, 3.9, 3.10.0, pypy-3.8 - architectures: amd64

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
    - `Aggregations`_
        - `AvgAggregation`_
        - `CountAggregation`_
        - `MaxAggregation`_
        - `MinAggregation`_
        - `SumAggregation`_
        - `StatsAggregation`_
        - `TermsAggregation`_
        - `FilterAggregation`_
        - `EntityAggregation`_
        - `DateHistogramAggregation`_
        - `NestingAggregations`_
    - `Associations`_
    - `Filters`_
        - `EqualsFilter`_
        - `EqualsAnyFilter`_
        - `ContainsFilter`_
        - `RangeFilter`_
        - `NotFilter`_
        - `MultiFilter`_
        - `PrefixFilter`_
        - `SuffixFilter`_
    - `Grouping`_
    - `ids`_
    - `includes`_
    - `page & limit`_
    - `Query`_
    - `Sort`_
        - `FieldSorting`_
        - `AscFieldSorting`_
        - `DescFieldSorting`_

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

for the definition of "Criteria" see `Query Syntax`_


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



        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test empty
        >>> my_criteria = Criteria()
        >>> pp(my_criteria.get_dict())
        {}

        >>> # Test Average aggregation
        >>> my_criteria = Criteria()
        >>> my_criteria.limit=1
        >>> my_criteria.includes['product'] = ['id', 'name']
        >>> my_criteria.aggregations = [AvgAggregation('average-price', 'price')]
        >>> pp(my_criteria.get_dict())
        {'limit': 1,
         'aggregations': [{'name': 'average-price', 'type': 'avg', 'field': 'price'}],
         'includes': {'product': ['id', 'name']}}

        >>> # Test Filter aggregation
        >>> my_criteria = Criteria(limit=1, includes={'product':['id', 'name']},
        ...     aggregations=FilterAggregation(name='active-price-avg',
        ...                                    filter=EqualsFilter(field='active', value=True),
        ...                                    aggregation=AvgAggregation(name='avg-price',field='price')))
        >>> pp(my_criteria.get_dict())
        {'limit': 1,
         'aggregations': {'name': 'active-price-avg',
                          'type': 'filter',
                          'filter': {'type': 'equals',
                                     'field': 'active',
                                     'value': True},
                          'aggregation': {'name': 'avg-price',
                                          'type': 'avg',
                                          'field': 'price'}},
         'includes': {'product': ['id', 'name']}}

        >>> # Association{{{
        >>> # Test Association
        >>> my_criteria = Criteria()
        >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter('active', 'true')])
        >>> pp(my_criteria.get_dict())
        {'associations': {'products': {'limit': 5,
                                       'filter': [{'type': 'equals',
                                                   'field': 'active',
                                                   'value': 'true'}]}}}
        >>> # Association}}}

        >>> # Test append filters
        >>> my_criteria = Criteria()
        >>> my_criteria.page = 0
        >>> my_criteria.limit=1
        >>> my_criteria.filter.append(EqualsFilter('a', 'a'))
        >>> my_criteria.filter.append(EqualsFilter('b', 'b'))
        >>> my_criteria.filter.append(EqualsFilter('d', 'd'))
        >>> pp(my_criteria.get_dict())
        {'limit': 1,
         'page': 0,
         'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                    {'type': 'equals', 'field': 'b', 'value': 'b'},
                    {'type': 'equals', 'field': 'd', 'value': 'd'}]}

        >>> # Test set filters
        >>> my_criteria = Criteria()
        >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]
        >>> pp(my_criteria.get_dict())
        {'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                    {'type': 'equals', 'field': 'b', 'value': 'b'},
                    {'type': 'equals', 'field': 'd', 'value': 'd'}]}

        >>> # Grouping{{{
        >>> # Test Grouping
        >>> my_criteria = Criteria()
        >>> my_criteria.limit=5
        >>> my_criteria.grouping=['active']
        >>> pp(my_criteria.get_dict())
        {'limit': 5, 'grouping': ['active']}
        >>> # Grouping}}}

        >>> # ids{{{
        >>> # Test ids
        >>> my_criteria = Criteria()
        >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
        >>> pp(my_criteria.get_dict())
        {'ids': ['012cd563cf8e4f0384eed93b5201cc98',
                 '075fb241b769444bb72431f797fd5776',
                 '090fcc2099794771935acf814e3fdb24']}

        >>> # ids}}}

        >>> # includes{{{
        >>> # Test includes
        >>> my_criteria = Criteria()
        >>> my_criteria.includes['product'] = ['id', 'name']
        >>> pp(my_criteria.get_dict())
        {'includes': {'product': ['id', 'name']}}

        >>> # includes}}}

        >>> # page&limit{{{
        >>> my_criteria = Criteria(page=1, limit=5)
        >>> pp(my_criteria.get_dict())
        {'limit': 5, 'page': 1}

        >>> # page&limit}}}

        >>> # Test Query
        >>> my_criteria = Criteria(
        ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
        ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
        ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
        >>> pp(my_criteria.get_dict())
        {'query': [{'score': 500,
                    'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
                   {'score': 500,
                    'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
                   {'score': 100,
                    'query': {'type': 'equals',
                              'field': 'manufacturerId',
                              'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}]}

        >>> # Test Sorting
        >>> my_criteria = Criteria(limit=5,
        ...                        sort=[FieldSorting('name', 'ASC', True),
        ...                              DescFieldSorting('active')])
        >>> pp(my_criteria.get_dict())
        {'limit': 5,
         'sort': [{'field': 'name', 'order': 'ASC', 'naturalSorting': True},
                  {'field': 'active', 'order': 'DESC'}]}

        """

Aggregations
------------
back to `Query Syntax`_

- `AvgAggregation`_
- `CountAggregation`_
- `MaxAggregation`_
- `MinAggregation`_
- `SumAggregation`_
- `StatsAggregation`_
- `TermsAggregation`_
- `FilterAggregation`_
- `EntityAggregation`_
- `DateHistogramAggregation`_
- `NestingAggregations`_


AvgAggregation
========================
back to `Aggregations`_

.. code-block:: python

    @attrs.define
    class AvgAggregation:
        """
        see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
        The Avg aggregation makes it possible to calculate the average value for a field.
        The following SQL statement is executed in the background: AVG(price).

        :parameter:
            name: str
            field: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = AvgAggregation('avg-price', 'price')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'avg-price', 'type': 'avg', 'field': 'price'}

        """

CountAggregation
========================
back to `Aggregations`_

.. code-block:: python

    @attrs.define
    class CountAggregation:
        """
        see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
        The count aggregation makes it possible to determine the number of entries for a field that are filled with a value.
        The following SQL statement is executed in the background: COUNT(DISTINCT(manufacturerId)).

        :parameter:
            name: str
            field: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = CountAggregation('count-manufacturers', 'manufacturerId')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'count-manufacturers', 'type': 'count', 'field': 'manufacturerId'}

        """

MaxAggregation
========================
back to `Aggregations`_

.. code-block:: python

    @attrs.define
    class MaxAggregation:
        """
        see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
        The max aggregation allows you to determine the maximum value of a field.
        The following SQL statement is executed in the background: MAX(price).

        :parameter:
            name: str
            field: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = MaxAggregation('max-price', 'price')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'max-price', 'type': 'max', 'field': 'price'}

        """

MinAggregation
========================
back to `Aggregations`_

.. code-block:: python

    @attrs.define
    class MinAggregation:
        """
        see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
        The min aggregation makes it possible to determine the minimum value of a field.
        The following SQL statement is executed in the background: MIN(price)

        :parameter:
            name: str
            field: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = MinAggregation('min-price', 'price')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'min-price', 'type': 'min', 'field': 'price'}

        """

SumAggregation
========================
back to `Aggregations`_

.. code-block:: python

    @attrs.define
    class SumAggregation:
        """
        see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
        The sum aggregation makes it possible to determine the total of a field.
        The following SQL statement is executed in the background: SUM(price)

        :parameter:
            name: str
            field: str

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = SumAggregation('sum-price', 'price')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'sum-price', 'type': 'sum', 'field': 'price'}

        """

StatsAggregation
========================
back to `Aggregations`_

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = StatsAggregation('stats-price', 'price')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'stats-price', 'type': 'stats', 'field': 'price'}

        """

TermsAggregation
========================
back to `Aggregations`_

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = TermsAggregation(name='manufacturer-ids', limit=3, sort=DescFieldSorting('manufacturer.name'), field='manufacturerId')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'manufacturer-ids',
         'type': 'terms',
         'field': 'manufacturerId',
         'sort': {'field': 'manufacturer.name',
                  'order': 'DESC',
                  'naturalSorting': None},
         'limit': 3,
         'aggregation': None}

        """

FilterAggregation
========================
back to `Aggregations`_

.. code-block:: python

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

        :parameter:
            name: str
            sort: SortType
            filter: FilterType
            aggregation : AggregationType

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = FilterAggregation(
        ...     name='active-price-avg',
        ...     filter=EqualsFilter(field='active', value=True),
        ...     aggregation=AvgAggregation(name='avg-price',field='price'))
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'active-price-avg',
         'type': 'filter',
         'filter': {'type': 'equals', 'field': 'active', 'value': True},
         'aggregation': {'name': 'avg-price', 'type': 'avg', 'field': 'price'}}

        """

EntityAggregation
========================
back to `Aggregations`_

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = EntityAggregation(name='manufacturers', definition='product_manufacturer', field='manufacturerId')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'manufacturers',
         'type': 'entity',
         'definition': 'product_manufacturer',
         'field': 'manufacturerId'}
        """

DateHistogramAggregation
========================
back to `Aggregations`_

.. code-block:: python

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

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_aggregation = DateHistogramAggregation(name='release-dates', field='releaseDate', interval='month')
        >>> pp(attrs.asdict(my_aggregation))
        {'name': 'release-dates',
         'type': 'histogram',
         'field': 'releaseDate',
         'interval': 'month'}

        """

NestingAggregations
========================
back to `Aggregations`_

.. code-block:: python

    """
    see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference#nesting-aggregations
    """

Associations
------------------------
back to `Query Syntax`_

The associations parameter allows you to load additional data to the minimal data set
of an entity without sending an extra request - similar to a SQL Join.
The key of the parameter is the property name of the association in the entity.
You can pass a nested criteria just for that association - e.g. to perform a sort
to or apply filters within the association.

.. code-block:: python

        >>> # Test Association
        >>> my_criteria = Criteria()
        >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter('active', 'true')])
        >>> pp(my_criteria.get_dict())
        {'associations': {'products': {'limit': 5,
                                       'filter': [{'type': 'equals',
                                                   'field': 'active',
                                                   'value': 'true'}]}}}
        >>>

Filters
------------------------
back to `Query Syntax`_

- `EqualsFilter`_
- `EqualsAnyFilter`_
- `ContainsFilter`_
- `RangeFilter`_
- `NotFilter`_
- `MultiFilter`_
- `PrefixFilter`_
- `SuffixFilter`_

EqualsFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_filter = EqualsFilter('stock', 10)
        >>> pp(attrs.asdict(my_filter))
        {'type': 'equals', 'field': 'stock', 'value': 10}

        """

EqualsAnyFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test Keyword param
        >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'equals',
         'field': 'productNumber',
         'value': ['3fed029475fa4d4585f3a119886e0eb1',
                   '77d26d011d914c3aa2c197c81241a45b']}

        >>> # Test positional param
        >>> my_filter = EqualsAnyFilter('productNumber', ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'equals',
         'field': 'productNumber',
         'value': ['3fed029475fa4d4585f3a119886e0eb1',
                   '77d26d011d914c3aa2c197c81241a45b']}

        """

ContainsFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'type': 'contains', 'field': 'productNumber', 'value': 'Lightweight'}


        """

RangeFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test (pass range type as string)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
        >>> pp(attrs.asdict(my_filter))
        {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

        >>> # Test (pass range type from 'range_filter' object)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.gte: 20, range_filter.lte: 30})
        >>> pp(attrs.asdict(my_filter))
        {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

        >>> # Test (wrong range)
        >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
        Traceback (most recent call last):
            ...
        ValueError: "less" is not a valid range

        """

NotFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test (pass operator as string)
        >>> my_filter = NotFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'not',
         'operator': 'or',
         'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                     {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

        >>> # Test (pass operator from 'not_filter_operator' object)
        >>> my_filter = NotFilter(not_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'not',
         'operator': 'or',
         'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                     {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

        >>> # Test unknown operator
        >>> my_filter = NotFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        Traceback (most recent call last):
            ...
        ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

        """

MultiFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test (pass operator as string)
        >>> my_filter = MultiFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'multi',
         'operator': 'or',
         'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                     {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

        >>> # Test (pass operator from 'not_filter_operator' object)
        >>> my_filter = MultiFilter(multi_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        >>> pp(attrs.asdict(my_filter))
        {'type': 'multi',
         'operator': 'or',
         'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                     {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

        >>> # Test unknown operator
        >>> my_filter = MultiFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
        Traceback (most recent call last):
            ...
        ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

        """

PrefixFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_filter = PrefixFilter('name', 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'type': 'prefix', 'field': 'name', 'value': 'Lightweight'}

        """

SuffixFilter
========================
back to `Filters`_

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
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_filter = SuffixFilter('name', 'Lightweight')
        >>> pp(attrs.asdict(my_filter))
        {'type': 'suffix', 'field': 'name', 'value': 'Lightweight'}

        """

Grouping
------------------------
back to `Query Syntax`_

The grouping parameter allows you to group the result over fields.
It can be used to realise queries such as:

- Fetch one product for each manufacturer
- Fetch one order per day and customer

.. code-block:: python

        >>> # Test Grouping
        >>> my_criteria = Criteria()
        >>> my_criteria.limit=5
        >>> my_criteria.grouping=['active']
        >>> pp(my_criteria.get_dict())
        {'limit': 5, 'grouping': ['active']}
        >>>

ids
------------------------
back to `Query Syntax`_

If you want to perform a simple lookup using just the ids of records,
you can pass a list of those using the ids field:

.. code-block:: python

        >>> # Test ids
        >>> my_criteria = Criteria()
        >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
        >>> pp(my_criteria.get_dict())
        {'ids': ['012cd563cf8e4f0384eed93b5201cc98',
                 '075fb241b769444bb72431f797fd5776',
                 '090fcc2099794771935acf814e3fdb24']}

        >>>

includes
------------------------
back to `Query Syntax`_

The includes parameter allows you to restrict the returned fields.

Transfer only what you need - reduces response payload
Easier to consume for client applications
When debugging, the response is smaller and you can concentrate on the essential fields

.. code-block:: python

        >>> # Test includes
        >>> my_criteria = Criteria()
        >>> my_criteria.includes['product'] = ['id', 'name']
        >>> pp(my_criteria.get_dict())
        {'includes': {'product': ['id', 'name']}}

        >>>

All response types come with a apiAlias field which you can use to identify the
type in your includes field.

If you only want a categories id, add: "category": ["id"].

For entities, this is the entity name: product, product_manufacturer, order_line_item, ...

For other non-entity-types like a listing result or a line item, check the full response.
This pattern applies not only to simple fields but also to associations.

page & limit
------------------------
back to `Query Syntax`_

The page and limit parameters can be used to control pagination. The page parameter is 1-indexed.

.. code-block:: python

        >>> my_criteria = Criteria(page=1, limit=5)
        >>> pp(my_criteria.get_dict())
        {'limit': 5, 'page': 1}

        >>>

Query
------------------------
back to `Query Syntax`_

Use this parameter to create a weighted search query that returns a _score for each found entity.
Any filter type can be used for the query. A score has to be defined for each query.
The sum of the matching queries then results in the total _score value.

.. code-block:: python

    @attrs.define
    class Query:
        """
        see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#query
        Enables you to determine a ranking for the search result
        Use this parameter to create a weighted search query that returns a _score for each found entity.
        Any filter type can be used for the query. A score has to be defined for each query.
        The sum of the matching queries then results in the total _score value.

        :parameter
            score   int
            query   FilterType

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_criteria = Criteria(
        ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
        ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
        ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
        >>> pp(my_criteria.get_dict())
        {'query': [{'score': 500,
                    'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
                   {'score': 500,
                    'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
                   {'score': 100,
                    'query': {'type': 'equals',
                              'field': 'manufacturerId',
                              'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}]}

        """

Sort
------------------------
back to `Query Syntax`_

The sort parameter allows to control the sorting of the result.
Several sorts can be transferred at the same time.

The field parameter defines which field is to be used for sorting.
The order parameter defines the sort direction.
The parameter naturalSorting allows to use a Natural Sorting Algorithm

FieldSorting
===============

.. code-block:: python

    @attrs.define
    class FieldSorting:
        """
        see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
        The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
        The field parameter defines which field is to be used for sorting.
        The order parameter defines the sort direction.
        The parameter naturalSorting allows to use a Natural Sorting Algorithm

        :parameter
            field : str
            order : str "ASC" or "DESC"
            naturalSorting : Optional[bool]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_sorting = FieldSorting('name', 'ASC', True)
        >>> pp(attrs.asdict(my_sorting))
        {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

        """

AscFieldSorting
===============

.. code-block:: python

    @attrs.define
    class AscFieldSorting:
        """
        see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
        The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
        The field parameter defines which field is to be used for sorting.
        The order parameter defines the sort direction.
        The parameter naturalSorting allows to use a Natural Sorting Algorithm

        :parameter
            field : str
            naturalSorting : Optional[bool]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_sorting = AscFieldSorting('name', True)
        >>> pp(attrs.asdict(my_sorting))
        {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

        """

DescFieldSorting
=================

.. code-block:: python

    @attrs.define
    class DescFieldSorting:
        """
        see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
        The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
        The field parameter defines which field is to be used for sorting.
        The order parameter defines the sort direction.
        The parameter naturalSorting allows to use a Natural Sorting Algorithm

        :parameter
            field : str
            naturalSorting : Optional[bool]

        >>> # Setup
        >>> import pprint
        >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

        >>> # Test
        >>> my_sorting = DescFieldSorting('name', True)
        >>> pp(attrs.asdict(my_sorting))
        {'field': 'name', 'order': 'DESC', 'naturalSorting': True}

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

v1.3.0
--------
2021-12-29:
    - add Sort, Group, Aggregations, Associations, etc ..

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

