---
title: Clean code in tests
date: 2017-02-16
summary: Because not only your production code deserves tenderness
tags:
- python
- tests
---

I like automated tests. I sleep better at night knowing that bugs in my projects will
be immediately detected. I try to keep the code in my tests clean and readable,
but I have noticed that (sadly) many developers seem to ignore this issue.

After all, why would you care about the code quality in tests? Tests are not
production code. You are not going to be paid for keeping them clean.
Moreover, usually you write a test once and never modify it later (unless
the requirements change). And you don't really look into tests
until something breaks, and then you do it only to check what went wrong.

Well, this is not entirely true. Test code is code, and it is (hopefully) the
only *untested* code in your project. Therefore you should keep it clean, just like anything
else you write. Also, you need to add new tests often. Nothing should keep you from
doing that, and badly structured tests will. Moreover, you need to
read tests quite frequently. Every time a test fails, you probably
have to dive into it to know what went wrong. And if the test is unreadable,
you will waste a lot of time just looking for a reason of the failure.

So in this post I would like to show you some of the problems you can encounter
in your tests and suggest how to fix them.

## Unclear names

One of the most common mistakes is vague or incorrect naming. Consider a test
like this one:

```python
def test_transaction_error(self):
    transaction_data = {
        'organization': 'Wayne Industries',
    }

    response = self.create_transaction(transaction_data)

    self.assertEqual(response.status_code, HTTP_422)
```

Now imagine that it fails. The only information you will receive will probably
be:

```
====== FAILURES ======
test_transaction_error
```

What does it tell you? That there is an error with transactions. But you already
know that, since the test failed. The name itself tells you nothing about
the nature of the problem. So you need to read the code to know what actually
went wrong. In this case, it is obvious that the test tries to create
a transaction and assumes that it's not possible. So, let's change the name
of the test:

```python
def test_transaction_creation_error(self):
    transaction_data = {
        'organization': 'Wayne Industries',
    }

    response = self.create_transaction(transaction_data)

    self.assertEqual(response.status_code, HTTP_422)
```

Now we know that there is a problem with transaction creation and not, let's
say, with transaction update or deletion. That's something. But we still don't
know *what* is wrong with transaction creation. So we keep on digging.
After a thorough examination we discover that response has not only the `status_code`,
but also some `data`. And that data contains a message, which says:
*You need to specify the amount*.
So, in order to improve our test, we can add another assertion:

```python
def test_transaction_creation_error(self):
    transaction_data = {
        'organization': 'Wayne Industries',
    }

    response = self.create_transaction(transaction_data)

    self.assertEqual(response.status_code, HTTP_422)
    self.assertEqual(
        response.data['message'],
        'You need to specify the amount.'
    )
```

Now the name of the test becomes more obvious:

```python
def test_cannot_create_transaction_without_amount(self):
    transaction_data = {
        'organization': 'Wayne Industries',
    }

    response = self.create_transaction(transaction_data)

    self.assertEqual(response.status_code, HTTP_422)
    self.assertEqual(
        response.data['message'],
        'You need to specify the amount.'
    )
```

Next time the test fails, you will immediately know what went wrong:

```
================= FAILURES ==================
test_cannot_create_transaction_without_amount
```

Naming things is a very delicate process and it takes a lot time and practice to master it.
In this example, the name was quite obvious (after a while).
But in your project it might be way more difficult. Also, if you are working in
a team, you will need to comply with the style that other developers use
(for example, you might agree on using shorter but less self-explainatory names).

## Multiple assertions

Another common mistake is putting multiple tests into one. Let's look at an
example:

```python
def test_list_transactions(self):
    response = self.get_transactions()
    self.assertIn(response.status_code, [HTTP_401, HTTP_403])
    self.login_as(self.user)
    response = self.get_transactions()
    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(response.data, [])
    self.create_transaction()
    response = self.get_transactions()
    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(len(response.data), 1)
```

If this test fails, do we know that exactly went wrong? Was it the authentication process?
Or was the new transaction not listed? We will not know that until we put
some breakpoints in the code and spend (or rather waste) some time figuring it
out.

Every test should do 3 things:

* prepare the data
* execute some action
* check if the result was as expected

Out example actually includes 3 assertions, and therefore it checks 3 things.
So let's split it into 3 tests, each with a meaningful name:

```python
def test_transaction_list_requires_authentication(self):
    response = self.get_transactions()

    self.assertEqual(response.status_code, HTTP_401)

def test_transaction_list_is_initially_empty(self):
    self.login_as(self.user)

    response = self.get_transactions()

    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(response.data, [])

def test_new_transactions_are_shown_on_transaction_list(self):
    self.login_as(self.user)
    self.create_transaction()

    response = self.get_transactions()

    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(len(response.data), 1)
```

Each of those tests checks just one thing, so if any of them fails, we will know
where to look for a bug. You might notice that there is a cost: we need to duplicate
some code (in our case we need to login twice in two different tests). Still,
it's better than having one huge test that checks many things at once.

## Complicated fixtures

Using overly complicated data in our tests is also a bad practice, although
a bit less obvious. Consider this example:

```python
def test_sell_same_stock_twice_in_one_transaction(self):
    seller = test_helpers.create_seller(
        name='Frank', surname='Sinatra', age='33'
    )
    stocks = [
        Stock(stock_id=35, no_of_shares=45, comment='First'),
        Stock(stock_id=35, no_of_shares=34, comment='Second'),
    ]

    response = self.sell_stocks(seller, stocks)

    self.assertEqual(response.status_code, HTTP_422)
```

At first it doesn't look that bad. It checks only one thing and it has a meaningful
name. But let's say you have to read it and maybe modify it (because the requirements
have changed). Which part of this test code is important and which is not? Will you know
it at first glance?

Let's start with `seller`. Why is it Frank Sinatra, age 33? Why not John Connor, age 10?
The `seller` is here only because we need someone to sell the stocks. The name and
age are not important. So, let's simplify the test:

```python
def test_sell_same_stock_twice_in_one_transaction(self):
    seller = test_helpers.create_seller()
    stocks = [
        Stock(stock_id=35, no_of_shares=45, comment='First'),
        Stock(stock_id=35, no_of_shares=34, comment='Second'),
    ]

    response = self.sell_stocks(seller, stocks)

    self.assertEqual(response.status_code, HTTP_422)
```

Now we will use a seller created with whatever default data the `create_seller`
method provides. And it should not bother us at all, since it's not the seller we are
testing here, it's stocks.

But stock creation also looks complicated. What do we need the comment for? Probably nothing.
Do we really need to specify the number of shares? Probably not.
The important part is the `stock_id`, and it should have the simplest possible value
(not 35, but 1). So let's fix that too:

```python
def test_sell_same_stock_twice_in_one_transaction(self):
    seller = test_helpers.create_ticket_seller()
    stocks = [Stock(stock_id=1), Stock(stock_id=1)]

    response = self.sell_stocks(seller, stocks)

    self.assertEqual(response.status_code, HTTP_422)
```

Now if we ever need to read this test, we will immediately know what we should
focus on.

## Confusing times

I have seen many tests that require date or time manipulation. Surprisingly,
a lot of them is confusing and unclear. Let's take a look:

```python
def test_view_sellers_for_past_transactions(self):
    past_transaction = test_helpers.create_transaction()
    test_helpers.add_seller(past_transaction)
    # we cannot add sellers for past transactions
    past_transaction.date = timezone.now() - timedelta(days=3)
    past_transaction.save()

    upcoming_transaction = test_helpers.create_transaction()
    test_helpers.add_seller(upcoming_transaction)

    response = self.call_api('/sellers/past')

    self.assertEqual(len(response.data), 1)
    self.assertEqual(
        response.data[0]['transaction'], past_transaction
    )
```

Some explaination is in order. We want to check if `sellers/past` endpoint
lists only the sellers associated with past transactions. The problem is, we cannot
add a seller to a past transaction. So, we create an upcoming transaction
(`create_transaction`), we add a seller, and we move it to the past manually.
Then, we create an upcoming transaction, we add a seller and then we can perform
an actual test.

Quite complicated, isn't it? Now imagine you have to find a reason why this test has failed.
It always takes me way too much time to figure out what a test like
this actually does. And this is not even the worst example I have encountered.
The worst one had a `sleep(1)` inside to make sure that the object we created
was a past one!

The solution here is simple: use [freezegun](https://github.com/spulec/freezegun).
It provides an easy way of controlling the time inside your tests:

```python
from freezegun import freeze_time


def test_view_sellers_for_past_transactions(self):
    with freeze_time('2000-01-01'):
        past_transaction = test_helpers.create_transaction()
        test_helpers.add_seller(past_transaction)

    with freeze_time('3000-01-01'):
        upcoming_transaction = test_helpers.create_transaction()
        test_helpers.add_seller(upcoming_transaction)

    with freeze_time('2500-01-01'):
        response = self.call_api('/sellers/past')

    self.assertEqual(len(response.data), 1)
    self.assertEqual(
        response.data[0]['transaction'], past_transaction
    )
```

Much nicer, isn't it? The freezegun module provides other useful tools,
that can make date and time manipulation much easier. Check the project's
GitHub page for more info.

## Summary

These were just some examples I have found while working on different projects.
I hope that this post will help you with solving similar problems in your code.
Also, if you encountered a code quality issue that I missed, please let me know.
