# -*- coding: utf-8 -*-
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import Base
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
    def __init__(self, session_application, statistics_url, b_size=1000):
        self.session_application = session_application
        self.statistics_url = statistics_url
        self.b_size = b_size

    def update_database(self, session_statistics, country=None):
        log.info("Init & cleanup")
        Base.metadata.create_all(bind=session_statistics.connection(), checkfirst=True)

        session_statistics.query(SurveySessionStatistics).delete()

        limit = self.b_size

        sessions = (
            self.session_application.query(SurveySession, Account)
            .filter(Account.id == SurveySession.account_id)
            .filter(Account.account_type != "guest")
            .order_by(SurveySession.id)
        )
        if country is not None:
            sessions = sessions.filter(SurveySession.zodb_path.startswith(country))
        log.info("Table: assessment")
        offset = 0
        rows = []
        while offset == 0 or len(rows) != 0:
            batch = sessions.limit(limit).offset(offset)
            rows = [
                SurveySessionStatistics(
                    id=session.id,
                    start_date=session.created,
                    completion_percentage=session.completion_percentage,
                    country=session.zodb_path.split("/")[0].encode("utf-8"),
                    sector=session.zodb_path.split("/")[1].encode("utf-8"),
                    tool=session.zodb_path.split("/")[2].encode("utf-8"),
                    account_type=account.account_type,
                )
                for session, account in batch
            ]
            if len(rows):
                session_statistics.add_all(rows)
                session_statistics.flush()
            offset = offset + len(rows)
            if offset % (100 * limit) == 0:
                log.info("Processed {} rows".format(offset))
        log.info("Processed {} rows".format(offset))

        session_statistics.query(AccountStatistics).delete()

        accounts = self.session_application.query(Account).order_by(Account.id)
        log.info("Table: account")
        offset = 0
        rows = []
        while offset == 0 or len(rows) != 0:
            batch = accounts.limit(limit).offset(offset)
            rows = [
                AccountStatistics(
                    id=account.id,
                    account_type=account.account_type,
                    creation_date=account.created or sqlalchemy.null(),
                )
                for account in batch
            ]
            if len(rows):
                session_statistics.add_all(rows)
                session_statistics.flush()
            offset = offset + len(rows)
            if offset % (100 * limit) == 0:
                log.info("Processed {} rows".format(offset))
        log.info("Processed {} rows".format(offset))

        session_statistics.commit()

    def __call__(self):
        for country in [None] + list_countries(self.session_application):
            database = STATISTICS_DATABASE_PATTERN.format(suffix=country or "global")
            log.info("Updating {}".format(database))
            session_statistics = create_session(
                self.statistics_url.format(database=database)
            )
            try:
                self.update_database(session_statistics, country=country)
            except sqlalchemy.exc.SQLAlchemyError as e:
                log.warn("Could not update {0}: {1}".format(database, e))
                continue
            session_statistics.close()
            log.info("Updated {}".format(database))
