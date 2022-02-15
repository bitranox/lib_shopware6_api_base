# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# EXT
# config_class{{{
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
    setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
    or directly via URL : https://<fqdn>/admin#/sw/integration/index
    were <fqdn> is the fully qualified domain name, like https://myshop.mydomain.com/admin#/sw/integration/index
    """
    # the client ID, setup at Web Administration Interface > settings > system > integration > access_id
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


# config_class}}}


class ShopwareAPIError(BaseException):
    pass
