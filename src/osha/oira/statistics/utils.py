# -*- coding: utf-8 -*-
from euphorie.client.model import Account
from euphorie.client.model import Company
from euphorie.client.model import SurveySession
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import Base
from osha.oira.statistics.model import CompanyStatistics
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

    def update_database(self, country=None):
        log.info("Init & cleanup")
        Base.metadata.drop_all(
            bind=self.session_statistics.connection(), checkfirst=True
        )
        Base.metadata.create_all(
            bind=self.session_statistics.connection(), checkfirst=True
        )

        self.update_assessment(country=country)
        self.update_account(country=country)
        self.update_company(country=country)

        self.session_statistics.commit()

    def update_assessment(self, country=None):
        sessions = (
            self.session_application.query(SurveySession, Account)
            .filter(Account.id == SurveySession.account_id)
            .filter(Account.account_type != "guest")
            .order_by(SurveySession.id)
        )
        if country is not None:
            sessions = sessions.filter(SurveySession.zodb_path.startswith(country))

        def assessment_rows(offset):
            batch = sessions.limit(self.b_size).offset(offset)
            rows = [
                SurveySessionStatistics(
                    id=session.id,
                    start_date=session.created,
                    completion_percentage=session.completion_percentage,
                    path=session.zodb_path,
                    country=session.zodb_path.split("/")[0].encode("utf-8"),
                    sector=session.zodb_path.split("/")[1].encode("utf-8"),
                    tool=session.zodb_path.split("/")[2].encode("utf-8"),
                    account_id=account.id,
                    account_type=account.account_type,
                )
                for session, account in batch
            ]
            return rows

        log.info("Table: assessment")
        self._process_batch(assessment_rows)

    def update_account(self, country=None):
        accounts = self.session_application.query(Account).order_by(Account.id)
        if country is not None:
            accounts = (
                accounts.filter(Account.id == SurveySession.account_id)
                .filter(SurveySession.zodb_path.startswith(country))
                .group_by(Account.id)
                .group_by(
                    sqlalchemy.func.substr(SurveySession.zodb_path, 0, len(country) + 1)
                )
            )

        def account_rows(offset):
            batch = accounts.limit(self.b_size).offset(offset)
            rows = [
                AccountStatistics(
                    id=account.id,
                    account_type=account.account_type,
                    creation_date=account.created or sqlalchemy.null(),
                )
                for account in batch
            ]
            return rows

        log.info("Table: account")
        self._process_batch(account_rows)

    def update_company(self, country=None):
        companies = self.session_application.query(Company)
        if country is not None:
            companies = companies.filter(Company.country == country)

        def yes_no(boolean):
            if boolean is None:
                return "no answer"
            elif boolean:
                return "yes"
            else:
                return "no"

        def company_rows(offset):
            batch = companies.limit(self.b_size).offset(offset)

            rows = [
                CompanyStatistics(
                    id=company.id,
                    session_id=company.session_id,
                    country=company.country,
                    employees=company.employees or "no answer",
                    conductor=company.conductor or "no answer",
                    referer=company.referer or "no answer",
                    workers_participated=yes_no(company.workers_participated),
                    needs_met=yes_no(company.needs_met),
                    recommend_tool=yes_no(company.recommend_tool),
                )
                for company in batch
            ]
            return rows

        log.info("Table: company")
        self._process_batch(company_rows)

    def _process_batch(self, rows_callback):
        offset = 0
        rows = []
        while offset == 0 or len(rows) != 0:
            rows = rows_callback(offset)
            if len(rows):
                self.session_statistics.add_all(rows)
                self.session_statistics.flush()
            offset = (offset + len(rows)) if len(rows) else -1
            if offset % (100 * self.b_size) == 0:
                log.info("Processed {} rows".format(offset))

    def __call__(self):
        for country in [None] + list_countries(self.session_application):
            database = STATISTICS_DATABASE_PATTERN.format(suffix=country or "global")
            log.info("Updating {}".format(database))
            self.session_statistics = create_session(
                self.statistics_url.format(database=database)
            )
            try:
                self.update_database(country=country)
            except sqlalchemy.exc.SQLAlchemyError as e:
                log.warn("Could not update {0}: {1}".format(database, e))
                continue
            self.session_statistics.close()
            log.info("Updated {}".format(database))
