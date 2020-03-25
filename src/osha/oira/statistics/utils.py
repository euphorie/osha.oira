# -*- coding: utf-8 -*-
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import STATISTICS_DATABASES
from osha.oira.statistics.model import SurveySessionStatistics
import logging
import sqlalchemy

log = logging.getLogger(__name__)


class UpdateStatisticsDatabases(object):
    def __init__(self, session_application, statistics_url):
        self.session_application = session_application
        self.statistics_url = statistics_url

    def update_database(self, session_statistics):
        session_statistics.query(SurveySessionStatistics).delete()

        sessions = self.session_application.query(SurveySession, Account).filter(
            Account.id == SurveySession.account_id
        )
        session_statistics.add_all(
            [
                SurveySessionStatistics(
                    id=session.id,
                    start_date=session.created,
                    completion_percentage=session.completion_percentage,
                    country=session.zodb_path.split("/")[0].encode("utf-8"),
                    sector=session.zodb_path.split("/")[1].encode("utf-8"),
                    tool=session.zodb_path.split("/")[2].encode("utf-8"),
                    account_type=account.account_type,
                )
                for session, account in sessions
            ]
        )

        session_statistics.query(AccountStatistics).delete()

        accounts = self.session_application.query(Account)
        session_statistics.add_all(
            [
                AccountStatistics(
                    id=account.id,
                    account_type=account.account_type,
                    creation_date=account.created or sqlalchemy.null(),
                )
                for account in accounts
            ]
        )
        return

    def __call__(self):
        for database in STATISTICS_DATABASES:
            session_statistics = create_session(
                self.statistics_url.format(database=database)
            )
            self.update_database(session_statistics)
            session_statistics.commit()
            session_statistics.close()
            log.info("Updated {}".format(database))
