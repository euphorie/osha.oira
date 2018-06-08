# coding=utf-8
from sqlalchemy import schema
from sqlalchemy import sql
from sqlalchemy import types
from sqlalchemy import orm
from sqlalchemy.ext.declarative import instrument_declarative
from euphorie.client import model
from euphorie.client.model import metadata


class LoginStatistics(model.BaseObject):
    """Data table to store login information for users.
    """
    __tablename__ = "statistics_login"
    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_id = schema.Column(types.Integer(),
            schema.ForeignKey(model.Account.id,
                onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False, index=True)
    account = orm.relation(model.Account,
            backref=orm.backref("logins",
                                cascade="all, delete, delete-orphan"))
    time = schema.Column(types.DateTime(timezone=False),
            server_default=sql.text('CURRENT_TIMESTAMP'),
            nullable=False, index=True)


_instrumented = False
if not _instrumented:
    for cls in [LoginStatistics]:
        instrument_declarative(
            cls, metadata._decl_registry, metadata
        )

    _instrumented = True

node = orm.aliased(model.SurveyTreeItem)
SKIPPED_MODULE = \
    sql.exists().where(
        sql.and_(
            model.SurveyTreeItem.type == "module",
            node.session_id == model.SurveyTreeItem.session_id,
            node.skip_children == True
        )
    )

UNANSWERED_RISKS_FILTER = \
        sql.and_(model.SurveyTreeItem.type == "risk",
                sql.exists(sql.select([model.Risk.sql_risk_id]).where(sql.and_(
                    model.Risk.sql_risk_id == model.SurveyTreeItem.id,
                    model.Risk.identification == None,
                    ))))

MODULE_WITH_UNANSWERED_RISKS_FILTER = \
        sql.and_(model.SurveyTreeItem.type == "module",
                model.SurveyTreeItem.skip_children == False,
                sql.exists(sql.select([node.id]).where(sql.and_(
                    node.session_id == model.SurveyTreeItem.session_id,
                    node.id == model.Risk.sql_risk_id,
                    node.type == "risk",
                    model.Risk.identification == None,
                    node.depth > model.SurveyTreeItem.depth,
                    node.path.like(model.SurveyTreeItem.path + "%")))))

MODULE_WITH_RISKS_NOT_PRESENT_FILTER = \
        sql.and_(model.SurveyTreeItem.type == "module",
                model.SurveyTreeItem.skip_children == False,
                sql.exists(sql.select([node.id]).where(sql.and_(
                    node.session_id == model.SurveyTreeItem.session_id,
                    node.id == model.Risk.sql_risk_id,
                    node.type == "risk",
                    model.Risk.identification == 'yes',
                    node.depth > model.SurveyTreeItem.depth,
                    node.path.like(model.SurveyTreeItem.path + "%")))))

RISK_NOT_PRESENT_FILTER = \
        sql.and_(model.SurveyTreeItem.type == "risk",
                sql.exists(sql.select([model.Risk.sql_risk_id]).where(sql.and_(
                    model.Risk.sql_risk_id == model.SurveyTreeItem.id,
                    model.Risk.identification == "yes"))))

del node
