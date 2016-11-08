Title: Run ESlint on each pull request
Date: 2016-11-08
Summary: Because, sooner or later, you will have to use JavaScript

Last time: PEP8 linter (link to article). But javascript. So here is another solution: update the bot to detect js style violations.

Assume you already have Pep8 bot

## Heroku configuration

add new buildpack

![Node.js buildpack]({filename}/images/eslint-bot-nodejs-buildpack.png)
![Two buildpacks]({filename}/images/eslint-bot-double-buildpack.png)

Note: this can also be achieved with command line.

```sh
heroku buildpacks:add heroku/nodejs
```

Check if working:

```sh
$ heroku buildpacks
=== pep8-linter Buildpack URLs
1. heroku/python
2. heroku/nodejs
```

## Code changes

already in repo

```sh
npm install --save eslint eslint-plugin-import eslint-plugin-react eslint-plugin-jsx-a11y eslint-config-airbnb
```

config file should look like this:

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

ugly coupling?

## New configuration

Add `eslint` to `.lintrc`:

```ini
[tools]
linters = flake8, eslint
```

Add `.eslintrc` file:

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

## New bot in action

`main.js`:

```js
var x = 5
a = x
```

Comments:

![ESlint comments]({filename}/images/eslint-bot-comments.png)

Change the name

That's it!
