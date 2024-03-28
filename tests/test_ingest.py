import os
import datetime

import sqlalchemy as sa

from models.base import CODE_ROOT, SmartSession
from models.event import Event, int_to_action, action_to_int, subject_to_int, int_to_subject
from models.report import Report

from src.ingest import process_webhook

data_dir = os.path.join(CODE_ROOT, "data")


def test_new_team():
    with open(os.path.join(data_dir, "example_new_team.json")) as f:
        raw_json = f.read()

    ret = process_webhook(raw_json)

    assert ret is None

    # check event is posted
    with SmartSession() as session:
        event = session.scalars(
            sa.select(Event).where(Event.action == "create", Event.subject == "team").order_by(Event.created_at.desc())
        ).first()

    now = datetime.datetime.utcnow()
    assert event is not None
    assert event.action == "create"
    assert event.subject == "team"
    assert event.name == "testing-team-name"
    assert event.created_at < now
    assert event.created_at > now - datetime.timedelta(seconds=3)

    with open(os.path.join(data_dir, "example_new_team_bad.json")) as f:
        raw_json = f.read()
