Detect PEP-8 violations on pull requests
########################################

:date: 2016-10-14
:summary: Your own automatic GitHub linter

I like the Zen of Python. *There should be one - and preferably only one - obvious way to do it* reflects perfectly my philosophy of life. That is why I also like PEP-8: it solves the problem of different coding conventions across many teams. Sure, you have to sacrifice a bit of your freedom as a developer, and sometimes it is difficult to keep the line under 79 characters, but still I think it is worth it in the long run.

Every Python developer has an editor or an IDE configured to display all PEP-8 violations
(initially, of course, since in time you learn those rules by heart and you no longer need any hints).
But sometimes there is this new junior, who starts to push changes without installing a linter plugin first.
Or the manual testers in your team, who have never before heard of PEP-8, start to write Behave tests.
Or one of your fellow developers simply does not notice that ``imported but unused [F401]`` message.
What then? How to ensure that no PEP-8 violations will ever find their way into your codebase?

Don't worry, you don't have to manually validate every pull request.
You can configure an automatic linter. Once in place, it will analyse the changes
in a branch once a pull request is created. If no errors are found, it will
add a comment with a nice message. If there are any errors, it will add a comment with a
full description for each incorrect line of code.

Application setup
-----------------

First you need to create an app on Heroku. In case you haven't used Heroku before,
`here <https://devcenter.heroku.com/articles/getting-started-with-python#introduction>`_
is a guide that will help you get started.

To create a new app, go to **Dashboard** -> **New** -> **Create new app**.
You can specify the name of your app if you want.


.. image:: |filename|images/pep8-bot-heroku-app-name.png
   :alt: PEP-8 bot Heroku app name

Once the app is created, provide it with the **RabbitMQ Bigwig** add-on.
Go to **Resources**, find the add-on and click **Provision**. Unfortunately,
the process requires you to provide billing information (you need to
configure a credit card for your account). But don't worry, the add-on itself is free.

.. image:: |filename|images/pep8-bot-rabbitmq-provision.png
   :alt: Provisioning PEP-8 bot with rabbitmq plugin

Now we move to the command line. First, you should install **Heroku CLI**.
Just run this command:

.. code:: sh

        wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh

Next you will need to clone the repository with PEP-8 linter bot:

.. code:: sh

        git clone https://github.com/pfertyk/lint-review.git
        cd lint-review

The time has come to tell Heroku who you are. Run ``heroku login`` an provide
it with your Heroku credentials (email and password). Next you have to
configure a git remote to be able to push the code to Heroku.
The name of the remote can be found in your app's **Settings**:

.. image:: |filename|images/pep8-bot-heroku-git-url.png
   :alt: Heroku Git URL for PEP-8 bot

.. code:: sh

        git remote add heroku https://git.heroku.com.pep8-linter.git

For some reason, when I tried to deploy this app, Heroku insisted on
treating it as if it was written in Ruby. So, to be sure that it will be
recognized as Python code, you should set a proper buildpack:

.. code:: sh

        heroku buildpacks:set heroku/python

When this is done, you can deploy the app to Heroku:

.. code:: sh

        git push heroku master

Bear in mind that this process can take a while.

Configuration
-------------

Once the app is deployed, you will notice that the celery worker's status if ``OFF``:

.. image:: |filename|images/pep8-bot-disabled-celery-worker.png
   :alt: Disabled celery worker

To fix this, go to **Resources**, click the edit icon next to ``worker``,
switch the state and confirm.

Next go to **Settings** and click **Reveal Config Vars**.
You should see the following variables:

+----------------------+
|RABBITMQ_BIGWIG_URL   |
+----------------------+
|RABBITMQ_BIGWIG_TX_URL|
+----------------------+
|RABBITMQ_BIGWIG_RX_URL|
+----------------------+

You need to configure the settings file and workspace for your app.
You also have to specify the name of the server, which is the same as your
app's domain (you can find it in **Settings** -> **Domains**).
In my case, the additional configuration looked like this:

======================= =========================
LINTREVIEW_SERVER_NAME  pep8-linter.herokuapp.com
LINTREVIEW_SETTINGS     ./settings.py
LINTREVIEW_WORKSPACE    ./workspace
======================= =========================

New GitHub account
------------------

Your automatic linter will need a GitHub account.
You can use your own, but it's more fun to create a new one.

.. image:: |filename|images/pep8-bot-github-profile.png
   :alt: PEP-8 bot profile

Once the account is created, you will have to generate a token.
Go to **Settings** -> **Personal access tokens** -> **Generate new token**.
Choose a good description and select the **notifications** scope and the whole **repo** scope
(or just **public_repo** if you are going to use this bot only for public repositories).

Copy the token and go back to your Heroku app's **Settings**.
Add two new config variables: ``GITHUB_USER`` with the name of newly created GitHub
profile (in my case ``PEPing-tom``) and ``GITHUB_OAUTH_TOKEN``
with the token you just generated.

Testing
-------

Let's see your new bot in action. Create a test repository on GitHub.
The bot will look for linter configuration in a file called ``.lintrc``,
so let's create one with the following content:

.. code:: ini

        [tools]
        linters = flake8

There are two more things you need to configure in every repository that you want
this linter to check. First, you have to add your bot's GitHub profile as a collaborator
(**Settings** -> **Collaborators**), and the bot has to accept the invitation.
Second, you need to add a webhook to your repository to inform the bot about pull requests.
Go to **Settings** -> **Webhooks** -> **Add webhook**.
The value in **Payload URL** should be ``{HEROKU_APP_DOMAIN}/review/start``
(in my case it was ``https://pep8-linter.herokuapp.com/review/start``).
Leave ``application/json`` as content type and choose **Let me select individual events**.
The only event you need is **Pull request**.
Make sure that **Active** is checked and add a webhook.

Now let's see how it works in practice. Create a new branch in your test repository
and add some atrocious Python code:

.. code:: python

        def x():
            a=x

Push the new branch to GitHub and create a new pull request. A moment later, you should see some comments:

.. image:: |filename|images/pep8-bot-github-error-comments.png
   :alt: PEP8 bot in action

Let's fix these errors:

.. code:: python

        def x():
            a = 1
            print(a)

Now your bot informs you that there are no problems:

.. image:: |filename|images/pep8-bot-github-nice-comment.png
   :alt: PEP8 bot is content

That's it! Now you can be sure that no PEP-8 violation will sneak into your clean and standard-compliant codebase. Unless, of course, you decide to ignore these comments...

I hope that you found this tutorial useful. Please contact me if there is anything missing or if you encounter any problems with the whole process.
