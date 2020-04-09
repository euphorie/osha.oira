# -*- coding: utf-8 -*-
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.model import SurveySessionStatistics
import logging
import sqlalchemy

log = logging.getLogger(__name__)


def list_countries(session_application):
    countries = set(
        [
            result[0].split("/")[0]
            for result in session_application.query(SurveySession.zodb_path).distinct()
        ]
    )
    return list(countries)


def list_statistics_databases(session_application):
    return [
        STATISTICS_DATABASE_PATTERN.format(suffix=suffix)
        for suffix in ["global"] + list_countries(session_application)
    ]


class UpdateStatisticsDatabases(object):
    def __init__(self, session_application, statistics_url):
        self.session_application = session_application
        self.statistics_url = statistics_url

    def update_database(self, session_statistics, country=None):
        session_statistics.query(SurveySessionStatistics).delete()

        sessions = self.session_application.query(SurveySession, Account).filter(
            Account.id == SurveySession.account_id
        )
        if country is not None:
            sessions = sessions.filter(SurveySession.zodb_path.startswith(country))
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
        for country in [None] + list_countries(self.session_application):
            database = STATISTICS_DATABASE_PATTERN.format(suffix=country or "global")
            session_statistics = create_session(
                self.statistics_url.format(database=database)
            )
            try:
                self.update_database(session_statistics, country=country)
            except sqlalchemy.exc.SQLAlchemyError as e:
                log.warn("Could not update {0}: {1}".format(database, e))
                continue
            session_statistics.commit()
            session_statistics.close()
            log.info("Updated {}".format(database))
