# a class to log reports made to the user about suspicious activity
import sqlalchemy as sa

from models.base import Base


class Report(Base):
    __tablename__ = "reports"

    content = sa.Column(sa.Text, nullable=False, default="", index=True, comment="The content of the report")

    event_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The event that triggered the report",
    )

    event = sa.orm.relationship("Event", back_populates="reports", lazy="selectin")

    def printout(self):
        print(self.content)
