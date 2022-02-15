# the configuration file for the dockware docker test container.


"""
# config_dockware{{{

for testing we use the dockware docker container,
see : `dockware <https://developer.shopware.com/docs/guides/installation/dockware>`_


on github actions the dockware docker test container is installed as a service and is available
for communication on localhost

You can start the dockware container locally with the command : sudo docker run -d --rm -p 80:80 --name dockware dockware/dev:latest
# config_dockware}}}
"""


# STDLIB
import os

# conf
try:
    from conf_shopware6_api_base_classes import ConfShopware6ApiBase
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .conf_shopware6_api_base_classes import ConfShopware6ApiBase  # type: ignore # pragma: no cover

conf_shopware6_api_base = ConfShopware6ApiBase()
# the api url, like : 'https://shop.yourdomain.com/api'
conf_shopware6_api_base.shopware_admin_api_url = "http://localhost/api"
# the storefront api url, like : 'https://shop.yourdomain.com/store-api'
conf_shopware6_api_base.shopware_storefront_api_url = "http://localhost/store-api"

# since dockware container does not support https, we need to disable secure transport for oauth2
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


"""
Admin API:
for User Credentials Grant Type:
==================================
- with refresh token
- we recommend to only use this grant flow for client applications that should
  perform administrative actions and require a user-based authentication

"""
conf_shopware6_api_base.username = "admin"
conf_shopware6_api_base.password = "shopware"

"""
Admin API:
for Resource Owner Password Grant Type:
=======================================
- no refresh token
- should be used for machine-to-machine communications, such as CLI jobs or automated services
see https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

those credentials will be created by the APi on the dockware container (fixed, hardcoded)
and are only used for testing purposes on the dockware container on github
"""
# the client ID, setup at Web Administration Interface > settings > system > integration > access_id
conf_shopware6_api_base.client_id = "SWIACWJOMUTXV1RMNGJUAKTUAA"  # noqa
# the client secret, setup at Web Administration Interface > settings > system > integration > access_secret
conf_shopware6_api_base.client_secret = "UkhvUG1qdmpuMjFudGJCdG1Xc0xMbEt2ck9CQ2xDTUtXMUZHRUQ"  # noqa

# which grant type to use can be either 'user_credentials'- or 'resource_owner'
conf_shopware6_api_base.grant_type = "user_credentials"

"""
Store API:
sw-access-key set in Administration/Sales Channels/API
this access key will be read out from the dockware container, and the config will be adjusted accordingly
"""
conf_shopware6_api_base.store_api_sw_access_key = ""
