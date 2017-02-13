Title: Clean code in tests
Date: 2017-02-16
Summary: Smart summary

My experience with tests

## Unclear names

```python
def test_event_error(self):
    organization = test_helpers.create_organization()
    event_data = {
        'name': 'Iron Maiden concert',
        'organization': organization,
    }

    response = self.create_event(event_data)

    self.assertEqual(response.status_code, HTTP_422)
```

```python
def test_create_event_invalid_request(self):
    organization = test_helpers.create_organization()
    event_data = {
        'name': 'Iron Maiden concert',
        'organization': organization,
    }

    response = self.create_event(event_data)

    self.assertEqual(response.status_code, HTTP_422)
```

```python
def test_create_event_invalid_request(self):
    organization = test_helpers.create_organization()
    event_data = {
        'name': 'Iron Maiden concert',
        'organization': organization,
    }

    response = self.create_event(event_data)

    self.assertEqual(response.status_code, HTTP_422)
    self.assertEqual(
        response.data['message'],
        'You cannot create an event without a venue.'
    )
```

```python
def test_cannot_create_event_without_venue(self):
    organization = test_helpers.create_organization()
    event_data = {
        'name': 'Iron Maiden concert',
        'organization': organization,
    }

    response = self.create_event(event_data)

    self.assertEqual(response.status_code, HTTP_422)
    self.assertEqual(
        response.data['message'],
        'You cannot create an event without a venue.'
    )
```

## Multiple assertions

```python
def test_list_tickets(self):
    response = self.get_tickets()
    self.assertIn(response.status_code, [HTTP_401, HTTP_403])
    self.login_as(self.user)
    response = self.get_tickets()
    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(response.data, [])
    self.allocate_ticket()
    response = self.get_tickets()
    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(len(response.data), 1)
```

```python
def test_ticket_list_requires_authentication(self):
    response = self.get_tickets()

    self.assertEqual(response.status_code, HTTP_401)
```

```python
def test_ticket_list_is_initially_empty(self):
    self.login_as(self.user)

    response = self.get_tickets()

    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(response.data, [])
```

```python
def test_ticket_list_contains_allocated_tickets(self):
    self.login_as(self.user)
    self.allocate_ticket()

    response = self.get_tickets()

    self.assertEqual(response.status_code, HTTP_200)
    self.assertEqual(len(response.data), 1)
```

## Complicated fixtures

```python
def test_cannot_allocate_overlapping_seats(self):
    seller = test_helpers.create_ticket_seller(
        name='Frank', surname='Sinatra', age='33')
    seat_ranges = [
        Range(34, 84, section='Balcony', block='B1'),
        Range(56, 95, section='Balcony', block='B1'),
    ]

    response = self.allocate_tickets(seller, seat_ranges)

    self.assertEqual(response.status_code, HTTP_422)
```

```python
def test_cannot_allocate_overlapping_seats(self):
    seller = test_helpers.create_ticket_seller()
    seat_ranges = [
        Range(34, 84, section='Balcony', block='B1'),
        Range(56, 95, section='Balcony', block='B1'),
    ]

    response = self.allocate_tickets(seller, seat_ranges)

    self.assertEqual(response.status_code, HTTP_422)
```

```python
def test_cannot_allocate_overlapping_seats(self):
    seller = test_helpers.create_ticket_seller()
    seat_ranges = [Range(1, 2), Range(2, 3)]

    response = self.allocate_tickets(seller, seat_ranges)

    self.assertEqual(response.status_code, HTTP_422)
```

```python
def test_cannot_allocate_overlapping_seats(self):
    seller = test_helpers.create_ticket_seller()
    seat_ranges = [Range(1, 2), Range(2, 3)]

    response = self.allocate_tickets(seller, seat_ranges)

    self.assertEqual(response.status_code, HTTP_422)
    self.assertEqual(response.data, {'errors': [
        {},
        {},
        {'You cannot create duplicate items.'},
        {},
    ]})
```

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
