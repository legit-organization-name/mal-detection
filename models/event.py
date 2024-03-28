# an event class for anything that gets posted from the webhook
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from models.base import Base, utcnow

int_to_action = {
    0: "NULL",
    1: "created",
    2: "deleted",
    3: "updated",
    # add more here
}

# invert the dictionary
action_to_int = {v: k for k, v in int_to_action.items()}


int_to_subject = {
    0: "NULL",
    1: "repository",
    2: "push",
    3: "team",
    4: "user",
    5: "issue",
    # add more here
}

# invert the dictionary
subject_to_int = {v: k for k, v in int_to_subject.items()}


class Event(Base):

    __tablename__ = "events"

    _action = sa.Column(
        sa.SMALLINT,
        index=True,
        default=0,
        nullable=False,
        doc="The type of action of the event that was posted, "
        "use the event_action_to_int or event_int_to_action to translate to a string",
    )

    @hybrid_property
    def action(self):
        if self._action is None:
            self._action = 0
        return int_to_action[self._action]

    @action.inplace.expression
    @classmethod
    def action(cls):
        return sa.case(int_to_action, value=cls._action)

    @action.inplace.setter
    def action(self, value):
        if value is None:
            self._action = 0
        self._action = action_to_int[value]

    _subject = sa.Column(
        sa.SMALLINT,
        index=True,
        default=0,
        nullable=False,
        doc="The subject of the post, e.g., repository, issue, teams, commit, etc. "
        "Use the subject_to_int or int_to_subject to translate to a string",
    )

    @hybrid_property
    def subject(self):
        if self._subject is None:
            self._subject = 0
        return int_to_subject[self._subject]

    @subject.inplace.expression
    @classmethod
    def subject(cls):
        return sa.case(int_to_subject, value=cls._subject)

    @subject.inplace.setter
    def subject(self, value):
        if value is None:
            self._subject = 0
        self._subject = subject_to_int[value]

    timestamp = sa.Column(
        sa.DateTime,
        index=True,
        nullable=False,
        default=utcnow,
        doc="The time the event was posted on github, "
        "if given in the payload, otherwise the time the event was received",
    )

    reports = sa.orm.relationship(
        "Report",
        back_populates="event",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    name = sa.Column(
        sa.Text,
        nullable=False,
        default="",
        index=True,
        comment="The name of the object that was created, deleted, or modified. ",
    )
    # TODO: do we need anthing else here?
