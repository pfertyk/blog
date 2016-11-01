Title: If you could just go ahead and automatically post images on Slack
Date: 2016-11-01
Summary: Yeah, that would be great

Have you seen *The Office*? Do you wake up at night to the sound of ? Does your team use Slack? If so, you came to the right place! In this blog post, I will show you how to use Python to automatically detect 'That would be great' in Slack messages and send a picture of Bill Lumbergh it this situation occurs. You will use bot users and outgoing webhooks, and finally you will deploy on Heroku. Let's get right to it!

## First attempt: bot user

Some short description of bot users

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
def inbound():
    return Response(), 200
```

This will accept **POST** requests to `123.1.2.3/lumbergh` and that's basically it.


drop token


The problem is that you still need to have a public IP address. Let's solve this problem using Heroku.

### Deploying on Heroku

I'm going to assume that you already have an account and that you installed **Heroku CLI**. Create a new app and give it a nice name. Go to **Settings** and check the git URL. 


## Summary
