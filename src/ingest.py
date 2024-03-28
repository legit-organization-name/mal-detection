import os
import yaml
import datetime

from models.base import SmartSession, CODE_ROOT
from models.event import Event, subject_to_int, action_to_int
from models.report import Report


# TODO: consider using asyncio or multiprocessing to allow this to run while returning a 200 status code
#  it is likely that we'd need asyncio because things like fetching past events from DB or getting
#  content from github are I/O bound operations.
#  on the other hand, if we need to do some heavy computation, we might want to use multiprocessing/multithreading.


class WebhookIngester:
    def __init__(self):
        config_path = os.path.join(CODE_ROOT, "configure.yaml")
        if os.path.isfile(config_path):
            self.config = yaml.safe_load(open(config_path))
        else:
            self.config = {}

        self.data = None
        self.headers = None
        self.bad_list = None
        self.timestamp = None
        self.event = None

    def ingest(self, data, headers, timestamp=None):
        """This function processes the incoming webhook data and runs a series of tests on it.
        If any of the tests fail, it will return a report of the failed tests.
        If all the tests pass, it will return None.

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
        self.data = data
        self.headers = headers
        self.timestamp = timestamp
        self.bad_list = []  # a new list
        self.event = None

        report = None  # the default is to return nothing
        # run all the tests one after the other (append to bad_list if there's a problem)
        with SmartSession() as session:
            # TODO: if moving to asyncio, need to consider opening a session for each subroutine

            # check if the data is consistent with an event we can use, if not, return None
            self.event = self.create_event()

            if self.event is not None:
                # can add more checks here...
                if self.event.subject == "push":
                    self.check_push(session)
                if self.event.subject == "team":
                    if self.event.action == "created":
                        self.check_team_creation(session)
                if self.event.subject == "repository":
                    if self.event.action == "created":
                        self.check_repo_creation(session)
                    if self.event.action == "deleted":
                        self.check_repo_deletion(session)

                if len(self.bad_list) > 0:
                    report = self.create_report()
                    self.event.reports.append(report)

                session.add(self.event)
                session.commit()

        return report

    def create_event(self):
        """Make a new Event object to log something that was reported via webhook.
        Will parse the data to figure out if this is a type of event we can use.

        Returns
        -------
        event: Event object
            The event that was logged.
        """
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow()  # default timestamp is when it was received

        action = self.data.get("action", None)

        subject = self.headers["X-GitHub-Event"]
        if subject == "repository":
            name = self.data["repository"]["name"]
        elif subject == "team":
            name = self.data["team"]["name"]
        elif subject == "push":
            name = self.data["head_commit"]["id"]
            action = "created"

        if subject in subject_to_int and action in action_to_int:
            self.event = Event(
                subject=subject,
                action=action,
                timestamp=self.timestamp,
                name=name,
            )
            if self.config.get("verbose", False):
                print(f"Event: subject= {subject}, action= {action}, name= {name}, timestamp= {self.timestamp}")

        return self.event

    def create_report(self):
        """Create a Report object to log the failed checks.

        The report will have a ";"-separated list of bad things that happened.

        Returns
        -------
        report: Report object
            The report of the failed checks.
        """
        report = Report(
            # content=json.dumps(self.bad_list),  # if we want to use dictionary instead of a list of strings
            content="; ".join(self.bad_list),
        )
        return report

    def check_push(self, session=None):
        """Check for push into one of the repositories.

        This check flags push times between 14:00 and 16:00.
        """
        if self.config.get("push", {}).get(
            "bad-time-start"
        ) <= self.event.timestamp.hour and self.event.timestamp.hour <= self.config.get("push", {}).get("bad-time-end"):
            self.bad_list.append("Push event timestamp is not within legal bounds")

    def check_team_creation(self, session=None):
        """Check if posting a new team.

        This check will flag any new teams with a name that starts with "hacker".
        """
        if self.data["team"]["name"].startswith(self.config.get("team", {}).get("illegal-prefix")):
            self.bad_list.append(f"Team name starts with '{self.config.get('team', {}).get('illegal-prefix')}'")

        if self.data["team"]["name"].endswith(self.config.get("team", {}).get("illegal-suffix")):
            self.bad_list.append(f"Team name ends with '{self.config.get('team', {}).get('illegal-suffix')}'")

    def check_repo_creation(self, session=None):
        """Checks to run when new repository is created.

        This will not flag anything right now.
        """
        pass

    def check_repo_deletion(self, session=None):
        """Checks to run when a repository is deleted.

        This will flag repos that were created less than 10 minutes ago.
        """
        created_timestamp = datetime.datetime.strptime(self.data["repository"]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        number = self.config.get("repository", {}).get("create-delete-time", 10)
        if self.event.timestamp - created_timestamp < datetime.timedelta(minutes=number):
            self.bad_list.append(f"Repository deleted less than {number} minutes after creation!")
