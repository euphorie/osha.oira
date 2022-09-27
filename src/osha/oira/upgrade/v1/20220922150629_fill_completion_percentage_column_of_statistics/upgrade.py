from euphorie.client.model import SurveySession
from ftw.upgrade import UpgradeStep
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.model import SurveySessionStatistics
from osha.oira.statistics.utils import list_countries
from sqlalchemy import exc
from z3c.saconfig import Session

import logging


logger = logging.getLogger(__name__)


class FillCompletionPercentageColumnOfStatistics(UpgradeStep):
    """Fill completion percentage column of statistics."""

    def fill_completion_percentage(self, country, session_statistics):
        logger.info("Filling completion_percentage for %r", country or "global")
        base_query = (
            session_statistics.query(SurveySessionStatistics)
            .filter(SurveySessionStatistics.completion_percentage.is_(None))
            .order_by(SurveySessionStatistics.modified.desc())
        )
        b_size = 1000
        handled = 0
        missing = 0
        batch = base_query.limit(b_size)
        while batch.count() > 0:
            for statistics_session in batch:
                application_session = (
                    Session.query(SurveySession)
                    .filter(SurveySession.id == statistics_session.id)
                    .first()
                )
                if application_session:
                    statistics_session.completion_percentage = (
                        application_session.completion_percentage
                    )
                    handled = handled + 1
                else:
                    statistics_session.completion_percentage = 0
                    missing = missing + 1
            session_statistics.commit()
            logger.info("Handled %r sessions (%r missing)", handled, missing)
            # Because we've committed, the rows we've updated are already reflected in
            # the next query. They don't match the query filter any more, so we don't
            # need to use an offset.
            batch = base_query.limit(b_size)
        else:
            logger.info("%r is up to date", country or "global")

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

            self.fill_completion_percentage(country, session_statistics)
