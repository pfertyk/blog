Title: Clean code in tests
Date: 2017-02-16
Summary: Smart summary

I like automated tests. I sleep better at night. I've seen many tests in my life
and I keep seeing the same mistakes in them. In this post I would like to show
you the most common ones and help you fix some of them.


Why would you care about the quality of code in tests? After all, they are not
production code. You are not going to be paid for keeping them clean.
Moreover, usually you write the test once and never modify it later (maybe if
if the requirement change). And you don't really look into the test code
until something breaks, and then you do it only to check what went wrong.

Well, this is not entirely true. Test code is code, and it is (hopefully) the
only *untested* code in your project. You should keep them clean, just as any
other code. Also, you need to write tests often. Nothing should keep you from
doing that, and badly structured code will do just that. Moreover, you need to
read tests more often than you think. Every time a test fails, you probably
have to dive into it to know that went wrong. And if the test is unreadable,
you will waste a lot of time just looking for a reason of a failure.

So let's consider a simple banking system where you need to handle transactions,
accounts and stuff like that.

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
went wrong. In this case, it is obvious that the tests tries to create
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
After thorough examination we discover that response has not only the `status_code`,
but also some `data`. And that data contains a message, which says:
*You need to specify an amount of the transaction.*.
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
        'You need to specify an amount of the transaction.'
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
        'You need to specify an amount of the transaction.'
    )
```

Next time the test fails, you will immediately know what went wrong:

```
================= FAILURES ==================
test_cannot_create_transaction_without_amount
```



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

When this test fails, what exactly went wrong? Was it the authentication process?
Or was the new transaction not listed? We will not know that until we put
some breakpoints in the code and spend (or rather waste) some time figuring
out what went wrong.

Each test should do 3 things:

* prepare the data
* execute some action
* check if the result was as expected

The example actually includes 3 assertions. So let's split it into 3 tests,
each with a meaningful name:

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

Each of those tests check just one thing, so if any of them fails, we will know
where to look for a bug. You might notice that there is a cost: we need to duplicate
some code (in our case we need to login twice in two different tests). Still,
it's worth it.

## Complicated fixtures

Using overly complicated data in our tests is also a bad practice, although
a bit less obvious. Consider this example:

```python
def test_sell_same_stock_twice_in_one_transaction(self):
    seller = test_helpers.create_seller(
        name='Frank', surname='Sinatra', age='33'
    )
    stocks = [
        Stock(stock_id=35, no_of_shares=45, comment='First item'),
        Stock(stock_id=35, no_of_shares=34, comment='Second'),
    ]

    response = self.sell_stocks(seller, stocks)

    self.assertEqual(response.status_code, HTTP_422)
```

At first it doesn't look that bad. It checks only one thing and it has a meaningful
name. But let's say you have to read it and maybe change it (because the requirements
have changed). Which part of this test code is important and which is not? Will you know
it at first glance?

Let's start with `seller`. Why is it Frank Sinatra, age 33? Why not John Connor, age 10?
The `seller` is here only because we need someone to sell the stocks. The name and
age are not important. So, let's simplify the test:

```python
def test_sell_same_stock_twice_in_one_transaction(self):
    seller = test_helpers.create_seller()
    stocks = [
        Stock(stock_id=35, no_of_shares=45, comment='First item'),
        Stock(stock_id=35, no_of_shares=34, comment='Second'),
    ]

    response = self.sell_stocks(seller, stocks)

    self.assertEqual(response.status_code, HTTP_422)
```

Now we will use a seller created with whatever default date the `create_seller`
method has. And it should not bother us at all, since it's not the seller we are
testing here, it's stock.

But stock creation also looks complicated. What do we need the comment for? Probably nothing.
Do we really need to specify the number of shares? Probably no.
The important part is the `stock_id`, and it should be the simplest one possible
(not 35, but 1). So let's leave just that:

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

```python
def test_view_tickets_for_past_events(self):
    event_past = test_helpers.save_event()
    test_helpers.allocate_ticket(event_past)
    event_past.start = timezone.now() - timedelta(days=3)
    event_past.end = timezone.now() - timedelta(days=2)
    event_past.save()

    event_upcoming = test_helpers.save_event()
    test_helpers.allocate_ticket(event_upcoming)

    response = self.call_api('/tickets/past')

    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['event'], event_past)
```

```python
from freezegun import freeze_time

def test_view_tickets_for_past_events(self):
    with freeze_time(2000-01-01):
        event_past = test_helpers.save_event()
        test_helpers.allocate_ticket(event_past)
    with freeze_time(3000-01-01):
        event_upcoming = test_helpers.save_event()
        test_helpers.allocate_ticket(event_upcoming)
    with freeze_time(2500-01-01):
        response = self.call_api('/tickets/past')

    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['event'], event_past)
```

```python
from freezegun import freeze_time

def test_view_tickets_for_past_events(self):
    with freeze_time(2000):
        event_past = test_helpers.save_event()
        test_helpers.allocate_ticket(event_past)
    with freeze_time(3000):
        event_upcoming = test_helpers.save_event()
        test_helpers.allocate_ticket(event_upcoming)
    with freeze_time(2500):
        response = self.call_api('/tickets/past')

    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['event'], event_past)
```

## Unhelpful helpers

```python
def test_allocating_tickets(self):
    self._validate_tickets()

def test_allocating_tickets_admin(self):
    tickets = self._validate_tickets(False)
    self.assertEqual(tickets, [])

def test_filter_past_tickets(self):
    self._validate_tickets()

    response = self.call_api('/tickets/past')
    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(len(response.data), 3)
```

```python
def _validate_tickets(self, is_normal_user=True):
    # login as self.user or self.admin if not is_normal_user
    # create 2 events (one past, one upcoming)
    # assert events creation was successful
    # prepare complicated test data for 6 tickets
    # call the API to create tickets (3 past, 3 upcoming)
    # assert tickets creation was successful
    # return created tickets as a list
```
