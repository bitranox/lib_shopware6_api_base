- `configuration`_
- `methods`_
- `headers`_
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

for the definition of "Criteria" see `Query Syntax`_


headers
-------


Endpoints like ``/api/_action/sync`` require request specific custom headers to manipulate the api behavior

see : `Bulk Payloads Performance`_  and `Bulk edit entities`_ in the Admin API Documentation

.. _`Bulk Payloads Performance`: https://shopware.stoplight.io/docs/admin-api/faf8f8e4e13a0-bulk-payloads#performance
.. _`Bulk edit entities`: https://shopware.stoplight.io/docs/admin-api/0612cb5d960ef-bulk-edit-entities

You may pass such custom header fields like that :

.. code-block::

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


following header fields are pre-defined :

.. include:: ..//lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # headers_for_bulk_operations{{{
    :end-before:  # headers_for_bulk_operations}}}


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

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # AvgAggregation{{{
    :end-before:  # AvgAggregation}}}

CountAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # CountAggregation{{{
    :end-before:  # CountAggregation}}}

MaxAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # MaxAggregation{{{
    :end-before:  # MaxAggregation}}}

MinAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # MinAggregation{{{
    :end-before:  # MinAggregation}}}

SumAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # SumAggregation{{{
    :end-before:  # SumAggregation}}}

StatsAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # StatsAggregation{{{
    :end-before:  # StatsAggregation}}}

TermsAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # TermsAggregation{{{
    :end-before:  # TermsAggregation}}}

FilterAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # FilterAggregation{{{
    :end-before:  # FilterAggregation}}}

EntityAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # EntityAggregation{{{
    :end-before:  # EntityAggregation}}}

DateHistogramAggregation
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # DateHistogramAggregation{{{
    :end-before:  # DateHistogramAggregation}}}

NestingAggregations
========================
back to `Aggregations`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_aggregation.py
    :code: python
    :start-after: # NestingAggregations{{{
    :end-before:  # NestingAggregations}}}

Associations
------------------------
back to `Query Syntax`_

The associations parameter allows you to load additional data to the minimal data set
of an entity without sending an extra request - similar to a SQL Join.
The key of the parameter is the property name of the association in the entity.
You can pass a nested criteria just for that association - e.g. to perform a sort
to or apply filters within the association.

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # Association{{{
    :end-before:  # Association}}}

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

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # EqualsFilter{{{
    :end-before:  # EqualsFilter}}}

EqualsAnyFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # EqualsAnyFilter{{{
    :end-before:  # EqualsAnyFilter}}}

ContainsFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # ContainsFilter{{{
    :end-before:  # ContainsFilter}}}

RangeFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # RangeFilter{{{
    :end-before:  # RangeFilter}}}

NotFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # NotFilter{{{
    :end-before:  # NotFilter}}}

MultiFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # MultiFilter{{{
    :end-before:  # MultiFilter}}}

PrefixFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # PrefixFilter{{{
    :end-before:  # PrefixFilter}}}

SuffixFilter
========================
back to `Filters`_

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_filter.py
    :code: python
    :start-after: # SuffixFilter{{{
    :end-before:  # SuffixFilter}}}

Grouping
------------------------
back to `Query Syntax`_

The grouping parameter allows you to group the result over fields.
It can be used to realise queries such as:

- Fetch one product for each manufacturer
- Fetch one order per day and customer

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # Grouping{{{
    :end-before:  # Grouping}}}

ids
------------------------
back to `Query Syntax`_

If you want to perform a simple lookup using just the ids of records,
you can pass a list of those using the ids field.
Please note that as soon as You use ids, limit and page does not apply anymore !

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # ids{{{
    :end-before:  # ids}}}

includes
------------------------
back to `Query Syntax`_

The includes parameter allows you to restrict the returned fields.

Transfer only what you need - reduces response payload
Easier to consume for client applications
When debugging, the response is smaller and you can concentrate on the essential fields

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # includes{{{
    :end-before:  # includes}}}

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
Please note that as soon as You use ids, limit and page does not apply anymore !

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # page&limit{{{
    :end-before:  # page&limit}}}

Query
------------------------
back to `Query Syntax`_

Use this parameter to create a weighted search query that returns a _score for each found entity.
Any filter type can be used for the query. A score has to be defined for each query.
The sum of the matching queries then results in the total _score value.

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria.py
    :code: python
    :start-after: # Query{{{
    :end-before:  # Query}}}

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

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_sorting.py
    :code: python
    :start-after: # FieldSorting{{{
    :end-before:  # FieldSorting}}}

AscFieldSorting
===============

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_sorting.py
    :code: python
    :start-after: # AscFieldSorting{{{
    :end-before:  # AscFieldSorting}}}

DescFieldSorting
=================

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base_criteria_sorting.py
    :code: python
    :start-after: # DescFieldSorting{{{
    :end-before:  # DescFieldSorting}}}

