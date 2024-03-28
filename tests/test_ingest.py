import os
import time
import datetime
import json

import sqlalchemy as sa

from models.base import CODE_ROOT, SmartSession
from models.event import Event, int_to_action, action_to_int, subject_to_int, int_to_subject
from models.report import Report

from src.ingest import process_webhook

data_dir = os.path.join(CODE_ROOT, "data")


def test_new_team():
    with open(os.path.join(data_dir, "example_new_team.json")) as f:
        json_data = json.load(f)

    ret = process_webhook(json_data, {"X-GitHub-Event": "team"})
    assert ret is None

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event).where(Event.action == "created", Event.subject == "team").order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "created"
    assert event.subject == "team"
    assert event.name == "testing-team-name"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)

    with open(os.path.join(data_dir, "example_new_team_bad.json")) as f:
        json_data = json.load(f)

    ret = process_webhook(json_data, {"X-GitHub-Event": "team"})
    assert ret is not None
    assert isinstance(ret, Report)
    assert ret.content == "Team name starts with 'hacker'"

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event).where(Event.action == "created", Event.subject == "team").order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "created"
    assert event.subject == "team"
    assert event.name == "hacker-team"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)
    assert len(event.reports) == 1
    assert event.reports[0].content == "Team name starts with 'hacker'"

    # check report is posted and can be recovered
    with SmartSession() as session:
        report = session.scalars(
            sa.select(Report)
            .where(Report.content == "Team name starts with 'hacker'")
            .order_by(Report.created_at.desc())
        ).first()

    assert report is not None
    assert report.created_at < now
    assert report.created_at > now - datetime.timedelta(seconds=3)
    assert report.event_id == event.id
    assert report.content == "Team name starts with 'hacker'"


def test_new_repo():
    with open(os.path.join(data_dir, "example_new_repo.json")) as f:
        json_data = json.load(f)

    ret = process_webhook(json_data, {"X-GitHub-Event": "repository"})
    assert ret is None

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event)
            .where(Event.action == "created", Event.subject == "repository")
            .order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "created"
    assert event.subject == "repository"
    assert event.name == "test-repo"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)

    with open(os.path.join(data_dir, "example_delete_repo.json")) as f:
        json_data = json.load(f)

    ret = process_webhook(json_data, {"X-GitHub-Event": "repository"})
    assert ret is None

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event)
            .where(Event.action == "deleted", Event.subject == "repository")
            .order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "deleted"
    assert event.subject == "repository"
    assert event.name == "test-repo"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)
    assert len(event.reports) == 0

    with open(os.path.join(data_dir, "example_delete_repo.json")) as f:
        json_data = json.load(f)

    timestamp = datetime.datetime.strptime(json_data["repository"]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    timestamp += datetime.timedelta(minutes=5)  # deletion 5 minutes after creation
    ret = process_webhook(json_data, {"X-GitHub-Event": "repository"}, timestamp=timestamp)
    assert ret is not None
    assert isinstance(ret, Report)
    assert ret.content == "Repository deleted less than 10 minutes after creation!"  # TODO: parametrize 10 minutes

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event)
            .where(Event.action == "deleted", Event.subject == "repository")
            .order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "deleted"
    assert event.subject == "repository"
    assert event.name == "test-repo"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)
    assert len(event.reports) == 1
    assert event.reports[0].content == "Repository deleted less than 10 minutes after creation!"

    # check report is posted and can be recovered
    with SmartSession() as session:
        report = session.scalars(
            sa.select(Report)
            .where(Report.content == "Repository deleted less than 10 minutes after creation!")
            .order_by(Report.created_at.desc())
        ).first()

    assert report is not None
    assert report.created_at < now
    assert report.created_at > now - datetime.timedelta(seconds=3)
    assert report.event_id == event.id
    assert report.content == "Repository deleted less than 10 minutes after creation!"
