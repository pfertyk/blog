Title: Crystal in real life
Date: 2016-11-28
Summary: Float like a Ruby, sting like a C?
Tags: crystal

At Polyconf 2016 I attended a workshop (organized by Aleksander Kwiatkowski and Serdar Dogruyol) about Crystal.
It is a relatively young programming language that's supposed to have both high-level
syntax (similar to Ruby) and high efficiency (comparable with C). Combining
these two traits seems difficult, but also very appealing to me.

Recently, I decided to try Crystal again, to check on my own if it can keep this
promise. The best way to test a programming language is to write some code, so
I decided to create a simple grayscale filter for PNG images (that way I could easily
test the efficiency). This posts describes the whole process.

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

Normally, I could just create a source file (`.cr`) and start coding. But image processing
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
Now that I have a project ready, let's install the dependency!

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
avoid the confusion (something that will be probably implemented in the future).

Crystal is no longer that helpful.
It seems that I have to edit `shard.yml` manually:

```yml
dependencies:
  stumpy_png:
    github: l3kn/stumpy_png
```

## Code

Using the trial and error approach (I'm not very familiar with Ruby syntax) I came up with this code:

```ruby
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

Note: I know that grayscale conversion is a bit more complicated than the average
value of all 3 colors, but this filter was supposed to be a simple test of Crystal.

The code works, but there are some issues:

* in the first line I included the name of the library (`stumpy_png`),
but that allowed me to use the name of the class (`StumpyPNG`),
which is a bit inconsistent (at least for a Python developer, who imports exactly the thing that
can be used later)
* the code is still a bit verbose (this particular library doesn't provide a way to apply a function
to each pixel)
* I had to manually declare the type of the grayscale color variable (`0_u32`)
and add all 3 colors to this variable,
otherwise the value was incorrect for bright colors due to integer overflow
* I needed to create a new color each time I wanted to change its value (this is a
limitation of stumpy_png, not Crystal itself)

So, the high-level syntax in this case was a bit of a disappointment.
I still have to worry about variable types and storing intermediary results.
The program looks better than the one written in C, but I expected more.
It seems that Crystal no longer wants to be my friend. However, the goal of this
language was also to be very fast, and I can forgive code like this if the speed is good.
So let's check the performance!

## Performance

The naive way to run a Crystal program would be something like this:

```
crystal grayscale.cr
```

This compiles the code and then executes it, without saving the executable
on disk. So it actually works like an interpreter that allows to run the program with
just one simple command. This is another great idea Crystal creators came up with,
but since I need the speed, I will use another way:

```
crystal build grayscale.cr
./grayscale
```

This will compile the code once and save the executable on disk for further use.
Since I *really* want the speed I should also turn on the optimization:

```
crystal build --release grayscale.cr
```

I executed this program on a 1920x1080 pixels image. I was a bit surprised that the
execution time was around 1 second. I compared it with the similar program written
in Python:

```python
from PIL import Image

im = Image.open('image.png')
im_gray = im.convert('L')
im_gray.save('output.png')
```

This one does the job done in around 0.2 second.

So... Crystal is both more verbose *and* slower than Python? That cannot be!
It has to keep at least part of its promise! There must be a way to make it run faster.
Maybe if I try to use all of the cores, the processing time will improve?
I decided to try this approach, however I got stopped by two things.

The first one is that Crystal [does not support parallel code execution](https://crystal-lang.org/docs/guides/concurrency.html).
I understand that it will be implemented in the future.
Still, that's kind of like shooting your own foot for a language that wants to be very fast.

The second reason was that I started a [discussion](https://github.com/l3kn/stumpy_png/issues/7)
about my problem on GitHub.
The owner of the project soon found out that the issue was not the processing time, but
rather the loading and saving times. This table shows the comparison:

Time spent on (s):|Crystal|Python
-|-|-
Loading the image| 0.4599181 | 0.1104393
Processing the pixels| 0.0112788 | 0.0521736
Saving the output| 0.2979503 | 0.0803592

So, the processing time is actually much better in Crystal than in Python, but the rest of the
program works a lot slower. Using multiple cores would not solve this problem.

Of course, contributors already declared to help with this issue and improve the loading
and saving times. But that doesn't change the fact that the only image processing
tool available for Crystal is at the moment very slow.

## Summary

That concludes my first attempt of using Crystal on my own. I noticed the
following things about this language:

**Pros**

* it has an excellent community (people respond very quickly and try to help newbies)
* it simplifies a lot of things
* it is fast (at least the image processing part)

**Cons**

* it lacks the libraries
* it does not support parallel code execution
* the package manager can be a bit confusing
* the code can still be quite verbose

Of course, these are only my personal observations. Moreover, the domain I chose (image processing)
might not be a thing among Crystal developers. Perhaps if I started with an HTTP server,
my experience would be very different. But the general impression I got was that
Crystal is not yet ready for being a general purpose tool. It has a bit of a charm,
but for now I will stick with Python (and, if I really need the speed, with C).
