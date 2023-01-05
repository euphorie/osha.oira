from euphorie.client.model import SurveySession
from ftw.upgrade import UpgradeStep
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.model import SurveySessionStatistics
from osha.oira.statistics.utils import list_countries
from osha.oira.upgrade.utils import alembic_upgrade_statistics_to
from sqlalchemy import exc
from z3c.saconfig import Session

import logging


logger = logging.getLogger(__name__)


class AddModifiedAndCompletionPercentageColumnsToSurveyStatistics(UpgradeStep):
    """Add modified and completion percentage columns to survey statistics."""

    def update_newest_session(self, country, session_statistics):
        """Make sure that the newest session is present in the statistics
        database and has a modified date so that update_statistics knows where
        to pick up."""
        if session_statistics.query(SurveySessionStatistics).count() <= 0:
            # if the statistics DB is empty we need to do a full update_statistics
            # run anyway
            return
        country_sessions = Session.query(SurveySession).order_by(
            SurveySession.modified.desc()
        )
        if country is not None:
            country_sessions = country_sessions.filter(
                SurveySession.zodb_path.startswith(country)
            )
        newest_statistics_session = None
        for newest_application_session in country_sessions:
            newest_statistics_session = (
                session_statistics.query(SurveySessionStatistics)
                .filter(SurveySessionStatistics.id == newest_application_session.id)
                .first()
            )
            if newest_statistics_session:
                break
        if newest_statistics_session:
            newest_statistics_session.modified = newest_application_session.modified
            session_statistics.commit()
        else:
            logger.warning("No matching sessions found for %r", country)

    def __call__(self):
        alembic_upgrade_statistics_to(self.target_version)
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

            self.update_newest_session(country, session_statistics)
