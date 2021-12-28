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

.. include:: ../lib_shopware6_api_base/conf_shopware6_api_base_classes.py
    :code: python
    :start-after: # config_class{{{
    :end-before:  # config_class}}}


now You can use this configuration:

.. code-block::

    from lib_shopware6_api_base import Shopware6AdminAPIClientBase
    from my_shop_config import ConfShopware6ApiBase

    my_conf = ConfShopware6ApiBase()
    my_api_client = Shopware6AdminAPIClientBase(config=my_conf)
    ...

- test configuration

.. include:: ../lib_shopware6_api_base/conf_shopware6_api_base_docker_testcontainer.py
    :start-after: # config_dockware{{{
    :end-before:  # config_dockware}}}

now You can test against that container with :

.. code-block::

    my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
    ...


methods
-------

please note, that on github actions the test configuration is used automatically,
therefore on all examples no configuration is passed on purpose.

methods which take the parameter 'payload', the payload is of following type :


.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :start-after: # payload_type{{{
    :end-before:  # payload_type}}}


Store API
---------


.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api{{{
    :end-before:  # store_api}}}


- Store API Get

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_get{{{
    :end-before:  # store_api_get}}}


- Store API Get List

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_get_list{{{
    :end-before:  # store_api_get_list}}}


- Store API Patch

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_patch{{{
    :end-before:  # store_api_patch}}}


- Store API Post

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_post{{{
    :end-before:  # store_api_post}}}


- Store API Put

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_put{{{
    :end-before:  # store_api_put}}}


- Store API Delete

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_delete{{{
    :end-before:  # store_api_delete}}}


Admin API
---------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api{{{
    :end-before:  # admin_api}}}


- Admin API GET

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_get{{{
    :end-before:  # admin_api_get}}}


- Admin API GET Paginated

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_get_paginated{{{
    :end-before:  # admin_api_get_paginated}}}


- Admin API PATCH

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_patch{{{
    :end-before:  # admin_api_patch}}}


- Admin API POST

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_post{{{
    :end-before:  # admin_api_post}}}


- Admin API POST PAGINATED

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_post_paginated{{{
    :end-before:  # admin_api_post_paginated}}}


- Admin API PUT

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_put{{{
    :end-before:  # admin_api_put}}}


- Admin API DELETE

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # admin_api_delete{{{
    :end-before:  # admin_api_delete}}}


Query Syntax
------------

The querying syntax closely resembling the one from the internal DAL.
If you're familiar with Shopware 6 DAL syntax and how to retrieve it,
you might see the examples are predictable and straightforward

a search criteria follows the following schema:

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # criteria{{{
    :end-before:  # criteria}}}


Filters
-------

EqualsFilter
------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # EqualsFilter{{{
    :end-before:  # EqualsFilter}}}


EqualsAnyFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # EqualsAnyFilter{{{
    :end-before:  # EqualsAnyFilter}}}


ContainsFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # ContainsFilter{{{
    :end-before:  # ContainsFilter}}}


RangeFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # RangeFilter{{{
    :end-before:  # RangeFilter}}}


NotFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # NotFilter{{{
    :end-before:  # NotFilter}}}


MultiFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # MultiFilter{{{
    :end-before:  # MultiFilter}}}


PrefixFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # PrefixFilter{{{
    :end-before:  # PrefixFilter}}}


SuffixFilter
---------------

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # SuffixFilter{{{
    :end-before:  # SuffixFilter}}}
