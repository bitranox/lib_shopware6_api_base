# STDLIB
import os
from functools import lru_cache
import json

import logging
import sys
import time
from typing import Any, Dict, Optional

# EXT
import oauthlib
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
import requests
import requests_oauthlib

# conf
try:
    from conf_shopware6_api_base_classes import ConfShopware6ApiBase, ShopwareAPIError
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .conf_shopware6_api_base_classes import ConfShopware6ApiBase, ShopwareAPIError  # type: ignore  # pragma: no cover

logger = logging.getLogger(__name__)


# store_api{{{
class Shopware6StoreAPIClientBase(object):
    def __init__(self, config: Optional[ConfShopware6ApiBase] = None, use_docker_test_container: bool = False) -> None:
        """
        the Shopware6 Store Base API

        :param config:  You can pass a configuration object here.
                        If not given and github actions is detected, or use_docker_test_container == True:
                            conf_shopware6_api_docker_testcontainer.py will be loaded automatically
                        If not given and no github actions is detected:
                            conf_shopware6_api_base_rotek.py will be loaded automatically

        :param use_docker_test_container:   if True, and no config is given, the dockware config will be loaded

        >>> # Test to load automatic configuration
        >>> my_api_client = Shopware6StoreAPIClientBase()

        >>> # Test pass configuration
        >>> if _is_github_actions():
        ...     my_config = _load_config_for_docker_test_container()
        ...     my_api_client = Shopware6StoreAPIClientBase(config=my_config)

        """
        # store_api}}}
        self.use_docker_test_container = use_docker_test_container

        if config is None:
            config = _load_config(use_docker_test_container=use_docker_test_container)

        self.config = config

    # store_api_post{{{
    def request_post(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """

        >>> # Setup
        >>> my_api_client = Shopware6StoreAPIClientBase()

        >>> # test POST without payload
        >>> my_response = my_api_client.request_post(request_url='product')
        >>> assert 'elements' in my_response

        >>> # test POST with payload
        >>> # see : https://shopware.stoplight.io/docs/store-api/b3A6ODI2NTY4MQ-fetch-a-list-of-products
        >>> my_payload = {}  # noqa
        >>> my_payload["filter"] = [{"type": "equals", "field": "active", "value": "true"}]
        >>> my_response = my_api_client.request_post(request_url='product', payload=my_payload)
        >>> assert 'elements' in my_response

        """
        # store_api_post}}}

        response = self._request(http_method="post", request_url=request_url, payload=payload)
        if hasattr(response, "json"):
            response_dict = dict(response.json())  # type: ignore
        else:
            response_dict = dict()
        return response_dict

    def _request(self, http_method: str, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """
        makes a request, using the conf.store_api_sw_access_key for authentication

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict


        >>> # Setup
        >>> my_api_client = Shopware6StoreAPIClientBase()

        >>> # test GET (a new cart)
        >>> my_api_client._request(http_method='get', request_url='checkout/cart', payload={'name': 'rn_doctest'})
        <Response [200]>

        >>> # test DELETE (a new cart)
        >>> my_api_client._request(http_method='delete', request_url='checkout/cart')
        <Response [204]>

        >>> # test POST (a single product)
        >>> my_payload = {'filter': [{"type": "equals", "field": "active", "value": "true"}]}
        >>> my_api_client._request(http_method='post', request_url='product', payload=my_payload)
        <Response [200]>

        >>> # test Link does not exist (a single product)
        >>> my_api_client._request(http_method='post', request_url='product/000')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: 400 Client Error: Bad Request for url: ...

        """
        formatted_request_url = self._format_storefront_api_url(request_url)
        response: requests.Response = requests.Response()
        headers = self._get_headers()

        if http_method == "get":
            response = requests.request("GET", formatted_request_url, params=payload, headers=headers)
        elif http_method == "patch":
            response = requests.request("PATCH", formatted_request_url, data=json.dumps(payload), headers=headers)
        elif http_method == "post":
            response = requests.request("POST", formatted_request_url, data=json.dumps(payload), headers=headers)
        elif http_method == "put":
            response = requests.request("PUT", formatted_request_url, data=json.dumps(payload), headers=headers)
        elif http_method == "delete":
            response = requests.request("DELETE", formatted_request_url, headers=headers)

        try:
            response.raise_for_status()
        except Exception as exc:
            if hasattr(exc, "response"):
                detailed_error = f" : {exc.response.text}"  # type: ignore
            else:
                detailed_error = ""
            raise ShopwareAPIError(f"{exc}{detailed_error}")
        return response

    @lru_cache(maxsize=None)
    def _get_headers(self) -> Dict[str, str]:
        """
        >>> my_api_client = Shopware6StoreAPIClientBase()
        >>> my_api_client._get_headers()
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'sw-access-key': '...'}
        >>> my_api_client._get_headers.cache_clear()

        """
        headers = {"Content-Type": "application/json", "Accept": "application/json", "sw-access-key": self.config.store_api_sw_access_key}
        return headers

    def _format_storefront_api_url(self, request_url: str) -> str:
        """
        formatted url to make a request

        :parameter
            request_url:                        the request url, for instance "oauth/token"
            self.shopware_storefront_api_url:   the api url, for instance https://your.shop-domain.com/store-api

        :returns
            the formatted url, like  https://your.shop-domain.com/store-api/product

        >>> my_api_client = Shopware6StoreAPIClientBase()
        >>> my_api_client._format_storefront_api_url('test')
        'http.../store-api/test'

        """
        request_url = request_url.lstrip("/")
        return f"{self.config.shopware_storefront_api_url}/{request_url}"


# admin_api{{{
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
        # admin_api}}}

        self.use_docker_test_container = use_docker_test_container
        if config is None:
            config = _load_config(use_docker_test_container=use_docker_test_container)
        self.config = config
        self.token: Dict[str, Any] = dict()
        self.session: requests_oauthlib.OAuth2Session = requests_oauthlib.OAuth2Session()

    # admin_api_get{{{
    def request_get(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        # admin_api_get}}}
        response_dict = self._make_request(http_method="get", request_url=request_url, payload=payload)
        return response_dict

    # admin_api_get_paginated{{{
    def request_get_paginated(self, request_url: str, payload: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
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
        # admin_api_get_paginated}}}
        response_dict = self._request_paginated(http_method="get", request_url=request_url, payload=payload, limit=limit)
        return response_dict

    # admin_api_patch{{{
    def request_patch(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_patch}}}
        response_dict = self._make_request(http_method="patch", request_url=request_url, payload=payload)
        return response_dict

    # admin_api_post{{{
    def request_post(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        makes a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_post}}}
        response_dict = self._make_request(http_method="post", request_url=request_url, payload=payload)
        return response_dict

    # admin_api_post_paginated{{{
    def request_post_paginated(self, request_url: str, payload: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
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
        # admin_api_post_paginated}}}
        response_dict = self._request_paginated(http_method="post", request_url=request_url, payload=payload, limit=limit)
        return response_dict

    # admin_api_put{{{
    def request_put(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        makes a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_put}}}
        response_dict = self._make_request(http_method="put", request_url=request_url, payload=payload)
        return response_dict

    # admin_api_delete{{{
    def request_delete(self, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        makes a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_delete}}}
        response_dict = self._make_request(http_method="delete", request_url=request_url, payload=payload)
        return response_dict

    def _request_paginated(self, http_method: str, request_url: str, payload: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
        response_dict: Dict[str, Any] = dict()
        response_dict["data"] = list()

        if payload is None:
            payload = dict()

        payload["limit"] = str(limit)
        page = 1

        while True:
            payload["page"] = str(page)
            partial_data = self._make_request(http_method=http_method, request_url=request_url, payload=payload)
            if partial_data["data"]:
                response_dict["data"] = response_dict["data"] + partial_data["data"]
                page = page + 1
            else:
                break
        return response_dict

    def _make_request(self, http_method: str, request_url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        makes a request - creates and refresh a token and sessions as needed

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict


        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # test resource owner token
        >>> ignore = my_api_client._get_access_token_by_user_credentials()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client._make_request('get', 'customer-group')  # noqa

        >>> # test resource owner token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client._make_request('get', 'customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        >>> # Test client credentials token
        >>> ignore = my_api_client._get_access_token_by_resource_owner()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client._make_request('get', 'customer-group')  # noqa

        >>> # test client credentials token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client._make_request('get', 'customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        >>> # test invalid endpoint
        >>> ignore = my_api_client._make_request('get', 'not-existing')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: 404 Client Error: ...

        """

        if payload is None:
            payload = dict()

        try:
            self._get_session()
            response = self._request(http_method=http_method, request_url=request_url, payload=payload)
        except requests_oauthlib.TokenUpdated as exc:
            self._token_saver(token=exc.token)
            response = self._request(http_method=http_method, request_url=request_url, payload=payload)
        except TokenExpiredError:
            if self._is_refreshable_token():
                # this actually should never happen - just in case.
                logger.warning("something went wrong - the token should have been automatically refreshed. getting a new token")
                self._get_access_token_by_user_credentials()
            else:
                self._get_access_token_by_resource_owner()
            self._get_session()
            response = self._request(http_method=http_method, request_url=request_url, payload=payload)
        try:
            response_dict = dict(response.json())
        except Exception:  # noqa
            response_dict = dict()
        return response_dict

    def _request(self, http_method: str, request_url: str, payload: Optional[Dict[str, Any]]) -> requests.Response:
        """
        makes a request, needs a self.session to be set up and authenticated

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary

        :returns
            response_dict: dictionary with the response as dict

        see : https://docs.python-requests.org/en/latest/user/quickstart/

        :param http_method:
        :param request_url:
        :param payload:
        :return:
        """
        if payload is None:
            payload = dict()
        response: requests.Response = requests.Response()
        headers = self._get_headers()

        if http_method == "get":
            response = self.session.get(self._format_admin_api_url(request_url), params=payload, headers=headers)
        elif http_method == "patch":
            response = self.session.patch(self._format_admin_api_url(request_url), data=json.dumps(payload), headers=headers)
        elif http_method == "post":
            response = self.session.post(self._format_admin_api_url(request_url), data=json.dumps(payload), headers=headers)
        elif http_method == "put":
            response = self.session.put(self._format_admin_api_url(request_url), data=json.dumps(payload), headers=headers)
        elif http_method == "delete":
            response = self.session.delete(self._format_admin_api_url(request_url))

        try:
            response.raise_for_status()
        except Exception as exc:
            if hasattr(exc, "response"):
                detailed_error = f" : {exc.response.text}"  # type: ignore
            else:
                detailed_error = ""
            raise ShopwareAPIError(f"{exc}{detailed_error}")

        return response

    def _get_token(self) -> Dict[str, Any]:
        """
        get access token, "Client Credentials Grant Type" or "Resource Owner Password Grant Type"

        :parameters
            conf.is_grant_type_resource_owner

        :return:
            the token, also saved in self.token

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> save_conf = my_api_client.config.grant_type

        >>> # test "Client Credentials Grant Type"
        >>> my_api_client.config.grant_type = 'user_credentials'
        >>> my_api_client._get_token()
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'refresh_token': '...', 'expires_at': ...}

        >>> # test "Resource Owner Password Grant Type"
        >>> my_api_client.config.grant_type = 'resource_owner'
        >>> my_api_client._get_token()
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'expires_at': ...}

        >>> # Teardown
        >>> my_api_client.config.grant_type = save_conf

        """

        if self.config.grant_type == "user_credentials":
            token = self._get_access_token_by_user_credentials()
        elif self.config.grant_type == "resource_owner":
            token = self._get_access_token_by_resource_owner()
        else:
            raise ShopwareAPIError(f'config.grant_type must bei either "user_credentials" or "resource_owner" not "{str(self.config.grant_type)}"')
        return token

    def _get_access_token_by_resource_owner(self) -> Dict[str, Any]:
        """
        get access token, "Client Credentials Grant Type"
        - no refresh token
        - should be used for machine-to-machine communications, such as CLI jobs or automated services

        see https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
        setup at admin/settings/system/itegrations: "access_id" and "access_secret"

        :parameter
            self.shopware_api_url   the api url, like : 'https://shop.yourdomain.com/api'
            self.client_id          the client ID, set up at setup at admin/settings/system/itegrations/access_id
            self.client_secret      the client secret, set up at setup at admin/settings/system/itegrations/access_secret

        :returns
            self.token

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> save_shopware_admin_api_url = my_api_client.config.shopware_admin_api_url
        >>> save_client_id = my_api_client.config.client_id
        >>> save_client_secret = my_api_client.config.client_secret

        >>> # Test Ok
        >>> my_api_client._get_access_token_by_resource_owner()
        {'token_type': 'Bearer', 'expires_in': 600, 'access_token': '...', 'expires_at': ...}

        >>> # Test no url
        >>> my_api_client.config.shopware_admin_api_url = ''
        >>> my_api_client._get_access_token_by_resource_owner()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: shopware_api_url needed
        >>> my_api_client.config.shopware_admin_api_url = save_shopware_admin_api_url

        >>> # Test no client_id
        >>> my_api_client.config.client_id = ''
        >>> my_api_client._get_access_token_by_resource_owner()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: client_id needed
        >>> my_api_client.config.client_id = save_client_id

        >>> # Test no client_secret
        >>> my_api_client.config.client_secret = ''
        >>> my_api_client._get_access_token_by_resource_owner()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: client_secret needed
        >>> my_api_client.config.client_secret = save_client_secret

        """
        if not self.config.shopware_admin_api_url:
            raise ShopwareAPIError("shopware_api_url needed")
        if not self.config.client_id:
            raise ShopwareAPIError("client_id needed")
        if not self.config.client_secret:
            raise ShopwareAPIError("client_secret needed")

        additional_parameters = {"grant_type": "user_credentials"}
        client = oauthlib.oauth2.BackendApplicationClient(client_id=self.config.client_id)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        self.token = oauth.fetch_token(
            token_url=self._format_admin_api_url("oauth/token"),
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            kwargs=additional_parameters,
        )
        return self.token

    def _get_access_token_by_user_credentials(self) -> Dict[str, Any]:
        """
        get access token, Integration (Resource Owner Password Grant)
        - with refresh token
        - we recommend to only use this grant flow for client applications that should
          perform administrative actions and require a user-based authentication

        see : https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#legacy-application-flow
        see : https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
        setup at admin/settings/system/user: "access_id" and "access_secret"

        :parameter
            self.shopware_api_url   the api url, like : 'https://shop.yourdomain.com/api'
            self.username           the username, set up at setup at admin/settings/system/users
            self.password           the password, set up at setup at admin/settings/system/users

        :returns
            self.token


        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> save_shopware_admin_api_url = my_api_client.config.shopware_admin_api_url
        >>> save_username = my_api_client.config.username
        >>> save_password = my_api_client.config.password

        >>> # Test Ok
        >>> my_api_client._get_access_token_by_user_credentials()
        {'token_type': 'Bearer', 'expires_in': 600, 'access_token': '...', 'refresh_token': '...', 'expires_at': ...}

        >>> # Test no url
        >>> my_api_client.config.shopware_admin_api_url = ''
        >>> my_api_client._get_access_token_by_user_credentials()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: shopware_api_url needed
        >>> my_api_client.config.shopware_admin_api_url = save_shopware_admin_api_url

        >>> # Test no username
        >>> my_api_client.config.username = ''
        >>> my_api_client._get_access_token_by_user_credentials()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: username needed
        >>> my_api_client.config.username = save_username

        >>> # Test no password
        >>> my_api_client.config.password = ''
        >>> my_api_client._get_access_token_by_user_credentials()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: password needed
        >>> my_api_client.config.password = save_password

        """

        if not self.config.shopware_admin_api_url:
            raise ShopwareAPIError("shopware_api_url needed")
        if not self.config.username:
            raise ShopwareAPIError("username needed")
        if not self.config.password:
            raise ShopwareAPIError("password needed")

        client_id = "administration"
        additional_parameters = {"grant_type": "password", "scopes": "write"}
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=client_id)
        session_oauth = requests_oauthlib.OAuth2Session(client=client)
        self.token = session_oauth.fetch_token(
            token_url=self._format_admin_api_url("oauth/token"),
            client_id=client_id,
            username=self.config.username,
            password=self.config.password,
            kwargs=additional_parameters,
        )
        return self.token

    def _get_session(self) -> None:
        """
        see : https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#legacy-application-flow
        see : https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation


        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # Test client credentials token
        >>> ignore = my_api_client._get_access_token_by_resource_owner()
        >>> my_api_client._get_session()
        >>> data = my_api_client.request_get('customer-group')

        >>> # Test resource owner token
        >>> ignore = my_api_client._get_access_token_by_user_credentials()
        >>> my_api_client._get_session()
        >>> data = my_api_client.request_get('customer-group')

        >>> # Test resource owner Token Refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> my_api_client._get_session()
        >>> data = my_api_client.request_get('customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        """
        try:
            if not self.token:
                self._get_token()
            if self._is_refreshable_token():
                self.token["expires_in"] = int(self.token["expires_at"] - time.time())
                client_id = "administration"
                extra = {"client_id": client_id}
                self.session = requests_oauthlib.OAuth2Session(
                    client_id, token=self.token, auto_refresh_kwargs=extra, auto_refresh_url=self._format_admin_api_url("oauth/token")
                )
            else:
                client_id = self.config.client_id
                self.session = requests_oauthlib.OAuth2Session(client_id, token=self.token)
        except requests_oauthlib.TokenUpdated as exc:
            self._token_saver(token=exc.token)

    def _token_saver(self, token: Dict[str, str]) -> None:
        """
        saves the token - this is needed for automatically refreshing the "resource owner" access token.
        the "user_credentials" can not be refreshed

        :parameter
            token:             the token to be saved

        :returns
            None

        """
        self.token = token

    def _is_refreshable_token(self) -> bool:
        """
        True if the token is refreshable ().
        the "resource owner" access token can be refreshed
        the "client_credentials" can not be refreshed
        """
        return "refresh_token" in self.token

    def _format_admin_api_url(self, request_url: str) -> str:
        """
        formatted url to make a request

        :parameter
            request_url:             the request url, for instance "oauth/token"
            self.shopware_api_url:          the api url, for instance https://your.shop-domain.com/api

        :returns
            the formatted url, like  https://your.shop-domain.com/api/oauth/token

        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_api_client._format_admin_api_url('test')
        'http.../api/test'

        """
        request_url = request_url.lstrip("/")
        return f"{self.config.shopware_admin_api_url}/{request_url}"

    @lru_cache(maxsize=None)
    def _get_headers(self) -> Dict[str, str]:
        """
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_api_client._get_headers()    # noqa
        {'Content-Type': 'application/json', 'Accept': 'application/json'}
        >>> my_api_client._get_headers.cache_clear()    # noqa

        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        return headers


def _load_config(use_docker_test_container: bool) -> ConfShopware6ApiBase:
    if _is_github_actions() or use_docker_test_container:   # pragma: no cover
        config = _load_config_for_docker_test_container()
        config.store_api_sw_access_key = _get_docker_test_container_store_access_key()
        _create_docker_test_container_resource_owner_credentials()
    else:
        config = _load_config_for_rotek_production()        # pragma: no cover
    return config


def _load_config_for_docker_test_container() -> ConfShopware6ApiBase:
    try:
        from conf_shopware6_api_base_docker_testcontainer import conf_shopware6_api_base
    except ImportError:  # pragma: no cover
        # Imports for Doctest
        from .conf_shopware6_api_base_docker_testcontainer import conf_shopware6_api_base  # type: ignore  # pragma: no cover
    return conf_shopware6_api_base


def _get_docker_test_container_store_access_key() -> str:
    """
    get the sales channel accessKey from the docker testcontainer
    :return:

    >>> if _is_local_docker_container_active():
    ...     store_access_key = _get_docker_test_container_store_access_key()
    ...     assert 26 == len(store_access_key)

    """
    config = _load_config_for_docker_test_container()
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    response_dict = admin_api_client.request_get("sales-channel")
    access_key = str(response_dict["data"][0]["accessKey"])
    return access_key


def _create_docker_test_container_resource_owner_credentials() -> None:
    """
    >>> if _is_local_docker_container_active():
    ...     _create_docker_test_container_resource_owner_credentials()
    ...     assert True == _is_resource_owner_credentials_present()

    """
    if not _is_resource_owner_credentials_present():
        _upsert_docker_test_container_resource_owner_credentials()


def _upsert_docker_test_container_resource_owner_credentials() -> None:
    """
    inserts resource_owner_credentials (admin) on the docker test container
    the credentials are hardcoded here and are also reflected in the config file

    """
    payload = {
        "id": "565c4ada878141d3b18d6977dbbd2a13",  # noqa
        "label": "dockware_integration_admin",  # noqa
        "accessKey": "SWIACWJOMUTXV1RMNGJUAKTUAA",  # noqa
        "secretAccessKey": "UkhvUG1qdmpuMjFudGJCdG1Xc0xMbEt2ck9CQ2xDTUtXMUZHRUQ",  # noqa
        "admin": True,
    }  # noqa
    config = _load_config_for_docker_test_container()
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    admin_api_client.request_post("integration", payload=payload)


def _is_resource_owner_credentials_present() -> bool:
    """
    Returns True if there are resource owner credentials present

    >>> if _is_local_docker_container_active():
    ...     discard = _is_resource_owner_credentials_present()

    """
    config = _load_config_for_docker_test_container()
    admin_api_client = Shopware6AdminAPIClientBase(config=config)
    admin_api_client._get_access_token_by_user_credentials()
    admin_api_client._get_session()
    response_dict = admin_api_client.request_post("search/integration")
    if response_dict["total"]:
        resource_owner_credentials_present = True
    else:
        resource_owner_credentials_present = False
    return resource_owner_credentials_present


def _load_config_for_rotek_production() -> ConfShopware6ApiBase:
    """
    load config file for the rotek shop

    """
    try:
        from conf_shopware6_api_base_rotek import conf_shopware6_api_base   # pragma: no cover
    except ImportError:                                                     # pragma: no cover
        # Imports for Doctest
        from .conf_shopware6_api_base_rotek import conf_shopware6_api_base  # type: ignore  # pragma: no cover
    return conf_shopware6_api_base                                          # pragma: no cover


def _is_github_actions() -> bool:
    """
    True if run on github actions
    >>> discard = _is_github_actions()
    """
    return os.getenv("GITHUB_ACTIONS", "false").lower() == "true"


def _is_local_docker_container_active() -> bool:
    """
    True if the local docker container is running

    >>> discard = _is_local_docker_container_active()

    """
    try:
        requests.get("http://localhost/admin")
        is_active = True
    except requests.exceptions.ConnectionError:
        is_active = False  # pragma: no cover
    return is_active


if __name__ == "__main__":
    print(b'this is a library only, the executable is named "lib_shopware6_api_base_cli.py"', file=sys.stderr)
