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

Now that your bot is created, go ahead and invite it to your slack channel:

image here

### Write some Python code

install slackclient

```sh
pip install slackclient
```

create new slack client

```python
sc = SlackClient(token)
```

```python
sc.rtm_read()
```


```python
from slackclient import SlackClient
import time
import os

token = os.environ.get('SLACKBOT_LUMBERGH_TOKEN')

sc = SlackClient(token)

link = '<https://cdn.meme.am/instances/400x/33568413.jpg|That would be great>'

if sc.rtm_connect():
    while True:
        events = sc.rtm_read()
        for event in events:
            if (
                'channel' in event and
                'text' in event and
                event.get('type') == 'message'
            ):
                channel = event['channel']
                text = event['text']
                if 'that would be great' in text.lower() and link not in text:
                    sc.api_call(
                        'chat.postMessage',
                        channel=channel,
                        text=link,
                        as_user='true:'
                    )
        time.sleep(1)
else:
    print('Connection failed, invalid token?')
```

### Issues

## Second attempt: outgoing webhook

### Create a webhook

### Write new Python code

the loop!

use flask

```sh
pip install flask
```

drop token

## Deploying on Heroku
