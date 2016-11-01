Title: If you could just go ahead and automatically post images on Slack
Date: 2016-11-01
Summary: Yeah, that would be great

Have you seen *The Office*? Do you wake up at night to the sound of ? Does your team use Slack? If so, you came to the right place! In this blog post, I will show you how to use Python to automatically detect 'That would be great' in Slack messages and send a picture of Bill Lumbergh it this situation occurs. You will use bot users and outgoing webhooks, and finally you will deploy on Heroku. Let's get right to it!

## First attempt: bot user

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

### Results

Assuming that you named your Python file `main.py`, you can now run your program:

```sh
python main.py
```

Now you can see your bot in action:

image here

## Second attempt: outgoing webhook

### Create a webhook

### Write new Python code

the loop!

use flask

```sh
pip install flask
```

drop token

### Results

not working locally

## Deploying on Heroku
