import json
import datetime

from models.base import SmartSession
from models.event import Event
from models.report import Report


# TODO: consider using asyncio or multiprocessing to allow this to run while returning a 200 status code
#  it is likely that we'd need asyncio because things like fetching past events from DB or getting
#  content from github are I/O bound operations.
#  on the other hand, if we need to do some heavy computation, we might want to use multiprocessing/multithreading.
def process_webhook(json_data):
    """
    This function processes the incoming webhook data and runs a series of tests on it. If any of the tests fail, it
    will return a report of the failed tests. If all the tests pass, it will return None.

    Parameters
    ----------
    json_data: str
        The incoming webhook data in JSON format.

    Returns
    -------
    report: str
        A report of the failed tests, or None if all tests passed.
    """

    data = json.loads(json_data)
    bad_list = []
    report = None  # the default is to return nothing
    # run all the tests one after the other (append to bad_list if there's a problem)
    with SmartSession() as session:
        # TODO: if moving to asyncio, need to consider opening a session for each subroutine

        # check if the data is consistent with an event we can use, if not, return None
        event = create_event(data)

        if event is not None:
            if event.subject == "commit":
                check_push(data, bad_list, session)
            if event.subject == "team":
                check_team_creation(data, bad_list, session)
            if event.subject == "repo":
                check_repo_creation(data, bad_list, session)
                check_repo_deletion(data, bad_list, session)

            if len(bad_list) > 0:
                report = create_report(bad_list, session)
                event.reports.append(report)

            session.add(event)
            session.commit()

    return report


def check_push(data, bad_list, session=None):
    """Check for push into one of the repositories.

    This check flags push times between 14:00 and 16:00.
    """
    pass


def check_team_creation(data, bad_list, session=None):
    """Check if posting a new team.

    This check will flag any new teams with a name that starts with "hacker".
    """


def check_repo_creation(data, bad_list, session=None):
    """Checks to run when new repository is created.

    This will not flag anything right now.
    """
    pass


def check_repo_deletion(data, bad_list, session=None):
    """Checks to run when a repository is deleted.

    This will flag repos that were created less than 10 minutes ago.
    """
    pass


def create_report(bad_list, session=None):
    """Create a Report object, and post it to the DB.

    The report will have a list of bad things that happened, and the time they happened.

    Returns
    -------
    report: Report object
        The report of the failed checks.
    """
    pass


def create_event(data):
    """Make a new Event object to log something that was reported via webhook.
    Will parse the data to figure out if this is a type of event we can use.

    Parameters
    ----------
    data: dict
        The incoming webhook data.

    Returns
    -------
    event: Event object
        The event that was logged.
    """
    now = datetime.datetime.utcnow()  # default timestamp is when it was received
    # check if it is a team creation event
    if data.get("action") == "created" and "team" in data:
        event = Event(
            subject="team",
            action="create",
            name=data["team"]["name"],
            timestamp=now,  # no timing data on this event
        )
    # check if it is a repo creation event

    # check if it is a repo deletion event

    # check if it is a commit push event

    else:
        event = None

    return event
