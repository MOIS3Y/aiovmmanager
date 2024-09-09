import asyncio
import sys
from typing import Optional, Union

from aiohttp.client_exceptions import ClientResponseError

from .base import BaseSession


class AuthSession(BaseSession):
    """
    Authorization and authentication API for VMmanager 6.
    -- -- --
    url: base_url that will be passed to aiohttp.ClientSession.
    definition: API definition. Defaults to 'auth'
    version: API version. Defaults to 'v4'
    **kwargs: named arguments that will be passed to aiohttp.ClientSession
    """
    def __init__(
        self,
        url: str,
        definition: Optional[str] = 'auth',
        version: Optional[str] = 'v4',
        **kwargs
    ) -> None:
        super().__init__(url, definition, version, **kwargs)

    async def get_key(self, email_or_id: Union[int, str], **kwargs) -> dict:
        """
        End-to-end authorization by key.
        -- -- --
        email_or_id: email or user id for which the key will be generated
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.post(url=f'/user/{email_or_id}/key', **kwargs)
        return response

    async def get_token(
        self,
        email: str,
        password: str,
        attempts: Optional[int] = 3,
        **kwargs
    ) -> dict:
        """
        Authenticate user using username and password
        If VMmanager is inactive for a long time, it can be suspended.
        In this case, API requests fail with code 503
        Repeat requests until code 200 is received in response.
        -- -- --
        email: user email
        password: user password
        attempts: number of attempts to obtain a token at one second intervals
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        while attempts:
            try:
                response = await self.post(
                    url='/public/token',
                    json={'email': email, 'password': password},
                    content_type=None,
                    **kwargs
                )
                return response
            except ClientResponseError as error:
                await asyncio.sleep(1)
                attempts -= 1
                if not attempts:
                    print(error)
                    print("attempts to get an auth token have been exhausted.")
                    sys.exit(1)

    async def whoami(self, **kwargs) -> dict:
        """Get your current session information"""
        response = await self.get(url='/whoami', **kwargs)
        return response


class DnsProxySession(BaseSession):
    """DNS Proxy service 6 API"""
    def __init__(self, url, definition='dnsproxy', version='v3', **kwargs):
        super().__init__(url, definition, version, **kwargs)


class IpSession(BaseSession):
    """IPmanager 6 API"""
    def __init__(self, url, definition='ip', version='v3', **kwargs):
        super().__init__(url, definition, version, **kwargs)


class VmSession(BaseSession):
    """ISPsystem vm API"""
    def __init__(self, url, definition='vm', version='v3', **kwargs):
        super().__init__(url, definition, version, **kwargs)

    async def get_task(self, task_id: int, **kwargs) -> dict:
        """
        Get task parameters by task_id of the task manager.
        -- -- --
        task_id:
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.get(
            url=f'/task/{task_id}',
            **kwargs
        )
        return response

    async def get_task_by_consul_id(self, consul_id: int, **kwargs) -> dict:
        """
        Get task parameters by consul id.
        All tasks that require a long processing time return task:id
        Subsequently, this task will go to the task manager and
        it will be possible to track the status of its completion.
        -- -- --
        consul_id: task ID by consul
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.get(
            url='/task',
            params={'where': f'consul_id+EQ+{consul_id}'},
            **kwargs
        )
        return response['list'][0]

    async def host_create(self, host_params: dict, **kwargs) -> dict:
        """
        Create a virtual machine
        -- -- --
        host_params: parameters of the new virtual machine
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.post(
            url='/host',
            json=host_params,
            **kwargs
        )
        return response

    async def host_delete(self, host_id: int, **kwargs):
        """
        Delete a virtual machine by ID
        -- -- --
        host_id: virtual machine ID
        **:kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.delete(
            url=f'/host/{host_id}',
            **kwargs
        )
        return response

    async def host_edit(
        self,
        host_id: int,
        host_params: dict,
        **kwargs
    ) -> dict:
        """
        Edit general virtual machine settings
        -- -- --
        host_id: virtual machine ID
        host_params: editable values
        **kwargs: named arguments that will be passed to ClientSession.request
        """
        response = await self.post(
            url=f'/host/{host_id}',
            json=host_params,
            **kwargs
        )
        return response
