# STDLIB
import logging
from typing import Any

# EXT
import httpx
import orjson

from ._http_common import (
    DEFAULT_REQUEST_TIMEOUT,
    HEADER_SW_ACCESS_KEY,
    PayLoad,
    build_api_url,
    log_request,
    log_response,
)
from .conf_shopware6_api_base_classes import (
    ConfShopware6ApiBase,
    HttpMethod,
    ShopwareAPIError,
)
from .lib_shopware6_api_base_criteria import Criteria

logger = logging.getLogger(__name__)

__all__ = [
    "Shopware6StoreFrontClientBase",
]


class Shopware6StoreFrontClientBase:
    def __init__(self, config: ConfShopware6ApiBase) -> None:
        """
        the Shopware6 Storefront Base API

        :param config: Configuration object with API credentials and URLs.

        >>> from lib_shopware6_api_base import ConfShopware6ApiBase
        >>> my_config = ConfShopware6ApiBase(
        ...     shopware_storefront_api_url="https://shop.example.com/store-api",
        ...     store_api_sw_access_key="SWSC..."
        ... )
        >>> my_storefront_client = Shopware6StoreFrontClientBase(config=my_config)

        """
        self.config = config

    def request_delete(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        make a delete request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._request_dict(
            http_method=HttpMethod.DELETE,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_get(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        make a get request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
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
        response_dict = self._request_dict(
            http_method=HttpMethod.GET,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_get_list(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """
        make a get request, expecting a list of dictionaries as result

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
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
        response_l_dict = self._request_list(
            http_method=HttpMethod.GET,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_l_dict

    def request_patch(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        makes a patch request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._request_dict(
            http_method=HttpMethod.PATCH,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_post(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        make a post request

        parameters:
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
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
        response_dict = self._request_dict(
            http_method=HttpMethod.POST,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def request_put(
        self, request_url: str, payload: PayLoad = None, update_header_fields: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        make a put request

        parameters:
            http_method: get, post, put, delete
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields: allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict

        """
        response_dict = self._request_dict(
            http_method=HttpMethod.PUT,
            request_url=request_url,
            payload=payload,
            update_header_fields=update_header_fields,
        )
        return response_dict

    def _request_dict(
        self,
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        http requests a dictionary. raises ShopwareAPIError if the result is not a dictionary
        :param http_method:
        :param request_url:
        :param payload:
        :param update_header_fields: allows to modify or add header fields
        :return:
        """
        response = self._request(
            http_method=http_method, request_url=request_url, payload=payload, update_header_fields=update_header_fields
        )
        response_dict: dict[str, Any]
        if hasattr(response, "json"):  # pragma: no cover
            response_json = response.json()  # type: ignore
            if isinstance(response_json, list):
                raise ShopwareAPIError(
                    f"received a list instead of a dict - You need to use the method request_{http_method.value}_list"
                )
            response_dict = dict(response_json)
        else:
            response_dict = {}  # pragma: no cover
        return response_dict

    def _request_list(
        self,
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        http requests a list of dictionaries. raises ShopwareAPIError if the result is not a list
        :param http_method:
        :param request_url:
        :param payload:
        :param update_header_fields: allows to modify or add header fields
        :return:
        """
        response = self._request(
            http_method=http_method, request_url=request_url, payload=payload, update_header_fields=update_header_fields
        )
        response_l_dict: list[dict[str, Any]]
        if hasattr(response, "json"):  # pragma: no cover
            response_json = response.json()  # type: ignore
            if isinstance(response_json, dict):
                raise ShopwareAPIError(
                    f"received a dict instead of a list - You need to use the method request_{http_method.value}"
                )
            response_l_dict = list(response_json)
        else:
            response_l_dict = []  # pragma: no cover
        return response_l_dict

    def _request(
        self,
        http_method: HttpMethod,
        request_url: str,
        payload: PayLoad = None,
        update_header_fields: dict[str, str] | None = None,
    ) -> httpx.Response | None:
        """
        makes a request, using the conf.store_api_sw_access_key for authentication

        parameters:
            http_method: HttpMethod.GET, HttpMethod.PATCH, HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE
            request_url: API Url, without the common api prefix
            payload : a dictionary
            update_header_fields : allows to modify or add header fields

        returns
            response_dict: dictionary with the response as dict


        >>> # Setup
        >>> my_api_client = Shopware6StoreFrontClientBase()

        >>> # test GET (a new cart)
        >>> my_api_client._request(http_method=HttpMethod.GET, request_url='checkout/cart', payload={'name': 'rn_doctest'})
        <Response [200 OK]>

        >>> # test DELETE (a new cart)
        >>> my_api_client._request(http_method=HttpMethod.DELETE, request_url='checkout/cart')
        <Response [204 No Content]>

        >>> # test POST (a single product)
        >>> my_payload=Criteria(filter=[EqualsFilter(field='active', value='true')])
        >>> my_api_client._request(http_method=HttpMethod.POST, request_url='product', payload=my_payload)
        <Response [200 OK]>

        >>> # test Link does not exist (a single product)
        >>> my_api_client._request(http_method=HttpMethod.POST, request_url='product/000')
        Traceback (most recent call last):
            ...
        conf_shopware6_api_base_classes.ShopwareAPIError: Client error '400 Bad Request' for url ...

        """
        if isinstance(payload, Criteria):
            payload = payload.get_dict()
        storefront_api_url = self._build_storefront_api_url(endpoint=request_url)
        response: httpx.Response
        headers = self._get_headers(update_header_fields=update_header_fields)

        if http_method == HttpMethod.GET:
            response = httpx.request(
                "GET",
                storefront_api_url,
                params=payload,
                headers=headers,
                timeout=DEFAULT_REQUEST_TIMEOUT,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.PATCH:
            response = httpx.request(
                "PATCH",
                storefront_api_url,
                content=orjson.dumps(payload).decode(),
                headers=headers,
                timeout=DEFAULT_REQUEST_TIMEOUT,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.POST:
            response = httpx.request(
                "POST",
                storefront_api_url,
                content=orjson.dumps(payload).decode(),
                headers=headers,
                timeout=DEFAULT_REQUEST_TIMEOUT,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.PUT:
            response = httpx.request(
                "PUT",
                storefront_api_url,
                content=orjson.dumps(payload).decode(),
                headers=headers,
                timeout=DEFAULT_REQUEST_TIMEOUT,
                follow_redirects=self.config.follow_redirects,
            )
        elif http_method == HttpMethod.DELETE:
            response = httpx.request(
                "DELETE",
                storefront_api_url,
                headers=headers,
                timeout=DEFAULT_REQUEST_TIMEOUT,
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

    def _get_headers(self, update_header_fields: dict[str, str] | None = None) -> dict[str, str]:
        """
        parameters:
            update_header_fields : allows to modify or add header fields

        returns the default header fields


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
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            HEADER_SW_ACCESS_KEY: self.config.store_api_sw_access_key,
        }
        if update_header_fields is not None:
            headers.update(update_header_fields)
        return headers

    def _build_storefront_api_url(self, endpoint: str) -> str:
        """
        Constructs a fully qualified URL for accessing the Storefront API.

        Parameters:
            endpoint: A string representing the specific API endpoint to be accessed, e.g., "oauth/token".
            self.config.shopware_storefront_api_url: The base URL of the Storefront API, e.g., https://your.shop-domain.com/store-api.

        Returns:
            A string containing the fully qualified URL to the specified API endpoint, formatted as https://your.shop-domain.com/store-api/endpoint.

        Raises:
            ShopwareAPIError: If the endpoint contains invalid characters or path traversal attempts.

        Example:
        >>> my_api_client = Shopware6StoreFrontClientBase()
        >>> my_api_client._build_storefront_api_url('test')
        'http.../store-api/test'

        """
        return build_api_url(self.config.shopware_storefront_api_url, endpoint)
