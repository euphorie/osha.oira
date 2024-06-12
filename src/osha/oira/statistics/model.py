from App.config import getConfiguration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging


log = logging.getLogger(__name__)

STATISTICS_DATABASE_PATTERN = "statistics_{suffix}"


def get_postgres_url():
    configuration = getConfiguration()
    if not hasattr(configuration, "product_config"):
        msg = "No product config found! Database connection cannot be set up"
        log.error(msg)
        return None
    conf = configuration.product_config.get("osha.oira")
    postgres_url_statistics = conf.get("postgres-url-statistics", "")
    return postgres_url_statistics


def create_session(database_url):
    engine = create_engine(database_url)
    if engine is None:
        return None
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
