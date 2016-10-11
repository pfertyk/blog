Detect PEP-8 violations on pull requests
###############################################################

:date: 2016-10-11
:summary: Your own automatic GitHub linter


I like the philosophy of Python. **"There should be one - and preferably only one - obvious way to do it"** seems like a very reasonable conclusion. That is why I also like PEP-8: it solves the problem of different coding conventions across many teams. Sure, you have to sacrifice a bit of your freedom as a developer, and sometimes it is difficult to keep the line under 79 characters, but still it is worth it in the long run.

Every Python developer has an editor or an IDE configured to display all PEP-8 warnings and errors (initially, of course, since in time you learn those rules by heart and you no longer need any hints). But sometimes there is this new junior, who starts to push changes without installing linter plugin first. Or the testers in your team, who have never before heard of PEP-8, start to write Behave tests. Or one of your fellow developers simply does not notice that :code:`imported but unused [F401]` message. What then? How to ensure that no PEP-8 violations will ever find their way into your codebase?

Don't worry, you don't have to manually validate every pull request. You can configure an automatic linter. Once in place, it will analyse the changes in a branch once a pull request is created. If no errors are found, it will add a comment with a nice message. If there are any errors, it will add a comment with a full description for each incorrect line of code.








Repo lint-review

Configuration!

Heroku

Github
token

Webhook

checked repo + invitation
