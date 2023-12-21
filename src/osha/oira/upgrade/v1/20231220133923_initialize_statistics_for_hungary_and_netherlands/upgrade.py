from ftw.upgrade import UpgradeStep
from osha.oira.statistics.model import Base
from osha.oira.statistics.model import create_session
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN


class InitializeStatisticsForHungaryAndNetherlands(UpgradeStep):
    """Initialize statistics for Germany, Hungary and Netherlands."""

    def __call__(self):
        for country in ["de", "hu", "nl"]:
            database = STATISTICS_DATABASE_PATTERN.format(suffix=country)
            session_statistics = create_session(
                get_postgres_url().format(database=database)
            )
            Base.metadata.create_all(session_statistics.bind, checkfirst=True)
