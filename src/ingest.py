import datetime

from models.base import SmartSession
from models.event import Event, subject_to_int, action_to_int
from models.report import Report


# TODO: consider using asyncio or multiprocessing to allow this to run while returning a 200 status code
#  it is likely that we'd need asyncio because things like fetching past events from DB or getting
#  content from github are I/O bound operations.
#  on the other hand, if we need to do some heavy computation, we might want to use multiprocessing/multithreading.
def process_webhook(data, headers, timestamp=None):
    """
    This function processes the incoming webhook data and runs a series of tests on it. If any of the tests fail, it
    will return a report of the failed tests. If all the tests pass, it will return None.

    Parameters
    ----------
    data: dict
        The incoming webhook data.
    headers: dict
        The headers of the incoming webhook.

    Returns
    -------
    report: str
        A report of the failed tests, or None if all tests passed.
    """
    bad_list = []
    report = None  # the default is to return nothing
    # run all the tests one after the other (append to bad_list if there's a problem)
    with SmartSession() as session:
        # TODO: if moving to asyncio, need to consider opening a session for each subroutine

        # check if the data is consistent with an event we can use, if not, return None
        event = create_event(data, headers, timestamp)

        if event is not None:
            # can add more checks here...
            if event.subject == "push":
                check_push(event, bad_list, session)
            if event.subject == "team":
                if event.action == "created":
                    check_team_creation(event, bad_list, session)
            if event.subject == "repository":
                if event.action == "created":
                    check_repo_creation(event, bad_list, session)
                if event.action == "deleted":
                    check_repo_deletion(event, bad_list, session)

            if len(bad_list) > 0:
                report = create_report(bad_list, session)
                event.reports.append(report)

            session.add(event)
            session.commit()

    return report


def create_event(data, headers, timestamp=None):
    """Make a new Event object to log something that was reported via webhook.
    Will parse the data to figure out if this is a type of event we can use.

    Parameters
    ----------
    data: dict
        The incoming webhook data.
    headers: dict
        The headers of the incoming webhook.
    timestamp: datetime.datetime, optional
        The timestamp of the event, if None, will default to the current time.

    Returns
    -------
    event: Event object
        The event that was logged.
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()  # default timestamp is when it was received

    action = data.get("action", None)

    subject = headers["X-GitHub-Event"]
    if subject == "repository":
        name = data["repository"]["name"]
    elif subject == "team":
        name = data["team"]["name"]
    elif subject == "push":
        name = data["head_commit"]["id"]
        action = "created"

    if subject in subject_to_int and action in action_to_int:
        event = Event(
            subject=subject,
            action=action,
            timestamp=timestamp,
            name=name,
        )
        event.data = data  # this is not stored in the database but is useful for checks
    else:
        event = None  # we don't know this type of event

    return event


def create_report(bad_list, session=None):
    """Create a Report object to log the failed checks.

    The report will have a ";"-separated list of bad things that happened.

    Returns
    -------
    report: Report object
        The report of the failed checks.
    """
    report = Report(
        # content=json.dumps(bad_list),  # if we want to use dictionary instead of a list of strings
        content="; ".join(bad_list),
    )

    return report


def check_push(event, bad_list, session=None):
    """Check for push into one of the repositories.

    This check flags push times between 14:00 and 16:00.
    """
    if 14 <= event.timestamp.hour < 16:
        bad_list.append("Push event timestamp is not within legal bounds")


def check_team_creation(event, bad_list, session=None):
    """Check if posting a new team.

    This check will flag any new teams with a name that starts with "hacker".
    """
    if event.data["team"]["name"].startswith("hacker"):
        bad_list.append("Team name starts with 'hacker'")


def check_repo_creation(event, bad_list, session=None):
    """Checks to run when new repository is created.

    This will not flag anything right now.
    """
    pass


def check_repo_deletion(event, bad_list, session=None):
    """Checks to run when a repository is deleted.

    This will flag repos that were created less than 10 minutes ago.
    """
    created_timestamp = datetime.datetime.strptime(event.data["repository"]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    if event.timestamp - created_timestamp < datetime.timedelta(minutes=10):
        bad_list.append("Repository deleted less than 10 minutes after creation!")
