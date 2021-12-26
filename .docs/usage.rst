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


- Store API
    for the Store API only "request_post" is implemented at the moment,
    which might be used as an example to implement all other methods
    like 'get', 'patch', 'put', 'delete'.

    this is, because I only need the AdminAPI myself - contributions welcome !


.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api{{{
    :end-before:  # store_api}}}


- Store API Post

.. include:: ../lib_shopware6_api_base/lib_shopware6_api_base.py
    :code: python
    :start-after: # store_api_post{{{
    :end-before:  # store_api_post}}}


- Admin API

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
