Title: Getting Mars photos from NASA using aiohttp
Date: 2017-06-12
Summary: One small step for coders, one giant leap for *The Martian* fans
Tags: python, aiohttp, nasa

I am a huge fan of the book *The Martian* by Andy Weir.
Reading it I wondered how did Mark Watney feel when he walked around the Red Planet.
Recently, thanks to
[this Twilio blog post](https://www.twilio.com/blog/2017/04/texting-robots-on-mars-using-python-flask-nasa-apis-and-twilio-mms.html)
I found out that NASA has a public API for accessing photos taken by Mars rovers. However, not being a huge fan of MMS,
I decided to write my own application to get the inspiring images delivered straight to my browser.

## Creating aiohttp application

Let's start with a simple application, just to get aiohttp up and running. First,
create a new virtualenv. It is recommended to use Python 3.5, since we will
be using new `async def` and `await` syntax. If you want to develop this project
further and take advantage of asynchronous comprehensions, you can use Python 3.6
(I did). Next, install aiohttp:

```bash
pip install aiohttp
```

Now create a source file (call it `nasa.py` ) and put some code inside:

```python
from aiohttp import web


async def get_mars_photo(request):
    return web.Response(text='A photo of Mars')


app = web.Application()
app.router.add_get('/', get_mars_photo, name='mars_photo')
```

If you are new to aiohttp some things might need explaining:

* `get_mars_photo` coroutine is a request handler; it takes a HTTP request as its
only argument and is responsible for returning a HTTP response (or raising an
exception)
* `app` is a high level server; it supports routers, middleware and signals
(for this program we are only going to use the router)
* `app.router.add_get` registers a request handler on HTTP GET method and
'/' path

Note: request handlers don't have to be coroutines, they can be regular
functions. But we are going to use the power of asyncio, so most functions
in our program are going to be defined with `async def`.

### Running the application

To run your application you can add this line at the end of your file:

```python
web.run_app(app, host='127.0.0.1', port=8080)
```

And then run it like any other Python script:

```bash
python nasa.py
```

However, there is a better way. Among many third-party libraries
you will find [aiohttp-devtools](https://github.com/aio-libs/aiohttp-devtools).
It provides a nice `runserver` command that detects your app automatically
and supports live reloading:

```bash
pip install aiohttp-devtools
adev runserver -p 8080 nasa.py
```

Now, if you visit [localhost:8080](localhost:8080), you should see *A photo of Mars* text in your browser.

## Using NASA API

Of course, this is not the end. If you are a keen observer, you noticed that
we are not getting an actual image, but rather some text. Let's fix that.

To get photos from Mars, we will use [NASA API](https://api.nasa.gov/api.html#MarsPhotos). Each rover has its own URL (for Curiosity it's `https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos`). We have to provide at least 2 params for each call:

* `sol`: the Martian rotation or day on which a photo was taken, counting up
from the rover's landing date (the maximum value can be found in
`rover/max_sol` part of the response)
* `API_KEY`: API key provided by NASA (you can use the default one: `DEMO_KEY`)

In return we will get a list of photos, each with a URL, camera info and rover
manifest.

Modify the `nasa.py` file to look like this:

```python
import random

from aiohttp import web, ClientSession
from aiohttp.web import HTTPFound

NASA_API_KEY = 'DEMO_KEY'
ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


async def get_mars_image_url_from_nasa():
    while True:
        sol = random.randint(0, 1722)
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

Here is what's going on:

* we select a random sol (for Curiosity the `max_sol` value is 1722 at the moment
of writing this post)
* `ClientSession` creates a session that we can use to get the response
from NASA API
* we obtain the JSON response using `resp.json()`
* we check if the 'photos' key is present in the response; if not, we have
reached the limit of hourly calls and we need to wait a bit
* if there are no photos taken on given day, we check again, for a different
random sol
* we then use `HTTPFound` response to redirect to the photo we found

### Getting NASA API key

The default `DEMO_KEY` provided by NASA works fine, but you will soon reach the
limit of hourly API calls. I recommend you to get your own API key. You can do
it [here](https://api.nasa.gov/index.html#apply-for-an-api-key)
(the sign up process is very simple and fast).

Now when you run the application, you will be redirected to a pretty image
straight from Mars:

![A rather uninspiring photo]({filename}/images/nasa-aiohttp-not-inspiring.jpg)

Well, that's not exactly what I meant ...

## Validating an image

The image you just saw is not very inspiring. It turns out that rovers take
a lot of really boring photos. I wanted to see what Mark Watney saw on his
incredible journey, and this is just not good enough. Let's find a way to fix
that.

We will need some sort of validation for our images. Without specifying the
criteria yet, we can modify our code:

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

Some new things happened here:

* we get the URL using the previously defined function and we read the raw bytes from
the image using `resp.read()`
* we check if our image is good enough; if not, we keep looking
* once we have a satisfying photo we put it in the response (notice we still
use the same `web.Response` as before, but this time we specify the `body`
instead of `text` and we define the `content_type`)

Note: in this code we removed the redirection (`HTTPFound`),
so now we can easily refresh the page to get another image.

Now we need to figure out how to validate the photos.
One thing we can do rather easily is to check if the image is big enough.
It's not a perfect validation, but it should do for now. To process images,
we will need Pillow (PIL fork):

```bash
pip install pillow
```

Our validation function could look like this:

```python
import io
from PIL import Image


async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024
```

![Mars in shades of gray]({filename}/images/nasa-aiohttp-landscape-grayscale.jpg)

Now that's more like it! We can go one step further and reject grayscale images:

```python
async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'
```

Now our program starts returning much more inspiring photos:

![Cool landscape]({filename}/images/nasa-aiohttp-landscape-rgb.jpg)

And, occasionally, a robot selfie:

![Rover's selfie]({filename}/images/nasa-aiohttp-selfie.jpg)

## Summary

Our program should now look like this:

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
        sol = random.randint(0, 1722)
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

There are many things we could improve (like getting `max_sol` value from
the API, passing the rover's name, caching the URLs) but for now it does the job
done: we can get a random, inspiring photo of Mars and feel like we
are actually there.

I hope you liked this short tutorial. If you spot a mistake or have any questions,
please let me know.
