Title: Getting Mars images from NASA using aiohttp
Date: 2017-06-11
Summary: Small step for coders, big step for *The Martian* fans
Tags: python, aiohttp, nasa

I am a huge fan of the book *The Martian* by Andy Weir. Recently, thanks to
[this article](https://www.twilio.com/blog/2017/04/texting-robots-on-mars-using-python-flask-nasa-apis-and-twilio-mms.html)
I found out that NASA has a public API for accessing photos taken from Mars rovers.

## Creating aiohttp application

```bash
pip install aiohttp
```

```python
from aiohttp import web


async def get_mars_photo(request):
    return web.Response(text='Here is a Mars picture for you!')


app = web.Application()
app.router.add_get('/', get_mars_photo, name='mars_photo')
```

### Running the application

```python
web.run_app(app, host='127.0.0.1', port=8080)
```

```bash
python main.py
```

```bash
pip install aiohttp-devtools
```

```bash
adev runserver -p 8080 nasa.py
```

## Getting the Mars image

```python
import random

from aiohttp import web, ClientSession
from aiohttp.web import HTTPFound

NASA_API_KEY = 'DEMO_KEY'
ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


async def get_mars_image_url_from_nasa():
    while True:
        sol = random.randint(0, 1700)
        params = {'sol': sol, 'api_key': NASA_API_KEY}
        async with ClientSession() as session:
            async with session.get(ROVER_URL, params=params) as resp:
                resp_dict = await resp.json()
        if 'photos' not in resp_dict:
            raise Exception
        photos = resp_dict['photos']
        if not photos:
            continue
        return random.choice(photos)['img_src']


async def get_mars_photo(request):
    url = await get_mars_image_url_from_nasa()
    return HTTPFound(url)
```


![A rather uninspiring photo]({filename}/images/nasa-aiohttp-not-inspiring.jpg)

### Getting NASA API key

[here](https://api.nasa.gov/index.html#apply-for-an-api-key)

[here](https://api.nasa.gov/api.html#MarsPhotos)

## Validating an image

```python
async def get_mars_photo_bytes():
    while True:
        image_url = await get_mars_image_url_from_nasa()
        async with ClientSession() as session:
            async with session.get(image_url) as resp:
                image_bytes = await resp.read()
        if await validate_image(image_bytes):
            break
    return image_bytes


async def get_mars_photo(request):
    image = await get_mars_photo_bytes()
    return web.Response(body=image, content_type='image/jpeg')
```

```bash
pip install pillow
```

```python
import io
from PIL import Image


async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024
```
![Mars in shades of gray]({filename}/images/nasa-aiohttp-landscape-grayscale.jpg)

```python
async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'
```

![Cool landscape]({filename}/images/nasa-aiohttp-landscape-rgb.jpg)

![Rover's selfie]({filename}/images/nasa-aiohttp-selfie.jpg)


```python
import random
import io

from aiohttp import web, ClientSession

from PIL import Image

NASA_API_KEY = 'DEMO_KEY'
ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'


async def get_mars_image_url_from_nasa():
    while True:
        sol = random.randint(0, 1700)
        params = {'sol': sol, 'api_key': NASA_API_KEY}
        async with ClientSession() as session:
            async with session.get(ROVER_URL, params=params) as resp:
                resp_dict = await resp.json()
        if 'photos' not in resp_dict:
            raise Exception
        photos = resp_dict['photos']
        if not photos:
            continue
        return random.choice(photos)['img_src']


async def get_mars_photo_bytes():
    while True:
        image_url = await get_mars_image_url_from_nasa()
        async with ClientSession() as session:
            async with session.get(image_url) as resp:
                image_bytes = await resp.read()
        if await validate_image(image_bytes):
            break
    return image_bytes


async def get_mars_photo(request):
    image = await get_mars_photo_bytes()
    return web.Response(body=image, content_type='image/jpeg')


app = web.Application()
app.router.add_get('/', get_mars_photo, name='mars_photo')
```
