from sqlalchemy import schema
from sqlalchemy import sql
from sqlalchemy import types
from sqlalchemy import orm
from sqlalchemy.ext.declarative import instrument_declarative
from euphorie.client.model import metadata
from euphorie.client.model import Account
from euphorie.client.model import BaseObject
from euphorie.client.model import SurveyTreeItem
from euphorie.client.model import Risk
from euphorie.client.model import Company
from euphorie.client.model import SKIPPED_PARENTS
from euphorie.client.model import MODULE_WITH_RISK_OR_TOP5_FILTER
from euphorie.client.model import RISK_PRESENT_OR_TOP5_FILTER


class LoginStatistics(BaseObject):
    """Data table to store login information for users.
    """
    __tablename__ = "statistics_login"
    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_id = schema.Column(types.Integer(),
            schema.ForeignKey(Account.id,
                onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False, index=True)
    account = orm.relation(Account,
            backref=orm.backref("logins",
                                cascade="all, delete, delete-orphan"))
    time = schema.Column(types.DateTime(timezone=False),
            server_default=sql.text('CURRENT_TIMESTAMP'),
            nullable=False, index=True)


_instrumented = False
if not _instrumented:
    for cls in [LoginStatistics]:
        instrument_declarative(cls, metadata._decl_registry, metadata)
    _instrumented = True


# Pyflakes
Company = Company
SKIPPED_PARENTS = SKIPPED_PARENTS
MODULE_WITH_RISK_OR_TOP5_FILTER = MODULE_WITH_RISK_OR_TOP5_FILTER
RISK_PRESENT_OR_TOP5_FILTER = RISK_PRESENT_OR_TOP5_FILTER
# Pyflakes

node = orm.aliased(SurveyTreeItem)

UNANSWERED_RISKS_FILTER = \
        sql.and_(SurveyTreeItem.type == "risk",
                sql.exists(sql.select([Risk.sql_risk_id]).where(sql.and_(
                    Risk.sql_risk_id == SurveyTreeItem.id,
                    Risk.identification == None,
                    ))))

MODULE_WITH_UNANSWERED_RISKS_FILTER = \
        sql.and_(SurveyTreeItem.type == "module",
                SurveyTreeItem.skip_children == False,
                sql.exists(sql.select([node.id]).where(sql.and_(
                    node.session_id == SurveyTreeItem.session_id,
                    node.id == Risk.sql_risk_id,
                    node.type == "risk",
                    Risk.identification == None,
                    node.depth > SurveyTreeItem.depth,
                    node.path.like(SurveyTreeItem.path + "%")))))

MODULE_WITH_RISKS_NOT_PRESENT_FILTER = \
        sql.and_(SurveyTreeItem.type == "module",
                SurveyTreeItem.skip_children == False,
                sql.exists(sql.select([node.id]).where(sql.and_(
                    node.session_id == SurveyTreeItem.session_id,
                    node.id == Risk.sql_risk_id,
                    node.type == "risk",
                    Risk.identification == 'yes',
                    node.depth > SurveyTreeItem.depth,
                    node.path.like(SurveyTreeItem.path + "%")))))

RISK_NOT_PRESENT_FILTER = \
        sql.and_(SurveyTreeItem.type == "risk",
                sql.exists(sql.select([Risk.sql_risk_id]).where(sql.and_(
                    Risk.sql_risk_id == SurveyTreeItem.id,
                    Risk.identification == "yes"))))

del node
