Title: Crystal in real life
Date: 2016-11-28
Summary: Float like a Ruby, sting like a C?

At Polyconf 2016 I attended a workshop about Crystal.
It is a relatively young programming language that's supposed to have both high-level
syntax (similar to Ruby) and high efficiency (comparable with C). Combining
these two traits seems difficult, but also very appealing to me.

Recently, I decided to try Crystal again, to check on my own if it can keep the
promise. The best way to do that was to write some code.
I needed a program that would take advantage of high efficiency, so I decided to
write a simple grayscale filter for PNG files.

## Installing Crystal

I'm using Ubuntu 16.04. Crystal is not available there by default, but the
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
will almost certainly require some sort of a third party library, so I decided to create a project.

Each Crystal project is expected to have a `shard.yml` file that contains the
dependencies and additional information. Fortunately, Crystal already has a neat
command to set this up:

```sh
crystal init app grayscale
```

This creates a Git repository, a directory for dependencies (`lib`), `.travis.yml` file
(initially only with the name of the language) and a lot of other stuff. The newly created `grayscale`
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

So there are two ways of creating a new project and both work out-of-the-box.
By far, Crystal seems to make my life easier at every step and I like it.
So now that I have a project ready, let's install the dependency!

## Installing the dependency

For a grayscale filter I needed an image processing library (obviously).
The page [crystalshards.xyz](http://crystalshards.xyz/) shows 2 results
when searched by the *image* keyword. One project still has *TODO* sections in the
README.md file. The other one is called [stumpy_png](https://github.com/l3kn/stumpy_png).
It looks like a decent piece of code, there is an example of usage provided on GitHub,
and there is more than one contributor. So I decided to use that one.

I tried installing the dependency with this command:

```sh
shards install stumpy_png
```

Much to my surprise, this command does nothing. It does not install the dependency and it does not
print any error message. According to the documentation, `shards install` doesn't add
a new dependency to the project, it only downloads and installs
all the dependencies from the `shard.yml` file.

So I started looking for a command like `shards add stumpy_png`, to easily add this new
dependency to `shard.yml` (something similar to `npm install --save <module>`).
But there is no such command. It was [suggested](https://github.com/crystal-lang/shards/issues/81)
to create one, but the idea was eventually rejected.
It was also mentioned (in [this comment](https://github.com/crystal-lang/shards/issues/81#issuecomment-261747349))
that Shards should fail when unknown arguments are left on the command line, to
avoid the confusion (something that will probably implemented in the future).

Crystal is no longer that helpful.
It seems that I have to edit `shard.yml` manually:

```sh
dependencies:
  stumpy_png:
    github: l3kn/stumpy_png
```

## Code

Using the trial and error approach I came up with this code:

```crystal
require "stumpy_png"

canvas = StumpyPNG.read("image.png")

canvas.width.times do |x|
  canvas.height.times do |y|
    color = canvas[x, y]
    grayscale = 0_u32
    grayscale = (grayscale + color.r + color.g + color.b) / 3
    canvas[x, y] = StumpyPNG::RGBA.from_gray_n(grayscale, 16)
  end
end

StumpyPNG.write(canvas, "output.png")
```

I know that grayscale conversion is a bit more complicated than the average
value of all 3 colors, but this filter was supposed to be a simple test of Crystal.
The code works, but there are some issues:

* in the first line I included the name of the library (`stumpy_png`),
but that allowed me to use the name of the class (`StumpyPNG`),
which is a bit inconsistent (at least for a Python developer, who imports exactly the thing that
can be used later)
* the code is still a bit verbose (this particular library doesn't provide a way to apply a function
to each pixel)
* I had to manually declare the type of the grayscale color variable (`0_u32`),
otherwise the value was incorrect for bright colors (apparently Crystal cannot
automatically choose the type that will hold the result)
* I need to create a new color each time I change its value (this is again the
limitation of stumpy_png)

So, the high-level syntax in this case was a bit of a disappointment.
The program looks better than the one written in C, but I expected more.

## Performance

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
