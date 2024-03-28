# A monitoring app that checks events on github for malicious activities

## Usage:

After checking out the code (inside the directory) do:

```bash
export FLASK_APP=src/main.py
python -m flask run
```

Make sure to first install the requirements!

## Requirements

The `requirements.txt` file should contain all the packages that are needed to run the code.
To install requirements, (e.g., using venv):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setting up webhooks:

TDA

## Malicious activities

Currently, the app will alert the user for the following activities:

- A team is created with a name that starts with "hackers".
- A team is created with a name that ends with "legit".
- A repo is created and then deleted within 10 minutes.
- Code is pushed between 14:00 and 16:00 UTC (TODO: we need to convert local time).

Additional checks will be added later.
Any malicious activity is printed to the terminal, and stored in a database.

## Configuration

Use the parameters in the `configure.yaml` file to set the conditions for flagging malicious software.

## Database

Events that are relevant (e.g., repo creation/deletion, team creation, pushing new commits)
are stored in a SQLite database.
These can be accessed using SQL alchemy, for example:

```python
import sqlalchemy as sa
from models.base import SmartSession
from models.event import Event

with SmartSession() as session:
    event = session.scalars(sa.select(Event).where(Event.subject == 'team')).first()
    print(f'event {event.id}: subject: {event.subject}, action: {event.action}, time: {event.timestamp}')
```

Similarly, `Report` objects can be loaded, linking back to the event object, with a string `content` that
contains information on malicious activities.

```python
import sqlalchemy as sa
from models.base import SmartSession
from models.report import Report

with SmartSession() as session:
    report = session.scalars(sa.select(Report)).first()
    print(f'report {report.id}: event: {report.event_id}, content: {report.content}')
```

## Tests

The code is accompanied by a few basic tests, in the `tests` directory.
We currently do not test the flask app accepting the webhooks,
as that takes some setup to do, and requires posting things to GitHub.
The behaviors after the webhooks are received is tested in the `test_ingest.py` file.

Tests are run automatically when new code is posted to the repo (either directly or in a pull-request).

## License

This project is licensed under the MIT License,
which means it is distributed as open source software.
See the [LICENSE.md](LICENSE.md) file for details.
