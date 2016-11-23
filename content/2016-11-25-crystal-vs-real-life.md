Title: Crystal in real life
Date: 2016-11-25
Summary: Float like a Ruby, sting like a C?

At Polyconf 2016 I attended a workshop about Crystal.
It is a relatively new language that's supposed to have a high-level syntax (similar to Ruby) and
high efficiency (comparable with C). I don't know Ruby, but the vision of
combining these two traits seemed very appealing to me. So recently I decided to
try this language again. And since the best way to try is to write some code,
I decided to create a simple grayscale filter. That way I could also test the
efficiency.

## Installing Crystal

Crystal is not available by default on Ubuntu, but the
[installation instructions](https://crystal-lang.org/docs/installation/on_debian_and_ubuntu.html)
are very clear and simple:

```sh
curl https://dist.crystal-lang.org/apt/setup.sh | sudo bash
sudo apt-get install crystal
```

This installs both the Crystal compiler and the default dependency manager called Shards
(I already like these names).

## Creating a new project

Normally, I could just create a source file and start coding. But image processing
will almost certainly require some sort of third party library, so I decided to create a project.

Each Crystal project is expected to have a `shard.yml` file that contains the
dependencies and additional information. Fortunately, Crystal already has a neat
command to set this up:

```sh
crystal init app hello_world
```

This creates a Git repository, a directory for dependencies (`lib`), `.travis.yml` file
(initially only with language name) and a lot of other stuff. The newly created `grayscale`
directory looks like this:

```sh
.
├── .git
│   ├── branches
│   ├── config
│   ├── description
│   ├── HEAD
│   ├── hooks
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   └── update.sample
│   ├── info
│   │   └── exclude
│   ├── objects
│   │   ├── info
│   │   └── pack
│   └── refs
│       ├── heads
│       └── tags
├── .gitignore
├── LICENSE
├── README.md
├── shard.yml
├── spec
│   ├── grayscale_spec.cr
│   └── spec_helper.cr
├── src
│   ├── grayscale
│   │   └── version.cr
│   └── grayscale.cr
└── .travis.yml
```

I decided that it is a bit of an overkill for a simple grayscale filter.
Fortunately, there is another way: I created a `grayscale` directory manually and
executed this command inside it:

```sh
shards init
```

This creates just the `shard.yml` file. By default it looks like this:

```yml
name: grayscale
version: 0.1.0

# authors:
#   - name <email@example.com>

# description: |
#   Short description of grayscale

# dependencies:
#   pg:
#     github: will/crystal-pg
#     version: "~> 0.5"

# development_dependencies:
#   webmock:
#     github: manastech/webmock.cr

# license: MIT
```

By far, Crystal seems to make my life easier on every occasion. So now that I have
a project ready, let's install the dependency!

## Installing the dependency

I needed an image processing library. The page crystalshards.xyz shows 2 results
when searched by the keyword 'image'. One project still has `TODO` sections in the
README.md file. The other one is *stumpy_png* and it looks like a decent piece of code.
There is an example provided on GitHub. So I decided to use that one.

```sh
shards install stumpy_png
```

That command does nothing. It does not install the dependency and it does not
print any error message. According to the documentation, `shards install` downloads
and install all the dependencies listed in `shard.yml` file.
So I started to look for a command like `shards add stumpy_png`

## Code

```crystal
require "stumpy_png"

canvas = StumpyPNG.read("image.png")

(0...canvas.width).each do |x|
  (0...canvas.height).each do |y|
    color = canvas[x, y]
    g = 0_u32
    g = (g + color.r + color.g + color.b) / 3
    canvas[x, y] = StumpyPNG::RGBA.from_gray_n(g, 16)
  end
end

StumpyPNG.write(canvas, "output.png")
```

Some issues:

* the first line uses the name of the library, but makes available the name of the class;
this seems to be inconsistent (at least for the Python developer, who import exactly the thing that
can be used later)
* the code is still a bit verbose
* I need to create a new color each time I change the value

## Performance

So, the high-level syntax in this case was a bit of a disappointment.
But what I really wanted is performance!

```
crystal grayscale.cr
```


```
crystal build grayscale.cr
./grayscale
```

Builds the executable. 4s
```
crystal build --release grayscale.cr
```

Starts to look a bit more like C than I wanted. Executes in 1s.

I compared the results with a Python program doing exactly the same job:

```python
from PIL import Image

im = Image.open('image.png')
im_gray = im.convert('L')
im_gray.save('output.png')
```

0.2s

I decided to improve the performance by using all the cores. Two things stopped me however.

The first one is that Crystal does not support parallel code execution (link).
Kind of like shooting your own foot for a language that wants to be efficient.

The second reason was that I created an issue on stumpy_png's github.
After a discussion with the developer of stumpy_png it become obvious that the
problem is not with the processing, but with loading and saving.

The table shows the comparison:

Time spent on:|Crystal|Python
-|-|-
Reading|0|0
Processing|0|0
Writing|0|0

## Summary

Cons:

* lack of tools
* no parallel code
* some issues with package manager
* the code can still be somewhat verbose
* need to pay attention to compiler flags

Pros:

* excellent community

Seems interesting, but not for now. Maybe in other domains (like HTTP server),
but not for general use.
