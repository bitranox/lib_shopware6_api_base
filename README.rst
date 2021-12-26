lib_shopware6_api_base
======================


Version v0.0.1 as of 2021-12-26 see `Changelog`_

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

this is a basic API client for shopware6.
it supports all available authorisation types to the Admin and Storefront API.
Paginated requests are supported.

This is only the basic abstraction layer, to enjoy higher level functions, check out "lib_shopware6_api"

----

automated tests, Travis Matrix, Documentation, Badges, etc. are managed with `PizzaCutter <https://github
.com/bitranox/PizzaCutter>`_ (cookiecutter on steroids)

Python version required: 3.6.0 or newer

tested on recent linux with python 3.6, 3.7, 3.8, 3.9, 3.10.0, pypy-3.8 - architectures: amd64

`100% code coverage <https://codecov.io/gh/bitranox/lib_shopware6_api_base>`_, flake8 style checking ,mypy static type checking ,tested under `Windows <https://github.com/bitranox/lib_shopware6_api_base/actions/workflows/python-package.yml>`_, automatic daily builds and monitoring

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

- configuration
    the configuration is passed to the client as an configuration object of the type "ConfShopware6ApiBase"
    simply copy the Class definition of "ConfShopware6ApiBase" and create Your own configuration file, for instance "my_shop_config.py"

.. code-block:: python

    import attr


    @attr.dataclass()
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

        # which grant type to use can be either 'user_credentials'- or 'resource_owner'
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
    .. include:: ../lib_shopware6_api_base/conf_shopware6_api_base_docker_testcontainer.py
        :start-after: # config_dockware{{{
        :end-before:  # config_dockware}}}
    now You can test against that container with :

    .. code-block::

        my_api_client = Shopware6AdminAPIClientBase(use_docker_test_container=True)
        ...

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
    attr
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

v0.0.1
--------
YYYY-MM-DD: <some release name>
    - change1
    - change2
    - ...
