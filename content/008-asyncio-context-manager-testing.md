Title: Testing asynchronous context managers in Python
Date: 2017-06-13
Summary: 
Tags: python, asyncio, aiohttp, tests

[link](http://pfertyk.me/2017/06/getting-mars-photos-from-nasa-using-aiohttp/)

```python
import random
from aiohttp import ClientSession


async def get_random_photo_url():
    while True:
        async with ClientSession() as session:
            async with session.get('random.photos') as resp:
                json = await resp.json()
        photos = json['photos']
        if not photos:
            continue
        return random.choice(photos)['img_src']
```

Python responses won't work (they are only good for testing Python requests).

```bash
pip install asynctest pytest-aiohttp
```

```python
from asynctest import patch
from main import get_random_photo_url


@patch('aiohttp.ClientSession.get')
async def test_call_api_again_if_photos_not_found(mock_get):
    mock_get.return_value.json.side_effect = [
        {'photos': []}, {'photos': [{'img_src': 'a.jpg'}]}
    ]

    image_url = await get_random_photo_url()

    assert mock_get.call_count == 2
    assert mock_get.return_value.json.call_count == 2
    assert image_url == 'a.jpg'
```

```text
    async def get_random_photo_url():
        while True:
            async with ClientSession() as session:
>               async with session.get('random.photos') as resp:
E               AttributeError: __aexit__
```

```text
+>>> from asynctest import MagicMock
+>>> m = MagicMock()
+>>>
+>>> m.__next__
<MagicMock id='139959347457160'>
+>>>
+>>> m.__aenter__
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python3.6/unittest/mock.py", line 584, in __getattr__
    raise AttributeError(name)
AttributeError: __aenter__
+>>>
+>>> m.__aexit__
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python3.6/unittest/mock.py", line 584, in __getattr__
    raise AttributeError(name)
AttributeError: __aexit__
```

```python
class AsyncContextManagerMock(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass
```

```python
from asynctest import MagicMock, patch
from main import get_random_photo_url


class AsyncContextManagerMock(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass


@patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
async def test_call_api_again_if_photos_not_found(mock_get):
    mock_get.return_value.aenter.json.side_effect = [
        {'photos': []}, {'photos': [{'img_src': 'a.jpg'}]}
    ]

    image_url = await get_random_photo_url()

    assert mock_get.call_count == 2
    assert mock_get.return_value.aenter.json.call_count == 2
    assert image_url == 'a.jpg'
```

```text
    async def get_random_photo_url():
        while True:
            async with ClientSession() as session:
                async with session.get('random.photos') as resp:
>                   json = await resp.json()
E                   TypeError: object dict can't be used in 'await' expression
```

```python
from asynctest import CoroutineMock, MagicMock, patch
from main import get_random_photo_url


class AsyncContextManagerMock(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass


@patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
async def test_call_api_again_if_photos_not_found(mock_get):
    mock_get.return_value.aenter.json = CoroutineMock(side_effect=[
        {'photos': []}, {'photos': [{'img_src': 'a.jpg'}]}
    ])

    image_url = await get_random_photo_url()

    assert mock_get.call_count == 2
    assert mock_get.return_value.aenter.json.call_count == 2
    assert image_url == 'a.jpg'
```
