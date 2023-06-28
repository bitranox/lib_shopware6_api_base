# STDLIB
import os
from functools import lru_cache
import json

import logging
import sys
import time
from typing import Any, Dict, List, Optional, Union, cast

# EXT
import oauthlib
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
import requests
import requests_oauthlib

# conf
try:
    from conf_shopware6_api_base_classes import *
    from lib_shopware6_api_base_criteria import *
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .conf_shopware6_api_base_classes import *  # type: ignore  # pragma: no cover
    from .lib_shopware6_api_base_criteria import *


logger = logging.getLogger(__name__)

# payload_type{{{
PayLoad = Union[None, Dict[str, Any], Criteria]
# payload_type}}}

# Endpoints like /api/_action/sync require request specific custom headers to manipulate the api behavior
# see : https://shopware.stoplight.io/docs/admin-api/faf8f8e4e13a0-bulk-payloads#performance
# see : https://shopware.stoplight.io/docs/admin-api/0612cb5d960ef-bulk-edit-entities
# You may pass such custom header fields like that :
#       only for python version >= 3.8 :
#      update_header_fields = HEADER_write_in_single_transactions | HEADER_index_asynchronously
#   or the same written explicitly for python 3.7 :
#      update_heater_fields = {'single-operation' : 'true', 'indexing-behavior' : 'use-queue-indexing'}
#   and pass those "update_heater_fields" to the request method (mostly request_post, with endpoint "/api/_action/sync")
# headers_for_bulk_operations{{{
HEADER_write_in_separate_transactions: Dict[str, str] = {"single-operation": "false"}  # default
HEADER_write_in_single_transactions: Dict[str, str] = {"single-operation": "true"}
HEADER_index_synchronously: Dict[str, str] = {"indexing-behavior": "null"}  # default
HEADER_index_asynchronously: Dict[str, str] = {"indexing-behavior": "use-queue-indexing"}
HEADER_index_disabled: Dict[str, str] = {"indexing-behavior": "disable-indexing"}
HEADER_fail_on_error: Dict[str, str] = {"fail-on-error": "true"}  # default
HEADER_do_not_fail_on_error: Dict[str, str] = {"fail-on-error": "false"}
# headers_for_bulk_operations}}}


# store_api{{{
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
        # store_api}}}
        self.use_docker_test_container = use_docker_test_container

        if config is None:
            config = _load_config(use_docker_test_container=use_docker_test_container)

        self.config = config

    # store_api_delete{{{
    def request_delete(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # store_api_delete}}}
        response_dict = self._request_dict(http_method="delete", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    # store_api_get{{{
    def request_get(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

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
        # store_api_get}}}
        response_dict = self._request_dict(http_method="get", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    # store_api_get_list{{{
    def request_get_list(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        make a get request, expecting a list of dictionaries as result

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

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
        # store_api_get_list}}}
        response_l_dict = self._request_list(http_method="get", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_l_dict

    # store_api_patch{{{
    def request_patch(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # store_api_patch}}}
        response_dict = self._request_dict(http_method="patch", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    # store_api_post{{{
    def request_post(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

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
        # store_api_post}}}

        response_dict = self._request_dict(http_method="post", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    # store_api_put{{{
    def request_put(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        make a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # store_api_put}}}
        response_dict = self._request_dict(http_method="put", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    def _request_dict(
        self, http_method: str, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        http requests a dictionary. raises ShopwareAPIError if the result is not a dictionary
        :param http_method:
        :param request_url:
        :param payload:
        :param update_header_fields: allows to modify or add header fields
        :return:
        """
        response = self._request(http_method=http_method, request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        if hasattr(response, "json"):  # pragma: no cover
            response_json = response.json()  # type: ignore
            if isinstance(response_json, list):
                raise ShopwareAPIError(f"received a list instead of a dict - You need to use the method request_{http_method}_list")
            response_dict = dict(response_json)
        else:
            response_dict = dict()  # pragma: no cover
        return response_dict

    def _request_list(
        self, http_method: str, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        http requests a list of dictionaries. raises ShopwareAPIError if the result is not a list
        :param http_method:
        :param request_url:
        :param payload:
        :param update_header_fields: allows to modify or add header fields
        :return:
        """
        response = self._request(http_method=http_method, request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        if hasattr(response, "json"):  # pragma: no cover
            response_json = response.json()  # type: ignore
            if isinstance(response_json, dict):
                raise ShopwareAPIError(f"received a dict instead of a list - You need to use the method request_{http_method}")
            response_l_dict = list(response_json)
        else:
            response_l_dict = list()  # pragma: no cover
        return response_l_dict

    def _request(
        self, http_method: str, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Optional[requests.Response]:
        """
        makes a request, using the conf.store_api_sw_access_key for authentication

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields : allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict


        >>> # Setup
        >>> my_api_client = Shopware6StoreFrontClientBase()

        >>> # test GET (a new cart)
        >>> my_api_client._request(http_method='get', request_url='checkout/cart', payload={'name': 'rn_doctest'})
        <Response [200]>

        >>> # test DELETE (a new cart)
        >>> my_api_client._request(http_method='delete', request_url='checkout/cart')
        <Response [204]>

        >>> # test POST (a single product)
        >>> my_payload=Criteria(filter=[EqualsFilter(field='active', value='true')])
        >>> my_api_client._request(http_method='post', request_url='product', payload=my_payload)
        <Response [200]>

        >>> # test Link does not exist (a single product)
        >>> my_api_client._request(http_method='post', request_url='product/000')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: 400 Client Error: Bad Request for url: ...

        """
        if isinstance(payload, Criteria):
            payload = payload.get_dict()
        formatted_request_url = self._format_storefront_api_url(request_url)
        response: requests.Response = requests.Response()
        headers = self._get_headers(update_header_fields=update_header_fields)

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
            if hasattr(exc, "response"):  # pragma: no cover
                detailed_error = f" : {exc.response.text}"  # type: ignore
            else:
                detailed_error = ""  # pragma: no cover
            raise ShopwareAPIError(f"{exc}{detailed_error}")
        return response

    def _get_headers(self, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        parameters:
            update_header_fields : allows to modify or add header fields

        :returns the default header fields


        >>> my_api_client = Shopware6StoreFrontClientBase()
        >>> my_api_client._get_headers()
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'sw-access-key': '...'}
        >>> # add keys
        >>> my_api_client._get_headers(update_header_fields = {'single-operation': '1', 'indexing-behavior': 'use-queue-indexing'})
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'sw-access-key': '...', 'single-operation': '1', 'indexing-behavior': '...'}
        >>> # add and update keys
        >>> my_api_client._get_headers(update_header_fields = {'single-operation': '1', 'sw-access-key': 'xyz'})
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'sw-access-key': 'xyz', 'single-operation': '1'}

        >>> # only for python >= 3.8:
        >>> # my_update_header_fields = HEADER_index_asynchronously | HEADER_write_in_single_transactions

        >>> # for python <= 3.7:
        >>> my_update_header_fields: dict = dict()
        >>> my_update_header_fields.update(HEADER_index_asynchronously)
        >>> my_update_header_fields.update(HEADER_write_in_single_transactions)
        >>> my_api_client._get_headers(update_header_fields=my_update_header_fields)
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'sw-access-key': '...', 'indexing-behavior': 'use-queue-indexing',
        'single-operation': 'true'}

        """
        headers = {"Content-Type": "application/json", "Accept": "application/json", "sw-access-key": self.config.store_api_sw_access_key}
        if update_header_fields is not None:
            headers.update(update_header_fields)
        return headers

    def _format_storefront_api_url(self, request_url: str) -> str:
        """
        formatted url to make a request

        :parameter
            request_url:                        the request url, for instance "oauth/token"
            self.shopware_storefront_api_url:   the api url, for instance https://your.shop-domain.com/store-api

        :returns
            the formatted url, like  https://your.shop-domain.com/store-api/product

        >>> my_api_client = Shopware6StoreFrontClientBase()
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
    def request_get(self, request_url: str, payload: PayLoad = None, update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        makes a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

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
        response_dict = self._make_request(http_method="get", request_url=request_url, payload=payload, update_header_fields=update_header_fields)
        return response_dict

    # admin_api_get_paginated{{{
    def request_get_paginated(
        self, request_url: str, payload: PayLoad = None, junk_size: int = 100, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        get the data paginated - metadata 'total' and 'totalCountMode' will be updated
        the paginated request reads those records in junks of junk_size=100 for performance reasons.

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        payload "page" will be ignored

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            limit : the junk size
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, no limit
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', junk_size=3)
        >>> assert 3 < len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 2
        >>> my_payload={'limit': 2}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 2 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        >>> # test read product junk_size=10, limit = None
        >>> my_payload=Criteria()
        >>> my_response_dict = my_api_client.request_get_paginated(request_url='product', payload=my_payload, junk_size=10)
        >>> assert 5 < len(my_response_dict['data'])


        """
        # admin_api_get_paginated}}}
        response_dict = self._request_paginated(
            http_method="get", request_url=request_url, payload=payload, junk_size=junk_size, update_header_fields=update_header_fields
        )
        return response_dict

    # admin_api_patch{{{
    def request_patch(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_patch}}}
        response_dict = self._make_request(
            http_method="patch",
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    # admin_api_post{{{
    def request_post(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_post}}}
        response_dict = self._make_request(
            http_method="post",
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    # admin_api_post_paginated{{{
    def request_post_paginated(
        self, request_url: str, payload: PayLoad = None, junk_size: int = 100, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        post the data paginated - metadata 'total' and 'totalCountMode' will be updated
        if You expect a big number of records, the paginated request reads those records in junks of junk_size=100 for performance reasons.

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        payload "page" will be ignored

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            junk_size : the junk size
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_url = 'search/product'

        >>> # test read product junk_size=10, limit = None
        >>> my_payload=Criteria()
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=10)
        >>> assert 5 < len(my_response_dict['data'])

        >>> # test read product junk_size=10, no limit
        >>> my_payload=None
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=10)
        >>> assert 10 < len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 2
        >>> my_payload={'limit': 2}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=3)
        >>> assert 2 == len(my_response_dict['data'])

        >>> # test read product junk_size=3, limit = 4
        >>> my_payload={'limit': 4}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url=my_url, payload=my_payload, junk_size=3)
        >>> assert 4 == len(my_response_dict['data'])

        """
        # admin_api_post_paginated}}}
        response_dict = self._request_paginated(
            http_method="post", request_url=request_url, payload=payload, junk_size=junk_size, update_header_fields=update_header_fields
        )
        return response_dict

    # admin_api_put{{{
    def request_put(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_put}}}
        response_dict = self._make_request(
            http_method="put",
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    # admin_api_delete{{{
    def request_delete(
        self,
        request_url: str,
        payload: PayLoad = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        """
        # admin_api_delete}}}
        response_dict = self._make_request(
            http_method="delete",
            request_url=request_url,
            payload=payload,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def _request_paginated(
        self, http_method: str, request_url: str, payload: PayLoad = None, junk_size: int = 100, update_header_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        request the data paginated - metadata 'total' and 'totalCountMode' will be updated
        the paginated request reads those records in junks of junk_size=100 for performance reasons.

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        "page" will be ignored

        parameters:
            http_method:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            junk_size : the junk size
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict


        :param http_method:
        :param request_url:
        :param payload:
        :param junk_size:
        :return:
        """
        response_dict: Dict[str, Any] = dict()
        response_dict["data"] = list()
        payload_dict = _get_payload_dict(payload)

        # when 'ids' are given, limit does not apply, so we need to set
        # 'limit' and 'junk_size' to len(payload.ids)
        if _is_type_criteria(payload):
            if payload.ids:  # type: ignore
                ids_limit = len(payload.ids)  # type: ignore
                junk_size = ids_limit
                payload_dict["limit"] = ids_limit

        total_limit: Union[None, int]
        records_left: Union[None, int]

        if "limit" in payload_dict:
            total_limit = payload_dict["limit"]
        else:
            total_limit = None

        if total_limit is None:
            payload_dict["limit"] = str(junk_size)
            records_left = 0
        else:
            payload_dict["limit"] = min(total_limit, junk_size)
            records_left = total_limit

        page = 1

        while True:
            payload_dict["page"] = page

            partial_data = self._make_request(http_method=http_method, request_url=request_url, payload=payload_dict, update_header_fields=update_header_fields)
            if partial_data["data"]:
                response_dict["data"] = response_dict["data"] + partial_data["data"]
                page = page + 1
                if total_limit is not None:
                    records_left = records_left - len(partial_data["data"])
                    if records_left < 1:
                        response_dict["data"] = response_dict["data"][:total_limit]
                        break
            else:
                break
        return response_dict

    def _make_request(
        self,
        http_method: str,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        makes a request - creates and refresh a token and sessions as needed

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary , a criteria object, or bytes (for file uploads)
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

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

        retry = 2
        while True:
            try:
                self._get_session()
                response = self._request(
                    http_method=http_method,
                    request_url=request_url,
                    payload=payload,
                    content_type=content_type,
                    additional_query_params=additional_query_params,
                    update_header_fields=update_header_fields,
                )
                retry = 0
            except requests_oauthlib.TokenUpdated as exc:
                self._token_saver(token=exc.token)
                response = self._request(
                    http_method=http_method,
                    request_url=request_url,
                    payload=payload,
                    content_type=content_type,
                    additional_query_params=additional_query_params,
                    update_header_fields=update_header_fields,
                )
                retry = 0
            except TokenExpiredError:
                if self._is_refreshable_token():  # pragma: no cover
                    # this actually should never happen - just in case.
                    logger.warning("something went wrong - the token should have been automatically refreshed. getting a new token")  # pragma: no cover
                    self._get_access_token_by_user_credentials()  # pragma: no cover
                else:
                    self._get_access_token_by_resource_owner()
                self._get_session()
                response = self._request(
                    http_method=http_method,
                    request_url=request_url,
                    payload=payload,
                    content_type=content_type,
                    additional_query_params=additional_query_params,
                    update_header_fields=update_header_fields,
                )
                retry = 0
            except ShopwareAPIError as exc:
                """
                retry   : how often to retry - sometimes we get error code:9, status:401, The resource owner or authorization server denied the request,
                detail: Access token could not be verified.
                But it works if You try again, it seems to be an error in shopware API or race condition
                """
                retry = retry - 1
                if not retry:
                    raise exc

            if not retry:
                break

        try:
            # noinspection PyUnboundLocalVariable
            response_dict = dict(response.json())
        except Exception:  # noqa
            response_dict = dict()
        return response_dict

    def _request(
        self,
        http_method: str,
        request_url: str,
        payload: PayLoad,
        content_type: str = "json",
        additional_query_params: Optional[Dict[str, Any]] = None,
        update_header_fields: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        makes a request, needs a self.session to be set up and authenticated

        parameters:
            http_method: 'get', 'patch', 'post', 'put', 'delete'
            request_url: API Url, without the common api prefix
            payload : a dictionary , a criteria object, or bytes (for file uploads)
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        :returns
            response_dict: dictionary with the response as dict

        see : https://docs.python-requests.org/en/latest/user/quickstart/

        """
        request_data: Union[str, PayLoad]
        payload_dict = dict()

        if _is_type_bytes(payload):
            request_data = payload
            if content_type.lower() == "json":
                raise ShopwareAPIError('Content type "json" does not match the payload data type "bytes"')
        else:
            payload_dict = _get_payload_dict(payload)
            request_data = json.dumps(payload_dict)

        if not additional_query_params:
            additional_query_params = dict()

        response: requests.Response = requests.Response()
        headers = self._get_headers(content_type=content_type, update_header_fields=update_header_fields)

        if http_method == "get":
            if additional_query_params:
                raise ShopwareAPIError("query parameters for GET requests need to be provided as payload")
            response = self.session.get(self._format_admin_api_url(request_url), params=payload_dict, headers=headers)
        elif http_method == "patch":
            response = self.session.patch(self._format_admin_api_url(request_url), data=request_data, headers=headers, params=additional_query_params)
        elif http_method == "post":
            response = self.session.post(self._format_admin_api_url(request_url), data=request_data, headers=headers, params=additional_query_params)
        elif http_method == "put":
            response = self.session.put(self._format_admin_api_url(request_url), data=request_data, headers=headers, params=additional_query_params)
        elif http_method == "delete":
            response = self.session.delete(self._format_admin_api_url(request_url), params=additional_query_params)

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
        setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
        or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

        :parameter
            self.shopware_api_url   the api url, like : 'https://shop.yourdomain.com/api'
            self.client_id          the client ID, setup via Web Administration Interface > settings > system > integration: "access_id"
                                    or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

            self.client_secret      the client secret, setup via Web Administration Interface > settings > system > integration: "access_secret"
                                    or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

        :returns
            self.token

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> save_shopware_admin_api_url = my_api_client.config.shopware_admin_api_url
        >>> save_client_id = my_api_client.config.client_id
        >>> save_client_secret = my_api_client.config.client_secret

        >>> # Test Ok
        >>> my_api_client._get_access_token_by_resource_owner()
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'expires_at': ...}

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
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'refresh_token': '...', 'expires_at': ...}

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

    @staticmethod
    def _get_headers(content_type: str = "json", update_header_fields: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        content_type can be any valid content type like json, octet-stream,

        parameters:
            update_header_fields: allows to modify or add header fields


        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_api_client._get_headers()
        {'Content-Type': 'application/json', 'Accept': 'application/json'}

        >>> my_api_client._get_headers(content_type='json')
        {'Content-Type': 'application/json', 'Accept': 'application/json'}

        >>> my_api_client._get_headers(content_type='octet-stream')
        {'Content-Type': 'application/octet-stream', 'Accept': 'application/json'}

        >>> # only for python >= 3.8:
        >>> # my_update_header_fields = HEADER_index_asynchronously | HEADER_write_in_single_transactions

        >>> # for python <= 3.7:
        >>> my_update_header_fields: dict = dict()
        >>> my_update_header_fields.update(HEADER_index_asynchronously)
        >>> my_update_header_fields.update(HEADER_write_in_single_transactions)
        >>> my_api_client._get_headers(content_type='json', update_header_fields=my_update_header_fields)
        {'Content-Type': 'application/json', 'Accept': 'application/json', 'indexing-behavior': 'use-queue-indexing', 'single-operation': 'true'}

        """
        headers = {"Content-Type": f"application/{content_type.lower()}", "Accept": "application/json"}
        if update_header_fields is not None:
            headers.update(update_header_fields)
        return headers


def _load_config(use_docker_test_container: bool) -> ConfShopware6ApiBase:
    if _is_github_actions() or use_docker_test_container:  # pragma: no cover
        config = _load_config_for_docker_test_container()
        config.store_api_sw_access_key = _get_docker_test_container_store_access_key()
        _create_docker_test_container_resource_owner_credentials()
    else:
        config = _load_config_for_rotek_production()  # pragma: no cover
    return config


def _load_config_for_docker_test_container() -> ConfShopware6ApiBase:
    try:
        from conf_shopware6_api_base_docker_testcontainer import conf_shopware6_api_base
    except ImportError:  # pragma: no cover
        # Imports for Doctest
        from .conf_shopware6_api_base_docker_testcontainer import conf_shopware6_api_base  # type: ignore  # pragma: no cover
    return conf_shopware6_api_base  # type: ignore


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
    try:  # pragma: no cover
        from conf_shopware6_api_base_rotek import conf_shopware6_api_base  # pragma: no cover
    except ImportError:  # pragma: no cover
        # Imports for Doctest
        from .conf_shopware6_api_base_rotek import conf_shopware6_api_base  # type: ignore  # pragma: no cover
    return conf_shopware6_api_base  # type: ignore


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
    except requests.exceptions.ConnectionError:  # pragma: no cover
        is_active = False  # pragma: no cover
    return is_active


def _is_type_bytes(payload: PayLoad) -> bool:
    """True if the passed type is bytes"""
    return type(payload).__name__ == "bytes"


def _is_type_criteria(payload: PayLoad) -> bool:
    """True if the passed type is Criteria"""
    return type(payload).__name__ == "Criteria"


def _get_payload_dict(payload: PayLoad) -> Dict[str, Any]:
    """return the payload as dictionary"""
    if payload is None:
        payload = dict()
    elif _is_type_criteria(payload):
        payload = payload.get_dict()  # type: ignore
    return payload  # type: ignore


if __name__ == "__main__":
    print(b'this is a library only, the executable is named "lib_shopware6_api_base_cli.py"', file=sys.stderr)
