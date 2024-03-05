Title: Redirections in Nginx
Date: 2017-04-04
Summary: Host different resources on port 80 using subdomains
Tags: nginx

Some time ago, I decided to host a [presentation ](http://clean-tests.pfertyk.me)
on my server. The idea was to have a nice URL (like `awesome-slides.pfertyk.me`)
that would point to a location handled by Nginx (like: `pfertyk.me/awesome-slides`).
This simple task turned out to be a bit more complicated.

The first problem that I stumbled upon was that the `/` location was already in use. As you
probably guessed, that is where my blog is (the one you are reading right now).
That caused Nginx to try to find other locations (like `/awesome-slides`) inside
by blog directory. There is probably a workaround for this problem,
but I couldn't find it in a reasonable amount of time. So I decided to solve
this other way.

I configured Nginx to host the slides on port 8000 (`pfertyk.me:8000`).
The configuration looked like this:

```nginx
server {
    listen 8000;

    location / {
        root /path/to/awesome/slides;
        index index.html;
    }
}
```

Now I just needed to add a subdomain redirection:

```
awesome-slides 60 IN TXT "2|pfertyk.me:8000"
```

and my presentation was available to the public. Everything seemed fine until I
opened the web console:

![Ugly redirection]({static}/images/nginx-ugly-redirection.png)

The first call was made to `awesome-slides.pfertyk.me`, but all the
subsequent ones used the domain `pfertyk.me:8000`. I know that normal users don't usually
open the web console, so it shouldn't be a problem. But it felt like I was doing
this wrong, like there was a way to hide that ugly port number.

So I dug deeper into this problem and, with some help, I found a solution.
I had to set `server_name` properly, so that Nginx would handle requests
from different subdomains. The new configuration looked like this:

```nginx
server {
    listen 80;
    server_name actually-awesome-slides.pfertyk.me;

    location / {
        root /path/to/awesome/slides;
        index index.html;
    }
}
```

I had to change the DNS record too:

```
actually-awesome-slides IN CNAME pfertyk.me.
```

And there it was:

![Pretty redirection]({static}/images/nginx-pretty-redirection.png)

The configuration was simple and elegant. The port number was hidden.
In fact, Nginx was now using port 80 for all the
resources (currently I have more than one presentation
hosted that way).

I hope this short tutorial helped you in some way. Please contact me if you
have any questions.
