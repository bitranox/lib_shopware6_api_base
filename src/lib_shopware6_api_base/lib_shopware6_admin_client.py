# STDLIB
import json
import logging
import time
from typing import Any

# EXT
import httpx
import orjson
from authlib.integrations.base_client import TokenExpiredError
from authlib.integrations.httpx_client import OAuth2Client

from ._http_common import (
    CONTENT_TYPE_JSON,
    MAX_RETRY_ATTEMPTS,
    PayLoad,
    build_api_url,
    get_payload_dict,
    is_type_bytes,
    is_type_criteria,
    log_request,
    log_response,
)
from .conf_shopware6_api_base_classes import (
    ConfShopware6ApiBase,
    GrantType,
    HttpMethod,
    ShopwareAPIError,
)

logger = logging.getLogger(__name__)

__all__ = [
    "Shopware6AdminAPIClientBase",
]


class Shopware6AdminAPIClientBase:
    def __init__(self, config: ConfShopware6ApiBase) -> None:
        """
        the Shopware6 Admin Base API

        :param config: Configuration object with API credentials and URLs.

        >>> from lib_shopware6_api_base import ConfShopware6ApiBase
        >>> my_config = ConfShopware6ApiBase(
        ...     shopware_admin_api_url="https://shop.example.com/api",
        ...     username="admin",
        ...     password="secret"
        ... )
        >>> my_api_client = Shopware6AdminAPIClientBase(config=my_config)

        """
        self.config = config
        self.token: dict[str, Any] = {}
        self.session: OAuth2Client | httpx.Client = httpx.Client()

    def request_get(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        makes a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
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
        response_dict = self._make_request(
            http_method=HttpMethod.GET,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_get_paginated(
        self,
        request_url: str,
        payload: PayLoad = None,
        junk_size: int = 100,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
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

        returns
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
        response_dict = self._request_paginated(
            http_method=HttpMethod.GET,
            request_url=request_url,
            payload=payload,
            junk_size=junk_size,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_patch(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = CONTENT_TYPE_JSON,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._make_request(
            http_method=HttpMethod.PATCH,
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_post(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = CONTENT_TYPE_JSON,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        makes a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._make_request(
            http_method=HttpMethod.POST,
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_post_paginated(
        self,
        request_url: str,
        payload: PayLoad = None,
        junk_size: int = 100,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
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

        returns
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

        >>> # search for orders
        >>> # test https://github.com/bitranox/lib_shopware6_api_base/issues/11
        >>> import pprint
        >>> date_from = '2024-09-29T00:00:00.000Z'
        >>> date_to = '2024-09-29T23:59:59.999Z'
        >>> my_criteria = Criteria()
        >>> my_criteria.filter.append(RangeFilter(field="orderDate", parameters = {'gte': date_from, 'lte': date_to}))
        >>> my_criteria.filter.append(MultiFilter('or', [
        ...     EqualsFilter(field='documents.documentType.technicalName', value='invoice'),
        ...     EqualsFilter(field='documents.documentType.technicalName', value='storno')]))
        >>> pprint_attrs(my_criteria)
        {'limit': None,
         'page': None,
         'filter': [{'type': 'range',
                     'field': 'orderDate',
                     'parameters': {'gte': '2024-09-29T00:00:00.000Z',
                                    'lte': '2024-09-29T23:59:59.999Z'}},
                    {'type': 'multi',
                     'operator': 'or',
                     'queries': [{'type': 'equals',
                                  'field': 'documents.documentType.technicalName',
                                  'value': 'invoice'},
                                 {'type': 'equals',
                                  'field': 'documents.documentType.technicalName',
                                  'value': 'storno'}]}],
         'term': None,
         'total_count_mode': None}
        >>> my_response_dict = my_api_client.request_post_paginated(request_url='search/order', payload=my_criteria)
        >>> pprint.pprint(my_response_dict)
        {'data': []}
        """
        response_dict = self._request_paginated(
            http_method=HttpMethod.POST,
            request_url=request_url,
            payload=payload,
            junk_size=junk_size,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_put(
        self,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = CONTENT_TYPE_JSON,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        makes a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary or bytes
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._make_request(
            http_method=HttpMethod.PUT,
            request_url=request_url,
            payload=payload,
            content_type=content_type,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_delete(
        self,
        request_url: str,
        payload: PayLoad = None,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        makes a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._make_request(
            http_method=HttpMethod.DELETE,
            request_url=request_url,
            payload=payload,
            additional_query_params=additional_query_params,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def _request_paginated(
        self,
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad = None,
        junk_size: int = 100,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        request the data paginated for performance reasons - metadata 'total' and 'totalCountMode' will be updated
        the paginated request reads all records in junks of junk_size=100 up to "limit"

        payload "limit" will be respected (meaning we deliver only 'limit' results back)
        "page" will be ignored

        parameters:
            http_method: HttpMethod.GET, HttpMethod.PATCH, HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE
            request_url: API Url, without the common api prefix
            payload : a dictionary
            junk_size : the junk size
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict: dict[str, Any] = {}
        response_dict["data"] = []
        payload_dict = get_payload_dict(payload)

        # when 'ids' are given, limit does not apply, so we need to set
        # 'limit' and 'junk_size' to len(payload.ids)
        if is_type_criteria(payload) and payload.ids:  # type: ignore
            ids_limit = len(payload.ids)  # type: ignore
            junk_size = ids_limit
            payload_dict["limit"] = ids_limit

        total_limit: None | int
        records_left: None | int

        total_limit = payload_dict.get("limit")

        if total_limit is None:
            payload_dict["limit"] = str(junk_size)
            records_left = 0
        else:
            payload_dict["limit"] = min(total_limit, junk_size)
            records_left = total_limit

        page = 1

        while True:
            payload_dict["page"] = page

            partial_data = self._make_request(
                http_method=http_method,
                request_url=request_url,
                payload=payload_dict,
                update_header_fields=update_header_fields,
            )
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
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad = None,
        content_type: str = CONTENT_TYPE_JSON,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        makes a request - creates and refresh a token and sessions as needed

        parameters:
            http_method: HttpMethod.GET, HttpMethod.PATCH, HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE
            request_url: API Url, without the common api prefix
            payload : a dictionary , a criteria object, or bytes (for file uploads)
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict


        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()

        >>> # test resource owner token
        >>> ignore = my_api_client._get_access_token_by_user_credentials()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client._make_request(HttpMethod.GET, 'customer-group')  # noqa

        >>> # test resource owner token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client._make_request(HttpMethod.GET, 'customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        >>> # Test client credentials token
        >>> ignore = my_api_client._get_access_token_by_resource_owner()
        >>> my_api_client._get_session()
        >>> ignore = my_api_client._make_request(HttpMethod.GET, 'customer-group')  # noqa

        >>> # test client credentials token refresh
        >>> my_access_token = my_api_client.token['access_token']
        >>> my_api_client.token['expires_in']=-1
        >>> my_api_client.token['expires_at']=time.time()-1
        >>> ignore = my_api_client._make_request(HttpMethod.GET, 'customer-group')
        >>> assert my_api_client.token['access_token'] != my_access_token

        >>> # test invalid endpoint
        >>> ignore = my_api_client._make_request(HttpMethod.GET, 'not-existing')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: 404 Client Error: ...

        """

        retry = MAX_RETRY_ATTEMPTS
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
            except TokenExpiredError:
                if self._is_refreshable_token():  # pragma: no cover
                    # this actually should never happen - just in case.
                    # Authlib handles token refresh via callback automatically
                    logger.warning(
                        "something went wrong - the token should have been automatically refreshed. getting a new token"
                    )  # pragma: no cover
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
                # retry: how often to retry - sometimes we get error code:9, status:401,
                # The resource owner or authorization server denied the request,
                # detail: Access token could not be verified.
                # But it works if You try again, it seems to be an error in shopware API or race condition
                retry = retry - 1
                if not retry:
                    raise exc

            if not retry:
                break

        response_dict: dict[str, Any]
        try:
            response_dict = dict(response.json())  # type: ignore[possibly-undefined]
        except (json.JSONDecodeError, ValueError) as exc:
            logger.debug("Failed to decode JSON response: %s", exc)
            response_dict = {}
        return response_dict

    def _request(
        self,
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad,
        content_type: str = CONTENT_TYPE_JSON,
        additional_query_params: dict[str, Any] | None = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> httpx.Response:
        """
        makes a request, needs a "self.session" to be set up and authenticated

        parameters:
            http_method: HttpMethod.GET, HttpMethod.PATCH, HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE
            request_url: API Url, without the common api prefix
            payload : a dictionary , a criteria object, or bytes (for file uploads)
            content_type: any valid content type like json, octet-stream, ...
            additional_query_params: additional query parameters for patch, post, put, delete
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        see : https://www.python-httpx.org/quickstart/

        """
        request_data: str
        payload_dict: dict[str, Any] = {}

        if is_type_bytes(payload):
            request_data = str(payload)
            if content_type.lower() == CONTENT_TYPE_JSON:
                raise ShopwareAPIError('Content type "json" does not match the payload data type "bytes"')
        else:
            payload_dict = get_payload_dict(payload)
            request_data = orjson.dumps(payload_dict).decode()

        if not additional_query_params:
            additional_query_params = {}

        response: httpx.Response
        headers = self._get_headers(content_type=content_type, update_header_fields=update_header_fields)

        if http_method == HttpMethod.GET:
            if additional_query_params:
                raise ShopwareAPIError("query parameters for GET requests need to be provided as payload")
            response = self.session.get(
                self._format_admin_api_url(request_url),
                params=payload_dict,
                headers=headers,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.PATCH:
            response = self.session.patch(
                self._format_admin_api_url(request_url),
                content=request_data,
                headers=headers,
                params=additional_query_params,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.POST:
            response = self.session.post(
                self._format_admin_api_url(request_url),
                content=request_data,
                headers=headers,
                params=additional_query_params,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.PUT:
            response = self.session.put(
                self._format_admin_api_url(request_url),
                content=request_data,
                headers=headers,
                params=additional_query_params,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.DELETE:
            response = self.session.delete(
                self._format_admin_api_url(request_url),
                params=additional_query_params,
                follow_redirects=self.config.follow_redirects,
            )

        # Log request/response if enabled
        if self.config.enable_request_logging:
            log_request(response.request)  # type: ignore[possibly-undefined]
            log_response(response)

        try:
            response.raise_for_status()  # type: ignore[possibly-undefined]
        except httpx.HTTPStatusError as exc:
            detailed_error = f" : {exc.response.text}"
            raise ShopwareAPIError(f"{exc}{detailed_error}") from exc

        return response

    def _get_token(self) -> dict[str, Any]:
        """
        get access token, "Client Credentials Grant Type" or "Resource Owner Password Grant Type"

        parameters
            conf.is_grant_type_resource_owner

        :return:
            the token, also saved in "self.token"

        >>> # Setup
        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> save_conf = my_api_client.config.grant_type

        >>> # test "Client Credentials Grant Type"
        >>> my_api_client.config.grant_type = GrantType.USER_CREDENTIALS
        >>> my_api_client._get_token()
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'refresh_token': '...', 'expires_at': ...}

        >>> # test "Resource Owner Password Grant Type"
        >>> my_api_client.config.grant_type = GrantType.RESOURCE_OWNER
        >>> my_api_client._get_token()
        {'token_type': 'Bearer', 'expires_in': ..., 'access_token': '...', 'expires_at': ...}

        >>> # test invalid type, which should fail
        >>> my_api_client.config.grant_type = None
        >>> my_api_client._get_token()
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: config.grant_type must be GrantType.USER_CREDENTIALS or GrantType.RESOURCE_OWNER, not None

        >>> # Teardown
        >>> my_api_client.config.grant_type = save_conf

        """

        if self.config.grant_type == GrantType.USER_CREDENTIALS:
            token = self._get_access_token_by_user_credentials()
        elif self.config.grant_type == GrantType.RESOURCE_OWNER:
            token = self._get_access_token_by_resource_owner()
        else:
            raise ShopwareAPIError(
                f"config.grant_type must be GrantType.USER_CREDENTIALS or GrantType.RESOURCE_OWNER, not {self.config.grant_type!r}"
            )
        return token

    def _get_access_token_by_resource_owner(self) -> dict[str, Any]:
        """
        get access token, "Client Credentials Grant Type"
        - no refresh token
        - should be used for machine-to-machine communications, such as CLI jobs or automated services

        see https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
        setup via Web Administration Interface > settings > system > integration: "access_id" and "access_secret"
        or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

        parameter
            self.config.shopware_api_url    the api url, like : 'https://shop.yourdomain.com/api'
            self.config.client_id           the client ID, setup via Web Administration Interface > settings > system > integration: "access_id"
                                            or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

            self.config.client_secret       the client secret, setup via Web Administration Interface > settings > system > integration: "access_secret"
                                            or directly via URL : https://shop.yourdomain.com/admin#/sw/integration/index

        returns
            "self.token"

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

        client = OAuth2Client(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
        )
        self.token = client.fetch_token(
            url=self._format_admin_api_url("oauth/token"),
            grant_type="client_credentials",
        )
        return self.token

    def _get_access_token_by_user_credentials(self) -> dict[str, Any]:
        """
        get access token, Integration (Resource Owner Password Grant)
        - with refresh token
        - we recommend to only use this grant flow for client applications that should
          perform administrative actions and require a user-based authentication

        see : https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#legacy-application-flow
        see : https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
        setup at admin/settings/system/user: "access_id" and "access_secret"

        parameter
            self.config.shopware_api_url   the api url, like : 'https://shop.yourdomain.com/api'
            self.config.username           the username, set up at setup at admin/settings/system/users
            self.config.password           the password, set up at setup at admin/settings/system/users

        returns and sets
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

        client = OAuth2Client(client_id="administration")
        self.token = client.fetch_token(
            url=self._format_admin_api_url("oauth/token"),
            grant_type="password",
            username=self.config.username,
            password=self.config.password,
        )
        return self.token

    def _get_session(self) -> None:
        """
        see : https://docs.authlib.org/en/latest/client/httpx.html
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
        if not self.token:
            self._get_token()
        if self._is_refreshable_token():
            self.token["expires_in"] = int(self.token["expires_at"] - time.time())
            client_id = "administration"
            self.session = OAuth2Client(
                client_id=client_id,
                token=self.token,
                token_endpoint=self._format_admin_api_url("oauth/token"),
                update_token=self._token_saver,
            )
        else:
            client_id = self.config.client_id
            self.session = OAuth2Client(client_id=client_id, token=self.token)

    def _token_saver(
        self,
        token: dict[str, Any],
        refresh_token: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """
        saves the token - this is needed for automatically refreshing the "resource owner" access token.
        the "user_credentials" can not be refreshed

        This is the callback for Authlib's OAuth2Client update_token parameter.

        parameter
            token:             the token to be saved
            refresh_token:     optional refresh token (Authlib callback parameter)
            access_token:      optional access token (Authlib callback parameter)

        returns
            None

        """
        _ = refresh_token, access_token  # unused, but required by Authlib callback signature
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
            request_url:                        the request url, for instance "oauth/token"
            self.config.shopware_api_url:       the api url, for instance https://your.shop-domain.com/api

        :returns
            the formatted url, like  https://your.shop-domain.com/api/oauth/token

        :raises
            ShopwareAPIError: If the endpoint contains invalid characters or path traversal attempts.

        >>> my_api_client = Shopware6AdminAPIClientBase()
        >>> my_api_client._format_admin_api_url('test')
        'http.../api/test'

        """
        return build_api_url(self.config.shopware_admin_api_url, request_url)

    @staticmethod
    def _get_headers(content_type: str = CONTENT_TYPE_JSON, update_header_fields: dict[str, str] | None = None) -> dict[str, str]:
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
