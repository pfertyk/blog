Title: Automatically respond to Slack messages containing specified text
Date: 2016-11-01
Summary: Yeah, that would be great

Recently I tried to create a Slack bot. It's job would be to read the messages and, if 'that would be great' was detected in the content, respond to the message with a picture of Bill Lumbergh from the office (yeah, I'm a funny guy). But I found out that the learning resources are somewhat scattered around the Internet. It was difficult for a person not familiar with Slack API and with bots in general to get a grip of the whole process.

I finally succeeded, and I would like to help others with a similar problem. This post will show you how to integrate with Slack in two ways: sing bot users and outgoing webhooks. You don't have to know anything about Slack or Python frameworks, but the basic Python skills and a Heroku account are required (unless you want to host the solution on your own server). The code will be simple and will do this one and only task that I mentioned: detect the text and respond with an image. Let't get right to it!

## First attempt: bot user

Slack allows you to create [bot users](https://api.slack.com/bot-users). They are very similar to normal users, except they can be controlled using the API token.

### Create a bot user

To create a new bot user, visit [this link](https://my.slack.com/services/new/bot) (of course, you have to be a full member of your team to do that). First, you need to pick a name for your bot:

image here

Then, you can access your bot settings. It is possible (and advised!) to give it a nice name and icon. But the important part here is the token:

image here

This will be required for our Python code to post messages to a slack channel as this bot user. From now on, I'm going to assume that your token is `xoxo-123token`.

Now that your bot is created, go ahead and invite it to your Slack channel:

image here

### Write some Python code

First, you will need to create a new virtualenv and install `slackclient`:

```sh
mkvirtualenv -p /usr/bin/python3 slack-bot
pip install slackclient
```

Next you need to actually create a Slack client, using the bot user's token. For security reasons set the environment variable with the token:

```sh
export SLACKBOT_LUMBERGH_TOKEN=xoxo-123token
```

And then use it in Python:

```python
from slackclient import SlackClient
import os


token = os.environ.get('SLACKBOT_LUMBERGH_TOKEN')
slack_client = SlackClient(token)
```

There are many methods provided by `slackclient` (you can check the [documentation](http://python-slackclient.readthedocs.io/en/latest/)). For this example, we are going to use just 3 of them.

To start working with Slack use `rtm_connect`. It will open a websocket connection and start to listen for events.

```python
if slack_client.rtm_connect():
    # proceed
else:
    print('Connection failed, invalid token?')
```

To get the list of events, use `rtm_read`. It will return a list of events since the last call.

```python
events = slack_client.rtm_read()
for event in events:
    # process event
```

There are different types of events. You want to intercept those that have a `message` type, come from a specific channel and contain some text:

```python
if (
    'channel' in event and
    'text' in event and
    event.get(type) == 'message'
):
    # this is the event you are looking for
```

Now that you have an event that you know is a message, you can check if the text contains the phrase. If so, you can post a new message to a Slack channel the event came from. To do this, use `api_call` method:

```python
slack_client.api_call(
    'chat.postMessage',
    channel=event['channel'],
    text='Your very clever response',
    as_user='true:'
)
```

Two things might require and explaination: `'chat.postMessage'` defines that type of API call you are going to make (in this case, you want to post a message), and `as_user='true:'` will make your bot's messages appear as they were sent by a normal Slack user.


You code by far should look something like this:

```python
from slackclient import SlackClient
import time
import os

token = os.environ.get('SLACKBOT_LUMBERGH_TOKEN')

slack_client = SlackClient(token)

link = '<https://cdn.meme.am/instances/400x/33568413.jpg|That would be great>'

if slack_client.rtm_connect():
    while True:
        events = slack_client.rtm_read()
        for event in events:
            if (
                'channel' in event and
                'text' in event and
                event.get('type') == 'message'
            ):
                channel = event['channel']
                text = event['text']
                if 'that would be great' in text.lower() and link not in text:
                    slack_client.api_call(
                        'chat.postMessage',
                        channel=channel,
                        text=link,
                        as_user='true:'
                    )
        time.sleep(1)
else:
    print('Connection failed, invalid token?')
```

the loop
the sleep
the link
the checking of link in title

Assuming that you named your Python file `main.py`, you can now run your program:

```sh
python main.py
```

Now you can see your bot in action:

image here

It works quite nicely, except for that awful endless loop. That is not how the code should look like. If only there was a way to react to actual messages instead of reading all the events...

## Second attempt: outgoing webhook

Fortunately, Slack provides another way of integrating other services: webhooks. Thanks to them you can receive a call each time a message is sent to a channel.

### Create a webhook

Go to [Outgoing WebHooks](https://my.slack.com/services/new/outgoing-webhook) page and click **Add Outgoing WebHooks integration**. You will be redirected to the **Edit configuration** page, and you will immediately notice some limitations:

* the integration can only be enabled for one specific channel or for all messages starting with specific words (**trigger words**)
* you will need a server with a public IP address to send the messages to (you need to provide a URL that Slack can find)
* you can still customize the name and the icon, but you will have to repeat the process for each channel (assuming you are not going to use **trigger words**)

So, is it even worth the effort to use this outgoing webhook instead of a bot user? I think it is. Infinite loops without breaking conditions are evil and you should avoid them. Besides, the downsides are not really that troublesome.

Let's proceed with the configuration. Select the channel and leave the **Trigger word(s)** section empty. I'm going to assume for a moment that you have your own public IP address and that it is `123.1.2.3` (don't worry, in just a moment you will deploy your program to Heroku and that will take care of the public IP problem). Put `http://123.1.2.3/lumbergh` in the **URL(s)** field. You can also customize the name and the icon.

There is one more important section here: **Token**. It contains the token that will be added to each API call send to the URLs you provided. You will use it in a moment.

### Write new Python code

The new version of your program will not require `slackclient` at all. Instead, you are going to use `flask`:


```sh
pip install flask
```

A very simpla `flask` application would look like this:

```python
from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # make the app externally visible
```

This of course will not do anything usefull, so let's create an endpoint:

```python
@app.route('/lumbergh', methods=['POST'])
def lumbergh():
    text = request.form.get('text', '')
    if 'that would be great' in text.lower() and link not in text:
        return jsonify(text=link)
    return Response(), 200
```

This will accept **POST** requests to `123.1.2.3/lumbergh` and if the text is detected in the message, our link will be returned as a response. As you can see, you don't need to post the message using the Slack API, since the response to this **POST** call will be automatically used as a message.

The code of your program should look something like this:


```python
from flask import Flask, request, Response, jsonify

app = Flask(__name__)
link = '<https://cdn.meme.am/instances/400x/33568413.jpg|That would be great>'


@app.route('/lumbergh', methods=['POST'])
def lumbergh():
    text = request.form.get('text', '')
    if 'that would be great' in text.lower() and link not in text:
        return jsonify(text=link)
    return Response(), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

You might notice that there is no token validation here. If you want, you can check if the call was made by Slack 

The problem is that you still need to have a public IP address. Let's solve this problem using Heroku.

### Deploying on Heroku

I'm going to assume that you already have an account and that you installed **Heroku CLI**. Create a new app and give it a nice name (I picked *lumbergh*). Go to **Settings**, check the git URL and configure the git remote accordingly:

image here

```sh
git init
git remote add heroku
https://git.heroku.com/lumbergh.git
```

To run the program, you will need a server, like `gunicorn`:

```sh
pip install gunicorn
```

For a program to work with Heroku, you will have to create an additional file called `Procfile`:

```ini
web: gunicorn lumbergh:app
```

Also, since [Python 2.x is legacy and Python 3.x is the present and future of the language](https://wiki.python.org/moin/Python2orPython3), you should inform Heroku that you want to use proper version of Python by creating a `runtime.txt` file:

```ini
python-3.4.3
```

Now you can deploy to Heroku (remember, that first you need to authenticate yourself using `heroku login`):

```sh
git push heroku master
```

On the **Overview** page you should see that the program is working:

image here

Now you can change the URL for the Slack webhook to your

Now if you post a proper message on Slack, you should see a response:

image here

## Summary

As it turns out, answering messages automatically on Slack is very easy. Bot users can be enabled for many channels, but they need an ugly loop. Outgoing webhooks can react on each message, but they need a public IP and have to be added to each channel separately.

If you don't have the time to configure the bot by yourself, you can use my instance. Just add a new outgoing webhook with the following URL:

```ini
https://lumbergh.herokuapp.com/lumbergh
```

If you find any problems with this tutorial, please let me know.
