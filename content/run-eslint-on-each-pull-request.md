Title: Run ESlint on each pull request
Date: 2016-11-08
Summary: Because, sooner or later, you will have to use JavaScript
Tags: bot, heroku, javascript

In one of my [previous posts]({filename}/pep8-github-linting-bot.md)
I described how to automatically check for PEP-8 violations on pull requests.
But sometimes Python is not enough, and your project will require some JavaScript as well.
Fortunately, you can modify the `PEPing-tom` bot to also use ESlint to ensure the quality of your whole codebase.

In this post I will show you how to update your linter to check also JavaScript files using [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript). To proceed you should first configure an automatic PEP-8 linter mentioned earlier.

## Heroku configuration

First thing you need to do is add another buildpack. As you remember, last time you
specifically told Heroku that your linter is a Python application. Now you need to
treat is also as a JavaScript application, so the dependencies in `package.json` file
can be properly installed.

Go to your app's **Settings** and click **Add buildpack** button. Next, select **nodejs** buildpack:

![Node.js buildpack]({static}/images/eslint-bot-nodejs-buildpack.png)

Now your app should have two buildpacks:

![Two buildpacks]({static}/images/eslint-bot-double-buildpack.png)

If you are passionate about the command line (like me), you can achieve the same effect this way:

```sh
heroku buildpacks:add heroku/nodejs
```

Now check if it worked:

```sh
$ heroku buildpacks
=== pep8-linter Buildpack URLs
1. heroku/python
2. heroku/nodejs
```

## Code changes

Next you need to update your linter. New version is already available in my
[repository](github.com/pfertyk/lint-review), you can just clone it and push it to Heroku. The only modification was to put proper
modules in `package.json` file:

```json
{
  "name": "lint-review",
  "version": "0.1.14",
  "private": true,
  "dependencies": {
    "eslint": "^3.9.1",
    "eslint-config-airbnb": "^12.0.0",
    "eslint-plugin-import": "^2.1.0",
    "eslint-plugin-jsx-a11y": "^2.2.3",
    "eslint-plugin-react": "^6.6.0"
  }
}
```

Of course, if you decide to use another linter (ESlint is not the only available option), then you will have to change the list of packages you want to install.

## New configuration

Now you need to modify the configuration in the repository you want to be checked by your linter.
Add `eslint` to the list of linters in `.lintrc` file:

```ini
[tools]
linters = flake8, eslint
```

Next create a new file with ESlint configuration (call it `.eslintrc`):

```json
{
  "extends": "airbnb",
  "rules": {
    "no-use-before-define": ["error", {"functions":false}],
    "no-unused-vars": ["error", {"vars": "all", "args": "none"}],
    "prefer-const": ["error", {
      "destructuring": "all"
    }],
    "no-else-return": "off",
    "class-methods-use-this": "off",
    "no-continue": "off"
  },
}
```

This is of course my choice of linting rules. You can configure anything you like or anything your team agreed to use.

## New bot in action

Now let's check if your modified bot actually works. Create a new file `main.js` and put the following
code in it:

```js
var x = 5
a = x
```

Soon after creating a pull request with this file, you should notice that your bot is not very happy:

![ESlint comments]({static}/images/eslint-bot-comments.png)

You might also notice that the name `PEPing-tom` no longer suits your bot, since now it can also use ESlint.
Maybe `ESPEP` would be better?

That's it! Your linter is up and running. Now it should keep both Python and JavaScript developers on their toes.

I hope this tutorial will make your life a bit easier. If any instructions are unclear or not working, please let me know.
