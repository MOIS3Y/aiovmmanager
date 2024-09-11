# aiovmmanager
Async lib based on aiohttp for working with the VMmanager6 API


## What is it?

A small library that contains several public classes for working with the VMmanager 6 API
- AuthSession
- DnsProxySession
- IpSession
- VmSession

Each class inherits from a base class, BaseSession,
which wraps aiohttp.ClientSession and acts as a context manager.

The library already implements the formation of convenient endpoints,
decodes JSON responses, and also raises a `ClientResponseError` exception
if the response status is 400 or higher.


### There are also several ready-made methods for basic actions:

**AuthSession**

- get_token
- get_key
- whoami


**VmSession**

- get_task
- get_task_by_consul_id
- host_create
- host_delete
- host_edit

## How to use it?

Each available direction of the VMmanager 6 API has its own class.
When initializing the class, you can specify the base url and SSL certificate verification.
All other parameters override the behavior of `aiohttp.ClientSession`
You can read more in the official documentation 
[aiohttp](https://docs.aiohttp.org/en/stable/client_reference.html)

Each class has methods that make it easier to generate API requests
Their names are the same as the `aiohttp.ClientSession` methods.
Methods currently implemented:

- get
- post
- delete

To start generating queries, import the required class
and use the context manager syntax


## Installation

### Requirements
- python = `^3.9`

### Manual
- install dependency `pip install aiohttp`
- copy the aiovmmanager package to your project

### Use pip

- `pip install iovmmanager`


## Examples

- **get an authorization token** 
this token will need to be added to the header of each request in the future

```python
import asyncio
from aiovmmanager import AuthSession


async def main():
    url = 'https://vm6.example.com'
    headers = {}

    # pass to AuthSession ssl=False if you have a self-signed or invalid certificate
    async with AuthSession(url=url) as session:
        response = await session.get_token(
            email='admin@example.com',
            password='password',
        )
        # set x-xsrf-token header:
        headers['x-xsrf-token'] = response.get('token', '')
        print(headers)


if __name__ == "__main__":
    asyncio.run(main())

```

- **end-to-end authorization by key**

```python
import asyncio
from aiovmmanager import AuthSession


async def main():
    url = 'https://vm6.example.com'
    headers = {'x-xsrf-token': 'the token can be obtained in the example above'}

    # pass to AuthSession ssl=False if you have a self-signed or invalid certificate
    async with AuthSession(url=url, headers=headers) as session:
        response = await session.get_key(email_or_id='admin@example.com')
        print(response)


if __name__ == "__main__":
    asyncio.run(main())

```

- **Create 3 virtual machines asynchronously**

```python
import asyncio
from aiovmmanager import VmSession


vm_template = {
    "name": "aiovmmgr",
    "os": 8211,
    "password": "root-password",
    "send_email_mode": "default",
    "cluster": 27,
    "preset": 1,
    "disks": [
        {
            "boot_order": 1,
            "size_mib": 10240,
            "tags": [],
            "storage": 61
        }
    ],
    "comment": "test vm from aiovmmgr",
    "account": 124,
    "node": 64,
    "custom_interfaces": [
        {
            "model": "virtio",
            "is_main_network": True,
            "bridge_id": 97,
            "ip_count": 1,
            "ippool": 111
        }
    ],
    "domain": "aiovmmgr.example.com"
}


async def main():
    url = 'https://vm6.example.com'
    headers = {'x-xsrf-token': 'the token can be obtained in the first example'}

    async with VmSession(url=url, headers=headers) as session:
        # create a list of three coroutines
        # of course in a real example host_params contains three different vms
        tasks = [session.host_create(host_params=vm_template) for _ in range(3)]
        # send a request to create virtual machines asynchronously
        results = await asyncio.gather(*tasks)

        for result in results:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

- **get task by consul id**

All tasks that are performed by the platform for a long time fall into the consul.
The response comes with the id of such a task. Subsequently, the task
will go to the task manager and will be processed and completed
You can find the task number in the task manager by requesting information by consul id.
The method is configured with an exact match filter by consul id

```python
import asyncio
from aiovmmanager import VmSession


async def main():
    url = 'https://vm6.example.com'
    headers = {'x-xsrf-token': 'the token can be obtained in the first example'}

    consul_id = 1488228  # example consul_id

    async with VmSession(url=url, headers=headers) as session:
        response = await session.get_task_by_consul_id(consul_id=consul_id)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

- **any request in accordance with the VMmanager 6 API documentation**

Since all classes inherit from `BaseSession` which is a
wrapper of `aiohttp.ClientSession` you can make requests for any handlers.


```python
import asyncio
from aiovmmanager import AuthSession, VmSession


async def main():
    url = 'https://vm6.example.com'
    headers = {'x-xsrf-token': 'the token can be obtained in the first example'}

    # -- Snip
    async with AuthSession(url=url, headers=headers) as session:
        # show active admins:
        list_admins = await session.get(
            url='/user',
            params={"where": "((roles+CP+'%@admin%')+AND+(state+EQ+'active'))"}
        )
        print(list_admins)
    # -- Snip

    # -- Snip
    async with VmSession(url=url, headers=headers) as session:
        # force restart vm by id:
        host_id = 228
        restart_vm = await session.post(
            url=f'/host/{host_id}/restart',
            json={'force': True}
        )
        print(restart_vm)
    # -- Snip

if __name__ == "__main__":
    asyncio.run(main())
```
