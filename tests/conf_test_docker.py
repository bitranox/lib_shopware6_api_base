"""Configuration for the dockware Docker test container.

For integration testing we use the dockware container.
See: https://developer.shopware.com/docs/guides/installation/dockware

On GitHub Actions the dockware container is installed as a service and is
available on localhost. Start it locally with::

    docker run -d --rm -p 80:80 --name dockware dockware/dev:latest

The config is built directly (no env/.env needed) with the public dockware
default credentials; ``conftest.py`` augments it at runtime with the storefront
access key and integration credentials.
"""

from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase, GrantType

conf_shopware6_api_base = ConfShopware6ApiBase(
    shopware_admin_api_url="http://localhost/api",
    shopware_storefront_api_url="http://localhost/store-api",
    username="admin",
    password="shopware",
    client_id="SWIACWJOMUTXV1RMNGJUAKTUAA",
    client_secret="UkhvUG1qdmpuMjFudGJCdG1Xc0xMbEt2ck9CQ2xDTUtXMUZHRUQ",
    grant_type=GrantType.USER_CREDENTIALS,
)
