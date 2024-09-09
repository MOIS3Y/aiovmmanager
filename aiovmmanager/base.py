import urllib
import aiohttp

from typing import Optional


class BaseSession(object):
    """
    Base class wrapper over aiohttp.ClientSession
    The class is a context manager.
    All others inherit from this class
    and extend it depending on the direction of requests
    It should not be used as an independent class;
    instead, classes that inherit its properties should be used.
    -- -- --
    url: base platform url
    definition: API definition (auth,vm,ip,dnsproxy)
    version: API version will be part of the full url path
    ssl: enable or disable certificate authentication
    **kwargs: named arguments that will be passed to aiohttp.ClientSession.
    """
    def __init__(
        self,
        url: str,
        definition: str,
        version: str,
        ssl: Optional[bool] = True,
        **kwargs
    ) -> None:
        self.url = url
        self.definition = definition
        self.version = version
        self.ssl = ssl
        self._kwargs = kwargs

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            base_url=self.url,
            **self._kwargs
        )
        return self

    async def __aexit__(self, *err):
        await self._session.close()
        self._session = None

    @property
    def endpoint(self) -> str:
        """
        The calculated property forms part of the url
        depending on the direction and version of the API
        """
        return f'/{self.definition}/{self.version}'

    async def get(
        self,
        url: str,
        params: Optional[dict] = {},
        content_type: Optional[str] = "application/json",
        **kwargs
    ) -> dict:
        """
        HTTP GET request.
        Some endpoints use filters.
        In the case of VMmanager 6, the standard get aiohttp.ClientSession
        method does not process +() symbols correctly,
        so we had to handle it manually.
        Always raises a ClientResponseError
        if the response status is 400 or higher.
        Returns the python dict JSON decoded value
        -- -- --
        url: relative path to the request endpoint
        params: get request parameters in the form key:value
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        params_str = urllib.parse.urlencode(params, safe="+'()")
        url = f'{self.endpoint}{url}'
        url = f'{url}?{params_str}' if params_str else url
        async with self._session.get(url=url, ssl=self.ssl, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=content_type)

    async def post(
        self,
        url: str,
        content_type: Optional[str] = "application/json",
        **kwargs
    ) -> dict:
        """
        HTTP POST request.
        Always raises a ClientResponseError
        if the response status is 400 or higher.
        Returns the python dict JSON decoded value
        -- -- --
        url: relative path to the request endpoint
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        url = f'{self.endpoint}{url}'
        async with self._session.post(url=url, ssl=self.ssl, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=content_type)

    async def delete(
        self,
        url: str,
        content_type: Optional[str] = "application/json",
        **kwargs
    ) -> dict:
        """
        HTTP DELETE request.
        Always raises a ClientResponseError
        if the response status is 400 or higher.
        Returns the python dict JSON decoded value
        -- -- --
        url: relative path to the request endpoint
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        url = f'{self.endpoint}{url}'
        async with self._session.delete(
            url=url,
            ssl=self.ssl,
            **kwargs
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=content_type)
