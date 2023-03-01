from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from ftw.upgrade import UpgradeStep
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.model import SurveySessionStatistics
from osha.oira.statistics.utils import list_countries
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from sqlalchemy import exc
from z3c.saconfig import Session

import logging
import sqlalchemy


logger = logging.getLogger(__name__)


class RemovePartnerAccountsFromStatistics(UpgradeStep):
    """Remove partner accounts from statistics."""

    def remove_partner_accounts(self, country, session_statistics):
        partner_accounts = (
            Session.query(Account.id, Account.loginname)
            .filter(
                sqlalchemy.or_(
                    Account.loginname.like(f"%@{domain}")
                    for domain in UpdateStatisticsDatabases.exclude_domains
                )
            )
            .order_by(Account.id)
        )
        if country is not None:
            partner_accounts = (
                partner_accounts.filter(Account.id == SurveySession.account_id)
                .filter(SurveySession.zodb_path.startswith(country))
                .group_by(Account.id)
                .group_by(
                    sqlalchemy.func.substr(SurveySession.zodb_path, 0, len(country) + 1)
                )
            )
        for account_id, account_login in partner_accounts:
            statistics_account = (
                session_statistics.query(AccountStatistics)
                .filter(AccountStatistics.id == account_id)
                .first()
            )
            if statistics_account:
                logger.info(f"Deleting account statistics for {account_login}")
                session_statistics.delete(statistics_account)

    def remove_partner_sessions(self, country, session_statistics):
        partner_sessions = (
            Session.query(SurveySession.id, Account.loginname)
            .outerjoin(SurveySession.account)
            .filter(
                sqlalchemy.or_(
                    Account.loginname.like(f"%@{domain}")
                    for domain in UpdateStatisticsDatabases.exclude_domains
                )
            )
            .order_by(SurveySession.id)
        )
        if country is not None:
            partner_sessions = partner_sessions.filter(
                SurveySession.zodb_path.startswith(country)
            )
        for session_id, account_login in partner_sessions:
            statistics_assessment = (
                session_statistics.query(SurveySessionStatistics)
                .filter(SurveySessionStatistics.id == session_id)
                .first()
            )
            if statistics_assessment:
                logger.info(
                    f"Deleting session statistics {session_id} of {account_login}"
                )
                session_statistics.delete(statistics_assessment)

    def remove_partners(self, country, session_statistics):
        self.remove_partner_accounts(country, session_statistics)
        self.remove_partner_sessions(country, session_statistics)

    def __call__(self):
        url_base = get_postgres_url()
        for country in [None] + list_countries(Session()):
            url = url_base.format(
                database=STATISTICS_DATABASE_PATTERN.format(suffix=country or "global")
            )
            session_statistics = create_session(url)
            try:
                session_statistics.connection()
            except exc.OperationalError as oe:
                logger.warning(str(oe))
                continue

            self.remove_partners(country, session_statistics)
