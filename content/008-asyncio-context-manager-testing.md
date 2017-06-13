Title: Testing asynchronous context managers in Python
Date: 2017-06-14
Summary: A bit harder than it looks
Tags: python, asyncio, aiohttp, tests

Recently I wrote a small aiohttp application that calls NASA API to get
photos from Mars (you can read about it [here](http://pfertyk.me/2017/06/getting-mars-photos-from-nasa-using-aiohttp/)).
Every good application needs tests, but in this case a process of writing one
turned out to be much more difficult than I imagined. HELLO

## Code under test

This is a simplified version of the code from my NASA API application:

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

The coroutine calls the `random.photos` API and gets a JSON response in return.
In that response, there is a 'photos' key with a list of images.
The problem is, since the API returns random photos, sometimes there are no photos (the list is there, but it's
empty). In that case we keep calling the API until we get any images and return a URL of a random one.

Note: the original program required a param that specified a day on which
the photo was taken, and subsequent API calls used random values of
this param and thus returned different lists of photos. The code was
simplified for the purpose of this post, so you just have to assume that
`random.photos` returns a different set of photos each time it is called.

## Testing

Start with installing some helpful modules:

```bash
pip install asynctest pytest-aiohttp
```

The asynctest module enhances standard unittest.mock to deal with coroutines,
and pytest-aiohttp provides an event loop to run asynchronous tests as if they were normal tests.

Now, I've got some bad news. There is no utility for mocking ClientSession.
Python responses module is useless here (it will only work with requests module), and
aiohttp doesn't have anything similar available. So, we need to patch it:

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

The mock is first going to provide an empty list and then a list with one item. We are going to check if the API and the `json` method were in fact called twice and if
the image URL of the second call was read correctly.
The problem is, this test doesn't work:

```text
    async def get_random_photo_url():
        while True:
            async with ClientSession() as session:
>               async with session.get('random.photos') as resp:
E               AttributeError: __aexit__
```

## Problems with context managers

To understand what's going on, let's try fiddling with the `MagicMock` object:

```text
+>>> from asynctest import MagicMock
+>>> m = MagicMock()
+>>>
+>>> m.__enter__
<MagicMock id='139882982853768'>
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

As you can see, standard magic methods are mocked, but not the `__aenter__` and `__aexit__` methods required by asynchronous context managers.
There is a [GitHub issue](https://github.com/Martiusweb/asynctest/issues/29)
for this problem, but it's still open. Instead of waiting we can write our own solution:

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

Our own implementation will return `aenter` value when used as a context manager. If we don't specify it, it will be a
`MagicMock` object, so we can just go on and assign the results of subsequent `json` method calls. There is just one problem with that solution:

```text
    async def get_random_photo_url():
        while True:
            async with ClientSession() as session:
                async with session.get('random.photos') as resp:
>                   json = await resp.json()
E                   TypeError: object dict can't be used in 'await' expression
```

Using `side_effect` turns our `json` method into a normal function, while it should be a coroutine. To fix this, we can use `CoroutineMock`:

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

And now the test should pass without problems.

I hope this post will save you some time.
It shows, of course, just a rough solution for testing aiohttp, but it should
work until the asynctest issue is fixed. 
If you know a better alternative, please let me know.
