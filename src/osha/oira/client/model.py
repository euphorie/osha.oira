from datetime import datetime
from euphorie.client import model
from euphorie.client.model import metadata
from logging import getLogger
from plone import api
from Products.CMFPlone.i18nl10n import monthname_msgid
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import sql
from sqlalchemy import types
from sqlalchemy.ext.declarative import instrument_declarative

import json


logger = getLogger(__name__)


class LoginStatistics(model.BaseObject):
    """Data table to store login information for users."""

    __tablename__ = "statistics_login"
    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_id = schema.Column(
        types.Integer(),
        schema.ForeignKey(model.Account.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account = orm.relation(
        model.Account,
        backref=orm.backref("logins", cascade="all, delete, delete-orphan"),
    )
    time = schema.Column(
        types.DateTime(timezone=False),
        server_default=sql.text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )


class SurveyStatistics(model.BaseObject):
    """Data table to store survey (tool) information."""

    __tablename__ = "statistics_surveys"

    zodb_path = schema.Column(types.String(512), primary_key=True)
    language = schema.Column(types.String(128), nullable=True)
    published = schema.Column(types.Boolean(), nullable=True)
    published_date = schema.Column(types.DateTime, nullable=True)
    creation_date = schema.Column(types.DateTime, nullable=True)


class UsersNotInterestedInCertificateStatusBox(model.BaseObject):
    """"""

    __tablename__ = "users_not_interested_in_certificate_status_box"
    account_id = schema.Column(
        types.Integer(),
        schema.ForeignKey(model.Account.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )


class Certificate(model.BaseObject):
    """"""

    __tablename__ = "certificate"
    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    json = schema.Column(types.UnicodeText())
    secret = schema.Column(types.UnicodeText())
    session_id = schema.Column(
        types.Integer(),
        schema.ForeignKey("session.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session = orm.relation("SurveySession", cascade="all")

    @property
    def json_data(self):
        try:
            return json.loads(self.json)
        except (TypeError, ValueError):
            return {}

    @property
    def title(self):
        return self.json_data.get("title", "")

    @property
    def hr_date(self):
        date = self.json_data.get("date", "").split("-")
        if not date:
            return ""
        try:
            date[1] = api.portal.translate(
                monthname_msgid(date[1]), domain="plonelocales"
            )
        except Exception:
            logger.error("Not a valid date %r", date)
        return " ".join(reversed(date))

    @property
    def hr_date_plain(self):
        date = self.json_data.get("date", "")
        if not date:
            return ""
        return datetime.strptime(date, "%Y-%m-%d")


class NewsletterSubscription(model.BaseObject):
    __tablename__ = "newsletter_subscription"

    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_id = schema.Column(
        types.Integer(),
        schema.ForeignKey(model.Account.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    zodb_path = schema.Column(types.String(512), nullable=False)


class NewsletterSetting(model.BaseObject):
    __tablename__ = "newsletter_setting"

    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_id = schema.Column(
        types.Integer(),
        schema.ForeignKey(model.Account.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    value = schema.Column(types.String(512), nullable=False)


_instrumented = False
if not _instrumented:
    for cls in [
        LoginStatistics,
        SurveyStatistics,
        Certificate,
        UsersNotInterestedInCertificateStatusBox,
        NewsletterSubscription,
        NewsletterSetting,
    ]:
        instrument_declarative(cls, metadata._decl_registry, metadata)

    _instrumented = True


def _SKIPPED_MODULE_factory():
    node = orm.aliased(model.SurveyTreeItem)
    return sql.exists().where(
        sql.and_(
            model.SurveyTreeItem.type == "module",
            node.session_id == model.SurveyTreeItem.session_id,
            node.skip_children == True,  # noqa: E712
        )
    )


SKIPPED_MODULE = _SKIPPED_MODULE_factory()


def _UNANSWERED_RISKS_FILTER_factory():
    Risk_ = orm.aliased(model.Risk)
    return sql.and_(
        model.SurveyTreeItem.type == "risk",
        sql.exists(
            sql.select([Risk_.sql_risk_id]).where(
                sql.and_(
                    Risk_.sql_risk_id == model.SurveyTreeItem.id,
                    Risk_.identification == None,  # noqa: E711
                )
            )
        ),
    )


UNANSWERED_RISKS_FILTER = _UNANSWERED_RISKS_FILTER_factory()


def MODULE_WITH_UNANSWERED_RISKS_FILTER_factory():
    node = orm.aliased(model.SurveyTreeItem)
    return sql.and_(
        model.SurveyTreeItem.type == "module",
        model.SurveyTreeItem.skip_children == False,  # noqa: E/12
        sql.exists(
            sql.select([node.id]).where(
                sql.and_(
                    node.session_id == model.SurveyTreeItem.session_id,
                    node.id == model.Risk.sql_risk_id,
                    node.type == "risk",
                    model.Risk.identification == None,  # noqa: E711
                    node.depth > model.SurveyTreeItem.depth,
                    node.path.like(model.SurveyTreeItem.path + "%"),
                )
            )
        ),
    )


MODULE_WITH_UNANSWERED_RISKS_FILTER = MODULE_WITH_UNANSWERED_RISKS_FILTER_factory()


def MODULE_WITH_RISKS_NOT_PRESENT_FILTER_factory():
    node = orm.aliased(model.SurveyTreeItem)
    return sql.and_(
        model.SurveyTreeItem.type == "module",
        model.SurveyTreeItem.skip_children == False,  # noqa: E712
        sql.exists(
            sql.select([node.id]).where(
                sql.and_(
                    node.session_id == model.SurveyTreeItem.session_id,
                    node.id == model.Risk.sql_risk_id,
                    node.type == "risk",
                    model.Risk.identification == "yes",
                    node.depth > model.SurveyTreeItem.depth,
                    node.path.like(model.SurveyTreeItem.path + "%"),
                )
            )
        ),
    )


MODULE_WITH_RISKS_NOT_PRESENT_FILTER = MODULE_WITH_RISKS_NOT_PRESENT_FILTER_factory()


def RISK_NOT_PRESENT_FILTER_factory():
    Risk_ = orm.aliased(model.Risk)
    return sql.and_(
        model.SurveyTreeItem.type == "risk",
        sql.exists(
            sql.select([Risk_.sql_risk_id]).where(
                sql.and_(
                    Risk_.sql_risk_id == model.SurveyTreeItem.id,
                    Risk_.identification == "yes",
                )
            )
        ),
    )


RISK_NOT_PRESENT_FILTER = RISK_NOT_PRESENT_FILTER_factory()
