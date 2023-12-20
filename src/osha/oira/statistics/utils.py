from datetime import datetime
from euphorie.client.model import Account
from euphorie.client.model import Company
from euphorie.client.model import Risk
from euphorie.client.model import Session as EuphorieSession
from euphorie.client.model import SurveySession
from euphorie.client.model import SurveyTreeItem
from osha.oira.client.model import NewsletterSubscription
from osha.oira.client.model import SurveyStatistics as Survey
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.model import CompanyStatistics
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import NewsletterStatistics
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.model import SurveySessionStatistics
from osha.oira.statistics.model import SurveyStatistics
from plone.memoize.instance import memoizedproperty

import logging
import sqlalchemy


log = logging.getLogger(__name__)


def list_countries(session_application):
    countries = {
        result[0].split("/")[0]
        for result in session_application.query(SurveySession.zodb_path).distinct()
    }
    return list(countries)


def list_statistics_databases(session_application):
    return [
        STATISTICS_DATABASE_PATTERN.format(suffix=suffix)
        for suffix in ["global"] + list_countries(session_application)
    ]


class UpdateStatisticsDatabases:
    exclude_domains = [
        "inrs.fr",
        "inail.it",
        "werk.belgie.be",
        "gli.government.bg",
        "mrosp.hr",
        "dli.mlsi.gov.cy",
        "ttl.fi",
        "ypakp.gr",
        "vdi.gov.lv",
        "vdi.lt",
        "gov.mt",
        "act.gov.pt",
        "gov.si",
        "gencat.cat",
        "mpsv.cz",
        "vubp.cz",
        "ip.gov.sk",
        "tim.gov.hu",
        "ver.is",
    ]

    def __init__(
        self,
        session_application,
        statistics_url,
        b_size=1000,
        optimize_cp_query=False,
        since=None,
    ):
        self.session_application = session_application
        self.statistics_url = statistics_url
        self.b_size = b_size
        self.optimize_cp_query = optimize_cp_query
        self.since = since

    def log_counts(self):
        num_tools = self.session_statistics.query(SurveyStatistics).count()
        num_assessments = self.session_statistics.query(SurveySessionStatistics).count()
        num_accounts = self.session_statistics.query(AccountStatistics).count()
        num_questionnaires = self.session_statistics.query(CompanyStatistics).count()
        log.info(
            "Tools: %s, Assessments: %s, Accounts: %s, Questionnaires: %s",
            num_tools,
            num_assessments,
            num_accounts,
            num_questionnaires,
        )

    def update_database(self, country=None):
        log.info("Init & cleanup")
        try:
            self.log_counts()
        except Exception as e:
            log.warning("Could not count rows: %s", e)
            self.session_statistics.rollback()

        self.update_tool(country=country)
        self.update_assessment(country=country)
        self.update_account(country=country)
        self.update_newsletter(country=country)
        self.update_company(country=country)

        self.session_statistics.commit()

        log.info("New statistics written")
        self.log_counts()

    def update_tool(self, country=None):
        log.info("Table: tool")

        tools = (
            self.session_application.query(
                Survey,
                sqlalchemy.func.count(
                    sqlalchemy.func.distinct(SurveySession.account_id)
                ),
                sqlalchemy.func.count(SurveySession.id),
            )
            .filter(Survey.zodb_path == SurveySession.zodb_path)
            .filter(Survey.published)
            .filter(Account.id == SurveySession.account_id)
            .filter(Account.account_type != "guest")
            .filter(
                sqlalchemy.and_(
                    sqlalchemy.not_(Account.loginname.like(f"%@{domain}"))
                    for domain in self.exclude_domains
                )
            )
            .group_by(Survey.zodb_path)
            .order_by(Survey.zodb_path)
        )
        if country is not None:
            tools = tools.filter(Survey.zodb_path.startswith(country))

        def tool_rows(offset):
            batch = tools.limit(self.b_size).offset(offset)
            handled = 0
            for tool, num_users, num_assessments in batch:
                existing = (
                    self.session_statistics.query(SurveyStatistics)
                    .filter(SurveyStatistics.tool_path == tool.zodb_path)
                    .first()
                )
                attribs = dict(
                    tool_path=tool.zodb_path,
                    published_date=tool.published_date,
                    years_online=(datetime.now() - tool.published_date).days / 365,
                    num_users=num_users,
                    num_assessments=num_assessments,
                )
                if existing:
                    for name, value in attribs.items():
                        setattr(existing, name, value)
                else:
                    self.session_statistics.add(SurveyStatistics(**attribs))
                handled = handled + 1
            return handled

        self._process_batch(tool_rows)

    @memoizedproperty
    def active_risks(self):
        module_query = (
            self.session_application.query(SurveyTreeItem).filter(
                SurveyTreeItem.type == "module"
            )
        ).order_by(SurveyTreeItem.path)

        good_module_ids = set()
        bad_module_ids = set()
        for module in module_query:
            if module.parent_id in bad_module_ids or module.skip_children:
                bad_module_ids.add(module.id)
            else:
                good_module_ids.add(module.id)

        active_risks = (
            self.session_application.query(
                Risk.id, Risk.identification, Risk.session_id
            )
            .filter(Risk.parent_id.in_(good_module_ids))
            .subquery()
        )
        return active_risks

    def update_assessment(self, country=None):
        log.info("Table: assessment")
        since = (
            self.session_statistics.query(
                sqlalchemy.func.max(SurveySessionStatistics.modified)
            ).first()[0]
            or datetime.min
        )
        if self.since and self.since < since:
            since = self.since
        if since > datetime.min:
            log.info("Skipping assessments up to and including %s", since)

        if self.optimize_cp_query:
            active_risks = self.active_risks
            sessions = self.session_application.query(
                SurveySession,
                Account,
                sqlalchemy.func.count(active_risks.c.id),
                sqlalchemy.func.count(active_risks.c.identification),
            ).outerjoin(active_risks, active_risks.c.session_id == SurveySession.id)
        else:
            sessions = self.session_application.query(
                SurveySession,
                Account,
            )

        sessions = (
            sessions.filter(SurveySession.modified > since)
            .outerjoin(SurveySession.account)
            .filter(Account.account_type != "guest")
            .filter(
                sqlalchemy.and_(
                    sqlalchemy.not_(Account.loginname.like(f"%@{domain}"))
                    for domain in self.exclude_domains
                )
            )
            .group_by(Account.id, SurveySession.id)
            .order_by(SurveySession.id)
        )
        if country is not None:
            sessions = sessions.filter(SurveySession.zodb_path.startswith(country))

        def _completion_percentage(session, total_risks, answered_risks):
            if self.optimize_cp_query:
                return (
                    int(round(answered_risks / total_risks * 100.0))
                    if total_risks
                    else 0
                )
            return session.completion_percentage

        def assessment_rows(offset):
            batch = sessions.limit(self.b_size).offset(offset)
            handled = 0
            for row in batch:
                if self.optimize_cp_query:
                    session, account, total_risks, answered_risks = row
                else:
                    session, account = row
                    total_risks = answered_risks = None
                existing = (
                    self.session_statistics.query(SurveySessionStatistics)
                    .filter(SurveySessionStatistics.id == session.id)
                    .first()
                )

                attribs = dict(
                    id=session.id,
                    start_date=session.created,
                    modified=session.modified,
                    tool_path=session.zodb_path,
                    completion_percentage=_completion_percentage(
                        session, total_risks, answered_risks
                    ),
                    country=session.zodb_path.split("/")[0],
                    account_id=account.id,
                    account_type=account.account_type,
                )
                if existing:
                    for name, value in attribs.items():
                        setattr(existing, name, value)
                else:
                    self.session_statistics.add(SurveySessionStatistics(**attribs))
                handled = handled + 1
            return handled

        self._process_batch(assessment_rows)

    def update_account(self, country=None):
        log.info("Table: account")
        since = (
            self.session_statistics.query(
                sqlalchemy.func.max(AccountStatistics.creation_date)
            ).first()[0]
            or datetime.min
        )
        if self.since and self.since < since:
            since = self.since
        if since > datetime.min:
            log.info("Skipping accounts up to and including %s", since)

        accounts = (
            self.session_application.query(Account)
            .filter(Account.created > since)
            .filter(
                sqlalchemy.and_(
                    sqlalchemy.not_(Account.loginname.like(f"%@{domain}"))
                    for domain in self.exclude_domains
                )
            )
            .order_by(Account.id)
        )
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
            handled = 0
            for account in batch:
                existing = (
                    self.session_statistics.query(AccountStatistics)
                    .filter(AccountStatistics.id == account.id)
                    .first()
                )
                attribs = dict(
                    id=account.id,
                    account_type=account.account_type,
                    creation_date=account.created or sqlalchemy.null(),
                )
                if existing:
                    for name, value in attribs.items():
                        setattr(existing, name, value)
                else:
                    self.session_statistics.add(AccountStatistics(**attribs))
                handled = handled + 1
            return handled

        self._process_batch(account_rows)

    def update_newsletter(self, country=None):
        log.info("Table: newsletter")
        subscriptions = (
            self.session_application.query(
                NewsletterSubscription.zodb_path,
                sqlalchemy.func.count(NewsletterSubscription.zodb_path),
            )
            .join(Account)
            .filter(Account.account_type != "guest")
            .group_by(NewsletterSubscription.zodb_path)
            .order_by(NewsletterSubscription.zodb_path)
        )
        # XXX Exclude domains?
        if country is not None:
            subscriptions = subscriptions.filter(
                NewsletterSubscription.zodb_path.startswith(country)
            )

        def newsletter_rows(offset):
            batch = subscriptions.limit(self.b_size).offset(offset)
            handled = 0
            for zodb_path, count in batch:
                existing = (
                    self.session_statistics.query(NewsletterStatistics)
                    .filter(NewsletterStatistics.zodb_path == zodb_path)
                    .first()
                )
                if existing:
                    if existing.count != count:
                        existing.count = count
                else:
                    self.session_statistics.add(
                        NewsletterStatistics(zodb_path=zodb_path, count=count)
                    )
                handled = handled + 1
            return handled

        self._process_batch(newsletter_rows)

    def update_company(self, country=None):
        log.info("Table: company")
        since = (
            self.session_statistics.query(
                sqlalchemy.func.max(CompanyStatistics.date)
            ).first()[0]
            or datetime.min
        )
        companies = self.session_application.query(Company, SurveySession.zodb_path)

        if self.since and self.since < since:
            since = self.since
        if since > datetime.min:
            log.info("Skipping company responses up to and including %s", since)
            companies = companies.filter(Company.timestamp > since)

        if country is not None:
            companies = companies.filter(SurveySession.zodb_path.startswith(country))

        companies = companies.filter(Company.session_id == SurveySession.id).order_by(
            Company.id
        )

        def yes_no(boolean):
            if boolean is None:
                return "no answer"
            elif boolean:
                return "yes"
            else:
                return "no"

        def company_rows(offset):
            batch = companies.limit(self.b_size).offset(offset)
            handled = 0
            for company, zodb_path in batch:
                existing = (
                    self.session_statistics.query(CompanyStatistics)
                    .filter(CompanyStatistics.id == company.id)
                    .first()
                )
                attribs = dict(
                    id=company.id,
                    country=company.country,
                    employees=company.employees or "no answer",
                    conductor=company.conductor or "no answer",
                    referer=company.referer or "no answer",
                    workers_participated=yes_no(company.workers_participated),
                    needs_met=yes_no(company.needs_met),
                    recommend_tool=yes_no(company.recommend_tool),
                    date=company.timestamp,
                    tool_path=zodb_path,
                )
                if existing:
                    for name, value in attribs.items():
                        setattr(existing, name, value)
                else:
                    self.session_statistics.add(CompanyStatistics(**attribs))
                handled = handled + 1
            return handled

        self._process_batch(company_rows)

    def _process_batch(self, batch_callback):
        offset = 0
        num_rows = 0
        while offset == 0 or num_rows != 0:
            num_rows = batch_callback(offset)
            if num_rows:
                self.session_statistics.flush()
            offset = (offset + num_rows) if num_rows else -1
            if offset % (100 * self.b_size) == 0:
                log.info("Processed %r rows", offset)

    def __call__(self):
        error = False
        for country in [None] + list_countries(self.session_application):
            database = STATISTICS_DATABASE_PATTERN.format(suffix=country or "global")
            self.session_statistics = create_session(
                self.statistics_url.format(database=database)
            )
            try:
                self.session_statistics.connection()
            except sqlalchemy.exc.OperationalError as oe:
                log.warning("Could not update %r: %r", database, oe)
                error = True
                continue

            log.info("Updating %r", database)
            try:
                self.update_database(country=country)
            except sqlalchemy.exc.SQLAlchemyError as e:
                log.warning("Could not update %r: %r", database, e)
                error = True
                continue
            self.session_statistics.close()
            log.info("Updated %r", database)
        return "OK" if not error else "FAIL"


def handle_tool_workflow(obj, event):
    surveygroup = obj.aq_parent
    update_tool_info(surveygroup)


def update_tool_info(surveygroup):
    survey = None
    if surveygroup.published:
        survey = surveygroup.get(surveygroup.published)

    creation_date = survey.created() if survey else surveygroup.created()
    if not isinstance(creation_date, datetime):
        try:
            creation_date = creation_date.asdatetime()
        except AttributeError:
            log.warning("Cannot handle creation date %r", creation_date)
            creation_date = None

    # cut out the part of the ZODB path that's used in postgresql
    # (country / sector / tool)
    zodb_path = "/".join(surveygroup.getPhysicalPath()[-3:])
    published_date = None
    if surveygroup.published and survey:
        if isinstance(survey.published, datetime):
            published_date = survey.published
        elif isinstance(survey.published, tuple):
            published_date = survey.published[2]

    EuphorieSession.query(Survey).filter(Survey.zodb_path == zodb_path).delete()

    EuphorieSession.add(
        Survey(
            zodb_path=zodb_path,
            language=survey.Language() if survey else surveygroup.Language(),
            published=bool(surveygroup.published),
            published_date=published_date,
            creation_date=creation_date,
        )
    )
