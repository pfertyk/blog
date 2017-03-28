Title: Redirections in Nginx
Date: 2017-03-28
Summary: Host different resources on port 80 using subdomains
Tags: nginx

Some time ago, I decided to host some slides on my server. Since I already host
a blog on the main address (pfertyk.me), I wanted to configure a redirection for
the slides (something like: awesome-slides.pfertyk.me). I thought it would be easy,
but it turned out a bit more troublesome than I expected.


```nginx
server {
    listen 8000;

    location / {
        root /path/to/awesome/slides;
        index index.html;
    }
}
```

I added a subdomain redirection:

```
awesome-slides 60 IN TXT "2|pfertyk.me:8000"
```

As a result I could access the my slides using the address `awesome-slides.pfertyk.me`.
It seemed to work quite well, until I opened the web console:

![Ugly redirection]({filename}/images/nginx-ugly-redirection.png)

Network tab revealed my redirection. It looked rather ugly to me. Sure, normal users
don't usually check the console, but the very thought that it is visible there
was annoying. Also, it made me think that I did something wrong (after all, I
should be able co configure the server to show only the pretty address without
displaying the port number).

So I dug deeper into this problem and with some help I found a solution.

```
actually-awesome-slides IN CNAME pfertyk.me.
```


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

![Pretty redirection]({filename}/images/nginx-pretty-redirection.png)
